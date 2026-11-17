#!/usr/bin/env python3
"""
STAGE 8.9.63 — Track D: Dual-Resolution Architecture Prototyping & Ablations
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import csv
import math
import sys
import time
from pathlib import Path
import numpy as np
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
# Dual-Resolution Feature Extractors
# -----------------------------------------------------------------------------
def extract_short_branch_features(audio: np.ndarray, sr: int = 16000):
    """Short-event branch: 250 ms analysis window with active region pooling."""
    n_250ms = int(0.250 * sr)  # 4000 samples
    if len(audio) < n_250ms:
        chunk = np.pad(audio, (0, n_250ms - len(audio)))
    else:
        # Find peak 250 ms energy window
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

    # Tile to 16000 samples for C5 filterbank compatibility
    tiled = np.tile(chunk, 4)[:16000]
    norm = tiled / (np.max(np.abs(tiled)) + 1e-9)
    sb_v = extract_subband_vector_c5(norm, sr=sr)
    ac_v = extract_phonation_stats_c5(norm, sr=sr)
    return np.concatenate([sb_v, ac_v])  # 17 dims

def extract_sustained_branch_features(audio: np.ndarray, sr: int = 16000):
    """Sustained-event branch: 1000 ms analysis window (C5 standard)."""
    if len(audio) >= 16000:
        c = audio[len(audio)//2 - 8000 : len(audio)//2 + 8000]
    else:
        c = np.pad(audio, (0, 16000 - len(audio)))
    norm = c / (np.max(np.abs(c)) + 1e-9)
    sb_v = extract_subband_vector_c5(norm, sr=sr)
    ac_v = extract_phonation_stats_c5(norm, sr=sr)
    return np.concatenate([sb_v, ac_v])  # 17 dims

# -----------------------------------------------------------------------------
# Dual-Resolution Neural Architecture Models
# -----------------------------------------------------------------------------
class DualResolutionModel(nn.Module):
    def __init__(self, mode="gated"):
        super().__init__()
        self.mode = mode
        # Short branch encoder
        self.short_enc = nn.Sequential(
            nn.Linear(17, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(0.10),
            nn.Linear(32, 16),
            nn.ReLU()
        )
        # Sustained branch encoder
        self.sust_enc = nn.Sequential(
            nn.Linear(17, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(0.10),
            nn.Linear(32, 16),
            nn.ReLU()
        )

        if mode == "short_only":
            self.head = nn.Linear(16, 1)
        elif mode == "sust_only":
            self.head = nn.Linear(16, 1)
        elif mode == "concat":
            self.head = nn.Sequential(
                nn.Linear(32, 16),
                nn.ReLU(),
                nn.Linear(16, 1)
            )
        elif mode == "gated":
            self.gate_net = nn.Sequential(
                nn.Linear(32, 16),
                nn.ReLU(),
                nn.Linear(16, 1),
                nn.Sigmoid()
            )
            self.head = nn.Linear(16, 1)
        elif mode == "late_fusion":
            self.head_short = nn.Linear(16, 1)
            self.head_sust = nn.Linear(16, 1)

    def forward(self, x_short, x_sust):
        if self.mode == "short_only":
            z_s = self.short_enc(x_short)
            return self.head(z_s).squeeze(-1)
        elif self.mode == "sust_only":
            z_l = self.sust_enc(x_sust)
            return self.head(z_l).squeeze(-1)
        elif self.mode == "concat":
            z_s = self.short_enc(x_short)
            z_l = self.sust_enc(x_sust)
            fused = torch.cat([z_s, z_l], dim=-1)
            return self.head(fused).squeeze(-1)
        elif self.mode == "gated":
            z_s = self.short_enc(x_short)
            z_l = self.sust_enc(x_sust)
            gate = self.gate_net(torch.cat([z_s, z_l], dim=-1))
            z_fused = gate * z_s + (1.0 - gate) * z_l
            return self.head(z_fused).squeeze(-1)
        elif self.mode == "late_fusion":
            z_s = self.short_enc(x_short)
            z_l = self.sust_enc(x_sust)
            logit_s = self.head_short(z_s).squeeze(-1)
            logit_l = self.head_sust(z_l).squeeze(-1)
            # Probability max fusion in logit space
            return torch.maximum(logit_s, logit_l)

def train_and_eval_cv(mode_name: str, X_short: np.ndarray, X_sust: np.ndarray, y_true: np.ndarray,
                      is_short: np.ndarray, is_sust: np.ndarray, is_neg: np.ndarray, is_shout: np.ndarray,
                      p95_dsp_ms: float):
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_probs = np.zeros(len(y_true))
    nn_times = []

    pos_weight = float(np.sum(y_true == 0) / np.sum(y_true == 1))
    criterion = nn.BCEWithLogitsLoss(pos_weight=torch.tensor([pos_weight]))

    for train_idx, val_idx in skf.split(X_short, y_true):
        model = DualResolutionModel(mode=mode_name)
        optimizer = optim.Adam(model.parameters(), lr=0.005, weight_decay=1e-4)

        X_s_tr = torch.tensor(X_short[train_idx], dtype=torch.float32)
        X_l_tr = torch.tensor(X_sust[train_idx], dtype=torch.float32)
        y_tr = torch.tensor(y_true[train_idx], dtype=torch.float32)

        X_s_val = torch.tensor(X_short[val_idx], dtype=torch.float32)
        X_l_val = torch.tensor(X_sust[val_idx], dtype=torch.float32)

        # Train 40 epochs
        model.train()
        for epoch in range(40):
            optimizer.zero_grad()
            logits = model(X_s_tr, X_l_tr)
            loss = criterion(logits, y_tr)
            loss.backward()
            optimizer.step()

        # Evaluate
        model.eval()
        with torch.no_grad():
            t0 = time.perf_counter()
            val_logits = model(X_s_val, X_l_val)
            nn_times.append((time.perf_counter() - t0) * 1000.0 / len(val_idx))
            val_probs = torch.sigmoid(val_logits).numpy()
            cv_probs[val_idx] = val_probs

    threshold = 0.5000
    preds = (cv_probs >= threshold).astype(int)

    n_pos = np.sum(y_true == 1)
    n_short = np.sum(is_short)
    n_sust = np.sum(is_sust)
    n_neg = np.sum(is_neg)
    n_shout = np.sum(is_shout)

    tp = np.sum((preds == 1) & (y_true == 1))
    fn = np.sum((preds == 0) & (y_true == 1))
    fp = np.sum((preds == 1) & is_neg)
    tn = np.sum((preds == 0) & is_neg)

    rec = tp / n_pos
    rec_short = np.sum((preds == 1) & is_short) / n_short
    rec_sust = np.sum((preds == 1) & is_sust) / n_sust
    fpr = fp / n_neg
    fpr_shout = np.sum((preds == 1) & is_shout) / n_shout if n_shout > 0 else 0.0
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
    roc_auc = roc_auc_score(y_true, cv_probs)
    pr_auc = average_precision_score(y_true, cv_probs)
    brier = brier_score_loss(y_true, cv_probs)

    model_p95 = float(np.percentile(nn_times, 95))
    total_p95 = p95_dsp_ms + model_p95

    return {
        "architecture_mode": mode_name,
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
        "brier_score": round(brier, 4),
        "model_only_p95_ms": round(model_p95, 3),
        "complete_pipeline_p95_ms": round(total_p95, 3)
    }

def main():
    print("=" * 80)
    print("STAGE 8.9.63 — TRACK D: ASYMMETRIC DUAL-RESOLUTION ARCHITECTURE RESEARCH")
    print("=" * 80)

    # Load 312 development recordings
    manifest_file = STAGE63_DIR / "stage_63_development_manifest.csv"
    with open(manifest_file, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"Loaded {len(rows)} recordings from Stage 63 Development Manifest.")

    X_short = []
    X_sust = []
    y_true = []
    is_short = []
    is_sust = []
    is_neg = []
    is_shout = []
    dsp_times = []

    print("Extracting Dual-Resolution Features (Short 250ms + Sustained 1000ms)...")
    for r in rows:
        audio = load_audio_wav(REPO_ROOT / r["workspace_audio_path"])
        dur = float(r["duration_seconds"])
        y = int(r["binary_label"])
        cat = r["target_category"]

        t0 = time.perf_counter()
        f_s = extract_short_branch_features(audio)
        f_l = extract_sustained_branch_features(audio)
        dsp_times.append((time.perf_counter() - t0) * 1000.0)

        X_short.append(f_s)
        X_sust.append(f_l)
        y_true.append(y)
        is_short.append(y == 1 and dur < 1.0)
        is_sust.append(y == 1 and dur >= 1.0)
        is_neg.append(y == 0)
        is_shout.append(y == 0 and cat == "shouted_speech")

    X_short = np.array(X_short)
    X_sust = np.array(X_sust)
    y_true = np.array(y_true)
    is_short = np.array(is_short)
    is_sust = np.array(is_sust)
    is_neg = np.array(is_neg)
    is_shout = np.array(is_shout)

    p95_dsp_ms = float(np.percentile(dsp_times, 95))
    print(f"Feature Extraction Completed. DSP P95 Latency: {p95_dsp_ms:.2f} ms")

    # Benchmarking the 5 configurations:
    # 1. Short-event branch alone
    # 2. Sustained-event branch alone
    # 3. Dual-resolution without fusion gating (concat)
    # 4. Dual-resolution with late probability fusion
    # 5. Dual-resolution with gated fusion
    configs = [
        ("short_only", "Short-Event Branch Alone (250 ms)"),
        ("sust_only", "Sustained-Event Branch Alone (1000 ms)"),
        ("concat", "Dual-Resolution Linear Concatenation"),
        ("late_fusion", "Dual-Resolution Late Probability Fusion"),
        ("gated", "Dual-Resolution Gated Feature Fusion")
    ]

    dual_results = []
    for mode, desc in configs:
        print(f"\nEvaluating Configuration: {desc} ({mode})...")
        res = train_and_eval_cv(mode, X_short, X_sust, y_true, is_short, is_sust, is_neg, is_shout, p95_dsp_ms)
        res["description"] = desc
        dual_results.append(res)
        print(f"  Overall Recall: {res['overall_recall']*100:.2f}% | Short: {res['short_scream_recall']*100:.2f}% | Sustained: {res['sustained_recall']*100:.2f}%")
        print(f"  Hard-Neg FPR:   {res['hard_negative_fpr']*100:.2f}% | F1: {res['f1']*100:.2f}% | ROC-AUC: {res['roc_auc']:.4f}")
        print(f"  Model P95:      {res['model_only_p95_ms']:.3f} ms | Complete Pipeline P95: {res['complete_pipeline_p95_ms']:.2f} ms")

    out_csv = STAGE63_DIR / "dual_resolution_metrics.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(dual_results[0].keys()))
        w.writeheader()
        w.writerows(dual_results)
    print(f"\nWrote dual-resolution metrics to {out_csv}")

if __name__ == "__main__":
    main()

