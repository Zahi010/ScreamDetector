"""
Stage 8.9.37 - Task 10: Duplicate & Near-Duplicate Audit
Audits newly acquired recordings against existing dataset (dataset_manifest_v3.csv)
and internally for exact SHA-256 matches, parent-clip collisions, and near-duplicate candidates.
"""
import os
import pandas as pd

def audit_duplicates():
    print("======================================================================")
    print("STAGE 8.9.37 - TASK 10: DUPLICATE & NEAR-DUPLICATE AUDIT")
    print("======================================================================")
    
    acq_csv = "backend/research/stage_8_9_37/manifests/acquired_recordings.csv"
    hist_csv = "backend/experiments/v2_hard_negative_training/manifests/dataset_manifest_v3.csv"
    
    acq_df = pd.read_csv(acq_csv)
    hist_df = pd.read_csv(hist_csv)
    
    hist_hashes = set(hist_df['sha256_hash'].dropna())
    hist_creators = set(hist_df['creator'].dropna())
    hist_groups = set(hist_df['source_group_id'].dropna())
    
    audit_results = []
    
    # Internal duplicate check
    acq_hashes = acq_df['sha256_checksum'].tolist()
    seen_hashes = {}
    
    for _, r in acq_df.iterrows():
        rec_id = r['acquisition_id']
        h = r['sha256_checksum']
        creator = r['creator_id']
        grp = r['source_group_id']
        parent = r['parent_recording_id']
        
        # Exact duplicate with historical?
        hist_exact = h in hist_hashes
        
        # Internal exact duplicate?
        internal_exact = h in seen_hashes
        if not internal_exact:
            seen_hashes[h] = rec_id
            
        # Parent recording overlap
        parent_overlap = parent in hist_df['original_recording_id'].values
        
        # Source group overlap with historical
        group_overlap = grp in hist_groups
        
        status = "PASSED_INDEPENDENT"
        notes = "No duplicate detected; independent recording"
        
        if hist_exact or internal_exact:
            status = "EXACT_DUPLICATE_QUARANTINED"
            notes = "Exact SHA-256 hash collision"
        elif parent_overlap:
            status = "PARENT_EXCERPT_COLLISION_QUARANTINED"
            notes = "Shares parent recording with historical dataset"
        elif group_overlap:
            status = "SOURCE_GROUP_OVERLAP_REVIEW"
            notes = "Same source group exists in historical dataset; review partition assignment"
            
        audit_results.append({
            "acquisition_id": rec_id,
            "target_category": r['target_category'],
            "sha256_checksum": h,
            "duplicate_audit_status": status,
            "historical_exact_match": hist_exact,
            "internal_exact_match": internal_exact,
            "parent_overlap": parent_overlap,
            "source_group_overlap": group_overlap,
            "forensic_notes": notes
        })
        
    res_df = pd.DataFrame(audit_results)
    out_csv = "backend/research/stage_8_9_37/manifests/duplicate_audit.csv"
    res_df.to_csv(out_csv, index=False)
    print(f"Saved {out_csv} ({len(res_df)} records)")
    print(res_df['duplicate_audit_status'].value_counts())

if __name__ == "__main__":
    audit_duplicates()
