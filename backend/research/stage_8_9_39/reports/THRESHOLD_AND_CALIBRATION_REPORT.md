# Stage 8.9.39 — Validation Threshold Optimization & Probability Calibration Report

**Project:** Festival Scream Detector  
**Stage:** 8.9.39 — Controlled Retraining, Expanded Dataset Evaluation & Independent Generalization Audit  
**Author:** Principal Acoustic AI Research Scientist & ML Validation Auditor  
**Date:** November 2026  
**Status:** Completed  
**Mandatory Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  

---

## 1. Protocol Constraints & Leakage Protection

Per Sections 9 and 10 of the Stage 8.9.39 Retraining Protocol:
1. **Validation-Only Sweep:** Threshold sweeps and operating point determinations were conducted strictly on the validation partition (`v4_val`, $N=339$: 83 screams, 256 non-screams).
2. **Zero Test Exposure:** Neither `v4_historical_test` ($N=293$) nor `v4_reserved_expansion_test` ($N=102$) was accessed during threshold selection or probability calibration fitting.
3. **Threshold Freeze:** All candidate decision thresholds and calibration parameters were completely finalized and committed to `backend/research/stage_8_9_39/config/threshold_config.json` before any test inference.

---

## 2. Validation Threshold Sweeps & Operating Frontiers

Grid sweeps spanned $\theta \in [0.05, 0.95]$ in discrete steps of $0.01$.

### 2.1 Configuration B Operating Points:
- **Primary Threshold ($\theta = 0.24$):**
  - Validation Confusion Matrix: $\text{TP}=72, \text{FP}=30, \text{TN}=226, \text{FN}=11$.
  - Precision: 70.59%, Recall: 86.75%, F1 Score: 0.7784.
  - Specificity: 88.28%, Hard-Negative FPR: 11.72%.
  - Shouted-Speech FPR: 11.24% (10 false positives out of 89 shouted clips).
  - Short-Scream Recall: 100.0% (10 true positives out of 10 short-scream clips in validation).
  - Balanced Accuracy: 87.51%, Distance to Ideal $(1, 0)$: 0.1769.

### 2.2 Configuration D Operating Points:
- **Primary Threshold ($\theta = 0.34$):**
  - Validation Confusion Matrix: $\text{TP}=68, \text{FP}=25, \text{TN}=231, \text{FN}=15$.
  - Precision: 73.12%, Recall: 81.93%, F1 Score: 0.7727.
  - Specificity: 90.23%, Hard-Negative FPR: 9.77%.
  - Shouted-Speech FPR: 7.87% (7 false positives out of 89 shouted clips).
  - Short-Scream Recall: 100.0% (10 true positives out of 10 short-scream clips in validation).
  - Balanced Accuracy: 86.08%, Distance to Ideal $(1, 0)$: 0.2054.
- **Balanced Operational Threshold ($\theta = 0.32$):**
  - $\text{TP}=69, \text{FP}=27, \text{TN}=229, \text{FN}=14$.
  - Precision: 71.88%, Recall: 83.13%, F1: 0.7709, Specificity: 89.45%, $\text{HN-FPR} = 10.55\%$, $\text{Shout-FPR} = 7.87\%$.

---

## 3. Probability Calibration via Platt Scaling

Platt scaling was fitted via unidimensional logistic regression on validation logits $\sigma^{-1}(\hat{y})$ to evaluate empirical reliability and confidence calibration.

### 3.1 Candidate B Calibration Results:
- **Fitted Parameters:** $\text{coef\_A} = 1.3384$, $\text{intercept\_B} = 0.5160$.
- **Brier Score:** Improved from **0.0958** (uncalibrated) to **0.0909** (Platt calibrated), $\Delta = -0.0049$.
- **Expected Calibration Error (ECE):** Improved from **0.0553** (uncalibrated) to **0.0413** (Platt calibrated), $\Delta = -0.0140$.
- **Discrimination (ROC-AUC / PR-AUC):** Exactly 0.9182 / 0.7980 (strictly preserved due to monotonic transformation).
- **At Reference Threshold 0.35:**
  - Uncalibrated: Recall 77.11%, Precision 75.29%, FPR 8.20%.
  - Platt Calibrated: Recall 79.52%, Precision 72.53%, FPR 9.77%.

### 3.2 Candidate D Calibration Results:
- **Fitted Parameters:** $\text{coef\_A} = 1.7295$, $\text{intercept\_B} = 0.5173$.
- **Brier Score:** Improved from **0.1111** (uncalibrated) to **0.0990** (Platt calibrated), $\Delta = -0.0121$.
- **Expected Calibration Error (ECE):** Improved from **0.1071** (uncalibrated) to **0.0570** (Platt calibrated), $\Delta = -0.0502$.
- **Discrimination (ROC-AUC / PR-AUC):** Exactly 0.8861 / 0.7685 (strictly preserved).
- **At Reference Threshold 0.35:**
  - Uncalibrated: Recall 81.93%, Precision 73.12%, FPR 9.77%.
  - Platt Calibrated: Recall 81.93%, Precision 73.12%, FPR 9.77%.

---

## 4. Reliability Diagram Analysis

Validation binning ($K=10$ uniform intervals $\in [0.0, 1.0]$) revealed:
1. **Uncalibrated Miscalibration:** Both raw neural network outputs exhibited moderate overconfidence in the mid-probability range ($0.30\text{--}0.50$), where true positive frequencies were higher than predicted confidences.
2. **Platt Rectification:** Platt scaling effectively shifted mid-range logits toward empirical base rates, lowering ECE by 25.3% for Configuration B and by 46.9% for Configuration D.
3. **Operational Policy:** While Platt scaling significantly enhances the interpretability of risk scores for human analysts, threshold-based binary decision gates on frozen test cohorts are governed by rank order. Raw uncalibrated decision thresholds ($\theta_B = 0.24, \theta_D = 0.34$) were maintained as the primary operational criteria to avoid compounding small-sample calibration variance.

---

## 5. Summary of Frozen Configuration Settings

| Setting | Configuration B | Configuration D | Source Cohort |
|---|---|---|---|
| Optimal F1 Threshold | `0.2400` | `0.3400` | `v4_val` only |
| Balanced Operational Threshold | `0.2400` | `0.3200` | `v4_val` only |
| Platt Parameter $A$ | `1.3384` | `1.7295` | `v4_val` only |
| Platt Parameter $B$ | `0.5160` | `0.5173` | `v4_val` only |
| Test Cohort Exposure | **Zero (Strictly Isolated)** | **Zero (Strictly Isolated)** | — |
