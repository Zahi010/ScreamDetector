# Research Acceptance Gate Evaluation — Stage 8.9.54

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Acceptance Gates Evaluated on Validation Partition (`expansion_val`, N=311)

*Note: Evaluated for development guidance; independent test generalization requires future evaluation.*

| Gate | Requirement | Best Retrained Candidate (Candidate E3 (Combined W+Aug)) | Point Estimate | Wilson 95% CI | Gate Status |
|---|---|---|---|---|---|
| **Gate 1: Overall Scream Recall** | $\ge 96.0\%$ | 78 / 99 | **78.79%** | [69.74%, 85.69%] | **FAIL** |
| **Gate 2: Hard-Negative FPR** | $\le 5.0\%$ | 10 / 212 | **4.72%** | [2.58%, 8.46%] | **PASS** |
| **Gate 3: Shouted-Speech FPR** | $\le 15.0\%$ | Shouted FP / Total | **10.23%** | [5.47%, 18.31%] | **PASS** |
| **Gate 4: Short-Scream Recall** | $\ge 90.0\%$ | Short TP / Total | **94.87%** | [83.11%, 98.58%] | **PASS** |
| **Gate 5: Computational Latency** | P95 $\le 25.0$ ms | Model Forward P95 | **< 1.0 ms** | Dedicated Benchmark | **PASS** |

---

## 2. Gate Compliance Summary
While expanded retraining substantially elevated Candidate E's discrimination and brought HN-FPR within the $\le 5.0\%$ boundary, achieving $\ge 96.0\%$ recall simultaneously remains challenging under realistic acoustically masked conditions.
