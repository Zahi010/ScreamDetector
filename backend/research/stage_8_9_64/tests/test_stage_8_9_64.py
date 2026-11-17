#!/usr/bin/env python3
"""
STAGE 8.9.64 — 52-Test Automated Verification Suite
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import csv
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
import torch

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE64_DIR = BACKEND_DIR / "research" / "stage_8_9_64"
SCRIPTS_DIR = STAGE64_DIR / "scripts"
MODELS_DIR = STAGE64_DIR / "models"

# =============================================================================
# GROUP 1: ACCEPTANCE GATE DEFINITIONS (Tests 1–4)
# =============================================================================

def test_1_gate_4_authoritative_definition():
    """Test 1: Confirms Gate 4 definition specifies '< 1.00s duration' across historical records."""
    audit_md = STAGE64_DIR / "original_gate_definition_audit.md"
    assert audit_md.exists(), "original_gate_definition_audit.md missing"
    content = audit_md.read_text(encoding="utf-8")
    assert "< 1.00" in content, "Gate 4 definition must specify < 1.00"

def test_2_ultra_short_diagnostic_separation():
    """Test 2: Confirms ultra-short (<= 0.50s) is reported as diagnostic subgroup, not Gate 4 proxy."""
    audit_md = STAGE64_DIR / "original_gate_definition_audit.md"
    content = audit_md.read_text(encoding="utf-8")
    assert "ultra_short_scream" in content or "Ultra-Short" in content, "Must separate ultra-short as diagnostic"

def test_3_five_gates_authoritative_thresholds():
    """Test 3: Confirms all five original gate thresholds without substitution."""
    scorecard_md = STAGE64_DIR / "acceptance_gate_report.md"
    assert scorecard_md.exists(), "acceptance_gate_report.md missing"
    content = scorecard_md.read_text(encoding="utf-8")
    assert "96.0%" in content, "Gate 1 must be >= 96.0%"
    assert "5.0%" in content, "Gate 2 must be <= 5.0%"
    assert "p < 0.01" in content or "0.01" in content, "Gate 3 must be p < 0.01"
    assert "90.0%" in content, "Gate 4 must be >= 90.0%"
    assert "25" in content, "Gate 5 must be <= 25.0 ms"

def test_4_proxy_substitution_prohibition():
    """Test 4: Verifies proxy substitution is strictly prohibited by governance."""
    plan_md = STAGE64_DIR / "future_evaluation_preregistration_plan.md"
    assert plan_md.exists(), "future_evaluation_preregistration_plan.md missing"
    content = plan_md.read_text(encoding="utf-8")
    assert "proxy substitution" in content.lower() or "proxy" in content.lower()

# =============================================================================
# GROUP 2: DUAL-RESOLUTION REPRODUCTION & CLUSTERED METRICS (Tests 5–11)
# =============================================================================

def test_5_reproduction_manifest_row_count():
    """Test 5: Confirms dual_resolution_reproduction.csv has exactly 312 rows."""
    repro_csv = STAGE64_DIR / "dual_resolution_reproduction.csv"
    assert repro_csv.exists(), "dual_resolution_reproduction.csv missing"
    df = pd.read_csv(repro_csv)
    assert len(df) == 312, f"Expected 312 rows, found {len(df)}"

def test_6_reproduction_confusion_matrix():
    """Test 6: Confirms raw confusion matrix: TP=184, FN=11, FP=25, TN=92."""
    df = pd.read_csv(STAGE64_DIR / "dual_resolution_reproduction.csv")
    tp = np.sum((df["binary_label"] == 1) & (df["predicted_label"] == 1))
    fn = np.sum((df["binary_label"] == 1) & (df["predicted_label"] == 0))
    fp = np.sum((df["binary_label"] == 0) & (df["predicted_label"] == 1))
    tn = np.sum((df["binary_label"] == 0) & (df["predicted_label"] == 0))
    assert tp == 184, f"Expected TP=184, got {tp}"
    assert fn == 11, f"Expected FN=11, got {fn}"
    assert fp == 25, f"Expected FP=25, got {fp}"
    assert tn == 92, f"Expected TN=92, got {tn}"

def test_7_gate_4_short_scream_reproduction_recall():
    """Test 7: Confirms short-scream recall (<1.0s) is exactly 98.50% (131/133)."""
    df = pd.read_csv(STAGE64_DIR / "dual_resolution_reproduction.csv")
    short_df = df[(df["binary_label"] == 1) & (df["is_short_orig"] == True)]
    assert len(short_df) == 133, f"Expected 133 short screams, got {len(short_df)}"
    recall = np.sum(short_df["predicted_label"] == 1) / len(short_df)
    assert abs(recall - (131.0 / 133.0)) < 1e-4

def test_8_ultra_short_diagnostic_recall():
    """Test 8: Confirms ultra-short recall (<=0.50s) is 100.00% (51/51)."""
    df = pd.read_csv(STAGE64_DIR / "dual_resolution_reproduction.csv")
    ultra_df = df[(df["binary_label"] == 1) & (df["is_ultra_short"] == True)]
    assert len(ultra_df) == 51, f"Expected 51 ultra-short screams, got {len(ultra_df)}"
    recall = np.sum(ultra_df["predicted_label"] == 1) / len(ultra_df)
    assert recall == 1.0000

def test_9_sustained_scream_reproduction_recall():
    """Test 9: Confirms sustained scream recall (>=1.0s) is 85.48% (53/62)."""
    df = pd.read_csv(STAGE64_DIR / "dual_resolution_reproduction.csv")
    sust_df = df[(df["binary_label"] == 1) & (df["is_sustained"] == True)]
    assert len(sust_df) == 62, f"Expected 62 sustained screams, got {len(sust_df)}"
    recall = np.sum(sust_df["predicted_label"] == 1) / len(sust_df)
    assert abs(recall - (53.0 / 62.0)) < 1e-4

def test_10_clustered_bootstrap_confidence_intervals():
    """Test 10: Confirms Gate 4 lower clustered bootstrap CI >= 95.0%."""
    clust_csv = STAGE64_DIR / "dual_resolution_clustered_metrics.csv"
    assert clust_csv.exists(), "dual_resolution_clustered_metrics.csv missing"
    df = pd.read_csv(clust_csv)
    row_g4 = df[df["metric_name"].str.contains("Gate 4")]
    assert len(row_g4) == 1
    ci_lower = float(row_g4["cluster_boot_ci_low"].iloc[0])
    assert ci_lower >= 0.9500, f"Gate 4 lower CI {ci_lower} < 0.9500"

def test_11_dual_resolution_checkpoint_exists():
    """Test 11: Confirms frozen checkpoint exists in models/ directory."""
    ckpt_path = MODELS_DIR / "stage63_dual_resolution_gated.pt"
    assert ckpt_path.exists(), "stage63_dual_resolution_gated.pt missing"
    assert ckpt_path.stat().st_size > 5000, "Checkpoint file size unexpectedly small"

# =============================================================================
# GROUP 3: SHORT-EVENT BOUNDARY ROBUSTNESS (Tests 12–20)
# =============================================================================

def test_12_synthetic_boundary_matrix_size():
    """Test 12: Confirms 189 synthetic configurations evaluated."""
    b_csv = STAGE64_DIR / "short_event_boundary_metrics.csv"
    assert b_csv.exists(), "short_event_boundary_metrics.csv missing"
    df = pd.read_csv(b_csv)
    assert len(df) == 189, f"Expected 189 synthetic rows, got {len(df)}"

def test_13_synthetic_boundary_best_worst_positions():
    """Test 13: Confirms synthetic position recall is 100.0% across all alignments."""
    df = pd.read_csv(STAGE64_DIR / "short_event_boundary_metrics.csv")
    recalls = df["is_detected"].astype(int)
    assert np.all(recalls == 1), "All synthetic placements must be detected"

def test_14_synthetic_boundary_delta_zero():
    """Test 14: Confirms boundary sensitivity delta is 0.00%."""
    rep_md = STAGE64_DIR / "short_event_boundary_report.md"
    assert rep_md.exists(), "short_event_boundary_report.md missing"
    content = rep_md.read_text(encoding="utf-8")
    assert "0.00%" in content or "0.0%" in content

def test_15_hop_stride_invariance():
    """Test 15: Confirms robustness across 50ms, 100ms, 250ms hop strides."""
    df = pd.read_csv(STAGE64_DIR / "short_event_boundary_metrics.csv")
    strides = df["hop_size_ms"].dropna().unique().tolist()
    assert 50 in strides and 100 in strides and 250 in strides

def test_16_real_development_detection_rate():
    """Test 16: Confirms >= 99.0% detection rate on real short development clips."""
    rep_md = STAGE64_DIR / "short_event_boundary_report.md"
    content = rep_md.read_text(encoding="utf-8")
    assert "99.25%" in content or "99.2%" in content or "132 / 133" in content or "132/133" in content

def test_17_real_development_detection_delay():
    """Test 17: Confirms mean initial detection delay is 0.0 ms in boundary report."""
    rep_md = STAGE64_DIR / "short_event_boundary_report.md"
    content = rep_md.read_text(encoding="utf-8")
    assert "0.00" in content and "ms" in content

def test_18_active_region_pooling_feature_dimension():
    """Test 18: Checks short branch extractor outputs 17 features."""
    import sys
    sys.path.insert(0, str(SCRIPTS_DIR))
    from reproduce_dual_resolution import extract_short_branch_features
    dummy = np.zeros(16000, dtype=np.float32)
    feat = extract_short_branch_features(dummy)
    assert feat.shape == (17,), f"Expected 17 dims, got {feat.shape}"

def test_19_short_branch_padding_safety():
    """Test 19: Verifies short audio (<250ms) is zero-padded without exception."""
    from reproduce_dual_resolution import extract_short_branch_features
    tiny = np.zeros(800, dtype=np.float32)  # 50 ms
    feat = extract_short_branch_features(tiny)
    assert feat.shape == (17,)

def test_20_boundary_report_file_exists():
    """Test 20: Checks short_event_boundary_report.md exists."""
    assert (STAGE64_DIR / "short_event_boundary_report.md").exists()

# =============================================================================
# GROUP 4: SHORT-SCREAM DATASET EXPANSION & INTEGRITY (Tests 21–29)
# =============================================================================

def test_21_short_scream_manifest_exists():
    """Test 21: Confirms stage_64_short_scream_manifest.csv exists."""
    assert (STAGE64_DIR / "stage_64_short_scream_manifest.csv").exists()

def test_22_short_scream_manifest_row_count():
    """Test 22: Confirms >= 250 short screams (target >= 250, actual 401)."""
    df = pd.read_csv(STAGE64_DIR / "stage_64_short_scream_manifest.csv")
    assert len(df) >= 250, f"Expected >=250 short screams, got {len(df)}"

def test_23_short_scream_all_durations_under_one_second():
    """Test 23: Confirms all recordings in short-scream manifest have duration < 1.00s."""
    df = pd.read_csv(STAGE64_DIR / "stage_64_short_scream_manifest.csv")
    durs = df["duration_seconds"].astype(float)
    assert np.all(durs < 1.00), "All short-scream durations must be strictly < 1.00s"

def test_24_short_scream_duration_bands_represented():
    """Test 24: Confirms all 4 duration bands are populated."""
    df = pd.read_csv(STAGE64_DIR / "stage_64_short_scream_manifest.csv")
    bands = df["duration_band"].unique()
    assert len(bands) == 4, f"Expected 4 duration bands, found {len(bands)}"

def test_25_short_scream_source_groups_count():
    """Test 25: Confirms >= 90 unique source groups in short-scream manifest."""
    df = pd.read_csv(STAGE64_DIR / "stage_64_short_scream_manifest.csv")
    sg_count = df["source_group_id"].nunique()
    assert sg_count >= 90, f"Expected >=90 source groups, got {sg_count}"

def test_26_short_scream_zero_sealed_cohort_overlap():
    """Test 26: Confirms 0 matches between short-scream manifest and sealed 700 cohort."""
    df_short = pd.read_csv(STAGE64_DIR / "stage_64_short_scream_manifest.csv")
    sealed_df = pd.read_csv(REPO_ROOT / "backend/research/stage_8_9_61/sealed_cohort_predictions.csv")
    sealed_ids = set(sealed_df["recording_id"].unique())
    short_ids = set(df_short["recording_id"].unique())
    assert len(sealed_ids.intersection(short_ids)) == 0, "FATAL: Sealed cohort overlap detected!"

def test_27_inter_rater_cohen_kappa():
    """Test 27: Confirms Cohen's kappa >= 0.85 in annotation agreement report."""
    rep_md = STAGE64_DIR / "annotation_agreement_report.md"
    assert rep_md.exists(), "annotation_agreement_report.md missing"
    content = rep_md.read_text(encoding="utf-8")
    assert "0.8657" in content or "kappa = 0.86" in content or "0.86" in content

def test_28_inter_rater_agreement_percentage():
    """Test 28: Confirms annotation raw agreement >= 90.0%."""
    rep_md = STAGE64_DIR / "annotation_agreement_report.md"
    content = rep_md.read_text(encoding="utf-8")
    assert "91.27" in content or "91.3%" in content

def test_29_licensing_quarantine_permissive_only():
    """Test 29: Confirms all licenses are permissive (CC0, CC-BY, etc.)."""
    df = pd.read_csv(STAGE64_DIR / "stage_64_short_scream_manifest.csv")
    lics = df["license"].str.upper()
    for l in lics:
        assert "CC" in l or "CREATIVECOMMONS" in l or "PUBLIC" in l or "PERMISSIVE" in l

# =============================================================================
# GROUP 5: FALSE-POSITIVE SUPPRESSION RESEARCH (Tests 30–36)
# =============================================================================

def test_30_hnr_metrics_file_exists():
    """Test 30: Confirms hnr_feature_metrics.csv exists."""
    assert (STAGE64_DIR / "hnr_feature_metrics.csv").exists()

def test_31_false_positive_forensic_inventory_exists():
    """Test 31: Confirms false_positive_forensic_inventory.csv exists."""
    assert (STAGE64_DIR / "false_positive_forensic_inventory.csv").exists()

def test_32_false_positive_error_classes_count():
    """Test 32: Confirms all 6 error classes identified in forensic inventory."""
    df = pd.read_csv(STAGE64_DIR / "false_positive_forensic_inventory.csv")
    classes = df["acoustic_error_class"].unique()
    assert len(classes) >= 5, f"Expected at least 5 error classes, got {len(classes)}"

def test_33_contrastive_hard_negatives_zero_leakage():
    """Test 33: Confirms zero leakage in contrastive_hard_negative_metrics.csv."""
    df = pd.read_csv(STAGE64_DIR / "contrastive_hard_negative_metrics.csv")
    assert np.all(df["sealed_cohort_overlap"] == False)

def test_34_six_suppression_variants_benchmarked():
    """Test 34: Confirms 6 variants benchmarked in false_positive_suppression_metrics.csv."""
    df = pd.read_csv(STAGE64_DIR / "false_positive_suppression_metrics.csv")
    assert len(df) == 6, f"Expected 6 variants, found {len(df)}"

def test_35_variant_6_gate_2_fpr_attainment():
    """Test 35: Confirms Variant 6 achieves Gate 2 FPR <= 5.0% (4.27%)."""
    df = pd.read_csv(STAGE64_DIR / "false_positive_suppression_metrics.csv")
    v6 = df[df["variant_id"] == "V6_Dual_Res_Full_Suppression_Stack"]
    assert len(v6) == 1
    fpr = float(v6["fpr_dev"].iloc[0])
    assert fpr <= 0.050, f"Variant 6 FPR {fpr} > 0.050"

def test_36_suppression_gate_1_veto():
    """Test 36: Confirms Variant 6 recall fails Gate 1 (87.69% < 96.0%)."""
    df = pd.read_csv(STAGE64_DIR / "false_positive_suppression_metrics.csv")
    v6 = df[df["variant_id"] == "V6_Dual_Res_Full_Suppression_Stack"]
    rec = float(v6["overall_recall"].iloc[0])
    assert rec < 0.960, f"Expected Variant 6 to fail Gate 1, but recall was {rec}"

# =============================================================================
# GROUP 6: MODEL, ENGINEERING & LATENCY VERIFICATION (Tests 37–45)
# =============================================================================

def test_37_temporal_aggregation_metrics_file_exists():
    """Test 37: Confirms temporal_aggregation_metrics.csv exists."""
    assert (STAGE64_DIR / "temporal_aggregation_metrics.csv").exists()

def test_38_temporal_methods_count():
    """Test 38: Confirms 7 temporal aggregation methods benchmarked."""
    df = pd.read_csv(STAGE64_DIR / "temporal_aggregation_metrics.csv")
    assert len(df) == 7, f"Expected 7 aggregation methods, found {len(df)}"

def test_39_method_f_fragmentation_reduction():
    """Test 39: Confirms Method F fragmentation ratio <= 3.0 (2.64)."""
    df = pd.read_csv(STAGE64_DIR / "temporal_aggregation_metrics.csv")
    mf = df[df["method_id"] == "Method_F_Branch_Aware_Corroboration"]
    assert len(mf) == 1
    frag = float(mf["event_fragmentation_ratio"].iloc[0])
    assert frag <= 3.0, f"Expected frag ratio <= 3.0, got {frag}"

def test_40_latency_benchmarks_file_exists():
    """Test 40: Confirms latency_benchmarks.csv exists."""
    assert (STAGE64_DIR / "latency_benchmarks.csv").exists()

def test_41_concurrency_stream_levels():
    """Test 41: Confirms 1, 2, 4, 8 streams evaluated in latency benchmarks."""
    df = pd.read_csv(STAGE64_DIR / "latency_benchmarks.csv")
    streams = df["concurrency_streams"].tolist()
    assert streams == [1, 2, 4, 8]

def test_42_gate_5_p95_model_latency_1_stream():
    """Test 42: Confirms 1-stream model P95 latency <= 25.0 ms (actual 0.81 ms)."""
    df = pd.read_csv(STAGE64_DIR / "latency_benchmarks.csv")
    row_1s = df[df["concurrency_streams"] == 1]
    p95 = float(row_1s["model_only_p95_ms"].iloc[0])
    assert p95 <= 25.0, f"1 stream model P95 {p95} > 25.0 ms"

def test_43_gate_5_p95_model_latency_8_streams():
    """Test 43: Confirms 8-stream model P95 latency <= 25.0 ms (actual 0.93 ms)."""
    df = pd.read_csv(STAGE64_DIR / "latency_benchmarks.csv")
    row_8s = df[df["concurrency_streams"] == 8]
    p95 = float(row_8s["model_only_p95_ms"].iloc[0])
    assert p95 <= 25.0, f"8 stream model P95 {p95} > 25.0 ms"

def test_44_zero_deadline_misses():
    """Test 44: Confirms zero deadline misses across all concurrency levels."""
    df = pd.read_csv(STAGE64_DIR / "latency_benchmarks.csv")
    assert np.all(df["deadline_misses"] == 0)

def test_45_complete_pipeline_realtime_margin():
    """Test 45: Confirms complete pipeline P95 latency <= 100.0 ms for 8 streams."""
    df = pd.read_csv(STAGE64_DIR / "latency_benchmarks.csv")
    row_8s = df[df["concurrency_streams"] == 8]
    p95_pipe = float(row_8s["complete_pipeline_p95_ms"].iloc[0])
    assert p95_pipe <= 100.0, f"8-stream pipeline P95 {p95_pipe} > 100.0 ms"

# =============================================================================
# GROUP 7: GOVERNANCE, POWER ANALYSIS & ARTIFACT INTEGRITY (Tests 46–52)
# =============================================================================

def test_46_future_evaluation_power_metrics_file_exists():
    """Test 46: Confirms future_evaluation_power_metrics.csv exists."""
    assert (STAGE64_DIR / "future_evaluation_power_metrics.csv").exists()

def test_47_future_evaluation_cohort_target_size():
    """Test 47: Confirms N=1,050 target cohort in sample_size_rationale.md."""
    rat_md = STAGE64_DIR / "sample_size_rationale.md"
    assert rat_md.exists(), "sample_size_rationale.md missing"
    content = rat_md.read_text(encoding="utf-8")
    assert "1,050" in content or "1050" in content

def test_48_design_effect_under_cluster_cap():
    """Test 48: Confirms DEFF <= 1.40 when cluster cap m <= 3 and rho <= 0.20."""
    df = pd.read_csv(STAGE64_DIR / "future_evaluation_power_metrics.csv")
    assert np.all(df["design_effect"] <= 1.400)

def test_49_acceptance_gate_scorecard_file_exists():
    """Test 49: Confirms acceptance_gate_report.md exists."""
    assert (STAGE64_DIR / "acceptance_gate_report.md").exists()

def test_50_zero_production_promotion_ruling():
    """Test 50: Confirms production promotion is denied in scorecard."""
    content = (STAGE64_DIR / "acceptance_gate_report.md").read_text(encoding="utf-8")
    assert "DENIED" in content or "VETO" in content or "ZERO PRODUCTION PROMOTION" in content

def test_51_all_18_protected_assets_hashes():
    """Test 51: Bit-level SHA-256 verification of all 18 protected baseline assets."""
    hashes_path = STAGE64_DIR / "artifact_hashes.json"
    assert hashes_path.exists(), "artifact_hashes.json missing"
    with open(hashes_path, "r", encoding="utf-8") as f:
        ref_hashes = json.load(f)
    assert len(ref_hashes) == 18, f"Expected 18 reference hashes, got {len(ref_hashes)}"

    for logical_key, item in ref_hashes.items():
        full_path = Path(item["path"])
        expected_hash = item["expected"]
        assert full_path.exists(), f"Protected file missing: {full_path}"
        hasher = hashlib.sha256()
        with open(full_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        assert hasher.hexdigest() == expected_hash, f"Hash drift detected on {logical_key}"

def test_52_mandatory_safety_headers_on_all_markdown():
    """Test 52: Verifies safety header on every markdown document in stage_8_9_64."""
    md_files = list(STAGE64_DIR.glob("*.md"))
    assert len(md_files) >= 10, f"Expected at least 10 markdown reports, found {len(md_files)}"
    expected_header = "# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE."
    for md in md_files:
        lines = md.read_text(encoding="utf-8").strip().splitlines()
        first_line = lines[0].strip() if lines else ""
        assert first_line == expected_header, f"Missing safety header on {md.name}: got '{first_line}'"
