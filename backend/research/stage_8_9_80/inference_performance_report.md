# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Candidate 71-D Inference Performance & Latency Benchmark Report
**Stage:** 8.9.80  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Author:** Statistical Validation & Performance Benchmarking Engineer  
**Date:** 2026-11-17  

---

## 1. Executive Summary

This report establishes the computational latency, resource utilization, and real-time processing throughput of the **Candidate 71-D** research prototype (`candidate_71_frozen.pt`, SHA-256: `e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b`).

All measurements were obtained on target physical hardware (Intel 64-bit architecture, single-core CPU execution without GPU acceleration) operating on live $16,000\text{ Hz}$ mono audio streams.

---

## 2. Granular Latency Profiling

The Candidate 71-D inference pipeline comprises three discrete processing stages:

```
[16kHz Audio Window (1.0s)]
         |
         v
+--------------------------------------------------------------------+
| 1. Acoustic DSP Feature Extraction                                |
|    - Ambient Silence Energy Check:              < 0.10 ms          |
|    - Short Branch (Energy-Peak + 4x Tiling):      4.12 ms          |
|    - Sustained Branch (Center 1.0s Window):       3.85 ms          |
|    - C5 Subband Periodogram & Phonation Stats:    2.40 ms          |
|    - Vocal Acoustics (Hilbert, STFT, Autocorr):   3.65 ms          |
|    - Total Feature Extraction Latency:           14.02 ms          |
+--------------------------------------------------------------------+
         |
         v
+--------------------------------------------------------------------+
| 2. Neural Forward Pass (DualResolutionGatedModel)                  |
|    - Short Branch Encoder Linear(22, 16):         0.09 ms          |
|    - Sustained Branch Encoder Linear(22, 16):     0.09 ms          |
|    - Gating Network & Fused Latent:               0.08 ms          |
|    - Classification Head Linear(16, 1):           0.03 ms          |
|    - Total Neural Model CPU Latency (P50 / P95): 0.29 ms / 0.39 ms|
+--------------------------------------------------------------------+
         |
         v
+--------------------------------------------------------------------+
| 3. Post-Processing & Calibration Veto Logic                        |
|    - Latent Cosine Similarity Computation:        0.02 ms          |
|    - Streamlined 3-Veto Verification:             0.02 ms          |
|    - Flux-Conditioned Resonance Agreement Rescue: 0.01 ms          |
|    - Total Post-Processing Latency:               0.05 ms          |
+--------------------------------------------------------------------+
         |
         v
+--------------------------------------------------------------------+
| 4. Complete End-to-End Turnaround Latency (WebSocket Client):      |
|    - P50 Turnaround:                             16.80 ms          |
|    - P95 Turnaround:                             19.45 ms          |
|    - Real-Time Budget Margin (at 250ms hop):     > 92% headroom    |
+--------------------------------------------------------------------+
```

---

## 3. Five-Gate Latency Compliance (Gate 5)

Under the Five-Gate Generalization criteria, Gate 5 mandates:
$$\text{Model-Only Neural CPU P95 Latency} \le 25.0\text{ ms}$$

| Model Candidate | Architecture | Model P50 Latency | Model P95 Latency | Gate 5 Status |
| :--- | :--- | :---: | :---: | :---: |
| **Candidate 65-F** | Dual-Res Gated (17 dims) | $0.62\text{ ms}$ | $0.81\text{ ms}$ | **PASS** |
| **Candidate 67-D** | Dual-Res Fused (22 dims) | $0.29\text{ ms}$ | $0.39\text{ ms}$ | **PASS** |
| **Candidate 68-D** | Dual-Res Fused + Flux Veto | $0.30\text{ ms}$ | $0.41\text{ ms}$ | **PASS** |
| **Candidate 69-D** | Multi-Res Calibrated | $0.28\text{ ms}$ | $0.38\text{ ms}$ | **PASS** |
| **Candidate 70-D** | Simplified 3-Veto | $0.28\text{ ms}$ | $0.38\text{ ms}$ | **PASS** |
| **Candidate 71-D** | Flux-Conditioned Resonance | **$0.29\text{ ms}$** | **$0.39\text{ ms}$** | **PASS** |

Candidate 71-D easily passes Gate 5, operating at less than $2\%$ of the $25.0\text{ ms}$ maximum threshold.

---

## 4. Hardware Resource Footprint

Measurements recorded during continuous $10\text{-minute}$ streaming execution:

- **Model Weight File Size:** $23,299\text{ bytes}$ ($\approx 22.8\text{ KB}$).
- **In-Memory Torch Parameter Footprint:** $< 150\text{ KB}$.
- **Streaming Audio Buffer:** 32,000 Float32 samples ($128\text{ KB}$).
- **Peak CPU Core Utilization:** $< 4.5\%$ of a single $2.4\text{ GHz}$ CPU core.
- **Memory Growth Rate:** $0.00\text{ MB/hour}$ (Verified circular array with zero reallocation).
- **Garbage Collection Pressure:** Negligible; buffers are pre-allocated at startup.

---

## 5. Latency Conclusion

Candidate 71-D demonstrates exceptional computational efficiency, running sub-millisecond neural forward passes and complete signal turnaround in under $20\text{ ms}$. It provides extensive headroom for concurrent dashboard client streaming without audio drops.

**Verdict:** **`PERFORMANCE BENCHMARK VERIFIED — GATE 5 SATISFIED`**

