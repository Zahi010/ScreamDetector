"""
Stage 8.9.40: Measure YAMNet Inference Latency on 0.975s Audio Window (16 kHz).
Executed using Python 3.11 virtualenv (with TensorFlow).
"""
import os
import sys
import time
import json
from pathlib import Path
import numpy as np

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from src.model.yamnet_loader import YAMNetLoader

def main():
    print("Loading YAMNet...")
    loader = YAMNetLoader()
    loader.load()

    # Generate 0.975s audio at 16kHz (15600 samples)
    audio = np.random.randn(15600).astype(np.float32)

    # Warmup
    print("Warming up YAMNet (20 runs)...")
    for _ in range(20):
        _ = loader.infer(audio)

    # Benchmark 200 runs
    N_RUNS = 200
    print(f"Benchmarking YAMNet ({N_RUNS} runs)...")
    durations = []
    for _ in range(N_RUNS):
        t0 = time.perf_counter()
        _ = loader.infer(audio)
        t1 = time.perf_counter()
        durations.append((t1 - t0) * 1000.0)

    durations = np.array(durations)
    results = {
        "n_runs": N_RUNS,
        "mean_ms": round(float(np.mean(durations)), 3),
        "std_ms": round(float(np.std(durations)), 3),
        "p50_ms": round(float(np.percentile(durations, 50)), 3),
        "p90_ms": round(float(np.percentile(durations, 90)), 3),
        "p95_ms": round(float(np.percentile(durations, 95)), 3),
        "p99_ms": round(float(np.percentile(durations, 99)), 3),
        "min_ms": round(float(np.min(durations)), 3),
        "max_ms": round(float(np.max(durations)), 3),
    }

    out_path = BACKEND_DIR / "research" / "stage_8_9_40" / "results" / "metrics" / "yamnet_latency.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"YAMNet latency: Mean={results['mean_ms']} ms | P50={results['p50_ms']} ms | P95={results['p95_ms']} ms | P99={results['p99_ms']} ms")
    print(f"Saved to: {out_path}")

if __name__ == "__main__":
    main()
