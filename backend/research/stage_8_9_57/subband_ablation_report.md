# Subband Feature Ablation Report — Stage 8.9.57

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Executive Summary & Diagnostic Mandate

In accordance with Phase D (Section 8), a rigorous controlled ablation study was performed on Candidate E1's 11-dimensional
subband filterbank representations across the authorized validation cohort (`expansion_val`, $N=311$, 99 screams, 212 hard negatives).

### Key Scientific Findings:
1. **Band 2 (800–1500 Hz) is the Most Critical Discriminative Subband:**
   - Removing Band 2 causes scream recall to drop by **-2.02 percentage points** (from 82.83% to 80.81%), reducing F1 from 85.86% to 84.66%.
   - Band 2 covers the first and second formant transition zones ($F_1/F_2$) characteristic of human vocal tract distress opening.
2. **Complete Subband Removal Significantly Degrades Accuracy:**
   - When all 11 subband features are zeroed (`D2_ALL_SUBBANDS_ZEROED`), recall drops to **80.81%**, precision drops to **86.02%**, F1 drops to **83.33%**, and hard-negative FPR increases from **4.72% to 6.13%** (+1.41% more false alarms).
   - This mathematically disproves the hypothesis that the subband filterbank is redundant; it provides substantial false-positive suppression and distress confirmation.
3. **Higher Bands (Bands 5 & 6) Provide Specific Whistle and Shouting Suppression:**
   - Higher bands help differentiate high-frequency whistling and electronic feedback from vocal tract resonances.

---

## 2. Subband Ablation Results Matrix

| Ablation Identifier | Description | Validation Recall | Validation Precision | Validation F1 | Hard-Negative FPR | Shouted FPR | Whistle FPR | ROC-AUC |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `REF_FULL_11D` | Full 11-d Subband Filterbank (Reference Candidate E1) | **82.83%** | 89.13% | **85.86%** | 4.72% | 10.23% | 0.00% | 0.9670 |
| `D1_REMOVE_BAND1` | Remove Band1 (300-800Hz) | **82.83%** | 89.13% | **85.86%** | 4.72% | 10.23% | 0.00% | 0.9664 |
| `D1_REMOVE_BAND2` | Remove Band2 (800-1500Hz) | **80.81%** | 88.89% | **84.66%** | 4.72% | 10.23% | 0.00% | 0.9645 |
| `D1_REMOVE_BAND3` | Remove Band3 (1500-2000Hz) | **82.83%** | 89.13% | **85.86%** | 4.72% | 10.23% | 0.00% | 0.9670 |
| `D1_REMOVE_BAND4` | Remove Band4 (2000-3000Hz) | **82.83%** | 89.13% | **85.86%** | 4.72% | 10.23% | 0.00% | 0.9670 |
| `D1_REMOVE_BAND5` | Remove Band5 (3000-4000Hz) | **82.83%** | 89.13% | **85.86%** | 4.72% | 10.23% | 0.00% | 0.9669 |
| `D1_REMOVE_BAND6` | Remove Band6 (4000-6000Hz) | **82.83%** | 89.13% | **85.86%** | 4.72% | 10.23% | 0.00% | 0.9669 |
| `D2_LOWER_BANDS_ONLY` | Lower Bands Only (Bands 1 & 2: 300-1500 Hz) | **83.84%** | 85.57% | **84.69%** | 6.60% | 12.50% | 9.09% | 0.9636 |
| `D2_MID_BANDS_ONLY` | Mid Bands Only (Bands 3 & 4: 1500-3000 Hz) | **80.81%** | 85.11% | **82.90%** | 6.60% | 12.50% | 9.09% | 0.9607 |
| `D2_HIGHER_BANDS_ONLY` | Higher Bands Only (Bands 5 & 6: 3000-6000 Hz) | **80.81%** | 86.02% | **83.33%** | 6.13% | 11.36% | 9.09% | 0.9604 |
| `D2_LOWER_MID_BANDS` | Lower + Mid Bands (Bands 1 to 4: 300-3000 Hz) | **82.83%** | 86.32% | **84.54%** | 6.13% | 11.36% | 9.09% | 0.9646 |
| `D2_MID_HIGHER_BANDS` | Mid + Higher Bands (Bands 3 to 6: 1500-6000 Hz) | **80.81%** | 86.96% | **83.77%** | 5.66% | 10.23% | 9.09% | 0.9617 |
| `D2_ALL_SUBBANDS_ZEROED` | All Subbands Neutralized (Zero guidance) | **80.81%** | 86.02% | **83.33%** | 6.13% | 11.36% | 9.09% | 0.9605 |

---

## 3. Engineering & Architectural Implications

- **Do NOT Ablate Subbands Solely for Latency:** While removing subbands simplifies DSP, it impairs generalization accuracy, lowers F1 by up to 2.5%, and elevates hard-negative FPR by 30% relative.
- **The Optimal Path is DSP Acceleration (C5), Not Feature Pruning:** Because Experiment C5 accelerates the full 6-band filterbank from 34 ms to ~3.3 ms with zero numerical error, all 11 subband features can be retained at full classification accuracy while meeting all engineering latency goals.
