"""Stage 8.9.11 Unified Feature Extraction Pipeline.

Extracts complete multimodal representations for all 1,384 commercial dataset recordings:
1. Multi-pooled YAMNet embeddings (mean, max, p10 -> 3,072-dim)
2. Unpooled temporal sequences padded to 70 frames (70 x 1,024)
3. Temporal variance and frame delta statistics (1,024 + 1,024)
4. 16 Acoustic Turbulence and Rhythmicity features
5. Contrastive vocal and crowd logits
6. 4 Adaptive SNR and low-frequency spectral tilt features

Outputs unified cache:
`stage8_9_11_evaluation/features/stage8_9_11_features.npz`.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
from scipy import signal

# Suppress TF logging
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.audio.preprocessor import load_audio
from src.config import TARGET_SAMPLE_RATE
from src.model.yamnet_loader import YAMNetLoader

# Import exact turbulence feature extractors
from experiments.v2_hard_negative_training.v4_temporal_research.extract_temporal_and_turbulence_features import (
    compute_frame_hnr,
    compute_spectral_features,
    compute_envelope_and_rhythm_features,
    compute_pitch_cv,
    extract_16_turbulence_features,
    MAX_SEQUENCE_LENGTH,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("stage8_9_11_features")

STAGE11_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_11_evaluation"
MANIFEST_PATH = STAGE11_DIR / "stage8_9_11_dataset_manifest.json"
FEATURES_OUT_DIR = STAGE11_DIR / "features"
FEATURES_OUT_PATH = FEATURES_OUT_DIR / "stage8_9_11_features.npz"

V4_FEATURES_PATH = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "features" / "temporal_and_turbulence_features.npz"
V3_FEATURES_PATH = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "features" / "yamnet_features_v3.npz"


def compute_snr_features(waveform: np.ndarray, sr: int = TARGET_SAMPLE_RATE) -> np.ndarray:
    """Compute 4 adaptive SNR and low-frequency spectral tilt features."""
    if len(waveform) < 320:
        return np.zeros(4, dtype=np.float32)

    # 1. Low frequency energy ratio (< 150 Hz)
    freqs, psd = signal.welch(waveform, fs=sr, nperseg=min(len(waveform), 1024))
    total_energy = float(np.sum(psd) + 1e-12)
    low_freq_mask = (freqs < 150.0)
    low_freq_ratio = float(np.sum(psd[low_freq_mask]) / total_energy)

    # 2. Band-SNR in scream resonance band (1.5 - 4.5 kHz)
    scream_band_mask = (freqs >= 1500.0) & (freqs <= 4500.0)
    scream_energy = float(np.sum(psd[scream_band_mask]) + 1e-12)
    out_band_energy = float(np.sum(psd[~scream_band_mask]) + 1e-12)
    band_snr_db = float(10.0 * np.log10(scream_energy / out_band_energy))

    # 3. Noise floor estimate (10th percentile of frame RMS)
    frame_len = int(sr * 0.050)  # 50 ms
    if len(waveform) >= frame_len:
        num_frames = len(waveform) // frame_len
        frames = waveform[: num_frames * frame_len].reshape(num_frames, frame_len)
        frame_rms = np.sqrt(np.mean(frames ** 2, axis=1) + 1e-12)
        noise_floor = float(np.percentile(frame_rms, 10))
    else:
        noise_floor = float(np.sqrt(np.mean(waveform ** 2) + 1e-12))

    # 4. Dynamic crest ratio (peak / RMS)
    rms = float(np.sqrt(np.mean(waveform ** 2) + 1e-12))
    peak = float(np.max(np.abs(waveform)))
    crest_ratio = float(peak / (rms + 1e-7))

    vec = np.array([low_freq_ratio, band_snr_db, noise_floor, crest_ratio], dtype=np.float32)
    return np.nan_to_num(vec, nan=0.0, posinf=10.0, neginf=-10.0)


def main():
    logger.info("=================================================================")
    logger.info("STAGE 8.9.11: UNIFIED MULTIMODAL FEATURE EXTRACTION")
    logger.info("=================================================================")

    FEATURES_OUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        records: List[Dict[str, Any]] = json.load(f)
    n_records = len(records)
    logger.info(f"Loaded {n_records} records from {MANIFEST_PATH.name}")

    # Load existing feature caches for fast indexing
    v4_cache = np.load(V4_FEATURES_PATH, allow_pickle=True)
    v3_cache = np.load(V3_FEATURES_PATH, allow_pickle=True)

    v4_id_to_idx = {fid: idx for idx, fid in enumerate(v4_cache["file_ids"])}
    v3_id_to_idx = {fid: idx for idx, fid in enumerate(v3_cache["file_ids"])}
    logger.info(f"Loaded V4 cache ({len(v4_id_to_idx)} entries) and V3 cache ({len(v3_id_to_idx)} entries).")

    # Pre-load arrays into memory to avoid repeated zip decompression inside loop
    v4_padded = v4_cache["padded_sequences"]
    v4_seqlens = v4_cache["sequence_lengths"]
    v4_t3 = v4_cache["features_t3_stats"]
    v4_turb = v4_cache["turbulence_features"]

    v3_concat = v3_cache["features_concat"]
    v3_vocal = v3_cache["vocal_features"]

    # Initialize feature arrays
    file_ids = []
    splits = []
    binary_labels = []
    categories = []
    source_groups = []

    features_concat = np.zeros((n_records, 3072), dtype=np.float32)
    padded_sequences = np.zeros((n_records, MAX_SEQUENCE_LENGTH, 1024), dtype=np.float32)
    sequence_lengths = np.zeros(n_records, dtype=np.int32)
    features_t3_stats = np.zeros((n_records, 5120), dtype=np.float32)
    turbulence_features = np.zeros((n_records, 16), dtype=np.float32)
    vocal_features = np.zeros((n_records, 6), dtype=np.float32)
    snr_features = np.zeros((n_records, 4), dtype=np.float32)

    yamnet: YAMNetLoader | None = None

    cache_hits = 0
    new_extractions = 0

    for i, r in enumerate(records):
        f_id = r["file_id"]
        split = r["split"]
        bin_label = r["binary_label"]
        cat = r["target_category"]
        grp = r["source_group_id"]

        file_ids.append(f_id)
        splits.append(split)
        binary_labels.append(bin_label)
        categories.append(cat)
        source_groups.append(grp)

        # Check if record is present in existing caches
        in_v4 = f_id in v4_id_to_idx
        in_v3 = f_id in v3_id_to_idx

        # Audio file path
        audio_p = BACKEND_DIR / r["workspace_audio_path"]
        if not audio_p.exists():
            audio_p = Path(r["workspace_audio_path"])
        if not audio_p.exists() and "source_path" in r:
            audio_p = Path(r["source_path"])

        wf, _ = load_audio(audio_p, target_sr=TARGET_SAMPLE_RATE)
        # Always compute fresh SNR features directly on waveform
        snr_features[i] = compute_snr_features(wf)

        if in_v4 and in_v3:
            v4_idx = v4_id_to_idx[f_id]
            v3_idx = v3_id_to_idx[f_id]

            features_concat[i] = v3_concat[v3_idx]
            vocal_features[i] = v3_vocal[v3_idx]
            padded_sequences[i] = v4_padded[v4_idx]
            sequence_lengths[i] = v4_seqlens[v4_idx]
            features_t3_stats[i] = v4_t3[v4_idx]
            turbulence_features[i] = v4_turb[v4_idx]
            cache_hits += 1
        else:
            # Extract fresh features using YAMNet
            if yamnet is None:
                logger.info("Initializing YAMNet model for newly acquired recordings...")
                yamnet = YAMNetLoader()
                yamnet.load()

            _, embs, _ = yamnet.infer(wf)
            t_len = min(len(embs), MAX_SEQUENCE_LENGTH)
            padded_sequences[i, :t_len, :] = embs[:t_len, :]
            sequence_lengths[i] = t_len

            # Multi-pool features (mean, max, p10 -> 3,072)
            f_mean = np.mean(embs, axis=0)
            f_max = np.max(embs, axis=0)
            f_p10 = np.percentile(embs, 10, axis=0)
            features_concat[i] = np.concatenate([f_max, f_p10, f_mean])

            # Model T3 stats (5,120)
            f_std = np.std(embs, axis=0)
            f_p90 = np.percentile(embs, 90, axis=0)
            if len(embs) > 1:
                f_delta = np.mean(np.abs(np.diff(embs, axis=0)), axis=0)
            else:
                f_delta = np.zeros(1024, dtype=np.float32)
            features_t3_stats[i] = np.concatenate([f_mean, f_std, f_p10, f_p90, f_delta])

            # 16 Acoustic turbulence features
            turb = extract_16_turbulence_features(wf, sr=TARGET_SAMPLE_RATE)
            turbulence_features[i] = turb

            # Approximate vocal logits using mean embedding dot products
            vocal_features[i] = np.array([
                float(np.mean(f_mean[:100])),
                float(np.std(f_mean[:100])),
                float(np.max(f_mean[:100])),
                float(np.mean(f_mean[100:200])),
                float(np.std(f_mean[100:200])),
                float(np.max(f_mean[100:200])),
            ], dtype=np.float32)

            new_extractions += 1

        if (i + 1) % 250 == 0 or (i + 1) == n_records:
            logger.info(f"Processed {i + 1}/{n_records} recordings (Cache hits: {cache_hits}, New extractions: {new_extractions})...")

    # Fit front-end vocal and crowd detectors on training split
    train_mask = (np.array(splits) == "train")
    is_vocal_train = np.isin(np.array(categories)[train_mask], ["scream", "shouting_and_speech", "infant_crying", "crowd_chant_cheering"]).astype(int)
    is_crowd_train = (np.array(categories)[train_mask] == "crowd_chant_cheering").astype(int)

    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import Pipeline

    pipe_vocal = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(C=1.0, class_weight="balanced", random_state=42, max_iter=1000)),
    ])
    pipe_vocal.fit(features_concat[train_mask], is_vocal_train)

    pipe_crowd = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(C=1.0, class_weight="balanced", random_state=42, max_iter=1000)),
    ])
    pipe_crowd.fit(features_concat[train_mask], is_crowd_train)

    vocal_logit = pipe_vocal.decision_function(features_concat).reshape(-1, 1).astype(np.float32)
    crowd_logit = pipe_crowd.decision_function(features_concat).reshape(-1, 1).astype(np.float32)

    logger.info(f"Saving {n_records} feature sets to {FEATURES_OUT_PATH}...")
    np.savez_compressed(
        FEATURES_OUT_PATH,
        file_ids=np.array(file_ids),
        splits=np.array(splits),
        binary_labels=np.array(binary_labels),
        categories=np.array(categories),
        source_groups=np.array(source_groups),
        features_concat=features_concat,
        padded_sequences=padded_sequences,
        sequence_lengths=sequence_lengths,
        features_t3_stats=features_t3_stats,
        turbulence_features=turbulence_features,
        vocal_features=vocal_features,
        vocal_logit=vocal_logit,
        crowd_logit=crowd_logit,
        snr_features=snr_features,
    )
    logger.info("Stage 8.9.11 Feature Extraction Complete!")


if __name__ == "__main__":
    main()
