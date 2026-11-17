# Stage 8.9.35 — Subband Feature Analysis Report

**Stage:** 8.9.35 — Frequency-Subband Discrimination & Spatial Audio Research  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Status:** Strictly Isolated Research  
**Data Artifact:** `backend/research/stage_8_9_35/frequency_analysis/subband_feature_analysis.csv` (1,328 recordings)  

---

## 1. Feature Extraction Methodology

To capture granular spectral, temporal, and modulation dynamics, an 11-dimensional feature vector was extracted from each recording using 4th-order Butterworth digital IIR bandpass filters (SOS structure, $f_s = 16\text{ kHz}$):

1. **`Band1_300_800Hz_rel_energy`**: Relative energy fraction in low vocal fundamental / male speech formant region.
2. **`Band2_800_1500Hz_rel_energy`**: Relative energy fraction in first/second vocal tract resonance region.
3. **`Band3_1500_2000Hz_rel_energy`**: Relative energy fraction in transition band.
4. **`Band4_2000_3000Hz_rel_energy`**: Relative energy fraction in primary scream resonance band.
5. **`Band5_3000_4000Hz_rel_energy`**: Relative energy fraction in secondary scream resonance band.
6. **`Band6_4000_6000Hz_rel_energy`**: Relative energy fraction in high-frequency whistle / noise band.
7. **`Band1_300_800Hz_temp_var`**: Temporal variance of energy in Band 1 (captures speech cadence vs. steady screaming).
8. **`Band4_2000_3000Hz_temp_var`**: Temporal variance in Band 4 (captures sustained vocal strain).
9. **`Band5_3000_4000Hz_temp_var`**: Temporal variance in Band 5 (captures turbulence instability).
10. **`scream_band_to_vocal_ratio`**: $\frac{B_4 + B_5}{B_1 + 10^{-6}}$ (discriminates high vocal tract strain from chest-voice speech).
11. **`high_band_whistle_ratio`**: $\frac{B_6}{B_4 + B_5 + 10^{-6}}$ (isolates synthetic whistles and alarms from human screams).

---

## 2. Standalone Subband Classifier Performance

To determine whether subband features alone can solve scream discrimination without deep semantic embeddings, two standalone classifiers were trained on the training partition ($N=739$) and evaluated on the frozen independent held-out cohort ($N=293$, 102 screams, 191 hard negatives across 111 source groups):

| Metric | Standalone Random Forest (Candidate B) | Standalone Logistic Regression (Candidate C) | Dual-Encoder Baseline (Stage 8.9.33) |
| :--- | :---: | :---: | :---: |
| **Scream Recall** | 73.53% (75/102) | 77.45% (79/102) | **82.35% (84/102)** |
| **Hard-Negative FPR** | 14.14% (27/191) | 24.08% (46/191) | **6.28% (12/191)** |
| **Shouted-Speech FPR** | 16.67% (8/48) | 18.75% (9/48) | **8.33% (4/48)** |
| **Infant-Cry FPR** | 6.67% (1/15) | 6.67% (1/15) | 6.67% (1/15) |
| **Crowd-Cheering FPR** | 16.67% (7/42) | 38.10% (16/42) | **11.90% (5/42)** |
| **Precision** | 73.53% | 63.20% | **87.50%** |
| **F1-Score** | 0.7353 | 0.6960 | **0.8485** |
| **ROC-AUC** | 0.8525 | 0.8335 | **0.9285** |
| **PR-AUC** | 0.7593 | 0.7279 | **0.8717** |
| **Short-Scream Recall (<1.0s)** | 40.00% (2/5) | 60.00% (3/5) | **80.00% (4/5)** |
| **Acceptance Status** | **REJECTED (FAILED)** | **REJECTED (FAILED)** | **REJECTED (FAILED)** |

---

## 3. Findings and Architectural Guidance

1. **Subband Features Are Complementary, Not Autonomous:**
   - Standalone subband classifiers exhibit unacceptable false-positive rates (14.14%–24.08% HN-FPR). Frequency band energies lack semantic context; an electric guitar solo, a synthesizer sweep, or a revving motorbike engine often mimics the exact frequency ratio $\frac{B_4+B_5}{B_1}$ of a human scream.
2. **Short Screams Require Temporal Context:**
   - On short screams (<1.0s), standalone subband features suffer from spectral leakage and transient boundary effects, achieving only 40.0%–60.0% recall compared to 80.0% for the baseline.
3. **Synergy with Semantic YAMNet Embeddings:**
   - While inadequate on their own, subband features capture explicit physical acoustic signatures that neural backbones occasionally smooth out. When fused into `MultiPathwayFusionModel` (Candidate D), they provide orthogonal evidence that elevates scream recall from 82.35% to 89.22%.
