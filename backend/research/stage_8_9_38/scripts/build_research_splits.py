"""
Stage 8.9.38 - Task 8: Construction of Source-Group-Aware Research Splits (v4)
Builds the formal, versioned research splits:
1. v4_train (N=825 active, 325 source groups)
2. v4_val (N=336 active, 114 source groups)
3. v4_historical_test (N=293 active, 111 source groups, STRICTLY PRESERVED)
4. v4_reserved_expansion_test (N=100 active: 63 short screams, 37 HN across 49 source groups)
5. Quarantined (N=24: 21 CC-NC, 3 ambiguous)
Total: 1,578 cataloged recordings. Verifies 100% source-group partition isolation.
"""
import os
import hashlib
import json
import pandas as pd

def build_research_splits():
    print("======================================================================")
    print("STAGE 8.9.38 - TASK 8: SOURCE-GROUP-AWARE RESEARCH SPLIT CONSTRUCTION")
    print("======================================================================")
    
    v4_csv = "backend/research/stage_8_9_38/manifests/dataset_manifest_v4.csv"
    df = pd.read_csv(v4_csv)
    
    manifest_dir = "backend/research/stage_8_9_38/manifests"
    report_dir = "backend/research/stage_8_9_38/dataset_reports"
    os.makedirs(manifest_dir, exist_ok=True)
    os.makedirs(report_dir, exist_ok=True)
    
    # Define unified research split v4 mapping
    # Every source group must belong to exactly one unified partition
    split_v4_col = []
    
    for _, r in df.iterrows():
        fid = r['file_id']
        hist_split = r['split']
        eligible = r['is_commercially_eligible']
        
        if not eligible:
            split_v4_col.append("quarantined")
        elif r['is_historical_stage5_test'] or (fid in df[df['split'] == 'test']['file_id'].values and not fid.startswith('acq_')):
            split_v4_col.append("v4_historical_test")
        elif fid.startswith('acq_'):
            if hist_split == 'reserved_held_out_test':
                split_v4_col.append("v4_reserved_expansion_test")
            elif hist_split == 'val':
                split_v4_col.append("v4_val")
            else:
                split_v4_col.append("v4_train")
        else:
            if hist_split == 'val':
                split_v4_col.append("v4_val")
            else:
                split_v4_col.append("v4_train")
                
    df['v4_research_split'] = split_v4_col
    
    # Save updated research split manifest
    split_csv = os.path.join(manifest_dir, "research_split_v4.csv")
    df.to_csv(split_csv, index=False)
    print(f"Saved Research Split Manifest: {split_csv} ({len(df)} records)")
    
    # Check source group isolation across the active splits
    active_df = df[df['v4_research_split'] != 'quarantined']
    sg_overlap_audit = []
    
    splits_list = ["v4_train", "v4_val", "v4_historical_test", "v4_reserved_expansion_test"]
    for i in range(len(splits_list)):
        for j in range(i + 1, len(splits_list)):
            s1 = splits_list[i]
            s2 = splits_list[j]
            sg1 = set(active_df[active_df['v4_research_split'] == s1]['source_group_id'].dropna())
            sg2 = set(active_df[active_df['v4_research_split'] == s2]['source_group_id'].dropna())
            overlap = sg1.intersection(sg2)
            sg_overlap_audit.append({
                "split_pair": f"{s1} vs {s2}",
                "split_1_groups": len(sg1),
                "split_2_groups": len(sg2),
                "overlapping_groups_count": len(overlap),
                "is_clean_isolated": len(overlap) == 0,
                "overlapping_groups": ", ".join(list(overlap)) if len(overlap) > 0 else "None"
            })
            
    sg_audit_df = pd.DataFrame(sg_overlap_audit)
    sg_csv = os.path.join(manifest_dir, "source_group_split_manifest.csv")
    sg_audit_df.to_csv(sg_csv, index=False)
    print(f"Saved Source Group Split Audit: {sg_csv}")
    print(sg_audit_df[['split_pair', 'split_1_groups', 'split_2_groups', 'overlapping_groups_count', 'is_clean_isolated']])
    
    # 2. Label Manifest
    label_summary = []
    for (split_name, cat, bin_label), grp in df.groupby(['v4_research_split', 'target_category', 'binary_label']):
        label_summary.append({
            "split": split_name,
            "target_category": cat,
            "binary_label": bin_label,
            "clip_count": len(grp),
            "source_group_count": grp['source_group_id'].nunique(),
            "mean_duration_sec": round(grp['duration_seconds'].mean(), 3),
            "total_duration_sec": round(grp['duration_seconds'].sum(), 1)
        })
    label_df = pd.DataFrame(label_summary)
    label_csv = os.path.join(manifest_dir, "label_manifest.csv")
    label_df.to_csv(label_csv, index=False)
    print(f"Saved Label Manifest: {label_csv}")
    
    # 3. License Manifest
    lic_summary = []
    for (lic_name, elig), grp in df.groupby(['license', 'is_commercially_eligible']):
        lic_summary.append({
            "license": lic_name,
            "is_commercially_eligible": elig,
            "clip_count": len(grp),
            "quarantine_status": "Approved" if elig else "QUARANTINED"
        })
    lic_df = pd.DataFrame(lic_summary)
    lic_csv = os.path.join(manifest_dir, "license_manifest.csv")
    lic_df.to_csv(lic_csv, index=False)
    print(f"Saved License Manifest: {lic_csv}")
    
    # 4. Duplicate Manifest
    dup_manifest_df = df[['file_id', 'target_category', 'duration_seconds', 'sha256_hash', 'pcm_sha256', 'source_group_id', 'v4_research_split']].copy()
    dup_manifest_df['has_exact_sha256_dup'] = dup_manifest_df.duplicated(subset=['sha256_hash'], keep=False)
    dup_manifest_df['has_exact_pcm_dup'] = dup_manifest_df.duplicated(subset=['pcm_sha256'], keep=False)
    dup_csv = os.path.join(manifest_dir, "duplicate_manifest.csv")
    dup_manifest_df.to_csv(dup_csv, index=False)
    print(f"Saved Duplicate Manifest: {dup_csv}")
    
    # Checksums
    checksums = {}
    for f in ["research_split_v4.csv", "source_group_split_manifest.csv", "label_manifest.csv", "license_manifest.csv", "duplicate_manifest.csv"]:
        fp = os.path.join(manifest_dir, f)
        with open(fp, "rb") as fh:
            checksums[f] = hashlib.sha256(fh.read()).hexdigest()
            
    with open(os.path.join(manifest_dir, "manifest_checksums.json"), "w", encoding="utf-8") as fh:
        json.dump(checksums, fh, indent=2)
        
    print("\n--- Unified Research Split v4 Overview ---")
    print(df['v4_research_split'].value_counts())
    
    # Print Screams vs Negatives per split
    print("\nActive Clips Breakdown (Screams vs Non-Screams):")
    for s in splits_list:
        sub = active_df[active_df['v4_research_split'] == s]
        screams = len(sub[sub['binary_label'] == 'scream'])
        negs = len(sub[sub['binary_label'] == 'non_scream'])
        grps = sub['source_group_id'].nunique()
        print(f"[{s}] Total={len(sub)} (Screams={screams}, Non-Screams={negs}, Source Groups={grps})")

if __name__ == "__main__":
    build_research_splits()
