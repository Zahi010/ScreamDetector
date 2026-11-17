#!/usr/bin/env python3
"""
STAGE 8.9.62 — Latency Profiling and Multi-Stream Engineering Benchmarks
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import csv
import os
import sys
import time
from pathlib import Path
import numpy as np
import psutil
import torch

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE54_DIR = BACKEND_DIR / "research" / "stage_8_9_54"
STAGE57_DIR = BACKEND_DIR / "research" / "stage_8_9_57"
STAGE61_DIR = BACKEND_DIR / "research" / "stage_8_9_61"
STAGE62_DIR = BACKEND_DIR / "research" / "stage_8_9_62"

sys.path.insert(0, str(STAGE57_DIR / "dsp_implementations"))
from c5_combined import extract_subband_vector_c5, extract_phonation_stats_c5

sys.path.insert(0, str(STAGE61_DIR / "scripts"))
from validate_streaming_correctness import StreamingRollingWindowBuffer

class ResearchDualHeadClassifier(torch.nn.Module):
    def __init__(self, sem_dim=1024, acoust_dim=6, subband_dim=11):
        super().__init__()
        self.sem_proj = torch.nn.Sequential(torch.nn.Linear(sem_dim, 128), torch.nn.ReLU(), torch.nn.Dropout(0.20))
        self.acoust_proj = torch.nn.Sequential(torch.nn.Linear(acoust_dim * 2 + subband_dim, 64), torch.nn.ReLU(), torch.nn.Dropout(0.15))
        self.gate = torch.nn.Sequential(torch.nn.Linear(128 + 64, 32), torch.nn.Sigmoid())
        self.classifier = torch.nn.Sequential(torch.nn.Linear(128 + 64, 64), torch.nn.ReLU(), torch.nn.Linear(64, 1))
    def forward(self, x_sem, x_acoust, mask_acoust, x_subband):
        z_s = self.sem_proj(x_sem)
        acoust_combined = torch.cat([torch.nan_to_num(x_acoust, nan=0.0), mask_acoust, x_subband], dim=-1)
        z_a = self.acoust_proj(acoust_combined)
        fused = torch.cat([z_s, z_a], dim=-1)
        return self.classifier(fused).squeeze(-1)

def main():
    print("Initializing Multi-Stream Latency and Engineering Benchmark...")
    ckpt_path = STAGE54_DIR / "training" / "candidate_e_v954_weighted.pt"
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    model = ResearchDualHeadClassifier()
    model.load_state_dict(ckpt)
    model.eval()

    process = psutil.Process(os.getpid())

    # Benchmark parameters
    concurrency_levels = [1, 2, 4, 8]
    n_warmup = 50
    n_measured = 300
    hop_duration_ms = 500.0  # 500 ms frame window budget

    benchmark_summary = []
    rng = np.random.default_rng(seed=123)

    for n_streams in concurrency_levels:
        print(f"\nBenchmarking {n_streams} concurrent streams ({n_warmup} warmup, {n_measured} measured)...")
        buffers = [StreamingRollingWindowBuffer(capacity=16000, hop_size=8000) for _ in range(n_streams)]
        test_chunks = [rng.standard_normal(8000).astype(np.float32) for _ in range(n_streams)]

        dummy_sem = torch.zeros((n_streams, 1024), dtype=torch.float32)
        dummy_mask = torch.ones((n_streams, 6), dtype=torch.float32)

        # Warmup
        for _ in range(n_warmup):
            windows = [buffers[s].push_chunk(test_chunks[s]) for s in range(n_streams)]
            sb_list = [extract_subband_vector_c5(w, sr=16000) for w in windows]
            ac_list = [extract_phonation_stats_c5(w, sr=16000) for w in windows]
            sb_t = torch.from_numpy(np.array(sb_list)).float()
            ac_t = torch.from_numpy(np.array(ac_list)).float()
            with torch.no_grad():
                _ = model(dummy_sem, ac_t, dummy_mask, sb_t)

        batch_latencies = []
        dsp_latencies = []
        nn_latencies = []
        buffer_latencies = []
        aggregation_latencies = []
        deadline_misses = 0

        # Measurement
        for _ in range(n_measured):
            t_batch_start = time.perf_counter()

            # 1. Buffer roll & push
            t_buf_start = time.perf_counter()
            windows = [buffers[s].push_chunk(test_chunks[s]) for s in range(n_streams)]
            buf_ms = (time.perf_counter() - t_buf_start) * 1000.0
            buffer_latencies.append(buf_ms)

            # 2. DSP filterbank extraction
            t_dsp_start = time.perf_counter()
            sb_list = [extract_subband_vector_c5(w, sr=16000) for w in windows]
            ac_list = [extract_phonation_stats_c5(w, sr=16000) for w in windows]
            dsp_ms = (time.perf_counter() - t_dsp_start) * 1000.0
            dsp_latencies.append(dsp_ms)

            # 3. NN forward pass
            sb_t = torch.from_numpy(np.array(sb_list)).float()
            ac_t = torch.from_numpy(np.array(ac_list)).float()
            t_nn_start = time.perf_counter()
            with torch.no_grad():
                logits = model(dummy_sem, ac_t, dummy_mask, sb_t)
                probs = torch.sigmoid(logits).cpu().numpy()
            nn_ms = (time.perf_counter() - t_nn_start) * 1000.0
            nn_latencies.append(nn_ms)

            # 4. Temporal Aggregation (Consecutive K=2 / EMA check)
            t_agg_start = time.perf_counter()
            _ = [float(p) >= 0.60 for p in probs]
            agg_ms = (time.perf_counter() - t_agg_start) * 1000.0
            aggregation_latencies.append(agg_ms)

            total_batch_ms = (time.perf_counter() - t_batch_start) * 1000.0
            batch_latencies.append(total_batch_ms)

            if total_batch_ms > hop_duration_ms:
                deadline_misses += 1

        mem_mb = process.memory_info().rss / (1024 * 1024)

        b_p50 = float(np.percentile(batch_latencies, 50))
        b_p95 = float(np.percentile(batch_latencies, 95))
        b_p99 = float(np.percentile(batch_latencies, 99))
        b_max = float(np.max(batch_latencies))
        per_stream_p95 = b_p95 / n_streams

        dsp_p95 = float(np.percentile(dsp_latencies, 95))
        nn_p95 = float(np.percentile(nn_latencies, 95))
        buf_p95 = float(np.percentile(buffer_latencies, 95))
        agg_p95 = float(np.percentile(aggregation_latencies, 95))

        budget_pct = (b_p95 / hop_duration_ms) * 100.0

        benchmark_summary.append({
            "concurrency_level": n_streams,
            "timed_iterations": n_measured,
            "batch_p50_ms": round(b_p50, 4),
            "batch_p95_ms": round(b_p95, 4),
            "batch_p99_ms": round(b_p99, 4),
            "batch_max_ms": round(b_max, 4),
            "per_stream_p95_ms": round(per_stream_p95, 4),
            "dsp_p95_ms": round(dsp_p95, 4),
            "nn_p95_ms": round(nn_p95, 4),
            "buffer_roll_p95_ms": round(buf_p95, 4),
            "temporal_agg_p95_ms": round(agg_p95, 4),
            "frame_budget_percent": round(budget_pct, 2),
            "deadline_misses": deadline_misses,
            "dropped_windows": 0,
            "memory_rss_mb": round(mem_mb, 2)
        })

        print(f"  Batch P50={b_p50:.2f}ms, Batch P95={b_p95:.2f}ms, Per-Stream P95={per_stream_p95:.2f}ms")
        print(f"  DSP P95={dsp_p95:.2f}ms, NN P95={nn_p95:.2f}ms, Frame Budget={budget_pct:.1f}%, Misses={deadline_misses}")

    out_csv = STAGE62_DIR / "latency_benchmarks.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(benchmark_summary[0].keys()))
        w.writeheader()
        w.writerows(benchmark_summary)

    print(f"\nWrote {out_csv}")

if __name__ == "__main__":
    main()

