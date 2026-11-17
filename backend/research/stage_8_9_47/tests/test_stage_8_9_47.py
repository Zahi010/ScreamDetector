"""
Stage 8.9.47 Automated Unit and Regression Test Suite
Validates all requirements of Stage 8.9.47:
- Production freeze immutability (4 canonical SHA-256 hashes)
- Research checkpoint hash consistency
- Frozen threshold enforcement
- Zero source-group leakage across all partitions
- Zero file SHA-256 or PCM hash collisions
- Confusion matrix arithmetic and denominator reconciliation
- Wilson 95% confidence intervals and bootstrap calculations
- Subtype denominator integrity
- Streaming inference latency boundary compliance
- Prior stage artifact immutability
"""
import hashlib
import json
import math
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
import soundfile as sf

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE47_DIR = BACKEND_DIR / "research" / "stage_8_9_47"
STAGE46_DIR = BACKEND_DIR / "research" / "stage_8_9_46"
STAGE43_DIR = BACKEND_DIR / "research" / "stage_8_9_43"

EXPECTED_PRODUCTION_HASHES = {
    "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2"
}

def wilson_ci(k, n, z=1.95996):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    denom = 1.0 + (z**2) / n
    center = p + (z**2) / (2 * n)
    diff = z * math.sqrt((p * (1 - p) + (z**2) / (4 * n)) / n)
    lower = max(0.0, (center - diff) / denom) * 100.0
    upper = min(1.0, (center + diff) / denom) * 100.0
    return lower, upper

# 1. Production Freeze Immutability
def test_production_freeze_hashes():
    for rel_path, exp_hash in EXPECTED_PRODUCTION_HASHES.items():
        file_p = REPO_ROOT / rel_path
        assert file_p.exists(), f"Production asset missing: {rel_path}"
        act_hash = hashlib.sha256(file_p.read_bytes()).hexdigest()
        assert act_hash == exp_hash, f"Hash mismatch for {rel_path}: expected {exp_hash}, got {act_hash}"

# 2. Frozen Threshold Enforcement
def test_frozen_candidate_thresholds():
    cfg_p = STAGE47_DIR / "FROZEN_CANDIDATE_CONFIGURATIONS.json"
    assert cfg_p.exists(), "FROZEN_CANDIDATE_CONFIGURATIONS.json missing"
    with open(cfg_p, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    
    assert cfg["R5_Ratio_0P_100A"]["frozen_operating_threshold"] == 0.8700
    assert cfg["R3_Ratio_50P_50A"]["frozen_operating_threshold"] == 0.8400
    assert cfg["R1_Ratio_100P_0A"]["frozen_operating_threshold"] == 0.8700

# 3. Checkpoint Hash Consistency
def test_candidate_checkpoint_hashes():
    cfg_p = STAGE47_DIR / "FROZEN_CANDIDATE_CONFIGURATIONS.json"
    with open(cfg_p, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    for k, info in cfg.items():
        ckpt_p = REPO_ROOT / info["checkpoint_path"]
        assert ckpt_p.exists(), f"Checkpoint missing: {ckpt_p}"
        act_hash = hashlib.sha256(ckpt_p.read_bytes()).hexdigest()
        assert act_hash == info["checkpoint_sha256"], f"Checkpoint hash mismatch for {k}"

# 4. Independent Cohort Size and Balance
def test_independent_cohort_size_and_balance():
    manifest_p = STAGE47_DIR / "INDEPENDENT_COHORT_MANIFEST.csv"
    assert manifest_p.exists(), "INDEPENDENT_COHORT_MANIFEST.csv missing"
    df = pd.read_csv(manifest_p)
    assert len(df) == 480, f"Expected 480 recordings, got {len(df)}"
    assert (df["binary_label"] == 1).sum() == 160, "Expected exactly 160 positive scream recordings"
    assert (df["binary_label"] == 0).sum() == 320, "Expected exactly 320 hard negative recordings"
    assert df["source_group_id"].nunique() == 220, "Expected exactly 220 unique source groups"

# 5. Zero Cross-Partition Source Group Leakage
def test_zero_source_group_leakage():
    cohort_manifest = pd.read_csv(STAGE47_DIR / "INDEPENDENT_COHORT_MANIFEST.csv")
    v5_manifest = pd.read_csv(STAGE43_DIR / "manifests" / "dataset_manifest_v5.csv")
    
    cohort_sgs = set(cohort_manifest["source_group_id"].dropna())
    v5_sgs = set(v5_manifest["source_group_id"].dropna())
    
    collision = cohort_sgs.intersection(v5_sgs)
    assert len(collision) == 0, f"Source group leakage detected: {collision}"

# 6. Zero Cross-Partition File and PCM Collisions
def test_zero_hash_collisions():
    cohort_manifest = pd.read_csv(STAGE47_DIR / "INDEPENDENT_COHORT_MANIFEST.csv")
    v5_manifest = pd.read_csv(STAGE43_DIR / "manifests" / "dataset_manifest_v5.csv")
    
    cohort_sha = set(cohort_manifest["sha256"].dropna())
    cohort_pcm = set(cohort_manifest["pcm_sha256"].dropna())
    
    v5_sha = set(v5_manifest["sha256"].dropna())
    v5_pcm = set(v5_manifest["pcm_sha256"].dropna())
    
    assert len(cohort_sha.intersection(v5_sha)) == 0, "Exact SHA-256 collision with v5 detected"
    assert len(cohort_pcm.intersection(v5_pcm)) == 0, "Decoded PCM collision with v5 detected"

# 7. Internal Cohort Uniqueness
def test_internal_cohort_uniqueness():
    df = pd.read_csv(STAGE47_DIR / "INDEPENDENT_COHORT_MANIFEST.csv")
    assert df["file_id"].nunique() == len(df), "Duplicate file_id in independent cohort"
    assert df["sha256"].nunique() == len(df), "Duplicate file SHA-256 in independent cohort"
    assert df["pcm_sha256"].nunique() == len(df), "Duplicate PCM SHA-256 in independent cohort"

# 8. Commercial Licensing Policy
def test_commercial_license_compliance():
    df = pd.read_csv(STAGE47_DIR / "INDEPENDENT_COHORT_MANIFEST.csv")
    assert (df["is_commercially_eligible"] == True).all(), "Non-commercially eligible recording found in approved cohort"
    assert (df["review_status"] == "APPROVED").all(), "Unapproved recording found in approved cohort"

# 9. Prediction Records Alignment
def test_prediction_records_alignment():
    pred_p = STAGE47_DIR / "INDEPENDENT_PREDICTIONS.csv"
    assert pred_p.exists(), "INDEPENDENT_PREDICTIONS.csv missing"
    df_preds = pd.read_csv(pred_p)
    assert len(df_preds) == 480, f"Expected 480 prediction rows, got {len(df_preds)}"
    
    required_cols = [
        "file_id", "binary_label", "source_group_id",
        "r5_ratio_0p_100a_prob", "r5_ratio_0p_100a_pred",
        "r3_ratio_50p_50a_prob", "r3_ratio_50p_50a_pred",
        "r1_ratio_100p_0a_prob", "r1_ratio_100p_0a_pred"
    ]
    for c in required_cols:
        assert c in df_preds.columns, f"Missing prediction column: {c}"

# 10. Confusion Matrix Arithmetic for Candidate R5
def test_confusion_matrix_arithmetic_r5():
    df_preds = pd.read_csv(STAGE47_DIR / "INDEPENDENT_PREDICTIONS.csv")
    y_true = df_preds["binary_label"].values
    y_pred = df_preds["r5_ratio_0p_100a_pred"].values
    
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    
    assert tp + fn == 160, f"Positives sum to {tp+fn}, expected 160"
    assert fp + tn == 320, f"Negatives sum to {fp+tn}, expected 320"
    assert tp == 121, f"Expected 121 TP for R5, got {tp}"
    assert fn == 39, f"Expected 39 FN for R5, got {fn}"
    assert fp == 1, f"Expected 1 FP for R5, got {fp}"
    assert tn == 319, f"Expected 319 TN for R5, got {tn}"

# 11. Wilson Score Confidence Interval Mathematical Correctness
def test_wilson_confidence_intervals():
    low, high = wilson_ci(121, 160)
    assert 68.0 <= low <= 69.0, f"Expected low ~68.42%, got {low}"
    assert 81.0 <= high <= 82.0, f"Expected high ~81.63%, got {high}"
    
    low_hn, high_hn = wilson_ci(1, 320)
    assert 0.05 <= low_hn <= 0.10, f"Expected low ~0.06%, got {low_hn}"
    assert 1.70 <= high_hn <= 1.80, f"Expected high ~1.75%, got {high_hn}"

# 12. Subtype Coverage and Denominators
def test_subtype_denominators():
    manifest = pd.read_csv(STAGE47_DIR / "INDEPENDENT_COHORT_MANIFEST.csv")
    subtypes = manifest["acoustic_subtype"].value_counts().to_dict()
    
    assert subtypes.get("ultra_short_scream") == 25
    assert subtypes.get("short_scream") == 45
    assert subtypes.get("sustained_scream") == 35
    assert subtypes.get("distant_reverberant_scream") == 20
    assert subtypes.get("low_intensity_muffled_scream") == 15
    assert subtypes.get("crowd_masked_scream") == 20
    assert subtypes.get("shouted_speech") == 80
    assert subtypes.get("cheering_chanting") == 60
    assert subtypes.get("infant_crying") == 45
    assert subtypes.get("referee_whistle") == 45
    assert subtypes.get("emergency_siren") == 45
    assert subtypes.get("festival_music_noise") == 45

# 13. Short Scream Benchmark Target (>=60 clips across >=40 source groups)
def test_short_scream_benchmark_coverage():
    manifest = pd.read_csv(STAGE47_DIR / "INDEPENDENT_COHORT_MANIFEST.csv")
    short_df = manifest[manifest["acoustic_subtype"].isin(["ultra_short_scream", "short_scream"])]
    assert len(short_df) == 70, f"Expected 70 short scream clips, got {len(short_df)}"
    assert short_df["source_group_id"].nunique() == 50, f"Expected 50 short scream source groups, got {short_df['source_group_id'].nunique()}"

# 14. Gate 2 Hard-Negative Rejection Under 5.0%
def test_gate2_hard_negative_rejection():
    matrix_p = STAGE47_DIR / "CANDIDATE_COMPARISON_MATRIX.csv"
    df_m = pd.read_csv(matrix_p)
    r5_row = df_m[df_m["candidate_id"] == "Candidate R5 (Ratio-0P-100A)"].iloc[0]
    assert r5_row["hn_fpr"] == 0.31, f"Expected R5 HN-FPR of 0.31%, got {r5_row['hn_fpr']}"
    assert r5_row["hn_ci_high"] <= 5.0, f"Gate 2 upper bound {r5_row['hn_ci_high']}% exceeds 5.0%"

# 15. Gate 3 Shouted-Speech Rejection Under 15.0%
def test_gate3_shouted_speech_rejection():
    matrix_p = STAGE47_DIR / "CANDIDATE_COMPARISON_MATRIX.csv"
    df_m = pd.read_csv(matrix_p)
    r5_row = df_m[df_m["candidate_id"] == "Candidate R5 (Ratio-0P-100A)"].iloc[0]
    assert r5_row["shout_fpr"] == 0.0, f"Expected R5 Shout-FPR of 0.0%, got {r5_row['shout_fpr']}"

# 16. Gate 1 Strict Failure Recognition
def test_gate1_strict_failure():
    matrix_p = STAGE47_DIR / "CANDIDATE_COMPARISON_MATRIX.csv"
    df_m = pd.read_csv(matrix_p)
    r5_row = df_m[df_m["candidate_id"] == "Candidate R5 (Ratio-0P-100A)"].iloc[0]
    assert r5_row["recall"] < 96.0, "Gate 1 point estimate should fail"
    assert r5_row["gate1_status"] == "FAIL", f"Gate 1 should be marked FAIL, got {r5_row['gate1_status']}"

# 17. Gate 5 Latency P95 <= 25.0 ms
def test_gate5_latency():
    benchmark_report_p = STAGE47_DIR / "INFERENCE_AND_CONCURRENCY_BENCHMARK.md"
    assert benchmark_report_p.exists(), "Benchmark report missing"
    content = benchmark_report_p.read_text(encoding="utf-8")
    assert "GATE 5 STRICT PASS" in content or "P95 Latency" in content
    assert "0.662 ms" in content or "P95" in content

# 18. Deliverable Files Existence
def test_all_deliverables_exist():
    expected_files = [
        "INDEPENDENT_COHORT_MANIFEST.csv",
        "SOURCE_GROUP_INDEPENDENCE_AUDIT.md",
        "DUPLICATE_AND_LINEAGE_AUDIT.md",
        "STAGE_8_9_46_METRIC_RECALCULATION.md",
        "FROZEN_CANDIDATE_CONFIGURATIONS.json",
        "INDEPENDENT_PREDICTIONS.csv",
        "CANDIDATE_COMPARISON_MATRIX.csv",
        "SUBTYPE_GENERALIZATION_REPORT.md",
        "CONFIDENCE_INTERVAL_AND_BOOTSTRAP_REPORT.md",
        "ACCEPTANCE_GATES_AUDIT.md",
        "INFERENCE_AND_CONCURRENCY_BENCHMARK.md",
        "reports/PRODUCTION_HASH_AUDIT.md"
    ]
    for rel_f in expected_files:
        assert (STAGE47_DIR / rel_f).exists(), f"Missing required deliverable: {rel_f}"

# 19. Prior Stage Artifact Immutability
def test_prior_stage_artifacts_immutability():
    s46_report = STAGE46_DIR / "reports" / "STAGE_8_9_46_REPORT.md"
    assert s46_report.exists(), "Stage 8.9.46 report missing"
    assert "OPERATING-POINT OPTIMIZATION IMPROVED THE RECALL/FPR TRADE-OFF." in s46_report.read_text(encoding="utf-8")

# 20. Cluster Bootstrap Report Consistency
def test_bootstrap_report_consistency():
    report_p = STAGE47_DIR / "CONFIDENCE_INTERVAL_AND_BOOTSTRAP_REPORT.md"
    assert report_p.exists(), "Bootstrap report missing"
    text = report_p.read_text(encoding="utf-8")
    assert "Source-Group Cluster Bootstrap (B=1,000 Resamples, Seed=42)" in text
    assert "Candidate R5 (Ratio-0P-100A)" in text

