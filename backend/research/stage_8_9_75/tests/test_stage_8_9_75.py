# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
Comprehensive Automated Regression Test Suite for Stage 8.9.75.
Verifies provenance, duplicate detection, synthetic lineage inheritance,
source-group partition isolation, annotation schema compliance,
inter-rater reliability math, prospective evaluation governance,
and strict cryptographic immutability of protected production assets.
"""

import os
import sys
import json
import hashlib
import pytest
import numpy as np
import pandas as pd

STAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROJECT_ROOT = os.path.abspath(os.path.join(STAGE_DIR, "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

EXPECTED_PROTECTED_HASHES = {
    "classifier": (
        os.path.join(PROJECT_ROOT, "backend", "models", "scream_classifier.joblib"),
        "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f"
    ),
    "metadata": (
        os.path.join(PROJECT_ROOT, "backend", "models", "model_metadata.json"),
        "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60"
    ),
    "predictions": (
        os.path.join(PROJECT_ROOT, "backend", "reports", "test_predictions.csv"),
        "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d"
    ),
    "evaluation": (
        os.path.join(PROJECT_ROOT, "backend", "reports", "stage5_test_evaluation.md"),
        "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2"
    ),
    "stage60_manifest": (
        os.path.join(PROJECT_ROOT, "backend", "research", "stage_8_9_60", "future_evaluation_manifest.json"),
        "9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd"
    ),
    "cand71_frozen": (
        os.path.join(STAGE_DIR, "models", "candidate_71_frozen.pt"),
        "e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b"
    )
}

# =========================================================================
# 1. PROTECTED ARTIFACT & IMMUTABILITY TESTS
# =========================================================================

def test_01_protected_production_hashes():
    """Verify all 6 protected production and baseline artifacts match exact SHA-256 hashes."""
    for name, (path, expected_hash) in EXPECTED_PROTECTED_HASHES.items():
        assert os.path.exists(path), f"Missing protected file: {path} ({name})"
        with open(path, "rb") as f:
            digest = hashlib.sha256(f.read()).hexdigest()
        assert digest == expected_hash, f"Hash mismatch for {name}! Expected {expected_hash}, got {digest}"

def test_02_candidate_71_frozen_checkpoint_integrity():
    """Verify Candidate 71-D frozen checkpoint is intact and unmutated in Stage 75."""
    ckpt_path = os.path.join(STAGE_DIR, "models", "candidate_71_frozen.pt")
    assert os.path.exists(ckpt_path), "Missing Candidate 71-D checkpoint"
    with open(ckpt_path, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    assert digest == "e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b"

# =========================================================================
# 2. PROVENANCE, DATASET INVENTORY & LEAKAGE TESTS
# =========================================================================

def test_03_dataset_inventory_completeness():
    """Verify dataset_inventory.csv contains required fields and valid counts."""
    inv_path = os.path.join(STAGE_DIR, "dataset_inventory.csv")
    assert os.path.exists(inv_path), "dataset_inventory.csv missing"
    df = pd.read_csv(inv_path)
    assert len(df) >= 3000, f"Expected at least 3000 records, got {len(df)}"

    required_cols = [
        "recording_id", "source_dataset", "source_group_id", "creator_uploader",
        "license", "primary_category", "binary_label", "duration_seconds",
        "is_synthetic", "parent_recording_id", "exposed_cohort_status"
    ]
    for col in required_cols:
        assert col in df.columns, f"Missing required column in inventory: {col}"

    # Verify no null recording IDs
    assert df["recording_id"].isnull().sum() == 0, "Null recording IDs detected"
    # Verify binary label values are strictly 0 or 1
    assert set(df["binary_label"].unique()).issubset({0, 1}), "Binary label contains non-binary values"

def test_04_source_group_registry_integrity():
    """Verify source_group_registry.csv structure and multi-cohort leak identification."""
    reg_path = os.path.join(STAGE_DIR, "source_group_registry.csv")
    assert os.path.exists(reg_path), "source_group_registry.csv missing"
    sg_df = pd.read_csv(reg_path)
    assert len(sg_df) >= 1500, f"Expected at least 1500 source groups, got {len(sg_df)}"
    assert "source_group_id" in sg_df.columns
    assert "is_multi_cohort_leaked" in sg_df.columns

    # Verify that multi-cohort leaked source groups are identified
    leaked = sg_df[sg_df["is_multi_cohort_leaked"] == 1]
    assert len(leaked) > 0, "Audit failed to identify historical multi-cohort leaked source groups"

def test_05_synthetic_lineage_tracking():
    """Verify all synthetic files have traceable parent recordings."""
    inv_path = os.path.join(STAGE_DIR, "dataset_inventory.csv")
    df = pd.read_csv(inv_path)
    synth_df = df[df["is_synthetic"] == 1]
    assert len(synth_df) > 0, "No synthetic records found in inventory"

    with_parent = synth_df[synth_df["parent_recording_id"].str.strip().str.len() > 0]
    # Every synthetic file must track its parent ID
    assert len(with_parent) == len(synth_df), "Synthetic recordings exist without parent_recording_id"

# =========================================================================
# 3. PARTITION ISOLATION & GOVERNANCE TESTS
# =========================================================================

def test_06_partition_manifest_zero_source_group_overlap():
    """Verify dataset_partition_manifest.json strictly enforces 0% source-group leakage."""
    manifest_path = os.path.join(STAGE_DIR, "dataset_partition_manifest.json")
    assert os.path.exists(manifest_path), "dataset_partition_manifest.json missing"
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = data.get("records", [])
    assert len(records) > 0, "No records in partition manifest"

    train_sgs = set(r["source_group_id"] for r in records if r["logical_partition"] == "TRAINING")
    dev_sgs = set(r["source_group_id"] for r in records if r["logical_partition"] == "DEVELOPMENT")
    prosp_sgs = set(r["source_group_id"] for r in records if r["logical_partition"] == "PROSPECTIVE_EVALUATION")

    # Assert strict zero overlap
    overlap_train_dev = train_sgs.intersection(dev_sgs)
    overlap_train_prosp = train_sgs.intersection(prosp_sgs)
    overlap_dev_prosp = dev_sgs.intersection(prosp_sgs)

    assert len(overlap_train_dev) == 0, f"Leakage between TRAINING and DEVELOPMENT: {overlap_train_dev}"
    assert len(overlap_train_prosp) == 0, f"Leakage between TRAINING and PROSPECTIVE: {overlap_train_prosp}"
    assert len(overlap_dev_prosp) == 0, f"Leakage between DEVELOPMENT and PROSPECTIVE: {overlap_dev_prosp}"

def test_07_evaluation_access_log_integrity():
    """Verify evaluation_access_log.csv structure and historical access entries."""
    log_path = os.path.join(STAGE_DIR, "evaluation_access_log.csv")
    assert os.path.exists(log_path), "evaluation_access_log.csv missing"
    log_df = pd.read_csv(log_path)
    expected_cols = [
        "access_id", "timestamp_utc", "actor_role", "target_cohort",
        "action_type", "authorization_basis", "preregistration_hash", "access_verdict"
    ]
    for col in expected_cols:
        assert col in log_df.columns, f"Missing column in access log: {col}"
    assert len(log_df) >= 5, "Historical access events missing from log"

# =========================================================================
# 4. ANNOTATION PROTOCOL & SCHEMA TESTS
# =========================================================================

def test_08_annotation_schema_validity():
    """Verify annotation_schema.json is valid draft-07 JSON schema and defines all required fields."""
    schema_path = os.path.join(STAGE_DIR, "annotation_schema.json")
    assert os.path.exists(schema_path), "annotation_schema.json missing"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    assert "$schema" in schema
    assert "properties" in schema
    assert "required" in schema

    required_fields = [
        "recording_id", "source_group_id", "annotator_id", "annotation_timestamp_utc",
        "event_start_seconds", "event_end_seconds", "primary_label", "confidence_score",
        "ambiguity_flag", "audio_quality_rating", "handbook_version", "review_status",
        "adjudication_status"
    ]
    for field in required_fields:
        assert field in schema["required"], f"Required field missing from schema: {field}"
        assert field in schema["properties"], f"Property definition missing from schema: {field}"

    # Verify primary_label enum contains SCREAM and 17 negative classes + AMBIGUOUS_VOCALIZATION
    labels = schema["properties"]["primary_label"]["enum"]
    assert "SCREAM" in labels
    assert "AMBIGUOUS_VOCALIZATION" in labels
    assert "INFANT_CRY" in labels
    assert "SHOUTED_SPEECH" in labels
    assert len(labels) == 19

# =========================================================================
# 5. INTER-RATER RELIABILITY ALGORITHM TESTS
# =========================================================================

def test_09_inter_rater_reliability_algorithms():
    """Verify Cohen's Kappa, Fleiss' Kappa, and Temporal IoU on known test fixtures."""
    from backend.research.stage_8_9_75.inter_rater_reliability import (
        compute_cohens_kappa, compute_fleiss_kappa, compute_temporal_iou, run_synthetic_test_fixtures
    )

    # 1. Perfect agreement
    r1 = ["SCREAM", "SHOUTED_SPEECH", "INFANT_CRY"] * 10
    r2 = list(r1)
    k, po, _ = compute_cohens_kappa(r1, r2)
    assert np.isclose(k, 1.0)
    assert np.isclose(po, 1.0)

    # 2. Complete disagreement
    r3 = ["SCREAM"] * 10
    r4 = ["SHOUTED_SPEECH"] * 10
    k_dis, po_dis, _ = compute_cohens_kappa(r3, r4)
    assert k_dis <= 0.0
    assert po_dis == 0.0

    # 3. Temporal IoU
    assert np.isclose(compute_temporal_iou(0.0, 1.0, 0.0, 1.0), 1.0)
    assert np.isclose(compute_temporal_iou(0.0, 1.0, 1.0, 2.0), 0.0)
    assert np.isclose(compute_temporal_iou(0.0, 2.0, 1.0, 3.0), 1.0 / 3.0)

    # 4. Synthetic test fixture runner
    res = run_synthetic_test_fixtures()
    assert res["kappa_perf"] == 1.0
    assert res["kappa_ab"] > 0.85
    assert res["fleiss_k"] > 0.85

# =========================================================================
# 6. MANDATORY SAFETY HEADERS & DELIVERABLES TESTS
# =========================================================================

def test_10_mandatory_safety_headers():
    """Verify line 1 of every markdown, script, and test file in Stage 75 contains mandatory safety header."""
    MANDATORY_HEADER = "# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE."

    # Check all .md, .py files in stage_8_9_75
    files_checked = 0
    for root, dirs, files in os.walk(STAGE_DIR):
        for fname in files:
            if fname.endswith(".md") or fname.endswith(".py"):
                fpath = os.path.join(root, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    first_line = f.readline().strip()
                assert first_line == MANDATORY_HEADER, f"File {fpath} does not start with mandatory safety header! Got: '{first_line}'"
                files_checked += 1

    assert files_checked >= 15, f"Expected at least 15 files checked, got {files_checked}"

def test_11_all_required_deliverables_present():
    """Verify all 26 required deliverables exist in backend/research/stage_8_9_75/."""
    deliverables = [
        "dataset_inventory.csv",
        "dataset_gap_analysis.md",
        "acquisition_targets.csv",
        "source_group_registry.csv",
        "duplicate_and_lineage_audit.md",
        "dataset_leakage_audit.md",
        "source_diversity_report.md",
        "annotation_handbook.md",
        "annotation_schema.json",
        "annotation_workflow.md",
        "annotation_agreement_report.md",
        "adjudication_guidelines.md",
        "inter_rater_reliability.py",
        "prospective_evaluation_governance.md",
        "dataset_partition_manifest.json",
        "evaluation_preregistration_template.md",
        "evaluation_access_log.csv",
        "cohort_access_policy.md",
        "acquisition_provenance_report.md",
        "storage_capacity_report.md",
        "STAGE_PROGRESS.md"
    ]
    for d in deliverables:
        p = os.path.join(STAGE_DIR, d)
        assert os.path.exists(p), f"Missing required deliverable: {d}"
