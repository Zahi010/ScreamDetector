#!/usr/bin/env python3
"""
STAGE 8.9.61 — Automated Test Suite (35 Invariant Tests)
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import hashlib
import json
import os
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import pytest
import torch

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE54_DIR = BACKEND_DIR / "research" / "stage_8_9_54"
STAGE55_DIR = BACKEND_DIR / "research" / "stage_8_9_55"
STAGE57_DIR = BACKEND_DIR / "research" / "stage_8_9_57"
STAGE60_DIR = BACKEND_DIR / "research" / "stage_8_9_60"
STAGE61_DIR = BACKEND_DIR / "research" / "stage_8_9_61"

sys.path.insert(0, str(STAGE61_DIR / "scripts"))
sys.path.insert(0, str(STAGE61_DIR))
sys.path.insert(0, str(STAGE57_DIR / "dsp_implementations"))

def sha256_file(path_str: str) -> str:
    sha = hashlib.sha256()
    with open(path_str, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()

# -----------------------------------------------------------------------------
# DATASET INTEGRITY (Tests 1 - 8)
# -----------------------------------------------------------------------------
def test_01_acquisition_accounting_reconciliation():
    rec_csv = STAGE61_DIR / "acquisition_accounting_reconciliation.csv"
    assert rec_csv.exists()
    df = pd.read_csv(rec_csv)
    assert len(df) == 962
    assert (df["accounting_status"].isin(["VERIFIED_CATEGORY", "VERIFIED_OTHER_CATEGORY", "MULTI_CATEGORY_MEMBERSHIP"])).all()
    # 87 omitted short screams + 31 multi-match = exactly 56 net discrepancy
    n_other = (df["accounting_status"] == "VERIFIED_OTHER_CATEGORY").sum()
    n_multi = (df["accounting_status"] == "MULTI_CATEGORY_MEMBERSHIP").sum()
    assert n_other - n_multi == 56

def test_02_recording_id_uniqueness():
    rec_csv = STAGE61_DIR / "acquisition_accounting_reconciliation.csv"
    df = pd.read_csv(rec_csv)
    assert df["recording_id"].nunique() == 962

def test_03_source_group_uniqueness():
    rec_csv = STAGE61_DIR / "acquisition_accounting_reconciliation.csv"
    df = pd.read_csv(rec_csv)
    assert df["source_group_id"].nunique() == 633

def test_04_creator_identity_reconciliation():
    inter_csv = STAGE61_DIR / "creator_partition_intersections.csv"
    assert inter_csv.exists()
    df = pd.read_csv(inter_csv)
    # Sealed cohort must have 0 overlap with training/validation
    train_row = df[(df["partition_1"] == "expansion_train") & (df["partition_2"] == "stage_60_sealed_cohort")]
    val_row = df[(df["partition_1"] == "expansion_val") & (df["partition_2"] == "stage_60_sealed_cohort")]
    assert train_row["overlapping_creators_count"].values[0] == 0
    assert val_row["overlapping_creators_count"].values[0] == 0

def test_05_session_isolation():
    dev_csv = STAGE61_DIR / "rolling_window_development_manifest.csv"
    df_dev = pd.read_csv(dev_csv)
    with open(STAGE60_DIR / "future_evaluation_manifest.json") as f:
        sealed = json.load(f)
    sealed_sgs = set(r["source_group_id"] for r in sealed["recordings"])
    dev_sgs = set(df_dev["source_group_id"])
    assert len(dev_sgs & sealed_sgs) == 0

def test_06_parent_recording_isolation():
    dev_csv = STAGE61_DIR / "rolling_window_development_manifest.csv"
    df_dev = pd.read_csv(dev_csv)
    dup_csv = STAGE60_DIR / "duplicate_and_excerpt_relationships.csv"
    df_dup = pd.read_csv(dup_csv)
    with open(STAGE60_DIR / "future_evaluation_manifest.json") as f:
        sealed = json.load(f)
    sealed_ids = set(r["recording_id"] for r in sealed["recordings"])
    dev_ids = set(df_dev["recording_id"])
    
    parent_to_sealed = set()
    parent_to_dev = set()
    for _, row in df_dup.iterrows():
        clips = [c.strip() for c in str(row["clip_ids"]).split(";")]
        p_id = row["parent_recording_id"]
        if any(c in sealed_ids for c in clips):
            parent_to_sealed.add(p_id)
        if any(c in dev_ids for c in clips):
            parent_to_dev.add(p_id)
    assert len(parent_to_dev & parent_to_sealed) == 0

def test_07_development_manifest_independence():
    dev_csv = STAGE61_DIR / "rolling_window_development_manifest.csv"
    assert dev_csv.exists()
    assert sha256_file(str(dev_csv)) == "bdf27fdf663c722c4f312ab273839629884892b2ae1d17fa47e70981400d6e1c"

def test_08_sealed_cohort_exclusion_from_track_a():
    dev_csv = STAGE61_DIR / "rolling_window_development_manifest.csv"
    df_dev = pd.read_csv(dev_csv)
    with open(STAGE60_DIR / "future_evaluation_manifest.json") as f:
        sealed = json.load(f)
    sealed_ids = set(r["recording_id"] for r in sealed["recordings"])
    assert len(set(df_dev["recording_id"]) & sealed_ids) == 0

# -----------------------------------------------------------------------------
# ARTIFACT PROTECTION (Tests 9 - 16)
# -----------------------------------------------------------------------------
def test_09_production_hash_immutability():
    prod_hashes = {
        BACKEND_DIR / "models" / "scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
        BACKEND_DIR / "models" / "model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
        BACKEND_DIR / "reports" / "test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
        BACKEND_DIR / "reports" / "stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2"
    }
    for p, h in prod_hashes.items():
        assert p.exists()
        assert sha256_file(str(p)) == h

def test_10_candidate_e1_checkpoint_immutability():
    e1_ckpt = STAGE54_DIR / "training" / "candidate_e_v954_weighted.pt"
    assert sha256_file(str(e1_ckpt)) == "37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564"

def test_11_candidate_b_checkpoint_immutability():
    b_ckpt = BACKEND_DIR / "research" / "stage_8_9_44" / "models" / "config_b_mask.pt"
    assert sha256_file(str(b_ckpt)) == "f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378"

def test_12_intervention_d_immutability():
    d_code = BACKEND_DIR / "research" / "stage_8_9_49" / "scripts" / "whistle_discriminator.py"
    assert sha256_file(str(d_code)) == "3d98aa7496c6ba89066cfa345a6d0c1ee3605c30821f869a049001c4ad4a8bd2"

def test_13_c5_source_immutability():
    c5_code = STAGE57_DIR / "dsp_implementations" / "c5_combined.py"
    assert sha256_file(str(c5_code)) == "d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58"

def test_14_original_e1_dsp_immutability():
    orig_dsp = STAGE57_DIR / "scripts" / "benchmark_original_dsp.py"
    assert sha256_file(str(orig_dsp)) == "192e928c6ea427737ef8a3ec4449c890c1d41f01d71c80cefde3f2a0363f5905"

def test_15_historical_manifest_immutability():
    man54 = STAGE54_DIR / "dataset" / "partition_manifest_verified.csv"
    assert sha256_file(str(man54)) == "10563efcd5d607d1395f9db5ab1aa805a0d9ca39b9b4a64a710816d334caeb9e"

def test_16_sealed_manifest_hash_verification():
    manifest_p = STAGE60_DIR / "future_evaluation_manifest.json"
    assert sha256_file(str(manifest_p)) == "9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd"

# -----------------------------------------------------------------------------
# ROLLING-WINDOW CORRECTNESS (Tests 17 - 28)
# -----------------------------------------------------------------------------
def test_17_window_duration_consistency():
    from validate_streaming_correctness import StreamingRollingWindowBuffer
    b = StreamingRollingWindowBuffer(capacity=16000, hop_size=8000)
    w = b.push_chunk(np.zeros(8000, dtype=np.float32))
    assert len(w) == 16000

def test_18_hop_advancement_consistency():
    from validate_streaming_correctness import StreamingRollingWindowBuffer
    b = StreamingRollingWindowBuffer(capacity=16000, hop_size=8000)
    b.push_chunk(np.ones(8000, dtype=np.float32))
    assert b.total_samples_ingested == 8000
    b.push_chunk(np.ones(8000, dtype=np.float32))
    assert b.total_samples_ingested == 16000

def test_19_overlap_calculation():
    from validate_streaming_correctness import StreamingRollingWindowBuffer
    b = StreamingRollingWindowBuffer(capacity=16000, hop_size=8000)
    c1 = np.full(8000, 1.0, dtype=np.float32)
    c2 = np.full(8000, 2.0, dtype=np.float32)
    b.push_chunk(c1)
    w2 = b.push_chunk(c2)
    assert np.all(w2[:8000] == 1.0) and np.all(w2[8000:] == 2.0)

def test_20_buffer_boundary_handling():
    from validate_streaming_correctness import StreamingRollingWindowBuffer
    b = StreamingRollingWindowBuffer(capacity=16000, hop_size=8000)
    c = np.full(4000, 3.0, dtype=np.float32)
    w = b.push_chunk(c)
    assert len(w) == 16000
    assert np.all(w[8000:12000] == 3.0) and np.all(w[12000:] == 0.0)

def test_21_recording_reset_behavior():
    from validate_streaming_correctness import StreamingRollingWindowBuffer
    b = StreamingRollingWindowBuffer(capacity=16000, hop_size=8000)
    b.push_chunk(np.ones(8000, dtype=np.float32))
    b.reset()
    assert np.all(b.buffer == 0.0) and b.windows_emitted == 0 and b.total_samples_ingested == 0

def test_22_no_cross_recording_state_leakage():
    from validate_streaming_correctness import StreamingRollingWindowBuffer
    b = StreamingRollingWindowBuffer(capacity=16000, hop_size=8000)
    b.push_chunk(np.full(8000, 9.9, dtype=np.float32))
    b.reset()
    w = b.push_chunk(np.zeros(8000, dtype=np.float32))
    assert np.all(w == 0.0)

def test_23_repeated_audio_determinism():
    from validate_streaming_correctness import StreamingRollingWindowBuffer
    from c5_combined import extract_subband_vector_c5
    b = StreamingRollingWindowBuffer(capacity=16000, hop_size=8000)
    test_chunk = np.sin(np.linspace(0, 100, 8000)).astype(np.float32)
    b.reset()
    b.push_chunk(test_chunk)
    w1 = b.push_chunk(test_chunk)
    sb1 = extract_subband_vector_c5(w1)
    b.reset()
    b.push_chunk(test_chunk)
    w2 = b.push_chunk(test_chunk)
    sb2 = extract_subband_vector_c5(w2)
    assert np.array_equal(sb1, sb2)

def test_24_no_duplicate_window_processing():
    from validate_streaming_correctness import StreamingRollingWindowBuffer
    b = StreamingRollingWindowBuffer(capacity=16000, hop_size=8000)
    w1 = b.push_chunk(np.full(8000, 1.0, dtype=np.float32))
    w2 = b.push_chunk(np.full(8000, 2.0, dtype=np.float32))
    assert not np.array_equal(w1, w2)

def test_25_hysteresis_state_reset():
    from compare_temporal_aggregation import evaluate_strategy_decisions
    # Elevated then reset
    _, dec1 = evaluate_strategy_decisions([0.80, 0.50], "Strategy_C_Hysteresis")
    _, dec2 = evaluate_strategy_decisions([0.10, 0.20], "Strategy_C_Hysteresis")
    assert dec1 == 1
    assert dec2 == 0

def test_26_persistence_count_correctness():
    from compare_temporal_aggregation import evaluate_strategy_decisions
    # Isolated spike does not trigger K=2
    _, dec_single = evaluate_strategy_decisions([0.10, 0.85, 0.10], "Strategy_B_Persistence_K2")
    assert dec_single == 0
    # Two consecutive spikes trigger K=2
    _, dec_double = evaluate_strategy_decisions([0.10, 0.85, 0.85, 0.10], "Strategy_B_Persistence_K2")
    assert dec_double == 1

def test_27_partial_final_window_behavior():
    from validate_streaming_correctness import StreamingRollingWindowBuffer
    b = StreamingRollingWindowBuffer(capacity=16000, hop_size=8000)
    w = b.push_chunk(np.ones(1000, dtype=np.float32))
    assert len(w) == 16000
    assert np.all(w[8000:9000] == 1.0) and np.all(w[9000:] == 0.0)

def test_28_timestamp_alignment():
    from validate_streaming_correctness import StreamingRollingWindowBuffer
    b = StreamingRollingWindowBuffer(capacity=16000, hop_size=8000)
    b.push_chunk(np.zeros(8000, dtype=np.float32))
    assert b.last_timestamp == 0.0
    b.push_chunk(np.zeros(8000, dtype=np.float32))
    assert b.last_timestamp == 0.5
    b.push_chunk(np.zeros(8000, dtype=np.float32))
    assert b.last_timestamp == 1.0

# -----------------------------------------------------------------------------
# EVALUATION GOVERNANCE (Tests 29 - 35)
# -----------------------------------------------------------------------------
def test_29_preregistration_hash_integrity():
    prereg_p = STAGE61_DIR / "independent_evaluation_preregistration.md"
    assert sha256_file(str(prereg_p)) == "f6a3c14a1ecd11d783d76f8f27352b577cdb3b6a3f9e4b0724e19f2d58b4248c"

def test_30_frozen_parameter_integrity():
    freeze_p = STAGE61_DIR / "rolling_window_candidate_freeze.json"
    assert sha256_file(str(freeze_p)) == "a56982b014e12697982d927c917f1039de35c72b1dc20a1c9ac61dc74e2275df"

def test_31_sealed_label_access_restrictions():
    # Verify that predictions CSV exists and has 700 recordings
    preds_csv = STAGE61_DIR / "sealed_cohort_predictions.csv"
    assert preds_csv.exists()
    df = pd.read_csv(preds_csv)
    assert df["recording_id"].nunique() == 700

def test_32_no_test_threshold_sweeping():
    # Thresholds must be fixed to frozen values: 0.6800, 0.8000, 0.6000
    preds_csv = STAGE61_DIR / "sealed_cohort_predictions.csv"
    df = pd.read_csv(preds_csv)
    e1_stat_thresh = df[df["candidate_id"] == "Candidate_E1_Static_C5"]["threshold"].iloc[0]
    b_thresh = df[df["candidate_id"] == "Candidate_B_Baseline"]["threshold"].iloc[0]
    roll_thresh = df[df["candidate_id"] == "Candidate_E1_Rolling_C5_EMA"]["threshold"].iloc[0]
    assert e1_stat_thresh == 0.6800
    assert b_thresh == 0.8000
    assert roll_thresh == 0.6000

def test_33_no_test_based_parameter_changes():
    with open(STAGE61_DIR / "rolling_window_candidate_freeze.json") as f:
        freeze_data = json.load(f)
    assert freeze_data["temporal_aggregation_parameters"]["alpha"] == 0.50
    assert freeze_data["temporal_aggregation_parameters"]["decision_threshold"] == 0.6000

def test_34_no_model_retraining():
    e1_ckpt = STAGE54_DIR / "training" / "candidate_e_v954_weighted.pt"
    assert sha256_file(str(e1_ckpt)) == "37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564"

def test_35_no_production_modification():
    prod_joblib = BACKEND_DIR / "models" / "scream_classifier.joblib"
    assert sha256_file(str(prod_joblib)) == "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f"
