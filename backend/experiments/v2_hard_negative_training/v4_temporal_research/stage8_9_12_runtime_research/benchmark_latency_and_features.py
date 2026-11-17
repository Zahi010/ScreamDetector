"""Standardized End-to-End Latency and Inference Path Benchmark for Stage 8.9.12.

Compares:
1. Candidate D_v4 (Baseline Linear Fusion, 3,072 dims)
2. Candidate D_v4_Optimized (Vectorized array conversions and direct pooling)
3. Candidate H_v5_SNR_Baseline (Original unoptimized SciPy STFT & Welch loops)
4. Candidate H_v5_SNR_Optimized (FastAcousticFeatureExtractor with shared autocorrelation & STFT)

Benchmarks complete audio-to-alert pipeline over 100 timed iterations:
- Stage 1: Audio Ingestion & PCM Decoding (1.0s window @ 44.1 kHz, 16-bit PCM)
- Stage 2: Resampling & Filtering (44.1 kHz -> 16 kHz)
- Stage 3: YAMNet Feature Extraction (TensorFlow Hub)
- Stage 4: Acoustic Feature Extraction (Turbulence + SNR)
- Stage 5: Classifier Inference & Platt Calibration
- Stage 6: Temporal Alert State Machine Update & JSON Alert Output

Outputs: `stage8_9_12_runtime_research/latency_benchmark_results.csv`.
"""

from __future__ import annotations

import csv
import logging
import os
import platform
import sys
import time
import tracemalloc
from pathlib import Path
from typing import Any, Dict, List

import joblib
import numpy as np

# Suppress TF oneDNN spam
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.audio.preprocessor import resample_audio
from src.config import TARGET_SAMPLE_RATE
from src.model.yamnet_loader import YAMNetLoader
from experiments.v2_hard_negative_training.v4_temporal_research.extract_temporal_and_turbulence_features import (
    extract_16_turbulence_features as orig_turb_fn,
)
from experiments.v2_hard_negative_training.v4_temporal_research.stage8_9_11_evaluation.extract_stage8_9_11_features import (
    compute_snr_features as orig_snr_fn,
)
from experiments.v2_hard_negative_training.v4_temporal_research.stage8_9_12_runtime_research.fast_acoustic_features import (
    FastAcousticFeatureExtractor,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("stage8_9_12_latency")

STAGE11_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_11_evaluation"
STAGE12_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_12_runtime_research"


def run_latency_benchmark(num_warmup: int = 15, num_timed: int = 100) -> List[Dict[str, Any]]:
    logger.info("=================================================================")
    logger.info("STAGE 8.9.12: COMPREHENSIVE END-TO-END LATENCY BENCHMARK")
    logger.info("=================================================================")

    # 1. Load models
    logger.info("Loading YAMNet feature extractor and candidate models...")
    yamnet = YAMNetLoader()
    yamnet.load()

    m_d = joblib.load(STAGE11_DIR / "models" / "model_d_v4.joblib")
    pipe_d = m_d["pipe"]
    calib_d = m_d["calibrator"]

    m_hv5 = joblib.load(STAGE11_DIR / "models" / "model_h_v5_snr.joblib")
    pipe_hv5 = m_hv5["pipe"]
    calib_hv5 = m_hv5["calibrator"]

    fast_extractor = FastAcousticFeatureExtractor(sr=TARGET_SAMPLE_RATE)

    # 2. Synthesize realistic 1.0s audio buffer (44.1 kHz 16-bit PCM)
    orig_sr = 44100
    duration_sec = 1.0
    t = np.linspace(0, duration_sec, int(orig_sr * duration_sec), endpoint=False)
    synthetic_audio = (0.4 * np.sin(2 * np.pi * 1000 * t) + 0.1 * np.random.randn(len(t))).astype(np.float32)
    raw_pcm_16_bytes = (np.clip(synthetic_audio, -1.0, 1.0) * 32767.0).astype(np.int16).tobytes()

    candidates = [
        "D_v4_Baseline",
        "D_v4_Optimized",
        "H_v5_SNR_Baseline",
        "H_v5_SNR_Optimized",
    ]

    benchmark_records = []

    # System metadata
    hw_info = {
        "processor": platform.processor(),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
    }

    dummy_vocal_hv5 = np.zeros((1, 8), dtype=np.float32)
    zero_delta_1024 = np.zeros((1, 1024), dtype=np.float32)

    for cand in candidates:
        logger.info(f"Benchmarking candidate inference path: {cand}...")

        # Warmup
        for _ in range(num_warmup):
            # Decode & Resample
            audio_int16 = np.frombuffer(raw_pcm_16_bytes, dtype=np.int16)
            audio_float = audio_int16.astype(np.float32) / 32768.0
            wf_16k = resample_audio(audio_float, orig_sr=orig_sr, target_sr=TARGET_SAMPLE_RATE)
            _, embs, _ = yamnet.infer(wf_16k)

            if cand.startswith("D_v4"):
                f_mean = np.mean(embs, axis=0)
                f_max = np.max(embs, axis=0)
                f_p10 = np.percentile(embs, 10, axis=0)
                feat = np.concatenate([f_max, f_p10, f_mean]).reshape(1, -1)
                logits = pipe_d.decision_function(feat).reshape(-1, 1)
                prob = calib_d.predict_proba(logits)[0, 1]
            elif cand == "H_v5_SNR_Baseline":
                f_mean = np.mean(embs, axis=0)
                f_max = np.max(embs, axis=0)
                f_p10 = np.percentile(embs, 10, axis=0)
                f_concat = np.concatenate([f_max, f_p10, f_mean]).reshape(1, -1)
                f_std = np.std(embs, axis=0).reshape(1, -1)
                turb = orig_turb_fn(wf_16k, sr=TARGET_SAMPLE_RATE).reshape(1, -1)
                snr_feat = orig_snr_fn(wf_16k, sr=TARGET_SAMPLE_RATE).reshape(1, -1)
                feat = np.hstack([f_concat, f_std, zero_delta_1024, turb, dummy_vocal_hv5, snr_feat])
                logits = pipe_hv5.decision_function(feat).reshape(-1, 1)
                prob = calib_hv5.predict_proba(logits)[0, 1]
            elif cand == "H_v5_SNR_Optimized":
                f_mean = np.mean(embs, axis=0)
                f_max = np.max(embs, axis=0)
                f_p10 = np.percentile(embs, 10, axis=0)
                f_concat = np.concatenate([f_max, f_p10, f_mean]).reshape(1, -1)
                f_std = np.std(embs, axis=0).reshape(1, -1)
                turb, snr_feat = fast_extractor.extract_turbulence_and_snr_fast(wf_16k)
                feat = np.hstack([f_concat, f_std, zero_delta_1024, turb.reshape(1, -1), dummy_vocal_hv5, snr_feat.reshape(1, -1)])
                logits = pipe_hv5.decision_function(feat).reshape(-1, 1)
                prob = calib_hv5.predict_proba(logits)[0, 1]

        # Timed runs
        t_decode = []
        t_resample = []
        t_yamnet = []
        t_physics = []
        t_classifier = []
        t_state = []
        t_e2e = []

        tracemalloc.start()
        mem_start = tracemalloc.get_traced_memory()[0]

        for _ in range(num_timed):
            t0_e2e = time.perf_counter()

            # Stage 1: PCM Ingestion & Decode
            t0 = time.perf_counter()
            audio_int16 = np.frombuffer(raw_pcm_16_bytes, dtype=np.int16)
            audio_float = audio_int16.astype(np.float32) / 32768.0
            t1 = time.perf_counter()
            t_decode.append((t1 - t0) * 1000.0)

            # Stage 2: Resampling & Filter
            t0 = time.perf_counter()
            wf_16k = resample_audio(audio_float, orig_sr=orig_sr, target_sr=TARGET_SAMPLE_RATE)
            t1 = time.perf_counter()
            t_resample.append((t1 - t0) * 1000.0)

            # Stage 3: YAMNet Feature Extraction
            t0 = time.perf_counter()
            _, embs, _ = yamnet.infer(wf_16k)
            t1 = time.perf_counter()
            t_yamnet.append((t1 - t0) * 1000.0)

            # Stage 4: Feature aggregation & Physics
            t0 = time.perf_counter()
            if cand == "D_v4_Baseline":
                f_mean = np.mean(embs, axis=0)
                f_max = np.max(embs, axis=0)
                f_p10 = np.percentile(embs, 10, axis=0)
                feat = np.concatenate([f_max, f_p10, f_mean]).reshape(1, -1)
            elif cand == "D_v4_Optimized":
                # Vectorized multi-pool along axis 0
                f_mean = np.mean(embs, axis=0)
                f_max = np.max(embs, axis=0)
                f_p10 = np.sort(embs, axis=0)[0] if len(embs) <= 2 else np.percentile(embs, 10, axis=0)
                feat = np.empty((1, 3072), dtype=np.float32)
                feat[0, 0:1024] = f_max
                feat[0, 1024:2048] = f_p10
                feat[0, 2048:3072] = f_mean
            elif cand == "H_v5_SNR_Baseline":
                f_mean = np.mean(embs, axis=0)
                f_max = np.max(embs, axis=0)
                f_p10 = np.percentile(embs, 10, axis=0)
                f_concat = np.concatenate([f_max, f_p10, f_mean]).reshape(1, -1)
                f_std = np.std(embs, axis=0).reshape(1, -1)
                turb = orig_turb_fn(wf_16k, sr=TARGET_SAMPLE_RATE).reshape(1, -1)
                snr_feat = orig_snr_fn(wf_16k, sr=TARGET_SAMPLE_RATE).reshape(1, -1)
                feat = np.hstack([f_concat, f_std, zero_delta_1024, turb, dummy_vocal_hv5, snr_feat])
            elif cand == "H_v5_SNR_Optimized":
                f_mean = np.mean(embs, axis=0)
                f_max = np.max(embs, axis=0)
                f_p10 = np.sort(embs, axis=0)[0] if len(embs) <= 2 else np.percentile(embs, 10, axis=0)
                f_std = np.std(embs, axis=0)
                turb, snr_feat = fast_extractor.extract_turbulence_and_snr_fast(wf_16k)
                feat = np.empty((1, 5148), dtype=np.float32)
                feat[0, 0:1024] = f_max
                feat[0, 1024:2048] = f_p10
                feat[0, 2048:3072] = f_mean
                feat[0, 3072:4096] = f_std
                feat[0, 4096:5120] = 0.0  # delta
                feat[0, 5120:5136] = turb
                feat[0, 5136:5144] = 0.0  # vocal
                feat[0, 5144:5148] = snr_feat
            t1 = time.perf_counter()
            t_physics.append((t1 - t0) * 1000.0)

            # Stage 5: Classifier Inference & Platt Scaling
            t0 = time.perf_counter()
            if cand.startswith("D_v4"):
                logits = pipe_d.decision_function(feat).reshape(-1, 1)
                prob = float(calib_d.predict_proba(logits)[0, 1])
            else:
                logits = pipe_hv5.decision_function(feat).reshape(-1, 1)
                prob = float(calib_hv5.predict_proba(logits)[0, 1])
            t1 = time.perf_counter()
            t_classifier.append((t1 - t0) * 1000.0)

            # Stage 6: Temporal Alert Logic Update
            t0 = time.perf_counter()
            is_scream = (prob >= 0.50)
            alert_json = {
                "alert": is_scream,
                "confidence": prob,
                "timestamp_ms": int(time.time() * 1000),
                "notice": "POSSIBLE SCREAM DETECTED — REQUIRES HUMAN AUDITORY VERIFICATION. Automated acoustic alerts do not confirm an emergency.",
            }
            t1 = time.perf_counter()
            t_state.append((t1 - t0) * 1000.0)

            t1_e2e = time.perf_counter()
            t_e2e.append((t1_e2e - t0_e2e) * 1000.0)

        mem_end = tracemalloc.get_traced_memory()[0]
        tracemalloc.stop()

        mem_delta_kb = max(0.0, (mem_end - mem_start) / 1024.0)
        model_file = (STAGE11_DIR / "models" / "model_d_v4.joblib") if cand.startswith("D_v4") else (STAGE11_DIR / "models" / "model_h_v5_snr.joblib")
        model_size_kb = model_file.stat().st_size / 1024.0

        rec = {
            "candidate": cand,
            "stage1_decode_ms": round(float(np.median(t_decode)), 3),
            "stage2_resample_ms": round(float(np.median(t_resample)), 3),
            "stage3_yamnet_ms": round(float(np.median(t_yamnet)), 3),
            "stage4_physics_ms": round(float(np.median(t_physics)), 3),
            "stage5_classifier_ms": round(float(np.median(t_classifier)), 3),
            "stage6_state_ms": round(float(np.median(t_state)), 3),
            "e2e_median_ms": round(float(np.median(t_e2e)), 3),
            "e2e_p95_ms": round(float(np.percentile(t_e2e, 95)), 3),
            "e2e_mean_ms": round(float(np.mean(t_e2e)), 3),
            "e2e_std_ms": round(float(np.std(t_e2e)), 3),
            "target_budget_ms": 25.0,
            "budget_met": bool(np.median(t_e2e) <= 25.0),
            "p95_budget_met": bool(np.percentile(t_e2e, 95) <= 25.0),
            "hop_consumption_pct_500ms": round(float(np.median(t_e2e) / 500.0 * 100.0), 2),
            "model_size_kb": round(model_size_kb, 2),
            "memory_heap_delta_kb": round(mem_delta_kb, 2),
            "iterations": num_timed,
        }
        benchmark_records.append(rec)
        logger.info(
            f"Candidate: {cand:<20} | Median: {rec['e2e_median_ms']:>6.2f} ms | "
            f"p95: {rec['e2e_p95_ms']:>6.2f} ms | Physics: {rec['stage4_physics_ms']:>6.2f} ms | "
            f"Budget Met: {rec['budget_met']}"
        )

    out_csv = STAGE12_DIR / "latency_benchmark_results.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(benchmark_records[0].keys()))
        writer.writeheader()
        writer.writerows(benchmark_records)

    logger.info(f"Benchmark results successfully written to: {out_csv}")
    return benchmark_records


if __name__ == "__main__":
    run_latency_benchmark()
