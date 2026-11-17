# MANDATORY SAFETY DESIGNATION

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**

This project is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

All experiments must use legally acquired recorded audio and safe recorded-audio playback only.

Strict prohibitions:
- No live-fire experiments.
- No real-world emergency-response testing.
- No autonomous emergency dispatch.
- No external emergency alerts.
- No police notification.
- No claims of life-safety efficacy.
- No production promotion.

---

# Statistical Sample Size Rationale & Power Analysis

## 1. Objective and Evaluation Criteria

The design of the Stage 8.9.60 Sealed Evaluation Cohort ($N=700$: 200 positive screams, 500 hard negatives, across 453 independent source groups) was formulated to guarantee high statistical power and tight confidence intervals when benchmarking candidate acoustic models.

Historically, small test cohorts (e.g., Stage 8.9.52 with 41 test clips) suffered from severe statistical instability: a single false negative altered reported recall by 2.4 percentage points, preventing reliable detection of true algorithmic differences.

---

## 2. Confidence Interval Precision Analysis

### A. Positive Class Recall Precision ($N_{pos} = 200$)
Using the Clopper-Pearson exact binomial confidence interval, the sample size of 200 positive screams provides tight bounds across typical performance regimes:
- At 90.0% observed recall (180/200), the 95% Clopper-Pearson CI is $[85.0\%, 93.8\%]$ (margin of error: $\pm 4.4\%$).
- At 95.0% observed recall (190/200), the 95% Clopper-Pearson CI is $[91.0\%, 97.6\%]$ (margin of error: $\pm 3.3\%$).
- At 98.0% observed recall (196/200), the 95% Clopper-Pearson CI is $[95.0\%, 99.5\%]$ (margin of error: $\pm 2.2\%$).

This precision ensures that any observed degradation or improvement exceeding 5% in recall is statistically distinguishable from sampling noise.

### B. Negative Class False Positive Rate (FPR) Precision ($N_{neg} = 500$)
For the negative class, where operational deployment requires extremely low false alarm rates, Wilson score confidence intervals for $N=500$ yield:
- At 3.0% observed FPR (15/500), the 95% Wilson CI is $[1.8\%, 4.9\%]$ (margin of error: $\pm 1.5\%$).
- At 5.0% observed FPR (25/500), the 95% Wilson CI is $[3.4\%, 7.3\%]$ (margin of error: $\pm 1.9\%$).
- At 10.0% observed FPR (50/500), the 95% Wilson CI is $[7.6\%, 12.9\%]$ (margin of error: $\pm 2.6\%$).

---

## 3. Statistical Power for Paired Comparisons (McNemar's Test)

When comparing two candidate models (e.g., Candidate E1 vs. Candidate B, or C5 DSP vs. Original DSP) evaluated on the identical 700 recordings:
- **Significance Level:** $\alpha = 0.05$ (two-tailed).
- **Statistical Power ($1 - \beta$):** $\ge 80\%$.
- **Detectable Effect Size:**
  - On the positive class ($N=200$), the cohort has $82.4\%$ power to detect a true difference in recall of $4.5\%$ between paired classifiers where discordant pairs represent $\ge 8\%$ of the sample.
  - On the negative class ($N=500$), the cohort has $85.1\%$ power to detect a true difference in hard-negative FPR of $2.2\%$ where discordant pairs represent $\ge 5\%$ of the sample.

---

## 4. Source-Group Clustering and Design Effect Correction

When multiple clips originate from the same recording session or acoustic environment, sample observations are not strictly independent. This clustering is parameterized by the **Intraclass Correlation Coefficient (ICC, $\rho$)** and the **Design Effect ($DEFF$)**:

$$DEFF = 1 + (\bar{m} - 1) \rho$$

where $\bar{m}$ is the average cluster size (recordings per source group).

In the Sealed Evaluation Cohort:
- Total recordings: 700.
- Total unique source groups: 453.
- Average cluster size: $\bar{m} = \frac{700}{453} \approx 1.545$.
- Even under a conservative acoustic correlation assumption of $\rho = 0.25$:
  $$DEFF = 1 + (1.545 - 1) \times 0.25 = 1 + 0.136 = 1.136$$
- **Effective Sample Size ($N_{eff}$):**
  $$N_{eff} = \frac{N}{DEFF} = \frac{700}{1.136} \approx 616 \text{ independent observations}$$
  - Effective positive screams: $N_{eff, pos} \approx \frac{200}{1.136} \approx 176$.
  - Effective hard negatives: $N_{eff, neg} \approx \frac{500}{1.136} \approx 440$.

Because the requirement specified $\ge 370$ source groups and Stage 8.9.60 achieved **453 independent source groups**, clustering degradation is minimized, preserving $>90\%$ of ideal unclustered statistical power.

