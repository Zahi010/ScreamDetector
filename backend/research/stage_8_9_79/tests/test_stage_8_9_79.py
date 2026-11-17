# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
Stage 8.9.79 Automated Regression & Integrity Test Suite
Verifies:
1. Protected production baseline immutability (SHA-256)
2. Frozen Candidate 71-D checkpoint integrity
3. Single-device session authentication & token generation
4. Explicit signout, token revocation & client state wipe
5. Cross-reviewer access blocked on shared device
6. Full model & metadata blinding in reviewer queues
7. Exactly 3 pilot recordings and 6 pilot tasks staged
8. Canonical 24-leaf taxonomy payload validation
9. Zero human submissions accurately accounted (no fabricated labels)
10. Inter-rater agreement honestly declared NOT CALCULATED
11. Adjudication queue staged & prospective manifest strictly empty
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

from backend.research.stage_8_9_79.scripts.single_device_session_manager import (
    SingleDeviceSessionManager,
    SingleDeviceAuthError,
    BlindingViolationError,
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
    """Verify Candidate 71-D frozen weights SHA-256 in stage_8_9_79/models/."""
    ckpt_path = os.path.join(STAGE_DIR, "models", "candidate_71_frozen.pt")
    assert os.path.exists(ckpt_path), "Missing candidate_71_frozen.pt in stage_8_9_79/models/"
    expected = "e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b"
    with open(ckpt_path, "rb") as f:
        actual = hashlib.sha256(f.read()).hexdigest()
    assert actual == expected, f"Candidate 71-D weights modified! Expected: {expected}, Got: {actual}"


def test_03_single_device_session_authentication():
    """Verify session manager authenticates RATER_A and RATER_B with isolated sessions."""
    mgr = SingleDeviceSessionManager()
    
    # Authenticate RATER_A
    sess_a = mgr.authenticate("token_sec_rater_a_9a77b81")
    assert sess_a["rater_id"] == "RATER_A"
    assert "no-store" in sess_a["cache_control"]
    
    # Authenticate RATER_B
    sess_b = mgr.authenticate("token_sec_rater_b_4c88e92")
    assert sess_b["rater_id"] == "RATER_B"
    assert sess_a["session_id"] != sess_b["session_id"]
    
    # Invalid token rejected
    with pytest.raises(SingleDeviceAuthError):
        mgr.authenticate("invalid_token_xyz")


def test_04_session_signout_and_state_wipe():
    """Verify signout revokes token and wipes state; subsequent access fails."""
    mgr = SingleDeviceSessionManager()
    token = "token_sec_rater_a_9a77b81"
    
    # Login then sign out
    mgr.authenticate(token)
    res = mgr.signout(token)
    assert res["status"] == "SIGNED_OUT"
    assert res["client_state_cleared"] is True
    
    # Subsequent calls using revoked token fail
    with pytest.raises(SingleDeviceAuthError):
        mgr.get_full_queue(token, "RATER_A")


def test_05_cross_reviewer_access_blocked():
    """Verify RATER_A token cannot access RATER_B queue or annotations on shared device."""
    mgr = SingleDeviceSessionManager()
    token_a = "token_sec_rater_a_9a77b81"
    mgr.authenticate(token_a)
    
    # RATER_A cannot request RATER_B queue
    with pytest.raises(SingleDeviceAuthError):
        mgr.get_full_queue(token_a, "RATER_B")
        
    with pytest.raises(SingleDeviceAuthError):
        mgr.get_pilot_queue(token_a, "RATER_B")


def test_06_model_blinding_in_queues():
    """Verify queues contain zero model predictions, probabilities, or detector scores."""
    mgr = SingleDeviceSessionManager()
    token_a = "token_sec_rater_a_9a77b81"
    mgr.authenticate(token_a)
    
    queue = mgr.get_full_queue(token_a, "RATER_A")
    assert len(queue) == 26
    
    forbidden = ["pred", "probability", "model_output", "candidate_71", "yamnet", "score"]
    for item in queue:
        for k in item.keys():
            for f in forbidden:
                assert f not in k.lower(), f"Model leakage detected in key: {k}"


def test_07_pilot_manifest_and_tasks():
    """Verify exactly 3 pilot recordings from distinct source groups and 6 tasks staged."""
    manifest_path = os.path.join(STAGE_DIR, "pilot_recording_manifest.csv")
    assert os.path.exists(manifest_path), "Missing pilot_recording_manifest.csv"
    df_manifest = pd.read_csv(manifest_path)
    
    assert len(df_manifest) == 3, f"Expected exactly 3 pilot recordings, got {len(df_manifest)}"
    assert df_manifest["source_group_id"].nunique() == 3, "Pilot recordings must come from 3 distinct source groups"
    
    status_path = os.path.join(STAGE_DIR, "pilot_annotation_status.csv")
    assert os.path.exists(status_path), "Missing pilot_annotation_status.csv"
    df_status = pd.read_csv(status_path)
    
    assert len(df_status) == 6, f"Expected 6 pilot tasks (3 per reviewer), got {len(df_status)}"
    assert (df_status["assigned_rater"].value_counts().to_dict()) == {"RATER_A": 3, "RATER_B": 3}
    assert (df_status["submitted"] == 0).all()


def test_08_annotation_payload_taxonomy_validation():
    """Verify validator enforces canonical 24-leaf taxonomy and timestamp logic."""
    mgr = SingleDeviceSessionManager()
    
    # Valid positive scream
    ok, msg = mgr.validate_annotation_payload({
        "primary_label": "scream",
        "subcategory": "VOCAL_SCREAM_CHILD",
        "confidence_rating": 4,
        "event_start_timestamp": 0.5,
        "event_end_timestamp": 1.2
    })
    assert ok, f"Valid payload rejected: {msg}"
    
    # Invalid timestamp logic (end <= start)
    ok, msg = mgr.validate_annotation_payload({
        "primary_label": "scream",
        "subcategory": "VOCAL_SCREAM_CHILD",
        "confidence_rating": 4,
        "event_start_timestamp": 2.5,
        "event_end_timestamp": 1.2
    })
    assert not ok


def test_09_actual_human_submissions_zero_accounted():
    """Verify submission status accurately reports 0 human submissions without fabrication."""
    sub_path = os.path.join(STAGE_DIR, "annotation_submission_status.csv")
    assert os.path.exists(sub_path), "Missing annotation_submission_status.csv"
    df = pd.read_csv(sub_path)
    
    assert len(df) == 52, f"Expected 52 assignments, got {len(df)}"
    assert (df["submitted"] == 0).all()
    assert (df["submission_status"] == "AWAITING_HUMAN_REVIEWER").all()
    
    paired_path = os.path.join(STAGE_DIR, "paired_annotation_status.csv")
    assert os.path.exists(paired_path), "Missing paired_annotation_status.csv"
    df_paired = pd.read_csv(paired_path)
    assert len(df_paired) == 26
    assert (df_paired["pair_completion_status"] == "INCOMPLETE_ZERO_SUBMISSIONS").all()


def test_10_inter_rater_agreement_honest_block():
    """Verify agreement report declares NOT CALCULATED / INSUFFICIENT EVIDENCE."""
    report_path = os.path.join(STAGE_DIR, "inter_rater_agreement_report.md")
    assert os.path.exists(report_path), "Missing inter_rater_agreement_report.md"
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "INSUFFICIENT EVIDENCE" in content
    assert "NOT CALCULATED" in content
    assert "NO AI-GENERATED OR SYNTHETIC LABELS" in content


def test_11_adjudication_and_prospective_empty():
    """Verify adjudication queue has 26 staged records and prospective manifest is empty."""
    adj_path = os.path.join(STAGE_DIR, "adjudication_status.csv")
    assert os.path.exists(adj_path), "Missing adjudication_status.csv"
    df_adj = pd.read_csv(adj_path)
    assert len(df_adj) == 26
    assert (df_adj["adjudication_status"] == "AWAITING_INITIAL_HUMAN_RATINGS").all()
    
    manifest_path = os.path.join(STAGE_DIR, "prospective_evaluation_manifest.json")
    assert os.path.exists(manifest_path), "Missing prospective_evaluation_manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert data["total_recordings"] == 0
    assert len(data["recordings"]) == 0
    assert data["cohort_status"] == "SEALED_EMPTY_PENDING_HUMAN_ANNOTATION"


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

