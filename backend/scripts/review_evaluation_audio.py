"""Human Labeling and Review Workflow CLI (Stage 8.6).

Provides an auditable tool for human verification of real-world evaluation recordings:
- Lists unreviewed and reviewed audio clips with acoustic metadata and file integrity.
- Audio playback support using sounddevice / winsound / system fallback.
- Explicit ground-truth assignment: 'scream', 'non_scream', 'ambiguous', 'exclude'.
- Appends every labeling action to label_review_audit.csv for full auditability.
- Updates recording_manifest.json and recording_manifest.csv.
- Supports exporting approved non_scream recordings into the Stage 6 hard-negative pool.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from src.config import (
    BACKEND_DIR,
    HARD_NEGATIVES_DIR,
    HARD_NEGATIVES_FALLBACK_DIR,
    RAW_DATASET_DIR,
    REAL_WORLD_EVAL_DIR,
    STAGE8_6_REPORTS_DIR,
)
from src.dataset.real_world import (
    ALLOWED_GROUND_TRUTH_LABELS,
    append_label_audit,
    export_reviewed_to_hard_negatives,
    load_recording_manifest,
    save_recording_manifests,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("review_evaluation_audio")


def play_audio_file(file_path: Path) -> None:
    """Play an audio file using available platform drivers."""
    if not file_path.exists():
        print(f"[ERROR] Audio file not found: {file_path}")
        return

    print(f"Playing '{file_path.name}'...")

    # 1. Try sounddevice & soundfile
    try:
        import sounddevice as sd
        import soundfile as sf
        data, fs = sf.read(str(file_path))
        sd.play(data, fs)
        sd.wait()
        print("Playback finished.")
        return
    except Exception as e:
        logger.debug(f"sounddevice playback unavailable: {e}")

    # 2. Try Windows winsound
    if sys.platform == "win32":
        try:
            import winsound
            winsound.PlaySound(str(file_path), winsound.SND_FILENAME)
            print("Playback finished.")
            return
        except Exception as e:
            logger.debug(f"winsound playback unavailable: {e}")

    # 3. Fallback: OS default player
    try:
        if sys.platform == "win32":
            os.startfile(str(file_path))
        else:
            import subprocess
            subprocess.run(["xdg-open", str(file_path)], check=True)
        print("Opened file with default OS audio player.")
    except Exception as e:
        print(f"[ERROR] Could not play audio file: {e}")


def display_recording_list(
    records: List[Dict[str, Any]],
    status_filter: Optional[str] = None,
) -> None:
    """Print tabular listing of recordings."""
    filtered = [r for r in records if (status_filter is None or r.get("ground_truth_label") == status_filter or r.get("label_status") == status_filter)]

    print("\n================================================================================")
    print(f"REAL-WORLD EVALUATION RECORDINGS (Total: {len(records)} | Displaying: {len(filtered)})")
    print("================================================================================")
    if not filtered:
        print("  No matching recordings found in manifest.")
        print("================================================================================\n")
        return

    print(f"{'ID':<25} | {'Label':<12} | {'Category':<15} | {'Duration':<8} | {'SR (Hz)':<7} | {'RMS':<8} | {'Notes'}")
    print("-" * 110)
    for r in filtered:
        rec_id = r.get("recording_id", "")[:25]
        label = r.get("ground_truth_label", "unlabeled")[:12]
        cat = r.get("sound_source_category", "other")[:15]
        dur = f"{r.get('duration_seconds', 0.0):.1f}s"
        sr = str(r.get("actual_sample_rate", 0))
        rms = f"{r.get('audio_rms', 0.0):.4f}"
        notes = (r.get("review_notes", "") or "")[:25]
        print(f"{rec_id:<25} | {label:<12} | {cat:<15} | {dur:<8} | {sr:<7} | {rms:<8} | {notes}")
    print("================================================================================\n")


def apply_label(
    records: List[Dict[str, Any]],
    recording_id: str,
    new_label: str,
    reviewer_id: str,
    notes: str,
    manifest_dir: Path,
    base_data_dir: Path,
) -> bool:
    """Assign ground-truth label, log to audit trail, and persist changes."""
    if new_label not in ALLOWED_GROUND_TRUTH_LABELS:
        print(f"[ERROR] Invalid label '{new_label}'. Allowed: {list(ALLOWED_GROUND_TRUTH_LABELS.keys())}")
        return False

    matching = [r for r in records if r.get("recording_id") == recording_id]
    if not matching:
        print(f"[ERROR] Recording ID '{recording_id}' not found in manifest.")
        return False

    rec = matching[0]
    old_label = rec.get("ground_truth_label", "unlabeled")
    rec["ground_truth_label"] = new_label
    rec["label_status"] = "unreviewed" if new_label == "unlabeled" else "reviewed"
    if notes:
        rec["review_notes"] = notes

    # Append to audit trail
    audit_csv = STAGE8_6_REPORTS_DIR / "label_review_audit.csv"
    append_label_audit(
        recording_id=recording_id,
        old_label=old_label,
        new_label=new_label,
        reviewer_id=reviewer_id,
        notes=notes,
        audit_csv_path=audit_csv,
    )

    # Save manifests
    save_recording_manifests(records, manifest_dir)
    save_recording_manifests(records, base_data_dir)

    # Also update sidecar JSON if it exists
    rel_path = rec.get("relative_audio_path", "")
    if rel_path:
        wav_path = base_data_dir / rel_path
        sidecar_path = wav_path.with_suffix(".json")
        if sidecar_path.exists():
            import json
            with open(sidecar_path, "w", encoding="utf-8") as f:
                json.dump(rec, f, indent=2)

    print(f"[SUCCESS] Label updated: '{recording_id}' -> '{new_label}' (Previous: '{old_label}')")
    print(f"          Audit entry written to: {audit_csv}")
    return True


def interactive_session(
    records: List[Dict[str, Any]],
    manifest_dir: Path,
    base_data_dir: Path,
    reviewer_id: str,
) -> None:
    """Run an interactive CLI labeling and listening session."""
    unreviewed = [r for r in records if r.get("label_status") == "unreviewed" or r.get("ground_truth_label") == "unlabeled"]
    print(f"\n[INTERACTIVE REVIEW MODE] Found {len(unreviewed)} unreviewed recordings.")

    if not unreviewed:
        print("All recordings have been reviewed! Exiting interactive session.")
        return

    for idx, r in enumerate(unreviewed, start=1):
        rec_id = r.get("recording_id", "")
        rel_path = r.get("relative_audio_path", "")
        audio_path = base_data_dir / rel_path

        print("\n" + "=" * 70)
        print(f"Recording [{idx}/{len(unreviewed)}]: {rec_id}")
        print(f"  Duration:     {r.get('duration_seconds')}s")
        print(f"  Sample Rate:  {r.get('actual_sample_rate')} Hz ({r.get('channel_count')} ch)")
        print(f"  Category:     {r.get('sound_source_category')} ({r.get('environment_category')})")
        print(f"  Device:       {r.get('recording_device_label')}")
        print(f"  RMS Level:    {r.get('audio_rms')} (Peak: {r.get('peak_amplitude')})")
        print(f"  Notes:        {r.get('review_notes')}")
        print("=" * 70)

        while True:
            choice = input("\nOptions: [p]lay, [s]cream, [n]on_scream, [a]mbiguous, [e]xclude, [skip], [q]uit: ").strip().lower()

            if choice in ("p", "play"):
                play_audio_file(audio_path)
            elif choice in ("s", "scream"):
                notes = input("Review notes (optional): ").strip()
                apply_label(records, rec_id, "scream", reviewer_id, notes, manifest_dir, base_data_dir)
                break
            elif choice in ("n", "non_scream"):
                notes = input("Review notes (optional): ").strip()
                apply_label(records, rec_id, "non_scream", reviewer_id, notes, manifest_dir, base_data_dir)
                break
            elif choice in ("a", "ambiguous"):
                notes = input("Reason for ambiguity: ").strip()
                apply_label(records, rec_id, "ambiguous", reviewer_id, notes, manifest_dir, base_data_dir)
                break
            elif choice in ("e", "exclude"):
                notes = input("Reason for exclusion: ").strip()
                apply_label(records, rec_id, "exclude", reviewer_id, notes, manifest_dir, base_data_dir)
                break
            elif choice in ("skip", ""):
                print(f"Skipped '{rec_id}'.")
                break
            elif choice in ("q", "quit", "exit"):
                print("Exiting interactive review.")
                return
            else:
                print("Invalid command. Choose 'p', 's', 'n', 'a', 'e', 'skip', or 'q'.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Human Audio Review & Ground-Truth Labeling CLI (Stage 8.6)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--manifest", type=str, default=str(STAGE8_6_REPORTS_DIR / "recording_manifest.json"), help="Path to recording manifest")
    parser.add_argument("--data-dir", type=str, default=str(REAL_WORLD_EVAL_DIR), help="Root directory containing audio files")
    parser.add_argument("--list", action="store_true", help="List all recordings in the manifest")
    parser.add_argument("--filter", type=str, default=None, choices=list(ALLOWED_GROUND_TRUTH_LABELS.keys()) + ["unreviewed", "reviewed"], help="Filter by label or review status")
    parser.add_argument("--play", type=str, default=None, help="Play audio clip by recording_id")
    parser.add_argument("--interactive", action="store_true", help="Launch interactive CLI review session")
    parser.add_argument("--reviewer", type=str, default="operator_1", help="Reviewer username/identifier")

    # Non-interactive labeling
    parser.add_argument("--label", type=str, default=None, help="Recording ID to label")
    parser.add_argument("--value", type=str, default=None, choices=list(ALLOWED_GROUND_TRUTH_LABELS.keys()), help="Ground-truth label value")
    parser.add_argument("--notes", type=str, default="", help="Review notes")

    # Hard-negative export
    parser.add_argument("--export-hard-negatives", action="store_true", help="Export approved non_scream clips to Stage 6 hard-negative pool")
    parser.add_argument("--hn-output-dir", type=str, default=str(HARD_NEGATIVES_FALLBACK_DIR), help="Target hard-negatives directory")

    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    base_data_dir = Path(args.data_dir)

    # If master manifest doesn't exist, check data_dir
    if not manifest_path.exists():
        fallback_manifest = base_data_dir / "recording_manifest.json"
        if fallback_manifest.exists():
            manifest_path = fallback_manifest

    records = load_recording_manifest(manifest_path)

    # 1. Export to Hard Negatives
    if args.export_hard_negatives:
        print("\n================================================================================")
        print("STAGE 8.6 -> STAGE 6: EXPORT TO HARD-NEGATIVE POOL")
        print("================================================================================")
        res = export_reviewed_to_hard_negatives(
            records=records,
            real_world_base_dir=base_data_dir,
            target_hn_dir=Path(args.hn_output_dir),
        )
        print(f"  Target Directory:  {res['target_directory']}")
        print(f"  Exported Clips:    {res['exported_count']}")
        print(f"  Skipped Clips:     {res['skipped_count']} (only reviewed 'non_scream' clips are eligible)")
        print("================================================================================\n")
        return

    # 2. Play Audio
    if args.play:
        matching = [r for r in records if r.get("recording_id") == args.play]
        if not matching:
            print(f"[ERROR] Recording ID '{args.play}' not found in manifest.")
            sys.exit(1)
        rel_path = matching[0].get("relative_audio_path", "")
        wav_path = base_data_dir / rel_path
        play_audio_file(wav_path)
        return

    # 3. Non-interactive labeling
    if args.label:
        if not args.value:
            print("[ERROR] Must provide --value <label> when using --label <id>.")
            sys.exit(1)
        success = apply_label(
            records=records,
            recording_id=args.label,
            new_label=args.value,
            reviewer_id=args.reviewer,
            notes=args.notes,
            manifest_dir=manifest_path.parent,
            base_data_dir=base_data_dir,
        )
        sys.exit(0 if success else 1)

    # 4. Interactive review session
    if args.interactive:
        interactive_session(
            records=records,
            manifest_dir=manifest_path.parent,
            base_data_dir=base_data_dir,
            reviewer_id=args.reviewer,
        )
        return

    # Default: List recordings
    display_recording_list(records, status_filter=args.filter)


if __name__ == "__main__":
    main()
