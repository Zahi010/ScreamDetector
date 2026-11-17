# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
FastAPI Backend Integration Tests for Stage 8.9.67 Research Endpoints.

MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import sys
import io
import wave
import numpy as np
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))
from src.main import app

client = TestClient(app)


def test_research_models_list():
    res = client.get("/api/research/models")
    assert res.status_code == 200
    data = res.json()
    assert "models" in data
    assert len(data["models"]) >= 3
    model_ids = [m["model_id"] for m in data["models"]]
    assert "PRODUCTION_BASELINE" in model_ids
    assert "CANDIDATE_65F" in model_ids
    assert "CANDIDATE_67_VADF" in model_ids


def test_research_models_active():
    res = client.get("/api/research/models/active")
    assert res.status_code == 200
    data = res.json()
    assert "model_id" in data
    assert "operating_threshold" in data


def test_research_models_select():
    # Select Candidate 65-F
    res = client.post("/api/research/models/select", json={"model_id": "CANDIDATE_65F"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["active_model"]["model_id"] == "CANDIDATE_65F"

    # Select Candidate 67-D
    res2 = client.post("/api/research/models/select", json={"model_id": "CANDIDATE_67_VADF"})
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["success"] is True
    assert data2["active_model"]["model_id"] == "CANDIDATE_67_VADF"


def test_research_metrics():
    res = client.get("/api/research/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "p50_latency_ms" in data
    assert "p95_latency_ms" in data
    assert "uptime_seconds" in data


def test_research_evaluation_summary():
    res = client.get("/api/research/evaluation/summary")
    assert res.status_code == 200
    data = res.json()
    assert "acceptance_gates" in data
    assert len(data["acceptance_gates"]) == 5
    assert data["research_verdict"] == "PARTIAL IMPROVEMENT — ONE OR MORE GATES FAILED"
    assert "safety_warning" in data


def test_research_events_and_clear():
    res = client.get("/api/research/events")
    assert res.status_code == 200
    data = res.json()
    assert "events" in data

    res_clear = client.post("/api/research/events/clear")
    assert res_clear.status_code == 200
    assert res_clear.json()["success"] is True

    res2 = client.get("/api/research/events")
    assert res2.status_code == 200
    assert len(res2.json()["events"]) == 0


def test_research_session_export_csv():
    res = client.get("/api/research/session/export?format=csv")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert "timestamp,event_id,model_id" in res.text


def test_research_inference_file():
    # Create synthetic 1.0 second WAV buffer in memory (16 kHz sine wave 1000 Hz)
    sr = 16000
    t = np.linspace(0, 1.0, sr, endpoint=False)
    sig = (0.5 * np.sin(2 * np.pi * 1000.0 * t) * 32767).astype(np.int16)

    bio = io.BytesIO()
    with wave.open(bio, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(sig.tobytes())
    bio.seek(0)

    files = {"file": ("test_sine.wav", bio, "audio/wav")}
    res = client.post("/api/research/inference/file", files=files)
    assert res.status_code == 200
    data = res.json()
    assert "calibrated_probability" in data
    assert "is_detected" in data
    assert "model_latency_ms" in data
    assert "state" in data

