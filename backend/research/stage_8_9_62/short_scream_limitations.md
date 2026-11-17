# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.62 — Short-Scream Acoustic & Representation Limitations

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary

This document formalizes the fundamental acoustic and architectural limitations that prevent the current Candidate E1 and Candidate B architectures from achieving reliable detection on short-duration screams ($< 1.0$s duration). 

With 40 out of 69 short screams ($57.97\%$) missed across every evaluated model configuration, the limitation is not an engineering artifact of threshold selection or hop alignment; it is a structural representation bottleneck in the fixed-scale feature extraction pipeline.

---

## 2. Core Technical Bottlenecks

### 2.1 Fixed 1.0-Second Time-Frequency Integration
- **Current Architecture:** Both Candidate B and Candidate E1 use a fixed 1.0-second (16,000 samples) analysis frame. The C5 DSP filterbank averages spectral magnitude across all 61 STFT frames to produce a static 128-dimensional subband vector.
- **The Failure Mode:** When an acoustic event lasts 300 ms, the remaining 700 ms of the window consists of silence or ambient background. Averaging across the entire 1.0-second frame mathematically dilutes the acoustic energy of the short scream by $-5 \text{ dB}$ to $-8 \text{ dB}$.
- **Consequence:** The neural network interprets the diluted energy vector as low-level ambient noise, causing the output probability to collapse below the operating threshold ($p \ll 0.60$).

### 2.2 Lack of Dynamic Energy Normalization Across Active Frames
- **Current Implementation:** Features are normalized using global fixed scalers computed over 1.0-second sustained samples.
- **Limitation:** The feature extractor does not perform Voice Activity Detection (VAD) or energy bounding prior to pooling. It computes energy across the entire fixed window regardless of how much of the window is occupied by active signal.
- **Consequence:** A high-intensity 400 ms scream produces an identical pooled feature vector to a very faint, distant 1.0-second scream, confounding acoustic intensity with event duration.

### 2.3 Loss of Temporal Modulation & Onset Dynamics
- **Current Implementation:** The 61 STFT temporal frames are collapsed into a single time-averaged vector $\mathbf{v} \in \mathbb{R}^{128}$.
- **Limitation:** Human distress shrieks are characterized by sharp onset transients (rapid attack time $< 30$ ms) and violent non-linear vocal fold phenomena (subharmonics, deterministic chaos, biphonation). By time-averaging the spectrogram, all onset velocity and spectral flux information is erased.
- **Consequence:** The classifier cannot distinguish between a sudden sharp shriek and a slow, gradual acoustic rise of equivalent average energy.

### 2.4 Training Distribution Duration Imbalance
- **Historical Dataset Bias:** In Candidate E1's training partition (`expansion_train`, Stage 8.9.54), $>85\%$ of scream samples were sustained vocalizations manually cropped or selected for clean 1.0-second duration.
- **Limitation:** The loss function during training was overwhelmingly dominated by sustained screams. The classifier learned decision boundaries optimized for sustained harmonic resonance rather than brief acoustic bursts.
- **Consequence:** The network's internal representations assign near-zero gradient importance to brief acoustic transients.

---

## 3. Necessary Architectural Paradigms for Short-Event Resolution

Overcoming the short-scream blind spot requires moving beyond single-scale, time-averaged filterbanks:
1. **Multi-Resolution Analysis:** Parallel STFT feature extractors operating at 250 ms (high temporal resolution), 500 ms, and 1000 ms (high frequency resolution).
2. **Active-Segment Energy Pooling:** Temporal pooling weighted by local frame energy (e.g., softmax pooling or energy-gated attention) rather than uniform arithmetic averaging.
3. **Dedicated Transient-Event Classification Head:** A specialized neural network branch trained exclusively on sub-second vocal bursts with duration-balanced loss weighting.

