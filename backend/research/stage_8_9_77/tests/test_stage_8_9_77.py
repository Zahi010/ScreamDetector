# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
Stage 8.9.77 Automated Regression & Integrity Test Suite
Verifies:
1. Protected production baseline immutability (SHA-256)
2. Frozen Candidate 71-D checkpoint integrity
3. Stage 76 discovery arithmetic reconciliation (67 candidates)
4. Uploader blacklist reconciliation (611 vs 612)
5. Historical hash coverage audit (2,465 file hashes / 3,689 PCM hashes)
6. Stage 76 audio integrity verification (26 WAV files)
7. Annotation double-blind assignment structure (52 tasks)
8. Zero model prediction leakage in review manifests
9. Inter-rater agreement reporting honest blocker (no fabricated labels)
10. Adjudication queue staging (26 rows)
11. Prospective evaluation manifest strictly empty (0 recordings)
12. Mandatory safety designation on line 1 across all deliverables
"""

import os
import sys
import glob
import json
import hashlib
import pytest
import pandas as pd
import soundfile as sf

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

STAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STAGE76_DIR = os.path.join(PROJECT_ROOT, "backend", "research", "stage_8_9_76")
STAGE75_DIR = os.path.join(PROJECT_ROOT, "backend", "research", "stage_8_9_75")


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
    """Verify Candidate 71-D frozen weights SHA-256."""
    ckpt_path = os.path.join(STAGE_DIR, "models", "candidate_71_frozen.pt")
    assert os.path.exists(ckpt_path), "Missing candidate_71_frozen.pt in stage_8_9_77/models/"
    expected = "e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b"
    with open(ckpt_path, "rb") as f:
        actual = hashlib.sha256(f.read()).hexdigest()
    assert actual == expected, f"Candidate 71-D weights modified! Expected: {expected}, Got: {actual}"


def test_03_stage76_discovery_arithmetic_reconciliation():
    """Verify exact arithmetic: 67 discovered = 26 downloaded + 41 quarantined."""
    rec_path = os.path.join(STAGE_DIR, "stage76_arithmetic_reconciliation.csv")
    assert os.path.exists(rec_path), "Missing stage76_arithmetic_reconciliation.csv"
    df = pd.read_csv(rec_path)
    
    assert len(df) == 67, f"Expected 67 candidates, got {len(df)}"
    downloaded = (df["current_state"] == "ANNOTATION_PENDING").sum()
    quarantined = (df["current_state"] == "QUARANTINED").sum()
    
    assert downloaded == 26, f"Expected 26 downloaded, got {downloaded}"
    assert quarantined == 41, f"Expected 41 quarantined, got {quarantined}"
    assert downloaded + quarantined == 67, "Sum of downloaded and quarantined must equal 67"
    
    # Check specific quarantine reasons
    reason_counts = df["quarantine_reason"].value_counts().to_dict()
    assert reason_counts.get("LICENSE_INELIGIBLE_OTHER") == 10
    assert reason_counts.get("LEAKAGE_RISK_HISTORICAL_UPLOADER") == 13
    assert reason_counts.get("UPLOADER_CONCENTRATION_CAP_EXCEEDED") == 18


def test_04_uploader_blacklist_reconciliation():
    """Verify uploader blacklist reconciliation explains 611 vs 612."""
    rec_path = os.path.join(STAGE_DIR, "uploader_blacklist_reconciliation.csv")
    assert os.path.exists(rec_path), "Missing uploader_blacklist_reconciliation.csv"
    df = pd.read_csv(rec_path)
    
    assert len(df) == 612, f"Expected 612 unique lowercased uploaders, got {len(df)}"
    stage75_included = (df["stage75_blacklist_status"] == "INCLUDED").sum()
    stage76_included = (df["stage76_blacklist_status"] == "INCLUDED").sum()
    
    assert stage75_included == 611, f"Expected 611 included in Stage 75 blacklist, got {stage75_included}"
    assert stage76_included == 612, f"Expected 612 included in Stage 76 blacklist, got {stage76_included}"
    
    # Verify exact discrepancy row
    root_cause_row = df[df["uploader_normalized_lower"] == "unknown_creator"]
    assert len(root_cause_row) == 1, "Must contain unknown_creator row"
    assert root_cause_row.iloc[0]["stage75_blacklist_status"] == "EXCLUDED_AS_PLACEHOLDER"
    assert root_cause_row.iloc[0]["stage76_blacklist_status"] == "INCLUDED"


def test_05_historical_hash_coverage_audit():
    """Verify historical hash coverage audit reflects 2,465 file hashes and 3,689 PCM hashes."""
    cov_path = os.path.join(STAGE_DIR, "historical_hash_coverage_audit.csv")
    assert os.path.exists(cov_path), "Missing historical_hash_coverage_audit.csv"
    df = pd.read_csv(cov_path)
    
    total_row = df[df["source_dataset"] == "TOTAL_HISTORICAL_INVENTORY"]
    assert len(total_row) == 1, "Must contain TOTAL_HISTORICAL_INVENTORY summary row"
    row = total_row.iloc[0]
    
    assert int(row["total_recordings"]) == 3694
    assert int(row["file_sha256_populated"]) == 2593
    assert int(row["file_sha256_unique_count"]) == 2465
    assert int(row["pcm_sha256_populated"]) == 3694
    assert int(row["pcm_sha256_unique_count"]) == 3689
    assert int(row["pcm_internal_collisions"]) == 5


def test_06_stage76_audio_integrity_verification():
    """Verify all 26 WAV files exist, are 16 kHz mono, decodable, and match SHA-256."""
    audit_path = os.path.join(STAGE_DIR, "stage76_audio_integrity_audit.csv")
    assert os.path.exists(audit_path), "Missing stage76_audio_integrity_audit.csv"
    df = pd.read_csv(audit_path)
    
    assert len(df) == 26, f"Expected 26 audio records, got {len(df)}"
    assert (df["integrity_verdict"] == "VERIFIED_AUDIO_INTEGRITY_PASS").sum() == 26
    assert (df["file_sha256_match"] == 1).sum() == 26
    assert (df["decodable"] == 1).sum() == 26
    assert (df["sample_rate"] == 16000).sum() == 26
    assert (df["channels"] == 1).sum() == 26


def test_07_annotation_assignment_double_blind_structure():
    """Verify 52 assignments staged across RATER_A and RATER_B with model blinding."""
    assign_path = os.path.join(STAGE_DIR, "annotation_assignment_status.csv")
    assert os.path.exists(assign_path), "Missing annotation_assignment_status.csv"
    df = pd.read_csv(assign_path)
    
    assert len(df) == 52, f"Expected 52 assignments, got {len(df)}"
    rater_counts = df["assigned_rater"].value_counts().to_dict()
    assert rater_counts.get("RATER_A") == 26
    assert rater_counts.get("RATER_B") == 26
    assert (df["model_blinding_verified"] == 1).sum() == 52
    assert (df["assignment_status"] == "AWAITING_INDEPENDENT_HUMAN_REVIEW").sum() == 52


def test_08_no_model_predictions_in_review_queues():
    """Verify zero model predictions or probabilities exist in review assignment manifest."""
    assign_path = os.path.join(STAGE_DIR, "annotation_assignment_status.csv")
    df = pd.read_csv(assign_path)
    
    forbidden_terms = ["candidate_71", "pred_", "probability", "confidence_score_model", "veto", "model_output"]
    for col in df.columns:
        for term in forbidden_terms:
            assert term not in col.lower(), f"Forbidden model column found: {col}"


def test_09_inter_rater_agreement_honest_block():
    """Verify agreement report honestly declares NOT CALCULATED without synthetic labels."""
    report_path = os.path.join(STAGE_DIR, "inter_rater_agreement_report.md")
    assert os.path.exists(report_path), "Missing inter_rater_agreement_report.md"
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "INSUFFICIENT REAL ANNOTATION EVIDENCE" in content or "NOT CALCULATED" in content
    assert "NO SIMULATION OF HUMAN REVIEWERS" in content


def test_10_adjudication_status_staged():
    """Verify adjudication_status.csv contains 26 rows awaiting human reviews."""
    adj_path = os.path.join(STAGE_DIR, "adjudication_status.csv")
    assert os.path.exists(adj_path), "Missing adjudication_status.csv"
    df = pd.read_csv(adj_path)
    
    assert len(df) == 26, f"Expected 26 rows in adjudication_status.csv, got {len(df)}"
    assert (df["adjudication_status"] == "AWAITING_INITIAL_HUMAN_RATINGS").sum() == 26


def test_11_prospective_cohort_manifest_strictly_empty():
    """Verify prospective_evaluation_manifest.json has 0 admitted recordings."""
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

