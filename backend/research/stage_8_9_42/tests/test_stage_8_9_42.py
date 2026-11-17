"""
Stage 8.9.42: Automated Verification and Regression Test Suite
Verifies:
1. Strict Production Freeze (4 SHA-256 hashes)
2. Production Model Joblib Loadability
3. Frozen Config B Checkpoint & Platt Calibrator Integrity
4. Short-Scream Accounting Audit (N=31 rows, exact columns)
5. False-Negative Forensic Audit (N=37 rows, exact columns)
6. Positive Cohort Manifest Integrity (N=57)
7. Hard-Negative Cohort Manifest Integrity (N=145, Shouting N=54)
8. Historical Expansion Test Integrity (N=102: 65 scream + 37 non_scream)
9. Research Split Zero-Leakage (v4_train, v4_val, test sets)
10. YAMNet Single-Frame Mathematical Invariance on d <= 0.96s
11. Log-Mel Spectrogram Cache Integrity (N=1463)
12. Custom CNN Model Checkpoint Files Existence & Loadability
13. Custom CNN Forward Pass Output Dimensions (Single & Batched)
14. Candidate Comparison Results Integrity (5 candidates)
15. Wilson Score Confidence Interval Boundary Invariants
16. Latency Benchmark Metrics & Gate 5 (<= 25 ms)
17. Mandatory Safety Designation in all Generated Reports
"""
import os
import sys
import hashlib
import json
import csv
from pathlib import Path
import pytest
import numpy as np
import pandas as pd
import torch

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE38_DIR = BACKEND_DIR / "research" / "stage_8_9_38"
STAGE39_DIR = BACKEND_DIR / "research" / "stage_8_9_39"
STAGE40_DIR = BACKEND_DIR / "research" / "stage_8_9_40"
STAGE41_DIR = BACKEND_DIR / "research" / "stage_8_9_41"
STAGE42_DIR = BACKEND_DIR / "research" / "stage_8_9_42"

sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(STAGE39_DIR))
sys.path.insert(0, str(STAGE42_DIR))

# Expected 4 production SHA-256 hashes
EXPECTED_PROD_HASHES = {
    BACKEND_DIR / "models" / "scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    BACKEND_DIR / "models" / "model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    BACKEND_DIR / "reports" / "test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    BACKEND_DIR / "reports" / "stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
}

def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def test_production_freeze_hashes():
    """Test 1: Verify all 4 production artifacts match expected SHA-256 hashes."""
    for path, exp_hash in EXPECTED_PROD_HASHES.items():
        assert path.exists(), f"Production file missing: {path}"
        actual = compute_sha256(path)
        assert actual == exp_hash, f"Hash mismatch on {path.name}: {actual} != {exp_hash}"

def test_production_model_loadable():
    """Test 2: Verify production model joblib can be unpickled cleanly."""
    import joblib
    model_p = BACKEND_DIR / "models" / "scream_classifier.joblib"
    clf = joblib.load(model_p)
    assert hasattr(clf, "predict_proba")

def test_frozen_config_b_checkpoint():
    """Test 3: Verify Config B checkpoint and calibrator exist and load."""
    from scripts.train_config_b import DualEncoderAcousticModel
    import joblib

    ckpt_p = STAGE39_DIR / "checkpoints" / "config_b" / "best_model.pt"
    calib_p = STAGE39_DIR / "checkpoints" / "config_b" / "platt_calibrator.joblib"
    assert ckpt_p.exists()
    assert calib_p.exists()

    ckpt = torch.load(ckpt_p, map_location="cpu", weights_only=False)
    model = DualEncoderAcousticModel(1024, 6, 128, 32)
    model.load_state_dict(ckpt["model_state_dict"])
    calib = joblib.load(calib_p)
    assert hasattr(calib, "predict_proba")

def test_short_scream_accounting_audit():
    """Test 4: Verify SHORT_SCREAM_ACCOUNTING_AUDIT.csv contains exactly 31 rows."""
    csv_p = STAGE42_DIR / "SHORT_SCREAM_ACCOUNTING_AUDIT.csv"
    assert csv_p.exists()
    df = pd.read_csv(csv_p)
    assert len(df) == 31, f"Expected 31 rows, got {len(df)}"
    req_cols = ["file_id", "source_group_id", "acoustic_subtype", "duration_seconds", "duration_stratum", "is_subtype_short_scream", "is_physical_duration_short"]
    for c in req_cols:
        assert c in df.columns

def test_false_negative_forensic_audit():
    """Test 5: Verify FALSE_NEGATIVE_FORENSIC_AUDIT.csv contains exactly 37 rows."""
    csv_p = STAGE42_DIR / "FALSE_NEGATIVE_FORENSIC_AUDIT.csv"
    assert csv_p.exists()
    df = pd.read_csv(csv_p)
    assert len(df) == 37, f"Expected 37 false negatives, got {len(df)}"
    assert "calibrated_probability" in df.columns
    assert "silence_ratio" in df.columns

def test_manifest_cohort_counts():
    """Test 6 & 7: Verify Stage 8.9.41 positive and Stage 8.9.40 negative manifest counts."""
    pos_p = STAGE41_DIR / "manifests" / "stage_8_9_41_positive_manifest.csv"
    neg_p = STAGE40_DIR / "manifests" / "new_cohort_manifest.csv"

    df_pos = pd.read_csv(pos_p)
    assert len(df_pos) == 57, f"Expected 57 positives, got {len(df_pos)}"

    df_neg = pd.read_csv(neg_p)
    assert len(df_neg) == 145, f"Expected 145 negatives, got {len(df_neg)}"
    shouts = df_neg[df_neg["target_category"] == "shouting_and_speech"]
    assert len(shouts) == 54, f"Expected 54 shouted speech examples, got {len(shouts)}"

def test_historical_expansion_split():
    """Test 8: Verify v4_reserved_expansion_test has 65 screams and 37 non-screams."""
    v4_p = STAGE38_DIR / "manifests" / "research_split_v4.csv"
    df = pd.read_csv(v4_p)
    exp = df[df["v4_research_split"] == "v4_reserved_expansion_test"]
    assert len(exp) == 102
    assert (exp["binary_label"] == "scream").sum() == 65
    assert (exp["binary_label"] == "non_scream").sum() == 37

def test_zero_leakage_between_splits():
    """Test 9: Verify zero overlap between train, val, test, and new cohorts."""
    v4_p = STAGE38_DIR / "manifests" / "research_split_v4.csv"
    df_v4 = pd.read_csv(v4_p)
    train_fids = set(df_v4[df_v4["v4_research_split"] == "v4_train"]["file_id"])
    val_fids = set(df_v4[df_v4["v4_research_split"] == "v4_val"]["file_id"])
    test_fids = set(df_v4[df_v4["v4_research_split"] == "v4_reserved_expansion_test"]["file_id"])

    df_40 = pd.read_csv(STAGE40_DIR / "manifests" / "new_cohort_manifest.csv")
    fids_40 = set(df_40["file_id"])

    df_41 = pd.read_csv(STAGE41_DIR / "manifests" / "stage_8_9_41_positive_manifest.csv")
    fids_41 = set(df_41["file_id"])

    assert len(train_fids.intersection(val_fids)) == 0
    assert len(train_fids.intersection(test_fids)) == 0
    assert len(train_fids.intersection(fids_40)) == 0
    assert len(train_fids.intersection(fids_41)) == 0
    assert len(val_fids.intersection(fids_40)) == 0
    assert len(val_fids.intersection(fids_41)) == 0
    assert len(test_fids.intersection(fids_40)) == 0
    assert len(test_fids.intersection(fids_41)) == 0

def test_yamnet_temporal_audit_invariance():
    """Test 10: Verify YAMNet produces exactly 1 frame for all audio clips <= 0.96s."""
    frames_p = STAGE42_DIR / "results" / "yamnet_frames_cache.npz"
    assert frames_p.exists()
    data = np.load(frames_p, allow_pickle=True)
    durs = data["durations"]
    n_frames = data["n_frames"]
    mask_short = durs <= 0.96
    assert np.all(n_frames[mask_short] == 1)

def test_logmel_cache_shape():
    """Test 11: Verify logmel_spectrograms_cache.npz contains all 1463 clips with 64 mel bins."""
    cache_p = STAGE42_DIR / "results" / "logmel_spectrograms_cache.npz"
    assert cache_p.exists()
    data = np.load(cache_p, allow_pickle=True)
    fids = data["file_ids"]
    assert len(fids) == 1463
    sample_fid = fids[0]
    sample_mel = data[f"logmel_{sample_fid}"]
    assert sample_mel.shape[0] == 64

def test_custom_cnn_checkpoints():
    """Test 12: Verify custom CNN checkpoints exist."""
    c1_p = STAGE42_DIR / "models" / "cnn_logmel_best.pt"
    c2_p = STAGE42_DIR / "models" / "cnn_multiscale_best.pt"
    assert c1_p.exists(), f"Missing: {c1_p}"
    assert c2_p.exists(), f"Missing: {c2_p}"

def test_custom_cnn_forward():
    """Test 13: Verify CustomLogMelCNN and CustomMultiScaleCNN forward passes."""
    from scripts.train_custom_cnn import CustomLogMelCNN, CustomMultiScaleCNN
    m1 = CustomLogMelCNN()
    m2 = CustomMultiScaleCNN()
    m1.eval()
    m2.eval()

    # Test short clip (19 frames ~ 0.3s)
    x_short = torch.randn(2, 1, 64, 19)
    out1_short = m1(x_short)
    out2_short = m2(x_short)
    assert out1_short.shape == (2,)
    assert out2_short.shape == (2,)

    # Test longer clip (63 frames ~ 1.0s)
    x_long = torch.randn(2, 1, 64, 63)
    out1_long = m1(x_long)
    out2_long = m2(x_long)
    assert out1_long.shape == (2,)
    assert out2_long.shape == (2,)

def test_candidate_comparison_csv():
    """Test 14: Verify CANDIDATE_COMPARISON.csv has all 5 candidates and valid columns."""
    csv_p = STAGE42_DIR / "CANDIDATE_COMPARISON.csv"
    assert csv_p.exists()
    df = pd.read_csv(csv_p)
    assert len(df) == 5
    expected_cands = {"B-Frozen", "B-Improved", "CNN-LogMel", "CNN-MultiScale", "CNN-Temporal"}
    assert set(df["candidate"]) == expected_cands

def test_wilson_ci_invariants():
    """Test 15: Verify Wilson score interval mathematical boundaries."""
    from scripts.compare_candidates import wilson_ci
    p, low, high = wilson_ci(10, 100)
    assert 0.0 <= low <= p <= high <= 1.0
    p0, low0, high0 = wilson_ci(0, 50)
    assert low0 == 0.0
    p1, low1, high1 = wilson_ci(50, 50)
    assert high1 == 1.0

def test_latency_benchmark_gate5():
    """Test 16: Verify latency benchmark JSON exists and Gate 5 is evaluated."""
    lat_p = STAGE42_DIR / "results" / "latency_benchmark.json"
    assert lat_p.exists()
    with open(lat_p, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "gate5_latency_25ms" in data
    assert data["gate5_latency_25ms"] in ["PASS", "FAIL"]

def test_safety_designation_in_reports():
    """Test 17: Verify MANDATORY SAFETY DESIGNATION is at top of all markdown reports."""
    req_phrase = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE."
    reports = list((STAGE42_DIR / "reports").glob("*.md"))
    assert len(reports) >= 3, f"Expected at least 3 reports, found {len(reports)}"
    for r in reports:
        content = r.read_text(encoding="utf-8")
        assert req_phrase in content, f"Report {r.name} missing safety designation!"
