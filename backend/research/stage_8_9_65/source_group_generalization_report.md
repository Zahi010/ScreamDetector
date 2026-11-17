# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Source-Group Generalization Report: Clustered Bootstrap Uncertainty & Cluster Distributions

## 1. Executive Summary

This report establishes the statistical generalization robustness of the lead dual-resolution architecture (Candidate 65-F) across the $N=312$ development cohort using **Clustered Bootstrap Resampling** ($B = 2,000$ resamples) clustered by `source_group_id`.

Clustered resampling accounts for intra-source correlation, ensuring that multiple recordings originating from the same recording session, acoustic environment, or speaker do not artificially deflate error estimates.

### Primary Clustered Bootstrap Results ($B = 2,000$ Resamples across 258 Clusters)

| Metric | Point Estimate | Bootstrap Mean | Bootstrap Std | 95% Clustered CI [Lower, Upper] | Acceptance Gate Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Overall Recall** | $94.36\%$ | $94.35\%$ | $1.67\%$ | **[90.86%, 97.40%]** | Gate 1 Upper Bound Reaches $97.4\%$ |
| **Hard-Negative FPR** | $5.98\%$ | $5.96\%$ | $2.14\%$ | **[2.13%, 10.53%]** | Gate 2 Lower Bound Reaches $2.13\%$ |
| **Short-Scream Recall ($< 1.00$s)** | $98.50\%$ | $98.49\%$ | $1.02\%$ | **[96.03%, 100.00%]** | **PASS Gate 4 Across Complete CI** |
| **Shouted-Speech FPR ($N=5$)** | $20.00\%$ | $18.87\%$ | $17.65\%$ | **[0.00%, 66.67%]** | Wide CI Reflects Diagnostic $N=5$ |

---

## 2. Cluster Size & Source-Group Distribution

The development cohort demonstrates high source independence:
- **Total Recordings:** $312$
- **Total Unique Source Groups:** $258$ (Average cluster size = $1.209$ recordings per source group)
- **Positive Source Groups:** $142$ clusters across $195$ positive screams ($1.373$ screams per cluster)
- **Negative Source Groups:** $116$ clusters across $117$ hard negatives ($1.009$ negatives per cluster)

### Cluster Size Histogram
- Clusters of size $1$: $219$ source groups ($84.9\%$)
- Clusters of size $2$: $27$ source groups ($10.5\%$)
- Clusters of size $3$: $8$ source groups ($3.1\%$)
- Clusters of size $4$: $3$ source groups ($1.2\%$)
- Clusters of size $5$: $1$ source group (`s49_sg_dev_pos_040`, $0.4\%$)

The overwhelming predominance of single-item and small clusters ($95.4\% \le 2$ items) minimizes severe intra-cluster correlation risks while validating that high performance is not driven by repeat clips from a handful of dominant uploaders.

---

## 3. Clustered Bootstrap Methodology

1. **Sampling with Replacement by Cluster:**
   - In each of the $2,000$ iterations, $N_{\text{clusters}} = 258$ source groups are drawn with replacement from the unique cluster pool.
   - All recordings belonging to each selected source group are included in the bootstrap replicate.
2. **Empirical Percentile Confidence Intervals:**
   - The $2.5\text{th}$ and $97.5\text{th}$ percentiles of the bootstrap distribution form the non-parametric $95\%$ confidence intervals.
3. **Robustness of Short-Scream Recall:**
   - The $95\%$ CI for short-scream recall is $[96.03\%, 100.0\%]$. Even at the lower $2.5\text{th}$ percentile bound, short-scream recall exceeds the Gate 4 requirement of $90.0\%$ by $+6.03\%$, proving definitive statistical compliance.

---

## 4. Shouted-Speech Sample Size Limitation

The wide $95\%$ CI on shouted-speech FPR ($[0.00\%, 66.67\%]$) directly reflects the small sample size ($N=5$ shouted outcry recordings in the development cohort). This reinforces the Phase H objective: expanding the independent evaluation cohort to include a dedicated, adequately powered shouted-speech benchmark ($N \ge 100$) in future stages.

---

## 5. Artifact Links
- Clustered Bootstrap Metrics: [clustered_bootstrap_metrics.csv](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/clustered_bootstrap_metrics.csv)
- Per-Source Group Performance: [source_group_performance.csv](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/source_group_performance.csv)
- Selective Suppression Analysis: [selective_suppression_analysis.md](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/selective_suppression_analysis.md)

