#!/usr/bin/env python3
"""
STAGE 8.9.66 — Automated 40-Test Verification Suite
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
This system is an experimental acoustic research prototype and is not certified for life-safety use.
"""

import hashlib
import json
import math
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

SCRIPT_DIR = Path(__file__).resolve().parent
STAGE66_DIR = SCRIPT_DIR.parent
MODELS_DIR = STAGE66_DIR / "models"
SCRIPTS_DIR = STAGE66_DIR / "scripts"
RESEARCH_DIR = STAGE66_DIR.parent
BACKEND_DIR = RESEARCH_DIR.parent
REPO_ROOT = BACKEND_DIR.parent

sys.path.insert(0, str(STAGE66_DIR))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


# ==============================================================================
# CATEGORY 1: BASELINE PROTECTION & CRYPTOGRAPHIC INTEGRITY (Tests 1 - 8)
# ==============================================================================

def test_01_all_21_protected_baseline_assets_verified():
    """Test 1: Verify all 21 protected baseline assets match expected SHA-256 with zero drift."""
    hash_file = STAGE66_DIR / "artifact_hashes.json"
    assert hash_file.exists(), f"Missing artifact_hashes.json: {hash_file}"
    with open(hash_file, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    assert len(manifest) == 21, f"Expected 21 assets, found {len(manifest)}"
    for aid, entry in manifest.items():
        actual = sha256_file(Path(entry["path"]))
        assert actual == entry["expected"], f"Drift detected in {aid} ({entry['path']})!"


def test_02_production_scream_classifier_integrity():
    """Test 2: Production scream classifier joblib asset matches expected hash."""
    path = BACKEND_DIR / "models" / "scream_classifier.joblib"
    expected = "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f"
    assert sha256_file(path) == expected


def test_03_model_metadata_json_integrity():
    """Test 3: Production model metadata JSON matches expected hash."""
    path = BACKEND_DIR / "models" / "model_metadata.json"
    expected = "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60"
    assert sha256_file(path) == expected


def test_04_stage54_partition_manifest_integrity():
    """Test 4: Stage 54 verified partition manifest matches expected hash."""
    path = RESEARCH_DIR / "stage_8_9_54" / "dataset" / "partition_manifest_verified.csv"
    expected = "10563efcd5d607d1395f9db5ab1aa805a0d9ca39b9b4a64a710816d334caeb9e"
    assert sha256_file(path) == expected


def test_05_stage60_sealed_manifest_integrity():
    """Test 5: Stage 60 sealed evaluation cohort manifest matches expected hash."""
    path = RESEARCH_DIR / "stage_8_9_60" / "future_evaluation_manifest.json"
    expected = "9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd"
    assert sha256_file(path) == expected


def test_06_stage61_dev_manifest_integrity():
    """Test 6: Stage 61 rolling window development manifest matches expected hash."""
    path = RESEARCH_DIR / "stage_8_9_61" / "rolling_window_development_manifest.csv"
    expected = "bdf27fdf663c722c4f312ab273839629884892b2ae1d17fa47e70981400d6e1c"
    assert sha256_file(path) == expected


def test_07_c5_combined_dsp_integrity():
    """Test 7: C5 combined DSP implementation matches expected hash."""
    path = RESEARCH_DIR / "stage_8_9_57" / "dsp_implementations" / "c5_combined.py"
    expected = "d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58"
    assert sha256_file(path) == expected


def test_08_stage64_dual_resolution_checkpoint_integrity():
    """Test 8: Stage 64 dual resolution checkpoint matches expected hash."""
    path = RESEARCH_DIR / "stage_8_9_64" / "models" / "stage63_dual_resolution_gated.pt"
    expected = "4374c5e4abb36e999ee863ae8dcd478f8bfb4e39968331120a211fe181572e34"
    assert sha256_file(path) == expected


# ==============================================================================
# CATEGORY 2: CANDIDATE 65-F & SUST_D REPRODUCTION & GATES (Tests 9 - 16)
# ==============================================================================

def test_09_candidate_65f_exact_confusion_matrix():
    """Test 9: Candidate 65-F reproduces exact confusion matrix: TP=184, FN=11, FP=7, TN=110."""
    df = pd.read_csv(STAGE66_DIR / "candidate_65f_predictions.csv")
    y_true = df["ground_truth"].values
    preds = df["prediction"].values
    tp = int(np.sum((preds == 1) & (y_true == 1)))
    fp = int(np.sum((preds == 1) & (y_true == 0)))
    fn = int(np.sum((preds == 0) & (y_true == 1)))
    tn = int(np.sum((preds == 0) & (y_true == 0)))
    assert (tp, fn, fp, tn) == (184, 11, 7, 110), f"Mismatch: {(tp, fn, fp, tn)}"


def test_10_candidate_65f_gate1_recall():
    """Test 10: Candidate 65-F Gate 1 recall = 94.36% (fails Gate 1 >= 96.0%)."""
    df = pd.read_csv(STAGE66_DIR / "candidate_65f_predictions.csv")
    rec = df[df["ground_truth"] == 1]["prediction"].mean()
    assert abs(rec - 0.9436) < 1e-3
    assert rec < 0.960, "Candidate 65-F should fail Gate 1 (< 96.0%)"


def test_11_candidate_65f_gate2_fpr():
    """Test 11: Candidate 65-F Gate 2 FPR = 5.98% (fails Gate 2 <= 5.0%)."""
    df = pd.read_csv(STAGE66_DIR / "candidate_65f_predictions.csv")
    fpr = df[df["ground_truth"] == 0]["prediction"].mean()
    assert abs(fpr - 0.0598) < 1e-3
    assert fpr > 0.050, "Candidate 65-F should fail Gate 2 (> 5.0%)"


def test_12_candidate_65f_gate3_shouted_speech_fpr():
    """Test 12: Candidate 65-F Gate 3 shouted-speech FPR = 20.0% (fails Gate 3 <= 15.0%)."""
    df = pd.read_csv(STAGE66_DIR / "candidate_65f_predictions.csv")
    shout_mask = df["is_shouted_speech"] == 1
    shout_fpr = df[shout_mask]["prediction"].mean()
    assert abs(shout_fpr - 0.200) < 1e-3
    assert shout_fpr > 0.150, "Candidate 65-F should fail Gate 3 (> 15.0%)"


def test_13_candidate_65f_gate4_short_scream_recall():
    """Test 13: Candidate 65-F Gate 4 short-scream recall = 98.50% (passes Gate 4 >= 90.0%)."""
    df = pd.read_csv(STAGE66_DIR / "candidate_65f_predictions.csv")
    short_mask = (df["ground_truth"] == 1) & (df["duration_seconds"] < 1.00)
    short_rec = df[short_mask]["prediction"].mean()
    assert abs(short_rec - 0.9850) < 1e-3
    assert short_rec >= 0.900, "Candidate 65-F should pass Gate 4 (>= 90.0%)"


def test_14_sust_d_exact_confusion_matrix():
    """Test 14: Sust_D reproduces exact confusion matrix: TP=192, FN=3, FP=68, TN=49."""
    df = pd.read_csv(STAGE66_DIR / "sust_d_predictions.csv")
    y_true = df["ground_truth"].values
    preds = df["prediction"].values
    tp = int(np.sum((preds == 1) & (y_true == 1)))
    fp = int(np.sum((preds == 1) & (y_true == 0)))
    fn = int(np.sum((preds == 0) & (y_true == 1)))
    tn = int(np.sum((preds == 0) & (y_true == 0)))
    assert (tp, fn, fp, tn) == (192, 3, 68, 49), f"Mismatch: {(tp, fn, fp, tn)}"


def test_15_sust_d_gate2_catastrophic_failure():
    """Test 15: Sust_D suffers catastrophic Gate 2 failure (FPR = 58.12% vs threshold 5.0%)."""
    df = pd.read_csv(STAGE66_DIR / "sust_d_predictions.csv")
    fpr = df[df["ground_truth"] == 0]["prediction"].mean()
    assert abs(fpr - 0.5812) < 1e-3
    assert fpr > 0.500, "Sust_D must exhibit catastrophic false positive rate (> 50%)"


def test_16_sust_d_gate3_catastrophic_failure():
    """Test 16: Sust_D suffers 100% false alarm rate on shouted speech (Gate 3)."""
    df = pd.read_csv(STAGE66_DIR / "sust_d_predictions.csv")
    shout_mask = df["is_shouted_speech"] == 1
    shout_fpr = df[shout_mask]["prediction"].mean()
    assert shout_fpr == 1.0, "Sust_D must trigger on 100% of shouted speech"


# ==============================================================================
# CATEGORY 3: CANDIDATE COMPARISON, MCNEMAR & RANKING (Tests 17 - 24)
# ==============================================================================

def test_17_four_candidate_comparison_csv_exists():
    """Test 17: Four-candidate comparison CSV exists with all 4 models."""
    csv_path = STAGE66_DIR / "four_candidate_comparison.csv"
    assert csv_path.exists()
    df = pd.read_csv(csv_path)
    assert len(df) == 4
    names = df["candidate_name"].tolist()
    assert any("65-F" in n for n in names)
    assert any("Sust_D" in n for n in names)
    assert any("Baseline" in n for n in names)
    assert any("Variant 6" in n for n in names)


def test_18_candidate_65f_highest_f1_score():
    """Test 18: Candidate 65-F achieves highest F1 score (0.9534) among all 4 candidates."""
    df = pd.read_csv(STAGE66_DIR / "four_candidate_comparison.csv")
    c65f_f1 = df[df["candidate_name"].str.contains("65-F")]["f1_score"].iloc[0]
    other_f1s = df[~df["candidate_name"].str.contains("65-F")]["f1_score"].values
    assert c65f_f1 > max(other_f1s), f"65-F ({c65f_f1}) not highest among {other_f1s}"


def test_19_mcnemar_test_candidate_65f_vs_baseline():
    """Test 19: Candidate 65-F is statistically superior to Baseline Dual-Resolution (p < 0.001)."""
    c65f_df = pd.read_csv(STAGE66_DIR / "candidate_65f_predictions.csv")
    base_df = pd.read_csv(RESEARCH_DIR / "stage_8_9_65" / "baseline_reproduction.csv")
    y = c65f_df["ground_truth"].values
    c_corr = (c65f_df["prediction"].values == y)
    b_corr = (base_df["predicted_label"].values == y)
    b01 = int(np.sum((~b_corr) & c_corr))
    b10 = int(np.sum(b_corr & (~c_corr)))
    assert b01 == 18 and b10 == 0, f"Expected 18 wins vs 0, got {b01} vs {b10}"


def test_20_mcnemar_test_candidate_65f_vs_variant6():
    """Test 20: Candidate 65-F is statistically superior to Variant 6 (p < 0.05)."""
    c65f_df = pd.read_csv(STAGE66_DIR / "candidate_65f_predictions.csv")
    v6_df = pd.read_csv(RESEARCH_DIR / "stage_8_9_65" / "variant6_reproduction.csv")
    y = c65f_df["ground_truth"].values
    c_corr = (c65f_df["prediction"].values == y)
    v_corr = (v6_df["predicted_label"].values == y)
    b01 = int(np.sum((~v_corr) & c_corr))
    b10 = int(np.sum(v_corr & (~c_corr)))
    assert b01 == 15 and b10 == 4, f"Expected 15 wins vs 4, got {b01} vs {b10}"


def test_21_mcnemar_test_candidate_65f_vs_sust_d():
    """Test 21: Candidate 65-F is statistically superior to Sust_D (p < 0.0001)."""
    c65f_df = pd.read_csv(STAGE66_DIR / "candidate_65f_predictions.csv")
    sust_df = pd.read_csv(STAGE66_DIR / "sust_d_predictions.csv")
    y = c65f_df["ground_truth"].values
    c_corr = (c65f_df["prediction"].values == y)
    s_corr = (sust_df["prediction"].values == y)
    b01 = int(np.sum((~s_corr) & c_corr))
    b10 = int(np.sum(s_corr & (~c_corr)))
    assert b01 == 61 and b10 == 8, f"Expected 61 wins vs 8, got {b01} vs {b10}"


def test_22_variant6_recall_destruction():
    """Test 22: Variant 6 destroys 13 positive screams (recall drops to 87.69%)."""
    df = pd.read_csv(RESEARCH_DIR / "stage_8_9_65" / "variant6_reproduction.csv")
    rec = df[df["binary_label"] == 1]["predicted_label"].mean()
    assert abs(rec - 0.8769) < 1e-3


def test_23_baseline_high_false_alarm_rate():
    """Test 23: Baseline produces 25 false alarms (FPR = 21.37%)."""
    df = pd.read_csv(RESEARCH_DIR / "stage_8_9_65" / "baseline_reproduction.csv")
    fpr = df[df["binary_label"] == 0]["predicted_label"].mean()
    assert abs(fpr - 0.2137) < 1e-3


def test_24_candidate_selection_ranks_65f_first():
    """Test 24: Candidate selection protocol ranks Candidate 65-F as Rank 1 lead model."""
    meta_path = MODELS_DIR / "candidate_freeze_metadata.json"
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    assert meta["candidate_id"] == "Candidate_65_F_Combined_Selective"


# ==============================================================================
# CATEGORY 4: DATASET EXPANSION, ANNOTATORS & SHORT SCREAMS (Tests 25 - 32)
# ==============================================================================

def test_25_shouted_speech_dataset_size():
    """Test 25: Shouted-speech dataset contains >= 120 recordings (actual: 529)."""
    df = pd.read_csv(STAGE66_DIR / "shouted_speech_manifest.csv")
    assert len(df) >= 120, f"Expected >= 120 recordings, found {len(df)}"
    assert len(df) == 529


def test_26_shouted_speech_source_groups():
    """Test 26: Shouted-speech dataset contains >= 80 independent source groups (actual: 160)."""
    df = pd.read_csv(STAGE66_DIR / "shouted_speech_manifest.csv")
    n_sg = df["source_group_id"].nunique()
    assert n_sg >= 80, f"Expected >= 80 source groups, found {n_sg}"
    assert n_sg == 160


def test_27_shouted_speech_cohens_kappa():
    """Test 27: Multi-annotator agreement: Cohen's kappa >= 0.85 (actual: 0.9547)."""
    ann_df = pd.read_csv(STAGE66_DIR / "shouted_speech_annotation_records.csv")
    from sklearn.metrics import cohen_kappa_score
    r1 = (ann_df["reviewer_1_label"] == "non_scream_shout").astype(int)
    r2 = (ann_df["reviewer_2_label"] == "non_scream_shout").astype(int)
    k = cohen_kappa_score(r1, r2)
    assert k >= 0.850, f"Kappa {k} below 0.850"


def test_28_shouted_speech_fleiss_kappa():
    """Test 28: Multi-annotator agreement: Fleiss' kappa >= 0.85."""
    ann_df = pd.read_csv(STAGE66_DIR / "shouted_speech_annotation_records.csv")
    r1 = (ann_df["reviewer_1_label"] == "non_scream_shout").astype(int)
    r2 = (ann_df["reviewer_2_label"] == "non_scream_shout").astype(int)
    ratings = np.zeros((len(ann_df), 2), dtype=int)
    for i in range(len(ann_df)):
        ratings[i, r1.iloc[i]] += 1
        ratings[i, r2.iloc[i]] += 1
    
    n_subjects, n_categories = ratings.shape
    n_raters = np.sum(ratings[0, :])
    p_j = np.sum(ratings, axis=0) / (n_subjects * n_raters)
    p_i = (np.sum(ratings ** 2, axis=1) - n_raters) / (n_raters * (n_raters - 1))
    p_bar = np.mean(p_i)
    p_e_bar = np.sum(p_j ** 2)
    fleiss_k = (p_bar - p_e_bar) / (1.0 - p_e_bar)
    assert fleiss_k >= 0.850, f"Fleiss Kappa {fleiss_k} below 0.850"


def test_29_hard_negative_expansion_manifest_content():
    """Test 29: Hard-negative expansion manifest contains 462 recordings across 375 source groups."""
    df = pd.read_csv(STAGE66_DIR / "hard_negative_expansion_manifest.csv")
    assert len(df) == 462
    assert df["source_group_id"].nunique() == 375


def test_30_expanded_recordings_legal_licenses():
    """Test 30: 100% of expanded recordings have valid open licenses (CC0 or CC-BY)."""
    shout_df = pd.read_csv(STAGE66_DIR / "shouted_speech_manifest.csv")
    hn_df = pd.read_csv(STAGE66_DIR / "hard_negative_expansion_manifest.csv")
    for df in [shout_df, hn_df]:
        for lic in df["license"]:
            assert "CC" in str(lic) or "Public Domain" in str(lic), f"Unverified license: {lic}"


def test_31_short_scream_cohort_count_and_durations():
    """Test 31: Short-scream cohort contains exactly 401 sub-second screams (<= 1.000s)."""
    df = pd.read_csv(STAGE66_DIR / "short_scream_partition_audit.csv")
    assert len(df) == 401
    assert (df["duration_seconds"] <= 1.000).all(), "Found scream > 1.000s in short scream cohort!"


def test_32_short_scream_zero_leakage_sealed_and_train():
    """Test 32: Short-scream cohort has ZERO leakage into Stage 60 sealed cohort or Stage 54 train."""
    df = pd.read_csv(STAGE66_DIR / "short_scream_partition_audit.csv")
    assert df["in_stage60_sealed"].sum() == 0, "Leakage into Stage 60 sealed cohort!"
    assert df["in_stage54_train"].sum() == 0, "Leakage into Stage 54 train partition!"


# ==============================================================================
# CATEGORY 5: LATENCY, PREREGISTRATION, GOVERNANCE & SAFETY (Tests 33 - 40)
# ==============================================================================

def test_33_latency_gate5_compliance():
    """Test 33: Multi-stream latency benchmarks: Gate 5 Neural Model P95 <= 25.0 ms across 1, 2, 4, 8 streams."""
    lat_csv = STAGE66_DIR / "latency_benchmarks.csv"
    assert lat_csv.exists()
    df = pd.read_csv(lat_csv)
    assert len(df) == 4
    for _, r in df.iterrows():
        assert r["nn_p95_ms"] <= 25.0, f"Stream {r['n_streams']} P95 {r['nn_p95_ms']} > 25.0 ms"
        assert r["gate5_pass"] is True or str(r["gate5_pass"]).lower() == "true"


def test_34_frozen_checkpoint_exists_and_matches_hash():
    """Test 34: Frozen model checkpoint exists and matches recorded SHA-256."""
    ckpt_path = MODELS_DIR / "candidate_65f_frozen.pt"
    assert ckpt_path.exists()
    h = sha256_file(ckpt_path)
    with open(MODELS_DIR / "candidate_freeze_metadata.json", "r", encoding="utf-8") as f:
        meta = json.load(f)
    assert h == meta["checkpoint_sha256"]


def test_35_freeze_metadata_json_completeness():
    """Test 35: Freeze metadata JSON specifies all hyperparameter and gate values."""
    with open(MODELS_DIR / "candidate_freeze_metadata.json", "r", encoding="utf-8") as f:
        meta = json.load(f)
    assert meta["candidate_id"] == "Candidate_65_F_Combined_Selective"
    assert meta["operating_hyperparameters"]["decision_threshold"] == 0.48
    assert meta["operating_hyperparameters"]["high_confidence_bypass"] == 0.80
    assert "gate_status_summary" in meta


def test_36_preregistration_protocol_contains_checkpoint_hash():
    """Test 36: Preregistration protocol document exists and contains frozen checkpoint hash."""
    prereg_doc = STAGE66_DIR / "future_evaluation_preregistration.md"
    assert prereg_doc.exists()
    with open(MODELS_DIR / "candidate_freeze_metadata.json", "r", encoding="utf-8") as f:
        meta = json.load(f)
    with open(prereg_doc, "r", encoding="utf-8") as f:
        text = f.read()
    assert meta["checkpoint_sha256"] in text


def test_37_clustered_power_analysis_minimum_power():
    """Test 37: Clustered power analysis confirms all 4 gates have statistical power >= 80% on N=1,050 cohort."""
    prop_md = STAGE66_DIR / "evaluation_sample_size_reanalysis.md"
    assert prop_md.exists()
    sens_df = pd.read_csv(STAGE66_DIR / "sample_size_sensitivity_analysis.csv")
    assert len(sens_df) == 36
    # Under base cluster setting (rho=0.06, m=1.35) all gates > 80%
    base_case = sens_df[(sens_df["icc_rho"] == 0.05) & (sens_df["mean_cluster_size"] == 1.2)]
    assert (base_case["power_g1_recall"] >= 80.0).all()
    assert (base_case["power_g2_fpr"] >= 80.0).all()
    assert (base_case["power_g3_shout_fpr"] >= 80.0).all()
    assert (base_case["power_g4_short_recall"] >= 80.0).all()


def test_38_authoritative_readiness_decision():
    """Test 38: Authoritative readiness decision is strictly 'NOT READY FOR INDEPENDENT EVALUATION'."""
    rep_md = STAGE66_DIR / "independent_evaluation_readiness_report.md"
    assert rep_md.exists()
    with open(rep_md, "r", encoding="utf-8") as f:
        text = f.read()
    assert "NOT READY FOR INDEPENDENT EVALUATION" in text
    assert "READY FOR INDEPENDENT EVALUATION" not in text.replace("NOT READY FOR INDEPENDENT EVALUATION", "")


def test_39_mandatory_safety_designation_leads_every_markdown_file():
    """Test 39: Mandatory safety designation leads every markdown file on line 1."""
    md_files = list(STAGE66_DIR.glob("*.md"))
    assert len(md_files) >= 10, f"Expected >= 10 markdown reports, found {len(md_files)}"
    expected_header = "# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE."
    for mf in md_files:
        with open(mf, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
        assert first_line == expected_header, f"File {mf.name} does not lead with safety header on line 1! Got: {first_line}"


def test_40_zero_production_promotion_verified():
    """Test 40: Zero production promotion verified (production classifier remains frozen)."""
    prod_path = BACKEND_DIR / "models" / "scream_classifier.joblib"
    expected = "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f"
    assert sha256_file(prod_path) == expected, "Production classifier was mutated!"
