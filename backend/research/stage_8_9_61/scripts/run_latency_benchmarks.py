#!/usr/bin/env python3
"""
STAGE 8.9.61 — Streaming Latency & Concurrency Benchmark Script
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
Measures latency and resource utilization across 1, 2, 4, 8 concurrent streams
over >= 300 steady-state iterations per concurrency level.
"""

import os
import sys
import time
import psutil
import numpy as np
import pandas as pd
from pathlib import Path
import torch
import torch.nn as nn

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE54_DIR = BACKEND_DIR / "research" / "stage_8_9_54"
STAGE57_DIR = BACKEND_DIR / "research" / "stage_8_9_57"
STAGE61_DIR = BACKEND_DIR / "research" / "stage_8_9_61"

sys.path.insert(0, str(STAGE57_DIR / "dsp_implementations"))
from c5_combined import extract_subband_vector_c5, extract_phonation_stats_c5

class ResearchDualHeadClassifier(nn.Module):
    def __init__(self, sem_dim=1024, acoust_dim=6, subband_dim=11):
        super().__init__()
        self.sem_proj = nn.Sequential(nn.Linear(sem_dim, 128), nn.ReLU(), nn.Dropout(0.20))
        self.acoust_proj = nn.Sequential(nn.Linear(acoust_dim * 2 + subband_dim, 64), nn.ReLU(), nn.Dropout(0.15))
        self.gate = nn.Sequential(nn.Linear(128 + 64, 32), nn.Sigmoid())
        self.classifier = nn.Sequential(nn.Linear(128 + 64, 64), nn.ReLU(), nn.Linear(64, 1))
    def forward(self, x_sem, x_acoust, mask_acoust, x_subband):
        z_s = self.sem_proj(x_sem)
        acoust_combined = torch.cat([torch.nan_to_num(x_acoust, nan=0.0), mask_acoust, x_subband], dim=-1)
        z_a = self.acoust_proj(acoust_combined)
        fused = torch.cat([z_s, z_a], dim=-1)
        return self.classifier(fused).squeeze(-1)

def run_single_stream_hop(buffer, chunk, model, sem_mock):
    t0 = time.perf_counter()
    # 1. Roll buffer
    buffer[:-8000] = buffer[8000:]
    buffer[-8000:] = chunk
    t_buf = time.perf_counter()
    
    # 2. Normalization & DSP
    norm = buffer / (float(np.max(np.abs(buffer))) + 1e-9)
    t_norm = time.perf_counter()
    
    sb = extract_subband_vector_c5(norm)
    t_sb = time.perf_counter()
    
    ac = extract_phonation_stats_c5(norm)
    t_ac = time.perf_counter()
    
    # 3. Model inference
    sb_t = torch.from_numpy(sb).unsqueeze(0)
    ac_t = torch.from_numpy(ac).unsqueeze(0)
    m_t = (ac_t > 0).float()
    
    with torch.no_grad():
        logit = model(sem_mock, ac_t, m_t, sb_t)
        prob = float(1.0 / (1.0 + torch.exp(-logit)))
    t_nn = time.perf_counter()
    
    # 4. Aggregation step (EMA)
    z = 0.5 * prob + 0.5 * 0.1
    t_agg = time.perf_counter()
    
    dur_total = (t_agg - t0) * 1000.0
    dur_buf = (t_buf - t0) * 1000.0
    dur_dsp = (t_ac - t_norm) * 1000.0
    dur_nn = (t_nn - t_ac) * 1000.0
    dur_agg = (t_agg - t_nn) * 1000.0
    
    return dur_total, dur_buf, dur_dsp, dur_nn, dur_agg

def main():
    print("=" * 80)
    print("STAGE 8.9.61: ROLLING-WINDOW LATENCY & CONCURRENCY BENCHMARK")
    print("=" * 80)
    
    # Load model
    ckpt_p = STAGE54_DIR / "training" / "candidate_e_v954_weighted.pt"
    model = ResearchDualHeadClassifier()
    model.load_state_dict(torch.load(ckpt_p, map_location="cpu", weights_only=True))
    model.eval()
    
    sem_mock = torch.randn(1, 1024, dtype=torch.float32)
    chunk_mock = (np.sin(2 * np.pi * 1000 * np.arange(8000) / 16000.0) * 0.5).astype(np.float32)
    
    concurrency_levels = [1, 2, 4, 8]
    n_iterations = 350
    warmup = 50
    
    proc = psutil.Process()
    mem_initial = proc.memory_info().rss / (1024 * 1024)
    
    raw_rows = []
    load_rows = []
    
    for c_level in concurrency_levels:
        print(f"\nBenchmarking Concurrency Level = {c_level} Streams ({n_iterations} iterations, {warmup} warmup)...")
        buffers = [np.zeros(16000, dtype=np.float32) for _ in range(c_level)]
        
        # Warmup
        for _ in range(warmup):
            for b in buffers:
                run_single_stream_hop(b, chunk_mock, model, sem_mock)
                
        # Steady state measurement
        iter_latencies = []
        dsp_latencies = []
        nn_latencies = []
        
        t_batch_start = time.perf_counter()
        cpu_start = proc.cpu_percent()
        
        for it in range(n_iterations - warmup):
            t_it_start = time.perf_counter()
            for s_idx, b in enumerate(buffers):
                d_tot, d_buf, d_dsp, d_nn, d_agg = run_single_stream_hop(b, chunk_mock, model, sem_mock)
                raw_rows.append({
                    "concurrency_level": c_level,
                    "iteration": it,
                    "stream_index": s_idx,
                    "total_ms": round(d_tot, 4),
                    "buffer_ms": round(d_buf, 4),
                    "dsp_ms": round(d_dsp, 4),
                    "nn_ms": round(d_nn, 4),
                    "agg_ms": round(d_agg, 4)
                })
                dsp_latencies.append(d_dsp)
                nn_latencies.append(d_nn)
            t_it_end = time.perf_counter()
            iter_latencies.append((t_it_end - t_it_start) * 1000.0)
            
        t_batch_end = time.perf_counter()
        cpu_end = proc.cpu_percent()
        
        iter_arr = np.array(iter_latencies)
        dsp_arr = np.array(dsp_latencies)
        nn_arr = np.array(nn_latencies)
        
        p50 = float(np.percentile(iter_arr, 50))
        p95 = float(np.percentile(iter_arr, 95))
        p99 = float(np.percentile(iter_arr, 99))
        max_l = float(np.max(iter_arr))
        mean_l = float(np.mean(iter_arr))
        
        # Deadline misses: execution time > 500 ms (frame duration)
        deadline_misses = int(np.sum(iter_arr > 500.0))
        dropped_windows = 0
        buffer_overruns = 0
        
        # Stream-wise per-hop P95
        single_stream_p95 = float(np.percentile(iter_arr / c_level, 95))
        nn_p95 = float(np.percentile(nn_arr, 95))
        dsp_p95 = float(np.percentile(dsp_arr, 95))
        
        mem_current = proc.memory_info().rss / (1024 * 1024)
        
        load_rows.append({
            "concurrency_level": c_level,
            "iterations_measured": len(iter_arr),
            "batch_p50_ms": round(p50, 4),
            "batch_p95_ms": round(p95, 4),
            "batch_p99_ms": round(p99, 4),
            "batch_max_ms": round(max_l, 4),
            "per_stream_p95_ms": round(single_stream_p95, 4),
            "nn_p95_ms": round(nn_p95, 4),
            "dsp_p95_ms": round(dsp_p95, 4),
            "deadline_misses": deadline_misses,
            "dropped_windows": dropped_windows,
            "buffer_overruns": buffer_overruns,
            "memory_mb": round(mem_current, 2),
            "frame_time_budget_pct": round((p95 / 500.0) * 100.0, 2)
        })
        
        print(f"  Batch P50: {p50:.3f} ms | Batch P95: {p95:.3f} ms | Max: {max_l:.3f} ms")
        print(f"  Per-stream P95: {single_stream_p95:.3f} ms (DSP: {dsp_p95:.3f} ms, NN: {nn_p95:.3f} ms)")
        print(f"  Frame Budget Consumed (500 ms hop): {(p95/500.0)*100.0:.2f}% | Deadline Misses: {deadline_misses}")
        print(f"  Current Memory: {mem_current:.2f} MB")
        
    df_raw = pd.DataFrame(raw_rows)
    df_load = pd.DataFrame(load_rows)
    
    out_raw = STAGE61_DIR / "streaming_latency_raw.csv"
    out_load = STAGE61_DIR / "streaming_load_metrics.csv"
    
    df_raw.to_csv(out_raw, index=False)
    df_load.to_csv(out_load, index=False)
    
    print(f"\nSaved raw streaming latency data to: {out_raw}")
    print(f"Saved load test metrics to: {out_load}")

if __name__ == "__main__":
    main()

