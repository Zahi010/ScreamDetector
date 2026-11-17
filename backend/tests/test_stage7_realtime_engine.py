"""Unit and Integration Tests for Stage 7 Real-Time Streaming Detection Engine.

Validates:
1. RollingAudioBuffer bounds, circular overwrites, and partial buffer handling.
2. EventStateMachine state transitions (IDLE -> CANDIDATE -> ALERT_ACTIVE -> COOLDOWN -> IDLE).
3. Temporal smoothing and consecutive-window alert requirements.
4. Cooldown suppression of duplicate alarms and re-enabling alerts after cooldown.
5. Injected mock predictor for deterministic testing without TensorFlow/mic hardware.
6. DetectionEventLogger JSON Lines schema, serialization, and privacy compliance.
7. StreamDetector window latency tracking, error recovery, and clean shutdown.
8. Stage 5 baseline artifact immutability verification.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pytest

from src.audio.preprocessor import generate_synthetic_chirp, generate_synthetic_tone
from src.config import MODELS_DIR, REPORTS_DIR, TARGET_SAMPLE_RATE
from src.detector import (
    BufferUnderrunError,
    DetectionEventLogger,
    DetectorState,
    EventStateMachine,
    RollingAudioBuffer,
    StreamDetector,
)

# Immutable Stage 5 baseline hashes
STAGE5_BASELINE_HASHES = {
    "scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "scream_classifier_v1.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
}


def test_stage5_baseline_remains_strictly_unchanged():
    """Verify that Stage 5 model artifacts and metadata have not been altered in Stage 7."""
    for filename, expected_sha in STAGE5_BASELINE_HASHES.items():
        filepath = MODELS_DIR / filename
        assert filepath.exists(), f"Missing Stage 5 file: {filepath}"
        with open(filepath, "rb") as f:
            actual_sha = hashlib.sha256(f.read()).hexdigest()
        assert actual_sha == expected_sha, f"Stage 5 artifact {filename} was mutated!"


def test_rolling_audio_buffer_bounds_and_partial_handling():
    """Test buffer write, capacity bounds, and partial buffer protection."""
    sr = 16000
    buf = RollingAudioBuffer(sample_rate=sr, max_duration_seconds=2.0)  # capacity = 32,000 samples

    # 1. Partial buffer: writing 8,000 samples (< window of 15,600 samples)
    chunk1 = np.ones(8000, dtype=np.float32)
    buf.write(chunk1)
    assert buf.buffered_samples == 8000
    assert buf.total_samples_written == 8000
    assert buf.has_window(15600, start_offset=0) is False
    assert buf.get_window(15600, start_offset=0) is None

    # 2. Writing second chunk: total 16,000 samples (>= 15,600)
    chunk2 = np.ones(8000, dtype=np.float32) * 2.0
    buf.write(chunk2)
    assert buf.buffered_samples == 16000
    assert buf.has_window(15600, start_offset=0) is True

    window = buf.get_window(15600, start_offset=0)
    assert window is not None
    assert len(window) == 15600
    assert window[0] == 1.0
    assert window[7999] == 1.0
    assert window[8000] == 2.0

    # 3. Buffer capacity capping (write 25,000 samples to push total to 41,000 > 32,000 capacity)
    chunk3 = np.ones(25000, dtype=np.float32) * 3.0
    buf.write(chunk3)
    assert buf.buffered_samples == 32000
    assert buf.total_samples_written == 41000
    assert buf.dropped_samples == 9000  # 41,000 - 32,000

    # Requesting expired offset raises BufferUnderrunError
    with pytest.raises(BufferUnderrunError):
        buf.get_window(15600, start_offset=0)


def test_state_machine_temporal_smoothing_and_transitions():
    """Test state machine progression: IDLE -> CANDIDATE -> ALERT_ACTIVE -> COOLDOWN -> IDLE."""
    alerts_received: List[Dict[str, Any]] = []
    events_resolved: List[Dict[str, Any]] = []

    sm = EventStateMachine(
        threshold=0.35,
        min_consecutive_positive=2,
        max_gap_negative_windows=2,
        cooldown_seconds=1.0,
        smoothing_alpha=0.6,
        on_alert_callback=lambda evt: alerts_received.append(evt),
        on_event_resolved_callback=lambda evt: events_resolved.append(evt),
    )

    assert sm.current_state == DetectorState.IDLE

    # Window 1: Low score -> stays IDLE
    res1 = sm.process_window(raw_probability=0.10, stream_time_seconds=0.0, window_index=1)
    assert sm.current_state == DetectorState.IDLE
    assert res1.is_positive is False

    # Window 2: Single positive score -> transitions to CANDIDATE (alert NOT yet triggered)
    res2 = sm.process_window(raw_probability=0.85, stream_time_seconds=0.4875, window_index=2)
    assert sm.current_state == DetectorState.CANDIDATE
    assert len(alerts_received) == 0

    # Window 3: Broken streak (negative window) -> drops back to IDLE
    res3 = sm.process_window(raw_probability=0.20, stream_time_seconds=0.975, window_index=3)
    assert sm.current_state == DetectorState.IDLE
    assert len(alerts_received) == 0

    # Window 4: First positive window -> CANDIDATE
    sm.process_window(raw_probability=0.90, stream_time_seconds=1.4625, window_index=4)
    assert sm.current_state == DetectorState.CANDIDATE

    # Window 5: Second consecutive positive window -> ALERT_ACTIVE (Alert emitted!)
    sm.process_window(raw_probability=0.95, stream_time_seconds=1.95, window_index=5)
    assert sm.current_state == DetectorState.ALERT_ACTIVE
    assert len(alerts_received) == 1
    assert alerts_received[0]["alert_emitted"] is True
    assert alerts_received[0]["peak_probability"] == pytest.approx(0.95, abs=0.01)

    # Window 6: Continued positive window -> stays ALERT_ACTIVE, NO duplicate alert
    sm.process_window(raw_probability=0.88, stream_time_seconds=2.4375, window_index=6)
    assert sm.current_state == DetectorState.ALERT_ACTIVE
    assert len(alerts_received) == 1  # Exactly ONE alert emitted

    # Window 7: First negative window -> still ALERT_ACTIVE (gap allowed)
    sm.process_window(raw_probability=0.15, stream_time_seconds=2.925, window_index=7)
    assert sm.current_state == DetectorState.ALERT_ACTIVE

    # Window 8: Second negative window (max_gap reached) -> transitions to COOLDOWN
    sm.process_window(raw_probability=0.10, stream_time_seconds=3.4125, window_index=8)
    assert sm.current_state == DetectorState.COOLDOWN
    assert len(events_resolved) == 1


def test_cooldown_suppression_and_rearm():
    """Verify that alerts are suppressed during cooldown, and re-armed after cooldown expires."""
    alerts_received: List[Dict[str, Any]] = []

    sm = EventStateMachine(
        threshold=0.35,
        min_consecutive_positive=1,  # 1 window triggers immediately for test brevity
        max_gap_negative_windows=1,
        cooldown_seconds=2.0,
        on_alert_callback=lambda evt: alerts_received.append(evt),
    )

    # Trigger event 1
    sm.process_window(raw_probability=0.90, stream_time_seconds=1.0, window_index=1)
    assert sm.current_state == DetectorState.ALERT_ACTIVE
    assert len(alerts_received) == 1

    # End event 1 at 1.5s -> enters COOLDOWN until 3.5s (1.5 + 2.0s)
    sm.process_window(raw_probability=0.10, stream_time_seconds=1.5, window_index=2)
    assert sm.current_state == DetectorState.COOLDOWN

    # Window during cooldown (at 2.0s < 3.5s): positive score is suppressed
    sm.process_window(raw_probability=0.95, stream_time_seconds=2.0, window_index=3)
    assert sm.current_state == DetectorState.COOLDOWN
    assert len(alerts_received) == 1  # Suppressed!
    assert sm.total_alerts_suppressed == 1

    # Window at 3.6s (> 3.5s): cooldown expired! Clean negative window returns to IDLE
    sm.process_window(raw_probability=0.10, stream_time_seconds=3.6, window_index=4)
    assert sm.current_state == DetectorState.IDLE

    # Window at 4.0s: Fresh scream event qualifies for a NEW alert!
    sm.process_window(raw_probability=0.92, stream_time_seconds=4.0, window_index=5)
    assert sm.current_state == DetectorState.ALERT_ACTIVE
    assert len(alerts_received) == 2  # Fresh alert emitted!


def test_detection_event_logger_jsonl(tmp_path: Path):
    """Test JSON Lines structured event logging and privacy compliance."""
    log_file = tmp_path / "test_events.jsonl"
    event_logger = DetectionEventLogger(log_filepath=log_file, opt_in_raw_audio_saving=False)

    mock_event = {
        "event_id": "evt_test_123",
        "start_stream_time": 1.25,
        "end_stream_time": 2.75,
        "duration_seconds": 1.50,
        "peak_probability": 0.942,
        "threshold": 0.35,
        "window_count": 3,
        "positive_window_count": 3,
        "alert_emitted": True,
        "suppressed_during_cooldown": False,
        "top_priors": [{"class_name": "Dog", "score": 0.45}],
    }

    event_logger.log_event(mock_event)
    assert log_file.exists()

    with open(log_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    assert len(lines) == 1
    logged_record = json.loads(lines[0])

    assert logged_record["event_id"] == "evt_test_123"
    assert logged_record["peak_probability"] == 0.942
    assert logged_record["raw_audio_saved"] is False  # Privacy verification
    assert "logged_at_iso" in logged_record


def test_stream_detector_with_mock_prediction_fn(tmp_path: Path):
    """Test end-to-end StreamDetector streaming pipeline with injected deterministic predictor."""
    # Custom deterministic mock predictor: returns high probability only if input mean > 0.5
    def mock_predictor(audio: np.ndarray) -> Tuple[float, List[Dict[str, Any]]]:
        mean_val = float(np.mean(np.abs(audio)))
        prob = 0.95 if mean_val > 0.4 else 0.05
        priors = [{"class_name": "MockClass", "score": prob}]
        return prob, priors

    log_file = tmp_path / "stream_events.jsonl"
    logger_instance = DetectionEventLogger(log_filepath=log_file)

    detector = StreamDetector(
        sample_rate=16000,
        window_duration_seconds=1.0,  # 16,000 samples
        hop_duration_seconds=0.5,      # 8,000 samples
        threshold=0.35,
        min_consecutive_positive=2,
        prediction_fn_override=mock_predictor,
        event_logger=logger_instance,
    )

    # 1. Push 1.0 second of silence (zeros)
    silence = np.zeros(16000, dtype=np.float32)
    detector.push_audio(silence)
    results1 = detector.process_available_windows()
    assert len(results1) == 1
    assert results1[0].is_positive is False
    assert detector.state_machine.current_state == DetectorState.IDLE

    # 2. Push 2.0 seconds of high-amplitude signal (mean > 0.5)
    high_signal = np.ones(32000, dtype=np.float32)
    detector.push_audio(high_signal)
    results2 = detector.process_available_windows()
    assert len(results2) == 4  # 4 overlapping windows evaluated

    # Verification: consecutive positive windows triggered alert
    assert detector.state_machine.total_alerts_emitted == 1
    metrics = detector.get_metrics()
    assert metrics["windows_processed"] == 5
    assert metrics["total_alerts_emitted"] == 1
    assert metrics["latency_metrics_ms"]["samples_timed"] == 5


def test_stream_detector_exception_recovery():
    """Verify that inference exceptions do not crash the detector or corrupt state."""
    call_count = 0

    def flaky_predictor(audio: np.ndarray) -> Tuple[float, List[Dict[str, Any]]]:
        nonlocal call_count
        call_count += 1
        if call_count == 2:
            raise RuntimeError("Simulated transient inference fault")
        return 0.10, []

    detector = StreamDetector(
        sample_rate=16000,
        window_duration_seconds=1.0,
        hop_duration_seconds=0.5,
        prediction_fn_override=flaky_predictor,
    )

    # Feed 2.0 seconds (3 windows)
    detector.push_audio(np.zeros(32000, dtype=np.float32))
    results = detector.process_available_windows()

    # Window 1 succeeded, Window 2 failed cleanly (caught and logged), Window 3 succeeded
    assert len(results) == 2
    assert detector._inference_errors == 1
    assert detector.state_machine.current_state == DetectorState.IDLE
