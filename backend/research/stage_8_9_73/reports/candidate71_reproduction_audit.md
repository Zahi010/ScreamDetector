# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Candidate 71-D Independent Reproduction Audit

**Project:** Festival Scream Detector  
**Stage:** 8.9.73  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Date:** 2026-11-14  
**Evaluated Checkpoint:** `backend/research/stage_8_9_71/models/candidate_71_frozen.pt`  
**Checkpoint SHA-256:** `e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b`  
**Operating Threshold:** 0.4920  
**Cohort:** Stage 54 Validation Cohort ($N=311$, `EXPOSED_DEVELOPMENT_COHORT`)

---

## 1. Executive Summary & Verification

Candidate 71-D reproduces bit-for-bit on Stage 54 Validation:
- **Overall Scream Recall (Gate 1):** 82.83% (82/99), 95% CI: [74.0%, 91.25%] (FAIL)
- **Hard-Negative FPR (Gate 2):** 8.06% (10/124), 95% CI: [2.83%, 14.29%] (FAIL)
- **Shouted-Speech FPR (Gate 3):** 14.77% (13/88), 95% CI: [2.13%, 32.5%] (PASS)
- **Short-Scream Recall (Gate 4):** 94.87% (37/39), 95% CI: [86.21%, 100.0%] (PASS)
- **Model-Only P95 CPU Latency (Gate 5):** 0.417 ms (PASS)
- **Downstream Pipeline P95 Latency:** 17.22 ms (PASS, $14.5\times$ headroom vs 250.0 ms)

---

## 2. Comprehensive Performance Metrics

- **Precision:** 78.10% (82/105)
- **F1 Score:** 80.39%
- **Specificity:** 89.15% (189/212)
- **Balanced Accuracy:** 85.99%
- **ROC-AUC:** 0.9069
- **PR-AUC:** 0.8482
- **Brier Score:** 0.1393
- **Expected Calibration Error (ECE):** 0.1574
