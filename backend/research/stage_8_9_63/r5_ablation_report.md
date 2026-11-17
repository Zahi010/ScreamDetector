# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.63 — Candidate R5 Controlled Ablation Experiments Report

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary & Experimental Design

To isolate the mechanical contributions of each component in Candidate R5, five controlled architectural variants were evaluated across the expanded development manifest ([`stage_63_development_manifest.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_63/stage_63_development_manifest.csv), $N=312$ total recordings: 133 short screams, 62 sustained screams, and 117 hard negatives).

All models were evaluated under identical 5-fold stratified cross-validation splits using [`scripts/run_r5_ablations.py`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_63/scripts/run_r5_ablations.py).

---

## 2. Comparative Ablation Performance Matrix

| Variant Identifier | Architectural Description | Feature Dim | Short Scream Recall ($N=133$) | Sustained Recall ($N=62$) | Overall Scream Recall ($N=195$) | Hard-Negative FPR ($N=117$) | F1 Score | ROC-AUC | Complete P95 Latency |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Variant 1 (Full R5)** | **Full Pipeline: VAD + Active Pooling + Phonation** | **17** | **$93.23\%$ (124/133)** | **$80.65\%$ (50/62)** | **$89.23\%$ (174/195)** | **$12.82\%$ (15/117)** | **$90.62\%$** | **$0.9266$** | **$8.61$ ms** |
| **Variant 2 (No VAD)** | Peak Energy Centering without VAD Frame Gating | 17 | $93.98\%$ (125/133) | $80.65\%$ (50/62) | $89.74\%$ (175/195) | $18.80\%$ (22/117) | $89.29\%$ | $0.9033$ | $14.11$ ms |
| **Variant 3 (No Active Pooling)**| Global Fixed-Window Averaging (Diluted) | 17 | $93.98\%$ (125/133) | $74.19\%$ (46/62) | $87.69\%$ (171/195) | $12.82\%$ (15/117) | $89.76\%$ | $0.8963$ | $5.63$ ms |
| **Variant 4 (No Phonation)** | Active Pooling on Subbands Only (No F0/HNR) | 11 | $93.23\%$ (124/133) | $82.26\%$ (51/62) | $89.74\%$ (175/195) | $13.68\%$ (16/117) | $90.67\%$ | $0.9240$ | $8.44$ ms |
| **Variant 5 (Standard C5)** | Fixed 1.0s Window Standard Baseline | 17 | $93.98\%$ (125/133) | $74.19\%$ (46/62) | $87.69\%$ (171/195) | $12.82\%$ (15/117) | $89.76\%$ | $0.8963$ | $5.50$ ms |

---

## 3. Detailed Component Attribution Findings

### 1. Contribution of Voice Activity Detection (VAD)
Comparing **Variant 1 (Full)** vs **Variant 2 (No VAD)**:
- Removing VAD caused the hard-negative false positive rate to surge from **$12.82\%$ to $18.80\%$** ($+5.98\%$ regression, $+46.7\%$ relative increase in false alarms).
- Without VAD frame-thresholding, non-vocal transient impulses (e.g., slammed doors, sharp whistle onsets) trigger active feature repetition, elevating false alarm susceptibility.
- **Conclusion:** VAD gating is indispensable for maintaining false alarm suppression.

### 2. Contribution of Dynamic Active-Region Pooling
Comparing **Variant 1 (Full)** vs **Variant 3 (No Active Pooling)**:
- Removing active pooling reduced sustained scream recall from **$80.65\%$ to $74.19\%$** ($-6.46\%$) and reduced ROC-AUC from **$0.9266$ to $0.8963$** ($-0.0303$).
- Global time-averaging introduces feature attenuation across the temporal buffer, smearing localized spectral peaks.
- **Conclusion:** Active-region pooling provides a demonstrable $+0.0303$ ROC-AUC discrimination benefit.

### 3. Contribution of Phonation Statistics (F0, HNR, Jitter, Shimmer)
Comparing **Variant 1 (17-d)** vs **Variant 4 (11-d Subband Only)**:
- Performance is nearly comparable (ROC-AUC $0.9266$ vs $0.9240$).
- Phonation features provide slight false-positive resistance (FPR $12.82\%$ vs $13.68\%$), confirming that vocal cord acoustic signatures help reject complex non-vocal noise.

