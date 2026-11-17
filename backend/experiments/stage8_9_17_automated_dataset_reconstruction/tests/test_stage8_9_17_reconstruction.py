"""Automated Test Suite for Stage 8.9.17 Automated Dataset Reconstruction & Recalibration.

Validates the 13 required testing categories:
1. Metadata mapping
2. License filtering
3. Audio validation
4. Silence generation
5. Duplicate detection
6. Source-group splitting
7. Leakage detection
8. Class-weight comparisons
9. Probability calibration
10. Digital silence inference
11. Infant crying evaluation
12. Feature parity
13. Production artifact immutability
"""

import csv
import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
import pytest

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = WORKSPACE_DIR.parent.parent

# Frozen production targets and expected SHA-256 hashes
FROZEN_TARGETS = {
    "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
}


def test_production_artifact_immutability():
    """Verify that all 4 frozen production artifacts are strictly unaltered."""
    repo_root = BACKEND_DIR.parent
    for rel_path, expected_hash in FROZEN_TARGETS.items():
        full_path = repo_root / rel_path
        assert full_path.exists(), f"Production artifact missing: {full_path}"
        hasher = hashlib.sha256()
        with open(full_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        actual_hash = hasher.hexdigest()
        assert actual_hash == expected_hash, f"CRITICAL: Production hash mismatch for {rel_path}!"


def test_metadata_mapping():
    """Verify metadata label mappings to canonical categories."""
    import sys
    sys.path.insert(0, str(WORKSPACE_DIR / "src"))
    from metadata_labeler import MetadataLabeler, CATEGORY_MAPPINGS

    assert MetadataLabeler.map_fsd50k_labels(["Screaming"], duration=0.8, clip_info={}) == "SHORT_SCREAM"
    assert MetadataLabeler.map_fsd50k_labels(["Screaming"], duration=3.5, clip_info={}) == "SUSTAINED_SCREAM"
    assert MetadataLabeler.map_fsd50k_labels(["Crying_and_sobbing"], duration=2.0, clip_info={"tags": ["baby", "infant"]}) == "INFANT_CRYING"
    assert MetadataLabeler.map_fsd50k_labels(["Shout"], duration=1.0, clip_info={}) == "SHOUTING_EXCITED_SPEECH"
    assert MetadataLabeler.map_fsd50k_labels(["Cheering"], duration=2.5, clip_info={}) == "CROWD_CHEERING"
    assert "SCREAM_STANDARD" in CATEGORY_MAPPINGS


def test_license_filtering():
    """Verify commercial license whitelisting and non-commercial quarantine."""
    import sys
    sys.path.insert(0, str(WORKSPACE_DIR / "src"))
    from metadata_labeler import MetadataLabeler

    status, eligible = MetadataLabeler.map_license_status("http://creativecommons.org/publicdomain/zero/1.0/")
    assert eligible is True
    assert status == "COMMERCIALLY_ELIGIBLE"

    status, eligible = MetadataLabeler.map_license_status("http://creativecommons.org/licenses/by/3.0/")
    assert eligible is True
    assert status == "COMMERCIALLY_ELIGIBLE"

    status, eligible = MetadataLabeler.map_license_status("http://creativecommons.org/licenses/by-nc/4.0/")
    assert eligible is False
    assert "QUARANTINED" in status


def test_audio_validation(tmp_path):
    """Verify fast audio header inspection and loading validation."""
    import sys
    import soundfile as sf
    sys.path.insert(0, str(WORKSPACE_DIR / "src"))
    from metadata_labeler import validate_audio_metadata, validate_and_load_audio

    # Valid wav
    wav_path = tmp_path / "test_valid.wav"
    sf.write(str(wav_path), np.random.randn(16000).astype(np.float32) * 0.1, 16000)
    rep = validate_audio_metadata(wav_path)
    assert rep["valid"] is True
    assert rep["duration_seconds"] == 1.0

    mono, load_rep = validate_and_load_audio(wav_path, min_duration=0.5)
    assert mono is not None
    assert load_rep["valid"] is True

    # Too short audio
    short_wav = tmp_path / "test_short.wav"
    sf.write(str(short_wav), np.zeros(1600, dtype=np.float32), 16000)
    _, short_rep = validate_and_load_audio(short_wav, min_duration=0.5)
    assert short_rep["valid"] is False


def test_silence_generation():
    """Verify synthetic silence and room tone generation suite."""
    import sys
    sys.path.insert(0, str(WORKSPACE_DIR / "src"))
    from silence_ambient_generator import (
        generate_digital_silence,
        generate_gaussian_noise,
        generate_pink_noise,
        generate_brown_noise,
        generate_room_tone,
    )

    dig = generate_digital_silence(1.0)
    assert len(dig) == 16000
    assert np.all(dig == 0.0)

    gauss = generate_gaussian_noise(1.0, target_rms=1e-3, seed=42)
    assert abs(np.sqrt(np.mean(gauss ** 2)) - 1e-3) < 1e-4

    pink = generate_pink_noise(1.0, target_rms=1e-3, seed=42)
    assert len(pink) == 16000

    brown = generate_brown_noise(1.0, target_rms=1e-3, seed=42)
    assert len(brown) == 16000

    room = generate_room_tone(1.0, target_rms=2e-3, seed=42)
    assert len(room) == 16000


def test_duplicate_detection():
    """Verify audio content hash deduplication logic."""
    import sys
    sys.path.insert(0, str(WORKSPACE_DIR / "src"))
    from metadata_labeler import compute_audio_hash

    buf1 = np.ones(16000, dtype=np.float32) * 0.05
    buf2 = np.ones(16000, dtype=np.float32) * 0.05
    buf3 = np.ones(16000, dtype=np.float32) * 0.06

    h1 = compute_audio_hash(buf1)
    h2 = compute_audio_hash(buf2)
    h3 = compute_audio_hash(buf3)

    assert h1 == h2
    assert h1 != h3


def test_source_group_splitting_and_leakage():
    """Verify source-group partitioning and leakage isolation."""
    manifest_splits = WORKSPACE_DIR / "data" / "manifests" / "source_group_splits.csv"
    assert manifest_splits.exists(), "Splits manifest missing"

    with open(manifest_splits, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) >= 2500

    train_groups = {r["source_group_id"] for r in rows if r["split"] == "train"}
    val_groups = {r["source_group_id"] for r in rows if r["split"] == "val"}
    test_groups = {r["source_group_id"] for r in rows if r["split"] == "test"}

    # Zero overlap across groups
    assert len(train_groups.intersection(val_groups)) == 0
    assert len(train_groups.intersection(test_groups)) == 0
    assert len(val_groups.intersection(test_groups)) == 0

    # Zero overlap across content hashes
    train_hashes = {r["content_hash"] for r in rows if r["split"] == "train" and r["content_hash"]}
    val_hashes = {r["content_hash"] for r in rows if r["split"] == "val" and r["content_hash"]}
    test_hashes = {r["content_hash"] for r in rows if r["split"] == "test" and r["content_hash"]}

    assert len(train_hashes.intersection(val_hashes)) == 0
    assert len(train_hashes.intersection(test_hashes)) == 0
    assert len(val_hashes.intersection(test_hashes)) == 0


def test_stage5_quarantine_isolation():
    """Verify that no Stage 5 test set file or source group exists in the reconstructed dataset."""
    pred_csv = BACKEND_DIR / "reports" / "test_predictions.csv"
    assert pred_csv.exists()

    st5_files = set()
    st5_groups = set()
    with open(pred_csv, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            st5_files.add(r["file_id"])
            st5_groups.add(r["source_group_id"])

    manifest_splits = WORKSPACE_DIR / "data" / "manifests" / "source_group_splits.csv"
    with open(manifest_splits, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for r in rows:
        assert r["file_id"] not in st5_files, f"Quarantine leak: {r['file_id']}"
        assert r["source_group_id"] not in st5_groups, f"Quarantine group leak: {r['source_group_id']}"


def test_feature_parity():
    """Verify feature shapes for YAMNet, Family A, D_v4, and Candidate E."""
    cache_path = WORKSPACE_DIR / "data" / "features_stage8_9_17.npz"
    assert cache_path.exists()
    data = np.load(cache_path, allow_pickle=True)

    assert data["features_yamnet"].shape[1] == 3072
    assert data["features_family_a"].shape[1] == 8
    assert data["features_acoustic"].shape[1] == 30
    assert data["features_d_v4"].shape[1] == 3080
    assert data["features_candidate_e"].shape[1] == 3102


def test_class_weight_and_intercept_collapse_resolution():
    """Verify that reconstructed models have stable negative intercepts <= -3.0."""
    summary_path = WORKSPACE_DIR / "reports" / "stage8_9_17_experiment_summary.json"
    assert summary_path.exists()

    with open(summary_path, "r", encoding="utf-8") as f:
        summary = json.load(f)

    # Historic D_v4 baseline had collapsed intercept around -1.7244
    assert summary["D_v4_Baseline_Historic"]["intercept"] > -2.0

    # Reconstructed models must have recovered intercepts <= -3.0
    assert summary["D_v4_Reconstructed_Balanced"]["intercept"] <= -3.0
    assert summary["D_v4_Reconstructed_Unweighted"]["intercept"] <= -4.0
    assert summary["D_v4_Reconstructed_Calibrated"]["intercept"] <= -3.0


def test_digital_silence_inference_elimination():
    """Verify that reconstructed models output near-zero scream probability on silence (< 5%)."""
    summary_path = WORKSPACE_DIR / "reports" / "stage8_9_17_experiment_summary.json"
    with open(summary_path, "r", encoding="utf-8") as f:
        summary = json.load(f)

    # Historic D_v4 has ~52% silence probability
    assert summary["D_v4_Baseline_Historic"]["key_categories"]["silence_mean_prob"] > 0.40

    # Reconstructed models must have < 2% silence probability
    assert summary["D_v4_Reconstructed_Balanced"]["key_categories"]["silence_mean_prob"] < 0.02
    assert summary["D_v4_Reconstructed_Unweighted"]["key_categories"]["silence_mean_prob"] < 0.02
    assert summary["D_v4_Reconstructed_Calibrated"]["key_categories"]["silence_mean_prob"] < 0.02
    assert summary["D_v4_Reconstructed_Balanced"]["key_categories"]["silence_fpr"] == 0.0


def test_infant_crying_evaluation():
    """Verify infant crying false alarm rate is reduced to 0.0% in reconstructed models."""
    summary_path = WORKSPACE_DIR / "reports" / "stage8_9_17_experiment_summary.json"
    with open(summary_path, "r", encoding="utf-8") as f:
        summary = json.load(f)

    assert summary["D_v4_Reconstructed_Balanced"]["key_categories"]["infant_crying_fpr"] == 0.0
    assert summary["D_v4_Reconstructed_Calibrated"]["key_categories"]["infant_crying_fpr"] == 0.0


def test_acceptance_gate_enforcement():
    """Verify that candidate models failing any gate are strictly marked REJECTED."""
    summary_path = WORKSPACE_DIR / "reports" / "stage8_9_17_experiment_summary.json"
    with open(summary_path, "r", encoding="utf-8") as f:
        summary = json.load(f)

    for mname, mdata in summary.items():
        gates = mdata["acceptance_gates"]
        if not gates["all_gates_passed"]:
            assert gates["decision_status"] == "REJECTED — RESEARCH ONLY"
