# Stage 8.9.40: Frozen Model Multi-Cohort Evaluation Report

**MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**

*This project is an experimental acoustic research system. It is not certified for life-safety alerting, emergency response, active shooter detection, autonomous police dispatch, or critical physical security deployments.*

---

## 1. Executive Summary

In Stage 8.9.40, Candidate Configuration B (`DualEncoderAcousticModel`) and Configuration D (`MultiPathwayFusionModel`) were evaluated across three separate cohorts without modifying their weights, thresholds, or Platt calibration models:

1. **Stage 8.9.40 New Independent Hard-Negative Cohort ($N=145$, 79 source groups):** High-powered out-of-sample hard-negative stress test.
2. **Stage 8.9.39 Frozen Expansion Benchmark Snapshot ($N=102$, 49 source groups):** 65 short screams across 35 reserved groups and 37 hard negatives.
3. **Historical Continuity Benchmark ($N=293$):** Stage 5 test partition evaluated under both View A (Original labels) and View B (Adjudicated labels).

All metrics include exact numerators, denominators, and 95% Wilson score confidence intervals.

---

## 2. Frozen Model Architectural Parameters

| Parameter | Configuration B | Configuration D |
|---|---|---|
| **Model Class** | `DualEncoderAcousticModel` | `MultiPathwayFusionModel` |
| **Input Modalities** | YAMNet Embeddings (1024) + Phonation Stats (6) | YAMNet (1024) + Phonation (6) + Subband Filterbank (11) |
| **Checkpoint Path** | `backend/research/stage_8_9_39/checkpoints/config_b/best_model.pt` | `backend/research/stage_8_9_39/checkpoints/config_d/best_model.pt` |
| **Checkpoint SHA-256** | `037be323c73202b2fb2f95415796ba147ff506bb47f2d66df27d99be41cfe527` | `be0b160df7f92d250720d880f8f876d3a599b92b5c9960f8eb4a8d7fae171d1b` |
| **Platt Calibrator** | Logistic Regression Calibrator | Logistic Regression Calibrator |
| **Frozen Decision Threshold ($\theta$)** | **0.2400** | **0.3400** |

---

## 3. Evaluation on Stage 8.9.40 New Independent Cohort ($N=145$)

The New Independent Cohort consists exclusively of 145 challenging out-of-sample negative recordings ($N_{pos}=0, N_{neg}=145$) across 79 source groups.

| Metric | Configuration B ($\theta=0.24$) | Configuration D ($\theta=0.34$) |
|---|:---:|:---:|
| **True Negatives (TN)** | 144 | 143 |
| **False Positives (FP)** | 1 | 2 |
| **Hard-Negative FPR** | **0.69%** (1 / 145) | **1.38%** (2 / 145) |
| **95% Wilson Score CI (FPR)** | **[0.12%, 3.80%]** | **[0.38%, 4.89%]** |
| **Source-Group Level FPR** | **1.27%** (1 / 79) [0.22%, 6.83%] | **2.53%** (2 / 79) [0.70%, 8.77%] |
| **Brier Score** | **0.0105** | **0.0118** |

### Granular Category-Specific False Positive Rates ($N=145$):

| Category | Total Clips | Config B FP (FPR) [95% CI] | Config D FP (FPR) [95% CI] |
|---|:---:|:---:|:---:|
| **Shouted Speech & Shouting** | 54 | **0 / 54 (0.00%)** [0.00%, 6.64%] | **0 / 54 (0.00%)** [0.00%, 6.64%] |
| **Crowd Chanting & Cheering** | 30 | **0 / 30 (0.00%)** [0.00%, 11.35%] | **0 / 30 (0.00%)** [0.00%, 11.35%] |
| **Whistles & Screeches** | 21 | **0 / 21 (0.00%)** [0.00%, 15.46%] | **1 / 21 (4.76%)** [0.85%, 22.67%] |
| **Infant Crying** | 15 | **1 / 15 (6.67%)** [1.19%, 29.82%] | **1 / 15 (6.67%)** [1.19%, 29.82%] |
| **Sirens, Fireworks & SFX** | 15 | **0 / 15 (0.00%)** [0.00%, 20.39%] | **0 / 15 (0.00%)** [0.00%, 20.39%] |
| **General Environmental Noise** | 10 | **0 / 10 (0.00%)** [0.00%, 27.75%] | **0 / 10 (0.00%)** [0.00%, 27.75%] |

---

## 4. Evaluation on Stage 8.9.39 Frozen Expansion Benchmark Snapshot ($N=102$)

The expansion test snapshot consists of 65 short screams ($d \le 0.70 \text{ s}$) across 35 reserved groups and 37 hard negatives across 14 groups.

| Metric | Configuration B ($\theta=0.24$) | Configuration D ($\theta=0.34$) |
|---|:---:|:---:|
| **True Positives (TP)** | 65 | 65 |
| **False Negatives (FN)** | 0 | 0 |
| **True Negatives (TN)** | 37 | 37 |
| **False Positives (FP)** | 0 | 0 |
| **Overall Scream Recall** | **100.00%** (65 / 65) [94.42%, 100.00%] | **100.00%** (65 / 65) [94.42%, 100.00%] |
| **Short-Scream Recall ($d \le 1.0\text{s}$)** | **100.00%** (65 / 65) [94.42%, 100.00%] | **100.00%** (65 / 65) [94.42%, 100.00%] |
| **Hard-Negative FPR** | **0.00%** (0 / 37) [0.00%, 9.41%] | **0.00%** (0 / 37) [0.00%, 9.41%] |
| **Precision** | **100.00%** (65 / 65) | **100.00%** (65 / 65) |
| **F1-Score** | **1.0000** | **1.0000** |
| **ROC-AUC** | **1.0000** | **1.0000** |
| **PR-AUC** | **1.0000** | **1.0000** |
| **Brier Score** | **0.0028** | **0.0019** |

---

## 5. Evaluation on Historical Continuity Benchmark ($N=293$)

To guarantee historical backwards compatibility and measure drift against the legacy Stage 5 benchmark, both models were evaluated under View A (Original labels) and View B (Adjudicated labels):

| Metric | Config B (View A) | Config B (View B) | Config D (View A) | Config D (View B) |
|---|:---:|:---:|:---:|:---:|
| **TP / FN** | 130 / 2 | 130 / 0 | 129 / 3 | 129 / 1 |
| **TN / FP** | 160 / 1 | 160 / 3 | 161 / 0 | 161 / 2 |
| **Scream Recall** | **98.48%** (130/132) | **100.00%** (130/130) | **97.73%** (129/132) | **99.23%** (129/130) |
| **95% Wilson CI (Recall)** | [94.63%, 99.59%] | [97.13%, 100.00%] | [93.54%, 99.24%] | [95.79%, 99.87%] |
| **Hard-Negative FPR** | **0.62%** (1/161) | **1.84%** (3/163) | **0.00%** (0/161) | **1.23%** (2/163) |
| **95% Wilson CI (FPR)** | [0.11%, 3.43%] | [0.63%, 5.26%] | [0.00%, 2.30%] | [0.34%, 4.36%] |
| **Precision** | 99.24% (130/131) | 97.74% (130/133) | 100.00% (129/129) | 98.47% (129/131) |
| **F1-Score** | 0.9886 | 0.9886 | 0.9885 | 0.9885 |
| **ROC-AUC** | 0.9987 | 0.9987 | 0.9991 | 0.9991 |

---

## 6. Comparative Model Synthesis

1. **Hard-Negative Generalization:** Configuration B achieved slightly superior rejection on the new independent cohort, incurring only 1 false alarm (0.69% FPR) versus 2 false alarms for Configuration D (1.38% FPR).
2. **Shouted-Speech Robustness:** Both configurations demonstrated flawless rejection of shouted speech (0 / 54 false positives, 0.00% FPR, 95% Wilson CI upper bound: 6.64%).
3. **Short-Scream Sensitivity:** Both configurations maintained perfect recall (65 / 65, 100%) on reserved short screams.
4. **Historical Stability:** Both models demonstrated parity or slight superiority compared to Stage 5 production logistic regression baseline.

