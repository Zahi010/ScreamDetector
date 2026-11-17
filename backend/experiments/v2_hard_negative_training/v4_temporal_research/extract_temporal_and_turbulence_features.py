"""Extract unpooled frame-level sequences, temporal statistics, and acoustic turbulence features (Stage 8.9.8).

Computes:
1. Frame-level unpooled YAMNet embeddings sequence (T_i x 1024)
2. Padded sequence tensor (N x T_max x 1024) and sequence lengths
3. Temporal pooling baseline features (Model T3: mean, std, p10, p90, delta_mean = 5,120-dim)
4. 16 Acoustic Turbulence and Rhythmicity features:
   - hnr_mean, hnr_min, hnr_std (autocorrelation HNR in vocal range)
   - spectral_flatness_mean, spectral_flatness_max (Wiener entropy in scream band)
   - spectral_entropy_mean (Shannon entropy of power spectrum)
   - subharmonic_energy_ratio (subharmonic vs harmonic energy ratio)
   - rms_energy_mean, rms_energy_std (RMS envelope statistics)
   - crest_factor (peak-to-RMS in dB)
   - log_attack_time (log10 ms from 10% to 90% peak envelope rise)
   - temporal_centroid (energy envelope center of mass)
   - onset_density (onsets per second via spectral flux)
   - ioi_mean (mean inter-onset interval)
   - ioi_cv (coefficient of variation of IOIs - rhythmicity vs chaos)
   - pitch_cv (pitch coefficient of variation across voiced frames)

Caches output in:
`backend/experiments/v2_hard_negative_training/v4_temporal_research/features/temporal_and_turbulence_features.npz`.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
from scipy import signal
from scipy import stats

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.audio.preprocessor import load_audio
from src.config import TARGET_SAMPLE_RATE
from src.model.yamnet_loader import YAMNetLoader

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("extract_temporal_features")

EXPERIMENT_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training"
MANIFEST_PATH = EXPERIMENT_DIR / "manifests" / "dataset_manifest_v3.json"
V4_DIR = EXPERIMENT_DIR / "v4_temporal_research"
FEATURES_OUT = V4_DIR / "features" / "temporal_and_turbulence_features.npz"

MAX_SEQUENCE_LENGTH = 70  # Cap at 70 frames (~35 seconds)


def compute_frame_hnr(frame: np.ndarray, sr: int = TARGET_SAMPLE_RATE) -> float:
    """Compute Harmonic-to-Noise Ratio in dB for a 1D frame using normalized autocorrelation.
    
    Search lag range corresponding to 100 Hz - 1000 Hz vocal pitch.
    Lag range at 16,000 Hz: [16, 160] samples.
    """
    n = len(frame)
    if n < 320:
        return 0.0

    energy = np.sum(frame ** 2)
    if energy < 1e-7:
        return -20.0

    # Normalized autocorrelation for lags 16 to 160
    min_lag = int(sr / 1000)  # 16
    max_lag = int(sr / 100)   # 160

    # FFT-based autocorrelation
    n_fft = 2 ** int(np.ceil(np.log2(2 * n - 1)))
    fx = np.fft.rfft(frame, n=n_fft)
    rx = np.fft.irfft(fx * np.conj(fx), n=n_fft)[:max_lag + 1]

    # Energy normalizer
    # Normalize by rx[0] (total energy)
    r_norm = rx / max(1e-7, rx[0])

    search_region = r_norm[min_lag:max_lag + 1]
    if len(search_region) == 0:
        return 0.0

    r_max = float(np.max(search_region))
    r_max = np.clip(r_max, -0.99, 0.99)

    if r_max <= 0.05:
        return -10.0  # Dominantly noise / unvoiced

    hnr_db = 10.0 * np.log10(r_max / max(1e-5, (1.0 - r_max)))
    return float(np.clip(hnr_db, -20.0, 40.0))


def compute_spectral_features(waveform: np.ndarray, sr: int = TARGET_SAMPLE_RATE) -> Tuple[float, float, float, float]:
    """Compute Wiener spectral flatness, spectral entropy, and subharmonic energy ratio."""
    # STFT
    n_fft = 1024
    hop_length = 512
    freqs, times, zxx = signal.stft(waveform, fs=sr, nperseg=n_fft, noverlap=n_fft - hop_length)
    mag_spec = np.abs(zxx)  # (n_freqs, n_times)
    pwr_spec = mag_spec ** 2

    # 1. Scream resonance band: 1500 Hz to 4500 Hz
    band_mask = (freqs >= 1500) & (freqs <= 4500)
    band_pwr = pwr_spec[band_mask, :]

    if band_pwr.size == 0 or np.sum(band_pwr) < 1e-8:
        return 0.0, 0.0, 0.0, 0.0

    # Spectral flatness across frames in scream band
    geom_means = np.exp(np.mean(np.log(band_pwr + 1e-9), axis=0))
    arith_means = np.mean(band_pwr + 1e-9, axis=0)
    flatness_frames = geom_means / arith_means
    flatness_mean = float(np.mean(flatness_frames))
    flatness_max = float(np.max(flatness_frames))

    # 2. Normalized Spectral Entropy
    total_pwr_per_frame = np.sum(pwr_spec + 1e-9, axis=0, keepdims=True)
    prob_spec = (pwr_spec + 1e-9) / total_pwr_per_frame
    entropy_frames = -np.sum(prob_spec * np.log(prob_spec), axis=0) / np.log(len(freqs))
    entropy_mean = float(np.mean(entropy_frames))

    # 3. Subharmonic energy ratio
    # Average spectrum
    mean_spec = np.mean(pwr_spec, axis=1)
    # Fundamental harmonic peaks vs inter-harmonic troughs
    # Search dominant peak in 200 - 800 Hz
    f0_mask = (freqs >= 200) & (freqs <= 800)
    if np.sum(f0_mask) > 0:
        f0_idx = np.where(f0_mask)[0][np.argmax(mean_spec[f0_mask])]
        f0_freq = freqs[f0_idx]

        # Check subharmonic at ~0.5 * f0
        sub_mask = (freqs >= 0.4 * f0_freq) & (freqs <= 0.6 * f0_freq)
        harm_mask = (freqs >= 0.9 * f0_freq) & (freqs <= 1.1 * f0_freq)

        sub_pwr = np.sum(mean_spec[sub_mask]) if np.sum(sub_mask) > 0 else 1e-7
        harm_pwr = np.sum(mean_spec[harm_mask]) if np.sum(harm_mask) > 0 else 1e-7
        subharmonic_ratio = float(np.clip(sub_pwr / max(1e-7, harm_pwr), 0.0, 5.0))
    else:
        subharmonic_ratio = 0.0

    return flatness_mean, flatness_max, entropy_mean, subharmonic_ratio


def compute_envelope_and_rhythm_features(waveform: np.ndarray, sr: int = TARGET_SAMPLE_RATE) -> Tuple[float, float, float, float, float, float, float, float]:
    """Compute RMS envelope variation, crest factor, log attack time, temporal centroid, onset density, and IOI CV."""
    frame_len = int(sr * 0.025)  # 25 ms
    hop_len = int(sr * 0.010)    # 10 ms
    n_frames = (len(waveform) - frame_len) // hop_len + 1

    if n_frames <= 1:
        return 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0

    rms_frames = np.zeros(n_frames, dtype=np.float32)
    for i in range(n_frames):
        start = i * hop_len
        chunk = waveform[start : start + frame_len]
        rms_frames[i] = np.sqrt(np.mean(chunk ** 2))

    rms_mean = float(np.mean(rms_frames))
    rms_std = float(np.std(rms_frames))
    peak_val = float(np.max(np.abs(waveform)))
    crest_factor = float(20.0 * np.log10((peak_val + 1e-6) / (rms_mean + 1e-6)))

    # Temporal centroid [0, 1]
    time_indices = np.linspace(0.0, 1.0, n_frames)
    total_energy = np.sum(rms_frames) + 1e-8
    centroid = float(np.sum(time_indices * rms_frames) / total_energy)

    # Log attack time: time in ms from 10% to 90% peak envelope rise
    peak_idx = int(np.argmax(rms_frames))
    if peak_idx > 0:
        envelope_to_peak = rms_frames[: peak_idx + 1]
        p_val = envelope_to_peak[-1]
        t10_idx = np.where(envelope_to_peak >= 0.10 * p_val)[0]
        t90_idx = np.where(envelope_to_peak >= 0.90 * p_val)[0]
        idx_10 = t10_idx[0] if len(t10_idx) > 0 else 0
        idx_90 = t90_idx[0] if len(t90_idx) > 0 else peak_idx
        attack_ms = max(1.0, (idx_90 - idx_10) * 10.0)  # 10ms hop
        log_attack_time = float(np.log10(attack_ms))
    else:
        log_attack_time = 0.0

    # Onset detection via Spectral Flux
    n_fft = 512
    _, _, zxx = signal.stft(waveform, fs=sr, nperseg=n_fft, noverlap=n_fft - hop_len)
    mag = np.abs(zxx)
    flux = np.sum(np.maximum(0.0, mag[:, 1:] - mag[:, :-1]), axis=0)

    # Find peaks in spectral flux
    flux_thresh = np.mean(flux) + 1.5 * np.std(flux)
    onset_peaks, _ = signal.find_peaks(flux, height=flux_thresh, distance=int(sr * 0.10 / hop_len))  # min 100ms distance

    dur_sec = max(0.5, len(waveform) / sr)
    onset_density = float(len(onset_peaks) / dur_sec)

    if len(onset_peaks) >= 2:
        onset_times = onset_peaks * (hop_len / sr)
        iois = np.diff(onset_times)
        ioi_mean = float(np.mean(iois))
        ioi_cv = float(np.std(iois) / max(1e-4, ioi_mean))
    else:
        ioi_mean = 0.0
        ioi_cv = 1.0  # Single onset or no rhythm

    return rms_mean, rms_std, crest_factor, log_attack_time, centroid, onset_density, ioi_mean, ioi_cv


def compute_pitch_cv(waveform: np.ndarray, sr: int = TARGET_SAMPLE_RATE) -> float:
    """Compute coefficient of variation of pitch across voiced frames."""
    frame_len = 1024
    hop_len = 512
    n_frames = (len(waveform) - frame_len) // hop_len + 1
    if n_frames < 2:
        return 0.0

    pitches = []
    min_lag = int(sr / 1000)
    max_lag = int(sr / 100)

    for i in range(n_frames):
        chunk = waveform[i * hop_len : i * hop_len + frame_len]
        if np.sum(chunk ** 2) < 1e-6:
            continue
        rx = np.correlate(chunk, chunk, mode="full")[len(chunk) - 1 :]
        if rx[0] < 1e-6:
            continue
        r_norm = rx / rx[0]
        if len(r_norm) <= max_lag:
            continue
        search = r_norm[min_lag : max_lag + 1]
        best_lag = min_lag + int(np.argmax(search))
        best_val = search[best_lag - min_lag]
        if best_val > 0.40:  # Voiced frame
            f0 = sr / best_lag
            pitches.append(f0)

    if len(pitches) >= 3:
        return float(np.std(pitches) / max(1.0, np.mean(pitches)))
    else:
        return 1.0  # Chaotic / unvoiced


def extract_16_turbulence_features(waveform: np.ndarray, sr: int = TARGET_SAMPLE_RATE) -> np.ndarray:
    """Extract complete 16-dimensional turbulence & rhythmicity acoustic feature vector."""
    # 1. HNR statistics
    frame_len = 1024
    hop_len = 512
    n_frames = (len(waveform) - frame_len) // hop_len + 1
    hnr_list = []
    if n_frames > 0:
        for i in range(min(n_frames, 100)):
            chunk = waveform[i * hop_len : i * hop_len + frame_len]
            hnr_list.append(compute_frame_hnr(chunk, sr=sr))
    if hnr_list:
        hnr_mean = float(np.mean(hnr_list))
        hnr_min = float(np.min(hnr_list))
        hnr_std = float(np.std(hnr_list))
    else:
        hnr_mean, hnr_min, hnr_std = 0.0, 0.0, 0.0

    # 2. Spectral features
    flat_mean, flat_max, ent_mean, sub_ratio = compute_spectral_features(waveform, sr=sr)

    # 3. Envelope and rhythm features
    rms_m, rms_s, crest, log_atk, cent, on_dens, ioi_m, ioi_cv = compute_envelope_and_rhythm_features(waveform, sr=sr)

    # 4. Pitch CV
    p_cv = compute_pitch_cv(waveform, sr=sr)

    vec = np.array([
        hnr_mean,
        hnr_min,
        hnr_std,
        flat_mean,
        flat_max,
        ent_mean,
        sub_ratio,
        rms_m,
        rms_s,
        crest,
        log_atk,
        cent,
        on_dens,
        ioi_m,
        ioi_cv,
        p_cv,
    ], dtype=np.float32)

    # Replace any NaNs/Infs with 0.0
    vec = np.nan_to_num(vec, nan=0.0, posinf=1.0, neginf=-1.0)
    return vec


def main():
    logger.info("=" * 75)
    logger.info("STAGE 8.9.8: EXTRACTION OF TEMPORAL SEQUENCES & TURBULENCE FEATURES")
    logger.info("=" * 75)

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        records: List[Dict[str, Any]] = json.load(f)

    logger.info(f"Loaded {len(records)} records from {MANIFEST_PATH.name}")

    yamnet = YAMNetLoader()
    yamnet.load()

    file_ids = []
    splits = []
    binary_labels = []
    categories = []
    source_groups = []

    # Temporal sequences (padded to MAX_SEQUENCE_LENGTH x 1024)
    padded_sequences = np.zeros((len(records), MAX_SEQUENCE_LENGTH, 1024), dtype=np.float32)
    sequence_lengths = np.zeros(len(records), dtype=np.int32)

    # Model T3 features: [mean, std, p10, p90, delta_mean] -> 5120-dim
    features_t3_stats = np.zeros((len(records), 5120), dtype=np.float32)

    # 16 Acoustic turbulence features
    turbulence_features = np.zeros((len(records), 16), dtype=np.float32)

    for i, r in enumerate(records):
        f_id = r["file_id"]
        audio_p = Path(r["workspace_audio_path"])
        if not audio_p.exists():
            audio_p = Path(r["source_path"])

        try:
            wf, _ = load_audio(audio_p, target_sr=TARGET_SAMPLE_RATE)
            _, embs, _ = yamnet.infer(wf)

            t_len = min(len(embs), MAX_SEQUENCE_LENGTH)
            padded_sequences[i, :t_len, :] = embs[:t_len, :]
            sequence_lengths[i] = t_len

            # 1. Model T3 statistics
            f_mean = np.mean(embs, axis=0)
            f_std = np.std(embs, axis=0)
            f_p10 = np.percentile(embs, 10, axis=0)
            f_p90 = np.percentile(embs, 90, axis=0)
            if len(embs) > 1:
                f_delta = np.mean(np.abs(np.diff(embs, axis=0)), axis=0)
            else:
                f_delta = np.zeros(1024, dtype=np.float32)

            features_t3_stats[i] = np.concatenate([f_mean, f_std, f_p10, f_p90, f_delta], axis=0)

            # 2. 16 Acoustic turbulence features
            turb_vec = extract_16_turbulence_features(wf, sr=TARGET_SAMPLE_RATE)
            turbulence_features[i] = turb_vec

            file_ids.append(f_id)
            splits.append(r["split"])
            binary_labels.append(r["binary_label"])
            categories.append(r["target_category"])
            source_groups.append(r["source_group_id"])

            if (i + 1) % 150 == 0 or (i + 1) == len(records):
                logger.info(f"Extracted {i + 1}/{len(records)} recordings...")

        except Exception as e:
            logger.warning(f"Error extracting features for {f_id}: {e}")
            file_ids.append(f_id)
            splits.append(r["split"])
            binary_labels.append(r["binary_label"])
            categories.append(r["target_category"])
            source_groups.append(r["source_group_id"])

    FEATURES_OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        FEATURES_OUT,
        file_ids=np.array(file_ids),
        splits=np.array(splits),
        binary_labels=np.array(binary_labels),
        categories=np.array(categories),
        source_groups=np.array(source_groups),
        padded_sequences=padded_sequences,
        sequence_lengths=sequence_lengths,
        features_t3_stats=features_t3_stats,
        turbulence_features=turbulence_features,
    )

    logger.info(f"Saved temporal and turbulence features to {FEATURES_OUT}")
    logger.info(f"Padded sequences shape: {padded_sequences.shape}")
    logger.info(f"T3 statistics shape   : {features_t3_stats.shape}")
    logger.info(f"Turbulence shape      : {turbulence_features.shape}")
    print("\n" + "=" * 75)
    print("FEATURE EXTRACTION COMPLETED SUCCESSFULLY")
    print("=" * 75)


if __name__ == "__main__":
    main()
