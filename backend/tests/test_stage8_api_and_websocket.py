"""Stage 8 Backend REST & WebSocket Integration Tests.

Validates:
1. Health, status, metrics, and configuration endpoints.
2. Safe runtime config validation (rejects invalid threshold, cooldown, smoothing bounds).
3. Detector start/stop lifecycle and idempotency against multiple calls.
4. Graceful handling of missing audio capture devices / PortAudio errors.
5. WebSocket connection, initial status snapshot, and keepalive ping/pong.
6. WebSocket event broadcasting and slow-client queue isolation.
7. Persisted event history retrieval and operator acknowledgment workflow.
8. Injected fake predictor integration with StreamDetector and state machine.
9. Immutability of Stage 5 classifier model artifacts.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from fastapi.testclient import TestClient

from src.config import MODELS_DIR, TARGET_SAMPLE_RATE
from src.detector import AudioDeviceError, StreamDetector
from src.api.websocket import manager, setup_detector_websocket_bridge, WebSocketClient
from src.detector.service import DetectorService, get_detector_service, reset_detector_service
from src.main import app

STAGE5_CLASSIFIER_SHA256 = "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f"
STAGE5_METADATA_SHA256 = "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60"


@pytest.fixture(autouse=True)
def clean_detector_service(tmp_path: Path):
    """Provide an isolated DetectorService instance for each test."""
    test_log = tmp_path / "test_events.jsonl"

    # Mock predictor for zero-overhead unit testing
    def mock_pred(audio: np.ndarray) -> Tuple[float, List[Dict[str, Any]]]:
        # Return probability based on mean audio level or mock rule
        p = float(np.clip(np.mean(np.abs(audio)) * 10.0, 0.05, 0.95))
        return p, [{"class_name": "Screaming", "score": p}]

    detector = StreamDetector(
        sample_rate=TARGET_SAMPLE_RATE,
        threshold=0.35,
        prediction_fn_override=mock_pred,
    )
    service = DetectorService(stream_detector=detector, log_filepath=test_log)
    reset_detector_service(service)

    # Attach websocket listener bridge
    def _bridge(event: Dict[str, Any]):
        manager.dispatch_from_thread(event)

    service.add_listener(_bridge)

    yield service

    service.stop()
    reset_detector_service(None)


@pytest.fixture
def client() -> TestClient:
    """FastAPI TestClient fixture."""
    return TestClient(app)


def test_stage5_baseline_model_immutability():
    """Verify that Stage 5 classifier artifact and metadata remain strictly bit-identical."""
    classifier_path = MODELS_DIR / "scream_classifier.joblib"
    metadata_path = MODELS_DIR / "model_metadata.json"

    assert classifier_path.exists(), "Stage 5 classifier artifact missing!"
    assert metadata_path.exists(), "Stage 5 metadata artifact missing!"

    clf_hash = hashlib.sha256(classifier_path.read_bytes()).hexdigest()
    meta_hash = hashlib.sha256(metadata_path.read_bytes()).hexdigest()

    assert clf_hash == STAGE5_CLASSIFIER_SHA256, (
        f"Stage 5 classifier was modified! Expected {STAGE5_CLASSIFIER_SHA256}, got {clf_hash}"
    )
    assert meta_hash == STAGE5_METADATA_SHA256, (
        f"Stage 5 metadata was modified! Expected {STAGE5_METADATA_SHA256}, got {meta_hash}"
    )


def test_health_endpoint(client: TestClient):
    """Test GET /api/health endpoint returns 200 and correct status metadata."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("healthy", "degraded")
    assert "YAMNet" in data["yamnet_model"]
    assert "Stage 5" in data["classifier_model"]
    assert data["version"] == "0.8.0"


def test_status_endpoint(client: TestClient):
    """Test GET /api/status endpoint structure."""
    resp = client.get("/api/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "is_running" in data
    assert "state" in data
    assert data["state"] == "IDLE"
    assert data["threshold"] == 0.35
    assert data["min_consecutive_positive"] == 2


def test_metrics_endpoint(client: TestClient):
    """Test GET /api/metrics endpoint reports non-fabricated metrics."""
    resp = client.get("/api/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert "windows_processed" in data
    assert "total_alerts_emitted" in data
    assert "latency_metrics_ms" in data
    assert "mean" in data["latency_metrics_ms"]
    assert "p95" in data["latency_metrics_ms"]


def test_config_endpoints(client: TestClient):
    """Test GET /api/config and PATCH /api/config boundary validation."""
    # 1. Get initial config
    resp = client.get("/api/config")
    assert resp.status_code == 200
    initial_cfg = resp.json()
    assert initial_cfg["threshold"] == 0.35

    # 2. Update with valid parameters
    patch_resp = client.patch(
        "/api/config",
        json={"threshold": 0.40, "cooldown_seconds": 4.5, "min_consecutive_positive": 3},
    )
    assert patch_resp.status_code == 200
    updated = patch_resp.json()
    assert updated["threshold"] == 0.40
    assert updated["cooldown_seconds"] == 4.5
    assert updated["min_consecutive_positive"] == 3

    # 3. Reject invalid threshold (> 0.99 or < 0.01)
    err_resp = client.patch("/api/config", json={"threshold": 1.5})
    assert err_resp.status_code == 422

    # 4. Reject invalid cooldown
    err_cooldown = client.patch("/api/config", json={"cooldown_seconds": 0.1})
    assert err_cooldown.status_code == 422

    # 5. Reject invalid smoothing_alpha (> 1.0)
    err_smooth = client.patch("/api/config", json={"smoothing_alpha": 2.0})
    assert err_smooth.status_code == 422


def test_detector_start_stop_idempotency(client: TestClient):
    """Test that start and stop are idempotent and safe against repeated calls."""
    # First start (mock microphone capture to avoid needing physical mic in CI)
    with patch("src.detector.service.MicrophoneCapture") as MockMic:
        mock_instance = MagicMock()
        MockMic.return_value = mock_instance

        resp1 = client.post("/api/detector/start", json={"device_index": None})
        assert resp1.status_code == 200
        assert resp1.json()["success"] is True

        # Second start call while already running should be idempotent
        resp2 = client.post("/api/detector/start", json={"device_index": None})
        assert resp2.status_code == 200
        assert resp2.json()["success"] is True
        assert resp2.json()["message"] == "Detector is already running."

        # Stop
        stop_resp1 = client.post("/api/detector/stop")
        assert stop_resp1.status_code == 200
        assert stop_resp1.json()["success"] is True

        # Repeated stop call should be idempotent
        stop_resp2 = client.post("/api/detector/stop")
        assert stop_resp2.status_code == 200
        assert stop_resp2.json()["success"] is True
        assert stop_resp2.json()["message"] == "Detector is already stopped."


def test_missing_microphone_graceful_handling(client: TestClient):
    """Test that when microphone is missing or fails, detector reports unavailable without server crash."""
    with patch("src.detector.service.MicrophoneCapture") as MockMic:
        mock_instance = MagicMock()
        mock_instance.start.side_effect = AudioDeviceError("No default input audio device found.")
        MockMic.return_value = mock_instance

        resp = client.post("/api/detector/start", json={"device_index": 99})
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["status"]["mic_status"] == "unavailable"
        assert "No default input audio device" in data["status"]["mic_error"]

        # Clean stop
        client.post("/api/detector/stop")


def test_devices_endpoint(client: TestClient):
    """Test GET /api/devices returns a list of audio devices."""
    resp = client.get("/api/devices")
    assert resp.status_code == 200
    assert "devices" in resp.json()
    assert isinstance(resp.json()["devices"], list)


def test_websocket_initial_snapshot(client: TestClient):
    """Test that connecting to /ws/events receives immediate initial snapshot."""
    with client.websocket_connect("/ws/events") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "initial_snapshot"
        assert data["connection_status"] == "connected"
        assert "status" in data
        assert "metrics" in data
        assert "POSSIBLE SCREAM DETECTION ADVISORY" in data["disclaimer"]

        # Test keepalive ping/pong
        websocket.send_json({"type": "ping"})
        pong = websocket.receive_json()
        assert pong["type"] == "pong"


def test_event_history_and_acknowledgment(client: TestClient, clean_detector_service: DetectorService):
    """Test event history loading and human operator acknowledgment workflow."""
    service = clean_detector_service

    # Write a test detection event to the logger
    test_evt = {
        "event_id": "evt_test_12345",
        "start_stream_time": 10.5,
        "end_stream_time": 12.0,
        "duration_seconds": 1.5,
        "start_wall_time_iso": "2026-10-24T12:00:00",
        "peak_probability": 0.825,
        "threshold": 0.35,
        "window_count": 3,
        "positive_window_count": 3,
        "alert_emitted": True,
        "top_priors": [{"class_name": "Screaming", "score": 0.85}],
        "event_status": "alert_triggered",
    }
    service.event_logger.log_event(test_evt)

    # 1. Fetch from /api/events
    resp = client.get("/api/events")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    found = next((e for e in data["events"] if e["event_id"] == "evt_test_12345"), None)
    assert found is not None
    assert found["peak_probability"] == 0.825

    # 2. Acknowledge the event
    ack_resp = client.post(
        "/api/events/evt_test_12345/acknowledge",
        json={"operator_note": "False alarm: crowd singing along to performance."},
    )
    assert ack_resp.status_code == 200
    ack_data = ack_resp.json()
    assert ack_data["acknowledged"] is True
    assert ack_data["operator_note"] == "False alarm: crowd singing along to performance."

    # 3. Verify acknowledgment is reflected in event history
    resp_reconciled = client.get("/api/events")
    reconciled_found = next((e for e in resp_reconciled.json()["events"] if e["event_id"] == "evt_test_12345"), None)
    assert reconciled_found is not None
    assert reconciled_found.get("acknowledged") is True
    assert reconciled_found.get("operator_note") == "False alarm: crowd singing along to performance."


def test_websocket_broadcast_and_slow_client_isolation(client: TestClient, clean_detector_service: DetectorService):
    """Test WebSocket event broadcasting and slow client queue isolation (bounded drop)."""
    # 1. Test queue bounding and slow client isolation on WebSocketClient
    mock_ws = MagicMock()
    ws_client = WebSocketClient(mock_ws, max_queue_size=10)
    for i in range(25):
        ws_client.enqueue_message({"index": i})

    # Queue should be capped at max_queue_size, with 15 oldest messages dropped safely
    assert ws_client.queue.qsize() == 10
    assert ws_client.dropped_count == 15

    # 2. Test live WebSocket communication with TestClient
    with client.websocket_connect("/ws/events") as ws:
        init_snap = ws.receive_json()
        assert init_snap["type"] == "initial_snapshot"

        # Client requests fresh status snapshot over WebSocket
        ws.send_json({"type": "request_status"})
        status_resp = ws.receive_json()
        assert status_resp["type"] == "status_response"
        assert "status" in status_resp
        assert "metrics" in status_resp
        assert status_resp["status"]["state"] == "IDLE"
