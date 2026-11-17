"""
Stage 8.9.36 - Phase 7: Dataset & Source-Group Quality Audit Script
Performs cryptographic deduplication, partition leakage auditing,
licensing compliance checking, and label consistency verification across 1,328 recordings.
"""
import os
import hashlib
import numpy as np
import pandas as pd

def audit_dataset():
    print("======================================================================")
    print("STAGE 8.9.36 - PHASE 7: DATASET & SOURCE-GROUP QUALITY AUDIT")
    print("======================================================================")
    
    manifest_path = "backend/experiments/v2_hard_negative_training/manifests/dataset_manifest_v3.csv"
    assert os.path.exists(manifest_path), f"Missing manifest: {manifest_path}"
    df = pd.read_csv(manifest_path)
    total_files = len(df)
    print(f"Total manifest records: {total_files}")
    
    # 1. Unique IDs & Hash Deduplication
    unique_fids = df['file_id'].nunique()
    unique_sha256 = df['sha256_hash'].nunique()
    unique_pcm_sha256 = df['pcm_sha256'].nunique()
    
    print(f"Unique file_ids: {unique_fids}")
    print(f"Unique sha256_hash: {unique_sha256}")
    print(f"Unique pcm_sha256 (exact audio content): {unique_pcm_sha256}")
    
    # Find exact duplicate PCM audio hashes
    pcm_counts = df['pcm_sha256'].value_counts()
    dup_hashes = pcm_counts[pcm_counts > 1].index.tolist()
    print(f"Number of duplicate PCM audio hashes: {len(dup_hashes)}")
    
    duplicate_rows = []
    if len(dup_hashes) > 0:
        dup_df = df[df['pcm_sha256'].isin(dup_hashes)].sort_values(by='pcm_sha256')
        for h, grp in dup_df.groupby('pcm_sha256'):
            fids = grp['file_id'].tolist()
            splits = grp['split'].tolist()
            labels = grp['binary_label'].tolist()
            cats = grp['target_category'].tolist()
            duplicate_rows.append({
                "pcm_sha256": h,
                "duplicate_count": len(grp),
                "file_ids": "; ".join(fids),
                "splits": "; ".join(splits),
                "binary_labels": "; ".join(labels),
                "categories": "; ".join(cats),
                "cross_split_leakage": len(set(splits)) > 1
            })
    else:
        duplicate_rows.append({
            "pcm_sha256": "NONE",
            "duplicate_count": 0,
            "file_ids": "None",
            "splits": "None",
            "binary_labels": "None",
            "categories": "None",
            "cross_split_leakage": False
        })
    df_dup = pd.DataFrame(duplicate_rows)
    eval_dir = "backend/research/stage_8_9_36/evaluation"
    os.makedirs(eval_dir, exist_ok=True)
    dup_csv = os.path.join(eval_dir, "duplicate_risk_report.csv")
    df_dup.to_csv(dup_csv, index=False)
    print(f"Saved {dup_csv}")

    # 2. Source-Group Partition Isolation Audit
    splits = df['split'].unique()
    train_groups = set(df[df['split'] == 'train']['source_group_id'])
    val_groups = set(df[df['split'] == 'val']['source_group_id'])
    test_groups = set(df[df['split'] == 'test']['source_group_id'])
    
    train_val_overlap = train_groups.intersection(val_groups)
    train_test_overlap = train_groups.intersection(test_groups)
    val_test_overlap = val_groups.intersection(test_groups)
    
    print("\nSource Group Partition Leakage Check:")
    print(f"  Train source groups: {len(train_groups)}")
    print(f"  Val source groups:   {len(val_groups)}")
    print(f"  Test source groups:  {len(test_groups)}")
    print(f"  Train-Val overlap:   {len(train_val_overlap)}")
    print(f"  Train-Test overlap:  {len(train_test_overlap)}")
    print(f"  Val-Test overlap:    {len(val_test_overlap)}")
    
    source_group_rows = []
    for sp in ['train', 'val', 'test']:
        sp_df = df[df['split'] == sp]
        source_group_rows.append({
            "split": sp,
            "total_recordings": len(sp_df),
            "screams": int((sp_df['binary_label'] == 'scream').sum()),
            "hard_negatives": int((sp_df['binary_label'] == 'non_scream').sum()),
            "ambiguous": int((sp_df['binary_label'] == 'ambiguous').sum()),
            "unique_source_groups": sp_df['source_group_id'].nunique(),
            "unique_creators": sp_df['creator'].nunique(),
            "mean_files_per_group": round(len(sp_df) / sp_df['source_group_id'].nunique(), 2),
            "leakage_count_with_test": len(set(sp_df['source_group_id']).intersection(test_groups)) if sp != 'test' else 0
        })
    df_sg = pd.DataFrame(source_group_rows)
    sg_csv = os.path.join(eval_dir, "source_group_integrity.csv")
    df_sg.to_csv(sg_csv, index=False)
    print(f"Saved {sg_csv}")

    # 3. Label Consistency Audit
    label_issues = []
    for idx, r in df.iterrows():
        cat = str(r['target_category']).lower()
        b_label = str(r['binary_label']).lower()
        fid = r['file_id']
        
        # Inconsistency checks
        issue = None
        if b_label == 'ambiguous':
            issue = "Ambiguous label (quarantined from training/evaluation)"
        elif b_label == 'scream' and 'scream' not in cat:
            issue = f"Category '{cat}' marked as scream"
        elif b_label == 'non_scream' and 'scream' in cat and 'masked' not in cat:
            issue = f"Scream category '{cat}' marked as non_scream"
            
        if issue:
            label_issues.append({
                "file_id": fid,
                "split": r['split'],
                "target_category": r['target_category'],
                "binary_label": r['binary_label'],
                "issue_description": issue
            })
            
    if not label_issues:
        label_issues.append({
            "file_id": "NONE",
            "split": "ALL",
            "target_category": "ALL",
            "binary_label": "ALL",
            "issue_description": "Zero label inconsistencies detected."
        })
        
    df_labels = pd.DataFrame(label_issues)
    label_csv = os.path.join(eval_dir, "label_consistency_report.csv")
    df_labels.to_csv(label_csv, index=False)
    print(f"Saved {label_csv} (Found {len(label_issues)} label flags)")

    # 4. Licensing Audit
    print("\n--- Licensing Compliance Breakdown ---")
    lic_counts = df['license'].value_counts()
    for lic, cnt in lic_counts.items():
        is_nc = "NC" in str(lic).upper()
        status = "QUARANTINE_FOR_COMMERCIAL" if is_nc else "COMMERCIALLY_ELIGIBLE"
        print(f"  {lic}: {cnt} files ({cnt/total_files*100:.1f}%) -> {status}")
        
    return df_dup, df_sg, df_labels

if __name__ == '__main__':
    audit_dataset()
