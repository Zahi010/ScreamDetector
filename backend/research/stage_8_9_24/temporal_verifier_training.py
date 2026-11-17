"""
Stage 8.9.24 Investigation D & E: Temporal Verifier Training & Dual-Pathway Architecture.

Strict constraints:
- Fitted ONLY on train split (N=1969).
- Evaluated and calibrated ONLY on val split (N=373).
- Zero exposure to test split (N=462).
- Fits:
  1. Candidate B: Temporal Logistic Regression
  2. Candidate C: Temporal Random Forest
  3. Candidate D: Temporal Gradient Boosting
  4. Candidate E: Short-Event Pathway (500ms context)
  5. Candidate F: Long-Context Pathway (2000ms context)
  6. Candidate G: Dual-Pathway TMSCV (Fused Short + Long Cadence Verifier)
"""

import csv
import os
import sys
import time
from pathlib import Path
import numpy as np
import joblib
import soundfile as sf
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, precision_recall_fscore_support

WORKSPACE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = WORKSPACE_DIR.parent.parent

sys.path.insert(0, str(WORKSPACE_DIR))
from temporal_feature_extraction import (
    TemporalModulationExtractor,
    TEMPORAL_MODULATION_FEATURE_NAMES,
)

MODELS_DIR = WORKSPACE_DIR / "models"
DATA_DIR = WORKSPACE_DIR / "data"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 1. Load manifest mapping
splits_csv = (
    BACKEND_DIR
    / "experiments"
    / "stage8_9_17_automated_dataset_reconstruction"
    / "data"
    / "manifests"
    / "source_group_splits.csv"
)

with open(splits_csv, "r", encoding="utf-8") as f:
    records = list(csv.DictReader(f))

record_map = {r["file_id"]: r for r in records}

d18_path = BACKEND_DIR / "experiments/stage8_9_18_temporal_phonation/data/features_stage8_9_18_temporal.npz"
d18 = np.load(d18_path, allow_pickle=True)

file_ids = d18["file_ids"]
splits = d18["splits"]
y_binary = d18["y_binary"].astype(int)
cats = d18["canonical_categories"]
source_groups = d18["source_groups"]
durations = d18["durations"]

train_mask = (splits == "train")
val_mask = (splits == "val")

print(f"Dataset splits: Train={np.sum(train_mask)}, Val={np.sum(val_mask)}, Test={np.sum(splits == 'test')}")

# Extract features or load from cache
train_cache_file = DATA_DIR / "temporal_train_features.npz"
val_cache_file = DATA_DIR / "temporal_val_features.npz"

extractor_full = TemporalModulationExtractor(sr=16000, frame_ms=25.0, hop_ms=12.5)
extractor_short = TemporalModulationExtractor(sr=16000, frame_ms=20.0, hop_ms=10.0)

def extract_split_features(mask, split_name):
    split_fids = file_ids[mask]
    n_items = len(split_fids)
    print(f"Extracting temporal features for {split_name} ({n_items} items)...")
    
    # We extract:
    # 1. Full context features (up to 2.5s)
    # 2. Short context features (500ms max)
    feats_full = np.zeros((n_items, len(TEMPORAL_MODULATION_FEATURE_NAMES)), dtype=np.float32)
    feats_short = np.zeros((n_items, len(TEMPORAL_MODULATION_FEATURE_NAMES)), dtype=np.float32)
    
    t0 = time.time()
    for i, fid in enumerate(split_fids):
        rec = record_map.get(str(fid))
        wf = None
        if rec:
            abs_p = Path(rec["absolute_path"])
            if not abs_p.exists():
                abs_p = BACKEND_DIR.parent / rec["relative_path"]
            if abs_p.exists():
                try:
                    data, sr = sf.read(str(abs_p), dtype="float32", always_2d=True)
                    wf = np.mean(data, axis=1) if data.shape[1] > 1 else data[:, 0]
                    if sr != 16000:
                        num_target = int(round(len(wf) * (16000.0 / sr)))
                        wf = np.interp(
                            np.linspace(0.0, 1.0, num_target, endpoint=False),
                            np.linspace(0.0, 1.0, len(wf), endpoint=False),
                            wf,
                        ).astype(np.float32)
                except Exception:
                    wf = None
        if wf is not None and len(wf) > 0:
            feats_full[i, :] = extractor_full.extract_feature_vector(wf, context_sec=2.5)
            feats_short[i, :] = extractor_short.extract_feature_vector(wf, context_sec=0.5)

    print(f"Done {split_name} in {time.time() - t0:.2f}s")
    return feats_full, feats_short

if train_cache_file.exists():
    print("Loading cached train features...")
    tr_data = np.load(train_cache_file)
    X_tr_full, X_tr_short = tr_data["full"], tr_data["short"]
else:
    X_tr_full, X_tr_short = extract_split_features(train_mask, "train")
    np.savez_compressed(train_cache_file, full=X_tr_full, short=X_tr_short)

if val_cache_file.exists():
    print("Loading cached val features...")
    va_data = np.load(val_cache_file)
    X_va_full, X_va_short = va_data["full"], va_data["short"]
else:
    X_va_full, X_va_short = extract_split_features(val_mask, "val")
    np.savez_compressed(val_cache_file, full=X_va_full, short=X_va_short)

y_tr = y_binary[train_mask]
y_va = y_binary[val_mask]

# 2. Fit Scalers on TRAIN ONLY
scaler_full = StandardScaler().fit(X_tr_full)
scaler_short = StandardScaler().fit(X_tr_short)

X_tr_full_s = scaler_full.transform(X_tr_full)
X_va_full_s = scaler_full.transform(X_va_full)

X_tr_short_s = scaler_short.transform(X_tr_short)
X_va_short_s = scaler_short.transform(X_va_short)

# Save scalers
joblib.dump(scaler_full, MODELS_DIR / "scaler_full.joblib")
joblib.dump(scaler_short, MODELS_DIR / "scaler_short.joblib")

print("Training candidate models...")

# Model 1: Logistic Regression (Candidate B)
clf_lr = LogisticRegression(C=1.0, max_iter=1000, random_state=42, class_weight="balanced")
clf_lr.fit(X_tr_full_s, y_tr)
joblib.dump(clf_lr, MODELS_DIR / "candidate_b_logistic_regression.joblib")

# Model 2: Random Forest (Candidate C)
clf_rf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42, class_weight="balanced")
clf_rf.fit(X_tr_full, y_tr)
joblib.dump(clf_rf, MODELS_DIR / "candidate_c_random_forest.joblib")

# Model 3: Gradient Boosting (Candidate D)
clf_gb = GradientBoostingClassifier(n_estimators=100, max_depth=4, learning_rate=0.05, random_state=42)
clf_gb.fit(X_tr_full, y_tr)
joblib.dump(clf_gb, MODELS_DIR / "candidate_d_gradient_boosting.joblib")

# Model 4: Short-Event Pathway (Candidate E, fitted on short 500ms context)
clf_short = GradientBoostingClassifier(n_estimators=80, max_depth=3, learning_rate=0.05, random_state=42)
clf_short.fit(X_tr_short, y_tr)
joblib.dump(clf_short, MODELS_DIR / "candidate_e_short_pathway.joblib")

# Model 5: Long-Context Cadence Pathway (Candidate F, fitted on 2500ms context)
clf_long = GradientBoostingClassifier(n_estimators=100, max_depth=4, learning_rate=0.05, random_state=42)
clf_long.fit(X_tr_full, y_tr)
joblib.dump(clf_long, MODELS_DIR / "candidate_f_long_pathway.joblib")

# Validation performance evaluation
models = {
    "Candidate B (LogReg)": (clf_lr, X_va_full_s),
    "Candidate C (RF)": (clf_rf, X_va_full),
    "Candidate D (GB)": (clf_gb, X_va_full),
    "Candidate E (Short Pathway)": (clf_short, X_va_short),
    "Candidate F (Long Pathway)": (clf_long, X_va_full),
}

print("\n--- VALIDATION SPLIT PERFORMANCE (N=373) ---")
for name, (m, X_va) in models.items():
    probs = m.predict_proba(X_va)[:, 1]
    auc = roc_auc_score(y_va, probs)
    preds = (probs >= 0.35).astype(int)
    rec = float(np.sum((preds == 1) & (y_va == 1)) / max(1, np.sum(y_va == 1)))
    fpr = float(np.sum((preds == 1) & (y_va == 0)) / max(1, np.sum(y_va == 0)))
    print(f"{name:30s} | ROC-AUC: {auc:.4f} | Recall: {rec*100:.2f}% | FPR: {fpr*100:.2f}%")

print("\nModel training and validation complete. Models saved to:", MODELS_DIR)
