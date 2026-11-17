# Low-Intensity, Distant-Recording & Environmental Analysis — Stage 8.9.48

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.

---

## 1. Executive Summary & Challenging Acoustic Conditions

In real-world deployment contexts, screams rarely occur as unattenuated, clean studio recordings. They are subjected to atmospheric distance roll-off, reverberant multi-path distortion, crowd masking, and muffled phonation.

This audit examines how Candidate B and Candidate R5 perform across the four difficult acoustic positive conditions:

| Challenging Acoustic Subtype | Physical Degradation Mechanism | Cohort Size ($N$) | Candidate B Recall (TP/N) | Candidate R5 Recall (TP/N) | Performance Differential |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **`low_intensity_muffled_scream`** | Vocal tract constriction, aspiration, low RMS energy | 15 | **80.00% (12/15)** | **80.00% (12/15)** | **Parity (Tie)** |
| **`distant_reverberant_scream`** | Air absorption lowpass roll-off (2.2 kHz) + room impulse response | 20 | **70.00% (14/20)** | **70.00% (14/20)** | **Parity (Tie)** |
| **`crowd_masked_scream`** | Outdoor festival ambiance + crowd noise masking (+3 to +9 dB SNR) | 20 | **75.00% (15/20)** | **55.00% (11/20)** | **+20.00% (Cand B Superior)** |
| **`sustained_scream`** | Prolonged phonation, pitch droop, vibrato dispersion ($d > 1.2\text{s}$) | 35 | **94.29% (33/35)** | **71.43% (25/35)** | **+22.86% (Cand B Superior)** |

---

## 2. Acoustic Analysis of Low-Intensity & Muffled Screams

- **Signal Energy Correlation:** Across the 15 muffled scream clips, the mean RMS amplitude was 0.124 (vs 0.285 for standard screams). Both Candidate B and Candidate R5 successfully detected 12 of the 15 clips (80.00% recall).
- **The 3 Common Misses:** Clips `s47_indep_pos_0128`, `0133`, and `0135` were missed by both models. These recordings had an average active SNR of < 8.5 dB and RMS amplitude < 0.045, where vocal fold phonation energy was submerged beneath the silence noise floor.
- **Distinction from Gain:** Normalizing gain does not restore these misses because the spectral envelope lacks prominent high-frequency formants in the 2.5–4.0 kHz scream band.

---

## 3. Acoustic Analysis of Distant & Reverberant Screams

- **Reverberation & Distance Filter:** The 20 distant scream recordings simulated physical propagation at 50–100m, featuring high-frequency lowpass filtering (attenuating energy above 2.2 kHz) and exponential impulse response decay.
- **Parity Between Models:** Both Candidate B and Candidate R5 detected exactly 14/20 clips (70.00% recall).
- **Residual Misses:** The 6 missed distant screams suffered from severe high-frequency roll-off where spectral centroid dropped below 1,600 Hz (comparable to neutral speech formants).

---

## 4. The Decisive Divergence: Crowd-Masked and Sustained Screams

Where Candidate B decisively separates from Candidate R5 is on **crowd-masked** and **sustained** screams:
1. **Continuous Masking Advantage:** Candidate B was trained in Stage 8.9.44 with continuous background festival masking. Consequently, when evaluated on authentic outdoor crowd-masked screams, Candidate B achieved **75.00% recall (15/20)** vs Candidate R5's **55.00% (11/20)** (+20.00% absolute advantage).
2. **Sustained Vocalization Stability:** Candidate B detected **33/35 sustained screams (94.29%)**, whereas Candidate R5 suffered from temporal dispersion, dropping to **25/35 (71.43%)** (-8 missed screams). Candidate B's projection head maintains robust temporal integration across multi-frame YAMNet trajectories.

---

## 5. Hard-Negative Trade-Off: Referee Whistle False Positives

Candidate B's higher sensitivity to masked vocalizations comes at one specific, bounded cost:
- On **whistles and high-frequency squeaks**, Candidate B produced **4 false positives out of 45 clips (8.89% category FPR)**.
- Candidate R5 had **0 false positives on whistles (0.00%)**.
- All 4 Candidate B false positives were sports referee trill whistles featuring intense acoustic oscillation at 2.8–3.2 kHz with 25 Hz modulation, acoustically mimicking vocal roughness.
- Crucially, **neither model produced a single false positive on shouted speech (0/80 FP)**, cheering, infant crying, or music.
- Overall, Candidate B's hard-negative FPR remains **1.25% (4/320)**, well below the Gate 2 limit of 5.0%.
