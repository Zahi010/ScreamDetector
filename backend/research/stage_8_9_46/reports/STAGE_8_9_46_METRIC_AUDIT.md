# Numerical & Metric Forensic Audit — Stage 8.9.46

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  

---

## 1. Complete Recalculation Audit Matrix (Final Holdout $N=205$)

| Candidate | Threshold | TP | FP | TN | FN | Recalculated Recall | Recalculated Precision | Recalculated F1 | Recalculated HN-FPR | Shout-FPR | Recalc ROC-AUC | Recalc PR-AUC | Audit Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Candidate A (Config-B-v5-baseline)** | 0.82 | 52 | 5 | 131 | 17 | **75.36%** | 91.23% | 82.54% | **3.68%** | 7.14% | 0.9487 | 0.9104 | **VERIFIED (PASS)** |
| **Candidate B (Config-B-Mask-v6)** | 0.86 | 50 | 6 | 130 | 19 | **72.46%** | 89.29% | 80.0% | **4.41%** | 7.14% | 0.9531 | 0.9152 | **VERIFIED (PASS)** |
| **Candidate C (Config-B-MildMask)** | 0.91 | 49 | 5 | 131 | 20 | **71.01%** | 90.74% | 79.67% | **3.68%** | 10.71% | 0.9533 | 0.8961 | **VERIFIED (PASS)** |
| **Candidate D (Config-B-MultiSNR)** | 0.85 | 49 | 7 | 129 | 20 | **71.01%** | 87.5% | 78.4% | **5.15%** | 7.14% | 0.9503 | 0.8831 | **VERIFIED (PASS)** |
| **Candidate E (Config-B-MaskAtten)** | 0.73 | 54 | 10 | 126 | 15 | **78.26%** | 84.38% | 81.2% | **7.35%** | 10.71% | 0.9442 | 0.8890 | **VERIFIED (PASS)** |
| **Candidate F (Config-B-MaskEarlyRIR)** | 0.86 | 52 | 8 | 128 | 17 | **75.36%** | 86.67% | 80.62% | **5.88%** | 10.71% | 0.9519 | 0.8991 | **VERIFIED (PASS)** |
| **Candidate G (Config-B-ProbMixed)** | 0.85 | 52 | 7 | 129 | 17 | **75.36%** | 88.14% | 81.25% | **5.15%** | 10.71% | 0.9474 | 0.8976 | **VERIFIED (PASS)** |
| **Ablation Ref: Attenuation Alone** | 0.93 | 48 | 5 | 131 | 21 | **69.57%** | 90.57% | 78.69% | **3.68%** | 14.29% | 0.9433 | 0.8954 | **VERIFIED (PASS)** |
| **Ablation Ref: RIR Alone** | 0.98 | 45 | 4 | 132 | 24 | **65.22%** | 91.84% | 76.27% | **2.94%** | 10.71% | 0.9514 | 0.9099 | **VERIFIED (PASS)** |
| **Ablation Ref: All Three Combined (v6)** | 0.85 | 51 | 5 | 131 | 18 | **73.91%** | 91.07% | 81.6% | **3.68%** | 7.14% | 0.9514 | 0.8913 | **VERIFIED (PASS)** |


## 2. Forensic Investigation: Candidate E Precision / F1 Discrepancy

### The Apparent Paradox
In Stage 8.9.45, Candidate E (`Config-B-MaskAtten`) achieved:
- **Holdout Recall:** 78.26% (54/69) — highest among all candidates.
- **Holdout Precision:** 84.38% (54/64).
- **Holdout F1 Score:** 81.20%.
- **BUT Hard-Negative FPR:** 7.35% (10/136) — **strictly FAILING Gate 2 ($\le 5.0\%$)**.

### Mathematical Proof & Ground Truth
$$\text{Precision} = \frac{54}{54 + 10} = \frac{54}{64} = 84.375\% \approx 84.38\%$$
$$\text{Recall} = \frac{54}{54 + 15} = \frac{54}{69} = 78.2608\% \approx 78.26\%$$
$$\text{F1} = \frac{2 \times 54}{2 \times 54 + 10 + 15} = \frac{108}{133} = 81.2030\% \approx 81.20\%$$
$$\text{HN-FPR} = \frac{10}{136} = 7.3529\% \approx 7.35\%$$

### Forensic Insight:
1. **Mathematical Accuracy:** There is no formula or arithmetic bug in Candidate E's reported metrics. The values in `CANDIDATE_COMPARISON_V7.csv` match the raw confusion matrix $(54, 10, 126, 15)$ byte-for-byte.
2. **The F1 Fallacy in Negative-Heavy Cohorts:** In an evaluation cohort with 136 hard negatives and 69 positives, false positives are diluted in the precision denominator by true positives $(\text{Prec} = \text{TP} / (\text{TP} + \text{FP}))$. Consequently, doubling false alarms from 5 to 10 only reduced precision from 91.23% to 84.38%, leaving F1 deceptively high at 81.20%.
3. **Threshold Sensitivity:** Candidate E's operating threshold was selected on `v5_validation` at $\theta^* = 0.7300$ because validation negatives were slightly easier than holdout negatives. When transferred to the unseen holdout sound sources, this low threshold permitted 10 false alarms (7.35% FPR).
4. **Takeaway for Stage 8.9.46:** Operating point selection must enforce strict safety constraints on HN-FPR with safety margins rather than unconstrained F1 maximization.
