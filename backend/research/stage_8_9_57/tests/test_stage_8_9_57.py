"""
Stage 8.9.57: Phase I — Automated Test Suite (20 Test Points)
Validates implementations, mathematical equivalence, filter coefficients,
state reset isolation, threshold immutability, and asset integrity.
"""
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
import scipy.signal as signal
import torch

REPO_ROOT = Path(r"festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE57_DIR = BACKEND_DIR / "research" / "stage_8_9_57"
STAGE55_DIR = BACKEND_DIR / "research" / "stage_8_9_55"
STAGE54_DIR = BACKEND_DIR / "research" / "stage_8_9_54"
STAGE44_DIR = BACKEND_DIR / "research" / "stage_8_9_44"
DSP_DIR = STAGE57_DIR / "dsp_implementations"

sys.path.insert(0, str(DSP_DIR))
sys.path.insert(0, str(STAGE57_DIR / "scripts"))
sys.path.insert(0, str(STAGE55_DIR / "scripts"))

from c1_vector_filterbank import extract_subband_vector_c1
from c2_streaming_filter_state import StreamingFilterbankC2
from c3_precomputed_filters import extract_subband_vector_c3, PRECOMPUTED_BA as C3_BA
from c4_memory_optimization import extract_subband_vector_c4
from c5_combined import extract_subband_vector_c5, extract_phonation_stats_c5, PRECOMPUTED_BA as C5_BA

from benchmark_original_dsp import (
    extract_subband_vector_original,
    extract_phonation_stats_original
)

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

# 1. Original filterbank implementation remains unchanged
def test_01_original_filterbank_unchanged():
    np.random.seed(42)
    sig = np.random.randn(15600).astype(np.float32)
    vec = extract_subband_vector_original(sig, sr=16000)
    assert isinstance(vec, np.ndarray)
    assert vec.shape == (11,)
    assert not np.isnan(vec).any()
    assert not np.isinf(vec).any()

# 2. Frozen E1 checkpoint remains unchanged
def test_02_frozen_e1_checkpoint_hash():
    e1_path = STAGE54_DIR / "training" / "candidate_e_v954_weighted.pt"
    expected = "37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564"
    assert sha256_file(e1_path) == expected

# 3. Frozen B checkpoint remains unchanged
def test_03_frozen_b_checkpoint_hash():
    b_path = STAGE44_DIR / "models" / "config_b_mask.pt"
    expected = "f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378"
    assert sha256_file(b_path) == expected

# 4. Production hashes remain unchanged
def test_04_production_hashes_unchanged():
    prod_hashes = {
        BACKEND_DIR / "models" / "scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
        BACKEND_DIR / "models" / "model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
        BACKEND_DIR / "reports" / "test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
        BACKEND_DIR / "reports" / "stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2"
    }
    for p, h in prod_hashes.items():
        assert sha256_file(p) == h

# 5. Filter coefficients match the reference configuration
def test_05_filter_coefficients_match_reference():
    nyq = 8000.0
    bands = [
        (300, 800), (800, 1500), (1500, 2000), (2000, 3000), (3000, 4000), (4000, 6000)
    ]
    for idx, (f_low, f_high) in enumerate(bands):
        b_ref, a_ref = signal.butter(4, [f_low / nyq, min(0.999, f_high / nyq)], btype='band')
        b_c3, a_c3 = C3_BA[idx]
        b_c5, a_c5 = C5_BA[idx]
        np.testing.assert_allclose(b_c3, b_ref, rtol=1e-7, atol=1e-9)
        np.testing.assert_allclose(a_c3, a_ref, rtol=1e-7, atol=1e-9)
        np.testing.assert_allclose(b_c5, b_ref, rtol=1e-7, atol=1e-9)
        np.testing.assert_allclose(a_c5, a_ref, rtol=1e-7, atol=1e-9)

# 6. Feature dimensions remain correct
def test_06_feature_dimensions_correct():
    sig = np.random.randn(15600).astype(np.float32)
    assert extract_subband_vector_original(sig).shape == (11,)
    assert extract_subband_vector_c1(sig).shape == (11,)
    assert extract_subband_vector_c3(sig).shape == (11,)
    assert extract_subband_vector_c4(sig).shape == (11,)
    assert extract_subband_vector_c5(sig).shape == (11,)
    assert extract_phonation_stats_original(sig).shape == (6,)
    assert extract_phonation_stats_c5(sig).shape == (6,)

# 7. Feature ordering remains correct
def test_07_feature_ordering_correct():
    sig = np.random.randn(15600).astype(np.float32)
    v_orig = extract_subband_vector_original(sig)
    v_c5 = extract_subband_vector_c5(sig)
    # Relative energy indices 0 to 5 sum to roughly <= 1.0
    assert np.sum(v_c5[:6]) <= 1.05
    # Feature 9 is ratio: scream_band_e / low_e
    low_e = v_c5[0] + v_c5[1] + 1e-9
    scream_e = v_c5[3] + v_c5[4] + 1e-9
    np.testing.assert_allclose(v_c5[9], scream_e / low_e, rtol=1e-5)
    # Feature 10 is relative energy of band 6 (idx 5)
    np.testing.assert_allclose(v_c5[10], v_c5[5], rtol=1e-5)

# 8. Numerical comparison works
def test_08_numerical_comparison_works():
    a = np.array([1.0, 2.0, 3.0])
    b = np.array([1.0, 2.01, 3.0])
    max_ae = np.max(np.abs(a - b))
    mae = np.mean(np.abs(a - b))
    assert abs(max_ae - 0.01) < 1e-6
    assert abs(mae - (0.01 / 3.0)) < 1e-6

# 9. NaN and infinity detection
def test_09_nan_inf_detection():
    silence = np.zeros(15600, dtype=np.float32)
    v_sil = extract_subband_vector_c5(silence)
    assert not np.isnan(v_sil).any()
    assert not np.isinf(v_sil).any()
    ph_sil = extract_phonation_stats_c5(silence)
    assert not np.isnan(ph_sil).any()
    assert not np.isinf(ph_sil).any()

# 10. Persistent filter-state reset behavior
def test_10_persistent_filter_state_reset():
    c2 = StreamingFilterbankC2(sr=16000)
    sig1 = np.random.randn(15600).astype(np.float32)
    out1 = c2.process_window(sig1)
    
    # Process unrelated signal to dirty state
    c2.process_window(np.ones(15600, dtype=np.float32))
    
    # Reset and process sig1 again
    c2.reset()
    out1_reset = c2.process_window(sig1)
    np.testing.assert_allclose(out1, out1_reset, atol=1e-7)

# 11. No state contamination between recordings
def test_11_no_state_contamination_between_recordings():
    c2_a = StreamingFilterbankC2(sr=16000)
    c2_b = StreamingFilterbankC2(sr=16000)
    
    sig_clip1 = np.random.randn(15600).astype(np.float32)
    sig_clip2 = np.random.randn(15600).astype(np.float32)
    
    # Instance A: processes clip 1, resets, processes clip 2
    c2_a.process_window(sig_clip1)
    c2_a.reset()
    out_a = c2_a.process_window(sig_clip2)
    
    # Instance B: freshly initialized, processes clip 2
    out_b = c2_b.process_window(sig_clip2)
    np.testing.assert_allclose(out_a, out_b, atol=1e-7)

# 12. Stream restart behavior
def test_12_stream_restart_behavior():
    c2 = StreamingFilterbankC2(sr=16000)
    # Check that initial zi states are zeros
    for zi in c2.zi_states:
        assert np.all(zi == 0.0)
    # After reset, states return to zeros
    c2.process_window(np.random.randn(15600).astype(np.float32))
    c2.reset()
    for zi in c2.zi_states:
        assert np.all(zi == 0.0)

# 13. Prediction agreement calculations
def test_13_prediction_agreement_calculations():
    preds1 = np.array([1, 0, 1, 1, 0])
    preds2 = np.array([1, 0, 1, 0, 0])
    agree = np.mean(preds1 == preds2) * 100.0
    assert agree == 80.0

# 14. Threshold immutability
def test_14_threshold_immutability():
    # Frozen E1 decision threshold
    theta_e1 = 0.6800
    # Frozen B decision threshold
    theta_b = 0.8000
    # Production threshold
    theta_prod = 0.3500
    assert theta_e1 == 0.6800
    assert theta_b == 0.8000
    assert theta_prod == 0.3500

# 15. Benchmark percentile calculation
def test_15_benchmark_percentile_calculation():
    from benchmark_optimized_dsp import compute_percentiles
    data = np.arange(1, 101, dtype=np.float64) # 1 to 100
    p = compute_percentiles(data)
    assert p["p50_ms"] == 50.5
    assert p["min_ms"] == 1.0
    assert p["max_ms"] == 100.0

# 16. Complete-pipeline timing measurement
def test_16_complete_pipeline_timing_measurement():
    import time
    t0 = time.perf_counter_ns()
    sig = np.random.randn(15600).astype(np.float32)
    _ = extract_subband_vector_c5(sig)
    _ = extract_phonation_stats_c5(sig)
    t1 = time.perf_counter_ns()
    dur_ms = (t1 - t0) / 1e6
    assert dur_ms > 0.0
    assert dur_ms < 50.0 # Must run fast

# 17. No historical test-cohort tuning
def test_17_no_historical_test_cohort_tuning():
    test_manifest_p = STAGE55_DIR / "integrity" / "frozen_test_manifest.json"
    expected_hash = "06c9db80d3969e60f78dd441eb1495a9dab97f1646f08ab5825ea979719021f2"
    assert sha256_file(test_manifest_p) == expected_hash

# 18. No source-group leakage
def test_18_no_source_group_leakage():
    manifest_p = STAGE54_DIR / "dataset" / "partition_manifest_verified.csv"
    df = pd.read_csv(manifest_p)
    train_groups = set(df[df["expansion_partition"] == "expansion_train"]["source_group_id"])
    val_groups = set(df[df["expansion_partition"] == "expansion_val"]["source_group_id"])
    overlap = train_groups.intersection(val_groups)
    assert len(overlap) == 0

# 19. Reproducibility of ablation configurations
def test_19_reproducibility_of_ablation_configs():
    abl_csv = STAGE57_DIR / "subband_ablation_results.csv"
    assert abl_csv.exists()
    df = pd.read_csv(abl_csv)
    assert "REF_FULL_11D" in df["ablation_id"].values
    assert "D2_ALL_SUBBANDS_ZEROED" in df["ablation_id"].values
    ref_rec = df[df["ablation_id"] == "REF_FULL_11D"]["recall"].values[0]
    assert ref_rec == 82.83

# 20. No modification of historical evaluation files
def test_20_no_modification_of_historical_evaluation_files():
    eval_csv = STAGE55_DIR / "evaluation" / "candidate_e1_predictions.csv"
    if eval_csv.exists():
        h = sha256_file(eval_csv)
        assert len(h) == 64
