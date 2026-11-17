# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.62 — Stage 8.9.61 Metric Reproduction & Forensic Verification

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary

As part of Track A (Phase A1) of Stage 8.9.62, this audit re-evaluated every individual prediction in the original Stage 8.9.61 evaluation log (`sealed_cohort_predictions.csv`, 2,800 total prediction rows: 700 recordings across 4 frozen candidate configurations).

All primary confusion matrix cells (TP, FN, FP, TN), subgroup performance breakdowns, and derived classification metrics were reproduced bit-for-bit with zero discrepancies.

---

## 2. Evaluation Cohort Invariants

The evaluation cohort invariants were verified against the original prediction log:
- **Total Unique Recordings:** 700
- **Positive Recordings (Screams):** 200 ($28.57\%$)
- **Negative Recordings (Hard Negatives):** 500 ($71.43\%$)
- **Sustained Screams ($\ge 1.0$s):** 131 ($65.50\%$ of positive class)
- **Short Screams ($< 1.0$s):** 69 ($34.50\%$ of positive class)
- **Shouted-Speech Hard Negatives:** 150
- **Referee Whistle Hard Negatives:** 60
- **Cheering / Stadium Chants:** 50
- **Infant Crying:** 19
- **Environmental Noise & Sirens:** 221
- **Unique Source Groups:** 453

---

## 3. Reproduced Confusion Matrices and Primary Metrics

| Metric | Candidate E1 Static C5 | Candidate B Baseline | Candidate B + Interv. D | Candidate E1 Rolling EMA | Reproduction Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Analysis Framing** | 1.0s Static Center | 1.0s Static Center | 1.0s Static Center | 500 ms Hop / EMA | Verified |
| **Operating Threshold** | $\theta = 0.6800$ | $\theta = 0.8000$ | $\theta = 0.8000$ + Whistle | $\alpha=0.50, \theta=0.6000$ | Verified |
| **True Positives (TP)** | 116 | 115 | 114 | **140** | **EXACT MATCH** |
| **False Negatives (FN)** | 84 | 85 | 86 | **60** | **EXACT MATCH** |
| **False Positives (FP)** | 96 | 79 | **74** | 177 | **EXACT MATCH** |
| **True Negatives (TN)** | 404 | 421 | **426** | 323 | **EXACT MATCH** |
| **Overall Scream Recall** | 58.00% (116/200) | 57.50% (115/200) | 57.00% (114/200) | **70.00% (140/200)** | **EXACT MATCH** |
| *Recall 95% Wilson CI* | [51.07%, 64.63%] | [50.57%, 64.15%] | [50.07%, 63.67%] | [63.32%, 75.93%] | **EXACT MATCH** |
| **Sustained Recall ($\ge 1.0$s)** | 69.47% (91/131) | 67.18% (88/131) | 67.18% (88/131) | **86.26% (113/131)** | **EXACT MATCH** |
| **Short Scream Recall ($< 1.0$s)** | 36.23% (25/69) | **39.13% (27/69)** | 37.68% (26/69) | **39.13% (27/69)** | **EXACT MATCH** |
| **Hard-Negative FPR** | 19.20% (96/500) | 15.80% (79/500) | **14.80% (74/500)** | 35.40% (177/500) | **EXACT MATCH** |
| *FPR 95% Wilson CI* | [15.99%, 22.88%] | [12.87%, 19.26%] | [11.96%, 18.18%] | [31.33%, 39.69%] | **EXACT MATCH** |
| **Shouted-Speech FPR** | 22.67% (34/150) | **14.00% (21/150)** | **14.00% (21/150)** | 30.67% (46/150) | **EXACT MATCH** |
| **Referee Whistle FPR** | 23.33% (14/60) | 10.00% (6/60) | **1.67% (1/60)** | 25.00% (15/60) | **EXACT MATCH** |
| **Overall Accuracy** | 74.29% (520/700) | 76.57% (536/700) | **77.14% (540/700)** | 66.14% (463/700) | **EXACT MATCH** |
| **Precision** | 54.72% | 59.28% | **60.64%** | 44.16% | **EXACT MATCH** |
| **F1 Score** | 56.31% | 58.38% | **58.76%** | 54.16% | **EXACT MATCH** |

---

## 4. Verification Conclusion

Every single count and rate reported in Stage 8.9.61 is mathematically grounded in the underlying prediction ledger. No data points were fabricated or missing. The primary data reproduction is certified.

