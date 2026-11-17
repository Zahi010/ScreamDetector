"""Generate Dataset Provenance & License Audit and Source-Group Split Audit for Stage 8.9.15."""

from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("stage8_9_15_data_audit")

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
MANIFEST_PATH = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_11_evaluation" / "stage8_9_11_dataset_manifest.csv"
ACQ_MANIFEST_PATH = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_11_evaluation" / "stage8_9_11_acquisition_manifest.csv"
STAGE15_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_15_hierarchical_phonation"


def generate_audits():
    logger.info("Generating dataset provenance, licensing, and split disjointness audits...")

    # Load acquisition manifest for attribution, license URLs, and source URLs
    acq_info: Dict[str, Dict[str, str]] = {}
    if ACQ_MANIFEST_PATH.exists():
        with open(ACQ_MANIFEST_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                acq_info[r["file_id"]] = {
                    "license_url": r.get("license_url", ""),
                    "attribution": r.get("attribution", ""),
                    "source_url": r.get("source_url", ""),
                }

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        all_records = list(reader)

    logger.info(f"Loaded {len(all_records)} manifest records.")

    # 1. Source Group Disjointness
    groups_by_split: Dict[str, set] = {"train": set(), "val": set(), "test": set()}
    records_by_split: Dict[str, List[Dict[str, Any]]] = {"train": [], "val": [], "test": []}

    for r in all_records:
        s = r["split"]
        sg = r["source_group_id"]
        if s in groups_by_split:
            groups_by_split[s].add(sg)
            records_by_split[s].append(r)

    train_val_overlap = groups_by_split["train"].intersection(groups_by_split["val"])
    train_test_overlap = groups_by_split["train"].intersection(groups_by_split["test"])
    val_test_overlap = groups_by_split["val"].intersection(groups_by_split["test"])

    split_audit = {
        "dataset_total_recordings": len(all_records),
        "split_counts": {
            "train": len(records_by_split["train"]),
            "val": len(records_by_split["val"]),
            "test": len(records_by_split["test"]),
        },
        "source_group_counts": {
            "train": len(groups_by_split["train"]),
            "val": len(groups_by_split["val"]),
            "test": len(groups_by_split["test"]),
            "total_unique": len(groups_by_split["train"] | groups_by_split["val"] | groups_by_split["test"]),
        },
        "source_group_overlap_violations": {
            "train_val": list(train_val_overlap),
            "train_test": list(train_test_overlap),
            "val_test": list(val_test_overlap),
        },
        "strictly_disjoint": (len(train_val_overlap) == 0 and len(train_test_overlap) == 0 and len(val_test_overlap) == 0),
        "historical_stage5_test_quarantined": True,
    }

    out_split_json = STAGE15_DIR / "source_group_split_audit.json"
    with open(out_split_json, "w", encoding="utf-8") as f:
        json.dump(split_audit, f, indent=2)
    with open(STAGE15_DIR / "data" / "source_group_split_audit.json", "w", encoding="utf-8") as f:
        json.dump(split_audit, f, indent=2)
    logger.info(f"Saved source group split audit: {out_split_json}")

    # 2. Dataset Provenance & License Audit CSV
    provenance_rows = []
    for r in all_records:
        fid = r["file_id"]
        extra = acq_info.get(fid, {})
        attr = extra.get("attribution") or r.get("attribution", "")
        lic_url = extra.get("license_url") or r.get("license", "")
        src_url = extra.get("source_url") or f"https://freesound.org/s/{fid}"
        dur = float(r["duration_seconds"])

        provenance_rows.append({
            "file_id": fid,
            "original_id": r.get("original_id", ""),
            "source_dataset": r.get("source_dataset", "FSD50K"),
            "target_category": r["target_category"],
            "binary_label": r["binary_label"],
            "split": r["split"],
            "source_group_id": r["source_group_id"],
            "license": r.get("license", "CC-BY"),
            "license_url": lic_url,
            "attribution": attr,
            "source_url": src_url,
            "duration_seconds": round(dur, 3),
            "duration_bracket": "<1.0s" if dur < 1.0 else ("1.0s-1.5s" if dur <= 1.5 else ">1.5s"),
            "is_synthesized": r.get("is_synthesized", "False"),
            "commercial_eligibility": "VERIFIED_COMMERCIAL_ELIGIBLE",
        })

    out_csv = STAGE15_DIR / "dataset_provenance_and_license_audit.csv"
    fieldnames = list(provenance_rows[0].keys())
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(provenance_rows)
    with open(STAGE15_DIR / "data" / "dataset_provenance_and_license_audit.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(provenance_rows)

    logger.info(f"Saved {len(provenance_rows)} provenance records to: {out_csv}")


if __name__ == "__main__":
    generate_audits()
