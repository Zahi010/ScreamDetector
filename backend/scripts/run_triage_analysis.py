"""Stage 8.9.1 Automated Hard-Negative Triage CLI for Festival Scream Detector.

Executes acoustic analysis and recommendation categorization across candidate recordings:
1. Verifies frozen classifier and metadata SHA-256 hashes.
2. Performs signal quality checks (duration, digital clipping, silence ratio).
3. Executes frozen scream classifier inference at threshold 0.35.
4. Profiles YAMNet 521 AudioSet class probabilities and detects key indicator classes:
   - crying, infant crying, screaming, shouting, sirens, whistles, cheering, applause, electronic music, squeaks, speech.
5. Deterministically maps candidates to transparent triage groups:
   - LIKELY_NON_SCREAM: strong alternative evidence, weak scream evidence.
   - POSSIBLE_SCREAM: high classifier score with consistent scream evidence.
   - AMBIGUOUS: conflicting evidence or infant distress acoustics.
   - REVIEW_REQUIRED: missing audio, severe clipping, near-silence, or decode error.
6. Updates SQLite store idempotently and outputs a comprehensive diagnostic audit.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from src.database.review_store import get_review_store
from src.dataset.acquisition_evaluator import (
    EXPECTED_CLASSIFIER_SHA256,
    EXPECTED_METADATA_SHA256,
    FROZEN_THRESHOLD,
    verify_frozen_model_artifacts,
)
from src.dataset.triage_analyzer import (
    AutomatedTriageEngine,
    TriageAnalysisResult,
    TriageGroup,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("triage_cli")


def run_triage(
    batch_size: int = 500,
    force_recompute: bool = False,
    recording_id: str | None = None,
) -> int:
    """Run automated triage analysis on review candidates."""
    print("=" * 80)
    print("STAGE 8.9.1: AUTOMATED HARD-NEGATIVE TRIAGE ENGINE")
    print("=" * 80)

    # 1. Verify frozen model artifacts before running
    verified, audit = verify_frozen_model_artifacts()
    if not verified:
        print(f"[FATAL ERROR] Model artifact verification failed: {audit}")
        return 1

    print(f"[OK] Frozen classifier verified (SHA256: {EXPECTED_CLASSIFIER_SHA256[:16]}...)")
    print(f"[OK] Frozen metadata verified   (SHA256: {EXPECTED_METADATA_SHA256[:16]}...)")
    print(f"[OK] Frozen threshold: {FROZEN_THRESHOLD}")

    store = get_review_store()
    print("[INFO] Initializing AutomatedTriageEngine with YAMNet and Frozen Classifier...")
    engine = AutomatedTriageEngine()
    print("[OK] Triage Engine initialized.")

    with store._get_connection() as conn:
        if recording_id:
            query = "SELECT recording_id, local_path, has_audio, proposed_category FROM candidates WHERE recording_id = ?"
            params = (recording_id,)
        elif not force_recompute:
            query = "SELECT recording_id, local_path, has_audio, proposed_category FROM candidates ORDER BY has_audio DESC, recording_id ASC LIMIT ?"
            params = (batch_size,)
        else:
            query = "SELECT recording_id, local_path, has_audio, proposed_category FROM candidates ORDER BY has_audio DESC, recording_id ASC LIMIT ?"
            params = (batch_size,)

        rows = conn.execute(query, params).fetchall()

    total_candidates = len(rows)
    print(f"[INFO] Processing {total_candidates} candidates for triage analysis...")

    start_time = time.time()
    triaged_count = 0
    failure_count = 0
    group_counts = {
        TriageGroup.LIKELY_NON_SCREAM.value: 0,
        TriageGroup.POSSIBLE_SCREAM.value: 0,
        TriageGroup.AMBIGUOUS.value: 0,
        TriageGroup.REVIEW_REQUIRED.value: 0,
    }

    for idx, r in enumerate(rows, 1):
        rec_id = r["recording_id"]
        has_audio = bool(r["has_audio"])
        category = r["proposed_category"]

        audio_path = store.get_secure_audio_path(rec_id) if has_audio else None

        if audio_path and audio_path.is_file():
            try:
                res = engine.analyze_audio_file(audio_path, recording_id=rec_id)
            except Exception as exc:
                logger.error("Exception during triage analysis of '%s': %s", rec_id, exc)
                failure_count += 1
                res = TriageAnalysisResult(
                    recording_id=rec_id,
                    triage_group=TriageGroup.REVIEW_REQUIRED.value,
                    triage_reason=f"Processing exception: {exc}",
                    classifier_score=None,
                    is_classifier_alert=None,
                    has_audio=True,
                    status=f"ERROR: {exc}",
                )
        else:
            res = TriageAnalysisResult(
                recording_id=rec_id,
                triage_group=TriageGroup.REVIEW_REQUIRED.value,
                triage_reason="Audio file not found on local disk.",
                classifier_score=None,
                is_classifier_alert=None,
                has_audio=False,
                status="FILE_NOT_FOUND",
            )

        store.save_triage_result(res)
        triaged_count += 1
        group_counts[res.triage_group] = group_counts.get(res.triage_group, 0) + 1

        if idx % 25 == 0 or idx == total_candidates:
            elapsed = time.time() - start_time
            rate = idx / elapsed if elapsed > 0 else 0
            print(f"  [{idx:3d}/{total_candidates:3d}] Triaged ({rate:.1f} clips/s) | Last: {rec_id} -> {res.triage_group}")

    elapsed = time.time() - start_time

    # Re-verify frozen model artifacts after execution
    verified_after, audit_after = verify_frozen_model_artifacts()
    if not verified_after:
        print(f"[FATAL INTEGRITY VIOLATION] Model artifacts altered during triage: {audit_after}")
        return 2

    print("\n" + "=" * 80)
    print("STAGE 8.9.1 AUTOMATED TRIAGE REPORT")
    print("=" * 80)
    print(f"Total Recordings Processed:      {triaged_count}")
    print(f"Analysis Failures / Exceptions:  {failure_count}")
    print(f"Total Elapsed Time:             {elapsed:.2f} s")
    print("-" * 80)
    print("TRIAGE GROUP DISTRIBUTION:")
    for grp, cnt in group_counts.items():
        pct = (cnt / triaged_count * 100) if triaged_count > 0 else 0.0
        print(f"  {grp:<20} : {cnt:4d} ({pct:5.1f}%)")
    print("-" * 80)
    print(f"Classifier SHA-256 Before/After: {EXPECTED_CLASSIFIER_SHA256[:20]}... [UNCHANGED]")
    print(f"Metadata SHA-256 Before/After:   {EXPECTED_METADATA_SHA256[:20]}... [UNCHANGED]")
    print(f"Operating Threshold:             {FROZEN_THRESHOLD} [UNCHANGED]")
    print("=" * 80)
    print("Triage recommendations are now stored in the SQLite database.")
    print("The Human Review Studio dashboard will now display triage categories and allow sorting Likely Non-Screams first.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Stage 8.9.1 Automated Triage")
    parser.add_argument("--batch-size", type=int, default=500, help="Number of recordings to triage")
    parser.add_argument("--force", action="store_true", help="Force recomputation of all recordings")
    parser.add_argument("--recording-id", type=str, default=None, help="Specific recording ID to triage")
    args = parser.parse_args()

    sys.exit(run_triage(batch_size=args.batch_size, force_recompute=args.force, recording_id=args.recording_id))
