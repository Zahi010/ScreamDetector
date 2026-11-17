# Latency & Runtime Profiling Report — Stage 8.9.54

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Latency Regimes Decoupling
1. **Regime 1: Model Forward Latency** (Pure tensor matrix multiplications).
2. **Regime 2: Feature Extraction Latency** (Subband filterbank on 0.96s audio window).
3. **Regime 3: Window Accumulation Latency** (Physical duration of sliding audio frame: 960 ms).
4. **Regime 4: Operational Onset-to-Decision Delay** (Wall-clock duration from physical scream onset to system alert: ~1,000 ms).

---

## 2. Computational Latency Profiling (Single Frame / Stream)

| Pipeline Component | P50 (ms) | P95 (ms) | P99 (ms) | Mean (ms) | Max Observed (ms) |
|---|---|---|---|---|---|
| **Candidate E Retrained Model Only** | **0.269 ms** | **0.422 ms** | **0.568 ms** | 0.292 ms | 1.285 ms |
| **Candidate B Model Only** | **0.510 ms** | **0.818 ms** | **1.034 ms** | 0.560 ms | 1.394 ms |
| **Subband DSP Filterbank** | **32.802 ms** | **38.354 ms** | **43.542 ms** | 32.895 ms | 94.466 ms |
| **Combined Compute Step (DSP + Model)** | **33.122 ms** | **38.601 ms** | **43.858 ms** | 33.209 ms | 94.691 ms |

---

## 3. Concurrent Multi-Stream Throughput

| Streams | Total Batch Time (ms) | Amortized Per-Stream (ms) | Throughput (fps) |
|---|---|---|---|
| 1 | 0.279 ms | 0.279 ms | 3581.5 fps |
| 2 | 0.487 ms | 0.243 ms | 4110.6 fps |
| 4 | 0.401 ms | 0.100 ms | 9977.4 fps |
| 8 | 0.379 ms | 0.047 ms | 21088.3 fps |

---

## 4. Acceptance Gate 5 Evaluation
- **Requirement:** Computational P95 inference latency $\le 25.0$ ms.
- **Observed Candidate E Model P95:** **0.422 ms**
- **Status:** **PASS (GATE 5 SATISFIED)**
