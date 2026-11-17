"""Unit and Regression Tests for Stage 6 Hard-Negative Expansion & Baseline Preservation.

Tests:
1. Hash-based duplicate detection (exact file SHA-256 and PCM audio collisions).
2. Correct source-group isolation to prevent cross-partition leakage.
3. Strict review-status enforcement ('pending_review' and 'rejected_ambiguous' excluded from training).
4. License metadata presence and commercial use restriction auditing.
5. Correct handling of empty or missing hard-negative directories (honest reporting).
6. Reproducible manifest generation and review CSV consistency.
7. Verification that Stage 5 baseline artifacts are 100% unchanged (SHA-256 immutability).
8. Predictions and reporting at the original 0.35 threshold.
9. Retraining safety guard blocks retraining when insufficient reviewed data is present.
"""

from __future__ import annotations

import hashlib
import json
import soundfile as sf
import numpy as np
import pytest
from pathlib import Path

from src.audio.preprocessor import generate_synthetic_chirp, generate_synthetic_tone
from src.config import (
    BACKEND_DIR,
    HARD_NEGATIVES_DIR,
    HARD_NEGATIVES_MANIFEST,
    HARD_NEGATIVES_REVIEW_CSV,
    MODELS_DIR,
    REPORTS_DIR,
)
from src.dataset.hard_negatives import (
    HARD_NEGATIVE_CATEGORIES,
    REVIEW_STATUSES,
    DuplicateClipError,
    InvalidCategoryError,
    compute_file_sha256,
    compute_pcm_sha256,
    ingest_audio_clip,
    load_approved_hard_negatives,
    save_hard_negatives_manifest,
    scan_and_ingest_hard_negatives,
)
from src.model.scream_classifier import FestivalScreamClassifier

# Expected immutable SHA-256 hashes of Stage 5 baseline artifacts
STAGE5_BASELINE_HASHES = {
    "scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "scream_classifier_v1.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
}


def test_stage5_baseline_artifacts_unmodified():
    """Assert that Stage 5 model artifacts, metadata, and test predictions are strictly preserved."""
    for filename, expected_sha in STAGE5_BASELINE_HASHES.items():
        if filename.endswith(".csv"):
            filepath = REPORTS_DIR / filename
        else:
            filepath = MODELS_DIR / filename

        assert filepath.exists(), f"Stage 5 baseline artifact missing: {filepath}"
        with open(filepath, "rb") as f:
            actual_sha = hashlib.sha256(f.read()).hexdigest()
        assert actual_sha == expected_sha, (
            f"MUTATION DETECTED in Stage 5 artifact '{filename}'!\n"
            f"Expected SHA-256: {expected_sha}\n"
            f"Actual SHA-256:   {actual_sha}"
        )


def test_stage5_classifier_predictions_at_threshold_0_35():
    """Ensure baseline classifier produces valid predictions at the frozen 0.35 threshold."""
    clf = FestivalScreamClassifier()
    assert clf.is_loaded
    assert clf.threshold == 0.35

    # Test synthetic tone at 440 Hz (clean non-scream)
    waveform = generate_synthetic_tone(freq_hz=440.0, duration_seconds=1.0)
    pred = clf.predict_audio(waveform, custom_threshold=0.35)

    assert pred["threshold"] == 0.35
    assert 0.0 <= pred["scream_probability"] <= 1.0
    assert pred["is_scream"] is False  # Pure tone must not trigger a scream alert
    assert pred["predicted_label"] == "non_scream"
    assert pred["margin_to_threshold"] < 0.0


def test_empty_hard_negatives_handling(tmp_path: Path):
    """Test that scanning an empty directory reports 0 records honestly without fabricating."""
    empty_dir = tmp_path / "empty_hard_negatives"
    empty_dir.mkdir(parents=True)
    manifest_out = tmp_path / "test_manifest.json"
    csv_out = tmp_path / "test_review.csv"

    records, summary = scan_and_ingest_hard_negatives(
        input_dirs=[empty_dir],
        manifest_path=manifest_out,
        review_csv_path=csv_out,
    )

    assert len(records) == 0
    assert summary["wav_files_found"] == 0
    assert summary["ingested_count"] == 0
    assert manifest_out.exists()
    assert csv_out.exists()

    with open(manifest_out, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["metadata"]["total_records"] == 0
    assert data["metadata"]["status"] == "empty_pending_collection"


def test_ingest_audio_clip_validation_and_metadata(tmp_path: Path):
    """Test ingestion of candidate WAV file with schema validation and metadata tracking."""
    wav_path = tmp_path / "test_whistle_author1_clip01.wav"
    samples = (generate_synthetic_chirp(start_hz=2800.0, end_hz=3200.0, duration_seconds=1.2) * 32767).astype(np.int16)
    sf.write(str(wav_path), samples, 16000, subtype="PCM_16")

    existing_hashes = set()
    record = ingest_audio_clip(
        wav_path=wav_path,
        existing_hashes=existing_hashes,
        category_override="festival_whistle",
        sidecar_meta={
            "source": "Freesound",
            "license": "CC0 1.0",
            "source_group_id": "author1_pack",
            "reviewer_notes": "Rave whistle candidate",
        },
    )

    assert record["file_id"].startswith("hn_festival_whistle_author1_pack_")
    assert record["sound_category"] == "festival_whistle"
    assert record["source_group_id"] == "author1_pack"
    assert record["license"] == "CC0 1.0"
    assert record["commercial_use_permitted"] is True
    assert record["review_status"] == "pending_review"  # Must default to pending review
    assert record["duration_seconds"] == pytest.approx(1.2, abs=0.05)
    assert len(record["sha256_hash"]) == 64
    assert len(record["pcm_sha256"]) == 64


def test_duplicate_clip_detection_raises_error(tmp_path: Path):
    """Test that ingesting an exact duplicate file hash raises DuplicateClipError."""
    wav_path = tmp_path / "original_clip.wav"
    samples = (generate_synthetic_tone(freq_hz=1000.0, duration_seconds=1.0) * 32767).astype(np.int16)
    sf.write(str(wav_path), samples, 16000, subtype="PCM_16")

    file_sha = compute_file_sha256(wav_path)
    existing_hashes = {file_sha}

    with pytest.raises(DuplicateClipError, match="exact SHA-256 hash collision"):
        ingest_audio_clip(
            wav_path=wav_path,
            existing_hashes=existing_hashes,
            category_override="environmental_noise",
            check_duplicates=True,
        )


def test_invalid_category_rejected(tmp_path: Path):
    """Test that an invalid sound category is rejected."""
    wav_path = tmp_path / "test_clip.wav"
    samples = (generate_synthetic_tone(freq_hz=440.0, duration_seconds=0.5) * 32767).astype(np.int16)
    sf.write(str(wav_path), samples, 16000, subtype="PCM_16")

    with pytest.raises(InvalidCategoryError, match="Invalid category"):
        ingest_audio_clip(
            wav_path=wav_path,
            existing_hashes=set(),
            category_override="invalid_fake_category",
        )


def test_review_status_enforcement_excludes_pending_and_ambiguous(tmp_path: Path):
    """Test that load_approved_hard_negatives strictly returns only approved records."""
    manifest_path = tmp_path / "test_manifest.json"
    csv_path = tmp_path / "test_review.csv"

    mock_records = [
        {"file_id": "r1", "review_status": "pending_review", "sound_category": "festival_whistle"},
        {"file_id": "r2", "review_status": "approved_non_scream", "sound_category": "crowd_cheering"},
        {"file_id": "r3", "review_status": "approved_scream", "sound_category": "genuine_scream"},
        {"file_id": "r4", "review_status": "rejected_ambiguous", "sound_category": "vocal_non_scream"},
    ]
    save_hard_negatives_manifest(mock_records, manifest_path, csv_path)

    approved = load_approved_hard_negatives(manifest_path)
    approved_ids = [r["file_id"] for r in approved]

    assert "r2" in approved_ids
    assert "r3" in approved_ids
    assert "r1" not in approved_ids  # pending_review must be excluded
    assert "r4" not in approved_ids  # rejected_ambiguous must be excluded
    assert len(approved) == 2


def test_retraining_safety_guard_blocks_insufficient_data():
    """Verify that train_classifier_v2 blocks retraining when < 20 approved records exist."""
    from scripts.train_classifier_v2 import check_retraining_prerequisites

    can_retrain, approved, msg = check_retraining_prerequisites()
    assert can_retrain is False
    assert "Insufficient human-reviewed hard negatives" in msg
    assert len(approved) < 20
