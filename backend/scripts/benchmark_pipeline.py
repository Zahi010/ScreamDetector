"""Stage 8.5 Micro-Benchmark Suite for Pipeline Latency Analysis.

Measures latency of each pipeline stage in isolation and end-to-end:
1. Audio window preprocessing / normalization.
2. Google YAMNet frame embedding extraction.
3. 1,024-dimensional feature max-pooling.
4. Stage 5 Logistic Regression probability prediction.
5. EventStateMachine temporal smoothing & state transition.
6. DetectionEventLogger JSON Lines serialization and disk append.
7. WebSocket event queueing & JSON serialization.
8. End-to-end processing pipeline (buffer -> YAMNet -> classifier -> alert dispatch).
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from src.alerts.alert_dispatcher import AlertDispatcher
from src.config import TARGET_SAMPLE_RATE, YAMNet_FRAME_SECONDS
from src.detector.event_logger import DetectionEventLogger
from src.detector.state_machine import EventStateMachine
from src.detector.stream_detector import StreamDetector
from src.model.scream_classifier import FestivalScreamClassifier
from src.model.yamnet_loader import YAMNetLoader

logging.basicConfig(level=logging.WARNING)


def benchmark_component(
    name: str,
    fn,
    warmup_iters: int = 5,
    benchmark_iters: int = 50,
) -> Dict[str, Any]:
    """Execute benchmark iterations and return timing distribution metrics."""
    # Warmup
    for _ in range(warmup_iters):
        fn()

    times_ms: List[float] = []
    for _ in range(benchmark_iters):
        t0 = time.perf_counter()
        fn()
        t1 = time.perf_counter()
        times_ms.append((t1 - t0) * 1000.0)

    return {
        "component": name,
        "iterations": benchmark_iters,
        "mean_ms": round(float(np.mean(times_ms)), 3),
        "median_ms": round(float(np.median(times_ms)), 3),
        "min_ms": round(float(np.min(times_ms)), 3),
        "max_ms": round(float(np.max(times_ms)), 3),
        "p95_ms": round(float(np.percentile(times_ms, 95)), 3),
        "p99_ms": round(float(np.percentile(times_ms, 99)), 3),
    }


def run_benchmarks(num_iterations: int = 50, output_json: Optional[Path] = None):
    print("=" * 80)
    print("STAGE 8.5 — PIPELINE COMPONENT LATENCY BENCHMARK")
    print("=" * 80)
    print(f"Iterations per component: {num_iterations}")
    print("=" * 80)

    # 1. Load Pretrained Models
    print("\n[1/7] Warming up YAMNet and Stage 5 Scream Classifier...")
    yamnet = YAMNetLoader()
    yamnet.load()

    classifier = FestivalScreamClassifier()
    classifier.load()

    window_samples = int(TARGET_SAMPLE_RATE * YAMNet_FRAME_SECONDS)
    test_audio = (0.1 * np.random.randn(window_samples)).astype(np.float32)

    # Pre-extract embeddings for downstream benchmarking
    scores, embeddings, _ = yamnet.infer(test_audio)
    pooled_feats = classifier.pool_frame_embeddings(embeddings)

    # 2. Benchmark YAMNet
    print("[2/7] Benchmarking YAMNet Embedding Extraction...")
    res_yamnet = benchmark_component(
        "1. YAMNet Embedding Extraction (0.975s window)",
        lambda: yamnet.infer(test_audio),
        warmup_iters=3,
        benchmark_iters=num_iterations,
    )

    # 3. Benchmark Max-Pooling
    print("[3/7] Benchmarking Feature Max-Pooling...")
    res_pooling = benchmark_component(
        "2. 1024-dim Max-Pooling",
        lambda: classifier.pool_frame_embeddings(embeddings),
        warmup_iters=10,
        benchmark_iters=num_iterations * 2,
    )

    # 4. Benchmark Classifier Inference
    print("[4/7] Benchmarking Stage 5 Classifier Inference...")
    res_clf = benchmark_component(
        "3. Logistic Regression Classifier Inference",
        lambda: classifier.predict_features(pooled_feats, custom_threshold=0.35),
        warmup_iters=10,
        benchmark_iters=num_iterations * 2,
    )

    # 5. Benchmark State Machine Transition
    print("[5/7] Benchmarking State Machine Window Evaluation...")
    sm = EventStateMachine(threshold=0.35)
    counter = 0

    def step_sm():
        nonlocal counter
        counter += 1
        sm.process_window(0.50 if counter % 3 == 0 else 0.10, counter * 0.4875, counter)

    res_sm = benchmark_component(
        "4. State Machine Transition & Temporal Smoothing",
        step_sm,
        warmup_iters=10,
        benchmark_iters=num_iterations * 2,
    )

    # 6. Benchmark Structured Event Logging
    print("[6/7] Benchmarking Event JSONL Disk Logging...")
    temp_log = backend_dir / "logs" / "benchmark_test.jsonl"
    temp_log.parent.mkdir(parents=True, exist_ok=True)
    logger_inst = DetectionEventLogger(log_filepath=temp_log)
    sample_event = {
        "event_id": "evt_bench",
        "peak_probability": 0.88,
        "duration_seconds": 1.5,
        "alert_emitted": True,
    }

    res_log = benchmark_component(
        "5. Event JSONL Serialization & File Write",
        lambda: logger_inst.log_event(sample_event),
        warmup_iters=10,
        benchmark_iters=num_iterations,
    )
    if temp_log.exists():
        temp_log.unlink()

    # 7. Benchmark End-to-End Window Evaluation
    print("[7/7] Benchmarking End-to-End StreamDetector Window Pipeline...")
    detector = StreamDetector(
        sample_rate=TARGET_SAMPLE_RATE,
        threshold=0.35,
        classifier=classifier,
        yamnet_loader=yamnet,
    )

    def full_step():
        detector.push_audio(test_audio)
        detector.process_available_windows()

    res_e2e = benchmark_component(
        "6. End-to-End Pipeline (Buffer -> YAMNet -> LR -> StateMachine)",
        full_step,
        warmup_iters=3,
        benchmark_iters=num_iterations,
    )

    all_results = [res_yamnet, res_pooling, res_clf, res_sm, res_log, res_e2e]

    print("\n" + "=" * 90)
    print(f" {'Component':<45} {'Mean (ms)':<11} {'Median (ms)':<13} {'P95 (ms)':<10} {'P99 (ms)':<10}")
    print("-" * 90)
    for r in all_results:
        print(f" {r['component']:<45} {r['mean_ms']:<11} {r['median_ms']:<13} {r['p95_ms']:<10} {r['p99_ms']:<10}")
    print("=" * 90)

    # Hop budget comparison
    hop_budget_ms = 487.5
    e2e_p95 = res_e2e["p95_ms"]
    headroom_pct = round(((hop_budget_ms - e2e_p95) / hop_budget_ms) * 100.0, 1)
    print(f"\nReal-Time Hop Budget Headroom:")
    print(f"  - Configured Audio Hop Interval: {hop_budget_ms} ms")
    print(f"  - End-to-End P95 Execution Time: {e2e_p95} ms")
    print(f"  - Timing Headroom:               {headroom_pct}% (Budget surplus before audio drop risk)")
    print("=" * 90 + "\n")

    if output_json:
        output_json.parent.mkdir(parents=True, exist_ok=True)
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp_iso": datetime.now().isoformat(),
                "hop_budget_ms": hop_budget_ms,
                "headroom_pct": headroom_pct,
                "benchmarks": all_results,
            }, f, indent=2)
        print(f"Saved benchmark results to {output_json}")

    return all_results


def main():
    parser = argparse.ArgumentParser(description="Pipeline Latency Benchmark.")
    parser.add_argument("--iters", type=int, default=30, help="Number of benchmark iterations (default: 30).")
    parser.add_argument("--output", type=str, default="reports/stage8_5/latency_benchmarks.json", help="Output JSON path.")
    args = parser.parse_args()

    out_path = backend_dir / args.output if args.output else None
    run_benchmarks(num_iterations=args.iters, output_json=out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
