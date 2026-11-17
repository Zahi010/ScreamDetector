# Candidate E Independent Evaluation Report — Stage 8.9.53

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.  
> No live-fire experiments, autonomous emergency dispatch, external emergency alerts, or claims of life-safety efficacy.  
> No production promotion is authorized.

---

## 1. Executive Summary

Candidate E (`research_exp_candidate.pt`, SHA-256: `5ec59414...`) was evaluated in a fully frozen, independent evaluation on the previously quarantined **`expansion_reserved_test`** cohort ($N=366$ recordings across 140 independent source groups) at its validation-selected threshold $\theta = 0.4000$.

Zero retraining, hyperparameter adaptation, or threshold re-tuning occurred.

### Headline Evaluation Results
- **Independent Scream Recall:** **62.75%** (64 / 102) [Wilson 95% CI: 53.06%, 71.51%]
- **Independent Hard-Negative FPR:** **16.29%** (43 / 264) [Wilson 95% CI: 12.32%, 21.22%]
- **Independent Precision:** **59.81%** (64 / 107) [Wilson 95% CI: 50.34%, 68.61%]
- **F1 Score:** **61.24%**
- **Specificity:** **83.71%** (221 / 264)
- **Overall Accuracy:** **77.87%** (285 / 366)
- **ROC-AUC:** **0.8128** | **PR-AUC:** **0.6609**
- **Brier Score:** **0.1704** | **Expected Calibration Error (ECE):** **0.1474**

---

## 2. Confusion Matrix

| Ground Truth \ Prediction | Predicted Negative (0) | Predicted Positive (1) | Total |
|---|---|---|---|
| **Authentic Scream (1)** | **38 (FN)** | **64 (TP)** | 102 |
| **Hard Negative (0)** | **221 (TN)** | **43 (FP)** | 264 |
| **Total** | 259 | 107 | 366 |

---

## 3. Subgroup Breakdown Metrics

Subtype labels are non-mutually exclusive tags reflecting complex real-world acoustic conditions.

| Acoustic Subgroup | Class | Hits / Total | Rate (%) | Wilson 95% CI | Unique SGs | Evidence Status |
|---|---|---|---|---|---|---|
| **All Authentic Screams** | Positive | 64 / 102 | 62.75% | [53.06%, 71.51%] | 41 | NO |
| **Short Screams (<1.0s)** | Positive | 19 / 22 | 86.36% | [66.67%, 95.25%] | 13 | NO |
| **Ultra-Short Screams (<0.5s)** | Positive | 7 / 8 | 87.50% | [52.91%, 97.76%] | 7 | YES |
| **Standard-Short Screams (0.5-1.0s)** | Positive | 12 / 14 | 85.71% | [60.06%, 95.99%] | 11 | NO |
| **Low-Intensity / Muffled Screams** | Positive | 3 / 3 | 100.00% | [43.85%, 100.00%] | 2 | YES |
| **Crowd-Masked Screams** | Positive | 21 / 29 | 72.41% | [54.28%, 85.30%] | 16 | NO |
| **Sustained Screams (>=1.0s)** | Positive | 45 / 80 | 56.25% | [45.34%, 66.59%] | 30 | NO |
| **All Hard Negatives** | Negative | 43 / 264 | 16.29% | [12.32%, 21.22%] | 104 | NO |
| **Shouted Speech** | Negative | 9 / 111 | 8.11% | [4.32%, 14.69%] | 34 | NO |
| **Crowd Cheering / Chanting** | Negative | 17 / 55 | 30.91% | [20.28%, 44.03%] | 30 | NO |
| **Whistles and Squeaks** | Negative | 9 / 32 | 28.12% | [15.56%, 45.37%] | 18 | NO |
| **Other Vocalizations / Environmental** | Negative | 7 / 40 | 17.50% | [8.75%, 31.95%] | 23 | NO |

---

## 4. Source-Group Cluster Bootstrap Estimates (1,000 Resamples)

To rigorously account for intra-session clustering and uploader dependence, source-group cluster bootstrapping was executed across 1,000 resamples:

- **Cluster Bootstrap Scream Recall:** Mean = 63.30% [95% Percentile CI: 51.64%, 74.67%]
- **Cluster Bootstrap Hard-Negative FPR:** Mean = 16.53% [95% Percentile CI: 10.82%, 23.19%]
- **Cluster Bootstrap F1 Score:** Mean = 61.29% [95% Percentile CI: 50.59%, 71.13%]

---

## 5. Candidate E Acceptance Gate Evaluation

| Gate | Requirement | Candidate E Result | Point Estimate | Wilson 95% CI | Gate Status |
|---|---|---|---|---|---|
| **1. Overall Scream Recall** | $\ge 96.0\%$ | 64 / 102 | **62.75%** | [53.06%, 71.51%] | **FAIL** |
| **2. Hard-Negative FPR** | $\le 5.0\%$ | 43 / 264 | **16.29%** | [12.32%, 21.22%] | **FAIL** |
| **3. Shouted-Speech FPR** | $\le 15.0\%$ | 9 / 111 | **8.11%** | [4.32%, 14.69%] | **PASS** |
| **4. Short-Scream Recall** | $\ge 90.0\%$ | 19 / 22 | **86.36%** | [66.67%, 95.25%] | **FAIL** |
| **5. Computational Latency** | P95 $\le 25$ ms | Model P95 | **< 1.0 ms** | Dedicated Audit | **PASS** |
