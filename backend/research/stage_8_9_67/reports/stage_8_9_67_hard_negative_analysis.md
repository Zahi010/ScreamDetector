# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.67 HARD NEGATIVE ANALYSIS: Non-Scream Acoustic Rejection, Category Breakdown & Gate 2 Evaluation

**Safety Designation:** Non-certified experimental acoustic research prototype. Prohibited for life-safety alerting, emergency dispatch, police notification, active-shooter systems, or critical security operations. Safe recorded-audio playback only.

---

## 1. Executive Summary & Objective

In real-world festival and dense public acoustic environments, detectors are continuously bombarded by high-energy, non-scream acoustic events: emergency sirens, brass instruments, amplified music, cheering crowds, PA announcements, whistles, and pyrotechnics.

In Stage 8.9.66.1, Candidate 65-F revealed catastrophic susceptibility to diverse hard negatives when evaluated outside its development cohort, yielding a **59.68% False Positive Rate (74 false alarms out of 124 non-vocal/non-scream files)**.

This report documents:
1. Performance of all candidates across 124 diverse hard negative files in the source-independent Stage 54 validation set.
2. Category-by-category false positive analysis.
3. Why Candidate 67-D achieved an 85.1% relative reduction in false alarms (dropping FPR from 59.68% to 8.87%).
4. The remaining gap to the mandatory Gate 2 target ($\le 5.00\%$) and the specific acoustic triggers responsible.

---

## 2. Hard Negative Evaluation Results ($N=124$)

| Candidate ID | Hard Negative FP | Hard Negative TN | Hard Negative FPR (%) | Relative Error Reduction vs 65-F | Gate 2 Status ($\le 5.0\%$) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Candidate 65-F (Ref)** | 74 | 50 | **59.68%** | Baseline | FAILED (+54.68% over limit) |
| **Candidate 67-A (Base Retrain)** | 23 | 101 | **18.55%** | -68.9% | FAILED (+13.55% over limit) |
| **Candidate 67-B (Vocal Fusion)** | 14 | 110 | **11.29%** | -81.1% | FAILED (+6.29% over limit) |
| **Candidate 67-C (Contrastive Penalty)** | 17 | 107 | **13.71%** | -77.0% | FAILED (+8.71% over limit) |
| **Candidate 67-D (Champion Veto)** | **11** | **113** | **8.87%** | **-85.1%** | **FAILED (+3.87% over limit)** |

### Gate 2 Determination
Gate 2 requires a diverse hard-negative False Positive Rate of **$\le 5.00\%$** (no more than 6 false alarms out of 124).
- Candidate 67-D produced **11 false alarms (8.87%)**.
- While this marks an extraordinary engineering improvement over Candidate 65-F (slashing false alarms from 74 down to 11), **Gate 2 is formally FAILED**.
- Antigravity protocols require strict, unvarnished reporting of this gate failure.

---

## 3. Category-by-Category Forensic Breakdown

The table below details false positives across the six major hard-negative acoustic categories in `expansion_val`:

| Acoustic Category | Total Clips ($N$) | Candidate 65-F FP | Candidate 67-D FP | Category FPR (67-D) | Acoustic Mechanism |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Crowd & Festival Cheering** | 32 | 19 (59.4%) | 0 (0.0%) | **0.00%** | Full suppression via envelope roughness filtering |
| **Sirens & Emergency Alarms** | 18 | 13 (72.2%) | 4 (22.2%) | **22.22%** | High-frequency pitch sweeps mimicking scream contour |
| **Brass & Woodwind Overblow** | 21 | 14 (66.7%) | 3 (14.3%) | **14.29%** | Trumpet and sax flutter-tonguing generating false roughness |
| **Whistles & Synth Sweeps** | 19 | 11 (57.9%) | 2 (10.5%) | **10.53%** | High acoustic energy above 2.5 kHz bypassing HF ratio |
| **Intense Laughter / Cackle** | 16 | 9 (56.2%) | 2 (12.5%) | **12.50%** | Vocal fold bifurcations during chaotic laughter |
| **Festival PA & Music Beat** | 18 | 8 (44.4%) | 0 (0.0%) | **0.00%** | Full suppression via dual-resolution branch coordination |
| **Total** | **124** | **74 (59.68%)** | **11 (8.87%)** | **8.87%** | **Overall 85% relative improvement** |

---

## 4. Acoustic Profile of the 11 Remaining False Positives

### 1. Sirens and Emergency Alarms (4 clips)
Modern electronic sirens (particularly "wail" and "yelp" modes) generate rapid cyclic frequency modulations between 800 Hz and 2,500 Hz at modulation rates of 20–40 Hz. When these sweeps transit through the 1.5–3.0 kHz band, they trigger both the short-event energy detector and the auditory roughness filter.

### 2. Brass Overblow and Instrumental Flutter (3 clips)
Clips featuring jazz trumpet and tenor saxophone solos where the performer employs "flutter-tonguing" (rapid lingual trilling) combined with overblowing. This creates chaotic sidebands in the 1,000–3,000 Hz region with an envelope modulation rate of 30–60 Hz, mathematically mimicking the non-linear bifurcation of a vocal scream.

### 3. Whistles and Synthetic Sweeps (2 clips)
Referee and pea-whistles produce acoustic sound pressures exceeding 110 dB SPL at 2.8–3.5 kHz. The rolling pea inside the whistle chamber creates mechanical amplitude modulation at approximately 50 Hz. This physical modulation passes the roughness test and exhibits an extreme high-frequency energy ratio.

### 4. Chaotic Spastic Laughter (2 clips)
Laughter at peak intensity involves intermittent glottal closure and spasmodic respiratory contractions. When subjects laugh hysterically, their vocal folds undergo true physiological bifurcations identical to fear screams.

---

## 5. Architectural Path to Sub-5.0% FPR in Stage 8.9.68

To eliminate the remaining 5 excess false alarms and achieve Gate 2 compliance ($\le 5.00\%$):
1. **Harmonic Purity Metric:** Introduce an instantaneous cepstral peak prominence (CPP) measure to differentiate pure acoustic sirens from vocal turbulence.
2. **Frequency Modulation Contour Tracking:** Electronic sirens follow deterministic geometric waveforms (triangular/sinusoidal frequency trajectories), whereas screams exhibit stochastic, non-monotonic pitch fluctuations.
3. **Multi-Pitch Formant Tracking:** Human screams exhibit identifiable formants ($F_1$ around 1 kHz, $F_2$ around 2 kHz) that shift continuously, unlike musical instruments which maintain fixed resonant modes.

