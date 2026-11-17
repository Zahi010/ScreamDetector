#!/usr/bin/env python3
"""
STAGE 8.9.64 — Track B: Dual-Resolution Reproduction Script
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import csv
import json
import math
import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
import scipy.io.wavfile as wav
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from sklearn.model_selection import StratifiedKFold

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE57_DIR = BACKEND_DIR / "research" / "stage_8_9_57"
STAGE63_DIR = BACKEND_DIR / "research" / "stage_8_9_63"
STAGE64_DIR = BACKEND_DIR / "research" / "stage_8_9_64"

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
    n_250ms = int(0.250 * sr)  # 4000 samples
    if len(audio) < n_250ms:
        chunk = np.pad(audio, (0, n_250ms - len(audio)))
    else:
        frame_len = 400  # 25 ms
        hop_len = 160    # 10 ms
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
    return np.concatenate([sb_v, ac_v])  # 17 dims

def extract_sustained_branch_features(audio: np.ndarray, sr: int = 16000):
    if len(audio) >= 16000:
        c = audio[len(audio)//2 - 8000 : len(audio)//2 + 8000]
    else:
        c = np.pad(audio, (0, 16000 - len(audio)))
    norm = c / (np.max(np.abs(c)) + 1e-9)
    sb_v = extract_subband_vector_c5(norm, sr=sr)
    ac_v = extract_phonation_stats_c5(norm, sr=sr)
    return np.concatenate([sb_v, ac_v])  # 17 dims

class DualResolutionGatedModel(nn.Module):
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
        self.gate_net = nn.Sequential(
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )
        self.head = nn.Linear(16, 1)

    def forward(self, x_short, x_sust):
        z_s = self.short_enc(x_short)
        z_l = self.sust_enc(x_sust)
        gate = self.gate_net(torch.cat([z_s, z_l], dim=-1))
        z_fused = gate * z_s + (1.0 - gate) * z_l
        return self.head(z_fused).squeeze(-1)

    def forward_with_gate(self, x_short, x_sust):
        z_s = self.short_enc(x_short)
        z_l = self.sust_enc(x_sust)
        gate = self.gate_net(torch.cat([z_s, z_l], dim=-1))
        z_fused = gate * z_s + (1.0 - gate) * z_l
        logits = self.head(z_fused).squeeze(-1)
        return logits, gate.squeeze(-1)

def main():
    print("=" * 80)
    print("STAGE 8.9.64 — TRACK B: DUAL-RESOLUTION RESULT REPRODUCTION")
    print("=" * 80)

    torch.manual_seed(42)
    np.random.seed(42)

    manifest_file = STAGE63_DIR / "stage_63_development_manifest.csv"
    with open(manifest_file, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"Loaded {len(rows)} recordings from Stage 8.9.63 Development Manifest.")

    X_short = []
    X_sust = []
    y_true = []
    durations = []
    is_short_orig = []
    is_ultra_short = []
    is_sustained = []
    is_hard_neg = []
    is_shouted = []

    print("Extracting features across all 312 recordings...")
    for r in rows:
        audio = load_audio_wav(REPO_ROOT / r["workspace_audio_path"])
        dur = float(r["duration_seconds"])
        y = int(r["binary_label"])
        cat = r["target_category"]

        f_s = extract_short_branch_features(audio)
        f_l = extract_sustained_branch_features(audio)

        X_short.append(f_s)
        X_sust.append(f_l)
        y_true.append(y)
        durations.append(dur)
        is_short_orig.append(y == 1 and dur < 1.0)
        is_ultra_short.append(y == 1 and dur <= 0.50)
        is_sustained.append(y == 1 and dur >= 1.0)
        is_hard_neg.append(y == 0)
        is_shouted.append(y == 0 and cat == "shouted_speech")

    X_short = np.array(X_short)
    X_sust = np.array(X_sust)
    y_true = np.array(y_true)
    durations = np.array(durations)
    is_short_orig = np.array(is_short_orig)
    is_ultra_short = np.array(is_ultra_short)
    is_sustained = np.array(is_sustained)
    is_hard_neg = np.array(is_hard_neg)
    is_shouted = np.array(is_shouted)

    print(f"Dataset Breakdown:")
    print(f"  Total Positives:              {np.sum(y_true == 1)}")
    print(f"  Original Short (<1.0s):       {np.sum(is_short_orig)}")
    print(f"  Ultra-Short (<=0.50s):        {np.sum(is_ultra_short)}")
    print(f"  Sustained Screams (>=1.0s):   {np.sum(is_sustained)}")
    print(f"  Hard Negatives:               {np.sum(is_hard_neg)}")
    print(f"  Shouted Speech Negatives:     {np.sum(is_shouted)}")

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_probs = np.zeros(len(y_true))
    cv_gates = np.zeros(len(y_true))
    fold_assignments = np.zeros(len(y_true), dtype=int)

    pos_weight = float(np.sum(y_true == 0) / np.sum(y_true == 1))
    criterion = nn.BCEWithLogitsLoss(pos_weight=torch.tensor([pos_weight]))

    best_model_fold0 = None

    for fold_num, (train_idx, val_idx) in enumerate(skf.split(X_short, y_true)):
        fold_assignments[val_idx] = fold_num
        model = DualResolutionGatedModel()
        optimizer = optim.Adam(model.parameters(), lr=0.005, weight_decay=1e-4)

        X_s_tr = torch.tensor(X_short[train_idx], dtype=torch.float32)
        X_l_tr = torch.tensor(X_sust[train_idx], dtype=torch.float32)
        y_tr = torch.tensor(y_true[train_idx], dtype=torch.float32)

        X_s_val = torch.tensor(X_short[val_idx], dtype=torch.float32)
        X_l_val = torch.tensor(X_sust[val_idx], dtype=torch.float32)

        model.train()
        for epoch in range(40):
            optimizer.zero_grad()
            logits = model(X_s_tr, X_l_tr)
            loss = criterion(logits, y_tr)
            loss.backward()
            optimizer.step()

        model.eval()
        with torch.no_grad():
            val_logits, val_gates = model.forward_with_gate(X_s_val, X_l_val)
            val_probs = torch.sigmoid(val_logits).numpy()
            cv_probs[val_idx] = val_probs
            cv_gates[val_idx] = val_gates.numpy()

        if fold_num == 0:
            best_model_fold0 = model

    # Save frozen checkpoint of the full architecture
    model_save_path = STAGE64_DIR / "models" / "stage63_dual_resolution_gated.pt"
    torch.save(best_model_fold0.state_dict(), model_save_path)
    print(f"\nSaved dual-resolution checkpoint to {model_save_path}")

    # Calculate metrics at threshold = 0.5000
    threshold = 0.5000
    preds = (cv_probs >= threshold).astype(int)

    tp = int(np.sum((preds == 1) & (y_true == 1)))
    fn = int(np.sum((preds == 0) & (y_true == 1)))
    fp = int(np.sum((preds == 1) & is_hard_neg))
    tn = int(np.sum((preds == 0) & is_hard_neg))

    rec = tp / np.sum(y_true == 1)
    rec_short_orig = np.sum((preds == 1) & is_short_orig) / np.sum(is_short_orig)
    rec_ultra_short = np.sum((preds == 1) & is_ultra_short) / np.sum(is_ultra_short)
    rec_sust = np.sum((preds == 1) & is_sustained) / np.sum(is_sustained)
    fpr_hard_neg = fp / np.sum(is_hard_neg)
    fpr_shouted = np.sum((preds == 1) & is_shouted) / np.sum(is_shouted) if np.sum(is_shouted) > 0 else 0.0
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
    roc_auc = roc_auc_score(y_true, cv_probs)
    pr_auc = average_precision_score(y_true, cv_probs)
    brier = brier_score_loss(y_true, cv_probs)

    print("\n" + "=" * 80)
    print("REPRODUCED DUAL-RESOLUTION CROSS-VALIDATION RESULTS:")
    print("=" * 80)
    print(f"  Confusion Matrix:        TP={tp}, FN={fn}, FP={fp}, TN={tn}")
    print(f"  Gate 1: Overall Recall:  {rec*100:.2f}% ({tp}/{np.sum(y_true == 1)}) [Threshold >= 96.00%]")
    print(f"  Gate 2: Hard-Neg FPR:    {fpr_hard_neg*100:.2f}% ({fp}/{np.sum(is_hard_neg)}) [Threshold <= 5.00%]")
    print(f"  Gate 3: Shouted FPR:     {fpr_shouted*100:.2f}% ({np.sum((preds == 1) & is_shouted)}/{np.sum(is_shouted)}) [Threshold <= 15.00%]")
    print(f"  Gate 4: Short (<1.0s):   {rec_short_orig*100:.2f}% ({np.sum((preds == 1) & is_short_orig)}/{np.sum(is_short_orig)}) [Threshold >= 90.00%]")
    print(f"  Ultra-Short (<=0.50s):   {rec_ultra_short*100:.2f}% ({np.sum((preds == 1) & is_ultra_short)}/{np.sum(is_ultra_short)}) [Diagnostic]")
    print(f"  Sustained Recall:        {rec_sust*100:.2f}% ({np.sum((preds == 1) & is_sustained)}/{np.sum(is_sustained)})")
    print(f"  Precision:               {prec*100:.2f}%")
    print(f"  F1 Score:                {f1*100:.2f}%")
    print(f"  ROC-AUC:                 {roc_auc:.4f}")
    print(f"  PR-AUC:                  {pr_auc:.4f}")
    print(f"  Brier Score:             {brier:.4f}")
    print("=" * 80)

    # Save per-recording reproduction predictions
    pred_records = []
    for i, r in enumerate(rows):
        pred_records.append({
            "recording_id": r["recording_id"],
            "source_group_id": r["source_group_id"],
            "target_category": r["target_category"],
            "subcategory": r["subcategory"],
            "duration_seconds": float(r["duration_seconds"]),
            "binary_label": int(r["binary_label"]),
            "is_short_orig": int(is_short_orig[i]),
            "is_ultra_short": int(is_ultra_short[i]),
            "is_sustained": int(is_sustained[i]),
            "is_hard_neg": int(is_hard_neg[i]),
            "is_shouted": int(is_shouted[i]),
            "fold": int(fold_assignments[i]),
            "predicted_probability": round(float(cv_probs[i]), 5),
            "predicted_label": int(preds[i]),
            "gating_weight_short": round(float(cv_gates[i]), 5),
            "is_correct": int(preds[i] == int(r["binary_label"]))
        })

    out_csv = STAGE64_DIR / "dual_resolution_reproduction.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(pred_records[0].keys()))
        writer.writeheader()
        writer.writerows(pred_records)
    print(f"Wrote {len(pred_records)} prediction records to {out_csv}")

if __name__ == "__main__":
    main()

