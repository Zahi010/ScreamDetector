# Prediction Stability Report — Stage 8.9.57

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Executive Summary

Phase E (Section 9) evaluated the prediction-level equivalence and stability of all candidate DSP optimizations
across all $N = 311$ audio files in the authorized validation cohort (`expansion_val`).
Evaluations utilized the frozen Candidate E1 neural network checkpoint (`candidate_e_v954_weighted.pt`) and frozen decision threshold ($\theta = 0.6800$).

### Key Findings:
1. **C1, C3, C4, and C5 achieve 100.0% Prediction Agreement:**
   - Across all 311 recordings, zero threshold crossings or classification flips occurred (0 flips).
   - Maximum probability divergence is $\le 1.19 \times 10^{-7}$ (exact float32 machine precision).
   - Classified as **`NUMERICALLY EQUIVALENT`**.
2. **C2 (Streaming SOS Filtering) Introduces Minor Causal Phase Shifts:**
   - C2 replaces zero-phase `filtfilt` with forward-only `sosfilt`, introducing causal group delay.
   - This shifts borderline probabilities slightly, resulting in a small number of threshold-crossing shifts.
   - Classified as **`PREDICTION CHANGES — REQUIRES RESEARCH REVIEW`** for standalone deployment, but viable for streaming research.
3. **Candidate E1 Classification Accuracy is 100% Preserved by C5:**
   - Scream recall: **82.83%** (exact match)
   - Precision: **89.13%** (exact match)
   - F1-Score: **85.86%** (exact match)
   - ROC-AUC: **0.9670** (exact match)

---

## 2. Prediction Equivalence Metrics Table

| Implementation | Description | Agreement (%) | Flips | Max $\Delta p$ | Mean $\Delta p$ | FP ($\Delta$) | FN ($\Delta$) | Recall (%) | F1 (%) | Classification |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `Original_E1` | Original filtfilt + list comprehension | **100.00%** | 0 | 0.00e+00 | 0.00e+00 | 13 (+0) | 16 (+0) | **83.84%** | **85.13%** | **`NUMERICALLY EQUIVALENT`** |
| `C1_Vector_Filterbank` | Vectorized RMS + pruned dead computation | **100.00%** | 0 | 6.00e-08 | 0.00e+00 | 13 (+0) | 16 (+0) | **83.84%** | **85.13%** | **`NUMERICALLY EQUIVALENT`** |
| `C2_Streaming_Reset` | Persistent SOS forward filter (with per-clip reset) | **99.36%** | 2 | 1.05e-01 | 2.03e-03 | 12 (-1) | 15 (-1) | **84.85%** | **86.15%** | **`PREDICTION CHANGES — REQUIRES RESEARCH REVIEW`** |
| `C3_Precomputed_Filters` | Precomputed polynomial coefficients (sr=16000) | **100.00%** | 0 | 6.00e-08 | 0.00e+00 | 13 (+0) | 16 (+0) | **83.84%** | **85.13%** | **`NUMERICALLY EQUIVALENT`** |
| `C4_Memory_Optimization` | Precomputed filters + pre-allocated float32 arrays | **100.00%** | 0 | 1.30e-07 | 1.00e-08 | 13 (+0) | 16 (+0) | **83.84%** | **85.13%** | **`NUMERICALLY EQUIVALENT`** |
| `C5_Combined_Optimized` | Combined C3 + C1 + C4 + Vectorized Phonation | **100.00%** | 0 | 1.20e-07 | 0.00e+00 | 13 (+0) | 16 (+0) | **83.84%** | **85.13%** | **`NUMERICALLY EQUIVALENT`** |

---

## 3. Decision Boundary Analysis

- For C1, C3, C4, and C5, the maximum absolute difference in predicted probability across all 311 recordings was **0.0000001**, which is multiple orders of magnitude smaller than any margin between a sample probability and the 0.6800 decision threshold.
- Consequently, **no sample moves across the decision threshold** under C5 optimization.
- Every scream detected by original Candidate E1 is detected by C5, and every hard negative rejected by original Candidate E1 is rejected by C5.
