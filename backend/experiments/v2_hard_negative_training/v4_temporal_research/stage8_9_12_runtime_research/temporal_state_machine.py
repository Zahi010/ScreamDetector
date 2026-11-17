"""Temporal Alert State Machine and Persistence Policies for Stage 8.9.12.

Implements two distinct operational layers:
Layer 1: Acoustic Classifier (emits instantaneous window probability p_t in [0.0, 1.0])
Layer 2: Temporal Alert Policy (state machine aggregating scores over time)

Preserves the mandatory safety directive:
"POSSIBLE SCREAM DETECTED — REQUIRES HUMAN AUDITORY VERIFICATION. Automated acoustic alerts do not confirm an emergency."
"""

from __future__ import annotations

from collections import deque
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class MachineState(Enum):
    IDLE = "IDLE"
    PENDING_CONFIRMATION = "PENDING_CONFIRMATION"
    ALERT_ACTIVE = "ALERT_ACTIVE"
    COOLDOWN = "COOLDOWN"


SAFETY_WARNING = (
    "POSSIBLE SCREAM DETECTED — REQUIRES HUMAN AUDITORY VERIFICATION. "
    "Automated acoustic alerts do not confirm an emergency."
)


class BaseTemporalPolicy:
    """Abstract base class for temporal alert policies."""

    def __init__(self, name: str, threshold: float):
        self.name = name
        self.threshold = threshold
        self.reset()

    def reset(self):
        raise NotImplementedError

    def step(self, prob: float, timestamp_sec: float) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Update state with current window probability.
        
        Returns:
            (alert_fired, alert_metadata_or_none)
        """
        raise NotImplementedError


class SingleWindowPolicy(BaseTemporalPolicy):
    """Policy P1: Instantaneous Single-Window Thresholding (Baseline).
    
    Fires an alert whenever prob >= threshold. No temporal memory or cooldown.
    """

    def __init__(self, threshold: float = 0.38):
        super().__init__("Single_Window", threshold)

    def reset(self):
        pass

    def step(self, prob: float, timestamp_sec: float) -> Tuple[bool, Optional[Dict[str, Any]]]:
        fired = bool(prob >= self.threshold)
        if fired:
            return True, {
                "policy": self.name,
                "timestamp_sec": timestamp_sec,
                "prob": prob,
                "threshold": self.threshold,
                "notice": SAFETY_WARNING,
            }
        return False, None


class ConsecutivePersistencePolicy(BaseTemporalPolicy):
    """Policy P2 / P3: Consecutive Positive Window Persistence.
    
    Fires an alert only after C consecutive windows with prob >= threshold.
    """

    def __init__(self, consecutive_required: int = 2, threshold: float = 0.38):
        name = f"Consecutive_{consecutive_required}"
        self.consecutive_required = consecutive_required
        super().__init__(name, threshold)

    def reset(self):
        self.current_streak = 0
        self.has_fired_for_current_streak = False

    def step(self, prob: float, timestamp_sec: float) -> Tuple[bool, Optional[Dict[str, Any]]]:
        if prob >= self.threshold:
            self.current_streak += 1
            if self.current_streak >= self.consecutive_required and not self.has_fired_for_current_streak:
                self.has_fired_for_current_streak = True
                return True, {
                    "policy": self.name,
                    "timestamp_sec": timestamp_sec,
                    "prob": prob,
                    "streak_length": self.current_streak,
                    "threshold": self.threshold,
                    "notice": SAFETY_WARNING,
                }
        else:
            self.current_streak = 0
            self.has_fired_for_current_streak = False
        return False, None


class VotingKofMPolicy(BaseTemporalPolicy):
    """Policy P4 / P5: k-of-m Sliding Window Voting.
    
    Maintains a FIFO queue of recent m window decisions.
    Fires an alert if at least k windows in the buffer satisfy prob >= threshold.
    """

    def __init__(self, k: int = 2, m: int = 3, threshold: float = 0.38):
        name = f"Voting_{k}_of_{m}"
        self.k = k
        self.m = m
        super().__init__(name, threshold)

    def reset(self):
        self.buffer = deque(maxlen=self.m)
        self.alert_active = False

    def step(self, prob: float, timestamp_sec: float) -> Tuple[bool, Optional[Dict[str, Any]]]:
        is_pos = (prob >= self.threshold)
        self.buffer.append(is_pos)

        positive_count = sum(self.buffer)
        if positive_count >= self.k and not self.alert_active:
            self.alert_active = True
            return True, {
                "policy": self.name,
                "timestamp_sec": timestamp_sec,
                "prob": prob,
                "positive_count": positive_count,
                "window_buffer_size": len(self.buffer),
                "threshold": self.threshold,
                "notice": SAFETY_WARNING,
            }
        elif positive_count < self.k:
            self.alert_active = False

        return False, None


class HysteresisCooldownPolicy(BaseTemporalPolicy):
    """Policy P6: Dual-Threshold Hysteresis and Temporal Cooldown Suppressor.
    
    1. High trigger threshold: tau_high
    2. Low release threshold: tau_low (e.g. 0.5 * tau_high)
    3. Hysteresis confirmation: requires 2 consecutive windows >= tau_high
    4. Cooldown window: cooldown_hops (e.g. 6 hops = 3.0s) prevents repeated alerts
       from one continuous acoustic event.
    5. Returns to IDLE after recovery_hops consecutive windows < tau_low.
    """

    def __init__(
        self,
        tau_high: float = 0.38,
        tau_low: float = 0.19,
        confirm_hops: int = 2,
        cooldown_hops: int = 6,
        recovery_hops: int = 3,
    ):
        name = "Hysteresis_Cooldown"
        self.tau_high = tau_high
        self.tau_low = tau_low
        self.confirm_hops = confirm_hops
        self.cooldown_hops = cooldown_hops
        self.recovery_hops = recovery_hops
        super().__init__(name, tau_high)

    def reset(self):
        self.state = MachineState.IDLE
        self.consecutive_high = 0
        self.consecutive_low = 0
        self.cooldown_counter = 0

    def step(self, prob: float, timestamp_sec: float) -> Tuple[bool, Optional[Dict[str, Any]]]:
        alert_fired = False
        meta = None

        if self.state == MachineState.IDLE:
            if prob >= self.tau_high:
                self.consecutive_high = 1
                if self.confirm_hops == 1:
                    self.state = MachineState.ALERT_ACTIVE
                    self.cooldown_counter = self.cooldown_hops
                    alert_fired = True
                else:
                    self.state = MachineState.PENDING_CONFIRMATION
            else:
                self.consecutive_high = 0

        elif self.state == MachineState.PENDING_CONFIRMATION:
            if prob >= self.tau_high:
                self.consecutive_high += 1
                if self.consecutive_high >= self.confirm_hops:
                    self.state = MachineState.ALERT_ACTIVE
                    self.cooldown_counter = self.cooldown_hops
                    alert_fired = True
            else:
                self.consecutive_high = 0
                self.state = MachineState.IDLE

        elif self.state == MachineState.ALERT_ACTIVE:
            # Alert is already active; decrement cooldown
            if self.cooldown_counter > 0:
                self.cooldown_counter -= 1

            if prob < self.tau_low:
                self.consecutive_low = 1
                self.state = MachineState.COOLDOWN
            else:
                self.consecutive_low = 0

        elif self.state == MachineState.COOLDOWN:
            if self.cooldown_counter > 0:
                self.cooldown_counter -= 1

            if prob < self.tau_low:
                self.consecutive_low += 1
                if self.consecutive_low >= self.recovery_hops and self.cooldown_counter == 0:
                    self.state = MachineState.IDLE
                    self.consecutive_low = 0
                    self.consecutive_high = 0
            else:
                self.consecutive_low = 0
                if prob >= self.tau_high and self.cooldown_counter == 0:
                    # New distinct event trigger
                    self.state = MachineState.ALERT_ACTIVE
                    self.cooldown_counter = self.cooldown_hops
                    alert_fired = True

        if alert_fired:
            meta = {
                "policy": self.name,
                "timestamp_sec": timestamp_sec,
                "prob": prob,
                "tau_high": self.tau_high,
                "tau_low": self.tau_low,
                "cooldown_hops": self.cooldown_hops,
                "notice": SAFETY_WARNING,
            }

        return alert_fired, meta
