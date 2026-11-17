# Prediction Stability Audit Report — Stage 8.9.58

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Executive Summary

Phase C evaluated the prediction stability of `E1_DSP_C5_COMBINED` against the original Candidate E1 baseline across all
$N = 311$ audio files in the authorized validation cohort (`expansion_val`).
Inferences were performed using the frozen Candidate E1 neural network checkpoint (`candidate_e_v954_weighted.pt`) and frozen threshold $\theta = 0.6800$.

### Key Audit Findings:
1. **Zero Classification Flips Across Entire Cohort:** Across all 311 validation recordings, **zero classification flips** occurred (100.0% binary decision agreement).
2. **Negligible Probability Divergence:** The maximum probability difference across the entire cohort is **1.49e-07**, and the mean probability difference is **4.52e-09** (median = **0.00e+00**).
3. **Zero Margin Risk:** The closest sample probability to the 0.6800 threshold is $\approx 0.6432$ ($>0.036$ away from the boundary), meaning a divergence of $\sim 10^{-7}$ cannot cause any threshold-crossing changes.
4. **Exact Metric Preservation:** All primary classification metrics match to 2 decimal places.

---

## 2. Classification Metrics Comparison Table

| Metric | Original Candidate E1 | Candidate E1 + C5 Combined | Metric Delta (C5 - Orig) | Agreement Status |
|---|:---:|:---:|:---:|:---:|
| **Prediction Agreement (%)** | 100.00% | **100.00%** | 0.00% | **EXACT (311/311)** |
| **Threshold-Crossing Flips** | 0 | **0** | 0 | **ZERO FLIPS** |
| **Overall Scream Recall (%)** | 83.84% | **83.84%** | 0.00% | **IDENTICAL** |
| **Precision (%)** | 86.46% | **86.46%** | 0.00% | **IDENTICAL** |
| **F1-Score (%)** | 85.13% | **85.13%** | 0.00% | **IDENTICAL** |
| **ROC-AUC** | 0.966171 | **0.966171** | 0.000000 | **IDENTICAL** |
| **Hard-Negative FPR (%)** | 6.13% | **6.13%** | 0.00% | **IDENTICAL** |
| **Shouted-Speech FPR (%)** | 11.36% | **11.36%** | 0.00% | **IDENTICAL** |
| **Short-Scream Recall (%)** | 94.87% | **94.87%** | 0.00% | **IDENTICAL** |

---

## 3. Probability Difference Statistics

| Statistic | Value |
|---|:---:|
| Maximum Absolute Difference ($\max \|p_{C5} - p_{orig}\|$) | **1.49011612e-07** |
| Mean Absolute Difference ($\text{MAE}$) | **4.52344647e-09** |
| Median Absolute Difference | **0.00000000e+00** |
| Root Mean Squared Error ($\text{RMSE}$) | **2.03955527e-08** |
| Minimum Absolute Difference | **0.00000000e+00** |

---

## 4. Conclusion

Candidate E1 with C5 DSP optimization exhibits complete decision stability and prediction equivalence across all validation recordings.
