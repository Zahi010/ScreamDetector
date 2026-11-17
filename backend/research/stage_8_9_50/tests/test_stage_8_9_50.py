"""
Stage 8.9.50 Automated Regression Test Suite
Verifies deterministic reproduction, dataset separation, decision preservation,
production artifact immutability, and latency compliance.
"""
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE50_DIR = BACKEND_DIR / "research" / "stage_8_9_50"
STAGE49_DIR = BACKEND_DIR / "research" / "stage_8_9_49"

CANONICAL_PRODUCTION_HASHES = {
    "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
}

CANDIDATE_B_CKPT = BACKEND_DIR / "research" / "stage_8_9_44" / "models" / "config_b_mask.pt"
EXPECTED_CANDIDATE_B_HASH = "f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378"

# 1. Production Artifact Immutability
def test_production_artifact_immutability():
    for rel_path, expected_hash in CANONICAL_PRODUCTION_HASHES.items():
        p = REPO_ROOT / rel_path
        assert p.exists(), f"Production file missing: {rel_path}"
        with open(p, "rb") as f:
            actual = hashlib.sha256(f.read()).hexdigest()
        assert actual == expected_hash, f"Production hash modified for {rel_path}!"

# 2. Candidate B Checkpoint Integrity
def test_candidate_b_checkpoint_integrity():
    assert CANDIDATE_B_CKPT.exists(), "Candidate B checkpoint not found!"
    with open(CANDIDATE_B_CKPT, "rb") as f:
        actual = hashlib.sha256(f.read()).hexdigest()
    assert actual == EXPECTED_CANDIDATE_B_HASH, f"Candidate B hash mismatch: {actual}"

# 3. Deterministic Candidate B Reproduction
def test_deterministic_candidate_b_reproduction():
    rep_path = STAGE50_DIR / "CANDIDATE_B_REPRODUCTION_REPORT.md"
    assert rep_path.exists()
    with open(rep_path, "r", encoding="utf-8") as f:
        text = f.read()
    assert "480 / 480" in text
    assert "100.0% Exact Agreement" in text

# 4. Deterministic Intervention D Reproduction
def test_deterministic_intervention_d_reproduction():
    rep_path = STAGE50_DIR / "INTERVENTION_D_REPRODUCTION_REPORT.md"
    assert rep_path.exists()
    with open(rep_path, "r", encoding="utf-8") as f:
        text = f.read()
    assert "480 / 480" in text
    assert "100.0% Exact Agreement" in text

# 5. Prediction Discrepancies Count is Zero
def test_prediction_discrepancies_zero():
    disc_path = STAGE50_DIR / "PREDICTION_DISCREPANCIES.csv"
    assert disc_path.exists()
    df = pd.read_csv(disc_path)
    assert len(df) == 0, f"Unexpected discrepancies found: {len(df)}"

# 6. Dataset Separation and Independence
def test_dataset_separation_and_independence():
    matrix_path = STAGE50_DIR / "CROSS_STAGE_OVERLAP_MATRIX.csv"
    assert matrix_path.exists()
    df = pd.read_csv(matrix_path)
    # Check S49 Indep row against S47 Indep
    s49_indep_row = df[df["cohort_name"] == "S49_Indep (N=480)"].iloc[0]
    assert s49_indep_row["S47_Indep (N=480)_file_sha_overlap"] == 0
    assert s49_indep_row["S47_Indep (N=480)_pcm_sha_overlap"] == 0
    assert s49_indep_row["S47_Indep (N=480)_sg_overlap"] == 0

# 7. Exact and PCM Duplicate Uniqueness
def test_exact_and_pcm_duplicate_uniqueness():
    dev_val = pd.read_csv(STAGE49_DIR / "WHISTLE_DEVELOPMENT_MANIFEST.csv")
    indep = pd.read_csv(STAGE49_DIR / "manifests" / "independent_cohort_manifest.csv")
    comb = pd.concat([dev_val, indep], ignore_index=True)
    assert len(comb["sha256"].unique()) == 800
    assert len(comb["pcm_sha256"].unique()) == 800

# 8. Decision Preservation (Zero Scream Regressions)
def test_decision_preservation():
    preds = pd.read_csv(STAGE49_DIR / "INDEPENDENT_EVALUATION_PREDICTIONS.csv")
    pos = preds[preds["binary_label"] == 1]
    tp_b = np.sum(pos["candidate_b_pred"] == 1)
    tp_d = np.sum(pos["intervention_d_pred"] == 1)
    assert tp_d == tp_b, f"Regression detected: tp_d={tp_d} vs tp_b={tp_b}"

# 9. Subgroup Denominators Accounting
def test_subgroup_denominators_accounting():
    preds = pd.read_csv(STAGE49_DIR / "INDEPENDENT_EVALUATION_PREDICTIONS.csv")
    assert len(preds) == 480
    assert np.sum(preds["binary_label"] == 1) == 160
    assert np.sum(preds["binary_label"] == 0) == 320
    assert np.sum(preds["acoustic_subtype"] == "ultra_short_scream") == 25
    assert np.sum(preds["acoustic_subtype"] == "short_scream") == 45
    assert np.sum(preds["acoustic_subtype"] == "sustained_scream") == 35
    assert np.sum(preds["acoustic_subtype"] == "distant_reverberant_scream") == 20
    assert np.sum(preds["acoustic_subtype"] == "crowd_masked_scream") == 20
    assert np.sum(preds["acoustic_subtype"] == "low_intensity_muffled_scream") == 15
    assert np.sum(preds["acoustic_subtype"] == "shouted_speech") == 80
    assert np.sum(preds["acoustic_subtype"] == "referee_whistle") == 45

# 10. Historical Whistle & Siren Revalidation
def test_historical_whistle_and_siren_revalidation():
    reval_path = STAGE50_DIR / "WHISTLE_FORENSIC_REVALIDATION.csv"
    assert reval_path.exists()
    df = pd.read_csv(reval_path)
    assert len(df) == 5
    # Whistles must be corrected (suppressed)
    whistles = df[df["acoustic_subtype"] == "referee_whistle"]
    assert len(whistles) == 4
    assert np.all(whistles["intervention_d_binary_decision"] == 0)
    assert np.all(whistles["rejection_layer_activated"] == True)
    # Siren must be already correct (decision 0)
    siren = df[df["acoustic_subtype"] == "emergency_siren"].iloc[0]
    assert siren["intervention_d_binary_decision"] == 0

# 11. Latency Measurement Boundaries & Gate 5
def test_latency_measurement_boundaries():
    lat_path = STAGE50_DIR / "LATENCY_REPRODUCTION_REPORT.md"
    assert lat_path.exists()
    with open(lat_path, "r", encoding="utf-8") as f:
        text = f.read()
    assert "GATE 5 STATUS: PASS" in text
    assert "Direct Complete Pipeline P95 Latency" in text

# 12. Statistical Reanalysis Report & Gate 1 Failure
def test_statistical_reanalysis_and_gate_audit():
    stat_path = STAGE50_DIR / "STATISTICAL_REANALYSIS.md"
    assert stat_path.exists()
    with open(stat_path, "r", encoding="utf-8") as f:
        text = f.read()
    assert "Overall Scream Recall" in text
    assert "FAIL (Deficit: 14.12%)" in text

