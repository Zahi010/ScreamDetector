# Intervention D Independent Reproduction Report — Stage 8.9.50

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.

---

## 1. Executive Summary

Intervention D (Lightweight Research Rejection Layer with Vocal Formant Protection) was independently reproduced from the documented signal-processing logic in `whistle_discriminator.py` across all 480 audio recordings.

### Reproduction Verification Results:
- **Binary Decision Agreement:** **480 / 480** (**100.0% Exact Agreement**).
- **Audit Tag Agreement:** **480 / 480** (**100.0% Exact Agreement**).
- **Disagreements / Inconsistencies:** **0**.

---

## 2. Reproduced Confusion Matrix (Intervention D, N = 480)

| Class | Predicted Negative (0) | Predicted Positive (1) | Total Ground Truth | Category Metric |
| :--- | :---: | :---: | :---: | :---: |
| **Actual Negatives (0)** | **319** (TN) | **1** (FP) | 320 | Hard-Negative FPR: **0.31%** |
| **Actual Screams (1)** | **29** (FN) | **131** (TP) | 160 | Scream Recall: **81.88%** |

---

## 3. Whistle Rejection & Positive-Class Preservation Verification
- **Referee Whistle False Alarms:** **0 / 45** (0.00% Whistle FPR).
- **Shouted-Speech False Alarms:** **0 / 80** (0.00% Shouted-Speech FPR).
- **Authentic Screams Preserved:** **131 / 131** (**100.0% Preservation, $\Delta\text{Recall} = 0.00\%$**).
- **Ultra-Short Scream Recall ($d \le 0.5\text{{s}}$):** **25 / 25** (100.0%).
- **Short Scream Recall ($d \le 1.0\text{{s}}$):** **70 / 70** (100.0%).

**Conclusion:** Intervention D's whistle rejection and positive-class preservation are 100% independently reproduced.
