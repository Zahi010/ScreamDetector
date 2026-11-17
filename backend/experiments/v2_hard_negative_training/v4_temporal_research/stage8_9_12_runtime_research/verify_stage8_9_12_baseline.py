"""Stage 8.9.12 Mandatory Baseline Freeze and Stage 8.9.11 Reproduction Audit.

Verifies:
1. Production hashes match authoritative ledger exactly.
2. Production threshold remains 0.3500.
3. Review database integrity (343 records, anchor fsd50k_349401 = SCREAM_PRESENT).
4. Stage 8.9.11 evaluation metrics reproduction directly from `stage8_9_11_test_predictions.csv`.
5. Model artifact existence and configurations for D_v4, T1_v4, H_v4_Commercial, H_v5_SNR.
"""

from __future__ import annotations

import csv
import hashlib
import json
import logging
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict

import joblib
import numpy as np
from sklearn.metrics import (
    precision_recall_fscore_support,
    roc_auc_score,
    precision_recall_curve,
    auc,
    average_precision_score,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("stage8_9_12_baseline_audit")

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent

AUTHORITATIVE_HASHES = {
    "backend/models/scream_classifier.joblib": "AD6E428D05D2359DA73B6DEE7CFDCEC646C87390B496B59CAD5F46B5A452851F",
    "backend/models/model_metadata.json": "30C1C75D81AD61B1D0CACB70B221D034840888C7BFEDE949A15D47B139699F60",
    "backend/reports/test_predictions.csv": "E93BE4550F97FE2CFE6BC0F2366650833D96F284C45CD1EB6026FBA0DB98449D",
    "backend/reports/stage5_test_evaluation.md": "9E55B1F574E18BC4623A871D58926FEFCCD29F4C4E3EE22010A4A54A4E4CD1D2",
}

STAGE11_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_11_evaluation"
STAGE12_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_12_runtime_research"


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().upper()


def audit_baseline() -> Dict[str, Any]:
    logger.info("=================================================================")
    logger.info("STAGE 8.9.12: MANDATORY BASELINE FREEZE & REPRODUCTION AUDIT")
    logger.info("=================================================================")

    audit_results: Dict[str, Any] = {
        "production_hashes": {},
        "production_threshold_verified": False,
        "database_audit": {},
        "stage11_model_artifacts": {},
        "stage11_reproduced_metrics": {},
        "all_checks_passed": False,
    }

    # 1. Verify production file hashes
    all_hashes_ok = True
    for rel_path, expected_hash in AUTHORITATIVE_HASHES.items():
        abs_path = BACKEND_DIR / rel_path.replace("backend/", "")
        if not abs_path.exists():
            logger.error(f"Missing production file: {abs_path}")
            audit_results["production_hashes"][rel_path] = {"status": "MISSING"}
            all_hashes_ok = False
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
            all_hashes_ok = False

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
        all_hashes_ok = False

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
        "total_reviewed": total_reviewed,
        "decision_counts": status_counts,
        "anchor_file_id": "fsd50k_349401",
        "anchor_decision": anchor_decision,
        "status": "PASSED" if db_ok else "FAILED",
    }
    logger.info(f"Database audit: {total_reviewed} reviewed records, anchor={anchor_decision} (Status: {audit_results['database_audit']['status']})")

    # 4. Confirm Stage 8.9.11 model artifacts
    stage11_models = {
        "D_v4": STAGE11_DIR / "models" / "model_d_v4.joblib",
        "T1_v4": STAGE11_DIR / "models" / "model_t1_v4.weights.h5",
        "H_v4_Commercial": STAGE11_DIR / "models" / "model_h_v4_commercial.joblib",
        "H_v5_SNR": STAGE11_DIR / "models" / "model_h_v5_snr.joblib",
    }
    models_ok = True
    for name, p in stage11_models.items():
        exists = p.exists()
        size_bytes = p.stat().st_size if exists else 0
        audit_results["stage11_model_artifacts"][name] = {
            "path": str(p),
            "exists": exists,
            "size_bytes": size_bytes,
        }
        if exists:
            logger.info(f"OK Stage 11 Model {name} exists ({size_bytes / 1024:.2f} KB)")
        else:
            logger.error(f"FAIL: Missing model {name} at {p}")
            models_ok = False

    # 5. Reproduce Stage 8.9.11 test metrics from predictions
    preds_path = STAGE11_DIR / "stage8_9_11_test_predictions.csv"
    thresh_path = STAGE11_DIR / "preregistered_candidate_thresholds.json"
    metrics_path = STAGE11_DIR / "stage8_9_11_evaluation_metrics.json"

    with open(thresh_path, "r", encoding="utf-8") as f:
        locked_thresholds = json.load(f)

    with open(metrics_path, "r", encoding="utf-8") as f:
        saved_metrics = json.load(f)

    rows: List[Dict[str, str]] = []
    with open(preds_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

    n_test = len(rows)
    logger.info(f"Loaded {n_test} test predictions from {preds_path.name}")
    labels = np.array([int(r["y_true"]) for r in rows], dtype=int)
    categories = [r["category"] for r in rows]

    pos_mask = (labels == 1)
    neg_mask = (labels == 0)
    shout_mask = np.array([c == "shouting_and_speech" for c in categories])

    candidate_mapping = {
        "D_v4": ("prob_D_v4", "Model D_v4 (Baseline Linear Fusion)"),
        "T1_v4": ("prob_T1_v4", "Model T1_v4 (Dilated 1D TCN)"),
        "H_v4_Commercial": ("prob_H_v4_Commercial", "Model H_v4_Commercial (Calibrated Hybrid)"),
        "H_v5_SNR": ("prob_H_v5_SNR", "Model H_v5_SNR (Context-Aware Hybrid with Dynamic SNR)"),
    }

    reproduced_metrics = {}
    metrics_match_ok = True

    for ckey, (prob_col, full_name) in candidate_mapping.items():
        tau = float(locked_thresholds[ckey]["selected_threshold"])
        probs = np.array([float(r[prob_col]) for r in rows], dtype=float)
        preds = (probs >= tau).astype(int)

        rec = float(np.mean(preds[pos_mask]))
        fpr = float(np.mean(preds[neg_mask]))
        shout_fpr = float(np.mean(preds[shout_mask]))

        p, r, f1, _ = precision_recall_fscore_support(labels, preds, average="binary", zero_division=0)
        roc_auc = float(roc_auc_score(labels, probs))
        pr_auc = float(average_precision_score(labels, probs))

        reproduced = {
            "locked_threshold": tau,
            "recall": round(rec, 4),
            "fpr": round(fpr, 4),
            "shout_fpr": round(shout_fpr, 4),
            "precision": round(float(p), 4),
            "f1": round(float(f1), 4),
            "pr_auc": round(pr_auc, 4),
            "roc_auc": round(roc_auc, 4),
        }
        reproduced_metrics[ckey] = reproduced

        # Compare with saved report
        saved = saved_metrics["candidate_evaluations"][ckey]["test_metrics"]
        diff_rec = abs(round(rec, 4) - saved["recall"])
        diff_fpr = abs(round(fpr, 4) - saved["fpr"])
        diff_pr_auc = abs(round(pr_auc, 4) - saved["pr_auc"])

        if diff_rec < 1e-3 and diff_fpr < 1e-3 and diff_pr_auc < 1e-3:
            logger.info(f"OK Metric Reproduction for {ckey}: Rec={rec*100:.2f}%, FPR={fpr*100:.2f}%, PR-AUC={pr_auc:.4f}")
        else:
            logger.error(f"FAIL Metric Discrepancy for {ckey}: diff_rec={diff_rec}, diff_fpr={diff_fpr}, diff_pr_auc={diff_pr_auc}")
            metrics_match_ok = False

    audit_results["stage11_reproduced_metrics"] = reproduced_metrics
    audit_results["all_checks_passed"] = bool(all_hashes_ok and db_ok and models_ok and metrics_match_ok)

    out_path = STAGE12_DIR / "production_integrity_audit.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(audit_results, f, indent=2)

    logger.info(f"Audit ledger saved to: {out_path}")
    logger.info(f"OVERALL AUDIT PASSED: {audit_results['all_checks_passed']}")
    return audit_results


if __name__ == "__main__":
    res = audit_baseline()
    if not res["all_checks_passed"]:
        logger.error("Mandatory baseline audit failed! Halting.")
        sys.exit(1)
    else:
        logger.info("Stage 8.9.12 baseline verified. Safe to proceed with experimental research.")
