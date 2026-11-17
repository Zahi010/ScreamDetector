#!/usr/bin/env python3
"""
STAGE 8.9.64 — Track E: Harmonic-to-Noise Ratio (HNR) & Acoustic Feature Extraction
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import csv
import math
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import scipy.io.wavfile as wav
import scipy.signal as signal

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE63_DIR = BACKEND_DIR / "research" / "stage_8_9_63"
STAGE64_DIR = BACKEND_DIR / "research" / "stage_8_9_64"

def compute_hnr_autocorr(audio: np.ndarray, sr: int = 16000, fmin: float = 80.0, fmax: float = 2000.0) -> float:
    """Compute Harmonic-to-Noise Ratio (HNR) via normalized autocorrelation in dB."""
    if len(audio) < int(sr * 0.025):
        return 0.0

    # High-pass filter above 70 Hz to remove rumble
    b, a = signal.butter(2, 70.0 / (sr / 2.0), btype='high')
    filtered = signal.filtfilt(b, a, audio)

    # Frame-level autocorrelation via FFT
    min_lag = int(sr / fmax)
    max_lag = int(sr / fmin)

    autocorr = signal.correlate(filtered, filtered, mode='full', method='fft')
    autocorr = autocorr[len(autocorr)//2:]

    r0 = autocorr[0]
    if r0 <= 1e-9:
        return 0.0

    norm_autocorr = autocorr / r0
    if len(norm_autocorr) <= max_lag:
        return 0.0

    lag_range = norm_autocorr[min_lag:max_lag]
    r_max = float(np.max(lag_range))

    if r_max <= 0.01:
        return -20.0
    if r_max >= 0.999:
        return 30.0

    hnr_db = 10.0 * np.log10(r_max / (1.0 - r_max + 1e-9))
    return float(np.clip(hnr_db, -25.0, 35.0))

def compute_spectral_flatness(audio: np.ndarray, sr: int = 16000) -> float:
    """Wiener entropy: ratio of geometric mean to arithmetic mean of power spectrum."""
    f, pxx = signal.periodogram(audio, fs=sr)
    pxx = pxx + 1e-12
    geom_mean = np.exp(np.mean(np.log(pxx)))
    arith_mean = np.mean(pxx)
    return float(geom_mean / arith_mean)

def compute_spectral_flux(audio: np.ndarray, sr: int = 16000) -> float:
    """Average Euclidean distance between adjacent spectrogram frames."""
    f, t, sxx = signal.spectrogram(audio, fs=sr, nperseg=400, noverlap=200)
    if sxx.shape[1] < 2:
        return 0.0
    flux = np.mean(np.sqrt(np.sum(np.diff(sxx, axis=1)**2, axis=0)))
    return float(flux)

def compute_subharmonic_ratio(audio: np.ndarray, sr: int = 16000) -> float:
    """Ratio of subharmonic (F0/2) energy to primary fundamental energy."""
    f, pxx = signal.periodogram(audio, fs=sr)
    peak_idx = np.argmax(pxx[1:]) + 1
    f0 = f[peak_idx]

    sub_f = f0 / 2.0
    sub_idx = np.argmin(np.abs(f - sub_f))

    e_f0 = float(pxx[peak_idx])
    e_sub = float(pxx[sub_idx])

    if e_f0 <= 1e-9:
        return 0.0
    return float(np.clip(e_sub / e_f0, 0.0, 2.0))

def extract_hnr_vector(audio: np.ndarray, sr: int = 16000) -> np.ndarray:
    """Extract a 7-dimensional HNR and spectral roughness vector."""
    hnr = compute_hnr_autocorr(audio, sr)
    flatness = compute_spectral_flatness(audio, sr)
    flux = compute_spectral_flux(audio, sr)
    subharmonic = compute_subharmonic_ratio(audio, sr)

    # Voicing probability proxy based on HNR sigmoid
    voicing_prob = float(1.0 / (1.0 + np.exp(-0.25 * hnr)))

    # Pitch stability (standard deviation across 4 quartiles)
    if len(audio) >= 4 * 400:
        q_len = len(audio) // 4
        hnrs = [compute_hnr_autocorr(audio[i*q_len:(i+1)*q_len], sr) for i in range(4)]
        pitch_stability = float(np.std(hnrs))
    else:
        pitch_stability = 0.0

    harmonicity = float(np.clip((hnr + 10.0) / 30.0, 0.0, 1.0))

    return np.array([
        hnr,               # HNR in dB (-25 to +35)
        voicing_prob,      # 0 to 1
        harmonicity,       # 0 to 1
        flatness,          # 0 to 1
        flux,              # spectral flux
        pitch_stability,   # stability variance
        subharmonic        # subharmonic roughness
    ], dtype=np.float32)

def main():
    print("=" * 80)
    print("STAGE 8.9.64 — TRACK E: HNR FEATURE EXTRACTION RESEARCH")
    print("=" * 80)

    # Load Stage 63 Development Manifest to measure HNR across classes
    manifest_path = STAGE63_DIR / "stage_63_development_manifest.csv"
    with open(manifest_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    category_stats = {}
    record_rows = []

    print(f"Extracting HNR and roughness features across {len(rows)} recordings...")
    for r in rows:
        audio_path = REPO_ROOT / r["workspace_audio_path"]
        sr, aud = wav.read(audio_path)
        if aud.ndim > 1:
            aud = np.mean(aud, axis=1)
        if aud.dtype == np.int16:
            aud = aud.astype(np.float32) / 32768.0
        elif aud.dtype == np.int32:
            aud = aud.astype(np.float32) / 2147483648.0
        else:
            aud = aud.astype(np.float32)

        feat = extract_hnr_vector(aud, sr=sr)
        cat = r["target_category"] if int(r["binary_label"]) == 1 else r["subcategory"]

        if cat not in category_stats:
            category_stats[cat] = []
        category_stats[cat].append(feat)

        record_rows.append({
            "recording_id": r["recording_id"],
            "category": cat,
            "binary_label": int(r["binary_label"]),
            "hnr_db": round(float(feat[0]), 3),
            "voicing_prob": round(float(feat[1]), 4),
            "harmonicity": round(float(feat[2]), 4),
            "spectral_flatness": round(float(feat[3]), 5),
            "spectral_flux": round(float(feat[4]), 4),
            "pitch_stability_std": round(float(feat[5]), 4),
            "subharmonic_ratio": round(float(feat[6]), 4)
        })

    # Summary table across acoustic categories
    summary_metrics = []
    print("\nAcoustic Category HNR & Roughness Profile:")
    print(f"{'Category':<28} {'Clips':<6} {'Mean HNR (dB)':<15} {'Mean Flatness':<15} {'Subharmonic Ratio':<18}")
    print("-" * 80)

    for cat, vecs in sorted(category_stats.items()):
        mat = np.array(vecs)
        m_hnr = float(np.mean(mat[:, 0]))
        m_flat = float(np.mean(mat[:, 3]))
        m_sub = float(np.mean(mat[:, 6]))
        m_flux = float(np.mean(mat[:, 4]))

        summary_metrics.append({
            "category": cat,
            "sample_size": len(vecs),
            "mean_hnr_db": round(m_hnr, 2),
            "std_hnr_db": round(float(np.std(mat[:, 0])), 2),
            "mean_spectral_flatness": round(m_flat, 5),
            "mean_subharmonic_ratio": round(m_sub, 4),
            "mean_spectral_flux": round(m_flux, 4)
        })

        print(f"{cat:<28} {len(vecs):<6} {m_hnr:<15.2f} {m_flat:<15.5f} {m_sub:<18.4f}")

    out_csv = STAGE64_DIR / "hnr_feature_metrics.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summary_metrics[0].keys()))
        w.writeheader()
        w.writerows(summary_metrics)
    print(f"\nWrote category HNR summary metrics to {out_csv}")

if __name__ == "__main__":
    main()
