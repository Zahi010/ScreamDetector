# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Stage 8.9.73 Five-Gate Acceptance Evaluation & Statistical Ledger

**Project:** Festival Scream Detector  
**Stage:** 8.9.73  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Evaluation Date:** 2026-11-14  
**Evaluated Cohort:** Stage 54 Validation Cohort ($N=311$, 138 Source Groups, `EXPOSED_DEVELOPMENT_COHORT`)  
**Diagnostic Cohort:** Stage 64 Short-Scream Collection ($N=268$, 7 Source Groups, `EXPOSED_DIAGNOSTIC_COHORT`)  
**Operating Threshold:** 0.4920  
**Overall Model Verdict:** **`PARTIAL IMPROVEMENT — ONE OR MORE GATES FAILED`**

---

## 1. Five-Gate Mandatory Acceptance Scorecard

| Gate ID | Target Requirement | Metric Name | Numerator / Denominator | Point Estimate | 95% Cluster-Aware Bootstrap CI | Source Groups ($N_{sg}$) | Cohort Exposure Status | Sample Sufficiency | Gate Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Gate 1** | $\ge 96.0\%$ | Overall Scream Recall | 82 / 99 | **82.83%** | [74.00%, 91.25%] | 47 | `EXPOSED_DEVELOPMENT_COHORT` | Sufficient ($N=99$) | **FAIL** |
| **Gate 2** | $\le 5.0\%$ | Hard-Negative FPR | 10 / 124 | **8.06%** | [2.83%, 14.29%] | 68 | `EXPOSED_DEVELOPMENT_COHORT` | Sufficient ($N=124$) | **FAIL** |
| **Gate 3** | $\le 15.0\%$ | Shouted-Speech FPR | 13 / 88 | **14.77%** | [2.13%, 32.50%] | 23 | `EXPOSED_DEVELOPMENT_COHORT` | Sufficient ($N=88$) | **PASS** |
| **Gate 4** | $\ge 90.0\%$ | Short-Scream Recall (< 1.0s) | 37 / 39 | **94.87%** | [86.21%, 100.00%] | 22 | `EXPOSED_DEVELOPMENT_COHORT` | Marginal ($N=39$) | **PASS** |
| **Gate 5** | $\le 25.0$ ms | Model-Only CPU P95 Latency | 0.417 ms / 25.0 ms | **0.417 ms** | [0.380 ms, 0.450 ms] | N/A (Local CPU) | Benchmarked Synthetic Batch | Highly Sufficient ($N=1000$) | **PASS** |

---

## 2. Additional Performance Metrics (Candidate 71-D Frozen Champion)

All metrics computed on the exposed validation cohort ($N=311$):

| Statistical Dimension | Observed Value | Point Estimate & Ratio | Scientific Interpretation |
| :--- | :--- | :--- | :--- |
| **Precision** | **78.10%** | 82 / 105 total detections | 21.9% of alarms in validation set are false positives |
| **F1 Score** | **80.39%** | Harmonic mean of precision & recall | Balanced detection efficiency on exposed data |
| **Specificity (True Negative Rate)** | **89.15%** | 189 / 212 non-screams | 10.85% overall non-scream alarm rate |
| **Balanced Accuracy** | **85.99%** | (Recall + Specificity) / 2 | Strong unweighted performance across imbalanced classes |
| **ROC-AUC** | **0.9069** | Rank discrimination ability | Area under receiver operating characteristic curve |
| **PR-AUC** | **0.8482** | Precision-Recall curve area | High positive predictive value curve |
| **Brier Score Loss** | **0.1393** | Mean squared probability error | Mean probability calibration deviation |
| **Expected Calibration Error (ECE)**| **0.1574** | 10-bin calibration gap | Indicates mild overconfidence in moderate probability band |

---

## 3. Disentangled Scream Recall (Real vs Synthetic)

The overall recall of 82.83% conflates two distinct acoustic populations:

| Sub-Cohort | Sample Size ($N$) | Correctly Detected (TP) | False Negatives (FN) | Sub-Cohort Recall | Primary Reason for Misses |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Genuine Recorded Screams** | 80 | 71 | 9 | **88.75%** | Low vocal roughness in child screams (2), distant low-intensity (5), threshold boundary (2) |
| **Synthetic Masked Screams** | 19 | 11 | 8 | **57.89%** | Heavy crowd noise (-6 dB to 0 dB SNR) elevates spectral floor, flattening formant contrast |
| **Total Combined Positives** | **99** | **82** | **17** | **82.83%** | Aggregate recall evaluated under Gate 1 |

---

## 4. Granular Category-Level False-Positive Rates

Breakdown of non-scream false alarms across specific environmental and vocal categories:

| Non-Scream Acoustic Category | False Positives | Total Category Samples | Category FPR | Primary Acoustic Trigger |
| :--- | :--- | :--- | :--- | :--- |
| `crowd_chant_cheering` | 1 | 37 | **2.70%** | Transient high-energy collective cheer burst |
| `general_environmental` | 1 | 36 | **2.78%** | Broadband friction sound with elevated roughness |
| `infant_crying` | 3 | 20 | **15.00%** | Physiological vocal distress & chaos overlap |
| `sfx_sirens_fireworks` | 2 | 9 | **22.22%** | Sustained frequency modulation mimicking scream contour |
| `shouting_and_speech` | 13 | 88 | **14.77%** | High-effort shouted vowel phonation |
| `whistles_and_squeaks` | 3 | 22 | **13.64%** | Resonant whistle burst with extreme high-frequency ratio |
| **Total Non-Screams Combined** | **23** | **212** | **10.85%** | Overall False Positive Rate across all negatives |

---

## 5. Multi-Candidate Tournament Comparison Matrix

Comprehensive head-to-head comparison across historical and Stage 73 candidate architectures on identical validation audio ($N=311$):

| Candidate Identifier | Architecture & Suppression Mechanism | Overall Recall (Gate 1) | Real Scream Recall | Synth Mask Recall | Hard-Neg FPR (Gate 2) | Shouted FPR (Gate 3) | Short Recall (Gate 4) | Latency P95 (Gate 5) | Gate Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Candidate 67-D** | Dual-Res Gated + 2-Veto (Whistle + Distress) | 73.74% (73/99) | 81.25% (65/80) | 42.11% (8/19) | 8.87% (11/124) | 13.64% (12/88) | 92.31% (36/39) | 0.397 ms | FAIL (G1, G2) |
| **Candidate 68-D** | Dual-Res Gated + 4-Veto (SNR Adaptive) | 74.75% (74/99) | 81.25% (65/80) | 47.37% (9/19) | 7.26% (9/124) | 13.64% (12/88) | 92.31% (36/39) | 0.409 ms | FAIL (G1, G2) |
| **Candidate 69-D** | Dual-Res Gated + Conditioned Multi-Veto | 79.80% (79/99) | 86.25% (69/80) | 52.63% (10/19) | 8.06% (10/124) | 13.64% (12/88) | 92.31% (36/39) | 0.384 ms | FAIL (G1, G2) |
| **Candidate 70-D** | Dual-Res Gated + Streamlined 3-Veto & Rescue | 82.83% (82/99) | 88.75% (71/80) | 57.89% (11/19) | 9.68% (12/124) | 14.77% (13/88) | 94.87% (37/39) | 0.384 ms | FAIL (G1, G2) |
| **Candidate 71-D** | **Dual-Res Gated + 3-Veto & Flux-Conditioned Rescue** | **82.83% (82/99)** | **88.75% (71/80)** | **57.89% (11/19)** | **8.06% (10/124)** | **14.77% (13/88)** | **94.87% (37/39)** | **0.417 ms** | **FAIL (G1, G2) [CHAMPION]** |
| **Candidate 73-A** | Hierarchical Vocalization Head (No Vetoes) | 81.82% (81/99) | 87.50% (70/80) | 57.89% (11/19) | 10.48% (13/124) | 27.27% (24/88) | 92.31% (36/39) | 0.465 ms | FAIL (G1, G2, G3) |
| **Candidate 73-B** | Hierarchical Vocalization Head + Calibrated Vetoes | 82.83% (82/99) | 88.75% (71/80) | 57.89% (11/19) | 8.06% (10/124) | 14.77% (13/88) | 94.87% (37/39) | 0.542 ms | FAIL (G1, G2) |
| **Candidate 73-C** | Candidate 71-D with Relaxed Child Distress Veto | 84.85% (84/99) | 91.25% (73/80) | 57.89% (11/19) | 8.06% (10/124) | 17.05% (15/88) | 94.87% (37/39) | 0.417 ms | FAIL (G1, G2, G3) |

---

## 6. Decision Rule & Final Verdict

1. **Gate Compliance Status:** No candidate in the tournament satisfies all five acceptance gates. Gates 1 and 2 remain unmet across all tested architectures.
2. **Research Champion Retention:** **Candidate 71-D is retained as the active research champion**.
   - Candidate 73-A (pure hierarchical neural head without vetoes) suffers catastrophic shouted-speech leakage (**27.27% FPR**, violating Gate 3).
   - Candidate 73-B matches Candidate 71-D accuracy identically but incurs +30% latency overhead (0.542 ms vs 0.417 ms).
   - Candidate 73-C recovers 2 child screams to reach 84.85% overall recall (and 91.25% real scream recall), but allows 2 additional shouted-speech false positives, driving Shouted-Speech FPR to **17.05%**, which fails Gate 3.
3. **Safety & Operational Boundaries:** Research demonstration prototype for engineering evaluation only. Production promotion is strictly prohibited.

