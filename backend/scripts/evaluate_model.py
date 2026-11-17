"""Model Evaluation and Diagnostics Script (Stage 5).

Evaluates the validation-selected model on the held-out test split once.
Generates:
1. Overall and dataset-specific metrics (ROC-AUC, PR-AUC, Accuracy, Precision, Recall, F1, FP/hr).
2. Group-aggregated detection statistics.
3. Test predictions CSV with detailed error tagging.
4. Comprehensive test evaluation report and error analysis report.
5. Publication-quality ROC and Precision-Recall curve plots.
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
from typing import Any, Dict, List, Tuple

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import joblib
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

from src.config import MODELS_DIR, REPORTS_DIR
from src.dataset import load_dataset_split
from src.model.scream_classifier import FestivalScreamClassifier

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("evaluate_model")


def compute_metrics(
    y_true: np.ndarray,
    y_probs: np.ndarray,
    threshold: float,
    duration_seconds_neg: float = 0.0,
) -> Dict[str, Any]:
    """Calculate comprehensive performance metrics at a given threshold."""
    y_preds = (y_probs >= threshold).astype(int)

    # Confusion matrix
    tn, fp, fn, tp = confusion_matrix(y_true, y_preds, labels=[0, 1]).ravel()
    total = len(y_true)

    # Basic rates
    prec = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
    rec = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
    f1 = float(2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
    acc = float((tp + tn) / total) if total > 0 else 0.0
    spec = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0

    # AUC scores (only if both classes exist in y_true)
    if len(np.unique(y_true)) > 1:
        roc_auc = float(roc_auc_score(y_true, y_probs))
        pr_auc = float(average_precision_score(y_true, y_probs))
    else:
        roc_auc = float("nan")
        pr_auc = float("nan")

    # False Positives per hour of negative audio
    if duration_seconds_neg > 0:
        total_hours = duration_seconds_neg / 3600.0
        fp_per_hour = float(fp / total_hours)
    else:
        fp_per_hour = float("nan")

    return {
        "total_samples": int(total),
        "positives": int(np.sum(y_true)),
        "negatives": int(total - np.sum(y_true)),
        "tp": int(tp),
        "fp": int(fp),
        "fn": int(fn),
        "tn": int(tn),
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "specificity": round(spec, 4),
        "roc_auc": round(roc_auc, 4) if np.isfinite(roc_auc) else None,
        "pr_auc": round(pr_auc, 4) if np.isfinite(pr_auc) else None,
        "threshold": round(threshold, 4),
        "fp_per_hour_negative_audio": round(fp_per_hour, 2) if np.isfinite(fp_per_hour) else None,
        "negative_audio_duration_hours": round(duration_seconds_neg / 3600.0, 3) if duration_seconds_neg > 0 else 0.0,
    }


def compute_group_metrics(
    records: List[Dict[str, Any]],
    y_preds: np.ndarray,
) -> Dict[str, Any]:
    """Compute performance aggregated by independent source groups."""
    groups: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"total": 0, "positives": 0, "detected": 0, "negatives": 0, "false_alarms": 0})

    for rec, pred in zip(records, y_preds):
        gid = rec["source_group_id"]
        is_pos = rec["true_binary"] == 1
        groups[gid]["total"] += 1
        if is_pos:
            groups[gid]["positives"] += 1
            if pred == 1:
                groups[gid]["detected"] += 1
        else:
            groups[gid]["negatives"] += 1
            if pred == 1:
                groups[gid]["false_alarms"] += 1

    scream_groups = {k: v for k, v in groups.items() if v["positives"] > 0}
    non_scream_groups = {k: v for k, v in groups.items() if v["positives"] == 0}

    # A scream group is detected if at least 1 scream in it was detected
    groups_detected = sum(1 for v in scream_groups.values() if v["detected"] > 0)
    groups_perfect = sum(1 for v in scream_groups.values() if v["detected"] == v["positives"])
    group_recall = groups_detected / len(scream_groups) if scream_groups else 0.0

    # A non-scream group is clean if it has 0 false alarms
    clean_non_scream_groups = sum(1 for v in non_scream_groups.values() if v["false_alarms"] == 0)
    groups_with_fa = len(non_scream_groups) - clean_non_scream_groups
    group_specificity = clean_non_scream_groups / len(non_scream_groups) if non_scream_groups else 0.0

    return {
        "total_unique_groups": len(groups),
        "scream_groups_count": len(scream_groups),
        "scream_groups_with_detection": groups_detected,
        "scream_groups_perfect_detection": groups_perfect,
        "group_level_scream_recall": round(group_recall, 4),
        "non_scream_groups_count": len(non_scream_groups),
        "non_scream_groups_clean": clean_non_scream_groups,
        "non_scream_groups_with_false_alarms": groups_with_fa,
        "group_level_specificity": round(group_specificity, 4),
    }


def plot_curves(
    y_true: np.ndarray,
    y_probs: np.ndarray,
    selected_threshold: float,
    plots_dir: Path,
) -> Tuple[Path, Path]:
    """Generate and save publication-quality ROC and Precision-Recall plots."""
    plots_dir.mkdir(parents=True, exist_ok=True)
    roc_plot_path = plots_dir / "roc_curve.png"
    pr_plot_path = plots_dir / "pr_curve.png"

    # 1. ROC Curve
    fpr, tpr, roc_threshs = roc_curve(y_true, y_probs)
    roc_auc = roc_auc_score(y_true, y_probs)

    # Find point closest to selected threshold
    idx_selected = int(np.argmin(np.abs(roc_threshs - selected_threshold)))

    plt.figure(figsize=(7, 6), dpi=200)
    plt.plot(fpr, tpr, color="#2563EB", lw=2.5, label=f"ROC Curve (AUC = {roc_auc:.4f})")
    plt.plot([0, 1], [0, 1], color="#94A3B8", lw=1.5, linestyle="--", label="Random Chance (AUC = 0.50)")
    plt.scatter(
        [fpr[idx_selected]],
        [tpr[idx_selected]],
        color="#DC2626",
        s=90,
        zorder=5,
        label=f"Selected Threshold ({selected_threshold:.2f})",
    )
    plt.xlim([-0.02, 1.02])
    plt.ylim([-0.02, 1.05])
    plt.xlabel("False Positive Rate (1 - Specificity)", fontsize=11, fontweight="medium")
    plt.ylabel("True Positive Rate (Recall)", fontsize=11, fontweight="medium")
    plt.title("Stage 5 Classifier — Test Set Receiver Operating Characteristic (ROC)", fontsize=12, fontweight="bold")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="lower right", frameon=True, facecolor="#F8FAFC", edgecolor="#CBD5E1")
    plt.tight_layout()
    plt.savefig(roc_plot_path)
    plt.close()

    # 2. Precision-Recall Curve
    precision, recall, pr_threshs = precision_recall_curve(y_true, y_probs)
    pr_auc = average_precision_score(y_true, y_probs)
    prevalence = np.sum(y_true) / len(y_true)

    # Find operating point on PR curve
    # Note: pr_threshs has length len(precision) - 1
    if len(pr_threshs) > 0:
        pr_idx = int(np.argmin(np.abs(pr_threshs - selected_threshold)))
        op_prec = precision[pr_idx]
        op_rec = recall[pr_idx]
    else:
        op_prec, op_rec = 1.0, 1.0

    plt.figure(figsize=(7, 6), dpi=200)
    plt.plot(recall, precision, color="#10B981", lw=2.5, label=f"PR Curve (AP = {pr_auc:.4f})")
    plt.axhline(y=prevalence, color="#94A3B8", lw=1.5, linestyle="--", label=f"Base Prevalence ({prevalence:.1%})")
    plt.scatter(
        [op_rec],
        [op_prec],
        color="#DC2626",
        s=90,
        zorder=5,
        label=f"Selected Threshold ({selected_threshold:.2f}): P={op_prec:.3f}, R={op_rec:.3f}",
    )
    plt.xlim([-0.02, 1.02])
    plt.ylim([-0.02, 1.05])
    plt.xlabel("Recall (Sensitivity)", fontsize=11, fontweight="medium")
    plt.ylabel("Precision (Positive Predictive Value)", fontsize=11, fontweight="medium")
    plt.title("Stage 5 Classifier — Test Set Precision-Recall Curve", fontsize=12, fontweight="bold")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="lower left", frameon=True, facecolor="#F8FAFC", edgecolor="#CBD5E1")
    plt.tight_layout()
    plt.savefig(pr_plot_path)
    plt.close()

    return roc_plot_path, pr_plot_path


def generate_evaluation_report(
    overall_metrics: Dict[str, Any],
    dataset_metrics: Dict[str, Dict[str, Any]],
    group_metrics: Dict[str, Any],
    metadata: Dict[str, Any],
    report_path: Path,
) -> None:
    """Generate comprehensive Stage 5 Held-Out Test Evaluation report."""
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Stage 5 Scream Classifier Held-Out Test Evaluation Report\n\n")
        f.write(f"**Evaluation Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("> [!IMPORTANT]\n")
        f.write("> **Strict Held-Out Isolation Protocol**:\n")
        f.write("> The test partition was strictly sealed during training, feature selection, hyperparameter tuning, ")
        f.write("> and threshold selection. The evaluation reported below was executed exactly once using the frozen validation-selected threshold.\n\n")
        f.write("---\n\n")

        f.write("## 1. Selected Model Configuration\n\n")
        f.write(f"- **Model Architecture**: **{metadata.get('model_type')}**\n")
        f.write(f"- **Feature Representation**: **`{metadata.get('feature_representation')}`** ({metadata.get('feature_dimension')} dims)\n")
        f.write(f"- **Pipeline Components**: `{' -> '.join(metadata.get('pipeline_steps', []))}`\n")
        f.write(f"- **Hyperparameters**: `{metadata.get('hyperparameters')}`\n")
        f.write(f"- **Validation-Selected Operating Threshold**: **{metadata.get('selected_threshold'):.2f}**\n\n")

        f.write("---\n\n")
        f.write("## 2. Test Set Sample Counts & Uncertainty Framing\n\n")
        f.write(f"- **Total Test Recordings**: **{overall_metrics['total_samples']}**\n")
        f.write(f"- **Positive Scream Recordings**: **{overall_metrics['positives']}** (from **{group_metrics['scream_groups_count']} independent source groups**)\n")
        f.write(f"- **Negative Recordings**: **{overall_metrics['negatives']}** (from **{group_metrics['non_scream_groups_count']} independent source groups**)\n\n")
        f.write("> [!NOTE]\n")
        f.write("> **Sample Size Uncertainty Context**:\n")
        f.write(f"> With exactly {overall_metrics['positives']} screams in the held-out test partition, a single misclassification shifts measured test recall by **{1.0 / overall_metrics['positives']:.2%}**. ")
        f.write("Therefore, metric comparisons across decimals should not be overstated without wider field validation.\n\n")

        f.write("---\n\n")
        f.write("## 3. Held-Out Test Evaluation Metrics\n\n")
        f.write("| Metric | Held-Out Test Set Value | Validation Baseline (Reference) |\n")
        f.write("| :--- | :--- | :--- |\n")
        f.write(f"| **ROC-AUC** | **{overall_metrics['roc_auc']:.4f}** | {metadata['validation_metrics']['roc_auc']:.4f} |\n")
        f.write(f"| **PR-AUC (Average Precision)** | **{overall_metrics['pr_auc']:.4f}** | {metadata['validation_metrics']['pr_auc']:.4f} |\n")
        f.write(f"| **Precision** | **{overall_metrics['precision']:.4f}** | {metadata['validation_metrics']['precision']:.4f} |\n")
        f.write(f"| **Recall (Sensitivity)** | **{overall_metrics['recall']:.4f}** | {metadata['validation_metrics']['recall']:.4f} |\n")
        f.write(f"| **F1-Score** | **{overall_metrics['f1_score']:.4f}** | {metadata['validation_metrics']['f1_score']:.4f} |\n")
        f.write(f"| **Accuracy** | **{overall_metrics['accuracy']:.4f}** | — |\n")
        f.write(f"| **Specificity** | **{overall_metrics['specificity']:.4f}** | {metadata['validation_metrics']['specificity']:.4f} |\n")
        f.write(f"| **True Positives (TP)** | **{overall_metrics['tp']}** / {overall_metrics['positives']} | {metadata['validation_metrics']['confusion_matrix']['tp']} / 19 |\n")
        f.write(f"| **False Positives (FP)** | **{overall_metrics['fp']}** / {overall_metrics['negatives']} | {metadata['validation_metrics']['confusion_matrix']['fp']} / 225 |\n")
        f.write(f"| **False Negatives (FN)** | **{overall_metrics['fn']}** / {overall_metrics['positives']} | {metadata['validation_metrics']['confusion_matrix']['fn']} / 19 |\n")
        f.write(f"| **True Negatives (TN)** | **{overall_metrics['tn']}** / {overall_metrics['negatives']} | {metadata['validation_metrics']['confusion_matrix']['tn']} / 225 |\n\n")

        f.write("---\n\n")
        f.write("## 4. Supplementary Operational Metric: False Positives per Hour\n\n")
        f.write(f"- **Verified Negative Audio Duration**: **{overall_metrics['negative_audio_duration_hours']:.2f} hours** ({overall_metrics['negatives']} audio files)\n")
        f.write(f"- **False Alarms Count**: **{overall_metrics['fp']}**\n")
        f.write(f"- **Estimated False Positives per Hour**: **{overall_metrics['fp_per_hour_negative_audio']:.2f} FP/hour**\n\n")
        f.write("> [!WARNING]\n")
        f.write("> **Calculation Methodology & Limitations**:\n")
        f.write("> This metric sums the discrete durations of all 224 negative recordings in the test set. ")
        f.write("However, real festival audio is continuous, multi-stream, and highly dynamic. Discrete non-overlapping audio slices ")
        f.write("do not experience real-time window boundary effects, continuous ambient reverberation, or overlapping acoustic mixtures. ")
        f.write("This figure serves as a benchmark upper/lower bound, not a guarantee for unattended live deployment.\n\n")

        f.write("---\n\n")
        f.write("## 5. Dataset-Specific Breakdown: OpenSLR 99 vs. NIGENS\n\n")
        f.write("| Sub-Dataset | Total Recordings | Screams | Non-Screams | ROC-AUC | PR-AUC | Precision | Recall | F1-Score | FP | FN |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for ds_name, dm in dataset_metrics.items():
            f.write(
                f"| **{ds_name}** | {dm['total_samples']} | {dm['positives']} | {dm['negatives']} | "
                f"{dm['roc_auc'] if dm['roc_auc'] is not None else 'N/A'} | {dm['pr_auc'] if dm['pr_auc'] is not None else 'N/A'} | "
                f"{dm['precision']:.4f} | {dm['recall']:.4f} | {dm['f1_score']:.4f} | {dm['fp']} | {dm['fn']} |\n"
            )

        f.write("\n---\n\n")
        f.write("## 6. Source-Group Aggregated Performance\n\n")
        f.write(f"- **Independent Scream Source Groups**: **{group_metrics['scream_groups_count']}**\n")
        f.write(f"  - Groups with at least 1 detection: **{group_metrics['scream_groups_with_detection']}** ({group_metrics['group_level_scream_recall']:.1%})\n")
        f.write(f"  - Groups with 100% detection: **{group_metrics['scream_groups_perfect_detection']}**\n")
        f.write(f"- **Independent Non-Scream Source Groups**: **{group_metrics['non_scream_groups_count']}**\n")
        f.write(f"  - Completely clean groups (0 false alarms): **{group_metrics['non_scream_groups_clean']}** ({group_metrics['group_level_specificity']:.1%})\n")
        f.write(f"  - Groups triggering false alarms: **{group_metrics['non_scream_groups_with_false_alarms']}**\n\n")

        f.write("---\n\n")
        f.write("## 7. Performance Visualization\n\n")
        f.write("- **Receiver Operating Characteristic (ROC)**: [roc_curve.png](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/reports/plots/roc_curve.png)\n")
        f.write("- **Precision-Recall Curve**: [pr_curve.png](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/reports/plots/pr_curve.png)\n")


def generate_error_analysis_report(
    predictions: List[Dict[str, Any]],
    threshold: float,
    report_path: Path,
) -> None:
    """Generate detailed Error Analysis report focusing on false negatives, false positives, and borderlines."""
    report_path.parent.mkdir(parents=True, exist_ok=True)

    false_negatives = [p for p in predictions if p["classification_result"] == "FN"]
    false_positives = [p for p in predictions if p["classification_result"] == "FP"]
    borderlines = [p for p in predictions if p["is_borderline"]]

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Stage 5 Custom Scream Classifier — Detailed Error Analysis\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")

        f.write("## 1. Summary of Discrepancies\n\n")
        f.write(f"- **Decision Threshold**: **{threshold:.2f}**\n")
        f.write(f"- **False Negatives (Missed Screams)**: **{len(false_negatives)}**\n")
        f.write(f"- **False Positives (Spurious Alarms)**: **{len(false_positives)}**\n")
        f.write(f"- **Borderline Predictions ($|P - \\tau| \\le 0.15$)**: **{len(borderlines)}**\n\n")

        f.write("---\n\n")
        f.write("## 2. False Negative Recordings (Missed Screams)\n\n")
        if not false_negatives:
            f.write("No false negatives observed on the test set. All positive scream recordings were successfully detected!\n\n")
        else:
            f.write("| File ID | Dataset | Relative Path | Source Group | Duration | Probability | Margin to Threshold |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
            for fn in false_negatives:
                f.write(
                    f"| `{fn['file_id']}` | {fn['dataset_name']} | `{fn['relative_path']}` | "
                    f"`{fn['source_group_id']}` | {fn['duration_seconds']:.2f}s | "
                    f"**{fn['predicted_probability']:.4f}** | {fn['margin_to_threshold']:+.4f} |\n"
                )
            f.write("\n")

        f.write("---\n\n")
        f.write("## 3. False Positive Recordings (Spurious Non-Scream Alarms)\n\n")
        if not false_positives:
            f.write("No false positives observed on the test set. Perfect specificity achieved!\n\n")
        else:
            f.write("| File ID | Dataset | Relative Path | Source Group | Duration | Probability | Margin to Threshold |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
            for fp in false_positives:
                f.write(
                    f"| `{fp['file_id']}` | {fp['dataset_name']} | `{fp['relative_path']}` | "
                    f"`{fp['source_group_id']}` | {fp['duration_seconds']:.2f}s | "
                    f"**{fp['predicted_probability']:.4f}** | {fp['margin_to_threshold']:+.4f} |\n"
                )
            f.write("\n")

        f.write("---\n\n")
        f.write("## 4. Borderline Predictions ($|P - \\tau| \\le 0.15$)\n\n")
        if not borderlines:
            f.write("No predictions fell within the borderline confidence margin.\n\n")
        else:
            f.write("| File ID | True Class | Predicted Class | Result | Probability | Margin | Relative Path |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
            for b in borderlines:
                f.write(
                    f"| `{b['file_id']}` | {b['true_label']} | {b['predicted_label']} | "
                    f"**{b['classification_result']}** | {b['predicted_probability']:.4f} | "
                    f"{b['margin_to_threshold']:+.4f} | `{b['relative_path']}` |\n"
                )
            f.write("\n")

        f.write("---\n\n")
        f.write("## 5. Acoustic Error Drivers & Dataset Dynamics\n\n")
        f.write("1. **Vocal Ambiguity & Emotional Valence**:\n")
        f.write("   - Nonverbal vocalizations in OpenSLR 99 include laughing, crying, groaning, and gasping. High-pitched crying and laughing share harmonic register, formant dispersion, and rapid pitch trajectories with screams.\n")
        f.write("2. **Transient Peak Energy in Environmental SFX (NIGENS)**:\n")
        f.write("   - Sharp mechanical sounds (e.g. car horns, screeching brakes, high-frequency alarm tones) can exhibit high instantaneous energy in mid-frequency bands (1–3 kHz) that resemble vocal distress onset.\n")
        f.write("3. **Duration Discrepancies**:\n")
        f.write("   - Screams that are brief (e.g. 0.5s - 1.0s) inside longer recordings (4s+) rely heavily on max-pooled features to avoid being diluted by mean pooling.\n\n")

        f.write("---\n\n")
        f.write("## 6. Actionable Hard-Negative Recommendations for Stage 6\n\n")
        f.write("To prevent real-world festival false alarms, the following hard-negative sound categories must be systematically gathered and introduced in Stage 6:\n")
        f.write("1. **Crowd Cheering & Chanting**: Prolonged collective cheering at stage climaxes.\n")
        f.write("2. **Rave Whistles & Vuvuzelas**: High-intensity sinusoidal shrieks common in EDM festivals.\n")
        f.write("3. **Amplified Vocal Echoes**: Reverb and delay effects applied to singing / MC hyping that artificially stretch vocal formants.\n")
        f.write("4. **Sub-bass Overload & Wind Pop**: Microphone clipping and sub-bass vibration inducing non-linear distortion.\n")
        f.write("5. **Laughter and High-Pitched Excitement**: Non-distress energetic human vocalizations.\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate trained scream classifier on held-out test split.")
    parser.add_argument("--model-path", type=str, default=None, help="Path to .joblib model file.")
    parser.add_argument("--metadata-path", type=str, default=None, help="Path to model metadata JSON.")
    args = parser.parse_args()

    print("=" * 75)
    print("STAGE 5 — MODEL EVALUATION & ERROR DIAGNOSTICS (TEST SET)")
    print("=" * 75)

    # 1. Load Trained Classifier
    print("\n[Step 1/5] Loading trained classifier and configuration metadata...")
    classifier = FestivalScreamClassifier(
        model_path=args.model_path,
        metadata_path=args.metadata_path,
    )
    if not classifier.is_loaded:
        print("[ERROR] Classifier could not be loaded. Please ensure train_classifier.py has been run.", file=sys.stderr)
        return 1

    feature_rep = classifier.feature_type
    operating_threshold = classifier.threshold
    print(f"  - Model Architecture:      {classifier.metadata.get('model_type')}")
    print(f"  - Feature Representation:  {feature_rep} ({classifier.expected_dim} dims)")
    print(f"  - Operating Threshold:     {operating_threshold:.2f}")

    # 2. Load Held-Out Test Set
    print("\n[Step 2/5] Loading held-out test split features and labels...")
    X_test, y_test, meta_test = load_dataset_split("test", feature_rep)
    total_test = len(y_test)
    num_screams = int(np.sum(y_test))
    num_non_screams = total_test - num_screams
    print(f"  - Loaded test records:     {total_test} ({num_screams} screams, {num_non_screams} non-screams)")

    # 3. Predict Probabilities and Binary Decisions
    print("\n[Step 3/5] Computing predictions on test split...")
    test_probs = classifier.pipeline.predict_proba(X_test)[:, 1]

    # Calculate total duration of verified negative audio
    neg_duration_seconds = sum(
        m["duration_seconds"] for m, y in zip(meta_test, y_test) if y == 0
    )

    # Compute overall metrics
    overall_metrics = compute_metrics(
        y_true=y_test,
        y_probs=test_probs,
        threshold=operating_threshold,
        duration_seconds_neg=neg_duration_seconds,
    )

    # Print summary
    print(f"  - Held-Out ROC-AUC:        {overall_metrics['roc_auc']:.4f}")
    print(f"  - Held-Out PR-AUC:         {overall_metrics['pr_auc']:.4f}")
    print(f"  - Precision:               {overall_metrics['precision']:.4f}")
    print(f"  - Recall:                  {overall_metrics['recall']:.4f} ({overall_metrics['tp']}/{overall_metrics['positives']} screams detected)")
    print(f"  - F1-Score:                {overall_metrics['f1_score']:.4f}")
    print(f"  - False Positives:         {overall_metrics['fp']} (out of {overall_metrics['negatives']} non-screams)")
    print(f"  - False Negatives:         {overall_metrics['fn']} (out of {overall_metrics['positives']} screams)")
    print(f"  - FP / Hour Neg Audio:     {overall_metrics['fp_per_hour_negative_audio']:.2f} FP/hr ({overall_metrics['negative_audio_duration_hours']:.2f} hrs verified negative audio)")

    # 4. Dataset-Specific Breakdown
    print("\n[Step 4/5] Computing dataset-specific performance (OpenSLR 99 vs. NIGENS)...")
    dataset_metrics: Dict[str, Dict[str, Any]] = {}
    for ds_name in ["OpenSLR99", "NIGENS"]:
        idx = [i for i, m in enumerate(meta_test) if m["dataset_name"] == ds_name]
        if idx:
            sub_y = y_test[idx]
            sub_p = test_probs[idx]
            sub_neg_dur = sum(meta_test[i]["duration_seconds"] for i in idx if y_test[i] == 0)
            dm = compute_metrics(sub_y, sub_p, threshold=operating_threshold, duration_seconds_neg=sub_neg_dur)
            dataset_metrics[ds_name] = dm
            print(
                f"  - {ds_name:<12}: Total={dm['total_samples']:3d} | Screams={dm['positives']:2d} | "
                f"P={dm['precision']:.3f} | R={dm['recall']:.3f} | F1={dm['f1_score']:.3f} | "
                f"FP={dm['fp']} | FN={dm['fn']}"
            )

    # 5. Build Detailed Predictions List and Tag Errors
    prediction_records: List[Dict[str, Any]] = []
    for i in range(total_test):
        rec = meta_test[i]
        true_b = int(y_test[i])
        prob = float(test_probs[i])
        pred_b = 1 if prob >= operating_threshold else 0

        if true_b == 1 and pred_b == 1:
            res_tag = "TP"
        elif true_b == 0 and pred_b == 0:
            res_tag = "TN"
        elif true_b == 0 and pred_b == 1:
            res_tag = "FP"
        else:
            res_tag = "FN"

        margin = prob - operating_threshold
        is_borderline = abs(margin) <= 0.15

        pred_entry = {
            "file_id": rec["file_id"],
            "dataset_name": rec["dataset_name"],
            "relative_path": rec["relative_path"],
            "source_group_id": rec["source_group_id"],
            "duration_seconds": rec["duration_seconds"],
            "true_binary": true_b,
            "true_label": "scream" if true_b == 1 else "non_scream",
            "predicted_probability": round(prob, 4),
            "predicted_binary": pred_b,
            "predicted_label": "scream" if pred_b == 1 else "non_scream",
            "classification_result": res_tag,
            "margin_to_threshold": round(margin, 4),
            "is_borderline": is_borderline,
        }
        prediction_records.append(pred_entry)

    # 6. Group-Level Metrics
    group_metrics = compute_group_metrics(prediction_records, (test_probs >= operating_threshold).astype(int))

    # 7. Generate Plots
    print("\n[Step 5/5] Generating plots, CSV diagnostics, and markdown reports...")
    plots_dir = REPORTS_DIR / "plots"
    roc_plot, pr_plot = plot_curves(y_test, test_probs, operating_threshold, plots_dir)
    print(f"  - ROC plot saved:         {roc_plot}")
    print(f"  - PR plot saved:          {pr_plot}")

    # Export test_predictions.csv
    csv_pred_path = REPORTS_DIR / "test_predictions.csv"
    with open(csv_pred_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "file_id",
                "dataset_name",
                "relative_path",
                "source_group_id",
                "duration_seconds",
                "true_binary",
                "true_label",
                "predicted_probability",
                "predicted_binary",
                "predicted_label",
                "classification_result",
                "margin_to_threshold",
                "is_borderline",
            ],
        )
        writer.writeheader()
        writer.writerows(prediction_records)
    print(f"  - Predictions CSV saved:  {csv_pred_path}")

    # Generate test evaluation markdown report
    eval_report_path = REPORTS_DIR / "stage5_test_evaluation.md"
    generate_evaluation_report(
        overall_metrics=overall_metrics,
        dataset_metrics=dataset_metrics,
        group_metrics=group_metrics,
        metadata=classifier.metadata,
        report_path=eval_report_path,
    )
    print(f"  - Evaluation report saved: {eval_report_path}")

    # Generate error analysis markdown report
    error_report_path = REPORTS_DIR / "stage5_error_analysis.md"
    generate_error_analysis_report(
        predictions=prediction_records,
        threshold=operating_threshold,
        report_path=error_report_path,
    )
    print(f"  - Error analysis report:   {error_report_path}")

    print("\n" + "=" * 75)
    print("STAGE 5 TEST EVALUATION COMPLETE!")
    print("=" * 75)
    return 0


if __name__ == "__main__":
    sys.exit(main())
