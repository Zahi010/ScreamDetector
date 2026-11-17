#!/usr/bin/env python3
"""
STAGE 8.9.62 — Phase C1: Development Dataset Audit and Manifest Creation
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import csv
import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE60_DIR = BACKEND_DIR / "research" / "stage_8_9_60"
STAGE61_DIR = BACKEND_DIR / "research" / "stage_8_9_61"
STAGE62_DIR = BACKEND_DIR / "research" / "stage_8_9_62"

def sha256_file(path_str: str) -> str:
    sha = hashlib.sha256()
    with open(path_str, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()

def main():
    # Load Stage 60 sealed cohort to ensure strict isolation
    with open(STAGE60_DIR / "future_evaluation_manifest.json") as f:
        sealed = json.load(f)
    sealed_rec_ids = set(r["recording_id"] for r in sealed["recordings"])
    sealed_sg_ids = set(r["source_group_id"] for r in sealed["recordings"])
    sealed_creators = set(r["uploader_or_creator"] for r in sealed["recordings"])

    # Load duplicate relationships to verify parent isolation
    dup_rows = []
    with open(STAGE60_DIR / "duplicate_and_excerpt_relationships.csv") as f:
        reader = csv.DictReader(f)
        for r in reader:
            dup_rows.append(r)

    sealed_parent_ids = set()
    for r in dup_rows:
        clips = [c.strip() for c in r["clip_ids"].split(";")]
        if any(c in sealed_rec_ids for c in clips):
            sealed_parent_ids.add(r["parent_recording_id"])

    # Load development cohort from Stage 61
    dev_csv_path = STAGE61_DIR / "rolling_window_development_manifest.csv"
    dev_rows = []
    with open(dev_csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            dev_rows.append(r)

    print(f"Loaded {len(dev_rows)} candidate development recordings.")

    # Verification checks
    dev_rec_ids = set(r["recording_id"] for r in dev_rows)
    dev_sg_ids = set(r["source_group_id"] for r in dev_rows)
    dev_creators = set(r["uploader_or_creator"] for r in dev_rows)

    # 1. No overlap with sealed cohort recordings
    overlap_recs = dev_rec_ids & sealed_rec_ids
    assert len(overlap_recs) == 0, f"Recording overlap detected: {overlap_recs}"

    # 2. No overlap with sealed cohort source groups
    overlap_sgs = dev_sg_ids & sealed_sg_ids
    assert len(overlap_sgs) == 0, f"Source group overlap detected: {overlap_sgs}"

    # 3. No overlap with parent recordings
    dev_parent_ids = set()
    for r in dup_rows:
        clips = [c.strip() for c in r["clip_ids"].split(";")]
        if any(c in dev_rec_ids for c in clips):
            dev_parent_ids.add(r["parent_recording_id"])

    overlap_parents = dev_parent_ids & sealed_parent_ids
    assert len(overlap_parents) == 0, f"Parent recording overlap detected: {overlap_parents}"

    # 4. Check for duplicate audio / PCM hashes
    pcm_hashes = [r["pcm_sha256"] for r in dev_rows]
    assert len(pcm_hashes) == len(set(pcm_hashes)), "Duplicate PCM hashes detected in development set!"

    # Compile dataset statistics
    n_total = len(dev_rows)
    n_pos = sum(1 for r in dev_rows if int(r["binary_label"]) == 1)
    n_neg = sum(1 for r in dev_rows if int(r["binary_label"]) == 0)
    n_sust = sum(1 for r in dev_rows if int(r["binary_label"]) == 1 and float(r["duration_seconds"]) >= 1.0)
    n_short = sum(1 for r in dev_rows if int(r["binary_label"]) == 1 and float(r["duration_seconds"]) < 1.0)
    n_low_int = sum(1 for r in dev_rows if r["subcategory"] == "low_intensity_scream")
    n_crowd_mask = sum(1 for r in dev_rows if r["subcategory"] == "crowd_masked_scream")
    n_unique_sgs = len(dev_sg_ids)
    n_unique_creators = len(dev_creators)

    # Write stage_62_development_manifest.csv
    out_dev_manifest = STAGE62_DIR / "stage_62_development_manifest.csv"
    with open(out_dev_manifest, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(dev_rows[0].keys()))
        writer.writeheader()
        writer.writerows(dev_rows)

    manifest_sha256 = sha256_file(str(out_dev_manifest))
    print(f"Wrote {out_dev_manifest} (SHA-256: {manifest_sha256})")

    summary = {
        "manifest_path": "backend/research/stage_8_9_62/stage_62_development_manifest.csv",
        "sha256": manifest_sha256,
        "total_recordings": n_total,
        "positive_recordings": n_pos,
        "negative_recordings": n_neg,
        "sustained_positive_recordings": n_sust,
        "short_positive_recordings": n_short,
        "low_intensity_positive_recordings": n_low_int,
        "crowd_masked_positive_recordings": n_crowd_mask,
        "unique_source_groups": n_unique_sgs,
        "unique_creators": n_unique_creators,
        "short_scream_evidence_status": "INSUFFICIENT_DEVELOPMENT_EVIDENCE" if n_short < 10 else "SUFFICIENT_EVIDENCE",
        "sealed_cohort_recording_overlap": 0,
        "sealed_cohort_source_group_overlap": 0,
        "sealed_cohort_parent_excerpt_overlap": 0
    }

    out_summary_json = STAGE62_DIR / "development_dataset_audit.json"
    with open(out_summary_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "="*80)
    print("PHASE C1: DEVELOPMENT DATASET AUDIT SUMMARY")
    print("="*80)
    for k, v in summary.items():
        print(f"  {k:<42}: {v}")

if __name__ == "__main__":
    main()

