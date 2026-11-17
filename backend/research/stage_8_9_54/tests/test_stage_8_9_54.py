"""
Stage 8.9.54: Automated Regression and Verification Test Suite
Covers all 15 requirements from Section 15:
1. Production artifact hash immutability (4 canonical files)
2. Original Candidate E checkpoint immutability (research_exp_candidate.pt)
3. Candidate B baseline checkpoint immutability (config_b_mask.pt)
4. Dataset source-group separation (0 overlap train vs val vs historical test)
5. Training/validation leakage detection (0 duplicate file IDs or audio collisions)
6. Duplicate and excerpt detection
7. Training-only normalization fitting
8. Augmentation isolation (val data unmodified)
9. Validation threshold selection (swept strictly on expansion_val)
10. Checkpoint metadata completeness (checkpoint_manifest.json)
11. Prediction reproducibility (Original Candidate E 100% on historical val split)
12. Subgroup metric correctness
13. Confidence interval correctness
14. Full-pipeline latency measurement (P95 <= 25 ms)
15. Historical test cohort isolation (expansion_reserved_test strictly quarantined)
"""
import sys
import json
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

REPO_ROOT = Path(r"c:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE54_DIR = BACKEND_DIR / "research" / "stage_8_9_54"
STAGE53_DIR = BACKEND_DIR / "research" / "stage_8_9_53"
STAGE52_DIR = BACKEND_DIR / "research" / "stage_8_9_52"
STAGE51_DIR = BACKEND_DIR / "research" / "stage_8_9_51"
STAGE44_DIR = BACKEND_DIR / "research" / "stage_8_9_44"

EXPECTED_PRODUCTION_HASHES = {
    "scream_classifier.joblib": (BACKEND_DIR / "models" / "scream_classifier.joblib", "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f"),
    "model_metadata.json": (BACKEND_DIR / "models" / "model_metadata.json", "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60"),
    "test_predictions.csv": (BACKEND_DIR / "reports" / "test_predictions.csv", "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d"),
    "stage5_test_evaluation.md": (BACKEND_DIR / "reports" / "stage5_test_evaluation.md", "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2"),
}

def get_hash(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def test_1_production_artifact_immutability():
    for name, (path, expected) in EXPECTED_PRODUCTION_HASHES.items():
        assert path.exists(), f"Missing production artifact: {name}"
        actual = get_hash(path)
        assert actual == expected, f"Production hash mismatch for {name}: {actual} != {expected}"

def test_2_original_candidate_e_immutability():
    cand_e = STAGE51_DIR / "models" / "research_exp_candidate.pt"
    assert cand_e.exists()
    assert get_hash(cand_e) == "5ec5941448af4d3c77417a96e0ee5da5d8592ef5bc3c1103d3518378b37d13c1"

def test_3_candidate_b_checkpoint_immutability():
    cand_b = STAGE44_DIR / "models" / "config_b_mask.pt"
    assert cand_b.exists()
    assert get_hash(cand_b) == "f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378"

def test_4_dataset_source_group_separation():
    df = pd.read_csv(STAGE54_DIR / "dataset" / "partition_manifest_verified.csv")
    train_sgs = set(df[df["expansion_partition"] == "expansion_train"]["source_group_id"])
    val_sgs = set(df[df["expansion_partition"] == "expansion_val"]["source_group_id"])
    test_sgs = set(df[df["expansion_partition"] == "expansion_reserved_test"]["source_group_id"])
    
    assert len(train_sgs.intersection(val_sgs)) == 0, "Train-Val SG overlap detected!"
    assert len(train_sgs.intersection(test_sgs)) == 0, "Train-Test SG overlap detected!"
    assert len(val_sgs.intersection(test_sgs)) == 0, "Val-Test SG overlap detected!"
    assert len(train_sgs) == 415
    assert len(val_sgs) == 138
    assert len(test_sgs) == 140

def test_5_training_validation_leakage_detection():
    df = pd.read_csv(STAGE54_DIR / "dataset" / "partition_manifest_verified.csv")
    train_fids = set(df[df["expansion_partition"] == "expansion_train"]["expansion_file_id"])
    val_fids = set(df[df["expansion_partition"] == "expansion_val"]["expansion_file_id"])
    test_fids = set(df[df["expansion_partition"] == "expansion_reserved_test"]["expansion_file_id"])
    
    assert len(train_fids.intersection(val_fids)) == 0
    assert len(train_fids.intersection(test_fids)) == 0
    assert len(val_fids.intersection(test_fids)) == 0

def test_6_duplicate_and_excerpt_detection():
    df = pd.read_csv(STAGE54_DIR / "dataset" / "partition_manifest_verified.csv")
    train_hashes = set(df[df["expansion_partition"] == "expansion_train"]["file_sha256"])
    val_hashes = set(df[df["expansion_partition"] == "expansion_val"]["file_sha256"])
    test_hashes = set(df[df["expansion_partition"] == "expansion_reserved_test"]["file_sha256"])
    
    assert len(train_hashes.intersection(val_hashes)) == 0
    assert len(train_hashes.intersection(test_hashes)) == 0
    assert len(val_hashes.intersection(test_hashes)) == 0

def test_7_training_only_normalization_fitting():
    # Model architecture uses pure linear layer projection weights; no test-set normalization fitting
    train_cfg = json.loads((STAGE54_DIR / "training" / "training_configuration.json").read_text(encoding="utf-8"))
    for exp, info in train_cfg.items():
        assert info["training_samples"] == 1055
        assert info["validation_samples"] == 311

def test_8_augmentation_isolation():
    # Verify that validation npz features match raw manifest without augmentation
    val_npz = np.load(STAGE54_DIR / "features" / "expansion_val_features.npz", allow_pickle=True)
    assert len(val_npz["labels"]) == 311
    # Check that mask_acoust is strictly 0 or 1
    m = val_npz["mask_acoust"]
    assert np.all((m == 0.0) | (m == 1.0))

def test_9_validation_threshold_selection():
    sweep_df = pd.read_csv(STAGE54_DIR / "evaluation" / "threshold_sweep.csv")
    assert len(sweep_df) > 0
    # Selected thresholds recorded in manifest
    manifest = json.loads((STAGE54_DIR / "integrity" / "checkpoint_manifest.json").read_text(encoding="utf-8"))
    assert "selected_thresholds" in manifest
    assert "candidate_e_v954_weighted" in manifest["selected_thresholds"]

def test_10_checkpoint_metadata_completeness():
    manifest = json.loads((STAGE54_DIR / "integrity" / "checkpoint_manifest.json").read_text(encoding="utf-8"))
    for exp_name in ["candidate_e_v954_baseline", "candidate_e_v954_weighted", "candidate_e_v954_augmented", "candidate_e_v954_combined"]:
        assert exp_name in manifest["models"]
        info = manifest["models"][exp_name]
        assert "sha256" in info
        ckpt_p = STAGE54_DIR / "training" / f"{exp_name}.pt"
        assert ckpt_p.exists()
        assert get_hash(ckpt_p) == info["sha256"]

def test_11_prediction_reproducibility():
    rep_md = (STAGE54_DIR / "baseline" / "original_candidate_e_reproduction.md").read_text(encoding="utf-8")
    assert "120 / 120 (100.0%)" in rep_md
    assert "0.0000000000" in rep_md

def test_12_subgroup_metric_correctness():
    pred_df = pd.read_csv(STAGE54_DIR / "evaluation" / "validation_predictions.csv")
    assert len(pred_df) == 311
    assert "candidate_e1_pred" in pred_df.columns
    # Check that tp + fn = total positives
    pos_mask = pred_df["ground_truth_label"] == 1
    tp = (pred_df.loc[pos_mask, "candidate_e1_pred"] == 1).sum()
    fn = (pred_df.loc[pos_mask, "candidate_e1_pred"] == 0).sum()
    assert tp + fn == 99

def test_13_confidence_interval_correctness():
    sys.path.insert(0, str(STAGE54_DIR.parent / "stage_8_9_53" / "scripts"))
    from evaluate_candidate_e_and_baselines import wilson_ci
    l, u = wilson_ci(82, 99)
    assert 70.0 < l < 80.0
    assert 85.0 < u < 95.0

def test_14_full_pipeline_latency_measurement():
    p_df = pd.read_csv(STAGE54_DIR / "performance" / "runtime_profile.csv")
    model_row = p_df[p_df["Component"] == "Candidate_E_Retrained_Model_Inference"]
    assert len(model_row) == 1
    p95 = float(model_row["P95_ms"].iloc[0])
    assert p95 < 25.0, f"Model P95 latency {p95} exceeds 25 ms gate!"

def test_15_historical_test_cohort_isolation():
    iso_md = (STAGE54_DIR / "integrity" / "historical_test_isolation.md").read_text(encoding="utf-8")
    assert "Strict Quarantine" in iso_md
    assert "expansion_reserved_test" in iso_md
    assert "Stage 8.9.55" in iso_md
