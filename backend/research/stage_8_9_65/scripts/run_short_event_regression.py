#!/usr/bin/env python3
"""
STAGE 8.9.65 — Track E: Short-Scream Protection & Boundary Regression
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

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE57_DIR = BACKEND_DIR / "research" / "stage_8_9_57"
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

def extract_sustained_branch_features(audio: np.ndarray, sr: int = 16000):
    if len(audio) >= 16000:
        c = audio[len(audio)//2 - 8000 : len(audio)//2 + 8000]
    else:
        c = np.pad(audio, (0, 16000 - len(audio)))
    norm = c / (np.max(np.abs(c)) + 1e-9)
    sb_v = extract_subband_vector_c5(norm, sr=sr)
    ac_v = extract_phonation_stats_c5(norm, sr=sr)
    return np.concatenate([sb_v, ac_v])

def compute_audio_acoustics(audio: np.ndarray, sr: int = 16000):
    rms = float(np.sqrt(np.mean(audio**2) + 1e-9))
    if len(audio) < int(sr * 0.025):
        return 0.0, 0.0, rms

    b, a = signal.butter(2, 70.0 / (sr / 2.0), btype='high')
    filtered = signal.filtfilt(b, a, audio)
    min_lag = int(sr / 2000.0)
    max_lag = int(sr / 80.0)
    autocorr = signal.correlate(filtered, filtered, mode='full', method='fft')
    autocorr = autocorr[len(autocorr)//2:]
    r0 = autocorr[0]
    if r0 <= 1e-9 or len(autocorr) <= max_lag:
        hnr_db = 0.0
    else:
        norm_autocorr = autocorr / r0
        lag_range = norm_autocorr[min_lag:max_lag]
        r_max = float(np.max(lag_range))
        if r_max <= 0.01:
            hnr_db = -20.0
        elif r_max >= 0.999:
            hnr_db = 30.0
        else:
            hnr_db = float(np.clip(10.0 * np.log10(r_max / (1.0 - r_max + 1e-9)), -25.0, 35.0))

    f, pxx = signal.periodogram(audio, fs=sr)
    pxx = pxx + 1e-12
    flatness = float(np.exp(np.mean(np.log(pxx))) / np.mean(pxx))
    return float(hnr_db), float(flatness), float(rms)

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

def main():
    print("=" * 80)
    print("STAGE 8.9.65 — TRACK E: SHORT-SCREAM PROTECTION & BOUNDARY REGRESSION")
    print("=" * 80)

    # 1. Load the 401 short screams from Stage 64 short manifest
    short_manifest_path = STAGE64_DIR / "stage_64_short_scream_manifest.csv"
    with open(short_manifest_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"Loaded {len(rows)} short screams from {short_manifest_path}")

    # Load frozen Stage 64 Dual-Resolution Model Checkpoint
    ckpt_path = STAGE64_DIR / "models" / "stage63_dual_resolution_gated.pt"
    model = DualResolutionGatedModel()
    model.load_state_dict(torch.load(ckpt_path, map_location="cpu", weights_only=True))
    model.eval()
    print(f"Loaded frozen Dual-Resolution model from {ckpt_path}")

    print("Extracting acoustic features and running inference on 401 short screams...")
    records = []
    durations = []

    for r in rows:
        rid = r["recording_id"]
        audio_path = REPO_ROOT / r["workspace_audio_path"]
        aud = load_audio_wav(audio_path)
        dur = float(r["duration_seconds"])

        f_s = extract_short_branch_features(aud)
        f_l = extract_sustained_branch_features(aud)
        hnr, flat, rms = compute_audio_acoustics(aud)

        with torch.no_grad():
            x_s = torch.tensor(f_s, dtype=torch.float32).unsqueeze(0)
            x_l = torch.tensor(f_l, dtype=torch.float32).unsqueeze(0)
            logits, gate = model(x_s, x_l)
            base_prob = float(torch.sigmoid(logits).item())
            gate_val = float(gate.item())

        # Baseline Prediction (threshold 0.50)
        base_pred = int(base_prob >= 0.50)

        # Variant 6 Prediction (HNR Tonal Veto + threshold 0.50)
        v6_prob = base_prob
        if hnr > 7.0 and flat < 0.008:
            v6_prob *= 0.20
        v6_pred = int(v6_prob >= 0.50)

        # Candidate 65-F Prediction (Selective Gating: high-confidence bypass, narrow-band whistle veto, threshold 0.48)
        c65f_prob = base_prob
        if base_prob < 0.80 and hnr > 12.0 and flat < 0.001:
            c65f_prob *= 0.15
        c65f_pred = int(c65f_prob >= 0.48)

        durations.append(dur)
        records.append({
            "recording_id": rid,
            "duration_seconds": dur,
            "source_group_id": r["source_group_id"],
            "base_prob": base_prob,
            "base_pred": base_pred,
            "v6_prob": v6_prob,
            "v6_pred": v6_pred,
            "c65f_prob": c65f_prob,
            "c65f_pred": c65f_pred,
            "gating_short": gate_val,
            "hnr_db": hnr,
            "spectral_flatness": flat,
            "rms_energy": rms
        })

    df = pd.DataFrame(records)
    print(f"Inference complete on {len(df)} short screams.")

    # 2. Benchmark across 7 Duration Horizons
    horizons = [
        ("H1_100ms", 0.0, 0.100),
        ("H2_200ms", 0.0, 0.200),
        ("H3_300ms", 0.0, 0.300),
        ("H4_400ms", 0.0, 0.400),
        ("H5_500ms_UltraShort", 0.0, 0.500),
        ("H6_750ms", 0.0, 0.750),
        ("H7_900ms", 0.0, 0.900),
        ("H8_1000ms_AllShort", 0.0, 1.000),
    ]

    horizon_rows = []
    print("\n" + "=" * 90)
    print(f"{'Duration Horizon':<25} {'N':<6} {'Base Recall':<15} {'V6 Recall':<15} {'65-F Recall':<15} {'Delta (65F-V6)'}")
    print("-" * 90)

    for h_name, d_min, d_max in horizons:
        sub = df[(df["duration_seconds"] >= d_min) & (df["duration_seconds"] <= d_max)]
        n = len(sub)
        if n == 0:
            continue

        base_rec = sub["base_pred"].sum() / n
        v6_rec = sub["v6_pred"].sum() / n
        c65f_rec = sub["c65f_pred"].sum() / n
        delta = c65f_rec - v6_rec

        horizon_rows.append({
            "horizon_id": h_name,
            "duration_min_sec": d_min,
            "duration_max_sec": d_max,
            "sample_count": n,
            "baseline_recall": round(float(base_rec), 4),
            "variant6_recall": round(float(v6_rec), 4),
            "candidate_65f_recall": round(float(c65f_rec), 4),
            "delta_recall_65f_minus_v6": round(float(delta), 4),
            "gate4_pass_65f": bool(c65f_rec >= 0.900)
        })

        print(f"{h_name:<25} {n:<6} {base_rec:<15.4f} {v6_rec:<15.4f} {c65f_rec:<15.4f} {delta:+15.4f}")

    # Also calculate 4 duration interval bins
    bins = [
        ("Bin_0_to_250ms", 0.0, 0.250),
        ("Bin_250_to_500ms", 0.250, 0.500),
        ("Bin_500_to_750ms", 0.500, 0.750),
        ("Bin_750_to_1000ms", 0.750, 1.000),
    ]

    print("\n" + "=" * 90)
    print(f"{'Duration Interval Bin':<25} {'N':<6} {'Base Recall':<15} {'V6 Recall':<15} {'65-F Recall':<15} {'Delta (65F-V6)'}")
    print("-" * 90)

    bin_rows = []
    for b_name, d_min, d_max in bins:
        sub = df[(df["duration_seconds"] >= d_min) & (df["duration_seconds"] <= d_max)]
        n = len(sub)
        if n == 0:
            continue

        base_rec = sub["base_pred"].sum() / n
        v6_rec = sub["v6_pred"].sum() / n
        c65f_rec = sub["c65f_pred"].sum() / n
        delta = c65f_rec - v6_rec

        bin_rows.append({
            "bin_id": b_name,
            "duration_min_sec": d_min,
            "duration_max_sec": d_max,
            "sample_count": n,
            "baseline_recall": round(float(base_rec), 4),
            "variant6_recall": round(float(v6_rec), 4),
            "candidate_65f_recall": round(float(c65f_rec), 4),
            "delta_recall_65f_minus_v6": round(float(delta), 4),
            "gate4_pass_65f": bool(c65f_rec >= 0.900)
        })

        print(f"{b_name:<25} {n:<6} {base_rec:<15.4f} {v6_rec:<15.4f} {c65f_rec:<15.4f} {delta:+15.4f}")

    out_metrics_csv = STAGE65_DIR / "short_duration_candidate_metrics.csv"
    pd.DataFrame(horizon_rows + bin_rows).to_csv(out_metrics_csv, index=False)
    print(f"\nEmitted short duration metrics to {out_metrics_csv}")

    # Save full predictions table
    full_preds_csv = STAGE65_DIR / "short_scream_cohort_predictions.csv"
    df.to_csv(full_preds_csv, index=False)
    print(f"Emitted short scream predictions to {full_preds_csv}")

if __name__ == "__main__":
    main()

