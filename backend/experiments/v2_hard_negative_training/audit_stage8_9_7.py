"""Independent Formal Evaluation and Calibration Audit (Stage 8.9.7).

Recomputes:
- Binary confusion matrices (TP, FP, FN, TN)
- Accuracy, Precision, Recall, Specificity, Hard-Negative FPR, F1-score
- ROC-AUC and PR-AUC from raw continuous probabilities
- Wilson score 95% confidence intervals for binomial metrics
- 1,000 bootstrap iterations for AUC confidence intervals
- Complete per-category error decomposition across 8 categories
- Calibration analysis: Brier score, Expected Calibration Error (ECE)
- Formal compliance check against pre-declared provisional acceptance targets

Outputs:
- `reports/stage8_9_7_recomputed_metrics.csv`
- `reports/stage8_9_7_confidence_intervals.csv`
- `reports/stage8_9_7_category_metrics.csv`
- `reports/stage8_9_7_calibration_metrics.csv`
"""

from __future__ import annotations

import csv
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("audit_stage8_9_7")

EXPERIMENT_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training"
REPORTS_DIR = EXPERIMENT_DIR / "reports"
PREDICTIONS_CSV = REPORTS_DIR / "stage8_9_7_test_predictions.csv"
BENCHMARK_JSON = REPORTS_DIR / "stage8_9_7_benchmark_summary.json"

BOOTSTRAP_ROUNDS = 1000
BOOTSTRAP_SEED = 42


def wilson_score_interval(successes: int, trials: int, confidence: float = 0.95) -> Tuple[float, float]:
    """Calculate Wilson score 95% confidence interval for a binomial proportion."""
    if trials == 0:
        return 0.0, 0.0
    z = 1.95996  # 95% normal quantile
    p = successes / trials
    denom = 1.0 + (z**2) / trials
    center = (p + (z**2) / (2.0 * trials)) / denom
    half_width = (z * np.sqrt((p * (1.0 - p) + (z**2) / (4.0 * trials)) / trials)) / denom
    lower = max(0.0, center - half_width)
    upper = min(1.0, center + half_width)
    return lower, upper


def bootstrap_auc_ci(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_rounds: int = BOOTSTRAP_ROUNDS,
    seed: int = BOOTSTRAP_SEED,
) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """Compute 95% bootstrap confidence intervals for ROC-AUC and PR-AUC."""
    rng = np.random.RandomState(seed)
    n = len(y_true)
    roc_samples = []
    pr_samples = []

    for _ in range(n_rounds):
        idx = rng.randint(0, n, size=n)
        sample_y = y_true[idx]
        sample_prob = y_prob[idx]

        # Require at least one positive and one negative in bootstrap sample
        if len(np.unique(sample_y)) < 2:
            continue

        try:
            r = roc_auc_score(sample_y, sample_prob)
            roc_samples.append(r)
        except Exception:
            pass

        try:
            p = average_precision_score(sample_y, sample_prob)
            pr_samples.append(p)
        except Exception:
            pass

    roc_ci = (float(np.percentile(roc_samples, 2.5)), float(np.percentile(roc_samples, 97.5))) if roc_samples else (0.0, 0.0)
    pr_ci = (float(np.percentile(pr_samples, 2.5)), float(np.percentile(pr_samples, 97.5))) if pr_samples else (0.0, 0.0)
    return roc_ci, pr_ci


def compute_ece(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> float:
    """Compute Expected Calibration Error (ECE)."""
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        mask = (y_prob >= bins[i]) & (y_prob < bins[i + 1])
        if np.sum(mask) > 0:
            bin_acc = np.mean(y_true[mask])
            bin_conf = np.mean(y_prob[mask])
            ece += (np.sum(mask) / len(y_true)) * abs(bin_acc - bin_conf)
    return float(ece)


def main():
    logger.info("=" * 70)
    logger.info("STAGE 8.9.7: FORMAL INDEPENDENT EVALUATION & CALIBRATION AUDIT")
    logger.info("=" * 70)

    if not PREDICTIONS_CSV.exists() or not BENCHMARK_JSON.exists():
        logger.error(f"Missing predictions ({PREDICTIONS_CSV}) or benchmark json ({BENCHMARK_JSON})")
        sys.exit(1)

    with open(BENCHMARK_JSON, "r", encoding="utf-8") as f:
        bench_data = json.load(f)

    # Read predictions CSV
    rows = []
    with open(PREDICTIONS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

    logger.info(f"Loaded {len(rows)} test prediction records.")

    file_ids = np.array([r["file_id"] for r in rows])
    categories = np.array([r["category"] for r in rows])
    y_true = np.array([int(r["y_true"]) for r in rows])

    n_total = len(y_true)
    n_pos = int(np.sum(y_true == 1))
    n_neg = int(np.sum(y_true == 0))
    logger.info(f"Held-Out Test Cohort: {n_total} samples ({n_pos} screams, {n_neg} non-screams).")

    candidate_models = [
        ("Model_A_v3_Baseline", "prob_model_a", bench_data["Model_A_v3_Baseline"]["threshold"]),
        ("Model_D_v3_Concat_LR", "prob_model_d", bench_data["Model_D_v3_Concat_LR"]["threshold"]),
        ("Model_G_Hybrid_Concat", "prob_model_g", bench_data["Model_G_Hybrid_Concat"]["threshold"]),
        ("Model_H_Calibrated_Hybrid", "prob_model_h", bench_data["Model_H_Calibrated_Hybrid"]["threshold"]),
        ("Model_I_NonLinear_GBT", "prob_model_i", bench_data["Model_I_NonLinear_GBT"]["threshold"]),
    ]

    recomputed_metrics_rows = []
    ci_rows = []
    category_metrics_rows = []
    calibration_rows = []

    # -------------------------------------------------------------
    # 1. Independent Recomputation of Test Metrics & CIs
    # -------------------------------------------------------------
    for model_name, prob_col, threshold in candidate_models:
        y_prob = np.array([float(r[prob_col]) for r in rows])
        y_pred = (y_prob >= threshold).astype(int)

        cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel()

        acc = (tp + tn) / n_total
        prec = tp / max(1, tp + fp)
        rec = tp / max(1, tp + fn)
        spec = tn / max(1, tn + fp)
        fpr = fp / max(1, tn + fp)
        f1 = 2 * prec * rec / max(1e-6, prec + rec)

        roc = roc_auc_score(y_true, y_prob)
        pr_auc = average_precision_score(y_true, y_prob)
        brier = brier_score_loss(y_true, y_prob)
        ece = compute_ece(y_true, y_prob)

        recomputed_metrics_rows.append({
            "model_architecture": model_name,
            "threshold": round(threshold, 4),
            "tp": int(tp),
            "fp": int(fp),
            "fn": int(fn),
            "tn": int(tn),
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "specificity": round(spec, 4),
            "hard_negative_fpr": round(fpr, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc, 4),
            "pr_auc": round(pr_auc, 4),
            "brier_score": round(brier, 4),
            "ece": round(ece, 4),
        })

        calibration_rows.append({
            "model_architecture": model_name,
            "brier_score": round(brier, 4),
            "ece": round(ece, 4),
            "prob_mean": round(float(np.mean(y_prob)), 4),
            "prob_std": round(float(np.std(y_prob)), 4),
            "prob_min": round(float(np.min(y_prob)), 4),
            "prob_max": round(float(np.max(y_prob)), 4),
        })

        # Confidence intervals
        rec_low, rec_high = wilson_score_interval(tp, n_pos)
        fpr_low, fpr_high = wilson_score_interval(fp, n_neg)
        prec_low, prec_high = wilson_score_interval(tp, tp + fp) if (tp + fp) > 0 else (0.0, 0.0)
        roc_ci, pr_ci = bootstrap_auc_ci(y_true, y_prob)

        ci_rows.append({
            "model_architecture": model_name,
            "metric": "Recall",
            "point_estimate": round(rec, 4),
            "ci_lower": round(rec_low, 4),
            "ci_upper": round(rec_high, 4),
            "margin_of_error": round((rec_high - rec_low) / 2.0, 4),
        })
        ci_rows.append({
            "model_architecture": model_name,
            "metric": "Hard-Negative FPR",
            "point_estimate": round(fpr, 4),
            "ci_lower": round(fpr_low, 4),
            "ci_upper": round(fpr_high, 4),
            "margin_of_error": round((fpr_high - fpr_low) / 2.0, 4),
        })
        ci_rows.append({
            "model_architecture": model_name,
            "metric": "Precision",
            "point_estimate": round(prec, 4),
            "ci_lower": round(prec_low, 4),
            "ci_upper": round(prec_high, 4),
            "margin_of_error": round((prec_high - prec_low) / 2.0, 4),
        })
        ci_rows.append({
            "model_architecture": model_name,
            "metric": "PR-AUC",
            "point_estimate": round(pr_auc, 4),
            "ci_lower": round(pr_ci[0], 4),
            "ci_upper": round(pr_ci[1], 4),
            "margin_of_error": round((pr_ci[1] - pr_ci[0]) / 2.0, 4),
        })

        # -------------------------------------------------------------
        # 2. Detailed Per-Category Metrics
        # -------------------------------------------------------------
        unique_cats = sorted(list(set(categories)))
        for cat in unique_cats:
            mask = (categories == cat)
            cat_y = y_true[mask]
            cat_p = y_pred[mask]
            c_samples = int(np.sum(mask))
            c_pos = int(np.sum(cat_y == 1))
            c_neg = int(np.sum(cat_y == 0))

            if c_pos > 0 and c_neg == 0:
                c_tp = int(np.sum((cat_p == 1) & (cat_y == 1)))
                c_fn = c_pos - c_tp
                c_rec = float(c_tp / c_pos)
                low_ci, high_ci = wilson_score_interval(c_tp, c_pos)
                category_metrics_rows.append({
                    "model_architecture": model_name,
                    "category": cat,
                    "type": "positive",
                    "total_samples": c_samples,
                    "pos_count": c_pos,
                    "neg_count": c_neg,
                    "metric_name": "Recall",
                    "rate": round(c_rec, 4),
                    "ci_lower": round(low_ci, 4),
                    "ci_upper": round(high_ci, 4),
                    "tp": c_tp,
                    "fn": c_fn,
                    "fp": 0,
                    "tn": 0,
                })
            elif c_neg > 0 and c_pos == 0:
                c_fp = int(np.sum((cat_p == 1) & (cat_y == 0)))
                c_tn = c_neg - c_fp
                c_fpr = float(c_fp / c_neg)
                low_ci, high_ci = wilson_score_interval(c_fp, c_neg)
                category_metrics_rows.append({
                    "model_architecture": model_name,
                    "category": cat,
                    "type": "negative",
                    "total_samples": c_samples,
                    "pos_count": c_pos,
                    "neg_count": c_neg,
                    "metric_name": "FPR",
                    "rate": round(c_fpr, 4),
                    "ci_lower": round(low_ci, 4),
                    "ci_upper": round(high_ci, 4),
                    "tp": 0,
                    "fn": 0,
                    "fp": c_fp,
                    "tn": c_tn,
                })

    # -------------------------------------------------------------
    # 3. Export CSV Files
    # -------------------------------------------------------------
    out_metrics_csv = REPORTS_DIR / "stage8_9_7_recomputed_metrics.csv"
    with open(out_metrics_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(recomputed_metrics_rows[0].keys()))
        writer.writeheader()
        writer.writerows(recomputed_metrics_rows)

    out_ci_csv = REPORTS_DIR / "stage8_9_7_confidence_intervals.csv"
    with open(out_ci_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(ci_rows[0].keys()))
        writer.writeheader()
        writer.writerows(ci_rows)

    out_cat_csv = REPORTS_DIR / "stage8_9_7_category_metrics.csv"
    with open(out_cat_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(category_metrics_rows[0].keys()))
        writer.writeheader()
        writer.writerows(category_metrics_rows)

    out_cal_csv = REPORTS_DIR / "stage8_9_7_calibration_metrics.csv"
    with open(out_cal_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(calibration_rows[0].keys()))
        writer.writeheader()
        writer.writerows(calibration_rows)

    # -------------------------------------------------------------
    # 4. Formatted Terminal Display
    # -------------------------------------------------------------
    print("\n" + "=" * 115)
    print("STAGE 8.9.7: INDEPENDENT CANDIDATE BENCHMARK AUDIT (HELD-OUT TEST SET N=293)")
    print("=" * 115)
    print(f"{'Model Architecture':26} {'Thresh':6} {'TP':4} {'FP':4} {'FN':4} {'TN':4} {'Acc':7} {'Prec':7} {'Recall':7} {'Hard-FPR':9} {'PR-AUC':7} {'Brier':7} {'ECE':7}")
    print("-" * 115)
    for r in recomputed_metrics_rows:
        print(f"{r['model_architecture']:26} {r['threshold']:6.3f} {r['tp']:4d} {r['fp']:4d} {r['fn']:4d} {r['tn']:4d} "
              f"{r['accuracy']*100:6.1f}% {r['precision']*100:6.1f}% {r['recall']*100:6.1f}% {r['hard_negative_fpr']*100:8.1f}% "
              f"{r['pr_auc']:7.4f} {r['brier_score']:7.4f} {r['ece']:7.4f}")
    print("=" * 115)

    print("\n" + "=" * 95)
    print("CATEGORY BREAKDOWN: RECALL & FALSE POSITIVE RATES ACROSS 8 ACOUSTIC CATEGORIES")
    print("=" * 95)
    cats = sorted(list(set(r["category"] for r in category_metrics_rows)))
    models = [m[0] for m in candidate_models]
    print(f"{'Category':26} {'Type':8} {'N':4} " + " ".join([f"{m[:10]:>10}" for m in models]))
    print("-" * 95)
    for c in cats:
        c_entries = [r for r in category_metrics_rows if r["category"] == c]
        c_type = c_entries[0]["type"]
        c_n = c_entries[0]["total_samples"]
        vals = []
        for m in models:
            m_ent = next((r for r in c_entries if r["model_architecture"] == m), None)
            if m_ent:
                vals.append(f"{m_ent['rate']*100:9.1f}%")
            else:
                vals.append("      N/A")
        print(f"{c:26} {c_type:8} {c_n:4d} " + " ".join(vals))
    print("=" * 95)


if __name__ == "__main__":
    main()
