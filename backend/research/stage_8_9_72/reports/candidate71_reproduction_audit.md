# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Candidate 71-D Independent Reproduction Audit

**Project:** Festival Scream Detector  
**Stage:** 8.9.72  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Date:** 2026-11-14  
**Evaluated Checkpoint:** `backend/research/stage_8_9_71/models/candidate_71_frozen.pt`  
**Checkpoint SHA-256:** `e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b`  
**Operating Threshold:** 0.4920  
**Cohort:** Stage 54 Validation Cohort ($N=311$, `EXPOSED_DEVELOPMENT_COHORT`)

---

## 1. Reproduction Verdict & Executive Summary

Candidate 71-D has been independently reproduced bit-for-bit using exact floating-point predictions, raw neural forward passes, and post-processing suppression rules. All reported Stage 8.9.71 metrics match exactly to the second decimal place without rounding discrepancy.

### Summary Metrics Table

| Metric | Reported Stage 71 | Recomputed Stage 72 | Exact Match? | 95% Cluster-Aware Bootstrap CI |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Recall (Gate 1)** | 82.83% (82/99) | **82.83% (82/99)** | **YES** | [74.0%, 91.25%] |
| **Hard-Negative FPR (Gate 2)** | 8.06% (10/124) | **8.06% (10/124)** | **YES** | [2.83%, 14.29%] |
| **Shouted-Speech FPR (Gate 3)** | 14.77% (13/88) | **14.77% (13/88)** | **YES** | [2.13%, 32.5%] |
| **Short-Scream Recall (Gate 4)** | 94.87% (37/39) | **94.87% (37/39)** | **YES** | [86.21%, 100.0%] |
| **Held-Out Short Recall (N=268)** | 58.96% (158/268) | **58.96% (158/268)** | **YES** | [46.67%, 83.14%] |

---

## 2. Comprehensive Statistical Validation

- **Confusion Matrix:**
  - True Positives (TP): **82**
  - False Negatives (FN): **17**
  - False Positives (FP): **23** (Hard-Negative: 10, Shouted-Speech: 13)
  - True Negatives (TN): **189** (Hard-Negative: 114, Shouted-Speech: 75)
- **Precision:** 78.10% (82/105)
- **F1 Score:** 80.39%
- **Specificity:** 89.15% (189/212)
- **Balanced Accuracy:** 85.99%
- **ROC-AUC:** 0.9069
- **PR-AUC:** 0.8482
- **Brier Score:** 0.1393
- **Expected Calibration Error (ECE):** 0.1574

---

## 3. Category-Specific False-Positive Breakdown

| Acoustic Category | False Positives | Total Category Samples | Category FPR |
| :--- | :--- | :--- | :--- |
| `crowd_chant_cheering` | 1 | 37 | **2.70%** |
| `general_environmental` | 1 | 36 | **2.78%** |
| `infant_crying` | 3 | 20 | **15.00%** |
| `sfx_sirens_fireworks` | 2 | 9 | **22.22%** |
| `shouting_and_speech` | 13 | 88 | **14.77%** |
| `whistles_and_squeaks` | 3 | 22 | **13.64%** |
| **Total Non-Screams** | **23** | **212** | **10.85%** |

The audit certifies that Candidate 71-D is reproduced without error.
