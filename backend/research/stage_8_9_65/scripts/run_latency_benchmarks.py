#!/usr/bin/env python3
"""
STAGE 8.9.65 — Track I: Multi-Stream Latency Benchmarking & Gate 5 Engineering Certification
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import csv
import os
import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
import psutil
import torch
import torch.nn as nn

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE57_DIR = BACKEND_DIR / "research" / "stage_8_9_57"
STAGE64_DIR = BACKEND_DIR / "research" / "stage_8_9_64"
STAGE65_DIR = BACKEND_DIR / "research" / "stage_8_9_65"

sys.path.insert(0, str(STAGE57_DIR / "dsp_implementations"))
from c5_combined import extract_subband_vector_c5, extract_phonation_stats_c5

class DualResolutionGatedModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.short_enc = nn.Sequential(
            nn.Linear(17, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(0.10),
            nn.Linear(32, 16),
            nn.ReLU()
        )
        self.sust_enc = nn.Sequential(
            nn.Linear(17, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(0.10),
            nn.Linear(32, 16),
            nn.ReLU()
        )
        self.gate_net = nn.Sequential(
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )
        self.head = nn.Linear(16, 1)

    def forward(self, x_short, x_sust):
        z_s = self.short_enc(x_short)
        z_l = self.sust_enc(x_sust)
        gate = self.gate_net(torch.cat([z_s, z_l], dim=-1))
        z_fused = gate * z_s + (1.0 - gate) * z_l
        return self.head(z_fused).squeeze(-1)

def benchmark_stream_concurrency(n_streams: int, n_iterations: int = 200):
    ckpt_path = STAGE64_DIR / "models" / "stage63_dual_resolution_gated.pt"
    model = DualResolutionGatedModel()
    if ckpt_path.exists():
        model.load_state_dict(torch.load(ckpt_path, map_location="cpu", weights_only=True))
    model.eval()

    sr = 16000
    win_len = 16000
    short_len = 4000

    dummy_buffers_1s = [np.random.normal(0, 0.1, win_len).astype(np.float32) for _ in range(n_streams)]
    dummy_buffers_short = [np.random.normal(0, 0.1, short_len).astype(np.float32) for _ in range(n_streams)]

    dsp_short_times = []
    dsp_sust_times = []
    nn_times = []
    temporal_times = []
    total_pipeline_times = []

    process = psutil.Process()
    cpu_before = process.cpu_percent(interval=None)

    # Warmup (20 iterations)
    for _ in range(20):
        t_s = torch.tensor(np.zeros((n_streams, 17)), dtype=torch.float32)
        t_l = torch.tensor(np.zeros((n_streams, 17)), dtype=torch.float32)
        with torch.no_grad():
            _ = model(t_s, t_l)

    for it in range(n_iterations):
        t_start_total = time.perf_counter()

        # 1. Short-branch DSP (250ms active pooling)
        t0 = time.perf_counter()
        short_feats = []
        for s in range(n_streams):
            tiled = np.tile(dummy_buffers_short[s], 4)[:16000]
            norm = tiled / (np.max(np.abs(tiled)) + 1e-9)
            sb = extract_subband_vector_c5(norm, sr=sr)
            ac = extract_phonation_stats_c5(norm, sr=sr)
            short_feats.append(np.concatenate([sb, ac]))
        t_dsp_short = (time.perf_counter() - t0) * 1000.0

        # 2. Sustained-branch DSP (1000ms C5)
        t0 = time.perf_counter()
        sust_feats = []
        for s in range(n_streams):
            norm = dummy_buffers_1s[s] / (np.max(np.abs(dummy_buffers_1s[s])) + 1e-9)
            sb = extract_subband_vector_c5(norm, sr=sr)
            ac = extract_phonation_stats_c5(norm, sr=sr)
            sust_feats.append(np.concatenate([sb, ac]))
        t_dsp_sust = (time.perf_counter() - t0) * 1000.0

        # 3. Model-only neural inference (Gate 5)
        t_nn_start = time.perf_counter()
        t_short = torch.tensor(np.array(short_feats), dtype=torch.float32)
        t_sust = torch.tensor(np.array(sust_feats), dtype=torch.float32)
        with torch.no_grad():
            logits = model(t_short, t_sust)
            probs = torch.sigmoid(logits).numpy()
        t_nn = (time.perf_counter() - t_nn_start) * 1000.0

        # 4. Temporal Aggregation & Post-Gating
        t_temp_start = time.perf_counter()
        for s in range(n_streams):
            p = float(probs.flat[s])
            _ = p >= 0.48
        t_temp = (time.perf_counter() - t_temp_start) * 1000.0

        t_total = (time.perf_counter() - t_start_total) * 1000.0

        dsp_short_times.append(t_dsp_short)
        dsp_sust_times.append(t_dsp_sust)
        nn_times.append(t_nn)
        temporal_times.append(t_temp)
        total_pipeline_times.append(t_total)

    cpu_after = process.cpu_percent(interval=None)
    ram_mb = process.memory_info().rss / (1024 * 1024)

    return {
        "n_streams": n_streams,
        "n_iterations": n_iterations,
        # Model-only neural latency (Gate 5 Authority)
        "nn_latency_mean_ms": round(float(np.mean(nn_times)), 4),
        "nn_latency_p50_ms": round(float(np.percentile(nn_times, 50.0)), 4),
        "nn_latency_p90_ms": round(float(np.percentile(nn_times, 90.0)), 4),
        "nn_latency_p95_ms": round(float(np.percentile(nn_times, 95.0)), 4),
        "nn_latency_p99_ms": round(float(np.percentile(nn_times, 99.0)), 4),
        "gate5_model_only_pass": bool(np.percentile(nn_times, 95.0) <= 25.0),
        # Complete pipeline latency
        "total_pipeline_mean_ms": round(float(np.mean(total_pipeline_times)), 4),
        "total_pipeline_p50_ms": round(float(np.percentile(total_pipeline_times, 50.0)), 4),
        "total_pipeline_p95_ms": round(float(np.percentile(total_pipeline_times, 95.0)), 4),
        "total_pipeline_p99_ms": round(float(np.percentile(total_pipeline_times, 99.0)), 4),
        # DSP break-downs
        "dsp_short_mean_ms": round(float(np.mean(dsp_short_times)), 4),
        "dsp_sust_mean_ms": round(float(np.mean(dsp_sust_times)), 4),
        "temporal_mean_ms": round(float(np.mean(temporal_times)), 4),
        "cpu_percent": round(float(cpu_after), 1),
        "ram_rss_mb": round(float(ram_mb), 2)
    }

def main():
    print("=" * 80)
    print("STAGE 8.9.65 — TRACK I: MULTI-STREAM LATENCY PROFILING (1, 2, 4, 8 STREAMS)")
    print("=" * 80)

    concurrencies = [1, 2, 4, 8]
    bench_results = []

    print(f"{'Streams':<10} {'NN Mean':<10} {'NN P95':<10} {'Total Mean':<12} {'Total P95':<12} {'Gate 5 (<=25ms)':<16} {'RAM (MB)'}")
    print("-" * 88)

    for n_s in concurrencies:
        res = benchmark_stream_concurrency(n_streams=n_s, n_iterations=400)
        bench_results.append(res)
        g5_str = "PASS" if res["gate5_model_only_pass"] else "FAIL"
        print(f"{res['n_streams']:<10} {res['nn_latency_mean_ms']:<10.3f} {res['nn_latency_p95_ms']:<10.3f} {res['total_pipeline_mean_ms']:<12.3f} {res['total_pipeline_p95_ms']:<12.3f} {g5_str:<16} {res['ram_rss_mb']:.1f}")

    out_csv = STAGE65_DIR / "latency_benchmarks.csv"
    pd.DataFrame(bench_results).to_csv(out_csv, index=False)
    print(f"\nEmitted multi-stream latency benchmarks to {out_csv}")

if __name__ == "__main__":
    main()

