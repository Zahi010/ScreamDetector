"""
Stage 8.9.44: Phase A Audit Script
Verifies:
1. Production freeze hashes byte-for-byte.
2. Dataset Manifest v5 schema, row counts, and strict source-group isolation.
3. Acoustic subtype distributions across splits.
4. Identifies the Stage 8.9.43 Config-B-v5 false negatives on final holdout.
"""
import os
import sys
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE43_DIR = BACKEND_DIR / "research" / "stage_8_9_43"
STAGE44_DIR = BACKEND_DIR / "research" / "stage_8_9_44"

MANIFEST_P = STAGE43_DIR / "manifests" / "dataset_manifest_v5.csv"

# 1. Production freeze check
EXPECTED_HASHES = {
    BACKEND_DIR / "models" / "scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    BACKEND_DIR / "models" / "model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    BACKEND_DIR / "reports" / "test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    BACKEND_DIR / "reports" / "stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
}

def main():
    print("=" * 80)
    print("STAGE 8.9.44: PHASE A AUDIT")
    print("=" * 80)

    # 1. Hash audit
    hash_results = []
    all_hashes_ok = True
    for p, exp in EXPECTED_HASHES.items():
        if not p.exists():
            print(f"Missing: {p}")
            all_hashes_ok = False
            continue
        actual = hashlib.sha256(p.read_bytes()).hexdigest()
        ok = (actual == exp)
        if not ok:
            all_hashes_ok = False
        hash_results.append({
            "path": str(p.relative_to(REPO_ROOT)),
            "expected": exp,
            "actual": actual,
            "match": ok
        })
        print(f"  {p.name}: {'MATCH' if ok else 'MISMATCH'}")

    assert all_hashes_ok, "Production hash audit FAILED!"

    # 2. Manifest audit
    df = pd.read_csv(MANIFEST_P)
    print(f"\nManifest loaded: {len(df)} records across {df['source_group_id'].nunique()} source groups.")
    
    splits = ["v5_train", "v5_validation", "v5_development_test", "v5_final_holdout"]
    split_stats = {}
    sg_sets = {}
    for s in splits:
        sub = df[df["v5_research_split"] == s]
        sgs = set(sub["source_group_id"].dropna().unique())
        sg_sets[s] = sgs
        n_pos = int((sub["binary_label"] == 1).sum())
        n_neg = int((sub["binary_label"] == 0).sum())
        split_stats[s] = {
            "total": len(sub),
            "pos": n_pos,
            "neg": n_neg,
            "source_groups": len(sgs)
        }
        print(f"  {s}: Total={len(sub)}, Pos={n_pos}, Neg={n_neg}, SourceGroups={len(sgs)}")

    # Check overlaps
    overlaps = {}
    has_leakage = False
    for i in range(len(splits)):
        for j in range(i + 1, len(splits)):
            ov = sg_sets[splits[i]].intersection(sg_sets[splits[j]])
            if len(ov) > 0:
                has_leakage = True
            overlaps[f"{splits[i]}_vs_{splits[j]}"] = len(ov)
            print(f"  Overlap {splits[i]} vs {splits[j]}: {len(ov)} source groups")

    assert not has_leakage, "Source group overlap detected!"

    # Subtype distribution on holdout
    holdout_df = df[df["v5_research_split"] == "v5_final_holdout"]
    holdout_pos = holdout_df[holdout_df["binary_label"] == 1]
    print(f"\nFinal Holdout Positives Subtype Breakdown ({len(holdout_pos)} clips):")
    subtypes = holdout_pos["acoustic_subtype"].value_counts()
    for st, c in subtypes.items():
        print(f"  {st}: {c}")

    # Inspect Stage 8.9.43 Config-B-v5 false negatives on holdout
    y_data = np.load(STAGE43_DIR / "features" / "yamnet_v5_cache.npz", allow_pickle=True)
    h_mask = (y_data["splits"] == "v5_final_holdout")
    h_fids = y_data["file_ids"][h_mask]
    h_labels = y_data["labels"][h_mask]
    h_cats = y_data["categories"][h_mask]
    h_subs = y_data["subtypes"][h_mask]
    h_durs = y_data["durations"][h_mask]

    import torch
    sys.path.insert(0, str(STAGE43_DIR / "scripts"))
    from train_all_candidates_v5 import DualEncoderAcousticModel
    model = DualEncoderAcousticModel()
    model.load_state_dict(torch.load(STAGE43_DIR / "models" / "config_b_v5.pt", map_location="cpu"))
    model.eval()

    X_sem = torch.tensor(y_data["X_sem"][h_mask], dtype=torch.float32)
    X_ac = torch.tensor(y_data["X_acoust"][h_mask], dtype=torch.float32)
    M_ac = torch.tensor(y_data["mask_acoust"][h_mask], dtype=torch.float32)

    with torch.no_grad():
        logits, _, _ = model(X_sem, X_ac, M_ac)
        probs = torch.sigmoid(logits).numpy()

    th_star = 0.8200
    preds = (probs >= th_star).astype(int)
    
    # Identify False Negatives
    fn_mask = (h_labels == 1) & (preds == 0)
    fn_fids = h_fids[fn_mask]
    fn_probs = probs[fn_mask]
    fn_subs = h_subs[fn_mask]
    fn_durs = h_durs[fn_mask]
    print(f"\nConfig-B-v5 Holdout Recall: {np.sum((h_labels==1) & (preds==1))}/{np.sum(h_labels==1)} ({np.mean(preds[h_labels==1])*100:.2f}%)")
    print(f"False Negatives Count: {len(fn_fids)} out of {np.sum(h_labels==1)}")
    
    fn_summary = []
    for fid, p, sub, dur in zip(fn_fids, fn_probs, fn_subs, fn_durs):
        fn_summary.append({
            "file_id": fid,
            "prob": round(float(p), 4),
            "subtype": sub,
            "duration": round(float(dur), 2)
        })

    print(f"Top FN subtypes: {pd.Series(fn_subs).value_counts().to_dict()}")

    # Save summary json
    audit_data = {
        "production_hashes": hash_results,
        "split_stats": split_stats,
        "overlaps": overlaps,
        "stage_43_holdout_false_negatives": fn_summary
    }
    with open(STAGE44_DIR / "results" / "phase_a_audit.json", "w", encoding="utf-8") as f:
        json.dump(audit_data, f, indent=2)
    print(f"\nPhase A audit saved to results/phase_a_audit.json")

if __name__ == "__main__":
    main()
