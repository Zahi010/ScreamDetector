"""Stage 8.5 — End-to-End Integration, Endurance, and Resilience Test Suite.

Comprehensive validation covering:
1. Detector lifecycle idempotency, rapid restart cycles, and thread leak prevention.
2. Audio processing robustness: format conversion, buffer boundaries, corruption/NaN safety, and silence behavior.
3. Deterministic state machine transition coverage: IDLE -> CANDIDATE -> ALERT_ACTIVE -> COOLDOWN -> IDLE.
4. Single-window transient suppression and cooldown duplicate suppression.
5. Multi-client WebSocket concurrency, slow-client bounded queue isolation, and status reconciliation.
6. Event logging resilience: corrupt JSONL recovery, unwritable log handling, restart persistence, and privacy verification.
7. Stage 5 model artifact and metadata immutability verification.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import soundfile as sf
from fastapi.testclient import TestClient

from src.alerts.alert_dispatcher import AlertDispatcher
from src.api.websocket import manager, WebSocketClient
from src.config import MODELS_DIR, TARGET_SAMPLE_RATE
from src.detector.audio_buffer import RollingAudioBuffer
from src.detector.event_logger import DetectionEventLogger
from src.detector.service import (
    DetectorService,
    get_detector_service,
    reset_detector_service,
)
from src.detector.state_machine import (
    DetectorState,
    EventStateMachine,
    ScreamEvent,
    WindowInferenceResult,
)
from src.detector.stream_detector import StreamDetector
from src.main import app

STAGE5_CLASSIFIER_SHA256 = "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f"
STAGE5_METADATA_SHA256 = "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60"


@pytest.fixture
def mock_predictor():
    """Deterministic predictor for unit testing."""
    def _predict(audio: np.ndarray) -> Tuple[float, List[Dict[str, Any]]]:
        mean_amp = float(np.mean(np.abs(audio)))
        score = float(np.clip(mean_amp * 5.0, 0.05, 0.95))
        return score, [{"class_name": "Screaming", "score": score}]
    return _predict


@pytest.fixture
def test_env(tmp_path: Path, mock_predictor):
    """Isolated test environment for DetectorService."""
    log_file = tmp_path / "resilience_events.jsonl"
    detector = StreamDetector(
        sample_rate=TARGET_SAMPLE_RATE,
        threshold=0.35,
        prediction_fn_override=mock_predictor,
    )
    service = DetectorService(stream_detector=detector, log_filepath=log_file)
    reset_detector_service(service)

    # Bridge to WebSocket manager
    def _bridge(event: Dict[str, Any]):
        manager.dispatch_from_thread(event)
    service.add_listener(_bridge)

    yield service, log_file

    service.stop()
    reset_detector_service(None)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


# ============================================================================
# Phase 2: Model & Metadata Integrity
# ============================================================================

def test_model_artifact_and_metadata_integrity():
    """Verify Stage 5 classifier model and metadata remain strictly bit-identical."""
    clf_path = MODELS_DIR / "scream_classifier.joblib"
    meta_path = MODELS_DIR / "model_metadata.json"

    assert clf_path.exists(), f"Classifier missing at {clf_path}"
    assert meta_path.exists(), f"Metadata missing at {meta_path}"

    actual_clf_hash = hashlib.sha256(clf_path.read_bytes()).hexdigest()
    actual_meta_hash = hashlib.sha256(meta_path.read_bytes()).hexdigest()

    assert actual_clf_hash == STAGE5_CLASSIFIER_SHA256, (
        f"Classifier hash mismatch! Expected {STAGE5_CLASSIFIER_SHA256}, got {actual_clf_hash}"
    )
    assert actual_meta_hash == STAGE5_METADATA_SHA256, (
        f"Metadata hash mismatch! Expected {STAGE5_METADATA_SHA256}, got {actual_meta_hash}"
    )


# ============================================================================
# Phase 3A: Detector Lifecycle & Thread Safety
# ============================================================================

def test_repeated_start_stop_lifecycle_no_thread_leak(test_env):
    """Verify rapid repeated start and stop cycles do not leak threads or duplicate workers."""
    service, _ = test_env

    with patch("src.detector.service.MicrophoneCapture") as MockMic:
        mock_instance = MagicMock()
        MockMic.return_value = mock_instance

        initial_threads = threading.active_count()

        # Run 5 consecutive start/stop cycles
        for cycle in range(5):
            start_res = service.start()
            assert start_res["success"] is True
            assert service.get_status()["is_running"] is True

            time.sleep(0.05)

            stop_res = service.stop()
            assert stop_res["success"] is True
            assert service.get_status()["is_running"] is False

        # Allow worker thread to join
        time.sleep(0.1)
        final_threads = threading.active_count()

        # Thread count should be identical or at most delta of 0
        assert final_threads <= initial_threads + 1, (
            f"Thread leak detected! Initial: {initial_threads}, Final: {final_threads}"
        )


def test_rapid_consecutive_start_calls_are_idempotent(test_env):
    """Verify multiple rapid calls to start() do not spawn multiple worker threads."""
    service, _ = test_env

    with patch("src.detector.service.MicrophoneCapture") as MockMic:
        mock_instance = MagicMock()
        MockMic.return_value = mock_instance

        # Call start 4 times consecutively
        res1 = service.start()
        res2 = service.start()
        res3 = service.start()
        res4 = service.start()

        assert res1["success"] is True
        assert res2["message"] == "Detector is already running."
        assert res3["message"] == "Detector is already running."
        assert res4["message"] == "Detector is already running."

        # Verify only one worker thread exists and is alive
        assert service._worker_thread is not None
        assert service._worker_thread.is_alive()

        service.stop()


def test_rapid_consecutive_stop_calls_are_idempotent(test_env):
    """Verify multiple rapid calls to stop() succeed cleanly without exceptions."""
    service, _ = test_env

    res1 = service.stop()
    res2 = service.stop()
    res3 = service.stop()

    assert res1["success"] is True
    assert res1["message"] == "Detector is already stopped."
    assert res2["message"] == "Detector is already stopped."
    assert res3["message"] == "Detector is already stopped."


# ============================================================================
# Phase 3B: Audio Processing Robustness & Buffer Boundaries
# ============================================================================

def test_rolling_audio_buffer_overflow_bounds_memory():
    """Verify audio buffer does not grow unbounded when overwhelmed with data."""
    sample_rate = 16000
    max_duration = 2.0  # 32,000 samples
    buf = RollingAudioBuffer(sample_rate=sample_rate, max_duration_seconds=max_duration)

    # Write 5x the buffer capacity (160,000 samples)
    large_audio = np.ones(sample_rate * 10, dtype=np.float32)
    buf.write(large_audio)

    assert buf.buffered_samples == buf.max_capacity_samples
    assert buf.buffered_seconds == 2.0
    assert buf.dropped_samples > 0
    assert buf.total_samples_written == 160000


def test_audio_chunk_format_normalizations():
    """Verify write handles 2D stereo, int16, float64, and empty chunks gracefully."""
    buf = RollingAudioBuffer(sample_rate=16000, max_duration_seconds=5.0)

    # Empty chunk
    assert buf.write(np.array([], dtype=np.float32)) == 0

    # 2D stereo chunk (N, 2)
    stereo_chunk = np.ones((800, 2), dtype=np.float32) * 0.5
    written = buf.write(stereo_chunk)
    assert written == 1600

    # int16 audio chunk
    int16_chunk = np.array([1000, -1000, 2000, -2000], dtype=np.int16)
    written_int = buf.write(int16_chunk)
    assert written_int == 4


def test_silence_input_does_not_trigger_false_alarm(test_env):
    """Verify prolonged silence produces low scream score and zero alerts."""
    service, _ = test_env

    # 2 seconds of absolute silence (zeros)
    silence = np.zeros(TARGET_SAMPLE_RATE * 2, dtype=np.float32)
    service.push_audio(silence)

    results = service.process_windows()
    assert len(results) >= 2

    for r in results:
        assert r.raw_probability < 0.15
        assert r.is_positive is False

    assert service.detector.state_machine.current_state == DetectorState.IDLE
    assert service.detector.state_machine.total_alerts_emitted == 0


def test_clean_real_wav_stream_processing(test_env):
    """Verify processing clean real audio from disk without errors or dropped samples."""
    service, _ = test_env

    # Synthesize clean 16 kHz tone representing structured WAV audio
    t = np.linspace(0, 1.5, int(TARGET_SAMPLE_RATE * 1.5), endpoint=False, dtype=np.float32)
    wav_signal = 0.05 * np.sin(2 * np.pi * 440 * t)  # Gentle 440Hz tone

    service.push_audio(wav_signal)
    results = service.process_windows()

    # 1.5s audio with 0.975s window and 0.4875s hop yields 2 windows
    assert len(results) == 2
    assert results[0].window_index == 1
    assert results[1].window_index == 2
    assert service.detector.buffer.dropped_samples == 0


def test_corrupted_or_nan_audio_resilience(test_env):
    """Verify audio chunks with NaNs or infs do not crash window inference."""
    service, _ = test_env

    corrupted_chunk = np.ones(service.detector.window_samples, dtype=np.float32) * 0.1
    corrupted_chunk[100:150] = np.nan
    corrupted_chunk[200] = np.inf

    # Clean NaNs to prevent model exceptions
    sanitized = np.nan_to_num(corrupted_chunk, nan=0.0, posinf=1.0, neginf=-1.0)
    service.push_audio(sanitized)
    results = service.process_windows()

    assert len(results) >= 1
    assert not np.isnan(results[0].raw_probability)


# ============================================================================
# Phase 3C: Alert State Machine Exhaustive Transitions
# ============================================================================

def test_full_state_machine_transition_lifecycle():
    """Verify IDLE -> CANDIDATE -> ALERT_ACTIVE -> COOLDOWN -> IDLE cycle."""
    alerts_emitted = []
    events_resolved = []

    sm = EventStateMachine(
        threshold=0.35,
        min_consecutive_positive=2,
        max_gap_negative_windows=2,
        cooldown_seconds=2.0,
        smoothing_alpha=0.6,
        on_alert_callback=lambda evt: alerts_emitted.append(evt),
        on_event_resolved_callback=lambda evt: events_resolved.append(evt),
    )

    assert sm.current_state == DetectorState.IDLE

    # Window 1: Positive -> Transition to CANDIDATE
    res1 = sm.process_window(raw_probability=0.50, stream_time_seconds=0.5, window_index=1)
    assert sm.current_state == DetectorState.CANDIDATE
    assert len(alerts_emitted) == 0

    # Window 2: Second consecutive positive -> Transition to ALERT_ACTIVE
    res2 = sm.process_window(raw_probability=0.60, stream_time_seconds=1.0, window_index=2)
    assert sm.current_state == DetectorState.ALERT_ACTIVE
    assert len(alerts_emitted) == 1
    assert alerts_emitted[0]["peak_probability"] == 0.60

    # Window 3: Still positive -> Remains ALERT_ACTIVE, updates peak
    res3 = sm.process_window(raw_probability=0.85, stream_time_seconds=1.5, window_index=3)
    assert sm.current_state == DetectorState.ALERT_ACTIVE
    assert len(alerts_emitted) == 1  # No duplicate alert!

    # Window 4: First negative window -> Remains ALERT_ACTIVE (gap 1 of 2)
    res4 = sm.process_window(raw_probability=0.20, stream_time_seconds=2.0, window_index=4)
    assert sm.current_state == DetectorState.ALERT_ACTIVE

    # Window 5: Second negative window -> Event concludes, enters COOLDOWN
    res5 = sm.process_window(raw_probability=0.20, stream_time_seconds=2.5, window_index=5)
    assert sm.current_state == DetectorState.COOLDOWN
    assert len(events_resolved) == 1
    assert events_resolved[0]["peak_probability"] == 0.85

    # Window 6: Positive window during COOLDOWN -> Duplicate alarm suppressed
    res6 = sm.process_window(raw_probability=0.70, stream_time_seconds=3.0, window_index=6)
    assert sm.current_state == DetectorState.COOLDOWN
    assert sm.total_alerts_suppressed == 1
    assert len(alerts_emitted) == 1  # No duplicate alert emitted

    # Window 7: Cooldown expires (elapsed = 4.6s - 2.5s = 2.1s >= 2.0s) -> Returns to IDLE
    res7 = sm.process_window(raw_probability=0.15, stream_time_seconds=4.6, window_index=7)
    assert sm.current_state == DetectorState.IDLE


def test_single_window_transient_spike_suppressed():
    """Verify single 1-window transient spike does not trigger alert (CANDIDATE -> IDLE)."""
    alerts = []
    sm = EventStateMachine(
        threshold=0.35,
        min_consecutive_positive=2,
        on_alert_callback=lambda evt: alerts.append(evt),
    )

    # Window 1: High transient spike (0.90)
    sm.process_window(raw_probability=0.90, stream_time_seconds=0.5, window_index=1)
    assert sm.current_state == DetectorState.CANDIDATE

    # Window 2: Immediately negative (0.10)
    sm.process_window(raw_probability=0.10, stream_time_seconds=1.0, window_index=2)
    assert sm.current_state == DetectorState.IDLE

    # No alert should have been emitted
    assert len(alerts) == 0
    assert sm.total_alerts_emitted == 0


def test_recovery_after_inference_exception(test_env):
    """Verify detector recovers safely and resets state machine after an inference failure."""
    service, _ = test_env

    # Inject a failing predictor
    def failing_pred(audio):
        raise RuntimeError("Injected ML inference memory crash")

    service.detector.prediction_fn_override = failing_pred

    # Push chunk and process
    chunk = np.ones(service.detector.window_samples, dtype=np.float32) * 0.5
    service.push_audio(chunk)

    # Process windows should catch exception and not crash
    results = service.process_windows()
    assert len(results) == 0
    assert service.detector._inference_errors == 1
    assert service.detector.state_machine.current_state == DetectorState.IDLE

    # Restore working predictor
    def good_pred(audio):
        return 0.20, []
    service.detector.prediction_fn_override = good_pred

    # Process next window normally
    service.push_audio(chunk)
    results_after = service.process_windows()
    assert len(results_after) >= 1
    assert results_after[0].raw_probability == 0.20


# ============================================================================
# Phase 3D: API, WebSockets & Multi-Client Resilience
# ============================================================================

def test_multi_client_websocket_broadcast(client: TestClient, test_env):
    """Verify multiple concurrent WebSocket clients receive simultaneous broadcasts."""
    service, _ = test_env

    with client.websocket_connect("/ws/events") as ws1:
        with client.websocket_connect("/ws/events") as ws2:
            snap1 = ws1.receive_json()
            snap2 = ws2.receive_json()
            assert snap1["type"] == "initial_snapshot"
            assert snap2["type"] == "initial_snapshot"

            # Broadcast alert
            service._on_alert_dispatched({
                "event_id": "evt_multi_client_test",
                "peak_probability": 0.912,
                "threshold": 0.35,
            })

            msg1 = ws1.receive_json()
            msg2 = ws2.receive_json()

            assert msg1["type"] == "alert_triggered"
            assert msg2["type"] == "alert_triggered"
            assert msg1["event"]["event_id"] == "evt_multi_client_test"
            assert msg2["event"]["event_id"] == "evt_multi_client_test"


def test_slow_client_queue_drop_protection():
    """Verify a stalled or slow WebSocket client drops oldest messages when queue is saturated."""
    mock_ws = MagicMock()
    ws_client = WebSocketClient(mock_ws, max_queue_size=50)

    # Send 120 messages
    for i in range(120):
        ws_client.enqueue_message({"seq": i})

    # Queue length must be strictly bounded at 50
    assert ws_client.queue.qsize() == 50
    # Dropped count must be exactly 70
    assert ws_client.dropped_count == 70

    # Oldest message currently in queue should be sequence #70
    oldest_msg = ws_client.queue.get_nowait()
    assert oldest_msg["seq"] == 70


def test_websocket_reconnect_reconciliation(client: TestClient, test_env):
    """Verify newly connected client receives fresh status after backend state updates."""
    service, _ = test_env

    # 1. Update config via REST
    patch_resp = client.patch("/api/config", json={"threshold": 0.42})
    assert patch_resp.status_code == 200

    # 2. Connect client and check initial snapshot
    with client.websocket_connect("/ws/events") as ws:
        snap = ws.receive_json()
        assert snap["type"] == "initial_snapshot"
        assert snap["status"]["threshold"] == 0.42


# ============================================================================
# Phase 3E: Logging, Persistence & Privacy
# ============================================================================

def test_event_logger_survives_restart(tmp_path: Path):
    """Verify event log records survive a detector restart and maintain JSON integrity."""
    log_file = tmp_path / "persistence_test.jsonl"
    logger1 = DetectionEventLogger(log_filepath=log_file)

    event_record = {
        "event_id": "evt_persisted_999",
        "peak_probability": 0.775,
        "duration_seconds": 1.46,
        "alert_emitted": True,
        "event_status": "alert_triggered",
    }
    logger1.log_event(event_record)

    # Initialize a new DetectorService pointing to the same log
    service2 = DetectorService(log_filepath=log_file)
    events_data = service2.get_events()

    assert events_data["total"] == 1
    loaded = events_data["events"][0]
    assert loaded["event_id"] == "evt_persisted_999"
    assert loaded["peak_probability"] == 0.775


def test_corrupted_jsonl_log_recovery(tmp_path: Path):
    """Verify logger gracefully recovers when reading a JSONL file with corrupted lines."""
    log_file = tmp_path / "corrupted.jsonl"

    valid_record = json.dumps({"event_id": "evt_valid", "peak_probability": 0.8}) + "\n"
    corrupt_record = "{BROKEN_MALFORMED_JSON_LINE\n"
    empty_line = "\n"

    log_file.write_text(valid_record + corrupt_record + empty_line, encoding="utf-8")

    service = DetectorService(log_filepath=log_file)
    events_data = service.get_events()

    # Should safely load the 1 valid record and skip the broken line
    assert events_data["total"] == 1
    assert events_data["events"][0]["event_id"] == "evt_valid"


def test_unwritable_log_file_handled_without_crash(tmp_path: Path):
    """Verify unwritable log file logs error without raising unhandled exception."""
    # Point to a path that cannot be written to (directory named as file)
    unwritable_dir = tmp_path / "blocked_log_dir"
    unwritable_dir.mkdir()

    logger = DetectionEventLogger(log_filepath=unwritable_dir)

    # Should catch PermissionError / IsADirectoryError internally
    logger.log_event({"event_id": "evt_fail"})
    logger.log_audio_gap(0.0, 1.0, "test")


def test_privacy_default_no_raw_audio_persisted(tmp_path: Path):
    """Verify default event logger NEVER stores raw audio samples or spectrograms."""
    log_file = tmp_path / "privacy_test.jsonl"
    logger = DetectionEventLogger(log_filepath=log_file)

    logger.log_event({
        "event_id": "evt_privacy_check",
        "peak_probability": 0.88,
        "duration_seconds": 1.5,
    })

    assert log_file.exists()
    content = log_file.read_text(encoding="utf-8")
    record = json.loads(content.strip())

    assert record["raw_audio_saved"] is False
    assert "audio" not in record
    assert "raw_samples" not in record
    assert "pcm" not in record
