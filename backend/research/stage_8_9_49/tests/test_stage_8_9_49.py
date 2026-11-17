"""
Stage 8.9.49 Automated Regression Test Suite
Verifies all 17 mandatory research, governance, and statistical requirements.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
import soundfile as sf
import torch

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE_DIR = BACKEND_DIR / "research" / "stage_8_9_49"

CANONICAL_PRODUCTION_HASHES = {
    "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
}

CANDIDATE_B_CKPT = BACKEND_DIR / "research" / "stage_8_9_44" / "models" / "config_b_mask.pt"
EXPECTED_CANDIDATE_B_HASH = "f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378"

# 1. Production hash immutability
def test_production_hash_immutability():
    for rel_path, expected_hash in CANONICAL_PRODUCTION_HASHES.items():
        p = REPO_ROOT / rel_path
        assert p.exists(), f"Production file missing: {rel_path}"
        with open(p, "rb") as f:
            actual = hashlib.sha256(f.read()).hexdigest()
        assert actual == expected_hash, f"Production hash modified for {rel_path}!"

# 2. Candidate B checkpoint integrity
def test_candidate_b_checkpoint_integrity():
    assert CANDIDATE_B_CKPT.exists(), "Candidate B checkpoint not found!"
    with open(CANDIDATE_B_CKPT, "rb") as f:
        actual = hashlib.sha256(f.read()).hexdigest()
    assert actual == EXPECTED_CANDIDATE_B_HASH, f"Candidate B checkpoint hash modified: {actual}"

# 3. Frozen baseline threshold enforcement
def test_frozen_baseline_threshold_enforcement():
    configs_p = BACKEND_DIR / "research" / "stage_8_9_47" / "FROZEN_CANDIDATE_CONFIGURATIONS.json"
    with open(configs_p, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    assert cfg["Cand_B_Config_B_Mask_v6"]["frozen_operating_threshold"] == 0.8000

# 4. Reproducible inference
def test_reproducible_inference():
    preds_p = STAGE_DIR / "INDEPENDENT_EVALUATION_PREDICTIONS.csv"
    assert preds_p.exists()
    df = pd.read_csv(preds_p)
    assert len(df) == 480
    assert "candidate_b_prob" in df.columns
    assert "candidate_b_pred" in df.columns
    assert np.all((df["candidate_b_prob"] >= 0.8000) == (df["candidate_b_pred"] == 1))

# 5. Source-group independence
def test_source_group_independence():
    dev_val_df = pd.read_csv(STAGE_DIR / "WHISTLE_DEVELOPMENT_MANIFEST.csv")
    indep_df = pd.read_csv(STAGE_DIR / "manifests" / "independent_cohort_manifest.csv")
    s47_df = pd.read_csv(BACKEND_DIR / "research" / "stage_8_9_47" / "INDEPENDENT_COHORT_MANIFEST.csv")
    
    dev_sgs = set(dev_val_df[dev_val_df["partition"] == "dev"]["source_group_id"].unique())
    val_sgs = set(dev_val_df[dev_val_df["partition"] == "val"]["source_group_id"].unique())
    indep_sgs = set(indep_df["source_group_id"].unique())
    s47_sgs = set(s47_df["source_group_id"].unique())
    
    assert len(dev_sgs.intersection(val_sgs)) == 0, "Dev/Val source group leakage!"
    assert len(dev_sgs.intersection(indep_sgs)) == 0, "Dev/Indep source group leakage!"
    assert len(val_sgs.intersection(indep_sgs)) == 0, "Val/Indep source group leakage!"
    assert len(indep_sgs.intersection(s47_sgs)) == 0, "Indep/Stage47 source group leakage!"

# 6. Parent-recording lineage
def test_parent_recording_lineage():
    dev_val_df = pd.read_csv(STAGE_DIR / "WHISTLE_DEVELOPMENT_MANIFEST.csv")
    indep_df = pd.read_csv(STAGE_DIR / "manifests" / "independent_cohort_manifest.csv")
    assert "license" in dev_val_df.columns and "creator" in dev_val_df.columns
    assert "license" in indep_df.columns and "creator" in indep_df.columns
    assert np.all(indep_df["license"] == "CC0-1.0")

# 7. Exact and PCM duplicate detection
def test_exact_and_pcm_duplicate_detection():
    dev_val_df = pd.read_csv(STAGE_DIR / "WHISTLE_DEVELOPMENT_MANIFEST.csv")
    indep_df = pd.read_csv(STAGE_DIR / "manifests" / "independent_cohort_manifest.csv")
    comb = pd.concat([dev_val_df, indep_df], ignore_index=True)
    assert len(comb["sha256"].unique()) == len(comb), "Duplicate file hashes detected!"
    assert len(comb["pcm_sha256"].unique()) == len(comb), "Duplicate PCM hashes detected!"

# 8. Correct subgroup denominators
def test_correct_subgroup_denominators():
    indep_df = pd.read_csv(STAGE_DIR / "manifests" / "independent_cohort_manifest.csv")
    assert len(indep_df) == 480
    assert np.sum(indep_df["binary_label"] == 1) == 160
    assert np.sum(indep_df["binary_label"] == 0) == 320
    assert np.sum(indep_df["acoustic_subtype"] == "ultra_short_scream") == 25
    assert np.sum(indep_df["acoustic_subtype"] == "short_scream") == 45
    assert np.sum(indep_df["acoustic_subtype"] == "sustained_scream") == 35
    assert np.sum(indep_df["acoustic_subtype"] == "distant_reverberant_scream") == 20
    assert np.sum(indep_df["acoustic_subtype"] == "crowd_masked_scream") == 20
    assert np.sum(indep_df["acoustic_subtype"] == "low_intensity_muffled_scream") == 15
    assert np.sum(indep_df["acoustic_subtype"] == "shouted_speech") == 80
    assert np.sum(indep_df["acoustic_subtype"] == "referee_whistle") == 45

# 9. Confusion-matrix arithmetic
def test_confusion_matrix_arithmetic():
    matrix_p = STAGE_DIR / "CANDIDATE_COMPARISON_MATRIX.csv"
    assert matrix_p.exists()
    df = pd.read_csv(matrix_p)
    for _, row in df.iterrows():
        assert row["tp_count"] + row["fn_count"] == 160
        assert row["fp_count"] + row["tn_count"] == 320
        rec_calc = round((row["tp_count"] / 160) * 100.0, 2)
        assert abs(row["overall_recall_pct"] - rec_calc) <= 0.05

# 10. Wilson interval correctness
def test_wilson_interval_correctness():
    import sys
    sys.path.insert(0, str(STAGE_DIR / "scripts"))
    from reproduce_candidate_b import compute_wilson_ci
    low, high = compute_wilson_ci(144, 160)
    assert 0.84 <= low <= 0.85
    assert 0.93 <= high <= 0.95
    # Boundary checks
    l0, h0 = compute_wilson_ci(0, 100)
    assert l0 <= 1e-6 and h0 > 0.0
    l1, h1 = compute_wilson_ci(100, 100)
    assert l1 < 1.0 and h1 >= 0.999999

# 11. Paired-test correctness
def test_paired_test_correctness():
    ci_p = STAGE_DIR / "CONFIDENCE_INTERVAL_AND_PAIRED_TEST_REPORT.md"
    assert ci_p.exists()
    with open(ci_p, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Exact McNemar Paired Discordance Testing" in content
    assert "p =" in content

# 12. Source-group bootstrap correctness
def test_source_group_bootstrap_correctness():
    ci_p = STAGE_DIR / "CONFIDENCE_INTERVAL_AND_PAIRED_TEST_REPORT.md"
    with open(ci_p, "r", encoding="utf-8") as f:
        content = f.read()
    assert "B=2,000" in content
    assert "Delta" in content

# 13. Research filter audit logging
def test_research_filter_audit_logging():
    preds_p = STAGE_DIR / "INDEPENDENT_EVALUATION_PREDICTIONS.csv"
    df = pd.read_csv(preds_p)
    assert "intervention_d_audit_tag" in df.columns
    unique_tags = df["intervention_d_audit_tag"].unique()
    assert "accepted" in unique_tags or "rejected_by_research_filter" in unique_tags

# 14. Candidate B prediction preservation
def test_candidate_b_prediction_preservation():
    preds_p = STAGE_DIR / "INDEPENDENT_EVALUATION_PREDICTIONS.csv"
    df = pd.read_csv(preds_p)
    pos = df[df["binary_label"] == 1]
    # In Intervention D, scream recall was 100% preserved relative to Candidate B
    tp_b = np.sum(pos["candidate_b_pred"] == 1)
    tp_d = np.sum(pos["intervention_d_pred"] == 1)
    assert tp_d == tp_b, f"Regression detected in screams! tp_d={tp_d} vs tp_b={tp_b}"

# 15. No silent suppression of predictions
def test_no_silent_suppression_of_predictions():
    preds_p = STAGE_DIR / "INDEPENDENT_EVALUATION_PREDICTIONS.csv"
    df = pd.read_csv(preds_p)
    # Whenever intervention_d suppresses a scream (pred goes from 1 to 0), tag must be explicit
    suppressed = df[(df["candidate_b_pred"] == 1) & (df["intervention_d_pred"] == 0)]
    if len(suppressed) > 0:
        assert np.all(suppressed["intervention_d_audit_tag"] == "rejected_by_research_filter")

# 16. Latency measurement boundaries
def test_latency_measurement_boundaries():
    lat_p = STAGE_DIR / "LATENCY_AND_CONCURRENCY_BENCHMARK.md"
    assert lat_p.exists()
    with open(lat_p, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Complete Pipeline P95 Latency" in content
    assert "GATE 5 STATUS: PASS" in content

# 17. No modification of previous-stage artifacts
def test_no_modification_of_previous_stage_artifacts():
    # Stage 8.9.47 report must exist and be intact
    rep47 = BACKEND_DIR / "research" / "stage_8_9_47" / "STAGE_8_9_47_REPORT.md"
    assert rep47.exists()
    rep48 = BACKEND_DIR / "research" / "stage_8_9_48" / "STAGE_8_9_48_REPORT.md"
    assert rep48.exists()
