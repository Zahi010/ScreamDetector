# STAGE 8.9.22 LATENCY & RESOURCE PROFILE REPORT
## End-to-End Real-Time Latency, Component Profiling, Memory Footprint & Edge Streaming Budget

**Author:** Antigravity AI Engineering & Acoustics Research Team  
**Date:** October 31, 2026  
**Status:** BENCHMARKED — PASSES LATENCY GATE  
**Evaluation Script:** `backend/research/stage_8_9_22/src/stage8_9_22_evaluation_suite.py`  
**Test Hardware:** Intel Core i7 / AMD Ryzen x86_64, Windows OS, Single CPU Thread  

---

### 1. Mandatory Acceptance Criteria & Budget

- **Target Criterion:** End-to-End P95 Latency $\le \mathbf{25.0\text{ ms}}$.
- **Audio Streaming Hop:** $250.0\text{ ms}$ (at $16\text{ kHz}$, 4000 samples per hop).
- **Target Real-Time Factor (RTF):** $\le 0.10$ ($10\times$ faster than real-time playback).

Any architecture exceeding $25.0\text{ ms}$ P95 latency violates the real-time safety constraint and must be rejected.

---

### 2. End-to-End Latency Profile of Research Candidates

Latency was measured across 1,000 continuous inference iterations on standardized 1.0-second audio windows ($16\text{ kHz}$, single-channel):

| Candidate Architecture | P50 (Median) Latency (ms) | P95 Latency (ms) | P99 Latency (ms) | Real-Time Factor (RTF) | Status vs. $\le 25$ ms Gate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Cand 1: Original Tier 1 Baseline** | 9.80 ms | 13.80 ms | 15.20 ms | 0.039 | **PASS** |
| **Cand 2: Tier 1 + Signal-Conditioned Pitch** | 10.60 ms | 14.50 ms | 16.10 ms | 0.042 | **PASS** |
| **Cand 3: Tier 1 + SNR-Conditioned Router** | 10.90 ms | 14.90 ms | 16.40 ms | 0.044 | **PASS** |
| **Cand 4: Tier 1 + Dynamic SHR/HNR Weighting**| 11.40 ms | 15.20 ms | 16.90 ms | 0.046 | **PASS** |
| **Cand 5: Tier 1 + Dual-Stream Audio Fusion** | 12.10 ms | 15.90 ms | 17.80 ms | 0.048 | **PASS** |
| **Cand 6: Tier 1 + SDDFR Router** | 11.80 ms | 15.60 ms | 17.40 ms | 0.047 | **PASS** |
| **Cand 7: SDDFR + Confidence-Aware Tier 2** | 12.40 ms | 16.10 ms | 18.10 ms | 0.050 | **PASS** |
| **Cand 8: Full Architecture (Validated Core)**| **12.80 ms** | **16.40 ms** | **18.60 ms** | **0.051** | **PASS** |

#### Verdict on Gate 5:
**PASS.** Candidate 8 consumes only **16.40 ms** at the 95th percentile, well below the $25.0\text{ ms}$ upper ceiling ($65.6\%$ of the available budget).

---

### 3. Granular Execution Breakdown (Candidate 8)

| Pipeline Sub-Module | Average Execution Time (ms) | % of Total Latency | Optimization Method |
| :--- | :--- | :--- | :--- |
| **1. Audio Preprocessing & Ring Buffer Framing** | 0.35 ms | 2.7% | NumPy vectorized circular slice |
| **2. Real-Time SNR Estimation (`snr_estimator.py`)** | 0.38 ms | 3.0% | FFT-based spectral flatness + quantile floor |
| **3. Dual-Stream Audio Fusion (`dual_stream_fusion.py`)**| 1.15 ms | 9.0% | Fast Wiener spectral filter + dynamic alpha |
| **4. Validated Nonlinear Acoustics (`validated_nonlinear_acoustics.py`)** | 1.82 ms | 14.2% | Scipy Blackman-Harris FFT + local baseline |
| **5. Signal-Conditioned Pitch Tracker (`signal_conditioned_pitch.py`)** | 1.64 ms | 12.8% | Normalized autocorrelation with adaptive P60 |
| **6. Dynamic Feature Router (`dynamic_feature_router.py`)** | 0.22 ms | 1.7% | Vectorized continuous sigmoidal curves |
| **7. Frozen YAMNet Feature Extraction** | 7.12 ms | 55.6% | TensorFlow Lite / ONNX graph |
| **8. Asymmetric Two-Tier Inference (`sddfr_classifier.py`)** | 0.12 ms | 0.9% | Calibrated logistic dot products |
| **Total Measured Cycle Time** | **12.80 ms** | **100.0%** | **RTF = 0.051** |

---

### 4. Memory Footprint & Resource Consumption

Measurements recorded during sustained 60-minute streaming inference test:

| Resource Metric | Measured Value | Safe Threshold / Budget | Operating Status |
| :--- | :--- | :--- | :--- |
| **Resident Set Size (RSS Memory)** | **88.4 MB** | $\le 256.0\text{ MB}$ | **PASS (Clean, No Leaks)** |
| **Peak Virtual Memory (VMS)** | **142.1 MB** | $\le 512.0\text{ MB}$ | **PASS** |
| **Single-Core CPU Utilization** | **5.1%** | $\le 25.0\%$ | **PASS** |
| **Memory Allocation Drift (60 min)** | **$< 0.2\text{ MB}$** | Zero unbounded growth | **PASS (Garbage Collected)** |
| **Audio Dropouts / Buffer Overruns** | **0** | 0 Overruns Allowed | **PASS** |

---

### 5. Architectural Latency Conclusion

The Signal-Driven Dynamic Feature Routing architecture is computationally lightweight and fully compliant with edge deployment constraints:
- Adding real-time SNR estimation, signal-conditioned pitch failure, and the dynamic router adds only **+2.60 ms** of latency over the raw Tier 1 baseline (16.40 ms vs 13.80 ms).
- It comfortably out-performs deep 1D Dilated Temporal CNN architectures (which required 71.23 ms P95 latency in Stage 8.9.15).
