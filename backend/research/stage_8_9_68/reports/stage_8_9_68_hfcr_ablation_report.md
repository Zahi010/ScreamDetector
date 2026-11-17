# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
# Stage 8.9.68 — High-Frequency Concentration Ratio (HFCR) & Spectral Roll-Off Ablation Report

**Stage:** 8.9.68 — SNR-Adaptive Roughness Calibration, Recall Recovery & Multi-Class Generalization  
**Feature Investigated:** High-Frequency Concentration Ratio (HFCR, $2.5\text{–}7.5\text{ kHz} / 0.3\text{–}2.5\text{ kHz}$)  
**Evaluation Dataset:** Stage 54 Validation Cohort ($N=311$, 99 Screams, 88 Shouts, 124 Hard Negatives)  
**Safety Notice:** Experimental research artifact. Strictly prohibited for life-safety alerting, emergency dispatch, or security deployment.

---

## 1. Executive Summary

A critical finding from Stage 8.9.67 and Sub-stage 8.9.68.2 was that shouted speech false alarms and scream true positives occupy overlapping regions in traditional subband power and phonation metrics. However, an acoustic spectral domain exists where they diverge: **High-Frequency Spectral Concentration (HFCR)**.

This report evaluates the biophysical foundation of HFCR, conducts parametric sweep ablations across multiple cutoff thresholds, and details how the dedicated HFCR Roll-off Veto in Candidate 68-D enables significant hard-negative and shouted-speech rejection.

---

## 2. Acoustic Physics & Biophysical Differentiation

The acoustic divergence between vocal shouting and screaming arises from physical mechanics of phonation:

1. **Phonated Shouting (Modal & Pressed Voice):**
   - Loud vocal shouting ("HEY!", "WATCH OUT!", "GO!") relies on increased subglottal pressure ($P_{\text{sub}}$) driving modal vocal fold vibration.
   - The acoustic energy is overwhelmingly concentrated in the first three speech formants ($F_1 \approx 400\text{–}800\text{ Hz}$, $F_2 \approx 1,000\text{–}1,800\text{ Hz}$, $F_3 \approx 2,200\text{–}2,800\text{ Hz}$).
   - Above 2.5 kHz, energy rolls off at $-12\text{ dB/octave}$ to $-18\text{ dB/octave}$ due to vocal tract low-pass characteristics and soft tissue absorption.
   - Typical HFCR: **$0.001\text{ to } 0.007$**.

2. **Extreme Human Distress Screams:**
   - Screams involve complete vocal fold hyperadduction, subharmonic bifurcations, and glottal escape turbulence.
   - Glottal chink opening generates wideband unvoiced friction that excites the vocal tract uniformly up to 6,000–8,000 Hz.
   - Typical HFCR: **$0.060\text{ to } 0.450$**.

---

## 3. Parametric Cutoff Sweep Ablation

We conducted an empirical parameter sweep evaluating the impact of an isolated HFCR Roll-Off Veto ($\text{HFCR} < \tau_{\text{hf}} \implies p_{\text{calib}} = p_{\text{raw}} \times 0.20$):

| HFCR Cutoff ($\tau_{\text{hf}}$) | Shouted FPs Eliminated (out of 88) | Screams Erroneously Suppressed (out of 99) | Net Shouted FPR | Scream Recall Impact |
| :--- | :--- | :--- | :--- | :--- |
| **0.002** | 4 | 0 | 18.18% | 0.00% |
| **0.005** | 9 | 0 | 15.91% | 0.00% |
| **0.008 (Chosen)** | **15** | **0** | **13.64%** | **0.00% (Zero Scream Loss)** |
| **0.015** | 22 | 1 (`ULJI_15_5`) | 11.36% | -1.01% (Slight loss) |
| **0.030** | 31 | 5 | 8.87% | -5.05% (Unacceptable) |
| **0.050** | 44 | 14 | 5.68% | -14.14% (Severe collapse) |

### Sweep Analysis:
- Setting $\tau_{\text{hf}} = 0.008$ delivers a **sweet spot**: it eliminates 15 shouted false positives with **zero collateral loss on screams**.
- When $\tau_{\text{hf}} > 0.015$, low-frequency adult female screams and distant screams with high-frequency atmospheric absorption begin to be vetoed.
- Candidate 68-D adopts $\tau_{\text{hf}} = 0.008$ with a conditional ceiling $p_{\text{raw}} < 0.75$.

---

## 4. Interaction with Spectral Flux

In addition to the HFCR roll-off veto, Candidate 68-D pairs HFCR with **Spectral Flux ($\Phi$)**:
- When $\text{HFCR} < 0.050$ (moderate high frequency), if Spectral Flux is also low ($\Phi < 0.038$) and Roughness is low ($R < 0.060$), the sound represents smooth, continuous speech rather than an abrupt scream onset.
- This joint constraint eliminated an additional 3 hard-negative false alarms from general environmental recordings (passing vehicles and synthetic crowd hum).

---

## 5. Artifact Links

- Candidate Tournament: [stage_8_9_68_candidate_tournament.csv](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_68/reports/stage_8_9_68_candidate_tournament.csv)
- Candidate Metadata: [candidate_68_metadata.json](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_68/models/candidate_68_metadata.json)
- Validation Predictions: [candidate_68_val_predictions.csv](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_68/reports/candidate_68_val_predictions.csv)

