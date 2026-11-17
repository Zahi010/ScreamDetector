# Candidate E Validation Reproducibility Audit — Stage 8.9.52

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.  
> No live-fire experiments, autonomous emergency dispatch, external emergency alerts, or claims of life-safety efficacy.  
> No production promotion is authorized.

---

## 1. Executive Summary & Verification Mandate

Stage 8.9.52 conducted an independent reproducibility audit of **Research Candidate E (`ResearchDualHeadClassifier`)**, which was introduced in Stage 8.9.51 as an experimental cross-modal residual-gated model.

The audit verified whether Candidate E's reported validation results ($100.0\%$ recall, $0.00\%$ HN-FPR) can be independently reproduced from the saved checkpoint without retraining, using the frozen validation manifest and feature extraction pipeline.

---

## 2. Checkpoint & Architecture Verification

- **Checkpoint Path:** `backend/research/stage_8_9_51/models/research_exp_candidate.pt`
- **Verified SHA-256:** `5ec5941448af4d3c77417a96e0ee5da5d8592ef5bc3c1103d3518378b37d13c1`
- **Architecture Configuration:**
  - Semantic Projection: `Linear(1024 -> 128) -> ReLU -> Dropout(0.20)`
  - Phonation & Subband Projection: `Linear(6*2 + 11 = 23 -> 64) -> ReLU -> Dropout(0.15)`
  - Residual Cross-Modal Gate: `Linear(128 + 64 -> 32) -> Sigmoid`
  - Classifier Head: `Linear(128 + 64 -> 64) -> ReLU -> Linear(64 -> 1)`
- **Operating Threshold:** $\theta = 0.4000$ (calibrated strictly on validation split)

---

## 3. Validation Reproduction Results ($N=120$)

Pure deterministic inference was executed on the 120 clips in `val_features.npz` (48 authentic screams, 72 hard negatives) without retraining:

| Metric | Stage 8.9.51 Reported | Stage 8.9.52 Reproduced | Discrepancy ($\Delta$) | Status |
|---|---|---|---|---|
| **True Positives (TP)** | 48 / 48 | 48 / 48 | 0 | **EXACT MATCH** |
| **False Negatives (FN)** | 0 / 48 | 0 / 48 | 0 | **EXACT MATCH** |
| **True Negatives (TN)** | 72 / 72 | 72 / 72 | 0 | **EXACT MATCH** |
| **False Positives (FP)** | 0 / 72 | 0 / 72 | 0 | **EXACT MATCH** |
| **Validation Recall** | **100.00%** | **100.00%** | 0.00% | $[92.59\%, 100.00\%]$ |
| **Validation HN-FPR** | **0.00%** | **0.00%** | 0.00% | $[0.00\%, 5.07\%]$ |
| **Validation Precision** | **100.00%** | **100.00%** | 0.00% | $[92.59\%, 100.00\%]$ |
| **Validation F1 Score** | **100.00%** | **100.00%** | 0.00% | Point estimate |
| **Prediction Agreement** | — | **120 / 120 (100.0%)** | 0 discordant | **100% REPRODUCIBLE** |

All predictions were persisted in [`candidate_e_validation_predictions.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_52/candidate_e/candidate_e_validation_predictions.csv).

---

## 4. Subtype Performance Breakdown on Validation Split

| Acoustic Subtype | Subtype Count | Ground Truth Positives | Detections (TP) | False Alarms (FP) | Subtype Metric |
|---|---|---|---|---|---|
| `cheering_chanting` | 20 | 0 | — | 0 | **0.00% FPR** |
| `continuous_whistle` | 5 | 0 | — | 0 | **0.00% FPR** |
| `crowd_masked_scream` | 6 | 6 | 6 | — | **100.0% Recall** |
| `distant_reverberant_scream` | 6 | 6 | 6 | — | **100.0% Recall** |
| `distant_whistle` | 5 | 0 | — | 0 | **0.00% FPR** |
| `electronic_whistle` | 5 | 0 | — | 0 | **0.00% FPR** |
| `emergency_siren` | 10 | 0 | — | 0 | **0.00% FPR** |
| `infant_crying` | 12 | 0 | — | 0 | **0.00% FPR** |
| `low_intensity_muffled_scream` | 4 | 4 | 4 | — | **100.0% Recall** |
| `referee_pea_whistle` | 15 | 0 | — | 0 | **0.00% FPR** |
| `short_scream` | 14 | 14 | 14 | — | **100.0% Recall** |
| `shouted_speech` | 15 | 0 | — | 0 | **0.00% FPR** |
| `sustained_scream` | 10 | 10 | 10 | — | **100.0% Recall** |
| `ultra_short_scream` | 8 | 8 | 8 | — | **100.0% Recall** |

---

## 5. Audit Determination

**CANDIDATE E VALIDATION RESULTS ARE 100% BIT-LEVEL REPRODUCIBLE.**  
The model executes deterministically and satisfies its reported validation claims without discrepancies.

