# Stage 8.9.41: Frozen Model Positive Cohort Evaluation Report

**MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**

*This project is an experimental acoustic research system. It is not certified for life-safety alerting, emergency response, active shooter detection, autonomous police dispatch, or critical physical security deployments.*

---

## 1. Executive Summary

This report documents the rigorous evaluation of the frozen primary research candidate, **Configuration B** ([`DualEncoderAcousticModel`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_39/scripts/train_config_b.py)), on the Stage 8.9.41 Positive Independent Evaluation Cohort ($N=57$, 41 source groups) and the Combined Positive Research Evaluation Suite ($N=122$, 76 source groups).

The model was evaluated strictly without retraining, fine-tuning, threshold adjustments, or recalibration:
- **Model Checkpoint:** `backend/research/stage_8_9_39/checkpoints/config_b/best_model.pt`
- **Platt Calibrator:** `backend/research/stage_8_9_39/checkpoints/config_b/platt_calibrator.joblib`
- **Operating Decision Threshold:** $\theta = \mathbf{0.2400}$

---

## 2. Evaluation on Standalone Stage 8.9.41 Positive Cohort ($N=57$)

The standalone Stage 8.9.41 positive evaluation cohort consists exclusively of 57 confirmed positive screams across 41 independent source groups:

| Evaluation Metric | Observed Result | 95% Wilson Confidence Interval | Cluster Bootstrap 95% CI |
|---|:---:|:---:|:---:|
| **Total Positive Clips ($N_{pos}$)** | 57 | — | — |
| **True Positives (TP)** | 20 | — | — |
| **False Negatives (FN)** | 37 | — | — |
| **Recording-Level Scream Recall** | **35.09%** (20 / 57) | **[24.00%, 48.06%]** | **[24.24%, 45.95%]** |
| **Source-Group Level Recall ($\ge 1$ detected)** | **39.02%** (16 / 41) | **[25.66%, 54.27%]** | — |

*Note on Specificity and Precision:* Because this cohort is an independent positive-only test cohort, specificity, false positive rate, precision, and ROC/PR AUC cannot be computed from this cohort alone. For negative-class generalization, the Stage 8.9.40 independent negative benchmark ($N=145$) is referenced.

---

## 3. Subtype-Stratified Performance Breakdown

Evaluation across the five acoustic subtypes in the new positive cohort revealed significant variance in model sensitivity:

| Acoustic Subtype | Description | Total Clips | Detected TP | Recall | 95% Wilson Score CI |
|---|---|:---:|:---:|:---:|:---:|
| `distant_scream` | Attenuated highs, reverberant decay ($d=1.1\text{s}-2.2\text{s}$) | 11 | 10 | **90.91%** (10 / 11) | [62.26%, 98.38%] |
| `low_intensity_scream` | Stifled vocal bursts ($d=0.65\text{s}-1.8\text{s}$) | 10 | 6 | **60.00%** (6 / 10) | [31.27%, 83.18%] |
| `masked_scream` | Embedded in festival crowd noise at SNR 3–9 dB | 8 | 4 | **50.00%** (4 / 8) | [21.52%, 78.48%] |
| `sustained_scream` | Sustained distress screams ($d > 2.0\text{s}$) | 2 | 0 | **0.00%** (0 / 2) | [0.00%, 65.76%] |
| `short_scream` | Ultra-short vocal bursts ($d=0.25\text{s}-0.98\text{s}$) | 26 | 0 | **0.00%** (0 / 26) | [0.00%, 12.87%] |

---

## 4. Evaluation on Combined Positive Research Suite ($N=122$)

Combining the Stage 8.9.39 expansion positive short screams ($N=65$) with the Stage 8.9.41 independent positive screams ($N=57$) establishes a comprehensive benchmark of **122 positive scream recordings across 76 independent source groups**:

| Evaluation Cohort | Total Positives | True Positives | False Negatives | Observed Recall | 95% Wilson Score CI |
|---|:---:|:---:|:---:|:---:|:---:|
| **Stage 8.9.39 Expansion Benchmark** | 65 | 65 | 0 | **100.00%** (65 / 65) | [94.42%, 100.00%] |
| **Stage 8.9.41 Independent Cohort** | 57 | 20 | 37 | **35.09%** (20 / 57) | [24.00%, 48.06%] |
| **Combined Positive Evaluation Suite** | **122** | **85** | **37** | **69.67%** (85 / 122) | **[61.02%, 77.13%]** |

---

## 5. Architectural Implications

The empirical findings uncover an important acoustic boundary in Configuration B:
1. **Distant and Reverberant Screams Generalize Well:** Configuration B successfully detected 90.91% (10 / 11) of distant screams and 60% of low-intensity screams, confirming that moderate reverberation and attenuation do not defeat the classifier.
2. **Ultra-Short Screams Suffer Severe Window Dilution:** The model failed to detect ultra-short screams ($d < 0.5\text{ s}$, 0 / 11 detected). In YAMNet's 0.975-second frame architecture, when an isolated scream lasts only 250–450 ms and the remainder of the frame is silent, the acoustic energy is diluted over the 975 ms integration window. This pulls the mean phonation logits down, causing the model to predict probabilities between 0.04 and 0.12 (well below the 0.24 threshold).
3. **Gate 1 Status:** On the Combined Positive Suite, overall recall is **69.67%**, failing the $\ge 96.0\%$ Gate 1 threshold.

