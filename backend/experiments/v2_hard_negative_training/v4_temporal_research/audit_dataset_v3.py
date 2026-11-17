"""Audit Dataset v3 composition, source groups, and licensing metadata (Stage 8.9.8).

Verifies:
1. Exact clip counts and source groups per split.
2. Source-group disjointness (0 leakage).
3. Zero Stage 5 historical test overlap in Train/Val.
4. Exact-hash deduplication and limits.
5. Licence metadata breakdown and commercial compatibility.
"""

from __future__ import annotations

import csv
import json
import logging
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Set

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent
MANIFEST_PATH = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "manifests" / "dataset_manifest_v3.json"
SPLIT_PATH = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "splits" / "split_manifest_v3.json"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("audit_dataset_v3")


def main():
    logger.info("Auditing Dataset v3 for Stage 8.9.8 Research...")

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        records: List[Dict[str, Any]] = json.load(f)

    with open(SPLIT_PATH, "r", encoding="utf-8") as f:
        split_summary = json.load(f)

    logger.info(f"Loaded {len(records)} records from {MANIFEST_PATH.name}")

    # 1. Split counts and source groups
    splits = {}
    for r in records:
        s = r["split"]
        splits.setdefault(s, []).append(r)

    print("\n" + "=" * 75)
    print("DATASET V3 COMPOSITION & SPLIT AUDIT")
    print("=" * 75)
    for s_name in ["train", "val", "test"]:
        s_recs = splits.get(s_name, [])
        groups = set(r["source_group_id"] for r in s_recs)
        scream_c = sum(1 for r in s_recs if r["binary_label"] == "scream")
        non_c = sum(1 for r in s_recs if r["binary_label"] == "non_scream")
        amb_c = sum(1 for r in s_recs if r["binary_label"] == "ambiguous")
        print(f"  {s_name.upper():5}: {len(s_recs):4d} clips | {scream_c:3d} screams, {non_c:3d} non-screams, {amb_c:2d} amb | {len(groups):3d} source groups")

    # 2. Source-Group Disjointness (Leakage Audit)
    train_groups = set(r["source_group_id"] for r in splits["train"])
    val_groups = set(r["source_group_id"] for r in splits["val"])
    test_groups = set(r["source_group_id"] for r in splits["test"])

    leak_train_val = train_groups & val_groups
    leak_train_test = train_groups & test_groups
    leak_val_test = val_groups & test_groups

    print("-" * 75)
    print("SOURCE GROUP DISJOINTNESS AUDIT:")
    print(f"  Train / Val shared groups : {len(leak_train_val)} (MUST BE 0)")
    print(f"  Train / Test shared groups: {len(leak_train_test)} (MUST BE 0)")
    print(f"  Val / Test shared groups  : {len(leak_val_test)} (MUST BE 0)")
    assert len(leak_train_val) == 0 and len(leak_train_test) == 0 and len(leak_val_test) == 0, "Source group leakage detected!"

    # 3. Exact Hash Deduplication (PCM SHA-256)
    pcm_hashes = [r["pcm_sha256"] for r in records]
    unique_pcm = set(pcm_hashes)
    print("-" * 75)
    print("PCM HASH DEDUPLICATION AUDIT:")
    print(f"  Total records    : {len(records)}")
    print(f"  Unique PCM hashes: {len(unique_pcm)}")
    print(f"  Duplicate count  : {len(records) - len(unique_pcm)} (MUST BE 0)")
    assert len(records) == len(unique_pcm), "Duplicate PCM hashes found in dataset v3!"

    # 4. Stage 5 Historical Isolation Audit
    hist_test_in_train = [r["file_id"] for r in splits["train"] if r.get("is_historical_stage5_test")]
    hist_test_in_val = [r["file_id"] for r in splits["val"] if r.get("is_historical_stage5_test")]
    hist_test_in_test = [r["file_id"] for r in splits["test"] if r.get("is_historical_stage5_test")]

    print("-" * 75)
    print("HISTORICAL STAGE 5 TEST SET ISOLATION AUDIT:")
    print(f"  Historical test clips in Train: {len(hist_test_in_train)} (MUST BE 0)")
    print(f"  Historical test clips in Val  : {len(hist_test_in_val)} (MUST BE 0)")
    print(f"  Historical test clips in Test : {len(hist_test_in_test)} (ISOLATED IN TEST)")
    assert len(hist_test_in_train) == 0 and len(hist_test_in_val) == 0, "Historical test set contaminated train/val!"

    # 5. Licensing & Commercial Compatibility Audit
    licenses = Counter(r.get("license", "unknown") for r in records)
    print("-" * 75)
    print("LICENSING METADATA AUDIT:")
    for lic, cnt in licenses.most_common():
        print(f"  {lic:45}: {cnt:4d} clips")

    # Commercial vs Research Distinction:
    # CC0, CC-BY 3.0/4.0 are commercially permissive.
    # CC-BY-NC is strictly non-commercial research use only.
    nc_clips = [r for r in records if "nc" in r.get("license", "").lower() or "noncommercial" in r.get("license", "").lower()]
    print("-" * 75)
    print("COMMERCIAL VS EXPERIMENTAL RESEARCH COMPATIBILITY:")
    print(f"  Total permissive (CC0, CC-BY, public domain): {len(records) - len(nc_clips):4d} clips")
    print(f"  Research-only (CC BY-NC, non-commercial)    : {len(nc_clips):4d} clips")
    print("  NOTE: CC BY-NC clips are valid for experimental research only; excluded from commercial deployment.")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    main()
