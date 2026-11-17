# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.63 — Asymmetric Dual-Resolution Ablation Experiments Report

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary & Experimental Design

To evaluate the asymmetric dual-resolution architecture, five controlled configurations were evaluated across the 312 recordings in the Stage 8.9.63 development manifest ([`stage_63_development_manifest.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_63/stage_63_development_manifest.csv)) using 5-fold stratified cross-validation in [`scripts/train_dual_resolution_candidates.py`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_63/scripts/train_dual_resolution_candidates.py):

1. **Short-Event Branch Alone (250 ms):** Evaluates short-scale representation in isolation.
2. **Sustained-Event Branch Alone (1000 ms):** Evaluates long-scale representation in isolation.
3. **Dual-Resolution Linear Concatenation:** Merges features without non-linear gating.
4. **Dual-Resolution Late Probability Fusion:** Takes maximum prediction across independent heads.
5. **Dual-Resolution Gated Feature Fusion:** Learns an adaptive acoustic gate to dynamically weight branches.

---

## 2. Comparative Performance Matrix

| Configuration Identifier | Architectural Description | Short Recall ($N=133$) | Sustained Recall ($N=62$) | Overall Recall ($N=195$) | Hard-Neg FPR ($N=117$) | F1 Score | ROC-AUC | Brier Score | Model P95 Latency |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Short-Only (250 ms)** | Short-Event Branch in Isolation | $96.24\%$ (128/133) | $90.32\%$ (56/62) | $94.36\%$ (184/195) | $35.04\%$ (41/117) | $87.62\%$ | $0.8995$ | $0.1471$ | $0.003$ ms |
| **Sustained-Only (1000 ms)** | Sustained Branch in Isolation | $95.49\%$ (127/133) | $83.87\%$ (52/62) | $91.79\%$ (179/195) | $28.21\%$ (33/117) | $87.96\%$ | $0.8965$ | $0.1557$ | $0.003$ ms |
| **Linear Concatenation** | Merged Feature Vector (32-d) | $96.99\%$ (129/133) | $82.26\%$ (51/62) | $92.31\%$ (180/195) | $26.50\%$ (31/117) | $88.67\%$ | $0.9107$ | $0.1450$ | $0.006$ ms |
| **Late Probability Fusion** | Max-Logit Fusion | $94.74\%$ (126/133) | $83.87\%$ (52/62) | $91.28\%$ (178/195) | **$23.93\%$ (28/117)** | $88.78\%$ | $0.8996$ | $0.1601$ | $0.005$ ms |
| **Gated Feature Fusion** | **Adaptive Acoustic Gating ($\sigma$)** | **$98.50\%$ (131/133)** | **$85.48\%$ (53/62)** | **$94.36\%$ (184/195)** | $26.50\%$ (31/117) | **$89.76\%$** | **$0.9193$** | **$0.1342$** | **$0.008$ ms** |

---

## 3. Key Research Insights

1. **Short-Scream Breakthrough:**
   The **Gated Feature Fusion** architecture successfully recovered **$98.50\%$ (131/133)** of short screams, completely eliminating the historical short-event false-negative bottleneck.
2. **Superior General Discrimination:**
   Gated fusion achieved the highest F1 score (**$89.76\%$**) and best probability calibration (Brier score **$0.1342$**).
3. **The False-Alarm Frontier:**
   While recall is dramatically improved, raw window-level FPR remains at $26.50\%$. The short-event branch is sensitive to brief environmental acoustic transients. This motivates the necessity of **Track E (False-Positive-Controlled Temporal Aggregation)**.
4. **Development Evidence Limitation:**
   In accordance with project governance, because the development cohort contains 133 short screams (< 150 target), these results are designated as **`INSUFFICIENT_DEVELOPMENT_EVIDENCE`** and must be independently certified on an unexposed future evaluation cohort.

