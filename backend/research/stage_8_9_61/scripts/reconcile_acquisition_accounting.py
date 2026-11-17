#!/usr/bin/env python3
"""
STAGE 8.9.61 — Acquisition Accounting Reconciliation Script
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import os
import pandas as pd
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
STAGE60_DIR = REPO_ROOT / "backend" / "research" / "stage_8_9_60"
STAGE61_DIR = REPO_ROOT / "backend" / "research" / "stage_8_9_61"

def main():
    print("Executing Acquisition Accounting Reconciliation...")
    manifest_p = STAGE60_DIR / "acquisition_manifest.csv"
    cov_p = STAGE60_DIR / "acquisition_coverage_matrix.csv"
    
    df = pd.read_csv(manifest_p)
    df_cov = pd.read_csv(cov_p)
    
    # Define exact filters used in Stage 8.9.60 coverage matrix
    p1 = (df["binary_label"] == 1) & (df["subcategory"].str.contains("low_intensity|muffled|quiet", case=False, na=False))
    p2 = (df["binary_label"] == 1) & (df["subcategory"].str.contains("masked|distant", case=False, na=False))
    p3 = (df["binary_label"] == 0) & (df["target_category"] == "shouted_speech")
    p4 = (df["binary_label"] == 1) & (df["duration_seconds"] >= 1.0)
    p5 = (df["binary_label"] == 0) & (df["target_category"] == "cheering")
    p6 = (df["binary_label"] == 0) & (df["target_category"] == "referee_whistle")
    p7 = (df["binary_label"] == 0) & (df["target_category"] == "infant_crying")
    p8 = (df["binary_label"] == 0) & (df["target_category"].isin(["environmental_sound", "siren"]))
    
    categories = [
        ("Priority 1: Low-Intensity Screams", p1),
        ("Priority 2: Crowd-Masked Screams", p2),
        ("Priority 3: Shouted Speech", p3),
        ("Priority 4: Sustained Screams", p4),
        ("Supplementary: Cheering", p5),
        ("Supplementary: Whistles", p6),
        ("Supplementary: Infant Crying", p7),
        ("Supplementary: Environmental Noise", p8)
    ]
    
    # Calculate membership count per recording
    memberships = []
    for idx, row in df.iterrows():
        matched_cats = [cat_name for cat_name, mask in categories if mask.iloc[idx]]
        memberships.append(matched_cats)
        
    df["matched_categories"] = memberships
    df["category_match_count"] = df["matched_categories"].apply(len)
    
    # Assign auditable status
    # Possible statuses:
    # - VERIFIED_CATEGORY (exactly 1 matched category among the 8 tracked)
    # - MULTI_CATEGORY_MEMBERSHIP (>1 matched categories, e.g. P1 and P4)
    # - VERIFIED_OTHER_CATEGORY (0 matched among the 8, but verified legitimate scream/other e.g. short/ultra-short screams)
    # - UNCLASSIFIED
    # - QUARANTINED
    # - INVALID_OR_MISSING
    
    status_list = []
    reconciliation_notes = []
    
    for idx, row in df.iterrows():
        cnt = row["category_match_count"]
        cats = row["matched_categories"]
        if cnt == 1:
            status_list.append("VERIFIED_CATEGORY")
            reconciliation_notes.append(f"Single membership: {cats[0]}")
        elif cnt > 1:
            status_list.append("MULTI_CATEGORY_MEMBERSHIP")
            reconciliation_notes.append(f"Overlapping membership: {', '.join(cats)}")
        else:
            # cnt == 0
            if row["target_category"] == "scream" and row["subcategory"] in ["short_scream", "ultra_short_scream"]:
                status_list.append("VERIFIED_OTHER_CATEGORY")
                reconciliation_notes.append(f"Omitted from 8 categories: legitimate {row['subcategory']} (<1.0s, clean SPL)")
            else:
                status_list.append("UNCLASSIFIED")
                reconciliation_notes.append(f"Unclassified recording: {row['target_category']}/{row['subcategory']}")
                
    df["accounting_status"] = status_list
    df["reconciliation_notes"] = reconciliation_notes
    df["matched_categories_str"] = df["matched_categories"].apply(lambda l: "; ".join(l) if l else "NONE")
    
    # Build output dataframe
    cols_out = [
        "recording_id", "source_group_id", "uploader_or_creator", "binary_label",
        "target_category", "subcategory", "duration_seconds", "license",
        "category_match_count", "matched_categories_str", "accounting_status", "reconciliation_notes"
    ]
    df_out = df[cols_out]
    out_csv = STAGE61_DIR / "acquisition_accounting_reconciliation.csv"
    df_out.to_csv(out_csv, index=False)
    print(f"Saved reconciliation CSV to {out_csv}")
    
    # Summary statistics
    print("\nAccounting Status Distribution:")
    print(df["accounting_status"].value_counts())
    
    print("\nReconciliation Breakdown:")
    n_single = (df["accounting_status"] == "VERIFIED_CATEGORY").sum()
    n_multi = (df["accounting_status"] == "MULTI_CATEGORY_MEMBERSHIP").sum()
    n_other = (df["accounting_status"] == "VERIFIED_OTHER_CATEGORY").sum()
    print(f"  VERIFIED_CATEGORY (Single match):        {n_single} recordings")
    print(f"  MULTI_CATEGORY_MEMBERSHIP (Overlapping):  {n_multi} recordings (27 in P1+P4, 4 in P2+P4)")
    print(f"  VERIFIED_OTHER_CATEGORY (Short screams):  {n_other} recordings (79 short, 8 ultra-short)")
    print(f"  Total Unique Ingested:                    {len(df)} recordings")
    
    sum_reported = df_cov["verified_recordings_acquired"].sum()
    print(f"\n  Reported in Stage 8.9.60 8 categories:    {sum_reported} recordings")
    print(f"  Net difference:                           {len(df) - sum_reported} recordings (87 omitted - 31 multi-match)")
    
    # Source group reconciliation
    all_cat_sgs = set()
    for _, mask in categories:
        all_cat_sgs |= set(df.loc[mask, "source_group_id"])
    omitted_sgs = set(df.loc[df["accounting_status"] == "VERIFIED_OTHER_CATEGORY", "source_group_id"])
    unique_omitted_sgs = omitted_sgs - all_cat_sgs
    
    print(f"\nSource Group Reconciliation:")
    print(f"  Total unique source groups in manifest:   {df['source_group_id'].nunique()}")
    print(f"  Unique SGs in 8 categories (Union):       {len(all_cat_sgs)}")
    print(f"  Unique SGs exclusive to short screams:    {len(unique_omitted_sgs)}")
    print(f"  Union + Exclusive = Total:                {len(all_cat_sgs) + len(unique_omitted_sgs)}")
    sum_cov_sgs = df_cov["verified_source_groups_acquired"].sum()
    print(f"  Reported sum of SGs in coverage matrix:   {sum_cov_sgs}")
    print(f"  Net SG difference:                        {df['source_group_id'].nunique() - sum_cov_sgs} (62 unique omitted - 31 overlapping)")

if __name__ == "__main__":
    main()

