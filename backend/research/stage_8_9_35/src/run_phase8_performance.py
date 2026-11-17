"""
Stage 8.9.35 - Phase Eight: Performance and Concurrency Benchmark
Profiles end-to-end inference latency, component breakdown, and multi-stream concurrency.
"""
import os
import sys
import time
import psutil
import torch
import numpy as np
import pandas as pd
from scipy.signal import butter, sosfilt

# Add local path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from train_and_evaluate_stage8_9_35 import MultiPathwayFusionModel

def extract_subband_vector_fast(audio, sr=16000):
    """Fast extraction of 11-dim subband feature vector."""
    bands = [
        (300, 800),
        (800, 1500),
        (1500, 2000),
        (2000, 3000),
        (3000, 4000),
        (4000, 6000)
    ]
    total_energy = np.sum(audio ** 2) + 1e-9
    rel_energies = []
    temp_vars = []
    
    # 6 subbands
    for low, high in bands:
        sos = butter(4, [low, high], btype='bandpass', fs=sr, output='sos')
        filtered = sosfilt(sos, audio)
        b_energy = np.sum(filtered ** 2)
        rel_energies.append(b_energy / total_energy)
        temp_vars.append(np.var(filtered))
        
    scream_ratio = (rel_energies[3] + rel_energies[4]) / (rel_energies[0] + 1e-6)
    whistle_ratio = rel_energies[5] / (rel_energies[3] + rel_energies[4] + 1e-6)
    
    vec = [
        rel_energies[0], rel_energies[1], rel_energies[2],
        rel_energies[3], rel_energies[4], rel_energies[5],
        temp_vars[0], temp_vars[3], temp_vars[4],
        scream_ratio, whistle_ratio
    ]
    return np.array(vec, dtype=np.float32)

def run_performance_audit():
    print("======================================================================")
    print("STAGE 8.9.35 - PHASE EIGHT: PERFORMANCE & CONCURRENCY AUDIT")
    print("======================================================================")
    
    model_path = os.path.join("backend", "research", "stage_8_9_35", "models", "mp_fusion_model.pt")
    device = torch.device("cpu")
    model = MultiPathwayFusionModel(sem_dim=1024, acoust_dim=6, subband_dim=11).to(device)
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path, map_location=device))
        print("Loaded trained MultiPathwayFusionModel weights.")
    model.eval()

    perf_dir = os.path.join("backend", "research", "stage_8_9_35", "performance")
    os.makedirs(perf_dir, exist_ok=True)

    # 1. Component Latency Breakdown
    print("\n--- 1. SINGLE-STREAM COMPONENT LATENCY BREAKDOWN (200 RUNS) ---")
    sr = 16000
    window_samples = 15600 # 975 ms
    dummy_audio = np.random.randn(window_samples).astype(np.float32)
    dummy_yamnet = torch.randn(1, 1024, device=device)
    dummy_acoust = torch.randn(1, 6, device=device)
    dummy_mask = torch.ones(1, 6, device=device)
    
    times_ingest = []
    times_subband = []
    times_neural = []
    times_decision = []
    times_e2e = []

    # Warmup
    for _ in range(20):
        _ = extract_subband_vector_fast(dummy_audio, sr)
        _ = model(dummy_yamnet, dummy_acoust, dummy_mask, torch.randn(1, 11, device=device))

    for _ in range(200):
        t0 = time.perf_counter()
        # Ingestion (ring-buffer slice)
        audio_slice = dummy_audio.copy()
        t1 = time.perf_counter()
        
        # Subband filtering & feature extraction (11 features)
        sb_feats = extract_subband_vector_fast(audio_slice, sr)
        sb_tensor = torch.from_numpy(sb_feats).unsqueeze(0).to(device)
        t2 = time.perf_counter()
        
        # Neural forward pass
        with torch.no_grad():
            logits, _, _ = model(dummy_yamnet, dummy_acoust, dummy_mask, sb_tensor)
            prob = torch.sigmoid(logits)
        t3 = time.perf_counter()
        
        # Decision logic
        decision = prob.item() >= 0.43
        t4 = time.perf_counter()
        
        times_ingest.append((t1 - t0) * 1000.0)
        times_subband.append((t2 - t1) * 1000.0)
        times_neural.append((t3 - t2) * 1000.0)
        times_decision.append((t4 - t3) * 1000.0)
        times_e2e.append((t4 - t0) * 1000.0)

    breakdown_df = pd.DataFrame([
        {
            "component": "Ring-Buffer Ingestion / Slicing",
            "mean_ms": np.mean(times_ingest),
            "p50_ms": np.percentile(times_ingest, 50),
            "p95_ms": np.percentile(times_ingest, 95),
            "p99_ms": np.percentile(times_ingest, 99),
            "max_ms": np.max(times_ingest)
        },
        {
            "component": "Subband IIR Filtering & Features (11-dim)",
            "mean_ms": np.mean(times_subband),
            "p50_ms": np.percentile(times_subband, 50),
            "p95_ms": np.percentile(times_subband, 95),
            "p99_ms": np.percentile(times_subband, 99),
            "max_ms": np.max(times_subband)
        },
        {
            "component": "Multi-Pathway Neural Forward Pass",
            "mean_ms": np.mean(times_neural),
            "p50_ms": np.percentile(times_neural, 50),
            "p95_ms": np.percentile(times_neural, 95),
            "p99_ms": np.percentile(times_neural, 99),
            "max_ms": np.max(times_neural)
        },
        {
            "component": "Threshold Evaluation & Post-Processing",
            "mean_ms": np.mean(times_decision),
            "p50_ms": np.percentile(times_decision, 50),
            "p95_ms": np.percentile(times_decision, 95),
            "p99_ms": np.percentile(times_decision, 99),
            "max_ms": np.max(times_decision)
        },
        {
            "component": "Total Pipeline (Excl. YAMNet Backbone)",
            "mean_ms": np.mean(times_e2e),
            "p50_ms": np.percentile(times_e2e, 50),
            "p95_ms": np.percentile(times_e2e, 95),
            "p99_ms": np.percentile(times_e2e, 99),
            "max_ms": np.max(times_e2e)
        },
        {
            "component": "Total End-to-End (Incl. YAMNet ~18ms)",
            "mean_ms": np.mean(times_e2e) + 18.0,
            "p50_ms": np.percentile(times_e2e, 50) + 18.0,
            "p95_ms": np.percentile(times_e2e, 95) + 18.0,
            "p99_ms": np.percentile(times_e2e, 99) + 18.0,
            "max_ms": np.max(times_e2e) + 18.0
        }
    ])
    
    breakdown_path = os.path.join(perf_dir, "latency_distribution.csv")
    breakdown_df.to_csv(breakdown_path, index=False)
    print(breakdown_df.to_string(index=False))

    # 2. Multi-Stream Concurrency Benchmark
    print("\n--- 2. MULTI-STREAM CONCURRENCY BENCHMARK (100 HOPS PER STREAM) ---")
    stream_counts = [1, 2, 4, 8]
    hops_per_stream = 100
    concurrency_results = []
    process = psutil.Process()

    for n_streams in stream_counts:
        yamnet_batch = torch.randn(n_streams, 1024, device=device)
        acoust_batch = torch.randn(n_streams, 6, device=device)
        mask_batch = torch.ones(n_streams, 6, device=device)
        audio_buffers = [np.random.randn(window_samples).astype(np.float32) for _ in range(n_streams)]
        
        hop_latencies = []
        deadline_misses_25ms = 0
        deadline_misses_100ms = 0
        
        cpu_start = process.cpu_percent(interval=None)
        mem_start_mb = process.memory_info().rss / (1024 * 1024)
        t_start = time.perf_counter()

        for hop in range(hops_per_stream):
            t_hop0 = time.perf_counter()
            
            # Process all streams for this 100ms audio hop
            sb_batch = []
            for s in range(n_streams):
                feats = extract_subband_vector_fast(audio_buffers[s], sr)
                sb_batch.append(feats)
            sb_tensor = torch.from_numpy(np.array(sb_batch)).to(device)
            
            with torch.no_grad():
                logits, _, _ = model(yamnet_batch, acoust_batch, mask_batch, sb_tensor)
                probs = torch.sigmoid(logits)
                decisions = (probs >= 0.43).cpu().numpy()
                
            t_hop1 = time.perf_counter()
            hop_ms = (t_hop1 - t_hop0) * 1000.0
            hop_latencies.append(hop_ms)
            
            per_stream_lat = hop_ms / n_streams
            if per_stream_lat > 25.0:
                deadline_misses_25ms += 1
            if hop_ms > 100.0:
                deadline_misses_100ms += 1

        t_end = time.perf_counter()
        total_wall_sec = t_end - t_start
        cpu_end = process.cpu_percent(interval=None)
        mem_end_mb = process.memory_info().rss / (1024 * 1024)
        
        concurrency_results.append({
            "concurrent_streams": n_streams,
            "total_hops": hops_per_stream * n_streams,
            "wall_clock_sec": round(total_wall_sec, 2),
            "hop_mean_ms": round(float(np.mean(hop_latencies)), 2),
            "hop_p50_ms": round(float(np.percentile(hop_latencies, 50)), 2),
            "hop_p95_ms": round(float(np.percentile(hop_latencies, 95)), 2),
            "hop_max_ms": round(float(np.max(hop_latencies)), 2),
            "per_stream_p95_ms": round(float(np.percentile(hop_latencies, 95)) / n_streams, 2),
            "deadline_misses_25ms": deadline_misses_25ms,
            "deadline_misses_100ms": deadline_misses_100ms,
            "memory_rss_mb": round(mem_end_mb, 1),
            "status": "PASS" if deadline_misses_100ms == 0 else "FAIL"
        })
        print(f"  Streams: {n_streams:2d} | Hop P95: {np.percentile(hop_latencies, 95):.2f} ms | Per-stream P95: {np.percentile(hop_latencies, 95)/n_streams:.2f} ms | 100ms Misses: {deadline_misses_100ms}")

    concurrency_df = pd.DataFrame(concurrency_results)
    concurrency_path = os.path.join(perf_dir, "concurrency_benchmark.csv")
    concurrency_df.to_csv(concurrency_path, index=False)
    print(f"\nSaved {concurrency_path}")
    print(f"Saved {breakdown_path}")

if __name__ == "__main__":
    run_performance_audit()
