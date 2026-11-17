# Computational Latency & Concurrency Stress Test Benchmark — Stage 8.9.47

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.

---

## 1. Executive Summary & Verification Scope

This benchmark profiles the computational inference latency and multi-stream concurrency capacity of the frozen **Candidate R5 (DualEncoderAcousticModel)** pipeline under real-time streaming constraints.

- **Profiling Regime:** 2,000 measured iterations following 200 warm-up passes.
- **Audio Hop Budget:** 100 ms audio-hop deadline (1,600 samples at 16 kHz).
- **Gate 5 Target Requirement:** Computational P95 latency <= 25.0 ms.
- **Observed Pipeline P95 Latency:** **0.662 ms** (GATE 5 STRICT PASS)
- **Memory Footprint:** 206.9 MB RSS | **CPU Load:** 0.0%
- **Multi-Stream Capacity:** Up to 8 concurrent streams processed in **1.480 ms** P95 (0 missed deadlines).

---

## 2. Component Latency Decomposition (Single Stream)

| Pipeline Stage | Implementation Details | P50 Latency | P95 Latency | P99 Latency | Max Latency | Percentage of Budget (100ms) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **DSP Feature Extraction** | RMS, ZCR, subband energy filters on 100ms buffer | 0.070 ms | 0.123 ms | 0.150 ms | 10.256 ms | 0.12% |
| **Model Forward Pass** | DualEncoderAcousticModel forward evaluation (PyTorch CPU) | 0.314 ms | 0.553 ms | 0.771 ms | 2.273 ms | 0.55% |
| **Calibration & Post-Proc** | Sigmoid activation, threshold comparison (theta=0.8700) | 0.006 ms | 0.011 ms | 0.016 ms | 0.171 ms | 0.01% |
| **Complete Pipeline** | **End-to-End Computational Inference Cycle** | **0.419 ms** | **0.662 ms** | **0.880 ms** | **2.386 ms** | **0.66%** |

---

## 3. Multi-Stream Concurrency Stress Test

| Concurrent Audio Streams | Batch Evaluation Strategy | P50 Latency | P95 Latency | P99 Latency | Max Observed | Missed 100ms Hop Deadlines | Concurrency Headroom |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1 Stream** | Vectorized PyTorch batch evaluation | 0.441 ms | **0.631 ms** | 0.771 ms | 5.723 ms | **0/500** | 99.4% spare capacity |
| **2 Streams** | Vectorized PyTorch batch evaluation | 0.635 ms | **0.975 ms** | 1.260 ms | 1.893 ms | **0/500** | 99.0% spare capacity |
| **4 Streams** | Vectorized PyTorch batch evaluation | 0.887 ms | **0.991 ms** | 1.094 ms | 1.327 ms | **0/500** | 99.0% spare capacity |
| **8 Streams** | Vectorized PyTorch batch evaluation | 1.299 ms | **1.480 ms** | 1.558 ms | 1.634 ms | **0/500** | 98.5% spare capacity |

---

## 4. Latency Boundary Disclaimers

1. **Computational vs Physical Latency:** The measured P95 latency (0.45 ms) represents strictly the algorithmic computation time per audio hop. It does not include hardware ADC buffer latency (e.g. 100 ms physical audio collection window) or acoustic propagation delay.
2. **Operational Real-Time Guarantee:** With 8 concurrent streams consuming less than 3.5 ms per 100 ms hop, the system provides >96% idle CPU headroom, easily preventing audio buffer overrun on modest host hardware.
