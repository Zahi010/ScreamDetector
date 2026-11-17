# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Statistical Confidence Interval Methodology & Resampling Audit

**Project:** Festival Scream Detector  
**Stage:** 8.9.74  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Date:** 2026-11-14  
**Target Subject:** Resampling methods, cluster-aware bootstrap vs. naive i.i.d. bootstrap, and uncertainty quantification.

---

## 1. Executive Summary & Core Principle

In acoustic signal processing, recordings frequently originate as segmented sister excerpts from the same continuous acoustic event, environment, microphone, or uploader session. Treating these excerpts as independent and identically distributed (i.i.d.) violates basic statistical assumptions and produces artificially narrow confidence intervals.

Stage 8.9.74 conducted a formal methodological audit comparing:
1. **Naive i.i.d. Bootstrap Resampling:** Resampling individual recording rows with replacement ($N=311$).
2. **Source-Group-Aware Cluster Bootstrap Resampling:** Resampling entire source groups with replacement ($N_{clusters}=138$), preserving intra-cluster acoustic correlations.

### Key Resampling Audit Findings:
- In Gate 3 (Shouted-Speech FPR), naive i.i.d. bootstrap yields `[7.78%, 22.89%]`, while true source-group cluster bootstrap yields `[2.33%, 31.15%]`.
- The cluster bootstrap interval is **$1.9×$ wider** because the 88 shouted-speech recordings originate from only 28 source groups (mean 3.14 clips/SG). Resampling a single uploader cluster (such as `reitanna` with 8 false alarms) drastically shifts the observed FPR.
- **Mandatory Decision Protocol:** While Candidate 71-D achieves a point estimate of **14.77%** (satisfying Gate 3 $\le 15.0\%$), the upper bound of the 95% cluster-aware bootstrap CI reaches **31.15%**. A point-estimate pass must never be cited as definitive population-level compliance when the confidence interval crosses the threshold.

---

## 2. Comparative Resampling Ledger ($B=2,000$ Resamples, Seed=42)

| Acceptance Gate | Evaluated Metric | Point Estimate | Naive i.i.d. 95% Bootstrap CI | Source-Group Cluster 95% Bootstrap CI | Independent Source Groups | Statistical Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Gate 1** | Overall Scream Recall ($\ge 96.0\%$) | **82.83%** (82/99) | [75.00%, 89.89%] | **[74.07%, 91.77%]** | 47 SGs | `FAIL — POINT ESTIMATE` |
| **Gate 2** | Hard-Negative FPR ($\le 5.0\%$) | **8.06%** (10/124) | [3.48%, 13.11%] | **[2.94%, 14.16%]** | 69 SGs | `FAIL — POINT ESTIMATE` |
| **Gate 3** | Shouted-Speech FPR ($\le 15.0\%$) | **14.77%** (13/88) | [7.78%, 22.89%] | **[2.33%, 31.15%]** | 28 SGs | `PASS — POINT ESTIMATE` (CI crosses ceiling) |
| **Gate 4** | Short-Scream Recall ($\ge 90.0\%$) | **94.87%** (37/39) | [87.18%, 100.00%] | **[86.84%, 100.00%]** | 24 SGs | `PASS — POINT ESTIMATE` (CI crosses floor) |
| **Gate 5** | Model CPU P95 Latency ($\le 25.0$ ms) | **0.370 ms** | [0.350 ms, 0.420 ms] | **[0.350 ms, 0.450 ms]** | Local CPU | `PASS — POINT ESTIMATE` (Strong Headroom) |

---

## 3. Methodological Formulation of Cluster Bootstrap

Let the dataset $\mathcal{D}$ be partitioned into $K$ disjoint clusters (source groups) $\mathcal{C}_1, \mathcal{C}_2, \dots, \mathcal{C}_K$, where $\sum_{k=1}^K |\mathcal{C}_k| = N$:

1. In each bootstrap iteration $b \in \{1, \dots, B\}$ ($B=2,000$):
   - Sample $K$ cluster indices with replacement: $\{k_1^*, k_2^*, \dots, k_K^*\}$ from $\{1, \dots, K\}$.
   - Construct the bootstrap sample $\mathcal{D}_b^* = \bigcup_{j=1}^K \mathcal{C}_{k_j^*}$.
2. Compute the metric of interest $\theta_b^* = \hat{\theta}(\mathcal{D}_b^*)$.
3. Construct the two-sided 95% empirical percentile confidence interval as:
   $$\text{CI}_{0.95} = \left[ \theta^*_{(0.025 \cdot B)}, \; \theta^*_{(0.975 \cdot B)} \right]$$

### Determinism & Reproducibility Guarantee:
- The random seed is permanently fixed to `42`.
- Intra-cluster memberships are strictly preserved.
- Subgroup masks (Positives, Hard Negatives, Shouted Speech, Short Screams) are evaluated solely on the resampled rows belonging to those target categories.

---

## 4. Evidence Sufficiency Guidelines

To prevent premature claims of compliance, Stage 8.9.74 establishes three distinct reporting designations:

1. `PASS — POINT ESTIMATE`: The empirical point estimate satisfies the numerical threshold, but the 95% cluster-aware CI may cross the boundary.
2. `FAIL — POINT ESTIMATE`: The empirical point estimate fails the numerical threshold.
3. `INSUFFICIENT EVIDENCE`: The sample size or number of independent source groups is statistically inadequate to establish bounded confidence, regardless of point estimate.

Under these definitions, Gates 1 and 2 fail unequivocally by point estimate. Gate 3 and Gate 4 pass by point estimate, but their cluster-aware confidence intervals indicate that true out-of-distribution performance could vary widely until tested on larger, independent cohorts.

