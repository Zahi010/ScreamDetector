"""Stage 8.9.3 Investigation & Audit of Human Labels and Model Evaluations."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from src.config import BACKEND_DIR
from src.database.review_store import get_review_store


def audit():
    store = get_review_store()
    with store._get_connection() as conn:
        # 1. Total candidates
        total_candidates = conn.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
        has_audio_count = conn.execute("SELECT COUNT(*) FROM candidates WHERE has_audio = 1").fetchone()[0]
        missing_audio_count = conn.execute("SELECT COUNT(*) FROM candidates WHERE has_audio = 0").fetchone()[0]

        # 2. Saved human decisions
        status_rows = conn.execute("""
            SELECT review_status, COUNT(*) as cnt
            FROM candidates
            GROUP BY review_status
            ORDER BY cnt DESC
        """).fetchall()
        status_counts = {r["review_status"]: r["cnt"] for r in status_rows}

        # 3. Audit log counts
        audit_log_count = conn.execute("SELECT COUNT(*) FROM review_audit_log").fetchone()[0]
        distinct_audit_recordings = conn.execute("SELECT COUNT(DISTINCT recording_id) FROM review_audit_log").fetchone()[0]

        # 4. Model evaluations in model_evaluations table
        eval_table_count = conn.execute("SELECT COUNT(*) FROM model_evaluations").fetchone()[0]
        eval_distinct_recordings = conn.execute("SELECT COUNT(DISTINCT recording_id) FROM model_evaluations").fetchone()[0]

        # 5. Model scores in candidates table
        with_model_score = conn.execute("SELECT COUNT(*) FROM candidates WHERE model_score IS NOT NULL").fetchone()[0]
        missing_model_score = conn.execute("SELECT COUNT(*) FROM candidates WHERE model_score IS NULL").fetchone()[0]

        # 6. Breakdown of missing scores: by has_audio and review_status
        missing_score_breakdown = conn.execute("""
            SELECT has_audio, review_status, COUNT(*) as cnt
            FROM candidates
            WHERE model_score IS NULL
            GROUP BY has_audio, review_status
        """).fetchall()

        # 7. Reviewed recordings with and without model score
        reviewed_without_score = conn.execute("""
            SELECT recording_id, source_provider, proposed_category, has_audio, review_status, download_validation_status
            FROM candidates
            WHERE review_status != 'UNREVIEWED' AND model_score IS NULL
        """).fetchall()

        # 8. Unreviewed recordings with and without model score
        unreviewed_missing_audio = conn.execute("""
            SELECT recording_id, source_provider, has_audio, review_status, model_score
            FROM candidates
            WHERE review_status = 'UNREVIEWED'
        """).fetchall()

    print("==================================================")
    print("STAGE 8.9.3 AUDIT: HUMAN LABELS & CLASSIFIER EVALUATIONS")
    print("==================================================")
    print(f"Total Candidates in Database       : {total_candidates}")
    print(f"Candidates with Audio (has_audio=1): {has_audio_count}")
    print(f"Candidates Missing Audio           : {missing_audio_count}")

    print("\n--- Human Review Decisions ---")
    for st, count in status_counts.items():
        print(f"  {st:<25}: {count}")

    total_human_decisions = sum(cnt for st, cnt in status_counts.items() if st != "UNREVIEWED")
    print(f"Total Reviewed Candidates          : {total_human_decisions}")
    print(f"Total Audit Log Entries            : {audit_log_count}")
    print(f"Distinct Recordings in Audit Log   : {distinct_audit_recordings}")

    print("\n--- Model Evaluations & Scores ---")
    print(f"Entries in model_evaluations table : {eval_table_count} (across {eval_distinct_recordings} distinct recordings)")
    print(f"Candidates with model_score        : {with_model_score}")
    print(f"Candidates with model_score IS NULL: {missing_model_score}")

    print("\n--- Missing Model Score Breakdown ---")
    for r in missing_score_breakdown:
        print(f"  has_audio={r['has_audio']}, review_status={r['review_status']}: {r['cnt']} recordings")

    print(f"\n--- Reviewed Recordings Missing Model Scores ({len(reviewed_without_score)} recordings) ---")
    for r in reviewed_without_score:
        print(f"  {r['recording_id']} ({r['source_provider']}, {r['proposed_category']}, has_audio={r['has_audio']}, status={r['review_status']})")

    print(f"\n--- Unreviewed Recordings ({len(unreviewed_missing_audio)} recordings) ---")
    for r in unreviewed_missing_audio[:5]:
        print(f"  {r['recording_id']} (has_audio={r['has_audio']}, status={r['review_status']}, score={r['model_score']})")
    if len(unreviewed_missing_audio) > 5:
        print(f"  ... and {len(unreviewed_missing_audio) - 5} more.")

    # 9. Check dashboard summary
    summary = store.get_summary()
    print("\n--- Dashboard Store Summary Counters ---")
    print(f"  total_candidates    : {summary['total_candidates']}")
    print(f"  audio_available     : {summary['audio_available']}")
    print(f"  reviewed_count      : {summary['reviewed_count']}")
    print(f"  pending_review      : {summary['pending_review']}")
    print(f"  approved_non_scream : {summary['approved_non_scream']}")
    print(f"  scream_present      : {summary['scream_present']}")
    print(f"  ambiguous           : {summary['ambiguous']}")
    print(f"  excluded            : {summary['excluded']}")
    print(f"  missing_audio       : {summary['missing_audio']}")
    print(f"  missing_model_scores: {summary['missing_model_scores']}")


if __name__ == "__main__":
    audit()
