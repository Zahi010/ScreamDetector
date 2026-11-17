"""Stage 8.9.11 Mandatory Readiness Gate and Verification.

Independently validates:
1. Stage 8.9.10 readiness files presence and internal consistency.
2. Commercially eligible manifest license integrity (Zero CC BY-NC, Sampling+, etc.).
3. Source-group disjointness (Train, Val, Test).
4. Stage 5 historical test quarantine (Zero Stage 5 test recordings/groups in Train or Val).
5. Production freeze verification (Authoritative SHA-256 for all production assets & threshold = 0.35).
6. Exact category counts and split counts verification.
"""

from __future__ import annotations

import csv
import hashlib
import json
import logging
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("readiness_gate_8_9_11")

STAGE10_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_10_readiness"
STAGE11_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_11_evaluation"

AUTHORITATIVE_HASHES = {
    "models/scream_classifier.joblib": "AD6E428D05D2359DA73B6DEE7CFDCEC646C87390B496B59CAD5F46B5A452851F",
    "models/model_metadata.json": "30C1C75D81AD61B1D0CACB70B221D034840888C7BFEDE949A15D47B139699F60",
    "reports/test_predictions.csv": "E93BE4550F97FE2CFE6BC0F2366650833D96F284C45CD1EB6026FBA0DB98449D",
    "reports/stage5_test_evaluation.md": "9E55B1F574E18BC4623A871D58926FEFCCD29F4C4E3EE22010A4A54A4E4CD1D2",
}

PERMISSIVE_LICENSES = {"CC0", "CC0 1.0", "CC0 1.0 Universal", "CC-0", "Public Domain", "CC BY", "CC BY 2.0", "CC BY 2.5", "CC BY 3.0", "CC BY 4.0"}
PROHIBITED_LICENSES = {"CC BY-NC", "CC BY-NC 3.0", "CC BY-NC 4.0", "CC BY-NC-ND", "CC BY-NC-SA", "Sampling+", "Sampling+ 1.0"}


def compute_file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().upper()


def run_readiness_audit() -> Dict[str, Any]:
    logger.info("=================================================================")
    logger.info("STAGE 8.9.11 — MANDATORY READINESS GATE & GOVERNANCE AUDIT")
    logger.info("=================================================================")

    results = {
        "stage10_artifacts_present": {},
        "production_freeze": {},
        "manifest_licensing_audit": {},
        "split_disjointness_audit": {},
        "stage5_quarantine_audit": {},
        "category_balance_verified": {},
        "gate_passed": False,
    }

    # 1. Verify Stage 8.9.10 deliverables presence
    required_stage10_files = [
        "stage8_9_10_readiness_report.md",
        "restricted_recordings_audit.csv",
        "commercially_eligible_manifest.json",
        "category_balance_before_after.csv",
        "targeted_data_acquisition_plan.md",
        "next_experiment_preregistration.md",
        "end_to_end_latency_protocol.md",
        "artifact_integrity_audit.json",
    ]
    all_files_present = True
    for fname in required_stage10_files:
        p = STAGE10_DIR / fname
        exists = p.exists() and p.stat().st_size > 0
        results["stage10_artifacts_present"][fname] = {
            "exists": exists,
            "size_bytes": p.stat().st_size if p.exists() else 0,
        }
        if not exists:
            all_files_present = False
            logger.error(f"Missing required Stage 8.9.10 artifact: {fname}")
        else:
            logger.info(f"Verified Stage 8.9.10 artifact: {fname} ({p.stat().st_size} bytes)")
    assert all_files_present, "Stage 8.9.10 files missing!"

    # 2. Production Freeze Verification
    logger.info("\n--- Verifying Production Artifact Hashes & DB ---")
    all_hashes_match = True
    for rel_path, expected_hash in AUTHORITATIVE_HASHES.items():
        p = BACKEND_DIR / rel_path
        actual_hash = compute_file_sha256(p)
        is_match = (actual_hash == expected_hash)
        results["production_freeze"][rel_path] = {
            "expected": expected_hash,
            "actual": actual_hash,
            "status": "EXACT_MATCH" if is_match else "MISMATCH",
        }
        if not is_match:
            all_hashes_match = False
            logger.error(f"HASH MISMATCH on {rel_path}!")
        else:
            logger.info(f"Production artifact {rel_path}: EXACT MATCH ({actual_hash[:16]}...)")
    assert all_hashes_match, "Production hash mismatch!"

    # Verify Production Threshold
    with open(BACKEND_DIR / "models" / "model_metadata.json", "r", encoding="utf-8") as f:
        meta = json.load(f)
    thresh = meta.get("selected_threshold")
    logger.info(f"Production threshold in metadata: {thresh} (expected 0.35)")
    assert thresh == 0.35, f"Production threshold altered: {thresh}"
    results["production_freeze"]["threshold"] = thresh

    # Verify Review DB
    db_path = BACKEND_DIR / "database" / "stage8_9_reviews.db"
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("SELECT review_status, COUNT(*) FROM candidates GROUP BY review_status")
    status_counts = dict(cur.fetchall())
    cur.execute("SELECT review_status FROM candidates WHERE recording_id = 'fsd50k_349401'")
    anchor_decision = cur.fetchone()[0]
    conn.close()

    results["production_freeze"]["database"] = {
        "status_counts": status_counts,
        "anchor_fsd50k_349401": anchor_decision,
        "total_reviewed": sum(v for k, v in status_counts.items() if k != "UNREVIEWED"),
    }
    logger.info(f"Database review status counts: {status_counts}")
    logger.info(f"Anchor clip fsd50k_349401: {anchor_decision}")
    assert anchor_decision == "SCREAM_PRESENT", "Anchor clip decision corrupted!"
    assert status_counts.get("APPROVED_NON_SCREAM") == 338, "Approved non-scream count corrupted!"
    assert status_counts.get("SCREAM_PRESENT") == 2, "Scream present count corrupted!"
    assert status_counts.get("AMBIGUOUS") == 3, "Ambiguous count corrupted!"

    # 3. Independently validate Commercially Eligible Manifest
    logger.info("\n--- Validating Commercially Eligible Manifest ---")
    manifest_path = STAGE10_DIR / "commercially_eligible_manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        eligible_manifest = json.load(f)
    logger.info(f"Loaded {len(eligible_manifest)} records from eligible manifest.")

    # Load quarantined audit
    quarantined_ids = set()
    with open(STAGE10_DIR / "restricted_recordings_audit.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            quarantined_ids.add(row["file_id"])
            quarantined_ids.add(row["original_recording_id"])
    logger.info(f"Loaded {len(quarantined_ids)} quarantined identifiers to ensure complete exclusion.")

    lic_counts = {}
    quarantine_leakage = 0
    prohibited_license_count = 0

    for rec in eligible_manifest:
        file_id = rec["file_id"]
        orig_id = rec.get("original_id") or ""
        lic = rec.get("license", "")
        lic_counts[lic] = lic_counts.get(lic, 0) + 1

        if file_id in quarantined_ids or orig_id in quarantined_ids:
            logger.error(f"LEAKAGE: Quarantined recording {file_id} found in eligible manifest!")
            quarantine_leakage += 1

        if any(bad in lic for bad in ["NC", "Non-Commercial", "Sampling+"]):
            logger.error(f"PROHIBITED LICENSE: {file_id} has license {lic}!")
            prohibited_license_count += 1

    results["manifest_licensing_audit"] = {
        "total_records": len(eligible_manifest),
        "license_breakdown": lic_counts,
        "quarantine_leakage": quarantine_leakage,
        "prohibited_licenses_found": prohibited_license_count,
    }
    logger.info(f"License breakdown: {lic_counts}")
    assert quarantine_leakage == 0, f"Found {quarantine_leakage} quarantined files in eligible manifest!"
    assert prohibited_license_count == 0, f"Found {prohibited_license_count} prohibited licenses!"

    # 4. Source-Group Disjointness & Stage 5 Historical Quarantine
    logger.info("\n--- Verifying Source-Group Disjointness & Historical Stage 5 Quarantine ---")
    train_groups = {r["source_group_id"] for r in eligible_manifest if r["split"] == "train"}
    val_groups = {r["source_group_id"] for r in eligible_manifest if r["split"] == "val"}
    test_groups = {r["source_group_id"] for r in eligible_manifest if r["split"] == "test"}

    train_val_overlap = train_groups.intersection(val_groups)
    train_test_overlap = train_groups.intersection(test_groups)
    val_test_overlap = val_groups.intersection(test_groups)

    results["split_disjointness_audit"] = {
        "train_groups": len(train_groups),
        "val_groups": len(val_groups),
        "test_groups": len(test_groups),
        "total_unique_groups": len(train_groups | val_groups | test_groups),
        "train_val_overlap": len(train_val_overlap),
        "train_test_overlap": len(train_test_overlap),
        "val_test_overlap": len(val_test_overlap),
    }
    logger.info(f"Train groups: {len(train_groups)}, Val groups: {len(val_groups)}, Test groups: {len(test_groups)}")
    assert len(train_val_overlap) == 0, f"Train and Val group overlap: {train_val_overlap}"
    assert len(train_test_overlap) == 0, f"Train and Test group overlap: {train_test_overlap}"
    assert len(val_test_overlap) == 0, f"Val and Test group overlap: {val_test_overlap}"
    logger.info("SPLIT DISJOINTNESS STRICTLY PRESERVED: ZERO GROUP OVERLAP!")

    # Check Stage 5 historical test quarantine
    with open(BACKEND_DIR / "reports" / "test_predictions.csv", "r", encoding="utf-8") as f:
        s5_rows = list(csv.DictReader(f))
    s5_files = {r["file_id"] for r in s5_rows}
    s5_groups = {r["source_group_id"] for r in s5_rows}

    train_files = {r["file_id"] for r in eligible_manifest if r["split"] == "train"}
    val_files = {r["file_id"] for r in eligible_manifest if r["split"] == "val"}

    s5_in_train_files = s5_files.intersection(train_files)
    s5_in_val_files = s5_files.intersection(val_files)
    s5_in_train_groups = s5_groups.intersection(train_groups)
    s5_in_val_groups = s5_groups.intersection(val_groups)

    results["stage5_quarantine_audit"] = {
        "stage5_total_test_files": len(s5_files),
        "stage5_total_test_groups": len(s5_groups),
        "stage5_files_in_train": len(s5_in_train_files),
        "stage5_files_in_val": len(s5_in_val_files),
        "stage5_groups_in_train": len(s5_in_train_groups),
        "stage5_groups_in_val": len(s5_in_val_groups),
    }
    logger.info(f"Stage 5 test recordings in Train: {len(s5_in_train_files)}, in Val: {len(s5_in_val_files)}")
    logger.info(f"Stage 5 test source groups in Train: {len(s5_in_train_groups)}, in Val: {len(s5_in_val_groups)}")
    assert len(s5_in_train_files) == 0, "Stage 5 test file leaked into Train!"
    assert len(s5_in_val_files) == 0, "Stage 5 test file leaked into Val!"
    assert len(s5_in_train_groups) == 0, "Stage 5 test group leaked into Train!"
    assert len(s5_in_val_groups) == 0, "Stage 5 test group leaked into Val!"
    logger.info("STAGE 5 HISTORICAL TEST PERMANENTLY QUARANTINED: ZERO CONTAMINATION!")

    # 5. Verify actual split counts and category totals directly from manifest
    logger.info("\n--- Verifying Actual Split Counts & Category Totals ---")
    cat_split_counts = {}
    for r in eligible_manifest:
        cat = r["target_category"]
        split = r["split"]
        if cat not in cat_split_counts:
            cat_split_counts[cat] = {"train": 0, "val": 0, "test": 0, "total": 0}
        cat_split_counts[cat][split] += 1
        cat_split_counts[cat]["total"] += 1

    split_totals = {"train": len(train_files), "val": len(val_files), "test": len(eligible_manifest) - len(train_files) - len(val_files), "total": len(eligible_manifest)}
    logger.info(f"Manifest Split Totals: Train={split_totals['train']}, Val={split_totals['val']}, Test={split_totals['test']}, Total={split_totals['total']}")

    for cat, counts in sorted(cat_split_counts.items()):
        logger.info(f"  {cat:25}: Train={counts['train']:3d}, Val={counts['val']:3d}, Test={counts['test']:3d}, Total={counts['total']:4d}")

    results["category_balance_verified"] = {
        "split_totals": split_totals,
        "category_totals": cat_split_counts,
    }

    # Compare with category_balance_before_after.csv
    csv_path = STAGE10_DIR / "category_balance_before_after.csv"
    with open(csv_path, "r", encoding="utf-8") as f:
        csv_rows = list(csv.DictReader(f))
    for row in csv_rows:
        cat = row["target_category"]
        if cat == "OVERALL_ALL_CATEGORIES":
            assert int(row["eligible_train"]) == split_totals["train"]
            assert int(row["eligible_val"]) == split_totals["val"]
            assert int(row["eligible_test"]) == split_totals["test"]
            assert int(row["eligible_total"]) == split_totals["total"]
        else:
            assert cat in cat_split_counts, f"Category {cat} missing from manifest counts!"
            assert int(row["eligible_train"]) == cat_split_counts[cat]["train"]
            assert int(row["eligible_val"]) == cat_split_counts[cat]["val"]
            assert int(row["eligible_test"]) == cat_split_counts[cat]["test"]
            assert int(row["eligible_total"]) == cat_split_counts[cat]["total"]
    logger.info("Actual manifest counts match category_balance_before_after.csv with 100% precision!")

    results["gate_passed"] = True
    logger.info("=================================================================")
    logger.info("ALL READINESS GATES PASSED SUCCESSFULLY!")
    logger.info("=================================================================")

    # Write readiness results JSON
    out_json = STAGE11_DIR / "stage8_9_11_readiness_audit.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Saved readiness audit report to {out_json}")

    return results


if __name__ == "__main__":
    run_readiness_audit()
