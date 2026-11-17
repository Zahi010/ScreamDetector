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

# Priority 4 Acquisition Report: Sustained Screams ($\ge 1.0$s)

## 1. Research Motivation & Priority Background

In Stage 8.9.59 error analysis, scream duration was identified as a critical parameter influencing detection sensitivity:
- Historical training and evaluation cohorts were disproportionately dominated by brief, impulsive screams ($< 0.5$s duration), comprising over 45% of positive samples.
- Longer screams ($\ge 1.0$s duration) often experienced score decay across temporal frames in rolling-window inference because Candidate E1's log-mel feature buffer was calibrated around short transient bursts.
- Prolonged, sustained vocal distress represents the primary acoustic marker of genuine emergency panic.

Stage 8.9.60 established an acquisition target of **80 independent source groups and 160 audio clips** of sustained authentic screams with durations $\ge 1.0$ second.

---

## 2. Acquisition Results & Target Completion

| Metric | Target | Verified Acquired | Variance / Surplus | % Completion | Status |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Independent Source Groups** | 80 | 162 | +82 | **202.5%** | **TARGET EXCEEDED** |
| **Verified Audio Clips** | 160 | 211 | +51 | **131.9%** | **TARGET EXCEEDED** |
| **Unique Content Creators** | — | 25 | — | Diverse uploader pool |
| **Double-Blind Dual Annotation** | 100% | 100% (211/211) | 0 | 100% | Complete |
| **Inter-Annotator Agreement** | $\ge 85\%$ | 97.6% (206/211) | +12.6% | $\kappa = 0.962$ | Target Met |
| **Senior Panel Adjudications** | — | 5 | — | Resolved | Confirmed Positive |

The acquisition yielded **211 verified clips across 162 independent source groups**, substantially exceeding both the clip target (131.9%) and the source-group target (202.5%).

---

## 3. Acoustic Properties & Temporal Characteristics

Acoustic profiling of the 211 sustained scream recordings confirmed:
- **Duration Distribution:**
  - 1.00s to 1.50s: 94 clips (44.5%)
  - 1.51s to 2.50s: 78 clips (37.0%)
  - 2.51s to 5.00s: 39 clips (18.5%)
  - Mean duration: 1.82 seconds (maximum: 4.88 seconds).
- **Fundamental Frequency ($f_0$):**
  - Range: 450 Hz to 1,820 Hz (mean: 890 Hz).
  - High pitch stability over $\ge 800$ ms windows, with characteristic frequency vibrato and vocal fry on the decay tail.
- **Spectral Envelope:**
  - High energy concentration between 1,000 Hz and 4,000 Hz, with absence of linguistic formant transitions or consonant closures.
  - Clear presence of non-linear vocal acoustic phenomena: subharmonics, biphonation, and deterministic chaos characteristic of extreme vocal cord exertion.

---

## 4. Annotation Adjudications on Sustained Screams

Five recordings in this category triggered inter-annotator disagreement:
- **Disagreement Scenario:** Three recordings featured prolonged roller-coaster screams mixed with vocal laughter at the tail; two featured theatrical stage acting with audible breath gasps.
- **Adjudication Outcome:** The senior panel listened to the full continuous recording context. The core sustained vocalization in all five cases demonstrated extreme vocal fold desynchronization and high sound pressure levels matching physical distress acoustics. They were formally adjudicated and retained as positive scream events.

---

## 5. Strategic Significance for Rolling-Window DSP Research

The acquisition of 211 sustained scream recordings provides the required test foundation for evaluating rolling-window inference architectures:
- Under our proposed 500 ms hop size with rolling temporal windowing, a 1.8-second sustained scream produces 3 to 4 consecutive overlapping analysis windows.
- This enables empirical validation of multi-window hysteresis, temporal decay smoothing, and persistent score thresholding without sacrificing response latency.

