# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Stage 8.9.74 Five-Gate Acceptance Evaluation & Statistical Ledger

**Project:** Festival Scream Detector  
**Stage:** 8.9.74  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Evaluation Date:** 2026-11-14  
**Evaluated Cohort:** Stage 54 Validation Cohort ($N=311$, 138 Source Groups, `EXPOSED_DEVELOPMENT_COHORT`)  
**Operating Threshold:** 0.4920  
**Overall Model Verdict:** **`PARTIAL IMPROVEMENT — ONE OR MORE GATES FAILED`**

---

## 1. Five-Gate Mandatory Acceptance Scorecard

All metrics evaluated against the exposed Stage 54 Validation Cohort ($N=311$) with 95% source-group cluster bootstrap confidence intervals ($B=2,000$ resamples across 138 source groups, seed=42):

| Gate ID | Target Requirement | Metric Name | Numerator / Denominator | Point Estimate | 95% Cluster-Aware Bootstrap CI | Source Groups ($N_{sg}$) | Cohort Exposure Status | Evidence Sufficiency | Gate Verdict |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Gate 1** | $\ge 96.0\%$ | Overall Scream Recall | 82 / 99 | **82.83%** | [74.07%, 91.77%] | 47 SGs | `EXPOSED_DEVELOPMENT_COHORT` | Sufficient ($N=99$) | **FAIL — POINT ESTIMATE** |
| **Gate 2** | $\le 5.0\%$ | Hard-Negative FPR | 10 / 124 | **8.06%** | [2.94%, 14.16%] | 69 SGs | `EXPOSED_DEVELOPMENT_COHORT` | Sufficient ($N=124$) | **FAIL — POINT ESTIMATE** |
| **Gate 3** | $\le 15.0\%$ | Shouted-Speech FPR | 13 / 88 | **14.77%** | [2.33%, 31.15%] | 28 SGs | `EXPOSED_DEVELOPMENT_COHORT` | Marginal (CI crosses 15%) | **PASS — POINT ESTIMATE** |
| **Gate 4** | $\ge 90.0\%$ | Short-Scream Recall (< 1.0s) | 37 / 39 | **94.87%** | [86.84%, 100.00%] | 24 SGs | `EXPOSED_DEVELOPMENT_COHORT` | Marginal ($N=39$, CI crosses 90%) | **PASS — POINT ESTIMATE** |
| **Gate 5** | $\le 25.0$ ms | Model-Only CPU P95 Latency | 0.370 ms / 25.0 ms | **0.370 ms** | [0.350 ms, 0.450 ms] | N/A (Local CPU) | Benchmarked Synthetic Batch | Highly Sufficient ($N=1000$) | **PASS — POINT ESTIMATE** ($> 67\times$ Headroom) |

---

## 2. Disentangled Scream Recall (Real vs Synthetic)

| Scream Sub-Cohort | Sample Count ($N$) | Correctly Detected (TP) | False Negatives (FN) | Recall Rate | Primary Failure Mechanism |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Genuine Real Screams** | 80 | **71** | **9** | **88.75%** | Low vocal roughness in child screams (2), distant gasps (5), threshold boundary (2) |
| **Synthetic Masked Screams** | 19 | **11** | **8** | **57.89%** | Severe crowd noise (-6 dB to 0 dB SNR) elevates noise floor and washes out harmonic contrast |
| **Combined Positives** | **99** | **82** | **17** | **82.83%** | Combined development benchmark (Gate 1) |

---

## 3. Granular Category-Level False-Positive Rates

| Non-Scream Acoustic Category | False Positives | Total Category Samples | Category FPR | Primary Acoustic Trigger |
| :--- | :---: | :---: | :---: | :--- |
| `crowd_chant_cheering` | 1 | 37 | **2.70%** | Transient high-energy collective cheer burst |
| `general_environmental` | 1 | 36 | **2.78%** | Broadband friction sound with elevated roughness |
| `infant_crying` | 3 | 20 | **15.00%** | Physiological vocal distress & chaos overlap |
| `sfx_sirens_fireworks` | 2 | 9 | **22.22%** | Sustained frequency modulation mimicking scream contour |
| `shouting_and_speech` | 13 | 88 | **14.77%** | High-effort shouted vowel phonation (8 from uploader `reitanna`) |
| `whistles_and_squeaks` | 3 | 22 | **13.64%** | Resonant whistle burst with extreme high-frequency ratio |
| **Total Non-Screams Combined** | **23** | **212** | **10.85%** | Overall False Positive Rate across all negatives |

---

## 4. Multi-Candidate Tournament Comparison Matrix

| Candidate Identifier | Architecture & Core Innovations | Overall Recall | Real Recall | Synth Recall | HN FPR | Shout FPR | Short Recall | CPU P95 Latency | Gate Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Candidate 67-D** | Dual-Res Gated + 2-Veto (Whistle + Distress) | 73.74% | 81.25% | 42.11% | 8.87% | 13.64% | 92.31% | 0.397 ms | FAIL (Gates 1, 2) |
| **Candidate 68-D** | Dual-Res Gated + 4-Veto (SNR Adaptive) | 74.75% | 81.25% | 47.37% | 7.26% | 13.64% | 92.31% | 0.409 ms | FAIL (Gates 1, 2) |
| **Candidate 69-D** | Dual-Res Gated + Conditioned Multi-Veto | 79.80% | 86.25% | 52.63% | 8.06% | 13.64% | 92.31% | 0.384 ms | FAIL (Gates 1, 2) |
| **Candidate 70-D** | Dual-Res Gated + Streamlined 3-Veto & Rescue | 82.83% | 88.75% | 57.89% | 9.68% | 14.77% | 94.87% | 0.384 ms | FAIL (Gates 1, 2) |
| **Candidate 71-D** | **Dual-Res Gated + Flux-Conditioned Rescue** | **82.83%** | **88.75%** | **57.89%** | **8.06%** | **14.77%** | **94.87%** | **0.370 ms** | **FAIL (Gates 1, 2) [CHAMPION]** |
| **Candidate 73-A** | Hierarchical Vocalization Head (No Vetoes) | 81.82% | 87.50% | 57.89% | 10.48% | 27.27% | 92.31% | 0.465 ms | FAIL (Gates 1, 2, 3) |
| **Candidate 73-B** | Hierarchical Head + Calibrated Vetoes | 82.83% | 88.75% | 57.89% | 8.06% | 14.77% | 94.87% | 0.542 ms | FAIL (Gates 1, 2) |
| **Candidate 73-C** | Candidate 71-D with Relaxed Child Distress Veto | 84.85% | 91.25% | 57.89% | 8.06% | 17.05% | 94.87% | 0.370 ms | FAIL (Gates 1, 2, 3) |

---

## 5. Final Research Ruling & Decision

1. **Gate Acceptance:** Gates 1 and 2 remain unmet across all tested candidates.
2. **Active Research Champion Retention:** Candidate 71-D is retained as the active frozen research champion.
3. **Safety Status:** Research demonstration prototype for engineering evaluation only. Production promotion is strictly prohibited.

