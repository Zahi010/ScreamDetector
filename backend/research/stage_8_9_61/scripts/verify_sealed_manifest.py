#!/usr/bin/env python3
"""
STAGE 8.9.61 — Verify Sealed Manifest Script
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import hashlib
import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
STAGE60_DIR = REPO_ROOT / "backend" / "research" / "stage_8_9_60"
STAGE61_DIR = REPO_ROOT / "backend" / "research" / "stage_8_9_61"

EXPECTED_SEALED_HASH = "9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd"

def sha256_file(path_str: str) -> str:
    sha = hashlib.sha256()
    with open(path_str, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()

def main():
    print("Executing Sealed Evaluation Manifest Access & Integrity Verification...")
    manifest_p = STAGE60_DIR / "future_evaluation_manifest.json"
    seal_p = STAGE60_DIR / "future_evaluation_manifest.sha256"
    
    assert manifest_p.exists(), f"Sealed manifest missing at {manifest_p}"
    assert seal_p.exists(), f"Seal file missing at {seal_p}"
    
    # 1. Compute hash of manifest
    actual_hash = sha256_file(str(manifest_p))
    print(f"Manifest path:   {manifest_p}")
    print(f"Computed SHA256: {actual_hash}")
    print(f"Expected SHA256: {EXPECTED_SEALED_HASH}")
    
    with open(seal_p) as f:
        seal_text = f.read().strip()
    print(f"Seal file text:  {seal_text}")
    
    assert actual_hash == EXPECTED_SEALED_HASH, "MANIFEST HASH MISMATCH!"
    assert EXPECTED_SEALED_HASH in seal_text, "SEAL FILE CONTENT MISMATCH!"
    
    # 2. Inspect manifest structure without exposing labels to development
    with open(manifest_p) as f:
        data = json.load(f)
        
    print(f"\nManifest Metadata:")
    print(f"  Cohort Name:           {data.get('cohort_name')}")
    print(f"  Sealing Date UTC:      {data.get('sealing_date_utc')}")
    print(f"  Cohort Status:         {data.get('cohort_status')}")
    print(f"  Total Recordings:      {data.get('total_recordings')}")
    print(f"  Positive Recordings:   {data.get('positive_recordings')}")
    print(f"  Negative Recordings:   {data.get('negative_recordings')}")
    print(f"  Unique Source Groups:  {data.get('unique_source_groups')}")
    print(f"  Unique Creators:       {data.get('unique_creators')}")
    
    assert data.get("total_recordings") == 700
    assert data.get("positive_recordings") == 200
    assert data.get("negative_recordings") == 500
    assert data.get("unique_source_groups") == 453
    assert len(data.get("recordings", [])) == 700
    
    print("\nIntegrity Verification: PASSED. Sealed manifest is 100% verified and immutable.")

if __name__ == "__main__":
    main()

