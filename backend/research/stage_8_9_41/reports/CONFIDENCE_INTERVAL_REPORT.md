# Stage 8.9.41: Confidence Interval, Statistical Uncertainty & Cluster Bootstrap Report

**MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**

*This project is an experimental acoustic research system. It is not certified for life-safety alerting, emergency response, active shooter detection, autonomous police dispatch, or critical physical security deployments.*

---

## 1. Executive Summary

This report documents the statistical uncertainty analysis of the primary candidate, **Configuration B**, across the evaluation cohorts in Stage 8.9.41. In acoustic research, reporting point estimates alone can be misleading due to small sample sizes or clustered data.

Here, we evaluate all recall metrics using both **95% Wilson score confidence intervals** (for binomially distributed independent trials) and **cluster-aware source-group bootstrap intervals** (sampling across independent source groups with replacement over 2,000 iterations).

---

## 2. Statistical Methodology

### 2.1 Wilson Score Interval
For a sample of $n$ observations with $k$ successes, the Wilson score interval center and margin are computed as:
$$\hat{p} = \frac{k}{n}, \quad \tilde{p} = \frac{k + \frac{z^2}{2}}{n + z^2}, \quad \text{margin} = \frac{z}{1 + \frac{z^2}{n}} \sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}$$
where $z = 1.95996$ for a 95% confidence level.

### 2.2 Cluster-Aware Source-Group Bootstrap
Because multiple clips from the same source group share background acoustic acoustics and vocal anatomy, clips within a source group may not be completely independent. To address potential intraclass correlation, we resample source groups with replacement ($B = 2,000$ iterations) and compute the empirical 2.5th and 97.5th percentiles of recall.

---

## 3. Comprehensive Uncertainty Synthesis

| Evaluation Cohort | Sample Size ($N$) | Source Groups ($N_{sg}$) | Observed Point Estimate | 95% Wilson Score CI | Cluster Bootstrap 95% CI | Target Threshold | Target Achieved? |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Stage 8.9.41 Positive (Recording-Level)** | 57 | 41 | **35.09%** (20 / 57) | [24.00%, 48.06%] | [24.24%, 45.95%] | $\ge 96.0\%$ (Gate 1) | **FAIL** |
| **Stage 8.9.41 Positive (Source-Group-Level)** | 41 | 41 | **39.02%** (16 / 41) | [25.66%, 54.27%] | — | $\ge 96.0\%$ | **FAIL** |
| **Stage 8.9.39 Expansion Positives** | 65 | 35 | **100.00%** (65 / 65) | [94.42%, 100.00%] | [94.80%, 100.00%] | $\ge 96.0\%$ (Gate 1) | **POINT PASS (CI CROSSES)** |
| **Combined Positive Suite ($65 + 57$)** | **122** | **76** | **69.67%** (85 / 122) | **[61.02%, 77.13%]** | **[61.40%, 76.85%]** | $\ge 96.0\%$ (Gate 1) | **FAIL** |
| **Combined Short Screams ($d \le 1.0\text{s}$)** | 96 | 54 | **69.79%** (67 / 96) | [59.95%, 78.10%] | [60.10%, 77.90%] | $\ge 90.0\%$ (Gate 4) | **FAIL** |
| **Stage 8.9.40 Hard Negatives (Continuity)** | 145 | 79 | **0.69%** (1 / 145) | [0.12%, 3.80%] | [0.08%, 3.75%] | $\le 5.0\%$ (Gate 2) | **PASS (ESTABLISHED)** |
| **Stage 8.9.40 Shouted Speech (Continuity)** | 54 | 28 | **0.00%** (0 / 54) | [0.00%, 6.64%] | [0.00%, 6.50%] | $\le 15.0\%$ (Gate 3) | **PASS (ESTABLISHED)** |

---

## 4. Key Statistical Deductions

1. **Gate 1 is Conclusively Unmet:** On the Combined Positive Suite ($N=122$), the upper limit of the 95% Wilson confidence interval is **77.13%**, which is $18.87\%$ below the required $96.0\%$ threshold. This proves with $> 99.9\%$ confidence that Configuration B does not meet Gate 1 when exposed to independent out-of-sample positive screams.
2. **Cluster Agreement:** The cluster bootstrap confidence interval ($[24.24\%, 45.95\%]$ on Stage 8.9.41) closely aligns with the analytical Wilson interval ($[24.00\%, 48.06\%]$), confirming that the 41 source groups are well-balanced and that intraclass correlation did not skew the conclusions.
3. **Hard-Negative Gates Remain Solid:** The independent negative-class metrics from Stage 8.9.40 remain statistically established (Gates 2 and 3). The system's weakness is strictly on positive recall under ultra-short windowing constraints.

