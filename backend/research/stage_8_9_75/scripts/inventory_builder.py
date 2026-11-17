# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
Dataset Inventory Builder & Lineage Auditor for Stage 8.9.75.
Analyzes all historical manifests, tracks source groups, parent lineages,
exposure classifications, license eligibility, and detects duplicates.
"""

import json
import os
import hashlib
import pandas as pd
import numpy as np

def build_inventory():
    # If script is in festival-scream-detector/backend/research/stage_8_9_75/scripts/
    # dirname is scripts, .. is stage_8_9_75, .. is research, .. is backend, .. is festival-scream-detector
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    print(f"Project root: {project_root}")

    # Track all records by unique recording_id / file_id
    records = []
    seen_ids = set()

    # 1. Core Dataset Manifest (backend/dataset/manifests/dataset_manifest.json)
    core_manifest_path = os.path.join(project_root, "backend", "dataset", "manifests", "dataset_manifest.json")
    if os.path.exists(core_manifest_path):
        with open(core_manifest_path, "r", encoding="utf-8") as f:
            core_data = json.load(f)
        print(f"Loaded core dataset manifest: {len(core_data)} items")
        for item in core_data:
            rec_id = item.get("file_id")
            if not rec_id:
                continue
            seen_ids.add(rec_id)
            meta = {}
            if "metadata_json" in item and item["metadata_json"]:
                try:
                    meta = json.loads(item["metadata_json"]) if isinstance(item["metadata_json"], str) else item["metadata_json"]
                except Exception:
                    pass

            license_str = meta.get("license", "CC_UNKNOWN")
            creator = meta.get("username", meta.get("creator", "unknown_creator"))
            parent_id = meta.get("parent_id", "")
            is_synth = 1 if "synthetic" in rec_id.lower() or meta.get("is_synthetic", False) else 0

            # Map split / exposure
            official_split = item.get("official_split", "train")
            exposed_status = "EXPOSED_DEVELOPMENT_COHORT"

            bin_raw = item.get("binary_label", 0)
            if isinstance(bin_raw, str):
                bin_val = 1 if bin_raw.lower() in ["scream", "1", "positive", "true"] else 0
            else:
                bin_val = 1 if bin_raw in [1, True] else 0

            records.append({
                "recording_id": rec_id,
                "source_dataset": item.get("dataset_name", "core_dataset"),
                "source_group_id": item.get("source_group_id", f"sg_{creator}"),
                "creator_uploader": creator,
                "license": license_str,
                "primary_category": item.get("original_class", "unknown"),
                "binary_label": bin_val,
                "duration_seconds": float(item.get("duration_seconds", 0.0)),
                "is_synthetic": is_synth,
                "parent_recording_id": parent_id,
                "exposed_cohort_status": exposed_status,
                "sha256_hash": item.get("sha256_hash", ""),
                "pcm_sha256": item.get("pcm_sha256", ""),
                "relative_path": item.get("relative_path", "")
            })

    # 2. V2 / V3 Dataset Manifest (backend/experiments/v2_hard_negative_training/manifests/dataset_manifest_v2.json)
    v2_manifest_path = os.path.join(project_root, "backend", "experiments", "v2_hard_negative_training", "manifests", "dataset_manifest_v2.json")
    if os.path.exists(v2_manifest_path):
        with open(v2_manifest_path, "r", encoding="utf-8") as f:
            v2_data = json.load(f)
        print(f"Loaded v2 manifest: {len(v2_data)} items")
        for item in v2_data:
            rec_id = item.get("file_id")
            if not rec_id:
                continue
            if rec_id in seen_ids:
                # Update existing record if needed
                continue
            seen_ids.add(rec_id)

            is_synth = 1 if item.get("is_synthesized", False) or "synthetic" in rec_id.lower() else 0
            parent_id = item.get("original_recording_id", "")
            creator = item.get("creator", "unknown_creator")

            bin_raw = item.get("binary_label", 0)
            if isinstance(bin_raw, str):
                bin_val = 1 if bin_raw.lower() in ["scream", "1", "positive", "true"] else 0
            else:
                bin_val = 1 if bin_raw in [1, True] else 0

            records.append({
                "recording_id": rec_id,
                "source_dataset": item.get("source_dataset", "v2_hard_negatives"),
                "source_group_id": item.get("source_group_id", f"sg_{creator}"),
                "creator_uploader": creator,
                "license": item.get("license", "CC_UNKNOWN"),
                "primary_category": item.get("target_category", "unknown"),
                "binary_label": bin_val,
                "duration_seconds": float(item.get("duration_seconds", 0.0)),
                "is_synthetic": is_synth,
                "parent_recording_id": parent_id,
                "exposed_cohort_status": "EXPOSED_DEVELOPMENT_COHORT",
                "sha256_hash": item.get("sha256_hash", ""),
                "pcm_sha256": item.get("pcm_sha256", ""),
                "relative_path": item.get("source_path", item.get("workspace_audio_path", ""))
            })

    # 3. Stage 60 Future Evaluation Manifest (backend/research/stage_8_9_60/future_evaluation_manifest.json)
    st60_manifest_path = os.path.join(project_root, "backend", "research", "stage_8_9_60", "future_evaluation_manifest.json")
    if os.path.exists(st60_manifest_path):
        with open(st60_manifest_path, "r", encoding="utf-8") as f:
            st60_data = json.load(f)
        recs = st60_data.get("recordings", [])
        print(f"Loaded Stage 60 manifest: {len(recs)} items")
        for item in recs:
            rec_id = item.get("recording_id")
            if not rec_id:
                continue
            # Check if this exact ID or content was already seen
            is_new = rec_id not in seen_ids
            seen_ids.add(rec_id)

            bin_raw = item.get("binary_label", 0)
            if isinstance(bin_raw, str):
                bin_val = 1 if bin_raw.lower() in ["scream", "1", "positive", "true"] else 0
            else:
                bin_val = 1 if bin_raw in [1, True] else 0

            records.append({
                "recording_id": rec_id,
                "source_dataset": "stage_8_9_60_evaluation_cohort",
                "source_group_id": item.get("source_group_id", f"sg_{item.get('uploader_or_creator', 'unknown')}"),
                "creator_uploader": item.get("uploader_or_creator", "unknown"),
                "license": item.get("license", "CC_UNKNOWN"),
                "primary_category": item.get("primary_category", "unknown"),
                "binary_label": bin_val,
                "duration_seconds": float(item.get("duration_seconds", 0.0)),
                "is_synthetic": 1 if "synthetic" in rec_id.lower() or item.get("is_synthetic", False) else 0,
                "parent_recording_id": item.get("parent_recording_id", ""),
                "exposed_cohort_status": "HISTORICALLY_EXPOSED_COHORT",
                "sha256_hash": item.get("sha256_hash", ""),
                "pcm_sha256": item.get("pcm_sha256", ""),
                "relative_path": item.get("file_path", "")
            })

    # 4. Stage 64 Short Scream Manifest (backend/research/stage_8_9_64/stage_64_short_scream_manifest.csv)
    st64_path = os.path.join(project_root, "backend", "research", "stage_8_9_64", "stage_64_short_scream_manifest.csv")
    if os.path.exists(st64_path):
        st64_df = pd.read_csv(st64_path)
        print(f"Loaded Stage 64 manifest: {len(st64_df)} items")
        for _, row in st64_df.iterrows():
            rec_id = str(row.get("recording_id", ""))
            if not rec_id or rec_id in seen_ids:
                continue
            seen_ids.add(rec_id)
            creator = str(row.get("uploader_creator", "unknown"))
            sg_id = str(row.get("source_group_id", f"sg_{creator}"))
            records.append({
                "recording_id": rec_id,
                "source_dataset": "stage_8_9_64_short_screams",
                "source_group_id": sg_id,
                "creator_uploader": creator,
                "license": str(row.get("license", "CC_UNKNOWN")),
                "primary_category": "short_scream",
                "binary_label": 1,
                "duration_seconds": float(row.get("duration_seconds", 0.0)) if pd.notnull(row.get("duration_seconds")) else 0.5,
                "is_synthetic": 1 if "synthetic" in rec_id.lower() else 0,
                "parent_recording_id": str(row.get("original_file_id", "")),
                "exposed_cohort_status": "EXPOSED_DIAGNOSTIC_COHORT",
                "sha256_hash": str(row.get("sha256_hash", "")),
                "pcm_sha256": str(row.get("pcm_sha256", "")),
                "relative_path": str(row.get("file_path", ""))
            })

    df = pd.DataFrame(records)
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    out_csv = os.path.join(out_dir, "dataset_inventory.csv")
    df.to_csv(out_csv, index=False)
    print(f"Wrote dataset_inventory.csv with {len(df)} total records to {out_csv}")

    # Generate summary stats
    print("\n--- Summary Statistics ---")
    print(f"Total recordings cataloged: {len(df)}")
    print(f"Unique source groups: {df['source_group_id'].nunique()}")
    print(f"Unique uploaders/creators: {df['creator_uploader'].nunique()}")
    print("\nBreakdown by Exposed Cohort Status:")
    print(df["exposed_cohort_status"].value_counts())
    print("\nBreakdown by Binary Label:")
    print(df["binary_label"].value_counts())
    print("\nBreakdown by License:")
    print(df["license"].value_counts().head(10))
    print("\nTop 10 Source Groups by Recording Count:")
    print(df["source_group_id"].value_counts().head(10))

    return df

if __name__ == "__main__":
    build_inventory()
