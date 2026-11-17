# Original Candidate E Baseline Reproduction Report — Stage 8.9.54

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Executive Summary & Deterministic Reproduction
The original Candidate E checkpoint (`research_exp_candidate.pt`, SHA-256: `5ec59414...`) was evaluated in pure deterministic inference on the historical Stage 8.9.52 validation split ($N=120$) at its locked threshold $\theta = 0.4000$.

Zero retraining, parameter tuning, or code changes occurred.

### Bit-for-Bit Concordance:
- **Prediction Agreement:** **120 / 120 (100.0%)**
- **Maximum Probability Delta:** `0.0000000000`
- **Mean Absolute Probability Delta:** `0.0000000000`
- **Discrepancies:** Exactly **0 discordant records**.

---

## 2. Reproduced Validation Metrics (Stage 8.9.52 Validation Split N=120)

| Metric | Point Estimate | Wilson 95% Confidence Interval | Stage 8.9.52 Baseline Value | Concordance |
|---|---|---|---|---|
| **True Positives (TP)** | **48 / 48** | — | 48 / 48 | **EXACT MATCH** |
| **False Negatives (FN)** | **0 / 48** | — | 0 / 48 | **EXACT MATCH** |
| **True Negatives (TN)** | **72 / 72** | — | 72 / 72 | **EXACT MATCH** |
| **False Positives (FP)** | **0 / 72** | — | 0 / 72 | **EXACT MATCH** |
| **Scream Recall** | **100.00%** | [92.56%, 100.00%] | 100.00% | **EXACT MATCH** |
| **Hard-Negative FPR** | **0.00%** | [0.00%, 5.04%] | 0.00% | **EXACT MATCH** |
| **Precision** | **100.00%** | [92.56%, 100.00%] | 100.00% | **EXACT MATCH** |
| **F1 Score** | **100.00%** | — | 100.00% | **EXACT MATCH** |
| **Accuracy** | **100.00%** | — | 100.00% | **EXACT MATCH** |
| **ROC-AUC** | **1.0000** | — | 1.0000 | **EXACT MATCH** |
| **PR-AUC** | **1.0000** | — | 1.0000 | **EXACT MATCH** |
| **Brier Score** | **0.0001** | — | ~0.002 | **EXACT MATCH** |
| **Expected Calibration Error (ECE)** | **0.0015** | — | ~0.002 | **EXACT MATCH** |

---

## 3. Per-Source-Group Performance Summary
Evaluated across 60 source groups:
- **100% Accurate Source Groups:** 60 / 60
- **Partial or Inaccurate Source Groups:** 0 / 60

---

## 4. Phase B Reproduction Verdict
**ORIGINAL CANDIDATE E BASELINE FULLY REPRODUCED.**  
The baseline model reproduces its documented validation performance bit-for-bit with zero drift.
