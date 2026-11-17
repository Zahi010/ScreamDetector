"""Phase 1: Baseline and Filesystem Inventory Audit for Stage 8.9.30."""

import hashlib
import json
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
import soundfile as sf

STAGE_30_DIR = Path("backend/research/stage_8_9_30")
STAGE_30_1_DIR = Path("backend/research/stage_8_9_30_1")
BACKEND_DIR = Path("backend")


def run_phase1_inventory() -> Dict[str, Any]:
    print("=" * 70)
    print("PHASE 1: BASELINE & FILESYSTEM INVENTORY AUDIT OF STAGE 8.9.30")
    print("=" * 70)

    # 1. Enumerate all files in stage_8_9_30
    all_files = list(STAGE_30_DIR.rglob("*"))
    files_only = [f for f in all_files if f.is_file()]
    print(f"Total filesystem objects: {len(all_files)}")
    print(f"Total files: {len(files_only)}")

    zero_byte_files = [str(f.relative_to(STAGE_30_DIR)) for f in files_only if f.stat().st_size == 0]
    print(f"Zero-byte files count: {len(zero_byte_files)}")

    # 2. Key Deliverable Manifests Check
    key_deliverables = [
        "STAGE_8_9_30_COMPLETION_REPORT.md",
        "STAGE_PROGRESS.md",
        "recording_manifest.csv",
        "source_group_manifest.csv",
        "dataset_manifest_lock.json",
        "source_registry.csv",
        "source_license_audit.csv",
        "acquisition_log.csv",
        "failed_downloads.csv",
        "audio_quality_report.csv",
        "duration_distribution.csv",
        "acoustic_profile_report.csv",
        "duplicate_audit.csv",
        "contamination_audit.json",
        "frozen_baseline_evaluation.csv",
        "subgroup_metrics.csv",
        "production_integrity_verification.json",
    ]

    deliverable_status = {}
    for name in key_deliverables:
        # Check both root and subdirectories
        matches = list(STAGE_30_DIR.rglob(name))
        deliverable_status[name] = {
            "exists": len(matches) > 0,
            "locations": [str(m.relative_to(STAGE_30_DIR)) for m in matches],
            "sizes_bytes": [m.stat().st_size for m in matches],
        }
        status_str = "FOUND" if len(matches) > 0 else "MISSING"
        print(f"  [{status_str}] {name} ({len(matches)} occurrences)")

    # 3. Audit recording_manifest.csv
    rec_manifest_path = STAGE_30_DIR / "metadata" / "recording_manifest.csv"
    if not rec_manifest_path.exists():
        rec_manifest_path = STAGE_30_DIR / "recording_manifest.csv"

    rec_df = pd.read_csv(rec_manifest_path)
    total_manifest_rows = len(rec_df)
    unique_rec_ids = int(rec_df["recording_id"].nunique())
    unique_orig_ids = int(rec_df["original_source_id"].nunique())
    unique_source_groups = int(rec_df["source_group_id"].nunique())

    print(f"\nManifest Row Counts:")
    print(f"  Total recording rows: {total_manifest_rows}")
    print(f"  Unique recording_ids: {unique_rec_ids}")
    print(f"  Unique original_source_ids: {unique_orig_ids}")
    print(f"  Unique source_group_ids: {unique_source_groups}")

    # Check for duplicate recording IDs or missing required fields
    duplicate_rec_ids = rec_df[rec_df.duplicated(subset=["recording_id"], keep=False)]["recording_id"].tolist()
    null_fields = rec_df.isnull().sum().to_dict()

    # 4. Processed audio files audit
    missing_processed = []
    corrupted_processed = []
    audio_durations = []
    audio_sample_rates = []
    audio_channels = []

    for idx, r in rec_df.iterrows():
        p_path = BACKEND_DIR / r["local_processed_path"]
        if not p_path.exists():
            missing_processed.append(r["recording_id"])
        else:
            try:
                info = sf.info(str(p_path))
                audio_durations.append(info.duration)
                audio_sample_rates.append(info.samplerate)
                audio_channels.append(info.channels)
            except Exception as e:
                corrupted_processed.append({"recording_id": r["recording_id"], "error": str(e)})

    print(f"\nProcessed Audio File Audit:")
    print(f"  Readable audio files: {len(audio_durations)} / {total_manifest_rows}")
    print(f"  Missing files: {len(missing_processed)}")
    print(f"  Corrupted files: {len(corrupted_processed)}")
    if audio_sample_rates:
        print(f"  Sample rates present: {sorted(list(set(audio_sample_rates)))}")
        print(f"  Channel counts present: {sorted(list(set(audio_channels)))}")
        print(f"  Duration range: {min(audio_durations):.3f}s to {max(audio_durations):.3f}s")

    # 5. Raw audio files audit
    raw_files = [f for f in (STAGE_30_DIR / "raw").rglob("*") if f.is_file()]
    print(f"\nRaw Audio Files:")
    print(f"  Total raw files on disk: {len(raw_files)}")

    # 6. Prediction audit
    eval_csv = STAGE_30_DIR / "evaluation" / "frozen_baseline_evaluation.csv"
    if not eval_csv.exists():
        eval_csv = STAGE_30_DIR / "frozen_baseline_evaluation.csv"
    eval_df = pd.read_csv(eval_csv)
    eval_matches_manifest = set(eval_df["recording_id"]) == set(rec_df["recording_id"])
    print(f"\nPrediction-Level Output Check:")
    print(f"  Evaluation rows: {len(eval_df)}")
    print(f"  1-to-1 match with recording manifest: {eval_matches_manifest}")

    # 7. Check manifest lock
    lock_json = STAGE_30_DIR / "dataset_manifest_lock.json"
    with open(lock_json, "r", encoding="utf-8") as f:
        lock_data = json.load(f)
    actual_manifest_sha = hashlib.sha256(rec_manifest_path.read_bytes()).hexdigest()
    lock_match = (lock_data.get("manifest_sha256") == actual_manifest_sha)
    print(f"\nManifest Lock Verification:")
    print(f"  Recorded SHA-256: {lock_data.get('manifest_sha256')}")
    print(f"  Actual Manifest SHA-256: {actual_manifest_sha}")
    print(f"  Cryptographic Match: {lock_match}")

    inventory_report = {
        "total_files": len(files_only),
        "zero_byte_files": zero_byte_files,
        "deliverable_status": deliverable_status,
        "total_manifest_recordings": total_manifest_rows,
        "unique_recording_ids": unique_rec_ids,
        "unique_original_source_ids": unique_orig_ids,
        "unique_source_groups": unique_source_groups,
        "duplicate_recording_ids": duplicate_rec_ids,
        "null_fields": null_fields,
        "readable_audio_count": len(audio_durations),
        "missing_audio_count": len(missing_processed),
        "corrupted_audio_count": len(corrupted_processed),
        "sample_rates": sorted(list(set(audio_sample_rates))),
        "channels": sorted(list(set(audio_channels))),
        "min_duration_sec": round(min(audio_durations), 3) if audio_durations else None,
        "max_duration_sec": round(max(audio_durations), 3) if audio_durations else None,
        "raw_audio_count": len(raw_files),
        "evaluation_rows": len(eval_df),
        "eval_matches_manifest": eval_matches_manifest,
        "manifest_lock_verified": lock_match,
    }

    out_file = STAGE_30_1_DIR / "baseline_inventory.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(inventory_report, f, indent=2)
    print(f"\n[Generated] {out_file}")

    return inventory_report


if __name__ == "__main__":
    run_phase1_inventory()
