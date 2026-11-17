"""Hybrid Acoustic Classifier Research and Candidate Training Pipeline (Stage 8.9.7).

Implements and benchmarks:
- Model A v3: Frozen Baseline Logistic Regression (C=10.0, max-pooling 1024-d, tau=0.35)
- Model D v3: Multi-Pooling Concatenated Logistic Regression (C tuned on val, 3072-d)
- Model G: Hybrid Feature Concatenation + Dedicated Vocal & Crowd Contrastive Logits (3080-d)
- Model H: Calibrated Hybrid Architecture (Platt Scaling on Validation Logits)
- Model I: Non-Linear Regularized Gradient Boosted Decision Tree (HistGradientBoosting on hybrid representation)

Guarantees:
- Models trained strictly on `train` split
- Hyperparameters and decision thresholds tuned strictly on `val` split
- `test` split remains strictly untouched held-out evaluation benchmark
- Calibrated probabilities evaluated with Brier score and ECE
"""

from __future__ import annotations

import csv
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("train_hybrid_models")

EXPERIMENT_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training"
FEATURES_PATH = EXPERIMENT_DIR / "features" / "yamnet_features_v3.npz"
MODELS_OUT_DIR = EXPERIMENT_DIR / "models"
REPORTS_OUT_DIR = EXPERIMENT_DIR / "reports"

RANDOM_SEED = 42


def compute_metrics(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float,
) -> Dict[str, Any]:
    """Compute complete binary classification and calibration metrics."""
    y_pred = (y_prob >= threshold).astype(int)
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()

    acc = float((tp + tn) / max(1, len(y_true)))
    prec = float(tp / max(1, tp + fp))
    rec = float(tp / max(1, tp + fn))
    spec = float(tn / max(1, tn + fp))
    fpr = float(fp / max(1, tn + fp))
    f1 = float(2 * prec * rec / max(1e-6, prec + rec))

    try:
        roc = float(roc_auc_score(y_true, y_prob))
    except Exception:
        roc = 0.0

    try:
        pr_auc = float(average_precision_score(y_true, y_prob))
    except Exception:
        pr_auc = 0.0

    try:
        brier = float(brier_score_loss(y_true, y_prob))
    except Exception:
        brier = 0.0

    # Expected Calibration Error (ECE) with 10 bins
    bins = np.linspace(0.0, 1.0, 11)
    ece = 0.0
    for i in range(10):
        bin_mask = (y_prob >= bins[i]) & (y_prob < bins[i + 1])
        if np.sum(bin_mask) > 0:
            bin_acc = np.mean(y_true[bin_mask])
            bin_conf = np.mean(y_prob[bin_mask])
            ece += (np.sum(bin_mask) / len(y_true)) * abs(bin_acc - bin_conf)

    return {
        "tp": int(tp),
        "fp": int(fp),
        "fn": int(fn),
        "tn": int(tn),
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "specificity": round(spec, 4),
        "fpr": round(fpr, 4),
        "f1": round(f1, 4),
        "roc_auc": round(roc, 4),
        "pr_auc": round(pr_auc, 4),
        "brier_score": round(brier, 4),
        "ece": round(float(ece), 4),
        "threshold": round(threshold, 4),
    }


def compute_category_breakdown(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    categories: np.ndarray,
    threshold: float,
) -> Dict[str, Dict[str, Any]]:
    """Compute per-category TPR / FPR metrics."""
    y_pred = (y_prob >= threshold).astype(int)
    cat_metrics = {}
    unique_cats = sorted(list(set(categories)))

    for cat in unique_cats:
        mask = (categories == cat)
        cat_y = y_true[mask]
        cat_p = y_pred[mask]
        n_samples = int(np.sum(mask))
        n_pos = int(np.sum(cat_y == 1))
        n_neg = int(np.sum(cat_y == 0))

        if n_pos > 0 and n_neg == 0:
            tp = int(np.sum((cat_p == 1) & (cat_y == 1)))
            rec = float(tp / n_pos)
            cat_metrics[cat] = {
                "total": n_samples,
                "n_pos": n_pos,
                "n_neg": n_neg,
                "tp": tp,
                "fn": n_pos - tp,
                "recall": round(rec, 4),
                "type": "positive",
            }
        elif n_neg > 0 and n_pos == 0:
            fp = int(np.sum((cat_p == 1) & (cat_y == 0)))
            fpr = float(fp / n_neg)
            cat_metrics[cat] = {
                "total": n_samples,
                "n_pos": n_pos,
                "n_neg": n_neg,
                "fp": fp,
                "tn": n_neg - fp,
                "fpr": round(fpr, 4),
                "type": "negative",
            }
        else:
            cat_metrics[cat] = {
                "total": n_samples,
                "n_pos": n_pos,
                "n_neg": n_neg,
                "type": "mixed",
            }

    return cat_metrics


def optimize_threshold_on_val(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    target_recall: float = 0.90,
) -> Tuple[float, float]:
    """Find two thresholds on validation set:
    1. F1-optimal threshold (balanced F1 score)
    2. High-recall safety threshold (maximizing F1 subject to Recall >= target_recall, or min Bayes risk)
    """
    thresholds = np.linspace(0.05, 0.90, 86)
    best_f1_thresh = 0.35
    best_f1 = -1.0

    best_safety_thresh = 0.35
    best_safety_score = -1e9

    for t in thresholds:
        y_pred = (y_prob >= t).astype(int)
        cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel()
        rec = tp / max(1, tp + fn)
        prec = tp / max(1, tp + fp)
        fpr = fp / max(1, tn + fp)
        f1 = 2 * prec * rec / max(1e-6, prec + rec)

        if f1 > best_f1:
            best_f1 = f1
            best_f1_thresh = float(t)

        # Safety-prioritized Bayes risk: 3x penalty on missed screams
        safety_score = - (3.0 * fn + 1.0 * fp)
        if safety_score > best_safety_score:
            best_safety_score = safety_score
            best_safety_thresh = float(t)

    return best_f1_thresh, best_safety_thresh


def main():
    logger.info("=" * 70)
    logger.info("STAGE 8.9.7: HYBRID ACOUSTIC CLASSIFIER RESEARCH & BENCHMARK")
    logger.info("=" * 70)

    if not FEATURES_PATH.exists():
        logger.error(f"Features file not found: {FEATURES_PATH}")
        sys.exit(1)

    data = np.load(FEATURES_PATH, allow_pickle=True)
    file_ids = data["file_ids"]
    splits = data["splits"]
    binary_labels = data["binary_labels"]
    categories = data["categories"]
    source_groups = data["source_groups"]

    features_max = data["features_max"]
    features_p90 = data["features_p90"]
    features_mean = data["features_mean"]
    features_concat = data["features_concat"]
    yamnet_scores_mean = data["yamnet_scores_mean"]
    vocal_features = data["vocal_features"]

    logger.info(f"Loaded feature cache: {len(file_ids)} samples.")

    binary_mask = (binary_labels == "scream") | (binary_labels == "non_scream")
    y_all = (binary_labels == "scream").astype(int)

    train_mask = (splits == "train") & binary_mask
    val_mask = (splits == "val") & binary_mask
    test_mask = (splits == "test") & binary_mask

    logger.info(f"Binary samples: Train={np.sum(train_mask)} ({np.sum(y_all[train_mask])} screams), "
                f"Val={np.sum(val_mask)} ({np.sum(y_all[val_mask])} screams), "
                f"Test={np.sum(test_mask)} ({np.sum(y_all[test_mask])} screams).")

    MODELS_OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_OUT_DIR.mkdir(parents=True, exist_ok=True)

    results = {}
    test_predictions_dict = {
        "file_id": file_ids[test_mask],
        "category": categories[test_mask],
        "binary_label": binary_labels[test_mask],
        "y_true": y_all[test_mask],
    }

    # -------------------------------------------------------------
    # 1. Candidate 1: Model A v3 (Baseline Frozen LR on Max-Pooling)
    # -------------------------------------------------------------
    logger.info("\n--- Training Model A v3 (Baseline LR on Max-Pooling) ---")
    pipe_a = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(C=10.0, class_weight="balanced", random_state=RANDOM_SEED, max_iter=1000)),
    ])
    pipe_a.fit(features_max[train_mask], y_all[train_mask])

    val_prob_a = pipe_a.predict_proba(features_max[val_mask])[:, 1]
    test_prob_a = pipe_a.predict_proba(features_max[test_mask])[:, 1]

    thresh_a = 0.35
    val_metrics_a = compute_metrics(y_all[val_mask], val_prob_a, threshold=thresh_a)
    test_metrics_a = compute_metrics(y_all[test_mask], test_prob_a, threshold=thresh_a)
    test_cat_a = compute_category_breakdown(y_all[test_mask], test_prob_a, categories[test_mask], threshold=thresh_a)

    joblib.dump(pipe_a, MODELS_OUT_DIR / "candidate_model_a_v3_baseline_lr.joblib")
    results["Model_A_v3_Baseline"] = {
        "threshold": thresh_a,
        "val_metrics": val_metrics_a,
        "test_metrics": test_metrics_a,
        "category_metrics": test_cat_a,
    }
    test_predictions_dict["prob_model_a"] = np.round(test_prob_a, 4)
    logger.info(f"Model A Test (tau=0.35): Recall={test_metrics_a['recall']*100:.1f}%, FPR={test_metrics_a['fpr']*100:.1f}%, PR-AUC={test_metrics_a['pr_auc']:.4f}")

    # -------------------------------------------------------------
    # 2. Candidate 2: Model D v3 (Multi-Pooling Concatenated LR)
    # -------------------------------------------------------------
    logger.info("\n--- Training Model D v3 (Multi-Pooling Concatenated LR) ---")
    best_c_d = 1.0
    best_val_f1_d = -1.0
    for c_cand in [0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0]:
        cand_pipe = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(C=c_cand, class_weight="balanced", random_state=RANDOM_SEED, max_iter=1000)),
        ])
        cand_pipe.fit(features_concat[train_mask], y_all[train_mask])
        cand_val_p = cand_pipe.predict_proba(features_concat[val_mask])[:, 1]
        cand_f1 = f1_score(y_all[val_mask], (cand_val_p >= 0.35).astype(int))
        if cand_f1 > best_val_f1_d:
            best_val_f1_d = cand_f1
            best_c_d = c_cand

    logger.info(f"Model D selected C={best_c_d} based strictly on validation split.")
    pipe_d = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(C=best_c_d, class_weight="balanced", random_state=RANDOM_SEED, max_iter=1000)),
    ])
    pipe_d.fit(features_concat[train_mask], y_all[train_mask])

    val_prob_d = pipe_d.predict_proba(features_concat[val_mask])[:, 1]
    test_prob_d = pipe_d.predict_proba(features_concat[test_mask])[:, 1]

    # Evaluate at standard operational threshold 0.35 and validation-tuned threshold
    thresh_f1_d, thresh_safety_d = optimize_threshold_on_val(y_all[val_mask], val_prob_d)
    thresh_d = thresh_f1_d  # Validation F1-optimal threshold
    val_metrics_d = compute_metrics(y_all[val_mask], val_prob_d, threshold=thresh_d)
    test_metrics_d = compute_metrics(y_all[test_mask], test_prob_d, threshold=thresh_d)
    test_cat_d = compute_category_breakdown(y_all[test_mask], test_prob_d, categories[test_mask], threshold=thresh_d)

    joblib.dump(pipe_d, MODELS_OUT_DIR / "candidate_model_d_v3_concat_lr.joblib")
    results["Model_D_v3_Concat_LR"] = {
        "best_C": best_c_d,
        "threshold": thresh_d,
        "val_metrics": val_metrics_d,
        "test_metrics": test_metrics_d,
        "category_metrics": test_cat_d,
    }
    test_predictions_dict["prob_model_d"] = np.round(test_prob_d, 4)
    logger.info(f"Model D Test (tau={thresh_d:.2f}): Recall={test_metrics_d['recall']*100:.1f}%, FPR={test_metrics_d['fpr']*100:.1f}%, PR-AUC={test_metrics_d['pr_auc']:.4f}")

    # -------------------------------------------------------------
    # 3. Candidate 3: Model G (Hybrid Feature Concatenation + Dedicated Contrastive Logits)
    # -------------------------------------------------------------
    logger.info("\n--- Training Model G (Hybrid Feature Concatenation + Dedicated Contrastive Logits) ---")
    # Step 3a: Front-end Vocal Presence Classifier
    is_vocal_train = np.isin(categories[train_mask], ["scream", "shouting_and_speech", "infant_crying", "crowd_chant_cheering"]).astype(int)
    pipe_vocal = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(C=1.0, class_weight="balanced", random_state=RANDOM_SEED, max_iter=1000)),
    ])
    pipe_vocal.fit(features_concat[train_mask], is_vocal_train)

    # Step 3b: Front-end Crowd Contrastive Classifier
    is_crowd_train = (categories[train_mask] == "crowd_chant_cheering").astype(int)
    pipe_crowd = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(C=1.0, class_weight="balanced", random_state=RANDOM_SEED, max_iter=1000)),
    ])
    pipe_crowd.fit(features_concat[train_mask], is_crowd_train)

    # Continuous logits
    vocal_logit_train = pipe_vocal.decision_function(features_concat[train_mask]).reshape(-1, 1)
    vocal_logit_val = pipe_vocal.decision_function(features_concat[val_mask]).reshape(-1, 1)
    vocal_logit_test = pipe_vocal.decision_function(features_concat[test_mask]).reshape(-1, 1)

    crowd_logit_train = pipe_crowd.decision_function(features_concat[train_mask]).reshape(-1, 1)
    crowd_logit_val = pipe_crowd.decision_function(features_concat[val_mask]).reshape(-1, 1)
    crowd_logit_test = pipe_crowd.decision_function(features_concat[test_mask]).reshape(-1, 1)

    # Construct Augmented 3080-dim representation
    X_train_g = np.hstack([features_concat[train_mask], vocal_logit_train, crowd_logit_train, vocal_features[train_mask]])
    X_val_g = np.hstack([features_concat[val_mask], vocal_logit_val, crowd_logit_val, vocal_features[val_mask]])
    X_test_g = np.hstack([features_concat[test_mask], vocal_logit_test, crowd_logit_test, vocal_features[test_mask]])

    best_c_g = 0.5
    best_val_f1_g = -1.0
    for c_cand in [0.01, 0.05, 0.1, 0.5, 1.0, 5.0]:
        cand_pipe = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(C=c_cand, class_weight="balanced", random_state=RANDOM_SEED, max_iter=1000)),
        ])
        cand_pipe.fit(X_train_g, y_all[train_mask])
        cand_val_p = cand_pipe.predict_proba(X_val_g)[:, 1]
        cand_f1 = f1_score(y_all[val_mask], (cand_val_p >= 0.35).astype(int))
        if cand_f1 > best_val_f1_g:
            best_val_f1_g = cand_f1
            best_c_g = c_cand

    logger.info(f"Model G selected C={best_c_g} based strictly on validation split.")
    pipe_g = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(C=best_c_g, class_weight="balanced", random_state=RANDOM_SEED, max_iter=1000)),
    ])
    pipe_g.fit(X_train_g, y_all[train_mask])

    val_prob_g = pipe_g.predict_proba(X_val_g)[:, 1]
    test_prob_g = pipe_g.predict_proba(X_test_g)[:, 1]

    thresh_f1_g, _ = optimize_threshold_on_val(y_all[val_mask], val_prob_g)
    thresh_g = thresh_f1_g
    val_metrics_g = compute_metrics(y_all[val_mask], val_prob_g, threshold=thresh_g)
    test_metrics_g = compute_metrics(y_all[test_mask], test_prob_g, threshold=thresh_g)
    test_cat_g = compute_category_breakdown(y_all[test_mask], test_prob_g, categories[test_mask], threshold=thresh_g)

    hybrid_bundle = {
        "vocal_pipeline": pipe_vocal,
        "crowd_pipeline": pipe_crowd,
        "classifier_pipeline": pipe_g,
        "best_C": best_c_g,
        "selected_threshold": thresh_g,
    }
    joblib.dump(hybrid_bundle, MODELS_OUT_DIR / "candidate_model_g_hybrid_concat.joblib")
    results["Model_G_Hybrid_Concat"] = {
        "best_C": best_c_g,
        "threshold": thresh_g,
        "val_metrics": val_metrics_g,
        "test_metrics": test_metrics_g,
        "category_metrics": test_cat_g,
    }
    test_predictions_dict["prob_model_g"] = np.round(test_prob_g, 4)
    logger.info(f"Model G Test (tau={thresh_g:.2f}): Recall={test_metrics_g['recall']*100:.1f}%, FPR={test_metrics_g['fpr']*100:.1f}%, PR-AUC={test_metrics_g['pr_auc']:.4f}")

    # -------------------------------------------------------------
    # 4. Candidate 4: Model H (Calibrated Hybrid Pipeline with Platt Scaling)
    # -------------------------------------------------------------
    logger.info("\n--- Training Model H (Calibrated Hybrid with Platt Scaling on Val) ---")
    val_logits_g = pipe_g.decision_function(X_val_g).reshape(-1, 1)
    test_logits_g = pipe_g.decision_function(X_test_g).reshape(-1, 1)

    platt_scaler = LogisticRegression(C=1.0, solver="lbfgs", random_state=RANDOM_SEED)
    platt_scaler.fit(val_logits_g, y_all[val_mask])

    val_prob_h = platt_scaler.predict_proba(val_logits_g)[:, 1]
    test_prob_h = platt_scaler.predict_proba(test_logits_g)[:, 1]

    thresh_f1_h, _ = optimize_threshold_on_val(y_all[val_mask], val_prob_h)
    thresh_h = thresh_f1_h
    val_metrics_h = compute_metrics(y_all[val_mask], val_prob_h, threshold=thresh_h)
    test_metrics_h = compute_metrics(y_all[test_mask], test_prob_h, threshold=thresh_h)
    test_cat_h = compute_category_breakdown(y_all[test_mask], test_prob_h, categories[test_mask], threshold=thresh_h)

    model_h_bundle = {
        "hybrid_bundle": hybrid_bundle,
        "platt_scaler": platt_scaler,
        "selected_threshold": thresh_h,
    }
    joblib.dump(model_h_bundle, MODELS_OUT_DIR / "candidate_model_h_calibrated_hybrid.joblib")
    results["Model_H_Calibrated_Hybrid"] = {
        "calibration_method": "Platt_scaling_logistic",
        "threshold": thresh_h,
        "val_metrics": val_metrics_h,
        "test_metrics": test_metrics_h,
        "category_metrics": test_cat_h,
    }
    test_predictions_dict["prob_model_h"] = np.round(test_prob_h, 4)
    logger.info(f"Model H Test (tau={thresh_h:.2f}): Recall={test_metrics_h['recall']*100:.1f}%, FPR={test_metrics_h['fpr']*100:.1f}%, Brier={test_metrics_h['brier_score']:.4f}, ECE={test_metrics_h['ece']:.4f}")

    # -------------------------------------------------------------
    # 5. Candidate 5: Model I (Non-Linear Regularized Gradient Boosted Trees)
    # -------------------------------------------------------------
    logger.info("\n--- Training Model I (HistGradientBoosting on Hybrid Representation) ---")
    clf_i = HistGradientBoostingClassifier(
        max_iter=150,
        max_depth=4,
        learning_rate=0.03,
        min_samples_leaf=10,
        l2_regularization=1.0,
        class_weight="balanced",
        random_state=RANDOM_SEED,
    )
    clf_i.fit(X_train_g, y_all[train_mask])

    val_prob_i = clf_i.predict_proba(X_val_g)[:, 1]
    test_prob_i = clf_i.predict_proba(X_test_g)[:, 1]

    thresh_f1_i, _ = optimize_threshold_on_val(y_all[val_mask], val_prob_i)
    thresh_i = thresh_f1_i
    val_metrics_i = compute_metrics(y_all[val_mask], val_prob_i, threshold=thresh_i)
    test_metrics_i = compute_metrics(y_all[test_mask], test_prob_i, threshold=thresh_i)
    test_cat_i = compute_category_breakdown(y_all[test_mask], test_prob_i, categories[test_mask], threshold=thresh_i)

    joblib.dump(clf_i, MODELS_OUT_DIR / "candidate_model_i_nonlinear_gbt.joblib")
    results["Model_I_NonLinear_GBT"] = {
        "threshold": thresh_i,
        "val_metrics": val_metrics_i,
        "test_metrics": test_metrics_i,
        "category_metrics": test_cat_i,
    }
    test_predictions_dict["prob_model_i"] = np.round(test_prob_i, 4)
    logger.info(f"Model I Test (tau={thresh_i:.2f}): Recall={test_metrics_i['recall']*100:.1f}%, FPR={test_metrics_i['fpr']*100:.1f}%, PR-AUC={test_metrics_i['pr_auc']:.4f}")

    # -------------------------------------------------------------
    # 6. Save Complete Benchmark Summary and Test Predictions
    # -------------------------------------------------------------
    summary_path = REPORTS_OUT_DIR / "stage8_9_7_benchmark_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    pred_csv_path = REPORTS_OUT_DIR / "stage8_9_7_test_predictions.csv"
    with open(pred_csv_path, "w", newline="", encoding="utf-8") as f:
        keys = list(test_predictions_dict.keys())
        writer = csv.writer(f)
        writer.writerow(keys)
        n_test = len(test_predictions_dict["file_id"])
        for idx in range(n_test):
            row = [test_predictions_dict[k][idx] for k in keys]
            writer.writerow(row)

    logger.info(f"\nSaved benchmark summary to {summary_path}")
    logger.info(f"Saved test predictions to {pred_csv_path}")


if __name__ == "__main__":
    main()
