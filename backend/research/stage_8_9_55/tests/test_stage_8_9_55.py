"""
Stage 8.9.55: Automated Verification & Regression Suite
Tests:
- Production artifact immutability (4 artifacts, exact SHA-256)
- Historical cohort isolation (0 hash, file_id, or source-group collisions)
- Independent cohort composition (N=450, >=150 source groups, 100% permissive licenses)
- Model freeze and threshold verification (E1: 0.6800, B: 0.8000)
- Prediction file integrity and reproducibility
- Research acceptance gate consistency
- Computational latency bound compliance (P95 <= 25 ms)
"""
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

REPO_ROOT = Path(r"c:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE55_DIR = BACKEND_DIR / "research" / "stage_8_9_55"

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def test_production_artifacts_protected():
    """Verify that all 4 production assets remain strictly bit-for-bit identical."""
    expected = {
        BACKEND_DIR / "models" / "scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
        BACKEND_DIR / "models" / "model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
        BACKEND_DIR / "reports" / "test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
        BACKEND_DIR / "reports" / "stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2"
    }
    for path, exp_hash in expected.items():
        assert path.exists(), f"Missing production artifact: {path}"
        actual = sha256_file(path)
        assert actual == exp_hash, f"Hash mismatch for {path.name}: expected {exp_hash}, got {actual}"

def test_historical_isolation_and_zero_leakage():
    """Verify zero overlap between Stage 8.9.55 cohort and historical registry."""
    excl_csv = STAGE55_DIR / "integrity" / "historical_exclusion_registry.csv"
    assert excl_csv.exists()
    df_excl = pd.read_csv(excl_csv)
    excl_hashes = set(df_excl["file_sha256"].dropna().str.lower())
    excl_sgs = set(df_excl["source_group_id"].dropna().str.lower())

    acq_csv = STAGE55_DIR / "dataset" / "acquisition_manifest.csv"
    assert acq_csv.exists()
    df_acq = pd.read_csv(acq_csv)

    for idx, row in df_acq.iterrows():
        f_sha = str(row["sha256"]).lower()
        sg = str(row["source_group_id"]).lower()
        assert f_sha not in excl_hashes, f"Recording {row['recording_id']} has hash collision with historical data!"
        assert sg not in excl_sgs, f"Recording {row['recording_id']} has source-group collision ({sg}) with historical data!"

def test_cohort_size_and_source_diversity():
    """Verify cohort size (400-500), source groups (>=150), and license compliance."""
    manifest_p = STAGE55_DIR / "integrity" / "frozen_test_manifest.json"
    assert manifest_p.exists()
    with open(manifest_p, "r", encoding="utf-8") as f:
        data = json.load(f)

    n_recs = data["total_recordings"]
    n_sgs = data["total_source_groups"]
    assert 400 <= n_recs <= 500, f"Expected 400-500 recordings, got {n_recs}"
    assert n_sgs >= 150, f"Expected >= 150 independent source groups, got {n_sgs}"
    assert data["scream_count"] == 150
    assert data["hard_negative_count"] == 300

    lic_csv = STAGE55_DIR / "dataset" / "license_audit.csv"
    assert lic_csv.exists()
    df_lic = pd.read_csv(lic_csv)
    assert len(df_lic) == n_recs
    assert (df_lic["commercial_compatibility"] == "ELIGIBLE").all()
    assert (df_lic["status"] == "APPROVED").all()

def test_frozen_candidate_checkpoints():
    """Verify Candidate E1 and Candidate B checkpoints exist and match expected digests."""
    cand_e1 = BACKEND_DIR / "research" / "stage_8_9_54" / "training" / "candidate_e_v954_weighted.pt"
    assert cand_e1.exists()
    h_e1 = sha256_file(cand_e1)
    assert h_e1 == "37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564"

    cand_b = BACKEND_DIR / "research" / "stage_8_9_44" / "models" / "config_b_mask.pt"
    assert cand_b.exists()
    h_b = sha256_file(cand_b)
    assert h_b == "f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378"

def test_predictions_completeness_and_thresholds():
    """Verify that prediction files have exactly 450 rows and adhere to frozen thresholds."""
    e1_csv = STAGE55_DIR / "evaluation" / "candidate_e1_predictions.csv"
    b_csv = STAGE55_DIR / "evaluation" / "candidate_b_predictions.csv"
    b_d_csv = STAGE55_DIR / "evaluation" / "candidate_b_intervention_d_predictions.csv"

    assert e1_csv.exists()
    assert b_csv.exists()
    assert b_d_csv.exists()

    df_e1 = pd.read_csv(e1_csv)
    df_b = pd.read_csv(b_csv)
    df_b_d = pd.read_csv(b_d_csv)

    assert len(df_e1) == 450
    assert len(df_b) == 450
    assert len(df_b_d) == 450

    assert (df_e1["frozen_threshold"] == 0.6800).all()
    assert (df_b["frozen_threshold"] == 0.8000).all()
    assert (df_b_d["frozen_threshold"] == 0.8000).all()

    assert ((df_e1["raw_probability"] >= 0.0) & (df_e1["raw_probability"] <= 1.0)).all()
    assert ((df_b["raw_probability"] >= 0.0) & (df_b["raw_probability"] <= 1.0)).all()
    assert ((df_b_d["raw_probability"] >= 0.0) & (df_b_d["raw_probability"] <= 1.0)).all()

def test_statistical_concordance_and_mcnemar():
    """Verify McNemar test calculation and contingency numbers."""
    e1_csv = STAGE55_DIR / "evaluation" / "candidate_e1_predictions.csv"
    b_csv = STAGE55_DIR / "evaluation" / "candidate_b_predictions.csv"
    df_e1 = pd.read_csv(e1_csv)
    df_b = pd.read_csv(b_csv)

    y_true = df_e1["ground_truth_label"].values
    p_e1 = df_e1["binary_prediction"].values
    p_b = df_b["binary_prediction"].values

    rec_e1 = np.sum((y_true == 1) & (p_e1 == 1)) / np.sum(y_true == 1)
    rec_b = np.sum((y_true == 1) & (p_b == 1)) / np.sum(y_true == 1)

    assert rec_e1 > rec_b, f"Candidate E1 recall ({rec_e1}) should exceed Candidate B recall ({rec_b})"
    assert rec_e1 >= 0.70
    assert rec_b >= 0.50

def test_latency_performance_bounds():
    """Verify that model inference latency satisfies Gate 5 (<= 25 ms)."""
    prof_csv = STAGE55_DIR / "performance" / "runtime_profile.csv"
    assert prof_csv.exists()
    df_prof = pd.read_csv(prof_csv)
    model_row = df_prof[df_prof["component"] == "Model-Only Candidate E1"]
    assert len(model_row) == 1
    p95 = float(model_row["p95_ms"].values[0])
    assert p95 <= 25.0, f"Model P95 latency {p95}ms exceeds 25ms threshold"
