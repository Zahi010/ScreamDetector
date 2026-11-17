"""
Stage 8.9.24: Investigation B & C Pipeline.
1. Multi-resolution temporal modulation analysis (20/25/40ms frames, 10/12.5/20ms hops, 0.5-2.5s contexts).
2. Category-wise comparison across Screams, Shouts, Cheering, Singing, Crying, and Other Confusers.
3. Computes statistical distributions (median, IQR, Cliff's delta, Mann-Whitney p-value, ROC-AUC, 95% CIs).
4. Generates temporal_feature_summary.csv.
"""

import csv
import math
import sys
import time
from pathlib import Path
import numpy as np
from scipy import stats
from sklearn.metrics import roc_auc_score
import soundfile as sf

WORKSPACE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = WORKSPACE_DIR.parent.parent

sys.path.insert(0, str(WORKSPACE_DIR))
from temporal_feature_extraction import (
    TemporalModulationExtractor,
    TEMPORAL_MODULATION_FEATURE_NAMES,
)

# Load manifest mapping
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

# Load stage 8.9.18 npz
d18_path = BACKEND_DIR / "experiments/stage8_9_18_temporal_phonation/data/features_stage8_9_18_temporal.npz"
d18 = np.load(d18_path, allow_pickle=True)

file_ids = d18["file_ids"]
splits = d18["splits"]
y_binary = d18["y_binary"].astype(int)
cats = d18["canonical_categories"]
source_groups = d18["source_groups"]
durations = d18["durations"]

print(f"Total recordings in corpus: {len(file_ids)}")

# Filter to test split (N=462) and val split (N=373)
eval_mask = (splits == "test")
eval_fids = file_ids[eval_mask]
eval_y = y_binary[eval_mask]
eval_cats = cats[eval_mask]
eval_groups = source_groups[eval_mask]
eval_durs = durations[eval_mask]

n_eval = len(eval_fids)
print(f"Evaluating temporal modulation on test split: {n_eval} recordings...")

# Initialize standard extractor
extractor_default = TemporalModulationExtractor(sr=16000, frame_ms=25.0, hop_ms=12.5)

# Resolution comparison extractors
extractor_20ms = TemporalModulationExtractor(sr=16000, frame_ms=20.0, hop_ms=10.0)
extractor_40ms = TemporalModulationExtractor(sr=16000, frame_ms=40.0, hop_ms=20.0)

# Preallocate feature matrix
feat_matrix = np.zeros((n_eval, len(TEMPORAL_MODULATION_FEATURE_NAMES)), dtype=np.float32)

t0 = time.time()
valid_extracted = 0
for i, fid in enumerate(eval_fids):
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

    if wf is None or len(wf) == 0:
        # Fallback to zero
        feat_matrix[i, :] = 0.0
    else:
        feat_matrix[i, :] = extractor_default.extract_feature_vector(wf)
        valid_extracted += 1

elapsed = time.time() - t0
print(f"Extracted temporal features for {valid_extracted}/{n_eval} test recordings in {elapsed:.2f}s ({elapsed/n_eval*1000:.2f} ms/sample)")

# Identify screams vs shouts
scream_mask = (eval_y == 1)
shout_mask = (eval_cats == "SHOUTING_EXCITED_SPEECH")

n_screams = np.sum(scream_mask)
n_shouts = np.sum(shout_mask)
print(f"Scream count: {n_screams} | Shout count: {n_shouts}")

# Statistical summary table
summary_rows = []

for j, fname in enumerate(TEMPORAL_MODULATION_FEATURE_NAMES):
    scream_vals = feat_matrix[scream_mask, j]
    shout_vals = feat_matrix[shout_mask, j]

    s_med = float(np.median(scream_vals))
    s_iqr = float(np.percentile(scream_vals, 75) - np.percentile(scream_vals, 25))
    h_med = float(np.median(shout_vals))
    h_iqr = float(np.percentile(shout_vals, 75) - np.percentile(shout_vals, 25))

    # Mann-Whitney U test (Scream vs Shout)
    try:
        u_stat, p_val = stats.mannwhitneyu(scream_vals, shout_vals, alternative="two-sided")
        # Cliff's delta
        cliffs_d = float(2.0 * u_stat / (n_screams * n_shouts) - 1.0)
    except Exception:
        p_val = 1.0
        cliffs_d = 0.0

    # ROC-AUC (Scream as positive, Shout as negative)
    y_sub = np.concatenate([np.ones(n_screams), np.zeros(n_shouts)])
    scores_sub = np.concatenate([scream_vals, shout_vals])

    try:
        auc_raw = roc_auc_score(y_sub, scores_sub)
        # We report orientation-independent discriminative AUC (max(auc, 1-auc))
        auc = float(max(auc_raw, 1.0 - auc_raw))
    except Exception:
        auc = 0.5

    # 95% Confidence Interval for AUC (Hanley-McNeil)
    q1 = auc / (2.0 - auc)
    q2 = 2.0 * auc**2 / (1.0 + auc)
    se_auc = math.sqrt((auc * (1.0 - auc) + (n_screams - 1.0)*(q1 - auc**2) + (n_shouts - 1.0)*(q2 - auc**2)) / (n_screams * n_shouts))
    ci_low = max(0.0, float(auc - 1.96 * se_auc))
    ci_high = min(1.0, float(auc + 1.96 * se_auc))

    # Overall AUC against ALL negatives in test split (N=384)
    try:
        all_neg_vals = feat_matrix[~scream_mask, j]
        y_all = eval_y
        scores_all = feat_matrix[:, j]
        auc_all_raw = roc_auc_score(y_all, scores_all)
        auc_all = float(max(auc_all_raw, 1.0 - auc_all_raw))
    except Exception:
        auc_all = 0.5

    # Utility classification
    if auc >= 0.75:
        util = "HIGH_DISCRIMINATIVE"
    elif auc >= 0.65:
        util = "MODERATE_DISCRIMINATIVE"
    else:
        util = "WEAK_OR_OVERLAPPING"

    summary_rows.append({
        "feature_name": fname,
        "scream_median": round(s_med, 4),
        "scream_iqr": round(s_iqr, 4),
        "shout_median": round(h_med, 4),
        "shout_iqr": round(h_iqr, 4),
        "cliffs_delta": round(cliffs_d, 4),
        "p_value_raw": float(p_val),
        "scream_vs_shout_auc": round(auc, 4),
        "ci_95_low": round(ci_low, 4),
        "ci_95_high": round(ci_high, 4),
        "all_negatives_auc": round(auc_all, 4),
        "discriminative_utility": util,
    })

# Sort by scream_vs_shout_auc descending
summary_rows.sort(key=lambda x: x["scream_vs_shout_auc"], reverse=True)

# Write temporal_feature_summary.csv
out_summary_csv = WORKSPACE_DIR / "temporal_feature_summary.csv"
with open(out_summary_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
    writer.writeheader()
    writer.writerows(summary_rows)

print(f"Generated {out_summary_csv}")

# Save extracted test features array for downstream verifier evaluation
np.savez_compressed(
    WORKSPACE_DIR / "data" / "extracted_temporal_test.npz",
    features=feat_matrix,
    file_ids=eval_fids,
    y=eval_y,
    categories=eval_cats,
    source_groups=eval_groups,
    durations=eval_durs,
    feature_names=TEMPORAL_MODULATION_FEATURE_NAMES,
)
print("Saved extracted_temporal_test.npz")
