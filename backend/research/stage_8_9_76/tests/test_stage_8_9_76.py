# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
Comprehensive Automated Test Suite for Stage 8.9.76.
Verifies canonical taxonomy reconciliation, acquisition licensing,
uploader blacklist enforcement, audio download integrity, double-blind review staging,
prospective partition isolation, and cryptographic baseline immutability.
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
    """Verify Candidate 71-D frozen checkpoint is intact and unmutated in Stage 76."""
    ckpt_path = os.path.join(STAGE_DIR, "models", "candidate_71_frozen.pt")
    assert os.path.exists(ckpt_path), "Missing Candidate 71-D checkpoint"
    with open(ckpt_path, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    assert digest == "e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b"

# =========================================================================
# 2. TAXONOMY AND SCHEMA RECONCILIATION TESTS
# =========================================================================

def test_03_canonical_taxonomy_reconciliation():
    """Verify canonical_taxonomy.json defines 19 primary categories, 6 scream subcategories, and 24 leaf classes."""
    tax_path = os.path.join(STAGE_DIR, "canonical_taxonomy.json")
    assert os.path.exists(tax_path), "Missing canonical_taxonomy.json"
    with open(tax_path, "r", encoding="utf-8") as f:
        tax = json.load(f)

    assert tax["taxonomy_version"] == "v1.1_canonical"
    assert len(tax["primary_categories"]) == 19
    assert len(tax["scream_subcategories"]) == 6
    assert len(tax["flattened_leaf_classes"]) == 24

    # Ensure all primary codes are unique
    primary_codes = [c["code"] for c in tax["primary_categories"]]
    assert len(primary_codes) == len(set(primary_codes))
    assert "SCREAM" in primary_codes
    assert "AMBIGUOUS_VOCALIZATION" in primary_codes

    # Ensure leaf codes are unique
    assert len(tax["flattened_leaf_classes"]) == len(set(tax["flattened_leaf_classes"]))

# =========================================================================
# 3. ACQUISITION, PROVENANCE & BLACKLIST TESTS
# =========================================================================

def test_04_acquisition_provenance_and_licensing():
    """Verify all downloaded recordings have approved licenses and valid audio files."""
    prov_path = os.path.join(STAGE_DIR, "acquisition_provenance.csv")
    assert os.path.exists(prov_path), "Missing acquisition_provenance.csv"
    df_prov = pd.read_csv(prov_path)
    assert len(df_prov) >= 20, f"Expected at least 20 acquired recordings, got {len(df_prov)}"

    # Check licenses are strictly CC0, CC BY 3.0, or CC BY 4.0
    for lic in df_prov["license"]:
        assert lic in ["CC0 1.0 Universal", "CC BY 3.0", "CC BY 4.0"], f"Ineligible license in downloaded audio: {lic}"

    # Verify actual audio files exist on disk and have non-zero size
    for p in df_prov["local_audio_path"]:
        full_p = os.path.join(PROJECT_ROOT, p)
        assert os.path.exists(full_p), f"Audio file missing on disk: {full_p}"
        assert os.path.getsize(full_p) > 1000, f"Audio file unexpectedly small: {full_p}"

def test_05_uploader_blacklist_zero_leakage():
    """Verify that zero downloaded recordings originate from historical blacklisted uploaders."""
    prov_path = os.path.join(STAGE_DIR, "acquisition_provenance.csv")
    df_prov = pd.read_csv(prov_path)

    # Load Stage 75 historical uploaders
    inv_path = os.path.join(PROJECT_ROOT, "backend", "research", "stage_8_9_75", "dataset_inventory.csv")
    df_inv = pd.read_csv(inv_path)
    hist_uploaders = set()
    for u in df_inv["creator_uploader"].dropna():
        for part in str(u).split(";"):
            clean = part.strip().lower()
            if clean and clean != "unknown":
                hist_uploaders.add(clean)

    # Assert zero overlap
    acquired_uploaders = set(df_prov["creator_uploader"].str.strip().str.lower().unique())
    overlap = acquired_uploaders.intersection(hist_uploaders)
    assert len(overlap) == 0, f"Uploader leakage detected! Overlapping creators: {overlap}"

def test_06_audio_duplicate_and_pcm_integrity():
    """Verify all downloaded files have unique SHA-256 and PCM digests without collisions."""
    prov_path = os.path.join(STAGE_DIR, "acquisition_provenance.csv")
    df_prov = pd.read_csv(prov_path)

    # Internal uniqueness
    assert df_prov["file_sha256"].nunique() == len(df_prov), "Duplicate file SHA-256 detected in new batch"
    assert df_prov["pcm_sha256"].nunique() == len(df_prov), "Duplicate PCM waveform hash detected in new batch"

    # Cross-cohort historical uniqueness
    inv_path = os.path.join(PROJECT_ROOT, "backend", "research", "stage_8_9_75", "dataset_inventory.csv")
    df_inv = pd.read_csv(inv_path)
    hist_file_hashes = set(df_inv["sha256_hash"].dropna().str.strip().str.lower())
    hist_pcm_hashes = set(df_inv["pcm_sha256"].dropna().str.strip().str.lower())

    for h in df_prov["file_sha256"]:
        assert h.lower() not in hist_file_hashes, f"File SHA-256 collision with historical dataset: {h}"
    for p in df_prov["pcm_sha256"]:
        assert p.lower() not in hist_pcm_hashes, f"PCM waveform collision with historical dataset: {p}"

# =========================================================================
# 4. ANNOTATION WORKFLOW & BLINDING TESTS
# =========================================================================

def test_07_annotation_assignment_double_blind_structure():
    """Verify annotation assignment manifest assigns two blinded raters per recording."""
    assign_path = os.path.join(STAGE_DIR, "annotation_assignment_manifest.csv")
    assert os.path.exists(assign_path), "Missing annotation_assignment_manifest.csv"
    df_assign = pd.read_csv(assign_path)

    prov_path = os.path.join(STAGE_DIR, "acquisition_provenance.csv")
    df_prov = pd.read_csv(prov_path)

    # Exactly 2 tasks per recording
    assert len(df_assign) == len(df_prov) * 2, f"Expected {len(df_prov) * 2} tasks, got {len(df_assign)}"

    # Ensure raters are RATER_A and RATER_B
    raters = set(df_assign["assigned_rater_id"].unique())
    assert raters == {"RATER_A", "RATER_B"}

    # Ensure blinding status is locked
    for b in df_assign["blinding_status"]:
        assert b == "DOUBLE_BLIND_LOCKED"

def test_08_no_model_prediction_exposure_in_review_queues():
    """Verify that annotation assignment manifests and session logs do not contain model predictions."""
    assign_path = os.path.join(STAGE_DIR, "annotation_assignment_manifest.csv")
    df_assign = pd.read_csv(assign_path)

    forbidden_cols = ["scream_probability", "predicted_label", "model_confidence", "veto_state"]
    for col in forbidden_cols:
        assert col not in df_assign.columns, f"Model prediction exposed in review assignment: {col}"

# =========================================================================
# 5. PROSPECTIVE EVALUATION GOVERNANCE TESTS
# =========================================================================

def test_09_prospective_cohort_manifest_empty_pending_human_annotation():
    """Verify prospective evaluation manifest remains empty (0 recordings) pending human review."""
    cohort_path = os.path.join(STAGE_DIR, "prospective_cohort_manifest.json")
    assert os.path.exists(cohort_path), "Missing prospective_cohort_manifest.json"
    with open(cohort_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["total_recordings"] == 0, "Prospective cohort prematurely populated before human annotation"
    assert len(data["recordings"]) == 0
    assert "PENDING" in data["cohort_status"]

def test_10_evaluation_access_log_continuity():
    """Verify evaluation_access_log.csv logs sequential access events including Stage 76."""
    log_path = os.path.join(STAGE_DIR, "evaluation_access_log.csv")
    assert os.path.exists(log_path), "Missing evaluation_access_log.csv"
    df_log = pd.read_csv(log_path)
    assert len(df_log) >= 7, f"Expected at least 7 access events, got {len(df_log)}"
    assert df_log.iloc[-1]["access_id"] == "ACC-007"
    assert df_log.iloc[-1]["target_cohort"] == "stage_8_9_76_prospective_cohort"

# =========================================================================
# 6. MANDATORY SAFETY HEADERS & DELIVERABLES TESTS
# =========================================================================

def test_11_mandatory_safety_headers():
    """Verify line 1 of every markdown and python file in Stage 76 contains mandatory safety header."""
    MANDATORY_HEADER = "# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE."

    files_checked = 0
    for root, dirs, files in os.walk(STAGE_DIR):
        for fname in files:
            if fname.endswith(".md") or fname.endswith(".py"):
                fpath = os.path.join(root, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    first_line = f.readline().strip()
                assert first_line == MANDATORY_HEADER, f"File {fpath} does not start with mandatory safety header! Got: '{first_line}'"
                files_checked += 1

    assert files_checked >= 20, f"Expected at least 20 files checked, got {files_checked}"

def test_12_required_deliverables_present():
    """Verify core Stage 76 deliverables exist in backend/research/stage_8_9_76/."""
    expected_deliverables = [
        "taxonomy_reconciliation.md",
        "canonical_taxonomy.json",
        "schema_validation_report.md",
        "candidate_audit.csv",
        "candidate_status_summary.md",
        "acquisition_decision_log.csv",
        "acquisition_provenance.csv",
        "license_verification_report.md",
        "uploader_independence_audit.md",
        "acquired_source_group_registry.csv",
        "new_audio_duplicate_audit.md",
        "source_lineage_audit.csv",
        "prospective_eligibility_audit.md",
        "acquisition_progress.csv",
        "category_source_diversity.md",
        "acquisition_shortfall_report.md",
        "storage_capacity_report.md",
        "download_integrity_report.md",
        "annotation_ui_audit.md",
        "annotation_assignment_manifest.csv",
        "annotation_session_log.csv",
        "annotation_completion_report.md",
        "real_inter_rater_reliability.md",
        "annotator_disagreement_matrix.csv",
        "adjudication_results.csv",
        "annotation_ambiguity_report.md",
        "prospective_candidate_eligibility.csv",
        "prospective_cohort_manifest.json",
        "prospective_cohort_seal_report.md",
        "evaluation_access_log.csv",
        "STAGE_PROGRESS.md"
    ]
    for d in expected_deliverables:
        p = os.path.join(STAGE_DIR, d)
        assert os.path.exists(p), f"Missing expected deliverable: {d}"

