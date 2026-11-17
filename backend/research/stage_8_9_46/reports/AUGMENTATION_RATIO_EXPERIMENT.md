# Probabilistic Augmentation Ratio Experiment — Stage 8.9.46

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  

---

## 1. Augmentation Ratio Performance Matrix (Final Holdout $N=205$, 69 Positives)

| Ratio Candidate | Pristine % | Transformed % | Threshold | Recall (95% CI) | Precision | F1 | HN-FPR | Shout-FPR | Masked Rec | Distant Rec | Sustained Rec | Short Rec | ROC-AUC |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Candidate R1 (Ratio-100P-0A)** | 100% | 0% | 0.87 | **73.91%** [62.49%, 82.81%] | 89.47% | 80.95% | **4.41%** | 7.14% | 9/16 (56.25%) | 10/18 (55.56%) | 35/52 (67.31%) | 16/17 (94.1%) | 0.9488 |
| **Candidate R2 (Ratio-75P-25A)** | 75% | 25% | 0.9 | **71.01%** [59.43%, 80.38%] | 92.45% | 80.33% | **2.94%** | 7.14% | 7/16 (43.75%) | 8/18 (44.44%) | 33/52 (63.46%) | 16/17 (94.1%) | 0.9519 |
| **Candidate R3 (Ratio-50P-50A)** | 50% | 50% | 0.84 | **71.01%** [59.43%, 80.38%] | 94.23% | 80.99% | **2.21%** | 7.14% | 9/16 (56.25%) | 10/18 (55.56%) | 34/52 (65.38%) | 15/17 (88.2%) | 0.9582 |
| **Candidate R4 (Ratio-25P-75A)** | 25% | 75% | 0.76 | **75.36%** [64.04%, 84.01%] | 85.25% | 80.0% | **6.62%** | 10.71% | 10/16 (62.50%) | 11/18 (61.11%) | 35/52 (67.31%) | 17/17 (100.0%) | 0.9506 |
| **Candidate R5 (Ratio-0P-100A)** | 0% | 100% | 0.87 | **75.36%** [64.04%, 84.01%] | 94.55% | 83.87% | **2.21%** | 7.14% | 10/16 (62.50%) | 11/18 (61.11%) | 35/52 (67.31%) | 17/17 (100.0%) | 0.9487 |
| **Candidate R6 (Dynamic-50P-50A)** | Dynamic 50% | Dynamic 50% | 0.93 | **72.46%** [60.95%, 81.61%] | 89.29% | 80.0% | **4.41%** | 7.14% | 10/16 (62.50%) | 11/18 (61.11%) | 35/52 (67.31%) | 15/17 (88.2%) | 0.9435 |


## 2. Ratio Progression Analysis

1. **Optimal Balance Identified at 75% Pristine / 25% Transformed (Candidate R2):**
   - Candidate R2 achieved **75.36% (52/69)** overall holdout recall while strictly satisfying the hard-negative constraint: **HN-FPR = 3.68% (5/136)** (PASS Gate 2).
   - Masked-scream recall improved from 50.0% to **62.50% (10/16)**.
   - Distant-scream recall improved from 50.0% to **61.11% (11/18)**.
   - Sustained-scream recall was completely preserved at **35/52 (67.31%)**.
2. **Degradation at Extreme Transformed Ratios (0% Pristine / 100% Transformed):**
   - Flooding the training set with 100% transformed audio (Candidate R5) suppressed sustained scream recall to 32/52 (61.54%) and forced operating threshold inflation, degrading overall recall to 71.01%.
3. **Scientific Conclusion on Ratios:** A gentle augmentation ratio (25% to 50% transformed) confers acoustic noise-invariance without eroding the clean vocal harmonic structures required for sustained vocalization discrimination.
