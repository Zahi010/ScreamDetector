# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
# Stage 8.9.68 — Neural Inference & Pipeline Latency Benchmark Report

**Stage:** 8.9.68 — SNR-Adaptive Roughness Calibration, Recall Recovery & Multi-Class Generalization  
**Component Evaluated:** Dual-Resolution Gated Network & Acoustic Feature Extraction Pipeline  
**Target Criterion:** Acceptance Gate 5 (Model-Only Neural P95 Latency $\le 25.0\text{ ms}$)  
**Hardware Environment:** Intel Core i7 / AMD CPU Benchmark (Single Core, Single Thread, PyTorch 2.x CPU)  
**Safety Notice:** Experimental acoustic prototype. Not certified for life-safety alerting, emergency dispatch, or security response.

---

## 1. Executive Summary

A critical engineering constraint for real-time edge deployment is low inference latency. High computational latency causes backlog buffering, drops audio packets, and delays threat warning. Acceptance Gate 5 mandates that the neural forward pass latency must remain under **25.0 ms P95**.

Benchmarking across 2,000 inference cycles demonstrated that Candidate 68-D achieves a neural model P95 latency of **0.409 ms** and an end-to-end pipeline P95 latency of **3.72 ms**, overwhelmingly **PASSING Acceptance Gate 5**.

---

## 2. Benchmark Methodology

Latency profiling was performed under controlled test harness conditions:
- **Audio Inputs:** 16,000 Hz 16-bit PCM single-channel streaming frames.
- **Warmup:** 100 burn-in iterations prior to measurement to eliminate cache cold-start effects.
- **Measurement Tool:** High-resolution monotonic clock (`time.perf_counter()`).
- **Sample Size:** 2,000 consecutive windows.

---

## 3. Neural Model Forward Pass Latency (Gate 5 Primary Metric)

The forward pass encompasses tensor transfer, short-branch linear projection, sustained-branch projection, gating sigmoid evaluation, convex fusion, and decision head calculation:

| Percentile Metric | Production Baseline (Stage 5 LR) | Candidate 65-F (Stage 8.9.66) | Candidate 67-D (Stage 8.9.67) | Candidate 68-D (Champion) | Gate 5 Target | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **P50 (Median)** | 14.20 ms | 0.582 ms | 0.285 ms | **0.291 ms** | — | — |
| **P90** | 16.85 ms | 0.741 ms | 0.362 ms | **0.375 ms** | — | — |
| **P95** | 18.42 ms | 0.812 ms | 0.397 ms | **0.409 ms** | $\le 25.0\text{ ms}$ | **PASS** |
| **P99** | 22.10 ms | 1.150 ms | 0.518 ms | **0.542 ms** | — | — |
| **Mean $\pm$ Std** | $14.85 \pm 2.1\text{ ms}$ | $0.612 \pm 0.12\text{ ms}$ | $0.298 \pm 0.05\text{ ms}$ | **$0.306 \pm 0.06\text{ ms}$** | — | — |

Candidate 68-D operates at **1.6% of the Gate 5 latency budget**, providing an expansive 61x safety margin for embedded or low-power DSP hardware.

---

## 4. Full End-to-End Pipeline Component Decomposition

While Gate 5 evaluates the neural network forward pass, full edge deployment requires understanding total processing time including DSP feature extraction:

| Processing Pipeline Stage | P50 (ms) | P95 (ms) | P99 (ms) | % of Total Time | Hardware Optimization Path |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Short-Branch C5 DSP (250 ms)** | 0.42 ms | 0.58 ms | 0.81 ms | 15.6% | FFT optimization / fixed-point |
| **2. Sustained-Branch C5 DSP (1,000 ms)** | 0.78 ms | 1.05 ms | 1.42 ms | 28.2% | Circular buffer FFT caching |
| **3. Vocal Non-Linear Dynamics** | 1.45 ms | 1.82 ms | 2.35 ms | 48.9% | SIMD Hilbert transform / Welch |
| **4. Neural Model Forward Pass** | 0.29 ms | 0.41 ms | 0.54 ms | 11.0% | PyTorch C++ LibTorch / ONNX |
| **5. Multi-Stage Suppression Vetos** | 0.01 ms | 0.02 ms | 0.03 ms | 0.5% | Scalar branch checks |
| **Total End-to-End Latency** | **2.85 ms** | **3.72 ms** | **4.98 ms** | **100.0%** | Real-Time Factor: $0.014\times$ |

---

## 5. Real-Time Streaming Feasibility

For a 250 ms hop size, an end-to-end P95 latency of 3.72 ms corresponds to a Real-Time Factor (RTF) of:
$$\text{RTF} = \frac{3.72\text{ ms}}{250.0\text{ ms}} = 0.0148$$
A single CPU core can simultaneously process **up to 67 independent acoustic microphone channels in real time** without frame drops.

---

## 6. Artifact Links

- Predictions CSV: [candidate_68_val_predictions.csv](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_68/reports/candidate_68_val_predictions.csv)
- Scorecard Report: [stage_8_9_68_five_gate_scorecard.md](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_68/reports/stage_8_9_68_five_gate_scorecard.md)
- Dashboard Update Report: [stage_8_9_68_dashboard_update_report.md](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_68/reports/stage_8_9_68_dashboard_update_report.md)

