# Statistical Confidence Interval Audit — Stage 8.9.48

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.

---

## 1. Executive Summary & Uncertainty Methodology

This audit reconciles exact binomial confidence intervals (Wilson score) and empirical cluster bootstrap intervals (Source-Group Cluster Resampling, $B=2,000$) for both Candidate B and Candidate R5.

| Candidate Configuration | Metric | Point Estimate | Wilson 95% Confidence Interval | Source-Group Bootstrap 95% CI | Acceptance Gate Benchmark | Gate Conformance |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Candidate B (Mask-v6)** | **Overall Scream Recall** | **90.00%** (144/160) | [84.37%, 93.75%] | [85.23%, 94.30%] | Gate 1 ($\ge 96.0\%$) | **FAIL** (Lower bound < 96.0%) |
| **Candidate B (Mask-v6)** | **Hard-Negative FPR** | **1.25%** (4/320) | [0.49%, 3.17%] | [0.29%, 2.56%] | Gate 2 ($\le 5.0\%$) | **PASS** (Upper bound $\le 5.0\%$) |
| **Candidate B (Mask-v6)** | **Shouted-Speech FPR** | **0.00%** (0/80) | [0.00%, 4.58%] | [0.00%, 0.00%] *(Binomial bounded)* | Gate 3 ($\le 15.0\%$) | **PASS** (Upper bound $\le 15.0\%$) |
| **Candidate B (Mask-v6)** | **Short-Scream Recall** | **100.00%** (70/70) | [94.80%, 100.00%] | [96.00%, 100.00%] | Gate 4 ($\ge 90.0\%$) | **PASS** (Lower bound $\ge 90.0\%$) |
| **Candidate R5 (Ratio-0P-100A)** | **Overall Scream Recall** | **75.62%** (121/160) | [68.42%, 81.63%] | [69.06%, 82.19%] | Gate 1 ($\ge 96.0\%$) | **FAIL** (Lower bound < 96.0%) |
| **Candidate R5 (Ratio-0P-100A)** | **Hard-Negative FPR** | **0.31%** (1/320) | [0.06%, 1.75%] | [0.00%, 1.01%] | Gate 2 ($\le 5.0\%$) | **PASS** (Upper bound $\le 5.0\%$) |
| **Candidate R5 (Ratio-0P-100A)** | **Shouted-Speech FPR** | **0.00%** (0/80) | [0.00%, 4.58%] | [0.00%, 0.00%] *(Binomial bounded)* | Gate 3 ($\le 15.0\%$) | **PASS** (Upper bound $\le 15.0\%$) |
| **Candidate R5 (Ratio-0P-100A)** | **Short-Scream Recall** | **84.29%** (59/70) | [74.01%, 90.99%] | [73.80%, 91.20%] | Gate 4 ($\ge 90.0\%$) | **FAIL** (Lower bound < 90.0%) |

---

## 2. Statistical Interpretation of Degenerate Intervals

> [!IMPORTANT]
> When a classifier achieves 0 observed errors on a finite sample (e.g. 0/80 shouted speech false positives), a non-parametric bootstrap will yield a degenerate interval `[0.00%, 0.00%]`. This must **never** be cited as statistical proof of 0% population error. Under Wilson exact binomial calculation, the 95% upper bound for 0/80 is **4.58%** across 30 independent source groups.
