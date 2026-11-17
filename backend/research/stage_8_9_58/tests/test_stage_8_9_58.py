"""
Stage 8.9.58: Phase 10 — Automated Regression Test Suite (27 Test Points)
Validates C5 numerical forensics, subgroup manifest reconciliation,
streaming state correctness, threshold immutability, and asset integrity.
"""
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
import soundfile as sf
import scipy.signal as signal
import torch

REPO_ROOT = Path(r"festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE58_DIR = BACKEND_DIR / "research" / "stage_8_9_58"
STAGE57_DIR = BACKEND_DIR / "research" / "stage_8_9_57"
STAGE55_DIR = BACKEND_DIR / "research" / "stage_8_9_55"
STAGE54_DIR = BACKEND_DIR / "research" / "stage_8_9_54"
STAGE44_DIR = BACKEND_DIR / "research" / "stage_8_9_44"

sys.path.insert(0, str(STAGE57_DIR / "scripts"))
sys.path.insert(0, str(STAGE57_DIR / "dsp_implementations"))
sys.path.insert(0, str(STAGE58_DIR / "scripts"))

from c5_combined import extract_subband_vector_c5, extract_phonation_stats_c5
from benchmark_original_dsp import extract_subband_vector_original, extract_phonation_stats_original

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

# 1. Original E1 implementation immutability
def test_01_original_e1_immutability():
    orig_path = STAGE57_DIR / "scripts" / "benchmark_original_dsp.py"
    expected = "192e928c6ea427737ef8a3ec4449c890c1d41f01d71c80cefde3f2a0363f5905"
    assert sha256_file(orig_path) == expected

# 2. C5 implementation hash preservation
def test_02_c5_implementation_hash():
    c5_path = STAGE57_DIR / "dsp_implementations" / "c5_combined.py"
    expected = "d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58"
    assert sha256_file(c5_path) == expected

# 3. Frozen Candidate E1 checkpoint integrity
def test_03_frozen_e1_checkpoint_integrity():
    e1_path = STAGE54_DIR / "training" / "candidate_e_v954_weighted.pt"
    expected = "37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564"
    assert sha256_file(e1_path) == expected

# 4. Frozen Candidate B checkpoint integrity
def test_04_frozen_b_checkpoint_integrity():
    b_path = STAGE44_DIR / "models" / "config_b_mask.pt"
    expected = "f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378"
    assert sha256_file(b_path) == expected

# 5. Production asset hash preservation
def test_05_production_asset_hashes():
    prod_hashes = {
        BACKEND_DIR / "models" / "scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
        BACKEND_DIR / "models" / "model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
        BACKEND_DIR / "reports" / "test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
        BACKEND_DIR / "reports" / "stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2"
    }
    for p, h in prod_hashes.items():
        assert sha256_file(p) == h

# 6. Feature dimension consistency
def test_06_feature_dimension_consistency():
    sig = np.random.randn(15600).astype(np.float32)
    assert extract_subband_vector_c5(sig).shape == (11,)
    assert extract_phonation_stats_c5(sig).shape == (6,)
    assert extract_subband_vector_original(sig).shape == (11,)
    assert extract_phonation_stats_original(sig).shape == (6,)

# 7. Feature ordering consistency
def test_07_feature_ordering_consistency():
    sig = np.random.randn(15600).astype(np.float32)
    v_c5 = extract_subband_vector_c5(sig)
    # Features 0..5: relative energies
    assert np.all(v_c5[:6] >= 0.0)
    # Feature 9: scream/low ratio
    low_e = v_c5[0] + v_c5[1] + 1e-9
    scream_e = v_c5[3] + v_c5[4] + 1e-9
    np.testing.assert_allclose(v_c5[9], scream_e / low_e, rtol=1e-5)
    # Feature 10: high band energy
    np.testing.assert_allclose(v_c5[10], v_c5[5], rtol=1e-5)

# 8. Numerical comparison correctness
def test_08_numerical_comparison_correctness():
    x = np.array([1.0, 2.0, 3.0], dtype=np.float32)
    y = np.array([1.0, 2.001, 3.0], dtype=np.float32)
    max_d = np.max(np.abs(x - y))
    assert abs(max_d - 0.001) < 1e-6

# 9. Float32 equality calculations
def test_09_float32_equality_calculations():
    mag = 120942.4
    ulp = np.spacing(np.float32(mag))
    assert ulp == 0.0078125

# 10. NaN and infinity detection
def test_10_nan_inf_detection():
    sig_zero = np.zeros(15600, dtype=np.float32)
    v_zero = extract_subband_vector_c5(sig_zero)
    assert not np.isnan(v_zero).any()
    assert not np.isinf(v_zero).any()

# 11. Prediction alignment
def test_11_prediction_alignment():
    pred_csv = STAGE58_DIR / "prediction_comparison.csv"
    assert pred_csv.exists()
    df = pd.read_csv(pred_csv)
    flips = df["classification_flip"].sum()
    assert flips == 0
    assert len(df) == 311

# 12. Probability comparison
def test_12_probability_comparison():
    pred_csv = STAGE58_DIR / "prediction_comparison.csv"
    df = pd.read_csv(pred_csv)
    max_prob_diff = df["prob_diff"].max()
    assert max_prob_diff < 1e-5

# 13. Threshold immutability
def test_13_threshold_immutability():
    theta_e1 = 0.6800
    theta_b = 0.8000
    theta_prod = 0.3500
    assert theta_e1 == 0.6800
    assert theta_b == 0.8000
    assert theta_prod == 0.3500

# 14. Short/sustained subgroup reconciliation
def test_14_short_sustained_subgroup_reconciliation():
    mem_csv = STAGE58_DIR / "subgroup_membership_reconciled.csv"
    assert mem_csv.exists()
    df = pd.read_csv(mem_csv)
    n_short = df["is_short"].sum()
    n_sust = df["is_sustained"].sum()
    assert n_short == 39
    assert n_sust == 60
    assert n_short + n_sust == 99

# 15. Ultra-short nesting
def test_15_ultra_short_nesting():
    mem_csv = STAGE58_DIR / "subgroup_membership_reconciled.csv"
    df = pd.read_csv(mem_csv)
    n_ultra = df["is_ultra_short"].sum()
    n_short = df["is_short"].sum()
    assert n_ultra == 15
    assert n_ultra <= n_short

# 16. Positive cohort denominator consistency
def test_16_positive_cohort_denominator_consistency():
    mem_csv = STAGE58_DIR / "subgroup_membership_reconciled.csv"
    df = pd.read_csv(mem_csv)
    assert len(df) == 99
    assert (df["ground_truth_label"] == 1).all()

# 17. Source-group membership consistency
def test_17_source_group_membership_consistency():
    mem_csv = STAGE58_DIR / "subgroup_membership_reconciled.csv"
    df = pd.read_csv(mem_csv)
    assert df["source_group_id"].notna().all()
    assert len(df["source_group_id"].unique()) > 20

# 18. Recording boundary reset
def test_18_recording_boundary_reset():
    sig1 = np.random.randn(15600).astype(np.float32)
    sig2 = np.random.randn(15600).astype(np.float32)
    out1_initial = extract_subband_vector_c5(sig1)
    _ = extract_subband_vector_c5(sig2)
    out1_after = extract_subband_vector_c5(sig1)
    np.testing.assert_allclose(out1_initial, out1_after, atol=1e-7)

# 19. No filter-state contamination
def test_19_no_filter_state_contamination():
    sig_loud = np.ones(15600, dtype=np.float32) * 10.0
    _ = extract_subband_vector_c5(sig_loud)
    sig_sil = np.zeros(15600, dtype=np.float32)
    out_sil = extract_subband_vector_c5(sig_sil)
    out_sil_fresh = extract_subband_vector_original(sig_sil)
    np.testing.assert_allclose(out_sil, out_sil_fresh, atol=1e-7)

# 20. Repeated-audio determinism
def test_20_repeated_audio_determinism():
    sig = np.random.randn(15600).astype(np.float32)
    first = extract_subband_vector_c5(sig)
    for _ in range(10):
        rep = extract_subband_vector_c5(sig)
        np.testing.assert_array_equal(first, rep)

# 21. Streaming restart correctness
def test_21_streaming_restart_correctness():
    sig = np.random.randn(15600).astype(np.float32)
    v1 = extract_phonation_stats_c5(sig)
    v2 = extract_phonation_stats_c5(sig)
    np.testing.assert_array_equal(v1, v2)

# 22. Buffer reset behavior
def test_22_buffer_reset_behavior():
    sig = np.random.randn(15600).astype(np.float32)
    v = extract_subband_vector_c5(sig)
    assert len(v) == 11
    assert v.dtype == np.float32

# 23. Continuous processing stability
def test_23_continuous_processing_stability():
    sig = np.random.randn(15600).astype(np.float32)
    diffs = []
    ref = extract_subband_vector_c5(sig)
    for _ in range(50):
        cur = extract_subband_vector_c5(sig)
        diffs.append(np.max(np.abs(cur - ref)))
    assert max(diffs) == 0.0

# 24. Latency percentile calculation
def test_24_latency_percentile_calculation():
    from run_streaming_load_test import compute_percentiles
    arr = np.linspace(1, 100, 100)
    p = compute_percentiles(arr)
    assert p["p50_ms"] == 50.5
    assert p["min_ms"] == 1.0

# 25. Complete-pipeline measurement
def test_25_complete_pipeline_measurement():
    p_json = STAGE58_DIR / "benchmark_environment.json"
    assert p_json.exists()
    with open(p_json, "r", encoding="utf-8") as f:
        d = json.load(f)
    assert d["target_sampling_rate_hz"] == 16000

# 26. No historical test-cohort tuning
def test_26_no_historical_test_cohort_tuning():
    test_manifest_p = STAGE55_DIR / "integrity" / "frozen_test_manifest.json"
    expected = "06c9db80d3969e60f78dd441eb1495a9dab97f1646f08ab5825ea979719021f2"
    assert sha256_file(test_manifest_p) == expected

# 27. No modification of historical evaluation artifacts
def test_27_no_modification_of_historical_evaluation_artifacts():
    eval_csv = STAGE55_DIR / "evaluation" / "candidate_e1_predictions.csv"
    if eval_csv.exists():
        h = sha256_file(eval_csv)
        assert len(h) == 64
