# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.70 — LATENCY, CONCURRENCY & STREAMING PIPELINE BENCHMARK

**Mandatory Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

---

## 1. Executive Summary

This report establishes the empirical latency profile for the simplified dual-resolution scream detector under controlled laboratory CPU execution, strictly distinguishing between **model-only inference latency** (the metric governed by Gate 5) and **complete downstream pipeline latency** (audio extraction + neural forward pass + multi-stage veto adjudication).

- **Gate 5 Compliance (Model-Only CPU P95):** **0.384 ms** (Target: $\le 25.0$ ms) — **PASSED** ($> 65\times$ faster than ceiling).
- **Complete Pipeline P95 Latency:** **16.66 ms** (Target: $\le 250.0$ ms audio hop deadline) — **PASSED** ($> 15.0\times$ faster than hop deadline).

---

## 2. Model-Only Inference Latency (Gate 5)

Host CPU: Windows x64. Execution: PyTorch CPU (Single & Multi-Stream). 100 warmup iterations, 1,000 timed passes.

| Concurrency (Streams) | Batch Size | Mean Latency | Median (P50) | P95 Latency | P99 Latency | Gate 5 Ceiling | Margin |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1 Stream** | 1 | 0.232 ms | 0.214 ms | **0.335 ms** | 0.473 ms | 25.000 ms | **74.7x faster** |
| **2 Streams** | 2 | 0.342 ms | 0.319 ms | **0.480 ms** | 0.593 ms | 25.000 ms | **52.0x faster** |
| **4 Streams** | 4 | 0.331 ms | 0.321 ms | **0.452 ms** | 0.586 ms | 25.000 ms | **55.3x faster** |
| **8 Streams** | 8 | 0.325 ms | 0.323 ms | **0.376 ms** | 0.495 ms | 25.000 ms | **66.5x faster** |

---

## 3. Complete Downstream Pipeline Latency

Includes:
1. Short-branch C5 subband energy + phonation extraction (250 ms window).
2. Sustained-branch C5 subband energy + phonation extraction (1,000 ms window).
3. Vocal non-linear acoustics extraction (Roughness 30–150 Hz, HFCR, Flux, HNR, Flatness).
4. Feature concatenation & dual-branch neural forward pass.
5. Calibrated multi-stage veto evaluation.

- **Mean Pipeline Latency:** 14.72 ms
- **Median (P50) Latency:** 14.45 ms
- **P95 Pipeline Latency:** **16.66 ms**
- **P99 Pipeline Latency:** 20.12 ms
- **Real-Time Hop Deadline:** 250.0 ms (4 hops/sec at 16 kHz).
- **Operational Headroom:** The complete processing pipeline consumes only approximately **6.7%** of each hop's available time slice.

---

## 4. Streaming Buffer Boundaries & Edge Cases

- **Buffer Boundary Alignment:** Short branch windows (4,000 samples = 250 ms) and sustained branch windows (16,000 samples = 1,000 ms) are ring-buffered at 4,000-sample hop increments.
- **Short-Event Handling:** Audio events lasting $< 250$ ms are zero-padded to 4,000 samples, preserving impulse onsets without buffer truncation.
- **End-of-File Flushing:** The streaming loop flushes residual audio buffers with trailing silence padding to ensure short screams arriving at the end of a recording are not dropped.
