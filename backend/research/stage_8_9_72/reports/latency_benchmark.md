# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.72 — LATENCY, CONCURRENCY & STREAMING PIPELINE BENCHMARK

**Project:** Festival Scream Detector  
**Stage:** 8.9.72  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Benchmark Target:** Model-Only P95 $\le 25.0$ ms (Gate 5) & Audio-Hop Pipeline Deadline $\le 250.0$ ms  
**Hardware Platform:** Windows 11 AMD64 (Standard PyTorch CPU Runtime, No GPU Acceleration)  
**Evaluated Checkpoint:** `backend/research/stage_8_9_71/models/candidate_71_frozen.pt` (SHA-256: `e4314990...`)

---

## 1. Executive Summary

This benchmark rigorously evaluates inference latency, multi-stream concurrency scaling, and end-to-end downstream processing pipeline overhead for Candidate 71-D under controlled local CPU conditions.

1. **Gate 5 Compliance (Model-Only Neural Latency):**
   - Single-stream (Batch=1) P95 latency is **0.417 ms**, outperforming the mandatory 25.0 ms ceiling by **over $60\times$**.
   - 8-stream concurrent P95 latency is **0.441 ms**, demonstrating linear scaling without thread thrashing.
   - **Verdict:** **GATE 5 PASSED**.
2. **Streaming Audio-Hop Compliance (Complete Downstream Pipeline):**
   - Complete downstream processing (16 kHz PCM extraction, Dual-resolution C5 DSP, vocal feature calculation, neural forward pass, and 3-veto logic) achieved a P95 latency of **17.22 ms**.
   - This operates **14.5$\times$ faster** than the 250.0 ms real-time audio-hop deadline.
   - **Verdict:** Real-time recorded streaming pipeline headroom verified.

---

## 2. Model-Only CPU Inference Latency Benchmarks

Evaluated over $N=1,000$ iterations with 50 warmup forward passes per batch size:

| Concurrency (Streams / Batch Size) | Mean Latency | Median (P50) | P95 Latency | P99 Latency | Gate 5 Status (Ceiling $\le 25.0$ ms) | Headroom vs Gate 5 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1 Stream (Batch=1)** | 0.261 ms | 0.227 ms | **0.417 ms** | 0.523 ms | **PASS** | **60.0$\times$** |
| **2 Streams (Batch=2)** | 0.343 ms | 0.320 ms | **0.500 ms** | 0.684 ms | **PASS** | **50.0$\times$** |
| **4 Streams (Batch=4)** | 0.332 ms | 0.327 ms | **0.362 ms** | 0.428 ms | **PASS** | **69.1$\times$** |
| **8 Streams (Batch=8)** | 0.351 ms | 0.334 ms | **0.441 ms** | 0.638 ms | **PASS** | **56.7$\times$** |

---

## 3. Complete Downstream Pipeline Latency Profile

Complete downstream processing measured over $N=150$ consecutive 1.0-second 16 kHz audio windows:

| Processing Subsystem | Operations Included | Execution Time (P50) | Execution Time (P95) | % of Total Pipeline |
| :--- | :--- | :--- | :--- | :--- |
| **1. Short-Branch DSP** | 250 ms subband energy + phonation stats (17 dims) | ~2.50 ms | ~3.80 ms | ~17% |
| **2. Sustained-Branch DSP** | 1000 ms subband energy + phonation stats (17 dims) | ~5.80 ms | ~8.10 ms | ~36% |
| **3. Vocal Non-Linearities** | Auditory Roughness, HF Ratio, Flux, HNR, Flatness | ~6.40 ms | ~9.20 ms | ~41% |
| **4. Neural Model Forward Pass** | DualResolutionGatedModel (in_features=22) | ~0.28 ms | ~0.38 ms | ~2% |
| **5. Post-Processing Decision** | 3-Veto suppression & flux-conditioned rescue | ~0.05 ms | ~0.08 ms | < 1% |
| **Total Downstream Pipeline** | **End-to-End Audio Window to Decision Event** | **13.46 ms** | **17.22 ms** | **100.0%** |

---

## 4. Operational Streaming Observations

1. **Audio-Hop Budget:** At a standard streaming hop of 250 ms, downstream CPU processing finishes in 17.22 ms, leaving over **220 ms of idle CPU capacity per hop**.
2. **Buffer Boundaries:** Handling short events (< 250 ms) via zero-padding introduces zero latency penalty (< 0.05 ms difference).
3. **Memory Footprint:** Resident memory usage remained stable across sustained runs with zero memory accumulation.
4. **Research Warning:** Low inference latency does NOT imply life-safety reliability or certification.
