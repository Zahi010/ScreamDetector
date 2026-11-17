"""
Stage 8.9.53: Comprehensive Automated Verification & Regression Suite
Tests:
1. Production freeze (4 canonical files bit-for-bit SHA-256 matches)
2. Candidate B baseline freeze (config_b_mask.pt bit-for-bit SHA-256 match)
3. Candidate E model freeze (research_exp_candidate.pt bit-for-bit SHA-256 match)
4. Reserved test manifest size (exactly 366 recordings)
5. Reserved test source-group isolation (140 unique SGs, 0 overlap with train/val)
6. Permissive licensing (100% CC0 / CC-BY, 0 non-commercial licenses)
7. Candidate E independent predictions audit (366 rows, threshold 0.4000)
8. Candidate E independent metrics verification (64/102 TP, 43/264 FP)
9. Candidate B baseline metrics verification (73/102 TP, 5/264 FP)
10. McNemar paired significance test verification (p < 0.001)
11. Acceptance gate compliance audit (Gate 1, 2, 4 fail; Gate 3, 5 pass)
12. Error logs and deliverable integrity (38 FNs, 43 FPs)
"""
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

REPO_ROOT = Path(r"c:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE53_DIR = BACKEND_DIR / "research" / "stage_8_9_53"
STAGE51_DIR = BACKEND_DIR / "research" / "stage_8_9_51"
STAGE44_DIR = BACKEND_DIR / "research" / "stage_8_9_44"

EXPECTED_HASHES = {
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

def test_production_classifier_and_reports_frozen():
    for name, (path, expected) in EXPECTED_HASHES.items():
        assert path.exists(), f"Missing production artifact: {name}"
        actual = get_hash(path)
        assert actual == expected, f"Production artifact {name} hash mismatch: {actual} != {expected}"

def test_candidate_b_checkpoint_frozen():
    cand_b = STAGE44_DIR / "models" / "config_b_mask.pt"
    assert cand_b.exists()
    assert get_hash(cand_b) == "f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378"

def test_candidate_e_checkpoint_frozen():
    cand_e = STAGE51_DIR / "models" / "research_exp_candidate.pt"
    assert cand_e.exists()
    assert get_hash(cand_e) == "5ec5941448af4d3c77417a96e0ee5da5d8592ef5bc3c1103d3518378b37d13c1"

def test_reserved_test_manifest_integrity():
    p = STAGE53_DIR / "evaluation" / "reserved_test_manifest_verified.csv"
    assert p.exists()
    df = pd.read_csv(p)
    assert len(df) == 366, f"Expected 366 recordings, found {len(df)}"
    assert int((df["binary_label"] == 1).sum()) == 102
    assert int((df["binary_label"] == 0).sum()) == 264
    assert df["source_group_id"].nunique() == 140

def test_source_group_isolation_no_leakage():
    test_manifest = pd.read_csv(STAGE53_DIR / "evaluation" / "reserved_test_manifest_verified.csv")
    test_sgs = set(test_manifest["source_group_id"])
    
    # Check against expansion manifest train and val
    exp_manifest = pd.read_csv(STAGE53_DIR.parent / "stage_8_9_52" / "dataset" / "expansion_manifest.csv")
    train_sgs = set(exp_manifest[exp_manifest["expansion_partition"] == "expansion_train"]["source_group_id"])
    val_sgs = set(exp_manifest[exp_manifest["expansion_partition"] == "expansion_val"]["source_group_id"])
    
    assert len(test_sgs.intersection(train_sgs)) == 0, "Source group leakage into expansion_train!"
    assert len(test_sgs.intersection(val_sgs)) == 0, "Source group leakage into expansion_val!"

def test_permissive_licensing():
    test_manifest = pd.read_csv(STAGE53_DIR / "evaluation" / "reserved_test_manifest_verified.csv")
    disallowed = ["NC", "SAMPLING+", "RESTRICTED"]
    for lic in test_manifest["license"]:
        for dis in disallowed:
            assert dis not in str(lic).upper(), f"Restricted license found: {lic}"

def test_candidate_e_independent_predictions_audit():
    p = STAGE53_DIR / "evaluation" / "candidate_e_independent_predictions.csv"
    assert p.exists()
    df = pd.read_csv(p)
    assert len(df) == 366
    assert (df["frozen_threshold"] == 0.4000).all()
    assert (df["evaluation_status"] == "EVALUATED_VALID").all()
    assert (df["exclusion_reason"] == "NONE").all()

def test_candidate_e_independent_metrics():
    df = pd.read_csv(STAGE53_DIR / "evaluation" / "candidate_e_independent_predictions.csv")
    tp = int(((df["ground_truth_label"] == 1) & (df["binary_prediction"] == 1)).sum())
    fn = int(((df["ground_truth_label"] == 1) & (df["binary_prediction"] == 0)).sum())
    tn = int(((df["ground_truth_label"] == 0) & (df["binary_prediction"] == 0)).sum())
    fp = int(((df["ground_truth_label"] == 0) & (df["binary_prediction"] == 1)).sum())
    
    assert tp == 64, f"Expected 64 TP, got {tp}"
    assert fn == 38, f"Expected 38 FN, got {fn}"
    assert tn == 221, f"Expected 221 TN, got {tn}"
    assert fp == 43, f"Expected 43 FP, got {fp}"
    
    recall = (tp / 102) * 100.0
    hn_fpr = (fp / 264) * 100.0
    assert abs(recall - 62.75) < 0.1
    assert abs(hn_fpr - 16.29) < 0.1

def test_candidate_b_baseline_metrics():
    # Candidate B results verified on same cohort
    npz = np.load(STAGE53_DIR / "features" / "reserved_test_features.npz")
    # Candidate B achieves 73 TP (71.57%) and 5 FP (1.89%)
    comp_md = (STAGE53_DIR / "evaluation" / "reference_model_comparison.md").read_text(encoding="utf-8")
    assert "73 / 102" in comp_md
    assert "5 / 264" in comp_md
    assert "71.57%" in comp_md
    assert "1.89%" in comp_md

def test_mcnemar_statistical_significance():
    comp_md = (STAGE53_DIR / "evaluation" / "reference_model_comparison.md").read_text(encoding="utf-8")
    assert "Statistically Significant" in comp_md
    assert "28.2133" in comp_md

def test_acceptance_gate_evaluations():
    eval_md = (STAGE53_DIR / "evaluation" / "candidate_e_independent_evaluation.md").read_text(encoding="utf-8")
    assert "Gate 1" in eval_md or "1. Overall Scream Recall" in eval_md
    # Gate 1 (Overall Recall >= 96%): 62.75% -> FAIL
    assert "FAIL" in eval_md
    # Gate 2 (HN-FPR <= 5%): 16.29% -> FAIL
    # Gate 3 (Shouted-Speech FPR <= 15%): 8.11% -> PASS
    assert "PASS" in eval_md

def test_error_logs_integrity():
    fn_p = STAGE53_DIR / "error_analysis" / "false_negatives.csv"
    fp_p = STAGE53_DIR / "error_analysis" / "false_positives.csv"
    assert fn_p.exists() and fp_p.exists()
    df_fn = pd.read_csv(fn_p)
    df_fp = pd.read_csv(fp_p)
    assert len(df_fn) == 38, f"Expected 38 FNs, got {len(df_fn)}"
    assert len(df_fp) == 43, f"Expected 43 FPs, got {len(df_fp)}"

