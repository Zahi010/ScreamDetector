# Candidate B Baseline Reproduction Report — Stage 8.9.50

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.

---

## 1. Executive Summary

Candidate B (`Config-B-Mask-v6`, `config_b_mask.pt`, $\theta=0.8000$) baseline inference was independently re-executed across the Stage 8.9.49 independent evaluation cohort ($N=480$).

### Reproduction Verification Results:
- **Binary Decision Agreement:** **480 / 480** (**100.0% Exact Agreement**).
- **Maximum Absolute Probability Difference:** **0.000000** ($\le 0.0001$).
- **Mean Absolute Probability Difference:** **0.000000**.
- **Prediction Discrepancies:** **0** discordant predictions.

---

## 2. Reproduced Confusion Matrix (Cohort N = 480)

| Class | Predicted Negative (0) | Predicted Positive (1) | Total Ground Truth | Category Metric |
| :--- | :---: | :---: | :---: | :---: |
| **Actual Negatives (0)** | **319** (TN) | **1** (FP) | 320 | Hard-Negative FPR: **0.31%** |
| **Actual Screams (1)** | **29** (FN) | **131** (TP) | 160 | Scream Recall: **81.88%** |

- **Precision:** **99.24%** (131/132)
- **Specificity:** **99.69%** (319/320)
- **Macro F1 Score:** **89.73%**

**Conclusion:** Candidate B baseline performance is 100% deterministically reproduced.
