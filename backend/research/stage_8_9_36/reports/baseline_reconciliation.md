# Stage 8.9.36 — Baseline Reconciliation Audit Report

**Stage:** 8.9.36 — Deep Error Forensics & Validation Audit  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Dimension:** Reconciliation of Stage 8.9.34 vs. Stage 8.9.35 Dual-Encoder Baseline Metrics  
**Audit Artifacts:**
- Prediction Difference Table: `backend/research/stage_8_9_36/evaluation/baseline_prediction_diff.csv`
- Recomputed Metrics JSON: `backend/research/stage_8_9_36/evaluation/baseline_recomputed_metrics.json`

---

## 1. Executive Summary & Root-Cause Finding

A critical apparent discrepancy was identified between Stage 8.9.34 and Stage 8.9.35:
- **Stage 8.9.34 Report:** Dual-Encoder Baseline achieved **84.31% recall (86/102)** and **7.85% HN-FPR (15/191)**.
- **Stage 8.9.35 Report:** Dual-Encoder Baseline achieved **82.35% recall (84/102)** and **6.28% HN-FPR (12/191)**.

### **The Definitive Root Cause:**
The underlying model weights, test recording IDs, labels, source-group partitions, feature representations, and raw model output probabilities are **100% IDENTICAL**.

The difference was caused entirely by the **operating threshold applied in the evaluation comparison table**:
1. Stage 8.9.34 evaluated the Dual-Encoder baseline at the historical threshold **$\theta = 0.3500$**.
2. Stage 8.9.35 evaluated all models in its comparative table (including the baseline) at the new validation-selected candidate threshold **$\theta^* = 0.4300$**.

When evaluated at the exact same threshold, the predictions and metrics are mathematically identical to six decimal places.

---

## 2. Multi-Dimensional Reconciliation Audit Table

| Audit Dimension | Stage 8.9.34 Baseline | Stage 8.9.35 Baseline | Identical? | Forensic Verification Details |
| :--- | :--- | :--- | :---: | :--- |
| **Test Recording IDs** | 293 files (102 screams, 191 HN) | 293 files (102 screams, 191 HN) | **YES** | Exact order & hash matching across all 293 IDs |
| **Ground-Truth Labels** | 102 screams, 191 hard negatives | 102 screams, 191 hard negatives | **YES** | Exact match (0 label changes) |
| **Source-Group Partition**| 111 disjoint test source groups | 111 disjoint test source groups | **YES** | Exact match; zero partition leakage |
| **Model Weights File** | `stage_8_9_33/models/best_dual_encoder.pt` | `stage_8_9_33/models/best_dual_encoder.pt` | **YES** | Same PyTorch state dict loaded |
| **Feature Extraction** | YAMNet 1024-d + Phonation 6-d + Mask | YAMNet 1024-d + Phonation 6-d + Mask | **YES** | Sourced from identical `.npz` feature cache |
| **Inference Preprocessing**| LayerNorm + Masked Phonation Projection | LayerNorm + Masked Phonation Projection | **YES** | Exact neural forward pass |
| **Raw Probabilities** | $P \in [0.0001, 0.9998]$ | $P \in [0.0001, 0.9998]$ | **YES** | Max absolute difference: $0.000000$ |
| **Decision Threshold** | **$\theta = 0.3500$** | **$\theta = 0.4300$** | **NO** | **Root cause of differing report numbers** |
| **Prediction Aggregation**| Max probability over recording | Max probability over recording | **YES** | Identical aggregation |
| **EOF Handling** | Padded trailing residual window | Padded trailing residual window | **YES** | Identical streaming EOF logic |

---

## 3. Mathematical Recalculation from Raw Predictions

Evaluating the exact same baseline model across both operating thresholds yields:

| Metric | Baseline at $\theta = 0.3500$ (Stage 8.9.34 Reporting) | Baseline at $\theta = 0.4300$ (Stage 8.9.35 Reporting) | Delta ($\Delta$) |
| :--- | :---: | :---: | :---: |
| **True Positives (TP)** | 86 / 102 | 84 / 102 | -2 screams |
| **False Negatives (FN)** | 16 / 102 | 18 / 102 | +2 screams |
| **False Positives (FP)** | 15 / 191 | 12 / 191 | -3 false alarms |
| **True Negatives (TN)** | 176 / 191 | 179 / 191 | +3 correct rejections |
| **Scream Recall** | **84.31%** | **82.35%** | **-1.96%** |
| **Hard-Negative FPR** | **7.85%** | **6.28%** | **-1.57%** |
| **Shouted-Speech FPR** | **8.33% (4/48)** | **8.33% (4/48)** | **0.00%** |
| **Infant-Cry FPR** | **6.67% (1/15)** | **6.67% (1/15)** | **0.00%** |
| **Precision** | 85.15% | 87.50% | +2.35% |
| **Specificity** | 92.15% | 93.72% | +1.57% |
| **F1-Score** | 0.8473 | 0.8485 | +0.0012 |

---

## 4. The 5 Discordant Recordings Identified

Exactly five recordings had baseline predicted probabilities falling in the interval $[0.3500, 0.4300)$:

| Recording ID | Acoustic Category | Source Group ID | Ground Truth | Baseline Prob | Status at $\theta=0.35$ | Status at $\theta=0.43$ | Forensic Impact |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| `v2_fsd50k_316558` | whistles_and_squeaks | `stage8_9_else_fucker` | Negative (0) | 0.3674 | FP | TN | False alarm eliminated |
| `v2_fsd50k_159750` | sfx_sirens_fireworks | `stage8_9_conleec` | Negative (0) | 0.4044 | FP | TN | False alarm eliminated |
| `v2_openslr_7IOA_15_11_1_33_0_0_0` | scream | `openslr_speaker_7IOA` | Positive (1) | 0.4120 | TP | FN | Genuine scream lost |
| `v2_fsd50k_57483` | whistles_and_squeaks | `fsd50k_uploader_sharkmail` | Negative (0) | 0.3822 | FP | TN | False alarm eliminated |
| `v3_fsd50k_9433` | scream | `fsd50k_uploader_thanvannispen` | Positive (1) | 0.4085 | TP | FN | Genuine scream lost |

---

## 5. Audit Conclusion

The discrepancy between Stage 8.9.34 and Stage 8.9.35 baseline figures is **FULLY RESOLVED AND RECONCILED**.
- Neither stage suffered from code corruption, weight changes, or dataset leakage.
- Stage 8.9.35 correctly subjected the baseline to the same operating threshold ($\theta = 0.43$) as the newly trained candidate to ensure fair apple-to-apple comparison under that specific operating point, but did not explicitly document that the historical 84.31% baseline was measured at $\theta = 0.3500$.
- Both reporting numbers are mathematically verified and reproducible.
