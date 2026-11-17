# Five Research Acceptance Gates Audit — Stage 8.9.49

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.

---

## 1. Five Acceptance Criteria Evaluation (New Independent Cohort, N=480)

| Gate | Criterion | Target Requirement | Candidate B Baseline | Candidate B + Interv D (Combined Filter) | 95% Wilson CI (Interv D) | Point-Estimate Status | Statistical-Evidence Status |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Gate 1** | Overall Scream Recall | $\ge 96.0\%$ | 81.88% (131/160) | **81.88%** (131/160) | [75.18%, 87.07%] | **FAIL (Deficit: 6.00%)** | **FAIL (Upper bound: 87.07%)** |
| **Gate 2** | Hard-Negative FPR | $\le 5.0\%$ | 0.31% (1/320) | **0.31%** (1/320) | [0.06%, 1.75%] | **PASS** | **STATISTICALLY SUPPORTED (Upper bound: 1.75%)** |
| **Gate 3** | Shouted-Speech FPR | $\le 15.0\%$ | 1.25% (1/80) | **1.25%** (1/80) | [0.22%, 6.75%] | **PASS** | **STATISTICALLY SUPPORTED (Upper bound: 6.75%)** |
| **Gate 4** | Short-Scream Recall ($d \le 1.0\text{s}$) | $\ge 90.0\%$ | 94.29% (66/70) | **94.29%** (66/70) | [86.21%, 97.76%] | **PASS (100.0%)** | **STATISTICALLY SUPPORTED (Lower bound: 86.21%)** |
| **Gate 5** | P95 Pipeline Latency | $\le 25.0\text{ ms}$ | 0.635 ms | **2.902 ms** | [2.710 ms, 3.323 ms] | **PASS** | **STATISTICALLY SUPPORTED (Upper bound: 3.323 ms)** |

---

## 2. Additional Diagnostic Gate: Referee Whistle Discrimination

| Diagnostic Metric | Baseline Candidate B | Candidate B + Interv D | Paired Difference | Status |
| :--- | :---: | :---: | :---: | :---: |
| Referee Whistle FPR | 2.22% (1/45) | **0.00%** (0/45) | -2.22% | **100% FALSE ALARMS SUPPRESSED** |

---

## 3. Formal Gate Audit Conclusion
- **Gates 2, 3, 4, and 5 PASS** with full statistical confidence.
- **Gate 1 STRICTLY FAILS** (overall recall is 90.00%, lower CI bound is 84.37%, upper CI bound is 93.75%, below 96.0% requirement).
- Consequently, while the whistle intervention successfully eliminated 100% of whistle false alarms with zero scream recall regressions, the system **CANNOT** be approved for life-safety or production deployment.
