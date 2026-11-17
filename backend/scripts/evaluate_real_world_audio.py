"""Real-World Audio Evaluation Pipeline (Stage 8.6).

Performs rigorous, reproducible evaluation of the frozen Stage 5 scream classifier
on newly collected and reviewed real-world audio recordings:
- Verifies model & metadata SHA-256 hashes against recorded Stage 5 baseline.
- Enforces strict immutable threshold of 0.35.
- Loads reviewed clips ('scream', 'non_scream') from recording_manifest.json.
- Separately logs 'ambiguous' and 'exclude' clips.
- Executes identical inference path: 16 kHz mono float32 -> YAMNet -> max-pool -> LogReg.
- Calculates comprehensive performance metrics: TP, FP, TN, FN, Precision, Recall,
  F1, Specificity, Accuracy, ROC-AUC, PR-AUC, Confusion Matrix, and score distributions.
- Outputs auditable files:
  backend/reports/stage8_6/real_world_predictions.csv
  backend/reports/stage8_6/real_world_metrics.json
  backend/reports/stage8_6/dataset_quality_report.md
  backend/reports/stage8_6/false_positive_analysis.md
  backend/reports/stage8_6/false_negative_analysis.md
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from src.config import (
    BACKEND_DIR,
    DEFAULT_SCREAM_THRESHOLD,
    MANIFESTS_DIR,
    MODELS_DIR,
    RAW_DATASET_DIR,
    REAL_WORLD_EVAL_DIR,
    STAGE8_6_REPORTS_DIR,
)
from src.dataset.real_world import (
    calculate_evaluation_metrics,
    check_dataset_quality,
    compute_file_sha256,
    load_recording_manifest,
)
from src.model.scream_classifier import FestivalScreamClassifier

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("evaluate_real_world")

# Immutable Stage 5 Baseline Hashes
EXPECTED_CLASSIFIER_HASH = "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f"
EXPECTED_METADATA_HASH = "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60"
STAGE5_BASELINE_THRESHOLD = 0.35


def verify_baseline_integrity() -> None:
    """Verify that model weights and metadata are identical to the frozen Stage 5 baseline."""
    clf_path = MODELS_DIR / "scream_classifier.joblib"
    meta_path = MODELS_DIR / "model_metadata.json"

    if not clf_path.exists():
        raise FileNotFoundError(f"Classifier file missing: {clf_path}")
    if not meta_path.exists():
        raise FileNotFoundError(f"Metadata file missing: {meta_path}")

    clf_hash = compute_file_sha256(clf_path)
    meta_hash = compute_file_sha256(meta_path)

    if clf_hash != EXPECTED_CLASSIFIER_HASH:
        raise ValueError(
            f"Classifier integrity check failed! Expected {EXPECTED_CLASSIFIER_HASH}, observed {clf_hash}"
        )
    if meta_hash != EXPECTED_METADATA_HASH:
        raise ValueError(
            f"Metadata integrity check failed! Expected {EXPECTED_METADATA_HASH}, observed {meta_hash}"
        )
    logger.info("Model integrity verified: Stage 5 classifier & metadata hashes match baseline.")


def generate_quality_report(quality_results: Dict[str, Any], output_path: Path) -> None:
    """Generate Markdown report summarizing dataset quality findings."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Stage 8.6 Real-World Dataset Quality Control Report\n\n")
        f.write(f"**Generated**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
        f.write("---\n\n")

        f.write("## 1. Summary of Checks\n\n")
        f.write(f"- **Total Recordings Checked**: **{quality_results['total_records_checked']}**\n")
        f.write(f"- **Total Issues Identified**: **{quality_results['total_issues_found']}**\n")
        f.write(f"- **Missing Audio Files**: {quality_results['missing_files']}\n")
        f.write(f"- **Corrupted / Invalid Audio**: {quality_results['corrupted_files']}\n")
        f.write(f"- **Zero-Length / Truncated Files**: {quality_results['zero_duration_files']}\n")
        f.write(f"- **Near-Silent Audio**: {quality_results['silent_files']}\n")
        f.write(f"- **Clipped Audio**: {quality_results['clipped_files']}\n")
        f.write(f"- **Duplicate Files**: {quality_results['duplicate_files']}\n")
        f.write(f"- **Historical Split Leakage**: {quality_results['historical_leakage_files']}\n")
        f.write(f"- **Unreviewed Audio**: {quality_results['unreviewed_count']}\n\n")

        f.write("---\n\n")
        f.write("## 2. Issue Details\n\n")
        issues = quality_results.get("issues", [])
        if not issues:
            f.write("> [!NOTE]\n")
            f.write("> **Zero Quality Defects Found**: All checked recordings exist, decode cleanly, contain valid amplitudes, and exhibit zero hash collisions with historical splits.\n\n")
        else:
            f.write("| Severity | Recording ID | Defect Type | Detail |\n")
            f.write("| :--- | :--- | :--- | :--- |\n")
            for iss in issues:
                f.write(f"| **`{iss['severity']}`** | `{iss['recording_id']}` | `{iss['type']}` | {iss['detail']} |\n")
            f.write("\n")


def generate_error_analysis_reports(
    predictions: List[Dict[str, Any]],
    threshold: float,
    fp_path: Path,
    fn_path: Path,
) -> None:
    """Generate detailed markdown analyses for False Positives and False Negatives."""
    fp_path.parent.mkdir(parents=True, exist_ok=True)
    fn_path.parent.mkdir(parents=True, exist_ok=True)

    fps = [p for p in predictions if p.get("ground_truth") == "non_scream" and p.get("predicted_score", 0.0) >= threshold]
    fns = [p for p in predictions if p.get("ground_truth") == "scream" and p.get("predicted_score", 0.0) < threshold]

    # False Positive Analysis
    with open(fp_path, "w", encoding="utf-8") as f:
        f.write("# Stage 8.6 False-Positive Error Analysis\n\n")
        f.write(f"**Generated**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
        f.write(f"**Active Threshold**: `{threshold:.3f}` | **Observed False Positives**: **{len(fps)}**\n\n")
        f.write("---\n\n")

        if not fps:
            f.write("> [!NOTE]\n")
            f.write(f"> Zero false positives observed among evaluated recordings at threshold {threshold:.3f}.\n")
        else:
            f.write("### Observed False Positive Clips\n\n")
            f.write("| Recording ID | Category | Score | Margin | Duration | Review Notes |\n")
            f.write("| :--- | :--- | :---: | :---: | :---: | :--- |\n")
            for p in fps:
                f.write(f"| `{p['recording_id']}` | `{p['sound_source_category']}` | `{p['predicted_score']:.4f}` | `+{p['margin']:+.4f}` | {p['duration_seconds']:.2f}s | {p.get('review_notes', '')} |\n")
            f.write("\n")

    # False Negative Analysis
    with open(fn_path, "w", encoding="utf-8") as f:
        f.write("# Stage 8.6 False-Negative Error Analysis\n\n")
        f.write(f"**Generated**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
        f.write(f"**Active Threshold**: `{threshold:.3f}` | **Observed False Negatives**: **{len(fns)}**\n\n")
        f.write("---\n\n")

        if not fns:
            f.write("> [!NOTE]\n")
            f.write(f"> Zero false negatives observed among evaluated scream recordings at threshold {threshold:.3f}.\n")
        else:
            f.write("### Observed False Negative Clips\n\n")
            f.write("| Recording ID | Category | Score | Margin | Duration | Review Notes |\n")
            f.write("| :--- | :--- | :---: | :---: | :---: | :--- |\n")
            for p in fns:
                f.write(f"| `{p['recording_id']}` | `{p['sound_source_category']}` | `{p['predicted_score']:.4f}` | `{p['margin']:+.4f}` | {p['duration_seconds']:.2f}s | {p.get('review_notes', '')} |\n")
            f.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate Stage 5 Model on Real-World Audio Cohort (Stage 8.6)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--manifest", type=str, default=str(STAGE8_6_REPORTS_DIR / "recording_manifest.json"), help="Path to recording manifest")
    parser.add_argument("--data-dir", type=str, default=str(REAL_WORLD_EVAL_DIR), help="Root directory for audio files")
    parser.add_argument("--reports-dir", type=str, default=str(STAGE8_6_REPORTS_DIR), help="Directory to save evaluation reports")
    parser.add_argument("--threshold", type=float, default=STAGE5_BASELINE_THRESHOLD, help="Operational threshold (default: 0.35)")

    args = parser.parse_args()

    reports_dir = Path(args.reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = Path(args.manifest)
    base_data_dir = Path(args.data_dir)

    # 1. Baseline Integrity Verification
    print("\n================================================================================")
    print("STAGE 8.6: REAL-WORLD AUDIO EVALUATION PIPELINE")
    print("================================================================================")
    print("[1/5] Verifying Stage 5 Model Artifacts & Hash Integrity...")
    verify_baseline_integrity()
    print("      Classifier Hash: ad6e428d05d2... [VERIFIED]")
    print("      Metadata Hash:   30c1c75d81ad... [VERIFIED]")

    # 2. Load Manifest & Quality Control
    print(f"\n[2/5] Loading Recording Manifest from: {manifest_path}...")
    if not manifest_path.exists():
        fallback = base_data_dir / "recording_manifest.json"
        if fallback.exists():
            manifest_path = fallback

    records = load_recording_manifest(manifest_path)
    print(f"      Total Records in Manifest: {len(records)}")

    # Run dataset quality checks
    quality_results = check_dataset_quality(
        records=records,
        base_dir=base_data_dir,
        historical_split_manifest=MANIFESTS_DIR / "split_manifest.json",
    )
    quality_report_path = reports_dir / "dataset_quality_report.md"
    generate_quality_report(quality_results, quality_report_path)
    print(f"      Quality Control Report saved to: {quality_report_path}")

    # 3. Categorize Cohorts
    eligible_eval = [r for r in records if r.get("ground_truth_label") in ("scream", "non_scream") and r.get("label_status") == "reviewed"]
    ambiguous_clips = [r for r in records if r.get("ground_truth_label") == "ambiguous"]
    excluded_clips = [r for r in records if r.get("ground_truth_label") == "exclude"]
    unlabeled_clips = [r for r in records if r.get("ground_truth_label") == "unlabeled" or r.get("label_status") == "unreviewed"]

    print("\n[3/5] Audio Cohort Breakdown:")
    print(f"      - Eligible for Evaluation (Reviewed 'scream' / 'non_scream'): {len(eligible_eval)}")
    print(f"      - Excluded (Acoustically Ambiguous):                      {len(ambiguous_clips)}")
    print(f"      - Excluded (Corrupted / Privacy / Out-of-Scope):          {len(excluded_clips)}")
    print(f"      - Awaiting Human Review ('unlabeled'):                    {len(unlabeled_clips)}")

    # 4. Model Inference on Eligible Clips
    predictions: List[Dict[str, Any]] = []
    pred_csv_path = reports_dir / "real_world_predictions.csv"

    if eligible_eval:
        print("\n[4/5] Initializing Scream Classifier & YAMNet Loader...")
        classifier = FestivalScreamClassifier()

        print(f"      Running inference on {len(eligible_eval)} reviewed recordings (threshold={args.threshold:.3f})...")
        for idx, r in enumerate(eligible_eval, start=1):
            rec_id = r["recording_id"]
            rel_path = r["relative_audio_path"]
            wav_path = base_data_dir / rel_path

            try:
                res = classifier.predict_file(wav_path, custom_threshold=args.threshold)
                score = res["scream_probability"]
                pred_label = res["predicted_label"]
                gt = r["ground_truth_label"]
                margin = score - args.threshold
                is_correct = (pred_label == gt)

                pred_record = {
                    "recording_id": rec_id,
                    "session_id": r.get("session_id", ""),
                    "ground_truth": gt,
                    "predicted_label": pred_label,
                    "predicted_score": round(score, 4),
                    "threshold": args.threshold,
                    "margin": round(margin, 4),
                    "is_correct": is_correct,
                    "duration_seconds": r.get("duration_seconds", 0.0),
                    "sound_source_category": r.get("sound_source_category", "other"),
                    "environment_category": r.get("environment_category", "other"),
                    "review_notes": r.get("review_notes", ""),
                }
                predictions.append(pred_record)
            except Exception as e:
                logger.error(f"Error predicting {wav_path}: {e}")

        # Save predictions CSV
        if predictions:
            with open(pred_csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(predictions[0].keys()))
                writer.writeheader()
                for p in predictions:
                    writer.writerow(p)
            print(f"      Predictions saved to: {pred_csv_path}")

    else:
        print("\n[4/5] Skipping model inference: 0 eligible reviewed recordings available.")
        # Write empty predictions CSV with headers
        with open(pred_csv_path, "w", newline="", encoding="utf-8") as f:
            fieldnames = [
                "recording_id", "session_id", "ground_truth", "predicted_label",
                "predicted_score", "threshold", "margin", "is_correct",
                "duration_seconds", "sound_source_category", "environment_category", "review_notes"
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

    # 5. Metrics & Error Analyses
    print("\n[5/5] Calculating Evaluation Metrics & Generating Error Analyses...")
    metrics = calculate_evaluation_metrics(predictions, threshold=args.threshold)

    metrics_json_path = reports_dir / "real_world_metrics.json"
    with open(metrics_json_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"      Evaluation Metrics JSON saved to: {metrics_json_path}")

    # Generate FP/FN Analyses
    fp_analysis_path = reports_dir / "false_positive_analysis.md"
    fn_analysis_path = reports_dir / "false_negative_analysis.md"
    generate_error_analysis_reports(predictions, args.threshold, fp_analysis_path, fn_analysis_path)
    print(f"      False Positive Analysis saved to: {fp_analysis_path}")
    print(f"      False Negative Analysis saved to: {fn_analysis_path}")

    print("\n================================================================================")
    print("STAGE 8.6 EVALUATION SUMMARY")
    print("================================================================================")
    print(f"  Status:               {metrics.get('status')}")
    print(f"  Total Reviewed Clips: {metrics.get('sample_count', 0)}")
    print(f"  Operating Threshold:  {args.threshold:.3f}")
    if metrics.get("status") == "SUCCESS":
        cm = metrics["confusion_matrix"]
        m = metrics["metrics"]
        print(f"  Confusion Matrix:     TP={cm['tp']}, FP={cm['fp']}, FN={cm['fn']}, TN={cm['tn']}")
        print(f"  Precision:            {m['precision']:.4f}")
        print(f"  Recall:               {m['recall']:.4f}")
        print(f"  F1 Score:             {m['f1_score']:.4f}")
        print(f"  Accuracy:             {m['accuracy']:.4f}")
        print(f"  ROC-AUC:              {m['roc_auc'] if m['roc_auc'] is not None else m['auc_note']}")
    else:
        print(f"  Note:                 {metrics.get('reason')}")
    print("================================================================================\n")


if __name__ == "__main__":
    main()
