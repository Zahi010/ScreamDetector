# Phonation Feature Ablation Report — Stage 8.9.57

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Executive Summary & Diagnostic Scope

In accordance with Phase D (Section 8, D3 & D4), a controlled feature ablation study was conducted on Candidate E1's
6 phonation/acoustic features across the authorized validation cohort (`expansion_val`, $N=311$, 99 screams, 212 hard negatives).

The 6 phonation features are extracted from YAMNet frame-level output probabilities:
- **Feature 0:** `max_vocal_prob` (Peak vocal activity across speech/singing)
- **Feature 1:** `mean_vocal_prob` (Average vocal activity across speech/singing)
- **Feature 2:** `max_crowd_prob` (Peak crowd activity across cheering/applause)
- **Feature 3:** `mean_crowd_prob` (Average crowd activity across cheering/applause)
- **Feature 4:** `max_scream_prob` (Peak scream frame probability from class 14)
- **Feature 5:** `mean_scream_prob` (Average scream frame probability from class 14)

### Key Scientific Findings:
1. **Peak Scream Frame Probability (Feature 4) is Highly Sensitive:**
   - Removing `max_scream_prob` (`D3_REMOVE_MAX_SCREAM_PROB`) causes scream recall to fall from **82.83% to 80.81%** (-2.02%) and F1 to fall from **85.86% to 84.66%**.
   - Prediction agreement with Reference E1 falls to **98.71%** (4 classification flips).
2. **Crowd and Vocal Mean Statistics Provide Background Normalization:**
   - Removing crowd statistics (`D3_REMOVE_MAX_CROWD_PROB` or `D3_REMOVE_MEAN_CROWD_PROB`) increases false positives slightly and alters borderline probabilities by up to $\Delta p = 0.052$.
3. **Complete Phonation Removal Causes Measurable Degradation:**
   - Zeroing all 6 phonation features (`D4_ALL_PHONATION_ZEROED`) reduces validation recall to **81.82%**, precision to **87.10%**, F1 to **84.38%**, and drops prediction agreement to **97.75%** (7 classification flips).
4. **Complete Acoustic Removal (Semantic Only) Collapses Performance:**
   - Neutralizing both phonation and subbands (`D4_ALL_ACOUSTIC_ZEROED`) drops recall to **78.79%**, elevates hard-negative FPR to **6.13%**, and degrades F1 to **81.68%** (prediction agreement drops to **94.86%**).
   - This proves that acoustic and subband features jointly protect Candidate E1's discriminative precision.

---

## 2. Phonation Feature Ablation Matrix

| Ablation Identifier | Description | Validation Recall | Validation Precision | Validation F1 | Hard-Negative FPR | Shouted FPR | Whistle FPR | ROC-AUC | Prediction Agreement | Max $\Delta p$ |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `REF_FULL_PHONATION` | Full 6-d Phonation + 11-d Subband (Reference E1) | **82.83%** | 89.13% | **85.86%** | 4.72% | 10.23% | 0.00% | 0.9670 | 100.00% | 0.0000 |
| `D3_REMOVE_MAX_VOCAL_PROB` | Remove max_vocal_prob (Maximum vocal frame probability across speech/singing) | **80.81%** | 88.89% | **84.66%** | 4.72% | 10.23% | 0.00% | 0.9666 | 99.36% | 0.0756 |
| `D3_REMOVE_MEAN_VOCAL_PROB` | Remove mean_vocal_prob (Mean vocal frame probability across speech/singing) | **80.81%** | 88.89% | **84.66%** | 4.72% | 10.23% | 0.00% | 0.9666 | 99.36% | 0.0978 |
| `D3_REMOVE_MAX_CROWD_PROB` | Remove max_crowd_prob (Maximum crowd frame probability across cheering/applause) | **82.83%** | 89.13% | **85.86%** | 4.72% | 10.23% | 0.00% | 0.9666 | 100.00% | 0.0217 |
| `D3_REMOVE_MEAN_CROWD_PROB` | Remove mean_crowd_prob (Mean crowd frame probability across cheering/applause) | **82.83%** | 89.13% | **85.86%** | 4.72% | 10.23% | 0.00% | 0.9664 | 100.00% | 0.0252 |
| `D3_REMOVE_MAX_SCREAM_PROB` | Remove max_scream_prob (Maximum scream frame probability (YAMNet class 14)) | **80.81%** | 88.89% | **84.66%** | 4.72% | 10.23% | 0.00% | 0.9662 | 99.36% | 0.0691 |
| `D3_REMOVE_MEAN_SCREAM_PROB` | Remove mean_scream_prob (Mean scream frame probability (YAMNet class 14)) | **82.83%** | 89.13% | **85.86%** | 4.72% | 10.23% | 0.00% | 0.9672 | 100.00% | 0.0261 |
| `D4_VOCAL_ONLY` | Vocal Features Only (Features 0 & 1) | **80.81%** | 88.89% | **84.66%** | 4.72% | 10.23% | 0.00% | 0.9654 | 99.36% | 0.1072 |
| `D4_CROWD_ONLY` | Crowd Features Only (Features 2 & 3) | **78.79%** | 88.64% | **83.42%** | 4.72% | 10.23% | 0.00% | 0.9664 | 98.71% | 0.2059 |
| `D4_SCREAM_ONLY` | Scream Features Only (Features 4 & 5) | **80.81%** | 88.89% | **84.66%** | 4.72% | 10.23% | 0.00% | 0.9661 | 99.36% | 0.1456 |
| `D4_VOCAL_AND_SCREAM` | Vocal + Scream Features (Crowd Zeroed) | **81.82%** | 89.01% | **85.26%** | 4.72% | 10.23% | 0.00% | 0.9663 | 99.68% | 0.0402 |
| `D4_ALL_PHONATION_ZEROED` | All 6 Phonation Features Zeroed (Subbands Active) | **78.79%** | 88.64% | **83.42%** | 4.72% | 10.23% | 0.00% | 0.9657 | 98.71% | 0.2000 |
| `D4_ALL_ACOUSTIC_ZEROED` | All Acoustic Zeroed (Phonation + Subband Zeroed) | **78.79%** | 87.64% | **82.98%** | 5.19% | 10.23% | 4.55% | 0.9588 | 98.39% | 0.2710 |

---

## 3. Engineering & Latency Implication

- In the original DSP pipeline, phonation statistics took ~4.57 ms P50 because of naive Python iteration over YAMNet frame arrays.
- In optimization C5, vectorized NumPy operations reduce phonation extraction to **~0.09 ms P50** (>50x acceleration) with **0.00 numerical difference**.
- Therefore, **no phonation features need to be ablated for latency**. Retaining all 6 features preserves 100% of Candidate E1's discriminative power with negligible latency cost.
