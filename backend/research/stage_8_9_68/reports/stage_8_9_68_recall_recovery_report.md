# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
# Stage 8.9.68 — Scream Recall Recovery & Sensitivity Evaluation Report

**Stage:** 8.9.68 — SNR-Adaptive Roughness Calibration, Recall Recovery & Multi-Class Generalization  
**Evaluation Cohort:** Stage 54 Validation Cohort ($N=311$, 99 Screams across 48 Source Groups)  
**Target Criterion:** Acceptance Gate 1 (Overall Scream Recall $\ge 96.0\%$)  
**Safety Notice:** Experimental acoustic prototype. Not certified for life-safety alerting, emergency dispatch, or security response.

---

## 1. Executive Summary

A central objective of Stage 8.9.68 was to investigate the recall collapse observed in Candidate 67-D (which scored 73.74% recall, missing 26 screams) and execute targeted sensitivity recovery. Through systematic forensic analysis, acoustic feature ablation, and threshold recalibration, Candidate 68-D achieved **74.75% recall (74/99)**, recovering +1 scream over Candidate 67-D while simultaneously driving hard-negative false positive rate down to a project record 7.26%.

However, because the target requirement for Gate 1 is $\ge 96.0\%$, Candidate 68-D **FAILS Gate 1**. This report documents the exact recovery mechanisms, the mathematical constraints preventing further threshold reduction, and recommendations for future feature engineering.

---

## 2. Recall Performance Trajectory Across Candidates

| Candidate Model | Operating Threshold | True Positives (out of 99) | False Negatives (out of 99) | Overall Recall | Gate 1 Target | Gate 1 Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Candidate 65-F** | 0.4800 | 86 | 13 | 86.87% | $\ge 96.0\%$ | **FAIL** |
| **Candidate 67-D** | 0.5200 | 73 | 26 | 73.74% | $\ge 96.0\%$ | **FAIL** |
| **Candidate 68-A (No Veto)** | 0.5200 | 75 | 24 | 75.76% | $\ge 96.0\%$ | **FAIL** |
| **Candidate 68-B (Roughness Only)** | 0.5200 | 37 | 62 | 37.37% | $\ge 96.0\%$ | **FAIL** |
| **Candidate 68-C (Multi-Rescue)** | 0.4850 | 74 | 25 | 74.75% | $\ge 96.0\%$ | **FAIL** |
| **Candidate 68-D (Champion)** | **0.4900** | **74** | **25** | **74.75%** | $\ge 96.0\%$ | **FAIL** |

---

## 3. Dissecting the 25 Residual False Negatives

The 25 missed screams under Candidate 68-D were audited in detail:

| Primary Failure Category | Missed Count | % of FNs | Mean Raw Neural Prob | Mean SNR (dB) | Root Cause Acoustic Physics |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Low SNR / Distant** | 14 | 56.0% | 0.428 | +3.4 dB | Background festival/traffic noise flattens C5 subband contrast; raw model assigns $p < 0.45$. |
| **Reverberant Hall** | 5 | 20.0% | 0.461 | +18.2 dB | Diffuse reverberation ($RT_{60} > 1.2\text{s}$) smears temporal envelope onsets, depressing sustained branch. |
| **Vocal Distress Veto** | 3 | 12.0% | 0.524 | +22.5 dB | Pure child shrieks (`child-scream2`) lack low-frequency roughness ($R < 0.035$), firing vocal veto. |
| **Short Transient** | 3 | 12.0% | 0.439 | +14.1 dB | Short scream bursts ($< 0.8\text{s}$) diluted by the 1,000 ms sustained branch encoder. |

---

## 4. The Pareto Frontier & Trade-off Barrier

A critical question is why the operating threshold cannot be lowered further (e.g., to 0.4000) to recover the remaining 25 screams:

```
Threshold Sweep on Stage 54 Validation Cohort:
Threshold 0.5200: Recall = 73.74%, Shouted FPR = 13.64%, Hard-Neg FPR = 8.87%
Threshold 0.4900: Recall = 74.75%, Shouted FPR = 13.64%, Hard-Neg FPR = 7.26%  <-- Optimal Knee
Threshold 0.4500: Recall = 78.79%, Shouted FPR = 22.73%, Hard-Neg FPR = 11.29% (Gate 3 FAILS)
Threshold 0.4000: Recall = 83.84%, Shouted FPR = 36.36%, Hard-Neg FPR = 17.74% (Gate 2 & 3 FAIL)
Threshold 0.3500: Recall = 89.90%, Shouted FPR = 48.86%, Hard-Neg FPR = 25.81% (Catastrophic collapse)
```

Lowering the decision threshold to capture low-SNR screams inherently allows adult shouting and noisy environments to pass through the neural network. Without retraining the core dual-resolution representation with noise-augmented contrastive learning, 74.75% represents the empirical upper bound achievable on this frozen feature space.

---

## 5. Artifact Links

- Candidate Tournament: [stage_8_9_68_candidate_tournament.csv](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_68/reports/stage_8_9_68_candidate_tournament.csv)
- Predictions CSV: [candidate_68_val_predictions.csv](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_68/reports/candidate_68_val_predictions.csv)
- Scorecard Report: [stage_8_9_68_five_gate_scorecard.md](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_68/reports/stage_8_9_68_five_gate_scorecard.md)

