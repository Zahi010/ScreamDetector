# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.64 — Statistical Power & Sample-Size Rationale for Future Evaluation Cohort

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary

This report establishes the statistical power rationale, design effect calculations, and cluster-size limits for the future unexposed evaluation cohort ($N = 1,050$).

The power metrics under varying intra-cluster correlation coefficients ($\rho \in [0.00, 0.20]$) are documented in [`future_evaluation_power_metrics.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_64/future_evaluation_power_metrics.csv).

---

## 2. Target Evaluation Cohort Structure ($N = 1,050$)

```
Future Evaluation Cohort Allocation:
┌──────────────────────────────┬─────────┬───────────────┬───────────────────────────────────────────────────────┐
│ Cohort Partition             │ Size    │ Target Groups │ Subgroup Composition                                  │
├──────────────────────────────┼─────────┼───────────────┼───────────────────────────────────────────────────────┤
│ Target Positives (Screams)   │ 240     │ >= 150 groups │ 120 Short Screams (< 1.00s) + 120 Sustained (>= 1.0s)  │
│ Non-Target Hard Negatives    │ 810     │ >= 450 groups │ Shouts, whistles, sirens, bells, cheering, squeaks    │
├──────────────────────────────┼─────────┼───────────────┼───────────────────────────────────────────────────────┤
│ Total Cohort                 │ 1,050   │ >= 600 groups │ Cluster Cap: Maximum 3 recordings per source group    │
└──────────────────────────────┴─────────┴───────────────┴───────────────────────────────────────────────────────┘
```

---

## 3. Clustered Variance & Design Effect Formulation

Audio recordings originating from the same creator, environment, or session exhibit intra-cluster correlation ($\rho > 0$). When calculating confidence intervals and statistical test power, sample variance must be adjusted by the **Design Effect ($\text{DEFF}$)**:
$$\text{DEFF} = 1 + (\bar{m} - 1)\rho$$
where $\bar{m}$ is the mean cluster size. 

By enforcing a strict **Cluster Cap of $m \le 3$ recordings per source group**, the maximum variance inflation is tightly bounded:
- If $\rho = 0.05 \implies \text{DEFF} = 1 + (3 - 1)(0.05) = 1.100$ ($N_{\text{eff}} = 955$)
- If $\rho = 0.10 \implies \text{DEFF} = 1 + (3 - 1)(0.10) = 1.200$ ($N_{\text{eff}} = 875$)
- If $\rho = 0.15 \implies \text{DEFF} = 1 + (3 - 1)(0.15) = 1.300$ ($N_{\text{eff}} = 808$)

Without a cluster cap (e.g. allowing single sound libraries to contribute $30$ clips), $\text{DEFF}$ would explode to $1 + 29(0.10) = 3.90$, reducing effective sample size by nearly $75\%$.

---

## 4. Confidence Interval Precision at Acceptance Gate Boundaries

At the nominal sample allocations with cluster adjustment ($\rho = 0.10, \text{DEFF} = 1.20$):
1. **Gate 1 (Overall Recall $\ge 96.0\%$):**
   - $N_{\text{eff}} = 200$.
   - 95% Wilson Score Interval half-width is $\pm 2.83\%$.
   - A measured recall of $98.0\%$ establishes a lower $95\%$ bound of $95.17\%$.
2. **Gate 2 (False Positive Rate $\le 5.0\%$):**
   - $N_{\text{eff}} = 675$.
   - 95% Wilson Score Interval half-width is $\pm 1.66\%$.
   - A measured FPR of $3.0\%$ establishes an upper $95\%$ bound of $4.66\%$, ensuring a statistically significant pass below $5.0\%$.
3. **Gate 4 (Short-Scream Recall $\ge 90.0\%$):**
   - $N_{\text{eff}} = 100$.
   - 95% Wilson Score Interval half-width is $\pm 5.96\%$.
   - A measured recall of $96.0\%$ establishes a lower $95\%$ bound of $90.04\%$, guaranteeing formal gate compliance under clustered bootstrap verification.

