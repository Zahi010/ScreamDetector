"""Automated test suite for Stage 8.9.2 Missing Hard-Negative Audio Recovery."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.config import BACKEND_DIR, MODELS_DIR
from src.database.review_store import get_review_store
from src.dataset.acquisition_evaluator import (
    EXPECTED_CLASSIFIER_SHA256,
    EXPECTED_METADATA_SHA256,
    FROZEN_THRESHOLD,
    verify_frozen_model_artifacts,
)
from src.dataset.audio_recovery_service import get_audio_recovery_service
from src.main import app

client = TestClient(app)


def test_frozen_model_integrity_stage8_9_2():
    """Verify that model artifact hashes and operating threshold 0.35 are strictly preserved."""
    verified, audit = verify_frozen_model_artifacts()
    assert verified is True, f"Model artifacts altered: {audit}"

    clf_path = MODELS_DIR / "scream_classifier.joblib"
    meta_path = MODELS_DIR / "model_metadata.json"

    assert hashlib.sha256(clf_path.read_bytes()).hexdigest() == EXPECTED_CLASSIFIER_SHA256
    assert hashlib.sha256(meta_path.read_bytes()).hexdigest() == EXPECTED_METADATA_SHA256
    assert FROZEN_THRESHOLD == 0.35


def test_human_reviews_strictly_preserved():
    """CRITICAL: Verify all 343 human review decisions remain exact."""
    store = get_review_store()
    with store._get_connection() as conn:
        counts = dict(conn.execute(
            "SELECT review_status, COUNT(*) as cnt FROM candidates GROUP BY review_status"
        ).fetchall())

    assert counts.get("APPROVED_NON_SCREAM") == 338, f"Expected 338 approved, got {counts.get('APPROVED_NON_SCREAM')}"
    assert counts.get("SCREAM_PRESENT") == 2, f"Expected 2 screams, got {counts.get('SCREAM_PRESENT')}"
    assert counts.get("AMBIGUOUS") == 3, f"Expected 3 ambiguous, got {counts.get('AMBIGUOUS')}"
    assert counts.get("UNREVIEWED") == 27, f"Expected 27 unreviewed, got {counts.get('UNREVIEWED')}"


def test_recovery_audit_structure():
    """Verify recovery service audit output structure and categorization."""
    service = get_audio_recovery_service()
    audit = service.get_audit()

    assert audit["total_candidates"] == 370
    assert audit["audio_available"] >= 341
    assert "audioset" in audit["missing_by_source"]
    assert audit["licence_restricted"] == 22
    assert audit["source_unavailable"] == 5
    assert audit["preserved_human_reviews"]["total_reviewed"] == 343
    assert audit["preserved_human_reviews"]["approved_non_scream"] == 338


def test_api_recovery_status_endpoint():
    """Test GET /api/review/recovery/status."""
    res = client.get("/api/review/recovery/status")
    assert res.status_code == 200
    data = res.json()

    assert data["total_candidates"] == 370
    assert "audio_available" in data
    assert "missing_audio" in data
    assert "licence_restricted" in data
    assert "source_unavailable" in data
    assert data["preserved_human_reviews"]["approved_non_scream"] == 338


def test_api_recovery_run_endpoint():
    """Test POST /api/review/recovery/run returns success and preserves reviews."""
    from unittest.mock import MagicMock, patch
    mock_service = MagicMock()
    mock_service.recover_missing_audio.return_value = {
        "success": True,
        "processed_count": 10,
        "recovered_fsd50k": 0,
        "recovered_freesound": 0,
        "total_newly_recovered": 0,
        "restricted_audioset": 0,
        "unavailable_fsd50k": 0,
        "failed_downloads": 0,
        "cancelled": False,
        "recovered_records": [],
        "post_recovery_audit": {
            "total_candidates": 370,
            "preserved_human_reviews": {
                "total_reviewed": 343,
                "approved_non_scream": 338,
                "scream_present": 2,
                "ambiguous": 3,
            },
        },
    }
    with patch("src.dataset.audio_recovery_service.get_audio_recovery_service", return_value=mock_service):
        res = client.post("/api/review/recovery/run", json={"batch_size": 10})
        assert res.status_code == 200
        data = res.json()

        assert data["success"] is True
        assert "post_recovery_audit" in data
        assert data["post_recovery_audit"]["preserved_human_reviews"]["total_reviewed"] == 343


def test_api_recovery_cancel_endpoint():
    """Test POST /api/review/recovery/cancel."""
    res = client.post("/api/review/recovery/cancel")
    assert res.status_code == 200
    assert "cancellation requested" in res.json()["message"]


def test_recovered_audio_file_serving():
    """Verify that newly recovered recordings have accessible audio streams."""
    store = get_review_store()
    with store._get_connection() as conn:
        row = conn.execute(
            "SELECT recording_id FROM candidates WHERE source_provider = 'fsd50k' AND has_audio = 1 LIMIT 1"
        ).fetchone()

    assert row is not None
    rec_id = row["recording_id"]

    res = client.get(f"/api/review/recordings/{rec_id}/audio")
    assert res.status_code in (200, 206)
    assert res.headers["content-type"].startswith("audio/")
    assert len(res.content) > 1000
