"""Temporal Smoothing and Event State Machine Engine (Stage 7).

Implements deterministic state tracking:
  IDLE -> CANDIDATE -> ALERT_ACTIVE -> COOLDOWN -> IDLE

Features:
- Prevents isolated 1-window transient false triggers (temporal smoothing).
- Emits exactly one alert for a continuous scream event rather than flooding per window.
- Updates ongoing event metadata (peak probability, duration, window history).
- Suppresses duplicate alerts during configurable cooldown.
- Re-enables fresh alerting after cooldown expires and a new event qualifies.
- Resets cleanly after audio gaps or exceptions.
"""

from __future__ import annotations

import enum
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("state_machine")


class DetectorState(enum.Enum):
    """Detector state machine operational states."""
    IDLE = "IDLE"
    CANDIDATE = "CANDIDATE"
    ALERT_ACTIVE = "ALERT_ACTIVE"
    COOLDOWN = "COOLDOWN"


@dataclass
class WindowInferenceResult:
    """Inference result for a single processed audio window."""
    window_index: int
    stream_time_seconds: float
    raw_probability: float
    smoothed_probability: float
    is_positive: bool
    threshold: float
    yamnet_top_priors: List[Dict[str, Any]] = field(default_factory=list)
    latency_ms: float = 0.0
    audio_rms: float = 0.0


@dataclass
class ScreamEvent:
    """Structured record of a detected distress vocalization event."""
    event_id: str
    start_stream_time: float
    end_stream_time: float
    start_wall_time_iso: str
    end_wall_time_iso: Optional[str] = None
    peak_probability: float = 0.0
    threshold: float = 0.35
    window_count: int = 0
    positive_window_count: int = 0
    alert_emitted: bool = False
    suppressed_during_cooldown: bool = False
    window_scores: List[float] = field(default_factory=list)
    top_priors_summary: List[Dict[str, Any]] = field(default_factory=list)
    state_history: List[str] = field(default_factory=list)
    resolved: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert event dataclass to JSON-serializable dictionary."""
        return {
            "event_id": self.event_id,
            "start_stream_time": round(self.start_stream_time, 3),
            "end_stream_time": round(self.end_stream_time, 3),
            "duration_seconds": round(max(0.0, self.end_stream_time - self.start_stream_time), 3),
            "start_wall_time_iso": self.start_wall_time_iso,
            "end_wall_time_iso": self.end_wall_time_iso,
            "peak_probability": round(self.peak_probability, 4),
            "threshold": self.threshold,
            "window_count": self.window_count,
            "positive_window_count": self.positive_window_count,
            "alert_emitted": self.alert_emitted,
            "suppressed_during_cooldown": self.suppressed_during_cooldown,
            "window_scores_summary": [round(s, 3) for s in self.window_scores[-10:]],
            "top_priors": self.top_priors_summary[:3],
            "state_history": self.state_history,
            "resolved": self.resolved,
        }


class EventStateMachine:
    """Deterministic, hardware-independent scream event detection state machine."""

    def __init__(
        self,
        threshold: float = 0.35,
        min_consecutive_positive: int = 2,
        max_gap_negative_windows: int = 2,
        cooldown_seconds: float = 3.0,
        smoothing_alpha: float = 0.6,
        on_alert_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_event_resolved_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        """Initialize event state machine.

        Args:
            threshold: Probability threshold for a positive window (default: 0.35 from Stage 5).
            min_consecutive_positive: Number of consecutive positive windows required to trigger an alert.
            max_gap_negative_windows: Number of consecutive negative windows before an active event ends.
            cooldown_seconds: Minimum duration in seconds to suppress duplicate alerts after an event.
            smoothing_alpha: Exponential moving average coefficient (1.0 = raw score, 0.0 = frozen).
            on_alert_callback: Function called immediately when ALERT_ACTIVE is triggered.
            on_event_resolved_callback: Function called when an event ends and enters COOLDOWN/IDLE.
        """
        self.threshold = float(threshold)
        self.min_consecutive_positive = int(min_consecutive_positive)
        self.max_gap_negative_windows = int(max_gap_negative_windows)
        self.cooldown_seconds = float(cooldown_seconds)
        self.smoothing_alpha = float(smoothing_alpha)

        self.on_alert_callback = on_alert_callback
        self.on_event_resolved_callback = on_event_resolved_callback

        # Internal state
        self._state: DetectorState = DetectorState.IDLE
        self._current_event: Optional[ScreamEvent] = None
        self._completed_events: List[ScreamEvent] = []

        self._consecutive_positive: int = 0
        self._consecutive_negative: int = 0
        self._smoothed_probability: float = 0.0
        self._cooldown_start_stream_time: float = -999.0

        self._total_windows_evaluated: int = 0
        self._total_alerts_emitted: int = 0
        self._total_alerts_suppressed: int = 0

    @property
    def current_state(self) -> DetectorState:
        """Current operational state."""
        return self._state

    @property
    def total_alerts_emitted(self) -> int:
        """Count of alert events dispatched."""
        return self._total_alerts_emitted

    @property
    def total_alerts_suppressed(self) -> int:
        """Count of alarms suppressed during cooldown periods."""
        return self._total_alerts_suppressed

    @property
    def active_event(self) -> Optional[ScreamEvent]:
        """Currently active or candidate event."""
        return self._current_event

    def process_window(
        self,
        raw_probability: float,
        stream_time_seconds: float,
        window_index: int,
        yamnet_top_priors: Optional[List[Dict[str, Any]]] = None,
        latency_ms: float = 0.0,
        audio_rms: float = 0.0,
    ) -> WindowInferenceResult:
        """Process a single window probability through temporal smoothing and state transitions.

        Args:
            raw_probability: Probability of scream output by classifier (0.0 to 1.0).
            stream_time_seconds: Time offset from beginning of audio stream.
            window_index: Sequential index of audio window.
            yamnet_top_priors: Optional list of top AudioSet categories for diagnostic logging.
            latency_ms: Window inference execution time in milliseconds.
            audio_rms: Root-mean-square amplitude of window audio for telemetry.

        Returns:
            WindowInferenceResult describing processed outcome.
        """
        self._total_windows_evaluated += 1

        # 1. Temporal Smoothing (Exponential Moving Average)
        if self._total_windows_evaluated == 1:
            self._smoothed_probability = raw_probability
        else:
            self._smoothed_probability = (
                self.smoothing_alpha * raw_probability + (1.0 - self.smoothing_alpha) * self._smoothed_probability
            )

        # Check positive condition: both raw and smoothed must meet threshold or raw exceeds threshold
        is_positive = bool(raw_probability >= self.threshold)

        if is_positive:
            self._consecutive_positive += 1
            self._consecutive_negative = 0
        else:
            self._consecutive_negative += 1
            self._consecutive_positive = 0

        # 2. State Machine Transitions
        self._transition(
            is_positive=is_positive,
            raw_prob=raw_probability,
            stream_time=stream_time_seconds,
            yamnet_priors=yamnet_top_priors or [],
        )

        return WindowInferenceResult(
            window_index=window_index,
            stream_time_seconds=stream_time_seconds,
            raw_probability=round(raw_probability, 4),
            smoothed_probability=round(self._smoothed_probability, 4),
            is_positive=is_positive,
            threshold=self.threshold,
            yamnet_top_priors=yamnet_top_priors or [],
            latency_ms=round(latency_ms, 2),
            audio_rms=round(audio_rms, 5),
        )

    def _transition(
        self,
        is_positive: bool,
        raw_prob: float,
        stream_time: float,
        yamnet_priors: List[Dict[str, Any]],
    ) -> None:
        """Execute state transition logic."""
        old_state = self._state

        # Cooldown Expiry Check
        if self._state == DetectorState.COOLDOWN:
            elapsed_cooldown = stream_time - self._cooldown_start_stream_time
            if elapsed_cooldown >= self.cooldown_seconds:
                # Cooldown expired: return to IDLE
                self._state = DetectorState.IDLE
                logger.debug(f"Cooldown expired at {stream_time:.2f}s -> Transition to IDLE")

        # --- IDLE STATE ---
        if self._state == DetectorState.IDLE:
            if is_positive:
                # First positive window: transition to CANDIDATE
                self._state = DetectorState.CANDIDATE
                self._current_event = ScreamEvent(
                    event_id=f"evt_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}",
                    start_stream_time=stream_time,
                    end_stream_time=stream_time,
                    start_wall_time_iso=datetime.now().isoformat(),
                    peak_probability=raw_prob,
                    threshold=self.threshold,
                    window_count=1,
                    positive_window_count=1,
                    window_scores=[raw_prob],
                    top_priors_summary=yamnet_priors,
                    state_history=[DetectorState.IDLE.value, DetectorState.CANDIDATE.value],
                )

                # If requirement is 1 window, jump immediately to ALERT_ACTIVE
                if self.min_consecutive_positive <= 1:
                    self._trigger_alert(stream_time, raw_prob)

        # --- CANDIDATE STATE ---
        elif self._state == DetectorState.CANDIDATE:
            assert self._current_event is not None
            self._current_event.window_count += 1
            self._current_event.end_stream_time = stream_time
            self._current_event.window_scores.append(raw_prob)
            self._current_event.peak_probability = max(self._current_event.peak_probability, raw_prob)

            if is_positive:
                self._current_event.positive_window_count += 1
                if self._consecutive_positive >= self.min_consecutive_positive:
                    # Sufficient consecutive evidence confirmed: trigger alert
                    self._trigger_alert(stream_time, raw_prob)
            else:
                # Positive streak broken before reaching confirmation threshold
                logger.debug(f"Candidate streak broken at {stream_time:.2f}s (prob: {raw_prob:.3f}) -> IDLE")
                self._state = DetectorState.IDLE
                self._current_event.state_history.append(DetectorState.IDLE.value)
                self._current_event.resolved = True
                self._completed_events.append(self._current_event)
                self._current_event = None

        # --- ALERT_ACTIVE STATE ---
        elif self._state == DetectorState.ALERT_ACTIVE:
            assert self._current_event is not None
            self._current_event.window_count += 1
            self._current_event.end_stream_time = stream_time
            self._current_event.window_scores.append(raw_prob)
            self._current_event.peak_probability = max(self._current_event.peak_probability, raw_prob)

            if is_positive:
                self._current_event.positive_window_count += 1
            else:
                # Check event end condition (consecutive negative windows)
                if self._consecutive_negative >= self.max_gap_negative_windows:
                    self._resolve_event(stream_time)

        # --- COOLDOWN STATE ---
        elif self._state == DetectorState.COOLDOWN:
            if is_positive:
                # Positive window detected during cooldown: suppress duplicate alarm
                self._total_alerts_suppressed += 1
                logger.debug(
                    f"Alarm suppressed during cooldown at {stream_time:.2f}s (prob: {raw_prob:.3f})"
                )

        if self._state != old_state:
            logger.info(f"State transition: {old_state.value} -> {self._state.value} at stream time {stream_time:.2f}s")

    def _trigger_alert(self, stream_time: float, raw_prob: float) -> None:
        """Trigger alert event and execute external callback."""
        self._state = DetectorState.ALERT_ACTIVE
        self._total_alerts_emitted += 1
        assert self._current_event is not None
        self._current_event.alert_emitted = True
        self._current_event.state_history.append(DetectorState.ALERT_ACTIVE.value)

        event_payload = self._current_event.to_dict()
        logger.warning(
            f"!!! SCREAM ALERT TRIGGERED !!! Event {event_payload['event_id']} at {stream_time:.2f}s "
            f"(Peak P: {event_payload['peak_probability']:.4f}, Threshold: {self.threshold:.2f})"
        )

        if self.on_alert_callback:
            try:
                self.on_alert_callback(event_payload)
            except Exception as e:
                logger.error(f"Error executing on_alert_callback: {e}", exc_info=True)

    def _resolve_event(self, stream_time: float) -> None:
        """Conclude an active alert event and enter cooldown."""
        assert self._current_event is not None
        self._current_event.end_wall_time_iso = datetime.now().isoformat()
        self._current_event.resolved = True
        self._current_event.state_history.append(DetectorState.COOLDOWN.value)

        self._state = DetectorState.COOLDOWN
        self._cooldown_start_stream_time = stream_time

        event_payload = self._current_event.to_dict()
        logger.info(
            f"Event {event_payload['event_id']} resolved at {stream_time:.2f}s. "
            f"Entering cooldown ({self.cooldown_seconds:.1f}s)."
        )

        if self.on_event_resolved_callback:
            try:
                self.on_event_resolved_callback(event_payload)
            except Exception as e:
                logger.error(f"Error executing on_event_resolved_callback: {e}", exc_info=True)

        self._completed_events.append(self._current_event)
        self._current_event = None

    def reset(self) -> None:
        """Reset state machine after audio gaps, exceptions, or stream restarts."""
        if self._current_event and not self._current_event.resolved:
            self._current_event.resolved = True
            self._completed_events.append(self._current_event)

        self._state = DetectorState.IDLE
        self._current_event = None
        self._consecutive_positive = 0
        self._consecutive_negative = 0
        self._smoothed_probability = 0.0
        self._cooldown_start_stream_time = -999.0
        logger.info("EventStateMachine reset to IDLE state.")
