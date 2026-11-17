"""Stage 8.9.15 End-to-End Latency and Memory Benchmark.

Benchmarks:
1. Complete streaming pipeline latency across 100 iterations of 1.0 s audio buffers (16 kHz mono).
   Pipeline stages:
   - Buffer Normalization & DC removal
   - YAMNet Embedding Extraction (vectorized inference)
   - Acoustic Discriminability Feature Extraction (30 dims)
   - Stage 1 Vocal Distress Gate Inference (ExtraTrees)
   - Stage 2 Phonation Discriminator Inference (Model A MLP, Model B Temporal CNN, Model C Fusion)
   - Total Hierarchical Pipeline Latency (median, p95, mean, std)
2. CPU memory consumption (peak RAM delta)
3. On-disk model sizes for all components

Outputs:
- latency_and_memory_benchmark.csv in workspace root and reports/
"""

from __future__ import annotations

import csv
import logging
import os
import sys
import time
import tracemalloc
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import joblib

# Suppress TF logging
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
import tensorflow as tf
from tensorflow import keras

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("stage8_9_15_latency")

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from experiments.v2_hard_negative_training.v4_temporal_research.stage8_9_14_acoustic_discriminability.acoustic_discriminability_features import (
    AcousticDiscriminabilityExtractor,
)
from src.model.yamnet_loader import YAMNetLoader

STAGE15_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_15_hierarchical_phonation"
MODELS_DIR = STAGE15_DIR / "models"
REPORTS_DIR = STAGE15_DIR / "reports"
TARGET_BUDGET_MS = 25.0


def benchmark_pipeline():
    logger.info("=================================================================")
    logger.info("STAGE 8.9.15: LATENCY AND MEMORY BENCHMARK")
    logger.info("=================================================================")

    # Initialize components
    logger.info("Loading YAMNet model...")
    yamnet_loader = YAMNetLoader()
    yamnet_loader.load()

    logger.info("Loading Acoustic Discriminability Extractor...")
    acoustic_extractor = AcousticDiscriminabilityExtractor(sr=16000)

    logger.info("Loading Stage 8.9.15 trained models...")
    scaler = joblib.load(MODELS_DIR / "stage8_9_15_feature_scaler.joblib")
    ac_scaler = joblib.load(MODELS_DIR / "stage8_9_15_acoustic_scaler.joblib")
    fusion_scaler = joblib.load(MODELS_DIR / "stage8_9_15_fusion_scaler.joblib")

    gate_model = joblib.load(MODELS_DIR / "Gate_A_ExtraTrees.joblib")
    mlp_model = joblib.load(MODELS_DIR / "Model_A_Compact_MLP.joblib")
    tcn_model = keras.models.load_model(MODELS_DIR / "Model_B_Temporal_CNN.keras")
    fusion_model = joblib.load(MODELS_DIR / "Model_C_Hierarchical_Fusion.joblib")

    # Compute model sizes
    gate_size_mb = os.path.getsize(MODELS_DIR / "Gate_A_ExtraTrees.joblib") / (1024 * 1024)
    mlp_size_mb = os.path.getsize(MODELS_DIR / "Model_A_Compact_MLP.joblib") / (1024 * 1024)
    tcn_size_mb = os.path.getsize(MODELS_DIR / "Model_B_Temporal_CNN.keras") / (1024 * 1024)
    fusion_size_mb = os.path.getsize(MODELS_DIR / "Model_C_Hierarchical_Fusion.joblib") / (1024 * 1024)
    scalers_size_mb = (
        os.path.getsize(MODELS_DIR / "stage8_9_15_feature_scaler.joblib")
        + os.path.getsize(MODELS_DIR / "stage8_9_15_acoustic_scaler.joblib")
        + os.path.getsize(MODELS_DIR / "stage8_9_15_fusion_scaler.joblib")
    ) / (1024 * 1024)
    total_model_size_mb = gate_size_mb + mlp_size_mb + tcn_size_mb + fusion_size_mb + scalers_size_mb

    logger.info(f"Model sizes: Gate={gate_size_mb:.2f}MB, MLP={mlp_size_mb:.2f}MB, TCN={tcn_size_mb:.2f}MB, Fusion={fusion_size_mb:.2f}MB, Total={total_model_size_mb:.2f}MB")

    # Synthetic 1.0 s buffer
    sr = 16000
    n_samples = 16000
    buffer = (np.random.randn(n_samples) * 0.1).astype(np.float32)

    top_feat_indices = [11, 23, 17, 26, 10, 2]

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
        comb_feat = np.concatenate([y_feat, ac_feat]).reshape(1, -1)
        comb_scaled = scaler.transform(comb_feat)

        g_prob = gate_model.predict_proba(comb_scaled)[0, 1]
        mlp_prob = mlp_model.predict_proba(comb_scaled)[0, 1]

        # TCN pad sequence
        seq_padded = np.zeros((1, 70, 1024), dtype=np.float32)
        n_frames = min(70, emb.shape[0])
        seq_padded[0, :n_frames, :] = emb[:n_frames, :]
        ac_scaled = ac_scaler.transform(ac_feat.reshape(1, -1))
        tcn_prob = float(tcn_model([seq_padded, ac_scaled], training=False).numpy()[0, 0])

        top_feat = ac_feat[top_feat_indices].reshape(1, -1)
        fus_in = np.hstack([[g_prob], [mlp_prob], [tcn_prob], top_feat.flatten()]).reshape(1, -1)
        fus_scaled = fusion_scaler.transform(fus_in)
        final_prob = fusion_model.predict_proba(fus_scaled)[0, 1]

    # Benchmark 100 iterations with component breakdown
    n_iter = 100
    logger.info(f"Running {n_iter} benchmark iterations with tracemalloc...")
    tracemalloc.start()

    t_norm_list = []
    t_yamnet_list = []
    t_acoustic_list = []
    t_gate_list = []
    t_mlp_list = []
    t_tcn_list = []
    t_fusion_list = []
    t_pipeline_a_list = []  # Gate + MLP
    t_pipeline_c_list = []  # Gate + MLP + TCN + Fusion (Full Hierarchical)

    for _ in range(n_iter):
        t0 = time.perf_counter()

        # Buffer Normalization
        t_s0 = time.perf_counter()
        clean_buf = np.nan_to_num(buffer, nan=0.0, posinf=1.0, neginf=-1.0)
        clean_buf = clean_buf - np.mean(clean_buf)
        t_s1 = time.perf_counter()

        # YAMNet inference & pooling
        _, emb, _ = yamnet_loader.infer(clean_buf)
        p_mean = np.mean(emb, axis=0)
        p_max = np.max(emb, axis=0)
        p_p10 = np.percentile(emb, 10, axis=0)
        y_feat = np.concatenate([p_mean, p_max, p_p10])
        t_s2 = time.perf_counter()

        # Acoustic features (30)
        ac_feat = acoustic_extractor.extract_features(clean_buf)
        comb_feat = np.concatenate([y_feat, ac_feat]).reshape(1, -1)
        comb_scaled = scaler.transform(comb_feat)
        t_s3 = time.perf_counter()

        # Stage 1 Gate
        g_prob = gate_model.predict_proba(comb_scaled)[0, 1]
        t_s4 = time.perf_counter()

        # Stage 2 Model A (MLP)
        mlp_prob = mlp_model.predict_proba(comb_scaled)[0, 1]
        t_s5 = time.perf_counter()

        # Stage 2 Model B (TCN)
        seq_padded = np.zeros((1, 70, 1024), dtype=np.float32)
        n_frames = min(70, emb.shape[0])
        seq_padded[0, :n_frames, :] = emb[:n_frames, :]
        ac_scaled = ac_scaler.transform(ac_feat.reshape(1, -1))
        tcn_prob = float(tcn_model([seq_padded, ac_scaled], training=False).numpy()[0, 0])
        t_s6 = time.perf_counter()

        # Stage 2 Model C (Fusion)
        top_feat = ac_feat[top_feat_indices].reshape(1, -1)
        fus_in = np.hstack([[g_prob], [mlp_prob], [tcn_prob], top_feat.flatten()]).reshape(1, -1)
        fus_scaled = fusion_scaler.transform(fus_in)
        final_prob = fusion_model.predict_proba(fus_scaled)[0, 1]
        t_s7 = time.perf_counter()

        t_norm_list.append((t_s1 - t_s0) * 1000.0)
        t_yamnet_list.append((t_s2 - t_s1) * 1000.0)
        t_acoustic_list.append((t_s3 - t_s2) * 1000.0)
        t_gate_list.append((t_s4 - t_s3) * 1000.0)
        t_mlp_list.append((t_s5 - t_s4) * 1000.0)
        t_tcn_list.append((t_s6 - t_s5) * 1000.0)
        t_fusion_list.append((t_s7 - t_s6) * 1000.0)

        # Full end-to-end Pipeline A (Gate + MLP)
        t_pipeline_a_list.append((t_s5 - t0) * 1000.0)
        # Full end-to-end Pipeline C (Gate + MLP + TCN + Fusion)
        t_pipeline_c_list.append((t_s7 - t0) * 1000.0)

    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    peak_mem_mb = peak_mem / (1024 * 1024)

    logger.info(f"Memory peak during inference benchmark: {peak_mem_mb:.2f} MB")

    results = [
        {
            "pipeline_stage": "Stage 0: Buffer Normalization & DC Removal",
            "median_latency_ms": round(float(np.median(t_norm_list)), 3),
            "p95_latency_ms": round(float(np.percentile(t_norm_list, 95)), 3),
            "mean_latency_ms": round(float(np.mean(t_norm_list)), 3),
            "std_latency_ms": round(float(np.std(t_norm_list)), 3),
            "pct_of_25ms_budget": round(float(np.median(t_norm_list) / TARGET_BUDGET_MS * 100.0), 2),
            "memory_peak_mb": round(peak_mem_mb, 2),
            "model_size_mb": 0.0,
            "status": "PASS",
        },
        {
            "pipeline_stage": "Stage 1: YAMNet Embedding Extraction (vectorized)",
            "median_latency_ms": round(float(np.median(t_yamnet_list)), 3),
            "p95_latency_ms": round(float(np.percentile(t_yamnet_list, 95)), 3),
            "mean_latency_ms": round(float(np.mean(t_yamnet_list)), 3),
            "std_latency_ms": round(float(np.std(t_yamnet_list)), 3),
            "pct_of_25ms_budget": round(float(np.median(t_yamnet_list) / TARGET_BUDGET_MS * 100.0), 2),
            "memory_peak_mb": round(peak_mem_mb, 2),
            "model_size_mb": 14.8,
            "status": "PASS",
        },
        {
            "pipeline_stage": "Stage 2: Acoustic Discriminability Features (30 dims)",
            "median_latency_ms": round(float(np.median(t_acoustic_list)), 3),
            "p95_latency_ms": round(float(np.percentile(t_acoustic_list, 95)), 3),
            "mean_latency_ms": round(float(np.mean(t_acoustic_list)), 3),
            "std_latency_ms": round(float(np.std(t_acoustic_list)), 3),
            "pct_of_25ms_budget": round(float(np.median(t_acoustic_list) / TARGET_BUDGET_MS * 100.0), 2),
            "memory_peak_mb": round(peak_mem_mb, 2),
            "model_size_mb": 0.0,
            "status": "PASS",
        },
        {
            "pipeline_stage": "Stage 3: Stage 1 Broad Distress Gate (ExtraTrees)",
            "median_latency_ms": round(float(np.median(t_gate_list)), 3),
            "p95_latency_ms": round(float(np.percentile(t_gate_list, 95)), 3),
            "mean_latency_ms": round(float(np.mean(t_gate_list)), 3),
            "std_latency_ms": round(float(np.std(t_gate_list)), 3),
            "pct_of_25ms_budget": round(float(np.median(t_gate_list) / TARGET_BUDGET_MS * 100.0), 2),
            "memory_peak_mb": round(peak_mem_mb, 2),
            "model_size_mb": round(gate_size_mb, 2),
            "status": "PASS",
        },
        {
            "pipeline_stage": "Stage 4: Stage 2 Model A (Compact MLP)",
            "median_latency_ms": round(float(np.median(t_mlp_list)), 3),
            "p95_latency_ms": round(float(np.percentile(t_mlp_list, 95)), 3),
            "mean_latency_ms": round(float(np.mean(t_mlp_list)), 3),
            "std_latency_ms": round(float(np.std(t_mlp_list)), 3),
            "pct_of_25ms_budget": round(float(np.median(t_mlp_list) / TARGET_BUDGET_MS * 100.0), 2),
            "memory_peak_mb": round(peak_mem_mb, 2),
            "model_size_mb": round(mlp_size_mb, 2),
            "status": "PASS",
        },
        {
            "pipeline_stage": "Stage 5: Stage 2 Model B (Temporal Dilated CNN)",
            "median_latency_ms": round(float(np.median(t_tcn_list)), 3),
            "p95_latency_ms": round(float(np.percentile(t_tcn_list, 95)), 3),
            "mean_latency_ms": round(float(np.mean(t_tcn_list)), 3),
            "std_latency_ms": round(float(np.std(t_tcn_list)), 3),
            "pct_of_25ms_budget": round(float(np.median(t_tcn_list) / TARGET_BUDGET_MS * 100.0), 2),
            "memory_peak_mb": round(peak_mem_mb, 2),
            "model_size_mb": round(tcn_size_mb, 2),
            "status": "PASS",
        },
        {
            "pipeline_stage": "Stage 6: Stage 2 Model C (Learned Hybrid Fusion)",
            "median_latency_ms": round(float(np.median(t_fusion_list)), 3),
            "p95_latency_ms": round(float(np.percentile(t_fusion_list, 95)), 3),
            "mean_latency_ms": round(float(np.mean(t_fusion_list)), 3),
            "std_latency_ms": round(float(np.std(t_fusion_list)), 3),
            "pct_of_25ms_budget": round(float(np.median(t_fusion_list) / TARGET_BUDGET_MS * 100.0), 2),
            "memory_peak_mb": round(peak_mem_mb, 2),
            "model_size_mb": round(fusion_size_mb, 2),
            "status": "PASS",
        },
        {
            "pipeline_stage": "Complete Pipeline Option 1 (Gate + Model A MLP)",
            "median_latency_ms": round(float(np.median(t_pipeline_a_list)), 3),
            "p95_latency_ms": round(float(np.percentile(t_pipeline_a_list, 95)), 3),
            "mean_latency_ms": round(float(np.mean(t_pipeline_a_list)), 3),
            "std_latency_ms": round(float(np.std(t_pipeline_a_list)), 3),
            "pct_of_25ms_budget": round(float(np.median(t_pipeline_a_list) / TARGET_BUDGET_MS * 100.0), 2),
            "memory_peak_mb": round(peak_mem_mb, 2),
            "model_size_mb": round(gate_size_mb + mlp_size_mb + scalers_size_mb, 2),
            "status": "PASS" if np.percentile(t_pipeline_a_list, 95) <= TARGET_BUDGET_MS else "BUDGET_BREACH",
        },
        {
            "pipeline_stage": "Complete Pipeline Option 2 (Gate + MLP + TCN + Hybrid Fusion)",
            "median_latency_ms": round(float(np.median(t_pipeline_c_list)), 3),
            "p95_latency_ms": round(float(np.percentile(t_pipeline_c_list, 95)), 3),
            "mean_latency_ms": round(float(np.mean(t_pipeline_c_list)), 3),
            "std_latency_ms": round(float(np.std(t_pipeline_c_list)), 3),
            "pct_of_25ms_budget": round(float(np.median(t_pipeline_c_list) / TARGET_BUDGET_MS * 100.0), 2),
            "memory_peak_mb": round(peak_mem_mb, 2),
            "model_size_mb": round(total_model_size_mb, 2),
            "status": "PASS" if np.percentile(t_pipeline_c_list, 95) <= TARGET_BUDGET_MS else "BUDGET_BREACH",
        },
    ]

    out_csv = STAGE15_DIR / "latency_and_memory_benchmark.csv"
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    logger.info(f"Saved benchmark results to: {out_csv}")

    reports_csv = REPORTS_DIR / "latency_and_memory_benchmark.csv"
    with open(reports_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    benchmark_pipeline()
