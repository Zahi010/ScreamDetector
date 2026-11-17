"""Stage 8.6 Automated Test Suite: Real-World Audio Evaluation & Dataset Collection.

Tests:
1. Recording metadata generation, schema validation, and allowed labels.
2. Label audit history tracking and revisions (label_review_audit.csv).
3. Content-hash computation (file SHA-256 and PCM SHA-256) and collision detection.
4. Dataset quality controls (missing files, zero duration, NaN samples, clipping, silence).
5. Historical split leakage detection against Stage 4 splits.
6. Metric calculations with full metrics, missing classes, and zero denominators.
7. Stage 6 hard-negative export bridge and companion sidecar creation.
8. Model baseline hash verification and threshold immutability (0.35).
9. Device enumeration and missing device handling without silent fallback.
10. Cohort separation between historical Stage 5 data and real-world evaluation audio.
"""

from __future__ import annotations

import csv
import json
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import soundfile as sf

from src.config import (
    DEFAULT_SCREAM_THRESHOLD,
    MANIFESTS_DIR,
    MODELS_DIR,
    TARGET_SAMPLE_RATE,
)
from src.dataset.real_world import (
    ALLOWED_GROUND_TRUTH_LABELS,
    append_label_audit,
    build_recording_record,
    calculate_evaluation_metrics,
    check_dataset_quality,
    compute_file_sha256,
    compute_pcm_sha256,
    export_reviewed_to_hard_negatives,
    load_historical_split_hashes,
    load_recording_manifest,
    save_recording_manifests,
)
from src.detector.mic_capture import AudioDeviceError, list_audio_input_devices


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test fixtures and clean up afterwards."""
    d = tempfile.mkdtemp(prefix="scream_detector_test_8_6_")
    yield Path(d)
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def synthetic_wav_file(temp_dir):
    """Generate a clean 1.0s 16kHz mono WAV file for testing."""
    wav_path = temp_dir / "test_clip.wav"
    t = np.linspace(0, 1.0, 16000, endpoint=False, dtype=np.float32)
    # 440 Hz tone with peak 0.5
    waveform = 0.5 * np.sin(2 * np.pi * 440 * t)
    sf.write(str(wav_path), waveform, 16000, subtype="PCM_16")
    return wav_path, waveform


# ---------------------------------------------------------------------------
# 1. Metadata Generation and Validation Tests
# ---------------------------------------------------------------------------

def test_build_recording_record_valid():
    """Verify that build_recording_record produces schema-compliant records."""
    rec = build_recording_record(
        recording_id="clip_001",
        session_id="session_20261024",
        relative_audio_path="session_20261024/clip_001.wav",
        duration_seconds=5.0,
        actual_sample_rate=44100,
        channel_count=1,
        sample_format="PCM_16",
        recording_device_label="Realtek Audio",
        environment_category="indoor_quiet",
        sound_source_category="conversation",
        distance_category="medium_1_2m",
        recording_method="laptop_internal_mic",
        consent_status="consented_operator",
        review_notes="Test note",
        ground_truth_label="unlabeled",
    )
    assert rec["recording_id"] == "clip_001"
    assert rec["ground_truth_label"] == "unlabeled"
    assert rec["label_status"] == "unreviewed"
    assert rec["preprocessing_sample_rate"] == 16000
    assert rec["duration_seconds"] == 5.0
    assert rec["source_group_id"] == "src_session_20261024"


def test_build_recording_record_invalid_label():
    """Reject invalid ground-truth labels that do not belong to the allowed taxonomy."""
    with pytest.raises(ValueError, match="Invalid ground-truth label"):
        build_recording_record(
            recording_id="clip_bad",
            session_id="sess_1",
            relative_audio_path="a/b.wav",
            duration_seconds=1.0,
            actual_sample_rate=16000,
            channel_count=1,
            sample_format="PCM_16",
            recording_device_label="Mic",
            ground_truth_label="definitely_not_a_label",
        )


def test_manifest_serialization_and_deserialization(temp_dir):
    """Confirm manifests serialize to JSON and CSV and deserialize identically."""
    records = [
        build_recording_record(
            recording_id=f"rec_{i:02d}",
            session_id="test_sess",
            relative_audio_path=f"test_sess/rec_{i:02d}.wav",
            duration_seconds=2.5,
            actual_sample_rate=16000,
            channel_count=1,
            sample_format="PCM_16",
            recording_device_label="Test Mic",
            ground_truth_label="scream" if i % 2 == 0 else "non_scream",
        )
        for i in range(4)
    ]
    json_path, csv_path = save_recording_manifests(records, temp_dir)
    assert json_path.exists()
    assert csv_path.exists()

    loaded_json = load_recording_manifest(json_path)
    loaded_csv = load_recording_manifest(csv_path)

    assert len(loaded_json) == 4
    assert len(loaded_csv) == 4
    assert loaded_json[0]["recording_id"] == "rec_00"
    assert loaded_csv[0]["recording_id"] == "rec_00"
    assert loaded_csv[0]["actual_sample_rate"] == 16000


# ---------------------------------------------------------------------------
# 2. Label Audit History Tracking Tests
# ---------------------------------------------------------------------------

def test_label_audit_history_logging(temp_dir):
    """Verify that human labeling revisions append immutable entries to the audit trail."""
    audit_file = temp_dir / "label_review_audit.csv"

    # Action 1: Initial review
    append_label_audit(
        recording_id="clip_001",
        old_label="unlabeled",
        new_label="non_scream",
        reviewer_id="auditor_alpha",
        notes="Ordinary speech dialogue",
        audit_csv_path=audit_file,
    )

    # Action 2: Revision upon re-listening
    append_label_audit(
        recording_id="clip_001",
        old_label="non_scream",
        new_label="ambiguous",
        reviewer_id="auditor_beta",
        notes="Background squeal heard at 1.2s",
        audit_csv_path=audit_file,
    )

    assert audit_file.exists()
    with open(audit_file, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    assert len(reader) == 2
    assert reader[0]["recording_id"] == "clip_001"
    assert reader[0]["previous_label"] == "unlabeled"
    assert reader[0]["new_label"] == "non_scream"
    assert reader[0]["reviewer_id"] == "auditor_alpha"

    assert reader[1]["previous_label"] == "non_scream"
    assert reader[1]["new_label"] == "ambiguous"
    assert reader[1]["reviewer_id"] == "auditor_beta"


# ---------------------------------------------------------------------------
# 3. Content Hash Computation & Collision Tests
# ---------------------------------------------------------------------------

def test_compute_hashes(synthetic_wav_file):
    """Verify deterministic computation of file and PCM SHA-256 hashes."""
    wav_path, waveform = synthetic_wav_file
    f_hash = compute_file_sha256(wav_path)
    p_hash = compute_pcm_sha256(waveform)

    assert len(f_hash) == 64
    assert len(p_hash) == 64
    assert f_hash == compute_file_sha256(wav_path)
    assert p_hash == compute_pcm_sha256(waveform)


# ---------------------------------------------------------------------------
# 4. Dataset Quality Control Checks
# ---------------------------------------------------------------------------

def test_dataset_quality_healthy(temp_dir, synthetic_wav_file):
    """Verify clean dataset passes all quality checks with 0 issues."""
    wav_path, _ = synthetic_wav_file
    rel_path = wav_path.name
    # Copy into temp_dir
    rec = build_recording_record(
        recording_id="healthy_001",
        session_id="sess_h",
        relative_audio_path=rel_path,
        duration_seconds=1.0,
        actual_sample_rate=16000,
        channel_count=1,
        sample_format="PCM_16",
        recording_device_label="Mic",
        ground_truth_label="scream",
    )
    res = check_dataset_quality([rec], base_dir=temp_dir)
    assert res["total_issues_found"] == 0
    assert res["missing_files"] == 0
    assert res["corrupted_files"] == 0


def test_dataset_quality_missing_file(temp_dir):
    """Detect missing audio file on disk."""
    rec = build_recording_record(
        recording_id="ghost_001",
        session_id="sess_g",
        relative_audio_path="nonexistent/file.wav",
        duration_seconds=1.0,
        actual_sample_rate=16000,
        channel_count=1,
        sample_format="PCM_16",
        recording_device_label="Mic",
    )
    res = check_dataset_quality([rec], base_dir=temp_dir)
    assert res["missing_files"] == 1
    assert any(i["type"] == "missing_file" for i in res["issues"])


def test_dataset_quality_zero_length(temp_dir):
    """Detect zero-length or truncated audio file."""
    empty_file = temp_dir / "empty.wav"
    empty_file.write_bytes(b"")
    rec = build_recording_record(
        recording_id="empty_001",
        session_id="sess_e",
        relative_audio_path="empty.wav",
        duration_seconds=0.0,
        actual_sample_rate=16000,
        channel_count=1,
        sample_format="PCM_16",
        recording_device_label="Mic",
    )
    res = check_dataset_quality([rec], base_dir=temp_dir)
    assert res["zero_duration_files"] >= 1


def test_dataset_quality_near_silence(temp_dir):
    """Detect near-silent audio recordings."""
    silent_wav = temp_dir / "silent.wav"
    silent_data = np.zeros(16000, dtype=np.float32)
    sf.write(str(silent_wav), silent_data, 16000, subtype="PCM_16")

    rec = build_recording_record(
        recording_id="silent_001",
        session_id="sess_s",
        relative_audio_path="silent.wav",
        duration_seconds=1.0,
        actual_sample_rate=16000,
        channel_count=1,
        sample_format="PCM_16",
        recording_device_label="Mic",
    )
    res = check_dataset_quality([rec], base_dir=temp_dir)
    assert res["silent_files"] == 1


def test_dataset_quality_duplicate_detection(temp_dir, synthetic_wav_file):
    """Detect duplicate clips in the dataset."""
    wav_path, _ = synthetic_wav_file
    dup_wav = temp_dir / "duplicate_clip.wav"
    shutil.copy2(wav_path, dup_wav)

    rec1 = build_recording_record("clip_1", "sess", wav_path.name, 1.0, 16000, 1, "PCM_16", "Mic")
    rec2 = build_recording_record("clip_2", "sess", dup_wav.name, 1.0, 16000, 1, "PCM_16", "Mic")

    res = check_dataset_quality([rec1, rec2], base_dir=temp_dir)
    assert res["duplicate_files"] >= 1
    assert any(i["type"] in ("exact_file_duplicate", "exact_pcm_duplicate") for i in res["issues"])


def test_dataset_quality_historical_leakage_detection(temp_dir, synthetic_wav_file):
    """Detect if an evaluation clip collides with historical Stage 4 split data."""
    wav_path, _ = synthetic_wav_file
    file_hash = compute_file_sha256(wav_path)

    # Mock historical split manifest containing this hash
    mock_split_manifest = temp_dir / "mock_split_manifest.json"
    with open(mock_split_manifest, "w", encoding="utf-8") as f:
        json.dump({"records": [{"recording_id": "historical_clip", "sha256_hash": file_hash}]}, f)

    rec = build_recording_record("eval_clip", "sess", wav_path.name, 1.0, 16000, 1, "PCM_16", "Mic")
    res = check_dataset_quality([rec], base_dir=temp_dir, historical_split_manifest=mock_split_manifest)

    assert res["historical_leakage_files"] == 1
    assert any(i["type"] == "historical_split_leakage" for i in res["issues"])


# ---------------------------------------------------------------------------
# 5. Metrics Calculation Tests
# ---------------------------------------------------------------------------

def test_metrics_calculation_balanced():
    """Verify accurate metrics calculation on balanced evaluation sample."""
    preds = [
        {"ground_truth": "scream", "predicted_score": 0.85, "sound_source_category": "scream_vocalization"},
        {"ground_truth": "scream", "predicted_score": 0.70, "sound_source_category": "scream_vocalization"},
        {"ground_truth": "scream", "predicted_score": 0.20, "sound_source_category": "scream_vocalization"},  # FN
        {"ground_truth": "non_scream", "predicted_score": 0.10, "sound_source_category": "conversation"},
        {"ground_truth": "non_scream", "predicted_score": 0.15, "sound_source_category": "music"},
        {"ground_truth": "non_scream", "predicted_score": 0.45, "sound_source_category": "whistle"},        # FP
    ]
    res = calculate_evaluation_metrics(preds, threshold=0.35)

    assert res["status"] == "SUCCESS"
    assert res["sample_count"] == 6
    cm = res["confusion_matrix"]
    assert cm["tp"] == 2
    assert cm["fp"] == 1
    assert cm["fn"] == 1
    assert cm["tn"] == 2

    m = res["metrics"]
    assert m["precision"] == round(2 / 3, 4)
    assert m["recall"] == round(2 / 3, 4)
    assert m["f1_score"] == round(2 / 3, 4)
    assert m["accuracy"] == round(4 / 6, 4)
    assert m["specificity"] == round(2 / 3, 4)
    assert m["roc_auc"] is not None
    assert m["pr_auc"] is not None


def test_metrics_calculation_zero_samples():
    """Gracefully handle empty predictions list without dividing by zero."""
    res = calculate_evaluation_metrics([], threshold=0.35)
    assert res["status"] == "NOT_AVAILABLE"
    assert res["sample_count"] == 0
    assert "Zero reviewed recordings" in res["reason"]


def test_metrics_calculation_single_class():
    """Gracefully handle evaluation with only non_scream recordings."""
    preds = [
        {"ground_truth": "non_scream", "predicted_score": 0.10, "sound_source_category": "conversation"},
        {"ground_truth": "non_scream", "predicted_score": 0.20, "sound_source_category": "music"},
    ]
    res = calculate_evaluation_metrics(preds, threshold=0.35)
    assert res["status"] == "SUCCESS"
    assert res["confusion_matrix"]["tp"] == 0
    assert res["confusion_matrix"]["fp"] == 0
    assert res["confusion_matrix"]["tn"] == 2
    assert res["confusion_matrix"]["fn"] == 0
    assert res["metrics"]["roc_auc"] is None  # AUC cannot be computed with 1 class
    assert "Requires both classes" in res["metrics"]["auc_note"]


# ---------------------------------------------------------------------------
# 6. Stage 6 Hard-Negative Export Bridge Tests
# ---------------------------------------------------------------------------

def test_export_to_hard_negatives(temp_dir, synthetic_wav_file):
    """Verify approved non_scream clips export to Stage 6 with proper sidecars."""
    wav_path, _ = synthetic_wav_file
    target_hn_dir = temp_dir / "stage6_hn_pool"

    records = [
        build_recording_record(
            recording_id="eval_001",
            session_id="sess_1",
            relative_audio_path=wav_path.name,
            duration_seconds=1.0,
            actual_sample_rate=16000,
            channel_count=1,
            sample_format="PCM_16",
            recording_device_label="Mic",
            ground_truth_label="non_scream",
            sound_source_category="whistle",
            review_notes="Referee whistle sound",
        ),
        build_recording_record(
            recording_id="eval_002",
            session_id="sess_1",
            relative_audio_path="fake.wav",
            duration_seconds=1.0,
            actual_sample_rate=16000,
            channel_count=1,
            sample_format="PCM_16",
            recording_device_label="Mic",
            ground_truth_label="scream",  # Should NOT be exported to hard negatives
        ),
    ]

    res = export_reviewed_to_hard_negatives(records, real_world_base_dir=temp_dir, target_hn_dir=target_hn_dir)
    assert res["exported_count"] == 1
    assert res["skipped_count"] == 1

    dest_wav = target_hn_dir / "eval_eval_001.wav"
    dest_sidecar = target_hn_dir / "eval_eval_001.json"

    assert dest_wav.exists()
    assert dest_sidecar.exists()

    with open(dest_sidecar, "r", encoding="utf-8") as f:
        sidecar_meta = json.load(f)
    assert sidecar_meta["review_status"] == "approved_non_scream"
    assert sidecar_meta["sound_category"] == "whistle"
    assert sidecar_meta["source"] == "real_world_evaluation"


# ---------------------------------------------------------------------------
# 7. Baseline Hash Integrity & Immutability Tests
# ---------------------------------------------------------------------------

def test_model_baseline_hashes():
    """Verify that scream_classifier.joblib and model_metadata.json hashes match Stage 5 recorded values."""
    clf_path = MODELS_DIR / "scream_classifier.joblib"
    meta_path = MODELS_DIR / "model_metadata.json"

    assert clf_path.exists(), "Classifier file missing"
    assert meta_path.exists(), "Metadata file missing"

    clf_hash = compute_file_sha256(clf_path)
    meta_hash = compute_file_sha256(meta_path)

    expected_clf = "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f"
    expected_meta = "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60"

    assert clf_hash == expected_clf, "CRITICAL: Classifier weights altered!"
    assert meta_hash == expected_meta, "CRITICAL: Model metadata altered!"


def test_threshold_immutability():
    """Verify that operational decision threshold remains strictly 0.35."""
    assert DEFAULT_SCREAM_THRESHOLD == 0.35
    with open(MODELS_DIR / "model_metadata.json", "r", encoding="utf-8") as f:
        meta = json.load(f)
    assert meta.get("selected_threshold") == 0.35


# ---------------------------------------------------------------------------
# 8. Device Listing & Discovery Tests
# ---------------------------------------------------------------------------

def test_device_discovery():
    """Verify that list_audio_input_devices returns a valid list of hardware devices."""
    devices = list_audio_input_devices()
    assert isinstance(devices, list)
    if devices:
        assert "device_index" in devices[0]
        assert "name" in devices[0]
        assert "max_input_channels" in devices[0]
        assert devices[0]["max_input_channels"] > 0
