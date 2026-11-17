# MANDATORY SAFETY DESIGNATION

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**

This project is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

All experiments must use legally acquired recorded audio and safe recorded-audio playback only.

Strict prohibitions:
- No live-fire experiments.
- No real-world emergency-response testing.
- No autonomous emergency dispatch.
- No external emergency alerts.
- No police notification.
- No claims of life-safety efficacy.
- No production promotion.

---

# Priority 1 Acquisition Report: Low-Intensity & Muffled Screams

## 1. Research Motivation & Priority Background

In Stage 8.9.59 error analysis, Candidate E1 exhibited a marked vulnerability to false negatives on low-intensity, muffled, and distant screams:
- In the Stage 8.9.55 evaluation cohort, screams with RMS energy below 0.05 or peak amplitude below -18 dBFS experienced a 55.6% false-negative rate (10 of 18 missed).
- Candidate E1's log-mel energy representation and convolutional feature maps consistently attenuated spectral energy in lower-amplitude distress vocalizations, dropping confidence scores below the 0.450 decision threshold.

Stage 8.9.60 established an acquisition target of **50 independent source groups and 100 audio clips** specifically for low-intensity and muffled distress vocalizations.

---

## 2. Acquisition Results & Gap Quantification

| Metric | Target | Verified Acquired | Variance / Gap | % Completion |
| :--- | :---: | :---: | :---: | :---: |
| **Independent Source Groups** | 50 | 21 | -29 | 42.0% |
| **Verified Audio Clips** | 100 | 27 | -73 | 27.0% |
| **Unique Content Creators** | — | 21 | — | High Isolation (1.0 clip/creator) |
| **Double-Blind Dual Annotation** | 100% | 100% (27/27) | 0 | 100% |
| **Inter-Annotator Agreement** | >= 85% | 100.0% (27/27) | +15% | $\kappa = 1.00$ |

The acquisition yielded **27 valid, unconsumed clips across 21 independent source groups**. While this represents a valuable expansion over the historical baseline (which possessed only 18 low-intensity clips across all historical partitions combined), a remaining gap of 73 clips persists.

---

## 3. Acoustic Properties of Acquired Low-Intensity Clips

Acoustic analysis was performed across the 27 acquired clips:
- **Mean RMS Energy:** 0.0241 (range: 0.0048 to 0.0482).
- **Mean Peak Amplitude:** -16.8 dBFS (range: -24.1 dBFS to -9.2 dBFS).
- **Mean Duration:** 1.84 seconds (range: 0.85s to 3.42s).
- **Spectral Energy Distribution:** Dominant energy concentrated between 800 Hz and 2.4 kHz, with marked high-frequency attenuation above 4 kHz characteristic of distance propagation and acoustic absorption.

---

## 4. Root Cause Analysis: Scarcity in Permissive Open Repositories

Auditing candidate sound repositories (Freesound, FSD50K, Zenodo) revealed three structural reasons for the scarcity of low-intensity screams:
1. **Curator Recording Bias:** Amateur and professional audio recordists upload vocalizations with high signal-to-noise ratio, close-mic placement, and normalized peak amplitudes to maximize audio utility.
2. **Actor Theatrical Bias:** Audio libraries predominantly catalogue staged theatrical screams ("horror screams", "wilhelm screams", "game combat screams"), which feature maximum vocal effort and full acoustic projection.
3. **Keyword Misclassification:** Searching for "muffled scream" or "distant shout" frequently retrieved Foley footsteps, muffled speech, or cloth rustling rather than genuine distress vocalizations.

---

## 5. Remediation Roadmap for Future Research Stages

To safely close the remaining 73-clip / 29-source-group gap without violating research safety standards:
1. **Calibrated Physical Distance Attenuation Simulation:** Apply standardized ISO 9613-2 acoustic propagation filtering (air absorption, spherical divergence, barrier diffraction) to high-quality studio screams.
2. **Controlled Anechoic Playback & Re-recording:** Playback legally acquired high-intensity screams through calibrated loudspeakers inside anechoic/reverberant test chambers at controlled distance offsets (10m, 25m, 50m).
3. **Strict Policy Compliance:** Maintain zero-scraping and zero-life-safety use boundaries during any future simulation.

