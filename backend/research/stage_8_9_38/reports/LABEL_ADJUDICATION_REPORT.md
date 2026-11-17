# Stage 8.9.38 — Label Adjudication & Dual Historical Evaluation Report

**Project:** Festival Scream Detector  
**Stage:** 8.9.38 — Dataset Integration, Independent Cohort Construction & Controlled Retraining Preparation  
**Author:** Principal Acoustic AI Research Scientist & ML Validation Auditor  
**Date:** November 2026  
**Status:** Completed  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE

---

## 1. Investigation of Suspected Positive-Label Anomalies

In Stage 8.9.36 and Stage 8.9.37, false-negative forensics identified two test recordings with anomalous acoustic properties:
1. `v2_nigens_242607__reitanna__gasp-oooh` (Duration: $1.324\text{ s}$, RMS: $0.368$, Mean F0: $0.7\text{ kHz}$, Scream Band Ratio: $0.103$).
2. `v2_nigens_242644__reitanna__another-surprised-oooh` (Duration: $1.498\text{ s}$, RMS: $0.436$, Mean F0: $0.8\text{ kHz}$, Scream Band Ratio: $0.036$).

Both files were introduced in dataset v2 as `scream` under source group `nigens_reitanna` and assigned to the test cohort.

### 1.1 Blinded Adjudication Protocol
In Stage 8.9.37, both recordings were presented to two independent acoustic engineers without model predictions or historical classification labels:
- **Reviewer 1 (Acoustic Specialist):** Classified both as `non_scream`. Finding: "Inspiratory gasp and relaxed glottal release; lacks sustained high-F0 phonation and 2.5–4.5 kHz resonance."
- **Reviewer 2 (DSP Engineer):** Classified both as `non_scream`. Finding: "Conversational surprised sigh ('oooh'); peak spectral energy concentrated below 800 Hz; no panic or forced vocal fold tension."
- **Adjudication Agreement:** **Unanimous (2/2) Non-Scream**.

---

## 2. Model Prediction Forensics

Every trained research candidate assigned extremely low scream probabilities to these recordings:

| Model Candidate | `gasp-oooh` Predicted Prob | `another-surprised-oooh` Predicted Prob | Classification at Threshold |
|---|---|---|---|
| **Config A (YAMNet-Only)** | 0.3369 | 0.3284 | Predicted 0 (Non-Scream at $\theta=0.38$) |
| **Config B (Dual-Encoder)** | 0.0008 | 0.0014 | Predicted 0 (Non-Scream at $\theta=0.44$) |
| **Config C (YAMNet+Subband)** | 0.2589 | 0.2589 | Predicted 0 (Non-Scream at $\theta=0.30$) |
| **Config D (MP-FS-DualEnc)** | 0.0407 | 0.0273 | Predicted 0 (Non-Scream at $\theta=0.43$) |

Because both files were labeled as positive `scream` in historical evaluation, they were penalized as False Negatives (FN) across all candidates, artificially depressing reported scream recall by up to $1.96\%$.

---

## 3. Dual Historical Evaluation Accounting

To maintain strict scientific integrity without retrospective metric manipulation, Stage 8.9.38 established **two separate official evaluation views** documented in [`dual_view_historical_metrics.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_38/audits/dual_view_historical_metrics.csv):

- **View A — Original-Label Historical Baseline ($N=293$: 102 screams, 191 hard negatives):**
  Preserves the exact historical ground truth without alteration.
- **View B — Adjudicated-Label Analytical View ($N=293$: 100 screams, 193 hard negatives):**
  Reclassifies the two unanimous non-scream recordings as negative, converting 2 False Negatives into True Negatives.

### Detailed Comparison Table:

| Model Candidate | Operating Threshold $\theta^*$ | View A: Recall ($k/n$) | View B: Recall ($k/n$) | Recall Delta | View A: HN-FPR ($k/n$) | View B: HN-FPR ($k/n$) | HN-FPR Delta |
|---|---|---|---|---|---|---|---|
| **Config A (YAMNet-Only)** | 0.38 | 70.59% (72/102) | 72.00% (72/100) | **+1.41%** | 9.95% (19/191) | 9.84% (19/193) | **-0.11%** |
| **Config B (Dual-Encoder)** | 0.44 | 81.37% (83/102) | 83.00% (83/100) | **+1.63%** | 6.28% (12/191) | 6.22% (12/193) | **-0.06%** |
| **Config C (YAMNet+Subband)**| 0.30 | 78.43% (80/102) | 80.00% (80/100) | **+1.57%** | 10.47% (20/191) | 10.36% (20/193) | **-0.11%** |
| **Config D (MP-FS-DualEnc)** | 0.43 | 89.22% (91/102) | **91.00% (91/100)** | **+1.78%** | 9.95% (19/191) | **9.84% (19/193)** | **-0.11%** |

*Note on Shouted-Speech FPR:* Because neither disputed recording belongs to the shouted speech category, Shouted-Speech FPR is identical under both views (Config D: $7/48 = 14.58\%$).

---

## 4. Policy Decision & Training Isolation

1. **Test Cohort Action:** In strict accordance with Section 4 ("Do not remove difficult examples merely to improve recall"), **both recordings are retained in the active historical test cohort**. Historical metric baselines remain governed by View A for cross-stage continuity, with View B reported as secondary analytical evidence.
2. **Training Quarantine:** Both recordings are **permanently quarantined from all future training and validation pools** to prevent corrupting gradient updates with non-scream acoustic patterns.
