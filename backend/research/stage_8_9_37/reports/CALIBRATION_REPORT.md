# Stage 8.9.37 — Probability Calibration Audit Report

**Project:** Festival Scream Detector  
**Stage:** 8.9.37 — Per-Model Threshold Optimization, Calibration Audit & Dataset Expansion  
**Author:** Principal Acoustic AI Research Scientist & ML Validation Auditor  
**Date:** November 2026  
**Status:** Completed  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE

---

## 1. Executive Summary

This report evaluates whether model scores across Configurations A, B, C, and D are well-calibrated probabilities, whether post-hoc calibration is necessary, and whether calibration improves operating-point selection or scream discrimination.

### Key Findings:
1. **Uncalibrated Status:** Raw sigmoid outputs from neural projection heads exhibit substantial overconfidence or underconfidence:
   - Configuration A (YAMNet-Only): Brier = 0.1584, ECE = 0.1902 (severe overconfidence in middle bins).
   - Configuration B (Dual-Encoder Phonation): Brier = 0.1293, ECE = 0.1217.
   - Configuration C (YAMNet + Subband): Brier = 0.1471, ECE = 0.1670.
   - Configuration D (MP-FS-DualEncoder): Brier = 0.1118, ECE = 0.0859 (best uncalibrated calibration).
2. **Platt Scaling Efficacy:** Fitting Platt Scaling (logistic sigmoid mapping) strictly on validation probabilities substantially improves probability fidelity:
   - For Configuration B, Platt scaling reduces Expected Calibration Error (ECE) from **0.1217 to 0.0401** (a 67% reduction).
   - For Configuration D, Platt scaling reduces ECE from **0.0859 to 0.0597** and Brier score to 0.1057.
3. **Isotonic Regression Warning:** While Isotonic Regression achieves empirical ECE = 0.0000 on the validation set, it fits piecewise step-functions that collapse continuous scores into coarse discrete bins. On small cohorts ($N=293$), this risks severe overfitting and creates score plateaus where small perturbations cause abrupt threshold instability.
4. **Impact on Classification Decision Quality:**
   Post-hoc calibration is a strictly monotonic transformation. Consequently:
   - **ROC-AUC and PR-AUC remain mathematically identical.**
   - **True separation between screams and hard negatives is unchanged.**
   - Calibration *does* improve risk interpretation (e.g. $P=0.80$ genuinely means an $80\%$ empirical event frequency) and centers decision boundaries closer to conventional $0.50$, but it **does not eliminate false alarms or salvage missed screams**.

---

## 2. Validation Calibration Metrics

Calibrators were fitted strictly on the validation partition ($N=293$: 79 screams, 214 negatives). No test data was exposed during fitting.

| Model Candidate | Calibration Method | Validation Brier Score | Validation ECE (10-bin) | Calibration Assessment |
|---|---|---|---|---|
| **Config A (YAMNet-Only)** | Uncalibrated | 0.1584 | 0.1902 | Substantial miscalibration |
| | Platt Scaling | 0.1375 | 0.1547 | Moderate improvement |
| | Isotonic Regression | 0.1017 | 0.0000 | Piecewise step function |
| **Config B (Dual-Encoder)** | Uncalibrated | 0.1293 | 0.1217 | Compressed logit distribution |
| | Platt Scaling | **0.1197** | **0.0401** | **Excellent calibration improvement (-67% ECE)** |
| | Isotonic Regression | 0.1029 | 0.0000 | Discrete binning risk |
| **Config C (YAMNet+Subband)**| Uncalibrated | 0.1471 | 0.1670 | Poorly calibrated |
| | Platt Scaling | 0.1399 | 0.1505 | Modest improvement |
| | Isotonic Regression | 0.1052 | 0.0000 | Overfitting on small sample |
| **Config D (MP-FS-DualEnc)** | Uncalibrated | 0.1118 | 0.0859 | Best baseline calibration |
| | Platt Scaling | **0.1057** | **0.0597** | **Robust probability scaling** |
| | Isotonic Regression | 0.0933 | 0.0000 | Degenerate plateauing |

---

## 3. Reliability Diagrams & Score Distributions

Diagnostic plots were generated and saved under `backend/research/stage_8_9_37/plots/`:
1. `val_reliability_diagrams.png`: Shows empirical fraction of positives vs. predicted probability bins.
   - Uncalibrated curves for Config A and C diverge significantly from the $y=x$ diagonal.
   - Platt-calibrated curves for Config B and D closely track the diagonal across low- and mid-probability regions.
2. `val_score_distributions_by_category.png`: Shows probability density distributions for:
   - Genuine screams ($N=79$).
   - Shouted speech ($N=74$).
   - Crowd cheering ($N=44$).
   - Infant crying ($N=19$).

### Score Distribution Forensics:
- **Shouted Speech:** In Config A and Config C, shouted speech has a heavy right tail extending above $0.35$ (accounting for $18.75\%$ and $20.83\%$ shout false positive rates).
- **Phonation Suppression:** In Config B and Config D, the addition of the 12-dimensional phonation mask suppresses shouted speech scores significantly, shifting the mode of shouting below $0.15$.
- **Infant Crying:** Infant crying exhibits bimodal behavior in all candidates: vocalized crying with high F0 overlaps with scream acoustic bands, while rhythmic sobbing is rejected.

---

## 4. Frozen Test Set Comparison: Calibrated vs. Uncalibrated

When evaluated on the independent frozen test cohort ($N=293$: 102 screams, 191 negatives):

| Model | Variant | Threshold | Test Recall | Test HN-FPR | Test Shout-FPR | Test F1 | Test Brier |
|---|---|---|---|---|---|---|---|
| **Config B (Dual-Encoder)** | Uncalibrated (Point A) | 0.44 | 81.37% (83/102) | 6.28% (12/191) | 8.33% (4/48) | 0.8177 | 0.1165 |
| | Platt Calibrated (Point A) | 0.50 | 81.37% (83/102) | 6.28% (12/191) | 8.33% (4/48) | 0.8177 | **0.1082** |
| **Config D (MP-FS-DualEnc)** | Uncalibrated (Point A) | 0.43 | 89.22% (91/102) | 9.95% (19/191) | 14.58% (7/48) | 0.8626 | 0.1004 |
| | Platt Calibrated (Point A) | 0.50 | 89.22% (91/102) | 9.95% (19/191) | 14.58% (7/48) | 0.8626 | **0.0945** |

### Critical Finding:
Platt scaling maps the optimal validation threshold $\theta^* = 0.43$ cleanly to the standard canonical threshold $\theta^* = 0.50$ without altering a single classification decision, while reducing test Brier score from $0.1004$ to $0.0945$.

**Recommendation:** Calibration should be preserved as an interpretability layer for confidence reporting, but it should not be promoted as a method to satisfy the 5 acceptance gates.
