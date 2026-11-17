# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Short-Scream Dual-Blind Human Annotation Protocol — Stage 8.9.64

**Stage Designation:** STAGE 8.9.64  
**Date:** November 12, 2026  
**Status:** AUTHORITATIVE ANNOTATION SPECIFICATION  

---

## 1. Scope and Objective

This protocol governs the dual-blind human acoustic review and adjudication of candidate short-scream recordings ($\le 1.00$ second total clip duration). The objective is to produce unambiguous ground-truth annotations with millisecond-accurate onset/offset boundaries and calibrated vocalization categories, ensuring zero ground truth leakage from model predictions.

---

## 2. Core Acoustic Definitions & Discriminative Criteria

Annotators must strictly distinguish genuine distress/panic vocalizations from acoustic confounders:

| Acoustic Phenomenon | Defining Acoustic Characteristics | Admissibility |
| :--- | :--- | :---: |
| **Distress Scream** | High subglottal pressure, non-linear vocal tract bifurcations, high-frequency dispersion (1.5–4.5 kHz), prolonged rough exhalation. | **ACCEPT** |
| **Panic Shriek** | Extremely rapid onset (<20 ms), elevated pitch (F0 > 1,200 Hz), piercing harmonic overtones, duration typically 100–350 ms. | **ACCEPT** |
| **Sudden Startle** | Explosive vocal release following acoustic shock, rapid onset, moderate duration (150–400 ms). | **ACCEPT** |
| **Vocal Outcry** | Involuntary distress vocalization, elevated vocal effort, distinct emotional valence. | **ACCEPT** |
| **Shouted Speech / Cheers** | Formant structure governed by linguistic phonemes, lack of chaotic non-linearities, periodic voicing without subharmonic roughness. | **REJECT** |
| **Involuntary Grunt / Gasp** | Low acoustic energy, brief unvoiced inhalation, lacking characteristic high-frequency scream formant dispersion. | **REJECT** |
| **Laughter Burst** | Staccato rhythmic pulses (4–6 Hz pulse rate), non-continuous spectral energy. | **REJECT** |

---

## 3. Annotation Parameters & Scoring Rubrics

Each independent reviewer must record eight mandatory acoustic fields:

1. **Temporal Onset ($T_{\text{onset}}$):** Timestamp (seconds) where the vocal scream energy first emerges above the ambient noise floor.
2. **Temporal Offset ($T_{\text{offset}}$):** Timestamp (seconds) where the scream energy decays into ambient background noise.
3. **Event Duration ($\Delta T$):** Calculated as $T_{\text{offset}} - T_{\text{onset}}$. Must be $\le 1.00$ s for Gate 4 inclusion; $\le 0.50$ s for ultra-short classification.
4. **Primary Vocalization Category:**
   - `distress_scream`
   - `panic_shriek`
   - `sudden_startle`
   - `vocal_outcry`
5. **Acoustic Intensity:**
   - `high`: Prominent signal, high SNR (> +15 dB above background).
   - `moderate`: Clear vocalization, moderate SNR (+6 to +15 dB).
   - `low`: Muffled or distant vocalization, low SNR (< +6 dB, RMS $\le -24$ dB).
6. **Acoustic Masking Context:**
   - `none`: Clean foreground recording.
   - `crowd`: Festival, stadium, or ambient crowd murmurs overlapping signal.
   - `music`: Synthesizer, percussion, or brass instrumental background.
   - `reverberation`: Severe room impulse response / echo tail.
7. **Perceived Distance:**
   - `near`: Close-proximity microphone pickup (< 2 meters).
   - `moderate`: Room or intermediate acoustic distance (2–10 meters).
   - `distant`: Far acoustic source (> 10 meters, high air absorption).
8. **Annotation Confidence:** Continuous scalar from $0.00$ to $1.00$. Clips with confidence $< 0.70$ are rejected.

---

## 4. Dual-Blind Adjudication & Consensus Rules

1. **Reviewer Independence:** Annotator Alpha and Annotator Beta review audio clips independently without access to each other's ratings, previous annotations, or model predictions.
2. **Consensus Agreement (`CONSENSUS_AGREED`):** When both annotators assign the identical primary vocalization category and temporal onset disagreement is $\le 50.0$ ms.
3. **Primary Adjudication (`ADJUDICATED_PRIMARY`):** If categorical disagreement occurs between valid scream subcategories (e.g., `panic_shriek` vs `sudden_startle`), a senior acoustic adjudicator conducts a blind third review.
4. **Mandatory Exclusion:** If either annotator flags the clip as non-scream (e.g., shouting speech, laughter, grunt) or if temporal onset disagreement exceeds $100.0$ ms, the clip is quarantined and discarded from the development manifest.

