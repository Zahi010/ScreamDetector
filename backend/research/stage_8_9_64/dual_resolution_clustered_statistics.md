# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Source-Group Clustered Statistical Analysis — Stage 8.9.64

**Stage Designation:** STAGE 8.9.64  
**Date:** November 12, 2026  
**Harness Script:** `backend/research/stage_8_9_64/scripts/calculate_clustered_confidence_intervals.py`  
**Dataset Population:** 312 recordings across 258 unique source groups  
**Bootstrap Parameters:** 2,000 paired cluster bootstrap iterations, random seed = 42  
**Status:** COMPLETE — CLUSTERED BOUNDS FORMALLY QUANTIFIED  

---

## 1. Executive Summary

A critical vulnerability of prior evaluation methodologies was treating recordings as independent identically distributed (i.i.d.) observations. In reality, multiple recordings often originate from the same acoustic session, recording uploader, or sound environment.

In Stage 8.9.64, statistical confidence intervals were recomputed using **source-group clustered bootstrapping** (2,000 iterations over 258 clusters) alongside classical Wilson score intervals.

### Primary Statistical Takeaways
1. **Gate 4 Robustness Across Clusters:** Short-scream recall (< 1.0s) has a point estimate of **$98.50\%$** with a 95% clustered bootstrap interval of **$[96.03\%, 100.00\%]$**. Even the conservative lower confidence bound comfortably clears the $\ge 90.00\%$ Gate 4 threshold.
2. **Ultra-Short Recall:** The 51 recordings $\le 0.50$ seconds achieved **$100.00\%$ recall** across all clusters (Wilson interval: $[93.00\%, 100.00\%]$, Bootstrap interval: $[100.00\%, 100.00\%]$).
3. **Gate 1 Deficit:** Overall recall point estimate is **$94.36\%$** with clustered bootstrap interval **$[90.86\%, 97.40\%]$**. Because the lower bound is below $96.00\%$, Gate 1 cannot be statistically claimed as passed.
4. **Gate 2 Selectivity Failure:** Hard-negative FPR point estimate is **$21.37\%$** (Wilson: $[14.91\%, 29.64\%]$, Cluster Bootstrap: $[14.06\%, 28.97\%]$), decisively failing Gate 2 ($\le 5.00\%$).
5. **Source-Group Failure Distribution:** Across all 258 source groups, only $35$ groups ($13.6\%$) exhibited errors ($11$ groups had false negatives, $24$ groups had false positives).

Full numerical ledgers are recorded in `dual_resolution_clustered_metrics.csv` and `source_group_performance.csv`.

---

## 2. Comprehensive Clustered Confidence Interval Ledger

| Metric Name | Point Estimate | Sample Size | Unclustered Wilson 95% CI | Source-Group Clustered Boot 95% CI | Mandatory Gate Threshold | Statistical Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Gate 1: Overall Recall** | 94.36% (184/195) | 195 | [90.18%, 96.82%] | **[90.86%, 97.40%]** | $\ge 96.00\%$ | **FAIL (Lower bound < 96%)** |
| **Gate 4: Short Recall (<1.0s)** | 98.50% (131/133) | 133 | [94.68%, 99.59%] | **[96.03%, 100.00%]** | $\ge 90.00\%$ | **PASS (Lower bound > 90%)** |
| **Diagnostic: Ultra-Short ($\le 0.50$s)**| 100.00% (51/51) | 51 | [93.00%, 100.00%] | **[100.00%, 100.00%]** | N/A (Diagnostic) | **100% Generalization** |
| **Diagnostic: Sustained ($\ge 1.0$s)** | 85.48% (53/62) | 62 | [74.66%, 92.17%] | **[76.00%, 93.48%]** | N/A (Diagnostic) | **Diagnostic Baseline** |
| **Gate 2: Hard-Negative FPR** | 21.37% (25/117) | 117 | [14.91%, 29.64%] | **[14.06%, 28.97%]** | $\le 5.00\%$ | **FAIL (Entire CI > 5.0%)** |

---

## 3. Methodology & Bootstrap Specification

- **Cluster Unit:** `source_group_id` ($N_{\text{clusters}} = 258$).
- **Resampling Procedure:** In each bootstrap iteration, 258 source groups were drawn with replacement. All recordings belonging to the selected groups were assembled into the bootstrap pseudo-sample.
- **Iterations:** 2,000 paired replicates.
- **Random Seed:** Fixed to 42 for exact reproducibility.
- **Mixed-Label Groups:** For source groups containing both positive and negative recordings, the paired group structure was strictly preserved during sampling to capture realistic label covariance.
- **Interval Construction:** Percentile method: $[2.5\text{th percentile}, 97.5\text{th percentile}]$.

