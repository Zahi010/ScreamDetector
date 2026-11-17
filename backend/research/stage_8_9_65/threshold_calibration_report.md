# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Threshold Calibration & Probability Reliability Report

## 1. Executive Summary

This report delivers a thorough empirical analysis of decision threshold tuning and probability calibration for the lead dual-resolution architecture (Candidate 65-F) evaluated on the development cohort ($N=312$).

### Primary Findings
1. **Decision Threshold Operating Frontier:**
   - **F1-Optimal Operating Point ($\tau = 0.50$):** Overall Recall = $94.36\%$, Dev FPR = $5.13\%$ ($6$ FPs), $\text{F1} = 0.9558$, $\text{Youden's } J = 0.8923$.
   - **Gate 2 Satisfying Operating Point ($\tau = 0.60$):** Overall Recall = $90.77\%$, Dev FPR = $3.42\%$ ($4$ FPs, **PASS Gate 2**), Short-Scream Recall = $95.49\%$ (**PASS Gate 4**), $\text{F1} = 0.9415$.
   - **Gate 1 Satisfying Operating Point ($\tau = 0.26$):** Overall Recall = $96.92\%$ (**PASS Gate 1**), Short-Scream Recall = $99.25\%$, Sustained Recall = $91.94\%$, but Dev FPR = $41.88\%$.
2. **Probability Calibration (Brier Score):**
   - **Uncalibrated Model:** $\text{Brier Score} = 0.0633$
   - **Platt Scaling (Logistic Calibration):** $\text{Brier Score} = 0.0579$ ($8.5\%$ reduction in calibration error)
   - **Isotonic Regression:** $\text{Brier Score} = 0.0476$ ($24.8\%$ reduction in calibration error)

---

## 2. Decision Threshold Sweep (Selected Operating Points)

| Threshold ($\tau$) | Overall Recall | Dev FPR | Shouted FPR | Short Recall | Sustained Recall | Precision | F1 Score | Youden's $J$ | Operating Characterization |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **0.26** | **96.92%** | $41.88\%$ | $100.0\%$ | $99.25\%$ | $91.94\%$ | $0.7941$ | $0.8730$ | $0.5504$ | High-Sensitivity / Gate 1 Compliant |
| **0.36** | $94.87\%$ | $12.82\%$ | $20.0\%$ | $99.25\%$ | $85.48\%$ | $0.9250$ | $0.9367$ | $0.8205$ | Relaxed Suppression Frontier |
| **0.46** | $94.36\%$ | $9.40\%$ | $20.0\%$ | $98.50\%$ | $85.48\%$ | $0.9436$ | $0.9436$ | $0.8496$ | Balanced Operation |
| **0.48** | $94.36\%$ | $5.98\%$ | $20.0\%$ | $98.50\%$ | $85.48\%$ | $0.9634$ | $0.9534$ | $0.8838$ | Candidate 65-F Baseline Operating Point |
| **0.50** | **94.36%** | **5.13%** | **20.0%** | **98.50%** | **85.48%** | **0.9684** | **0.9558** | **0.8923** | **Peak F1 Score & Youden's J** |
| **0.54** | $92.31\%$ | $5.13\%$ | $20.0\%$ | $96.24\%$ | $83.87\%$ | $0.9677$ | $0.9449$ | $0.8718$ | Strict Conservative Gating |
| **0.60** | **90.77%** | **3.42%** | **20.0%** | **95.49%** | **80.65%** | **0.9779** | **0.9415** | **0.8735** | **Gate 2 Specificity Compliant ($\le 5\%$)** |
| **0.70** | $88.21\%$ | $3.42\%$ | $20.0\%$ | $95.49\%$ | $72.58\%$ | $0.9773$ | $0.9272$ | $0.8479$ | High-Specificity Gating |

---

## 3. Probability Reliability & Calibration Analysis

### 3.1 Brier Score Assessment
The Brier score measures the mean squared difference between predicted probabilities and binary outcomes:
$$\text{Brier} = \frac{1}{N} \sum_{i=1}^N (p_i - y_i)^2$$
- Uncalibrated neural probabilities yielded a Brier score of $0.0633$, reflecting mild over-confidence on borderline false positives.
- Fitting a monotonic logistic transform (Platt scaling) corrected probability dispersion around $p=0.50$, reducing Brier score to $0.0579$.
- Non-parametric isotonic regression provided the sharpest empirical calibration ($\text{Brier} = 0.0476$), confirming high posterior reliability.

### 3.2 Operating Threshold Selection Guidance
- When operating in acoustic environments where false alarms carry substantial cost (e.g. monitored public festivals), threshold $\tau = 0.60$ is recommended, securing $\text{FPR} = 3.42\%$ while preserving $95.49\%$ short-scream recall.
- When maximum sensitivity is prioritized, threshold $\tau = 0.48\text{--}0.50$ achieves the peak F1 score of $0.9558$.

---

## 4. Artifact Links
- Threshold Sweep CSV: [threshold_calibration_sweep.csv](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/threshold_calibration_sweep.csv)
- Calibration Metrics CSV: [probability_calibration_metrics.csv](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/probability_calibration_metrics.csv)
- Selective Suppression Analysis: [selective_suppression_analysis.md](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/selective_suppression_analysis.md)

