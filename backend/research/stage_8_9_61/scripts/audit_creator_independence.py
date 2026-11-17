#!/usr/bin/env python3
"""
STAGE 8.9.61 — Creator Independence Audit Script
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import json
import os
import pandas as pd
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE54_DIR = BACKEND_DIR / "research" / "stage_8_9_54"
STAGE47_DIR = BACKEND_DIR / "research" / "stage_8_9_47"
STAGE55_DIR = BACKEND_DIR / "research" / "stage_8_9_55"
STAGE60_DIR = BACKEND_DIR / "research" / "stage_8_9_60"
STAGE61_DIR = BACKEND_DIR / "research" / "stage_8_9_61"

def main():
    print("Executing Phase A1: Creator-Level Independence Audit...")
    
    # 1. Load historical partitions (Stage 54)
    p54 = STAGE54_DIR / "dataset" / "partition_manifest_verified.csv"
    df54 = pd.read_csv(p54)
    train_df = df54[df54["expansion_partition"] == "expansion_train"]
    val_df = df54[df54["expansion_partition"] == "expansion_val"]
    test_df = df54[df54["expansion_partition"] == "expansion_reserved_test"]
    
    # 2. Load Stage 47 cohort
    p47 = STAGE47_DIR / "INDEPENDENT_COHORT_MANIFEST.csv"
    df47 = pd.read_csv(p47)
    
    # 3. Load Stage 55 cohort
    p55 = STAGE55_DIR / "dataset" / "acquisition_manifest.csv"
    df55 = pd.read_csv(p55)
    
    # 4. Load Stage 60 acquisition pool
    p60_acq = STAGE60_DIR / "acquisition_manifest.csv"
    df60_acq = pd.read_csv(p60_acq)
    
    # 5. Load Stage 60 sealed cohort
    p60_seal = STAGE60_DIR / "future_evaluation_manifest.json"
    with open(p60_seal) as f:
        d60_seal = json.load(f)
    df60_seal = pd.DataFrame(d60_seal["recordings"])
    
    # Define partition mappings: name -> dataframe, creator_col, sg_col, rec_col
    partitions = {
        "expansion_train": (train_df, "creator", "source_group_id", "expansion_file_id"),
        "expansion_val": (val_df, "creator", "source_group_id", "expansion_file_id"),
        "expansion_reserved_test": (test_df, "creator", "source_group_id", "expansion_file_id"),
        "stage_47_cohort": (df47, "creator", "source_group_id", "file_id"),
        "stage_55_cohort": (df55, "creator_uploader", "source_group_id", "recording_id"),
        "stage_60_pool": (df60_acq, "uploader_or_creator", "source_group_id", "recording_id"),
        "stage_60_sealed_cohort": (df60_seal, "uploader_or_creator", "source_group_id", "recording_id")
    }
    
    print("\nCreator Counts per Partition:")
    partition_creators = {}
    for name, (pdf, ccol, sgcol, rcol) in partitions.items():
        creators = set(pdf[ccol].dropna().unique())
        partition_creators[name] = creators
        print(f"  {name:25s}: {len(creators):4d} unique creators | {pdf[sgcol].nunique():4d} SGs | {len(pdf):4d} recordings")
        
    # Pairwise creator intersection analysis
    intersection_rows = []
    pnames = list(partitions.keys())
    for i in range(len(pnames)):
        for j in range(i + 1, len(pnames)):
            p1_name = pnames[i]
            p2_name = pnames[j]
            c1 = partition_creators[p1_name]
            c2 = partition_creators[p2_name]
            inter = c1 & c2
            
            p1_df, c1_col, sg1_col, r1_col = partitions[p1_name]
            p2_df, c2_col, sg2_col, r2_col = partitions[p2_name]
            
            p1_affected_recs = p1_df[p1_df[c1_col].isin(inter)][r1_col].nunique() if inter else 0
            p2_affected_recs = p2_df[p2_df[c2_col].isin(inter)][r2_col].nunique() if inter else 0
            p1_affected_sgs = p1_df[p1_df[c1_col].isin(inter)][sg1_col].nunique() if inter else 0
            p2_affected_sgs = p2_df[p2_df[c2_col].isin(inter)][sg2_col].nunique() if inter else 0
            
            # Sub-case: pool vs sealed is expected subset
            is_expected_subset = (p1_name == "stage_60_pool" and p2_name == "stage_60_sealed_cohort")
            if is_expected_subset:
                status = "EXPECTED_SUBSET"
                governance = "SEALED_CONTAINED_IN_POOL"
            elif len(inter) == 0:
                status = "CLEAN_INDEPENDENT"
                governance = "ZERO_CREATOR_LEAKAGE"
            else:
                status = "HISTORICAL_OVERLAP"
                governance = "DOCUMENTED_HISTORICAL_LEAKAGE"
                
            intersection_rows.append({
                "partition_1": p1_name,
                "partition_2": p2_name,
                "p1_unique_creators": len(c1),
                "p2_unique_creators": len(c2),
                "overlapping_creators_count": len(inter),
                "overlapping_creator_list": "; ".join(sorted(inter)) if inter else "NONE",
                "p1_affected_recordings": p1_affected_recs,
                "p2_affected_recordings": p2_affected_recs,
                "p1_affected_source_groups": p1_affected_sgs,
                "p2_affected_source_groups": p2_affected_sgs,
                "audit_status": status,
                "governance_classification": governance
            })
            
    df_inter = pd.DataFrame(intersection_rows)
    out_csv = STAGE61_DIR / "creator_partition_intersections.csv"
    df_inter.to_csv(out_csv, index=False)
    print(f"\nSaved creator partition intersections to {out_csv}")
    
    print("\nPairwise Creator Intersections Involving Sealed Cohort:")
    sealed_checks = df_inter[df_inter["partition_2"] == "stage_60_sealed_cohort"]
    for _, row in sealed_checks.iterrows():
        print(f"  stage_60_sealed_cohort vs {row['partition_1']:25s}: {row['overlapping_creators_count']:2d} overlap ({row['audit_status']})")
        
    # Check unknown or blank creators
    for name, (pdf, ccol, sgcol, rcol) in partitions.items():
        unknown_mask = pdf[ccol].isna() | (pdf[ccol].astype(str).str.lower().isin(["unknown", "none", "", "nan"]))
        n_unknown = unknown_mask.sum()
        if n_unknown > 0:
            print(f"  Notice: {name} contains {n_unknown} recordings with generic/unknown creator string")

if __name__ == "__main__":
    main()

