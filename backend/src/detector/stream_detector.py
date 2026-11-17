"""Modular Streaming Scream Detection Engine (Stage 7).

Orchestrates:
1. Thread-safe rolling audio buffering (16 kHz mono float32).
2. Rolling-window extraction (0.975s window with 0.4875s hop).
3. Pretrained frozen YAMNet embedding extraction & Stage 5 classifier inference.
4. Temporal smoothing and explicit state machine event lifecycle.
5. Structured JSON Lines event logging and local alert dispatch.
6. Execution latency tracking, window counting, and dropped-sample auditing.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

from src.alerts.alert_dispatcher import AlertDispatcher
from src.config import (
    DEFAULT_ALERT_COOLDOWN_SECONDS,
    DEFAULT_SCREAM_THRESHOLD,
    TARGET_SAMPLE_RATE,
    YAMNet_FRAME_SECONDS,
    YAMNet_HOP_SECONDS,
)
from src.detector.audio_buffer import BufferUnderrunError, RollingAudioBuffer
from src.detector.event_logger import DetectionEventLogger
from src.detector.state_machine import (
    DetectorState,
    EventStateMachine,
    ScreamEvent,
    WindowInferenceResult,
)
from src.model.scream_classifier import FestivalScreamClassifier
from src.model.yamnet_loader import YAMNetLoader

logger = logging.getLogger("stream_detector")


class StreamDetector:
    """Production modular streaming scream detection engine."""

    def __init__(
        self,
        sample_rate: int = TARGET_SAMPLE_RATE,
        window_duration_seconds: float = YAMNet_FRAME_SECONDS,  # 0.975s (15,600 samples)
        hop_duration_seconds: float = YAMNet_HOP_SECONDS,      # 0.4875s (7,800 samples)
        threshold: float = 0.35,  # Stage 5 validation-selected threshold
        min_consecutive_positive: int = 2,
        max_gap_negative_windows: int = 2,
        cooldown_seconds: float = DEFAULT_ALERT_COOLDOWN_SECONDS,
        smoothing_alpha: float = 0.6,
        classifier: Optional[FestivalScreamClassifier] = None,
        yamnet_loader: Optional[YAMNetLoader] = None,
        event_logger: Optional[DetectionEventLogger] = None,
        alert_dispatcher: Optional[AlertDispatcher] = None,
        prediction_fn_override: Optional[Callable[[np.ndarray], Tuple[float, List[Dict[str, Any]]]]] = None,
        max_buffer_seconds: float = 15.0,
    ):
        """Initialize streaming scream detector with configurable parameters.

        Args:
            sample_rate: Input sample rate in Hz (default: 16,000 Hz).
            window_duration_seconds: Duration of rolling window in seconds (default: 0.975s).
            hop_duration_seconds: Step size between consecutive windows (default: 0.4875s).
            threshold: Probability threshold for positive classification (default: 0.35).
            min_consecutive_positive: Consecutive positive windows required to emit an alert (default: 2).
            max_gap_negative_windows: Negative windows before an active event ends (default: 2).
            cooldown_seconds: Minimum cooldown duration in seconds to suppress duplicate alerts (default: 3.0s).
            smoothing_alpha: EMA smoothing coefficient (default: 0.6).
            classifier: Loaded FestivalScreamClassifier instance.
            yamnet_loader: Loaded YAMNetLoader instance.
            event_logger: DetectionEventLogger instance.
            alert_dispatcher: AlertDispatcher instance.
            prediction_fn_override: Optional custom predictor for unit testing without hardware/TF.
            max_buffer_seconds: Maximum rolling audio buffer capacity in seconds.
        """
        self.sample_rate = int(sample_rate)
        self.window_duration_seconds = float(window_duration_seconds)
        self.hop_duration_seconds = float(hop_duration_seconds)
        self.threshold = float(threshold)

        self.window_samples = int(round(self.window_duration_seconds * self.sample_rate))
        self.hop_samples = int(round(self.hop_duration_seconds * self.sample_rate))

        # Audio Buffer
        self.buffer = RollingAudioBuffer(
            sample_rate=self.sample_rate,
            max_duration_seconds=max_buffer_seconds,
        )

        # Alerts and Logging
        self.alert_dispatcher = alert_dispatcher or AlertDispatcher()
        self.event_logger = event_logger or DetectionEventLogger()

        # State Machine
        self.state_machine = EventStateMachine(
            threshold=self.threshold,
            min_consecutive_positive=min_consecutive_positive,
            max_gap_negative_windows=max_gap_negative_windows,
            cooldown_seconds=cooldown_seconds,
            smoothing_alpha=smoothing_alpha,
            on_alert_callback=self._handle_alert_triggered,
            on_event_resolved_callback=self._handle_event_resolved,
        )

        # ML Inference Pipeline
        self.prediction_fn_override = prediction_fn_override
        self._classifier = classifier
        self._yamnet_loader = yamnet_loader

        # Stream Progress Tracking
        self._current_sample_offset: int = 0
        self._window_index: int = 0
        self._is_running: bool = False

        # Latency & Throughput Metrics
        self._latencies_ms: List[float] = []
        self._inference_errors: int = 0
        self._dropped_windows: int = 0

    def _ensure_models_loaded(self) -> None:
        """Lazy load classifier and YAMNet models if not using mock override."""
        if self.prediction_fn_override is not None:
            return

        if self._classifier is None:
            self._classifier = FestivalScreamClassifier()
            if not self._classifier.is_loaded:
                self._classifier.load()

        if self._yamnet_loader is None:
            self._yamnet_loader = YAMNetLoader()
            self._yamnet_loader.load()

    def _handle_alert_triggered(self, event_data: Dict[str, Any]) -> None:
        """Callback executed when state machine transitions to ALERT_ACTIVE."""
        # Dispatch to console & subscribers
        self.alert_dispatcher.dispatch_alert(event_data)
        # Log structured event
        self.event_logger.log_event({**event_data, "event_status": "alert_triggered"})

    def _handle_event_resolved(self, event_data: Dict[str, Any]) -> None:
        """Callback executed when an event concludes and enters cooldown."""
        self.event_logger.log_event({**event_data, "event_status": "event_concluded"})

    def push_audio(self, chunk: np.ndarray) -> int:
        """Ingest incoming audio samples into the rolling buffer.

        Args:
            chunk: 1D or 2D audio array.

        Returns:
            Number of samples written.
        """
        return self.buffer.write(chunk)

    def process_available_windows(self) -> List[WindowInferenceResult]:
        """Process all complete audio windows currently accumulated in the buffer.

        Returns:
            List of WindowInferenceResult for each window evaluated in this step.
        """
        self._ensure_models_loaded()
        results: List[WindowInferenceResult] = []

        while self.buffer.has_window(self.window_samples, self._current_sample_offset):
            try:
                window_audio = self.buffer.get_window(self.window_samples, self._current_sample_offset)
            except BufferUnderrunError as e:
                # Buffer overflow skipped unread samples; catch up to oldest available
                self._dropped_windows += 1
                logger.warning(f"Audio buffer underrun: {e}. Skipping to newest available offset.")
                oldest_safe = max(0, self.buffer.total_samples_written - self.buffer.max_capacity_samples)
                self._current_sample_offset = oldest_safe
                self.event_logger.log_audio_gap(
                    stream_time_seconds=self._current_sample_offset / self.sample_rate,
                    gap_duration_seconds=self.hop_duration_seconds,
                    reason="Buffer overflow caught up",
                )
                continue

            if window_audio is None:
                break

            stream_time = self._current_sample_offset / self.sample_rate
            self._window_index += 1

            # Execute Model Inference with Latency Timing
            t0 = time.perf_counter()
            try:
                if self.prediction_fn_override is not None:
                    prob_scream, priors = self.prediction_fn_override(window_audio)
                else:
                    assert self._yamnet_loader is not None
                    assert self._classifier is not None

                    # Extract YAMNet frame embeddings
                    scores, embeddings, _ = self._yamnet_loader.infer(window_audio)
                    # Pool embeddings to expected dimension (max_pooled 1024-dim)
                    pooled_features = self._classifier.pool_frame_embeddings(embeddings)
                    # Run classifier pipeline
                    pred = self._classifier.predict_features(pooled_features, custom_threshold=self.threshold)
                    prob_scream = pred["scream_probability"]

                    # Extract top AudioSet priors for context
                    mean_scores = np.mean(scores, axis=0)
                    top_indices = np.argsort(mean_scores)[::-1][:3]
                    priors = [
                        {"class_name": self._yamnet_loader.class_names[idx], "score": round(float(mean_scores[idx]), 4)}
                        for idx in top_indices
                    ]

                latency_ms = (time.perf_counter() - t0) * 1000.0
                self._latencies_ms.append(latency_ms)

                # Real window RMS audio activity
                window_rms = float(np.sqrt(np.mean(window_audio ** 2))) if len(window_audio) > 0 else 0.0

                # Feed probability into State Machine
                win_res = self.state_machine.process_window(
                    raw_probability=prob_scream,
                    stream_time_seconds=stream_time,
                    window_index=self._window_index,
                    yamnet_top_priors=priors,
                    latency_ms=latency_ms,
                    audio_rms=window_rms,
                )
                results.append(win_res)

            except Exception as e:
                latency_ms = (time.perf_counter() - t0) * 1000.0
                self._inference_errors += 1
                logger.error(f"Inference error on window {self._window_index} at {stream_time:.2f}s: {e}", exc_info=True)
                self.state_machine.reset()
                self.event_logger.log_audio_gap(
                    stream_time_seconds=stream_time,
                    gap_duration_seconds=self.window_duration_seconds,
                    reason=f"Inference exception: {e}",
                )

            # Advance by hop step
            self._current_sample_offset += self.hop_samples

        return results

    def reset(self) -> None:
        """Reset internal buffer, state machine, and stream offsets."""
        self.buffer.clear()
        self.state_machine.reset()
        self._current_sample_offset = 0
        self._window_index = 0
        self._latencies_ms.clear()
        self._inference_errors = 0
        self._dropped_windows = 0

    def get_metrics(self) -> Dict[str, Any]:
        """Compute performance, throughput, and latency summary metrics."""
        latencies = self._latencies_ms
        avg_lat = float(np.mean(latencies)) if latencies else 0.0
        min_lat = float(np.min(latencies)) if latencies else 0.0
        max_lat = float(np.max(latencies)) if latencies else 0.0
        p95_lat = float(np.percentile(latencies, 95)) if latencies else 0.0

        total_audio_sec = self._current_sample_offset / self.sample_rate

        return {
            "windows_processed": self._window_index,
            "total_audio_seconds": round(total_audio_sec, 3),
            "total_alerts_emitted": self.state_machine.total_alerts_emitted,
            "total_alerts_suppressed": self.state_machine.total_alerts_suppressed,
            "inference_errors": self._inference_errors,
            "dropped_windows": self._dropped_windows,
            "dropped_samples": self.buffer.dropped_samples,
            "latency_metrics_ms": {
                "mean": round(avg_lat, 2),
                "min": round(min_lat, 2),
                "max": round(max_lat, 2),
                "p95": round(p95_lat, 2),
                "samples_timed": len(latencies),
            },
            "hop_duration_ms": round(self.hop_duration_seconds * 1000.0, 1),
            "realtime_factor": round(avg_lat / (self.hop_duration_seconds * 1000.0), 4) if self.hop_duration_seconds > 0 else 0.0,
        }
