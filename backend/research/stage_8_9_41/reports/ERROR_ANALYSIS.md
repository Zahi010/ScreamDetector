# Stage 8.9.41: Error Analysis & False Negative Review

**MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**

*This project is an experimental acoustic research system. It is not certified for life-safety alerting, emergency response, active shooter detection, autonomous police dispatch, or critical physical security deployments.*

---

## 1. Overview

During the evaluation of frozen Configuration B on the Stage 8.9.41 positive evaluation cohort ($N=57$), **20 recordings were detected as True Positives** ($\text{Recall} = 35.09\%$) and **37 recordings were missed as False Negatives**.

All 37 false negatives were extracted and compiled in [`backend/research/stage_8_9_41/reports/false_negative_review.csv`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_41/reports/false_negative_review.csv). This report provides an acoustic and spectro-temporal post-mortem into the failure modes.

---

## 2. False Negative Distribution Across Subtypes

| Acoustic Subtype | Total in Cohort | False Negatives | Miss Rate | Mean Predicted Probability |
|---|:---:|:---:|:---:|:---:|
| `short_scream` | 26 | 26 | **100.0%** | 0.0656 (Threshold: 0.24) |
| `masked_scream` | 8 | 4 | **50.0%** | 0.1742 |
| `low_intensity_scream` | 10 | 4 | **40.0%** | 0.1812 |
| `sustained_scream` | 2 | 2 | **100.0%** | 0.0604 |
| `distant_scream` | 11 | 1 | **9.1%** | 0.1984 |
| **Total** | **57** | **37** | **64.9%** | **0.1182** |

---

## 3. Acoustic Root Cause Analysis

### Failure Mode 1: Temporal Window Dilution on Ultra-Short Bursts (26 False Negatives)
- **Acoustic Profile:** Durations ranging from $0.25\text{ s}$ to $0.98\text{ s}$ (11 recordings $< 0.50\text{ s}$).
- **Mechanism:** YAMNet extracts features using a fixed 0.975-second spectrogram window. When an audio burst lasts only 250–500 ms, the remaining 50% to 75% of the frame consists of silence. In YAMNet's global pooling, the dense semantic features of the brief scream are averaged against silence, diluting the embedding towards ambient silence.
- **Model Activation:** The mean phonation logit `scream_max` for these clips was $0.091$ (vs. $0.85+$ in training positives), and calibrated output probabilities hovered between $0.038$ and $0.145$, failing to cross $\theta=0.24$.

### Failure Mode 2: Acoustic Masking in Dense Festival Noise (4 False Negatives)
- **Acoustic Profile:** Screams mixed with authentic stadium chant/crowd murmurs at low signal-to-noise ratios ($+3\text{ dB}$ to $+6\text{ dB}$).
- **Mechanism:** Crowd noise features heavy acoustic energy in the $700 - 1500\text{ Hz}$ vocal band. When the scream energy is comparable to or lower than the crowd bed, YAMNet's multi-class probabilities attribute the segment predominantly to AudioSet Class 67/68 (`Crowd` / `Cheering`).
- **Model Activation:** Predicted probabilities reached $0.165 - 0.218$, narrowly missing the $0.24$ threshold.

### Failure Mode 3: Low-Intensity / Breathy Aspiration (4 False Negatives)
- **Acoustic Profile:** Stifled screams characterized by low fundamental pitch ($f_0 \approx 650\text{ Hz}$) and high turbulent breath noise rather than clear harmonic saturation.
- **Mechanism:** The acoustic branch relies on phonation features that require high vocal pitch. In the absence of loud harmonic peaks, the model treats the recording as breathy environmental sound.

### Failure Mode 4: Guttural Subharmonic Distortion in Sustained Screams (2 False Negatives)
- **Acoustic Profile:** Screams with extreme vocal fry and frequency bifurcation ($f_0 / 2$).
- **Mechanism:** Strong energy at lower subharmonics ($350 - 450\text{ Hz}$) caused YAMNet to classify the vocalization as speech rather than a scream.

---

## 4. Remediation Pathways for Future Architecture Stages

1. **Multi-Scale Windowing:** Replacing YAMNet's monolithic 0.975s window with multi-resolution analysis (e.g. 250 ms, 500 ms, and 1000 ms sliding frames) to capture short bursts before energy dilution occurs.
2. **Dynamic Energy-Weighted Temporal Pooling:** Weighting frame embeddings by short-term RMS energy rather than uniform arithmetic mean, preventing silent padding from diluting active vocal bursts.
3. **Adaptive Thresholding:** Implementing SNR-aware decision boundaries for noisy festival environments.

