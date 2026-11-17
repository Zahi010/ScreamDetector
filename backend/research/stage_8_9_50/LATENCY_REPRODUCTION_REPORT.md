# Latency Reproduction & Concurrency Benchmark — Stage 8.9.50

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.

---

## 1. Executive Summary & Verification of Gate 5

Gate 5 specifies: **P95 computational inference latency $\le 25.0\text{ ms}$**.

- **Direct Complete Pipeline P95 Latency:** **0.788 ms** (Target: $\le 25.0\text{ ms}$) — **GATE 5 STATUS: PASS**.
- **Median (P50) Latency:** **0.514 ms**.
- **P99 Latency:** **1.004 ms**.
- **Maximum Observed Latency:** **1.867 ms**.
- **Execution Headroom:** **31.7x faster** than the mandatory 25 ms ceiling.
- **Concurrency:** 8 concurrent streams require only **2.961 ms** P95 (0 missed 100 ms audio-hop deadlines out of 1000 iterations).

---

## 2. Component Latency Decomposition (Single Stream, N=2,000 Iterations)

| Processing Component | P50 (ms) | P95 (ms) | P99 (ms) | Fraction of Pipeline |
| :--- | :---: | :---: | :---: | :---: |
| **1. DualEncoder Model Forward Pass** | 0.366 ms | 0.589 ms | 0.769 ms | 71.2% |
| **2. Intervention D Whistle Filter (DSP)** | 0.001 ms | 0.002 ms | 0.003 ms | 0.3% |
| **3. Spectral / Subband DSP Feature Extraction** | 0.141 ms | 0.229 ms | 0.269 ms | 27.4% |
| **Direct Complete Pipeline Measured End-to-End** | **0.514 ms** | **0.788 ms** | **1.004 ms** | **100.0%** |

> [!NOTE]
> Complete pipeline latency was measured directly in an uninterrupted timing block, complying strictly with Section 8 requirements (not derived by summing percentiles).

---

## 3. Multi-Stream Concurrency Benchmark

| Concurrent Streams | Batch P50 (ms) | Batch P95 (ms) | Batch P99 (ms) | Max (ms) | Missed 100 ms Hop Deadlines | Throughput (FPS) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1 Stream** | 0.499 ms | 0.747 ms | 0.893 ms | 1.156 ms | 0 | 2004.0 |
| **2 Streams** | 2.362 ms | 2.720 ms | 3.035 ms | 4.602 ms | 0 | 846.7 |
| **4 Streams** | 2.494 ms | 2.881 ms | 3.166 ms | 34.815 ms | 0 | 1604.1 |
| **8 Streams** | 2.516 ms | 2.961 ms | 3.225 ms | 4.994 ms | 0 | 3180.1 |

---

## 4. Hardware Environment & Measurement Rigor
- **OS / Hardware:** Windows 11 Enterprise (x86_64), Intel Core architecture.
- **Runtime Engine:** PyTorch CPU inference with oneDNN acceleration.
- **Peak Resident Set Size (Memory):** 314.4 MB.
- **CPU Utilization:** 210.0%.
- **Timing Precision:** Python `time.perf_counter` with 50 discarded warm-up runs.
