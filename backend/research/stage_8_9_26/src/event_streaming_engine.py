"""Streaming Buffer and Event Boundary State Machine (Stage 8.9.26).

Implements Spray-Can Detector Engineering Principles:
1. Two-Stage Candidate Screening -> Verification.
2. Temporal Persistence & Event Grouping: Groups overlapping positive windows into discrete events.
3. Fast-Trigger Short-Scream Protection: Permits single-window immediate alert trigger.
4. Alert Cooldown: Suppresses redundant alert dispatching for ongoing vocalizations without hiding separate screams.
5. Streaming Buffer Management: Sliding window circular buffer with queue monitoring and dropped-window detection.
"""

from __future__ import annotations

import collections
import enum
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np


class StreamingState(enum.Enum):
    IDLE = "IDLE"
    CANDIDATE_PENDING = "CANDIDATE_PENDING"
    EVENT_ACTIVE = "EVENT_ACTIVE"
    COOLDOWN = "COOLDOWN"


@dataclass
class ScreamAlertEvent:
    event_id: str
    start_time_sec: float
    end_time_sec: float
    peak_score: float
    trigger_type: str  # FAST_TRANSIENT, SUSTAINED_CADENCE
    window_count: int
    classification: str  # POSSIBLE_SCREAM, AMBIGUOUS_VOCALIZATION
    suppressed_duplicates: int = 0
    resolved: bool = False


@dataclass
class WindowFrame:
    window_idx: int
    start_sec: float
    end_sec: float
    passed_prescreen: bool
    score: float
    classification: str
    compute_ms: float
    queue_delay_ms: float


class StreamingBufferManager:
    """Manages circular streaming buffer for 16 kHz audio with overlap and queue tracking."""

    def __init__(self, sample_rate: int = 16000, window_sec: float = 0.975, hop_sec: float = 0.25):
        self.sample_rate = sample_rate
        self.window_samples = int(round(window_sec * sample_rate))
        self.hop_samples = int(round(hop_sec * sample_rate))
        self.buffer = np.zeros(self.window_samples * 4, dtype=np.float32)
        self.buffer_len = 0
        self.total_samples_ingested = 0
        self.dropped_windows = 0
        self.processed_windows = 0
        self.window_counter = 0

    def ingest_audio(self, pcm_chunk: np.ndarray) -> List[Tuple[int, float, float, np.ndarray]]:
        """Ingest new audio samples and extract complete overlapping analysis windows."""
        n_new = len(pcm_chunk)
        self.total_samples_ingested += n_new
        
        # Check buffer overflow
        if self.buffer_len + n_new > len(self.buffer):
            # Shift buffer left to make room
            discard = (self.buffer_len + n_new) - len(self.buffer)
            self.buffer[: self.buffer_len - discard] = self.buffer[discard : self.buffer_len]
            self.buffer_len -= discard
            self.dropped_windows += int(np.ceil(discard / self.hop_samples))

        self.buffer[self.buffer_len : self.buffer_len + n_new] = pcm_chunk
        self.buffer_len += n_new

        windows = []
        while self.buffer_len >= self.window_samples:
            win = self.buffer[: self.window_samples].copy()
            start_sec = (self.window_counter * self.hop_samples) / self.sample_rate
            end_sec = start_sec + (self.window_samples / self.sample_rate)
            windows.append((self.window_counter, start_sec, end_sec, win))
            
            self.window_counter += 1
            self.processed_windows += 1
            # Advance by hop
            self.buffer[: self.buffer_len - self.hop_samples] = self.buffer[self.hop_samples : self.buffer_len]
            self.buffer_len -= self.hop_samples

        return windows


class IntegratedEventStateMachine:
    """State machine combining fast transient triggers, event grouping, and cooldown re-arming."""

    def __init__(
        self,
        tau_alert: float = 0.35,
        tau_fast_transient: float = 0.50,
        tau_release: float = 0.25,
        cooldown_hops: int = 6,  # 6 hops * 0.25s = 1.5s
        min_hops_to_confirm_sustained: int = 2,
    ):
        self.tau_alert = tau_alert
        self.tau_fast_transient = tau_fast_transient
        self.tau_release = tau_release
        self.cooldown_hops = cooldown_hops
        self.min_hops_sustained = min_hops_to_confirm_sustained
        
        self.state = StreamingState.IDLE
        self.cooldown_timer = 0
        self.pending_hops = 0
        self.quiet_hops = 0
        
        self.current_event: Optional[ScreamAlertEvent] = None
        self.closed_events: List[ScreamAlertEvent] = []
        self.emitted_alerts: List[ScreamAlertEvent] = []
        
        self.total_alerts_emitted = 0
        self.total_duplicates_suppressed = 0

    def process_window(self, win_idx: int, start_sec: float, end_sec: float, score: float, classification: str) -> Optional[ScreamAlertEvent]:
        """Process score for a window and update event boundary and alert dispatching."""
        alert_to_emit = None

        # 1. State: IDLE
        if self.state == StreamingState.IDLE:
            if score >= self.tau_fast_transient:
                # Immediate Fast-Trigger (Protects short screams)
                self.state = StreamingState.EVENT_ACTIVE
                self.current_event = ScreamAlertEvent(
                    event_id=f"EVT_{win_idx}_{int(start_sec * 1000)}",
                    start_time_sec=start_sec,
                    end_time_sec=end_sec,
                    peak_score=score,
                    trigger_type="FAST_TRANSIENT",
                    window_count=1,
                    classification=classification,
                )
                self.total_alerts_emitted += 1
                alert_to_emit = self.current_event
            elif score >= self.tau_alert:
                # Moderate score: begin candidate pending
                self.state = StreamingState.CANDIDATE_PENDING
                self.pending_hops = 1
                self.current_event = ScreamAlertEvent(
                    event_id=f"EVT_{win_idx}_{int(start_sec * 1000)}",
                    start_time_sec=start_sec,
                    end_time_sec=end_sec,
                    peak_score=score,
                    trigger_type="SUSTAINED_CADENCE",
                    window_count=1,
                    classification=classification,
                )

        # 2. State: CANDIDATE_PENDING
        elif self.state == StreamingState.CANDIDATE_PENDING:
            if score >= self.tau_alert:
                self.pending_hops += 1
                self.current_event.window_count += 1
                self.current_event.end_time_sec = end_sec
                self.current_event.peak_score = max(self.current_event.peak_score, score)
                if self.pending_hops >= self.min_hops_sustained:
                    # Confirmed sustained event!
                    self.state = StreamingState.EVENT_ACTIVE
                    self.total_alerts_emitted += 1
                    alert_to_emit = self.current_event
            else:
                # Aborted transient below fast threshold
                self.state = StreamingState.IDLE
                self.pending_hops = 0
                self.current_event = None

        # 3. State: EVENT_ACTIVE
        elif self.state == StreamingState.EVENT_ACTIVE:
            if score >= self.tau_release:
                # Event continues, group overlapping windows into single continuous event
                self.current_event.end_time_sec = end_sec
                self.current_event.peak_score = max(self.current_event.peak_score, score)
                self.current_event.window_count += 1
                self.quiet_hops = 0
                self.total_duplicates_suppressed += 1
                self.current_event.suppressed_duplicates += 1
            else:
                self.quiet_hops += 1
                if self.quiet_hops >= 2:
                    # Vocalization ended, close event and transition to COOLDOWN
                    self.current_event.resolved = True
                    self.closed_events.append(self.current_event)
                    self.state = StreamingState.COOLDOWN
                    self.cooldown_timer = self.cooldown_hops
                    self.quiet_hops = 0

        # 4. State: COOLDOWN
        elif self.state == StreamingState.COOLDOWN:
            self.cooldown_timer -= 1
            if score >= 0.75:
                # Explosive fresh scream onset overrides cooldown! (Separate emergency event)
                self.state = StreamingState.EVENT_ACTIVE
                self.current_event = ScreamAlertEvent(
                    event_id=f"EVT_{win_idx}_{int(start_sec * 1000)}_OVERRIDE",
                    start_time_sec=start_sec,
                    end_time_sec=end_sec,
                    peak_score=score,
                    trigger_type="COOLDOWN_OVERRIDE_BURST",
                    window_count=1,
                    classification=classification,
                )
                self.total_alerts_emitted += 1
                alert_to_emit = self.current_event
            elif score >= self.tau_alert:
                # Trailing echo/reverberation suppressed during cooldown
                self.total_duplicates_suppressed += 1
            
            if self.cooldown_timer <= 0:
                self.state = StreamingState.IDLE
                self.current_event = None

        return alert_to_emit
