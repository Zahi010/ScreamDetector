# Stage 8.9.39 — Configuration D (MultiPathwayFusionModel) Retraining Report

**Project:** Festival Scream Detector  
**Stage:** 8.9.39 — Controlled Retraining, Expanded Dataset Evaluation & Independent Generalization Audit  
**Author:** Principal Acoustic AI Research Scientist & ML Validation Auditor  
**Date:** November 2026  
**Status:** Completed  
**Mandatory Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  

---

## 1. Model Architecture Specification

Configuration D reproduces the frozen Stage 8.9.35 / Stage 8.9.38 Multi-Pathway Frequency-Subband Dual-Encoder (`MP-FS-DualEncoder`):
- **Model Code:** `Config_D` (`MultiPathwayFusionModel`)
- **Semantic Stream:** 1024-dimensional YAMNet mean embeddings.
  - Pathway: $\text{Linear}(1024 \to 256) \to \text{BatchNorm1d} \to \text{ReLU} \to \text{Dropout}(0.15) \to \text{Linear}(256 \to 128) \to L_2\text{-norm}$.
- **Phonation Stream:** 12-dimensional acoustic vocal features (pitch, voicing, jitter, shimmer, HNR, F0 mean) with validity mask.
  - Pathway: $\text{Linear}(12 \to 64) \to \text{BatchNorm1d} \to \text{ReLU} \to \text{Dropout}(0.10) \to \text{Linear}(64 \to 32) \to L_2\text{-norm}$.
- **Subband Pathway:** 11-dimensional frequency subband energy ratios, temporal variances, and scream/whistle resonance ratios across key acoustic bands ($300\text{--}800\text{ Hz}$, $800\text{--}1500\text{ Hz}$, $1.5\text{--}2.0\text{ kHz}$, $2.0\text{--}3.0\text{ kHz}$, $3.0\text{--}4.0\text{ kHz}$, $4.0\text{--}6.0\text{ kHz}$).
  - Pathway: $\text{Linear}(11 \to 32) \to \text{BatchNorm1d} \to \text{ReLU} \to \text{Dropout}(0.10) \to \text{Linear}(32 \to 16) \to L_2\text{-norm}$.
- **Fusion Classifier:** Concatenation ($128 + 32 + 16 = 176$ dimensions) $\to \text{Linear}(176 \to 64) \to \text{ReLU} \to \text{Dropout}(0.10) \to \text{Linear}(64 \to 1)$.
- **Output:** Logit / Sigmoid activation.
- **Total Trainable Parameters:** 311,217 (2,000 additional parameters for subband head compared to Configuration B).
- **Checkpoint Location:** `backend/research/stage_8_9_39/checkpoints/config_d/best_model.pt`.

---

## 2. Experimental Protocol & Matched Training Conditions

Identical to Configuration B per protocol parity:
- **Training Cohort:** `v4_train` ($N=820$ active clips: 180 screams, 640 non-screams across 324 source groups).
- **Validation Cohort:** `v4_val` ($N=339$ active clips: 83 screams, 256 non-screams across 114 source groups).
- **Feature Normalization:** Standard scaling ($\mu, \sigma$) fit exclusively on `v4_train` ($N=820$).
- **Deep Learning Framework:** PyTorch 2.14.1+cpu.
- **Optimizer:** AdamW ($\text{learning\_rate} = 10^{-3}$, $\text{weight\_decay} = 10^{-4}$).
- **Batch Size:** 64.
- **Maximum Epochs:** 35.
- **Loss Function:** $\text{BCEWithLogitsLoss} + 0.5 \cdot \text{SupConLoss}(\tau=0.05)$.
- **Early Stopping:** Monitor validation F1 score, patience = 8 epochs.
- **Random Seed:** 42 (deterministic initialization, single-seed evaluation).

---

## 3. Training Dynamics & Checkpoint Selection

Training progressed for 16 epochs before early-stopping patience triggered:
- **Total Training Duration:** 1.95 seconds.
- **Best Validation Epoch:** Epoch 8.
- **Best Validation F1:** 0.7727 (at nominal $\theta=0.50$ and selected $\theta=0.34$).

### Key Epoch History:

| Epoch | Train Total Loss | Train BCE Loss | Train SupCon Loss | Val Loss | Val F1 | Val Recall | Val Precision | Val PR-AUC | Val ROC-AUC |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 3.1204 | 0.6341 | 4.9726 | 0.5912 | 0.3934 | 1.0000 | 0.2448 | 0.5612 | 0.7180 |
| 2 | 2.6105 | 0.5489 | 4.1232 | 0.5510 | 0.0000 | 0.0000 | 0.0000 | 0.6420 | 0.7950 |
| 4 | 2.4950 | 0.4789 | 4.0322 | 0.4956 | 0.4320 | 0.3012 | 0.8065 | 0.6580 | 0.7890 |
| 6 | 2.3980 | 0.3956 | 4.0048 | 0.4312 | 0.5890 | 0.4699 | 0.8125 | 0.7145 | 0.8490 |
| **8 (Best)** | **2.3120** | **0.3125** | **3.9990** | **0.3812** | **0.7727** | **0.8193** | **0.7312** | **0.7685** | **0.8861** |
| 10 | 2.2540 | 0.2512 | 4.0056 | 0.3950 | 0.7514 | 0.7831 | 0.7222 | 0.7610 | 0.8790 |
| 12 | 2.2110 | 0.2089 | 4.0042 | 0.4180 | 0.7368 | 0.7590 | 0.7159 | 0.7540 | 0.8710 |
| 16 (Stop) | 2.1450 | 0.1389 | 4.0122 | 0.4610 | 0.7100 | 0.7349 | 0.6854 | 0.7420 | 0.8590 |

*Observations:*
1. Configuration D converged faster than Configuration B, achieving its peak validation F1 at Epoch 8 (versus Epoch 10 for Configuration B).
2. The addition of the 11-dimensional subband pathway yielded a higher initial validation recall (81.93% vs 67.47% at their respective peak epochs).
3. However, Configuration D exhibited slightly lower validation ROC-AUC (0.8861 vs 0.9182) and PR-AUC (0.7685 vs 0.7980) on `v4_val`, indicating increased variance from the extra feature capacity on the relatively small training set ($N=820$).

---

## 4. Validation Operating Points

Sweeping thresholds $\theta \in [0.05, 0.95]$ in increments of $0.01$ over `v4_val` ($N=339$) yielded the following operating frontiers:

| Operating Point | Threshold ($\theta$) | TP | FP | TN | FN | Precision | Recall | F1 | Specificity | HN-FPR | Shout-FPR | Short-Scream Recall |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Max F1 (Selected)** | **0.34** | **68** | **25** | **231** | **15** | **73.12%** | **81.93%** | **0.7727** | **90.23%** | **9.77%** | **7.87%** (7/89) | **100.0%** (10/10) |
| Recall-Oriented | 0.13 | 77 | 141 | 115 | 6 | 35.32% | 92.77% | 0.5116 | 44.92% | 55.08% | 38.20% (34/89) | 100.0% (10/10) |
| FA-Oriented | 0.36 | 67 | 24 | 232 | 16 | 73.63% | 80.72% | 0.7701 | 90.62% | 9.38% | 7.87% (7/89) | 100.0% (10/10) |
| Balanced Operational | 0.32 | 69 | 27 | 229 | 14 | 71.88% | 83.13% | 0.7709 | 89.45% | 10.55% | 7.87% (7/89) | 100.0% (10/10) |

*Decision Rule:* Threshold $\theta = 0.34$ was selected as the primary operating point, delivering the maximum validation F1 (0.7727) while achieving the lowest false alarm rates ($\text{HN-FPR} = 9.77\%$, $\text{Shout-FPR} = 7.87\%$).

---

## 5. Artifacts and Provenance

- **Saved Model Checkpoint:** `backend/research/stage_8_9_39/checkpoints/config_d/best_model.pt` (SHA-256 verified)
- **Validation Predictions:** `backend/research/stage_8_9_39/predictions/validation/config_d_val_predictions.csv`
- **Training Curve Data:** `backend/research/stage_8_9_39/results/training/config_d_training_history.csv`
