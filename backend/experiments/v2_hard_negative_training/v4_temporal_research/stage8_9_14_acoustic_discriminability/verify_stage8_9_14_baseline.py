"""Stage 8.9.14 Mandatory Baseline Freeze and Stage 8.9.13 Reproduction Audit.

Verifies:
1. Production hashes match authoritative ledger exactly.
2. Production threshold remains 0.3500.
3. Review database integrity (343 records, anchor fsd50k_349401 = SCREAM_PRESENT).
4. Stage 8.9.13 artifact verification and reproduction of event-level metrics.
"""

from __future__ import annotations

import csv
import hashlib
import json
import logging
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("stage8_9_14_baseline_audit")

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))

AUTHORITATIVE_HASHES = {
    "backend/models/scream_classifier.joblib": "AD6E428D05D2359DA73B6DEE7CFDCEC646C87390B496B59CAD5F46B5A452851F",
    "backend/models/model_metadata.json": "30C1C75D81AD61B1D0CACB70B221D034840888C7BFEDE949A15D47B139699F60",
    "backend/reports/test_predictions.csv": "E93BE4550F97FE2CFE6BC0F2366650833D96F284C45CD1EB6026FBA0DB98449D",
    "backend/reports/stage5_test_evaluation.md": "9E55B1F574E18BC4623A871D58926FEFCCD29F4C4E3EE22010A4A54A4E4CD1D2",
}

STAGE13_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_13_event_logic"
STAGE14_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_14_acoustic_discriminability"


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().upper()


def audit_baseline() -> Dict[str, Any]:
    logger.info("=================================================================")
    logger.info("STAGE 8.9.14: MANDATORY BASELINE FREEZE & REPRODUCTION AUDIT")
    logger.info("=================================================================")

    audit_results: Dict[str, Any] = {
        "production_hashes": {},
        "production_threshold_verified": False,
        "database_audit": {},
        "stage13_artifacts_present": {},
        "stage13_reproduced_metrics": {},
        "all_checks_passed": False,
    }

    all_ok = True

    # 1. Verify production hashes
    for rel_path, expected_hash in AUTHORITATIVE_HASHES.items():
        sub_rel = rel_path.replace("backend/", "")
        abs_path = BACKEND_DIR / sub_rel
        if not abs_path.exists():
            logger.error(f"FAIL: Missing production file: {abs_path}")
            audit_results["production_hashes"][rel_path] = {"error": "FILE_NOT_FOUND"}
            all_ok = False
            continue
        actual_hash = compute_sha256(abs_path)
        match = (actual_hash == expected_hash)
        audit_results["production_hashes"][rel_path] = {
            "expected": expected_hash,
            "actual": actual_hash,
            "match": match,
        }
        if match:
            logger.info(f"OK SHA-256 MATCH: {rel_path}")
        else:
            logger.error(f"FAIL SHA-256 MISMATCH: {rel_path} (got {actual_hash})")
            all_ok = False

    # 2. Verify operating threshold in metadata
    meta_path = BACKEND_DIR / "models" / "model_metadata.json"
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    operating_thresh = meta.get("selected_threshold")
    logger.info(f"Production operating threshold in metadata: {operating_thresh}")
    if operating_thresh == 0.35:
        audit_results["production_threshold_verified"] = True
        logger.info("OK Production threshold verified as 0.3500.")
    else:
        logger.error(f"FAIL: Operating threshold is {operating_thresh}, expected 0.3500!")
        all_ok = False

    # 3. Verify review database
    db_path = BACKEND_DIR / "database" / "stage8_9_reviews.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT review_status, COUNT(*) FROM candidates GROUP BY review_status")
    status_counts = dict(cursor.fetchall())
    total_reviewed = sum(v for k, v in status_counts.items() if k != "UNREVIEWED")
    cursor.execute("SELECT review_status FROM candidates WHERE recording_id = 'fsd50k_349401'")
    anchor_row = cursor.fetchone()
    anchor_decision = anchor_row[0] if anchor_row else None
    conn.close()

    db_ok = (total_reviewed == 343 and anchor_decision == "SCREAM_PRESENT")
    audit_results["database_audit"] = {
        "database_path": str(db_path),
        "total_reviewed": total_reviewed,
        "status_counts": status_counts,
        "anchor_fsd50k_349401": anchor_decision,
        "status": "PASSED" if db_ok else "FAILED",
    }
    if db_ok:
        logger.info(f"Database audit: {total_reviewed} reviewed records, anchor={anchor_decision} (Status: PASSED)")
    else:
        logger.error(f"Database audit FAILED: {total_reviewed} reviewed records, anchor={anchor_decision}")
        all_ok = False

    # 4. Verify Stage 8.9.13 artifacts
    required_stage13_files = [
        "stage8_9_13_event_logic_report.md",
        "event_annotation_protocol.md",
        "false_positive_event_analysis.csv",
        "temporal_policy_validation_results.csv",
        "event_level_test_results.csv",
        "detection_delay_analysis.csv",
        "latency_benchmark_results.csv",
        "experiment_configurations.json",
        "production_integrity_audit.json",
        "dual_path_state_machine.py",
        "test_stage8_9_13_regression.py",
    ]
    for fn in required_stage13_files:
        p = STAGE13_DIR / fn
        exists = p.exists()
        size = p.stat().st_size if exists else 0
        audit_results["stage13_artifacts_present"][fn] = {"exists": exists, "size_bytes": size}
        if exists:
            logger.info(f"OK Stage 8.9.13 artifact: {fn} ({size} bytes)")
        else:
            logger.error(f"FAIL: Missing Stage 8.9.13 artifact: {fn}")
            all_ok = False

    # 5. Reproduce Stage 8.9.13 key metrics from saved test results
    test_results_csv = STAGE13_DIR / "event_level_test_results.csv"
    if test_results_csv.exists():
        with open(test_results_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            records = {r["candidate_id"]: r for r in reader}

        # Check D_v4_Single_Window_Base
        d_base = records.get("D_v4_Single_Window_Base", {})
        d_recall = float(d_base.get("event_recall_pct", 0.0))
        d_fpr = float(d_base.get("event_fpr_pct", 0.0))
        d_short = float(d_base.get("short_scream_recall_pct", 0.0))

        # Check D_v4_DualPath_Balanced
        dp_bal = records.get("D_v4_DualPath_Balanced", {})
        dp_recall = float(dp_bal.get("event_recall_pct", 0.0))
        dp_fpr = float(dp_bal.get("event_fpr_pct", 0.0))
        dp_short = float(dp_bal.get("short_scream_recall_pct", 0.0))
        dp_dupes = float(dp_bal.get("duplicate_alerts_per_event", 99.0))

        # Check D_v4_Consecutive_2_Base
        c2_base = records.get("D_v4_Consecutive_2_Base", {})
        c2_short = float(c2_base.get("short_scream_recall_pct", 99.0))

        metric_match = (
            abs(d_recall - 71.56) < 0.1
            and abs(d_fpr - 37.37) < 0.1
            and abs(dp_recall - 81.65) < 0.1
            and abs(dp_fpr - 43.94) < 0.1
            and abs(dp_dupes - 0.00) < 0.01
            and abs(c2_short - 0.0) < 0.01
        )

        audit_results["stage13_reproduced_metrics"] = {
            "D_v4_Single_Window_Base": {"recall": d_recall, "fpr": d_fpr, "short_recall": d_short},
            "D_v4_DualPath_Balanced": {"recall": dp_recall, "fpr": dp_fpr, "short_recall": dp_short, "dupes": dp_dupes},
            "D_v4_Consecutive_2_Base": {"short_recall": c2_short},
            "verified": metric_match,
        }
        if metric_match:
            logger.info("OK Verified Stage 8.9.13 test event metrics reproduction.")
        else:
            logger.error("FAIL: Metric mismatch reproducing Stage 8.9.13 test results!")
            all_ok = False

    audit_results["all_checks_passed"] = all_ok
    STAGE14_DIR.mkdir(parents=True, exist_ok=True)
    out_path = STAGE14_DIR / "production_integrity_audit.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(audit_results, f, indent=2)
    logger.info(f"Audit ledger saved to: {out_path}")
    logger.info(f"OVERALL AUDIT PASSED: {all_ok}")

    if not all_ok:
        raise RuntimeError("Stage 8.9.14 Baseline Verification FAILED!")
    return audit_results


if __name__ == "__main__":
    audit_baseline()
