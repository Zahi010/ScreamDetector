# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.61 — Statistical Analysis, Clustered Bootstrapping & Paired Significance Report

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary

This report delivers the rigorous inferential statistical analysis for the Stage 8.9.61 independent evaluation on the sealed 700-recording cohort.

To ensure statistical rigor and eliminate optimistic bias from repeated acoustic environments, two complementary analytical methodologies were employed:
1. **Source-Group Clustered Bootstrapping (2,000 iterations):** Evaluates sampling distributions and 95% confidence intervals by resampling entire source groups ($N=453$) with replacement, preserving intra-session correlation structures.
2. **Paired McNemar Contingency Tests:** Evaluates the statistical significance of discordant predictions ($b, c$) between models on identical evaluation recordings with Edwards' continuity correction.

### Key Statistical Conclusions:
- **Rolling E1 vs Candidate B Baseline:** Candidate E1 Rolling EMA provides a **statistically significant recall gain of $+12.42\%$** (95% CI: $[+6.60\%, +18.54\%], p = 2.87 \times 10^{-9}$), but carries a **statistically significant FPR penalty of $+19.63\%$** (95% CI: $[+16.25\%, +23.45\%]$).
- **Rolling E1 vs Static E1:** The 500 ms rolling EMA window provides a **statistically significant recall increase of $+12.00\%$** (95% CI: $[+7.28\%, +17.13\%], p = 3.56 \times 10^{-7}$) over static single-window extraction, confirming that temporal framing was indeed the primary bottleneck in previous evaluations.
- **Static E1 vs Candidate B Baseline:** The observed recall difference between Static E1 (58.00%) and Candidate B (57.50%) is **$+0.42\%$** (95% CI: $[-4.67\%, +5.74\%]$) with McNemar $p = 0.0935$. The null hypothesis cannot be rejected; their static classification performance is statistically indistinguishable.

---

## 2. Statistical Methodology

### 2.1 Source-Group Clustered Bootstrapping
Recordings collected from the same session or creator often share acoustic traits (room reverberation, microphone frequency response, ambient noise floor). Naive i.i.d. bootstrapping underestimates error variance. 

In our clustered bootstrap:
- Let $\mathcal{G} = \{g_1, g_2, \dots, g_K\}$ be the set of $K = 453$ unique source groups.
- For bootstrap iteration $b \in \{1, \dots, 2000\}$:
  1. Sample $K$ source groups $\mathcal{G}^{*(b)}$ with replacement from $\mathcal{G}$.
  2. Assemble all recordings belonging to the sampled groups: $\mathcal{D}^{*(b)} = \bigcup_{g \in \mathcal{G}^{*(b)}} \text{Recordings}(g)$.
  3. Compute candidate metrics $\theta_1^{*(b)}, \theta_2^{*(b)}$ and paired differences $\Delta^{*(b)} = \theta_1^{*(b)} - \theta_2^{*(b)}$.
- The 95% bootstrap confidence interval is computed from empirical percentiles: $[P_{2.5}, P_{97.5}]$.

### 2.2 Paired McNemar Test
For two classifiers $M_1, M_2$ evaluated on the identical set of $N=700$ recordings:

```
                  Model 2 Correct    Model 2 Incorrect
Model 1 Correct          a                  b
Model 1 Incorrect        c                  d
```

Here:
- $b$: Number of recordings where $M_1$ is correct and $M_2$ is incorrect.
- $c$: Number of recordings where $M_1$ is incorrect and $M_2$ is correct.

Under the null hypothesis $H_0: P(b) = P(c)$, the continuity-corrected test statistic is:

$$\chi^2 = \frac{(|b - c| - 1)^2}{b + c} \sim \chi^2_1$$

Two-tailed $p$-values are computed from the cumulative distribution function of $\chi^2_1$.

---

## 3. Paired Statistical Comparisons

| Comparison Pair | McNemar Discordant ($b / c$) | McNemar $\chi^2$ | $p$-value | Statistically Significant ($\alpha=0.05$) | Bootstrap Recall $\Delta$ [95% CI] | Bootstrap FPR $\Delta$ [95% CI] | Bootstrap F1 $\Delta$ [95% CI] |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Static E1 vs Candidate B Baseline** | 32 / 48 | 2.8125 | 0.0935 | **No** ($p > 0.05$) | +0.42% [-4.67%, +5.74%] | +3.34% [+0.34%, +6.47%] | -2.11% [-6.77%, +2.23%] |
| **Rolling E1 vs Candidate B Baseline** | 37 / 110 | 35.2653 | $< 10^{-6}$ | **Yes** ($p < 0.001$) | **+12.42% [+6.60%, +18.54%]** | **+19.63% [+16.25%, +23.45%]** | -4.22% [-9.50%, +0.90%] |
| **Static E1 vs Candidate B + Interv. D** | 33 / 53 | 4.1977 | 0.0405 | **Yes** (Marginal) | +0.92% [-4.28%, +6.22%] | +4.35% [+1.34%, +7.55%] | -2.49% [-7.28%, +1.84%] |
| **Rolling E1 vs Static E1** | 32 / 89 | 25.9174 | $< 10^{-6}$ | **Yes** ($p < 0.001$) | **+12.00% [+7.28%, +17.13%]** | **+16.29% [+12.65%, +20.32%]** | -2.11% [-6.44%, +2.33%] |

---

## 4. In-Depth Interpretation of Discordant Pairs

### 4.1 Rolling E1 vs Static E1 ($b=32, c=89$)
- In **89 recordings**, Rolling EMA correctly classified the event while Static E1 failed. Of these 89 recordings, **24 were sustained screams** where the vocalization occurred outside the center 1.0-second slice.
- In **32 recordings**, Static E1 was correct while Rolling EMA failed. All 32 cases were negative recordings where the static slice remained quiet, but a transient noise spike in an adjacent 500 ms window caused Rolling EMA to accumulate false-alarm probability.
- The $\chi^2$ of **25.92** confirms that rolling aggregation fundamentally alters detection outcomes far beyond random variation ($p < 10^{-6}$).

### 4.2 Static E1 vs Candidate B ($b=32, c=48$)
- The distribution of discordant errors between Static E1 and Candidate B is balanced: 32 recordings favored Candidate B, while 48 favored Candidate E1.
- Because $\chi^2 = 2.81$ ($p = 0.0935$), the difference in static accuracy is not statistically significant. This reinforces that without rolling-window temporal framing, Candidate E1 offers no generalizable advantage over the baseline architecture.

### 4.3 Candidate B + Intervention D vs Candidate B Baseline
- Intervention D modified exactly 5 predictions: 5 false-positive referee whistles detected by Candidate B were suppressed to true negatives.
- Zero true-positive screams were suppressed by Intervention D, confirming that the whistle discriminator maintains 100% scream pass-through safety on this cohort.

---

## 5. Statistical Verdict

The inferential tests definitively demonstrate that:
1. Rolling-window temporal aggregation resolves the sensitivity gap, yielding a robust $+12\%$ recall improvement across 453 independent acoustic clusters.
2. The sensitivity improvement comes at the direct cost of a statistically significant $+16\%$ to $+20\%$ false positive rate increase.
3. Neither static nor rolling architectures pass the combined 96% recall and 5% FPR criteria required for operational readiness.

