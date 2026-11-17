# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.62 — Statistical Discrepancy Log & Methodological Corrections

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary

This forensic log documents methodological discrepancies and reporting conflations identified in the Stage 8.9.61 statistical analysis (`statistical_analysis_report.md` and `candidate_paired_comparisons.csv`).

While the underlying raw predictions in `sealed_cohort_predictions.csv` and point-estimate percentages were reproduced with 100% fidelity, the inferential test procedures in Stage 8.9.61 contained three significant methodological weaknesses:
1. **Population Conflation in McNemar Contingency Testing:** Stage 8.9.61 computed McNemar contingency tables across all 700 recordings (overall classification accuracy) but tabulated them alongside class-specific recall bootstrap deltas, leading readers to interpret overall accuracy discordant counts ($b, c$) as scream-recall discordant counts.
2. **Omission of Paired Specificity / FPR Hypothesis Tests:** Stage 8.9.61 did not execute separate paired McNemar tests on the negative partition ($N=500$), omitting the critical finding that Candidate E1 Static has a statistically significantly higher false alarm rate than Candidate B Baseline ($p = 0.0241$).
3. **Absence of Multiple-Testing Correction:** Multiple pairwise hypotheses were evaluated without family-wise or False Discovery Rate (FDR) adjustments.

---

## 2. Discrepancy Audit Items

### Item 1: Conflation of Overall Accuracy Discordance with Recall Discordance

- **Original Stage 8.9.61 Reporting:**
  In `candidate_paired_comparisons.csv`, Stage 8.9.61 reported:
  - *Comparison:* `Candidate_E1_Static_C5` vs `Candidate_B_Baseline`
  - *Reported McNemar:* $b = 32, c = 48, \chi^2 = 2.8125, p = 0.093533$
  - *Adjacent Metric:* `bootstrap_recall_delta_pct = +0.42%`
- **Methodological Flaw:**
  The counts $b=32$ and $c=48$ represent recordings across all 700 files where Model 1 was correct and Model 2 was wrong. They are **not** recall discordant counts.
- **Audited Mathematical Correction:**
  When paired McNemar testing is restricted strictly to the positive scream population ($N=200$):
  - $b$ (E1 detects, B misses): **15**
  - $c$ (E1 misses, B detects): **14**
  - Both detect: 101; Both miss: 70
  - Paired Recall Difference: **$+0.50\%$** (116 vs 115)
  - Continuity-corrected $\chi^2$: **0.0000**
  - Exact Two-Tailed Binomial $p$-value: **1.000000**
- **Impact Assessment:**
  The true recall difference on screams between Static E1 and Candidate B is even smaller than suggested by the overall test ($p = 1.0000$ vs $p = 0.0935$). Their static scream detection capability is completely identical.

---

### Item 2: Failure to Test False-Positive Discordance on Negative Recordings

- **Original Stage 8.9.61 Reporting:**
  Stage 8.9.61 reported bootstrap confidence intervals for FPR differences, but provided zero hypothesis tests or $p$-values evaluating paired false alarm rates on the 500 hard-negative recordings.
- **Audited Mathematical Correction:**
  Evaluating paired false positives on the negative class ($N=500$):
  - *Static E1 vs Candidate B Baseline:*
    - Both FP: 62; Both TN: 387
    - $b$ (Static E1 FP, Candidate B TN): **34**
    - $c$ (Static E1 TN, Candidate B FP): **17**
    - FPR Difference: **$+3.40\%$** (19.20% vs 15.80%)
    - Continuity-corrected $\chi^2$: **5.0196** ($p = 0.0251$)
    - Exact Two-Tailed Binomial $p$-value: **0.024093** (Statistically Significant at $\alpha=0.05$)
  - *Rolling E1 vs Static E1:*
    - $b$ (Rolling FP, Static TN): **87**
    - $c$ (Rolling TN, Static FP): **6**
    - FPR Difference: **$+16.20\%$** (35.40% vs 19.20%)
    - Exact Binomial $p$-value: **$< 10^{-15}$** (Statistically Significant)
- **Impact Assessment:**
  This proves a key forensic finding: Candidate E1's static representation does not merely tie Candidate B on recall; it has a **statistically significant higher false positive rate ($p = 0.0241$)**. Candidate B remains the superior baseline for distractor suppression.

---

### Item 3: Directional Reversal in Rolling vs Static Comparison

- **Original Stage 8.9.61 Reporting:**
  In Stage 8.9.61, the paired table listed `Candidate_E1_Rolling_C5_EMA` vs `Candidate_E1_Static_C5` with $b = 32, c = 89, \chi^2 = 25.9174, p < 10^{-6}$.
- **Methodological Flaw:**
  Because this test evaluated overall correctness ($N=700$), $c=89$ represented Static E1 being correct while Rolling E1 was wrong (driven by Rolling E1's 87 excess false positives). Because this was listed alongside recall delta, it was easily misinterpreted as Rolling E1 having 89 gains over Static E1.
- **Audited Mathematical Correction:**
  When isolated by class:
  - On Screams ($N=200$): Rolling E1 is superior with **$b=26$ gains** vs **$c=2$ losses** (Exact Binomial $p = 0.000003$).
  - On Negatives ($N=500$): Static E1 is superior with **$b=6$ gains** vs **$c=87$ losses** for Rolling E1 (Exact Binomial $p < 10^{-15}$).
  - On Overall Correctness ($N=700$): Static E1 has higher overall accuracy ($74.29\%$ vs $66.14\%$, $\Delta = -8.14\%$, $p < 10^{-6}$).

---

### Item 4: Application of False Discovery Rate (FDR) Multiple-Testing Correction

- When Benjamini-Hochberg correction ($q=0.05$) is applied across all 13 hypothesis tests (4 recall tests, 5 FPR tests, 4 overall accuracy tests):
  - All primary conclusions remain robust.
  - The marginal difference in overall accuracy between Static E1 and Candidate B + Intervention D (raw $p = 0.039854$) shifts to an adjusted $p = 0.051810$, falling just outside the $\alpha=0.05$ threshold.

---

## 3. Corrected Statistical Summary Table

| Evaluation Domain | Comparison Pair | Correct Denominator | Discrepancy / Discordant Counts ($b / c$) | Exact Binomial $p$-value | Benjamini-Hochberg Adjusted $p$ | Significant ($q=0.05$) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Scream Recall** | Rolling E1 vs Static E1 | Positives ($N=200$) | $b=26, c=2$ | $0.000003$ | $0.000006$ | **YES** |
| **Scream Recall** | Rolling E1 vs Candidate B | Positives ($N=200$) | $b=31, c=6$ | $0.000041$ | $0.000067$ | **YES** |
| **Scream Recall** | Static E1 vs Candidate B | Positives ($N=200$) | $b=15, c=14$ | $1.000000$ | $1.000000$ | **NO** |
| **Scream Recall** | Rolling E1 vs Candidate B + D | Positives ($N=200$) | $b=32, c=6$ | $0.000024$ | $0.000045$ | **YES** |
| **Hard-Negative FPR** | Rolling E1 vs Static E1 | Negatives ($N=500$) | $b=87, c=6$ | $< 10^{-15}$ | $< 10^{-15}$ | **YES** |
| **Hard-Negative FPR** | Rolling E1 vs Candidate B | Negatives ($N=500$) | $b=104, c=6$ | $< 10^{-15}$ | $< 10^{-15}$ | **YES** |
| **Hard-Negative FPR** | Rolling E1 vs Candidate B + D | Negatives ($N=500$) | $b=109, c=6$ | $< 10^{-15}$ | $< 10^{-15}$ | **YES** |
| **Hard-Negative FPR** | Candidate B vs Candidate B + D | Negatives ($N=500$) | $b=5, c=0$ | $0.062500$ | $0.073864$ | **NO** |
| **Hard-Negative FPR** | Static E1 vs Candidate B | Negatives ($N=500$) | $b=34, c=17$ | $0.024093$ | $0.034801$ | **YES** |
| **Overall Accuracy** | Static E1 vs Candidate B | All ($N=700$) | $b=32, c=48$ | $0.092912$ | $0.100655$ | **NO** |
| **Overall Accuracy** | Rolling E1 vs Candidate B | All ($N=700$) | $b=37, c=110$ | $< 10^{-7}$ | $< 10^{-7}$ | **YES** |
| **Overall Accuracy** | Static E1 vs Candidate B + D | All ($N=700$) | $b=33, c=53$ | $0.039854$ | $0.051810$ | **NO** |
| **Overall Accuracy** | Rolling E1 vs Static E1 | All ($N=700$) | $b=32, c=89$ | $< 10^{-6}$ | $< 10^{-6}$ | **YES** |

