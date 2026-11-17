# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.63 — Hard-Negative Category Profiling & False-Positive Breakdown

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary

This report documents the category-level false-positive behavior of the scream detection system across the 117 hard negatives in the development cohort, broken down by acoustic class in [`false_positive_category_metrics.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_63/false_positive_category_metrics.csv).

---

## 2. Category-Specific False-Alarm Vulnerability

```
False Alarm Rate Breakdown by Acoustic Sound Class (Method A vs Baseline)
┌───────────────────────────────┬───────────────────┬───────────────────┬────────────────────┐
│ Sound Category                │ Baseline FPR (OR) │ Method A FPR (K=2)│ Absolute Reduction │
├───────────────────────────────┼───────────────────┼───────────────────┼────────────────────┤
│ Shouted Speech                │      100.00%      │      100.00%      │       0.00%        │
│ Referee Whistles & Squeaks    │       40.00%      │       20.00%      │      -20.00%       │
│ Crowd Cheering & Chants       │       45.45%      │       27.27%      │      -18.18%       │
│ Infant Crying                 │       33.33%      │       16.67%      │      -16.66%       │
│ Environmental Noise & Sirens  │       64.71%      │       32.94%      │      -31.77%       │
└───────────────────────────────┴───────────────────┴───────────────────┴────────────────────┘
```

---

## 3. Physical Causes of False Positives

### 1. Shouted Speech & Vocal Outcries
- **Acoustic Overlap:** Aggressive male and female shouts produce high subharmonic phonation, high F0 energy ($> 500$ Hz), and non-linear vocal fold turbulence that closely mimics distress screams.
- **Why Method A Fails on Shouts:** Sustained shouting lasts $> 1.0$s, maintaining consecutive high-probability hops. Shouted speech cannot be suppressed by temporal filtering alone; it requires fine-grained spectral harmonicity vetoes (e.g. Candidate B spectral masks).

### 2. Referee Whistles & Squeaks
- **Acoustic Overlap:** High acoustic energy concentrated in the $2$–$4$ kHz critical band.
- **Why Method A Succeeds on Whistles:** Whistle onsets and trills produce sharp, momentary transient spikes that rarely maintain scream-like subband spectral flatness across consecutive hops. Method A reduced whistle false alarms by **$-20.00\%$**.

### 3. Sirens & Industrial Alarms
- **Acoustic Overlap:** Frequency sweeps and high SPL continuous tones.
- **Why Method A Succeeds on Sirens:** Sweeping tones cross individual subbands quickly, producing isolated window activations. Requiring two consecutive windows reduces siren false alarms by **$-31.77\%$**.

---

## 4. Architectural Recommendations for Stage 8.9.64

1. **Integrated Harmonicity Veto:** Incorporate Candidate B's Intervention D whistle discriminator and harmonic-to-noise ratio (HNR) checks directly into the dual-resolution network.
2. **Formant Dispersion Checks for Shouted Speech:** Exploit the physical vowel formant dispersion present in speech (F1/F2 separation) which collapses during genuine panic screaming due to extreme pharyngeal constriction.

