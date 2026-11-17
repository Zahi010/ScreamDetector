# Stage 8.9.39 — Configuration B (DualEncoderAcousticModel) Retraining Report

**Project:** Festival Scream Detector  
**Stage:** 8.9.39 — Controlled Retraining, Expanded Dataset Evaluation & Independent Generalization Audit  
**Author:** Principal Acoustic AI Research Scientist & ML Validation Auditor  
**Date:** November 2026  
**Status:** Completed  
**Mandatory Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  

---

## 1. Model Architecture Specification

Configuration B reproduces the frozen Stage 8.9.33 / Stage 8.9.38 Dual-Encoder Acoustic Phonation baseline architecture:
- **Model Code:** `Config_B` (`DualEncoderAcousticModel`)
- **Semantic Stream:** 1024-dimensional YAMNet mean embeddings.
  - Pathway: $\text{Linear}(1024 \to 256) \to \text{BatchNorm1d} \to \text{ReLU} \to \text{Dropout}(0.15) \to \text{Linear}(256 \to 128) \to L_2\text{-norm}$.
- **Phonation Stream:** 12-dimensional acoustic vocal features (pitch, voicing, jitter, shimmer, HNR, F0 mean) with concatenated missing-indicator mask.
  - Pathway: $\text{Linear}(12 \to 64) \to \text{BatchNorm1d} \to \text{ReLU} \to \text{Dropout}(0.10) \to \text{Linear}(64 \to 32) \to L_2\text{-norm}$.
- **Subband Pathway:** None (`null`).
- **Fusion Classifier:** Concatenation ($128 + 32 = 160$ dimensions) $\to \text{Linear}(160 \to 64) \to \text{ReLU} \to \text{Dropout}(0.10) \to \text{Linear}(64 \to 1)$.
- **Output:** Logit / Sigmoid activation.
- **Total Trainable Parameters:** 309,217.
- **Checkpoint Location:** `backend/research/stage_8_9_39/checkpoints/config_b/best_model.pt`.

---

## 2. Experimental Protocol & Matched Training Conditions

Retraining was conducted under strict protocol parity defined in `controlled_retraining_protocol.json`:
- **Training Cohort:** `v4_train` ($N=820$ active clips: 180 screams, 640 non-screams across 324 source groups).
- **Validation Cohort:** `v4_val` ($N=339$ active clips: 83 screams, 256 non-screams across 114 source groups).
- **Feature Normalization:** Standard scaling ($\mu, \sigma$) fit exclusively on `v4_train` ($N=820$). Zero contamination from validation or test splits.
- **Deep Learning Framework:** PyTorch 2.14.1+cpu.
- **Optimizer:** AdamW ($\text{learning\_rate} = 10^{-3}$, $\text{weight\_decay} = 10^{-4}$).
- **Batch Size:** 64.
- **Maximum Epochs:** 35.
- **Loss Function:** Binary Cross Entropy with Logits plus Supervised Contrastive Loss ($\text{BCEWithLogitsLoss} + 0.5 \cdot \text{SupConLoss}(\tau=0.05)$).
- **Early Stopping:** Monitor validation F1 score, patience = 8 epochs.
- **Random Seed:** 42 (deterministic initialization, single-seed evaluation).

---

## 3. Training Dynamics & Checkpoint Selection

Training progressed for 18 epochs before the early-stopping patience triggered:
- **Total Training Duration:** 1.85 seconds.
- **Best Validation Epoch:** Epoch 10.
- **Best Validation F1:** 0.7619 (at nominal $\theta=0.50$); reaching 0.7784 after validation threshold optimization ($\theta=0.24$).

### Key Epoch History:

| Epoch | Train Total Loss | Train BCE Loss | Train SupCon Loss | Val Loss | Val F1 | Val Recall | Val Precision | Val PR-AUC | Val ROC-AUC |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 3.0780 | 0.6215 | 4.9131 | 0.5857 | 0.3934 | 1.0000 | 0.2448 | 0.5846 | 0.7422 |
| 2 | 2.5776 | 0.5342 | 4.0870 | 0.5439 | 0.0000 | 0.0000 | 0.0000 | 0.6660 | 0.8203 |
| 4 | 2.4771 | 0.4676 | 4.0190 | 0.4898 | 0.4144 | 0.2771 | 0.8214 | 0.6720 | 0.8004 |
| 6 | 2.3850 | 0.3860 | 3.9980 | 0.4234 | 0.5512 | 0.4217 | 0.7955 | 0.7293 | 0.8670 |
| 8 | 2.3012 | 0.3015 | 3.9994 | 0.3754 | 0.7050 | 0.5904 | 0.8750 | 0.7654 | 0.8988 |
| **10 (Best)** | **2.2458** | **0.2441** | **4.0034** | **0.3621** | **0.7619** | **0.6747** | **0.8750** | **0.7980** | **0.9182** |
| 12 | 2.2045 | 0.2012 | 4.0066 | 0.3742 | 0.7451 | 0.6867 | 0.8143 | 0.7912 | 0.9125 |
| 15 | 2.1634 | 0.1589 | 4.0090 | 0.4011 | 0.7308 | 0.6867 | 0.7808 | 0.7845 | 0.9056 |
| 18 (Stop) | 2.1321 | 0.1278 | 4.0086 | 0.4356 | 0.7180 | 0.6747 | 0.7671 | 0.7760 | 0.8992 |

*Observations:*
1. Contrastive regularization rapidly clustered embeddings within the first 6 epochs, stabilizing the representation.
2. Minimum validation loss (0.3621) and peak validation PR-AUC (0.7980) coincided at Epoch 10.
3. Overfitting became noticeable after Epoch 14 as training loss continued to decline while validation loss drifted upward to 0.4356. Early stopping halted training appropriately at Epoch 18.

---

## 4. Validation Operating Points

Sweeping thresholds $\theta \in [0.05, 0.95]$ in increments of $0.01$ over `v4_val` ($N=339$) yielded the following operational frontiers:

| Operating Point | Threshold ($\theta$) | TP | FP | TN | FN | Precision | Recall | F1 | Specificity | HN-FPR | Shout-FPR | Short-Scream Recall |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Max F1 (Selected)** | **0.24** | **72** | **30** | **226** | **11** | **70.59%** | **86.75%** | **0.7784** | **88.28%** | **11.72%** | **11.24%** (10/89) | **100.0%** (10/10) |
| Recall-Oriented | 0.12 | 75 | 77 | 179 | 8 | 49.34% | 90.36% | 0.6383 | 69.92% | 30.08% | 26.97% (24/89) | 100.0% (10/10) |
| FA-Oriented | 0.29 | 67 | 25 | 231 | 16 | 72.83% | 80.72% | 0.7657 | 90.23% | 9.77% | 8.99% (8/89) | 100.0% (10/10) |
| Balanced Operational | 0.24 | 72 | 30 | 226 | 11 | 70.59% | 86.75% | 0.7784 | 88.28% | 11.72% | 11.24% (10/89) | 100.0% (10/10) |

*Decision Rule:* Threshold $\theta = 0.24$ was selected as the primary operating point maximizing validation F1 and short-scream recall.

---

## 5. Artifacts and Provenance

- **Saved Model Checkpoint:** `backend/research/stage_8_9_39/checkpoints/config_b/best_model.pt` (SHA-256 verified)
- **Validation Predictions:** `backend/research/stage_8_9_39/predictions/validation/config_b_val_predictions.csv`
- **Training Curve Data:** `backend/research/stage_8_9_39/results/training/config_b_training_history.csv`
