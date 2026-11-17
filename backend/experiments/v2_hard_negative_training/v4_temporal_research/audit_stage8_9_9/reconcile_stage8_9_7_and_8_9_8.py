"""Reconcile Stage 8.9.7 and Stage 8.9.8 metrics and evaluate discrepancies."""

import csv
import json
from pathlib import Path
import numpy as np
from sklearn.metrics import confusion_matrix, precision_score, recall_score, roc_auc_score, average_precision_score

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent

pred_7_path = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "reports" / "stage8_9_7_test_predictions.csv"
pred_8_path = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "reports" / "stage8_9_8_test_predictions.csv"

# Load Stage 8.9.7 predictions
rows_7 = []
with open(pred_7_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows_7.append(r)

# Load Stage 8.9.8 predictions
rows_8 = []
with open(pred_8_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows_8.append(r)

print(f"Stage 8.9.7 row count: {len(rows_7)}")
print(f"Stage 8.9.8 row count: {len(rows_8)}")

# Check file ID alignment
fids_7 = [r["file_id"] for r in rows_7]
fids_8 = [r["file_id"] for r in rows_8]
print(f"Identical file IDs? {fids_7 == fids_8}")

y_true_7 = np.array([int(r["y_true"]) for r in rows_7])
y_true_8 = np.array([int(r["y_true"]) for r in rows_8])
print(f"Identical labels? {np.array_equal(y_true_7, y_true_8)}")
print(f"Total: {len(y_true_7)}, Pos: {np.sum(y_true_7 == 1)}, Neg: {np.sum(y_true_7 == 0)}")

# Check Model H in Stage 8.9.7 predictions across various thresholds
probs_h = np.array([float(r["prob_model_h"]) for r in rows_7])
probs_d = np.array([float(r["prob_model_d"]) for r in rows_7])

print("\n--- Model H Evaluations across thresholds ---")
for t in [0.30, 0.35, 0.37, 0.40, 0.41, 0.42, 0.43, 0.44, 0.45, 0.50]:
    pred = (probs_h >= t).astype(int)
    cm = confusion_matrix(y_true_7, pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    rec = tp / (tp + fn)
    fpr = fp / (tn + fp)
    prec = tp / max(1, tp + fp)
    f1 = 2 * prec * rec / max(1e-6, prec + rec)
    print(f"Threshold {t:.2f}: TP={tp:2d}, FP={fp:2d}, FN={fn:2d}, TN={tn:3d} | Recall={rec*100:5.2f}%, FPR={fpr*100:5.2f}%, F1={f1:.4f}")

print("\n--- Model D Evaluations across thresholds ---")
for t in [0.30, 0.35, 0.37, 0.40, 0.50]:
    pred = (probs_d >= t).astype(int)
    cm = confusion_matrix(y_true_7, pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    rec = tp / (tp + fn)
    fpr = fp / (tn + fp)
    prec = tp / max(1, tp + fp)
    f1 = 2 * prec * rec / max(1e-6, prec + rec)
    print(f"Threshold {t:.2f}: TP={tp:2d}, FP={fp:2d}, FN={fn:2d}, TN={tn:3d} | Recall={rec*100:5.2f}%, FPR={fpr*100:5.2f}%, F1={f1:.4f}")
