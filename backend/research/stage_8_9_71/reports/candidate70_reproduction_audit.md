# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Candidate 70-D Independent Reproduction & Forensic Statistical Audit

**Mandatory Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.  
**Research Stage:** Stage 8.9.71  
**Evaluator:** Independent Forensic Verification Engine  
**Frozen Model Checkpoint:** `backend/research/stage_8_9_70/models/candidate_70_frozen.pt`  
**Checkpoint SHA-256:** `40a162d1f9e34564a93c1b88fb2a290909ee4deb32e659bd21bcf9c2d3c44b6d`  
**Evaluation Cohort:** Stage 54 Validation Partition ($N=311$, formally designated `EXPOSED_DEVELOPMENT_COHORT`)  
**Operating Threshold:** 0.4920  

---

## 1. Executive Summary

This audit independently replicates and extends the statistical profile of Candidate 70-D from its bit-for-bit frozen PyTorch checkpoint (`candidate_70_frozen.pt`). All metrics reported in Stage 8.9.70 were verified with exactly **0.00% discrepancy**.

Candidate 70-D achieved:
- **Overall Scream Recall (Gate 1):** **82.83%** (82/99, TP=82, FN=17) — 95% Bootstrap CI: [75.76%, 89.90%]
- **Hard-Negative FPR (Gate 2):** **9.68%** (12/124, FP=12, TN=112) — 95% Bootstrap CI: [4.84%, 15.32%]
- **Shouted-Speech FPR (Gate 3):** **14.77%** (13/88, FP=13, TN=75) — 95% Bootstrap CI: [7.95%, 22.73%]
- **Short-Scream Recall (Gate 4):** **94.87%** (37/39, TP=37, FN=2) — 95% Bootstrap CI: [87.18%, 100.00%]
- **Precision:** **76.64%** (82/107)
- **F1-Score:** **79.61%**
- **Specificity:** **88.21%** (187/212 total negative samples)
- **Balanced Accuracy:** **85.52%**
- **ROC-AUC:** **0.9057**
- **PR-AUC:** **0.8470**
- **Brier Score:** **0.1398**
- **Expected Calibration Error (ECE):** **0.1582**

---

## 2. Comprehensive Confusion Matrix & Metric Verification

### 2.1 Confusion Matrix ($N=311$)

| True Condition | Predicted Negative ($p < 0.4920$) | Predicted Positive ($p \ge 0.4920$) | Total Clips | Recall / FPR |
| :--- | :--- | :--- | :--- | :--- |
| **Scream (Ground Truth = 1)** | 17 (False Negatives) | 82 (True Positives) | 99 | **82.83% Recall** |
| **Shouted Speech (Category = shout)** | 75 (True Negatives) | 13 (False Positives) | 88 | **14.77% FPR** |
| **Hard Negatives (Other non-scream)** | 112 (True Negatives) | 12 (False Positives) | 124 | **9.68% FPR** |
| **All Negative Combined** | 187 (True Negatives) | 25 (False Positives) | 212 | **11.79% Total FPR** |

### 2.2 Category-Specific False-Positive Rate Breakdown

| Acoustic Category | Sample Count ($N$) | False Positives (FP) | True Negatives (TN) | Category FPR (%) | Primary Acoustic Challenge |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Crowd Chants & Cheering** | 37 | 1 | 36 | **2.70%** | Resonant collective harmonic vocalizations |
| **General Environmental Noise** | 36 | 2 | 34 | **5.56%** | Synthesizer distortion, mechanical scraping |
| **Infant Crying** | 20 | 3 | 17 | **15.00%** | Biologically authentic vocal distress cries |
| **SFX, Sirens, Fireworks** | 9 | 2 | 7 | **22.22%** | High-energy FM modulation & pyrotechnic cracks |
| **Shouting and Speech** | 88 | 13 | 75 | **14.77%** | High-energy vowel formants and prosodic shouting |
| **Whistles and Squeaks** | 22 | 4 | 18 | **18.18%** | High-frequency acoustic whistle bursts |
| **Total Non-Scream** | **212** | **25** | **187** | **11.79%** | Cross-category rejection benchmark |

---

## 3. Forensic Analysis of the 12 Hard-Negative False Positives

All 12 false positives among the 124 hard negatives were extracted and recorded with their complete acoustic parameter sets in [candidate70_false_positive_forensics.csv](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_71/reports/candidate70_false_positive_forensics.csv).

### 3.1 Failure Mode Stratification

1. **High-Frequency Whistles with Air Turbulence (4 Clips):**
   - `src_v5_parent_0104`, `src_v5_parent_0108`, `src_v5_parent_0116` originate from related whistle recording sessions (`whistle_008` and `012`).
   - Acoustic signature: Ultra-low roughness ($\le 0.0030$), extreme high-frequency concentration ratio ($hf\_ratio \approx 43.7$), moderate HNR ($\approx 8.27$ dB).
   - **Why Candidate 70-D Failed:**
     - The narrowband whistle veto required $HNR > 12.0$ dB and $flatness < 0.001$, but airflow noise in real whistles lowered HNR to 8.27 dB and raised flatness to 0.0040.
     - The vocal distress veto had a dual condition: $roughness < 0.022$ AND $hf\_ratio < 0.050$. Because whistles have massive high-frequency energy ($hf\_ratio > 43.0$), the veto failed to fire despite the near-total absence of vocal fold modulation.
2. **Accidental Rescue of Non-Screams by Latent Resonance Logic (2 Clips):**
   - `fsd50k_323723` (whistle, $p_{\text{raw}} = 0.4666 \to p_{\text{final}} = 0.5016$)
   - `fsd50k_424603` (environmental noise, $p_{\text{raw}} = 0.4611 \to p_{\text{final}} = 0.4961$)
   - **Finding:** Both clips had raw neural probabilities safely below threshold ($< 0.4920$). Candidate 70-D's resonance rescue rule blindly boosted them by $+0.035$ because branch cosine similarity exceeded 0.78, pushing them over the decision boundary.
3. **Infant Crying Vocal Distress (3 Clips):**
   - `fsd50k_154428`, `fsd50k_343976`, `fsd50k_344030` ($p_{\text{raw}} = 0.5632, 0.5844, 0.6787$).
   - Acoustic signature: Legitimate vocal fold bifurcation, genuine 30–150 Hz subharmonic roughness, and high-pitch screaming formant peaks. These are true acoustic confounders that cannot be rejected by simple heuristic spectral thresholds without suppressing screams of young children.
4. **Distorted Sirens & Pyrotechnic Crackle (2 Clips):**
   - `fsd50k_34280`, `fsd50k_184623` ($p_{\text{raw}} = 0.6258, 0.5365$).
   - High roughness ($> 0.270$) caused by audio clipping and non-linear distortion.
5. **Crowd Chants (1 Clip):**
   - `fsd50k_83199` ($p_{\text{raw}} = 0.5046$).

### 3.2 Scientific Implications for Stage 8.9.71
- **Eliminate Unconditioned Resonance Rescue:** Removing the blind $+0.035$ probability boost immediately eliminates 2 false alarms (`fsd50k_323723` and `fsd50k_424603`).
- **Decouple the High-Frequency Whistle Suppression:** Whistles have zero vocal fold roughness ($roughness < 0.005$). Decoupling the vocal distress veto so that $roughness < 0.005$ triggers suppression regardless of $hf\_ratio$ will safely eliminate all 3 whistle parent false alarms (`src_v5_parent_0104`, `0108`, `0116`) without risking soprano human screams (which maintain $roughness > 0.015$).

