# Stage 8.9.29 — ONNX Runtime Export, Compatibility & Performance Report

**Stage:** 8.9.29 — Multi-Stream Concurrency Stress Testing & ONNX Runtime Packaging  
**Operating Mode:** Offline Research & Experimental Runtime Comparison  
**Date of Audit:** October 31, 2026  
**Status:** CERTIFIED EXPERIMENTAL EQUIVALENCE — 100.00% DECISION AGREEMENT  

---

## 1. Executive Summary

Stage 8.9.29 investigated ONNX Runtime as an alternative, lightweight inference backend for the core neural network component of the multi-stage pipeline: **Model C (Temporal 1D-CNN)**.

### Key Benchmark Findings:
- **Decision Agreement:** **100.00%** (0 mismatches across all 107 audited independent cohort recordings).
- **Numerical Drift:** Certified maximum probability delta of **5.9605e-07**, well below the floating-point tolerance of $1.0\times 10^-5$.
- **Latency Comparison:**
  - Compiled TensorFlow Model C: **1.16 ms** ($P_95$) / **0.89 ms** (Mean)
  - ONNX Runtime Model C (CPU): **0.18 ms** ($P_95$) / **0.13 ms** (Mean)
  - Performance Advantage: ONNX Runtime achieves an additional **6.91x speedup** on Model C inference.
- **Model Load Time:** ONNX Runtime initializes in **8.7 ms** vs **174.0 ms** for Keras (20.0x faster startup).

---

## 2. Model C Architectural & Conversion Specification

| Attribute | TensorFlow Reference | ONNX Exported Copy |
|---|---|---|
| **Source File** | `backend/research/stage_8_9_25/models/model_c_temporal_1d_cnn.keras` | `backend/research/stage_8_9_29/onnx/model_c_temporal_1d_cnn.onnx` |
| **Input Tensor** | `temporal_seq_input: float32[None, 70, 16]` | `temporal_seq_input: float32[None, 70, 16]` |
| **Output Tensor** | `temporal_prob: float32[None, 1]` | `temporal_prob: float32[None, 1]` |
| **Conversion Tool** | Keras 3 / TensorFlow 2.19 | `tf2onnx` v1.17.0 (Opset 17) |
| **Execution Provider** | Native CPU (AVX2/FMA) | `CPUExecutionProvider` (single-thread deterministic) |

---

## 3. Comprehensive Performance Comparison Table

| Metric | Compiled TensorFlow | ONNX Runtime (CPU) | Comparison / Ratio |
|---|---|---|---|
| **Model Load Time** | 173.95 ms | 8.68 ms | **20.0x faster** |
| **Warm-up Time (50 iters)** | 178.50 ms | 4.61 ms | **38.7x faster** |
| **Mean Inference Latency** | 0.892 ms | 0.129 ms | **6.91x faster** |
| **P50 Inference Latency** | 0.841 ms | 0.118 ms | **7.13x faster** |
| **P95 Inference Latency** | 1.160 ms | 0.179 ms | **6.48x faster** |
| **P99 Inference Latency** | 1.410 ms | 0.239 ms | **5.90x faster** |
| **Max Absolute Numerical Delta** | 0.00 | 5.9605e-07 | **Identical (< 1e-6)** |
| **Decision Agreement Rate** | 100.0% | 100.00% | **100% Agreement (0 mismatches)** |

---

## 4. Architectural & Production Decision

1. **Compatibility Confirmed:** Model C exports cleanly to ONNX with zero operator translation issues.
2. **Zero Functional Drift:** All classification decisions and scores remain identical to the TensorFlow baseline.
3. **Role Designation:** ONNX Runtime is validated as a high-performance **research alternative** for deployment environments where full TensorFlow wheels (500+ MB) are prohibitive. Per non-negotiable stage rules, the production classifier remains strictly frozen, and the compiled TensorFlow pipeline remains the primary research reference.
