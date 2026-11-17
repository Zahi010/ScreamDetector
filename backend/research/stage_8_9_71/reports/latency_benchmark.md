# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.71 — LATENCY, CONCURRENCY & STREAMING PIPELINE BENCHMARK

**Mandatory Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.  
**Research Stage:** Stage 8.9.71  
**Target Architecture:** Candidate 71-D (Flux-Conditioned Resonance & Streamlined 3-Veto Multi-Resolution)  
**Host Environment:** Windows x64 CPU Execution (PyTorch CPU, Single & Multi-Stream)  

---

## 1. Executive Summary

This report delivers empirical benchmarks for Candidate 71-D on host CPU, rigorously distinguishing between:
1. **Model-Only CPU Inference Latency (Governed by Gate 5):** Evaluates the raw PyTorch neural forward pass.
2. **Complete Downstream Pipeline Latency:** Evaluates real-time audio windowing, multi-resolution C5 feature extraction, vocal non-linear acoustics extraction, neural forward pass, and multi-stage veto evaluation.

### Key Latency Findings:
- **Gate 5 Compliance (Model-Only CPU P95):** **0.402 ms** (Target: $\le 25.0$ ms) — **PASSED** ($> 62.1\times$ faster than ceiling).
- **Complete Pipeline P95 Latency:** **22.56 ms** (Audio Hop Deadline: 250.0 ms) — **PASSED** ($> 11.1\times$ real-time headroom).

---

## 2. Model-Only Inference Latency Table (Gate 5)

Evaluated across 100 warmup iterations and 1,000 timed evaluations:

| Stream Concurrency | Batch Size | Mean Latency | Median (P50) | P95 Latency (Gate 5) | P99 Latency | Gate 5 Ceiling | Headroom Margin |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1 Stream** | 1 | 0.317 ms | 0.309 ms | **0.402 ms** | 0.436 ms | 25.000 ms | **62.1x faster** |
| **2 Streams** | 2 | 0.542 ms | 0.548 ms | **0.661 ms** | 1.015 ms | 25.000 ms | **37.8x faster** |
| **4 Streams** | 4 | 0.548 ms | 0.550 ms | **0.645 ms** | 0.708 ms | 25.000 ms | **38.7x faster** |
| **8 Streams** | 8 | 0.554 ms | 0.554 ms | **0.644 ms** | 0.735 ms | 25.000 ms | **38.8x faster** |

---

## 3. Complete Downstream Pipeline Latency

Includes:
1. Ring buffer audio slice extraction (250 ms short-branch window = 4,000 samples).
2. Ring buffer sustained audio slice extraction (1,000 ms sustained-branch window = 16,000 samples).
3. Short-branch C5 subband energy + phonation extraction (17 dims).
4. Sustained-branch C5 subband energy + phonation extraction (17 dims).
5. Vocal non-linear acoustics extraction (Roughness 30–150 Hz, HF Concentration Ratio, Spectral Flux, HNR, Spectral Flatness = 5 dims).
6. Multi-resolution feature concatenation ($22 + 22 = 44$ dims).
7. Dual-branch gated neural forward pass.
8. Streamlined 3-veto adjudication + flux-conditioned resonance rescue.

- **Mean Pipeline Latency:** 20.58 ms
- **Median (P50) Latency:** 20.26 ms
- **P95 Pipeline Latency:** **22.56 ms**
- **P99 Pipeline Latency:** 26.16 ms
- **Audio-Hop Real-Time Deadline:** 250.0 ms (4 hops/sec at 16 kHz).
- **Time-Slice Consumption:** Complete processing consumes only **9.0%** of each hop's available duration, providing **11.1x real-time headroom**.

---

## 4. Streaming Buffer Boundaries & Edge Cases

- **Buffer Boundary Ring-Buffering:** The 250 ms hop is strictly aligned with the 4,000 sample increment.
- **Short-Event Handling:** Audio events $< 250$ ms are zero-padded to 4,000 samples, preserving sharp onsets without dropping samples.
- **End-of-File (EOF) Flushing:** Trailing residual buffers are padded with silence to ensure short screams at recording boundaries are not truncated.
- **Memory Stability:** Feature arrays and PyTorch tensors are pre-allocated in ring buffers without heap fragmentation or memory leakage across continuous streaming runs.
