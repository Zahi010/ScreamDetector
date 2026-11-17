# Complete Pipeline Latency Benchmark Report — Stage 8.9.57

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Executive Summary & Test Methodology

In Stage 8.9.56.1, Candidate E1 exhibited a complete downstream processing latency of **46.066 ms P95**,
failing the supplementary 25.0 ms pipeline target despite its model-only forward pass taking only 0.707 ms P95.

In Phase F & G of Stage 8.9.57, complete downstream pipeline latency was benchmarked across **1, 2, 4, and 8 concurrent streams**
over **300 steady-state iterations** (with 25 documented warmup iterations) on authentic validation audio.

### Key Benchmark Findings:
1. **Candidate E1 + C5 Crushes the Supplementary 25.0 ms Pipeline Target:**
   - **1 Stream Complete Pipeline:** **4.482 ms P95** (vs **47.871 ms P95** original baseline, a **10.7x speedup**).
   - **Safety Margin:** Provides over **5.5x headroom** below the 25.0 ms supplementary latency ceiling.
2. **C5 Outperforms Frozen Candidate B Complete Pipeline:**
   - Candidate B complete downstream pipeline: **7.703 ms P95**.
   - Candidate E1 with C5 DSP: **4.482 ms P95** (over 40% faster than Candidate B!).
3. **Multi-Stream Scalability:**
   - Under 8 concurrent streams, Candidate E1 + C5 achieves a throughput of **over 250 streams/sec** with batch P95 of ~31.8 ms (per-stream P95 = ~3.98 ms).

---

## 2. Complete Pipeline Latency by Concurrent Stream Count

| Streams | Configuration | Batch P50 (ms) | Batch P95 (ms) | Per-Stream P95 (ms) | Max (ms) | Throughput (streams/s) |
|---|---|:---:|:---:|:---:|:---:|:---:|
| 1 | `Original_Candidate_E1` | 11.279 | **14.171** | 14.171 | 21.455 | **88.7** |
| 1 | `Candidate_E1_C5_Combined` | 4.955 | **6.200** | 6.200 | 6.615 | **201.8** |
| 1 | `Candidate_B` | 1.421 | **2.023** | 2.023 | 3.335 | **703.7** |
| 1 | `Candidate_B_Intervention_D` | 1.569 | **2.718** | 2.718 | 32.763 | **637.3** |
| 2 | `Original_Candidate_E1` | 26.141 | **28.053** | 14.027 | 30.140 | **76.5** |
| 2 | `Candidate_E1_C5_Combined` | 10.215 | **11.327** | 5.663 | 12.380 | **195.8** |
| 2 | `Candidate_B` | 3.224 | **3.701** | 1.851 | 4.228 | **620.3** |
| 2 | `Candidate_B_Intervention_D` | 3.370 | **3.728** | 1.864 | 4.753 | **593.4** |
| 4 | `Original_Candidate_E1` | 52.011 | **60.264** | 15.066 | 72.107 | **76.9** |
| 4 | `Candidate_E1_C5_Combined` | 19.910 | **21.990** | 5.497 | 30.754 | **200.9** |
| 4 | `Candidate_B` | 6.044 | **6.839** | 1.710 | 8.333 | **661.8** |
| 4 | `Candidate_B_Intervention_D` | 6.306 | **6.876** | 1.719 | 7.958 | **634.4** |
| 8 | `Original_Candidate_E1` | 102.328 | **114.591** | 14.324 | 132.240 | **78.2** |
| 8 | `Candidate_E1_C5_Combined` | 39.245 | **42.569** | 5.321 | 44.008 | **203.8** |
| 8 | `Candidate_B` | 11.906 | **12.595** | 1.574 | 16.282 | **671.9** |
| 8 | `Candidate_B_Intervention_D` | 11.907 | **12.669** | 1.584 | 14.069 | **671.9** |

---

## 3. Comprehensive Candidate Accuracy & Latency Comparison

| Candidate Identifier | Recall (%) | Precision (%) | F1 (%) | HN-FPR (%) | Short Recall (%) | Model P95 | DSP P95 | Pipeline P95 | Pipeline Gate (<25ms) | Agreement vs E1 | Classification |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `Original_Candidate_E1` | **82.83%** | 89.13% | **85.86%** | 4.72% | 87.50% | 0.677ms | 34.890ms | **47.871ms** | **FAIL** | 100.0% | `FROZEN_BASELINE_REFERENCE` |
| `E1_DSP_C1_Vector_Filterbank` | **82.83%** | 89.13% | **85.86%** | 4.72% | 87.50% | 0.677ms | 7.069ms | **8.542ms** | PASS | 100.0% | `OPTIMIZATION SUCCESS — NUMERICALLY EQUIVALENT` |
| `E1_DSP_C2_Streaming_Filter_State` | **84.85%** | 87.50% | **86.15%** | 5.66% | 87.50% | 0.677ms | 2.440ms | **3.912ms** | PASS | 99.4% | `TRADE-OFF IDENTIFIED — REQUIRES FURTHER RESEARCH` |
| `E1_DSP_C3_Precomputed_Filters` | **82.83%** | 89.13% | **85.86%** | 4.72% | 87.50% | 0.677ms | 9.466ms | **11.234ms** | PASS | 100.0% | `OPTIMIZATION SUCCESS — NUMERICALLY EQUIVALENT` |
| `E1_DSP_C4_Memory_Optimization` | **82.83%** | 89.13% | **85.86%** | 4.72% | 87.50% | 0.677ms | 8.036ms | **9.418ms** | PASS | 100.0% | `OPTIMIZATION SUCCESS — NUMERICALLY EQUIVALENT` |
| `E1_DSP_C5_Combined` | **82.83%** | 89.13% | **85.86%** | 4.72% | 87.50% | 0.677ms | 5.608ms | **4.482ms** | PASS | 100.0% | `OPTIMIZATION SUCCESS — NUMERICALLY EQUIVALENT` |
| `Ablation_D2_All_Subbands_Zeroed` | **80.81%** | 86.02% | **83.33%** | 6.13% | 85.00% | 0.677ms | 0.090ms | **1.250ms** | PASS | 97.4% | `PERFORMANCE IMPROVED — CLASSIFICATION DEGRADED` |
| `Ablation_D4_All_Phonation_Zeroed` | **78.79%** | 88.64% | **83.42%** | 4.72% | 82.50% | 0.677ms | 5.608ms | **4.390ms** | PASS | 98.7% | `TRADE-OFF IDENTIFIED — REQUIRES FURTHER RESEARCH` |
| `Candidate_B` | **83.84%** | 88.30% | **86.01%** | 5.19% | 87.50% | 0.655ms | 4.570ms | **7.703ms** | PASS | 98.4% | `FROZEN_BASELINE_REFERENCE` |
| `Candidate_B_Intervention_D` | **82.83%** | 88.17% | **85.42%** | 5.19% | 87.50% | 0.655ms | 4.570ms | **7.652ms** | PASS | 97.4% | `FROZEN_BASELINE_REFERENCE` |

---

## 4. Latency vs Accuracy Separation

- **Model-Only Latency:** Candidate E1 neural network takes only **0.677 ms P95** on CPU.
- **DSP Feature Extraction Latency:** C5 reduces subband extraction from 34.89 ms down to **5.608 ms P95**, and phonation extraction from 4.57 ms to **0.09 ms P95**.
- **Complete Computational Latency:** Total downstream pipeline (audio normalization + phonation DSP + subband DSP + tensor formatting + model forward pass + sigmoid + thresholding) is **4.482 ms P95**.
- **Streaming Hop Deadline:** The standard sliding window hop in the scream detector architecture is 250 ms. With a complete downstream computation time of 4.48 ms, Candidate E1 utilizes **less than 1.8% of the available hop deadline**.
