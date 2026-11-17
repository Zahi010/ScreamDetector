# Stage 8.9.38 — Controlled Retraining Readiness Report

**Project:** Festival Scream Detector  
**Stage:** 8.9.38 — Dataset Integration, Independent Cohort Construction & Controlled Retraining Preparation  
**Author:** Principal Acoustic AI Research Scientist & ML Validation Auditor  
**Date:** November 2026  
**Status:** Completed (Ready for Controlled Retraining Execution in Stage 8.9.39)  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE

---

## 1. Executive Summary

Stage 8.9.38 established the complete data foundation, source-group-isolated partitions, and experimental configurations necessary to execute **controlled retraining** in the next research stage (Stage 8.9.39).

Per non-negotiable instructions, **no model training was performed in Stage 8.9.38**. All work was dedicated to ensuring experimental integrity, feature alignment, and rigorous protocol specification.

---

## 2. Model Candidates for Controlled Comparison

Retraining will focus strictly on the head-to-head comparison between **Configuration B** and **Configuration D**:

### 2.1 Configuration B: Dual-Encoder Acoustic Phonation Baseline
- **Specification:** [`config_b_dual_encoder_spec.json`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_38/experiment_configs/config_b_dual_encoder_spec.json)
- **Input Channels:**
  1. Semantic Stream: 1024-dimensional YAMNet mean embeddings.
  2. Phonation Stream: 12-dimensional acoustic vocal features (pitch, voicing, jitter, shimmer, HNR, F0 mean) with concatenated missing-indicator mask.
- **Projection Architecture:** $\text{SemanticHead}(1024 \to 128) + \text{PhonationHead}(12 \to 32) \to \text{Linear}(160 \to 1)$.
- **Role:** Primary reference baseline to evaluate whether subband frequency pathways provide genuine value over phonation alone.

### 2.2 Configuration D: Multi-Pathway Frequency-Subband Dual-Encoder (MP-FS-DualEncoder)
- **Specification:** [`config_d_multipathway_spec.json`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_38/experiment_configs/config_d_multipathway_spec.json)
- **Input Channels:**
  1. Semantic Stream: 1024-dimensional YAMNet mean embeddings.
  2. Phonation Stream: 12-dimensional acoustic vocal features + validity mask.
  3. Frequency-Subband Stream: 11-dimensional subband energy ratios, temporal variances, and scream/whistle ratios ($300\text{--}800\text{ Hz}$, $800\text{--}1500\text{ Hz}$, $1.5\text{--}2.0\text{ kHz}$, $2.0\text{--}3.0\text{ kHz}$, $3.0\text{--}4.0\text{ kHz}$, $4.0\text{--}6.0\text{ kHz}$).
- **Projection Architecture:** $\text{SemanticHead}(1024 \to 128) + \text{PhonationHead}(12 \to 32) + \text{SubbandHead}(11 \to 16) \to \text{Linear}(176 \to 1)$.
- **Role:** Leading research candidate exhibiting superior recall and false-alarm suppression in Stage 8.9.36 and 8.9.37.

---

## 3. Controlled Retraining Protocol

Full execution settings are frozen in [`controlled_retraining_protocol.json`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_38/experiment_configs/controlled_retraining_protocol.json):

1. **Cohort Standardization:**
   - Training: `v4_train` ($N=820$ active, 180 screams, 640 negatives across 324 source groups).
   - Validation: `v4_val` ($N=339$ active, 83 screams, 256 negatives across 114 source groups).
   - Independent Test 1 (Historical Baseline): `v4_historical_test` ($N=293$, 102 screams, 191 negatives).
   - Independent Test 2 (Reserved Expansion): `v4_reserved_expansion_test` ($N=102$, 65 short screams, 37 negatives across 49 source groups).
2. **Deterministic Hyperparameters:**
   - Random seed: `42`.
   - Optimizer: AdamW ($\text{lr} = 10^{-3}$, $\text{weight\_decay} = 10^{-4}$).
   - Batch size: 64.
   - Max epochs: 35 with early stopping patience of 8 epochs monitored on validation F1.
3. **Threshold & Calibration Protocol:**
   - Threshold sweeps $\theta \in [0.05, 0.95]$ in $0.01$ increments on validation only.
   - Four validation operating points selected per candidate (Max F1, Recall-oriented, FA-oriented, Balanced).
   - Platt scaling fit strictly on validation data.
   - Thresholds and calibrators frozen before test cohort exposure.

---

## 4. Five Research Acceptance Gates

Every candidate in the subsequent retraining stage will be evaluated against all five mandatory gates on both test cohorts:
1. Overall scream recall $\ge 96\%$.
2. Hard-negative false-positive rate $\le 5\%$.
3. Shouted-speech false-positive rate $\le 15\%$.
4. Short-scream recall $\ge 90\%$.
5. Computational P95 inference latency $\le 25\text{ ms}$.
