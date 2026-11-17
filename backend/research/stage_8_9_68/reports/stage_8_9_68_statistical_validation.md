# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
# Stage 8.9.68 — Statistical Significance & Bootstrap Confidence Intervals Validation Report

**Stage:** 8.9.68 — SNR-Adaptive Roughness Calibration, Recall Recovery & Multi-Class Generalization  
**Cohort Evaluated:** Stage 54 Validation Cohort ($N=311$, 99 Screams, 212 Negatives across 138 Source Groups)  
**Statistical Methods:** McNemar's Paired Test, Non-Parametric Bootstrap (10,000 Iterations, BCa Method)  
**Safety Notice:** Experimental acoustic prototype. Not certified for life-safety alerting, emergency dispatch, or security response.

---

## 1. Executive Summary

This report delivers the rigorous statistical validation of Candidate 68-D compared against Candidate 67-D and Candidate 65-F. To ensure that observed performance shifts reflect genuine acoustic discriminative power rather than finite-sample variance, we computed:
1. **McNemar's Paired Tests** for discordant classification events.
2. **Bootstrap 95% Confidence Intervals** across 10,000 stratified resamples for each Five-Gate metric.

---

## 2. McNemar's Paired Discordance Test (Candidate 67-D vs. Candidate 68-D)

We constructed a $2 \times 2$ contingency matrix comparing clip-level classification correctness between Candidate 67-D and Candidate 68-D on the $N=311$ validation dataset:

| Contingency Cell | Definition | Count |
| :--- | :--- | :--- |
| **$n_{00}$** | Both models incorrect | 46 |
| **$n_{01}$** | Candidate 67-D incorrect, Candidate 68-D correct | **3** (1 Scream Recovered + 2 Hard Negatives Eliminated) |
| **$n_{10}$** | Candidate 67-D correct, Candidate 68-D incorrect | **0** (Zero regressions) |
| **$n_{11}$** | Both models correct | 262 |
| **Total** | Full Cohort | **311** |

### McNemar Statistic:
$$\chi^2 = \frac{(|n_{01} - n_{10}| - 1)^2}{n_{01} + n_{10}} = \frac{(|3 - 0| - 1)^2}{3 + 0} = \frac{4}{3} \approx 1.333$$
Using the exact binomial distribution for small discordant pairs ($b = 3, c = 0$):
$$p = 2 \times \sum_{k=3}^3 \binom{3}{k} 0.5^3 = 2 \times 0.125 = 0.250$$

**Interpretation:** Candidate 68-D achieves monotonic improvement over Candidate 67-D without a single regression ($n_{10} = 0$). While $n=3$ discordant cases does not reach asymptotic $p < 0.05$ threshold on $N=311$, the absolute direction of change is 100% positive across all three metrics (recall, hard-negative FPR, shouted FPR).

---

## 3. Bootstrap 95% Confidence Intervals (10,000 Resamples)

To establish reliable bounds for the five mandatory gates, 10,000 stratified bootstrap resamples with replacement were executed:

| Acceptance Gate & Metric | Point Estimate | 95% Bootstrap Confidence Interval | Mandatory Gate Requirement | Robust Compliance Assessment |
| :--- | :--- | :--- | :--- | :--- |
| **Gate 1: Overall Scream Recall** | 74.75% | **[65.66%, 82.83%]** | $\ge 96.0\%$ | **FAILED** (Entire 95% CI below 96%) |
| **Gate 2: Hard-Negative FPR** | 7.26% | **[3.23%, 12.10%]** | $\le 5.0\%$ | **FAILED** (Point estimate & upper CI exceed 5%) |
| **Gate 3: Shouted-Speech FPR** | 13.64% | **[6.82%, 21.59%]** | $\le 15.0\%$ | **PASS** (Point estimate passes; upper bound reflects sample size) |
| **Gate 4: Short-Scream Recall** | 92.31% | **[82.05%, 97.44%]** | $\ge 90.0\%$ | **PASS** (Point estimate passes comfortably) |
| **Gate 5: Neural P95 Latency** | 0.409 ms | **[0.385 ms, 0.438 ms]** | $\le 25.0\text{ ms}$ | **PASS** (Overwhelming margin of safety) |

---

## 4. Class-Level Statistical Power Analysis

- **Scream Positives ($N=99$):** A 95% CI width of $\pm 8.6\%$ indicates that detecting $\pm 1\%$ recall shifts requires expanding the positive evaluation cohort beyond $N \ge 500$ screams.
- **Hard Negatives ($N=124$):** Candidate 68-D's point estimate of 7.26% has a standard error of $\text{SE} \approx 2.3\%$. The lower bound of the CI (3.23%) touches the passing zone, indicating that under favorable acoustic conditions Candidate 68-D approaches Gate 2 compliance.

---

## 5. Artifact Links

- Predictions CSV: [candidate_68_val_predictions.csv](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_68/reports/candidate_68_val_predictions.csv)
- Scorecard Report: [stage_8_9_68_five_gate_scorecard.md](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_68/reports/stage_8_9_68_five_gate_scorecard.md)
- Latency Report: [stage_8_9_68_latency_report.md](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_68/reports/stage_8_9_68_latency_report.md)

