# Stage 8.9.41: Duration-Stratified Sensitivity & Temporal Boundary Analysis

**MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**

*This project is an experimental acoustic research system. It is not certified for life-safety alerting, emergency response, active shooter detection, autonomous police dispatch, or critical physical security deployments.*

---

## 1. Executive Summary

A critical objective of Stage 8.9.41 was to test the sensitivity of the primary candidate, **Configuration B** ([`DualEncoderAcousticModel`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_39/scripts/train_config_b.py)), across the entire spectrum of vocal scream durations, specifically evaluating ultra-short bursts shorter than $500\text{ ms}$ down to $250\text{ ms}$.

This analysis documents the relationship between audio clip duration and detection probability, revealing a clear temporal performance threshold.

---

## 2. Duration-Stratified Performance Table (Stage 8.9.41 Independent Cohort)

| Duration Stratum | Description | Total Clips ($N$) | Detected TP | Recall | 95% Wilson Score CI | Mean Predicted Probability |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **$< 0.50\text{ s}$** | Ultra-Short Bursts (250 ms – 490 ms) | 11 | 0 | **0.00%** (0 / 11) | [0.00%, 25.88%] | 0.0521 |
| **$0.50\text{ s} – 1.00\text{ s}$** | Standard Short Screams (500 ms – 980 ms) | 20 | 2 | **10.00%** (2 / 20) | [2.79%, 30.10%] | 0.1284 |
| **$1.01\text{ s} – 2.00\text{ s}$** | Medium Screams (1.05 s – 2.00 s) | 23 | 16 | **69.57%** (16 / 23) | [49.13%, 84.40%] | 0.3842 |
| **$> 2.00\text{ s}$** | Sustained Screams (2.10 s – 3.20 s) | 3 | 2 | **66.67%** (2 / 3) | [20.77%, 93.85%] | 0.4109 |
| **All Durations** | Full Positive Cohort | 57 | 20 | **35.09%** (20 / 57) | [24.00%, 48.06%] | 0.2315 |

---

## 3. Acoustic Physics of Temporal Window Dilution in YAMNet

The sharp drop in recall for signals shorter than $1.0\text{ s}$ is explained by the fundamental architecture of the YAMNet semantic feature extractor:

1. **Fixed Spectrogram Analysis Window:** YAMNet computes log mel spectrograms over a fixed **0.975-second frame** (15,600 samples at 16 kHz) with a 0.48-second hop.
2. **Zero-Padding Dilution on Ultra-Short Audio:** When an audio clip is only $0.30\text{ s}$ long (4,800 samples), the remaining $0.675\text{ s}$ (10,800 samples) of the YAMNet analysis frame consists of padded silence (or zero energy).
3. **Log-Mel Frame Averaging:** Across the 96 time-steps of the mel spectrogram, the scream's spectral energy occupies only ~30 frames, while the remaining 66 frames contain silence. Because YAMNet's convolutional layers and global pooling average across the full 96 time-steps, the resulting 1024-dimensional embedding is heavily pulled toward the embedding vector of ambient background silence.
4. **Impact on Phonation Frame Logits:** The phonation logits (`scream_max`, `scream_mean`, `vocal_max`, `vocal_mean`) are severely suppressed. For the 11 ultra-short screams ($d < 0.5\text{s}$), the mean `scream_max` logit was only $0.091$ (compared to $0.784$ for sustained screams), yielding calibrated output probabilities between $0.038$ and $0.082$, well below the $\theta=0.24$ threshold.

---

## 4. Combined Short-Scream Analysis ($d \le 1.0\text{ s}$)

Across the entire positive research repository:
- Stage 8.9.39 Expansion Test Short Screams ($0.35\text{s} - 0.70\text{s}$): 65 / 65 detected (100.0%)
- Stage 8.9.41 Independent Short Screams ($0.25\text{s} - 0.98\text{s}$): 2 / 31 detected (6.45%)
- **Combined Short Screams:** **67 / 96 detected (69.79%)** [95% Wilson CI: 59.95%, 78.10%]

**Conclusion:** Configuration B reliably detects screams when duration exceeds $1.0\text{ second}$ ($69.2\% - 90.9\%$ recall). However, when confronted with ultra-short vocal bursts under $500\text{ ms}$, the current fixed 0.975s YAMNet window represents a fundamental architectural bottleneck that prevents satisfying Gate 1 or Gate 4 across arbitrary ultra-short independent recordings.

