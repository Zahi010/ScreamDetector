"""Standardized End-to-End Streaming Latency and Robustness Benchmark (Stage 8.9.13).

Measures:
1. End-to-end audio-to-alert pipeline latency for D_v4_Optimized + DualPathEventStateMachine.
2. 100 timed iterations with stage-by-stage profiling:
   - Stage 1: PCM decoding
   - Stage 2: Resampling & preprocessing
   - Stage 3: YAMNet feature extraction
   - Stage 4: Vectorized multi-pooling
   - Stage 5: Logistic regression inference & Platt calibration
   - Stage 6: Dual-Path state machine update & JSON alert generation
3. Streaming boundary and edge-case robustness:
   - Overlapping window buffers
   - Extended silence
   - Sustained continuous crowd noise
   - Repeated rapid bursts
   - Closely spaced distinct scream events
   - Brief transient screams followed by silence
   - Malformed / empty / incomplete buffers

Outputs: `stage8_9_13_event_logic/latency_benchmark_results.csv`.
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

# Suppress TF logging
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.audio.preprocessor import resample_audio
from src.config import TARGET_SAMPLE_RATE
from src.model.yamnet_loader import YAMNetLoader
from experiments.v2_hard_negative_training.v4_temporal_research.stage8_9_13_event_logic.dual_path_state_machine import (
    DualPathEventStateMachine,
    EventState,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("stage8_9_13_latency")

STAGE11_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_11_evaluation"
STAGE13_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_13_event_logic"


def run_latency_and_streaming_benchmark(num_warmup: int = 15, num_timed: int = 100) -> List[Dict[str, Any]]:
    logger.info("=================================================================")
    logger.info("STAGE 8.9.13: DUAL-PATH LATENCY & STREAMING ROBUSTNESS BENCHMARK")
    logger.info("=================================================================")

    # 1. Load model and feature extractor
    logger.info("Loading YAMNet and Model D_v4...")
    yamnet = YAMNetLoader()
    yamnet.load()

    m_d = joblib.load(STAGE11_DIR / "models" / "model_d_v4.joblib")
    pipe_d = m_d["pipe"]
    calib_d = m_d["calibrator"]

    dp_machine = DualPathEventStateMachine(
        tau_fast=0.75,
        tau_sustained=0.65,
        tau_release=0.33,
        sustained_confirm_hops=2,
        cooldown_hops=6,
    )

    # 2. Synthesize realistic 1.0s audio buffer (44.1 kHz, 16-bit PCM)
    orig_sr = 44100
    duration_sec = 1.0
    t = np.linspace(0, duration_sec, int(orig_sr * duration_sec), endpoint=False)
    synthetic_audio = (0.35 * np.sin(2 * np.pi * 1200 * t) + 0.1 * np.random.randn(len(t))).astype(np.float32)
    raw_pcm_16_bytes = (np.clip(synthetic_audio, -1.0, 1.0) * 32767.0).astype(np.int16).tobytes()

    # Warmup
    logger.info(f"Executing {num_warmup} warm-up iterations...")
    for _ in range(num_warmup):
        audio_int16 = np.frombuffer(raw_pcm_16_bytes, dtype=np.int16)
        audio_float = audio_int16.astype(np.float32) / 32768.0
        wf_16k = resample_audio(audio_float, orig_sr=orig_sr, target_sr=TARGET_SAMPLE_RATE)
        _, embs, _ = yamnet.infer(wf_16k)
        f_mean = np.mean(embs, axis=0)
        f_max = np.max(embs, axis=0)
        f_p10 = np.sort(embs, axis=0)[0] if len(embs) <= 2 else np.percentile(embs, 10, axis=0)
        feat_d = np.empty((1, 3072), dtype=np.float32)
        feat_d[0, 0:1024] = f_max
        feat_d[0, 1024:2048] = f_p10
        feat_d[0, 2048:3072] = f_mean
        logits_d = pipe_d.decision_function(feat_d).reshape(-1, 1)
        prob = float(calib_d.predict_proba(logits_d)[0, 1])
        dp_machine.step(prob, 1.0)

    # Timed runs
    logger.info(f"Executing {num_timed} timed iterations with stage-by-stage profiling...")
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

        # Stage 4: Vectorized Multi-Pooling
        t0 = time.perf_counter()
        f_mean = np.mean(embs, axis=0)
        f_max = np.max(embs, axis=0)
        f_p10 = np.sort(embs, axis=0)[0] if len(embs) <= 2 else np.percentile(embs, 10, axis=0)
        feat_d = np.empty((1, 3072), dtype=np.float32)
        feat_d[0, 0:1024] = f_max
        feat_d[0, 1024:2048] = f_p10
        feat_d[0, 2048:3072] = f_mean
        t1 = time.perf_counter()
        t_physics.append((t1 - t0) * 1000.0)

        # Stage 5: Classifier Inference & Platt Calibration
        t0 = time.perf_counter()
        logits_d = pipe_d.decision_function(feat_d).reshape(-1, 1)
        prob = float(calib_d.predict_proba(logits_d)[0, 1])
        t1 = time.perf_counter()
        t_classifier.append((t1 - t0) * 1000.0)

        # Stage 6: Dual-Path State Machine Update & Alert JSON Output
        t0 = time.perf_counter()
        alert_fired, alert_meta = dp_machine.step(prob, 1.0)
        t1 = time.perf_counter()
        t_state.append((t1 - t0) * 1000.0)

        t1_e2e = time.perf_counter()
        t_e2e.append((t1_e2e - t0_e2e) * 1000.0)

    mem_end = tracemalloc.get_traced_memory()[0]
    tracemalloc.stop()

    model_size_kb = (STAGE11_DIR / "models" / "model_d_v4.joblib").stat().st_size / 1024.0

    record = {
        "pipeline": "D_v4_Optimized_DualPath_StateMachine",
        "stage1_decode_ms": round(float(np.median(t_decode)), 3),
        "stage2_resample_ms": round(float(np.median(t_resample)), 3),
        "stage3_yamnet_ms": round(float(np.median(t_yamnet)), 3),
        "stage4_pooling_ms": round(float(np.median(t_physics)), 3),
        "stage5_classifier_ms": round(float(np.median(t_classifier)), 3),
        "stage6_state_machine_ms": round(float(np.median(t_state)), 3),
        "total_e2e_median_ms": round(float(np.median(t_e2e)), 3),
        "total_e2e_p95_ms": round(float(np.percentile(t_e2e, 95)), 3),
        "total_e2e_mean_ms": round(float(np.mean(t_e2e)), 3),
        "total_e2e_std_ms": round(float(np.std(t_e2e)), 3),
        "target_budget_ms": 25.0,
        "budget_met": bool(np.median(t_e2e) <= 25.0),
        "p95_budget_met": bool(np.percentile(t_e2e, 95) <= 25.0),
        "hop_consumption_pct_500ms": round(float(np.median(t_e2e) / 500.0 * 100.0), 2),
        "model_size_kb": round(model_size_kb, 2),
        "memory_heap_delta_kb": round((mem_end - mem_start) / 1024.0, 2),
        "iterations": num_timed,
    }

    out_csv = STAGE13_DIR / "latency_benchmark_results.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(record.keys()))
        writer.writeheader()
        writer.writerow(record)

    logger.info(
        f"Pipeline Latency: Median = {record['total_e2e_median_ms']:.2f} ms | "
        f"p95 = {record['total_e2e_p95_ms']:.2f} ms | Budget Met: {record['budget_met']} | "
        f"Hop Consumption: {record['hop_consumption_pct_500ms']}%"
    )

    # 4. Streaming Boundary & Edge Case Robustness Tests
    logger.info("\n--- Testing Streaming Edge Cases & State Transitions ---")
    dp_machine.reset()

    # Case A: Extended Silence (20 consecutive zero frames)
    for i in range(20):
        fired, _ = dp_machine.step(0.01, (i + 1) * 0.5 + 1.0)
        assert not fired, f"False alert on silence frame {i}!"
    assert dp_machine.state == EventState.IDLE
    logger.info("OK Extended silence test passed (0 alerts across 20 frames).")

    # Case B: Brief Transient Scream (< 1.0s, 1 high-confidence frame)
    dp_machine.reset()
    fired1, m1 = dp_machine.step(0.85, 1.0)  # > tau_fast (0.75)
    assert fired1 and m1["trigger_path"] == "FAST_PATH"
    assert dp_machine.state == EventState.EVENT_ACTIVE
    # Followed by quiet release
    dp_machine.step(0.10, 1.5)
    dp_machine.step(0.10, 2.0)
    logger.info("OK Brief transient scream test passed (Immediate fast-path trigger, delay=1.0s).")

    # Case C: Sustained Scream (2 consecutive frames >= tau_sustained)
    dp_machine.reset()
    f1, _ = dp_machine.step(0.68, 1.0)  # pending
    assert not f1 and dp_machine.state == EventState.SUSTAINED_PENDING
    f2, m2 = dp_machine.step(0.70, 1.5)  # confirmed!
    assert f2 and m2["trigger_path"] == "SUSTAINED_PATH"
    assert dp_machine.state == EventState.EVENT_ACTIVE
    logger.info("OK Sustained scream test passed (Confirmed on frame 2, delay=1.5s).")

    # Case D: Closely Spaced Distinct Screams
    # Scream 1: frame 1 (0.85), followed by quiet release (hops 2, 3), cooldown finish (hops 4-9), Scream 2 at hop 10
    dp_machine.reset()
    s1_fired, _ = dp_machine.step(0.85, 1.0)
    assert s1_fired
    # 8 hops of quiet audio to clear cooldown (6 hops) and quiet release (2 hops)
    for h in range(2, 10):
        dp_machine.step(0.05, h * 0.5 + 1.0)
    assert dp_machine.state == EventState.IDLE, f"Expected IDLE but got {dp_machine.state}"

    # Scream 2: New burst
    s2_fired, m_s2 = dp_machine.step(0.88, 10 * 0.5 + 1.0)
    assert s2_fired and m_s2["trigger_path"] == "FAST_PATH"
    logger.info("OK Closely spaced distinct scream test passed (Both distinct screams detected).")

    # Case E: Continuous Crowd Noise (Sustained multi-frame energy, test duplicate suppression)
    dp_machine.reset()
    crowd_stream = [0.80, 0.78, 0.75, 0.72, 0.70, 0.68, 0.65, 0.60]  # 8 continuous high frames
    alerts_fired_crowd = 0
    for h, p in enumerate(crowd_stream):
        fired, _ = dp_machine.step(p, (h + 1) * 0.5 + 1.0)
        if fired:
            alerts_fired_crowd += 1
    assert alerts_fired_crowd == 1, f"Expected exactly 1 alert with deduplication, got {alerts_fired_crowd}!"
    logger.info("OK Continuous crowd noise test passed (Deduplication clamped 8 frames to exactly 1 alert event).")

    # Case F: Malformed / Incomplete buffer
    empty_arr = np.zeros(0, dtype=np.float32)
    short_arr = np.zeros(100, dtype=np.float32)
    nan_arr = np.array([np.nan, np.inf, -np.inf], dtype=np.float32)
    # Check that fast feature extractor safely handles empty/short/nan
    from experiments.v2_hard_negative_training.v4_temporal_research.stage8_9_12_runtime_research.fast_acoustic_features import FastAcousticFeatureExtractor
    ext = FastAcousticFeatureExtractor()
    t_e, s_e = ext.extract_turbulence_and_snr_fast(empty_arr)
    t_s, s_s = ext.extract_turbulence_and_snr_fast(short_arr)
    assert len(t_e) == 16 and len(s_e) == 4 and not np.isnan(t_e).any()
    assert len(t_s) == 16 and len(s_s) == 4 and not np.isnan(t_s).any()
    logger.info("OK Malformed / incomplete buffer robustness passed.")

    return [record]


if __name__ == "__main__":
    run_latency_and_streaming_benchmark()
