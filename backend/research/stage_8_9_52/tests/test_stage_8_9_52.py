"""
Stage 8.9.52: Automated Test Suite & Integrity Regression Verification
Tests all 12 mandatory requirements from Section 9:
1. Recording-level reconciliation correctness.
2. Stable-ID and hash-based joins.
3. Subtype overlap handling.
4. Historical prediction reproducibility.
5. Candidate E checkpoint reproducibility.
6. Source-group split isolation.
7. Duplicate and excerpt leakage checks.
8. License quarantine.
9. Threshold-selection isolation.
10. Confidence interval calculations.
11. Full-pipeline latency measurement.
12. Production artifact immutability.
"""
import sys
import hashlib
from pathlib import Path
import pytest
import numpy as np
import pandas as pd
import torch

REPO_ROOT = Path(r"c:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE49_DIR = BACKEND_DIR / "research" / "stage_8_9_49"
STAGE51_DIR = BACKEND_DIR / "research" / "stage_8_9_51"
STAGE52_DIR = BACKEND_DIR / "research" / "stage_8_9_52"

sys.path.insert(0, str(STAGE49_DIR / "scripts"))
sys.path.insert(0, str(STAGE51_DIR / "scripts"))

from run_evaluations import wilson_ci
from run_controlled_experiments import ResearchDualHeadClassifier

# -----------------------------------------------------------------------------
# 1. RECORDING-LEVEL RECONCILIATION CORRECTNESS
# -----------------------------------------------------------------------------
def test_recording_level_reconciliation_correctness():
    recon_csv = STAGE52_DIR / "reconciliation" / "record_level_reconciliation.csv"
    assert recon_csv.exists(), "Reconciliation CSV missing!"
    df = pd.read_csv(recon_csv)
    assert len(df) == 480, f"Expected 480 records, got {len(df)}"
    
    # Verify zero prediction discrepancies between Stage 50 and Stage 51
    assert df["decision_discrepancy"].sum() == 0, "Non-zero decision discrepancies found!"
    assert df["prob_absolute_delta"].max() < 1e-6, "Non-zero probability drift found!"

# -----------------------------------------------------------------------------
# 2. STABLE-ID AND HASH-BASED JOINS
# -----------------------------------------------------------------------------
def test_stable_id_and_hash_based_joins():
    recon_csv = STAGE52_DIR / "reconciliation" / "record_level_reconciliation.csv"
    df = pd.read_csv(recon_csv)
    assert df["file_sha256"].nunique() == 480, "Hash collision in independent evaluation cohort!"
    assert df["pcm_sha256"].nunique() == 480, "PCM collision in independent evaluation cohort!"
    assert df["file_id"].nunique() == 480, "Duplicate file_id in independent evaluation cohort!"

# -----------------------------------------------------------------------------
# 3. SUBTYPE OVERLAP & COUNT HANDLING
# -----------------------------------------------------------------------------
def test_subtype_overlap_handling():
    recon_csv = STAGE52_DIR / "reconciliation" / "record_level_reconciliation.csv"
    df = pd.read_csv(recon_csv)
    pos_df = df[df["ground_truth_label"] == 1]
    
    subtypes = pos_df["acoustic_subtype"].value_counts().to_dict()
    assert subtypes["short_scream"] == 45
    assert subtypes["ultra_short_scream"] == 25
    assert subtypes["sustained_scream"] == 35
    assert subtypes["distant_reverberant_scream"] == 20
    assert subtypes["crowd_masked_scream"] == 20
    assert subtypes["low_intensity_muffled_scream"] == 15
    
    # Verify detections
    detected = pos_df.groupby("acoustic_subtype")["stage_50_interv_d_pred"].sum().to_dict()
    assert detected["short_scream"] == 41
    assert detected["ultra_short_scream"] == 25
    assert detected["sustained_scream"] == 26
    assert detected["distant_reverberant_scream"] == 20
    assert detected["crowd_masked_scream"] == 13
    assert detected["low_intensity_muffled_scream"] == 6
    
    assert sum(detected.values()) == 131, f"Expected 131 detections, got {sum(detected.values())}"
    assert len(pos_df) - sum(detected.values()) == 29, "Expected exactly 29 misses"

# -----------------------------------------------------------------------------
# 4. HISTORICAL PREDICTION REPRODUCIBILITY
# -----------------------------------------------------------------------------
def test_historical_prediction_reproducibility():
    s49_csv = STAGE49_DIR / "INDEPENDENT_EVALUATION_PREDICTIONS.csv"
    df = pd.read_csv(s49_csv)
    
    tp = np.sum((df["binary_label"] == 1) & (df["intervention_d_pred"] == 1))
    fn = np.sum((df["binary_label"] == 1) & (df["intervention_d_pred"] == 0))
    tn = np.sum((df["binary_label"] == 0) & (df["intervention_d_pred"] == 0))
    fp = np.sum((df["binary_label"] == 0) & (df["intervention_d_pred"] == 1))
    
    assert tp == 131, f"Expected 131 TP, got {tp}"
    assert fn == 29, f"Expected 29 FN, got {fn}"
    assert tn == 319, f"Expected 319 TN, got {tn}"
    assert fp == 1, f"Expected 1 FP, got {fp}"
    
    # Verify single false positive is s49_indep_neg_0009
    fp_row = df[(df["binary_label"] == 0) & (df["intervention_d_pred"] == 1)].iloc[0]
    assert fp_row["file_id"] == "s49_indep_neg_0009"
    assert fp_row["acoustic_subtype"] == "shouted_speech"

# -----------------------------------------------------------------------------
# 5. CANDIDATE E CHECKPOINT REPRODUCIBILITY
# -----------------------------------------------------------------------------
def test_candidate_e_checkpoint_reproducibility():
    cand_e_ckpt = STAGE51_DIR / "models" / "research_exp_candidate.pt"
    assert cand_e_ckpt.exists(), "Candidate E checkpoint missing!"
    
    with open(cand_e_ckpt, "rb") as f:
        h = hashlib.sha256(f.read()).hexdigest()
    assert h == "5ec5941448af4d3c77417a96e0ee5da5d8592ef5bc3c1103d3518378b37d13c1"
    
    # Load and run inference on validation split
    val_npz = np.load(STAGE49_DIR / "features" / "val_features.npz", allow_pickle=True)
    val_sem = torch.from_numpy(val_npz["X_sem"]).float()
    val_ac = torch.from_numpy(val_npz["X_acoust"]).float()
    val_m = torch.from_numpy(val_npz["mask_acoust"]).float()
    val_sb = torch.from_numpy(val_npz["X_subband"]).float()
    val_y = val_npz["labels"]
    
    model = ResearchDualHeadClassifier(sem_dim=1024, acoust_dim=6, subband_dim=11)
    model.load_state_dict(torch.load(cand_e_ckpt, map_location="cpu", weights_only=True))
    model.eval()
    
    with torch.no_grad():
        logits = model(val_sem, val_ac, val_m, val_sb).numpy()
        probs = 1.0 / (1.0 + np.exp(-logits))
        
    preds = (probs >= 0.4000).astype(int)
    tp = np.sum((val_y == 1) & (preds == 1))
    fn = np.sum((val_y == 1) & (preds == 0))
    tn = np.sum((val_y == 0) & (preds == 0))
    fp = np.sum((val_y == 0) & (preds == 1))
    
    assert tp == 48, f"Expected 48 TP, got {tp}"
    assert fn == 0, f"Expected 0 FN, got {fn}"
    assert tn == 72, f"Expected 72 TN, got {tn}"
    assert fp == 0, f"Expected 0 FP, got {fp}"

# -----------------------------------------------------------------------------
# 6. SOURCE-GROUP SPLIT ISOLATION
# -----------------------------------------------------------------------------
def test_source_group_split_isolation():
    manifest_csv = STAGE52_DIR / "dataset" / "expansion_manifest.csv"
    assert manifest_csv.exists(), "Expansion manifest missing!"
    df = pd.read_csv(manifest_csv)
    
    train_sgs = set(df[df["expansion_partition"] == "expansion_train"]["source_group_id"])
    val_sgs = set(df[df["expansion_partition"] == "expansion_val"]["source_group_id"])
    test_sgs = set(df[df["expansion_partition"] == "expansion_reserved_test"]["source_group_id"])
    
    assert len(train_sgs.intersection(val_sgs)) == 0, "Source-group overlap between train and val!"
    assert len(train_sgs.intersection(test_sgs)) == 0, "Source-group overlap between train and test!"
    assert len(val_sgs.intersection(test_sgs)) == 0, "Source-group overlap between val and test!"

# -----------------------------------------------------------------------------
# 7. DUPLICATE AND EXCERPT LEAKAGE CHECKS
# -----------------------------------------------------------------------------
def test_duplicate_and_excerpt_leakage():
    manifest_csv = STAGE52_DIR / "dataset" / "expansion_manifest.csv"
    recon_csv = STAGE52_DIR / "reconciliation" / "record_level_reconciliation.csv"
    
    df_exp = pd.read_csv(manifest_csv)
    df_recon = pd.read_csv(recon_csv)
    
    exp_file_hashes = set(df_exp["file_sha256"])
    exp_pcm_hashes = set(df_exp["pcm_sha256"])
    
    recon_file_hashes = set(df_recon["file_sha256"])
    recon_pcm_hashes = set(df_recon["pcm_sha256"])
    
    assert len(exp_file_hashes.intersection(recon_file_hashes)) == 0, "File hash collision with historical evaluation!"
    assert len(exp_pcm_hashes.intersection(recon_pcm_hashes)) == 0, "PCM collision with historical evaluation!"

# -----------------------------------------------------------------------------
# 8. LICENSE QUARANTINE
# -----------------------------------------------------------------------------
def test_license_quarantine():
    lic_csv = STAGE52_DIR / "dataset" / "license_audit.csv"
    assert lic_csv.exists(), "License audit CSV missing!"
    df = pd.read_csv(lic_csv)
    
    # Check that CC-BY-NC and Sampling+ are marked quarantined
    nc_rows = df[df["license_string"].str.contains("nc|sampling", case=False)]
    for _, r in nc_rows.iterrows():
        assert r["quarantined"] == "YES", f"Restricted license {r['license_string']} was not quarantined!"

# -----------------------------------------------------------------------------
# 9. THRESHOLD-SELECTION ISOLATION
# -----------------------------------------------------------------------------
def test_threshold_selection_isolation():
    cand_comp_csv = STAGE52_DIR / "evaluation" / "candidate_comparison_template.csv"
    assert cand_comp_csv.exists(), "Candidate comparison CSV missing!"
    df = pd.read_csv(cand_comp_csv)
    
    b_row = df[df["Candidate_Name"].str.contains("Candidate B Baseline")].iloc[0]
    assert b_row["Operating_Threshold"] == 0.8000
    
    e_row = df[df["Candidate_Name"].str.contains("Candidate E")].iloc[0]
    assert e_row["Operating_Threshold"] == 0.4000

# -----------------------------------------------------------------------------
# 10. CONFIDENCE INTERVAL CALCULATIONS
# -----------------------------------------------------------------------------
def test_confidence_interval_calculations():
    # Edge case: k=0, n=80 -> [0.00%, 4.51%]
    l0, u0 = wilson_ci(0, 80)
    assert abs(l0 - 0.0) < 1e-4
    assert abs(u0 - 4.51) < 0.1
    
    # Edge case: k=1, n=80 -> [0.22%, 6.75%]
    l1, u1 = wilson_ci(1, 80)
    assert abs(l1 - 0.22) < 0.1
    assert abs(u1 - 6.75) < 0.1
    
    # Edge case: k=48, n=48 -> [92.59%, 100.0%]
    l_full, u_full = wilson_ci(48, 48)
    assert abs(l_full - 92.59) < 0.2
    assert abs(u_full - 100.0) < 1e-4

# -----------------------------------------------------------------------------
# 11. FULL-PIPELINE LATENCY MEASUREMENT
# -----------------------------------------------------------------------------
def test_full_pipeline_latency_measurement():
    bench_csv = STAGE51_DIR / "STANDARDIZED_LATENCY_BENCHMARK.csv"
    assert bench_csv.exists(), "Standardized latency benchmark CSV missing!"
    df = pd.read_csv(bench_csv)
    
    p1 = df[df["Profile"].str.contains("Profile 1")].iloc[0]
    assert p1["Pipeline_P95_ms"] < 1.0, f"Profile 1 P95 too high: {p1['Pipeline_P95_ms']}"
    
    p2 = df[df["Profile"].str.contains("Profile 2")].iloc[0]
    assert 2.0 < p2["Pipeline_P95_ms"] < 5.0, f"Profile 2 P95 out of range: {p2['Pipeline_P95_ms']}"
    
    p8 = df[df["Profile"].str.contains("Concurrent Streams = 8")].iloc[0]
    assert p8["Pipeline_P95_ms"] <= 25.0, f"8-stream P95 exceeded 25ms: {p8['Pipeline_P95_ms']}"

# -----------------------------------------------------------------------------
# 12. CANONICAL PRODUCTION ARTIFACT IMMUTABILITY
# -----------------------------------------------------------------------------
def test_production_artifact_immutability():
    expected_production_hashes = {
        REPO_ROOT / "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
        REPO_ROOT / "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
        REPO_ROOT / "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
        REPO_ROOT / "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
        REPO_ROOT / "backend/research/stage_8_9_44/models/config_b_mask.pt": "f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378"
    }
    for path, expected in expected_production_hashes.items():
        assert path.exists(), f"Protected artifact missing: {path}"
        with open(path, "rb") as f:
            actual = hashlib.sha256(f.read()).hexdigest()
        assert actual == expected, f"Protected artifact altered: {path}!\nExpected: {expected}\nActual: {actual}"

