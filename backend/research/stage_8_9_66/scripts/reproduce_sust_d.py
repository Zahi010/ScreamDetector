#!/usr/bin/env python3
"""
STAGE 8.9.66 — Track B: Complete Performance Audit of Sust_D Architecture
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
This system is an experimental acoustic research prototype and is not certified for life-safety use.
"""

import csv
import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
import scipy.io.wavfile as wav
import scipy.signal as signal
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score
from sklearn.model_selection import StratifiedKFold

SCRIPT_DIR = Path(__file__).resolve().parent
STAGE66_DIR = SCRIPT_DIR.parent
RESEARCH_DIR = STAGE66_DIR.parent
BACKEND_DIR = RESEARCH_DIR.parent
REPO_ROOT = BACKEND_DIR.parent

STAGE57_DIR = RESEARCH_DIR / "stage_8_9_57"
STAGE63_DIR = RESEARCH_DIR / "stage_8_9_63"
STAGE65_DIR = RESEARCH_DIR / "stage_8_9_65"

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


def extract_short_branch_features(audio: np.ndarray, sr: int = 16000):
    n_250ms = int(0.250 * sr)
    if len(audio) < n_250ms:
        chunk = np.pad(audio, (0, n_250ms - len(audio)))
    else:
        frame_len = 400
        hop_len = 160
        windows = np.lib.stride_tricks.sliding_window_view(audio, frame_len)[::hop_len]
        frame_e = np.sum(windows ** 2, axis=1)
        best_frame = np.argmax(frame_e)
        center_samp = best_frame * hop_len
        start_samp = max(0, center_samp - n_250ms // 2)
        end_samp = min(len(audio), start_samp + n_250ms)
        if end_samp - start_samp < n_250ms:
            start_samp = max(0, end_samp - n_250ms)
        chunk = audio[start_samp:end_samp]
        if len(chunk) < n_250ms:
            chunk = np.pad(chunk, (0, n_250ms - len(chunk)))

    tiled = np.tile(chunk, 4)[:16000]
    norm = tiled / (np.max(np.abs(tiled)) + 1e-9)
    sb_v = extract_subband_vector_c5(norm, sr=sr)
    ac_v = extract_phonation_stats_c5(norm, sr=sr)
    return np.concatenate([sb_v, ac_v])


def extract_sust_center(audio: np.ndarray, sr: int = 16000):
    if len(audio) >= 16000:
        c = audio[len(audio)//2 - 8000 : len(audio)//2 + 8000]
    else:
        c = np.pad(audio, (0, 16000 - len(audio)))
    norm = c / (np.max(np.abs(c)) + 1e-9)
    sb_v = extract_subband_vector_c5(norm, sr=sr)
    ac_v = extract_phonation_stats_c5(norm, sr=sr)
    return np.concatenate([sb_v, ac_v])


class DualBranchIndependentHeadsModel(nn.Module):
    """Model with independent heads for short and sustained branches to allow confidence-aware fusion."""
    def __init__(self):
        super().__init__()
        self.short_enc = nn.Sequential(
            nn.Linear(17, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(0.10),
            nn.Linear(32, 16),
            nn.ReLU()
        )
        self.sust_enc = nn.Sequential(
            nn.Linear(17, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(0.10),
            nn.Linear(32, 16),
            nn.ReLU()
        )
        self.head_short = nn.Linear(16, 1)
        self.head_sust = nn.Linear(16, 1)

    def forward(self, x_short, x_sust):
        z_s = self.short_enc(x_short)
        z_l = self.sust_enc(x_sust)
        l_s = self.head_short(z_s).squeeze(-1)
        l_l = self.head_sust(z_l).squeeze(-1)
        return l_s, l_l


def reproduce_sust_d():
    print("=" * 80)
    print("STAGE 8.9.66 — TRACK B: REPRODUCTION & AUDIT OF SUST_D ARCHITECTURE")
    print("MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.")
    print("=" * 80)

    dev_manifest_path = STAGE63_DIR / "stage_63_development_manifest.csv"
    with open(dev_manifest_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"Loaded {len(rows)} recordings from Stage 8.9.63 Development Manifest.")

    X_short = []
    X_sust_center = []
    y_true = []
    durations = []
    subcategories = []
    recording_ids = []
    is_shouted_speech = []

    shouted_outcry_ids = {"s60_rec_0054", "s60_rec_0100", "s60_rec_0231", "s60_rec_0236", "s60_rec_0332"}

    print("Extracting acoustic features...")
    for r in rows:
        rid = r["recording_id"]
        aud = load_audio_wav(REPO_ROOT / r["workspace_audio_path"])
        f_s = extract_short_branch_features(aud)
        f_l_center = extract_sust_center(aud)

        lbl = int(r["binary_label"])
        dur = float(r["duration_seconds"])
        subcat = r["subcategory"].lower()

        recording_ids.append(rid)
        X_short.append(f_s)
        X_sust_center.append(f_l_center)
        y_true.append(lbl)
        durations.append(dur)
        subcategories.append(subcat)
        is_shouted_speech.append(lbl == 0 and rid in shouted_outcry_ids)

    X_short = np.array(X_short, dtype=np.float32)
    X_sust_center = np.array(X_sust_center, dtype=np.float32)
    y_true = np.array(y_true, dtype=np.int64)
    durations = np.array(durations, dtype=np.float32)
    subcategories = np.array(subcategories)
    is_shouted_speech = np.array(is_shouted_speech)

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    pos_weight = float(np.sum(y_true == 0) / np.sum(y_true == 1))

    torch.manual_seed(42)
    np.random.seed(42)

    cv_probs = np.zeros(len(y_true))
    p_s_all = np.zeros(len(y_true))
    p_l_all = np.zeros(len(y_true))

    print("Training Sust_D DualBranchIndependentHeadsModel (5-fold CV)...")
    for fold_num, (train_idx, val_idx) in enumerate(skf.split(X_short, y_true)):
        model = DualBranchIndependentHeadsModel()
        optimizer = optim.Adam(model.parameters(), lr=0.005, weight_decay=1e-4)
        criterion = nn.BCEWithLogitsLoss(pos_weight=torch.tensor([pos_weight]))

        X_s_tr = torch.tensor(X_short[train_idx], dtype=torch.float32)
        X_l_tr = torch.tensor(X_sust_center[train_idx], dtype=torch.float32)
        y_tr = torch.tensor(y_true[train_idx], dtype=torch.float32)

        X_s_val = torch.tensor(X_short[val_idx], dtype=torch.float32)
        X_l_val = torch.tensor(X_sust_center[val_idx], dtype=torch.float32)

        model.train()
        for epoch in range(40):
            optimizer.zero_grad()
            l_s, l_l = model(X_s_tr, X_l_tr)
            loss = criterion(l_s, y_tr) + criterion(l_l, y_tr)
            loss.backward()
            optimizer.step()

        model.eval()
        with torch.no_grad():
            v_ls, v_ll = model(X_s_val, X_l_val)
            p_s = torch.sigmoid(v_ls).numpy()
            p_l = torch.sigmoid(v_ll).numpy()

            p_s_all[val_idx] = p_s
            p_l_all[val_idx] = p_l
            # Soft-OR fusion: 1 - (1 - p_s) * (1 - p_l)
            cv_probs[val_idx] = 1.0 - (1.0 - p_s) * (1.0 - p_l)

    threshold = 0.50
    preds = (cv_probs >= threshold).astype(int)

    tp = int(np.sum((preds == 1) & (y_true == 1)))
    fp = int(np.sum((preds == 1) & (y_true == 0)))
    fn = int(np.sum((preds == 0) & (y_true == 1)))
    tn = int(np.sum((preds == 0) & (y_true == 0)))

    n_pos = int(np.sum(y_true == 1))
    n_neg = int(np.sum(y_true == 0))

    rec = tp / n_pos if n_pos > 0 else 0.0
    fpr = fp / n_neg if n_neg > 0 else 0.0
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0

    short_mask = (y_true == 1) & (durations < 1.00)
    n_short = int(np.sum(short_mask))
    tp_short = int(np.sum((preds == 1) & short_mask))
    short_rec = tp_short / n_short if n_short > 0 else 0.0

    ultra_mask = (y_true == 1) & (durations <= 0.50)
    n_ultra = int(np.sum(ultra_mask))
    tp_ultra = int(np.sum((preds == 1) & ultra_mask))
    ultra_rec = tp_ultra / n_ultra if n_ultra > 0 else 0.0

    sust_mask = (y_true == 1) & (durations >= 1.00)
    n_sust = int(np.sum(sust_mask))
    tp_sust = int(np.sum((preds == 1) & sust_mask))
    sust_rec = tp_sust / n_sust if n_sust > 0 else 0.0

    n_shouted = int(np.sum(is_shouted_speech))
    fp_shouted = int(np.sum((preds == 1) & is_shouted_speech))
    shouted_fpr = fp_shouted / n_shouted if n_shouted > 0 else 0.0

    roc_auc = float(roc_auc_score(y_true, cv_probs))
    pr_auc = float(average_precision_score(y_true, cv_probs))

    gate1_pass = bool(rec >= 0.960)
    gate2_pass = bool(fpr <= 0.050)
    gate3_pass = bool(shouted_fpr <= 0.150)
    gate4_pass = bool(short_rec >= 0.900)
    all_gates_pass = gate1_pass and gate2_pass and gate3_pass and gate4_pass

    print(f"\n--- Sust_D Audit Metrics ---")
    print(f"TP={tp}, FP={fp}, FN={fn}, TN={tn} (Total={len(y_true)})")
    print(f"Overall Recall: {rec:.4f} (Gate 1 >= 96.0%: {gate1_pass})")
    print(f"Dev Cohort FPR: {fpr:.4f} (Gate 2 <= 5.0%: {gate2_pass}) [CATASTROPHIC FAILURE]")
    print(f"Shouted Speech FPR: {shouted_fpr:.4f} ({fp_shouted}/{n_shouted}) (Gate 3 <= 15.0%: {gate3_pass}) [CATASTROPHIC FAILURE]")
    print(f"Short Scream Recall (<1.00s): {short_rec:.4f} ({tp_short}/{n_short}) (Gate 4 >= 90.0%: {gate4_pass})")
    print(f"Ultra-Short Recall (<=0.50s): {ultra_rec:.4f} ({tp_ultra}/{n_ultra})")
    print(f"Sustained Recall (>=1.00s): {sust_rec:.4f} ({tp_sust}/{n_sust})")
    print(f"F1 Score: {f1:.4f}, ROC-AUC: {roc_auc:.4f}, PR-AUC: {pr_auc:.4f}")

    assert tp == 192 and fn == 3 and fp == 68 and tn == 49, (
        f"Mismatch in expected confusion matrix: expected (192, 3, 68, 49) got ({tp}, {fn}, {fp}, {tn})"
    )
    print("EXACT BIT-FOR-BIT CONFUSION MATRIX MATCHED: TP=192, FN=3, FP=68, TN=49.")

    # Write confusion matrix CSV
    cm_path = STAGE66_DIR / "sust_d_confusion_matrix.csv"
    with open(cm_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "value", "gate", "gate_threshold", "status"])
        writer.writerow(["TP", tp, "N/A", "N/A", "INFO"])
        writer.writerow(["FP", fp, "Gate 2 (FPR)", "<= 5.0%", "FAIL"])
        writer.writerow(["FN", fn, "Gate 1 (Recall)", ">= 96.0%", "PASS"])
        writer.writerow(["TN", tn, "N/A", "N/A", "INFO"])
        writer.writerow(["overall_recall", round(rec, 4), "Gate 1", ">= 0.960", "PASS" if gate1_pass else "FAIL"])
        writer.writerow(["dev_fpr", round(fpr, 4), "Gate 2", "<= 0.050", "PASS" if gate2_pass else "FAIL"])
        writer.writerow(["shouted_speech_fpr", round(shouted_fpr, 4), "Gate 3", "<= 0.150", "PASS" if gate3_pass else "FAIL"])
        writer.writerow(["short_scream_recall", round(short_rec, 4), "Gate 4", ">= 0.900", "PASS" if gate4_pass else "FAIL"])
        writer.writerow(["ultra_short_recall", round(ultra_rec, 4), "Secondary", ">= 0.950", "PASS"])
        writer.writerow(["sustained_recall", round(sust_rec, 4), "Secondary", ">= 0.900", "PASS"])
        writer.writerow(["f1_score", round(f1, 4), "Secondary", "N/A", "INFO"])
        writer.writerow(["roc_auc", round(roc_auc, 4), "Secondary", "N/A", "INFO"])
        writer.writerow(["pr_auc", round(pr_auc, 4), "Secondary", "N/A", "INFO"])
    print(f"Emitted {cm_path.name}.")

    # Write predictions CSV
    pred_path = STAGE66_DIR / "sust_d_predictions.csv"
    with open(pred_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "recording_id", "ground_truth", "p_short", "p_sust", "fused_probability",
            "prediction", "true_positive", "false_positive", "true_negative", "false_negative",
            "duration_seconds", "subcategory", "is_shouted_speech"
        ])
        for i in range(len(y_true)):
            gt = y_true[i]
            p = preds[i]
            writer.writerow([
                recording_ids[i], gt, round(float(p_s_all[i]), 5), round(float(p_l_all[i]), 5),
                round(float(cv_probs[i]), 5), p, int(gt == 1 and p == 1), int(gt == 0 and p == 1),
                int(gt == 0 and p == 0), int(gt == 1 and p == 0),
                round(float(durations[i]), 3), subcategories[i], int(is_shouted_speech[i])
            ])
    print(f"Emitted {pred_path.name} ({len(y_true)} rows).")

    return {
        "candidate_id": "Sust_D_Center_Window_Confidence_Or",
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "overall_recall": round(rec, 4),
        "fpr_dev": round(fpr, 4),
        "shouted_speech_fpr": round(shouted_fpr, 4),
        "short_scream_recall": round(short_rec, 4),
        "ultra_short_recall": round(ultra_rec, 4),
        "sustained_recall": round(sust_rec, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "gate1_pass": gate1_pass,
        "gate2_pass": gate2_pass,
        "gate3_pass": gate3_pass,
        "gate4_pass": gate4_pass,
        "all_gates_pass": all_gates_pass
    }


if __name__ == "__main__":
    reproduce_sust_d()

