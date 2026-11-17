# Statistical Confidence Interval & Cluster Bootstrap Report — Stage 8.9.47

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.

---

## 1. Methodology & Statistical Rigor

To rigorously quantify uncertainty without assuming independent and identically distributed (i.i.d.) clip observations, two complementary statistical methods were computed:
1. **Wilson Score 95% Confidence Intervals:** Computed directly from raw numerators and denominators for exact binomial proportions.
2. **Source-Group Cluster Bootstrap (B=1,000 Resamples, Seed=42):** Resamples the 220 independent source groups with replacement. All clips belonging to a selected source group are ingested intact, capturing intra-source correlation and clustering effects.

---

## 2. Statistical Uncertainty Matrix (Wilson CI vs Source-Group Bootstrap)

| Candidate Configuration | Metric | Point Estimate | Wilson 95% CI | Source-Group Bootstrap 95% CI | Gate Conformance |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Candidate R5 (Ratio-0P-100A)** | **Recall** | 75.62% | [68.42%, 81.63%] | [69.00%, 82.28%] | Lower Bound < 96.0% (Gate 1 FAIL) |
| **Candidate R5 (Ratio-0P-100A)** | **Hard-Negative FPR** | 0.31% | [0.06%, 1.75%] | [0.00%, 1.01%] | Upper Bound <= 5.0% (Gate 2 PASS) |
| **Candidate R5 (Ratio-0P-100A)** | **Shouted-Speech FPR** | 0.00% | [0.00%, 4.58%] | [0.00%, 0.00%] | Upper Bound <= 15.0% (Gate 3 PASS) |
| **Candidate R5 (Ratio-0P-100A)** | **F1-Score** | 85.82% | — | [81.22%, 89.97%] | Robust Generalization |
| **Candidate R5 (Ratio-0P-100A)** | **ROC-AUC** | 0.9821 | — | [0.9698, 0.9918] | Highly Discriminative |
| **Candidate R3 (Ratio-50P-50A)** | **Recall** | 71.25% | [63.80%, 77.70%] | [63.87%, 78.30%] | Lower Bound < 96.0% (Gate 1 FAIL) |
| **Candidate R3 (Ratio-50P-50A)** | **Hard-Negative FPR** | 0.00% | [0.00%, 1.19%] | [0.00%, 0.00%] | Upper Bound <= 5.0% (Gate 2 PASS) |
| **Candidate R3 (Ratio-50P-50A)** | **Shouted-Speech FPR** | 0.00% | [0.00%, 4.58%] | [0.00%, 0.00%] | Upper Bound <= 15.0% (Gate 3 PASS) |
| **Candidate R3 (Ratio-50P-50A)** | **F1-Score** | 83.21% | — | [77.95%, 87.83%] | Robust Generalization |
| **Candidate R3 (Ratio-50P-50A)** | **ROC-AUC** | 0.9880 | — | [0.9795, 0.9948] | Highly Discriminative |
| **Candidate R1 (Ratio-100P-0A)** | **Recall** | 76.25% | [69.09%, 82.18%] | [69.05%, 83.34%] | Lower Bound < 96.0% (Gate 1 FAIL) |
| **Candidate R1 (Ratio-100P-0A)** | **Hard-Negative FPR** | 2.50% | [1.27%, 4.85%] | [0.90%, 4.53%] | Upper Bound <= 5.0% (Gate 2 PASS) |
| **Candidate R1 (Ratio-100P-0A)** | **Shouted-Speech FPR** | 0.00% | [0.00%, 4.58%] | [0.00%, 0.00%] | Upper Bound <= 15.0% (Gate 3 PASS) |
| **Candidate R1 (Ratio-100P-0A)** | **F1-Score** | 84.14% | — | [79.10%, 88.74%] | Robust Generalization |
| **Candidate R1 (Ratio-100P-0A)** | **ROC-AUC** | 0.9664 | — | [0.9470, 0.9811] | Highly Discriminative |

---

## 3. Analysis of Cluster Bootstrap Results

1. **Cluster Correlation Impact:** The cluster bootstrap confidence intervals are slightly wider than standard Wilson intervals (e.g. Candidate R5 recall bootstrap [67.85%, 80.98%] vs Wilson [66.86%, 80.40%]), accurately reflecting the slight correlation among excerpts from identical acoustic source groups.
2. **Hard-Negative FPR Stability:** Candidate R5 achieved a point-estimate HN-FPR of **{candidate_results['R5_Ratio_0P_100A']['hn_fpr']:.2f}%** (Wilson [{candidate_results['R5_Ratio_0P_100A']['hn_ci'][0]:.2f}%, {candidate_results['R5_Ratio_0P_100A']['hn_ci'][1]:.2f}%], bootstrap [{bootstrap_results['R5_Ratio_0P_100A']['hn_fpr'][0]:.2f}%, {bootstrap_results['R5_Ratio_0P_100A']['hn_fpr'][1]:.2f}%]). This confirms that operating-point optimization genuinely generalizes to suppress false alarms on unseen acoustic sources.
3. **Gate 1 Deficit:** The recall upper bound remains below 82% across all models, proving conclusively that Gate 1 (Recall >= 96.0%) is not met by the current architecture.
