"""Stage 8.9.15 Comprehensive Robustness Testing Suite.

Tests 14 challenging acoustic conditions and edge cases:
1. Extended silence (zero amplitude)
2. Digital clipping (severe saturation / square wave)
3. Severe DC bias (+0.3 DC offset)
4. Impulse noise (random full-scale Dirac spikes)
5. Heavy AWGN noise (0 dB SNR)
6. Music and bass-heavy audio
7. Background crowd cheering & babble
8. Reverberation (synthetic impulse response convolution)
9. Distant screams (low SNR, high-frequency attenuation)
10. Low-amplitude screams (-25 dBFS)
11. High-amplitude shouting (+6 dBFS strained vocalization)
12. Multiple simultaneous voices (polyphonic vocal mixture)
13. Whistles and sirens (high-frequency non-scream sinusoidal tones)
14. Malformed audio buffer / very short buffer (0.1s, NaNs, Infs)

Outputs:
- robustness_test_results.csv in workspace root and reports/
"""

from __future__ import annotations

import csv
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
from scipy import signal
import joblib

# Suppress TF logging
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
import tensorflow as tf
from tensorflow import keras

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("stage8_9_15_robustness")

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from experiments.v2_hard_negative_training.v4_temporal_research.stage8_9_14_acoustic_discriminability.acoustic_discriminability_features import (
    AcousticDiscriminabilityExtractor,
)
from src.model.yamnet_loader import YAMNetLoader

STAGE15_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_15_hierarchical_phonation"
MODELS_DIR = STAGE15_DIR / "models"
REPORTS_DIR = STAGE15_DIR / "reports"


def run_robustness_suite():
    logger.info("=================================================================")
    logger.info("STAGE 8.9.15: COMPREHENSIVE 14-CONDITION ROBUSTNESS SUITE")
    logger.info("=================================================================")

    # Initialize components
    logger.info("Loading YAMNet model...")
    yamnet_loader = YAMNetLoader()
    yamnet_loader.load()

    logger.info("Loading Acoustic Discriminability Extractor...")
    acoustic_extractor = AcousticDiscriminabilityExtractor(sr=16000)

    logger.info("Loading Stage 8.9.15 models...")
    scaler = joblib.load(MODELS_DIR / "stage8_9_15_feature_scaler.joblib")
    ac_scaler = joblib.load(MODELS_DIR / "stage8_9_15_acoustic_scaler.joblib")
    fusion_scaler = joblib.load(MODELS_DIR / "stage8_9_15_fusion_scaler.joblib")

    gate_model = joblib.load(MODELS_DIR / "Gate_A_ExtraTrees.joblib")
    mlp_model = joblib.load(MODELS_DIR / "Model_A_Compact_MLP.joblib")
    tcn_model = keras.models.load_model(MODELS_DIR / "Model_B_Temporal_CNN.keras")
    fusion_model = joblib.load(MODELS_DIR / "Model_C_Hierarchical_Fusion.joblib")

    # Load operating thresholds from threshold selection audit
    with open(STAGE15_DIR / "threshold_selection_audit.json", "r", encoding="utf-8") as f:
        th_audit = json.load(f)

    gate_th = th_audit.get("Gate_A_ExtraTrees", {}).get("operating_threshold", 0.10)
    fusion_th = th_audit.get("Model_C_Hybrid_Fusion", {}).get("operating_threshold", 0.40)
    logger.info(f"Using Gate Threshold: {gate_th}, Fusion Threshold: {fusion_th}")

    sr = 16000
    n_samples = 16000
    top_feat_indices = [11, 23, 17, 26, 10, 2]

    def infer_pipeline(audio_buf: np.ndarray) -> Dict[str, Any]:
        """Run full hierarchical inference pipeline safely on an arbitrary buffer."""
        # Sanitization
        clean_buf = np.nan_to_num(audio_buf, nan=0.0, posinf=1.0, neginf=-1.0).astype(np.float32)
        if len(clean_buf) < 1600:
            clean_buf = np.pad(clean_buf, (0, 1600 - len(clean_buf)))
        clean_buf = clean_buf - np.mean(clean_buf)

        # YAMNet
        _, emb, _ = yamnet_loader.infer(clean_buf)
        if emb.shape[0] == 0:
            emb = np.zeros((1, 1024), dtype=np.float32)
        p_mean = np.mean(emb, axis=0)
        p_max = np.max(emb, axis=0)
        p_p10 = np.percentile(emb, 10, axis=0)
        y_feat = np.concatenate([p_mean, p_max, p_p10])

        # Acoustic features
        ac_feat = acoustic_extractor.extract_features(clean_buf)
        comb_feat = np.concatenate([y_feat, ac_feat]).reshape(1, -1)
        comb_scaled = scaler.transform(comb_feat)

        # Stage 1 Gate
        gate_p = float(gate_model.predict_proba(comb_scaled)[0, 1])

        # Stage 2 Models
        mlp_p = float(mlp_model.predict_proba(comb_scaled)[0, 1])

        seq_padded = np.zeros((1, 70, 1024), dtype=np.float32)
        n_frames = min(70, emb.shape[0])
        seq_padded[0, :n_frames, :] = emb[:n_frames, :]
        ac_scaled = ac_scaler.transform(ac_feat.reshape(1, -1))
        tcn_p = float(tcn_model([seq_padded, ac_scaled], training=False).numpy()[0, 0])

        top_feat = ac_feat[top_feat_indices].reshape(1, -1)
        fus_in = np.hstack([[gate_p], [mlp_p], [tcn_p], top_feat.flatten()]).reshape(1, -1)
        fus_scaled = fusion_scaler.transform(fus_in)
        fusion_p = float(fusion_model.predict_proba(fus_scaled)[0, 1])

        # Gated Cascade decision
        gated_prob = fusion_p if gate_p >= gate_th else 0.0

        # Three-outcome uncertainty categorization:
        # Confident Scream: gated_prob >= 0.55
        # Confident Non-Scream: gated_prob < 0.25
        # Uncertain / Requires Review: 0.25 <= gated_prob < 0.55
        if gated_prob >= 0.55:
            decision = "SCREAM_CANDIDATE"
        elif gated_prob < 0.25:
            decision = "NON_SCREAM"
        else:
            decision = "UNCERTAIN_REQUIRES_HUMAN_REVIEW"

        return {
            "gate_prob": round(gate_p, 4),
            "mlp_prob": round(mlp_p, 4),
            "tcn_prob": round(tcn_p, 4),
            "fusion_prob": round(fusion_p, 4),
            "gated_prob": round(gated_prob, 4),
            "decision": decision,
        }

    # Synthesize test stimuli
    t = np.linspace(0, 1.0, sr, endpoint=False)
    # Scream prototype (frequency modulation 1200-2400 Hz + noise turbulence)
    scream_proto = (
        0.5 * np.sin(2 * np.pi * (1400 * t + 300 * np.sin(2 * np.pi * 8 * t)))
        + 0.3 * np.sin(2 * np.pi * 2800 * t)
        + 0.2 * np.random.randn(sr)
    ).astype(np.float32)

    # Shouting prototype (F0=400 Hz + strong harmonics + syllabic pulse)
    shout_env = 0.5 * (1 + np.sin(2 * np.pi * 3 * t))
    shout_proto = shout_env * (
        0.6 * np.sin(2 * np.pi * 400 * t)
        + 0.3 * np.sin(2 * np.pi * 800 * t)
        + 0.2 * np.sin(2 * np.pi * 1200 * t)
    ).astype(np.float32)

    test_conditions = [
        {
            "condition_id": "C01_Silence",
            "name": "Extended Silence (Zero Buffer)",
            "ground_truth": "NON_SCREAM",
            "audio": np.zeros(sr, dtype=np.float32),
            "expected_behavior": "Gated probability ≈ 0.0, rejected immediately",
        },
        {
            "condition_id": "C02_Digital_Clipping",
            "name": "Digital Clipping (Square Wave Saturation)",
            "ground_truth": "NON_SCREAM",
            "audio": np.sign(np.sin(2 * np.pi * 500 * t)).astype(np.float32),
            "expected_behavior": "Rejects synthetic square harmonics as non-scream",
        },
        {
            "condition_id": "C03_Severe_DC_Bias",
            "name": "Severe DC Bias (+0.3 DC offset)",
            "ground_truth": "NON_SCREAM",
            "audio": (0.3 + 0.05 * np.random.randn(sr)).astype(np.float32),
            "expected_behavior": "DC removal normalizes buffer cleanly; non-scream decision",
        },
        {
            "condition_id": "C04_Impulse_Spikes",
            "name": "Impulse Noise (Random Dirac Spikes)",
            "ground_truth": "NON_SCREAM",
            "audio": (lambda: (a := np.zeros(sr, dtype=np.float32), a.__setitem__(np.random.randint(0, sr, 10), 1.0), a)[2])(),
            "expected_behavior": "Nonlinear phonation continuity rejects isolated impulse spikes",
        },
        {
            "condition_id": "C05_AWGN_Noise",
            "name": "Heavy AWGN Noise (0 dB SNR)",
            "ground_truth": "NON_SCREAM",
            "audio": np.random.randn(sr).astype(np.float32),
            "expected_behavior": "Spectral flatness and gate reject pure Gaussian noise",
        },
        {
            "condition_id": "C06_Music_Bass",
            "name": "Music and Bass-Heavy Beat (60 Hz + 120 Hz Sub-bass)",
            "ground_truth": "NON_SCREAM",
            "audio": (0.7 * np.sin(2 * np.pi * 60 * t) + 0.4 * np.sin(2 * np.pi * 120 * t)).astype(np.float32),
            "expected_behavior": "Low vocal energy ratio rejects high sub-1kHz concentration",
        },
        {
            "condition_id": "C07_Crowd_Cheering",
            "name": "Background Crowd Cheering & Babble",
            "ground_truth": "NON_SCREAM",
            "audio": signal.convolve(np.random.randn(sr), signal.butter(4, [300, 3000], btype="bandpass", fs=sr, output="sos").flatten()[:500], mode="same").astype(np.float32) * 0.4,
            "expected_behavior": "Phonation continuity rejects diffuse incoherent babble",
        },
        {
            "condition_id": "C08_Reverberation",
            "name": "Reverberant Scream (Late Room Reflection)",
            "ground_truth": "SCREAM",
            "audio": signal.convolve(scream_proto, np.exp(-np.linspace(0, 5, 2000)), mode="same").astype(np.float32),
            "expected_behavior": "Scream characteristics preserved despite temporal reverberation smear",
        },
        {
            "condition_id": "C09_Distant_Scream",
            "name": "Distant Scream (High-freq attenuation + low SNR)",
            "ground_truth": "SCREAM",
            "audio": (signal.sosfilt(signal.butter(4, 2500, btype="lowpass", fs=sr, output="sos"), scream_proto) * 0.15 + 0.05 * np.random.randn(sr)).astype(np.float32),
            "expected_behavior": "Gate preserves candidate; classifier flags as scream or human review",
        },
        {
            "condition_id": "C10_Low_Amplitude_Scream",
            "name": "Low-Amplitude Scream (-25 dBFS)",
            "ground_truth": "SCREAM",
            "audio": (scream_proto * 0.06).astype(np.float32),
            "expected_behavior": "Dynamic normalization preserves relative spectral ratios",
        },
        {
            "condition_id": "C11_High_Amplitude_Shout",
            "name": "High-Amplitude Strained Shouting (+6 dBFS Peak)",
            "ground_truth": "NON_SCREAM",
            "audio": np.clip(shout_proto * 2.0, -1.0, 1.0).astype(np.float32),
            "expected_behavior": "Harmonic decay & low vocal energy ratio prevent false positive",
        },
        {
            "condition_id": "C12_Polyphonic_Voices",
            "name": "Multiple Simultaneous Voices (Polyphonic Mixture)",
            "ground_truth": "NON_SCREAM",
            "audio": (0.3 * np.sin(2 * np.pi * 220 * t) + 0.3 * np.sin(2 * np.pi * 330 * t) + 0.3 * np.sin(2 * np.pi * 440 * t)).astype(np.float32),
            "expected_behavior": "Interference harmonics without scream turbulence classified as non-scream",
        },
        {
            "condition_id": "C13_Whistles_Sirens",
            "name": "Whistles and Sirens (Narrowband Swept Sine)",
            "ground_truth": "NON_SCREAM",
            "audio": np.sin(2 * np.pi * (2500 + 500 * np.sin(2 * np.pi * 5 * t)) * t).astype(np.float32),
            "expected_behavior": "Zero vocal turbulence and extreme narrow bandwidth rejected",
        },
        {
            "condition_id": "C14_Malformed_Buffer",
            "name": "Malformed / Truncated Buffer with NaNs and Infs",
            "ground_truth": "NON_SCREAM",
            "audio": np.array([np.nan, 1e10, -1e10, 0.5, -0.5] + list(np.random.randn(1595)), dtype=np.float32),
            "expected_behavior": "Sanitization prevents exception; safely outputs non-scream",
        },
    ]

    results = []
    for cond in test_conditions:
        logger.info(f"Running robustness test: {cond['condition_id']} - {cond['name']}...")
        inf = infer_pipeline(cond["audio"])

        is_correct = (
            (cond["ground_truth"] == "SCREAM" and inf["decision"] in ("SCREAM_CANDIDATE", "UNCERTAIN_REQUIRES_HUMAN_REVIEW"))
            or (cond["ground_truth"] == "NON_SCREAM" and inf["decision"] == "NON_SCREAM")
        )

        results.append({
            "condition_id": cond["condition_id"],
            "condition_name": cond["name"],
            "ground_truth": cond["ground_truth"],
            "gate_probability": inf["gate_prob"],
            "mlp_probability": inf["mlp_prob"],
            "tcn_probability": inf["tcn_prob"],
            "hybrid_fusion_probability": inf["fusion_prob"],
            "gated_cascade_probability": inf["gated_prob"],
            "pipeline_decision": inf["decision"],
            "expected_behavior": cond["expected_behavior"],
            "test_verdict": "PASS" if is_correct else "FAIL_INVESTIGATION_REQUIRED",
        })

    out_csv = STAGE15_DIR / "robustness_test_results.csv"
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    logger.info(f"Saved robustness results to: {out_csv}")

    reports_csv = REPORTS_DIR / "robustness_test_results.csv"
    with open(reports_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    run_robustness_suite()
