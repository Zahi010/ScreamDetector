#!/usr/bin/env python3
"""
STAGE 8.9.63 — Phase C1 & C2: Candidate R5 Audit & Controlled Ablation Experiments
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import csv
import math
import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
import scipy.io.wavfile as wav
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.model_selection import StratifiedKFold
import torch

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE57_DIR = BACKEND_DIR / "research" / "stage_8_9_57"
STAGE62_DIR = BACKEND_DIR / "research" / "stage_8_9_62"
STAGE63_DIR = BACKEND_DIR / "research" / "stage_8_9_63"

sys.path.insert(0, str(STAGE57_DIR / "dsp_implementations"))
from c5_combined import extract_subband_vector_c5, extract_phonation_stats_c5

def load_audio_wav(path: Path):
    sr, raw = wav.read(path)
    if raw.ndim > 1:
        raw = np.mean(raw, axis=1)
    if raw.dtype == np.int16:
        aud = raw.astype(np.float32) / 32768.0
    elif raw.dtype == np.int32:
        aud = raw.astype(np.float32) / 2147483648.0
    else:
        aud = raw.astype(np.float32)
    return aud

# -----------------------------------------------------------------------------
# Feature Extraction Variants for Ablations
# -----------------------------------------------------------------------------
def extract_r5_full_features(audio: np.ndarray, sr: int = 16000):
    """Variant 1: Full R5 with VAD-gated active region pooling."""
    frame_len = int(0.025 * sr)
    hop_len = int(0.010 * sr)
    if len(audio) < frame_len:
        audio = np.pad(audio, (0, frame_len - len(audio)))
    windows = np.lib.stride_tricks.sliding_window_view(audio, frame_len)[::hop_len]
    frame_rms = np.sqrt(np.mean(windows ** 2, axis=1) + 1e-9)
    peak_rms = np.max(frame_rms)

    active_mask = (frame_rms >= 0.10 * peak_rms) & (frame_rms > 0.01)
    if np.sum(active_mask) >= 3:
        active_indices = np.where(active_mask)[0]
        start_samp = active_indices[0] * hop_len
        end_samp = min(len(audio), (active_indices[-1] + 1) * hop_len + frame_len)
        active_audio = audio[start_samp:end_samp]
    else:
        active_audio = audio

    if len(active_audio) < 16000:
        n_repeats = int(math.ceil(16000 / max(1, len(active_audio))))
        dense_audio = np.tile(active_audio, n_repeats)[:16000]
    else:
        dense_audio = active_audio[:16000]

    norm = dense_audio / (np.max(np.abs(dense_audio)) + 1e-9)
    sb_v = extract_subband_vector_c5(norm, sr=sr)
    ac_v = extract_phonation_stats_c5(norm, sr=sr)
    return np.concatenate([sb_v, ac_v])

def extract_r5_no_vad_features(audio: np.ndarray, sr: int = 16000):
    """Variant 2: R5 without VAD (Centers highest 500ms peak, no frame thresholding)."""
    if len(audio) < 8000:
        chunk = np.pad(audio, (0, 8000 - len(audio)))
    else:
        step = 800
        best_chunk = audio[:8000]
        best_e = np.sum(best_chunk ** 2)
        for i in range(step, len(audio) - 8000 + 1, step):
            cand = audio[i:i+8000]
            e = np.sum(cand ** 2)
            if e > best_e:
                best_e = e
                best_chunk = cand
        chunk = best_chunk
    dense_audio = np.tile(chunk, 2)[:16000]
    norm = dense_audio / (np.max(np.abs(dense_audio)) + 1e-9)
    sb_v = extract_subband_vector_c5(norm, sr=sr)
    ac_v = extract_phonation_stats_c5(norm, sr=sr)
    return np.concatenate([sb_v, ac_v])

def extract_r5_no_active_pooling_features(audio: np.ndarray, sr: int = 16000):
    """Variant 3: R5 without active-region pooling (Fixed 1.0s window, zero padded)."""
    if len(audio) >= 16000:
        c = audio[len(audio)//2 - 8000 : len(audio)//2 + 8000]
    else:
        c = np.pad(audio, (0, 16000 - len(audio)))
    norm = c / (np.max(np.abs(c)) + 1e-9)
    sb_v = extract_subband_vector_c5(norm, sr=sr)
    ac_v = extract_phonation_stats_c5(norm, sr=sr)
    return np.concatenate([sb_v, ac_v])

def extract_r5_no_phonation_features(audio: np.ndarray, sr: int = 16000):
    """Variant 4: R5 without phonation branch (Subband spectral only, 11-d)."""
    full = extract_r5_full_features(audio, sr=sr)
    return full[:11]

def extract_r5_standard_c5_features(audio: np.ndarray, sr: int = 16000):
    """Variant 5: Standard fixed-window C5 features."""
    return extract_r5_no_active_pooling_features(audio, sr=sr)

def evaluate_feature_variant(name: str, extract_fn, dataset: list, y_true: np.ndarray, is_short: np.ndarray, is_sust: np.ndarray, is_neg: np.ndarray, is_shout: np.ndarray):
    X = []
    latencies = []
    for d in dataset:
        t0 = time.perf_counter()
        feat = extract_fn(d["audio"])
        latencies.append((time.perf_counter() - t0) * 1000.0)
        X.append(feat)
    X = np.array(X)

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_probs = np.zeros(len(dataset))
    cv_times = []

    for train_idx, val_idx in skf.split(X, y_true):
        clf = LogisticRegression(class_weight="balanced", max_iter=1000, C=1.0)
        clf.fit(X[train_idx], y_true[train_idx])
        t_start = time.perf_counter()
        p_val = clf.predict_proba(X[val_idx])[:, 1]
        cv_times.append((time.perf_counter() - t_start) * 1000.0 / len(val_idx))
        cv_probs[val_idx] = p_val

    threshold = 0.5000
    preds = (cv_probs >= threshold).astype(int)

    tp = np.sum((preds == 1) & (y_true == 1))
    fn = np.sum((preds == 0) & (y_true == 1))
    fp = np.sum((preds == 1) & is_neg)
    tn = np.sum((preds == 0) & is_neg)

    n_pos = np.sum(y_true == 1)
    n_short = np.sum(is_short)
    n_sust = np.sum(is_sust)
    n_neg = np.sum(is_neg)
    n_shout = np.sum(is_shout)

    rec = tp / n_pos
    rec_short = np.sum((preds == 1) & is_short) / n_short if n_short > 0 else 0.0
    rec_sust = np.sum((preds == 1) & is_sust) / n_sust if n_sust > 0 else 0.0
    fpr = fp / n_neg
    fpr_shout = np.sum((preds == 1) & is_shout) / n_shout if n_shout > 0 else 0.0
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
    roc_auc = roc_auc_score(y_true, cv_probs)
    pr_auc = average_precision_score(y_true, cv_probs)
    p95_dsp = float(np.percentile(latencies, 95))
    p95_nn = float(np.percentile(cv_times, 95))

    return {
        "variant_id": name,
        "feature_dim": X.shape[1],
        "tp": int(tp), "fn": int(fn), "fp": int(fp), "tn": int(tn),
        "overall_recall": round(rec, 4),
        "short_scream_recall": round(rec_short, 4),
        "sustained_recall": round(rec_sust, 4),
        "hard_negative_fpr": round(fpr, 4),
        "shouted_speech_fpr": round(fpr_shout, 4),
        "precision": round(prec, 4),
        "f1": round(f1, 4),
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "model_only_p95_ms": round(p95_nn, 3),
        "complete_pipeline_p95_ms": round(p95_dsp + p95_nn, 3)
    }

def main():
    print("=" * 80)
    print("STAGE 8.9.63 — TRACK C: CANDIDATE R5 AUDIT & CONTROLLED ABLATIONS")
    print("=" * 80)

    # 1. Reproduce Stage 62 R5 result on original stage 62 dev cohort (N=187)
    dev62_manifest = STAGE62_DIR / "stage_62_development_manifest.csv"
    with open(dev62_manifest, "r", encoding="utf-8") as f:
        rows62 = list(csv.DictReader(f))

    print(f"\n--- Phase C1: Reproducing Stage 62 R5 on original dev cohort (N={len(rows62)}) ---")
    data62 = []
    y62 = []
    is_short62 = []
    is_sust62 = []
    is_neg62 = []
    is_shout62 = []

    for r in rows62:
        audio = load_audio_wav(REPO_ROOT / r["workspace_audio_path"])
        dur = float(r["duration_seconds"])
        y = int(r["binary_label"])
        cat = r["target_category"]
        data62.append({"audio": audio, "duration": dur})
        y62.append(y)
        is_short62.append(y == 1 and dur < 1.0)
        is_sust62.append(y == 1 and dur >= 1.0)
        is_neg62.append(y == 0)
        is_shout62.append(y == 0 and cat == "shouted_speech")

    res_repro = evaluate_feature_variant(
        "Stage62_R5_Reproduction_Subset",
        extract_r5_full_features,
        data62, np.array(y62), np.array(is_short62), np.array(is_sust62), np.array(is_neg62), np.array(is_shout62)
    )
    print(f"Reproduction Result: Short Recall = {res_repro['short_scream_recall']*100:.2f}% (TP={int(round(res_repro['short_scream_recall']*np.sum(is_short62)))}/{np.sum(is_short62)})")
    print(f"Overall Recall = {res_repro['overall_recall']*100:.2f}%, FPR = {res_repro['hard_negative_fpr']*100:.2f}%, ROC-AUC = {res_repro['roc_auc']:.4f}")
    assert int(round(res_repro['short_scream_recall']*np.sum(is_short62))) == 6, "Expected 6/8 short screams reproduced!"
    print("SUCCESS: Exactly 6/8 short screams reproduced!")

    # 2. Run Controlled Ablations on Expanded Stage 63 Development Manifest (N=312)
    dev63_manifest = STAGE63_DIR / "stage_63_development_manifest.csv"
    with open(dev63_manifest, "r", encoding="utf-8") as f:
        rows63 = list(csv.DictReader(f))

    print(f"\n--- Phase C2: Running R5 Controlled Ablations on expanded dev cohort (N={len(rows63)}) ---")
    data63 = []
    y63 = []
    is_short63 = []
    is_sust63 = []
    is_neg63 = []
    is_shout63 = []

    for r in rows63:
        audio = load_audio_wav(REPO_ROOT / r["workspace_audio_path"])
        dur = float(r["duration_seconds"])
        y = int(r["binary_label"])
        cat = r["target_category"]
        data63.append({"audio": audio, "duration": dur})
        y63.append(y)
        is_short63.append(y == 1 and dur < 1.0)
        is_sust63.append(y == 1 and dur >= 1.0)
        is_neg63.append(y == 0)
        is_shout63.append(y == 0 and cat == "shouted_speech")

    y63 = np.array(y63)
    is_short63 = np.array(is_short63)
    is_sust63 = np.array(is_sust63)
    is_neg63 = np.array(is_neg63)
    is_shout63 = np.array(is_shout63)

    variants = [
        ("R5_Variant_1_Full_Architecture", extract_r5_full_features),
        ("R5_Variant_2_No_VAD", extract_r5_no_vad_features),
        ("R5_Variant_3_No_Active_Pooling", extract_r5_no_active_pooling_features),
        ("R5_Variant_4_No_Phonation_Branch", extract_r5_no_phonation_features),
        ("R5_Variant_5_Standard_Fixed_C5", extract_r5_standard_c5_features)
    ]

    ablation_results = []
    for vname, fn in variants:
        print(f"Evaluating {vname}...")
        res = evaluate_feature_variant(vname, fn, data63, y63, is_short63, is_sust63, is_neg63, is_shout63)
        ablation_results.append(res)
        print(f"  Short Recall: {res['short_scream_recall']*100:.2f}% | Sustained: {res['sustained_recall']*100:.2f}% | FPR: {res['hard_negative_fpr']*100:.2f}% | ROC-AUC: {res['roc_auc']:.4f}")

    out_csv = STAGE63_DIR / "r5_ablation_metrics.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(ablation_results[0].keys()))
        w.writeheader()
        w.writerows(ablation_results)
    print(f"\nWrote R5 ablation metrics to {out_csv}")

if __name__ == "__main__":
    main()
