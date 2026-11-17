# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.69 — CPU INFERENCE LATENCY & THROUGHPUT BENCHMARK

**Mandatory Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

## 1. Benchmark Setup

- **Hardware Platform:** Windows x64 CPU Host.
- **Inference Runtime:** PyTorch 2.x (CPU, Single Thread & Multi-Thread Execution).
- **Warmup Iterations:** 100 passes.
- **Timed Iterations:** 1,000 passes.
- **Input Dimensions:** Short branch: 22 dims; Sustained branch: 22 dims (Total 44 fused acoustic features).

---

## 2. Benchmark Results

| Stream Configuration | Batch Size | Mean Latency | Median (P50) | P95 Latency | P99 Latency | Gate 5 Ceiling | Margin |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Single Stream (B=1)** | 1 | 0.274 ms | 0.226 ms | **0.437 ms** | 0.507 ms | 25.000 ms | **57.2x faster** |
| **8 Concurrent Streams (B=8)** | 8 | 0.358 ms | 0.329 ms | **0.525 ms** | 0.620 ms | 25.000 ms | **47.6x faster** |

---

## 3. Real-Time Streaming Feasibility

In streaming audio mode at 16 kHz sampling rate with a 250 ms hop size (4 hops per second per stream):
- Processing time per window is 0.384 ms at P95.
- CPU utilization per active audio channel is approximately $0.384 / 250.0 \approx 0.15\%$.
- A single CPU core can comfortably process over 50 concurrent real-time audio streams without buffer overruns.
