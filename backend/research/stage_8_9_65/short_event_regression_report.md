# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Short-Event Boundary Regression Report: Sensitivity Horizons Across $100$ms to $1000$ms

## 1. Executive Summary

This report delivers a duration-boundary regression audit benchmarking Candidate 65-F against the Baseline Dual-Resolution Model and Variant 6 Full Suppression Stack across the complete $N=401$ short-scream evaluation cohort (all recordings with duration $< 1.00$s).

The regression demonstrates that Candidate 65-F fully recovers the catastrophic sensitivity losses incurred by Variant 6, achieving:
- **All-Short Recall ($< 1.00$s, $N=401$):** **$96.51\%$** for Candidate 65-F vs **$80.55\%$** for Variant 6 (a net recovery of **$+15.96\%$**, or $64$ additional screams detected).
- **Ultra-Short Recall ($\le 500$ms, $N=119$):** **$99.16\%$** for Candidate 65-F vs **$91.60\%$** for Variant 6.
- **Gate 4 Compliance:** Candidate 65-F decisively surpasses Acceptance Gate 4 ($\ge 90.0\%$) across every single evaluated duration horizon.

---

## 2. Granular Horizon Regression Metrics

| Horizon ID | Duration Window | Cohort $N$ | Baseline Recall | Variant 6 Recall | Candidate 65-F Recall | Delta ($\text{65-F} - \text{V6}$) | Gate 4 Status ($\ge 90\%$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **H3: 300ms** | $\le 300\text{ ms}$ | 20 | $100.0\%$ | $100.0\%$ | **100.0%** | $+0.00\%$ | **PASS** |
| **H4: 400ms** | $\le 400\text{ ms}$ | 68 | $98.53\%$ | $95.59\%$ | **98.53%** | $+2.94\%$ | **PASS** |
| **H5: 500ms (Ultra-Short)** | $\le 500\text{ ms}$ | 119 | $99.16\%$ | $91.60\%$ | **99.16%** | $+7.56\%$ | **PASS** |
| **H6: 750ms** | $\le 750\text{ ms}$ | 272 | $98.16\%$ | $83.82\%$ | **98.16%** | $+14.34\%$ | **PASS** |
| **H7: 900ms** | $\le 900\text{ ms}$ | 365 | $96.71\%$ | $80.82\%$ | **96.71%** | $+15.89\%$ | **PASS** |
| **H8: 1000ms (All Short)** | $< 1000\text{ ms}$ | 401 | $96.51\%$ | $80.55\%$ | **96.51%** | **+15.96%** | **PASS** |

---

## 3. Disjoint Interval Duration Bins

Evaluating disjoint duration intervals reveals where Variant 6's recall collapsed and where Candidate 65-F succeeded:

| Interval Bin | Duration Span | Cohort $N$ | Baseline Recall | Variant 6 Recall | Candidate 65-F Recall | Net Recovery (65-F vs V6) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Bin 1: Sub-250ms** | $[0, 250)\text{ ms}$ | 6 | $100.0\%$ | $100.0\%$ | **100.0%** | $0.00\%$ |
| **Bin 2: 250 to 500ms** | $[250, 500]\text{ ms}$ | 116 | $99.14\%$ | $91.38\%$ | **99.14%** | **+7.76%** |
| **Bin 3: 500 to 750ms** | $(500, 750]\text{ ms}$ | 155 | $97.42\%$ | $78.06\%$ | **97.42%** | **+19.35%** |
| **Bin 4: 750 to 1000ms** | $(750, 1000)\text{ ms}$ | 133 | $93.23\%$ | $72.93\%$ | **93.23%** | **+20.30%** |

### Critical Analytical Insights
1. **The Collapse Zone ($500\text{--}1000$ ms):**
   - In Variant 6, recall collapsed most severely in the $500\text{--}1000\text{ ms}$ window, dropping by $19.35\%$ in Bin 3 and $20.30\%$ in Bin 4.
   - In this duration range, screams are long enough to develop sustained harmonic periodicity, but short enough that the sustained branch receives partial zero-padding. The crude HNR tonal veto perceived the harmonicity as a whistle and slashed probabilities by $0.20\times$.
2. **Selective Gating Protection:**
   - Candidate 65-F's high-confidence bypass and branch agreement gating prevented false attenuation, restoring recall in Bins 3 and 4 back to $97.42\%$ and $93.23\%$.

---

## 4. Acceptance Gate Assessment
- **Acceptance Gate 4 Authority:** Gate 4 is defined as `Short-Scream Recall >= 90.0% on screams < 1.00s in duration`.
- **Validation Outcome:** Candidate 65-F achieves **$96.51\%$** across all 401 short screams, satisfying Gate 4 by an authoritative margin of $+6.51\%$.

---

## 5. Artifact Links
- Horizon Metrics CSV: [short_duration_candidate_metrics.csv](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/short_duration_candidate_metrics.csv)
- Short Scream Cohort Predictions: [short_scream_cohort_predictions.csv](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/short_scream_cohort_predictions.csv)
- Generalization Report: [short_duration_generalization_report.md](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/short_duration_generalization_report.md)

