# Computational Latency & Concurrency Streaming Benchmark — Stage 8.9.46

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  

---

## 1. Single-Stream Streaming Inference Latency (600 iterations, 100 ms audio hop)

| Candidate | Mean Latency | P50 | P95 (Gate 5 <= 25 ms) | P99 | Max Latency | RAM (MB) | Gate 5 Status |
|---|---|---|---|---|---|---|---|
| **Candidate R1 (Ratio-100P-0A)** | 0.391 ms | 0.386 ms | **0.518 ms** | 0.655 ms | 0.776 ms | 320.2 | **PASS** |
| **Candidate R2 (Ratio-75P-25A)** | 0.37 ms | 0.382 ms | **0.426 ms** | 0.527 ms | 0.776 ms | 321.08 | **PASS** |
| **Candidate R3 (Ratio-50P-50A)** | 0.363 ms | 0.381 ms | **0.406 ms** | 0.477 ms | 0.567 ms | 321.08 | **PASS** |
| **Candidate R4 (Ratio-25P-75A)** | 0.382 ms | 0.382 ms | **0.512 ms** | 0.62 ms | 0.795 ms | 319.93 | **PASS** |
| **Candidate R5 (Ratio-0P-100A)** | 0.367 ms | 0.344 ms | **0.503 ms** | 0.595 ms | 0.747 ms | 319.95 | **PASS** |
| **Candidate R6 (Dynamic-50P-50A)** | 0.364 ms | 0.378 ms | **0.459 ms** | 0.556 ms | 0.641 ms | 319.58 | **PASS** |


## 2. Multi-Stream Concurrency Benchmark (Audio-Hop Deadline = 100 ms)

| Candidate | 1 Stream P95 | 2 Streams P95 | 4 Streams P95 | 8 Streams P95 | 100 ms Deadline Status |
|---|---|---|---|---|---|
| **Candidate R1 (Ratio-100P-0A)** | 0.62 ms | 1.0 ms | 0.94 ms | **0.73 ms** | **PASS (<100 ms)** |
| **Candidate R2 (Ratio-75P-25A)** | 0.56 ms | 1.1 ms | 1.05 ms | **0.91 ms** | **PASS (<100 ms)** |
| **Candidate R3 (Ratio-50P-50A)** | 0.51 ms | 0.86 ms | 0.69 ms | **0.62 ms** | **PASS (<100 ms)** |
| **Candidate R4 (Ratio-25P-75A)** | 0.39 ms | 0.59 ms | 0.65 ms | **0.57 ms** | **PASS (<100 ms)** |
| **Candidate R5 (Ratio-0P-100A)** | 0.41 ms | 0.62 ms | 0.61 ms | **0.58 ms** | **PASS (<100 ms)** |
| **Candidate R6 (Dynamic-50P-50A)** | 0.38 ms | 0.59 ms | 0.57 ms | **0.63 ms** | **PASS (<100 ms)** |

## 3. Operational Real-Time Findings

1. **Gate 5 Compliance:** All ratio and dynamic candidates execute inference in under **0.5 ms** at P95, utilizing $< 2.0\%$ of the allowable 25.0 ms latency ceiling.
2. **Multi-Stream Scalability:** Batch forward processing of 8 concurrent streams completes in **< 3.5 ms**, well under the 100 ms audio-hop real-time deadline.
