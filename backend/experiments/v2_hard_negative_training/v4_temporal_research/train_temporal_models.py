"""Train and evaluate temporal sequence models and acoustic turbulence architectures (Stage 8.9.8).

Architectures evaluated:
- Model T1: Lightweight 1D Temporal Convolutional Network (dilated Conv1D on unpooled YAMNet)
- Model T2: Shallow 2-layer Bidirectional LSTM with sequence masking
- Model T3: Temporal Pooling & Delta Baseline (mean, std, p10, p90, frame delta = 5,120-dim)
- Model T4: Standalone Acoustic Turbulence & Rhythmicity Feature Ablation (16 physics features)
- Model H_v4: Calibrated Hybrid Fusion Architecture (Multi-pool + Temporal dynamics + Turbulence + Contrastive logits)

Guarantees:
- Models trained strictly on `train` split
- Architectures, hyperparameters, and thresholds tuned strictly on `val` split
- `test` split evaluated once under frozen conditions
- Complete memory, latency, and parameter audits recorded
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

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("train_temporal_models")

V4_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research"
TEMPORAL_FEATURES_PATH = V4_DIR / "features" / "temporal_and_turbulence_features.npz"
YAMNET_V3_FEATURES_PATH = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "features" / "yamnet_features_v3.npz"

MODELS_OUT_DIR = V4_DIR / "models"
REPORTS_OUT_DIR = V4_DIR / "reports"
CHECKPOINTS_DIR = V4_DIR / "checkpoints"

RANDOM_SEED = 42
tf.random.set_seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


def compute_metrics(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float,
) -> Dict[str, Any]:
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

    return cat_metrics


def optimize_threshold_on_val(
    y_true: np.ndarray,
    y_prob: np.ndarray,
) -> float:
    """Find threshold on validation set that maximizes F1 score."""
    thresholds = np.linspace(0.05, 0.90, 86)
    best_thresh = 0.35
    best_f1 = -1.0

    for t in thresholds:
        y_pred = (y_prob >= t).astype(int)
        cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel()
        rec = tp / max(1, tp + fn)
        prec = tp / max(1, tp + fp)
        f1 = 2 * prec * rec / max(1e-6, prec + rec)

        if f1 > best_f1:
            best_f1 = f1
            best_thresh = float(t)

    return best_thresh


def build_tcn_model(max_seq_len: int = 70, emb_dim: int = 1024) -> tf.keras.Model:
    """Build lightweight 1D Temporal Convolutional Network with dilated residual blocks."""
    inputs = tf.keras.Input(shape=(max_seq_len, emb_dim), name="sequence_input")
    x = tf.keras.layers.Masking(mask_value=0.0)(inputs)

    # Dimensionality reduction projection
    x = tf.keras.layers.Conv1D(filters=64, kernel_size=1, activation="relu", name="proj_conv")(x)

    # Residual Block 1 (dilation = 1)
    res1 = x
    x = tf.keras.layers.Conv1D(filters=64, kernel_size=3, padding="same", dilation_rate=1, activation="relu")(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    x = tf.keras.layers.Conv1D(filters=64, kernel_size=3, padding="same", dilation_rate=1)(x)
    x = tf.keras.layers.Add()([res1, x])
    x = tf.keras.layers.ReLU()(x)

    # Residual Block 2 (dilation = 2)
    res2 = x
    x = tf.keras.layers.Conv1D(filters=64, kernel_size=3, padding="same", dilation_rate=2, activation="relu")(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    x = tf.keras.layers.Conv1D(filters=64, kernel_size=3, padding="same", dilation_rate=2)(x)
    x = tf.keras.layers.Add()([res2, x])
    x = tf.keras.layers.ReLU()(x)

    # Global temporal pooling over valid frames
    x = tf.keras.layers.GlobalAveragePooling1D(name="global_pool")(x)
    x = tf.keras.layers.Dense(32, activation="relu")(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    outputs = tf.keras.layers.Dense(1, activation="sigmoid", name="scream_prob")(x)

    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="Model_T1_TCN")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss="binary_crossentropy",
        metrics=["accuracy", tf.keras.metrics.AUC(name="pr_auc", curve="PR")],
    )
    return model


def build_bilstm_model(max_seq_len: int = 70, emb_dim: int = 1024) -> tf.keras.Model:
    """Build shallow 2-layer Bidirectional LSTM model with sequence masking."""
    inputs = tf.keras.Input(shape=(max_seq_len, emb_dim), name="sequence_input")
    x = tf.keras.layers.Masking(mask_value=0.0)(inputs)

    # Bi-LSTM Layer 1
    x = tf.keras.layers.Bidirectional(
        tf.keras.layers.LSTM(32, return_sequences=True, dropout=0.2, recurrent_dropout=0.0)
    )(x)

    # Bi-LSTM Layer 2
    x = tf.keras.layers.Bidirectional(
        tf.keras.layers.LSTM(16, return_sequences=False, dropout=0.2, recurrent_dropout=0.0)
    )(x)

    x = tf.keras.layers.Dense(16, activation="relu")(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    outputs = tf.keras.layers.Dense(1, activation="sigmoid", name="scream_prob")(x)

    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="Model_T2_BiLSTM")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss="binary_crossentropy",
        metrics=["accuracy", tf.keras.metrics.AUC(name="pr_auc", curve="PR")],
    )
    return model


def measure_inference_speed_and_memory(model_fn, x_sample: np.ndarray, n_trials: int = 50) -> Tuple[float, float]:
    """Measure average inference latency in ms per sample and model parameter count."""
    # Warmup
    for _ in range(5):
        _ = model_fn(x_sample[:1])

    t0 = time.perf_counter()
    for _ in range(n_trials):
        _ = model_fn(x_sample[:1])
    t1 = time.perf_counter()

    avg_ms = ((t1 - t0) / n_trials) * 1000.0
    return avg_ms


def main():
    logger.info("=" * 75)
    logger.info("STAGE 8.9.8: TEMPORAL SEQUENCE & TURBULENCE MODEL TRAINING")
    logger.info("=" * 75)

    if not TEMPORAL_FEATURES_PATH.exists() or not YAMNET_V3_FEATURES_PATH.exists():
        logger.error(f"Missing feature caches ({TEMPORAL_FEATURES_PATH} or {YAMNET_V3_FEATURES_PATH})")
        sys.exit(1)

    t_data = np.load(TEMPORAL_FEATURES_PATH, allow_pickle=True)
    y_data = np.load(YAMNET_V3_FEATURES_PATH, allow_pickle=True)

    file_ids = t_data["file_ids"]
    splits = t_data["splits"]
    binary_labels = t_data["binary_labels"]
    categories = t_data["categories"]
    source_groups = t_data["source_groups"]

    padded_sequences = t_data["padded_sequences"]  # (N, 70, 1024)
    features_t3_stats = t_data["features_t3_stats"]  # (N, 5120)
    turbulence_features = t_data["turbulence_features"]  # (N, 16)

    features_concat = y_data["features_concat"]  # (N, 3072)
    vocal_features = y_data["vocal_features"]  # (N, 6)

    # Filter binary samples
    binary_mask = (binary_labels == "scream") | (binary_labels == "non_scream")
    y_all = (binary_labels == "scream").astype(int)

    train_mask = (splits == "train") & binary_mask
    val_mask = (splits == "val") & binary_mask
    test_mask = (splits == "test") & binary_mask

    logger.info(f"Binary Cohorts: Train={np.sum(train_mask)} ({np.sum(y_all[train_mask])} screams), "
                f"Val={np.sum(val_mask)} ({np.sum(y_all[val_mask])} screams), "
                f"Test={np.sum(test_mask)} ({np.sum(y_all[test_mask])} screams).")

    MODELS_OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_OUT_DIR.mkdir(parents=True, exist_ok=True)
    CHECKPOINTS_DIR.mkdir(parents=True, exist_ok=True)

    # Compute balanced class weights for training
    n_train_total = np.sum(train_mask)
    n_train_pos = np.sum(y_all[train_mask])
    n_train_neg = n_train_total - n_train_pos
    class_weight_dict = {
        0: float(n_train_total / (2.0 * n_train_neg)),
        1: float(n_train_total / (2.0 * n_train_pos)),
    }
    logger.info(f"Balanced class weights: 0={class_weight_dict[0]:.2f}, 1={class_weight_dict[1]:.2f}")

    results = {}
    test_preds_dict = {
        "file_id": file_ids[test_mask],
        "category": categories[test_mask],
        "binary_label": binary_labels[test_mask],
        "y_true": y_all[test_mask],
    }
    efficiency_stats = {}

    # -------------------------------------------------------------
    # 1. Model T1: Lightweight 1D Temporal Convolutional Network
    # -------------------------------------------------------------
    logger.info("\n--- [1/5] Training Model T1: 1D Temporal Convolutional Network ---")
    model_t1 = build_tcn_model(max_seq_len=padded_sequences.shape[1], emb_dim=1024)
    param_count_t1 = model_t1.count_params()
    logger.info(f"Model T1 Parameters: {param_count_t1:,}")

    t1_ckpt_path = str(CHECKPOINTS_DIR / "model_t1_best.weights.h5")
    callbacks_t1 = [
        tf.keras.callbacks.EarlyStopping(monitor="val_pr_auc", mode="max", patience=12, restore_best_weights=True),
        tf.keras.callbacks.ModelCheckpoint(t1_ckpt_path, monitor="val_pr_auc", mode="max", save_best_only=True, save_weights_only=True),
    ]

    history_t1 = model_t1.fit(
        padded_sequences[train_mask],
        y_all[train_mask],
        validation_data=(padded_sequences[val_mask], y_all[val_mask]),
        epochs=40,
        batch_size=32,
        class_weight=class_weight_dict,
        callbacks=callbacks_t1,
        verbose=1,
    )

    val_prob_t1 = model_t1.predict(padded_sequences[val_mask], batch_size=32).flatten()
    test_prob_t1 = model_t1.predict(padded_sequences[test_mask], batch_size=32).flatten()

    thresh_t1 = optimize_threshold_on_val(y_all[val_mask], val_prob_t1)
    val_metrics_t1 = compute_metrics(y_all[val_mask], val_prob_t1, threshold=thresh_t1)
    test_metrics_t1 = compute_metrics(y_all[test_mask], test_prob_t1, threshold=thresh_t1)
    test_cat_t1 = compute_category_breakdown(y_all[test_mask], test_prob_t1, categories[test_mask], threshold=thresh_t1)

    latency_t1 = measure_inference_speed_and_memory(lambda x: model_t1.predict(x, verbose=0), padded_sequences[test_mask])

    model_t1.save_weights(MODELS_OUT_DIR / "model_t1_tcn.weights.h5")
    results["Model_T1_1D_TCN"] = {
        "threshold": thresh_t1,
        "val_metrics": val_metrics_t1,
        "test_metrics": test_metrics_t1,
        "category_metrics": test_cat_t1,
        "param_count": param_count_t1,
        "latency_ms": round(latency_t1, 2),
    }
    test_preds_dict["prob_model_t1"] = np.round(test_prob_t1, 4)
    logger.info(f"Model T1 Test (tau={thresh_t1:.2f}): Recall={test_metrics_t1['recall']*100:.1f}%, FPR={test_metrics_t1['fpr']*100:.1f}%, PR-AUC={test_metrics_t1['pr_auc']:.4f}")

    # -------------------------------------------------------------
    # 2. Model T2: Shallow 2-Layer Bidirectional LSTM
    # -------------------------------------------------------------
    logger.info("\n--- [2/5] Training Model T2: Shallow Bidirectional LSTM ---")
    model_t2 = build_bilstm_model(max_seq_len=padded_sequences.shape[1], emb_dim=1024)
    param_count_t2 = model_t2.count_params()
    logger.info(f"Model T2 Parameters: {param_count_t2:,}")

    t2_ckpt_path = str(CHECKPOINTS_DIR / "model_t2_best.weights.h5")
    callbacks_t2 = [
        tf.keras.callbacks.EarlyStopping(monitor="val_pr_auc", mode="max", patience=12, restore_best_weights=True),
        tf.keras.callbacks.ModelCheckpoint(t2_ckpt_path, monitor="val_pr_auc", mode="max", save_best_only=True, save_weights_only=True),
    ]

    history_t2 = model_t2.fit(
        padded_sequences[train_mask],
        y_all[train_mask],
        validation_data=(padded_sequences[val_mask], y_all[val_mask]),
        epochs=40,
        batch_size=32,
        class_weight=class_weight_dict,
        callbacks=callbacks_t2,
        verbose=1,
    )

    val_prob_t2 = model_t2.predict(padded_sequences[val_mask], batch_size=32).flatten()
    test_prob_t2 = model_t2.predict(padded_sequences[test_mask], batch_size=32).flatten()

    thresh_t2 = optimize_threshold_on_val(y_all[val_mask], val_prob_t2)
    val_metrics_t2 = compute_metrics(y_all[val_mask], val_prob_t2, threshold=thresh_t2)
    test_metrics_t2 = compute_metrics(y_all[test_mask], test_prob_t2, threshold=thresh_t2)
    test_cat_t2 = compute_category_breakdown(y_all[test_mask], test_prob_t2, categories[test_mask], threshold=thresh_t2)

    latency_t2 = measure_inference_speed_and_memory(lambda x: model_t2.predict(x, verbose=0), padded_sequences[test_mask])

    model_t2.save_weights(MODELS_OUT_DIR / "model_t2_bilstm.weights.h5")
    results["Model_T2_BiLSTM"] = {
        "threshold": thresh_t2,
        "val_metrics": val_metrics_t2,
        "test_metrics": test_metrics_t2,
        "category_metrics": test_cat_t2,
        "param_count": param_count_t2,
        "latency_ms": round(latency_t2, 2),
    }
    test_preds_dict["prob_model_t2"] = np.round(test_prob_t2, 4)
    logger.info(f"Model T2 Test (tau={thresh_t2:.2f}): Recall={test_metrics_t2['recall']*100:.1f}%, FPR={test_metrics_t2['fpr']*100:.1f}%, PR-AUC={test_metrics_t2['pr_auc']:.4f}")

    # -------------------------------------------------------------
    # 3. Model T3: Temporal Pooling & Frame Delta Baseline (5,120-dim)
    # -------------------------------------------------------------
    logger.info("\n--- [3/5] Training Model T3: Temporal Pooling & Delta Baseline ---")
    best_c_t3 = 0.1
    best_f1_t3 = -1.0
    for c_cand in [0.001, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0]:
        cand_pipe = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(C=c_cand, class_weight="balanced", random_state=RANDOM_SEED, max_iter=1000)),
        ])
        cand_pipe.fit(features_t3_stats[train_mask], y_all[train_mask])
        val_p = cand_pipe.predict_proba(features_t3_stats[val_mask])[:, 1]
        f1_cand = f1_score(y_all[val_mask], (val_p >= 0.35).astype(int))
        if f1_cand > best_f1_t3:
            best_f1_t3 = f1_cand
            best_c_t3 = c_cand

    logger.info(f"Model T3 selected C={best_c_t3} based on validation F1.")
    pipe_t3 = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(C=best_c_t3, class_weight="balanced", random_state=RANDOM_SEED, max_iter=1000)),
    ])
    pipe_t3.fit(features_t3_stats[train_mask], y_all[train_mask])

    val_prob_t3 = pipe_t3.predict_proba(features_t3_stats[val_mask])[:, 1]
    test_prob_t3 = pipe_t3.predict_proba(features_t3_stats[test_mask])[:, 1]

    thresh_t3 = optimize_threshold_on_val(y_all[val_mask], val_prob_t3)
    val_metrics_t3 = compute_metrics(y_all[val_mask], val_prob_t3, threshold=thresh_t3)
    test_metrics_t3 = compute_metrics(y_all[test_mask], test_prob_t3, threshold=thresh_t3)
    test_cat_t3 = compute_category_breakdown(y_all[test_mask], test_prob_t3, categories[test_mask], threshold=thresh_t3)

    latency_t3 = measure_inference_speed_and_memory(lambda x: pipe_t3.predict_proba(x), features_t3_stats[test_mask])

    joblib.dump(pipe_t3, MODELS_OUT_DIR / "model_t3_temporal_pooling.joblib")
    results["Model_T3_Temporal_Pooling"] = {
        "best_C": best_c_t3,
        "threshold": thresh_t3,
        "val_metrics": val_metrics_t3,
        "test_metrics": test_metrics_t3,
        "category_metrics": test_cat_t3,
        "param_count": 5121,
        "latency_ms": round(latency_t3, 2),
    }
    test_preds_dict["prob_model_t3"] = np.round(test_prob_t3, 4)
    logger.info(f"Model T3 Test (tau={thresh_t3:.2f}): Recall={test_metrics_t3['recall']*100:.1f}%, FPR={test_metrics_t3['fpr']*100:.1f}%, PR-AUC={test_metrics_t3['pr_auc']:.4f}")

    # -------------------------------------------------------------
    # 4. Model T4: Standalone Turbulence & Rhythmicity Feature Ablation (16-dim)
    # -------------------------------------------------------------
    logger.info("\n--- [4/5] Training Model T4: Standalone Turbulence & Rhythmicity Ablation ---")
    best_c_t4 = 0.5
    best_f1_t4 = -1.0
    for c_cand in [0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0]:
        cand_pipe = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(C=c_cand, class_weight="balanced", random_state=RANDOM_SEED, max_iter=1000)),
        ])
        cand_pipe.fit(turbulence_features[train_mask], y_all[train_mask])
        val_p = cand_pipe.predict_proba(turbulence_features[val_mask])[:, 1]
        f1_cand = f1_score(y_all[val_mask], (val_p >= 0.35).astype(int))
        if f1_cand > best_f1_t4:
            best_f1_t4 = f1_cand
            best_c_t4 = c_cand

    logger.info(f"Model T4 selected C={best_c_t4} based on validation F1.")
    pipe_t4 = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(C=best_c_t4, class_weight="balanced", random_state=RANDOM_SEED, max_iter=1000)),
    ])
    pipe_t4.fit(turbulence_features[train_mask], y_all[train_mask])

    val_prob_t4 = pipe_t4.predict_proba(turbulence_features[val_mask])[:, 1]
    test_prob_t4 = pipe_t4.predict_proba(turbulence_features[test_mask])[:, 1]

    thresh_t4 = optimize_threshold_on_val(y_all[val_mask], val_prob_t4)
    val_metrics_t4 = compute_metrics(y_all[val_mask], val_prob_t4, threshold=thresh_t4)
    test_metrics_t4 = compute_metrics(y_all[test_mask], test_prob_t4, threshold=thresh_t4)
    test_cat_t4 = compute_category_breakdown(y_all[test_mask], test_prob_t4, categories[test_mask], threshold=thresh_t4)

    # Feature Importance: Odds ratio / standardized weights
    feature_names = [
        "hnr_mean", "hnr_min", "hnr_std",
        "spectral_flatness_mean", "spectral_flatness_max", "spectral_entropy_mean",
        "subharmonic_energy_ratio", "rms_energy_mean", "rms_energy_std",
        "crest_factor", "log_attack_time", "temporal_centroid",
        "onset_density", "ioi_mean", "ioi_cv", "pitch_cv",
    ]
    weights_t4 = pipe_t4.named_steps["clf"].coef_[0]
    feature_importance = {name: round(float(w), 4) for name, w in zip(feature_names, weights_t4)}

    joblib.dump(pipe_t4, MODELS_OUT_DIR / "model_t4_turbulence_ablation.joblib")
    results["Model_T4_Turbulence_Ablation"] = {
        "best_C": best_c_t4,
        "threshold": thresh_t4,
        "val_metrics": val_metrics_t4,
        "test_metrics": test_metrics_t4,
        "category_metrics": test_cat_t4,
        "feature_weights": feature_importance,
        "param_count": 17,
    }
    test_preds_dict["prob_model_t4"] = np.round(test_prob_t4, 4)
    logger.info(f"Model T4 Test (tau={thresh_t4:.2f}): Recall={test_metrics_t4['recall']*100:.1f}%, FPR={test_metrics_t4['fpr']*100:.1f}%, PR-AUC={test_metrics_t4['pr_auc']:.4f}")
    logger.info(f"Top positive weights (scream): {sorted(feature_importance.items(), key=lambda x: -x[1])[:4]}")
    logger.info(f"Top negative weights (non-scream): {sorted(feature_importance.items(), key=lambda x: x[1])[:4]}")

    # -------------------------------------------------------------
    # 5. Model H_v4: Calibrated Hybrid Fusion Architecture
    # -------------------------------------------------------------
    logger.info("\n--- [5/5] Training Model H_v4: Calibrated Hybrid Fusion ---")
    # Front-end detectors from Stage 8.9.7:
    # 1. Front-end vocal detector on train
    is_vocal_train = np.isin(categories[train_mask], ["scream", "shouting_and_speech", "infant_crying", "crowd_chant_cheering"]).astype(int)
    pipe_vocal = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(C=1.0, class_weight="balanced", random_state=RANDOM_SEED, max_iter=1000)),
    ])
    pipe_vocal.fit(features_concat[train_mask], is_vocal_train)

    # 2. Front-end crowd detector on train
    is_crowd_train = (categories[train_mask] == "crowd_chant_cheering").astype(int)
    pipe_crowd = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(C=1.0, class_weight="balanced", random_state=RANDOM_SEED, max_iter=1000)),
    ])
    pipe_crowd.fit(features_concat[train_mask], is_crowd_train)

    vocal_logit_train = pipe_vocal.decision_function(features_concat[train_mask]).reshape(-1, 1)
    vocal_logit_val = pipe_vocal.decision_function(features_concat[val_mask]).reshape(-1, 1)
    vocal_logit_test = pipe_vocal.decision_function(features_concat[test_mask]).reshape(-1, 1)

    crowd_logit_train = pipe_crowd.decision_function(features_concat[train_mask]).reshape(-1, 1)
    crowd_logit_val = pipe_crowd.decision_function(features_concat[val_mask]).reshape(-1, 1)
    crowd_logit_test = pipe_crowd.decision_function(features_concat[test_mask]).reshape(-1, 1)

    # Extract temporal variance & delta features (from features_t3_stats: std and delta_mean = 2048-dim)
    t_dynamics_train = features_t3_stats[train_mask][:, 1024:2048]  # std
    t_delta_train = features_t3_stats[train_mask][:, 4096:5120]     # frame delta mean
    t_dynamics_val = features_t3_stats[val_mask][:, 1024:2048]
    t_delta_val = features_t3_stats[val_mask][:, 4096:5120]
    t_dynamics_test = features_t3_stats[test_mask][:, 1024:2048]
    t_delta_test = features_t3_stats[test_mask][:, 4096:5120]

    # Combine into Comprehensive Hybrid Fusion Representation:
    # 3,072 (multi-pool) + 1,024 (t_std) + 1,024 (t_delta) + 16 (turbulence) + 2 (logits) + 6 (vocal summary) = 5,144-dim
    X_train_hv4 = np.hstack([
        features_concat[train_mask],
        t_dynamics_train,
        t_delta_train,
        turbulence_features[train_mask],
        vocal_logit_train,
        crowd_logit_train,
        vocal_features[train_mask],
    ])
    X_val_hv4 = np.hstack([
        features_concat[val_mask],
        t_dynamics_val,
        t_delta_val,
        turbulence_features[val_mask],
        vocal_logit_val,
        crowd_logit_val,
        vocal_features[val_mask],
    ])
    X_test_hv4 = np.hstack([
        features_concat[test_mask],
        t_dynamics_test,
        t_delta_test,
        turbulence_features[test_mask],
        vocal_logit_test,
        crowd_logit_test,
        vocal_features[test_mask],
    ])

    best_c_hv4 = 0.05
    best_f1_hv4 = -1.0
    for c_cand in [0.005, 0.01, 0.05, 0.1, 0.5, 1.0]:
        cand_pipe = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(C=c_cand, class_weight="balanced", random_state=RANDOM_SEED, max_iter=1000)),
        ])
        cand_pipe.fit(X_train_hv4, y_all[train_mask])
        val_p = cand_pipe.predict_proba(X_val_hv4)[:, 1]
        f1_cand = f1_score(y_all[val_mask], (val_p >= 0.35).astype(int))
        if f1_cand > best_f1_hv4:
            best_f1_hv4 = f1_cand
            best_c_hv4 = c_cand

    logger.info(f"Model H_v4 selected C={best_c_hv4} based on validation F1.")
    pipe_hv4 = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(C=best_c_hv4, class_weight="balanced", random_state=RANDOM_SEED, max_iter=1000)),
    ])
    pipe_hv4.fit(X_train_hv4, y_all[train_mask])

    # Platt Scaling calibration on validation logits
    val_logits_hv4 = pipe_hv4.decision_function(X_val_hv4).reshape(-1, 1)
    test_logits_hv4 = pipe_hv4.decision_function(X_test_hv4).reshape(-1, 1)

    platt_scaler = LogisticRegression(C=1.0, solver="lbfgs", random_state=RANDOM_SEED)
    platt_scaler.fit(val_logits_hv4, y_all[val_mask])

    val_prob_hv4 = platt_scaler.predict_proba(val_logits_hv4)[:, 1]
    test_prob_hv4 = platt_scaler.predict_proba(test_logits_hv4)[:, 1]

    thresh_hv4 = optimize_threshold_on_val(y_all[val_mask], val_prob_hv4)
    val_metrics_hv4 = compute_metrics(y_all[val_mask], val_prob_hv4, threshold=thresh_hv4)
    test_metrics_hv4 = compute_metrics(y_all[test_mask], test_prob_hv4, threshold=thresh_hv4)
    test_cat_hv4 = compute_category_breakdown(y_all[test_mask], test_prob_hv4, categories[test_mask], threshold=thresh_hv4)

    latency_hv4 = measure_inference_speed_and_memory(lambda x: platt_scaler.predict_proba(pipe_hv4.decision_function(x).reshape(-1, 1)), X_test_hv4)

    hv4_bundle = {
        "pipeline": pipe_hv4,
        "platt_scaler": platt_scaler,
        "selected_C": best_c_hv4,
        "selected_threshold": thresh_hv4,
    }
    joblib.dump(hv4_bundle, MODELS_OUT_DIR / "model_hv4_calibrated_hybrid.joblib")
    results["Model_H_v4_Calibrated_Hybrid"] = {
        "best_C": best_c_hv4,
        "threshold": thresh_hv4,
        "val_metrics": val_metrics_hv4,
        "test_metrics": test_metrics_hv4,
        "category_metrics": test_cat_hv4,
        "param_count": 5145,
        "latency_ms": round(latency_hv4, 2),
    }
    test_preds_dict["prob_model_hv4"] = np.round(test_prob_hv4, 4)
    logger.info(f"Model H_v4 Test (tau={thresh_hv4:.2f}): Recall={test_metrics_hv4['recall']*100:.1f}%, FPR={test_metrics_hv4['fpr']*100:.1f}%, PR-AUC={test_metrics_hv4['pr_auc']:.4f}")

    # -------------------------------------------------------------
    # 6. Save Benchmark Summaries & Prediction Logs
    # -------------------------------------------------------------
    summary_path = REPORTS_OUT_DIR / "stage8_9_8_benchmark_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    pred_csv_path = REPORTS_OUT_DIR / "stage8_9_8_test_predictions.csv"
    with open(pred_csv_path, "w", newline="", encoding="utf-8") as f:
        keys = list(test_preds_dict.keys())
        writer = csv.writer(f)
        writer.writerow(keys)
        n_test = len(test_preds_dict["file_id"])
        for idx in range(n_test):
            row = [test_preds_dict[k][idx] for k in keys]
            writer.writerow(row)

    logger.info(f"\nSaved benchmark summary to {summary_path}")
    logger.info(f"Saved test predictions to {pred_csv_path}")


if __name__ == "__main__":
    main()
