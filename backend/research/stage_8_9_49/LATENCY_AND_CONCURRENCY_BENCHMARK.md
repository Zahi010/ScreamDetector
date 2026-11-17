# Computational Latency & Concurrency Benchmark — Stage 8.9.49

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.

---

## 1. Executive Summary & Verification of Gate 5

Gate 5 mandates that the complete computational inference latency P95 must not exceed **25.0 ms** (to preserve real-time streaming capability across audio hops).

- **Single-Stream Complete Pipeline P95 Latency:** **2.902 ms** (Target: $\le 25.0\text{ ms}$) — **GATE 5 STATUS: PASS**.
- **Headroom:** **8.6x faster** than the mandatory latency envelope.
- **8-Stream Batch P95 Latency:** **4.562 ms** (0 missed 100 ms audio hop deadlines out of 1000 iterations).

---

## 2. Component-Level Latency Decomposition (Single Stream, N=2,000 Iterations)

| Pipeline Stage | P50 (Median) | P95 | P99 | Percent of Total Runtime |
| :--- | :---: | :---: | :---: | :---: |
| **1. DualEncoder Model Forward Pass** | 0.416 ms | 0.726 ms | 0.951 ms | 21.6% |
| **2. Research Rejection Layer (Interv D)** | 1.336 ms | 2.060 ms | 2.417 ms | 69.4% |
| **3. Spectral / Subband DSP Feature Extraction** | 0.128 ms | 0.225 ms | 0.302 ms | 6.6% |
| **4. Post-Processing & Threshold Calibration** | 0.001 ms | 0.002 ms | 0.003 ms | 0.2% |
| **Complete Pipeline End-to-End** | **1.925 ms** | **2.902 ms** | **3.323 ms** | **100.0%** |

---

## 3. Multi-Stream Concurrency Benchmark

| Concurrent Audio Streams | Batch P50 (ms) | Batch P95 (ms) | Batch P99 (ms) | Missed 100 ms Hop Deadlines | Throughput (FPS) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **1 Stream** | 1.759 ms | 2.594 ms | 3.014 ms | 0 | 568.6 |
| **2 Streams** | 0.419 ms | 0.596 ms | 0.820 ms | 0 | 4769.3 |
| **4 Streams** | 3.984 ms | 4.516 ms | 5.064 ms | 0 | 1003.9 |
| **8 Streams** | 4.048 ms | 4.562 ms | 4.943 ms | 0 | 1976.5 |

---

## 4. Hardware Environment & Runtime Metrics
- **OS:** Windows 11 Enterprise (x86_64).
- **Execution Engine:** PyTorch CPU inference with Intel oneDNN acceleration.
- **Peak Process Memory:** 316.5 MB.
- **CPU Utilization:** 105.9% single-core equivalent.
- **Measurement Rigor:** 50 warm-up runs discarded, high-precision `time.perf_counter` timers, clean process isolation.
