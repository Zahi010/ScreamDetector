# Stage 8.9.39 — Reserved Expansion Cohort Independent Generalization Audit Report

**Project:** Festival Scream Detector  
**Stage:** 8.9.39 — Controlled Retraining, Expanded Dataset Evaluation & Independent Generalization Audit  
**Author:** Principal Acoustic AI Research Scientist & ML Validation Auditor  
**Date:** November 2026  
**Status:** Completed  
**Mandatory Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  

---

## 1. Executive Summary & Audit Mandate

The Reserved Expansion Benchmark (`v4_reserved_expansion_test`, $N=102$) is the **primary independent generalization benchmark** of Stage 8.9.39.

It was designed in Stage 8.9.38 under strict source-group isolation to test generalization to:
- 35 completely unseen short-scream source groups ($N=65$ active short-scream clips).
- Multi-talker hard-negative festival crowd environments and shouted speech ($N=37$ active non-scream clips, including 16 shouted speech clips).
- Zero overlap with training (`v4_train`, $N=820$), validation (`v4_val`, $N=339$), or historical benchmark (`v4_historical_test`, $N=293$).

**Strict Independence Safeguards:** No model selection, hyperparameter tuning, feature engineering, early stopping, threshold search, or calibration fitting had access to this cohort. All model weights, preprocessing routines, and decision thresholds were frozen before test execution.

---

## 2. Benchmark Composition & Reconciled Accounting

As verified in the Pre-Training Integrity Audit (`pretraining_integrity_report.json`):
- **35 Reserved Short-Scream Source Groups:** Account for 71 total clips.
  - 65 clips are approved linear PCM WAV short screams ($< 1.0\text{ s}$).
  - 6 clips are quarantined due to non-commercial licensing (`CC BY-NC 4.0`), verified 100% excluded.
  - Active short screams: Exactly **65**.
- **Expansion Hard Negatives:** Exactly **37** active non-scream recordings:
  - 16 shouted speech / multi-talker vocalizations.
  - 14 crowd cheering / stadium chanting clips.
  - 3 infant crying clips.
  - 2 sirens / fireworks SFX clips.
  - 2 general festival environmental noise clips.
- **Total Cohort Size:** Exactly **102** active recordings across 49 independent source groups.

---

## 3. Candidate B Evaluation on Reserved Expansion Benchmark

Evaluated using the validation-frozen optimal threshold $\theta = 0.24$:

| Metric | Point Estimate | Exact Ratio | 95% Wilson Score CI | Gate Threshold | Gate Compliance |
|---|---|---|---|---|---|
| **True Positives (TP)** | 65 | 65/65 | — | — | — |
| **False Positives (FP)** | 0 | 0/37 | — | — | — |
| **True Negatives (TN)** | 37 | 37/37 | — | — | — |
| **False Negatives (FN)** | 0 | 0/65 | — | — | — |
| **Overall Scream Recall** | **100.0%** | **65/65** | **[94.42%, 100.0%]** | $\ge 96.0\%$ | **Point PASS (CI Caveat)** |
| **Hard-Negative FPR** | **0.0%** | **0/37** | **[0.00%, 9.41%]** | $\le 5.0\%$ | **Point PASS (CI Caveat)** |
| **Shouted-Speech FPR** | **0.0%** | **0/16** | **[0.00%, 19.36%]** | $\le 15.0\%$ | **Point PASS (CI Caveat)** |
| **Short-Scream Recall** | **100.0%** | **65/65** | **[94.42%, 100.0%]** | $\ge 90.0\%$ | **PASS (Statistically Valid)** |
| **Precision** | 100.0% | 65/65 | [94.42%, 100.0%] | — | — |
| **F1 Score** | 1.0000 | — | — | — | — |
| **ROC-AUC / PR-AUC** | 1.0000 / 1.0000 | — | — | — | — |

*Evaluation at Reference Threshold $\theta = 0.35$:* Identical ($\text{TP}=65, \text{FP}=0, \text{TN}=37, \text{FN}=0$).

---

## 4. Candidate D Evaluation on Reserved Expansion Benchmark

Evaluated using the validation-frozen optimal threshold $\theta = 0.34$:

| Metric | Point Estimate | Exact Ratio | 95% Wilson Score CI | Gate Threshold | Gate Compliance |
|---|---|---|---|---|---|
| **True Positives (TP)** | 65 | 65/65 | — | — | — |
| **False Positives (FP)** | 0 | 0/37 | — | — | — |
| **True Negatives (TN)** | 37 | 37/37 | — | — | — |
| **False Negatives (FN)** | 0 | 0/65 | — | — | — |
| **Overall Scream Recall** | **100.0%** | **65/65** | **[94.42%, 100.0%]** | $\ge 96.0\%$ | **Point PASS (CI Caveat)** |
| **Hard-Negative FPR** | **0.0%** | **0/37** | **[0.00%, 9.41%]** | $\le 5.0\%$ | **Point PASS (CI Caveat)** |
| **Shouted-Speech FPR** | **0.0%** | **0/16** | **[0.00%, 19.36%]** | $\le 15.0\%$ | **Point PASS (CI Caveat)** |
| **Short-Scream Recall** | **100.0%** | **65/65** | **[94.42%, 100.0%]** | $\ge 90.0\%$ | **PASS (Statistically Valid)** |
| **Precision** | 100.0% | 65/65 | [94.42%, 100.0%] | — | — |
| **F1 Score** | 1.0000 | — | — | — | — |
| **ROC-AUC / PR-AUC** | 1.0000 / 1.0000 | — | — | — | — |

*Evaluation at Balanced Threshold $\theta = 0.32$ & Reference $\theta = 0.35$:* Identical ($\text{TP}=65, \text{FP}=0, \text{TN}=37, \text{FN}=0$).

---

## 5. Formal Evaluation Against the Five Research Acceptance Gates

Per Section 12 of the research specification, gates must be evaluated with exact fractions and 95% Wilson confidence intervals:

| Research Gate | Requirement | Candidate B ($\theta=0.24$) | Candidate D ($\theta=0.34$) | Formal Statistical Compliance Finding |
|---|---|---|---|---|
| **Gate 1: Overall Scream Recall** | $\ge 96.0\%$ | **100.0%** (65/65)<br>CI: [94.42%, 100.0%] | **100.0%** (65/65)<br>CI: [94.42%, 100.0%] | **POINT PASS — CI CAVEAT:** Point estimate (100.0%) exceeds 96%, but lower CI bound (94.42%) dips below 96.0% due to finite positive sample size ($N=65$). |
| **Gate 2: Hard-Negative FPR** | $\le 5.0\%$ | **0.0%** (0/37)<br>CI: [0.00%, 9.41%] | **0.0%** (0/37)<br>CI: [0.00%, 9.41%] | **POINT PASS — CI CAVEAT:** Point estimate (0.0%) satisfies requirement, but upper CI bound (9.41%) exceeds 5.0% due to sample size ($N=37$). |
| **Gate 3: Shouted-Speech FPR** | $\le 15.0\%$ | **0.0%** (0/16)<br>CI: [0.00%, 19.36%] | **0.0%** (0/16)<br>CI: [0.00%, 19.36%] | **INSUFFICIENT EVIDENCE (STATISTICAL):** With $N=16$ shouted clips, 0/16 yields upper bound of 19.36% > 15%. Reliable statistical verification requires $N \ge 25$ shouted speech clips. |
| **Gate 4: Short-Scream Recall** | $\ge 90.0\%$ | **100.0%** (65/65)<br>CI: [94.42%, 100.0%] | **100.0%** (65/65)<br>CI: [94.42%, 100.0%] | **PASS (STATISTICALLY ESTABLISHED):** Point estimate is 100.0% and entire 95% CI [94.42%, 100.0%] remains strictly above the 90.0% threshold. |
| **Gate 5: P95 Inference Latency** | $\le 25.0\text{ ms}$ | **0.516 ms** | **0.678 ms** | **PASS:** P95 latency is $< 1.0\text{ ms}$ on CPU, well below 25.0 ms limit. |

---

## 6. Scientific Analysis of Generalization & Acoustic Separation

### 6.1 Why Did Both Models Achieve Perfect Separation on the Expansion Cohort?
1. **Targeted Acoustic Diversity in Training:** Integrating 85 short screams and 165 multi-talker recordings into the broader v4 dataset successfully taught both architectures the specific spectral boundaries of brief screams ($< 1.0\text{ s}$) versus multi-talker festival babble.
2. **Clear Morphological Separation:** The reserved short-scream recordings in `v4_reserved_expansion_test` exhibit sharp, unambiguous acoustic energy spikes in the $1.5\text{--}4.0\text{ kHz}$ resonance band.
3. **Contrastive Regularization:** The supervised contrastive loss penalty in both models effectively repelled shouted speech and crowd laughter embeddings from the high-arousal scream manifold.

### 6.2 Contrast with Historical Test Benchmark:
While both models achieved 100% precision and recall on the newly acquired expansion cohort, their performance on `v4_historical_test` ($N=293$) was lower:
- Configuration B: Recall 87.25% (View A) / 89.00% (View B), Hard-Negative FPR 12.04%.
- Configuration D: Recall 83.33% (View A) / 85.00% (View B), Hard-Negative FPR 13.09%.

This dichotomy reveals that the expansion cohort—while an independent, previously unseen test set—primarily consists of distinct short screams and crowd babble. In contrast, the historical cohort contains highly adverse acoustic confounders: sirens, reverberant referee whistles, and masked screams recorded through heavy festival distortion.

---

## 7. Audit Verdict on Gate Compliance

- **Point-Estimate Pass Count:** 5 of 5 gates passed by both candidates.
- **Statistically Established Pass Count:** 2 of 5 gates fully established by confidence intervals (Gate 4 Short-Scream Recall and Gate 5 Latency).
- **Statistical Insufficiency Finding:** Due to $N=16$ for shouted speech and $N=37$ for hard negatives, statistical evidence remains insufficient to conclusively guarantee Gates 2 and 3 at the 95% confidence level.
- **Promotion Status:** **NOT AUTHORIZED FOR PRODUCTION.** Research prototype designation remains mandatory.

