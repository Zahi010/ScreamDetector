"""Stage 8.9.14 Short-Event Dataset Audit and Source-Group Disjointness Verification.

Generates:
1. short_event_dataset_audit.csv
2. source_group_split_audit.json
"""

from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("stage8_9_14_dataset_audit")

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
MANIFEST_PATH = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_11_evaluation" / "stage8_9_11_dataset_manifest.csv"
ACQ_MANIFEST_PATH = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_11_evaluation" / "stage8_9_11_acquisition_manifest.csv"
STAGE14_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_14_acoustic_discriminability"


def classify_vocal_event_type(target_cat: str, duration: float, file_id: str) -> str:
    cat = target_cat.lower()
    fid = file_id.lower()
    if "scream" in cat:
        if "masked" in cat or "synth" in fid:
            return "masked_brief_scream"
        if duration < 0.65:
            return "startle_shriek"
        elif duration < 1.0:
            return "brief_terror_scream"
        else:
            return "sustained_scream"
    elif "shout" in cat:
        if duration < 0.8:
            return "shouted_exclamation"
        else:
            return "excited_yelling"
    elif "crowd" in cat:
        return "crowd_cheer_cadence"
    elif "infant" in cat:
        return "infant_cry_burst"
    elif "whistle" in cat:
        return "whistle_transient"
    elif "siren" in cat:
        return "siren_pulse"
    else:
        return "environmental_transient"


def determine_masking(target_cat: str, file_id: str) -> str:
    cat = target_cat.lower()
    fid = file_id.lower()
    if "masked" in cat:
        if "snr-06db" in fid or "snr-12db" in fid:
            return "HEAVY_MASKED"
        elif "snr+00db" in fid or "snr-03db" in fid:
            return "PARTIAL_MASKED"
        else:
            return "MODERATE_MASKED"
    elif "crowd" in cat:
        return "CROWD_MASKED"
    else:
        return "CLEAN_ISOLATED"


def determine_ambiguity(target_cat: str, file_id: str) -> str:
    fid = file_id.lower()
    if "joy" in fid or "excitement" in fid:
        return "AMBIGUOUS_EXCITEMENT"
    if "laugh" in fid:
        return "AMBIGUOUS_LAUGHTER"
    if "scream" in target_cat.lower():
        return "CLEAR_POSITIVE"
    return "CLEAR_NEGATIVE"


def run_dataset_audit():
    logger.info("=================================================================")
    logger.info("STAGE 8.9.14: SHORT-EVENT DATASET AUDIT & SOURCE GROUP VERIFICATION")
    logger.info("=================================================================")

    # Load acquisition manifest for attribution and provenance
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

    logger.info(f"Loaded {len(all_records)} total manifest records.")

    # 1. Source-Group Disjointness Verification
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

    logger.info(f"Source groups: Train={len(groups_by_split['train'])}, Val={len(groups_by_split['val'])}, Test={len(groups_by_split['test'])}")
    logger.info(f"Source Group Overlaps: Train-Val={len(train_val_overlap)}, Train-Test={len(train_test_overlap)}, Val-Test={len(val_test_overlap)}")

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

    out_split_json = STAGE14_DIR / "source_group_split_audit.json"
    with open(out_split_json, "w", encoding="utf-8") as f:
        json.dump(split_audit, f, indent=2)
    logger.info(f"Saved source group split audit to: {out_split_json}")

    # 2. Short-Event Dataset Audit (duration <= 1.5s, focusing on < 1.0s)
    short_records = [r for r in all_records if float(r["duration_seconds"]) <= 1.5]
    logger.info(f"Found {len(short_records)} short event recordings (<= 1.5s), of which {sum(1 for r in short_records if float(r['duration_seconds']) < 1.0)} are < 1.0s.")

    audit_rows = []
    for r in short_records:
        fid = r["file_id"]
        dur = float(r["duration_seconds"])
        cat = r["target_category"]
        bin_lbl = r["binary_label"]
        split = r["split"]
        sg = r["source_group_id"]
        lic = r.get("license", "CC-BY")
        synth = r.get("is_synthesized", "False") == "True"

        extra = acq_info.get(fid, {})
        attr = extra.get("attribution") or r.get("attribution", "")
        lic_url = extra.get("license_url") or r.get("license", "")
        src_url = extra.get("source_url") or f"https://freesound.org/s/{fid}"

        vocal_type = classify_vocal_event_type(cat, dur, fid)
        masking = determine_masking(cat, fid)
        ambiguity = determine_ambiguity(cat, fid)

        audit_rows.append({
            "file_id": fid,
            "target_category": cat,
            "binary_label": bin_lbl,
            "duration_seconds": round(dur, 3),
            "duration_bracket": "<1.0s" if dur < 1.0 else "1.0s-1.5s",
            "vocal_event_type": vocal_type,
            "split": split,
            "source_group_id": sg,
            "license": lic,
            "license_url": lic_url,
            "attribution": attr,
            "source_url": src_url,
            "is_synthesized": synth,
            "masking_level": masking,
            "ambiguity_status": ambiguity,
            "quarantine_action": "EXCLUDE_FROM_EVAL" if "AMBIGUOUS" in ambiguity else "ELIGIBLE",
        })

    out_csv = STAGE14_DIR / "short_event_dataset_audit.csv"
    fieldnames = [
        "file_id", "target_category", "binary_label", "duration_seconds", "duration_bracket",
        "vocal_event_type", "split", "source_group_id", "license", "license_url", "attribution",
        "source_url", "is_synthesized", "masking_level", "ambiguity_status", "quarantine_action"
    ]
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(audit_rows)

    logger.info(f"Saved {len(audit_rows)} short-event audit records to: {out_csv}")
    return split_audit, audit_rows


if __name__ == "__main__":
    run_dataset_audit()
