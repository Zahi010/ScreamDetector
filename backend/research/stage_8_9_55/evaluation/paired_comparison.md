# Paired Model Comparison Report — Stage 8.9.55

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. 2x2 Contingency Table (Candidate E1 vs Candidate B)

Evaluated on identical 450 recordings across 246 independent source groups:

| | Candidate B Correct | Candidate B Incorrect | Total |
|---|---|---|---|
| **Candidate E1 Correct** | 353 | 37 | 390 |
| **Candidate E1 Incorrect** | 10 | 50 | 60 |
| **Total** | 363 | 87 | 450 |

---

## 2. McNemar's Statistical Significance Test
- Disagreement Pairs: **47 recordings** (37 E1-only correct vs 10 B-only correct)
- McNemar's $\chi^2$ (with continuity correction): **14.3830**
- Two-sided asymptotic $p$-value: **0.00015**
- Statistical Significance: **STATISTICALLY SIGNIFICANT (p < 0.05)**

---

## 3. Stratified Source-Group Cluster Bootstrap (2,000 Replicates)

Sampling unit: **Independent Source Group** (N = 246), fixed seed = 42.

| Metric Delta ($\Delta = \text{E1} - \text{B}$) | Point Estimate Delta | Bootstrap Mean | 95% Cluster Bootstrap CI |
|---|---|---|---|
| **$\Delta$ Scream Recall** | **+17.33%** | +17.33% | **[+10.96%, +25.00%]** |
| **$\Delta$ Hard-Negative FPR** | **-0.33%** | -0.32% | **[-3.47%, +2.93%]** |
| **$\Delta$ F1-Score** | **+12.80%** | +12.87% | **[+7.11%, +19.82%]** |
