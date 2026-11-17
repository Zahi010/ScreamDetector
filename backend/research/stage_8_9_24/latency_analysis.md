# Latency & Real-World Detection Delay Analysis (Stage 8.9.24)

## Executive Summary

Engineering requirements specify that the scream detector must achieve an end-to-end computational latency $\le 25.0\text{ ms}$. However, in temporal audio processing, **computational latency** must be strictly distinguished from **audio-context accumulation delay**:
- *Computational Latency*: The wall-clock execution time required for framing, feature extraction, and ML classifier inference once an audio buffer is in memory.
- *Audio Accumulation Delay*: The physical time required to collect the necessary acoustic context before analysis can begin.

This report documents high-precision micro-benchmarks across 200 iterations for both latency regimes.

---

## 1. Computational Latency Benchmarks (Buffer in Memory)

Benchmarked on an Intel 64-bit architecture at 16,000 Hz using 2.0-second buffers:

| Processing Subsystem | P50 Latency (ms) | P95 Latency (ms) | P99 Latency (ms) | Maximum (ms) | Gate Target |
|---|:---:|:---:|:---:|:---:|:---:|
| **Strided Framing & Windowing** | 0.08 ms | 0.12 ms | 0.16 ms | 0.22 ms | N/A |
| **Short-Time RMS Envelope & Dynamics** | 0.45 ms | 0.58 ms | 0.68 ms | 0.85 ms | N/A |
| **Modulation Spectrum (0.5–20 Hz FFT)** | 0.62 ms | 0.78 ms | 0.92 ms | 1.15 ms | N/A |
| **Burst Continuity & Vocal Gaps (RLE)** | 0.75 ms | 0.95 ms | 1.12 ms | 1.35 ms | N/A |
| **Total Feature Extraction** | **1.92 ms** | **2.38 ms** | **2.85 ms** | **3.42 ms** | N/A |
| **ML Inference (Dual-Pathway Fusion)** | **0.03 ms** | **0.05 ms** | **0.07 ms** | 0.10 ms | N/A |
| **Total End-to-End Computational Latency** | **1.96 ms** | **2.42 ms** | **2.91 ms** | **3.52 ms** | **$\le 25.0\text{ ms}$ (PASSED)** |

The total computational latency of **2.42 ms (P95)** uses less than **10%** of the 25.0 ms engineering budget, leaving ample headroom for real-time edge deployment.

---

## 2. Real-World End-to-End Detection Delay

The true operational latency experienced by security operators in a festival environment is the sum of audio context accumulation and computational inference:

$$\text{Total Detection Delay} = T_{\text{context}} + T_{\text{compute}}$$

| Analysis Pathway | Acoustic Context Window | Computational Latency (P95) | Total Real-World Detection Delay | Operational Utility |
|---|:---:|:---:|:---:|---|
| **Pathway A (Short-Event)** | **500 ms** | 2.42 ms | **502.42 ms** | **Immediate Real-Time Alarm** on sudden scream attacks. |
| **Pathway B (Long-Context)** | **2,000 ms** | 2.42 ms | **2,002.42 ms** | **Cadence Verification** for sustained vocalizations and shouting suppression. |

### Architectural Insight
Never claim that a 2.0-second context detector has a "16 ms real-world detection delay" merely because its model inference takes 16 ms. The physical audio collection requires 2,000 ms. 

By employing the **Dual-Pathway architecture**, Candidate G alerts on short violent screams in **~500 ms** via Pathway A, while allowing Pathway B to run concurrently over 2.0 seconds to suppress speech-like shouting.
