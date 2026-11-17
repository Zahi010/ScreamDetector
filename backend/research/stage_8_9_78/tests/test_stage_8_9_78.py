# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
Stage 8.9.78 Automated Regression & Integrity Test Suite
Verifies:
1. Protected production baseline immutability (SHA-256)
2. Frozen Candidate 71-D checkpoint integrity
3. Reviewer onboarding & separation enforcement
4. Reviewer isolation & cross-access prevention
5. Full model and prior blinding in reviewer queues
6. Annotation payload taxonomy validation
7. Zero human submissions correctly accounted (no fabricated labels)
8. Inter-rater agreement reporting honest blocker (NOT CALCULATED)
9. Adjudication queue staging (26 rows awaiting review)
10. Prospective evaluation manifest strictly empty (0 recordings)
11. Prospective eligibility rules require human consensus
12. Mandatory safety designation on line 1 across all deliverables
"""

import os
import sys
import glob
import json
import hashlib
import pytest
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

STAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STAGE77_DIR = os.path.join(PROJECT_ROOT, "backend", "research", "stage_8_9_77")
STAGE76_DIR = os.path.join(PROJECT_ROOT, "backend", "research", "stage_8_9_76")

from backend.research.stage_8_9_78.scripts.annotation_session_manager import (
    AnnotationSessionManager,
    ReviewerAuthorizationError,
    ModelBlindingViolationError,
    PRIMARY_CATEGORIES,
    SCREAM_SUBCATEGORIES
)


def test_01_protected_production_hashes():
    """Verify bit-for-bit match for 4 production baseline files + Stage 60 manifest."""
    expected_hashes = {
        os.path.join(PROJECT_ROOT, "backend", "models", "scream_classifier.joblib"): "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
        os.path.join(PROJECT_ROOT, "backend", "models", "model_metadata.json"): "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
        os.path.join(PROJECT_ROOT, "backend", "reports", "test_predictions.csv"): "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
        os.path.join(PROJECT_ROOT, "backend", "reports", "stage5_test_evaluation.md"): "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
        os.path.join(PROJECT_ROOT, "backend", "research", "stage_8_9_60", "future_evaluation_manifest.json"): "9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd"
    }
    for fpath, expected in expected_hashes.items():
        assert os.path.exists(fpath), f"Missing protected file: {fpath}"
        with open(fpath, "rb") as f:
            actual = hashlib.sha256(f.read()).hexdigest()
        assert actual == expected, f"Hash mismatch on {fpath}! Expected: {expected}, Got: {actual}"


def test_02_candidate_71_frozen_checkpoint_integrity():
    """Verify Candidate 71-D frozen weights SHA-256 in stage_8_9_78/models/."""
    ckpt_path = os.path.join(STAGE_DIR, "models", "candidate_71_frozen.pt")
    assert os.path.exists(ckpt_path), "Missing candidate_71_frozen.pt in stage_8_9_78/models/"
    expected = "e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b"
    with open(ckpt_path, "rb") as f:
        actual = hashlib.sha256(f.read()).hexdigest()
    assert actual == expected, f"Candidate 71-D weights modified! Expected: {expected}, Got: {actual}"


def test_03_reviewer_onboarding_and_isolation():
    """Verify onboarding table tracks RATER_A and RATER_B with strict separation."""
    onboard_path = os.path.join(STAGE_DIR, "reviewer_onboarding_status.csv")
    assert os.path.exists(onboard_path), "Missing reviewer_onboarding_status.csv"
    df = pd.read_csv(onboard_path)
    
    assert len(df) == 2, f"Expected 2 reviewers, got {len(df)}"
    raters = set(df["reviewer_role"].tolist())
    assert raters == {"RATER_A", "RATER_B"}
    assert (df["assigned_task_count"] == 26).all()
    assert (df["reviewer_isolation_verified"] == 1).all()
    assert (df["model_blinding_verified"] == 1).all()


def test_04_cross_reviewer_access_prevention():
    """Verify backend enforces strict authorization blocking cross-reviewer access."""
    mgr = AnnotationSessionManager()
    
    # RATER_A valid token retrieves RATER_A queue
    queue_a = mgr.get_reviewer_queue("RATER_A", "token_sec_rater_a_9a77b81")
    assert len(queue_a) == 26
    
    # RATER_B valid token retrieves RATER_B queue
    queue_b = mgr.get_reviewer_queue("RATER_B", "token_sec_rater_b_4c88e92")
    assert len(queue_b) == 26
    
    # RATER_A token cannot access RATER_B queue
    with pytest.raises(ReviewerAuthorizationError):
        mgr.get_reviewer_queue("RATER_B", "token_sec_rater_a_9a77b81")
        
    # Direct cross-access simulation fails
    with pytest.raises(ReviewerAuthorizationError):
        mgr.attempt_cross_reviewer_access("RATER_A", "token_sec_rater_a_9a77b81", "RATER_B")


def test_05_model_blinding_in_reviewer_queues():
    """Verify reviewer queues contain zero model predictions, probabilities, or detector scores."""
    mgr = AnnotationSessionManager()
    queue_a = mgr.get_reviewer_queue("RATER_A", "token_sec_rater_a_9a77b81")
    
    forbidden_terms = ["candidate_71", "pred_", "probability", "confidence_score_model", "veto", "yamnet", "score"]
    for task in queue_a:
        for k in task.keys():
            for term in forbidden_terms:
                assert term not in k.lower(), f"Leaked model field '{k}' in reviewer queue!"


def test_06_annotation_payload_taxonomy_validation():
    """Verify validator enforces canonical 24-leaf taxonomy and rejects invalid categories."""
    mgr = AnnotationSessionManager()
    
    # Valid positive scream
    valid_payload = {
        "primary_label": "scream",
        "subcategory": "VOCAL_SCREAM_CHILD",
        "confidence_rating": 4
    }
    ok, msg = mgr.validate_annotation_payload(valid_payload)
    assert ok, f"Valid payload rejected: {msg}"
    
    # Valid negative class
    valid_neg = {
        "primary_label": "shouted_speech",
        "confidence_rating": 5
    }
    ok, msg = mgr.validate_annotation_payload(valid_neg)
    assert ok, f"Valid negative rejected: {msg}"
    
    # Invalid primary class
    invalid_pri = {
        "primary_label": "fake_alarm_sound",
        "confidence_rating": 3
    }
    ok, msg = mgr.validate_annotation_payload(invalid_pri)
    assert not ok
    
    # Invalid scream subcategory
    invalid_sub = {
        "primary_label": "scream",
        "subcategory": "NOT_A_VALID_SUBCAT",
        "confidence_rating": 4
    }
    ok, msg = mgr.validate_annotation_payload(invalid_sub)
    assert not ok
    
    # Invalid confidence bounds (e.g. 0 or 6)
    invalid_conf = {
        "primary_label": "infant_cry",
        "confidence_rating": 6
    }
    ok, msg = mgr.validate_annotation_payload(invalid_conf)
    assert not ok


def test_07_zero_human_submissions_accounted():
    """Verify submission status accurately reports 0 human submissions without fabrication."""
    sub_path = os.path.join(STAGE_DIR, "annotation_submission_status.csv")
    assert os.path.exists(sub_path), "Missing annotation_submission_status.csv"
    df = pd.read_csv(sub_path)
    
    assert len(df) == 52, f"Expected 52 assignments, got {len(df)}"
    assert (df["submitted"] == 0).all(), "No submissions should exist when human raters are absent"
    assert (df["submission_status"] == "AWAITING_HUMAN_REVIEWER").all()
    
    paired_path = os.path.join(STAGE_DIR, "paired_annotation_status.csv")
    assert os.path.exists(paired_path), "Missing paired_annotation_status.csv"
    df_paired = pd.read_csv(paired_path)
    assert len(df_paired) == 26
    assert (df_paired["pair_completion_status"] == "INCOMPLETE_ZERO_SUBMISSIONS").all()


def test_08_inter_rater_agreement_honest_block():
    """Verify agreement report declares NOT CALCULATED / INSUFFICIENT EVIDENCE."""
    report_path = os.path.join(STAGE_DIR, "inter_rater_agreement_report.md")
    assert os.path.exists(report_path), "Missing inter_rater_agreement_report.md"
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "INSUFFICIENT EVIDENCE" in content
    assert "NOT CALCULATED" in content
    assert "PROHIBITION AGAINST SYNTHETIC / AI-GENERATED RATINGS" in content


def test_09_adjudication_and_disagreement_staged():
    """Verify adjudication queue has 26 staged records and disagreement table is clean."""
    adj_path = os.path.join(STAGE_DIR, "adjudication_status.csv")
    assert os.path.exists(adj_path), "Missing adjudication_status.csv"
    df_adj = pd.read_csv(adj_path)
    assert len(df_adj) == 26
    assert (df_adj["adjudication_status"] == "AWAITING_INITIAL_HUMAN_RATINGS").all()
    
    dis_path = os.path.join(STAGE_DIR, "disagreement_analysis.csv")
    assert os.path.exists(dis_path), "Missing disagreement_analysis.csv"
    df_dis = pd.read_csv(dis_path)
    assert len(df_dis) == 0, "Disagreement table must be empty when 0 submissions have occurred"


def test_10_prospective_cohort_manifest_strictly_empty():
    """Verify prospective evaluation manifest remains strictly empty (0 recordings)."""
    manifest_path = os.path.join(STAGE_DIR, "prospective_evaluation_manifest.json")
    assert os.path.exists(manifest_path), "Missing prospective_evaluation_manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert data["total_recordings"] == 0
    assert len(data["recordings"]) == 0
    assert data["cohort_status"] == "SEALED_EMPTY_PENDING_HUMAN_ANNOTATION"


def test_11_prospective_eligibility_requires_human_annotations():
    """Verify prospective eligibility audit quarantines all 26 recordings pending human review."""
    audit_path = os.path.join(STAGE_DIR, "prospective_eligibility_audit.csv")
    assert os.path.exists(audit_path), "Missing prospective_eligibility_audit.csv"
    df = pd.read_csv(audit_path)
    
    assert len(df) == 26
    assert (df["prospective_eligible"] == 0).all()
    assert (df["eligibility_verdict"] == "QUARANTINED_PENDING_HUMAN_ANNOTATION").all()
    assert (df["rule_10_reviewer_a_complete"] == 0).all()
    assert (df["rule_11_reviewer_b_complete"] == 0).all()


def test_12_mandatory_safety_headers():
    """Verify exact safety designation on line 1 of all markdown, python, and test files."""
    expected_header = "# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE."
    
    target_files = []
    for ext in ("*.md", "*.py"):
        target_files.extend(glob.glob(os.path.join(STAGE_DIR, ext)))
        target_files.extend(glob.glob(os.path.join(STAGE_DIR, "scripts", ext)))
        target_files.extend(glob.glob(os.path.join(STAGE_DIR, "tests", ext)))
        
    assert len(target_files) > 0, "No files found to verify headers!"
    for fpath in target_files:
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            line1 = f.readline().strip()
        assert line1 == expected_header, f"Header violation in {os.path.relpath(fpath, PROJECT_ROOT)}: '{line1}'"

