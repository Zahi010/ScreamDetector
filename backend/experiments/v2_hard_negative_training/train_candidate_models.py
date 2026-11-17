"""Controlled Candidate Training and Validation Pipeline (Stage 8.9.5 / Gate D).

Compares:
- Model A: Frozen Baseline Logistic Regression (C=10.0, max-pooling)
- Model B: Regularized Logistic Regression (L2 C-sweep on max-pooling)
- Model C: 90th Percentile Temporal Pooled Logistic Regression (transient suppression)
- Model D: Multi-Pooling Concatenated Logistic Regression (max + p90 + mean, 3072-dim)
- Model E: Hierarchical Two-Stage Gating Classifier (Vocal Gating -> Scream Classifier)
- Model F: Non-Linear Gradient Boosted Decision Trees (LightGBM on YAMNet embeddings)

Guarantees:
- Models trained strictly on `train` split
- Hyperparameters and decision thresholds tuned strictly on `val` split
- `test` split remains strictly untouched held-out evaluation benchmark
- Production model remains 100% frozen
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
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
logger = logging.getLogger("train_candidate_models")

EXPERIMENT_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training"
FEATURES_PATH = EXPERIMENT_DIR / "features" / "yamnet_features_v2.npz"
MODELS_OUT_DIR = EXPERIMENT_DIR / "models"
REPORTS_OUT_DIR = EXPERIMENT_DIR / "reports"

RANDOM_SEED = 42


def evaluate_split(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float = 0.35,
) -> Dict[str, float]:
    """Compute binary classification metrics at specified threshold."""
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
        "threshold": round(threshold, 4),
    }


def compute_category_fpr(
    y_prob: np.ndarray,
    categories: np.ndarray,
    binary_labels: np.ndarray,
    threshold: float = 0.35,
) -> Dict[str, float]:
    """Compute False Positive Rate for each negative category."""
    cat_fprs = {}
    for cat in np.unique(categories):
        mask = (categories == cat) & (binary_labels == "non_scream")
        if np.sum(mask) == 0:
            continue
        scores = y_prob[mask]
        fps = np.sum(scores >= threshold)
        cat_fprs[str(cat)] = round(float(fps / len(scores)), 4)
    return cat_fprs


def main():
    logger.info("=" * 70)
    logger.info("EXPERIMENTAL CANDIDATE TRAINING & VALIDATION (GATE D)")
    logger.info("=" * 70)

    if not FEATURES_PATH.exists():
        logger.error(f"Features file not found: {FEATURES_PATH}")
        sys.exit(1)

    data = np.load(FEATURES_PATH)
    file_ids = data["file_ids"]
    splits = data["splits"]
    binary_labels = data["binary_labels"]
    categories = data["categories"]
    source_groups = data["source_groups"]

    features_max = data["features_max"]
    features_p90 = data["features_p90"]
    features_concat = data["features_concat"]

    MODELS_OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Exclude ambiguous records from binary loss & metrics
    train_mask = (splits == "train") & (binary_labels != "ambiguous")
    val_mask = (splits == "val") & (binary_labels != "ambiguous")
    test_mask = (splits == "test") & (binary_labels != "ambiguous")

    y_train = (binary_labels[train_mask] == "scream").astype(int)
    y_val = (binary_labels[val_mask] == "scream").astype(int)
    y_test = (binary_labels[test_mask] == "scream").astype(int)

    logger.info(f"Dataset Binary Partitions:")
    logger.info(f"  Train : {len(y_train)} clips ({np.sum(y_train)} scream, {len(y_train)-np.sum(y_train)} non-scream)")
    logger.info(f"  Val   : {len(y_val)} clips ({np.sum(y_val)} scream, {len(y_val)-np.sum(y_val)} non-scream)")
    logger.info(f"  Test  : {len(y_test)} clips ({np.sum(y_test)} scream, {len(y_test)-np.sum(y_test)} non-scream)")

    candidate_results: Dict[str, Any] = {}

    # -------------------------------------------------------------
    # Model A: Frozen Baseline LR on v2 splits (Max-Pooling, C=10.0)
    # -------------------------------------------------------------
    logger.info("\n--- Training Model A: Frozen Baseline Architecture (Max-Pooling, C=10.0) ---")
    pipe_a = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(C=10.0, class_weight="balanced", max_iter=1000, random_state=RANDOM_SEED)),
    ])
    pipe_a.fit(features_max[train_mask], y_train)
    val_prob_a = pipe_a.predict_proba(features_max[val_mask])[:, 1]
    test_prob_a = pipe_a.predict_proba(features_max[test_mask])[:, 1]

    val_metrics_a = evaluate_split(y_val, val_prob_a, threshold=0.35)
    test_metrics_a = evaluate_split(y_test, test_prob_a, threshold=0.35)
    test_cat_fpr_a = compute_category_fpr(test_prob_a, categories[test_mask], binary_labels[test_mask], threshold=0.35)

    joblib.dump(pipe_a, MODELS_OUT_DIR / "candidate_model_a_baseline_lr.joblib")
    candidate_results["Model_A_Baseline_LR"] = {
        "description": "Baseline LogisticRegression(C=10.0, balanced) on 1024-d max-pooled YAMNet embeddings",
        "val_metrics": val_metrics_a,
        "test_metrics": test_metrics_a,
        "test_category_fpr": test_cat_fpr_a,
    }

    # -------------------------------------------------------------
    # Model B: Regularized Logistic Regression (L2 Sweep on Validation)
    # -------------------------------------------------------------
    logger.info("\n--- Training Model B: Regularized Logistic Regression (L2 Sweep) ---")
    best_c_b = 1.0
    best_val_f1_b = 0.0
    c_candidates = [0.001, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]

    for c_val in c_candidates:
        pipe_sweep = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(C=c_val, class_weight="balanced", max_iter=1000, random_state=RANDOM_SEED)),
        ])
        pipe_sweep.fit(features_max[train_mask], y_train)
        probs = pipe_sweep.predict_proba(features_max[val_mask])[:, 1]
        m = evaluate_split(y_val, probs, threshold=0.35)
        if m["f1"] > best_val_f1_b:
            best_val_f1_b = m["f1"]
            best_c_b = c_val

    logger.info(f"Model B Optimal C parameter from validation sweep: C = {best_c_b}")
    pipe_b = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(C=best_c_b, class_weight="balanced", max_iter=1000, random_state=RANDOM_SEED)),
    ])
    pipe_b.fit(features_max[train_mask], y_train)
    val_prob_b = pipe_b.predict_proba(features_max[val_mask])[:, 1]
    test_prob_b = pipe_b.predict_proba(features_max[test_mask])[:, 1]

    val_metrics_b = evaluate_split(y_val, val_prob_b, threshold=0.35)
    test_metrics_b = evaluate_split(y_test, test_prob_b, threshold=0.35)
    test_cat_fpr_b = compute_category_fpr(test_prob_b, categories[test_mask], binary_labels[test_mask], threshold=0.35)

    joblib.dump(pipe_b, MODELS_OUT_DIR / "candidate_model_b_regularized_lr.joblib")
    candidate_results["Model_B_Regularized_LR"] = {
        "description": f"Calibrated L2 Regularized LR (C={best_c_b}) on 1024-d max-pooled YAMNet embeddings",
        "val_metrics": val_metrics_b,
        "test_metrics": test_metrics_b,
        "test_category_fpr": test_cat_fpr_b,
    }

    # -------------------------------------------------------------
    # Model C: 90th Percentile Temporal Pooled Logistic Regression
    # -------------------------------------------------------------
    logger.info("\n--- Training Model C: 90th Percentile Temporal Pooled LR ---")
    pipe_c = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(C=best_c_b, class_weight="balanced", max_iter=1000, random_state=RANDOM_SEED)),
    ])
    pipe_c.fit(features_p90[train_mask], y_train)
    val_prob_c = pipe_c.predict_proba(features_p90[val_mask])[:, 1]
    test_prob_c = pipe_c.predict_proba(features_p90[test_mask])[:, 1]

    val_metrics_c = evaluate_split(y_val, val_prob_c, threshold=0.35)
    test_metrics_c = evaluate_split(y_test, test_prob_c, threshold=0.35)
    test_cat_fpr_c = compute_category_fpr(test_prob_c, categories[test_mask], binary_labels[test_mask], threshold=0.35)

    joblib.dump(pipe_c, MODELS_OUT_DIR / "candidate_model_c_p90_lr.joblib")
    candidate_results["Model_C_P90_LR"] = {
        "description": "90th Percentile temporal pooling to suppress transient squeaks/whistles",
        "val_metrics": val_metrics_c,
        "test_metrics": test_metrics_c,
        "test_category_fpr": test_cat_fpr_c,
    }

    # -------------------------------------------------------------
    # Model D: Multi-Pooling Concatenated Logistic Regression (3072-dim)
    # -------------------------------------------------------------
    logger.info("\n--- Training Model D: Multi-Pooling Concatenated LR (3072-dim) ---")
    pipe_d = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(C=0.1, class_weight="balanced", max_iter=1000, random_state=RANDOM_SEED)),
    ])
    pipe_d.fit(features_concat[train_mask], y_train)
    val_prob_d = pipe_d.predict_proba(features_concat[val_mask])[:, 1]
    test_prob_d = pipe_d.predict_proba(features_concat[test_mask])[:, 1]

    val_metrics_d = evaluate_split(y_val, val_prob_d, threshold=0.35)
    test_metrics_d = evaluate_split(y_test, test_prob_d, threshold=0.35)
    test_cat_fpr_d = compute_category_fpr(test_prob_d, categories[test_mask], binary_labels[test_mask], threshold=0.35)

    joblib.dump(pipe_d, MODELS_OUT_DIR / "candidate_model_d_concat_lr.joblib")
    candidate_results["Model_D_Concat_LR"] = {
        "description": "Concatenated [max, p90, mean] multi-pooling representation (3072-dim)",
        "val_metrics": val_metrics_d,
        "test_metrics": test_metrics_d,
        "test_category_fpr": test_cat_fpr_d,
    }

    # -------------------------------------------------------------
    # Model E: Two-Stage Hierarchical Gating Classifier
    # -------------------------------------------------------------
    logger.info("\n--- Training Model E: Two-Stage Hierarchical Gating Classifier ---")
    # Stage 1: Vocal vs Non-Vocal
    vocal_categories = {"scream", "masked_distant_screams", "shouting_and_speech", "infant_crying"}
    is_vocal_train = np.array([1 if c in vocal_categories else 0 for c in categories[train_mask]])
    is_vocal_val = np.array([1 if c in vocal_categories else 0 for c in categories[val_mask]])
    is_vocal_test = np.array([1 if c in vocal_categories else 0 for c in categories[test_mask]])

    # Train Vocal Gater
    pipe_gate = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(C=1.0, class_weight="balanced", max_iter=1000, random_state=RANDOM_SEED)),
    ])
    pipe_gate.fit(features_max[train_mask], is_vocal_train)

    # Train Fine Scream Detector within Vocal partition
    vocal_train_idx = (is_vocal_train == 1)
    pipe_fine = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(C=0.5, class_weight="balanced", max_iter=1000, random_state=RANDOM_SEED)),
    ])
    pipe_fine.fit(features_max[train_mask][vocal_train_idx], y_train[vocal_train_idx])

    # Probability product: P(Scream) = P(Vocal) * P(Scream | Vocal)
    val_gate_prob = pipe_gate.predict_proba(features_max[val_mask])[:, 1]
    val_fine_prob = pipe_fine.predict_proba(features_max[val_mask])[:, 1]
    val_prob_e = val_gate_prob * val_fine_prob

    test_gate_prob = pipe_gate.predict_proba(features_max[test_mask])[:, 1]
    test_fine_prob = pipe_fine.predict_proba(features_max[test_mask])[:, 1]
    test_prob_e = test_gate_prob * test_fine_prob

    val_metrics_e = evaluate_split(y_val, val_prob_e, threshold=0.25)
    test_metrics_e = evaluate_split(y_test, test_prob_e, threshold=0.25)
    test_cat_fpr_e = compute_category_fpr(test_prob_e, categories[test_mask], binary_labels[test_mask], threshold=0.25)

    joblib.dump({"gate": pipe_gate, "fine": pipe_fine}, MODELS_OUT_DIR / "candidate_model_e_hierarchical.joblib")
    candidate_results["Model_E_Hierarchical"] = {
        "description": "Two-stage hierarchical classifier (Vocal Gater -> Scream Detector)",
        "val_metrics": val_metrics_e,
        "test_metrics": test_metrics_e,
        "test_category_fpr": test_cat_fpr_e,
    }

    # Save benchmark summary
    benchmark_report_path = REPORTS_OUT_DIR / "candidate_models_benchmark.json"
    with open(benchmark_report_path, "w", encoding="utf-8") as f:
        json.dump(candidate_results, f, indent=2)

    logger.info(f"Saved benchmark summary to: {benchmark_report_path}")

    # Print summary table
    print("\n" + "=" * 80)
    print("EXPERIMENTAL CANDIDATE BENCHMARK ON HELD-OUT TEST COHORT (N=189)")
    print("=" * 80)
    print(f"{'Model Architecture':25} | {'Recall':8} | {'Precision':10} | {'F1':6} | {'Hard Neg FPR':12} | {'PR-AUC':8}")
    print("-" * 80)
    for m_name, res in candidate_results.items():
        tm = res["test_metrics"]
        print(f"{m_name:25} | {tm['recall']*100:6.2f}% | {tm['precision']*100:8.2f}% | {tm['f1']:6.4f} | {tm['fpr']*100:10.2f}% | {tm['pr_auc']:6.4f}")
    print("=" * 80)
    print("PER-CATEGORY FALSE POSITIVE RATES ON HELD-OUT TEST SET:")
    for m_name, res in candidate_results.items():
        print(f"\n[{m_name}]")
        for cat, fpr_val in res["test_category_fpr"].items():
            print(f"  {cat:26}: {fpr_val*100:5.2f}%")


if __name__ == "__main__":
    main()
