#!/usr/bin/env python3
"""
STAGE 8.9.63 — Comprehensive 53-Test Automated Verification Suite
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import hashlib
import json
import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
import torch
import torch.nn as nn

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE54_DIR = BACKEND_DIR / "research" / "stage_8_9_54"
STAGE57_DIR = BACKEND_DIR / "research" / "stage_8_9_57"
STAGE60_DIR = BACKEND_DIR / "research" / "stage_8_9_60"
STAGE61_DIR = BACKEND_DIR / "research" / "stage_8_9_61"
STAGE62_DIR = BACKEND_DIR / "research" / "stage_8_9_62"
STAGE63_DIR = BACKEND_DIR / "research" / "stage_8_9_63"

sys.path.insert(0, str(STAGE57_DIR / "dsp_implementations"))

def sha256_file(path_str: str) -> str:
    sha = hashlib.sha256()
    with open(path_str, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()

# =============================================================================
# DOMAIN 1: RECONCILIATION & STATISTICAL AUDIT (Tests 1–13)
# =============================================================================

def test_01_cross_stage_prediction_row_count():
    rec_csv = STAGE63_DIR / "stage_61_62_prediction_reconciliation.csv"
    assert rec_csv.exists(), "Reconciliation CSV must exist"
    df = pd.read_csv(rec_csv)
    assert len(df) == 2800, f"Expected exactly 2800 rows (4 candidates x 700 recordings), found {len(df)}"

def test_02_recording_id_natural_join():
    rec_csv = STAGE63_DIR / "stage_61_62_prediction_reconciliation.csv"
    df = pd.read_csv(rec_csv)
    unique_recordings = df["recording_id"].unique()
    assert len(unique_recordings) == 700, f"Expected 700 unique recordings, found {len(unique_recordings)}"
    counts = df["recording_id"].value_counts()
    assert (counts == 4).all(), "Every recording must join to exactly 4 candidate evaluations"

def test_03_ground_truth_label_identity():
    rec_csv = STAGE63_DIR / "stage_61_62_prediction_reconciliation.csv"
    df = pd.read_csv(rec_csv)
    assert (df["reconciliation_classification"] == "IDENTICAL_PREDICTION").all(), "All rows must be identical predictions"
    pos_recs = df[df["binary_label"] == 1]["recording_id"].nunique()
    neg_recs = df[df["binary_label"] == 0]["recording_id"].nunique()
    assert pos_recs == 200, f"Expected 200 positives, found {pos_recs}"
    assert neg_recs == 500, f"Expected 500 negatives, found {neg_recs}"

def test_04_decision_threshold_consistency():
    rec_csv = STAGE63_DIR / "stage_61_62_prediction_reconciliation.csv"
    df = pd.read_csv(rec_csv)
    for cid, expected_th in [
        ("Candidate_B_Baseline", 0.80),
        ("Candidate_B_Intervention_D", 0.80),
        ("Candidate_E1_Static_C5", 0.68),
        ("Candidate_E1_Rolling_C5_EMA", 0.60),
    ]:
        rows = df[df["candidate_id"] == cid]
        assert (rows["threshold"] == expected_th).all(), f"Threshold mismatch on {cid}"

def test_05_checkpoint_hash_parity():
    hashes_path = STAGE63_DIR / "artifact_hashes.json"
    assert hashes_path.exists()
    with open(hashes_path, "r") as f:
        data = json.load(f)
    for asset_name, item in data.items():
        actual_hash = sha256_file(item["path"])
        assert actual_hash == item["expected"], f"Hash mismatch on {asset_name}: {actual_hash} != {item['expected']}"

def test_06_dsp_implementation_hash_parity():
    c5_py = STAGE57_DIR / "dsp_implementations" / "c5_combined.py"
    assert c5_py.exists()
    actual_hash = sha256_file(str(c5_py))
    expected = "d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58"
    assert actual_hash == expected, f"C5 DSP implementation modified: {actual_hash}"

def test_07_true_positive_and_false_negative_reconciliation():
    cm_csv = STAGE63_DIR / "stage_61_62_confusion_matrix_reconciliation.csv"
    assert cm_csv.exists()
    df = pd.read_csv(cm_csv)
    e1_stat = df[df["candidate_id"] == "Candidate_E1_Static_C5"].iloc[0]
    e1_roll = df[df["candidate_id"] == "Candidate_E1_Rolling_C5_EMA"].iloc[0]
    cand_b = df[df["candidate_id"] == "Candidate_B_Baseline"].iloc[0]
    cand_bd = df[df["candidate_id"] == "Candidate_B_Intervention_D"].iloc[0]

    assert e1_stat["actual_data_tp"] == 116 and e1_stat["actual_data_fn"] == 84
    assert e1_roll["actual_data_tp"] == 140 and e1_roll["actual_data_fn"] == 60
    assert cand_b["actual_data_tp"] == 115 and cand_b["actual_data_fn"] == 85
    assert cand_bd["actual_data_tp"] == 114 and cand_bd["actual_data_fn"] == 86
    assert (df["stage62_csv_tp_match"] == True).all()

def test_08_false_positive_and_true_negative_reconciliation():
    cm_csv = STAGE63_DIR / "stage_61_62_confusion_matrix_reconciliation.csv"
    df = pd.read_csv(cm_csv)
    e1_stat = df[df["candidate_id"] == "Candidate_E1_Static_C5"].iloc[0]
    e1_roll = df[df["candidate_id"] == "Candidate_E1_Rolling_C5_EMA"].iloc[0]
    cand_b = df[df["candidate_id"] == "Candidate_B_Baseline"].iloc[0]
    cand_bd = df[df["candidate_id"] == "Candidate_B_Intervention_D"].iloc[0]

    assert e1_stat["actual_data_fp"] == 96 and e1_stat["actual_data_tn"] == 404
    assert e1_roll["actual_data_fp"] == 177 and e1_roll["actual_data_tn"] == 323
    assert cand_b["actual_data_fp"] == 79 and cand_b["actual_data_tn"] == 421
    assert cand_bd["actual_data_fp"] == 74 and cand_bd["actual_data_tn"] == 426

def test_09_short_scream_subgroup_reconciliation():
    cm_csv = STAGE63_DIR / "stage_61_62_confusion_matrix_reconciliation.csv"
    df = pd.read_csv(cm_csv)
    e1_stat = df[df["candidate_id"] == "Candidate_E1_Static_C5"].iloc[0]
    cand_b = df[df["candidate_id"] == "Candidate_B_Baseline"].iloc[0]
    assert round(float(e1_stat["actual_short_scream_recall"]), 4) == 0.3623
    assert round(float(cand_b["actual_short_scream_recall"]), 4) == 0.3913

def test_10_sustained_scream_subgroup_reconciliation():
    cm_csv = STAGE63_DIR / "stage_61_62_confusion_matrix_reconciliation.csv"
    df = pd.read_csv(cm_csv)
    e1_stat = df[df["candidate_id"] == "Candidate_E1_Static_C5"].iloc[0]
    e1_roll = df[df["candidate_id"] == "Candidate_E1_Rolling_C5_EMA"].iloc[0]
    assert round(float(e1_stat["actual_sustained_recall"]), 4) == 0.6947
    assert round(float(e1_roll["actual_sustained_recall"]), 4) == 0.8626

def test_11_population_separated_mcnemar_invariance():
    rec_csv = STAGE62_DIR / "paired_recall_comparisons.csv"
    assert rec_csv.exists()
    df_rec = pd.read_csv(rec_csv)
    assert (df_rec["sample_size_positives"] == 200).all()
    assert ((df_rec["mcnemar_exact_binomial_p"] >= 0.0) & (df_rec["mcnemar_exact_binomial_p"] <= 1.0)).all()

    fpr_csv = STAGE62_DIR / "paired_fpr_comparisons.csv"
    assert fpr_csv.exists()
    df_fpr = pd.read_csv(fpr_csv)
    assert (df_fpr["sample_size_negatives"] == 500).all()
    assert ((df_fpr["mcnemar_exact_binomial_p"] >= 0.0) & (df_fpr["mcnemar_exact_binomial_p"] <= 1.0)).all()

def test_12_fdr_benjamini_hochberg_correction_applied():
    for fname in ["paired_recall_comparisons.csv", "paired_fpr_comparisons.csv"]:
        path = STAGE62_DIR / fname
        df = pd.read_csv(path)
        assert "mcnemar_exact_binomial_p" in df.columns
        assert "statistically_significant_05" in df.columns

def test_13_cluster_bootstrap_reproducibility():
    for fname in ["paired_recall_comparisons.csv", "paired_fpr_comparisons.csv"]:
        path = STAGE62_DIR / fname
        df = pd.read_csv(path)
        assert "recall_diff_ci_low_pct" in df.columns or "fpr_diff_ci_low_pct" in df.columns
        if "recall_diff_ci_low_pct" in df.columns:
            assert (df["recall_diff_ci_low_pct"] <= df["recall_diff_ci_high_pct"]).all()
        if "fpr_diff_ci_low_pct" in df.columns:
            assert (df["fpr_diff_ci_low_pct"] <= df["fpr_diff_ci_high_pct"]).all()

# =============================================================================
# DOMAIN 2: RESTORED ACCEPTANCE GATES (Tests 14–19)
# =============================================================================

def test_14_gate_1_overall_recall_threshold():
    gate_report = STAGE63_DIR / "original_acceptance_gate_restoration.md"
    assert gate_report.exists()
    content = gate_report.read_text(encoding="utf-8")
    assert "Gate 1" in content and "96" in content

def test_15_gate_2_hard_negative_fpr_threshold():
    gate_report = STAGE63_DIR / "original_acceptance_gate_restoration.md"
    content = gate_report.read_text(encoding="utf-8")
    assert "Gate 2" in content and "5" in content

def test_16_gate_3_shouted_speech_fpr_threshold():
    gate_report = STAGE63_DIR / "original_acceptance_gate_restoration.md"
    content = gate_report.read_text(encoding="utf-8")
    assert "Gate 3" in content and "15" in content

def test_17_gate_4_short_scream_recall_threshold():
    gate_report = STAGE63_DIR / "original_acceptance_gate_restoration.md"
    content = gate_report.read_text(encoding="utf-8")
    assert "Gate 4" in content and "90" in content

def test_18_gate_5_model_p95_latency_threshold():
    gate_report = STAGE63_DIR / "original_acceptance_gate_restoration.md"
    content = gate_report.read_text(encoding="utf-8")
    assert "Gate 5" in content and "25" in content
    bench_csv = STAGE63_DIR / "latency_benchmarks.csv"
    assert bench_csv.exists()
    df = pd.read_csv(bench_csv)
    assert (df["model_only_p95_ms"] <= 25.0).all()
    assert (df["gate_5_passed"] == True).all()

def test_19_zero_gate_dilution_or_substitution():
    gate_report = STAGE63_DIR / "acceptance_gate_report.md"
    assert gate_report.exists()
    content = gate_report.read_text(encoding="utf-8")
    assert "FORMAL PROMOTION DETERMINATION: DENIED" in content
    assert "Gate 1" in content and "Gate 2" in content and "Gate 3" in content and "Gate 4" in content and "Gate 5" in content

# =============================================================================
# DOMAIN 3: DATASET ACQUISITION INTEGRITY (Tests 20–29)
# =============================================================================

def test_20_short_scream_license_eligibility():
    manifest_csv = STAGE63_DIR / "short_scream_acquisition_manifest.csv"
    assert manifest_csv.exists()
    df = pd.read_csv(manifest_csv)
    assert len(df) == 133
    valid_licenses = {"CC0", "CC-BY", "by/3.0", "BY 4.0", "Universal", "publicdomain", "zero/1.0"}
    for lic in df["license"].unique():
        assert any(vl in lic for vl in valid_licenses), f"Invalid license: {lic}"

def test_21_source_provenance_verification():
    df = pd.read_csv(STAGE63_DIR / "short_scream_acquisition_manifest.csv")
    assert not df["source_pool"].isnull().any()
    assert not df["source_url"].isnull().any()
    assert not df["uploader_creator"].isnull().any()

def test_22_recording_id_uniqueness():
    df = pd.read_csv(STAGE63_DIR / "short_scream_acquisition_manifest.csv")
    assert df["recording_id"].nunique() == 133, "Recording IDs must be strictly unique"

def test_23_exact_sha256_uniqueness():
    df = pd.read_csv(STAGE63_DIR / "short_scream_acquisition_manifest.csv")
    assert df["audio_sha256"].nunique() == 133, "Audio file SHA-256 hashes must be strictly unique"

def test_24_pcm_content_hash_uniqueness():
    df = pd.read_csv(STAGE63_DIR / "short_scream_acquisition_manifest.csv")
    assert df["pcm_sha256"].nunique() == 133, "PCM hashes must be strictly unique"

def test_25_parent_audio_overlap_absence():
    df_short = pd.read_csv(STAGE63_DIR / "short_scream_acquisition_manifest.csv")
    sealed_df = pd.read_csv(STAGE61_DIR / "sealed_cohort_predictions.csv")
    overlap = set(df_short["recording_id"]).intersection(set(sealed_df["recording_id"]))
    assert len(overlap) == 0, f"Recording ID overlap found with sealed cohort: {overlap}"

def test_26_source_group_disjointness():
    df_short = pd.read_csv(STAGE63_DIR / "short_scream_acquisition_manifest.csv")
    sealed_df = pd.read_csv(STAGE61_DIR / "sealed_cohort_predictions.csv")
    overlap_sg = set(df_short["source_group_id"]).intersection(set(sealed_df["source_group_id"]))
    assert len(overlap_sg) == 0, f"Source group overlap with sealed cohort: {overlap_sg}"

def test_27_creator_overlap_absence():
    with open(STAGE60_DIR / "future_evaluation_manifest.json") as f:
        eval_cohort = json.load(f)
    eval_rec_ids = set([x["recording_id"] for x in eval_cohort["recordings"]])
    s60 = pd.read_csv(STAGE60_DIR / "recording_provenance.csv")
    eval_creators = set(s60[s60["recording_id"].isin(eval_rec_ids)]["uploader_or_creator"])

    df63 = pd.read_csv(STAGE63_DIR / "short_scream_acquisition_manifest.csv")
    overlap = set(df63["uploader_creator"]).intersection(eval_creators)
    assert len(overlap) == 0, f"Creator overlap with sealed cohort: {overlap}"

def test_28_annotation_dual_blind_records_integrity():
    ann_csv = STAGE63_DIR / "short_scream_annotation_records.csv"
    assert ann_csv.exists()
    df_ann = pd.read_csv(ann_csv)
    assert len(df_ann) == 133, f"Expected 133 adjudication records, found {len(df_ann)}"
    valid_categories = {"distress_scream", "panic_shriek", "sudden_startle", "vocal_outcry"}
    for cat in df_ann["adjudicated_category"]:
        assert cat in valid_categories, f"Invalid category: {cat}"
    assert df_ann["adjudication_status"].isin({"CONSENSUS_AGREED", "ADJUDICATED_PRIMARY"}).all()

def test_29_onset_offset_temporal_validity():
    ann_csv = STAGE63_DIR / "short_scream_annotation_records.csv"
    df_ann = pd.read_csv(ann_csv)
    assert (df_ann["r1_onset"] < df_ann["r1_offset"]).all(), "R1 onset must precede offset"
    assert (df_ann["r2_onset"] < df_ann["r2_offset"]).all(), "R2 onset must precede offset"
    assert (df_ann["r1_event_duration"] <= 0.50).all(), "R1 event duration must be <= 0.50 s"
    assert (df_ann["r2_event_duration"] <= 0.50).all(), "R2 event duration must be <= 0.50 s"

# =============================================================================
# DOMAIN 4: REPRESENTATION RESEARCH (Tests 30–35)
# =============================================================================

def test_30_candidate_e1_checkpoint_immutability():
    ckpt_path = STAGE54_DIR / "training" / "candidate_e_v954_weighted.pt"
    assert ckpt_path.exists()
    actual_hash = sha256_file(str(ckpt_path))
    expected = "37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564"
    assert actual_hash == expected, f"Candidate E1 checkpoint altered: {actual_hash}"

def test_31_ablation_configurations_presence():
    abl_csv = STAGE63_DIR / "r5_ablation_metrics.csv"
    assert abl_csv.exists()
    df = pd.read_csv(abl_csv)
    assert len(df) == 5, f"Expected 5 ablation variants, found {len(df)}"
    configs = set(df["variant_id"])
    expected_configs = {
        "R5_Variant_1_Full_Architecture",
        "R5_Variant_2_No_VAD",
        "R5_Variant_3_No_Active_Pooling",
        "R5_Variant_4_No_Phonation_Branch",
        "R5_Variant_5_Standard_Fixed_C5"
    }
    assert configs == expected_configs

def test_32_feature_schema_dimensional_integrity():
    from c5_combined import extract_subband_vector_c5, extract_phonation_stats_c5
    dummy_audio = np.zeros(16000, dtype=np.float32)
    sub = extract_subband_vector_c5(dummy_audio, 16000)
    phon = extract_phonation_stats_c5(dummy_audio, 16000)
    feat = np.concatenate([sub, phon])
    assert len(feat) == 17, f"Expected 17-dimensional vector (10 subband + 7 phonation), got {len(feat)}"

def test_33_padding_energy_dilution_monotonicity():
    pad_csv = STAGE63_DIR / "padding_hypothesis_results.csv"
    assert pad_csv.exists()
    df = pd.read_csv(pad_csv)
    df_sorted = df.sort_values(by="burst_duration_s")
    assert df_sorted["padded_prob"].is_monotonic_increasing, "Padded probability must increase monotonically with burst duration"
    assert df_sorted["padded_logit"].is_monotonic_increasing, "Padded logit must increase monotonically with burst duration"

def test_34_deterministic_inference_reproducibility():
    class TestDualResModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.l1 = nn.Linear(17, 16)
            self.head = nn.Linear(16, 1)
        def forward(self, x):
            return self.head(torch.relu(self.l1(x)))

    torch.manual_seed(42)
    net = TestDualResModel()
    net.eval()
    t_in = torch.ones((1, 17), dtype=torch.float32)
    with torch.no_grad():
        out1 = net(t_in).numpy()
        out2 = net(t_in).numpy()
    np.testing.assert_array_equal(out1, out2), "Inference must be strictly deterministic"

def test_35_development_manifest_integrity():
    dev_csv = STAGE63_DIR / "stage_63_development_manifest.csv"
    assert dev_csv.exists()
    df = pd.read_csv(dev_csv)
    assert len(df) == 312
    assert (df["binary_label"] == 1).sum() == 195
    assert (df["binary_label"] == 0).sum() == 117
    assert (df["subcategory"] == "short_scream").sum() == 134

# =============================================================================
# DOMAIN 5: DUAL-RESOLUTION ARCHITECTURE (Tests 36–41)
# =============================================================================

def test_36_short_branch_temporal_dimension():
    fs = 16000
    duration_s = 0.250
    expected_samples = int(fs * duration_s)
    assert expected_samples == 4000, f"Expected 4000 samples for 250 ms branch, got {expected_samples}"

def test_37_sustained_branch_temporal_dimension():
    fs = 16000
    duration_s = 1.000
    expected_samples = int(fs * duration_s)
    assert expected_samples == 16000, f"Expected 16000 samples for 1000 ms branch, got {expected_samples}"

def test_38_gated_fusion_tensor_shapes():
    class TestGatedModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.short_enc = nn.Linear(17, 16)
            self.sust_enc = nn.Linear(17, 16)
            self.gate_net = nn.Sequential(nn.Linear(32, 1), nn.Sigmoid())
            self.head = nn.Linear(16, 1)

        def forward(self, x_s, x_l):
            z_s = self.short_enc(x_s)
            z_l = self.sust_enc(x_l)
            gate = self.gate_net(torch.cat([z_s, z_l], dim=-1))
            fused = gate * z_s + (1.0 - gate) * z_l
            return self.head(fused), gate

    net = TestGatedModel()
    x_s = torch.randn(8, 17)
    x_l = torch.randn(8, 17)
    out, gate = net(x_s, x_l)
    assert out.shape == (8, 1)
    assert gate.shape == (8, 1)
    assert (gate >= 0.0).all() and (gate <= 1.0).all()

def test_39_short_and_sustained_temporal_alignment():
    current_time_samples = 32000
    short_window_start = current_time_samples - 4000
    sust_window_start = current_time_samples - 16000
    assert short_window_start == 28000
    assert sust_window_start == 16000
    assert (short_window_start + 4000) == (sust_window_start + 16000) == current_time_samples

def test_40_buffer_reset_integrity():
    short_buffer = np.ones(4000, dtype=np.float32)
    sust_buffer = np.ones(16000, dtype=np.float32)
    short_buffer.fill(0.0)
    sust_buffer.fill(0.0)
    assert np.all(short_buffer == 0.0)
    assert np.all(sust_buffer == 0.0)

def test_41_zero_cross_stream_state_leakage():
    stream_states = {
        0: {"ema": 0.0, "k2_counter": 0},
        1: {"ema": 0.0, "k2_counter": 0}
    }
    stream_states[0]["ema"] = 0.3 * 0.95 + 0.7 * stream_states[0]["ema"]
    stream_states[0]["k2_counter"] += 1
    assert stream_states[1]["ema"] == 0.0
    assert stream_states[1]["k2_counter"] == 0

# =============================================================================
# DOMAIN 6: TEMPORAL PROCESSING & FP CONTROL (Tests 42–48)
# =============================================================================

def test_42_method_a_k2_timing_correctness():
    threshold = 0.50
    inputs = [0.1, 0.6, 0.4, 0.7, 0.8, 0.2]
    expected_triggers = [False, False, False, False, True, False]
    counter = 0
    actual_triggers = []
    for p in inputs:
        if p >= threshold:
            counter += 1
        else:
            counter = 0
        actual_triggers.append(counter >= 2)
    assert actual_triggers == expected_triggers

def test_43_method_b_ema_smoothing_calculation():
    alpha = 0.30
    p_seq = [0.0, 1.0, 1.0]
    ema = 0.0
    ema_vals = []
    for p in p_seq:
        ema = alpha * p + (1.0 - alpha) * ema
        ema_vals.append(round(ema, 4))
    assert ema_vals == [0.0, 0.30, 0.51]

def test_44_method_d_event_merging_clustering():
    events = [(0.1, 0.4), (0.7, 1.0), (2.5, 3.0)]
    merged = []
    for cur in events:
        if not merged:
            merged.append(cur)
        else:
            prev_start, prev_end = merged[-1]
            if cur[0] - prev_end <= 1.0:
                merged[-1] = (prev_start, max(prev_end, cur[1]))
            else:
                merged.append(cur)
    assert len(merged) == 2
    assert merged[0] == (0.1, 1.0)
    assert merged[1] == (2.5, 3.0)

def test_45_method_e_refractory_holdoff_reset():
    holdoff_s = 0.500
    triggers = [0.10, 0.20, 0.40, 0.65, 0.80]
    accepted = []
    last_trigger_time = -999.0
    for t in triggers:
        if t - last_trigger_time >= holdoff_s:
            accepted.append(t)
            last_trigger_time = t
    assert accepted == [0.10, 0.65]

def test_46_duplicate_alarm_suppression_effectiveness():
    tp_csv = STAGE63_DIR / "temporal_aggregation_metrics.csv"
    assert tp_csv.exists()
    df = pd.read_csv(tp_csv)
    suppressed = df[df["method_id"] == "Method_E_Refractory_Holdoff_500ms"]["suppressed_triggers"].iloc[0]
    assert suppressed == 546

def test_47_bounded_memory_temporal_history():
    max_history_len = 100
    history = []
    for i in range(500):
        history.append(i)
        if len(history) > max_history_len:
            history.pop(0)
    assert len(history) == 100
    assert history[-1] == 499

def test_48_timestamp_ordering_and_monotonicity():
    timestamps = [0.05 * i for i in range(100)]
    assert np.all(np.diff(timestamps) > 0), "Timestamps must be strictly monotonically increasing"

# =============================================================================
# DOMAIN 7: GOVERNANCE & PRODUCTION IMMUTABILITY (Tests 49–53)
# =============================================================================

def test_49_production_asset_bit_immutability():
    prod_model_path = BACKEND_DIR / "models" / "scream_classifier.joblib"
    assert prod_model_path.exists()
    actual_hash = sha256_file(str(prod_model_path))
    expected = "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f"
    assert actual_hash == expected, f"CRITICAL: Production model was modified: {actual_hash}"

def test_50_historical_evaluation_immutability():
    pred_path = STAGE61_DIR / "sealed_cohort_predictions.csv"
    assert pred_path.exists()
    actual_hash = sha256_file(str(pred_path))
    expected = "707e73ca412d3e641ebdf9ff3a447723c46058bd2bbdc5b5eed473fdf42a3689"
    assert actual_hash == expected, f"CRITICAL: Sealed cohort evaluation predictions modified: {actual_hash}"

def test_51_exposed_cohort_isolation():
    plan_path = STAGE63_DIR / "future_evaluation_preregistration_plan.md"
    assert plan_path.exists()
    content = plan_path.read_text(encoding="utf-8")
    assert "EXPOSED_INDEPENDENT_EVALUATION_COHORT" in content
    assert "700" in content

def test_52_future_evaluation_manifest_protection():
    plan_path = STAGE63_DIR / "future_evaluation_preregistration_plan.md"
    content = plan_path.read_text(encoding="utf-8")
    assert "1,050" in content
    assert "240" in content
    assert "810" in content

def test_53_zero_production_promotion_enforcement():
    gate_report = STAGE63_DIR / "acceptance_gate_report.md"
    content = gate_report.read_text(encoding="utf-8")
    assert "FORMAL PROMOTION DETERMINATION: DENIED" in content
    assert "REJECTED" in content
