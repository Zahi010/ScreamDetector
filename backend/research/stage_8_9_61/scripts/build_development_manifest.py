#!/usr/bin/env python3
"""
STAGE 8.9.61 — Build Rolling Window Development Manifest Script
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import hashlib
import json
import os
import pandas as pd
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
STAGE60_DIR = REPO_ROOT / "backend" / "research" / "stage_8_9_60"
STAGE61_DIR = REPO_ROOT / "backend" / "research" / "stage_8_9_61"

def sha256_file(path_str: str) -> str:
    sha = hashlib.sha256()
    with open(path_str, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()

def main():
    print("Executing Phase A2: Building Rolling-Window Development Manifest...")
    
    # 1. Load acquisition manifest
    df_acq = pd.read_csv(STAGE60_DIR / "acquisition_manifest.csv")
    print(f"Total Stage 8.9.60 acquired recordings: {len(df_acq)}")
    
    # 2. Load sealed evaluation cohort to exclude it completely
    with open(STAGE60_DIR / "future_evaluation_manifest.json") as f:
        sealed_data = json.load(f)
    sealed_recs = set(r["recording_id"] for r in sealed_data["recordings"])
    sealed_sgs = set(r["source_group_id"] for r in sealed_data["recordings"])
    print(f"Sealed cohort recordings to exclude: {len(sealed_recs)}")
    print(f"Sealed cohort source groups to exclude: {len(sealed_sgs)}")
    
    # 3. Filter out all recordings in sealed cohort
    df_non_sealed = df_acq[~df_acq["recording_id"].isin(sealed_recs)].copy()
    print(f"Remaining non-sealed recordings: {len(df_non_sealed)}")
    
    # 4. Strict source-group boundary preservation:
    # Exclude any recording sharing a source group with the sealed cohort
    df_eligible = df_non_sealed[~df_non_sealed["source_group_id"].isin(sealed_sgs)].copy()
    quarantined_shared_sg = df_non_sealed[df_non_sealed["source_group_id"].isin(sealed_sgs)]
    
    print(f"Quarantined shared-source-group recordings: {len(quarantined_shared_sg)}")
    print(f"Eligible development recordings: {len(df_eligible)}")
    print(f"Eligible unique source groups: {df_eligible['source_group_id'].nunique()}")
    print(f"Eligible unique creators: {df_eligible['uploader_or_creator'].nunique()}")
    
    # Check eligibility rules
    assert (df_eligible["review_status"] == "APPROVED").all(), "All dev recordings must have approved review status!"
    assert (df_eligible["license"].notna()).all(), "All dev recordings must have verified license!"
    assert len(set(df_eligible["recording_id"]) & sealed_recs) == 0, "Zero recording overlap with sealed cohort!"
    assert len(set(df_eligible["source_group_id"]) & sealed_sgs) == 0, "Zero source group overlap with sealed cohort!"
    
    # Save development manifest
    out_csv = STAGE61_DIR / "rolling_window_development_manifest.csv"
    df_eligible.to_csv(out_csv, index=False)
    dev_sha = sha256_file(str(out_csv))
    print(f"\nSaved development manifest to: {out_csv}")
    print(f"Development manifest SHA-256: {dev_sha}")
    
    # Save metadata summary
    summary = {
        "manifest_file": "rolling_window_development_manifest.csv",
        "sha256": dev_sha,
        "total_recordings": len(df_eligible),
        "positive_recordings": int((df_eligible["binary_label"] == 1).sum()),
        "negative_recordings": int((df_eligible["binary_label"] == 0).sum()),
        "unique_source_groups": int(df_eligible["source_group_id"].nunique()),
        "unique_creators": int(df_eligible["uploader_or_creator"].nunique()),
        "category_distribution": df_eligible["target_category"].value_counts().to_dict(),
        "subcategory_distribution": df_eligible["subcategory"].value_counts().to_dict(),
        "source_group_overlap_with_sealed": 0,
        "recording_overlap_with_sealed": 0
    }
    with open(STAGE61_DIR / "development_manifest_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("Saved development manifest summary JSON.")

if __name__ == "__main__":
    main()

