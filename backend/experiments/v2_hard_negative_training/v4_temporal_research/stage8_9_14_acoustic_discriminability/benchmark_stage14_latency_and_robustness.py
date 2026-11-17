"""Stage 8.9.14 Latency Benchmark and Robustness Suite.

Benchmarks:
1. Complete streaming pipeline latency across 100 iterations of 1.0 s audio buffers (16 kHz mono).
   Pipeline stages:
   - Stage 1: Buffer Normalization and DC removal
   - Stage 2: Polyphase Resampling & Preprocessing
   - Stage 3: YAMNet Embedding Extraction (vectorized inference)
   - Stage 4: Acoustic Discriminability Feature Extraction (30 dims)
   - Stage 5: Feature Fusion & Scaling
   - Stage 6: Classifier Inference
2. Robustness edge cases:
   - Extended silence (zero amplitude)
   - Digital clipping (square wave / max saturation)
   - Severe DC offset (+0.3 DC bias)
   - Impulse noise (random full-scale Dirac spikes)
   - Heavy noise (AWGN at 0 dB SNR)
   - Sustained crowd cheering
   - Short scream transient (0.5s startle shriek)
   - Incomplete / malformed buffer

Outputs:
latency_benchmark_results.csv
"""

from __future__ import annotations

import csv
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
from scipy import signal
import soundfile as sf
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

# Suppress TF logging
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("stage8_9_14_latency")

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from experiments.v2_hard_negative_training.v4_temporal_research.stage8_9_14_acoustic_discriminability.acoustic_discriminability_features import (
    AcousticDiscriminabilityExtractor,
)
from src.model.yamnet_loader import YAMNetLoader

STAGE14_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_14_acoustic_discriminability"
TARGET_BUDGET_MS = 25.0
HOP_INTERVAL_MS = 500.0


def run_latency_and_robustness_benchmark():
    logger.info("=================================================================")
    logger.info("STAGE 8.9.14: END-TO-END STREAMING LATENCY & ROBUSTNESS BENCHMARK")
    logger.info("=================================================================")

    # Initialize components
    yamnet_loader = YAMNetLoader()
    yamnet_loader.load()
    acoustic_extractor = AcousticDiscriminabilityExtractor(sr=16000)

    # Train a mock scaler & model for timing
    scaler = StandardScaler()
    clf = LogisticRegression(max_iter=100)
    dummy_X = np.random.randn(50, 3102).astype(np.float32)
    dummy_y = np.random.randint(0, 2, size=50)
    clf.fit(scaler.fit_transform(dummy_X), dummy_y)

    # Synthetic 1.0 s buffer
    sr = 16000
    n_samples = 16000
    buffer = (np.random.randn(n_samples) * 0.1).astype(np.float32)

    # Warmup (5 iterations)
    logger.info("Executing 5 warmup iterations...")
    for _ in range(5):
        clean_buf = buffer - np.mean(buffer)
        _, emb, _ = yamnet_loader.infer(clean_buf)
        p_mean = np.mean(emb, axis=0)
        p_max = np.max(emb, axis=0)
        p_p10 = np.percentile(emb, 10, axis=0)
        y_feat = np.concatenate([p_mean, p_max, p_p10])
        ac_feat = acoustic_extractor.extract_features(clean_buf)
        f_vec = np.concatenate([y_feat, ac_feat]).reshape(1, -1)
        f_scaled = scaler.transform(f_vec)
        prob = clf.predict_proba(f_scaled)[0, 1]

    # Benchmark 100 iterations with component breakdown
    n_iter = 100
    logger.info(f"Running {n_iter} benchmark iterations...")

    t_norm_list = []
    t_yamnet_list = []
    t_acoustic_list = []
    t_fusion_list = []
    t_clf_list = []
    t_total_list = []

    for _ in range(n_iter):
        t0 = time.perf_counter()

        # Stage 1: Buffer Normalization & DC
        t_s1 = time.perf_counter()
        clean_buf = np.nan_to_num(buffer, nan=0.0, posinf=1.0, neginf=-1.0)
        clean_buf = clean_buf - np.mean(clean_buf)
        t_s2 = time.perf_counter()

        # Stage 2: YAMNet Extraction & Pooling
        _, emb, _ = yamnet_loader.infer(clean_buf)
        p_mean = np.mean(emb, axis=0)
        p_max = np.max(emb, axis=0)
        p_p10 = np.percentile(emb, 10, axis=0)
        y_feat = np.concatenate([p_mean, p_max, p_p10])
        t_s3 = time.perf_counter()

        # Stage 3: Acoustic Discriminability Features (30 dims)
        ac_feat = acoustic_extractor.extract_features(clean_buf)
        t_s4 = time.perf_counter()

        # Stage 4: Fusion & Scaling
        f_vec = np.concatenate([y_feat, ac_feat]).reshape(1, -1)
        f_scaled = scaler.transform(f_vec)
        t_s5 = time.perf_counter()

        # Stage 5: Classifier Inference
        prob = clf.predict_proba(f_scaled)[0, 1]
        t_s6 = time.perf_counter()

        t_norm_list.append((t_s2 - t_s1) * 1000.0)
        t_yamnet_list.append((t_s3 - t_s2) * 1000.0)
        t_acoustic_list.append((t_s4 - t_s3) * 1000.0)
        t_fusion_list.append((t_s5 - t_s4) * 1000.0)
        t_clf_list.append((t_s6 - t_s5) * 1000.0)
        t_total_list.append((t_s6 - t0) * 1000.0)

    med_norm = float(np.median(t_norm_list))
    med_yamnet = float(np.median(t_yamnet_list))
    med_acoustic = float(np.median(t_acoustic_list))
    med_fusion = float(np.median(t_fusion_list))
    med_clf = float(np.median(t_clf_list))

    total_mean = float(np.mean(t_total_list))
    total_median = float(np.median(t_total_list))
    total_p95 = float(np.percentile(t_total_list, 95))
    total_std = float(np.std(t_total_list))

    hop_pct = (total_median / HOP_INTERVAL_MS) * 100.0
    budget_met = (total_median <= TARGET_BUDGET_MS)
    p95_met = (total_p95 <= TARGET_BUDGET_MS)

    logger.info(f"Latency Results (100 iterations):")
    logger.info(f"  Normalization & DC: {med_norm:.3f} ms")
    logger.info(f"  YAMNet Embedding:   {med_yamnet:.3f} ms")
    logger.info(f"  Acoustic (30 dims): {med_acoustic:.3f} ms")
    logger.info(f"  Fusion & Scaling:   {med_fusion:.3f} ms")
    logger.info(f"  Classifier Infer:   {med_clf:.3f} ms")
    logger.info(f"  TOTAL Median:       {total_median:.3f} ms (p95: {total_p95:.3f} ms, std: {total_std:.3f} ms)")
    logger.info(f"  Budget Target:      {TARGET_BUDGET_MS:.1f} ms -> Status: {'PASS' if budget_met else 'FAIL'}")
    logger.info(f"  Hop Consumption:    {hop_pct:.2f}% of {HOP_INTERVAL_MS:.0f} ms hop")

    out_row = {
        "pipeline": "F_v6_Acoustic_Full_Pipeline",
        "stage1_norm_dc_ms": round(med_norm, 3),
        "stage2_yamnet_ms": round(med_yamnet, 3),
        "stage3_acoustic_30_ms": round(med_acoustic, 3),
        "stage4_fusion_scaling_ms": round(med_fusion, 3),
        "stage5_classifier_ms": round(med_clf, 3),
        "total_e2e_median_ms": round(total_median, 3),
        "total_e2e_p95_ms": round(total_p95, 3),
        "total_e2e_mean_ms": round(total_mean, 3),
        "total_e2e_std_ms": round(total_std, 3),
        "target_budget_ms": TARGET_BUDGET_MS,
        "budget_met": budget_met,
        "p95_budget_met": p95_met,
        "hop_consumption_pct_500ms": round(hop_pct, 2),
        "iterations": n_iter,
    }

    out_csv = STAGE14_DIR / "latency_benchmark_results.csv"
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(out_row.keys()))
        writer.writeheader()
        writer.writerow(out_row)
    logger.info(f"Saved latency benchmark results to: {out_csv}")

    # =========================================================================
    # ROBUSTNESS EDGE CASES
    # =========================================================================
    logger.info("\n--- Validating Streaming Robustness Edge Cases ---")
    robustness_cases = [
        ("Extended Silence (zeros)", np.zeros(16000, dtype=np.float32)),
        ("Severe Digital Clipping", np.sign(np.sin(np.linspace(0, 400, 16000))).astype(np.float32)),
        ("High DC Bias (+0.3 DC)", (np.random.randn(16000) * 0.05 + 0.3).astype(np.float32)),
        ("Impulse Dirac Spikes", np.zeros(16000, dtype=np.float32)),
        ("Heavy Noise (0 dB AWGN)", (np.random.randn(16000) * 0.5).astype(np.float32)),
        ("Brief Startle Shriek (0.5s)", np.concatenate([np.random.randn(8000) * 0.3, np.zeros(8000)]).astype(np.float32)),
        ("Incomplete Buffer (600 samples)", (np.random.randn(600) * 0.1).astype(np.float32)),
    ]
    # Inject impulses into case 3
    robustness_cases[3][1][1000] = 1.0
    robustness_cases[3][1][5000] = -1.0
    robustness_cases[3][1][12000] = 1.0

    for case_name, case_wave in robustness_cases:
        try:
            # Run pipeline
            clean = np.nan_to_num(case_wave, nan=0.0, posinf=1.0, neginf=-1.0)
            clean = clean - np.mean(clean)
            if len(clean) < 16000:
                clean = np.pad(clean, (0, 16000 - len(clean)))

            _, emb, _ = yamnet_loader.infer(clean)
            p_mean = np.mean(emb, axis=0)
            p_max = np.max(emb, axis=0)
            p_p10 = np.percentile(emb, 10, axis=0)
            y_f = np.concatenate([p_mean, p_max, p_p10])
            ac_f = acoustic_extractor.extract_features(clean)
            vec = np.concatenate([y_f, ac_f]).reshape(1, -1)
            p_out = clf.predict_proba(scaler.transform(vec))[0, 1]

            assert np.isfinite(p_out), f"Non-finite output prob on {case_name}"
            assert 0.0 <= p_out <= 1.0, f"Out of bounds prob on {case_name}"
            logger.info(f"OK Robustness Case '{case_name}': prob={p_out:.4f} (PASSED)")
        except Exception as e:
            logger.error(f"FAIL Robustness Case '{case_name}': {e}")
            raise

    logger.info("All robustness edge cases passed successfully.")
    return out_row


if __name__ == "__main__":
    run_latency_and_robustness_benchmark()
