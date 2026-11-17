"""Dual-Path Temporal State Machine with Event Boundary Detection (Stage 8.9.13).

Architecture:
1. Fast-Path: High-confidence threshold (tau_fast) triggers immediately on a single window.
   Protects short screams (< 1.0s) and startle shrieks from being suppressed.
2. Sustained-Path: Moderate-confidence threshold (tau_sustained) requires temporal evidence
   (e.g. consecutive positive windows or k-of-m voting) to confirm persistent screams.
3. Event Boundary Tracking: Merges overlapping positive windows into a single event.
   Closes event after N_quiet consecutive windows below tau_release.
4. Cooldown Deduplication: Suppresses duplicate alert dispatching during ongoing event.

Safety Notice:
"POSSIBLE SCREAM DETECTED — REQUIRES HUMAN AUDITORY VERIFICATION. Automated acoustic alerts do not confirm an emergency."
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class EventState(Enum):
    IDLE = "IDLE"
    SUSTAINED_PENDING = "SUSTAINED_PENDING"
    EVENT_ACTIVE = "EVENT_ACTIVE"
    COOLDOWN = "COOLDOWN"


SAFETY_WARNING = (
    "POSSIBLE SCREAM DETECTED — REQUIRES HUMAN AUDITORY VERIFICATION. "
    "Automated acoustic alerts do not confirm an emergency."
)


class DualPathEventStateMachine:
    """State machine combining fast transient path and sustained persistent path with boundary tracking."""

    def __init__(
        self,
        tau_fast: float = 0.85,
        tau_sustained: float = 0.60,
        tau_release: float = 0.30,
        sustained_confirm_hops: int = 2,
        quiet_release_hops: int = 2,
        cooldown_hops: int = 6,
        name: str = "DualPath_Event_State_Machine",
    ):
        self.name = name
        self.tau_fast = tau_fast
        self.tau_sustained = tau_sustained
        self.tau_release = tau_release
        self.sustained_confirm_hops = sustained_confirm_hops
        self.quiet_release_hops = quiet_release_hops
        self.cooldown_hops = cooldown_hops
        self.reset()

    def reset(self):
        self.state = EventState.IDLE
        self.pending_hops = 0
        self.quiet_hops = 0
        self.cooldown_counter = 0
        self.active_event_onset_sec: Optional[float] = None
        self.peak_confidence: float = 0.0
        self.active_trigger_path: Optional[str] = None

    def step(self, prob: float, timestamp_sec: float) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Update state machine with window probability at timestamp_sec (end of window).
        
        Returns:
            (alert_dispatched, alert_metadata_or_none)
        """
        alert_dispatched = False
        meta = None

        # -------------------------------------------------------------
        # State: IDLE
        # -------------------------------------------------------------
        if self.state == EventState.IDLE:
            # 1. Check Fast-Path (Instantaneous trigger on high confidence)
            if prob >= self.tau_fast:
                self.state = EventState.EVENT_ACTIVE
                self.active_event_onset_sec = timestamp_sec
                self.peak_confidence = prob
                self.active_trigger_path = "FAST_PATH"
                self.quiet_hops = 0
                self.cooldown_counter = self.cooldown_hops
                alert_dispatched = True

            # 2. Check Sustained-Path (Moderate confidence enters pending)
            elif prob >= self.tau_sustained:
                self.pending_hops = 1
                self.peak_confidence = prob
                if self.sustained_confirm_hops <= 1:
                    self.state = EventState.EVENT_ACTIVE
                    self.active_event_onset_sec = timestamp_sec
                    self.active_trigger_path = "SUSTAINED_PATH"
                    self.quiet_hops = 0
                    self.cooldown_counter = self.cooldown_hops
                    alert_dispatched = True
                else:
                    self.state = EventState.SUSTAINED_PENDING
            else:
                self.pending_hops = 0

        # -------------------------------------------------------------
        # State: SUSTAINED_PENDING
        # -------------------------------------------------------------
        elif self.state == EventState.SUSTAINED_PENDING:
            # Check if high confidence arrived
            if prob >= self.tau_fast:
                self.state = EventState.EVENT_ACTIVE
                self.active_event_onset_sec = timestamp_sec
                self.peak_confidence = max(self.peak_confidence, prob)
                self.active_trigger_path = "FAST_PATH_ESCALATED"
                self.quiet_hops = 0
                self.cooldown_counter = self.cooldown_hops
                alert_dispatched = True
            elif prob >= self.tau_sustained:
                self.pending_hops += 1
                self.peak_confidence = max(self.peak_confidence, prob)
                if self.pending_hops >= self.sustained_confirm_hops:
                    self.state = EventState.EVENT_ACTIVE
                    self.active_event_onset_sec = timestamp_sec
                    self.active_trigger_path = "SUSTAINED_PATH"
                    self.quiet_hops = 0
                    self.cooldown_counter = self.cooldown_hops
                    alert_dispatched = True
            else:
                # Dropped below sustained threshold before confirmation
                self.state = EventState.IDLE
                self.pending_hops = 0
                self.peak_confidence = 0.0

        # -------------------------------------------------------------
        # State: EVENT_ACTIVE
        # -------------------------------------------------------------
        elif self.state == EventState.EVENT_ACTIVE:
            self.peak_confidence = max(self.peak_confidence, prob)
            if self.cooldown_counter > 0:
                self.cooldown_counter -= 1

            # Check for event offset (quiet release)
            if prob < self.tau_release:
                self.quiet_hops += 1
                if self.quiet_hops >= self.quiet_release_hops:
                    self.state = EventState.COOLDOWN
            else:
                self.quiet_hops = 0  # Still ongoing sound

        # -------------------------------------------------------------
        # State: COOLDOWN
        # -------------------------------------------------------------
        elif self.state == EventState.COOLDOWN:
            if self.cooldown_counter > 0:
                self.cooldown_counter -= 1

            if prob < self.tau_release:
                self.quiet_hops += 1
                # If cooldown finished and quiet holds, return to IDLE
                if self.cooldown_counter == 0 and self.quiet_hops >= self.quiet_release_hops:
                    self.state = EventState.IDLE
                    self.active_event_onset_sec = None
                    self.active_trigger_path = None
                    self.peak_confidence = 0.0
                    self.quiet_hops = 0
            else:
                self.quiet_hops = 0
                # If cooldown finished and new burst appears, trigger new event!
                if self.cooldown_counter == 0:
                    if prob >= self.tau_fast:
                        self.state = EventState.EVENT_ACTIVE
                        self.active_event_onset_sec = timestamp_sec
                        self.peak_confidence = prob
                        self.active_trigger_path = "FAST_PATH_NEW_EVENT"
                        self.cooldown_counter = self.cooldown_hops
                        alert_dispatched = True
                    elif prob >= self.tau_sustained:
                        self.pending_hops = 1
                        self.peak_confidence = prob
                        self.state = EventState.SUSTAINED_PENDING

        if alert_dispatched:
            meta = {
                "policy": self.name,
                "timestamp_sec": timestamp_sec,
                "prob": prob,
                "peak_confidence": self.peak_confidence,
                "trigger_path": self.active_trigger_path,
                "tau_fast": self.tau_fast,
                "tau_sustained": self.tau_sustained,
                "tau_release": self.tau_release,
                "notice": SAFETY_WARNING,
            }

        return alert_dispatched, meta
