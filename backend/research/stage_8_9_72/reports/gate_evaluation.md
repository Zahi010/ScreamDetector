# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Stage 8.9.72 Five-Gate Acceptance Evaluation & Statistical Ledger

**Project:** Festival Scream Detector  
**Stage:** 8.9.72  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Evaluation Date:** 2026-11-14  
**Evaluated Cohort:** Stage 54 Validation Cohort ($N=311$, 138 Source Groups, `EXPOSED_DEVELOPMENT_COHORT`)  
**Diagnostic Cohort:** Stage 64 Short-Scream Collection ($N=268$, 7 Source Groups, `EXPOSED_DIAGNOSTIC_COHORT`)  
**Operating Threshold:** 0.4920  
**Overall Model Verdict:** **`PARTIAL IMPROVEMENT — ONE OR MORE GATES FAILED`**

---

## 1. Five-Gate Mandatory Acceptance Scorecard

| Gate ID | Target Requirement | Metric Name | Numerator / Denominator | Point Estimate | 95% Cluster-Aware Bootstrap CI | Source Groups ($N_{sg}$) | Cohort Exposure Status | Sample Sufficiency | Gate Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
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

## 3. Granular Category-Level False-Positive Rates

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

## 4. Multi-Candidate Tournament Comparison Matrix

Comprehensive head-to-head comparison across all historical and Stage 72 candidates on identical validation audio ($N=311$):

| Candidate Identifier | Architecture & Suppression Mechanism | Overall Recall (Gate 1) | Hard-Neg FPR (Gate 2) | Shouted FPR (Gate 3) | Short Recall (Gate 4) | Latency P95 (Gate 5) | Gate Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Candidate 67-D** | Dual-Res Gated + 2-Veto (Whistle + Distress) | 73.74% (73/99) | 8.87% (11/124) | 13.64% (12/88) | 92.31% (36/39) | 0.397 ms | FAIL (G1, G2) |
| **Candidate 68-D** | Dual-Res Gated + 4-Veto (SNR Adaptive) | 74.75% (74/99) | 7.26% (9/124) | 13.64% (12/88) | 92.31% (36/39) | 0.409 ms | FAIL (G1, G2) |
| **Candidate 69-D** | Dual-Res Gated + Conditioned Multi-Veto | 79.80% (79/99) | 8.06% (10/124) | 13.64% (12/88) | 92.31% (36/39) | 0.384 ms | FAIL (G1, G2) |
| **Candidate 70-D** | Dual-Res Gated + Simplified 3-Veto & Resonance Rescue | 82.83% (82/99) | 9.68% (12/124) | 14.77% (13/88) | 94.87% (37/39) | 0.384 ms | FAIL (G1, G2) |
| **Candidate 71-D** | **Dual-Res Gated + 3-Veto & Flux-Conditioned Rescue** | **82.83% (82/99)** | **8.06% (10/124)** | **14.77% (13/88)** | **94.87% (37/39)** | **0.417 ms** | **FAIL (G1, G2) [CHAMPION]** |
| **Candidate 72-A** | Dual-Res + Low-SNR Noise-Floor Norm (EXP_A1) | 83.84% (83/99) | 10.48% (13/124) | 18.18% (16/88) | 94.87% (37/39) | 0.388 ms | FAIL (G1, G2, G3) |
| **Candidate 72-B** | Dual-Res + Supervised Contrastive Loss (EXP_C1) | 80.81% (80/99) | 8.06% (10/124) | 13.64% (12/88) | 92.31% (36/39) | 0.384 ms | FAIL (G1, G2) |
| **Candidate 72-C** | Multi-Task Hard-Negative Regularization (EXP_D1) | 80.81% (80/99) | 7.26% (9/124) | 13.64% (12/88) | 92.31% (36/39) | 0.392 ms | FAIL (G1, G2) |

---

## 5. Decision Rule & Final Verdict

1. **Gate Compliance Status:** No candidate in the tournament satisfies all five acceptance gates. Gates 1 and 2 remain unmet across all architectures.
2. **Research Champion Designation:** Candidate 71-D is retained as the active research champion. Candidate 72-A achieved +1 TP but suffered unacceptable regression on Gate 3 (18.18% FPR). Candidates 72-B and 72-C reduced false alarms slightly but sacrificed recall (80.81%).
3. **Production Promotion:** **STRICTLY PROHIBITED**. Non-certified acoustic prototype for laboratory demonstration only.

