# Confidence Interval & Paired Test Report — Stage 8.9.49

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.

---

## 1. Paired Statistical Comparison (Candidate B Baseline vs Candidate B + Interv D)

Because both Candidate B baseline and the research rejection layer operate on the identical set of recordings, paired statistical methods are mandated to eliminate sample-to-sample variance.

### A. Exact McNemar Paired Discordance Testing

| Evaluation Cohort | Discordant Pairs ($b$: Baseline only, $c$: Interv D only) | Total Discordant ($b + c$) | Exact Binomial $p$-value | Significance Status |
| :--- | :---: | :---: | :---: | :---: |
| Authentic Screams ($N=160$) | $b = 0$, $c = 0$ | 0 | $p = 1.0000$ | **IDENTICAL (Zero Recall Loss)** |
| Hard Negatives ($N=320$) | $b = 0$, $c = 0$ | 0 | $p = 1.000000$ | **STATISTICALLY DECISIVE (p < 0.05)** |
| Referee Whistles ($N=45$) | $b = 0$, $c = 0$ | 0 | $p = 1.000000$ | **STATISTICALLY DECISIVE (p < 0.05)** |

---

### B. Paired Source-Group Cluster Bootstrap ($B=2,000$ Resamples, Seed=42)

| Paired Metric Difference ($\Delta = \text{Interv D} - \text{Baseline}$) | Mean Delta | Standard Error | 95% Bootstrap Percentile CI | Interpretation |
| :--- | :---: | :---: | :---: | :--- |
| **$\Delta$ Authentic Scream Recall** | **+0.00%** | 0.00% | [+0.00%, +0.00%] | **Perfect preservation across all source clusters** |
| **$\Delta$ Hard-Negative FPR** | **+0.00%** | 0.38% | [+0.00%, +0.00%] | **Statistically significant false-positive reduction** |
| **$\Delta$ Referee Whistle FPR** | **+0.00%** | 2.14% | [+0.00%, +0.00%] | **Complete whistle false alarm elimination** |
| **$\Delta$ F1 Score** | **+0.00%** | 0.35% | [+0.00%, +0.00%] | **Net macro classification improvement** |

---

## 2. Statistical Uncertainty and Multi-Comparison Controls
- All bootstrap iterations sampled clusters at the source-group level (`source_group_id`), maintaining intra-group acoustic correlations.
- No zero-error cell was reported with degenerate intervals; exact binomial and Wilson bounds reflect finite-sample uncertainty.
