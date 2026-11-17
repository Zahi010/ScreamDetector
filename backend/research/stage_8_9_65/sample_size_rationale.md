# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Sample Size Rationale & Statistical Power Report for Planned $N=1,050$ Independent Evaluation

## 1. Executive Summary

This report delivers the rigorous sample size justification and statistical power analysis for a planned, independent sealed evaluation cohort of $N = 1,050$ recordings ($N_{\text{pos}} = 550$, $N_{\text{neg}} = 500$).

The power calculations formally incorporate **cluster design effects** ($D_{\text{eff}} = 1 + (\bar{m} - 1)\rho$) based on empirical intra-cluster correlations observed across development source groups ($\rho \in [0.04, 0.06]$), demonstrating that the planned cohort achieves **$> 92\%$ statistical power** across all four primary classification gates at significance level $\alpha = 0.05$.

---

## 2. Statistical Power Summary Table

| Evaluation Gate Target | Nominal $N$ | Mean Cluster Size ($\bar{m}$) | ICC ($\rho$) | Design Effect ($D_{\text{eff}}$) | Effective $N$ ($N_{\text{eff}}$) | Null Benchmark ($H_0$) | Target Performance ($H_1$) | Statistical Power ($1 - \beta$) | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Gate 1: Overall Recall** | 550 | 1.35 | 0.06 | 1.021 | 538.7 | $93.0\%$ | $96.0\%$ | **92.10%** | Adequately Powered ($> 90\%$) |
| **Gate 2: Hard-Negative FPR** | 500 | 1.15 | 0.04 | 1.006 | 497.0 | $7.5\%$ | $4.0\%$ | **96.17%** | Adequately Powered ($> 90\%$) |
| **Gate 3: Shouted-Speech FPR** | 120 | 1.20 | 0.05 | 1.010 | 118.8 | $20.0\%$ | $10.0\%$ | **92.51%** | Adequately Powered ($> 90\%$) |
| **Gate 4: Short-Scream Recall** | 350 | 1.30 | 0.06 | 1.018 | 343.8 | $90.0\%$ | $96.0\%$ | **99.92%** | Decisively Powered ($> 99\%$) |

---

## 3. Cohort Composition & Stratification Plan

To guarantee robust coverage of high-risk acoustic edge cases, the $N=1,050$ independent cohort is partitioned into six orthogonal sub-cohorts:

### 3.1 Positive Scream Cohort ($N_{\text{pos}} = 550$)
1. **Ultra-Short Screams ($\le 500$ ms):** $N = 150$ recordings across $\ge 100$ unique uploaders. Validates 250ms short-branch transient capture.
2. **Short Screams ($500\text{--}1000$ ms):** $N = 200$ recordings across $\ge 140$ unique uploaders. Validates the boundary zone where Variant 6 previously failed.
3. **Sustained Screams ($\ge 1.00$ s):** $N = 200$ recordings across $\ge 120$ unique uploaders. Validates 1,000ms sustained-branch integration and multi-phrase cries.

### 3.2 Negative Noise Cohort ($N_{\text{neg}} = 500$)
1. **Vocal Outcries & Shouted Speech (Gate 3 Diagnostic):** $N = 120$ recordings across $\ge 80$ speakers. Provides the definitive statistical test for Gate 3 ($\text{FPR} \le 15.0\%$).
2. **Mechanical & Athletic Whistles:** $N = 150$ recordings across $\ge 100$ sources. Validates narrow-band tonal rejection.
3. **Friction Squeaks & Creaks:** $N = 100$ recordings. Tests high-frequency metal-on-metal non-vocal transients.
4. **Ambient Festival Soundscapes:** $N = 130$ recordings. Tests complex crowd noise, amplified music basslines, and carnival machinery.

---

## 4. Methodological Defense Against Statistical Leakage

1. **Source Group Quarantine:** Every recording in the independent cohort must originate from a `source_group_id` that has never appeared in any training, validation, or development partition across Stages 1 through 65.
2. **Pre-Registered Checksum Locking:** The SHA-256 hash of the complete manifest must be published before running any model inference.
3. **Zero Dynamic Retraining:** All candidate architectures evaluated against the independent cohort must be evaluated in a strictly frozen, read-only state.

---

## 5. Artifact Links
- Power Analysis CSV: [future_evaluation_power_analysis.csv](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/future_evaluation_power_analysis.csv)
- Pre-Registration Plan: [future_evaluation_preregistration_plan.md](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/future_evaluation_preregistration_plan.md)

