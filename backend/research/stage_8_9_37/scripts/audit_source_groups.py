"""
Stage 8.9.37 - Task 10b: Source Group Audit & Partition Isolation
Verifies source group independence and partition isolation for the expansion dataset.
Outputs manifests/source_groups.csv with reservation counts.
"""
import os
import pandas as pd

def audit_source_groups():
    print("======================================================================")
    print("STAGE 8.9.37 - TASK 10B: SOURCE GROUP AUDIT & PARTITION ISOLATION")
    print("======================================================================")
    
    acq_csv = "backend/research/stage_8_9_37/manifests/acquired_recordings.csv"
    df = pd.read_csv(acq_csv)
    
    grp_summary = []
    for grp_id, gdf in df.groupby('source_group_id'):
        cats = gdf['target_category'].unique().tolist()
        splits = gdf['target_split_reservation'].unique().tolist()
        creators = gdf['creator_id'].unique().tolist()
        
        # Check single partition per source group
        is_isolated = (len(splits) == 1)
        
        grp_summary.append({
            "source_group_id": grp_id,
            "creator_id": ", ".join(creators),
            "num_clips": len(gdf),
            "categories": ", ".join(cats),
            "target_partition": splits[0] if is_isolated else "LEAKED_MULTIPLE_PARTITIONS",
            "is_partition_isolated": is_isolated,
            "min_duration": round(gdf['duration_seconds'].min(), 3),
            "max_duration": round(gdf['duration_seconds'].max(), 3)
        })
        
    sg_df = pd.DataFrame(grp_summary)
    out_csv = "backend/research/stage_8_9_37/manifests/source_groups.csv"
    sg_df.to_csv(out_csv, index=False)
    print(f"Saved {out_csv} ({len(sg_df)} unique source groups)")
    
    print("\nSource Group Partition Allocations:")
    print(sg_df['target_partition'].value_counts())
    
    short_test_grps = sg_df[sg_df['source_group_id'].str.contains('short_scream') & (sg_df['target_partition'] == 'reserved_held_out_test')]
    print(f"\nShort Scream Reserved Test Groups: {len(short_test_grps)} (Target: >= 35)")
    print(f"Any Partition Leakage? {not sg_df['is_partition_isolated'].all()}")

if __name__ == "__main__":
    audit_source_groups()
