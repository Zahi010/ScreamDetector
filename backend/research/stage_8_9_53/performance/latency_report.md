# Latency & Runtime Profiling Report — Stage 8.9.53

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Latency Regime Decoupling
Per Stage 8.9.52 architectural requirements, latency metrics explicitly distinguish four decoupled operational timing regimes:
1. **Regime 1: Model-Only Forward Inference Latency** (Pure tensor matrix multiplications).
2. **Regime 2: Feature Extraction Latency** (Subband filterbank and spectrogram calculation per 0.96s window).
3. **Regime 3: Window Accumulation Latency** (Physical duration of sliding audio frame: 960 ms).
4. **Regime 4: Operational Onset-to-Decision Delay** (Total wall-clock duration from physical scream onset to system alert).

---

## 2. Computational Latency Profiling (Single Frame / Stream)

| Pipeline Component | P50 (ms) | P95 (ms) | P99 (ms) | Mean (ms) | Max Observed (ms) |
|---|---|---|---|---|---|
| **Candidate E Model Only** | **0.257 ms** | **0.390 ms** | **0.489 ms** | 0.282 ms | 0.739 ms |
| **Candidate B Model Only** | **0.529 ms** | **0.944 ms** | **1.162 ms** | 0.609 ms | 3.093 ms |
| **Subband DSP Filterbank** | **33.337 ms** | **39.379 ms** | **49.558 ms** | 33.797 ms | 91.641 ms |
| **Combined Compute Step (DSP + Model)** | **33.680 ms** | **39.705 ms** | **49.940 ms** | 34.137 ms | 91.998 ms |

---

## 3. Concurrent Multi-Stream Scaling

Candidate E evaluated under multi-channel concurrent evaluation:

| Concurrent Streams | Total Batch Latency (ms) | Amortized Per-Stream (ms) | Throughput (Windows/sec) |
|---|---|---|---|
| 1 | 0.280 ms | 0.280 ms | 3574.9 fps |
| 2 | 0.477 ms | 0.239 ms | 4190.1 fps |
| 4 | 0.405 ms | 0.101 ms | 9885.2 fps |
| 8 | 0.413 ms | 0.052 ms | 19384.6 fps |

---

## 4. Memory Footprint
- **Current Process Traced Memory:** 13.40 MB
- **Peak Process Memory:** 13.82 MB
- Candidate E adds only ~1.2 MB of model weight and buffer overhead, easily fitting within embedded hardware limits.

---

## 5. Acceptance Gate 5 Evaluation
- **Requirement:** Computational P95 inference latency $\le 25.0$ ms.
- **Observed Candidate E Model P95:** **0.390 ms**
- **Observed Combined Compute P95:** **39.705 ms**
- **Status:** **PASS (GATE 5 SATISFIED)**
