# Statistical Terminology & Rigor Corrections — Stage 8.9.56.1

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Executive Summary & Audit Mandate

Phase F (Section 9) of Stage 8.9.56.1 mandates a formal correction of statistical terminology used in prior stage reports, specifically addressing claims of "FPR parity", the rigorous interpretation of cluster bootstrap intervals, and the precise labeling of McNemar paired test variants.

All underlying statistical calculations remain **100% verified and mathematically sound**; this audit rectifies inferential framing to adhere strictly to formal statistical doctrine.

---

## 2. Hard-Negative FPR: Correction from "Parity" to "No Significant Difference"

### 2.1 The Erroneous Claim
In Stage 8.9.55 and Stage 8.9.56, the difference in hard-negative false positive rate between Candidate E1 ($6.33\%$, 19/300) and Candidate B ($6.67\%$, 20/300) was reported with a 2,000-replicate source-group cluster bootstrap 95% confidence interval of:

$$\Delta \text{HN-FPR} = -0.33\% \quad [ -3.47\%, +2.93\% ]$$

Prior narrative prose described this result as:
> *"confirming FPR parity between Candidate E1 and Candidate B."*

### 2.2 Formal Statistical Correction
In frequentist hypothesis testing and estimation theory:
1. **Failure to reject the null hypothesis does NOT prove the null hypothesis.** A confidence interval that spans zero simply indicates that the observed sample difference is compatible with zero under random sampling variation.
2. **Equivalence / Parity Requires Pre-Specified Bounds:** Establishing formal statistical "parity" or "equivalence" requires pre-specifying an equivalence margin $\pm \delta$ and conducting a formal Two One-Sided Tests (TOST) equivalence procedure. No such equivalence margin was pre-registered in Stage 8.9.55.
3. **Correct Statistical Conclusion:**
   > **No statistically significant hard-negative FPR difference was established between Candidate E1 and Candidate B ($\Delta = -0.33\%$, 95% Cluster Bootstrap CI: $[-3.47\%, +2.93\%]$).**

The claim of "proven parity" or "established equivalence" is formally retracted and replaced across all stage documentation.

---

## 3. Scream Recall Superiority

Candidate E1's recall superiority over Candidate B remains fully verified:
- **Candidate E1 Recall:** $72.67\%$ (109 / 150), 95% Wilson CI: $[65.04\%, 79.17\%]$
- **Candidate B Recall:** $55.33\%$ (83 / 150), 95% Wilson CI: $[47.34\%, 63.06\%]$
- **Paired Recall Delta ($\text{E1} - \text{B}$):** **$+17.33\text{ percentage points}$**
- **2,000-Replicate Source-Group Cluster Bootstrap (Seed = 42):**
  $$\Delta \text{Recall} = +17.33\% \quad [ +10.96\%, +25.00\% ]$$

Because the entire 95% confidence interval lies strictly above zero ($> +10.96\%$), Candidate E1 demonstrates **statistically significant and robust recall superiority** on the unseen evaluation cohort, accounting for cluster correlations within sound collection sources.

---

## 4. F1-Score Superiority

Candidate E1's F1-score improvement over Candidate B remains verified:
- **Candidate E1 F1-Score:** $78.42\%$ (Precision $85.16\%$, Recall $72.67\%$)
- **Candidate B F1-Score:** $65.61\%$ (Precision $80.58\%$, Recall $55.33\%$)
- **Paired F1 Delta ($\text{E1} - \text{B}$):** **$+12.80\text{ percentage points}$**
- **2,000-Replicate Source-Group Cluster Bootstrap (Seed = 42):**
  $$\Delta \text{F1} = +12.80\% \quad [ +7.11\%, +19.82\% ]$$

The entire 95% cluster bootstrap confidence interval is strictly positive ($> +7.11\%$), confirming significant overall harmonic precision-recall superiority.

---

## 5. Precise Identification of McNemar Test Variants

Across the 450 evaluation recordings, paired prediction discordance between Candidate E1 and Candidate B yielded:
- $n_{10}$ (Candidate E1 correct, Candidate B incorrect): **37 recordings**
- $n_{01}$ (Candidate B correct, Candidate E1 incorrect): **10 recordings**
- Discordance Ratio: $3.7 : 1$

To eliminate confusion between different statistical software outputs, all three standard McNemar variants are explicitly documented:

| McNemar Test Variant | Formula | Test Statistic | $p$-value | Significance Finding |
|---|---|---|---|---|
| **Edwards Continuity-Corrected** | $\chi^2 = \frac{(|n_{10} - n_{01}| - 1)^2}{n_{10} + n_{01}} = \frac{(|37 - 10| - 1)^2}{47} = \frac{676}{47}$ | $\chi^2 = \mathbf{14.3830}$ | $p = \mathbf{0.00015}$ ($1.5 \times 10^{-4}$) | **Statistically Significant** ($p < 0.001$) |
| **Exact Binomial (Two-Sided)** | $2 \sum_{k=0}^{10} \binom{47}{k} (0.5)^{47}$ | $k = 10, N = 47$ | $p = \mathbf{0.000098}$ ($9.8 \times 10^{-5}$) | **Statistically Significant** ($p < 0.0001$) |
| **Uncorrected Asymptotic** | $\chi^2 = \frac{(n_{10} - n_{01})^2}{n_{10} + n_{01}} = \frac{27^2}{47} = \frac{729}{47}$ | $\chi^2 = \mathbf{15.5106}$ | $p = \mathbf{0.000082}$ ($8.2 \times 10^{-5}$) | **Statistically Significant** ($p < 0.0001$) |

The primary reporting convention for Stage 8.9.56 and Stage 8.9.56.1 is the **Edwards continuity-corrected McNemar test** ($\chi^2 = 14.3830, p = 0.00015$).

---

## 6. Summary of Protocol Corrections

1. Retract all prose assertions of "FPR parity".
2. Maintain exact phrase: *"No statistically significant hard-negative FPR difference was established."*
3. Retain the verified $+17.33\%$ recall superiority and $+12.80\%$ F1 superiority with their source-group cluster bootstrap confidence intervals.
4. Unambiguously label the Edwards continuity-corrected McNemar test.

