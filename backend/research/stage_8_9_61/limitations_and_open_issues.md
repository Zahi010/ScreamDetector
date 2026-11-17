# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.61 — Acoustic Limitations, Trade-Offs & Open Research Issues

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary

Stage 8.9.61 systematically resolved the long-standing temporal alignment question: advancing an analysis window continuously via rolling 500 ms hops increases sustained scream sensitivity from 69.47% to 86.26%. However, independent evaluation across 453 unseen source groups revealed fundamental acoustic trade-offs and structural limitations inherent in single-frame subband classification.

This document enumerates the open engineering and acoustic limitations that currently prevent the system from meeting life-safety standards.

---

## 2. Primary Acoustic & Architectural Limitations

### 2.1 The Continuous Streaming Multiple-Testing Penalty
Continuous acoustic monitoring inherently subjects streaming audio to repeated inference calls (2 inferences per second for 500 ms hops). If the per-frame false positive probability is $\alpha_w \approx 0.08$:
- Over a 10-second monitoring window (19 evaluation hops), the cumulative probability of at least one false alarm exceeds $1 - (1 - 0.08)^{19} \approx 79.5\%$.
- While Exponential Moving Average smoothing ($\alpha=0.50$) filters out single-frame spikes, sustained non-target acoustic activity (such as 2–3 seconds of continuous cheering or loud laughter) inevitably charges the EMA accumulator above $\theta=0.6000$.
- **Open Issue:** A single-frame classifier cannot be deployed in continuous streaming mode without a high-level temporal sequence model (e.g., Hidden Markov Model, temporal CRF, or recurrent state-space architecture) trained explicitly on streaming backgrounds.

### 2.2 Short-Scream Blind Spot ($< 1.0$s Vocalizations)
On the sealed evaluation cohort, short-scream recall remained stagnant at **39.13% (27/69)** across all models:
- The underlying C5 filterbank requires a fixed 16,000-sample (1.0-second) input window.
- When a 300 ms or 500 ms panic shriek is captured in a 1.0-second frame, the remaining 500–700 ms consists of silence or background ambience.
- The STFT integration dilutes the high-frequency formant energy across multiple time bins, causing the mean subband energy vector to fall below the classifier's activation threshold.
- **Open Issue:** Solving short-scream detection requires multi-scale analysis (e.g., parallel 250 ms, 500 ms, and 1000 ms receptive fields) or adaptive wavelet-based feature extraction.

### 2.3 Acoustic Overlap Between Panic Screams and Ecstatic Cheering
Cheering, chanting, and stadium crowd roar generated the highest false-positive rate across all hard-negative subgroups:
- Static Candidate E1: **32.00% FPR** (16/50).
- Candidate B Baseline: **36.00% FPR** (18/50).
- Rolling EMA Candidate E1: **58.00% FPR** (29/50).
- Human distress screams and joyous cheers share fundamental acoustic properties: high fundamental frequency ($F_0 > 800$ Hz), non-linear vocal fold phenomena (subharmonics, biphonation, deterministic chaos), and elevated vocal effort.
- **Open Issue:** Subband energy vectors cannot differentiate emotional valence (fear vs joy). A linguistic or phonetic front-end (phoneme discriminator or speech-to-intent model) is required to reject ecstatic cheers.

### 2.4 Vulnerability to High-Pitch Synthetic Distractors (Whistles)
Candidate E1's neural network, lacking explicit domain constraints, misclassified **25.00% (15/60)** of referee whistles and squeaks under rolling evaluation. In contrast, Candidate B paired with Intervention D reduced whistle false alarms to **1.67% (1/60)**.
- Purely data-driven neural nets are susceptible to out-of-distribution acoustic phenomena with high energy in the 2.5–4.5 kHz range.
- **Open Issue:** Pure neural classifiers must be augmented with deterministic DSP guardrails (e.g., harmonic-to-noise ratio and spectral peak bandwidth checks) to prevent trivial false alarms.

### 2.5 Insufficient Sample Size for Rare Distress Categories
While the sealed cohort provided robust sample sizes for sustained screams ($N=131$) and shouted speech ($N=150$), specific critical categories remain severely underrepresented:
- Priority 2 (Crowd-Masked Screams): **$N = 4$ recordings** (1 unique source group).
- Infant Crying: **$N = 19$ recordings** (6 unique source groups).
- Priority 1 (Low-Intensity Screams): **$N = 27$ recordings** (21 unique source groups).
- **Open Issue:** While Rolling E1 achieved 100% (4/4) on crowd-masked screams, an $N=4$ sample has a 95% Wilson CI spanning $[51.0\%, 100.0\%]$. Future research must focus on synthetic acoustic mixing (injecting clean screams into calibrated festival crowd beds) to generate statistically valid benchmark cohorts.

---

## 3. Summary of Research Roadmap Priorities

1. **Multi-Scale Temporal Receptive Fields:** Transition from fixed 1.0s STFT windows to multi-resolution filterbanks to capture sub-second shrieks without sensitivity dilution.
2. **Context-Aware Dynamic Thresholding:** Implement local background noise estimation (energy percentile tracking) to float operating thresholds dynamically during loud concert passages.
3. **Hybrid Neural-DSP Guardrails:** Permanently integrate Intervention D's whistle and squeak discriminators into any Candidate E successor.
4. **Discriminative Streaming Training:** Train temporal aggregation layers (e.g., CRFs or TCNs) directly on continuous multi-minute audio streams rather than isolated pre-sliced chunks.

