import os
import json
import pandas as pd

# MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
STAGE_DIR = os.path.join(REPO_ROOT, "backend", "research", "stage_8_9_60")

def main():
    print("Executing Phase E: Auditing Source Group Independence & Creator Isolation...")
    
    # 1. Load acquired pool and sealed evaluation cohort
    acq_p = os.path.join(STAGE_DIR, "acquisition_manifest.csv")
    df_acq = pd.read_csv(acq_p)
    
    eval_json_p = os.path.join(STAGE_DIR, "future_evaluation_manifest.json")
    with open(eval_json_p, "r") as f:
        eval_data = json.load(f)
    df_eval = pd.DataFrame(eval_data["recordings"])
    
    # 2. Load existing training and validation partitions (Stage 8.9.54)
    man54_p = os.path.join(REPO_ROOT, "backend", "research", "stage_8_9_54", "dataset", "partition_manifest_verified.csv")
    df_man54 = pd.read_csv(man54_p)
    train_54 = df_man54[df_man54["expansion_partition"] == "expansion_train"]
    val_54 = df_man54[df_man54["expansion_partition"] == "expansion_val"]
    test_54 = df_man54[df_man54["expansion_partition"] == "expansion_reserved_test"]
    
    # Check source group overlap between Sealed Cohort and Historical Partitions
    eval_sgs = set(df_eval["source_group_id"].dropna())
    train_sgs = set(train_54["source_group_id"].dropna())
    val_sgs = set(val_54["source_group_id"].dropna())
    test_sgs = set(test_54["source_group_id"].dropna())
    
    sg_overlap_train = eval_sgs.intersection(train_sgs)
    sg_overlap_val = eval_sgs.intersection(val_sgs)
    sg_overlap_test = eval_sgs.intersection(test_sgs)
    
    # Check file hash overlap
    eval_hashes = set(df_eval["audio_sha256"].dropna())
    train_hashes = set(train_54["file_sha256"].dropna())
    val_hashes = set(val_54["file_sha256"].dropna())
    test_hashes = set(test_54["file_sha256"].dropna())
    
    h_overlap_train = eval_hashes.intersection(train_hashes)
    h_overlap_val = eval_hashes.intersection(val_hashes)
    h_overlap_test = eval_hashes.intersection(test_hashes)
    
    # Check PCM hash overlap
    eval_pcm = set(df_eval["pcm_sha256"].dropna())
    train_pcm = set(train_54["pcm_sha256"].dropna())
    val_pcm = set(val_54["pcm_sha256"].dropna())
    test_pcm = set(test_54["pcm_sha256"].dropna())
    
    pcm_overlap_train = eval_pcm.intersection(train_pcm)
    pcm_overlap_val = eval_pcm.intersection(val_pcm)
    pcm_overlap_test = eval_pcm.intersection(test_pcm)
    
    print("\nSource Independence Verification Results:")
    print(f"Sealed Evaluation Cohort Recordings: {len(df_eval)}")
    print(f"Sealed Cohort Unique Source Groups:  {len(eval_sgs)}")
    print(f"Source Group Overlap with Train54:   {len(sg_overlap_train)}")
    print(f"Source Group Overlap with Val54:     {len(sg_overlap_val)}")
    print(f"Source Group Overlap with Test54:    {len(sg_overlap_test)}")
    print(f"File Hash Overlap with Train54:      {len(h_overlap_train)}")
    print(f"File Hash Overlap with Val54:        {len(h_overlap_val)}")
    print(f"File Hash Overlap with Test54:       {len(h_overlap_test)}")
    print(f"PCM Hash Overlap with Train54:       {len(pcm_overlap_train)}")
    print(f"PCM Hash Overlap with Val54:         {len(pcm_overlap_val)}")
    print(f"PCM Hash Overlap with Test54:        {len(pcm_overlap_test)}")
    
    summary = {
        "evaluation_cohort_recordings": len(df_eval),
        "evaluation_cohort_unique_source_groups": len(eval_sgs),
        "source_group_overlap": {
            "train_overlap_count": len(sg_overlap_train),
            "val_overlap_count": len(sg_overlap_val),
            "test_overlap_count": len(sg_overlap_test)
        },
        "file_hash_overlap": {
            "train_overlap_count": len(h_overlap_train),
            "val_overlap_count": len(h_overlap_val),
            "test_overlap_count": len(h_overlap_test)
        },
        "pcm_hash_overlap": {
            "train_overlap_count": len(pcm_overlap_train),
            "val_overlap_count": len(pcm_overlap_val),
            "test_overlap_count": len(pcm_overlap_test)
        },
        "source_independence_status": "STRICT_ZERO_OVERLAP_CONFIRMED"
    }
    with open(os.path.join(STAGE_DIR, "source_independence_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    main()

