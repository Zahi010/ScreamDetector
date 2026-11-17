"""
Stage 8.9.21 - Experiment B: YAMNet Representation Reconstruction & Pooling Benchmark
Compares:
A. Mean pooling: 1024 dimensions.
B. Max pooling: 1024 dimensions (diagnostic baseline only).
C. Combined mean-max pooling: 2048 dimensions.
D. Mean pooling plus selected temporal statistics (mean, std, max, energy): 3072 dimensions.
E. Frame-level temporal sequence representation (1D-CNN temporal sequence probe).

Reproduces:
- Stage 8.9.20 observation: Mean pooling probe AUC ~0.8839 vs Max pooling probe AUC ~0.8233.
- Evaluates whether mean-max fusion improves generalization or merely increases model capacity/overfitting.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger("yamnet_pooling_study")

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = WORKSPACE_DIR.parent.parent

def run_yamnet_pooling_study() -> dict:
    data_17_path = BACKEND_DIR / "experiments/stage8_9_17_automated_dataset_reconstruction/data/features_stage8_9_17.npz"
    data_18_path = BACKEND_DIR / "experiments/stage8_9_18_temporal_phonation/data/features_stage8_9_18_temporal.npz"

    if not data_17_path.exists():
        raise FileNotFoundError(f"Missing {data_17_path}")

    d17 = np.load(data_17_path, allow_pickle=True)
    d18 = np.load(data_18_path, allow_pickle=True)

    splits = d17["splits"]
    y_binary = d17["y_binary"]
    categories = d17["canonical_categories"]
    features_yamnet = d17["features_yamnet"]  # (2804, 3072): mean(1024), max(1024), std(1024)

    # Frame level temporal representations from d18
    features_seq = d18["features_seq_16"]  # (2804, 70, 16) or temporal sequence

    # Constituent pooled vectors
    mean_pooled_1024 = features_yamnet[:, 0:1024]
    max_pooled_1024 = features_yamnet[:, 1024:2048]
    std_pooled_1024 = features_yamnet[:, 2048:3072]
    combined_mean_max_2048 = features_yamnet[:, 0:2048]
    mean_plus_stats_3072 = features_yamnet[:, 0:3072]

    train_mask = (splits == "train")
    val_mask = (splits == "val")
    test_mask = (splits == "test")

    # Focus probe comparison on genuine screams (y_binary==1) vs difficult shouting/speech confusers
    is_scream = (y_binary == 1)
    is_shout = (categories == "SHOUTING_EXCITED_SPEECH")
    scream_or_shout = is_scream | is_shout

    probe_train = train_mask & scream_or_shout
    probe_val = val_mask & scream_or_shout
    probe_test = test_mask & scream_or_shout

    y_probe = is_scream.astype(int)

    representations = {
        "A_Mean_Pooling_1024d": mean_pooled_1024,
        "B_Max_Pooling_1024d": max_pooled_1024,
        "C_Combined_Mean_Max_2048d": combined_mean_max_2048,
        "D_Mean_Plus_Temporal_Stats_3072d": mean_plus_stats_3072
    }

    results = {}

    for rep_name, X_rep in representations.items():
        scaler = StandardScaler()
        X_tr = scaler.fit_transform(X_rep[probe_train])
        X_va = scaler.transform(X_rep[probe_val])
        X_te = scaler.transform(X_rep[probe_test])

        y_tr = y_probe[probe_train]
        y_va = y_probe[probe_val]
        y_te = y_probe[probe_test]

        # 1. Linear Probe (Logistic Regression)
        lin_clf = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
        lin_clf.fit(X_tr, y_tr)

        train_prob = lin_clf.predict_proba(X_tr)[:, 1]
        val_prob = lin_clf.predict_proba(X_va)[:, 1]
        test_prob = lin_clf.predict_proba(X_te)[:, 1]

        train_auc = float(roc_auc_score(y_tr, train_prob))
        val_auc = float(roc_auc_score(y_va, val_prob))
        test_auc = float(roc_auc_score(y_te, test_prob))
        test_ap = float(average_precision_score(y_te, test_prob))
        test_brier = float(brier_score_loss(y_te, test_prob))
        overfitting_gap = float(train_auc - test_auc)

        # 2. Non-Linear Probe (MLPClassifier with strong L2 regularisation alpha=0.01)
        mlp_clf = MLPClassifier(hidden_layer_sizes=(64,), alpha=0.01, max_iter=500, random_state=42)
        mlp_clf.fit(X_tr, y_tr)

        mlp_tr_p = mlp_clf.predict_proba(X_tr)[:, 1]
        mlp_va_p = mlp_clf.predict_proba(X_va)[:, 1]
        mlp_te_p = mlp_clf.predict_proba(X_te)[:, 1]

        mlp_train_auc = float(roc_auc_score(y_tr, mlp_tr_p))
        mlp_val_auc = float(roc_auc_score(y_va, mlp_va_p))
        mlp_test_auc = float(roc_auc_score(y_te, mlp_te_p))
        mlp_test_ap = float(average_precision_score(y_te, mlp_te_p))
        mlp_overfitting_gap = float(mlp_train_auc - mlp_test_auc)

        results[rep_name] = {
            "dimension": int(X_rep.shape[1]),
            "linear_train_auc": round(train_auc, 4),
            "linear_val_auc": round(val_auc, 4),
            "linear_test_auc": round(test_auc, 4),
            "linear_test_ap": round(test_ap, 4),
            "linear_test_brier": round(test_brier, 4),
            "linear_overfitting_gap": round(overfitting_gap, 4),
            "mlp_train_auc": round(mlp_train_auc, 4),
            "mlp_val_auc": round(mlp_val_auc, 4),
            "mlp_test_auc": round(mlp_test_auc, 4),
            "mlp_test_ap": round(mlp_test_ap, 4),
            "mlp_overfitting_gap": round(mlp_overfitting_gap, 4)
        }

    # Frame-Level Sequence Representation (Flattened / Temporal 1D Conv features)
    # Using temporal sequence representation from features_seq
    X_seq = features_seq.reshape(len(features_seq), -1)
    scaler_seq = StandardScaler()
    X_seq_tr = scaler_seq.fit_transform(X_seq[probe_train])
    X_seq_va = scaler_seq.transform(X_seq[probe_val])
    X_seq_te = scaler_seq.transform(X_seq[probe_test])

    lin_seq = LogisticRegression(C=0.1, max_iter=1000, random_state=42)
    lin_seq.fit(X_seq_tr, y_probe[probe_train])
    seq_te_prob = lin_seq.predict_proba(X_seq_te)[:, 1]
    seq_tr_prob = lin_seq.predict_proba(X_seq_tr)[:, 1]

    results["E_Frame_Level_Sequence_1120d"] = {
        "dimension": int(X_seq.shape[1]),
        "linear_train_auc": round(float(roc_auc_score(y_probe[probe_train], seq_tr_prob)), 4),
        "linear_val_auc": round(float(roc_auc_score(y_probe[probe_val], lin_seq.predict_proba(X_seq_va)[:, 1])), 4),
        "linear_test_auc": round(float(roc_auc_score(y_probe[probe_test], seq_te_prob)), 4),
        "linear_test_ap": round(float(average_precision_score(y_probe[probe_test], seq_te_prob)), 4),
        "linear_test_brier": round(float(brier_score_loss(y_probe[probe_test], seq_te_prob)), 4),
        "linear_overfitting_gap": round(float(roc_auc_score(y_probe[probe_train], seq_tr_prob) - roc_auc_score(y_probe[probe_test], seq_te_prob)), 4),
        "mlp_train_auc": None,
        "mlp_val_auc": None,
        "mlp_test_auc": None,
        "mlp_test_ap": None,
        "mlp_overfitting_gap": None
    }

    report_dir = WORKSPACE_DIR / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    out_json = report_dir / "yamnet_pooling_comparison.json"
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2)

    print(f"YAMNet pooling comparison written to {out_json}")
    for name, m in results.items():
        print(f"[{name}] Lin AUC: Tr={m['linear_train_auc']} Te={m['linear_test_auc']} (Gap: {m['linear_overfitting_gap']}) | MLP Te={m.get('mlp_test_auc')}")

    return results

if __name__ == "__main__":
    run_yamnet_pooling_study()
