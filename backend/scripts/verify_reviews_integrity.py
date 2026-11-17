"""Verify the exact integrity of existing human reviews and model hashes."""

from __future__ import annotations

import hashlib
import sqlite3
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from src.config import BACKEND_DIR, MODELS_DIR
from src.dataset.acquisition_evaluator import EXPECTED_CLASSIFIER_SHA256, EXPECTED_METADATA_SHA256, FROZEN_THRESHOLD


def verify_database_integrity():
    db_path = BACKEND_DIR / "database" / "stage8_9_reviews.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    # 1. Total counts
    total = conn.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
    has_audio = conn.execute("SELECT COUNT(*) FROM candidates WHERE has_audio = 1").fetchone()[0]
    missing_audio = conn.execute("SELECT COUNT(*) FROM candidates WHERE has_audio = 0").fetchone()[0]

    # 2. Review decisions breakdown
    status_counts = conn.execute(
        "SELECT review_status, COUNT(*) as cnt FROM candidates GROUP BY review_status ORDER BY cnt DESC"
    ).fetchall()
    status_dict = {row["review_status"]: row["cnt"] for row in status_counts}

    print("==================================================")
    print("DATABASE REVIEW INTEGRITY CHECK")
    print("==================================================")
    print(f"Total Candidates in Database: {total}")
    print(f"Has Audio Available         : {has_audio}")
    print(f"Missing Audio               : {missing_audio}")
    print("\nReview Statuses:")
    for st, count in status_dict.items():
        print(f"  - {st:<22}: {count}")

    # Verify expected numbers
    approved = status_dict.get("APPROVED_NON_SCREAM", 0)
    scream = status_dict.get("SCREAM_PRESENT", 0)
    ambiguous = status_dict.get("AMBIGUOUS", 0)
    unreviewed = status_dict.get("UNREVIEWED", 0)
    total_reviewed = approved + scream + ambiguous

    print(f"\nTotal Human Reviews Finalized: {total_reviewed}")
    print(f"  - APPROVED_NON_SCREAM      : {approved} (Expected: 181)")
    print(f"  - SCREAM_PRESENT           : {scream} (Expected: 2)")
    print(f"  - AMBIGUOUS                : {ambiguous} (Expected: 2)")
    print(f"  - UNREVIEWED (Pending)     : {unreviewed} (Expected: 185)")

    is_exact = (approved == 181 and scream == 2 and ambiguous == 2 and total_reviewed == 185)
    print(f"Human Decisions Exactly Preserved: {is_exact}")

    # Check model artifact hashes
    clf_path = MODELS_DIR / "scream_classifier.joblib"
    meta_path = MODELS_DIR / "model_metadata.json"

    clf_hash = hashlib.sha256(clf_path.read_bytes()).hexdigest()
    meta_hash = hashlib.sha256(meta_path.read_bytes()).hexdigest()

    print("\nModel Artifact Integrity:")
    print(f"  - Classifier Hash: {clf_hash}")
    print(f"    Expected Hash  : {EXPECTED_CLASSIFIER_SHA256}")
    print(f"    Match          : {clf_hash == EXPECTED_CLASSIFIER_SHA256}")
    print(f"  - Metadata Hash  : {meta_hash}")
    print(f"    Expected Hash  : {EXPECTED_METADATA_SHA256}")
    print(f"    Match          : {meta_hash == EXPECTED_METADATA_SHA256}")
    print(f"  - Operating Thresh: {FROZEN_THRESHOLD} (Expected: 0.35)")

    conn.close()
    return is_exact and (clf_hash == EXPECTED_CLASSIFIER_SHA256) and (meta_hash == EXPECTED_METADATA_SHA256)


if __name__ == "__main__":
    ok = verify_database_integrity()
    sys.exit(0 if ok else 1)
