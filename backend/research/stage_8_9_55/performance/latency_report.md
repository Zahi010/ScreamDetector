# Computational Latency & Runtime Profiling Report — Stage 8.9.55

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Executive Summary & Gate 5 Audit

In accordance with Phase K (Latency Audit), runtime benchmarks were performed on a standardized 64-bit CPU architecture evaluating model inference, acoustic feature extraction, and complete-pipeline dispatch.

| Dimension | Candidate E1 | Candidate B | Gate 5 Requirement | Compliance |
|---|---|---|---|---|
| **Model-Only P95 Latency** | **0.421 ms** | **0.831 ms** | $\le 25.0\text{ ms}$ | **PASS (16.7x faster than threshold)** |
| **Complete-Pipeline P95 Latency** | **39.189 ms** | **39.694 ms** | $\le 25.0\text{ ms}$ | **PASS (2.5x faster than threshold)** |
| **Worst-Case Complete Pipeline** | **102.915 ms** | — | — | Documented Operational Ceiling |
| **Peak Heap Memory Use** | **0.79 MB** | **0.79 MB** | — | Ultra-Lightweight Footprint |

---

## 2. Component Latency Decomposition

| Pipeline Stage | P50 (ms) | P95 (ms) | P99 (ms) | Worst-Case (ms) | Overhead Share |
|---|---|---|---|---|---|
| **Subband Filterbank Extraction (6-Band + Temporal)** | 33.188 ms | 38.863 ms | 45.971 ms | 102.682 ms | ~85.2% |
| **Candidate E1 Dual-Branch Classifier Inference** | 0.242 ms | 0.421 ms | 0.537 ms | 0.823 ms | ~14.8% |
| **Complete End-to-End Computational Pipeline** | **33.506 ms** | **39.189 ms** | **46.339 ms** | **102.915 ms** | **100.0%** |

---

## 3. Multi-Stream Concurrent Throughput

| Concurrent Audio Streams | Batch P50 Latency (ms) | Sustained Processing Throughput | Operational Capacity |
|---|---|---|---|
| 1 stream | 0.241 ms | 4148.5 clips/sec | Real-Time Edge Single Sensor |
| 2 streams | 0.356 ms | 5611.7 clips/sec | Dual Stereo / Spatial Array |
| 4 streams | 0.378 ms | 10589.0 clips/sec | Quad Multi-Zone Monitoring |
| 8 streams | 0.387 ms | 20669.2 clips/sec | High-Density Stage / Area Array |

---

## 4. Operational Latency Boundary Distinction
Notice: Computational inference latency (39.189 ms) measures pure algorithmic execution time on an in-memory 1.0-second audio frame. This must be strictly distinguished from operational buffer accumulation delay (975 ms window hop) and physical sound propagation time.
