"""Detector Service Layer (Stage 8).

Bridges the real-time audio detection engine (Stage 7 StreamDetector & MicrophoneCapture)
with the FastAPI REST routes and WebSocket event broadcaster.

Responsibilities:
- Manages thread-safe detector lifecycle (start, stop, device selection).
- Prevents duplicate microphone streams and handles missing audio devices gracefully.
- Runs window inference in a dedicated background worker thread to keep the API responsive.
- Buffers and bridges detection events, state transitions, and audio activity telemetry.
- Maintains operator acknowledgments and historical event retrieval from JSONL.
- Enforces strict input validation for runtime detection parameter updates.
"""

from __future__ import annotations

import asyncio
import json
import logging
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

import numpy as np

from src.alerts.alert_dispatcher import AlertDispatcher
from src.config import (
    DEFAULT_ALERT_COOLDOWN_SECONDS,
    DEFAULT_SCREAM_THRESHOLD,
    TARGET_SAMPLE_RATE,
)
from src.detector.audio_buffer import RollingAudioBuffer
from src.detector.event_logger import DEFAULT_EVENTS_LOG_FILE, DetectionEventLogger
from src.detector.mic_capture import (
    AudioDeviceError,
    MicrophoneCapture,
    list_audio_input_devices,
)
from src.detector.state_machine import (
    DetectorState,
    EventStateMachine,
    ScreamEvent,
    WindowInferenceResult,
)
from src.detector.stream_detector import StreamDetector

logger = logging.getLogger("detector_service")


class DetectorService:
    """Thread-safe singleton detector service managing streaming audio inference."""

    def __init__(
        self,
        stream_detector: Optional[StreamDetector] = None,
        log_filepath: Optional[Path] = None,
    ):
        """Initialize detector service.

        Args:
            stream_detector: Optional pre-configured StreamDetector instance.
            log_filepath: Path to detection events JSONL log.
        """
        self.log_filepath = log_filepath or DEFAULT_EVENTS_LOG_FILE
        self.event_logger = DetectionEventLogger(log_filepath=self.log_filepath)
        self.alert_dispatcher = AlertDispatcher()

        # Stream Detector Engine
        self.detector = stream_detector or StreamDetector(
            threshold=DEFAULT_SCREAM_THRESHOLD,
            cooldown_seconds=DEFAULT_ALERT_COOLDOWN_SECONDS,
            event_logger=self.event_logger,
            alert_dispatcher=self.alert_dispatcher,
        )

        # Connect alert dispatcher subscription
        self.alert_dispatcher.subscribe(self._on_alert_dispatched)

        # Microphone capture & worker thread
        self.mic: Optional[MicrophoneCapture] = None
        self._worker_thread: Optional[threading.Thread] = None
        self._is_running: bool = False
        self._start_time: Optional[float] = None
        self._selected_device_index: Optional[int] = None
        self._mic_status: str = "stopped"
        self._mic_error: Optional[str] = None

        # Operator acknowledgments cache: event_id -> record
        self._acknowledged_events: Dict[str, Dict[str, Any]] = {}

        # Thread synchronization and listeners
        self._lock = threading.Lock()
        self._listeners: Set[Callable[[Dict[str, Any]], None]] = set()
        self._async_loop: Optional[asyncio.AbstractEventLoop] = None
        self._prev_state: DetectorState = DetectorState.IDLE

        # Attach state machine completion callback
        orig_resolved = self.detector.state_machine.on_event_resolved_callback

        def _wrapped_resolved(event_dict: Dict[str, Any]) -> None:
            if orig_resolved:
                try:
                    orig_resolved(event_dict)
                except Exception as e:
                    logger.error(f"Error in original on_event_resolved_callback: {e}")
            self._broadcast_event({
                "type": "event_concluded",
                "timestamp": datetime.now().isoformat(),
                "event": event_dict,
            })

        self.detector.state_machine.on_event_resolved_callback = _wrapped_resolved

    def set_async_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Register the running asyncio event loop for thread-safe UI notifications."""
        self._async_loop = loop

    def add_listener(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Register an event listener callback."""
        with self._lock:
            self._listeners.add(callback)

    def remove_listener(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Remove a previously registered event listener callback."""
        with self._lock:
            self._listeners.discard(callback)

    def _broadcast_event(self, message: Dict[str, Any]) -> None:
        """Deliver an event message to all registered listeners."""
        with self._lock:
            callbacks = list(self._listeners)

        for cb in callbacks:
            try:
                cb(message)
            except Exception as e:
                logger.error(f"Error notifying detector listener: {e}")

    def _on_alert_dispatched(self, event_data: Dict[str, Any]) -> None:
        """Callback invoked when AlertDispatcher dispatches an alert."""
        self._broadcast_event({
            "type": "alert_triggered",
            "timestamp": datetime.now().isoformat(),
            "event": event_data,
        })

    def start(self, device_index: Optional[int] = None) -> Dict[str, Any]:
        """Start the audio detection stream and background inference worker idempotently.

        Args:
            device_index: Optional PortAudio device index for microphone capture.

        Returns:
            Dictionary with startup outcome and status details.
        """
        with self._lock:
            if self._is_running:
                logger.info("DetectorService is already running (idempotent call).")
                return {
                    "success": True,
                    "message": "Detector is already running.",
                    "status": self._get_status_locked(),
                }

            self._selected_device_index = device_index
            self._mic_error = None

            # 1. Initialize Microphone Capture
            try:
                self.mic = MicrophoneCapture(
                    on_audio_chunk=self.detector.push_audio,
                    sample_rate=TARGET_SAMPLE_RATE,
                    device_index=device_index,
                    block_duration_ms=50.0,
                )
                self.mic.start()
                self._mic_status = "active"
                logger.info(f"Microphone capture started on device index {device_index}.")
            except AudioDeviceError as e:
                self._mic_status = "unavailable"
                self._mic_error = str(e)
                logger.warning(f"Audio device error on start: {e}. Running in simulation/buffer-only mode.")
            except Exception as e:
                self._mic_status = "error"
                self._mic_error = f"Unexpected audio capture error: {e}"
                logger.error(f"Unexpected error starting microphone: {e}", exc_info=True)

            # 2. Launch background inference worker
            self._is_running = True
            self._start_time = time.time()
            self._prev_state = self.detector.state_machine.current_state

            self._worker_thread = threading.Thread(
                target=self._worker_loop,
                daemon=True,
                name="DetectorInferenceWorker",
            )
            self._worker_thread.start()

            status = self._get_status_locked()

        self._broadcast_event({
            "type": "detector_status_changed",
            "timestamp": datetime.now().isoformat(),
            "status": status,
        })

        return {
            "success": True,
            "message": "Detection engine started successfully." if self._mic_status == "active" else f"Detection engine started (Mic: {self._mic_status}).",
            "status": status,
        }

    def stop(self) -> Dict[str, Any]:
        """Gracefully stop live microphone capture and the inference worker idempotently.

        Returns:
            Dictionary with shutdown outcome and final status.
        """
        with self._lock:
            if not self._is_running:
                logger.info("DetectorService is already stopped (idempotent call).")
                return {
                    "success": True,
                    "message": "Detector is already stopped.",
                    "status": self._get_status_locked(),
                }

            self._is_running = False
            self._mic_status = "stopped"

            # Stop microphone capture
            if self.mic:
                try:
                    self.mic.stop()
                except Exception as e:
                    logger.warning(f"Error stopping microphone: {e}")
                self.mic = None

            status = self._get_status_locked()

        # Wait briefly for worker thread to exit cleanly
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=1.5)

        self._broadcast_event({
            "type": "detector_status_changed",
            "timestamp": datetime.now().isoformat(),
            "status": status,
        })

        logger.info("DetectorService stopped cleanly.")
        return {
            "success": True,
            "message": "Detection engine stopped gracefully.",
            "status": status,
        }

    def _worker_loop(self) -> None:
        """Background worker thread continuously executing window inference."""
        logger.info("Inference worker thread running.")
        last_heartbeat = time.time()

        while self._is_running:
            try:
                # Process all accumulated rolling windows
                results: List[WindowInferenceResult] = self.detector.process_available_windows()

                for r in results:
                    current_state = self.detector.state_machine.current_state

                    # Broadcast window telemetry
                    window_msg = {
                        "type": "window_update",
                        "timestamp": datetime.now().isoformat(),
                        "window_index": r.window_index,
                        "stream_time_seconds": r.stream_time_seconds,
                        "raw_probability": r.raw_probability,
                        "smoothed_probability": r.smoothed_probability,
                        "is_positive": r.is_positive,
                        "threshold": r.threshold,
                        "state": current_state.value,
                        "audio_rms": r.audio_rms,
                        "latency_ms": r.latency_ms,
                        "priors": r.yamnet_top_priors,
                    }
                    self._broadcast_event(window_msg)

                    # State transition detection
                    if current_state != self._prev_state:
                        active_evt = self.detector.state_machine.active_event
                        self._broadcast_event({
                            "type": "state_changed",
                            "timestamp": datetime.now().isoformat(),
                            "old_state": self._prev_state.value,
                            "new_state": current_state.value,
                            "event": active_evt.to_dict() if active_evt else None,
                        })
                        self._prev_state = current_state

                    # If an event is active or candidate, broadcast periodic updates
                    elif current_state in (DetectorState.ALERT_ACTIVE, DetectorState.CANDIDATE):
                        active_evt = self.detector.state_machine.active_event
                        if active_evt:
                            self._broadcast_event({
                                "type": "event_updated",
                                "timestamp": datetime.now().isoformat(),
                                "event": active_evt.to_dict(),
                            })

                # Yield CPU
                time.sleep(0.02)

                # Periodic heartbeat metrics broadcast every 5 seconds
                if time.time() - last_heartbeat >= 5.0:
                    metrics = self.get_metrics()
                    self._broadcast_event({
                        "type": "metrics_update",
                        "timestamp": datetime.now().isoformat(),
                        "metrics": metrics,
                    })
                    last_heartbeat = time.time()

            except Exception as e:
                logger.error(f"Unexpected error in inference worker loop: {e}", exc_info=True)
                time.sleep(0.1)

        logger.info("Inference worker thread terminated.")

    def push_audio(self, chunk: np.ndarray) -> int:
        """Push an audio chunk into the detector buffer (for simulation/testing)."""
        return self.detector.push_audio(chunk)

    def process_windows(self) -> List[WindowInferenceResult]:
        """Manually trigger window processing (useful in synchronous tests)."""
        return self.detector.process_available_windows()

    def _get_status_locked(self) -> Dict[str, Any]:
        """Internal helper returning current status dictionary (assumes caller holds lock)."""
        active_event = self.detector.state_machine.active_event
        uptime = round(time.time() - self._start_time, 2) if (self._is_running and self._start_time) else 0.0

        return {
            "is_running": self._is_running,
            "state": self.detector.state_machine.current_state.value,
            "mic_status": self._mic_status,
            "mic_error": self._mic_error,
            "selected_device_index": self._selected_device_index,
            "uptime_seconds": uptime,
            "threshold": self.detector.threshold,
            "cooldown_seconds": self.detector.state_machine.cooldown_seconds,
            "min_consecutive_positive": self.detector.state_machine.min_consecutive_positive,
            "smoothing_alpha": self.detector.state_machine.smoothing_alpha,
            "active_event": active_event.to_dict() if active_event else None,
            "available_devices": len(list_audio_input_devices()),
        }

    def get_status(self) -> Dict[str, Any]:
        """Get snapshot of current detector status, operational state, and configuration."""
        with self._lock:
            return self._get_status_locked()

    def get_metrics(self) -> Dict[str, Any]:
        """Retrieve real window latency, count, throughput, and error metrics."""
        metrics = self.detector.get_metrics()
        with self._lock:
            uptime = round(time.time() - self._start_time, 2) if (self._is_running and self._start_time) else 0.0
            ack_count = len(self._acknowledged_events)

        return {
            **metrics,
            "session_uptime_seconds": uptime,
            "acknowledged_events_count": ack_count,
        }

    def get_config(self) -> Dict[str, Any]:
        """Get currently configured runtime detection parameters."""
        return {
            "threshold": self.detector.threshold,
            "cooldown_seconds": self.detector.state_machine.cooldown_seconds,
            "min_consecutive_positive": self.detector.state_machine.min_consecutive_positive,
            "smoothing_alpha": self.detector.state_machine.smoothing_alpha,
            "max_gap_negative_windows": self.detector.state_machine.max_gap_negative_windows,
            "opt_in_recording": self.event_logger.opt_in_raw_audio_saving,
        }

    def update_config(
        self,
        threshold: Optional[float] = None,
        cooldown_seconds: Optional[float] = None,
        min_consecutive_positive: Optional[int] = None,
        smoothing_alpha: Optional[float] = None,
        max_gap_negative_windows: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Validate and apply runtime configuration updates safely.

        Args:
            threshold: Scream classification threshold (0.01 - 0.99).
            cooldown_seconds: Alert cooldown in seconds (0.5 - 60.0).
            min_consecutive_positive: Windows needed to trigger alert (1 - 10).
            smoothing_alpha: Exponential smoothing factor (0.05 - 1.0).
            max_gap_negative_windows: Allowed negative window gap (1 - 10).

        Returns:
            Updated configuration dictionary.

        Raises:
            ValueError: If any parameter falls outside safe valid boundaries.
        """
        updates: Dict[str, Any] = {}

        if threshold is not None:
            if not (0.01 <= threshold <= 0.99):
                raise ValueError("Threshold must be between 0.01 and 0.99.")
            self.detector.threshold = float(threshold)
            self.detector.state_machine.threshold = float(threshold)
            updates["threshold"] = float(threshold)

        if cooldown_seconds is not None:
            if not (0.5 <= cooldown_seconds <= 60.0):
                raise ValueError("Cooldown must be between 0.5 and 60.0 seconds.")
            self.detector.state_machine.cooldown_seconds = float(cooldown_seconds)
            updates["cooldown_seconds"] = float(cooldown_seconds)

        if min_consecutive_positive is not None:
            if not (1 <= min_consecutive_positive <= 10):
                raise ValueError("min_consecutive_positive must be between 1 and 10.")
            self.detector.state_machine.min_consecutive_positive = int(min_consecutive_positive)
            updates["min_consecutive_positive"] = int(min_consecutive_positive)

        if smoothing_alpha is not None:
            if not (0.05 <= smoothing_alpha <= 1.0):
                raise ValueError("smoothing_alpha must be between 0.05 and 1.0.")
            self.detector.state_machine.smoothing_alpha = float(smoothing_alpha)
            updates["smoothing_alpha"] = float(smoothing_alpha)

        if max_gap_negative_windows is not None:
            if not (1 <= max_gap_negative_windows <= 10):
                raise ValueError("max_gap_negative_windows must be between 1 and 10.")
            self.detector.state_machine.max_gap_negative_windows = int(max_gap_negative_windows)
            updates["max_gap_negative_windows"] = int(max_gap_negative_windows)

        current_cfg = self.get_config()
        self._broadcast_event({
            "type": "config_updated",
            "timestamp": datetime.now().isoformat(),
            "config": current_cfg,
        })

        logger.info(f"Updated detection config: {updates}")
        return current_cfg

    def acknowledge_event(self, event_id: str, operator_note: Optional[str] = None) -> Dict[str, Any]:
        """Record an operator acknowledgment for an event.

        Args:
            event_id: Unique event identifier.
            operator_note: Optional note from the venue operator.

        Returns:
            Acknowledgment record dictionary.
        """
        with self._lock:
            record = {
                "event_id": event_id,
                "acknowledged": True,
                "acknowledged_at": datetime.now().isoformat(),
                "operator_note": operator_note or "Acknowledged by operator",
            }
            self._acknowledged_events[event_id] = record

        self._broadcast_event({
            "type": "event_acknowledged",
            "timestamp": datetime.now().isoformat(),
            "acknowledgment": record,
        })

        logger.info(f"Operator acknowledged event {event_id}: {record['operator_note']}")
        return record

    def get_events(
        self,
        limit: int = 50,
        offset: int = 0,
        event_status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Retrieve paginated persisted events from detection_events.jsonl.

        Merges operator acknowledgments into historical records.
        """
        events_by_id: Dict[str, Dict[str, Any]] = {}

        if self.log_filepath.exists():
            try:
                with open(self.log_filepath, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            record = json.loads(line)
                            evt_id = record.get("event_id")
                            if not evt_id:
                                continue

                            # If seen, merge updates
                            if evt_id in events_by_id:
                                existing = events_by_id[evt_id]
                                existing.update(record)
                                # Keep earliest start time, latest end time, max peak prob
                                existing["peak_probability"] = max(
                                    existing.get("peak_probability", 0.0),
                                    record.get("peak_probability", 0.0),
                                )
                            else:
                                events_by_id[evt_id] = record
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                logger.error(f"Error reading events log {self.log_filepath}: {e}")

        # Merge in-memory acknowledged status
        with self._lock:
            for evt_id, ack in self._acknowledged_events.items():
                if evt_id in events_by_id:
                    events_by_id[evt_id]["acknowledged"] = True
                    events_by_id[evt_id]["acknowledged_at"] = ack["acknowledged_at"]
                    events_by_id[evt_id]["operator_note"] = ack["operator_note"]

        all_events = list(events_by_id.values())

        # Sort newest first based on start_wall_time_iso or logged_at_iso
        all_events.sort(
            key=lambda x: x.get("start_wall_time_iso") or x.get("logged_at_iso") or "",
            reverse=True,
        )

        # Filter by status if specified
        if event_status:
            all_events = [e for e in all_events if e.get("event_status") == event_status]

        total = len(all_events)
        paginated = all_events[offset : offset + limit]

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "events": paginated,
        }


# Global singleton instance
_GLOBAL_DETECTOR_SERVICE: Optional[DetectorService] = None
_GLOBAL_LOCK = threading.Lock()


def get_detector_service() -> DetectorService:
    """Retrieve or initialize the global DetectorService singleton."""
    global _GLOBAL_DETECTOR_SERVICE
    with _GLOBAL_LOCK:
        if _GLOBAL_DETECTOR_SERVICE is None:
            _GLOBAL_DETECTOR_SERVICE = DetectorService()
        return _GLOBAL_DETECTOR_SERVICE


def reset_detector_service(new_service: Optional[DetectorService] = None) -> None:
    """Reset the global detector service (primarily for testing isolation)."""
    global _GLOBAL_DETECTOR_SERVICE
    with _GLOBAL_LOCK:
        if _GLOBAL_DETECTOR_SERVICE and _GLOBAL_DETECTOR_SERVICE._is_running:
            _GLOBAL_DETECTOR_SERVICE.stop()
        _GLOBAL_DETECTOR_SERVICE = new_service
