# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Variant 6 Paired Prediction Audit Report: Baseline vs Variant 6 Full Suppression Stack

## 1. Executive Summary

This audit delivers a rigorous, sample-by-sample paired comparison between the **Baseline Dual-Resolution Model** (Stage 8.9.64 Track B reference) and **Variant 6 Full Suppression Stack** (Stage 8.9.64 Track E reference) evaluated across the identical $N=312$ development cohort ($N_{\text{pos}}=195$, $N_{\text{neg}}=117$).

The audit confirms the exact confusion matrices and quantifies the paired transition dynamics:
- **Baseline Dual-Resolution:** $TP=184$, $FN=11$, $FP=25$, $TN=92$
  - Overall Recall: $94.36\%$ (184/195)
  - Hard-Negative FPR: $21.37\%$ (25/117)
- **Variant 6 Full Stack:** $TP=171$, $FN=24$, $FP=5$, $TN=112$
  - Overall Recall: $87.69\%$ (171/195)
  - Hard-Negative FPR: $4.27\%$ (5/117)

While Variant 6 successfully achieved Gate 2 compliance ($\text{FPR} \le 5.0\%$), it introduced a severe, statistically significant recall degradation ($p = 8.74 \times 10^{-4}$ via McNemar's test), dropping 13 true positive screams below the $0.50$ decision boundary.

---

## 2. Four-Way Transition Matrices

### 2.1 Positive Screams ($N = 195$)

| Transition Category | Count | Percentage | Description |
| :--- | :---: | :---: | :--- |
| **Both Detect ($TP \to TP$)** | 171 | $87.69\%$ | Consistently detected screams across both architectures. |
| **Baseline Only ($TP \to FN$)** | 13 | $6.67\%$ | **Suppressed screams:** True screams detected by Baseline but missed by Variant 6. |
| **Variant 6 Only ($FN \to TP$)** | 0 | $0.00\%$ | No false negatives were recovered by Variant 6. |
| **Both Miss ($FN \to FN$)** | 11 | $5.64\%$ | Persistent edge-case misses common to both models. |
| **Total Positives** | **195** | **100.00%** | Denominator verified bit-for-bit. |

### 2.2 Hard Negatives ($N = 117$)

| Transition Category | Count | Percentage | Description |
| :--- | :---: | :---: | :--- |
| **Both Correct Reject ($TN \to TN$)** | 90 | $76.92\%$ | Clean rejection across both architectures. |
| **Baseline FP, V6 Correct ($FP \to TN$)** | 22 | $18.80\%$ | **Successfully suppressed non-targets:** Whistles, tone bursts, and mechanical noise. |
| **Baseline Reject, V6 FP ($TN \to FP$)** | 2 | $1.71\%$ | Novel false alarms introduced by Variant 6 hyperplane adjustments. |
| **Both False Positive ($FP \to FP$)** | 3 | $2.56\%$ | Persistent non-target false alarms (including vocal outcry negatives). |
| **Total Hard Negatives** | **117** | **100.00%** | Denominator verified bit-for-bit. |

---

## 3. Paired Statistical Hypothesis Testing

To assess whether the observed shifts in detection and false alarm rates represent statistically significant changes or random variation, two-tailed McNemar tests with continuity correction were performed on discordant pairs.

### 3.1 Recall Degradation Test (Positive Screams)
- Discordant pairs:
  - $b = \text{Baseline Detect, V6 Miss} = 13$
  - $c = \text{Baseline Miss, V6 Detect} = 0$
- McNemar test statistic with continuity correction:
  $$\chi^2 = \frac{(|b - c| - 1)^2}{b + c} = \frac{(|13 - 0| - 1)^2}{13} = \frac{144}{13} \approx 11.0769$$
- Degrees of freedom: $df = 1$
- **p-value:** $p = 8.7409 \times 10^{-4}$ ($p < 0.001$)
- **Conclusion:** Highly significant recall destruction. Variant 6 incurs a genuine, systemic loss of acoustic sensitivity.

### 3.2 Specificity Enhancement Test (Hard Negatives)
- Discordant pairs:
  - $b = \text{Baseline FP, V6 Correct Reject} = 22$
  - $c = \text{Baseline Reject, V6 FP} = 2$
- McNemar test statistic with continuity correction:
  $$\chi^2 = \frac{(|b - c| - 1)^2}{b + c} = \frac{(|22 - 2| - 1)^2}{24} = \frac{361}{24} \approx 15.0417$$
- Degrees of freedom: $df = 1$
- **p-value:** $p = 1.0516 \times 10^{-4}$ ($p < 0.001$)
- **Conclusion:** Highly significant false-alarm reduction. The suppression stack effectively eliminates transient and tonal false alarms.

---

## 4. Source-Group Cluster Distribution

The 13 suppressed positive screams originate from 7 distinct source groups:
1. `s49_sg_dev_pos_040` (3 recordings: `s60_rec_0733`, `s60_rec_0734`, `s60_rec_0732`)
2. `sg_pos_v6_029` (1 recording: `s63_short_0122`)
3. `sg_pos_v6_030` (1 recording: `s63_short_0123`)
4. `sg_pos_v6_031` (1 recording: `s63_short_0124`)
5. `sg_pos_v6_032` (1 recording: `s63_short_0125`)
6. `s49_sg_dev_pos_030` (1 recording: `s60_rec_0713`)
7. `s49_sg_dev_pos_037` (1 recording: `s60_rec_0728`)
8. `sg_s60_NIGENS_35716` (1 recording: `s60_rec_0523`)
9. `sg_s60_NIGENS_16872` (1 recording: `s60_rec_0492`)
10. `nigens_juskiddink` (1 recording: `s63_short_0002`)
11. `sg_s60_s20_336004` (1 recording: `s63_short_0132`)

The clustering confirms that suppression was not confined to a single defective source group, but impacted multiple recording cohorts sharing specific acoustic properties.

---

## 5. Artifact Links
- Paired Transition Dataset: [paired_prediction_transitions.csv](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/paired_prediction_transitions.csv)
- Positive Failure Inventory: [variant6_positive_failure_inventory.csv](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/variant6_positive_failure_inventory.csv)
- Baseline Reproduction: [baseline_reproduction.csv](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/baseline_reproduction.csv)
- Variant 6 Reproduction: [variant6_reproduction.csv](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/variant6_reproduction.csv)

