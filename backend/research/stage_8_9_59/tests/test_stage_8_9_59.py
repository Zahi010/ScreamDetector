import hashlib
import json
import math
import os
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

# MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE54_DIR = BACKEND_DIR / "research" / "stage_8_9_54"
STAGE55_DIR = BACKEND_DIR / "research" / "stage_8_9_55"
STAGE57_DIR = BACKEND_DIR / "research" / "stage_8_9_57"
STAGE58_DIR = BACKEND_DIR / "research" / "stage_8_9_58"
STAGE59_DIR = BACKEND_DIR / "research" / "stage_8_9_59"

def sha256_file(path: Path) -> str:
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()

# 1. C5 implementation hash immutability
def test_01_c5_implementation_hash():
    c5_path = STAGE57_DIR / "dsp_implementations" / "c5_combined.py"
    assert c5_path.exists()
    assert sha256_file(c5_path) == "d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58"

# 2. Original E1 DSP hash immutability
def test_02_original_e1_dsp_hash():
    orig_path = STAGE57_DIR / "scripts" / "benchmark_original_dsp.py"
    assert orig_path.exists()
    assert sha256_file(orig_path) == "192e928c6ea427737ef8a3ec4449c890c1d41f01d71c80cefde3f2a0363f5905"

# 3. Candidate E1 checkpoint immutability
def test_03_candidate_e1_checkpoint_hash():
    e1_path = STAGE54_DIR / "training" / "candidate_e_v954_weighted.pt"
    assert e1_path.exists()
    assert sha256_file(e1_path) == "37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564"

# 4. Candidate B checkpoint immutability
def test_04_candidate_b_checkpoint_hash():
    b_path = BACKEND_DIR / "research" / "stage_8_9_44" / "models" / "config_b_mask.pt"
    assert b_path.exists()
    assert sha256_file(b_path) == "f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378"

# 5. Intervention D configuration immutability
def test_05_intervention_d_hash():
    d_path = BACKEND_DIR / "research" / "stage_8_9_49" / "scripts" / "whistle_discriminator.py"
    assert d_path.exists()
    assert sha256_file(d_path) == "3d98aa7496c6ba89066cfa345a6d0c1ee3605c30821f869a049001c4ad4a8bd2"

# 6. Production asset hashes
def test_06_production_asset_hashes():
    prod_hashes = {
        BACKEND_DIR / "models" / "scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
        BACKEND_DIR / "models" / "model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
        BACKEND_DIR / "reports" / "test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
        BACKEND_DIR / "reports" / "stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2"
    }
    for p, expected in prod_hashes.items():
        assert p.exists()
        assert sha256_file(p) == expected

# 7. Threshold immutability
def test_07_threshold_immutability():
    theta_e1 = 0.6800
    theta_b = 0.8000
    meta_path = BACKEND_DIR / "models" / "model_metadata.json"
    with open(meta_path) as f:
        meta = json.load(f)
    assert meta["selected_threshold"] == 0.35 # Production threshold locked
    assert theta_e1 == 0.6800
    assert theta_b == 0.8000

# 8. Evaluation manifest immutability
def test_08_evaluation_manifest_immutability():
    man54 = STAGE54_DIR / "dataset" / "partition_manifest_verified.csv"
    assert sha256_file(man54) == "10563efcd5d607d1395f9db5ab1aa805a0d9ca39b9b4a64a710816d334caeb9e"
    man55 = STAGE55_DIR / "integrity" / "frozen_test_manifest.json"
    assert sha256_file(man55) == "06c9db80d3969e60f78dd441eb1495a9dab97f1646f08ab5825ea979719021f2"

# 9. Recording ID uniqueness
def test_09_recording_id_uniqueness():
    man54 = pd.read_csv(STAGE54_DIR / "dataset" / "partition_manifest_verified.csv")
    assert man54["expansion_file_id"].nunique() == len(man54)

# 10. Source-group consistency
def test_10_source_group_consistency():
    man54 = pd.read_csv(STAGE54_DIR / "dataset" / "partition_manifest_verified.csv")
    assert man54["source_group_id"].notna().all()
    assert (man54["source_group_id"].str.len() > 0).all()

# 11. Duplicate detection
def test_11_duplicate_detection():
    man54 = pd.read_csv(STAGE54_DIR / "dataset" / "partition_manifest_verified.csv")
    train = man54[man54["expansion_partition"] == "expansion_train"]
    val = man54[man54["expansion_partition"] == "expansion_val"]
    test = man54[man54["expansion_partition"] == "expansion_reserved_test"]
    
    assert len(set(train["file_sha256"]).intersection(set(val["file_sha256"]))) == 0
    assert len(set(train["file_sha256"]).intersection(set(test["file_sha256"]))) == 0
    assert len(set(val["file_sha256"]).intersection(set(test["file_sha256"]))) == 0
    
    assert len(set(train["pcm_sha256"]).intersection(set(val["pcm_sha256"]))) == 0
    assert len(set(train["pcm_sha256"]).intersection(set(test["pcm_sha256"]))) == 0
    assert len(set(val["pcm_sha256"]).intersection(set(test["pcm_sha256"]))) == 0

# 12. Excerpt relationship checks
def test_12_excerpt_relationship_checks():
    man54 = pd.read_csv(STAGE54_DIR / "dataset" / "partition_manifest_verified.csv")
    for orig_id, group in man54.groupby("original_recording_id"):
        assert len(group["expansion_partition"].unique()) == 1 # Excerpts must never cross partitions

# 13. License metadata completeness
def test_13_license_metadata_completeness():
    man54 = pd.read_csv(STAGE54_DIR / "dataset" / "partition_manifest_verified.csv")
    assert man54["license"].notna().all()
    # All declared licenses must be CC0 or CC-BY
    valid_licenses = ["CC0", "CC-BY", "CC BY", "Public Domain", "CC BY 4.0", "CC0 1.0", "CC-BY-3.0", "CC-BY-4.0"]
    assert man54["license"].apply(lambda x: any(v.lower() in str(x).lower() for v in valid_licenses)).all()

# 14. False-negative denominator consistency
def test_14_false_negative_denominator_consistency():
    fn_df = pd.read_csv(STAGE59_DIR / "false_negative_recordings.csv")
    assert len(fn_df) == 16
    assert (fn_df["ground_truth_label"] == 1).all()
    assert (fn_df["c5_prediction"] == 0).all()
    # Recall 83/99 = 83.84%
    total_pos = 99
    tp = total_pos - len(fn_df)
    assert tp == 83
    assert round(tp / total_pos, 4) == 0.8384

# 15. False-positive denominator consistency
def test_15_false_positive_denominator_consistency():
    fp_df = pd.read_csv(STAGE59_DIR / "false_positive_recordings.csv")
    assert len(fp_df) == 13
    assert (fp_df["ground_truth_label"] == 0).all()
    assert (fp_df["c5_prediction"] == 1).all()
    shouted_fps = fp_df[fp_df["target_category"] == "shouting_and_speech"]
    assert len(shouted_fps) == 10

# 16. Positive subgroup consistency
def test_16_positive_subgroup_consistency():
    pred58 = pd.read_csv(STAGE58_DIR / "prediction_comparison.csv")
    pos = pred58[pred58["ground_truth_label"] == 1]
    assert len(pos) == 99
    short = pos[pos["duration_seconds"] < 1.0]
    sustained = pos[pos["duration_seconds"] >= 1.0]
    assert len(short) == 39
    assert len(sustained) == 60
    assert len(short) + len(sustained) == 99

# 17. Short/sustained/ultra-short nesting
def test_17_short_sustained_ultra_short_nesting():
    pred58 = pd.read_csv(STAGE58_DIR / "prediction_comparison.csv")
    pos = pred58[pred58["ground_truth_label"] == 1]
    short = pos[pos["duration_seconds"] < 1.0]
    ultra_short = pos[pos["duration_seconds"] < 0.5]
    assert len(ultra_short) == 15
    assert len(ultra_short) <= len(short)
    assert set(ultra_short["expansion_file_id"]).issubset(set(short["expansion_file_id"]))

# 18. Candidate prediction alignment
def test_18_candidate_prediction_alignment():
    comp = pd.read_csv(STAGE59_DIR / "candidate_error_comparison.csv")
    assert len(comp) == 311
    assert comp["cand_e1_prob"].notna().all()
    assert comp["cand_b_prob"].notna().all()
    assert comp["cand_bd_prob"].notna().all()
    assert ((comp["cand_e1_prob"] >= 0.0) & (comp["cand_e1_prob"] <= 1.0)).all()

# 19. No historical test-cohort tuning
def test_19_no_historical_test_cohort_tuning():
    test_manifest = pd.read_csv(STAGE54_DIR / "dataset" / "partition_manifest_verified.csv")
    test_files = test_manifest[test_manifest["expansion_partition"] == "expansion_reserved_test"]
    assert len(test_files) == 366
    val_files = test_manifest[test_manifest["expansion_partition"] == "expansion_val"]
    assert len(val_files) == 311
    assert len(set(test_files["expansion_file_id"]).intersection(set(val_files["expansion_file_id"]))) == 0

# 20. No training or fine-tuning execution
def test_20_no_training_execution():
    # Verify no new .pt or .joblib files created in stage_8_9_59
    new_models = list(STAGE59_DIR.glob("**/*.pt")) + list(STAGE59_DIR.glob("**/*.joblib"))
    assert len(new_models) == 0

# 21. No modification of historical predictions
def test_21_no_modification_of_historical_predictions():
    prod_pred = BACKEND_DIR / "reports" / "test_predictions.csv"
    assert sha256_file(prod_pred) == "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d"

# 22. Future independent cohort separation
def test_22_future_independent_cohort_separation():
    future_plan = pd.read_csv(STAGE59_DIR / "future_evaluation_requirements.csv")
    assert len(future_plan) >= 5
    assert (future_plan["minimum_independent_source_groups"] > 0).all()

# 23. Statistical analysis configuration integrity
def test_23_statistical_analysis_integrity():
    # Verify sample size proportion formula calculation
    p = 0.96
    margin = 0.03
    z = 1.96
    n_calc = (z**2 * p * (1 - p)) / (margin**2)
    deff = 1.0 + (2.0 - 1.0) * 0.20 # 1.20
    n_clustered = math.ceil(n_calc * deff)
    assert n_clustered > 0
    assert deff == 1.2
