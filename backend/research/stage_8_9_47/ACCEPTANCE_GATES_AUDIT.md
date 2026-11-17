# Five Original Acceptance Gates Audit — Stage 8.9.47

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.

---

## 1. Executive Summary & Dual Acceptance Criteria

Every gate is audited against two distinct criteria as mandated by Section 10:
- **Criterion A: Point-Estimate Result** (Does the observed sample mean satisfy the numerical threshold?)
- **Criterion B: Statistical Evidence** (Does the confidence interval statistically support the requirement?)

---

## 2. Gate-by-Gate Evaluation Table (Primary Candidate R5 — Ratio-0P-100A, $\theta^* = 0.8700$)

| Gate | Criterion | Target Requirement | Observed Point Estimate | 95% Wilson CI | Point-Estimate Result | Statistical Evidence Conclusion | Final Gate Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Gate 1** | Overall Scream Recall | $\ge 96.0\%$ | **75.62%** (121/160) | [68.42%, 81.63%] | FAIL | Lower bound (68.42%) < 96.0% | **FAIL** |
| **Gate 2** | Hard-Negative FPR | $\le 5.0\%$ | **0.31%** (1/320) | [0.06%, 1.75%] | PASS | Upper bound (1.75%) <= 5.0% | **PASS** |
| **Gate 3** | Shouted-Speech FPR | $\le 15.0\%$ | **0.00%** (0/80) | [0.00%, 4.58%] | PASS | Upper bound (4.58%) <= 15.0% | **PASS** |
| **Gate 4** | Short-Scream Recall | $\ge 90.0\%$ | **84.29%** (59/70) | [74.01%, 90.99%] | FAIL | Lower bound (74.01%) < 90.0% | **FAIL** |
| **Gate 5** | P95 Streaming Latency | $\le 25.0\text{ ms}$ | **0.452 ms** | [0.410 ms, 0.490 ms] | PASS | Upper bound << 25.0 ms | **PASS** |

---

## 3. Comparison Across Frozen Candidates

| Candidate Configuration | Role | Frozen $\theta^*$ | Gate 1 (Recall $\ge 96\%$) | Gate 2 (HN-FPR $\le 5\%$) | Gate 3 (Shout $\le 15\%$) | Gate 4 (Short $\ge 90\%$) | Gate 5 (Latency $\le 25\text{ms}$) | Overall Gates Passed |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Candidate R5 (Ratio-0P-100A)** | PRIMARY_CANDIDATE | 0.8700 | FAIL | PASS | PASS | FAIL | PASS | 3/5 Full Pass |
| **Candidate R3 (Ratio-50P-50A)** | SECONDARY_CANDIDATE | 0.8400 | FAIL | PASS | PASS | POINT ESTIMATE PASS — STATISTICAL EVIDENCE INSUFFICIENT | PASS | 3/5 Full Pass |
| **Candidate R1 (Ratio-100P-0A)** | REFERENCE_PRISTINE | 0.8700 | FAIL | PASS | PASS | POINT ESTIMATE PASS — STATISTICAL EVIDENCE INSUFFICIENT | PASS | 3/5 Full Pass |
| **Candidate A (Config-B-v5-baseline)** | HISTORICAL_BASELINE | 0.6500 | FAIL | PASS | PASS | PASS | PASS | 4/5 Full Pass |
| **Candidate B (Config-B-Mask-v6)** | HISTORICAL_CONTINUOUS_MASK | 0.8000 | FAIL | PASS | PASS | PASS | PASS | 4/5 Full Pass |
| **Candidate F (Config-B-MaskEarlyRIR)** | HISTORICAL_RIR_MASK | 0.8200 | FAIL | PASS | PASS | PASS | PASS | 4/5 Full Pass |
| **Candidate G (Config-B-ProbMixed-v7)** | HISTORICAL_PROB_MIXED | 0.8500 | FAIL | PASS | PASS | FAIL | PASS | 3/5 Full Pass |

---

## 4. Key Takeaways & Gate Synthesis

1. **Replication of Low False Alarms:** Candidate R5 successfully replicated low hard-negative false alarms on the new cohort ({r5['hn_fpr']:.2f}% HN-FPR, passing Gate 2 point-estimate with upper bound {r5['hn_ci'][1]:.2f}%).
2. **Strict Failure of Gate 1:** Scream recall reached {r5['recall']:.2f}% (95% CI [{r5['rec_ci'][0]:.2f}%, {r5['rec_ci'][1]:.2f}%]), strictly failing Gate 1 across all candidates. No candidate achieves >= 96.0% recall under source-independent evaluation.
3. **Operational Implication:** The system cannot be certified for emergency life-safety alerting.
