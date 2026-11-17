# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.62 — Statistical Forensic Audit: Corrected Paired Tests, Clustered Bootstraps & Multiple Testing Adjustments

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary

This report delivers the comprehensive statistical forensic audit of the Stage 8.9.61 independent evaluation. The audit examined every record in the 2,800-prediction evaluation log across four frozen models:
1. `Candidate_E1_Static_C5` (1.0s static center, $\theta=0.6800$)
2. `Candidate_B_Baseline` (1.0s static center, $\theta=0.8000$)
3. `Candidate_B_Intervention_D` (1.0s static center, $\theta=0.8000$ + Whistle Discriminator)
4. `Candidate_E1_Rolling_C5_EMA` (500 ms hop, $\alpha=0.50, \theta=0.6000$)

The audit resolved three key methodological ambiguities in Stage 8.9.61:
- **Class-Conditional Paired Testing:** Separate paired McNemar contingency tables were constructed for screams ($N=200$) to evaluate recall, and for hard negatives ($N=500$) to evaluate false positive rates, eliminating the previous conflation of overall classification discordance with class-specific error rates.
- **Clustered Bootstrap Resampling:** 2,000 paired source-group clustered resamples were computed across 453 clusters, accounting for intra-cluster acoustic correlation.
- **False Discovery Rate (FDR) Control:** The Benjamini-Hochberg procedure ($q=0.05$) was applied across all 13 evaluated hypothesis tests.

### Primary Forensic Conclusions:
1. **Scream Recall:** Rolling E1 provides a statistically significant recall advantage over Static E1 ($+12.00\%$, adj $p = 0.000006$) and Candidate B Baseline ($+12.50\%$, adj $p = 0.000067$). Static E1 and Candidate B have completely identical recall on screams ($+0.50\%$, adj $p = 1.000000$).
2. **Hard-Negative FPR:** Rolling E1 suffers a massive, statistically significant false-positive inflation ($+16.20\%$ over Static E1, $+19.60\%$ over Candidate B, both adj $p < 10^{-15}$). Furthermore, Static E1 has a statistically significant higher FPR than Candidate B ($+3.40\%$, adj $p = 0.0348$), establishing Candidate B as the superior baseline for noise rejection.
3. **Overall Accuracy:** Due to excessive false positives, Rolling E1 has statistically significantly lower overall classification accuracy than Candidate B ($-10.43\%$, adj $p < 10^{-7}$) and Static E1 ($-8.14\%$, adj $p < 10^{-6}$).

---

## 2. Methodology & Population Isolation

To prevent statistical contamination:
- **Recall Analysis:** Evaluates $H_0: \text{Recall}_1 = \text{Recall}_2$ using strictly the $N=200$ positive scream recordings. Discordant pairs $b$ (Model 1 detects, Model 2 misses) and $c$ (Model 1 misses, Model 2 detects) are tested via two-tailed exact binomial tests and continuity-corrected $\chi^2$.
- **False Positive Rate Analysis:** Evaluates $H_0: \text{FPR}_1 = \text{FPR}_2$ using strictly the $N=500$ hard-negative recordings. Discordant pairs $b$ (Model 1 FP, Model 2 TN) and $c$ (Model 1 TN, Model 2 FP) are tested via two-tailed exact binomial tests.
- **Overall Accuracy Analysis:** Evaluates $H_0: \text{Accuracy}_1 = \text{Accuracy}_2$ using all $N=700$ recordings where $b$ (Model 1 correct, Model 2 wrong) and $c$ (Model 1 wrong, Model 2 correct).
- **Cluster Bootstrap:** Resamples $K=453$ source groups with replacement, assembling all associated audio files, computing paired deltas, and deriving empirical 95% percentiles ($[P_{2.5}, P_{97.5}]$).
- **Multiple Comparisons:** Benjamini-Hochberg adjustment applied across all 13 hypothesis tests at $q=0.05$.

---

## 3. Audited Paired Comparison Results

### 3.1 Paired Recall Comparisons (Positives Only, $N=200$)

| Candidate 1 vs Candidate 2 | Both Detect | $b$ (C1 Detect, C2 Miss) | $c$ (C1 Miss, C2 Detect) | Both Miss | Recall Delta [95% CI] | Exact Binomial $p$ | BH Adjusted $p$ | Significant ($q=0.05$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Rolling E1 vs Static E1** | 114 | **26** | **2** | 58 | **+12.00% [+7.09%, +16.91%]** | $0.000003$ | $0.000006$ | **YES** |
| **Rolling E1 vs Candidate B** | 109 | **31** | **6** | 54 | **+12.50% [+6.80%, +18.20%]** | $0.000041$ | $0.000067$ | **YES** |
| **Static E1 vs Candidate B** | 101 | **15** | **14** | 70 | **+0.50% [-4.78%, +5.78%]** | $1.000000$ | $1.000000$ | **NO** |
| **Rolling E1 vs Candidate B + D**| 108 | **32** | **6** | 54 | **+13.00% [+7.23%, +18.77%]** | $0.000024$ | $0.000045$ | **YES** |

### 3.2 Paired Hard-Negative FPR Comparisons (Negatives Only, $N=500$)

| Candidate 1 vs Candidate 2 | Both FP | $b$ (C1 FP, C2 TN) | $c$ (C1 TN, C2 FP) | Both TN | FPR Delta [95% CI] | Exact Binomial $p$ | BH Adjusted $p$ | Significant ($q=0.05$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Rolling E1 vs Static E1** | 90 | **87** | **6** | 317 | **+16.20% [+12.70%, +19.70%]**| $< 10^{-15}$ | $< 10^{-15}$ | **YES** |
| **Rolling E1 vs Candidate B** | 73 | **104** | **6** | 317 | **+19.60% [+15.86%, +23.34%]**| $< 10^{-15}$ | $< 10^{-15}$ | **YES** |
| **Rolling E1 vs Candidate B + D**| 68 | **109** | **6** | 317 | **+20.60% [+16.80%, +24.40%]**| $< 10^{-15}$ | $< 10^{-15}$ | **YES** |
| **Candidate B vs Candidate B + D**| 74 | **5** | **0** | 421 | **+1.00% [+0.13%, +1.87%]** | $0.062500$ | $0.073864$ | **NO** |
| **Static E1 vs Candidate B** | 62 | **34** | **17** | 387 | **+3.40% [+0.62%, +6.18%]** | $0.024093$ | $0.034801$ | **YES** |

### 3.3 Overall Classification Accuracy Comparisons (All Files, $N=700$)

| Candidate 1 vs Candidate 2 | Both Correct | $b$ (C1 Right, C2 Wrong) | $c$ (C1 Wrong, C2 Right) | Both Wrong | Accuracy Delta [95% CI] | Exact Binomial $p$ | BH Adjusted $p$ | Significant ($q=0.05$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Static E1 vs Candidate B** | 488 | **32** | **48** | 132 | **-2.29% [-4.78%, +0.21%]** | $0.092912$ | $0.100655$ | **NO** |
| **Rolling E1 vs Candidate B** | 426 | **37** | **110** | 127 | **-10.43% [-13.73%, -7.12%]**| $< 10^{-7}$ | $< 10^{-7}$ | **YES** |
| **Static E1 vs Candidate B + D**| 487 | **33** | **53** | 127 | **-2.86% [-5.45%, -0.27%]** | $0.039854$ | $0.051810$ | **NO** |
| **Rolling E1 vs Static E1** | 431 | **32** | **89** | 148 | **-8.14% [-11.16%, -5.12%]**| $< 10^{-6}$ | $< 10^{-6}$ | **YES** |

---

## 4. Source-Group Clustered Bootstrap Verification (2,000 Iterations)

The clustered bootstrap accounted for intra-session correlation across 453 clusters:

| Paired Comparison | Metric Delta Type | Point Delta (%) | Clustered Mean Delta (%) | Clustered 95% Percentile CI |
| :--- | :--- | :---: | :---: | :---: |
| **Rolling E1 vs Static E1** | Scream Recall | +12.00% | +11.95% | [+7.11%, +16.93%] |
| | Hard-Negative FPR | +16.20% | +16.30% | [+12.65%, +20.44%] |
| | Overall Accuracy | -8.14% | -8.08% | [-11.26%, -4.60%] |
| | F1 Score | -2.15% | -2.12% | [-6.23%, +2.22%] |
| **Rolling E1 vs Candidate B** | Scream Recall | +12.50% | +12.42% | [+6.45%, +18.38%] |
| | Hard-Negative FPR | +19.60% | +19.67% | [+16.20%, +23.39%] |
| | Overall Accuracy | -10.43% | -10.35% | [-13.57%, -6.50%] |
| | F1 Score | -4.22% | -4.21% | [-9.16%, +0.84%] |
| **Static E1 vs Candidate B** | Scream Recall | +0.50% | +0.47% | [-4.55%, +5.80%] |
| | Hard-Negative FPR | +3.40% | +3.37% | [+0.24%, +6.70%] |
| | Overall Accuracy | -2.29% | -2.27% | [-5.01%, +0.52%] |
| | F1 Score | -2.07% | -2.09% | [-6.47%, +2.22%] |

---

## 5. Audit Conclusions and Recommendations

1. **Static Model Parity on Screams:** The audit conclusively confirms that Candidate E1 provides zero recall gain over Candidate B when evaluated statically ($+0.50\%$, Exact $p = 1.000000$).
2. **E1 Specificity Defect:** Candidate E1 Static has a statistically significantly higher false alarm rate ($+3.40\%$, adj $p = 0.0348$) than Candidate B. Candidate B has superior background noise suppression.
3. **Temporal Trade-Off Invariance:** Rolling aggregation yields a consistent $+12\%$ recall boost on screams, but incurs a $+16\%$ to $+20\%$ false-positive penalty, causing a net $-8\%$ to $-10\%$ drop in overall accuracy.
4. **Recommendation for Evaluation Protocol:** Future stages must maintain strictly partitioned contingency reporting: never present overall classification discordance as evidence of scream recall.

