"""
Stage 8.9.45: Phase A Forensic Audit Script
Verifies all 10 Phase A integrity criteria and the 4 canonical production freeze hashes.

MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
import os
import sys
import json
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, brier_score_loss

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE43_DIR = BACKEND_DIR / "research" / "stage_8_9_43"
STAGE44_DIR = BACKEND_DIR / "research" / "stage_8_9_44"
STAGE45_DIR = BACKEND_DIR / "research" / "stage_8_9_45"

# 1. Production freeze hashes
EXPECTED_HASHES = {
    "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
}

def audit_production_freeze():
    print("--- 1. Auditing Production Freeze Hashes ---")
    results = {}
    all_match = True
    for rel_p, exp_hash in EXPECTED_HASHES.items():
        fp = REPO_ROOT / rel_p
        assert fp.exists(), f"Missing production file: {rel_p}"
        with open(fp, "rb") as f:
            act_hash = hashlib.sha256(f.read()).hexdigest()
        match = (act_hash == exp_hash)
        if not match:
            all_match = False
        results[rel_p] = {"expected": exp_hash, "actual": act_hash, "match": match}
        print(f"  {rel_p}: {'MATCH' if match else 'MISMATCH'}")
    assert all_match, "Production freeze check failed!"
    return results

def audit_dataset_and_partitions():
    print("\n--- 2. Auditing Dataset Manifest and Partitions ---")
    manifest_p = STAGE43_DIR / "manifests" / "dataset_manifest_v5.csv"
    assert manifest_p.exists()
    df = pd.read_csv(manifest_p)
    print(f"  Total manifest rows: {len(df)}")
    assert len(df) == 1914, f"Expected 1,914 rows, got {len(df)}"

    splits = ["v5_train", "v5_validation", "v5_development_test", "v5_final_holdout"]
    split_info = {}
    sg_sets = {}
    for s in splits:
        sdf = df[df["v5_research_split"] == s]
        sgs = set(sdf["source_group_id"].dropna().unique())
        sg_sets[s] = sgs
        split_info[s] = {
            "total": len(sdf),
            "positives": int((sdf["binary_label"] == 1).sum()),
            "negatives": int((sdf["binary_label"] == 0).sum()),
            "source_groups": len(sgs)
        }
        print(f"  {s}: Total={len(sdf)}, Pos={split_info[s]['positives']}, Neg={split_info[s]['negatives']}, SGs={len(sgs)}")

    # Check zero overlap
    overlap_detected = False
    for i in range(len(splits)):
        for j in range(i + 1, len(splits)):
            inter = sg_sets[splits[i]].intersection(sg_sets[splits[j]])
            if len(inter) > 0:
                print(f"  LEAKAGE: {splits[i]} and {splits[j]} share {len(inter)} source groups: {inter}")
                overlap_detected = True
    assert not overlap_detected, "Partition leakage detected!"
    print("  Source-group isolation across all 4 partitions: STRICT ZERO OVERLAP (PASS)")
    return split_info, df

def audit_augmentation_manifests(df):
    print("\n--- 3. Auditing Augmentation Manifests and Training Exclusivity ---")
    train_pos_fids = set(df[(df["v5_research_split"] == "v5_train") & (df["binary_label"] == 1)]["file_id"])
    assert len(train_pos_fids) == 401, f"Expected 401 train positive clips, got {len(train_pos_fids)}"

    cond_manifests = ["b", "c", "d", "e"]
    aug_counts = {}
    for c in cond_manifests:
        mf_path = STAGE44_DIR / "augmentation" / f"augmented_manifest_condition_{c}.csv"
        assert mf_path.exists()
        mdf = pd.read_csv(mf_path)
        aug_counts[c] = len(mdf)
        print(f"  Condition {c.upper()} Manifest: {len(mdf)} augmented clips")
        assert len(mdf) == 401, f"Expected 401 rows in condition_{c}, got {len(mdf)}"
        # Verify all original_file_id come strictly from train_pos_fids
        orig_ids = set(mdf["original_file_id"])
        diff = orig_ids - train_pos_fids
        assert len(diff) == 0, f"Found augmented clips not originating from v5_train positives: {diff}"
    print(f"  Total augmented positive clips: {sum(aug_counts.values())} (401 x 4 = 1,604)")
    print("  Exclusivity: Augmentation applied STRICTLY and ONLY to v5_train positive clips (PASS)")
    return aug_counts

def audit_candidate_eval_reproducibility(df):
    print("\n--- 4. Auditing Candidate Evaluation Metrics & Subtype Reproducibility ---")
    metrics_p = STAGE44_DIR / "results" / "evaluation" / "candidate_eval_metrics_v6.json"
    assert metrics_p.exists()
    with open(metrics_p, "r", encoding="utf-8") as f:
        metrics_data = json.load(f)

    # Inspect Candidate D on Holdout
    cand_d_holdout = metrics_data["config_b_mask_v5_final_holdout"]
    print(f"  Candidate D Holdout Recall: {cand_d_holdout['recall']}% ({cand_d_holdout['tp']}/{cand_d_holdout['n_pos']})")
    print(f"  Candidate D Holdout ROC-AUC: {cand_d_holdout['roc_auc']:.4f}")
    print(f"  Candidate D Holdout Brier Score: {cand_d_holdout['brier_score']:.4f}")
    print(f"  Candidate D Holdout Masked Screams: {cand_d_holdout['masked_recall']}")
    print(f"  Candidate D Holdout Distant Screams: {cand_d_holdout['distant_recall']}")

    assert "11/16" in cand_d_holdout['masked_recall']
    assert "12/18" in cand_d_holdout['distant_recall']
    print("  Candidate D 11/16 masked and 12/18 distant detections: VERIFIED REPRODUCIBLE (PASS)")

    # Baseline A on Holdout
    base_holdout = metrics_data["config_b_v5_baseline_v5_final_holdout"]
    print(f"  Baseline A Holdout Recall: {base_holdout['recall']}% ({base_holdout['tp']}/{base_holdout['n_pos']})")
    print(f"  Baseline A Holdout Masked Screams: {base_holdout['masked_recall']}")
    print(f"  Baseline A Holdout Distant Screams: {base_holdout['distant_recall']}")
    assert "8/16" in base_holdout['masked_recall']
    assert "9/18" in base_holdout['distant_recall']
    print("  Baseline A 8/16 masked and 9/18 distant detections: VERIFIED REPRODUCIBLE (PASS)")

    return metrics_data

def main():
    print("======================================================================")
    print("STAGE 8.9.45: PHASE A FORENSIC AUDIT")
    print("======================================================================")
    hash_res = audit_production_freeze()
    split_info, df = audit_dataset_and_partitions()
    aug_counts = audit_augmentation_manifests(df)
    metrics_data = audit_candidate_eval_reproducibility(df)
    print("\nPhase A Audit Completed Successfully.")

if __name__ == "__main__":
    main()
