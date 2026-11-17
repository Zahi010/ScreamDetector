"""Integration Tests for Experimental Live Testing Lab REST Endpoints & WebSocket.

Verifies:
1. GET /api/experimental/live/models returns all 7 models with correct thresholds and flags.
2. GET /api/experimental/live/status returns active engine status.
3. POST /api/experimental/live/config toggles model enabled state.
4. POST /api/experimental/live/simulate-audio injects synthetic audio into shared buffer.
5. POST /api/experimental/live/start and stop lifecycle.
6. POST /api/experimental/live/review records human verification and computes metrics.
7. WebSocket /ws/experimental/multi-model delivers initial snapshot.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_get_experimental_models():
    """Verify registry endpoint returns all 7 registered models with metadata."""
    response = client.get("/api/experimental/live/models")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["primary_model_id"] == "D_V4_FAMILY_A"
    assert data["production_model_id"] == "PRODUCTION_BASELINE"

    models = {m["model_id"]: m for m in data["models"]}
    assert len(models) == 7

    # Check Primary Model
    fam_a = models["D_V4_FAMILY_A"]
    assert fam_a["is_primary"] is True
    assert fam_a["operating_threshold"] == 0.420
    assert fam_a["expected_feature_dims"] == 3080
    assert fam_a["status"] == "LOADED"

    # Check Production Baseline
    prod = models["PRODUCTION_BASELINE"]
    assert prod["is_production"] is True
    assert prod["operating_threshold"] == 0.3500
    assert prod["expected_feature_dims"] == 1024


def test_get_experimental_status():
    """Verify status endpoint returns stream state and buffer info."""
    response = client.get("/api/experimental/live/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "lab_status" in data
    assert "audio_devices" in data
    assert "buffer_stats" in data["lab_status"]


def test_toggle_model_config():
    """Verify model can be enabled/disabled via config endpoint."""
    res = client.post(
        "/api/experimental/live/config",
        json={"model_id": "STAGE_8915_MODEL_B", "enabled": False},
    )
    assert res.status_code == 200
    assert res.json()["enabled"] is False

    # Restore
    res2 = client.post(
        "/api/experimental/live/config",
        json={"model_id": "STAGE_8915_MODEL_B", "enabled": True},
    )
    assert res2.status_code == 200
    assert res2.json()["enabled"] is True


def test_simulate_audio_injection():
    """Verify synthetic audio injection feeds buffer."""
    res = client.post(
        "/api/experimental/live/simulate-audio",
        json={"signal_type": "scream_burst", "duration_seconds": 1.0, "amplitude": 0.5},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["samples_injected"] == 16000
    assert data["buffer_stats"]["total_samples_written"] >= 16000


def test_session_lifecycle_and_human_review():
    """Verify session start, human review submission, and session metrics retrieval."""
    # 1. Start session
    start_res = client.post(
        "/api/experimental/live/session/start",
        json={"notes": "Integration test session", "enabled_models": ["D_V4_FAMILY_A", "PRODUCTION_BASELINE"]},
    )
    assert start_res.status_code == 200
    sess_id = start_res.json()["session_id"]
    assert sess_id.startswith("sess_")

    # 2. Submit human review
    rev_res = client.post(
        "/api/experimental/live/review",
        json={
            "session_id": sess_id,
            "event_id": "evt_integration_1",
            "window_start_idx": 1,
            "window_end_idx": 2,
            "timestamp_start": 100.0,
            "timestamp_end": 101.0,
            "ground_truth_label": "SCREAM",
            "sound_class": "screaming",
            "reviewer_notes": "Auditory confirmation of genuine distress scream",
        },
    )
    assert rev_res.status_code == 200
    assert "review_id" in rev_res.json()
    assert rev_res.json()["session_metrics"]["reviewed_events_count"] == 1

    # 3. Retrieve session details
    get_res = client.get(f"/api/experimental/live/session/{sess_id}")
    assert get_res.status_code == 200
    sess = get_res.json()["session"]
    assert sess["session_id"] == sess_id
    assert len(sess["human_reviews"]) == 1

    # 4. Stop session
    stop_res = client.post("/api/experimental/live/session/stop")
    assert stop_res.status_code == 200


def test_websocket_snapshot():
    """Verify WebSocket connects and delivers initial multi-model snapshot."""
    with client.websocket_connect("/ws/experimental/multi-model") as ws:
        data = ws.receive_json()
        assert data["type"] == "multimodel_snapshot"
        assert "models" in data
        assert "status" in data
        assert len(data["models"]) == 7

        # Ping-pong test
        ws.send_text(json.dumps({"command": "ping"}))
        pong = ws.receive_json()
        assert pong["type"] == "pong"


def test_live_start_and_stop_lab():
    """Verify POST /api/experimental/live/start and stop endpoints succeed without error."""
    # 1. Start live testing
    start_res = client.post(
        "/api/experimental/live/start",
        json={"device_index": None, "session_notes": "Live testing automated test"},
    )
    assert start_res.status_code == 200
    start_data = start_res.json()
    assert start_data["status"] == "success"
    assert "session_id" in start_data
    assert "details" in start_data

    # 2. Check status while running
    status_res = client.get("/api/experimental/live/status")
    assert status_res.status_code == 200
    lab_status = status_res.json()["lab_status"]
    assert lab_status["is_running"] is True

    # 3. Stop live testing
    stop_res = client.post("/api/experimental/live/stop")
    assert stop_res.status_code == 200
    stop_data = stop_res.json()
    assert stop_data["status"] == "success"
    assert stop_data["details"]["status"]["is_running"] is False


def test_toggle_acoustic_gate():
    """Verify acoustic gate toggle endpoint configures engine state."""
    # Toggle off
    res = client.post(
        "/api/experimental/live/acoustic-gate",
        json={"enabled": False, "rms_threshold": 0.005, "peak_threshold": 0.015},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["acoustic_gate"]["enabled"] is False

    # Restore on
    res2 = client.post(
        "/api/experimental/live/acoustic-gate",
        json={"enabled": True, "rms_threshold": 0.0035, "peak_threshold": 0.010},
    )
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["status"] == "success"
    assert data2["acoustic_gate"]["enabled"] is True
