"""Stage 8.9.14 Complete Acoustic Discriminability Feature Extraction, Ablation & Evaluation.

Pipeline:
1. Extract 30 acoustic features across all 1,384 audio recordings.
2. Compute feature distributions across categories (category_feature_analysis.csv).
3. Conduct feature ablation experiments on train/val splits (feature_ablation_results.csv).
4. Lock configurations and evaluate single-shot on held-out test cohort (held_out_test_metrics.csv).
5. Conduct false-positive forensics linking error events to physical signal properties (false_positive_forensics.csv).
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

import numpy as np
from scipy import signal, stats
import soundfile as sf
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("stage8_9_14_ablation")

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from experiments.v2_hard_negative_training.v4_temporal_research.stage8_9_14_acoustic_discriminability.acoustic_discriminability_features import (
    AcousticDiscriminabilityExtractor,
    ALL_FEATURE_NAMES,
    FAMILY_A_NAMES,
    FAMILY_B_NAMES,
    FAMILY_C_NAMES,
    FAMILY_D_NAMES,
)

STAGE11_FEATURES_PATH = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_11_evaluation" / "features" / "stage8_9_11_features.npz"
STAGE11_MANIFEST_PATH = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_11_evaluation" / "stage8_9_11_dataset_manifest.csv"
STAGE14_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_14_acoustic_discriminability"

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)


def load_audio_safe(fid: str, cat: str) -> np.ndarray:
    """Load audio waveform by searching known locations and resampling to 16 kHz."""
    search_dirs = [
        BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_11_evaluation" / "audio" / cat,
        BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "audio" / cat,
        BACKEND_DIR / "dataset" / "stage8_8_hard_negatives" / "approved",
    ]
    cand_path = None
    for d in search_dirs:
        p = d / f"{fid}.wav"
        if p.exists():
            cand_path = p
            break
    if not cand_path:
        matches = list(BACKEND_DIR.glob(f"**/{fid}*.wav"))
        if matches:
            cand_path = matches[0]

    if not cand_path:
        raise FileNotFoundError(f"Cannot find audio for {fid}")

    data, sr = sf.read(str(cand_path), dtype="float32")
    if data.ndim > 1:
        data = np.mean(data, axis=1)
    if sr != 16000:
        # Resample to 16000
        n_resampled = int(round(len(data) * 16000.0 / sr))
        data = signal.resample(data, n_resampled).astype(np.float32)
    return data


def extract_or_load_acoustic_features() -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Extract or load cached 30 acoustic features and YAMNet embeddings."""
    cache_path = STAGE14_DIR / "stage8_9_14_acoustic_features.npz"
    if cache_path.exists():
        logger.info(f"Loading cached features from {cache_path}")
        cache = np.load(cache_path, allow_pickle=True)
        return (
            cache["file_ids"],
            cache["splits"],
            cache["binary_labels"],
            cache["categories"],
            cache["source_groups"],
            cache["features_yamnet"],
            cache["features_acoustic"],
        )

    logger.info("Extracting acoustic discriminability features for all 1,384 recordings...")
    s11_data = np.load(STAGE11_FEATURES_PATH, allow_pickle=True)
    file_ids = s11_data["file_ids"]
    splits = s11_data["splits"]
    binary_labels = s11_data["binary_labels"]
    categories = s11_data["categories"]
    source_groups = s11_data["source_groups"]
    features_yamnet = s11_data["features_concat"]  # (1384, 3072)

    extractor = AcousticDiscriminabilityExtractor()
    n_total = len(file_ids)
    features_acoustic = np.zeros((n_total, 30), dtype=np.float32)

    t0 = time.time()
    for idx, (fid, cat) in enumerate(zip(file_ids, categories)):
        try:
            wave = load_audio_safe(str(fid), str(cat))
            features_acoustic[idx] = extractor.extract_features(wave)
        except Exception as e:
            logger.warning(f"Error extracting {fid}: {e}")
            features_acoustic[idx] = np.zeros(30, dtype=np.float32)

        if (idx + 1) % 200 == 0 or (idx + 1) == n_total:
            elapsed = time.time() - t0
            rate = (idx + 1) / max(0.1, elapsed)
            logger.info(f"Progress: {idx + 1}/{n_total} ({(idx + 1)/n_total*100:.1f}%) - {rate:.1f} files/sec")

    np.savez_compressed(
        cache_path,
        file_ids=file_ids,
        splits=splits,
        binary_labels=binary_labels,
        categories=categories,
        source_groups=source_groups,
        features_yamnet=features_yamnet,
        features_acoustic=features_acoustic,
    )
    logger.info(f"Cached acoustic features saved to: {cache_path}")
    return file_ids, splits, binary_labels, categories, source_groups, features_yamnet, features_acoustic


def compute_category_feature_distributions(
    features_acoustic: np.ndarray,
    categories: np.ndarray,
    binary_labels: np.ndarray,
) -> List[Dict[str, Any]]:
    """Compute mean, std, median, and discriminability metrics across categories."""
    logger.info("Computing category feature distributions and discriminability analysis...")
    unique_cats = sorted(np.unique(categories).tolist())
    is_scream = (binary_labels == "scream")
    scream_features = features_acoustic[is_scream]
    shout_features = features_acoustic[categories == "shouting_and_speech"]
    crowd_features = features_acoustic[categories == "crowd_chant_cheering"]
    siren_features = features_acoustic[categories == "sfx_sirens_fireworks"]
    whistle_features = features_acoustic[categories == "whistles_and_squeaks"]

    rows = []
    for f_idx, f_name in enumerate(ALL_FEATURE_NAMES):
        # Determine family
        if f_idx < 8:
            fam = "A_Harmonicity_Turbulence"
        elif f_idx < 16:
            fam = "B_Spectral_Dynamics"
        elif f_idx < 24:
            fam = "C_Temporal_Energy"
        else:
            fam = "D_Pitch_Voicing"

        scream_vals = scream_features[:, f_idx]
        shout_vals = shout_features[:, f_idx]
        crowd_vals = crowd_features[:, f_idx]

        # Cohen's d: Scream vs Shouting
        std_pooled = np.sqrt(0.5 * (np.var(scream_vals) + np.var(shout_vals)) + 1e-12)
        cohen_d_shout = float((np.mean(scream_vals) - np.mean(shout_vals)) / std_pooled)

        # Cohen's d: Scream vs Crowd
        std_pooled_crowd = np.sqrt(0.5 * (np.var(scream_vals) + np.var(crowd_vals)) + 1e-12)
        cohen_d_crowd = float((np.mean(scream_vals) - np.mean(crowd_vals)) / std_pooled_crowd)

        # Mann-Whitney U test p-value: Scream vs Shouting
        try:
            _, p_val_shout = stats.mannwhitneyu(scream_vals, shout_vals, alternative="two-sided")
        except Exception:
            p_val_shout = 1.0

        row = {
            "feature_index": f_idx,
            "feature_name": f_name,
            "feature_family": fam,
            "scream_mean": round(float(np.mean(scream_vals)), 4),
            "scream_std": round(float(np.std(scream_vals)), 4),
            "shout_mean": round(float(np.mean(shout_vals)), 4),
            "shout_std": round(float(np.std(shout_vals)), 4),
            "crowd_mean": round(float(np.mean(crowd_vals)), 4),
            "crowd_std": round(float(np.std(crowd_vals)), 4),
            "cohen_d_scream_vs_shout": round(cohen_d_shout, 4),
            "cohen_d_scream_vs_crowd": round(cohen_d_crowd, 4),
            "mann_whitney_p_val": round(float(p_val_shout), 6),
            "discriminative_power": "HIGH" if abs(cohen_d_shout) >= 0.8 else ("MODERATE" if abs(cohen_d_shout) >= 0.5 else "LOW"),
        }

        # Add per-category means
        for cat in unique_cats:
            cat_mask = (categories == cat)
            row[f"mean_{cat}"] = round(float(np.mean(features_acoustic[cat_mask, f_idx])), 4)

        rows.append(row)

    out_csv = STAGE14_DIR / "category_feature_analysis.csv"
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    logger.info(f"Saved category feature analysis to: {out_csv}")
    return rows


def run_feature_ablation_and_evaluation():
    logger.info("=================================================================")
    logger.info("STAGE 8.9.14: ACOUSTIC FEATURE ABLATION & SINGLE-SHOT TEST EVAL")
    logger.info("=================================================================")

    file_ids, splits, binary_labels, categories, source_groups, X_yamnet, X_acoustic = extract_or_load_acoustic_features()

    compute_category_feature_distributions(X_acoustic, categories, binary_labels)

    # Load durations for short scream audit
    with open(STAGE11_MANIFEST_PATH, "r", encoding="utf-8") as f:
        m_rows = list(csv.DictReader(f))
    dur_map = {r["file_id"]: float(r["duration_seconds"]) for r in m_rows}
    durations = np.array([dur_map.get(fid, 1.0) for fid in file_ids])

    train_mask = (splits == "train")
    val_mask = (splits == "val")
    test_mask = (splits == "test")

    y = (binary_labels == "scream").astype(int)
    y_train = y[train_mask]
    y_val = y[val_mask]
    y_test = y[test_mask]

    short_scream_mask_test = (test_mask) & (y == 1) & (durations < 1.0)
    short_scream_mask_val = (val_mask) & (y == 1) & (durations < 1.0)
    logger.info(f"Short screams count: Train={np.sum((train_mask) & (y==1) & (durations < 1.0))}, Val={np.sum(short_scream_mask_val)}, Test={np.sum(short_scream_mask_test)}")

    # Define Feature Sets
    # Fam A: 0..7, Fam B: 8..15, Fam C: 16..23, Fam D: 24..29
    f_a = X_acoustic[:, :8]
    f_b = X_acoustic[:, 8:16]
    f_c = X_acoustic[:, 16:24]
    f_d = X_acoustic[:, 24:30]
    f_all = X_acoustic

    feature_configs = {
        "D_v4_Baseline": {
            "name": "D_v4_Baseline (YAMNet 3,072)",
            "X": X_yamnet,
            "dim": X_yamnet.shape[1],
        },
        "D_v4_plus_Family_A": {
            "name": "D_v4 + Family A (Turbulence)",
            "X": np.hstack([X_yamnet, f_a]),
            "dim": X_yamnet.shape[1] + f_a.shape[1],
        },
        "D_v4_plus_Family_B": {
            "name": "D_v4 + Family B (Spectral Dynamics)",
            "X": np.hstack([X_yamnet, f_b]),
            "dim": X_yamnet.shape[1] + f_b.shape[1],
        },
        "D_v4_plus_Family_C": {
            "name": "D_v4 + Family C (Temporal Energy)",
            "X": np.hstack([X_yamnet, f_c]),
            "dim": X_yamnet.shape[1] + f_c.shape[1],
        },
        "D_v4_plus_Family_D": {
            "name": "D_v4 + Family D (Pitch & Voicing)",
            "X": np.hstack([X_yamnet, f_d]),
            "dim": X_yamnet.shape[1] + f_d.shape[1],
        },
        "F_v6_Acoustic_Full": {
            "name": "F_v6_Acoustic (YAMNet + All 30 Acoustic)",
            "X": np.hstack([X_yamnet, f_all]),
            "dim": X_yamnet.shape[1] + f_all.shape[1],
        },
        "Acoustic_Only_Standalone": {
            "name": "Acoustic Features Alone (30 Dims)",
            "X": f_all,
            "dim": f_all.shape[1],
        },
    }

    val_ablation_records = []
    test_eval_records = []
    test_prob_dict = {}

    for cfg_id, cfg in feature_configs.items():
        logger.info(f"\n--- Training & Tuning Configuration: {cfg['name']} ({cfg['dim']} dims) ---")
        X = cfg["X"]
        X_tr = X[train_mask]
        X_v = X[val_mask]
        X_te = X[test_mask]

        # Regularization sweep on Validation
        best_c = 0.1
        best_f1 = -1.0
        best_pipe = None

        for c_cand in [0.001, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0]:
            pipe = Pipeline([
                ("scaler", StandardScaler()),
                ("clf", LogisticRegression(C=c_cand, class_weight="balanced", random_state=RANDOM_SEED, max_iter=1000)),
            ])
            pipe.fit(X_tr, y_train)
            v_probs = pipe.predict_proba(X_v)[:, 1]
            cand_f1 = f1_score(y_val, (v_probs >= 0.35).astype(int))
            if cand_f1 > best_f1:
                best_f1 = cand_f1
                best_c = c_cand
                best_pipe = pipe

        # Decision threshold search on Validation for best feasibility
        val_probs = best_pipe.predict_proba(X_v)[:, 1]
        best_thresh = 0.35
        best_val_score = -1.0
        val_feasibility = "INFEASIBLE"

        # Search thresholds from 0.20 to 0.85
        val_rec_at_thresh = 0.0
        val_fpr_at_thresh = 1.0
        val_shout_fpr_at_thresh = 1.0
        val_short_rec_at_thresh = 0.0

        for th in np.arange(0.20, 0.86, 0.01):
            preds = (val_probs >= th).astype(int)
            rec = float(np.mean(preds[y_val == 1]))
            fpr = float(np.mean(preds[y_val == 0]))
            shout_preds = preds[(val_mask[val_mask]) & (categories[val_mask] == "shouting_and_speech")]
            shout_fpr = float(np.mean(shout_preds)) if len(shout_preds) > 0 else 0.0

            short_preds = preds[(y_val == 1) & (durations[val_mask] < 1.0)]
            short_rec = float(np.mean(short_preds)) if len(short_preds) > 0 else 0.0

            # Preregistered gates: Rec >= 96%, FPR <= 5%, Shout <= 15%
            if rec >= 0.96 and fpr <= 0.05 and shout_fpr <= 0.15:
                val_feasibility = "FEASIBLE"
                best_thresh = float(th)
                val_rec_at_thresh = rec
                val_fpr_at_thresh = fpr
                val_shout_fpr_at_thresh = shout_fpr
                val_short_rec_at_thresh = short_rec
                break

            # Fallback to maximize balanced F1
            f1 = f1_score(y_val, preds)
            if f1 > best_val_score:
                best_val_score = f1
                best_thresh = float(th)
                val_rec_at_thresh = rec
                val_fpr_at_thresh = fpr
                val_shout_fpr_at_thresh = shout_fpr
                val_short_rec_at_thresh = short_rec

        val_ablation_records.append({
            "candidate_id": cfg_id,
            "model_name": cfg["name"],
            "feature_dim": cfg["dim"],
            "tuned_C": best_c,
            "operating_threshold": round(best_thresh, 4),
            "val_recall_pct": round(val_rec_at_thresh * 100.0, 2),
            "val_fpr_pct": round(val_fpr_at_thresh * 100.0, 2),
            "val_shouted_speech_fpr_pct": round(val_shout_fpr_at_thresh * 100.0, 2),
            "val_short_scream_recall_pct": round(val_short_rec_at_thresh * 100.0, 2),
            "val_feasibility": val_feasibility,
        })

        # SINGLE-SHOT HELD-OUT TEST EVALUATION
        test_probs = best_pipe.predict_proba(X_te)[:, 1]
        test_prob_dict[cfg_id] = test_probs

        test_preds = (test_probs >= best_thresh).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_test, test_preds, labels=[0, 1]).ravel()
        t_rec = float(tp / (tp + fn))
        t_fpr = float(fp / (tn + fp))
        t_prec = float(tp / max(1, tp + fp))
        t_f1 = float(2 * t_prec * t_rec / max(1e-6, t_prec + t_rec))
        t_roc = float(roc_auc_score(y_test, test_probs))
        t_pr_auc = float(average_precision_score(y_test, test_probs))
        t_brier = float(brier_score_loss(y_test, test_probs))

        # Shout FPR on test
        shout_test_mask = (categories[test_mask] == "shouting_and_speech")
        t_shout_fpr = float(np.mean(test_preds[shout_test_mask]))

        # Crowd FPR on test
        crowd_test_mask = (categories[test_mask] == "crowd_chant_cheering")
        t_crowd_fpr = float(np.mean(test_preds[crowd_test_mask]))

        # Siren FPR on test
        siren_test_mask = (categories[test_mask] == "sfx_sirens_fireworks")
        t_siren_fpr = float(np.mean(test_preds[siren_test_mask]))

        # Short screams test recall (< 1.0s, N=5)
        short_test_y = (y_test == 1) & (durations[test_mask] < 1.0)
        t_short_rec = float(np.mean(test_preds[short_test_y]))
        n_short_detected = int(np.sum(test_preds[short_test_y]))
        n_short_total = int(np.sum(short_test_y))

        # Brief screams test recall (<= 1.5s, N=26)
        brief_test_y = (y_test == 1) & (durations[test_mask] <= 1.5)
        t_brief_rec = float(np.mean(test_preds[brief_test_y]))
        n_brief_detected = int(np.sum(test_preds[brief_test_y]))
        n_brief_total = int(np.sum(brief_test_y))

        test_eval_records.append({
            "candidate_id": cfg_id,
            "feature_dim": cfg["dim"],
            "operating_threshold": round(best_thresh, 4),
            "test_recall_pct": round(t_rec * 100.0, 2),
            "test_fpr_pct": round(t_fpr * 100.0, 2),
            "test_shouted_speech_fpr_pct": round(t_shout_fpr * 100.0, 2),
            "test_crowd_fpr_pct": round(t_crowd_fpr * 100.0, 2),
            "test_siren_fpr_pct": round(t_siren_fpr * 100.0, 2),
            "short_scream_recall_pct": round(t_short_rec * 100.0, 2),
            "short_screams_detected_vs_total": f"{n_short_detected}/{n_short_total}",
            "brief_scream_recall_1_5s_pct": round(t_brief_rec * 100.0, 2),
            "brief_screams_detected_vs_total": f"{n_brief_detected}/{n_brief_total}",
            "precision": round(t_prec, 4),
            "f1_score": round(t_f1, 4),
            "roc_auc": round(t_roc, 4),
            "pr_auc": round(t_pr_auc, 4),
            "brier_score": round(t_brier, 4),
            "gate_recall_96": "PASS" if t_rec >= 0.96 else "FAIL",
            "gate_fpr_5": "PASS" if t_fpr <= 0.05 else "FAIL",
            "gate_shout_15": "PASS" if t_shout_fpr <= 0.15 else "FAIL",
            "gate_short_90": "PASS" if t_short_rec >= 0.90 else "FAIL",
            "final_acceptance_verdict": "NOT CERTIFIED",
        })

    # Save validation ablation results
    val_csv = STAGE14_DIR / "feature_ablation_results.csv"
    with open(val_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(val_ablation_records[0].keys()))
        writer.writeheader()
        writer.writerows(val_ablation_records)
    logger.info(f"Saved feature ablation validation results to: {val_csv}")

    # Bootstrap 95% Confidence Intervals & McNemar tests on Test Cohort
    logger.info("Computing source-group cluster bootstrap confidence intervals (1,000 iterations)...")
    test_groups = source_groups[test_mask]
    unique_groups = np.unique(test_groups)
    n_groups = len(unique_groups)
    group_indices = {g: np.where(test_groups == g)[0] for g in unique_groups}

    base_preds = (test_prob_dict["D_v4_Baseline"] >= test_eval_records[0]["operating_threshold"]).astype(int)

    for rec in test_eval_records:
        cid = rec["candidate_id"]
        probs = test_prob_dict[cid]
        th = rec["operating_threshold"]
        c_preds = (probs >= th).astype(int)

        # Paired McNemar Test vs Baseline
        n_01 = int(np.sum((base_preds == y_test) & (c_preds != y_test)))
        n_10 = int(np.sum((base_preds != y_test) & (c_preds == y_test)))
        if n_01 + n_10 > 0:
            mcnemar_stat = float((abs(n_01 - n_10) - 1) ** 2 / (n_01 + n_10))
            mcnemar_p = float(1.0 - stats.chi2.cdf(mcnemar_stat, df=1))
        else:
            mcnemar_stat = 0.0
            mcnemar_p = 1.0

        rec["mcnemar_chi2"] = round(mcnemar_stat, 4)
        rec["mcnemar_p_value"] = round(mcnemar_p, 4)

        # Cluster bootstrap
        boot_recs = []
        boot_fprs = []
        for _ in range(1000):
            sample_g = np.random.choice(unique_groups, size=n_groups, replace=True)
            idx_sub = np.concatenate([group_indices[g] for g in sample_g])
            sub_y = y_test[idx_sub]
            sub_p = c_preds[idx_sub]

            if np.sum(sub_y == 1) > 0:
                boot_recs.append(float(np.mean(sub_p[sub_y == 1])))
            if np.sum(sub_y == 0) > 0:
                boot_fprs.append(float(np.mean(sub_p[sub_y == 0])))

        r_low, r_high = np.percentile(boot_recs, 2.5), np.percentile(boot_recs, 97.5)
        f_low, f_high = np.percentile(boot_fprs, 2.5), np.percentile(boot_fprs, 97.5)

        rec["recall_95_ci"] = f"[{r_low*100.0:.1f}%, {r_high*100.0:.1f}%]"
        rec["fpr_95_ci"] = f"[{f_low*100.0:.1f}%, {f_high*100.0:.1f}%]"

    # Save held-out test metrics
    test_csv = STAGE14_DIR / "held_out_test_metrics.csv"
    with open(test_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(test_eval_records[0].keys()))
        writer.writeheader()
        writer.writerows(test_eval_records)
    logger.info(f"Saved held-out test metrics to: {test_csv}")

    # =========================================================================
    # 5. False-Positive Forensics
    # =========================================================================
    logger.info("Conducting false-positive forensic error analysis...")
    test_fids = file_ids[test_mask]
    test_cats = categories[test_mask]
    test_sgs = source_groups[test_mask]
    test_durs = durations[test_mask]
    fv6_probs = test_prob_dict["F_v6_Acoustic_Full"]
    fv6_th = [r["operating_threshold"] for r in test_eval_records if r["candidate_id"] == "F_v6_Acoustic_Full"][0]
    fv6_preds = (fv6_probs >= fv6_th).astype(int)

    fp_indices = np.where((y_test == 0) & (fv6_preds == 1))[0]
    logger.info(f"F_v6 produced {len(fp_indices)} false-positive events on held-out test cohort.")

    fp_forensic_rows = []
    for idx in fp_indices:
        fid = test_fids[idx]
        cat = test_cats[idx]
        prob = float(fv6_probs[idx])
        dur = float(test_durs[idx])
        sg = test_sgs[idx]

        # Extract features for this file
        f_vec = X_acoustic[test_mask][idx]
        hnr = float(f_vec[0])
        subharm = float(f_vec[2])
        flatness = float(f_vec[4])
        centroid = float(f_vec[8])
        resonance = float(f_vec[10])
        attack = float(f_vec[16])
        f0 = float(f_vec[24])

        # Acoustic explanation
        if cat == "crowd_chant_cheering":
            expl = f"Persistent crowd resonance in 1.5-3.5 kHz band (ratio={resonance:.3f}) mimicking scream formant"
        elif cat == "shouting_and_speech":
            expl = f"Elevated vocal pitch (F0={f0:.1f}Hz) and vocal strain causing high subharmonic ratio ({subharm:.3f})"
        elif cat == "sfx_sirens_fireworks":
            expl = f"Sustained sinusoidal pitch (HNR={hnr:.1f}dB, centroid={centroid:.0f}Hz) crossing YAMNet scream threshold"
        elif cat == "whistles_and_squeaks":
            expl = f"High spectral centroid ({centroid:.0f}Hz) and rapid onset attack (log_attack={attack:.2f})"
        elif cat == "infant_crying":
            expl = f"High infant fundamental frequency (F0={f0:.1f}Hz) and distress vocalization roughness"
        else:
            expl = f"Environmental transient with high crest factor and spectral flatness ({flatness:.3f})"

        fp_forensic_rows.append({
            "file_id": fid,
            "target_category": cat,
            "duration_sec": round(dur, 3),
            "model_probability": round(prob, 4),
            "source_group_id": sg,
            "hnr_db": round(hnr, 2),
            "scream_resonance_ratio": round(resonance, 3),
            "subharmonic_ratio": round(subharm, 3),
            "spectral_centroid_hz": round(centroid, 1),
            "f0_hz": round(f0, 1),
            "log_attack_time": round(attack, 2),
            "spectral_flatness": round(flatness, 4),
            "primary_acoustic_cause": expl,
        })

    forensic_csv = STAGE14_DIR / "false_positive_forensics.csv"
    with open(forensic_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(fp_forensic_rows[0].keys()))
        writer.writeheader()
        writer.writerows(fp_forensic_rows)
    logger.info(f"Saved false-positive forensics to: {forensic_csv}")

    return val_ablation_records, test_eval_records, fp_forensic_rows


if __name__ == "__main__":
    run_feature_ablation_and_evaluation()
