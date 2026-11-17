import os
import json
import pandas as pd

# MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
STAGE_DIR = os.path.join(REPO_ROOT, "backend", "research", "stage_8_9_59")
STAGE54_DIR = os.path.join(REPO_ROOT, "backend", "research", "stage_8_9_54")

def main():
    print("Executing Phase E: Source Independence and Leakage Audit...")
    
    manifest_p = os.path.join(STAGE54_DIR, "dataset", "partition_manifest_verified.csv")
    df = pd.read_csv(manifest_p)
    
    train = df[df["expansion_partition"] == "expansion_train"].copy()
    val = df[df["expansion_partition"] == "expansion_val"].copy()
    test = df[df["expansion_partition"] == "expansion_reserved_test"].copy()
    
    # 1. Exact File Hash Duplicates
    h_train = set(train["file_sha256"].dropna())
    h_val = set(val["file_sha256"].dropna())
    h_test = set(test["file_sha256"].dropna())
    
    exact_hash_leakage = {
        "train_val_overlap": len(h_train.intersection(h_val)),
        "train_test_overlap": len(h_train.intersection(h_test)),
        "val_test_overlap": len(h_val.intersection(h_test))
    }
    
    # 2. PCM Hash Duplicates
    pcm_train = set(train["pcm_sha256"].dropna())
    pcm_val = set(val["pcm_sha256"].dropna())
    pcm_test = set(test["pcm_sha256"].dropna())
    
    pcm_hash_leakage = {
        "train_val_overlap": len(pcm_train.intersection(pcm_val)),
        "train_test_overlap": len(pcm_train.intersection(pcm_test)),
        "val_test_overlap": len(pcm_val.intersection(pcm_test))
    }
    
    # 3. Source Group ID Duplicates
    sg_train = set(train["source_group_id"].dropna())
    sg_val = set(val["source_group_id"].dropna())
    sg_test = set(test["source_group_id"].dropna())
    
    sg_leakage = {
        "train_val_overlap": len(sg_train.intersection(sg_val)),
        "train_test_overlap": len(sg_train.intersection(sg_test)),
        "val_test_overlap": len(sg_val.intersection(sg_test))
    }
    
    # 4. Parent Recording Excerpts
    parent_records = []
    for orig_id, group in df.groupby("original_recording_id"):
        partitions = group["expansion_partition"].unique().tolist()
        count = len(group)
        is_cross = len(partitions) > 1
        parent_records.append({
            "original_recording_id": orig_id,
            "crop_count": count,
            "partitions": "; ".join(partitions),
            "is_cross_partition_leak": is_cross,
            "file_ids": "; ".join(group["expansion_file_id"].tolist())
        })
        
    df_parents = pd.DataFrame(parent_records)
    multicrop_parents = df_parents[df_parents["crop_count"] > 1]
    cross_partition_crops = df_parents[df_parents["is_cross_partition_leak"] == True]
    
    # 5. Creator / Uploader Audit
    c_train = set(train["creator"].dropna())
    c_val = set(val["creator"].dropna())
    c_test = set(test["creator"].dropna())
    
    shared_c_train_val = sorted(list(c_train.intersection(c_val)))
    shared_c_train_test = sorted(list(c_train.intersection(c_test)))
    shared_c_val_test = sorted(list(c_val.intersection(c_test)))
    
    creator_leakage = {
        "train_val_shared_creators": shared_c_train_val,
        "train_val_shared_count": len(shared_c_train_val),
        "train_test_shared_creators": shared_c_train_test,
        "train_test_shared_count": len(shared_c_train_test),
        "val_test_shared_creators": shared_c_val_test,
        "val_test_shared_count": len(shared_c_val_test)
    }
    
    # Detail recordings from shared creators
    creator_leak_rows = []
    for c in set(shared_c_train_val + shared_c_train_test + shared_c_val_test):
        c_recs = df[df["creator"] == c]
        for idx, r in c_recs.iterrows():
            creator_leak_rows.append({
                "creator": c,
                "expansion_file_id": r["expansion_file_id"],
                "original_recording_id": r["original_recording_id"],
                "expansion_partition": r["expansion_partition"],
                "target_category": r["target_category"],
                "binary_label": r["binary_label"],
                "duration_seconds": r["duration_seconds"],
                "source_group_id": r["source_group_id"]
            })
    df_creator_leak = pd.DataFrame(creator_leak_rows)
    
    # Save duplicate_and_excerpt_audit.csv
    audit_csv = os.path.join(STAGE_DIR, "duplicate_and_excerpt_audit.csv")
    df_parents.to_csv(audit_csv, index=False)
    print(f"Saved parent recording audit to {audit_csv} ({len(df_parents)} unique parent sources)")
    
    # Save creator leakage details
    creator_csv = os.path.join(STAGE_DIR, "creator_overlap_details.csv")
    df_creator_leak.to_csv(creator_csv, index=False)
    print(f"Saved creator overlap details to {creator_csv} ({len(df_creator_leak)} recordings)")
    
    summary = {
        "exact_file_hash_leakage": exact_hash_leakage,
        "pcm_hash_leakage": pcm_hash_leakage,
        "source_group_id_leakage": sg_leakage,
        "multi_crop_parent_recordings": len(multicrop_parents),
        "cross_partition_parent_leaks": len(cross_partition_crops),
        "creator_uploader_leakage": {
            "train_val_count": len(shared_c_train_val),
            "train_test_count": len(shared_c_train_test),
            "val_test_count": len(shared_c_val_test),
            "shared_train_val": shared_c_train_val,
            "shared_train_test": shared_c_train_test,
            "shared_val_test": shared_c_val_test
        }
    }
    with open(os.path.join(STAGE_DIR, "source_independence_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
        
    print("\nSource Independence Summary:")
    print(f"  Exact File Hash Overlap: Train/Val: {exact_hash_leakage['train_val_overlap']}, Train/Test: {exact_hash_leakage['train_test_overlap']}")
    print(f"  PCM Hash Overlap:        Train/Val: {pcm_hash_leakage['train_val_overlap']}, Train/Test: {pcm_hash_leakage['train_test_overlap']}")
    print(f"  Source Group ID Overlap: Train/Val: {sg_leakage['train_val_overlap']}, Train/Test: {sg_leakage['train_test_overlap']}")
    print(f"  Multi-crop Parent Sources: {len(multicrop_parents)} (Cross-partition: {len(cross_partition_crops)})")
    print(f"  Creator/Uploader Overlap: Train/Val: {len(shared_c_train_val)}, Train/Test: {len(shared_c_train_test)}, Val/Test: {len(shared_c_val_test)}")

if __name__ == "__main__":
    main()

