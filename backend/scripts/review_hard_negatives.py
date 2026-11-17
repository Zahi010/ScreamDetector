"""Human Review and Labeling CLI Workflow for Hard Negatives (Stage 6).

Provides an auditable command-line interface to inspect, classify, approve,
or reject candidate audio recordings for festival scream detection.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from src.config import HARD_NEGATIVES_MANIFEST, HARD_NEGATIVES_REVIEW_CSV
from src.dataset.hard_negatives import (
    HARD_NEGATIVE_CATEGORIES,
    REVIEW_STATUSES,
    save_hard_negatives_manifest,
)

LABELING_GUIDE = """
========================================================================================
FESTIVAL SCREAM DETECTOR — ACOUSTIC LABELING & REVIEW GUIDE
========================================================================================

1. GENUINE DISTRESS SCREAM (`approved_scream`):
   - Vocal characteristics: High pitch, sudden explosive onset, turbulent vocal tract noise,
     subharmonic bifurcation, erratic frequency modulation, wide formant dispersion.
   - Emotional context: Fear, pain, panic, or acute distress.
   - Decision rule: Label as 'approved_scream' if the vocal energy clearly exhibits
     physical distress strain. If in doubt, mark as 'rejected_ambiguous'.

2. NON-DISTRESS CHEERING OR CELEBRATORY SHOUTING (`approved_non_scream`):
   - Vocal characteristics: Periodic harmonic structure, rising intonation, collective choral
     reverberation, rhythmic chanting, absence of physical distress bifurcation.
   - Typical festival contexts: Crowd roar at stage drop, sporting cheers, 'woo-hoo' yells.
   - Decision rule: Label as 'approved_non_scream'. These are critical hard negatives
     to prevent false alarms during high-energy musical climaxes.

3. CRYING, LAUGHTER & NON-SCREAM VOCALIZATIONS (`approved_non_scream`):
   - Vocal characteristics: Rhythmic glottal stops (laughter), sobbing intake of breath (crying),
     low-pitch groans, speech shouts.
   - Decision rule: Label as 'approved_non_scream'. Infant crying in particular shares
     acoustic properties with screams; verify carefully.

4. NON-VOCAL SCREAM-LIKE SOUNDS (`approved_non_scream`):
   - Acoustic types: Referee whistles, rave vuvuzelas, synthesizer resonance sweeps,
     slide whistles, squeaky toys, ambulance sirens, microphone feedback squeals.
   - Decision rule: Label as 'approved_non_scream'. These represent critical non-vocal
     distractors that frequently cause false positives in general audio classifiers.

5. AMBIGUOUS OR MIXED RECORDINGS (`rejected_ambiguous`):
   - Cases:
     * Euphoric screams on rollercoasters or dancefloors where acoustic intent is undecidable.
     * Overlapping mixtures where screams cannot be separated from loud music.
     * Recordings with dubious permissions, missing license provenance, or copyright tags.
   - Decision rule: Label as 'rejected_ambiguous'. These are strictly excluded from
     both positive and negative training partitions to preserve ground truth integrity.

* TASK DEFINITION LIMITATION NOTE:
  Acoustically distinguishing high-arousal joyful screams from high-arousal distress screams
  can be fundamentally ambiguous without visual or contextual evidence. When audio alone
  cannot disambiguate valence, the clip MUST be labeled 'rejected_ambiguous'.
========================================================================================
"""


def load_manifest(manifest_path: Path) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Load hard-negatives manifest data."""
    if not manifest_path.exists():
        return {"metadata": {"total_records": 0}}, []
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("metadata", {}), data.get("records", [])


def print_record_table(records: List[Dict[str, Any]], status_filter: Optional[str] = None) -> None:
    """Print formatted summary table of records."""
    filtered = [r for r in records if status_filter is None or r.get("review_status") == status_filter]
    if not filtered:
        print(f"No records found matching status filter '{status_filter}'.")
        return

    print("-" * 105)
    print(f"{'File ID':<38} {'Category':<20} {'Duration':<10} {'Status':<22} {'License':<12}")
    print("-" * 105)
    for r in filtered:
        dur_str = f"{r.get('duration_seconds', 0.0):.2f}s"
        lic_str = r.get("license", "Unknown")[:12]
        print(
            f"{r['file_id']:<38} {r.get('sound_category', ''):<20} "
            f"{dur_str:<10} {r.get('review_status', ''):<22} {lic_str:<12}"
        )
    print("-" * 105)
    print(f"Total matching records: {len(filtered)}\n")


def update_record_status(
    records: List[Dict[str, Any]],
    file_id: str,
    new_status: str,
    reviewer_note: str = "",
    reviewer_id: str = "human_reviewer",
) -> bool:
    """Update review status of a specific record by file_id."""
    for r in records:
        if r["file_id"] == file_id or r.get("original_filename") == file_id:
            r["review_status"] = new_status
            r["reviewed_at"] = datetime.now().isoformat()
            r["reviewer_id"] = reviewer_id
            if reviewer_note:
                r["reviewer_notes"] = reviewer_note
            return True
    return False


def run_interactive_review(
    records: List[Dict[str, Any]],
    manifest_path: Path,
    csv_path: Path,
) -> None:
    """Run interactive terminal-based review session for pending clips."""
    pending = [r for r in records if r.get("review_status") == "pending_review"]
    if not pending:
        print("No recordings are currently pending review.")
        return

    print(f"\nStarting interactive review for {len(pending)} pending recordings.")
    print("Commands: [1] Non-Scream  [2] Genuine Scream  [3] Reject/Ambiguous  [S] Skip  [Q] Save & Quit\n")

    reviewed_count = 0
    for idx, r in enumerate(pending, 1):
        print("=" * 80)
        print(f"[{idx}/{len(pending)}] Candidate: {r['original_filename']}")
        print(f"  - File ID:         {r['file_id']}")
        print(f"  - Category:        {r.get('sound_category')}")
        print(f"  - Source Group:    {r.get('source_group_id')}")
        print(f"  - Duration:        {r.get('duration_seconds')} seconds")
        print(f"  - License:         {r.get('license')} (Commercial Permitted: {r.get('commercial_use_permitted')})")
        print(f"  - Local Path:      {r.get('source_path')}")
        print("=" * 80)

        while True:
            try:
                choice = input("Enter decision [1=Non-Scream, 2=Scream, 3=Ambiguous, S=Skip, Q=Quit]: ").strip().upper()
            except (EOFError, KeyboardInterrupt):
                choice = "Q"

            if choice == "1":
                r["review_status"] = "approved_non_scream"
                r["reviewed_at"] = datetime.now().isoformat()
                r["reviewer_id"] = "cli_reviewer"
                r["reviewer_notes"] = "Approved as non-scream distractor."
                reviewed_count += 1
                break
            elif choice == "2":
                r["review_status"] = "approved_scream"
                r["reviewed_at"] = datetime.now().isoformat()
                r["reviewer_id"] = "cli_reviewer"
                r["reviewer_notes"] = "Approved as genuine scream."
                reviewed_count += 1
                break
            elif choice == "3":
                r["review_status"] = "rejected_ambiguous"
                r["reviewed_at"] = datetime.now().isoformat()
                r["reviewer_id"] = "cli_reviewer"
                r["reviewer_notes"] = "Rejected as acoustically ambiguous or mixed."
                reviewed_count += 1
                break
            elif choice == "S":
                print("Skipped.")
                break
            elif choice == "Q":
                print("\nSaving and quitting...")
                save_hard_negatives_manifest(records, manifest_path, csv_path)
                print(f"Saved {reviewed_count} decisions to {manifest_path}.")
                return
            else:
                print("Invalid input. Please enter 1, 2, 3, S, or Q.")

    save_hard_negatives_manifest(records, manifest_path, csv_path)
    print(f"\n[DONE] Reviewed {reviewed_count} records. Updated manifests saved successfully.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Review and label candidate hard-negative audio clips.")
    parser.add_argument("--guide", action="store_true", help="Display the acoustic labeling guidelines.")
    parser.add_argument("--list", action="store_true", help="List all tracked hard-negative records.")
    parser.add_argument("--status", type=str, default=None, choices=list(REVIEW_STATUSES.keys()), help="Filter --list by status.")
    parser.add_argument("--interactive", action="store_true", help="Start interactive review session for pending recordings.")
    parser.add_argument("--approve", type=str, default=None, help="File ID or filename to approve.")
    parser.add_argument("--as-label", type=str, default="non_scream", choices=["non_scream", "scream"], help="Approval target.")
    parser.add_argument("--reject", type=str, default=None, help="File ID or filename to mark as rejected_ambiguous.")
    parser.add_argument("--note", type=str, default="", help="Reviewer note to record.")
    args = parser.parse_args()

    if args.guide:
        print(LABELING_GUIDE)
        return 0

    manifest_path = HARD_NEGATIVES_MANIFEST
    csv_path = HARD_NEGATIVES_REVIEW_CSV
    meta, records = load_manifest(manifest_path)

    if args.list:
        print("\nStage 6 Hard Negatives Review Status:")
        print_record_table(records, status_filter=args.status)

        # Also display Stage 8.8 queue if present
        from src.config import STAGE8_8_MANIFEST_JSON
        if STAGE8_8_MANIFEST_JSON.exists():
            try:
                with open(STAGE8_8_MANIFEST_JSON, "r", encoding="utf-8") as f:
                    s88_data = json.load(f)
                    s88_cands = s88_data.get("candidates", [])
                    print("\n" + "=" * 95)
                    print(f"STAGE 8.8 ACQUIRED HARD NEGATIVES REVIEW QUEUE ({len(s88_cands)} candidates tracked):")
                    print("=" * 95)
                    print(f"{'Recording ID':<22} {'Category':<24} {'License':<18} {'Status':<16} {'Model Score':<10}")
                    print("-" * 95)
                    for c in s88_cands[:20]:
                        score_str = f"{c.get('model_score'):.4f}" if c.get("model_score") is not None else "N/A"
                        print(f"{c.get('recording_id', '')[:20]:<22} {c.get('proposed_category', '')[:22]:<24} {c.get('commercial_compatibility', '')[:16]:<18} {c.get('review_status', ''):<16} {score_str:<10}")
                    if len(s88_cands) > 20:
                        print(f"... and {len(s88_cands) - 20} more candidates in review_queue.csv")
                    print("=" * 95)
            except Exception as e:
                print(f"[Note] Could not read Stage 8.8 manifest: {e}")
        return 0

    if args.approve:
        target_status = "approved_scream" if args.as_label == "scream" else "approved_non_scream"
        if update_record_status(records, args.approve, target_status, reviewer_note=args.note):
            save_hard_negatives_manifest(records, manifest_path, csv_path)
            print(f"[SUCCESS] Updated '{args.approve}' -> '{target_status}'. Manifest saved.")
            return 0
        else:
            print(f"[ERROR] Record '{args.approve}' not found in manifest.", file=sys.stderr)
            return 1

    if args.reject:
        if update_record_status(records, args.reject, "rejected_ambiguous", reviewer_note=args.note):
            save_hard_negatives_manifest(records, manifest_path, csv_path)
            print(f"[SUCCESS] Updated '{args.reject}' -> 'rejected_ambiguous'. Manifest saved.")
            return 0
        else:
            print(f"[ERROR] Record '{args.reject}' not found in manifest.", file=sys.stderr)
            return 1

    if args.interactive:
        run_interactive_review(records, manifest_path, csv_path)
        return 0

    # Default action: show summary & guide reminder
    print("=" * 75)
    print("STAGE 6 — HARD-NEGATIVE REVIEW CLI")
    print("=" * 75)
    print(f"Manifest: {manifest_path}")
    print(f"Total Tracked Records: {len(records)}")
    status_summary = {k: sum(1 for r in records if r.get("review_status") == k) for k in REVIEW_STATUSES}
    for k, v in status_summary.items():
        print(f"  - {k:<22}: {v}")
    print("\nUsage Options:")
    print("  python scripts/review_hard_negatives.py --guide        (View acoustic labeling guide)")
    print("  python scripts/review_hard_negatives.py --list         (List all tracked records)")
    print("  python scripts/review_hard_negatives.py --interactive  (Review pending recordings step-by-step)")
    print("  python scripts/review_hard_negatives.py --approve <ID> --as-label [non_scream|scream]")
    print("  python scripts/review_hard_negatives.py --reject <ID>  --note \"Reason\"")
    print("=" * 75)
    return 0


if __name__ == "__main__":
    sys.exit(main())
