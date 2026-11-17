"""Standardized End-to-End Latency Benchmark for Stage 8.9.11.

Measures complete audio-to-alert pipeline on target hardware:
1. Audio input and decoding (16-bit PCM waveform)
2. Resampling and preprocessing
3. YAMNet feature extraction
4. Turbulence STFT and adaptive SNR feature extraction
5. Classifier evaluation and Platt scaling calibration
6. Output thresholding and alert state machine

Separates classifier-only latency from full end-to-end pipeline latency.
Outputs: `stage8_9_11_evaluation/reports/end_to_end_latency_results.json`.
"""

from __future__ import annotations

import io
import json
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

from src.audio.preprocessor import load_audio, resample_audio
from src.config import TARGET_SAMPLE_RATE
from src.model.yamnet_loader import YAMNetLoader
from experiments.v2_hard_negative_training.v4_temporal_research.extract_temporal_and_turbulence_features import (
    extract_16_turbulence_features,
)
from experiments.v2_hard_negative_training.v4_temporal_research.stage8_9_11_evaluation.extract_stage8_9_11_features import (
    compute_snr_features,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("stage8_9_11_latency")

STAGE11_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_11_evaluation"
MODELS_DIR = STAGE11_DIR / "models"
REPORTS_DIR = STAGE11_DIR / "reports"


def run_latency_benchmark(num_warmup: int = 10, num_timed: int = 50) -> Dict[str, Any]:
    logger.info("=================================================================")
    logger.info("STAGE 8.9.11: STANDARDIZED END-TO-END PIPELINE LATENCY BENCHMARK")
    logger.info("=================================================================")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load runtime dependencies
    logger.info("Loading YAMNet feature extractor and Candidate H_v5_SNR model...")
    yamnet = YAMNetLoader()
    yamnet.load()

    model_bundle = joblib.load(MODELS_DIR / "model_h_v5_snr.joblib")
    pipe = model_bundle["pipe"]
    calibrator = model_bundle["calibrator"]

    # Also load Model D_v4 for comparison
    model_d_bundle = joblib.load(MODELS_DIR / "model_d_v4.joblib")
    pipe_d = model_d_bundle["pipe"]
    calibrator_d = model_d_bundle["calibrator"]

    # Serialized file sizes
    size_hv5_bytes = (MODELS_DIR / "model_h_v5_snr.joblib").stat().st_size
    size_d_bytes = (MODELS_DIR / "model_d_v4.joblib").stat().st_size

    # Synthesize realistic 1.0-second 16-bit PCM audio test buffer at 44.1 kHz (simulating raw mic stream)
    orig_sr = 44100
    duration_sec = 1.0
    t = np.linspace(0, duration_sec, int(orig_sr * duration_sec), endpoint=False)
    synthetic_audio = (0.5 * np.sin(2 * np.pi * 1000 * t) + 0.2 * np.random.randn(len(t))).astype(np.float32)
    raw_pcm_16_bytes = (np.clip(synthetic_audio, -1.0, 1.0) * 32767.0).astype(np.int16).tobytes()

    logger.info(f"Test Audio Buffer: {len(raw_pcm_16_bytes)} bytes PCM 16-bit ({orig_sr} Hz, {duration_sec}s window)")

    # Warmup runs
    logger.info(f"Executing {num_warmup} warm-up iterations...")
    for _ in range(num_warmup):
        # Decode
        audio_int16 = np.frombuffer(raw_pcm_16_bytes, dtype=np.int16)
        audio_float = audio_int16.astype(np.float32) / 32768.0
        # Resample
        wf_16k = resample_audio(audio_float, orig_sr=orig_sr, target_sr=TARGET_SAMPLE_RATE)
        # YAMNet
        _, embs, _ = yamnet.infer(wf_16k)
        # Features
        f_mean = np.mean(embs, axis=0)
        f_max = np.max(embs, axis=0)
        f_p10 = np.percentile(embs, 10, axis=0)
        f_concat = np.concatenate([f_max, f_p10, f_mean]).reshape(1, -1)
        f_std = np.std(embs, axis=0).reshape(1, -1)
        f_delta = np.zeros((1, 1024), dtype=np.float32)
        turb = extract_16_turbulence_features(wf_16k, sr=TARGET_SAMPLE_RATE).reshape(1, -1)
        snr_feat = compute_snr_features(wf_16k, sr=TARGET_SAMPLE_RATE).reshape(1, -1)
        vocal_feat = np.zeros((1, 6), dtype=np.float32)
        v_logit = np.zeros((1, 1), dtype=np.float32)
        c_logit = np.zeros((1, 1), dtype=np.float32)

        feat_hv5 = np.hstack([f_concat, f_std, f_delta, turb, v_logit, c_logit, vocal_feat, snr_feat])
        raw_logits = pipe.decision_function(feat_hv5).reshape(-1, 1)
        prob = calibrator.predict_proba(raw_logits)[0, 1]
        alert = (prob >= 0.51)

    # Timed runs
    logger.info(f"Executing {num_timed} timed iterations with stage-by-stage profiling...")
    t_stage1_decode = []
    t_stage2_resample = []
    t_stage3_yamnet = []
    t_stage4_physics = []
    t_stage5_classifier_hv5 = []
    t_stage5_classifier_d = []
    t_stage6_alert = []
    t_total_e2e_hv5 = []
    t_total_e2e_d = []

    tracemalloc.start()
    mem_before = tracemalloc.get_traced_memory()[0]

    for _ in range(num_timed):
        t0_e2e = time.perf_counter()

        # Stage 1: Audio Input & Decoding
        t0 = time.perf_counter()
        audio_int16 = np.frombuffer(raw_pcm_16_bytes, dtype=np.int16)
        audio_float = audio_int16.astype(np.float32) / 32768.0
        t1 = time.perf_counter()
        t_stage1_decode.append((t1 - t0) * 1000.0)

        # Stage 2: Resampling & Preprocessing
        t0 = time.perf_counter()
        wf_16k = resample_audio(audio_float, orig_sr=orig_sr, target_sr=TARGET_SAMPLE_RATE)
        t1 = time.perf_counter()
        t_stage2_resample.append((t1 - t0) * 1000.0)

        # Stage 3: YAMNet Feature Extraction
        t0 = time.perf_counter()
        _, embs, _ = yamnet.infer(wf_16k)
        t1 = time.perf_counter()
        t_stage3_yamnet.append((t1 - t0) * 1000.0)

        # Stage 4: Turbulence & Adaptive SNR Features
        t0 = time.perf_counter()
        f_mean = np.mean(embs, axis=0)
        f_max = np.max(embs, axis=0)
        f_p10 = np.percentile(embs, 10, axis=0)
        f_concat = np.concatenate([f_max, f_p10, f_mean]).reshape(1, -1)
        f_std = np.std(embs, axis=0).reshape(1, -1)
        f_delta = np.zeros((1, 1024), dtype=np.float32)
        turb = extract_16_turbulence_features(wf_16k, sr=TARGET_SAMPLE_RATE).reshape(1, -1)
        snr_feat = compute_snr_features(wf_16k, sr=TARGET_SAMPLE_RATE).reshape(1, -1)
        vocal_feat = np.zeros((1, 6), dtype=np.float32)
        v_logit = np.zeros((1, 1), dtype=np.float32)
        c_logit = np.zeros((1, 1), dtype=np.float32)
        feat_hv5 = np.hstack([f_concat, f_std, f_delta, turb, v_logit, c_logit, vocal_feat, snr_feat])
        t1 = time.perf_counter()
        t_stage4_physics.append((t1 - t0) * 1000.0)

        # Stage 5A: Classifier Inference & Platt Calibration (Model H_v5_SNR)
        t0 = time.perf_counter()
        raw_logits_hv5 = pipe.decision_function(feat_hv5).reshape(-1, 1)
        prob_hv5 = calibrator.predict_proba(raw_logits_hv5)[0, 1]
        t1 = time.perf_counter()
        t_stage5_classifier_hv5.append((t1 - t0) * 1000.0)

        # Stage 5B: Classifier Inference & Platt Calibration (Model D_v4)
        t0 = time.perf_counter()
        raw_logits_d = pipe_d.decision_function(f_concat).reshape(-1, 1)
        prob_d = calibrator_d.predict_proba(raw_logits_d)[0, 1]
        t1 = time.perf_counter()
        t_stage5_classifier_d.append((t1 - t0) * 1000.0)

        # Stage 6: Alert Thresholding & Output Logic
        t0 = time.perf_counter()
        alert_state = (prob_hv5 >= 0.5100)
        json_output = json.dumps({"timestamp": time.time(), "scream_detected": bool(alert_state), "score": round(float(prob_hv5), 4)})
        t1 = time.perf_counter()
        t_stage6_alert.append((t1 - t0) * 1000.0)

        t1_e2e = time.perf_counter()
        t_total_e2e_hv5.append((t1_e2e - t0_e2e) * 1000.0)
        t_total_e2e_d.append(
            (t_stage1_decode[-1] + t_stage2_resample[-1] + t_stage3_yamnet[-1] + t_stage5_classifier_d[-1] + t_stage6_alert[-1])
        )

    mem_peak = tracemalloc.get_traced_memory()[1] - mem_before
    tracemalloc.stop()

    def stats_dict(arr):
        return {
            "median_ms": round(float(np.median(arr)), 3),
            "p95_ms": round(float(np.percentile(arr, 95)), 3),
            "min_ms": round(float(np.min(arr)), 3),
            "max_ms": round(float(np.max(arr)), 3),
        }

    report = {
        "hardware_environment": {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "sample_rate_input_hz": orig_sr,
            "sample_rate_target_hz": TARGET_SAMPLE_RATE,
            "window_duration_seconds": duration_sec,
            "hop_interval_seconds": 0.5,
            "timed_iterations": num_timed,
            "warmup_iterations": num_warmup,
        },
        "stage_breakdown_ms": {
            "stage_1_decoding": stats_dict(t_stage1_decode),
            "stage_2_resampling": stats_dict(t_stage2_resample),
            "stage_3_yamnet": stats_dict(t_stage3_yamnet),
            "stage_4_physics_turbulence": stats_dict(t_stage4_physics),
            "stage_5_classifier_hv5": stats_dict(t_stage5_classifier_hv5),
            "stage_5_classifier_d_v4": stats_dict(t_stage5_classifier_d),
            "stage_6_output_alert": stats_dict(t_stage6_alert),
        },
        "pipeline_comparison": {
            "classifier_only_latency_ms": {
                "Model_D_v4": stats_dict(t_stage5_classifier_d),
                "Model_H_v5_SNR": stats_dict(t_stage5_classifier_hv5),
            },
            "total_end_to_end_latency_ms": {
                "Model_D_v4_Pipeline": stats_dict(t_total_e2e_d),
                "Model_H_v5_SNR_Pipeline": stats_dict(t_total_e2e_hv5),
            },
            "edge_budget_ms": 25.0,
            "is_within_edge_budget": float(np.percentile(t_total_e2e_hv5, 95)) < 25.0,
        },
        "resource_footprint": {
            "model_h_v5_snr_size_bytes": size_hv5_bytes,
            "model_h_v5_snr_size_kb": round(size_hv5_bytes / 1024.0, 2),
            "model_d_v4_size_bytes": size_d_bytes,
            "model_d_v4_size_kb": round(size_d_bytes / 1024.0, 2),
            "peak_inference_memory_kb": round(mem_peak / 1024.0, 2),
        },
    }

    out_json = REPORTS_DIR / "end_to_end_latency_results.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    logger.info(f"\n=================================================================")
    logger.info(f"LATENCY BENCHMARK RESULTS (50 Iterations on {duration_sec}s Window):")
    logger.info(f"  Stage 1 (Decode):         {report['stage_breakdown_ms']['stage_1_decoding']['median_ms']:.3f} ms")
    logger.info(f"  Stage 2 (Resample):       {report['stage_breakdown_ms']['stage_2_resampling']['median_ms']:.3f} ms")
    logger.info(f"  Stage 3 (YAMNet):         {report['stage_breakdown_ms']['stage_3_yamnet']['median_ms']:.3f} ms")
    logger.info(f"  Stage 4 (Turbulence/SNR): {report['stage_breakdown_ms']['stage_4_physics_turbulence']['median_ms']:.3f} ms")
    logger.info(f"  Stage 5 (Classifier H5):  {report['stage_breakdown_ms']['stage_5_classifier_hv5']['median_ms']:.3f} ms")
    logger.info(f"  Stage 6 (Output Alert):   {report['stage_breakdown_ms']['stage_6_output_alert']['median_ms']:.3f} ms")
    logger.info(f"  -------------------------------------------------------------")
    logger.info(f"  Classifier-Only Latency:  {report['pipeline_comparison']['classifier_only_latency_ms']['Model_H_v5_SNR']['median_ms']:.3f} ms (p95: {report['pipeline_comparison']['classifier_only_latency_ms']['Model_H_v5_SNR']['p95_ms']:.3f} ms)")
    logger.info(f"  FULL END-TO-END LATENCY:  {report['pipeline_comparison']['total_end_to_end_latency_ms']['Model_H_v5_SNR_Pipeline']['median_ms']:.3f} ms (p95: {report['pipeline_comparison']['total_end_to_end_latency_ms']['Model_H_v5_SNR_Pipeline']['p95_ms']:.3f} ms)")
    logger.info(f"  Target Edge Budget:       25.000 ms (Met: {report['pipeline_comparison']['is_within_edge_budget']})")
    logger.info(f"  Model Size on Disk:       {report['resource_footprint']['model_h_v5_snr_size_kb']:.2f} KB")
    logger.info(f"=================================================================")

    return report


if __name__ == "__main__":
    run_latency_benchmark()
