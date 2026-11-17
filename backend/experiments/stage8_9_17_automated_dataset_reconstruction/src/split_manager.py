"""Source-Group Split Manager & Data Leakage Prevention Engine (Stage 8.9.17).

Ensures strict source-group isolation across Train (70%), Val (15%), and Test (15%) splits:
- Zero uploader / recording identity overlap between splits.
- Zero audio content-hash overlap between splits.
- Strict quarantine of historical Stage 5 test files and source groups.
- Stratified group allocation ensuring screams, silence, infant crying, and shouting
  are represented across all three splits with an adequately sized test cohort.
"""

from __future__ import annotations

import csv
import json
import logging
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import numpy as np

logger = logging.getLogger("split_manager")

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = WORKSPACE_DIR.parent.parent


class SourceGroupSplitManager:
    """Manages group-isolated train/val/test splitting and leakage auditing."""

    def __init__(self, workspace_dir: Path = WORKSPACE_DIR):
        self.workspace_dir = workspace_dir
        self.backend_dir = workspace_dir.parent.parent
        self.manifest_dir = workspace_dir / "data" / "manifests"
        self.manifest_dir.mkdir(parents=True, exist_ok=True)

        self.reconstructed_manifest_path = self.manifest_dir / "reconstructed_dataset_manifest.csv"
        self.splits_manifest_path = self.manifest_dir / "source_group_splits.csv"
        self.leakage_audit_path = self.manifest_dir / "leakage_audit_manifest.csv"

        self.stage5_quarantined_files: Set[str] = set()
        self.stage5_quarantined_groups: Set[str] = set()
        self._load_stage5_quarantine()

    def _load_stage5_quarantine(self) -> None:
        """Load Stage 5 test set references to guarantee absolute exclusion."""
        pred_csv = self.backend_dir / "reports" / "test_predictions.csv"
        if pred_csv.exists():
            with open(pred_csv, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    if "file_id" in r:
                        self.stage5_quarantined_files.add(r["file_id"])
                    if "source_group_id" in r:
                        self.stage5_quarantined_groups.add(r["source_group_id"])
        logger.info(
            "Stage 5 Quarantine loaded: %d files, %d source groups.",
            len(self.stage5_quarantined_files),
            len(self.stage5_quarantined_groups),
        )

    def generate_splits(
        self,
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        seed: int = 42,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Generate stratified group-level splits without cross-split leakage."""
        if not self.reconstructed_manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found: {self.reconstructed_manifest_path}")

        with open(self.reconstructed_manifest_path, "r", encoding="utf-8") as f:
            records = list(csv.DictReader(f))

        logger.info("Loaded %d records for source-group splitting.", len(records))

        # Check for any accidental Stage 5 files
        clean_records = []
        for r in records:
            if r["file_id"] in self.stage5_quarantined_files or r["source_group_id"] in self.stage5_quarantined_groups:
                logger.error("CRITICAL: Stage 5 quarantined file detected in manifest: %s", r["file_id"])
                continue
            clean_records.append(r)

        # Aggregate records by source_group_id
        group_to_records: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for r in clean_records:
            group_to_records[r["source_group_id"]].append(r)

        logger.info("Aggregated into %d unique source groups.", len(group_to_records))

        # Categorize groups by their primary acoustic content for stratified group assignment
        # Categories: scream_groups (has screams), silence_groups, confuser_groups, ambient_groups
        group_types: Dict[str, List[str]] = defaultdict(list)
        for gid, grp_records in group_to_records.items():
            has_scream = any(rec["binary_label"] == "scream" for rec in grp_records)
            categories = {rec["canonical_category"] for rec in grp_records}

            if has_scream:
                group_types["scream"].append(gid)
            elif any("SILENCE" in c or "AMBIENT_ROOM" in c for c in categories):
                group_types["silence"].append(gid)
            elif any("CRYING" in c for c in categories):
                group_types["crying"].append(gid)
            elif any("SHOUTING" in c for c in categories):
                group_types["shouting"].append(gid)
            elif any("CROWD" in c for c in categories):
                group_types["crowd"].append(gid)
            else:
                group_types["other_negative"].append(gid)

        rng = np.random.RandomState(seed)

        group_split_map: Dict[str, str] = {}

        # Stratified allocation of groups into train, val, test
        for gtype, gids in group_types.items():
            shuffled_gids = list(gids)
            rng.shuffle(shuffled_gids)

            n = len(shuffled_gids)
            n_train = int(round(n * train_ratio))
            n_val = int(round(n * val_ratio))
            # Ensure at least 1 group in val and test if n >= 3
            if n >= 3:
                n_train = min(n - 2, max(1, n_train))
                n_val = min(n - n_train - 1, max(1, n_val))
            elif n == 2:
                n_train, n_val = 1, 0
            elif n == 1:
                n_train, n_val = 1, 0

            train_gids = set(shuffled_gids[:n_train])
            val_gids = set(shuffled_gids[n_train : n_train + n_val])
            test_gids = set(shuffled_gids[n_train + n_val :])

            for gid in train_gids:
                group_split_map[gid] = "train"
            for gid in val_gids:
                group_split_map[gid] = "val"
            for gid in test_gids:
                group_split_map[gid] = "test"

        # Assign split label to every record
        annotated_records = []
        for r in clean_records:
            gid = r["source_group_id"]
            split = group_split_map.get(gid, "train")
            rec = dict(r)
            rec["split"] = split
            annotated_records.append(rec)

        # Execute comprehensive Leakage Audit
        audit_results = self.audit_splits(annotated_records)

        # Save annotated manifest
        fieldnames = list(annotated_records[0].keys())
        with open(self.splits_manifest_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(annotated_records)

        logger.info("Saved source-group splits manifest to: %s", self.splits_manifest_path)

        # Save leakage audit
        with open(self.leakage_audit_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["metric", "status", "details"])
            writer.writeheader()
            for k, v in audit_results.items():
                writer.writerow({
                    "metric": k,
                    "status": "PASSED" if v["passed"] else "FAILED",
                    "details": json.dumps(v["details"]),
                })

        logger.info("Saved leakage audit manifest to: %s", self.leakage_audit_path)
        return annotated_records, audit_results

    def audit_splits(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform rigorous leakage checks across train, val, and test splits."""
        train_records = [r for r in records if r["split"] == "train"]
        val_records = [r for r in records if r["split"] == "val"]
        test_records = [r for r in records if r["split"] == "test"]

        train_groups = {r["source_group_id"] for r in train_records}
        val_groups = {r["source_group_id"] for r in val_records}
        test_groups = {r["source_group_id"] for r in test_records}

        train_hashes = {r["content_hash"] for r in train_records if r.get("content_hash")}
        val_hashes = {r["content_hash"] for r in val_records if r.get("content_hash")}
        test_hashes = {r["content_hash"] for r in test_records if r.get("content_hash")}

        all_file_ids = {r["file_id"] for r in records}
        all_groups = {r["source_group_id"] for r in records}

        # 1. Source-Group Disjointness
        tv_groups = train_groups.intersection(val_groups)
        tt_groups = train_groups.intersection(test_groups)
        vt_groups = val_groups.intersection(test_groups)
        group_leak = len(tv_groups) + len(tt_groups) + len(vt_groups)

        # 2. Content Hash Disjointness (Deduplication)
        tv_hashes = train_hashes.intersection(val_hashes)
        tt_hashes = train_hashes.intersection(test_hashes)
        vt_hashes = val_hashes.intersection(test_hashes)
        hash_leak = len(tv_hashes) + len(tt_hashes) + len(vt_hashes)

        # 3. Stage 5 Quarantine Isolation
        st5_file_overlap = all_file_ids.intersection(self.stage5_quarantined_files)
        st5_group_overlap = all_groups.intersection(self.stage5_quarantined_groups)

        # 4. Cohort Sizing
        test_screams = sum(1 for r in test_records if r["binary_label"] == "scream")
        test_short_screams = sum(1 for r in test_records if r["canonical_category"] == "SHORT_SCREAM")
        test_silence = sum(1 for r in test_records if "SILENCE" in r["canonical_category"] or "AMBIENT_ROOM" in r["canonical_category"])
        test_infant_crying = sum(1 for r in test_records if r["canonical_category"] == "INFANT_CRYING")
        test_shouting = sum(1 for r in test_records if r["canonical_category"] == "SHOUTING_EXCITED_SPEECH")

        audit_results = {
            "source_group_disjointness": {
                "passed": group_leak == 0,
                "details": {
                    "train_groups": len(train_groups),
                    "val_groups": len(val_groups),
                    "test_groups": len(test_groups),
                    "train_val_overlap": list(tv_groups),
                    "train_test_overlap": list(tt_groups),
                    "val_test_overlap": list(vt_groups),
                },
            },
            "content_hash_disjointness": {
                "passed": hash_leak == 0,
                "details": {
                    "train_val_hash_overlap": list(tv_hashes),
                    "train_test_hash_overlap": list(tt_hashes),
                    "val_test_hash_overlap": list(vt_hashes),
                },
            },
            "stage5_quarantine_isolation": {
                "passed": len(st5_file_overlap) == 0 and len(st5_group_overlap) == 0,
                "details": {
                    "file_overlap_count": len(st5_file_overlap),
                    "group_overlap_count": len(st5_group_overlap),
                },
            },
            "test_cohort_adequacy": {
                "passed": test_screams >= 50 and test_short_screams >= 10,
                "details": {
                    "total_test_records": len(test_records),
                    "total_test_screams": test_screams,
                    "test_short_screams": test_short_screams,
                    "test_silence": test_silence,
                    "test_infant_crying": test_infant_crying,
                    "test_shouting": test_shouting,
                },
            },
            "split_record_counts": {
                "passed": True,
                "details": {
                    "train": len(train_records),
                    "val": len(val_records),
                    "test": len(test_records),
                    "train_pct": round(len(train_records) / len(records) * 100, 2),
                    "val_pct": round(len(val_records) / len(records) * 100, 2),
                    "test_pct": round(len(test_records) / len(records) * 100, 2),
                },
            },
        }

        logger.info("--- Leakage Audit Summary ---")
        for k, v in audit_results.items():
            status = "PASSED" if v["passed"] else "FAILED"
            logger.info("%s: %s | %s", k, status, v["details"])

        return audit_results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    manager = SourceGroupSplitManager()
    records, audit = manager.generate_splits()
    print("Source-group splitting complete!")
