"""Hard-Negative Evaluation Script for Frozen Stage 5 Baseline Classifier.

Evaluates the frozen Stage 5 Logistic Regression model (at threshold 0.35)
against human-reviewed hard-negative audio clips without modifying model weights.
Generates hard_negative_predictions.csv and stage6_hard_negative_evaluation.md.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import numpy as np

from src.audio.preprocessor import load_audio
from src.config import (
    HARD_NEGATIVES_MANIFEST,
    MODELS_DIR,
    REPORTS_DIR,
    TARGET_SAMPLE_RATE,
)
from src.dataset.hard_negatives import (
    HARD_NEGATIVE_CATEGORIES,
    load_approved_hard_negatives,
)
from src.model.scream_classifier import FestivalScreamClassifier
from src.model.yamnet_loader import YAMNetLoader

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("evaluate_hard_negatives")


def generate_hard_negative_report(
    eval_results: List[Dict[str, Any]],
    metadata: Dict[str, Any],
    excluded_counts: Dict[str, int],
    report_path: Path,
) -> None:
    """Generate Markdown report for hard-negative evaluation."""
    report_path.parent.mkdir(parents=True, exist_ok=True)

    non_scream_evals = [r for r in eval_results if r["true_label"] == "non_scream"]
    scream_evals = [r for r in eval_results if r["true_label"] == "scream"]

    num_total = len(eval_results)
    num_non_screams = len(non_scream_evals)
    num_screams = len(scream_evals)

    false_alarms = [r for r in non_scream_evals if r["is_scream"]]
    missed_screams = [r for r in scream_evals if not r["is_scream"]]

    # Unique source groups
    unique_groups = len(set(r["source_group_id"] for r in eval_results))

    # Category breakdown
    cat_metrics: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"total": 0, "false_alarms": 0, "scores": []})
    for r in non_scream_evals:
        c = r["sound_category"]
        cat_metrics[c]["total"] += 1
        cat_metrics[c]["scores"].append(r["scream_probability"])
        if r["is_scream"]:
            cat_metrics[c]["false_alarms"] += 1

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Stage 6 Hard-Negative Acoustic Robustness Evaluation\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("> [!IMPORTANT]\n")
        f.write("> **Frozen Baseline Preservation Protocol**:\n")
        f.write("> All evaluations in this report were performed using the frozen Stage 5 baseline model ")
        f.write("(`LogisticRegression`, $C=10.0$, max-pooled 1024-dim features) at the validation-selected ")
        f.write(f"operating threshold **$\\tau = {metadata.get('selected_threshold', 0.35):.2f}$**. ")
        f.write("No model weights or threshold parameters were altered.\n\n")
        f.write("---\n\n")

        f.write("## 1. Evaluation Dataset Overview\n\n")
        f.write(f"- **Total Reviewed Clips Evaluated**: **{num_total}**\n")
        f.write(f"- **Independent Source Groups**: **{unique_groups}**\n")
        f.write(f"- **Reviewed Non-Scream Distractors**: **{num_non_screams}**\n")
        f.write(f"- **Reviewed Genuine Screams**: **{num_screams}**\n")
        f.write(f"- **Excluded Records (Pending Review)**: **{excluded_counts.get('pending_review', 0)}**\n")
        f.write(f"- **Excluded Records (Rejected / Ambiguous)**: **{excluded_counts.get('rejected_ambiguous', 0)}**\n\n")

        if num_total == 0:
            f.write("> [!NOTE]\n")
            f.write("> **Dataset Collection Status**:\n")
            f.write("> Currently, **0 human-reviewed clips** are recorded in `hard_negatives_manifest.json`. ")
            f.write("In accordance with project integrity standards, no artificial scores or synthetic evaluations were fabricated. ")
            f.write("Below is the established acoustic baseline from Stage 5, along with the testing protocol ready to execute as soon as real audio is ingested.\n\n")
        else:
            f.write("---\n\n")
            f.write("## 2. Hard-Negative Evaluation Metrics (At $\\tau = 0.35$)\n\n")
            fp_rate = len(false_alarms) / num_non_screams if num_non_screams > 0 else 0.0
            spec = 1.0 - fp_rate
            f.write(f"- **Overall False Alarm Rate on Hard Negatives**: **{fp_rate:.2%}** ({len(false_alarms)}/{num_non_screams} false positives)\n")
            f.write(f"- **Acoustic Specificity on Hard Negatives**: **{spec:.2%}**\n")
            if num_screams > 0:
                rec = (num_screams - len(missed_screams)) / num_screams
                f.write(f"- **Recall on New Sourced Screams**: **{rec:.2%}** ({num_screams - len(missed_screams)}/{num_screams})\n")

            f.write("\n### Category-by-Category Vulnerability Analysis\n\n")
            f.write("| Sound Category | Tested Clips | False Alarms | False Alarm Rate | Mean Probability | Max Probability |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
            for cat, data in sorted(cat_metrics.items()):
                tot = data["total"]
                fa = data["false_alarms"]
                r = fa / tot if tot > 0 else 0.0
                mean_p = float(np.mean(data["scores"])) if data["scores"] else 0.0
                max_p = float(np.max(data["scores"])) if data["scores"] else 0.0
                f.write(f"| **`{cat}`** | {tot} | {fa} | {r:.1%} | {mean_p:.4f} | {max_p:.4f} |\n")
            f.write("\n")

        f.write("---\n\n")
        f.write("## 3. Comparison with Stage 5 Historical Baseline\n\n")
        f.write("| Metric | Stage 5 Held-Out Test Set | Stage 6 Hard-Negative Set |\n")
        f.write("| :--- | :--- | :--- |\n")
        f.write(f"| **Model Architecture** | Logistic Regression (C=10.0, max-pooled) | Logistic Regression (Unchanged) |\n")
        f.write(f"| **Operating Threshold** | 0.35 | 0.35 |\n")
        f.write(f"| **Total Negative Samples** | 224 (NIGENS + OpenSLR) | {num_non_screams} (Dedicated Festival Distractors) |\n")
        f.write(f"| **False Positives** | 4 (Specificity: 98.21%) | {len(false_alarms) if num_total > 0 else 'Pending Data'} |\n")
        if num_non_screams > 0:
            total_neg_dur = sum(r["duration_seconds"] for r in non_scream_evals)
            fp_hr_str = f"{len(false_alarms) / (total_neg_dur / 3600):.2f} FP/hr" if total_neg_dur > 0 else "0.00 FP/hr"
        else:
            fp_hr_str = "Pending Data"

        f.write(f"| **False Positives / Hour** | 7.44 FP/hr (0.54h duration) | {fp_hr_str} |\n\n")

        if false_alarms:
            f.write("---\n\n")
            f.write("## 4. Specific False Alarms on Hard Negatives\n\n")
            f.write("| File ID | Category | Source Group | Duration | Probability | Margin to Threshold |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
            for fa in false_alarms:
                f.write(
                    f"| `{fa['file_id']}` | `{fa['sound_category']}` | `{fa['source_group_id']}` | "
                    f"{fa['duration_seconds']:.2f}s | **{fa['scream_probability']:.4f}** | {fa['margin']:+.4f} |\n"
                )
            f.write("\n")

        f.write("---\n\n")
        f.write("## 5. Methodological Caution Regarding Real Festival Noise\n\n")
        f.write("Even when a hard-negative collection achieves 0 false alarms on isolated clips, this **cannot** be claimed as representative of live festival conditions because:\n")
        f.write("1. **Continuous Audio Overlap**: In actual festivals, music drops, cheering crowds, PA feedback, and reverberation overlap simultaneously rather than playing as clean, isolated sound events.\n")
        f.write("2. **Dynamic Range & SPL**: Live outdoor sound reinforcement systems produce SPLs exceeding 100 dB(A), causing microphone membrane saturation and acoustic nonlinearities.\n")
        f.write("3. **Sliding-Window Dynamics**: A continuous stream evaluated with a 0.975s window hopping every 0.48s produces ~7,385 inference passes per hour. A false-alarm rate of 1 per 1,000 passes yields >7 false alarms/hour.\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate Stage 5 classifier on reviewed hard negatives.")
    parser.add_argument("--manifest", type=str, default=None, help="Path to hard_negatives_manifest.json.")
    parser.add_argument("--threshold", type=float, default=None, help="Threshold override (defaults to 0.35).")
    args = parser.parse_args()

    print("=" * 75)
    print("STAGE 6 — HARD-NEGATIVE ROBUSTNESS EVALUATION")
    print("=" * 75)

    # 1. Load Frozen Stage 5 Classifier
    print("\n[Step 1/4] Loading frozen Stage 5 classifier...")
    classifier = FestivalScreamClassifier()
    if not classifier.is_loaded:
        print("[ERROR] Stage 5 model could not be loaded from backend/models/.", file=sys.stderr)
        return 1

    operating_threshold = args.threshold if args.threshold is not None else classifier.threshold
    print(f"  - Model Architecture:    {classifier.metadata.get('model_type')}")
    print(f"  - Feature Representation:{classifier.feature_type} ({classifier.expected_dim} dims)")
    print(f"  - Operating Threshold:   {operating_threshold:.2f}")

    # 2. Load Reviewed Hard Negatives Manifest
    target_manifest = Path(args.manifest).resolve() if args.manifest else HARD_NEGATIVES_MANIFEST
    print(f"\n[Step 2/4] Loading human-reviewed recordings from manifest...")
    print(f"  - Manifest Path:         {target_manifest}")

    if not target_manifest.exists():
        print(f"[WARN] Manifest not found: {target_manifest}. Run ingest_hard_negatives.py first.")
        records = []
        excluded_counts = {"pending_review": 0, "rejected_ambiguous": 0}
    else:
        with open(target_manifest, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        all_records = raw_data.get("records", [])
        excluded_counts = {
            "pending_review": sum(1 for r in all_records if r.get("review_status") == "pending_review"),
            "rejected_ambiguous": sum(1 for r in all_records if r.get("review_status") == "rejected_ambiguous"),
        }
        records = load_approved_hard_negatives(target_manifest)

    print(f"  - Approved Clips Found:  {len(records)}")
    print(f"  - Excluded (Pending):    {excluded_counts['pending_review']}")
    print(f"  - Excluded (Ambiguous):  {excluded_counts['rejected_ambiguous']}")

    # 3. If zero approved clips, report honestly and output report
    eval_results: List[Dict[str, Any]] = []
    report_path = REPORTS_DIR / "stage6_hard_negative_evaluation.md"
    csv_path = REPORTS_DIR / "hard_negative_predictions.csv"

    if len(records) == 0:
        print("\n[Step 3/4] No approved hard-negative clips found. Skipping inference.")
        print("           (Retraining is blocked until real human-reviewed audio is ingested).")
        generate_hard_negative_report(eval_results, classifier.metadata, excluded_counts, report_path)

        # Write empty CSV header
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "file_id", "original_filename", "sound_category", "source_group_id",
                "duration_seconds", "true_label", "scream_probability",
                "is_scream", "threshold", "margin", "source_path"
            ])
        print(f"\n[Step 4/4] Generated baseline reports:")
        print(f"  - Evaluation Report:     {report_path}")
        print(f"  - Predictions CSV:       {csv_path}")
        print("\n" + "=" * 75)
        print("[SUCCESS] Stage 6 hard-negative evaluation completed (Status: 0 approved clips).")
        print("=" * 75 + "\n")
        return 0

    # 4. If approved clips exist, run YAMNet feature extraction and Stage 5 model inference
    print(f"\n[Step 3/4] Running inference on {len(records)} approved hard negatives...")
    yamnet_loader = YAMNetLoader()
    yamnet_loader.load()

    for idx, r in enumerate(records, 1):
        audio_file = Path(r["source_path"])
        if not audio_file.exists():
            print(f"  [WARN] Audio file missing on disk: {audio_file}", file=sys.stderr)
            continue

        waveform, meta = load_audio(audio_file, target_sr=TARGET_SAMPLE_RATE)
        scores, embeddings, _ = yamnet_loader.infer(waveform)
        pooled_feat = classifier.pool_frame_embeddings(embeddings)
        pred = classifier.predict_features(pooled_feat, custom_threshold=operating_threshold)

        true_label = "scream" if r.get("review_status") == "approved_scream" else "non_scream"
        margin = pred["scream_probability"] - operating_threshold

        eval_entry = {
            "file_id": r["file_id"],
            "original_filename": r["original_filename"],
            "sound_category": r.get("sound_category", "unknown"),
            "source_group_id": r.get("source_group_id", "unknown"),
            "duration_seconds": r.get("duration_seconds", meta.duration_seconds),
            "true_label": true_label,
            "scream_probability": round(pred["scream_probability"], 4),
            "is_scream": pred["is_scream"],
            "threshold": operating_threshold,
            "margin": round(margin, 4),
            "source_path": r["source_path"],
        }
        eval_results.append(eval_entry)
        if idx % 20 == 0 or idx == len(records):
            print(f"  Processed [{idx}/{len(records)}] clips...")

    # Export predictions CSV
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "file_id", "original_filename", "sound_category", "source_group_id",
            "duration_seconds", "true_label", "scream_probability",
            "is_scream", "threshold", "margin", "source_path"
        ])
        writer.writeheader()
        writer.writerows(eval_results)

    # Generate Markdown report
    print(f"\n[Step 4/4] Writing evaluation report and predictions...")
    generate_hard_negative_report(eval_results, classifier.metadata, excluded_counts, report_path)
    print(f"  - Evaluation Report:     {report_path}")
    print(f"  - Predictions CSV:       {csv_path}")

    false_alarms = [r for r in eval_results if r["true_label"] == "non_scream" and r["is_scream"]]
    print(f"\n[RESULTS] Tested {len(eval_results)} clips | False Alarms: {len(false_alarms)}")
    print("=" * 75 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
