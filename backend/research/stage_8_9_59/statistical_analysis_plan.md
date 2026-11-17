# Statistical Analysis Plan — Stage 8.9.59

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. Not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. No production promotion is authorized.

---

## 1. Executive Summary

In Phase I of Stage 8.9.59, a formalized Statistical Analysis Plan (SAP) was authored to govern the evaluation of future candidate models.

The plan defines:
- Primary and secondary endpoints based strictly on the Original Five Project Acceptance Gates.
- Clustered bootstrap confidence interval formulations that prevent pseudo-replication.
- Hypothesis testing procedures for candidate comparisons.
- Multiplicity corrections for subgroup analyses.
- Minimum subgroup sample size thresholds for statistical defensibility.

This plan must be preregistered and cryptographically frozen before any future test cohort is evaluated.

---

## 2. Evaluation Endpoints (Restoring the Original Five Project Gates)

| Gate # | Endpoint Name | Metric Definition | Target Acceptance Criterion | Operational Dataset Cohort |
|:---:|---|---|:---:|---|
| **Gate 1** | **Overall Scream Recall** | $\text{TP} / (\text{TP} + \text{FN})$ | **$\ge 96.00\%$** | All authentic scream positives |
| **Gate 2** | **Hard-Negative FPR** | $\text{FP} / (\text{FP} + \text{TN})$ | **$\le 5.00\%$** | All non-scream hard negatives |
| **Gate 3** | **Shouted-Speech FPR** | $\text{FP}_{\text{shout}} / N_{\text{shout}}$ | **$\le 15.00\%$** | Shouted speech negatives |
| **Gate 4** | **Short-Scream Recall** | $\text{TP}_{\text{short}} / N_{\text{short}}$ | **$\ge 90.00\%$** | Transient screams $<1.0\text{ s}$ |
| **Gate 5** | **Model-Only Inference P95** | 95th percentile forward pass | **$\le 25.00\text{ ms}$** | Steady-state CPU inference ($N \ge 300$) |

### Engineering Checks (Reported Separately)
- **DSP Numerical Equivalence:** $\text{MaxAE} \le 1.0\text{ ULP}$, Pearson $r \ge 0.99999$.
- **Downstream Pipeline Latency:** Preprocessing + DSP + Model P95 $\le 25.00\text{ ms}$.
- **Streaming Correctness:** 0 memory leaks, 0 state contamination, 0 deadline misses against 250 ms hop.
- **Production Immutability:** 100% SHA-256 match on all 4 production assets.

---

## 3. Confidence Interval Methodology

### 3.1 Cluster-Adjusted Bootstrap Resampling
Recordings derived from the same source group or speaker share latent acoustic properties (microphone type, room acoustics, vocal tract dimensions). Treating multiple clips from one source group as independent observations causes severe pseudo-replication and artificially narrows confidence intervals.

**Mandatory Procedure:**
1. Resample at the **source-group cluster level** with replacement for $B = 2,000$ iterations.
2. For each bootstrap iteration $b \in \{1, \dots, 2000\}$, extract all recording clips associated with the selected source groups.
3. Compute the endpoint metric $\hat{\theta}^{(b)}$.
4. Calculate the 95% two-sided confidence interval using the **Bias-Corrected and Accelerated ($\text{BC}_a$) bootstrap method**.

### 3.2 Wilson Score Interval for Small Subgroups
For small acoustic subgroups where $N < 50$, the Wilson score interval with continuity correction shall be reported alongside the bootstrap interval to guarantee bounded performance bounds:
$$\text{CI}_{95\%} = \frac{\hat{p} + \frac{z^2}{2N} \pm z \sqrt{\frac{\hat{p}(1 - \hat{p})}{N} + \frac{z^2}{4N^2}}}{1 + \frac{z^2}{N}}$$

---

## 4. Hypothesis Testing & Comparative Candidate Analysis

### 4.1 Paired McNemar Test on Discordant Pairs
When comparing two frozen candidate models (e.g. Candidate E1 vs Candidate B) evaluated on the identical test cohort, an unpaired two-sample test is statistically invalid.
- Construct the $2 \times 2$ contingency table of discordant classifications:
  - $b$: Model 1 correct, Model 2 incorrect.
  - $c$: Model 1 incorrect, Model 2 correct.
- Evaluate exact binomial McNemar test statistic:
  $$\chi^2 = \frac{(|b - c| - 1)^2}{b + c}, \quad p < 0.05 \implies \text{Statistically Significant Difference}$$

### 4.2 Multiplicity Correction (Benjamini-Hochberg FDR)
When evaluating models across multiple exploratory subgroups (short screams, sustained screams, crowd-masked screams, infant crying, sirens, whistles, cheering), $p$-values must be adjusted using the **Benjamini-Hochberg False Discovery Rate (FDR) procedure** at $q = 0.05$ to prevent Type I error inflation.

---

## 5. Minimum Evidence Requirements for Subgroup Reporting

- Any subgroup with fewer than **15 independent source groups** shall be reported as **"Preliminary / Exploratory Only"** and cannot be used to substantiate generalization claims.
- Formal statistical claims require a minimum of **30 independent source groups**.
- No candidate threshold tuning or post-hoc model recalibration on the evaluation cohort is permitted.

