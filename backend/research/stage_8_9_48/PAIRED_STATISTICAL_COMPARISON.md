# Paired Statistical Comparison: Candidate B vs Candidate R5 — Stage 8.9.48

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.

---

## 1. Executive Summary & Paired Methodology

Because Candidate B and Candidate R5 were evaluated on the exact same 480 audio recordings, standard two-sample independent tests (e.g. Fisher's exact test) are invalid due to paired correlation. This audit evaluates differences using:
1. **Exact McNemar Discordance Testing:** Evaluates the asymmetry of discordant predictions ($b$ vs $c$) under the exact binomial distribution.
2. **Paired Source-Group Cluster Bootstrap ($B=2,000$ Resamples, Seed=42):** Preserves source-group clusters to construct robust empirical confidence intervals for metric differences ($\Delta\text{Recall}$, $\Delta\text{HN-FPR}$, $\Delta\text{F1}$, $\Delta\text{ROC-AUC}$).
3. **Multiple Testing Correction:** Exploratory subtype comparisons apply a Bonferroni-adjusted significance threshold of $\alpha = 0.05 / 6 = 0.00833$.

---

## 2. Contingency Tables of Discordant Predictions

### A. Positive Scream Cohort ($N=160$)

| | Candidate R5 Detected (TP) | Candidate R5 Missed (FN) | Total Candidate B |
| :--- | :---: | :---: | :---: |
| **Candidate B Detected (TP)** | 121 *(Both Detect)* | **23** *(Candidate B Only)* | **144** (90.00%) |
| **Candidate B Missed (FN)** | **0** *(Candidate R5 Only)* | 16 *(Both Miss)* | **16** (10.00%) |
| **Total Candidate R5** | **121** (75.62%) | **39** (24.38%) | **160** |

- **Discordant Pairs:** $b = 23, c = 0$
- **Two-Sided Exact McNemar Test:** $p = 2.3842e-07$ (**STATISTICALLY HIGHLY SIGNIFICANT, $p < 10^{-6}$**)
- **Interpretation:** Candidate B recovered **23 screams** that Candidate R5 missed, while Candidate R5 recovered **0 screams** that Candidate B missed. Candidate B's recall advantage is not an artifact of random sampling.

### B. Hard-Negative Cohort ($N=320$)

| | Candidate R5 Rejected (TN) | Candidate R5 False Alarm (FP) | Total Candidate B |
| :--- | :---: | :---: | :---: |
| **Candidate B Rejected (TN)** | 315 *(Both Reject)* | **1** *(R5 FP Only)* | **316** (98.75%) |
| **Candidate B False Alarm (FP)** | **4** *(Candidate B FP Only)* | 0 *(Both False Alarm)* | **4** (1.25%) |
| **Total Candidate R5** | **319** (99.69%) | **1** (0.31%) | **320** |

- **Discordant Pairs:** $b = 4, c = 1$
- **Two-Sided Exact McNemar Test:** $p = 0.3750$ (**NOT STATISTICALLY SIGNIFICANT, $p = 0.3750 > 0.05$**)
- **Interpretation:** Although Candidate B produced 4 false positives compared to R5's 1 false positive, this difference fails to achieve statistical significance on this sample size. Both candidates pass Gate 2 ($\le 5.0\%$) and Gate 3 ($\le 15.0\%$).

---

## 3. Paired Source-Group Cluster Bootstrap Distribution ($B=2,000$ Resamples)

| Metric Difference ($\Delta = \text{Cand B} - \text{R5}$) | Observed Mean Difference | Bootstrap 95% Confidence Interval | Statistical Conclusion |
| :--- | :---: | :---: | :--- |
| **$\Delta$ Scream Recall** | **+14.30\%** | **[+9.04\%, +20.00\%]** | Strictly positive interval; Candidate B significantly superior ($p < 0.001$). |
| **$\Delta$ Hard-Negative FPR** | **+0.94\%** | **[-0.33\%, +2.34\%]** | Interval includes zero; no statistically significant penalty in rejection. |
| **$\Delta$ F1-Score** | **+7.66\%** | **[+4.02\%, +11.52\%]** | Strictly positive interval; Candidate B provides higher harmonic balance. |
| **$\Delta$ ROC-AUC** | **+0.0106** | **[+0.0036, +0.0184]** | Strictly positive interval; Candidate B has superior global rank separation. |

---

## 4. Subgroup Paired Comparison & Bonferroni Multiple Testing

| Positive Acoustic Subtype | Cohort Clips ($N$) | Candidate B Correct | Candidate R5 Correct | Discordant $b$ (B only) | Discordant $c$ (R5 only) | Exact Binomial $p$-value | Bonferroni Significance ($\alpha=0.0083$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`ultra_short_scream`** | 25 | 25 | 20 | 5 | 0 | 6.2500e-02 | **NOT SIGNIFICANT** |
| **`short_scream`** | 45 | 45 | 39 | 6 | 0 | 3.1250e-02 | **NOT SIGNIFICANT** |
| **`sustained_scream`** | 35 | 33 | 25 | 8 | 0 | 7.8125e-03 | **SIGNIFICANT (p < 0.0083)** |
| **`distant_reverberant_scream`** | 20 | 14 | 14 | 0 | 0 | 1.0000e+00 | **NOT SIGNIFICANT** |
| **`low_intensity_muffled_scream`** | 15 | 12 | 12 | 0 | 0 | 1.0000e+00 | **NOT SIGNIFICANT** |
| **`crowd_masked_scream`** | 20 | 15 | 11 | 4 | 0 | 1.2500e-01 | **NOT SIGNIFICANT** |

---

## 5. Synthesis & Statistical Decision

1. **Asymmetric Detection Advantage:** In 23 clips across 23 distinct independent source groups, Candidate B successfully detected screams that Candidate R5 missed, with zero inverse occurrences.
2. **Short Scream Recovery:** Candidate B achieved a 100% detection rate on short and ultra-short screams ($d \le 1.0\text{s}$), eliminating R5's 11 false negatives in those categories.
3. **Absence of Generalization Failure in Candidate B:** Candidate B maintains 100% specificity on shouted speech (0/80 FP) and 98.75% specificity on overall hard negatives, confirming that its higher recall does not cause a catastrophic false alarm spike.
