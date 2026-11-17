"""Evaluate Acquired Hard Negatives with Frozen Stage 5 Classifier (Stage 8.8).

Runs:
1. Frozen artifact SHA-256 integrity verification.
2. Threshold immutability verification (0.35).
3. Audio feature extraction (YAMNet embeddings + max-pooling).
4. Frozen Logistic Regression probability estimation.
5. Emits `frozen_model_evaluation.json` and `artifact_integrity.json`.

Usage:
  python scripts/evaluate_acquired_negatives.py
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from src.config import STAGE8_8_REPORTS_DIR
from src.dataset.acquisition_client import AcquisitionPipeline
from src.dataset.acquisition_evaluator import (
    AcquiredAudioEvaluator,
    verify_frozen_model_artifacts,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("evaluate_acquired_negatives")


def main() -> int:
    print("=" * 80)
    print("STAGE 8.8 — FROZEN MODEL EVALUATION ON ACQUIRED NEGATIVES")
    print("=" * 80)

    # 1. Verify frozen model artifacts
    verified, audit = verify_frozen_model_artifacts()
    STAGE8_8_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    integrity_json = STAGE8_8_REPORTS_DIR / "artifact_integrity.json"
    with open(integrity_json, "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2)

    print(f"Classifier Hash Match: {audit['classifier_sha256_match']}")
    print(f"Metadata Hash Match  : {audit['metadata_sha256_match']}")
    print(f"Threshold Match      : {audit['threshold_match']} (Threshold: {audit['operating_threshold']})")
    print(f"Integrity Audit Saved: {integrity_json}")

    if not verified:
        print("[FATAL ERROR] Model artifact verification failed. Frozen baseline has been compromised!", file=sys.stderr)
        return 1

    # 2. Load candidates
    pipeline = AcquisitionPipeline()
    candidates = list(pipeline.candidates.values())
    if not candidates:
        print("[WARNING] No candidates found in manifest. Run download/discovery first.")
        return 1

    print(f"\nEvaluating {len(candidates)} candidates using frozen model...")
    evaluator = AcquiredAudioEvaluator()
    eval_results = evaluator.evaluate_all(candidates)

    # Save manifest with model scores
    pipeline.save_manifest()

    # Save evaluation report JSON
    eval_json = STAGE8_8_REPORTS_DIR / "frozen_model_evaluation.json"
    with open(eval_json, "w", encoding="utf-8") as f:
        json.dump(eval_results, f, indent=2)

    print("\n" + "=" * 80)
    print("FROZEN MODEL INFERENCE SUMMARY:")
    print(f"Total Clips Evaluated       : {eval_results['total_audio_clips_evaluated']}")
    print(f"Total Model Alerts (>= 0.35): {eval_results['total_model_alerts']}")
    print(f"Total Reviewed Non-Screams  : {eval_results['total_reviewed_non_scream']}")
    print(f"Confirmed False Positives   : {eval_results['total_confirmed_false_positives']}")
    print(f"Evaluation JSON Saved To    : {eval_json}")
    print("=" * 80)

    for cat, stats in eval_results["by_category"].items():
        if stats["total_audio_clips"] > 0:
            print(f"\nCategory: {cat}")
            print(f"  Clips Evaluated    : {stats['total_audio_clips']} ({stats['unique_source_groups']} unique sources)")
            print(f"  Model Alerts (0.35): {stats['model_alerts_at_0_35']}")
            print(f"  FPR (Reviewed)     : {stats['false_positive_rate_reviewed']}")
            dist = stats["score_distribution"]
            print(f"  Score Distribution : min={dist['min']}, max={dist['max']}, mean={dist['mean']}, median={dist['median']}")

    print("\n[NOTICE] Unreviewed model alerts highlight potential acoustic vulnerabilities for human inspection,")
    print("         and are NOT reported as confirmed false positives until human ground truth is assigned.")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
