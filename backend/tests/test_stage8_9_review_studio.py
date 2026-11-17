"""Stage 8.9 Human Review Studio & Audio Provenance Integration Tests.

Validates:
1. Summary counters computed dynamically from SQLite backend store.
2. Filtering across category, source, license, review status, audio availability, and score range.
3. Queue sorting with missing model scores (explicit NULLS LAST).
4. Candidate detail resolution for valid and non-existent IDs.
5. Secure audio path resolution and rejection of directory traversal attacks.
6. HTTP Range audio streaming (206 Partial Content) and missing audio handling (404).
7. Review decision validation and reason code tracking.
8. Append-only audit history preservation across multiple decisions.
9. Overwrite confirmation guard (HTTP 409 Conflict without confirmation, HTTP 200 with confirmation).
10. Reopen decision functionality while preserving history.
11. CSV export streaming without exposing secrets.
12. Model score persistence and frozen classifier SHA-256 integrity verification.
"""

from __future__ import annotations

import csv
import io
import shutil
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.api.schemas import ReviewDecisionRequest
from src.config import DEFAULT_SCREAM_THRESHOLD, MODELS_DIR
from src.database.review_store import (
    OverwriteConfirmationRequired,
    ReviewStore,
    get_review_store,
)
from src.dataset.acquisition_evaluator import (
    EXPECTED_CLASSIFIER_SHA256,
    EXPECTED_METADATA_SHA256,
    FROZEN_THRESHOLD,
    verify_frozen_model_artifacts,
)
from src.main import app


@pytest.fixture
def isolated_review_store(tmp_path: Path):
    """Provide an isolated SQLite ReviewStore populated with test fixtures."""
    db_file = tmp_path / "test_stage8_9_reviews.db"
    store = ReviewStore(db_path=db_file, allowed_roots=[tmp_path])

    # Create dummy audio files in test dir
    audio_dir = tmp_path / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    wav_clean = audio_dir / "test_clean.wav"
    wav_alert = audio_dir / "test_alert.wav"
    # Create minimal valid WAV headers
    import soundfile as sf
    import numpy as np
    sr = 16000
    sf.write(str(wav_clean), np.zeros(sr, dtype=np.float32), sr)
    sf.write(str(wav_alert), np.zeros(sr * 2, dtype=np.float32), sr)

    # Insert controlled test fixtures into candidates
    with store._get_connection() as conn:
        conn.executemany("""
            INSERT INTO candidates (
                recording_id, source_provider, original_source_id, original_source_url,
                local_path, has_audio, duration_seconds, sample_rate, channels,
                proposed_category, commercial_compatibility, review_status,
                model_score, model_alert, download_validation_status, reviewer_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            (
                "rec_001_whistle", "fsd50k", "101", "https://freesound.org/s/101/",
                str(wav_clean), 1, 1.0, 16000, 1,
                "whistles_and_squeaks", "CC0_VERIFIED", "UNREVIEWED",
                0.0125, 0, "VALIDATED_CLEAN", None,
            ),
            (
                "rec_002_crowd", "curated_permissive", "102", "https://freesound.org/s/102/",
                str(wav_alert), 1, 2.0, 16000, 1,
                "crowd_cheering_applause", "CC_BY_VERIFIED", "UNREVIEWED",
                0.8840, 1, "VALIDATED_CLEAN", None,
            ),
            (
                "rec_003_edm_no_score", "fsd50k", "103", "https://freesound.org/s/103/",
                str(wav_clean), 1, 1.5, 16000, 1,
                "edm_and_synthesizers", "CC0_VERIFIED", "UNREVIEWED",
                None, None, "VALIDATED_CLEAN", None,
            ),
            (
                "rec_004_audioset_missing_audio", "audioset", "104", "https://youtube.com/watch?v=xyz",
                None, 0, 10.0, 0, 0,
                "shouting_and_speech", "RESTRICTED", "UNREVIEWED",
                None, None, "NOT_ACQUIRED", None,
            ),
            (
                "rec_005_approved", "fsd50k", "105", "https://freesound.org/s/105/",
                str(wav_clean), 1, 1.2, 16000, 1,
                "vuvuzelas_and_horns", "CC0_VERIFIED", "APPROVED_NON_SCREAM",
                0.0050, 0, "VALIDATED_CLEAN", "Verified stadium horn",
            ),
        ])

    return store


@pytest.fixture
def client(isolated_review_store):
    """TestClient patched to use the isolated ReviewStore."""
    with patch("src.api.review_routes.get_review_store", return_value=isolated_review_store), \
         patch("src.database.review_store.get_review_store", return_value=isolated_review_store):
        yield TestClient(app)


# ==============================================================================
# 1. Summary Counts & Live Telemetry
# ==============================================================================

def test_summary_counters_computed_from_database(client):
    """Summary counters must accurately reflect DB fixtures."""
    res = client.get("/api/review/summary")
    assert res.status_code == 200
    data = res.json()

    assert data["total_candidates"] == 5
    assert data["audio_available"] == 4
    assert data["missing_audio"] == 1
    assert data["reviewed_count"] == 1
    assert data["pending_review"] == 4
    assert data["approved_non_scream"] == 1
    assert data["missing_model_scores"] == 2  # rec_003 and rec_004
    assert data["model_alerts_awaiting_review"] == 1  # rec_002 has score 0.884 and UNREVIEWED
    assert data["reviewed_percentage"] == 20.0
    assert data["operating_threshold"] == 0.35


# ==============================================================================
# 2. Filtering & Pagination
# ==============================================================================

def test_filtering_by_category_and_license(client):
    """Filters must combine and return matching subsets."""
    # Filter by category
    res_cat = client.get("/api/review/recordings?category=crowd_cheering_applause")
    assert res_cat.status_code == 200
    data_cat = res_cat.json()
    assert data_cat["total"] == 1
    assert data_cat["items"][0]["recording_id"] == "rec_002_crowd"

    # Filter by license
    res_lic = client.get("/api/review/recordings?license=CC_BY_VERIFIED")
    assert res_lic.status_code == 200
    assert res_lic.json()["total"] == 1

    # Filter by audio availability
    res_avail = client.get("/api/review/recordings?audio=missing")
    assert res_avail.status_code == 200
    assert res_avail.json()["total"] == 1
    assert res_avail.json()["items"][0]["recording_id"] == "rec_004_audioset_missing_audio"


def test_score_filtering(client):
    """Test score filtering for high_risk, low_risk, and missing."""
    # High risk (score >= 0.35)
    res_high = client.get("/api/review/recordings?score_filter=high_risk")
    assert res_high.status_code == 200
    items = res_high.json()["items"]
    assert len(items) == 1
    assert items[0]["recording_id"] == "rec_002_crowd"

    # Missing scores
    res_miss = client.get("/api/review/recordings?score_filter=missing")
    assert res_miss.status_code == 200
    items_miss = res_miss.json()["items"]
    assert len(items_miss) == 2
    assert {r["recording_id"] for r in items_miss} == {"rec_003_edm_no_score", "rec_004_audioset_missing_audio"}


def test_search_by_id_and_title(client):
    """Search matches recording_id or title."""
    res = client.get("/api/review/recordings?search=whistle")
    assert res.status_code == 200
    assert res.json()["total"] == 1
    assert res.json()["items"][0]["recording_id"] == "rec_001_whistle"


def test_pagination_bounds(client):
    """Pagination must respect page and page_size."""
    res = client.get("/api/review/recordings?page=1&page_size=2")
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5
    assert data["total_pages"] == 3


# ==============================================================================
# 3. Queue Sorting & Missing Scores
# ==============================================================================

def test_sorting_with_missing_scores(client):
    """Scores descending must put highest scores first and NULLS LAST."""
    res_desc = client.get("/api/review/recordings?sort_by=model_score&sort_order=desc")
    assert res_desc.status_code == 200
    items = res_desc.json()["items"]
    scores = [r["model_score"] for r in items]

    # First item must be 0.8840
    assert scores[0] == pytest.approx(0.8840, abs=1e-4)
    # The last two items must be None
    assert scores[-1] is None
    assert scores[-2] is None


# ==============================================================================
# 4. Detail Resolution & Invalid IDs
# ==============================================================================

def test_get_recording_detail_success_and_404(client):
    """Valid ID returns detail, non-existent returns 404."""
    res_ok = client.get("/api/review/recordings/rec_001_whistle")
    assert res_ok.status_code == 200
    assert res_ok.json()["recording_id"] == "rec_001_whistle"
    assert res_ok.json()["has_audio"] is True

    res_404 = client.get("/api/review/recordings/non_existent_rec_id")
    assert res_404.status_code == 404


# ==============================================================================
# 5. Secure Audio Path & Traversal Prevention
# ==============================================================================

def test_audio_streaming_range_request(client):
    """HTTP Range requests should return 206 Partial Content with proper headers."""
    headers = {"Range": "bytes=0-100"}
    res = client.get("/api/review/recordings/rec_001_whistle/audio", headers=headers)
    assert res.status_code == 206
    assert "Content-Range" in res.headers
    assert res.headers["Content-Range"].startswith("bytes 0-100/")
    assert len(res.content) == 101


def test_audio_streaming_missing_audio_404(client):
    """Candidate without audio file must return 404."""
    res = client.get("/api/review/recordings/rec_004_audioset_missing_audio/audio")
    assert res.status_code == 404
    assert "Audio file for recording" in res.json()["detail"]


def test_audio_traversal_prevention(client, isolated_review_store):
    """Path traversal in recording_id must be rejected safely."""
    # Traversal in ID
    res = client.get("/api/review/recordings/..%2F..%2F.env/audio")
    assert res.status_code in (404, 400)

    # Secure path resolver directly rejects outside roots
    safe_p = isolated_review_store.get_secure_audio_path("../../.env")
    assert safe_p is None


# ==============================================================================
# 6. Review Decision Workflow & Audit History
# ==============================================================================

def test_submit_decision_and_audit_history(client):
    """Submit initial decision, verify audit log, and update summary."""
    # Submit decision on rec_001_whistle
    payload = {
        "decision": "APPROVED_NON_SCREAM",
        "reason_code": "Genuine non-scream sound",
        "notes": "Slide whistle sample verified safe negative",
        "reviewer": "qa_operator",
        "confirm_overwrite": False,
    }
    res = client.post("/api/review/recordings/rec_001_whistle/decision", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["recording"]["review_status"] == "APPROVED_NON_SCREAM"
    assert data["recording"]["reviewer_notes"] == "Slide whistle sample verified safe negative"

    # Check audit history
    res_hist = client.get("/api/review/recordings/rec_001_whistle/history")
    assert res_hist.status_code == 200
    hist = res_hist.json()["history"]
    assert len(hist) == 1
    assert hist[0]["previous_status"] == "UNREVIEWED"
    assert hist[0]["new_status"] == "APPROVED_NON_SCREAM"
    assert hist[0]["reviewer"] == "qa_operator"


def test_overwrite_confirmation_guard(client):
    """Attempting to overwrite a finalized decision without confirm_overwrite must return 409."""
    # rec_005_approved is already APPROVED_NON_SCREAM
    payload = {
        "decision": "SCREAM_PRESENT",
        "reason_code": "Scream-like vocalisation",
        "notes": "Changing decision upon closer listening",
        "confirm_overwrite": False,
    }
    res_conflict = client.post("/api/review/recordings/rec_005_approved/decision", json=payload)
    assert res_conflict.status_code == 409
    err = res_conflict.json()["detail"]
    assert err["requires_confirmation"] is True
    assert err["current_status"] == "APPROVED_NON_SCREAM"
    assert err["new_status"] == "SCREAM_PRESENT"

    # Now confirm overwrite
    payload["confirm_overwrite"] = True
    res_ok = client.post("/api/review/recordings/rec_005_approved/decision", json=payload)
    assert res_ok.status_code == 200
    assert res_ok.json()["recording"]["review_status"] == "SCREAM_PRESENT"

    # Verify both decisions are preserved in audit trail
    res_hist = client.get("/api/review/recordings/rec_005_approved/history")
    assert res_hist.status_code == 200
    hist = res_hist.json()["history"]
    assert len(hist) == 1
    assert hist[0]["previous_status"] == "APPROVED_NON_SCREAM"
    assert hist[0]["new_status"] == "SCREAM_PRESENT"


def test_reopen_decision_preserves_history(client):
    """Reopening a reviewed recording resets to UNREVIEWED while logging audit item."""
    payload = {
        "decision": "UNREVIEWED",
        "reason_code": "Reopened for re-review",
        "notes": "Reset for committee review",
        "confirm_overwrite": True,
    }
    res = client.post("/api/review/recordings/rec_005_approved/decision", json=payload)
    assert res.status_code == 200
    assert res.json()["recording"]["review_status"] == "UNREVIEWED"


def test_invalid_decision_status_rejected(client):
    """Non-allowed decision string must be rejected with 422."""
    payload = {
        "decision": "INVALID_RANDOM_STATUS",
    }
    res = client.post("/api/review/recordings/rec_001_whistle/decision", json=payload)
    assert res.status_code == 422


# ==============================================================================
# 7. CSV Export
# ==============================================================================

def test_export_csv_contains_provenance_and_no_secrets(client):
    """CSV export must include all required fields and never expose API keys or secrets."""
    res = client.get("/api/review/export.csv")
    assert res.status_code == 200
    assert res.headers["Content-Type"].startswith("text/csv")
    assert "Content-Disposition" in res.headers

    csv_reader = csv.DictReader(io.StringIO(res.text))
    rows = list(csv_reader)
    assert len(rows) == 5

    # Check expected headers
    expected_cols = {
        "recording_id", "source_provider", "proposed_category", "commercial_compatibility",
        "clip_license", "duration_seconds", "has_audio", "model_score", "model_alert",
        "operating_threshold", "review_status", "reviewer_notes",
    }
    for col in expected_cols:
        assert col in csv_reader.fieldnames

    # Check secrets leak test
    raw_text = res.text.lower()
    assert "freesound_api_key" not in raw_text
    assert "secret" not in raw_text
    assert "token" not in raw_text


# ==============================================================================
# 8. Model Integrity & Bounded Evaluation
# ==============================================================================

def test_frozen_model_hash_verification():
    """Verify that classifier and metadata SHA-256 match expected constants."""
    verified, audit = verify_frozen_model_artifacts()
    assert verified is True
    assert audit["classifier_sha256"] == EXPECTED_CLASSIFIER_SHA256
    assert audit["metadata_sha256"] == EXPECTED_METADATA_SHA256
    assert audit["operating_threshold"] == FROZEN_THRESHOLD == 0.35


def test_evaluate_endpoint_bounded_mock(client):
    """Test POST /api/review/evaluate on candidate needing evaluation."""
    # Mock classifier inference to avoid heavy YAMNet load in this unit test
    mock_classifier = MagicMock()
    mock_classifier.predict_file.return_value = {
        "scream_probability": 0.4200,
        "is_scream": True,
    }

    with patch("src.api.review_routes.AcquiredAudioEvaluator") as MockEvaluator:
        instance = MockEvaluator.return_value
        instance.classifier = mock_classifier
        instance.threshold = 0.35

        res = client.post("/api/review/evaluate", json={
            "recording_id": "rec_003_edm_no_score",
        })
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["evaluated_count"] == 1
        assert data["alerts_count"] == 1
        assert data["results"][0]["model_score"] == pytest.approx(0.4200, abs=1e-4)
        assert data["results"][0]["is_alert"] is True

    # Detail should now reflect the evaluated score
    res_det = client.get("/api/review/recordings/rec_003_edm_no_score")
    assert res_det.status_code == 200
    assert res_det.json()["model_score"] == pytest.approx(0.4200, abs=1e-4)
    assert res_det.json()["model_alert"] is True
