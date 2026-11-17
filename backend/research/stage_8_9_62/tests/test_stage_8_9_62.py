#!/usr/bin/env python3
"""
STAGE 8.9.62 — Automated Test Suite (40 Invariant Tests)
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
STAGE57_DIR = BACKEND_DIR / "research" / "stage_8_9_57"
STAGE60_DIR = BACKEND_DIR / "research" / "stage_8_9_60"
STAGE61_DIR = BACKEND_DIR / "research" / "stage_8_9_61"
STAGE62_DIR = BACKEND_DIR / "research" / "stage_8_9_62"

sys.path.insert(0, str(STAGE62_DIR / "scripts"))
sys.path.insert(0, str(STAGE61_DIR / "scripts"))
sys.path.insert(0, str(STAGE57_DIR / "dsp_implementations"))

def sha256_file(path_str: str) -> str:
    sha = hashlib.sha256()
    with open(path_str, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()

# -----------------------------------------------------------------------------
# DOMAIN 1: STATISTICAL RECONSTRUCTION (Tests 1 - 9)
# -----------------------------------------------------------------------------
def test_01_confusion_matrix_reproduction():
    rep_csv = STAGE62_DIR / "stage_61_metric_reproduction.csv"
    assert rep_csv.exists()
    df = pd.read_csv(rep_csv)
    assert len(df) == 4
    # Check Candidate E1 Static C5
    e1_stat = df[df["candidate_id"] == "Candidate_E1_Static_C5"].iloc[0]
    assert e1_stat["tp"] == 116 and e1_stat["fn"] == 84
    assert e1_stat["fp"] == 96 and e1_stat["tn"] == 404
    # Check Candidate B Baseline
    b_stat = df[df["candidate_id"] == "Candidate_B_Baseline"].iloc[0]
    assert b_stat["tp"] == 115 and b_stat["fn"] == 85
    assert b_stat["fp"] == 79 and b_stat["tn"] == 421

def test_02_positive_only_recall_comparison():
    rec_csv = STAGE62_DIR / "paired_recall_comparisons.csv"
    assert rec_csv.exists()
    df = pd.read_csv(rec_csv)
    assert (df["sample_size_positives"] == 200).all()
    # Rolling vs Static
    roll_stat = df[(df["candidate_1"] == "Candidate_E1_Rolling_C5_EMA") & (df["candidate_2"] == "Candidate_E1_Static_C5")].iloc[0]
    assert roll_stat["cand1_detect_cand2_miss_b"] == 26
    assert roll_stat["cand1_miss_cand2_detect_c"] == 2
    assert roll_stat["recall_diff_pct"] == 12.0

def test_03_negative_only_fpr_comparison():
    fpr_csv = STAGE62_DIR / "paired_fpr_comparisons.csv"
    assert fpr_csv.exists()
    df = pd.read_csv(fpr_csv)
    assert (df["sample_size_negatives"] == 500).all()
    # Static E1 vs Candidate B
    e1_b = df[(df["candidate_1"] == "Candidate_E1_Static_C5") & (df["candidate_2"] == "Candidate_B_Baseline")].iloc[0]
    assert e1_b["cand1_fp_cand2_tn_b"] == 34
    assert e1_b["cand1_tn_cand2_fp_c"] == 17
    assert e1_b["statistically_significant_05"] == True

def test_04_overall_accuracy_comparison():
    acc_csv = STAGE62_DIR / "overall_accuracy_comparisons.csv"
    assert acc_csv.exists()
    df = pd.read_csv(acc_csv)
    assert (df["sample_size_all"] == 700).all()
    # Static E1 vs Candidate B
    e1_b = df[(df["candidate_1"] == "Candidate_E1_Static_C5") & (df["candidate_2"] == "Candidate_B_Baseline")].iloc[0]
    assert e1_b["cand1_correct_cand2_wrong_b"] == 32
    assert e1_b["cand1_wrong_cand2_correct_c"] == 48
    assert e1_b["statistically_significant_05"] == False

def test_05_mcnemar_contingency_table_correctness():
    # Verify that both_detect + b + c + both_miss == 200 for recall
    rec_csv = STAGE62_DIR / "paired_recall_comparisons.csv"
    df = pd.read_csv(rec_csv)
    for _, r in df.iterrows():
        assert r["both_detect"] + r["cand1_detect_cand2_miss_b"] + r["cand1_miss_cand2_detect_c"] + r["both_miss"] == 200

def test_06_exact_mcnemar_calculation():
    from scipy.stats import binomtest
    rec_csv = STAGE62_DIR / "paired_recall_comparisons.csv"
    df = pd.read_csv(rec_csv)
    for _, r in df.iterrows():
        b = int(r["cand1_detect_cand2_miss_b"])
        c = int(r["cand1_miss_cand2_detect_c"])
        expected_p = binomtest(min(b, c), b + c, 0.5, alternative="two-sided").pvalue
        assert round(expected_p, 6) == round(r["mcnemar_exact_binomial_p"], 6)

def test_07_bootstrap_source_group_resampling():
    boot_csv = STAGE62_DIR / "clustered_bootstrap_reproduction.csv"
    assert boot_csv.exists()
    df = pd.read_csv(boot_csv)
    assert (df["bootstrap_iterations"] == 2000).all()
    assert (df["cluster_count"] == 453).all()

def test_08_paired_bootstrap_consistency():
    boot_csv = STAGE62_DIR / "clustered_bootstrap_reproduction.csv"
    df = pd.read_csv(boot_csv)
    # Rolling vs Static recall delta mean should be approximately +12.0%
    roll_row = df[(df["candidate_1"] == "Candidate_E1_Rolling_C5_EMA") & (df["candidate_2"] == "Candidate_E1_Static_C5")].iloc[0]
    assert 11.0 <= roll_row["recall_delta_mean_pct"] <= 13.0

def test_09_multiple_testing_correction():
    mtc_csv = STAGE62_DIR / "multiple_testing_correction.csv"
    assert mtc_csv.exists()
    df = pd.read_csv(mtc_csv)
    assert len(df) == 13
    assert (df["fdr_adjusted_p_bh"] >= df["raw_mcnemar_exact_p"]).all()

# -----------------------------------------------------------------------------
# DOMAIN 2: SHORT-SCREAM ANALYSIS (Tests 10 - 16)
# -----------------------------------------------------------------------------
def test_10_all_69_expected_recordings_accounted_for():
    inv_csv = STAGE62_DIR / "short_scream_forensic_inventory.csv"
    assert inv_csv.exists()
    df = pd.read_csv(inv_csv)
    assert len(df) == 69
    assert (df["duration_seconds"] < 1.0).all()

def test_11_no_duplicate_recording_ids():
    inv_csv = STAGE62_DIR / "short_scream_forensic_inventory.csv"
    df = pd.read_csv(inv_csv)
    assert df["recording_id"].nunique() == 69

def test_12_correct_candidate_prediction_joins():
    inv_csv = STAGE62_DIR / "short_scream_forensic_inventory.csv"
    df = pd.read_csv(inv_csv)
    # Candidate E1 Static detects exactly 25
    assert (df["e1_static_pred"] == 1).sum() == 25
    # Candidate B Baseline detects exactly 27
    assert (df["cand_b_pred"] == 1).sum() == 27
    # Candidate E1 Rolling detects exactly 27
    assert (df["e1_rolling_pred"] == 1).sum() == 27

def test_13_correct_short_sustained_subgroup_assignment():
    preds_csv = STAGE61_DIR / "sealed_cohort_predictions.csv"
    df = pd.read_csv(preds_csv)
    screams = df[(df["candidate_id"] == "Candidate_E1_Static_C5") & (df["binary_label"] == 1)]
    assert (screams["duration_seconds"] < 1.0).sum() == 69
    assert (screams["duration_seconds"] >= 1.0).sum() == 131

def test_14_feature_extraction_validity():
    feat_csv = STAGE62_DIR / "short_scream_feature_analysis.csv"
    assert feat_csv.exists()
    df = pd.read_csv(feat_csv)
    assert len(df) == 69
    assert (df["spectral_centroid_hz"] > 500).all()
    assert (df["rms_amplitude"] > 0).all()

def test_15_missing_audio_handling():
    # Verify that all 69 audio files actually exist on disk
    with open(STAGE60_DIR / "future_evaluation_manifest.json") as f:
        eval_manifest = json.load(f)
    rec_map = {r["recording_id"]: r for r in eval_manifest["recordings"]}
    inv_csv = STAGE62_DIR / "short_scream_forensic_inventory.csv"
    df = pd.read_csv(inv_csv)
    for rid in df["recording_id"]:
        p = REPO_ROOT / rec_map[rid]["workspace_audio_path"]
        assert p.exists()

def test_16_original_labels_preserved():
    inv_csv = STAGE62_DIR / "short_scream_forensic_inventory.csv"
    df = pd.read_csv(inv_csv)
    assert (df["ground_truth_label"] == 1).all()

# -----------------------------------------------------------------------------
# DOMAIN 3: DEVELOPMENT DATASET (Tests 17 - 22)
# -----------------------------------------------------------------------------
def test_17_manifest_integrity():
    dev_csv = STAGE62_DIR / "stage_62_development_manifest.csv"
    assert dev_csv.exists()
    assert sha256_file(str(dev_csv)) == "bdf27fdf663c722c4f312ab273839629884892b2ae1d17fa47e70981400d6e1c"
    df = pd.read_csv(dev_csv)
    assert len(df) == 187

def test_18_no_duplicate_file_hashes():
    dev_csv = STAGE62_DIR / "stage_62_development_manifest.csv"
    df = pd.read_csv(dev_csv)
    assert df["audio_sha256"].nunique() == len(df)

def test_19_no_pcm_duplicates():
    dev_csv = STAGE62_DIR / "stage_62_development_manifest.csv"
    df = pd.read_csv(dev_csv)
    assert df["pcm_sha256"].nunique() == len(df)

def test_20_no_source_group_leakage():
    dev_csv = STAGE62_DIR / "stage_62_development_manifest.csv"
    df_dev = pd.read_csv(dev_csv)
    with open(STAGE60_DIR / "future_evaluation_manifest.json") as f:
        sealed = json.load(f)
    sealed_sgs = set(r["source_group_id"] for r in sealed["recordings"])
    assert len(set(df_dev["source_group_id"]) & sealed_sgs) == 0

def test_21_creator_overlap_reporting():
    with open(STAGE62_DIR / "development_dataset_audit.json") as f:
        audit = json.load(f)
    assert audit["unique_creators"] == 8
    assert audit["short_scream_evidence_status"] == "INSUFFICIENT_DEVELOPMENT_EVIDENCE"

def test_22_exposed_evaluation_cohort_exclusion():
    dev_csv = STAGE62_DIR / "stage_62_development_manifest.csv"
    df_dev = pd.read_csv(dev_csv)
    with open(STAGE60_DIR / "future_evaluation_manifest.json") as f:
        sealed = json.load(f)
    sealed_rids = set(r["recording_id"] for r in sealed["recordings"])
    assert len(set(df_dev["recording_id"]) & sealed_rids) == 0

# -----------------------------------------------------------------------------
# DOMAIN 4: EXPERIMENTAL MODELS (Tests 23 - 27)
# -----------------------------------------------------------------------------
def test_23_frozen_baseline_immutability():
    e1_ckpt = STAGE54_DIR / "training" / "candidate_e_v954_weighted.pt"
    assert sha256_file(str(e1_ckpt)) == "37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564"

def test_24_experimental_checkpoint_versioning():
    cand_csv = STAGE62_DIR / "development_candidate_metrics.csv"
    assert cand_csv.exists()
    df = pd.read_csv(cand_csv)
    assert "Candidate_R5_Dedicated_Short_Event_Classifier" in df["candidate_id"].values

def test_25_feature_schema_consistency():
    from c5_combined import extract_subband_vector_c5, extract_phonation_stats_c5
    test_chunk = np.zeros(16000, dtype=np.float32)
    sb = extract_subband_vector_c5(test_chunk)
    ac = extract_phonation_stats_c5(test_chunk)
    assert len(sb) == 11
    assert len(ac) == 6

def test_26_deterministic_inference():
    from compare_short_event_candidates import load_e1_model
    model = load_e1_model()
    t_sem = torch.zeros((1, 1024), dtype=torch.float32)
    t_mask = torch.ones((1, 6), dtype=torch.float32)
    t_ac = torch.zeros((1, 6), dtype=torch.float32)
    t_sb = torch.zeros((1, 11), dtype=torch.float32)
    with torch.no_grad():
        out1 = model(t_sem, t_ac, t_mask, t_sb).item()
        out2 = model(t_sem, t_ac, t_mask, t_sb).item()
    assert out1 == out2

def test_27_threshold_configuration_isolation():
    cand_csv = STAGE62_DIR / "development_candidate_metrics.csv"
    df = pd.read_csv(cand_csv)
    base_thresh = df[df["candidate_id"] == "Baseline_C5_Static_1s"]["threshold"].iloc[0]
    assert base_thresh == 0.6800

# -----------------------------------------------------------------------------
# DOMAIN 5: TEMPORAL PROCESSING (Tests 28 - 35)
# -----------------------------------------------------------------------------
def test_28_window_advancement():
    from validate_streaming_correctness import StreamingRollingWindowBuffer
    b = StreamingRollingWindowBuffer(capacity=16000, hop_size=8000)
    b.push_chunk(np.zeros(8000, dtype=np.float32))
    assert b.total_samples_ingested == 8000
    b.push_chunk(np.zeros(8000, dtype=np.float32))
    assert b.total_samples_ingested == 16000

def test_29_buffer_boundaries():
    from validate_streaming_correctness import StreamingRollingWindowBuffer
    b = StreamingRollingWindowBuffer(capacity=16000, hop_size=8000)
    w = b.push_chunk(np.ones(4000, dtype=np.float32))
    assert len(w) == 16000
    assert np.all(w[8000:12000] == 1.0) and np.all(w[12000:] == 0.0)

def test_30_state_reset():
    from validate_streaming_correctness import StreamingRollingWindowBuffer
    b = StreamingRollingWindowBuffer(capacity=16000, hop_size=8000)
    b.push_chunk(np.ones(8000, dtype=np.float32))
    b.reset()
    assert np.all(b.buffer == 0.0) and b.windows_emitted == 0 and b.total_samples_ingested == 0

def test_31_no_cross_recording_leakage():
    from validate_streaming_correctness import StreamingRollingWindowBuffer
    b = StreamingRollingWindowBuffer(capacity=16000, hop_size=8000)
    b.push_chunk(np.full(8000, 9.9, dtype=np.float32))
    b.reset()
    w = b.push_chunk(np.zeros(8000, dtype=np.float32))
    assert np.all(w == 0.0)

def test_32_temporal_event_merging():
    from run_temporal_aggregation_experiments import evaluate_method_decisions
    # Multiple adjacent active frames should merge into one event
    score, dec = evaluate_method_decisions([0.10, 0.65, 0.70, 0.65, 0.10], "Method_D_Event_Level_Score_Aggregation")
    assert dec == 1
    assert score > 1.20

def test_33_hysteresis_reset():
    from run_temporal_aggregation_experiments import evaluate_method_decisions
    _, dec1 = evaluate_method_decisions([0.80, 0.50], "Method_E_Adaptive_Context_Hysteresis")
    _, dec2 = evaluate_method_decisions([0.10, 0.20], "Method_E_Adaptive_Context_Hysteresis")
    assert dec1 == 1 and dec2 == 0

def test_34_bounded_memory():
    from validate_streaming_correctness import StreamingRollingWindowBuffer
    b = StreamingRollingWindowBuffer(capacity=16000, hop_size=8000)
    for _ in range(500):
        b.push_chunk(np.zeros(8000, dtype=np.float32))
    assert len(b.buffer) == 16000

def test_35_repeated_audio_determinism():
    from validate_streaming_correctness import StreamingRollingWindowBuffer
    from c5_combined import extract_subband_vector_c5
    b = StreamingRollingWindowBuffer(capacity=16000, hop_size=8000)
    test_chunk = np.sin(np.linspace(0, 50, 8000)).astype(np.float32)
    b.reset()
    b.push_chunk(test_chunk)
    w1 = b.push_chunk(test_chunk)
    sb1 = extract_subband_vector_c5(w1)
    b.reset()
    b.push_chunk(test_chunk)
    w2 = b.push_chunk(test_chunk)
    sb2 = extract_subband_vector_c5(w2)
    assert np.array_equal(sb1, sb2)

# -----------------------------------------------------------------------------
# DOMAIN 6: GOVERNANCE & PROMOTION PROTECTION (Tests 36 - 40)
# -----------------------------------------------------------------------------
def test_36_production_artifact_immutability():
    prod_hashes = {
        BACKEND_DIR / "models" / "scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
        BACKEND_DIR / "models" / "model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
        BACKEND_DIR / "reports" / "test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
        BACKEND_DIR / "reports" / "stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2"
    }
    for p, h in prod_hashes.items():
        assert sha256_file(str(p)) == h

def test_37_historical_evaluation_artifact_immutability():
    b_ckpt = BACKEND_DIR / "research" / "stage_8_9_44" / "models" / "config_b_mask.pt"
    assert sha256_file(str(b_ckpt)) == "f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378"
    d_code = BACKEND_DIR / "research" / "stage_8_9_49" / "scripts" / "whistle_discriminator.py"
    assert sha256_file(str(d_code)) == "3d98aa7496c6ba89066cfa345a6d0c1ee3605c30821f869a049001c4ad4a8bd2"

def test_38_no_sealed_cohort_tuning():
    # Verify that stage 62 development candidate metrics used stage_62_development_manifest
    cand_csv = STAGE62_DIR / "development_candidate_metrics.csv"
    df = pd.read_csv(cand_csv)
    # Total samples evaluated must be 187 (the dev set size), not 700!
    assert (df["tp"] + df["fn"] + df["fp"] + df["tn"] == 187).all()

def test_39_no_production_retraining():
    prod_joblib = BACKEND_DIR / "models" / "scream_classifier.joblib"
    assert sha256_file(str(prod_joblib)) == "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f"

def test_40_acceptance_gates_unchanged():
    with open(STAGE62_DIR / "acceptance_gate_report.md", "r", encoding="utf-8") as f:
        text = f.read()
    assert "Gate 1" in text and "96" in text
    assert "Gate 2" in text and "5" in text
    assert "Gate 3" in text and "15" in text
    assert "Gate 4" in text and "90" in text
    assert "Gate 5" in text and "25" in text
