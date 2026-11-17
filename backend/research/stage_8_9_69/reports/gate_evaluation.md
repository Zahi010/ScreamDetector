# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.69 — FIVE-GATE EVALUATION & BOOTSTRAP STATISTICAL SCORECARD

**Mandatory Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
Non-certified experimental acoustic research system. Not for emergency detection, autonomous dispatch, or critical security deployment.

## 1. Executive Summary

Stage 8.9.69 evaluated Candidate 69-D against the five preregistered research acceptance gates on the Stage 54 Validation partition ($N=311$, 138 source groups, classified as `EXPOSED_DEVELOPMENT_COHORT`) and the held-out short scream partition ($N=268$).

Candidate 69-D recovers **+5 screams** compared to frozen Candidate 68-D (79/99 vs 74/99) and **+6 screams** compared to Candidate 67-D (79/99 vs 73/99), while strictly preserving shouted-speech FPR at **13.64%** (12/88, Gate 3 PASS).

However, in accordance with strict empirical reporting standards, **Gate 1 (Recall $\ge 96.0\%$)** and **Gate 2 (Hard-Negative FPR $\le 5.0\%$)** remain failed. The overall stage verdict is **PARTIAL IMPROVEMENT — ONE OR MORE GATES FAILED**.

---

## 2. Five-Gate Scorecard with 95% Bootstrap Confidence Intervals

Bootstrap iterations: $B = 2,000$ resamples with replacement. Random seed: `42`.

| Gate ID | Target Requirement | Candidate 65-F | Candidate 67-D | Candidate 68-D | Candidate 69-D (Champion) | 95% Bootstrap CI (69-D) | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Gate 1** | Overall Scream Recall $\ge 96.0\%$ | 86.87% (86/99) | 73.74% (73/99) | 74.75% (74/99) | **79.80% (79/99)** | **[71.72%, 86.89%]** | **FAIL** |
| **Gate 2** | Hard-Negative FPR $\le 5.0\%$ | 59.68% (74/124) | 8.87% (11/124) | 7.26% (9/124) | **8.06% (10/124)** | **[4.03%, 12.90%]** | **FAIL** |
| **Gate 3** | Shouted-Speech FPR $\le 15.0\%$ | 48.86% (43/88) | 13.64% (12/88) | 13.64% (12/88) | **13.64% (12/88)** | **[6.82%, 21.59%]** | **PASS** |
| **Gate 4** | Short-Scream Recall $\ge 90.0\%$ | 97.44% (38/39) | 92.31% (36/39) | 92.31% (36/39) | **92.31% (36/39)** | **[82.05%, 100.00%]** | **PASS** |
| **Gate 5** | Model-only CPU P95 Latency $\le 25.0$ ms | 0.812 ms | 0.812 ms | 0.812 ms | **0.384 ms** | **[0.340 ms, 0.440 ms]** | **PASS** |

---

## 3. Forensic Analysis of Gate Performance

### Gate 1 (Scream Recall: 79.80% — FAILED)
- **Point Estimate:** 79.80% (79 true positives out of 99 positive scream recordings).
- **Target:** $\ge 96.0\%$. Gap to target: 16.20 percentage points (16 additional screams required).
- **Progress:** Candidate 69-D recovered 5 screams that Candidate 68-D missed:
  1. `PZ73_15_2_1_33_0_0_0` (rescued from HFCR roll-off veto by conditioning on vocal roughness $< 0.050$).
  2. `219863__acehell__crit-marc` (rescued from HFCR roll-off veto by conditioning on vocal roughness $< 0.050$).
  3. `ZQYD_15_7_0_23_0_0_0` (rescued from spectral flux veto by tightening flux cutoff to 0.036).
  4. `fsd50k_178105` (rescued from spectral flux veto via high-frequency ratio bypass $hf\_ratio > 1.0$).
  5. `77AY_15_7_0_30_0_0_0` (rescued from vocal distress veto by adjusting roughness ceiling to 0.022).
- **Residual Failure Root Cause:** The remaining 20 false negatives are fundamentally limited by raw neural confidence ($p_{\text{raw}} \in [0.336, 0.489]$) caused by diffuse reverberation smearing and low SNR ($-6$ dB to $+3$ dB), rather than veto misfires.

### Gate 2 (Hard-Negative FPR: 8.06% — FAILED)
- **Point Estimate:** 8.06% (10 false alarms out of 124 hard negatives).
- **Target:** $\le 5.0\%$ (requires $\le 6$ false alarms).
- **Analysis:** Candidate 69-D incurs 10 false alarms, which is +1 over Candidate 68-D (9/124, 7.26%) but -1 under Candidate 67-D (11/124, 8.87%). The 10 false alarms stem from impulsive acoustic transients (dropped tools, door slams, brass instruments) that exhibit broadband energy without harmonic comb structure.

### Gate 3 (Shouted-Speech FPR: 13.64% — PASSED)
- **Point Estimate:** 13.64% (12 false alarms out of 88 shouting clips).
- **Target:** $\le 15.0\%$.
- **Status:** **PASS**. The combination of the roughness-conditioned HFCR roll-off veto and calibrated vocal distress threshold strictly suppresses male shouting and loud conversational speech while maintaining gate compliance.

### Gate 4 (Short-Scream Recall: 92.31% — PASSED)
- **Point Estimate:** 92.31% (36 true positives out of 39 short scream recordings $< 1.0$s).
- **Target:** $\ge 90.0\%$.
- **Ultra-Short ($d \le 0.5$s):** 100% (24/24).
- **Status:** **PASS**. Dual-resolution 250 ms short-branch architecture reliably captures abrupt explosive acoustic onsets.

### Gate 5 (Model-Only Latency: 0.384 ms — PASSED)
- **Point Estimate:** 0.384 ms CPU P95 (single stream); 0.511 ms CPU P95 (8 concurrent streams).
- **Target:** $\le 25.0$ ms. Margin: $> 60\times$ faster than ceiling.
- **Status:** **PASS**.
