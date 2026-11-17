#!/usr/bin/env python3
"""
STAGE 8.9.65 — Track D: Sustained-Scream Branch Enhancements & Ablations
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
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

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE57_DIR = BACKEND_DIR / "research" / "stage_8_9_57"
STAGE63_DIR = BACKEND_DIR / "research" / "stage_8_9_63"
STAGE64_DIR = BACKEND_DIR / "research" / "stage_8_9_64"
STAGE65_DIR = BACKEND_DIR / "research" / "stage_8_9_65"

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
    """Method A: Center 1000ms window."""
    if len(audio) >= 16000:
        c = audio[len(audio)//2 - 8000 : len(audio)//2 + 8000]
    else:
        c = np.pad(audio, (0, 16000 - len(audio)))
    norm = c / (np.max(np.abs(c)) + 1e-9)
    sb_v = extract_subband_vector_c5(norm, sr=sr)
    ac_v = extract_phonation_stats_c5(norm, sr=sr)
    return np.concatenate([sb_v, ac_v])

def extract_sust_multi_max(audio: np.ndarray, sr: int = 16000):
    """Method B: Multi-window 1000ms sliding extraction with element-wise max pooling."""
    win_len = 16000
    hop = 8000
    if len(audio) <= win_len:
        return extract_sust_center(audio, sr)
    feats = []
    for st in range(0, len(audio) - win_len + 1, hop):
        seg = audio[st:st + win_len]
        norm = seg / (np.max(np.abs(seg)) + 1e-9)
        sb_v = extract_subband_vector_c5(norm, sr=sr)
        ac_v = extract_phonation_stats_c5(norm, sr=sr)
        feats.append(np.concatenate([sb_v, ac_v]))
    if not feats:
        return extract_sust_center(audio, sr)
    return np.max(np.array(feats), axis=0)

def extract_sust_multi_mean(audio: np.ndarray, sr: int = 16000):
    """Method C: Multi-window 1000ms sliding extraction with element-wise mean pooling."""
    win_len = 16000
    hop = 8000
    if len(audio) <= win_len:
        return extract_sust_center(audio, sr)
    feats = []
    for st in range(0, len(audio) - win_len + 1, hop):
        seg = audio[st:st + win_len]
        norm = seg / (np.max(np.abs(seg)) + 1e-9)
        sb_v = extract_subband_vector_c5(norm, sr=sr)
        ac_v = extract_phonation_stats_c5(norm, sr=sr)
        feats.append(np.concatenate([sb_v, ac_v]))
    if not feats:
        return extract_sust_center(audio, sr)
    return np.mean(np.array(feats), axis=0)

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
        fused_in = torch.cat([z_s, z_l], dim=-1)
        gate = self.gate_net(fused_in)
        z_fused = gate * z_s + (1.0 - gate) * z_l
        logits = self.head(z_fused).squeeze(-1)
        return logits, gate.squeeze(-1)

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

def train_and_eval_architecture(arch_id: str,
                                X_short: np.ndarray,
                                X_sust: np.ndarray,
                                y_true: np.ndarray,
                                durations: np.ndarray,
                                is_shouted: np.ndarray,
                                fusion_type: str = "gated",
                                threshold: float = 0.50):
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    pos_weight = float(np.sum(y_true == 0) / np.sum(y_true == 1))
    cv_probs = np.zeros(len(y_true))

    torch.manual_seed(42)
    np.random.seed(42)

    if fusion_type == "gated":
        for fold_num, (train_idx, val_idx) in enumerate(skf.split(X_short, y_true)):
            model = DualResolutionGatedModel()
            optimizer = optim.Adam(model.parameters(), lr=0.005, weight_decay=1e-4)
            criterion = nn.BCEWithLogitsLoss(pos_weight=torch.tensor([pos_weight]))

            X_s_tr = torch.tensor(X_short[train_idx], dtype=torch.float32)
            X_l_tr = torch.tensor(X_sust[train_idx], dtype=torch.float32)
            y_tr = torch.tensor(y_true[train_idx], dtype=torch.float32)

            X_s_val = torch.tensor(X_short[val_idx], dtype=torch.float32)
            X_l_val = torch.tensor(X_sust[val_idx], dtype=torch.float32)

            model.train()
            for epoch in range(40):
                optimizer.zero_grad()
                logits, _ = model(X_s_tr, X_l_tr)
                loss = criterion(logits, y_tr)
                loss.backward()
                optimizer.step()

            model.eval()
            with torch.no_grad():
                val_logits, _ = model(X_s_val, X_l_val)
                cv_probs[val_idx] = torch.sigmoid(val_logits).numpy()

    elif fusion_type in ("confidence_soft_or", "confidence_max"):
        for fold_num, (train_idx, val_idx) in enumerate(skf.split(X_short, y_true)):
            model = DualBranchIndependentHeadsModel()
            optimizer = optim.Adam(model.parameters(), lr=0.005, weight_decay=1e-4)
            criterion = nn.BCEWithLogitsLoss(pos_weight=torch.tensor([pos_weight]))

            X_s_tr = torch.tensor(X_short[train_idx], dtype=torch.float32)
            X_l_tr = torch.tensor(X_sust[train_idx], dtype=torch.float32)
            y_tr = torch.tensor(y_true[train_idx], dtype=torch.float32)

            X_s_val = torch.tensor(X_short[val_idx], dtype=torch.float32)
            X_l_val = torch.tensor(X_sust[val_idx], dtype=torch.float32)

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

                if fusion_type == "confidence_soft_or":
                    cv_probs[val_idx] = 1.0 - (1.0 - p_s) * (1.0 - p_l)
                elif fusion_type == "confidence_max":
                    cv_probs[val_idx] = np.maximum(p_s, p_l)

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
    short_rec = int(np.sum((preds == 1) & short_mask)) / int(np.sum(short_mask))

    ultra_mask = (y_true == 1) & (durations <= 0.50)
    ultra_rec = int(np.sum((preds == 1) & ultra_mask)) / int(np.sum(ultra_mask))

    sust_mask = (y_true == 1) & (durations >= 1.00)
    sust_rec = int(np.sum((preds == 1) & sust_mask)) / int(np.sum(sust_mask))

    shouted_fpr = int(np.sum((preds == 1) & is_shouted)) / int(np.sum(is_shouted))

    roc_auc = float(roc_auc_score(y_true, cv_probs))
    pr_auc = float(average_precision_score(y_true, cv_probs))

    return {
        "architecture_id": arch_id,
        "fusion_type": fusion_type,
        "threshold": threshold,
        "overall_recall": round(rec, 4),
        "fpr_dev": round(fpr, 4),
        "shouted_speech_fpr": round(shouted_fpr, 4),
        "short_scream_recall": round(short_rec, 4),
        "ultra_short_recall": round(ultra_rec, 4),
        "sustained_recall": round(sust_rec, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "gate1_pass": rec >= 0.960,
        "gate2_pass": fpr <= 0.050,
        "gate3_pass": shouted_fpr <= 0.150,
        "gate4_pass": short_rec >= 0.900,
    }

def main():
    print("=" * 80)
    print("STAGE 8.9.65 — TRACK D: SUSTAINED-SCREAM BRANCH ENHANCEMENTS & ABLATIONS")
    print("=" * 80)

    dev_manifest_path = STAGE63_DIR / "stage_63_development_manifest.csv"
    with open(dev_manifest_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"Loaded {len(rows)} recordings from Development Manifest.")

    X_short = []
    X_sust_center = []
    X_sust_max = []
    X_sust_mean = []
    y_true = []
    durations = []
    is_shouted = []

    shouted_outcry_ids = {"s60_rec_0054", "s60_rec_0100", "s60_rec_0231", "s60_rec_0236", "s60_rec_0332"}

    print("Pre-extracting short, center-sustained, multi-window-max, and multi-window-mean features...")
    for r in rows:
        rid = r["recording_id"]
        aud = load_audio_wav(REPO_ROOT / r["workspace_audio_path"])
        f_s = extract_short_branch_features(aud)
        f_l_center = extract_sust_center(aud)
        f_l_max = extract_sust_multi_max(aud)
        f_l_mean = extract_sust_multi_mean(aud)

        lbl = int(r["binary_label"])
        dur = float(r["duration_seconds"])

        X_short.append(f_s)
        X_sust_center.append(f_l_center)
        X_sust_max.append(f_l_max)
        X_sust_mean.append(f_l_mean)
        y_true.append(lbl)
        durations.append(dur)
        is_shouted.append(lbl == 0 and rid in shouted_outcry_ids)

    X_short = np.array(X_short, dtype=np.float32)
    X_sust_center = np.array(X_sust_center, dtype=np.float32)
    X_sust_max = np.array(X_sust_max, dtype=np.float32)
    X_sust_mean = np.array(X_sust_mean, dtype=np.float32)
    y_true = np.array(y_true, dtype=np.int64)
    durations = np.array(durations, dtype=np.float32)
    is_shouted = np.array(is_shouted)

    experiments = [
        ("Sust_A_Center_Window_Gated", X_short, X_sust_center, "gated", 0.50),
        ("Sust_B_MultiWindow_Max_Gated", X_short, X_sust_max, "gated", 0.50),
        ("Sust_C_MultiWindow_Mean_Gated", X_short, X_sust_mean, "gated", 0.50),
        ("Sust_D_Center_Window_Confidence_Or", X_short, X_sust_center, "confidence_soft_or", 0.50),
        ("Sust_E_MultiWindow_Max_Confidence_Max", X_short, X_sust_max, "confidence_max", 0.50),
        ("Sust_F_MultiWindow_Max_Confidence_Or", X_short, X_sust_max, "confidence_soft_or", 0.50),
    ]

    results = []
    print("\n" + "=" * 100)
    print(f"{'Experiment':<40} {'Recall':<8} {'FPR':<8} {'SustRec':<9} {'ShortRec':<10} {'F1':<8} {'PR-AUC':<8}")
    print("-" * 100)

    for eid, xs, xl, f_type, th in experiments:
        m = train_and_eval_architecture(
            arch_id=eid,
            X_short=xs,
            X_sust=xl,
            y_true=y_true,
            durations=durations,
            is_shouted=is_shouted,
            fusion_type=f_type,
            threshold=th
        )
        results.append(m)
        print(f"{m['architecture_id']:<40} {m['overall_recall']:<8.4f} {m['fpr_dev']:<8.4f} {m['sustained_recall']:<9.4f} {m['short_scream_recall']:<10.4f} {m['f1_score']:<8.4f} {m['pr_auc']:<8.4f}")

    out_csv = STAGE65_DIR / "sustained_branch_ablation.csv"
    pd.DataFrame(results).to_csv(out_csv, index=False)
    print(f"\nEmitted sustained branch ablation metrics to {out_csv}")

if __name__ == "__main__":
    main()

