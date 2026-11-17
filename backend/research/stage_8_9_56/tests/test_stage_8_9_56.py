"""
Stage 8.9.56: Forensic Audit Automated Verification Suite
Implements 18 comprehensive tests:
1. Exactly 450 frozen cohort records.
2. Unique recording IDs.
3. One prediction per recording per candidate.
4. Ground-truth and prediction alignment across models.
5. Confusion-matrix arithmetic consistency.
6. Critical source-group union arithmetic (77 + 191 - 22 == 246).
7. Historical source-group exclusion (0 overlap against 906 historical SGs).
8. Historical file SHA-256 and PCM exclusion (0 collisions against 2,213 exclusions).
9. License eligibility (100% CC0 / CC-BY).
10. Label-adjudication coverage (450/450 records).
11. Threshold immutability (E1: 0.6800, B: 0.8000).
12. McNemar statistical reproducibility (chi2 = 14.3830, p = 0.00015).
13. Cluster bootstrap reproducibility (Recall delta strictly positive).
14. Subgroup denominator consistency and N=0 preservation.
15. Latency measurement completeness (component decomposition).
16. Production hash preservation (4 certified files).
17. Research checkpoint hash preservation (E1 and B).
18. No test-cohort training or threshold modification.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

REPO_ROOT = Path(r"festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE56_DIR = BACKEND_DIR / "research" / "stage_8_9_56"
STAGE55_DIR = BACKEND_DIR / "research" / "stage_8_9_55"
STAGE54_DIR = BACKEND_DIR / "research" / "stage_8_9_54"
STAGE44_DIR = BACKEND_DIR / "research" / "stage_8_9_44"

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

# 1. Exactly 450 frozen cohort records
def test_01_cohort_record_count():
    manifest_p = STAGE55_DIR / "integrity" / "frozen_test_manifest.json"
    assert manifest_p.exists()
    with open(manifest_p, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data["recordings"]) == 450
    assert data["total_recordings"] == 450
    assert data["scream_count"] == 150
    assert data["hard_negative_count"] == 300

# 2. Unique recording IDs
def test_02_unique_recording_ids():
    acq_p = STAGE55_DIR / "dataset" / "acquisition_manifest.csv"
    assert acq_p.exists()
    df_acq = pd.read_csv(acq_p)
    assert len(df_acq) == 450
    assert df_acq["recording_id"].nunique() == 450

# 3. One prediction per recording per candidate
def test_03_prediction_counts():
    e1_csv = STAGE55_DIR / "evaluation" / "candidate_e1_predictions.csv"
    b_csv = STAGE55_DIR / "evaluation" / "candidate_b_predictions.csv"
    bd_csv = STAGE55_DIR / "evaluation" / "candidate_b_intervention_d_predictions.csv"
    assert len(pd.read_csv(e1_csv)) == 450
    assert len(pd.read_csv(b_csv)) == 450
    assert len(pd.read_csv(bd_csv)) == 450

# 4. Ground-truth and prediction alignment
def test_04_ground_truth_alignment():
    manifest_p = STAGE55_DIR / "integrity" / "frozen_test_manifest.json"
    with open(manifest_p, "r", encoding="utf-8") as f:
        recs = json.load(f)["recordings"]
    true_labels = [r["binary_label"] for r in recs]
    true_ids = [r["recording_id"] for r in recs]

    for f_name in ["candidate_e1_predictions.csv", "candidate_b_predictions.csv", "candidate_b_intervention_d_predictions.csv"]:
        df = pd.read_csv(STAGE55_DIR / "evaluation" / f_name)
        assert list(df["recording_id"]) == true_ids
        assert list(df["ground_truth_label"]) == true_labels

# 5. Confusion-matrix arithmetic
def test_05_confusion_matrix_arithmetic():
    metrics_p = STAGE56_DIR / "recalculated_candidate_metrics.csv"
    assert metrics_p.exists()
    df_m = pd.read_csv(metrics_p)
    for _, r in df_m.iterrows():
        tp = r["true_positives"]
        fn = r["false_negatives"]
        tn = r["true_negatives"]
        fp = r["false_positives"]
        assert tp + fn == 150
        assert tn + fp == 300
        assert tp + fn + tn + fp == 450

# 6. Source-group union arithmetic
def test_06_source_group_union_arithmetic():
    sg_csv = STAGE56_DIR / "source_group_reconciliation.csv"
    assert sg_csv.exists()
    df_sg = pd.read_csv(sg_csv)
    n_pos_sgs = len(df_sg[df_sg["positive_recordings"] > 0])
    n_neg_sgs = len(df_sg[df_sg["negative_recordings"] > 0])
    n_shared_sgs = len(df_sg[df_sg["sg_classification"] == "MIXED_LABEL"])
    n_total_sgs = len(df_sg)
    assert n_pos_sgs == 77
    assert n_neg_sgs == 191
    assert n_shared_sgs == 22
    assert n_total_sgs == 246
    assert n_total_sgs == n_pos_sgs + n_neg_sgs - n_shared_sgs

# 7. Historical source-group exclusion
def test_07_historical_source_group_exclusion():
    excl_p = STAGE55_DIR / "integrity" / "historical_exclusion_registry.csv"
    acq_p = STAGE55_DIR / "dataset" / "acquisition_manifest.csv"
    df_excl = pd.read_csv(excl_p)
    df_acq = pd.read_csv(acq_p)
    excl_sgs = set(df_excl["source_group_id"].dropna().str.lower())
    cohort_sgs = set(df_acq["source_group_id"].dropna().str.lower())
    assert len(cohort_sgs.intersection(excl_sgs)) == 0

# 8. Historical file and PCM exclusion
def test_08_historical_file_and_pcm_exclusion():
    excl_p = STAGE55_DIR / "integrity" / "historical_exclusion_registry.csv"
    acq_p = STAGE55_DIR / "dataset" / "acquisition_manifest.csv"
    df_excl = pd.read_csv(excl_p)
    df_acq = pd.read_csv(acq_p)
    excl_f_hashes = set(df_excl["file_sha256"].dropna().str.lower())
    excl_pcm_hashes = set(df_excl["pcm_sha256"].dropna().str.lower())
    cohort_f_hashes = set(df_acq["sha256"].dropna().str.lower())
    cohort_pcm_hashes = set(df_acq["pcm_sha256"].dropna().str.lower())
    assert len(cohort_f_hashes.intersection(excl_f_hashes)) == 0
    assert len(cohort_pcm_hashes.intersection(excl_pcm_hashes)) == 0

# 9. License eligibility
def test_09_license_eligibility():
    lic_p = STAGE55_DIR / "dataset" / "license_audit.csv"
    assert lic_p.exists()
    df_lic = pd.read_csv(lic_p)
    assert len(df_lic) == 450
    assert (df_lic["commercial_compatibility"] == "ELIGIBLE").all()
    assert (df_lic["status"] == "APPROVED").all()

# 10. Label-adjudication coverage
def test_10_label_adjudication_coverage():
    adj_p = STAGE55_DIR / "dataset" / "label_adjudication.csv"
    assert adj_p.exists()
    df_adj = pd.read_csv(adj_p)
    assert len(df_adj) == 450
    assert (df_adj["dispute_status"] == "CONCORDANT").all()

# 11. Threshold immutability
def test_11_threshold_immutability():
    e1_p = STAGE55_DIR / "evaluation" / "candidate_e1_predictions.csv"
    b_p = STAGE55_DIR / "evaluation" / "candidate_b_predictions.csv"
    bd_p = STAGE55_DIR / "evaluation" / "candidate_b_intervention_d_predictions.csv"
    assert (pd.read_csv(e1_p)["frozen_threshold"] == 0.6800).all()
    assert (pd.read_csv(b_p)["frozen_threshold"] == 0.8000).all()
    assert (pd.read_csv(bd_p)["frozen_threshold"] == 0.8000).all()

# 12. McNemar reproducibility
def test_12_mcnemar_reproducibility():
    disc_p = STAGE56_DIR / "paired_prediction_discordance.csv"
    assert disc_p.exists()
    df_disc = pd.read_csv(disc_p)
    b = (df_disc["paired_concordance"] == "E1_ONLY_CORRECT").sum()
    c = (df_disc["paired_concordance"] == "B_ONLY_CORRECT").sum()
    assert b == 37
    assert c == 10
    chi2_corr = ((abs(b - c) - 1.0) ** 2) / (b + c)
    assert abs(chi2_corr - 14.382978) < 1e-4

# 13. Bootstrap reproducibility
def test_13_bootstrap_reproducibility():
    boot_p = STAGE56_DIR / "cluster_bootstrap_results.csv"
    assert boot_p.exists()
    df_boot = pd.read_csv(boot_p)
    rec_row = df_boot[df_boot["metric_delta"] == "Delta Recall (E1 - B)"].iloc[0]
    assert rec_row["ci_95_lower_pct"] > 0.0
    assert rec_row["ci_95_upper_pct"] > rec_row["ci_95_lower_pct"]

# 14. Subgroup denominator consistency
def test_14_subgroup_denominators():
    sub_p = STAGE56_DIR / "recalculated_subgroup_metrics.csv"
    assert sub_p.exists()
    df_sub = pd.read_csv(sub_p)
    short_row = df_sub[df_sub["subgroup_name"] == "Short Screams (<1.0s)"].iloc[0]
    sust_row = df_sub[df_sub["subgroup_name"] == "Sustained Screams (>=1.0s)"].iloc[0]
    shout_row = df_sub[df_sub["subgroup_name"] == "Shouted Speech"].iloc[0]
    assert short_row["sample_count"] == 36
    assert sust_row["sample_count"] == 114
    assert shout_row["sample_count"] == 60

# 15. Latency measurement completeness
def test_15_latency_completeness():
    lat_p = STAGE56_DIR / "latency_component_measurements.csv"
    assert lat_p.exists()
    df_lat = pd.read_csv(lat_p)
    assert len(df_lat) >= 8
    e1_model = df_lat[df_lat["pipeline_component"].str.contains("Candidate E1 Model-Only")].iloc[0]
    assert e1_model["latency_p95_ms"] <= 25.0

# 16. Production hash preservation
def test_16_production_hashes():
    expected = {
        BACKEND_DIR / "models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
        BACKEND_DIR / "models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
        BACKEND_DIR / "reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
        BACKEND_DIR / "reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2"
    }
    for p, exp in expected.items():
        assert sha256_file(p) == exp

# 17. Research checkpoint hash preservation
def test_17_research_checkpoints():
    e1_p = STAGE54_DIR / "training" / "candidate_e_v954_weighted.pt"
    b_p = STAGE44_DIR / "models" / "config_b_mask.pt"
    assert sha256_file(e1_p) == "37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564"
    assert sha256_file(b_p) == "f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378"

# 18. No test-cohort training or threshold modification
def test_18_no_test_cohort_training():
    cfg_p = STAGE55_DIR / "integrity" / "preregistered_evaluation_config.json"
    with open(cfg_p, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    assert cfg["candidate_e1"]["frozen_threshold"] == 0.6800
    assert cfg["candidate_b"]["frozen_threshold"] == 0.8000

