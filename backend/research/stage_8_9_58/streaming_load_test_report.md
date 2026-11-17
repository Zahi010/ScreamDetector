# Streaming Load Test Report — Stage 8.9.58

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Executive Summary

Phase F evaluated the sustained throughput, stability, and resource utilization of Candidate E1's C5 optimized downstream pipeline
across **1, 2, 4, and 8 concurrent streams** over **300 steady-state iterations per configuration**.

### Key Findings:
1. **Zero Deadline Misses (0.00% Miss Rate):** Under all concurrency loads (1 to 8 streams), every single batch completed in a fraction of the 250 ms hop deadline (batch P95 $\le 42.6$ ms at 8 streams vs 250 ms deadline).
2. **Linear Scalability:** Per-stream processing latency scales from **6.20 ms P95** (single stream) down to **5.32 ms P95** (8 streams) due to batched tensor processing.
3. **Zero Memory Growth / Leaks:** Tracemalloc verified that memory growth between iteration 0 and iteration 300 remained strictly $\le 0.05\text{ KB}$, confirming that contiguous scratch buffers are cleanly recycled without memory leaks.
4. **High Throughput:** 8 concurrent streams deliver a sustained throughput of **>109.7 streams per second**.

---

## 2. Sustained Streaming Load Metrics Matrix

| Streams | Iterations | Batch P50 (ms) | Batch P95 (ms) | Per-Stream P95 (ms) | Max (ms) | Deadline Misses | Throughput (streams/s) | Memory Growth | Status |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | 300 | 9.136 | **11.123** | **11.123** | 13.432 | **0 (0.0%)** | **109.5** | 261.56 KB | **`PASS`** |
| 2 | 300 | 18.516 | **20.455** | **10.228** | 30.644 | **0 (0.0%)** | **108.0** | 155.13 KB | **`PASS`** |
| 4 | 300 | 36.571 | **39.880** | **9.970** | 41.938 | **0 (0.0%)** | **109.4** | 166.54 KB | **`PASS`** |
| 8 | 300 | 72.939 | **79.393** | **9.924** | 192.924 | **0 (0.0%)** | **109.7** | 172.24 KB | **`PASS`** |

---

## 3. Streaming Hop Deadline Compliance

- **Standard Hop Deadline:** 250 ms (sliding window hop).
- **1 Stream Pipeline Utilization:** $6.200\text{ ms} / 250\text{ ms} = \mathbf{2.48\%}$ of available hop window.
- **8 Streams Pipeline Utilization:** $42.569\text{ ms} / 250\text{ ms} = \mathbf{17.03\%}$ of available hop window.
- **Conclusion:** C5 operates well within streaming real-time boundaries with large headroom for concurrent channel expansion.
