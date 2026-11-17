# STAGE 8.9.33 — PERFORMANCE, CONCURRENCY & LATENCY BENCHMARK REPORT

**Project:** Festival Scream Detector  
**Stage:** 8.9.33 — Dual-Objective Optimization, Hard-Negative Discrimination & Independent Validation  
**Operating Mode:** Offline-First Machine Learning Research & Systems Engineering Benchmark  
**Production Status:** STRICTLY FROZEN (Production Decision Threshold: `0.3500`)  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Hardware Profile:** AMD Ryzen 7 5700U with Radeon Graphics (1.80 GHz, 8 Cores, 16 Logical Processors), 16.0 GB RAM, Windows 11 x64  

---

## 1. THREE CRITICAL LATENCY DOMAINS

To avoid methodological conflation, Stage 8.9.33 strictly categorizes and separates three distinct temporal concepts:

1. **A. Computational Inference Latency:** The processor wall-clock time required to execute feature extraction, neural forward passes, and threshold classification for a single audio window.
2. **B. Physical Audio Hop Scheduling Deadline:** The wall-clock duration of new incoming PCM samples per window stride. For a 100 ms hop (1,600 samples @ 16 kHz), the system has an upper bound of 100 ms before buffer overrun occurs.
3. **C. Operational Onset-to-Detection Delay:** The total elapsed physical time from when a vocal scream commences in the acoustic environment until an alert boolean flag is emitted.

---

## 2. STAGE-BY-STAGE LATENCY PROFILING (SINGLE STREAM)

Benchmarking the exact Dual-Encoder candidate over 100 continuous iterations:

| Pipeline Stage | Mean Latency (ms) | Median P50 (ms) | P95 Latency (ms) | P99 Latency (ms) | Max Latency (ms) | Computational Gate Target | Target Met? |
|---|---:|---:|---:|---:|---:|---|---|
| **Ring-Buffer Ingestion & Boundary Check** | 0.005 ms | 0.004 ms | 0.012 ms | 0.015 ms | 0.018 ms | $\le 1.00\text{ ms}$ | **PASS** |
| **Acoustic & Semantic Feature Extraction** | 18.204 ms | 18.203 ms | 18.225 ms | 18.241 ms | 18.250 ms | $\le 22.00\text{ ms}$ | **PASS** |
| **Dual-Encoder PyTorch Forward Pass** | 0.258 ms | 0.251 ms | 0.334 ms | 0.380 ms | 0.412 ms | $\le 2.00\text{ ms}$ | **PASS** |
| **Decision Policy & Threshold Check** | 0.002 ms | 0.002 ms | 0.003 ms | 0.004 ms | 0.005 ms | $\le 0.50\text{ ms}$ | **PASS** |
| **Total End-to-End Computational Pipeline** | **18.469 ms** | **18.460 ms** | **18.574 ms** | **18.640 ms** | **18.685 ms** | $\mathbf{\le 25.00\text{ ms}}$ | **PASS (Gate 5 Passed)** |

**Key Finding:** The Dual-Encoder architecture adds only **0.26 ms** of computational overhead over raw YAMNet extraction, easily meeting Gate 5 with a $6.43\text{ ms}$ margin.

---

## 3. MULTI-STREAM CONCURRENCY SCALING (1, 2, 4, 8 STREAMS)

To validate production readiness under multi-channel audio feeds, we executed concurrent streaming benchmarks across 1, 2, 4, and 8 simultaneous simulated audio streams:

| Concurrent Streams | Total Hops Processed | Wall-Clock Time (s) | Throughput (Hops / s) | P50 Latency (ms) | P95 Latency (ms) | Max Latency (ms) | Physical Hop Deadline Misses (>100ms) | Deadline Miss Rate (%) | Computational Gate Met ($\le 25\text{ms}$)? |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| **1 Stream** | 25 | 0.418 s | 59.81 hops/s | 16.37 ms | 16.79 ms | 18.21 ms | 0 | 0.00% | **PASS** |
| **2 Streams** | 50 | 0.426 s | 117.37 hops/s | 16.72 ms | 17.02 ms | 18.44 ms | 0 | 0.00% | **PASS** |
| **4 Streams** | 100 | 0.465 s | 215.05 hops/s | 18.04 ms | 18.60 ms | 19.82 ms | 0 | 0.00% | **PASS** |
| **8 Streams** | 200 | 0.482 s | 414.94 hops/s | 17.59 ms | 20.01 ms | 21.85 ms | 0 | 0.00% | **PASS** |

### 3.1 Concurrency Performance Analysis
1. **Zero Deadline Misses:** Across all 375 multi-stream hops tested, exactly 0 hops exceeded the 100 ms physical audio ingestion deadline (miss rate = 0.00%).
2. **Linear Throughput Scaling:** System throughput scaled from 59.8 hops/s (1 stream) to 414.9 hops/s (8 streams).
3. **P95 Latency Stability:** Even under an 8-stream workload, the 95th percentile latency was **20.01 ms**, well under the 25.00 ms computational limit.
4. **Memory Stability:** Circular buffer pre-allocation resulted in zero dynamic memory allocations per hop, maintaining a flat memory profile without garbage collection stutter.
