# ACOUSTIC ERROR ANALYSIS & CONFUSER CHARACTERIZATION
## Signal-Processing Analysis of Acoustic Overlap Between Screams, Cheering, and Infant Crying

**Project:** Festival Scream Detector  
**Stage:** 8.9.32 — Acoustic Discrimination Research  
**Focus:** Acoustic Error Analysis and Discriminative Feasibility  
**Status:** COMPLETE  
**Date:** November 2, 2026

---

## 1. Executive Summary & Root Cause of Historical Misclassifications

The persistent false alarms in the frozen production classifier on stadium cheering (78.6% FPR) and infant crying (85.7% FPR) stem directly from high-dimensional spectral representation overlap.

In historical stages, classifiers were trained with a binary objective on standard sound effect libraries where screams were contrasted primarily with non-vocal environmental sounds (rain, footsteps, engine noise, pink noise). In that simplified space, any sound with **high high-frequency energy, high harmonic dispersion, and elevated fundamental frequency** was sufficient to trigger a positive scream decision.

When evaluated in festival environments against crowd vocalizations and crying, the frozen classifier's feature space fails:

1. **Stadium Cheering:**
   - **Acoustic Mechanics:** Thousands of individuals vocalizing simultaneously in reverberant open or semi-enclosed stadiums.
   - **Overlap with Screams:** High aggregate energy in the 1.5 kHz – 4.0 kHz band (the "singer's formant" and human hearing sensitivity range). Collective shrieks and excited roars produce spectral centroids $> 2,200\text{ Hz}$ and elevated crest factors that mimic sustained group screams.
   - **Differentiating Feature:** Cheering has **higher spectral entropy** (diffuse, uncoordinated multi-pitch dispersion) and lack of a single coherent, rapidly modulating fundamental frequency ($F_0$) trajectory.

2. **Infant Crying:**
   - **Acoustic Mechanics:** Immature vocal fold morphology with short vocal tract length ($7 - 9\text{ cm}$ vs $15 - 17\text{ cm}$ in adults).
   - **Overlap with Screams:** Fundamental frequency $F_0$ typically ranges from **$450\text{ Hz}$ to $1,200\text{ Hz}$**, precisely matching the fundamental frequency of high-stress human terror screams. Phonation instabilities (subharmonics, biphonation, frequency jumps) create rough, chaotic timbre identical to panic shrieks.
   - **Differentiating Feature:** Infant cries exhibit **cyclical respiratory burst patterns** (periodic inspiratory gasp followed by expiratory wail), whereas emergency adult screams feature abrupt onset, high initial blast energy, and rapid decay.

3. **Shouted Commands:**
   - **Acoustic Mechanics:** Elevated phonation effort in spoken vowels ($A, O, E$).
   - **Overlap with Screams:** Elevated formant energies ($F_1, F_2$) and high intensity.
   - **Differentiating Feature:** Preserves structured linguistic formant transitions and lower fundamental frequency ($180 - 320\text{ Hz}$ for adult males/females).

---

## 2. Quantitative Acoustic Feature Overlap Analysis

Based on empirical extraction across the audited cohort ([`class_feature_distribution.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_32/analysis/class_feature_distribution.csv)):

| Acoustic Feature | Genuine Screams | Stadium Cheering | Infant Crying | Normal Speech | Separability Potential |
|---|---|---|---|---|---|
| **Spectral Centroid (Hz)** | $2,450 \pm 410$ | $2,280 \pm 380$ | $2,620 \pm 450$ | $1,320 \pm 220$ | Moderate (separates speech, overlaps cheering/crying) |
| **Spectral Bandwidth (Hz)** | $2,150 \pm 350$ | $2,380 \pm 310$ | $2,050 \pm 390$ | $1,480 \pm 260$ | Low |
| **Harmonic-to-Noise Ratio** | High / Nonlinear | Low (Diffuse) | High / Biphonic | High (Voiced) | **High (separates cheering)** |
| **Spectral Entropy** | $0.62 \pm 0.08$ | $0.81 \pm 0.06$ | $0.58 \pm 0.09$ | $0.48 \pm 0.07$ | **High (separates cheering)** |
| **Crest Factor (Peak/RMS)** | $5.8 \pm 1.2$ | $4.2 \pm 0.9$ | $5.1 \pm 1.1$ | $4.1 \pm 0.8$ | Moderate |
| **Cosine Sim to Scream Embedding** | **1.0000** | **0.9584** | **0.9672** | **0.7812** | Highlights severe confuser overlap in frozen space |

---

## 3. Visualizations

The spectral profile comparison figure is saved under:  
[`acoustic_feature_overlap.png`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_32/figures/acoustic_feature_overlap.png)

---

## 4. Implication for Stage 8.9.32 Representation Learning

Because standard pretrained audio representations (like YAMNet) assign high cosine similarity between screams, cheering, and crying, **supervised contrastive learning** is required to pull genuine scream embeddings into an isolated cluster while pushing cheering and crying embeddings into separate, distinct clusters.
