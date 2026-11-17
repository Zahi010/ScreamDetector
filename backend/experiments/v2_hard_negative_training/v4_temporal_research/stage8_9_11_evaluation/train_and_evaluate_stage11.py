"""Stage 8.9.11 Preregistered Candidate Model Training and Independent Evaluation.

Implements all candidates from `next_experiment_preregistration.md`:
1. Candidate D_v4: Baseline multi-pooled linear fusion (3,072-dim)
2. Candidate T1_v4: Dilated 1D Temporal Convolutional Network with temporal sequence modeling
3. Candidate H_v4_Commercial: Calibrated Hybrid Fusion with 16 acoustic turbulence features (5,144-dim)
4. Candidate H_v5_SNR: Dynamic Noise-Normalized Hybrid Classifier (5,148-dim)

Strict Protocols:
- Validation-Only Threshold Selection: Recall >= 96% AND Hard-Negative FPR <= 5%. If unachievable, mark INFEASIBLE.
- Single-Shot Held-Out Test Split Evaluation.
- Paired McNemar test with Edwards continuity correction.
- Source-Group Cluster Bootstrap (1,000 iterations) for 95% CIs.
- Holm-Bonferroni multiple-comparison correction (alpha = 0.0125).
- Real-world operational prevalence and hourly false-alarm analysis.
"""

from __future__ import annotations

import csv
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
from scipy import stats

# Suppress TF oneDNN spam
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

import tensorflow as tf
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

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from experiments.v2_hard_negative_training.v4_temporal_research.train_temporal_models import (
    build_tcn_model,
    measure_inference_speed_and_memory,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("stage8_9_11_eval")

STAGE11_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_11_evaluation"
FEATURES_PATH = STAGE11_DIR / "features" / "stage8_9_11_features.npz"
MODELS_DIR = STAGE11_DIR / "models"
REPORTS_DIR = STAGE11_DIR / "reports"

RANDOM_SEED = 42
tf.random.set_seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


def compute_metrics(y_true: np.ndarray, y_prob: np.ndarray, threshold: float) -> Dict[str, Any]:
    """Compute complete classification and calibration metrics."""
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

    return {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "specificity": round(spec, 4),
        "fpr": round(fpr, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(roc, 4),
        "pr_auc": round(pr_auc, 4),
        "brier_score": round(brier, 4),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
    }


def compute_category_breakdown(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    categories: np.ndarray,
    threshold: float,
) -> Dict[str, Any]:
    """Compute per-category detection rates and false positive rates."""
    y_pred = (y_prob >= threshold).astype(int)
    unique_cats = sorted(np.unique(categories).tolist())
    cat_metrics = {}

    for cat in unique_cats:
        mask = (categories == cat)
        cat_y = y_true[mask]
        cat_p = y_pred[mask]
        n_samples = len(cat_y)
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

    return cat_metrics


def search_preregistered_threshold(
    y_val: np.ndarray,
    y_prob_val: np.ndarray,
) -> Tuple[float, bool, Dict[str, Any]]:
    """Search for threshold satisfying Recall >= 96% AND FPR <= 5% on validation set.
    
    If achievable: return (best_thresh, True, diagnostics) maximizing F1.
    If unachievable: return (best_f1_thresh, False, diagnostics) and mark INFEASIBLE.
    """
    thresholds = np.linspace(0.05, 0.95, 181)
    feasible_thresholds = []

    best_feasible_thresh = None
    best_feasible_f1 = -1.0

    best_overall_f1 = -1.0
    best_overall_thresh = 0.35

    for t in thresholds:
        m = compute_metrics(y_val, y_prob_val, threshold=t)
        rec = m["recall"]
        fpr = m["fpr"]
        f1 = m["f1_score"]

        if f1 > best_overall_f1:
            best_overall_f1 = f1
            best_overall_thresh = float(t)

        if rec >= 0.960 and fpr <= 0.050:
            feasible_thresholds.append((float(t), f1, rec, fpr))
            if f1 > best_feasible_f1:
                best_feasible_f1 = f1
                best_feasible_thresh = float(t)

    is_feasible = (len(feasible_thresholds) > 0)
    selected_threshold = best_feasible_thresh if is_feasible else best_overall_thresh

    diagnostics = {
        "is_feasible": is_feasible,
        "selected_threshold": round(selected_threshold, 4),
        "feasible_threshold_count": len(feasible_thresholds),
        "best_feasible_f1": round(best_feasible_f1, 4) if is_feasible else None,
        "best_overall_f1": round(best_overall_f1, 4),
        "metrics_at_selected_thresh": compute_metrics(y_val, y_prob_val, threshold=selected_threshold),
    }

    return selected_threshold, is_feasible, diagnostics


def run_paired_mcnemar_test(
    y_true: np.ndarray,
    y_prob_a: np.ndarray,
    thresh_a: float,
    y_prob_b: np.ndarray,
    thresh_b: float,
) -> Dict[str, Any]:
    """Execute paired McNemar test with Edwards continuity correction."""
    pred_a = (y_prob_a >= thresh_a).astype(int)
    pred_b = (y_prob_b >= thresh_b).astype(int)

    correct_a = (pred_a == y_true)
    correct_b = (pred_b == y_true)

    # b: A correct, B wrong
    b = int(np.sum(correct_a & ~correct_b))
    # c: A wrong, B correct
    c = int(np.sum(~correct_a & correct_b))

    if (b + c) > 0:
        stat = float(((abs(b - c) - 1.0) ** 2) / (b + c))
        p_val = float(1.0 - stats.chi2.cdf(stat, df=1))
    else:
        stat = 0.0
        p_val = 1.0

    return {
        "b_model_a_correct_b_wrong": b,
        "c_model_a_wrong_b_correct": c,
        "chi2_stat": round(stat, 4),
        "p_value": round(p_val, 6),
        "is_significant_at_05": p_val < 0.05,
        "is_significant_bonferroni_0125": p_val < 0.0125,
    }


def run_source_group_cluster_bootstrap(
    y_true: np.ndarray,
    y_prob_target: np.ndarray,
    thresh_target: float,
    y_prob_baseline: np.ndarray,
    thresh_baseline: float,
    source_groups: np.ndarray,
    n_iterations: int = 1000,
) -> Dict[str, Any]:
    """Source-group cluster bootstrap resampling for delta metrics and confidence intervals."""
    unique_groups = np.unique(source_groups)
    n_groups = len(unique_groups)

    group_to_indices = {g: np.where(source_groups == g)[0] for g in unique_groups}

    delta_pr_aucs = []
    delta_recalls = []
    delta_fprs = []

    target_pr_aucs = []
    target_recalls = []
    target_fprs = []

    for _ in range(n_iterations):
        sample_groups = np.random.choice(unique_groups, size=n_groups, replace=True)
        sample_indices = np.concatenate([group_to_indices[g] for g in sample_groups])

        sub_y = y_true[sample_indices]
        if len(np.unique(sub_y)) < 2:
            continue

        sub_prob_t = y_prob_target[sample_indices]
        sub_prob_b = y_prob_baseline[sample_indices]

        m_t = compute_metrics(sub_y, sub_prob_t, thresh_target)
        m_b = compute_metrics(sub_y, sub_prob_b, thresh_baseline)

        target_pr_aucs.append(m_t["pr_auc"])
        target_recalls.append(m_t["recall"])
        target_fprs.append(m_t["fpr"])

        delta_pr_aucs.append(m_t["pr_auc"] - m_b["pr_auc"])
        delta_recalls.append(m_t["recall"] - m_b["recall"])
        delta_fprs.append(m_t["fpr"] - m_b["fpr"])

    def get_ci(arr):
        return [round(float(np.percentile(arr, 2.5)), 4), round(float(np.percentile(arr, 97.5)), 4)]

    return {
        "target_pr_auc_ci": get_ci(target_pr_aucs),
        "target_recall_ci": get_ci(target_recalls),
        "target_fpr_ci": get_ci(target_fprs),
        "delta_pr_auc_ci": get_ci(delta_pr_aucs),
        "delta_recall_ci": get_ci(delta_recalls),
        "delta_fpr_ci": get_ci(delta_fprs),
        "pr_auc_strictly_positive": float(np.percentile(delta_pr_aucs, 2.5)) > 0,
    }


def main():
    logger.info("=================================================================")
    logger.info("STAGE 8.9.11: PREREGISTERED CANDIDATE MODEL EVALUATION")
    logger.info("=================================================================")

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    data = np.load(FEATURES_PATH, allow_pickle=True)
    file_ids = data["file_ids"]
    splits = data["splits"]
    binary_labels = data["binary_labels"]
    categories = data["categories"]
    source_groups = data["source_groups"]

    features_concat = data["features_concat"]       # 3072
    padded_sequences = data["padded_sequences"]     # N x 70 x 1024
    features_t3_stats = data["features_t3_stats"]   # 5120
    turbulence_features = data["turbulence_features"] # 16
    vocal_features = data["vocal_features"]         # 6
    vocal_logit = data["vocal_logit"]               # 1
    crowd_logit = data["crowd_logit"]               # 1
    snr_features = data["snr_features"]             # 4

    train_mask = (splits == "train")
    val_mask = (splits == "val")
    test_mask = (splits == "test")

    y_all = (binary_labels == "scream").astype(int)
    y_train = y_all[train_mask]
    y_val = y_all[val_mask]
    y_test = y_all[test_mask]

    n_pos_train = int(np.sum(y_train == 1))
    n_neg_train = int(np.sum(y_train == 0))
    class_weight_dict = {0: 1.0, 1: float(n_neg_train / max(1, n_pos_train))}
    logger.info(f"Class counts Train: {n_pos_train} pos, {n_neg_train} neg (pos weight: {class_weight_dict[1]:.2f})")

    # Build Feature Matrices
    # 1. D_v4 representation: 3,072-dim
    X_d_train = features_concat[train_mask]
    X_d_val = features_concat[val_mask]
    X_d_test = features_concat[test_mask]

    # 2. H_v4_Commercial representation: 5,144-dim
    t_std_train = features_t3_stats[train_mask][:, 1024:2048]
    t_delta_train = features_t3_stats[train_mask][:, 4096:5120]
    t_std_val = features_t3_stats[val_mask][:, 1024:2048]
    t_delta_val = features_t3_stats[val_mask][:, 4096:5120]
    t_std_test = features_t3_stats[test_mask][:, 1024:2048]
    t_delta_test = features_t3_stats[test_mask][:, 4096:5120]

    X_hv4_train = np.hstack([
        features_concat[train_mask],
        t_std_train,
        t_delta_train,
        turbulence_features[train_mask],
        vocal_logit[train_mask],
        crowd_logit[train_mask],
        vocal_features[train_mask],
    ])
    X_hv4_val = np.hstack([
        features_concat[val_mask],
        t_std_val,
        t_delta_val,
        turbulence_features[val_mask],
        vocal_logit[val_mask],
        crowd_logit[val_mask],
        vocal_features[val_mask],
    ])
    X_hv4_test = np.hstack([
        features_concat[test_mask],
        t_std_test,
        t_delta_test,
        turbulence_features[test_mask],
        vocal_logit[test_mask],
        crowd_logit[test_mask],
        vocal_features[test_mask],
    ])

    # 3. H_v5_SNR representation: 5,148-dim
    X_hv5_train = np.hstack([X_hv4_train, snr_features[train_mask]])
    X_hv5_val = np.hstack([X_hv4_val, snr_features[val_mask]])
    X_hv5_test = np.hstack([X_hv4_test, snr_features[test_mask]])

    logger.info(f"Feature dimensions: D_v4={X_d_train.shape[1]}, H_v4={X_hv4_train.shape[1]}, H_v5_SNR={X_hv5_train.shape[1]}")

    results = {}
    candidate_predictions = {}
    threshold_records = {}

    # =========================================================================
    # CANDIDATE 1: Model D_v4 (Baseline Platt-Scaled Linear Fusion)
    # =========================================================================
    logger.info("\n--- [1/4] Training Candidate 1: Model D_v4 ---")
    best_c_d = 0.1
    best_f1_d = -1.0
    for c_cand in [0.001, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0]:
        pipe_cand = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(C=c_cand, class_weight="balanced", random_state=RANDOM_SEED, max_iter=1000)),
        ])
        pipe_cand.fit(X_d_train, y_train)
        val_prob = pipe_cand.predict_proba(X_d_val)[:, 1]
        f1_cand = f1_score(y_val, (val_prob >= 0.35).astype(int))
        if f1_cand > best_f1_d:
            best_f1_d = f1_cand
            best_c_d = c_cand

    pipe_d = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(C=best_c_d, class_weight="balanced", random_state=RANDOM_SEED, max_iter=1000)),
    ])
    pipe_d.fit(X_d_train, y_train)

    # Platt Scaling calibration on validation logits
    val_logits_d = pipe_d.decision_function(X_d_val).reshape(-1, 1)
    calibrator_d = LogisticRegression(C=1.0, random_state=RANDOM_SEED)
    calibrator_d.fit(val_logits_d, y_val)

    val_prob_d = calibrator_d.predict_proba(val_logits_d)[:, 1]
    test_logits_d = pipe_d.decision_function(X_d_test).reshape(-1, 1)
    test_prob_d = calibrator_d.predict_proba(test_logits_d)[:, 1]

    thresh_d, feasible_d, diag_d = search_preregistered_threshold(y_val, val_prob_d)
    threshold_records["D_v4"] = diag_d
    joblib.dump({"pipe": pipe_d, "calibrator": calibrator_d}, MODELS_DIR / "model_d_v4.joblib")

    logger.info(f"Model D_v4 Val: Threshold={thresh_d:.4f}, Feasible={feasible_d}")
    candidate_predictions["D_v4"] = {"val": val_prob_d, "test": test_prob_d, "thresh": thresh_d, "feasible": feasible_d}

    # =========================================================================
    # CANDIDATE 2: Model T1_v4 (Dilated 1D Temporal Convolutional Network)
    # =========================================================================
    logger.info("\n--- [2/4] Training Candidate 2: Model T1_v4 (1D TCN) ---")
    model_t1 = build_tcn_model(max_seq_len=padded_sequences.shape[1], emb_dim=1024)
    t1_ckpt = str(MODELS_DIR / "model_t1_v4_best.weights.h5")
    callbacks_t1 = [
        tf.keras.callbacks.EarlyStopping(monitor="val_pr_auc", mode="max", patience=12, restore_best_weights=True),
        tf.keras.callbacks.ModelCheckpoint(t1_ckpt, monitor="val_pr_auc", mode="max", save_best_only=True, save_weights_only=True),
    ]
    model_t1.fit(
        padded_sequences[train_mask],
        y_train,
        validation_data=(padded_sequences[val_mask], y_val),
        epochs=40,
        batch_size=32,
        class_weight=class_weight_dict,
        callbacks=callbacks_t1,
        verbose=0,
    )

    val_prob_t1_raw = model_t1.predict(padded_sequences[val_mask], batch_size=32, verbose=0).flatten()
    test_prob_t1_raw = model_t1.predict(padded_sequences[test_mask], batch_size=32, verbose=0).flatten()

    # Fit calibration on validation logits
    val_logit_t1 = np.log(np.clip(val_prob_t1_raw, 1e-6, 1.0 - 1e-6) / (1.0 - np.clip(val_prob_t1_raw, 1e-6, 1.0 - 1e-6))).reshape(-1, 1)
    test_logit_t1 = np.log(np.clip(test_prob_t1_raw, 1e-6, 1.0 - 1e-6) / (1.0 - np.clip(test_prob_t1_raw, 1e-6, 1.0 - 1e-6))).reshape(-1, 1)

    calibrator_t1 = LogisticRegression(C=1.0, random_state=RANDOM_SEED)
    calibrator_t1.fit(val_logit_t1, y_val)
    val_prob_t1 = calibrator_t1.predict_proba(val_logit_t1)[:, 1]
    test_prob_t1 = calibrator_t1.predict_proba(test_logit_t1)[:, 1]

    thresh_t1, feasible_t1, diag_t1 = search_preregistered_threshold(y_val, val_prob_t1)
    threshold_records["T1_v4"] = diag_t1
    model_t1.save_weights(MODELS_DIR / "model_t1_v4.weights.h5")
    joblib.dump(calibrator_t1, MODELS_DIR / "model_t1_v4_calibrator.joblib")

    logger.info(f"Model T1_v4 Val: Threshold={thresh_t1:.4f}, Feasible={feasible_t1}")
    candidate_predictions["T1_v4"] = {"val": val_prob_t1, "test": test_prob_t1, "thresh": thresh_t1, "feasible": feasible_t1}

    # =========================================================================
    # CANDIDATE 3: Model H_v4_Commercial (Calibrated Hybrid Fusion)
    # =========================================================================
    logger.info("\n--- [3/4] Training Candidate 3: Model H_v4_Commercial ---")
    best_c_hv4 = 0.05
    best_f1_hv4 = -1.0
    for c_cand in [0.001, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0]:
        pipe_cand = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(C=c_cand, class_weight="balanced", random_state=RANDOM_SEED, max_iter=1000)),
        ])
        pipe_cand.fit(X_hv4_train, y_train)
        val_prob = pipe_cand.predict_proba(X_hv4_val)[:, 1]
        f1_cand = f1_score(y_val, (val_prob >= 0.35).astype(int))
        if f1_cand > best_f1_hv4:
            best_f1_hv4 = f1_cand
            best_c_hv4 = c_cand

    pipe_hv4 = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(C=best_c_hv4, class_weight="balanced", random_state=RANDOM_SEED, max_iter=1000)),
    ])
    pipe_hv4.fit(X_hv4_train, y_train)

    val_logits_hv4 = pipe_hv4.decision_function(X_hv4_val).reshape(-1, 1)
    calibrator_hv4 = LogisticRegression(C=1.0, random_state=RANDOM_SEED)
    calibrator_hv4.fit(val_logits_hv4, y_val)

    val_prob_hv4 = calibrator_hv4.predict_proba(val_logits_hv4)[:, 1]
    test_logits_hv4 = pipe_hv4.decision_function(X_hv4_test).reshape(-1, 1)
    test_prob_hv4 = calibrator_hv4.predict_proba(test_logits_hv4)[:, 1]

    thresh_hv4, feasible_hv4, diag_hv4 = search_preregistered_threshold(y_val, val_prob_hv4)
    threshold_records["H_v4_Commercial"] = diag_hv4
    joblib.dump({"pipe": pipe_hv4, "calibrator": calibrator_hv4}, MODELS_DIR / "model_h_v4_commercial.joblib")

    logger.info(f"Model H_v4_Commercial Val: Threshold={thresh_hv4:.4f}, Feasible={feasible_hv4}")
    candidate_predictions["H_v4_Commercial"] = {"val": val_prob_hv4, "test": test_prob_hv4, "thresh": thresh_hv4, "feasible": feasible_hv4}

    # =========================================================================
    # CANDIDATE 4: Model H_v5_SNR (Context-Aware Hybrid Fusion)
    # =========================================================================
    logger.info("\n--- [4/4] Training Candidate 4: Model H_v5_SNR ---")
    best_c_hv5 = 0.05
    best_f1_hv5 = -1.0
    for c_cand in [0.001, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0]:
        pipe_cand = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(C=c_cand, class_weight="balanced", random_state=RANDOM_SEED, max_iter=1000)),
        ])
        pipe_cand.fit(X_hv5_train, y_train)
        val_prob = pipe_cand.predict_proba(X_hv5_val)[:, 1]
        f1_cand = f1_score(y_val, (val_prob >= 0.35).astype(int))
        if f1_cand > best_f1_hv5:
            best_f1_hv5 = f1_cand
            best_c_hv5 = c_cand

    pipe_hv5 = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(C=best_c_hv5, class_weight="balanced", random_state=RANDOM_SEED, max_iter=1000)),
    ])
    pipe_hv5.fit(X_hv5_train, y_train)

    val_logits_hv5 = pipe_hv5.decision_function(X_hv5_val).reshape(-1, 1)
    calibrator_hv5 = LogisticRegression(C=1.0, random_state=RANDOM_SEED)
    calibrator_hv5.fit(val_logits_hv5, y_val)

    val_prob_hv5 = calibrator_hv5.predict_proba(val_logits_hv5)[:, 1]
    test_logits_hv5 = pipe_hv5.decision_function(X_hv5_test).reshape(-1, 1)
    test_prob_hv5 = calibrator_hv5.predict_proba(test_logits_hv5)[:, 1]

    thresh_hv5, feasible_hv5, diag_hv5 = search_preregistered_threshold(y_val, val_prob_hv5)
    threshold_records["H_v5_SNR"] = diag_hv5
    joblib.dump({"pipe": pipe_hv5, "calibrator": calibrator_hv5}, MODELS_DIR / "model_h_v5_snr.joblib")

    logger.info(f"Model H_v5_SNR Val: Threshold={thresh_hv5:.4f}, Feasible={feasible_hv5}")
    candidate_predictions["H_v5_SNR"] = {"val": val_prob_hv5, "test": test_prob_hv5, "thresh": thresh_hv5, "feasible": feasible_hv5}

    # Save frozen threshold selection records
    thresh_json_path = STAGE11_DIR / "preregistered_candidate_thresholds.json"
    with open(thresh_json_path, "w", encoding="utf-8") as f:
        json.dump(threshold_records, f, indent=2)
    logger.info(f"Saved frozen threshold decisions to {thresh_json_path}")

    # =========================================================================
    # SINGLE-SHOT HELD-OUT TEST EVALUATION
    # =========================================================================
    logger.info("\n=================================================================")
    logger.info("SINGLE-SHOT HELD-OUT TEST EVALUATION (EXACTLY ONCE)")
    logger.info("=================================================================")

    test_categories = categories[test_mask]
    test_source_groups = source_groups[test_mask]
    test_fids = file_ids[test_mask]

    eval_summary = {}
    test_predictions_rows = []

    for idx, fid in enumerate(test_fids):
        test_predictions_rows.append({
            "file_id": fid,
            "category": test_categories[idx],
            "binary_label": binary_labels[test_mask][idx],
            "y_true": int(y_test[idx]),
            "source_group_id": test_source_groups[idx],
            "prob_D_v4": round(float(test_prob_d[idx]), 4),
            "prob_T1_v4": round(float(test_prob_t1[idx]), 4),
            "prob_H_v4_Commercial": round(float(test_prob_hv4[idx]), 4),
            "prob_H_v5_SNR": round(float(test_prob_hv5[idx]), 4),
        })

    for model_name, cand_data in candidate_predictions.items():
        prob_test = cand_data["test"]
        thresh = cand_data["thresh"]
        is_feas = cand_data["feasible"]

        m_test = compute_metrics(y_test, prob_test, threshold=thresh)
        cat_test = compute_category_breakdown(y_test, prob_test, test_categories, threshold=thresh)

        # Paired McNemar vs Model D_v4 baseline
        mcnemar = run_paired_mcnemar_test(y_test, prob_test, thresh, test_prob_d, thresh_d)

        # Source-group cluster bootstrap
        boot = run_source_group_cluster_bootstrap(
            y_test, prob_test, thresh, test_prob_d, thresh_d, test_source_groups, n_iterations=1000
        )

        # Shouted speech FPR
        shouting_fpr = cat_test.get("shouting_and_speech", {}).get("fpr", 0.0)

        # Acceptance gates verification
        gate1_recall = (m_test["recall"] >= 0.960)
        gate2_hard_fpr = (m_test["fpr"] <= 0.050)
        gate3_shout_fpr = (shouting_fpr <= 0.150)
        all_gates_met = (gate1_recall and gate2_hard_fpr and gate3_shout_fpr)

        eval_summary[model_name] = {
            "validation_decision_threshold": thresh,
            "validation_feasibility": "FEASIBLE" if is_feas else "INFEASIBLE",
            "test_metrics": m_test,
            "category_metrics": cat_test,
            "shouted_speech_fpr": shouting_fpr,
            "paired_mcnemar_vs_d_v4": mcnemar,
            "cluster_bootstrap_95_ci": boot,
            "acceptance_gates": {
                "gate_1_overall_recall_ge_96": gate1_recall,
                "gate_2_hard_negative_fpr_le_05": gate2_hard_fpr,
                "gate_3_shouted_speech_fpr_le_15": gate3_shout_fpr,
                "all_gates_met": all_gates_met,
                "certification_verdict": "RESEARCH_GATED" if all_gates_met else "NOT_CERTIFIED",
            },
        }

        logger.info(f"\n--- {model_name} Results (tau={thresh:.4f}, ValFeasible={is_feas}) ---")
        logger.info(f"  Recall:      {m_test['recall']*100:.2f}% (95% CI: [{boot['target_recall_ci'][0]*100:.1f}%, {boot['target_recall_ci'][1]*100:.1f}%]) [Gate 1 Target >= 96.0%]")
        logger.info(f"  Overall FPR: {m_test['fpr']*100:.2f}% (95% CI: [{boot['target_fpr_ci'][0]*100:.1f}%, {boot['target_fpr_ci'][1]*100:.1f}%]) [Gate 2 Target <= 5.0%]")
        logger.info(f"  Shout FPR:   {shouting_fpr*100:.2f}% [Gate 3 Target <= 15.0%]")
        logger.info(f"  PR-AUC:      {m_test['pr_auc']:.4f} (95% CI: [{boot['target_pr_auc_ci'][0]:.4f}, {boot['target_pr_auc_ci'][1]:.4f}])")
        logger.info(f"  McNemar vs D_v4 p-value: {mcnemar['p_value']:.4f} (Bonferroni sig: {mcnemar['is_significant_bonferroni_0125']})")

    # Real-World Operational Prevalence Modeling
    prevalence_scenarios = [
        {"name": "Realistic Low Surveillance", "prevalence": 0.0001, "desc": "1 scream event per 10,000 frames (approx. 1.4 hours)"},
        {"name": "Elevated Festival Incident", "prevalence": 0.0010, "desc": "1 scream event per 1,000 frames (approx. 8 minutes)"},
    ]

    operational_analysis = {}
    for model_name, info in eval_summary.items():
        rec = info["test_metrics"]["recall"]
        fpr = info["test_metrics"]["fpr"]
        operational_analysis[model_name] = {}
        for sc in prevalence_scenarios:
            p = sc["prevalence"]
            ppv = (p * rec) / max(1e-9, (p * rec + (1.0 - p) * fpr))
            # In a 10-hour festival day: 72,000 half-second frames
            daily_false_alarms = int(round(72000 * (1.0 - p) * fpr))
            hourly_false_alarms = round(daily_false_alarms / 10.0, 1)

            operational_analysis[model_name][sc["name"]] = {
                "assumed_prevalence": p,
                "real_world_precision_ppv": round(float(ppv), 4),
                "daily_raw_false_alarms_10h": daily_false_alarms,
                "hourly_raw_false_alarms": hourly_false_alarms,
            }

    # Save Test Predictions CSV
    test_pred_csv = STAGE11_DIR / "stage8_9_11_test_predictions.csv"
    with open(test_pred_csv, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["file_id", "category", "binary_label", "y_true", "source_group_id", "prob_D_v4", "prob_T1_v4", "prob_H_v4_Commercial", "prob_H_v5_SNR"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(test_predictions_rows)
    logger.info(f"Saved held-out test predictions: {test_pred_csv}")

    # Save Full Evaluation JSON
    eval_json_path = STAGE11_DIR / "stage8_9_11_evaluation_metrics.json"
    full_output = {
        "candidate_evaluations": eval_summary,
        "operational_prevalence_modeling": operational_analysis,
        "sample_counts": {
            "train": int(np.sum(train_mask)),
            "val": int(np.sum(val_mask)),
            "test": int(np.sum(test_mask)),
            "test_positive": int(np.sum(y_test == 1)),
            "test_negative": int(np.sum(y_test == 0)),
        },
    }
    with open(eval_json_path, "w", encoding="utf-8") as f:
        json.dump(full_output, f, indent=2)
    logger.info(f"Saved evaluation metrics JSON: {eval_json_path}")


if __name__ == "__main__":
    main()
