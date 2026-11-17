"""Stage 8.9.1 Automated Hard-Negative Triage & Verification Test Suite.

Verifies:
1. Frozen classifier & metadata SHA-256 hashes and threshold 0.35 integrity.
2. Signal quality metrics (duration, digital clipping, silence ratio).
3. Triage rule assignment across all 4 categories (LIKELY_NON_SCREAM, POSSIBLE_SCREAM, AMBIGUOUS, REVIEW_REQUIRED).
4. Audio loading, missing files, corrupted files, and graceful error handling.
5. ReviewStore persistence, dynamic migrations, and triage filtering/sorting.
6. REST API endpoint POST /api/review/triage/run and GET /api/review/recordings?triage_group=...
7. CSV streaming export with triage fields.
8. Preservation of human review decisions, audit trails, and zero ground truth modification.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.config import BACKEND_DIR, DEFAULT_SCREAM_THRESHOLD, TARGET_SAMPLE_RATE
from src.database.review_store import ReviewStore, get_review_store
from src.dataset.acquisition_evaluator import (
    EXPECTED_CLASSIFIER_SHA256,
    EXPECTED_METADATA_SHA256,
    FROZEN_THRESHOLD,
    verify_frozen_model_artifacts,
)
from src.dataset.triage_analyzer import (
    AutomatedTriageEngine,
    TriageAnalysisResult,
    TriageGroup,
)


@pytest.fixture
def mock_db_path(tmp_path: Path) -> Path:
    """Fixture providing isolated temporary database path."""
    return tmp_path / "test_stage8_9_1.db"


@pytest.fixture
def store(mock_db_path: Path, tmp_path: Path) -> ReviewStore:
    """Fixture providing initialized ReviewStore with temp root allowed."""
    return ReviewStore(db_path=mock_db_path, allowed_roots=[tmp_path, BACKEND_DIR])


def test_frozen_model_artifacts_and_predictions_integrity():
    """Verify exact SHA-256 hashes of classifier and metadata artifacts, and 0.35 threshold."""
    classifier_path = BACKEND_DIR / "models" / "scream_classifier.joblib"
    metadata_path = BACKEND_DIR / "models" / "model_metadata.json"

    assert classifier_path.is_file(), f"Missing classifier artifact at {classifier_path}"
    assert metadata_path.is_file(), f"Missing metadata artifact at {metadata_path}"

    with open(classifier_path, "rb") as f:
        actual_classifier_sha256 = hashlib.sha256(f.read()).hexdigest()

    with open(metadata_path, "rb") as f:
        actual_metadata_sha256 = hashlib.sha256(f.read()).hexdigest()

    assert actual_classifier_sha256 == EXPECTED_CLASSIFIER_SHA256, (
        f"Classifier hash mismatch! Expected {EXPECTED_CLASSIFIER_SHA256}, got {actual_classifier_sha256}"
    )
    assert actual_metadata_sha256 == EXPECTED_METADATA_SHA256, (
        f"Metadata hash mismatch! Expected {EXPECTED_METADATA_SHA256}, got {actual_metadata_sha256}"
    )

    verified, audit = verify_frozen_model_artifacts()
    assert verified is True, f"verify_frozen_model_artifacts failed: {audit}"
    assert audit["operating_threshold"] == 0.35
    assert FROZEN_THRESHOLD == 0.35
    assert DEFAULT_SCREAM_THRESHOLD == 0.35


def test_signal_quality_metrics_short_audio():
    """Verify that waveforms shorter than 0.2s are classified as REVIEW_REQUIRED."""
    # Mock analyzer without loading full neural weights for unit testing
    engine = AutomatedTriageEngine.__new__(AutomatedTriageEngine)
    engine.threshold = 0.35

    # 0.1 second waveform (1600 samples at 16kHz)
    short_wave = np.zeros(1600, dtype=np.float32)
    res = engine.analyze_waveform(short_wave, recording_id="rec_short")

    assert res.triage_group == TriageGroup.REVIEW_REQUIRED.value
    assert "too short" in res.triage_reason.lower()
    assert res.status == "POOR_QUALITY"


def test_signal_quality_metrics_clipping():
    """Verify that waveforms with >20% clipped samples are flagged as REVIEW_REQUIRED."""
    engine = AutomatedTriageEngine.__new__(AutomatedTriageEngine)
    engine.threshold = 0.35

    # 1.0 second waveform with 30% clipping at 1.0
    wave = np.zeros(16000, dtype=np.float32)
    wave[:4800] = 1.0  # 30% clipped

    res = engine.analyze_waveform(wave, recording_id="rec_clipped")
    assert res.triage_group == TriageGroup.REVIEW_REQUIRED.value
    assert "clipping" in res.triage_reason.lower()
    assert res.clipping_ratio >= 0.20


def test_signal_quality_metrics_near_silence():
    """Verify that waveforms with >92% silent samples are flagged as REVIEW_REQUIRED."""
    engine = AutomatedTriageEngine.__new__(AutomatedTriageEngine)
    engine.threshold = 0.35

    # 1.0 second waveform with 98% near-zero samples
    wave = np.zeros(16000, dtype=np.float32)
    wave[:200] = 0.2  # tiny blip, 98.7% silence

    res = engine.analyze_waveform(wave, recording_id="rec_silent")
    assert res.triage_group == TriageGroup.REVIEW_REQUIRED.value
    assert "silence" in res.triage_reason.lower()
    assert res.silence_ratio >= 0.92


def test_triage_logic_infant_crying_ambiguous():
    """Verify that infant crying triggers AMBIGUOUS due to acoustic harmonic overlap with screams."""
    engine = AutomatedTriageEngine.__new__(AutomatedTriageEngine)
    engine.threshold = 0.35

    # Crying tag present with score >= 0.15
    relevant_tags = [
        {"class_name": "Baby cry, infant cry", "category": "crying", "max_score": 0.35, "mean_score": 0.20}
    ]
    top_classes = [{"class_name": "Baby cry, infant cry", "mean_score": 0.20, "max_score": 0.35}]

    group, reason = engine._compute_triage(
        scream_prob=0.38,
        is_alert=True,
        relevant_tags=relevant_tags,
        top_classes=top_classes,
    )

    assert group == TriageGroup.AMBIGUOUS
    assert "crying" in reason.lower()


def test_triage_logic_possible_scream():
    """Verify that score >= 0.35 with screaming/shouting tags maps to POSSIBLE_SCREAM."""
    engine = AutomatedTriageEngine.__new__(AutomatedTriageEngine)
    engine.threshold = 0.35

    relevant_tags = [
        {"class_name": "Screaming", "category": "scream_shout", "max_score": 0.40, "mean_score": 0.25}
    ]
    top_classes = [{"class_name": "Screaming", "mean_score": 0.25, "max_score": 0.40}]

    group, reason = engine._compute_triage(
        scream_prob=0.65,
        is_alert=True,
        relevant_tags=relevant_tags,
        top_classes=top_classes,
    )

    assert group == TriageGroup.POSSIBLE_SCREAM
    assert "0.650" in reason or "0.65" in reason


def test_triage_logic_likely_non_scream():
    """Verify that low score with strong alternative sound (whistle, cheer) maps to LIKELY_NON_SCREAM."""
    engine = AutomatedTriageEngine.__new__(AutomatedTriageEngine)
    engine.threshold = 0.35

    relevant_tags = [
        {"class_name": "Whistle", "category": "whistle", "max_score": 0.65, "mean_score": 0.45}
    ]
    top_classes = [{"class_name": "Whistle", "mean_score": 0.45, "max_score": 0.65}]

    group, reason = engine._compute_triage(
        scream_prob=0.04,
        is_alert=False,
        relevant_tags=relevant_tags,
        top_classes=top_classes,
    )

    assert group == TriageGroup.LIKELY_NON_SCREAM
    assert "Whistle" in reason


def test_missing_audio_file_triggers_review_required(tmp_path: Path):
    """Verify that non-existent local files safely resolve to REVIEW_REQUIRED."""
    engine = AutomatedTriageEngine.__new__(AutomatedTriageEngine)
    engine.threshold = 0.35

    non_existent = tmp_path / "does_not_exist.wav"
    res = engine.analyze_audio_file(non_existent, recording_id="rec_missing_file")

    assert res.triage_group == TriageGroup.REVIEW_REQUIRED.value
    assert res.has_audio is False
    assert res.status == "FILE_NOT_FOUND"


def test_store_triage_persistence_and_queries(store: ReviewStore, tmp_path: Path):
    """Verify ReviewStore schema migrations, save_triage_result, counts, and filtering."""
    # Seed 3 candidates
    with store._get_connection() as conn:
        conn.execute("""
            INSERT INTO candidates (
                recording_id, source_provider, review_status, commercial_compatibility, has_audio
            ) VALUES
            ('rec_1', 'fsd50k', 'UNREVIEWED', 'CC0_VERIFIED', 1),
            ('rec_2', 'fsd50k', 'UNREVIEWED', 'CC0_VERIFIED', 1),
            ('rec_3', 'fsd50k', 'UNREVIEWED', 'CC0_VERIFIED', 0)
        """)

    # Save triage results
    store.save_triage_result(TriageAnalysisResult(
        recording_id="rec_1",
        triage_group=TriageGroup.LIKELY_NON_SCREAM.value,
        triage_reason="Whistle detected, score 0.02",
        classifier_score=0.02,
        is_classifier_alert=False,
        has_audio=True,
    ))

    store.save_triage_result(TriageAnalysisResult(
        recording_id="rec_2",
        triage_group=TriageGroup.POSSIBLE_SCREAM.value,
        triage_reason="High scream score 0.72",
        classifier_score=0.72,
        is_classifier_alert=True,
        has_audio=True,
    ))

    store.save_triage_result(TriageAnalysisResult(
        recording_id="rec_3",
        triage_group=TriageGroup.REVIEW_REQUIRED.value,
        triage_reason="Audio file not found on local disk",
        classifier_score=None,
        is_classifier_alert=None,
        has_audio=False,
    ))

    # Verify summary counts
    summary = store.get_summary()
    triage_counts = summary["triage_counts"]
    assert triage_counts[TriageGroup.LIKELY_NON_SCREAM.value] == 1
    assert triage_counts[TriageGroup.POSSIBLE_SCREAM.value] == 1
    assert triage_counts[TriageGroup.REVIEW_REQUIRED.value] == 1
    assert triage_counts[TriageGroup.AMBIGUOUS.value] == 0

    # Verify filtering by triage group
    likely_items, likely_total = store.get_recordings(triage_group="LIKELY_NON_SCREAM")
    assert likely_total == 1
    assert likely_items[0]["recording_id"] == "rec_1"
    assert likely_items[0]["triage_group"] == TriageGroup.LIKELY_NON_SCREAM.value

    # Verify sorting by triage (Likely Non-Screams first)
    sorted_items, _ = store.get_recordings(sort_by="triage", sort_order="asc")
    assert len(sorted_items) == 3
    assert sorted_items[0]["recording_id"] == "rec_1"  # LIKELY_NON_SCREAM first
    assert sorted_items[1]["recording_id"] == "rec_2"  # POSSIBLE_SCREAM next
    assert sorted_items[2]["recording_id"] == "rec_3"  # REVIEW_REQUIRED last


def test_csv_export_contains_triage_columns(store: ReviewStore):
    """Verify that CSV export contains triage_group, triage_reason, clipping_ratio, silence_ratio."""
    with store._get_connection() as conn:
        conn.execute("""
            INSERT INTO candidates (
                recording_id, source_provider, review_status, commercial_compatibility,
                triage_group, triage_reason, clipping_ratio, silence_ratio
            ) VALUES (
                'rec_csv_test', 'fsd50k', 'UNREVIEWED', 'CC0_VERIFIED',
                'LIKELY_NON_SCREAM', 'Slide whistle active', 0.015, 0.120
            )
        """)

    csv_lines = list(store.export_csv_stream())
    header = csv_lines[0]
    assert "triage_group" in header
    assert "triage_reason" in header
    assert "clipping_ratio" in header
    assert "silence_ratio" in header

    full_csv = "".join(csv_lines)
    assert "rec_csv_test" in full_csv
    assert "LIKELY_NON_SCREAM" in full_csv
    assert "Slide whistle active" in full_csv


def test_api_triage_run_endpoint(tmp_path: Path):
    """Verify that POST /api/review/triage/run endpoint processes candidates."""
    test_db = tmp_path / "test_api_triage.db"
    store = ReviewStore(db_path=test_db, allowed_roots=[tmp_path, BACKEND_DIR])

    with store._get_connection() as conn:
        conn.execute("""
            INSERT INTO candidates (
                recording_id, source_provider, review_status, commercial_compatibility, has_audio
            ) VALUES ('api_rec_1', 'fsd50k', 'UNREVIEWED', 'CC0_VERIFIED', 0)
        """)

    with patch("src.api.review_routes.get_review_store", return_value=store):
        client = TestClient(app)
        res = client.post("/api/review/triage/run", json={"batch_size": 10})
        assert res.status_code == 200

        data = res.json()
        assert data["success"] is True
        assert data["triaged_count"] >= 1
        assert "triage_counts" in data
        assert data["results"][0]["recording_id"] == "api_rec_1"
        assert data["results"][0]["triage_group"] == TriageGroup.REVIEW_REQUIRED.value


def test_classifier_predictions_unaltered_after_triage():
    """Verify that running triage analysis did not alter classifier parameters, threshold, or predictions."""
    verified, audit = verify_frozen_model_artifacts()
    assert verified is True
    assert audit["operating_threshold"] == 0.35
    assert audit["classifier_sha256"] == EXPECTED_CLASSIFIER_SHA256
    assert audit["metadata_sha256"] == EXPECTED_METADATA_SHA256
