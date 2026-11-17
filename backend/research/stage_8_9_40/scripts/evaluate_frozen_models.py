"""
Stage 8.9.40 - Phase E: Frozen Model Multi-Cohort Evaluation & Gates Verification
Evaluates:
- Configuration B (DualEncoderAcousticModel, frozen checkpoint, frozen threshold 0.24)
- Configuration D (MultiPathwayFusionModel, frozen checkpoint, frozen threshold 0.34)

Across three separate cohorts:
1. Stage 8.9.39 Frozen Expansion Benchmark Snapshot (N=102: 65 short screams, 37 hard negatives across 49 source groups)
2. Stage 8.9.40 New Independent Hard-Negative Evaluation Cohort (N=145: 54 shouted speech, 30 crowd chanting, 21 whistles, 16 infant crying, 14 sirens/transients, 10 environmental across 79 source groups)
3. Historical Continuity Benchmark (N=293: View A & View B)

Computes:
- Clip-level & source-group-level TP, FP, TN, FN, Recall, FPR, Precision, F1, ROC-AUC, PR-AUC, Brier score.
- Exact numerators, denominators, and 95% Wilson score confidence intervals.
- Category-specific FPRs.
- Formal evaluation of the Five Research Acceptance Gates.
"""
import os
import sys
import json
import csv
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import soundfile as sf
import scipy.signal as signal
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    average_precision_score, confusion_matrix, brier_score_loss
)
import joblib

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

STAGE38_DIR = BACKEND_DIR / "research" / "stage_8_9_38"
STAGE39_DIR = BACKEND_DIR / "research" / "stage_8_9_39"
STAGE40_DIR = BACKEND_DIR / "research" / "stage_8_9_40"

# Import model architectures from Stage 8.9.39
sys.path.insert(0, str(STAGE39_DIR))
from scripts.train_config_b import DualEncoderAcousticModel
from scripts.train_config_d import MultiPathwayFusionModel

VOCAL_CLASS_INDICES = [0, 1, 2, 3, 6, 7, 8, 13, 14, 16, 17]
CROWD_CLASS_INDICES = [67, 68, 69]
SCREAM_CLASS_INDEX = 6

BANDS = [
    ("Band1_300_800Hz", 300, 800),
    ("Band2_800_1500Hz", 800, 1500),
    ("Band3_1500_2000Hz", 1500, 2000),
    ("Band4_2000_3000Hz", 2000, 3000),
    ("Band5_3000_4000Hz", 3000, 4000),
    ("Band6_4000_6000Hz", 4000, 6000)
]

def extract_subband_vector(audio, sr=16000):
    nyq = sr / 2.0
    total_energy = np.sum(audio ** 2) + 1e-9
    
    band_energies = []
    temp_vars = []
    
    for b_name, f_low, f_high in BANDS:
        low_norm = f_low / nyq
        high_norm = min(0.999, f_high / nyq)
        b, a = signal.butter(4, [low_norm, high_norm], btype='band')
        filtered = signal.filtfilt(b, a, audio)
        
        band_energy = float(np.sum(filtered ** 2))
        band_energies.append(band_energy)
        
        hop = int(0.010 * sr)
        frame = int(0.025 * sr)
        n_frames = max(1, (len(filtered) - frame) // hop + 1)
        frame_rms = [np.sqrt(np.mean(filtered[i*hop:i*hop+frame]**2) + 1e-9) for i in range(n_frames)]
        energy_std = float(np.std(frame_rms))
        energy_mean = float(np.mean(frame_rms))
        temp_var = energy_std / (energy_mean + 1e-9)
        temp_vars.append(temp_var)
        
    rel_energies = [be / total_energy for be in band_energies]
    low_e = band_energies[0] + band_energies[1] + 1e-9
    scream_band_e = band_energies[3] + band_energies[4] + 1e-9
    scream_band_to_vocal_ratio = float(scream_band_e / low_e)
    high_band_whistle_ratio = float(band_energies[5] / total_energy)
    
    vec = [
        float(rel_energies[0]),
        float(rel_energies[1]),
        float(rel_energies[2]),
        float(rel_energies[3]),
        float(rel_energies[4]),
        float(rel_energies[5]),
        float(temp_vars[0]),
        float(temp_vars[3]),
        float(temp_vars[4]),
        scream_band_to_vocal_ratio,
        high_band_whistle_ratio
    ]
    return np.array(vec, dtype=np.float32)

def wilson_score_interval(k, n, confidence=0.95):
    if n == 0:
        return 0.0, 0.0, 0.0
    z = 1.95996
    p_hat = k / n
    denom = 1 + (z**2) / n
    center = (p_hat + (z**2) / (2 * n)) / denom
    margin = (z / denom) * np.sqrt((p_hat * (1 - p_hat) / n) + (z**2) / (4 * n**2))
    ci_low = max(0.0, center - margin)
    ci_high = min(1.0, center + margin)
    return float(p_hat), float(ci_low), float(ci_high)

def extract_features_for_new_cohort(manifest_path, cache_out_path):
    print(f"Extracting YAMNet and acoustic features for new cohort: {manifest_path}")
    df = pd.read_csv(manifest_path)
    
    yamnet = YAMNetLoader()
    yamnet.load()

    X_sem_list = []
    X_acoust_list = []
    X_subband_list = []

    for idx, r in df.iterrows():
        audio_path = REPO_ROOT / r["workspace_audio_path"]
        wf, _ = load_audio(audio_path, target_sr=TARGET_SAMPLE_RATE)
        preds, embs, _ = yamnet.infer(wf)

        f_sem = np.mean(embs, axis=0).astype(np.float32)

        vocal_frames = np.max(preds[:, VOCAL_CLASS_INDICES], axis=1)
        crowd_frames = np.max(preds[:, CROWD_CLASS_INDICES], axis=1)
        scream_frames = preds[:, SCREAM_CLASS_INDEX]

        f_acoust = np.array([
            float(np.max(vocal_frames)),
            float(np.mean(vocal_frames)),
            float(np.max(crowd_frames)),
            float(np.mean(crowd_frames)),
            float(np.max(scream_frames)),
            float(np.mean(scream_frames)),
        ], dtype=np.float32)

        raw_audio, sr = sf.read(str(audio_path))
        if raw_audio.ndim > 1:
            raw_audio = np.mean(raw_audio, axis=1)
        f_sb = extract_subband_vector(raw_audio, sr=sr)

        X_sem_list.append(f_sem)
        X_acoust_list.append(f_acoust)
        X_subband_list.append(f_sb)

    X_sem = np.array(X_sem_list, dtype=np.float32)
    X_acoust = np.array(X_acoust_list, dtype=np.float32)
    mask_acoust = (~np.isnan(X_acoust) & (X_acoust > 0.0)).astype(np.float32)
    X_subband = np.array(X_subband_list, dtype=np.float32)

    np.savez_compressed(
        cache_out_path,
        file_ids=df["file_id"].values,
        categories=df["target_category"].values,
        source_groups=df["source_group_id"].values,
        labels=np.zeros(len(df), dtype=np.int32), # All hard negatives
        durations=df["duration_seconds"].values,
        X_sem=X_sem,
        X_acoust=X_acoust,
        mask_acoust=mask_acoust,
        X_subband=X_subband
    )
    print(f"Saved extracted features: {cache_out_path}")

def run_evaluation():
    print("=" * 80)
    print("STAGE 8.9.40 - PHASE E: FROZEN MODEL EVALUATION ON ALL COHORTS")
    print("=" * 80)

    # 1. Feature extraction for new cohort if not already cached
    new_cache_path = STAGE40_DIR / "results" / "new_cohort_features.npz"
    new_manifest_path = STAGE40_DIR / "manifests" / "new_cohort_manifest.csv"
    if not new_cache_path.exists():
        extract_features_for_new_cohort(new_manifest_path, new_cache_path)

    # Load frozen checkpoints and calibrators from Stage 8.9.39
    ckpt_b_path = STAGE39_DIR / "checkpoints" / "config_b" / "best_model.pt"
    ckpt_d_path = STAGE39_DIR / "checkpoints" / "config_d" / "best_model.pt"
    calib_b_path = STAGE39_DIR / "checkpoints" / "config_b" / "platt_calibrator.joblib"
    calib_d_path = STAGE39_DIR / "checkpoints" / "config_d" / "platt_calibrator.joblib"

    print("Loading frozen Stage 8.9.39 checkpoints...")
    ckpt_b = torch.load(ckpt_b_path, map_location='cpu')
    model_b = DualEncoderAcousticModel(sem_dim=1024, acoustic_dim=6, proj_sem=128, proj_acoust=32)
    model_b.load_state_dict(ckpt_b['model_state_dict'])
    model_b.eval()

    ckpt_d = torch.load(ckpt_d_path, map_location='cpu')
    model_d = MultiPathwayFusionModel(sem_dim=1024, acoust_dim=6, subband_dim=11)
    model_d.load_state_dict(ckpt_d['model_state_dict'])
    model_d.eval()

    calib_b = joblib.load(calib_b_path)
    calib_d = joblib.load(calib_d_path)

    # Frozen thresholds
    thresh_b = 0.24
    thresh_d = 0.34
    print(f"Frozen thresholds: Config B = {thresh_b}, Config D = {thresh_d}")

    # Load Stage 8.9.39 cached features for Expansion and Historical cohorts
    v4_cache_path = STAGE39_DIR / "cache" / "stage_8_9_39_features.npz"
    v4_cache = np.load(v4_cache_path, allow_pickle=True)
    splits = v4_cache['splits']

    # Load new cohort cache
    new_cache = np.load(new_cache_path, allow_pickle=True)

    # -------------------------------------------------------------
    # Helper to evaluate a cohort
    # -------------------------------------------------------------
    def evaluate_model_on_data(model, t_sem, t_acoust, t_mask, t_sb=None):
        with torch.no_grad():
            if t_sb is None:
                logits, _, _ = model(t_sem, t_acoust, t_mask)
            else:
                logits, _, _ = model(t_sem, t_acoust, t_mask, t_sb)
            probs = torch.sigmoid(logits).numpy().flatten()
            logits_np = logits.numpy().flatten()
        return logits_np, probs

    def calculate_cohort_metrics(y_true, y_prob, threshold, categories, source_groups, durations):
        y_pred = (y_prob >= threshold).astype(int)
        tp = int(np.sum((y_true == 1) & (y_pred == 1)))
        fp = int(np.sum((y_true == 0) & (y_pred == 1)))
        tn = int(np.sum((y_true == 0) & (y_pred == 0)))
        fn = int(np.sum((y_true == 1) & (y_pred == 0)))
        n_pos = tp + fn
        n_neg = fp + tn

        rec, rec_low, rec_high = wilson_score_interval(tp, n_pos)
        hn_fpr, fpr_low, fpr_high = wilson_score_interval(fp, n_neg)
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
        brier = float(brier_score_loss(y_true, y_prob)) if len(y_true) > 0 else 0.0

        try:
            roc_auc = float(roc_auc_score(y_true, y_prob)) if len(np.unique(y_true)) > 1 else None
        except Exception:
            roc_auc = None

        try:
            pr_auc = float(average_precision_score(y_true, y_prob)) if len(np.unique(y_true)) > 1 else None
        except Exception:
            pr_auc = None

        # Category specific FPRs
        cat_metrics = {}
        for cat in np.unique(categories):
            cat_mask = (categories == cat)
            cat_neg_mask = cat_mask & (y_true == 0)
            n_cat_neg = int(np.sum(cat_neg_mask))
            if n_cat_neg > 0:
                cat_fp = int(np.sum(cat_neg_mask & (y_pred == 1)))
                cat_fpr, cat_low, cat_high = wilson_score_interval(cat_fp, n_cat_neg)
                cat_metrics[cat] = {
                    "total": n_cat_neg,
                    "fp": cat_fp,
                    "fpr": round(cat_fpr, 4),
                    "ci95": [round(cat_low, 4), round(cat_high, 4)],
                    "fraction": f"{cat_fp}/{n_cat_neg}"
                }

        # Short scream recall
        short_scream_mask = (y_true == 1) & (durations <= 1.0)
        n_short = int(np.sum(short_scream_mask))
        if n_short > 0:
            ss_tp = int(np.sum(short_scream_mask & (y_pred == 1)))
            ss_rec, ss_low, ss_high = wilson_score_interval(ss_tp, n_short)
            short_scream_stat = {
                "total": n_short, "tp": ss_tp,
                "recall": round(ss_rec, 4),
                "ci95": [round(ss_low, 4), round(ss_high, 4)],
                "fraction": f"{ss_tp}/{n_short}"
            }
        else:
            short_scream_stat = {"total": 0, "tp": 0, "recall": None, "ci95": None, "fraction": "0/0"}

        # Source-group level false alarm metrics
        unique_neg_sgs = np.unique(source_groups[y_true == 0]) if n_neg > 0 else np.array([])
        sg_fp_count = 0
        for sg in unique_neg_sgs:
            sg_mask = (source_groups == sg) & (y_true == 0)
            if np.any(y_pred[sg_mask] == 1):
                sg_fp_count += 1
        n_sg_neg = len(unique_neg_sgs)
        sg_fpr, sg_low, sg_high = wilson_score_interval(sg_fp_count, n_sg_neg)

        return {
            "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "total_samples": len(y_true),
            "scream_recall": {
                "value": round(rec, 4) if n_pos > 0 else None,
                "fraction": f"{tp}/{n_pos}",
                "ci95": [round(rec_low, 4), round(rec_high, 4)] if n_pos > 0 else None
            },
            "hard_negative_fpr": {
                "value": round(hn_fpr, 4) if n_neg > 0 else None,
                "fraction": f"{fp}/{n_neg}",
                "ci95": [round(fpr_low, 4), round(fpr_high, 4)] if n_neg > 0 else None
            },
            "source_group_fpr": {
                "value": round(sg_fpr, 4) if n_sg_neg > 0 else None,
                "fraction": f"{sg_fp_count}/{n_sg_neg}",
                "ci95": [round(sg_low, 4), round(sg_high, 4)] if n_sg_neg > 0 else None
            },
            "short_scream_recall": short_scream_stat,
            "category_metrics": cat_metrics,
            "precision": round(prec, 4) if (tp + fp) > 0 else None,
            "f1_score": round(f1, 4) if (tp + fp + fn) > 0 else None,
            "roc_auc": round(roc_auc, 4) if roc_auc is not None else None,
            "pr_auc": round(pr_auc, 4) if pr_auc is not None else None,
            "brier_score": round(brier, 4)
        }

    # -------------------------------------------------------------
    # 1. EVALUATE ON NEW INDEPENDENT HARD-NEGATIVE COHORT (N=145)
    # -------------------------------------------------------------
    print("\n--- Evaluating on Stage 8.9.40 New Independent Hard-Negative Cohort (N=145) ---")
    t_sem_new = torch.tensor(new_cache['X_sem'], dtype=torch.float32)
    t_acoust_new = torch.tensor(new_cache['X_acoust'], dtype=torch.float32)
    t_mask_new = torch.tensor(new_cache['mask_acoust'], dtype=torch.float32)
    t_sb_new = torch.tensor(new_cache['X_subband'], dtype=torch.float32)

    logits_b_new, probs_b_new = evaluate_model_on_data(model_b, t_sem_new, t_acoust_new, t_mask_new)
    logits_d_new, probs_d_new = evaluate_model_on_data(model_d, t_sem_new, t_acoust_new, t_mask_new, t_sb_new)

    metrics_b_new = calculate_cohort_metrics(
        new_cache['labels'], probs_b_new, thresh_b,
        new_cache['categories'], new_cache['source_groups'], new_cache['durations']
    )
    metrics_d_new = calculate_cohort_metrics(
        new_cache['labels'], probs_d_new, thresh_d,
        new_cache['categories'], new_cache['source_groups'], new_cache['durations']
    )

    print(f"Config B on New Cohort: Hard-Negative FPR = {metrics_b_new['hard_negative_fpr']['fraction']} ({metrics_b_new['hard_negative_fpr']['value']*100:.2f}%), 95% CI: {metrics_b_new['hard_negative_fpr']['ci95']}")
    print(f"  - Shouted Speech FPR: {metrics_b_new['category_metrics'].get('shouting_and_speech', {}).get('fraction')} ({metrics_b_new['category_metrics'].get('shouting_and_speech', {}).get('fpr', 0)*100:.2f}%)")
    print(f"  - Source Group FPR: {metrics_b_new['source_group_fpr']['fraction']} ({metrics_b_new['source_group_fpr']['value']*100:.2f}%)")

    print(f"Config D on New Cohort: Hard-Negative FPR = {metrics_d_new['hard_negative_fpr']['fraction']} ({metrics_d_new['hard_negative_fpr']['value']*100:.2f}%), 95% CI: {metrics_d_new['hard_negative_fpr']['ci95']}")
    print(f"  - Shouted Speech FPR: {metrics_d_new['category_metrics'].get('shouting_and_speech', {}).get('fraction')} ({metrics_d_new['category_metrics'].get('shouting_and_speech', {}).get('fpr', 0)*100:.2f}%)")
    print(f"  - Source Group FPR: {metrics_d_new['source_group_fpr']['fraction']} ({metrics_d_new['source_group_fpr']['value']*100:.2f}%)")

    # Save predictions
    df_pred_new_b = pd.DataFrame({
        "file_id": new_cache['file_ids'],
        "target_category": new_cache['categories'],
        "source_group_id": new_cache['source_groups'],
        "duration_seconds": new_cache['durations'],
        "ground_truth": new_cache['labels'],
        "logit": logits_b_new,
        "probability": probs_b_new,
        "threshold": thresh_b,
        "prediction": (probs_b_new >= thresh_b).astype(int)
    })
    df_pred_new_b.to_csv(STAGE40_DIR / "predictions" / "config_b_predictions.csv", index=False)

    df_pred_new_d = pd.DataFrame({
        "file_id": new_cache['file_ids'],
        "target_category": new_cache['categories'],
        "source_group_id": new_cache['source_groups'],
        "duration_seconds": new_cache['durations'],
        "ground_truth": new_cache['labels'],
        "logit": logits_d_new,
        "probability": probs_d_new,
        "threshold": thresh_d,
        "prediction": (probs_d_new >= thresh_d).astype(int)
    })
    df_pred_new_d.to_csv(STAGE40_DIR / "predictions" / "config_d_predictions.csv", index=False)

    # -------------------------------------------------------------
    # 2. EVALUATE ON FROZEN EXPANSION BENCHMARK SNAPSHOT (N=102)
    # -------------------------------------------------------------
    print("\n--- Evaluating on Stage 8.9.39 Frozen Expansion Benchmark (N=102) ---")
    exp_idx = np.where(splits == 'v4_reserved_expansion_test')[0]
    t_sem_exp = torch.tensor(v4_cache['X_sem'][exp_idx], dtype=torch.float32)
    t_acoust_exp = torch.tensor(v4_cache['X_acoust'][exp_idx], dtype=torch.float32)
    t_mask_exp = torch.tensor(v4_cache['mask_acoust'][exp_idx], dtype=torch.float32)
    t_sb_exp = torch.tensor(v4_cache['X_subband'][exp_idx], dtype=torch.float32)

    # Load durations from split csv
    split_csv_path = STAGE38_DIR / "manifests" / "research_split_v4.csv"
    df_split = pd.read_csv(split_csv_path)
    dur_map = {r["file_id"]: float(r["duration_seconds"]) for _, r in df_split.iterrows()}
    exp_fids = v4_cache['file_ids'][exp_idx]
    exp_durs = np.array([dur_map.get(f, 0.5) for f in exp_fids])

    _, probs_b_exp = evaluate_model_on_data(model_b, t_sem_exp, t_acoust_exp, t_mask_exp)
    _, probs_d_exp = evaluate_model_on_data(model_d, t_sem_exp, t_acoust_exp, t_mask_exp, t_sb_exp)

    metrics_b_exp = calculate_cohort_metrics(
        v4_cache['labels'][exp_idx], probs_b_exp, thresh_b,
        v4_cache['categories'][exp_idx], v4_cache['source_groups'][exp_idx], exp_durs
    )
    metrics_d_exp = calculate_cohort_metrics(
        v4_cache['labels'][exp_idx], probs_d_exp, thresh_d,
        v4_cache['categories'][exp_idx], v4_cache['source_groups'][exp_idx], exp_durs
    )

    # -------------------------------------------------------------
    # 3. EVALUATE ON HISTORICAL CONTINUITY BENCHMARK (N=293)
    # -------------------------------------------------------------
    print("\n--- Evaluating on Historical Continuity Benchmark (N=293) ---")
    hist_idx = np.where(splits == 'v4_historical_test')[0]
    t_sem_hist = torch.tensor(v4_cache['X_sem'][hist_idx], dtype=torch.float32)
    t_acoust_hist = torch.tensor(v4_cache['X_acoust'][hist_idx], dtype=torch.float32)
    t_mask_hist = torch.tensor(v4_cache['mask_acoust'][hist_idx], dtype=torch.float32)
    t_sb_hist = torch.tensor(v4_cache['X_subband'][hist_idx], dtype=torch.float32)

    hist_fids = v4_cache['file_ids'][hist_idx]
    hist_durs = np.array([dur_map.get(f, 0.5) for f in hist_fids])

    _, probs_b_hist = evaluate_model_on_data(model_b, t_sem_hist, t_acoust_hist, t_mask_hist)
    _, probs_d_hist = evaluate_model_on_data(model_d, t_sem_hist, t_acoust_hist, t_mask_hist, t_sb_hist)

    # View A: Original labels
    labels_hist_view_a = v4_cache['labels'][hist_idx].copy()
    
    # View B: Adjudicated labels (reitanna clips are non-screams)
    labels_hist_view_b = labels_hist_view_a.copy()
    for i, fid in enumerate(hist_fids):
        if fid in ["v2_nigens_242607__reitanna__gasp-oooh", "v2_nigens_242644__reitanna__another-surprised-oooh"]:
            labels_hist_view_b[i] = 0

    metrics_b_hist_a = calculate_cohort_metrics(labels_hist_view_a, probs_b_hist, thresh_b, v4_cache['categories'][hist_idx], v4_cache['source_groups'][hist_idx], hist_durs)
    metrics_b_hist_b = calculate_cohort_metrics(labels_hist_view_b, probs_b_hist, thresh_b, v4_cache['categories'][hist_idx], v4_cache['source_groups'][hist_idx], hist_durs)

    metrics_d_hist_a = calculate_cohort_metrics(labels_hist_view_a, probs_d_hist, thresh_d, v4_cache['categories'][hist_idx], v4_cache['source_groups'][hist_idx], hist_durs)
    metrics_d_hist_b = calculate_cohort_metrics(labels_hist_view_b, probs_d_hist, thresh_d, v4_cache['categories'][hist_idx], v4_cache['source_groups'][hist_idx], hist_durs)

    # -------------------------------------------------------------
    # 4. FIVE RESEARCH ACCEPTANCE GATES AUDIT
    # -------------------------------------------------------------
    # Evaluated on New Independent Cohort + Frozen Expansion Test
    # Notice: New cohort provides high-powered hard negatives (N=145, 54 shouts)
    # Frozen expansion provides high-powered short screams (N=65)
    def evaluate_gates(rec_data, hn_data, shout_data, ss_data, p95_latency):
        # Gate 1: Overall scream recall >= 96%
        g1_rec = rec_data["value"]
        g1_pass = (g1_rec >= 0.96)
        g1_stat = (g1_rec >= 0.96) and (rec_data["ci95"][0] >= 0.96)

        # Gate 2: Hard-negative FPR <= 5%
        g2_fpr = hn_data["value"]
        g2_pass = (g2_fpr <= 0.05)
        g2_stat = (g2_fpr <= 0.05) and (hn_data["ci95"][1] <= 0.05)

        # Gate 3: Shouted-speech FPR <= 15%
        g3_fpr = shout_data["fpr"]
        g3_pass = (g3_fpr <= 0.15)
        g3_stat = (g3_fpr <= 0.15) and (shout_data["ci95"][1] <= 0.15)

        # Gate 4: Short-scream recall >= 90%
        g4_rec = ss_data["recall"]
        g4_pass = (g4_rec >= 0.90)
        g4_stat = (g4_rec >= 0.90) and (ss_data["ci95"][0] >= 0.90)

        # Gate 5: P95 computational latency <= 25 ms
        g5_pass = (p95_latency <= 25.0)

        return {
            "gate_1_overall_recall": {
                "target": ">= 0.96",
                "value": g1_rec, "fraction": rec_data["fraction"], "ci95": rec_data["ci95"],
                "point_pass": g1_pass, "statistically_established": g1_stat,
                "status": "PASS" if g1_stat else ("POINT PASS — INSUFFICIENT STATISTICAL EVIDENCE" if g1_pass else "FAIL")
            },
            "gate_2_hard_negative_fpr": {
                "target": "<= 0.05",
                "value": g2_fpr, "fraction": hn_data["fraction"], "ci95": hn_data["ci95"],
                "point_pass": g2_pass, "statistically_established": g2_stat,
                "status": "PASS" if g2_stat else ("POINT PASS — INSUFFICIENT STATISTICAL EVIDENCE" if g2_pass else "FAIL")
            },
            "gate_3_shouted_speech_fpr": {
                "target": "<= 0.15",
                "value": g3_fpr, "fraction": shout_data["fraction"], "ci95": shout_data["ci95"],
                "point_pass": g3_pass, "statistically_established": g3_stat,
                "status": "PASS" if g3_stat else ("POINT PASS — INSUFFICIENT STATISTICAL EVIDENCE" if g3_pass else "FAIL")
            },
            "gate_4_short_scream_recall": {
                "target": ">= 0.90",
                "value": g4_rec, "fraction": ss_data["fraction"], "ci95": ss_data["ci95"],
                "point_pass": g4_pass, "statistically_established": g4_stat,
                "status": "PASS" if g4_stat else "FAIL"
            },
            "gate_5_p95_latency": {
                "target": "<= 25.0 ms",
                "value_ms": p95_latency,
                "status": "PASS" if g5_pass else "FAIL"
            }
        }

    # Use actual P95 latencies from Stage 8.9.39 benchmark
    latency_b = 0.516
    latency_d = 0.678

    gates_b = evaluate_gates(
        metrics_b_exp["scream_recall"],
        metrics_b_new["hard_negative_fpr"],
        metrics_b_new["category_metrics"]["shouting_and_speech"],
        metrics_b_exp["short_scream_recall"],
        latency_b
    )

    gates_d = evaluate_gates(
        metrics_d_exp["scream_recall"],
        metrics_d_new["hard_negative_fpr"],
        metrics_d_new["category_metrics"]["shouting_and_speech"],
        metrics_d_exp["short_scream_recall"],
        latency_d
    )

    # -------------------------------------------------------------
    # 5. SAVE CONSOLIDATED METRICS JSON
    # -------------------------------------------------------------
    all_results = {
        "candidate_b": {
            "name": "Configuration B (DualEncoderAcousticModel)",
            "frozen_threshold": thresh_b,
            "new_independent_cohort_n145": metrics_b_new,
            "frozen_expansion_cohort_n102": metrics_b_exp,
            "historical_cohort_n293_view_a": metrics_b_hist_a,
            "historical_cohort_n293_view_b": metrics_b_hist_b,
            "research_acceptance_gates": gates_b
        },
        "candidate_d": {
            "name": "Configuration D (MultiPathwayFusionModel)",
            "frozen_threshold": thresh_d,
            "new_independent_cohort_n145": metrics_d_new,
            "frozen_expansion_cohort_n102": metrics_d_exp,
            "historical_cohort_n293_view_a": metrics_d_hist_a,
            "historical_cohort_n293_view_b": metrics_d_hist_b,
            "research_acceptance_gates": gates_d
        }
    }

    out_metrics_path = STAGE40_DIR / "results" / "metrics" / "frozen_model_evaluation_results.json"
    with open(out_metrics_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)
    print(f"\n[Artifact] Saved consolidated evaluation metrics: {out_metrics_path}")

    print("\n" + "=" * 80)
    print("PHASE E EVALUATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    run_evaluation()
