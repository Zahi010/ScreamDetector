"""Stage 8.8 Hard-Negative Review Queue CLI.

Displays prioritized review queue sorted by:
1. Category Priority (Stage 8.7 gap rank)
2. License Confidence (CC0, CC BY first)
3. Audio Quality (Clean before flagged)
4. Duplicate Status (Unique before duplicate)
5. Model Scream Score (High score prioritized for review without automatic labeling)

Usage:
  python scripts/review_hard_negatives_queue.py --list
  python scripts/review_hard_negatives_queue.py --export-csv
  python scripts/review_hard_negatives_queue.py --approve <ID>
  python scripts/review_hard_negatives_queue.py --reject <ID> --note "Reason"
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from src.config import STAGE8_8_REPORTS_DIR
from src.dataset.acquisition_client import AcquisitionPipeline
from src.dataset.acquisition_reviewer import ReviewQueueManager
from src.dataset.acquisition_types import ReviewStatus

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("review_hard_negatives_queue")


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect and review Stage 8.8 candidate recordings.")
    parser.add_argument("--list", action="store_true", help="List prioritized review queue.")
    parser.add_argument("--export-csv", action="store_true", help="Export review_queue.csv to reports directory.")
    parser.add_argument("--approve", type=str, default=None, help="Recording ID to approve as verified non-scream.")
    parser.add_argument("--reject", type=str, default=None, help="Recording ID to reject or exclude.")
    parser.add_argument("--scream-present", type=str, default=None, help="Recording ID containing distress scream.")
    parser.add_argument("--ambiguous", type=str, default=None, help="Recording ID marked as acoustically ambiguous.")
    parser.add_argument("--note", type=str, default="", help="Reviewer note/rationale.")
    args = parser.parse_args()

    pipeline = AcquisitionPipeline()
    manager = ReviewQueueManager(pipeline.candidates)

    if args.approve:
        if manager.update_label(args.approve, ReviewStatus.APPROVED_NON_SCREAM.value, args.note):
            pipeline.save_manifest()
            print(f"[SUCCESS] Candidate '{args.approve}' marked as APPROVED_NON_SCREAM.")
            return 0
        return 1

    if args.reject:
        if manager.update_label(args.reject, ReviewStatus.EXCLUDED.value, args.note):
            pipeline.save_manifest()
            print(f"[SUCCESS] Candidate '{args.reject}' marked as EXCLUDED.")
            return 0
        return 1

    if args.scream_present:
        if manager.update_label(args.scream_present, ReviewStatus.SCREAM_PRESENT.value, args.note):
            pipeline.save_manifest()
            print(f"[SUCCESS] Candidate '{args.scream_present}' marked as SCREAM_PRESENT.")
            return 0
        return 1

    if args.ambiguous:
        if manager.update_label(args.ambiguous, ReviewStatus.AMBIGUOUS.value, args.note):
            pipeline.save_manifest()
            print(f"[SUCCESS] Candidate '{args.ambiguous}' marked as AMBIGUOUS.")
            return 0
        return 1

    queue = manager.get_sorted_queue()

    if args.export_csv or not args.list:
        csv_path = STAGE8_8_REPORTS_DIR / "review_queue.csv"
        manager.export_queue_csv(csv_path)
        print(f"Exported {len(queue)} queue records to {csv_path}")

    if args.list:
        print("=" * 110)
        print("STAGE 8.8 — HUMAN REVIEW QUEUE (SORTED BY PRIORITY)")
        print("=" * 110)
        print(f"{'Pos':<4} {'Recording ID':<22} {'Category':<24} {'License':<18} {'Status':<16} {'Model Score':<12}")
        print("-" * 110)
        for idx, c in enumerate(queue[:30], start=1):
            score_str = f"{c.model_score:.4f}" if c.model_score is not None else "N/A"
            if c.model_alert:
                score_str += " (!)"
            print(
                f"{idx:<4} {c.recording_id:<22} {c.proposed_category[:23]:<24} "
                f"{c.commercial_compatibility:<18} {c.review_status:<16} {score_str:<12}"
            )
        if len(queue) > 30:
            print(f"... and {len(queue) - 30} more candidates in review_queue.csv")
        print("=" * 110)

    return 0


if __name__ == "__main__":
    sys.exit(main())
