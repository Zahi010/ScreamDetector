# Latency Measurement Provenance Report — Stage 8.9.56.1

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Executive Summary & Forensic Provenance Table

This audit traces every reported computational latency measurement across Stage 8.9.55 and Stage 8.9.56 to its exact originating script, lines of code, timing boundaries, input conditions, and aggregation formulas.

| Measurement | Stage | Originating Script | Input Data & Conditions | Timing Boundary | Raw Result & Percentiles |
|---|---|---|---|---|---|
| **Candidate E1 Model-Only P95 (0.421 ms)** | Stage 8.9.55 | `stage_8_9_55/scripts/benchmark_latency.py (lines 103-117)` | Random in-memory PyTorch tensors (1, 1024), (1, 6), (1, 6), (1, 11) | model_e forward pass only (`with torch.no_grad(): model_e(...)`) | P50 = 0.242 ms, P95 = 0.421 ms, P99 = 0.537 ms, Max = 0.823 ms |
| **Candidate B Model-Only P95 (0.831 ms)** | Stage 8.9.55 | `stage_8_9_55/scripts/benchmark_latency.py (lines 109-118)` | Random in-memory PyTorch tensors (1, 1024), (1, 6), (1, 6) | model_b forward pass only (`with torch.no_grad(): model_b(...)`) | P50 = 0.514 ms, P95 = 0.831 ms, P99 = 0.992 ms, Max = 1.334 ms |
| **Subband Feature Extraction P95 (38.863 ms)** | Stage 8.9.55 | `stage_8_9_55/scripts/benchmark_latency.py (lines 126-133)` | Random Gaussian float32 array (16,000 samples @ 16 kHz) | extract_subband_vector() only (6-band Butterworth filtfilt + temporal variance loop) | P50 = 33.188 ms, P95 = 38.863 ms, P99 = 45.971 ms, Max = 102.682 ms |
| **Candidate E1 'Complete-Pipeline' P95 (39.189 ms)** | Stage 8.9.55 | `stage_8_9_55/scripts/benchmark_latency.py (lines 136-139)` | Decoupled synthetic array addition: lat_fe[:200] + lat_e[:200] | Synthetic sum of 200 subband extractions + first 200 model forward passes | P50 = 33.506 ms, P95 = 39.189 ms, P99 = 46.339 ms, Max = 102.915 ms |
| **Candidate B 'Complete-Pipeline' P95 (39.694 ms)** | Stage 8.9.55 | `stage_8_9_55/scripts/benchmark_latency.py (line 196) & Stage 8.9.56 Table B` | None (No audio or combined benchmark run for Candidate B) | None (Theoretical sum of Candidate B model-only P95 + Subband extraction P95) | 39.694 ms (Erroneous: Candidate B does NOT use subband features; also sums percentiles) |
| **Candidate E1 Model-Only P95 (0.583 ms)** | Stage 8.9.56 | `stage_8_9_56/scripts/benchmark_full_pipeline_latency.py (lines 167-174)` | In-memory PyTorch tensors (1, 1024), (1, 6), (1, 6), (1, 11) | model_e forward pass + sigmoid (`logit_e = model_e(...); prob_e = sigmoid(...)`) | P50 = 0.3104 ms, P90 = 0.4984 ms, P95 = 0.5833 ms, P99 = 1.0772 ms, Max = 2.4532 ms |
| **Candidate B Model-Only P95 (1.029 ms)** | Stage 8.9.56 | `stage_8_9_56/scripts/benchmark_full_pipeline_latency.py (lines 177-184)` | In-memory PyTorch tensors (1, 1024), (1, 6), (1, 6) | model_b forward pass + sigmoid (`logit_b = model_b(...); prob_b = sigmoid(...)`) | P50 = 0.5982 ms, P90 = 0.8654 ms, P95 = 1.0291 ms, P99 = 1.8413 ms, Max = 3.8421 ms |
| **Subband Filterbank Synthesis P95 (47.793 ms)** | Stage 8.9.56 | `stage_8_9_56/scripts/benchmark_full_pipeline_latency.py (lines 159-164)` | 1.0s float32 audio buffer (16,000 samples @ 16 kHz) | extract_subband_vector() (6 Butterworth IIR filters + filtfilt + temporal variance loop) | P50 = 35.3341 ms, P90 = 42.1092 ms, P95 = 47.7934 ms, P99 = 62.4011 ms, Max = 78.9123 ms |
| **Phonation Feature Extraction P95 (7.193 ms)** | Stage 8.9.56 | `stage_8_9_56/scripts/benchmark_full_pipeline_latency.py (lines 151-156)` | 1.0s float32 audio buffer (16,000 samples @ 16 kHz) | extract_phonation_stats() (frame RMS window loop across 98 frames) | P50 = 4.6961 ms, P90 = 6.2104 ms, P95 = 7.1932 ms, P99 = 9.8451 ms, Max = 14.2103 ms |
| **Intervention D Filter P95 (3.554 ms)** | Stage 8.9.56 | `stage_8_9_56/scripts/benchmark_full_pipeline_latency.py (lines 187-192)` | 1.0s float32 audio buffer (16,000 samples @ 16 kHz), prob=0.85, pred=1 | apply_intervention_d() (spectral energy ratios + trill autocorrelation) | P50 = 2.3712 ms, P90 = 3.1023 ms, P95 = 3.5541 ms, P99 = 5.2104 ms, Max = 8.1203 ms |
| **Candidate E1 Complete End-to-End Pipeline P95 (56.802 ms)** | Stage 8.9.56 | `stage_8_9_56/scripts/benchmark_full_pipeline_latency.py (lines 203-221)` | 1.0s float32 audio buffer + in-memory YAMNet embedding tensor | Unified sequential loop: Normalization + Subband DSP + Phonation DSP + Tensor conversion + Model forward pass + Threshold application | P50 = 40.7821 ms, P90 = 49.3321 ms, P95 = 56.8023 ms, P99 = 71.4932 ms, Max = 86.3451 ms |

---

## 2. Root Cause of the 39.189 ms vs 56.802 ms Reporting Discrepancy

The forensic inspection reveals that **39.189 ms** and **56.802 ms** reflect fundamentally different timing boundaries and benchmark methodologies:

### 2.1 The Origin and Scope of 39.189 ms (Stage 8.9.55)
- **Script:** `stage_8_9_55/scripts/benchmark_latency.py` (lines 136-139).
- **Methodology:** Sliced array addition: `lat_pipeline_e = lat_fe[:200] + lat_e[:200]`.
- **Timing Scope:** Only included: (1) 11-d subband filterbank extraction (`lat_fe`, P95 = 38.863 ms), and (2) Candidate E1 model forward pass (`lat_e`, P95 = 0.421 ms).
- **Critical Omissions:** Omitted amplitude normalization, resampling checks, 6-d phonation acoustic statistics extraction (which takes ~7.2 ms), PyTorch tensor creation and device placement, sigmoid probability calculation, and threshold decision logic.
- **Execution Flaw:** Not an integrated sequential end-to-end loop; it decoupled feature extraction from inference and artificially summed the first 200 array elements.

### 2.2 The Origin and Scope of 56.802 ms (Stage 8.9.56)
- **Script:** `stage_8_9_56/scripts/benchmark_full_pipeline_latency.py` (lines 203-221, Component 9).
- **Methodology:** Integrated sequential loop measuring wall-clock time per iteration over 300 steady-state iterations.
- **Timing Scope:** Complete downstream inference: (1) Audio amplitude normalization, (2) 11-d Subband filterbank synthesis, (3) 6-d Phonation feature extraction, (4) Tensor conversion and batching, (5) Candidate E1 forward pass, and (6) Sigmoid threshold application.
- **Empirical Validation:** The observed P95 of 56.802 ms closely matches the sum of the independently profiled components: Subband (~47.8 ms) + Phonation (~7.2 ms) + Model (~0.58 ms) + Normalization (~0.05 ms) = ~55.6 ms.

### 2.3 The Origin of 39.694 ms for Candidate B (Stage 8.9.55 & Stage 8.9.56 Table B)
- **Script:** `stage_8_9_55/scripts/benchmark_latency.py` (line 196) and copy-pasted into `stage_8_9_56/acceptance_gate_reconciliation.md` Table B.
- **Methodology:** Literal scalar addition: `p95_b + p95_fe = 0.831 ms + 38.863 ms = 39.694 ms`.
- **Forensic Flaw 1 (Mathematical):** Summing P95 percentiles directly violates statistical percentile theory ($P_{95}(A + B) \le P_{95}(A) + P_{95}(B)$ is not generally an equality, and requires paired observation).
- **Forensic Flaw 2 (Architectural):** Candidate B does **NOT** use subband filterbank features. Candidate B only uses 1024-d YAMNet and 6-d phonation acoustic statistics. Attributing 38.863 ms of subband extraction to Candidate B was an erroneous architectural assumption in Stage 8.9.55.
- **Documentation Copy-Paste in Stage 8.9.56:** Table B in Stage 8.9.56 copy-pasted the 39.189 ms and 39.694 ms values from Stage 8.9.55 instead of populating Table B with the fresh Component 9 measurements from `latency_component_measurements.csv`.

---

## 3. Provenance Audit Conclusion
Both measurements have clear, verifiable provenance. 39.189 ms was a partial synthetic benchmark omitting phonation feature extraction. 56.802 ms represents the genuine, integrated complete downstream pipeline. In both cases, complete-pipeline latency exceeds the 25.0 ms target.
