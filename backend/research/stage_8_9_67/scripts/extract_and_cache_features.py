# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
STAGE 8.9.67 — Feature Extraction and Dataset Cache Engine
Extracts C5 DSP features and novel vocal discriminability features (Roughness, HF-ratio, Flux)
for Stage 54 train (N=1055) and val (N=311) partitions, and Stage 64 held-out short screams (N=268).

MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import sys
import time
from pathlib import Path
import pandas as pd
import numpy as np
import scipy.signal as signal

REPO_ROOT = Path(__file__).resolve().parents[4]
STAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "backend/research/stage_8_9_57/dsp_implementations"))
sys.path.insert(0, str(REPO_ROOT / "backend/research/stage_8_9_66/scripts"))

from reproduce_candidate_65f import (
    extract_short_branch_features,
    extract_sustained_branch_features,
    compute_audio_acoustics,
    load_audio_wav,
)


def extract_vocal_acoustic_features(audio: np.ndarray, sr: int = 16000) -> np.ndarray:
    """Extract 4 specialized non-linear & spectral vocal discriminability features:
    1. Auditory Roughness (Modulation power in 30-150 Hz envelope)
    2. High-Frequency Concentration Ratio (Energy in 2.5-7.5 kHz vs 0.3-2.5 kHz)
    3. Spectral Flux (Frame-to-frame spectral energy variability)
    4. Subharmonic Energy Ratio (Energy in half-integer harmonics vs integer harmonics)
    """
    # 1. Auditory Roughness
    if len(audio) >= 512:
        analytic = signal.hilbert(audio)
        envelope = np.abs(analytic)
        env_dc_removed = envelope - np.mean(envelope)
        f_env, pxx_env = signal.welch(env_dc_removed, fs=sr, nperseg=min(len(audio), 2048))
        roughness_band = (f_env >= 30.0) & (f_env <= 150.0)
        total_env_power = np.sum(pxx_env) + 1e-9
        roughness = float(np.sum(pxx_env[roughness_band]) / total_env_power)
    else:
        roughness = 0.0

    # 2. High-Frequency Concentration Ratio
    f, pxx = signal.periodogram(audio, fs=sr)
    hf_band = (f >= 2500.0) & (f <= 7500.0)
    lf_band = (f >= 300.0) & (f < 2500.0)
    hf_power = float(np.sum(pxx[hf_band])) + 1e-9
    lf_power = float(np.sum(pxx[lf_band])) + 1e-9
    hf_ratio = float(hf_power / lf_power)

    # 3. Spectral Flux
    f_stft, t_stft, zxx = signal.stft(audio, fs=sr, nperseg=512, noverlap=256)
    mag = np.abs(zxx)
    if mag.shape[1] > 1:
        diff = np.diff(mag, axis=1)
        flux = float(np.mean(np.sqrt(np.sum(diff**2, axis=0))))
    else:
        flux = 0.0

    # 4. Harmonic-to-Noise & Flatness from standard acoustics
    hnr, flatness, rms = compute_audio_acoustics(audio, sr=sr)

    return np.array([roughness, hf_ratio, flux, hnr, flatness], dtype=np.float32)


def process_dataset(df: pd.DataFrame, desc: str) -> dict:
    print(f"Extracting features for {desc} (N={len(df)})...")
    t0 = time.time()
    short_feats = []
    sust_feats = []
    vocal_feats = []
    labels = []
    source_groups = []
    categories = []
    durations = []
    ids = []

    for idx, row in df.iterrows():
        p = REPO_ROOT / row["workspace_audio_path"]
        aud = load_audio_wav(p)
        f_s = extract_short_branch_features(aud)
        f_l = extract_sustained_branch_features(aud)
        f_v = extract_vocal_acoustic_features(aud)

        short_feats.append(f_s)
        sust_feats.append(f_l)
        vocal_feats.append(f_v)
        labels.append(row["binary_label"])
        source_groups.append(row["source_group_id"])
        categories.append(row.get("target_category", "scream" if row["binary_label"] == 1 else "negative"))
        durations.append(row["duration_seconds"])
        ids.append(row.get("recording_id", row.get("original_recording_id", f"rec_{idx}")))

    elapsed = time.time() - t0
    print(f"Finished {desc} in {elapsed:.2f}s ({elapsed/len(df)*1000:.2f} ms/sample).")

    return {
        "x_short": np.array(short_feats, dtype=np.float32),
        "x_sust": np.array(sust_feats, dtype=np.float32),
        "x_vocal": np.array(vocal_feats, dtype=np.float32),
        "y": np.array(labels, dtype=np.int64),
        "source_groups": np.array(source_groups),
        "categories": np.array(categories),
        "durations": np.array(durations, dtype=np.float32),
        "ids": np.array(ids),
    }


def main():
    cache_dir = STAGE_DIR / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # 1. Stage 54 train and val
    s54_path = REPO_ROOT / "backend/research/stage_8_9_54/dataset/partition_manifest_verified.csv"
    df_s54 = pd.read_csv(s54_path)

    train_df = df_s54[df_s54["expansion_partition"] == "expansion_train"].copy()
    val_df = df_s54[df_s54["expansion_partition"] == "expansion_val"].copy()

    train_data = process_dataset(train_df, "Stage 54 Train (expansion_train)")
    val_data = process_dataset(val_df, "Stage 54 Val (expansion_val)")

    # 2. Stage 64 held-out short screams (N=268)
    s63_path = REPO_ROOT / "backend/research/stage_8_9_63/stage_63_development_manifest.csv"
    df_s63 = pd.read_csv(s63_path)
    s64_path = REPO_ROOT / "backend/research/stage_8_9_64/stage_64_short_scream_manifest.csv"
    df_s64 = pd.read_csv(s64_path)
    dev_pcm = set(df_s63["pcm_sha256"])
    held_out_s64 = df_s64[~df_s64["pcm_sha256"].isin(dev_pcm)].copy()

    short_data = process_dataset(held_out_s64, "Stage 64 Held-Out Short Screams")

    # Save to disk
    np.savez_compressed(cache_dir / "train_features.npz", **train_data)
    np.savez_compressed(cache_dir / "val_features.npz", **val_data)
    np.savez_compressed(cache_dir / "held_out_short_features.npz", **short_data)
    print(f"\nAll features cached successfully to {cache_dir}!")


if __name__ == "__main__":
    main()

