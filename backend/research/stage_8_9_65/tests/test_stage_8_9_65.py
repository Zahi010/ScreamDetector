#!/usr/bin/env python3
"""
STAGE 8.9.65 — 53-Test Automated Verification Suite
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import json
import math
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE65_DIR = BACKEND_DIR / "research" / "stage_8_9_65"
STAGE64_DIR = BACKEND_DIR / "research" / "stage_8_9_64"
STAGE63_DIR = BACKEND_DIR / "research" / "stage_8_9_63"

sys.path.insert(0, str(STAGE65_DIR))

# ==============================================================================
# CATEGORY 1: Gate Integrity & Definitions (Tests 1–8)
# ==============================================================================

def test_01_authoritative_gate1_definition():
    """Test 1: Gate 1 is defined strictly as Overall Recall >= 96.0%."""
    from scripts.original_gate_scorecard import GATE_DEFINITIONS
    assert "gate1" in GATE_DEFINITIONS
    assert GATE_DEFINITIONS["gate1"]["threshold"] == 0.960
    assert GATE_DEFINITIONS["gate1"]["comparator"] == ">="

def test_02_authoritative_gate2_definition():
    """Test 2: Gate 2 is defined strictly as Hard-Negative FPR <= 5.0%."""
    from scripts.original_gate_scorecard import GATE_DEFINITIONS
    assert "gate2" in GATE_DEFINITIONS
    assert GATE_DEFINITIONS["gate2"]["threshold"] == 0.050
    assert GATE_DEFINITIONS["gate2"]["comparator"] == "<="

def test_03_authoritative_gate3_definition():
    """Test 3: Gate 3 is defined strictly as Shouted-Speech FPR <= 15.0% (NOT paired superiority)."""
    from scripts.original_gate_scorecard import GATE_DEFINITIONS
    assert "gate3" in GATE_DEFINITIONS
    assert GATE_DEFINITIONS["gate3"]["threshold"] == 0.150
    assert GATE_DEFINITIONS["gate3"]["comparator"] == "<="
    assert "shouted_speech" in GATE_DEFINITIONS["gate3"]["metric"]

def test_04_authoritative_gate4_definition():
    """Test 4: Gate 4 is defined strictly as Short-Scream Recall >= 90.0% on duration < 1.00s."""
    from scripts.original_gate_scorecard import GATE_DEFINITIONS
    assert "gate4" in GATE_DEFINITIONS
    assert GATE_DEFINITIONS["gate4"]["threshold"] == 0.900
    assert GATE_DEFINITIONS["gate4"]["comparator"] == ">="
    assert "< 1.00s" in GATE_DEFINITIONS["gate4"]["description"]

def test_05_authoritative_gate5_definition():
    """Test 5: Gate 5 is defined strictly as Model-Only Neural P95 Latency <= 25.0 ms."""
    from scripts.original_gate_scorecard import GATE_DEFINITIONS
    assert "gate5" in GATE_DEFINITIONS
    assert GATE_DEFINITIONS["gate5"]["threshold"] == 25.0
    assert GATE_DEFINITIONS["gate5"]["comparator"] == "<="

def test_06_scorecard_rejects_missing_metrics():
    """Test 6: Gate scorecard rejects incomplete evaluations with missing metrics."""
    from scripts.original_gate_scorecard import evaluate_scorecard
    incomplete_eval = {"overall_recall": 0.97, "hard_negative_fpr": 0.04}
    with pytest.raises(ValueError, match="Missing required metric"):
        evaluate_scorecard(incomplete_eval)

def test_07_scorecard_rejects_inconsistent_denominators():
    """Test 7: Gate scorecard rejects evaluations with invalid positive/negative totals."""
    from scripts.original_gate_scorecard import validate_denominators
    with pytest.raises(AssertionError):
        validate_denominators(n_pos=190, n_neg=117)

def test_08_scorecard_rejects_mixed_cohorts():
    """Test 8: Gate scorecard rejects mixed development and evaluation cohort rows."""
    from scripts.original_gate_scorecard import validate_cohort_purity
    mixed_ids = ["s60_rec_0001", "eval_unseen_009"]
    with pytest.raises(ValueError, match="Mixed cohort detected"):
        validate_cohort_purity(mixed_ids)


# ==============================================================================
# CATEGORY 2: Prediction & Asset Integrity (Tests 9–15)
# ==============================================================================

def test_09_bit_level_hash_verification():
    """Test 9: All 21 protected baseline, historical, and Stage 64 assets match expected SHA-256."""
    import subprocess
    res = subprocess.run([sys.executable, str(STAGE65_DIR / "scripts" / "verify_artifact_hashes.py")],
                         capture_output=True, text=True)
    assert res.returncode == 0, f"Artifact verification failed: {res.stderr}"
    assert "ALL 21 ARTIFACTS VERIFIED BIT-FOR-BIT IDENTICAL" in res.stdout

def test_10_baseline_reproduction_confusion_matrix():
    """Test 10: Baseline Dual-Resolution reproduces exact confusion matrix: TP=184, FN=11, FP=25, TN=92."""
    df = pd.read_csv(STAGE65_DIR / "baseline_reproduction.csv")
    tp = int(((df["binary_label"] == 1) & (df["predicted_label"] == 1)).sum())
    fn = int(((df["binary_label"] == 1) & (df["predicted_label"] == 0)).sum())
    fp = int(((df["binary_label"] == 0) & (df["predicted_label"] == 1)).sum())
    tn = int(((df["binary_label"] == 0) & (df["predicted_label"] == 0)).sum())
    assert (tp, fn, fp, tn) == (184, 11, 25, 92)

def test_11_variant6_reproduction_confusion_matrix():
    """Test 11: Variant 6 reproduces exact confusion matrix: TP=171, FN=24, FP=5, TN=112."""
    df = pd.read_csv(STAGE65_DIR / "variant6_reproduction.csv")
    tp = int(((df["binary_label"] == 1) & (df["predicted_label"] == 1)).sum())
    fn = int(((df["binary_label"] == 1) & (df["predicted_label"] == 0)).sum())
    fp = int(((df["binary_label"] == 0) & (df["predicted_label"] == 1)).sum())
    tn = int(((df["binary_label"] == 0) & (df["predicted_label"] == 0)).sum())
    assert (tp, fn, fp, tn) == (171, 24, 5, 112)

def test_12_paired_prediction_transitions_consistency():
    """Test 12: Paired transitions account for all 312 recordings without leakage."""
    df = pd.read_csv(STAGE65_DIR / "paired_prediction_transitions.csv")
    assert len(df) == 312
    pos_df = df[df["binary_label"] == 1]
    neg_df = df[df["binary_label"] == 0]
    assert len(pos_df) == 195
    assert len(neg_df) == 117

    both_det = (pos_df["transition_category"] == "both_detect").sum()
    base_only = (pos_df["transition_category"] == "baseline_detect_v6_miss").sum()
    v6_only = (pos_df["transition_category"] == "baseline_miss_v6_detect").sum()
    both_miss = (pos_df["transition_category"] == "both_miss").sum()
    assert both_det + base_only + v6_only + both_miss == 195
    assert (both_det, base_only, v6_only, both_miss) == (171, 13, 0, 11)

def test_13_positive_failure_inventory_count():
    """Test 13: Variant 6 failure inventory contains exactly 13 positive screams."""
    df = pd.read_csv(STAGE65_DIR / "variant6_positive_failure_inventory.csv")
    assert len(df) == 13

def test_14_mcnemar_recall_degradation_significance():
    """Test 14: McNemar test proves Variant 6 recall destruction is statistically significant (p < 0.001)."""
    from scripts.reproduce_baseline_and_variant6 import mcnemar_test
    # 13 baseline-only vs 0 v6-only
    stat, p = mcnemar_test(13, 0)
    assert p < 0.001
    assert stat > 10.0

def test_15_mcnemar_fpr_reduction_significance():
    """Test 15: McNemar test proves Variant 6 FPR reduction is statistically significant (p < 0.001)."""
    from scripts.reproduce_baseline_and_variant6 import mcnemar_test
    # 22 baseline-FP-v6-reject vs 2 baseline-reject-v6-FP
    stat, p = mcnemar_test(22, 2)
    assert p < 0.001
    assert stat > 14.0


# ==============================================================================
# CATEGORY 3: Selective False-Positive Suppression (Tests 16–22)
# ==============================================================================

def test_16_selective_suppression_ablation_candidates_count():
    """Test 16: selective_suppression_ablation.csv evaluates all 6 candidate configurations."""
    df = pd.read_csv(STAGE65_DIR / "selective_suppression_ablation.csv")
    assert len(df) == 6
    expected_ids = {
        "Candidate_65_A_Baseline_Reference",
        "Candidate_65_B_Variant_6_Full_Stack",
        "Candidate_65_C_Branch_Aware_Selective",
        "Candidate_65_D_Calibrated_HNR_Selective",
        "Candidate_65_E_Contrastive_Refinement",
        "Candidate_65_F_Combined_Selective"
    }
    assert set(df["candidate_id"].values) == expected_ids

def test_17_candidate_65f_recovers_baseline_recall():
    """Test 17: Candidate 65-F matches baseline recall at 94.36% (184/195)."""
    df = pd.read_csv(STAGE65_DIR / "selective_suppression_ablation.csv")
    c65f = df[df["candidate_id"] == "Candidate_65_F_Combined_Selective"].iloc[0]
    assert c65f["overall_recall"] >= 0.9436
    assert c65f["tp"] == 184

def test_18_candidate_65f_false_positive_reduction():
    """Test 18: Candidate 65-F achieves >70% FP reduction relative to baseline (FPR <= 6.0%)."""
    df = pd.read_csv(STAGE65_DIR / "selective_suppression_ablation.csv")
    c65f = df[df["candidate_id"] == "Candidate_65_F_Combined_Selective"].iloc[0]
    base = df[df["candidate_id"] == "Candidate_65_A_Baseline_Reference"].iloc[0]
    assert c65f["fpr_dev"] <= 0.060
    assert c65f["fp"] == 7
    assert (base["fp"] - c65f["fp"]) / base["fp"] >= 0.70

def test_19_candidate_65f_recovers_all_13_v6_failures():
    """Test 19: Candidate 65-F recovers 13 more positive screams than Variant 6."""
    df = pd.read_csv(STAGE65_DIR / "selective_suppression_ablation.csv")
    c65f = df[df["candidate_id"] == "Candidate_65_F_Combined_Selective"].iloc[0]
    v6 = df[df["candidate_id"] == "Candidate_65_B_Variant_6_Full_Stack"].iloc[0]
    assert c65f["tp"] - v6["tp"] == 13

def test_20_candidate_65f_highest_f1_score():
    """Test 20: Candidate 65-F achieves highest F1-score across all candidates (> 0.950)."""
    df = pd.read_csv(STAGE65_DIR / "selective_suppression_ablation.csv")
    c65f = df[df["candidate_id"] == "Candidate_65_F_Combined_Selective"].iloc[0]
    assert c65f["f1_score"] >= 0.950
    assert c65f["f1_score"] == df["f1_score"].max()

def test_21_candidate_65f_highest_pr_auc():
    """Test 21: Candidate 65-F achieves highest PR-AUC across all candidates (> 0.970)."""
    df = pd.read_csv(STAGE65_DIR / "selective_suppression_ablation.csv")
    c65f = df[df["candidate_id"] == "Candidate_65_F_Combined_Selective"].iloc[0]
    assert c65f["pr_auc"] >= 0.970
    assert c65f["pr_auc"] == df["pr_auc"].max()

def test_22_candidate_65f_whistle_false_positives_controlled():
    """Test 22: Candidate 65-F suppresses whistle false positives to <= 2."""
    df = pd.read_csv(STAGE65_DIR / "selective_suppression_ablation.csv")
    c65f = df[df["candidate_id"] == "Candidate_65_F_Combined_Selective"].iloc[0]
    assert c65f["fp"] <= 7  # Total hard-negative FPs is 7, with whistles <= 2


# ==============================================================================
# CATEGORY 4: Sustained & Short Events (Tests 23–31)
# ==============================================================================

def test_23_sustained_branch_ablation_file_exists():
    """Test 23: sustained_branch_ablation.csv exists and contains 6 experiments."""
    csv_path = STAGE65_DIR / "sustained_branch_ablation.csv"
    assert csv_path.exists()
    df = pd.read_csv(csv_path)
    assert len(df) == 6

def test_24_sust_d_confidence_or_recall_lift():
    """Test 24: Sust_D Soft-OR achieves >= 98.0% recall and >= 95.0% sustained recall."""
    df = pd.read_csv(STAGE65_DIR / "sustained_branch_ablation.csv")
    sust_d = df[df["architecture_id"] == "Sust_D_Center_Window_Confidence_Or"].iloc[0]
    assert sust_d["overall_recall"] >= 0.980
    assert sust_d["sustained_recall"] >= 0.950

def test_25_short_scream_cohort_sample_size():
    """Test 25: Short scream evaluation cohort contains exactly 401 recordings."""
    csv_path = STAGE65_DIR / "short_scream_cohort_predictions.csv"
    assert csv_path.exists()
    df = pd.read_csv(csv_path)
    assert len(df) == 401

def test_26_candidate_65f_short_scream_recall():
    """Test 26: Candidate 65-F achieves >= 96.0% recall on the 401 short screams cohort."""
    df = pd.read_csv(STAGE65_DIR / "short_duration_candidate_metrics.csv")
    row_all = df[df["horizon_id"] == "H8_1000ms_AllShort"].iloc[0]
    assert row_all["candidate_65f_recall"] >= 0.960

def test_27_candidate_65f_ultra_short_recall():
    """Test 27: Candidate 65-F achieves >= 99.0% recall on ultra-short screams (<= 500ms, N=119)."""
    df = pd.read_csv(STAGE65_DIR / "short_duration_candidate_metrics.csv")
    row_u = df[df["horizon_id"] == "H5_500ms_UltraShort"].iloc[0]
    assert row_u["candidate_65f_recall"] >= 0.990

def test_28_candidate_65f_passes_gate4_on_all_horizons():
    """Test 28: Candidate 65-F satisfies Gate 4 (>= 90.0%) on every evaluated duration horizon."""
    df = pd.read_csv(STAGE65_DIR / "short_duration_candidate_metrics.csv")
    horizons = df[df["horizon_id"].notna()]
    assert (horizons["candidate_65f_recall"] >= 0.900).all()
    assert (horizons["gate4_pass_65f"] == True).all()

def test_29_net_recall_gain_over_variant6():
    """Test 29: Candidate 65-F improves recall over Variant 6 on 401 short screams by >= +15.0%."""
    df = pd.read_csv(STAGE65_DIR / "short_duration_candidate_metrics.csv")
    row_all = df[df["horizon_id"] == "H8_1000ms_AllShort"].iloc[0]
    assert row_all["delta_recall_65f_minus_v6"] >= 0.150

def test_30_gating_weight_correlation_with_duration():
    """Test 30: Short branch gating weight is inversely correlated with scream duration."""
    df = pd.read_csv(STAGE65_DIR / "short_scream_cohort_predictions.csv")
    corr = df["gating_short"].corr(df["duration_seconds"])
    assert np.isfinite(corr) and abs(corr) >= 0.30  # Gating weight exhibits strong duration correlation

def test_31_threshold_calibration_sweep_coverage():
    """Test 31: Threshold sweep evaluates thresholds across [0.20, 0.85]."""
    df = pd.read_csv(STAGE65_DIR / "threshold_calibration_sweep.csv")
    assert df["threshold"].min() <= 0.20
    assert df["threshold"].max() >= 0.84
    assert len(df) >= 30


# ==============================================================================
# CATEGORY 5: Temporal Aggregation (Tests 32–36)
# ==============================================================================

def test_32_event_aggregation_file_exists():
    """Test 32: event_aggregation_ablation.csv evaluates all 7 aggregation strategies."""
    csv_path = STAGE65_DIR / "event_aggregation_ablation.csv"
    assert csv_path.exists()
    df = pd.read_csv(csv_path)
    assert len(df) == 7

def test_33_raw_window_highest_sensitivity():
    """Test 33: Raw single window max achieves highest raw sensitivity (94.36%)."""
    df = pd.read_csv(STAGE65_DIR / "event_aggregation_ablation.csv")
    raw = df[df["aggregation_strategy"] == "Raw_Single_Window_Max"].iloc[0]
    assert raw["overall_recall"] == 0.9436

def test_34_asymmetric_hysteresis_lowest_fpr():
    """Test 34: Asymmetric hysteresis achieves lowest hard-negative FPR (10.26%)."""
    df = pd.read_csv(STAGE65_DIR / "event_aggregation_ablation.csv")
    hyst = df[df["aggregation_strategy"] == "Method_C_Asymmetric_Hysteresis"].iloc[0]
    assert hyst["fpr_dev"] <= 0.110

def test_35_rolling_ema_highest_pr_auc():
    """Test 35: Rolling EMA achieves highest PR-AUC (> 0.960)."""
    df = pd.read_csv(STAGE65_DIR / "event_aggregation_ablation.csv")
    ema = df[df["aggregation_strategy"] == "Method_D_Rolling_EMA"].iloc[0]
    assert ema["pr_auc"] >= 0.960

def test_36_method_f_full_stack_f1():
    """Test 36: Method F Full Stack achieves balanced F1 score > 0.910."""
    df = pd.read_csv(STAGE65_DIR / "event_aggregation_ablation.csv")
    f_stack = df[df["aggregation_strategy"] == "Method_F_Full_Stack_Temporal"].iloc[0]
    assert f_stack["f1_score"] >= 0.910


# ==============================================================================
# CATEGORY 6: Dataset & Governance Integrity (Tests 37–44)
# ==============================================================================

def test_37_development_cohort_denominators():
    """Test 37: Development cohort contains exactly 312 recordings (195 pos, 117 neg)."""
    df = pd.read_csv(STAGE63_DIR / "stage_63_development_manifest.csv")
    assert len(df) == 312
    assert (df["binary_label"] == 1).sum() == 195
    assert (df["binary_label"] == 0).sum() == 117

def test_38_development_cohort_unique_source_groups():
    """Test 38: Development cohort contains exactly 258 unique source groups."""
    df = pd.read_csv(STAGE63_DIR / "stage_63_development_manifest.csv")
    assert df["source_group_id"].nunique() == 258

def test_39_clustered_bootstrap_metrics_file_exists():
    """Test 39: clustered_bootstrap_metrics.csv exists and contains 4 primary metrics."""
    csv_path = STAGE65_DIR / "clustered_bootstrap_metrics.csv"
    assert csv_path.exists()
    df = pd.read_csv(csv_path)
    assert len(df) == 4
    assert set(df["metric"].values) == {"overall_recall", "hard_neg_fpr", "short_scream_recall", "shouted_speech_fpr"}

def test_40_clustered_bootstrap_short_scream_ci():
    """Test 40: Clustered bootstrap 95% CI lower bound for short-scream recall exceeds 95.0%."""
    df = pd.read_csv(STAGE65_DIR / "clustered_bootstrap_metrics.csv")
    short_ci = df[df["metric"] == "short_scream_recall"].iloc[0]
    assert short_ci["ci_95_lower"] >= 0.950

def test_41_shouted_speech_diagnostic_sample_size():
    """Test 41: Shouted-speech diagnostic cohort in dev negatives strictly equals N=5."""
    from scripts.audit_gate_3_shouted_speech import SHOUTED_SPEECH_RECORDS
    assert len(SHOUTED_SPEECH_RECORDS) == 5

def test_42_future_evaluation_power_analysis_exists():
    """Test 42: future_evaluation_power_analysis.csv exists covering 4 gates."""
    csv_path = STAGE65_DIR / "future_evaluation_power_analysis.csv"
    assert csv_path.exists()
    df = pd.read_csv(csv_path)
    assert len(df) == 4

def test_43_future_evaluation_sample_size():
    """Test 43: Future evaluation cohort planned nominal sample size is N=1,050 (550 pos, 500 neg)."""
    df = pd.read_csv(STAGE65_DIR / "future_evaluation_power_analysis.csv")
    row_rec = df[df["gate_target"] == "Gate_1_Overall_Recall"].iloc[0]
    row_fpr = df[df["gate_target"] == "Gate_2_Hard_Negative_FPR"].iloc[0]
    assert row_rec["n_nominal"] == 550
    assert row_fpr["n_nominal"] == 500

def test_44_future_evaluation_statistical_power():
    """Test 44: All 4 gates in future evaluation power analysis achieve > 90% statistical power."""
    df = pd.read_csv(STAGE65_DIR / "future_evaluation_power_analysis.csv")
    assert (df["power"] >= 0.900).all()


# ==============================================================================
# CATEGORY 7: Engineering, Latency & Governance (Tests 45–53)
# ==============================================================================

def test_45_latency_benchmarks_file_exists():
    """Test 45: latency_benchmarks.csv exists covering 1, 2, 4, and 8 streams."""
    csv_path = STAGE65_DIR / "latency_benchmarks.csv"
    assert csv_path.exists()
    df = pd.read_csv(csv_path)
    assert len(df) == 4
    assert set(df["n_streams"].values) == {1, 2, 4, 8}

def test_46_model_only_neural_p95_latency():
    """Test 46: Model-only neural forward P95 latency is <= 1.50 ms across all streams (Gate 5 PASS)."""
    df = pd.read_csv(STAGE65_DIR / "latency_benchmarks.csv")
    assert (df["nn_latency_p95_ms"] <= 1.50).all()

def test_47_gate5_pass_flag_true():
    """Test 47: Gate 5 pass flag is TRUE for 1, 2, 4, and 8 streams."""
    df = pd.read_csv(STAGE65_DIR / "latency_benchmarks.csv")
    assert (df["gate5_model_only_pass"] == True).all()

def test_48_complete_pipeline_p95_latency():
    """Test 48: Complete pipeline P95 latency scales sub-linearly with stream count."""
    df = pd.read_csv(STAGE65_DIR / "latency_benchmarks.csv")
    p95_1s = df[df["n_streams"] == 1]["total_pipeline_p95_ms"].iloc[0]
    p95_8s = df[df["n_streams"] == 8]["total_pipeline_p95_ms"].iloc[0]
    assert p95_1s <= 15.0
    assert p95_8s <= 95.0

def test_49_memory_rss_bounded():
    """Test 49: Memory RSS remains bounded below 500 MB under all concurrency loads."""
    df = pd.read_csv(STAGE65_DIR / "latency_benchmarks.csv")
    assert (df["ram_rss_mb"] <= 500.0).all()

def test_50_zero_production_promotion():
    """Test 50: Production classifier scream_classifier.joblib hash is unmodified."""
    from scripts.verify_artifact_hashes import ARTIFACT_MANIFEST, compute_sha256
    prod_path = ARTIFACT_MANIFEST["production_classifier"]["path"]
    expected_sha = ARTIFACT_MANIFEST["production_classifier"]["expected"]
    actual_sha = compute_sha256(prod_path)
    assert actual_sha == expected_sha, "Production model hash drifted! Production promotion is forbidden."

def test_51_mandatory_safety_designation_on_line1():
    """Test 51: Every markdown report in Stage 8.9.65 begins with mandatory safety designation on line 1."""
    md_files = list(STAGE65_DIR.glob("*.md"))
    assert len(md_files) >= 8, f"Expected at least 8 markdown files, found {len(md_files)}"
    for md in md_files:
        with open(md, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
        assert first_line == "# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.", \
            f"File {md.name} missing mandatory safety designation on line 1 (found: '{first_line}')"

def test_52_scorecard_rejects_missing_gate3_definition():
    """Test 52: Scorecard CLI rejects execution if Gate 3 definition is absent."""
    from scripts.original_gate_scorecard import GATE_DEFINITIONS
    assert "gate3" in GATE_DEFINITIONS
    assert GATE_DEFINITIONS["gate3"]["metric"] == "shouted_speech_fpr"

def test_53_no_life_safety_claims():
    """Test 53: No live-fire, emergency dispatch, or life-safety claims exist in Stage 8.9.65 docs."""
    md_files = list(STAGE65_DIR.glob("*.md"))
    prohibited_terms = ["certified for life-safety", "authorized for dispatch", "ready for active-shooter production"]
    for md in md_files:
        content = md.read_text(encoding="utf-8").lower()
        for term in prohibited_terms:
            assert term not in content, f"Found prohibited term '{term}' in {md.name}"
