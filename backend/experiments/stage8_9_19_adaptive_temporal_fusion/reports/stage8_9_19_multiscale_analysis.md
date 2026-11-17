# Stage 8.9.19 Multi-Scale Temporal Analysis: Resolution Decomposition & Uncertainty Estimation

**Status:** COMPLETE — RESEARCH EXPERIMENTATION STAGE  
**Candidate Status:** REJECTED — RESEARCH ONLY  
**Author:** Senior Audio AI Researcher & Signal-Processing Specialist  

---

## 1. Architectural Motivation

A key discovery in Stage 8.9.18 was that the 1D Dilated Temporal CNN (Model B) failed disproportionately on brief screams ($\le 1.5$s), achieving only 78.57% short-scream recall. Analysis revealed this was not due to an acoustic misclassification of scream phonation, but rather a **temporal receptive field starvation**:
- The dilated CNN architecture required a minimum receptive field of 32–48 frames ($\sim 1.0–1.5$s) to establish syllabic modulation and phonation continuity.
- Brief screams of 250–500 ms presented zero-padded or incomplete frame sequences, causing the convolutional activations to collapse.
- Conversely, static pooled embeddings (such as $D_{v4}$) flattened the entire sequence, discarding the temporal modulation cues necessary to reject shouted speech.

To solve this, Stage 8.9.19 formulated an explicit **Multi-Scale Temporal Decomposition Framework** that decomposes the audio stream across three operational temporal resolutions.

```
                      +---------------------------------------+
                      |         Raw Audio Stream              |
                      +---------------------------------------+
                                          |
                        Short-Time Windowing (70 frames x 32ms)
                                          |
            +-----------------------------+-----------------------------+
            |                             |                             |
    [0 - 512 ms]                  [512 - 1024 ms]               [1024 - 2240 ms]
    SHORT-SCALE BRANCH            MEDIUM-SCALE BRANCH           LONG-SCALE BRANCH
    - Onset attack time           - Consonant closures          - Sustained phonation
    - Peak onset RMS              - Syllabic cadence            - Plateau duration
    - Crest factor                - Energy modulation depth     - Harmonic continuity
    - HF turbulence (>6kHz)       - Spectral flux variance      - Syllable frequency
            |                             |                             |
    Confidence: c_short           Confidence: c_med             Confidence: c_long
    Mask: m_short                 Mask: m_med                   Mask: m_long
            +-----------------------------+-----------------------------+
                                          |
                      +---------------------------------------+
                      | Missing-Context Uncertainty Estimator |
                      |    u_long = 1.0 - c_long              |
                      +---------------------------------------+
```

---

## 2. Temporal Scale Specifications

### 2.1 Short-Scale Branch ($0 - 512$ ms / Frames 0–16)
Designed for rapid acoustic event detection, distress onsets, and abrupt energy transitions.
- **Onset Attack Time ($\tau_{attack}$):** The time required for RMS energy to rise from 10% to 90% of local peak amplitude. Genuine screams exhibit explosive onsets ($\tau_{attack} < 45$ ms), whereas speech shouting typically exhibits gradual vocal tract buildup ($\tau_{attack} \sim 80–180$ ms).
- **Peak Onset RMS:** Maximum instantaneous power within the initial 500 ms window.
- **Onset Crest Factor:** Ratio of peak onset amplitude to RMS energy, quantifying impulsive vocal burstiness.
- **High-Frequency Turbulence Ratio ($HF_{turb}$):** Proportion of acoustic energy residing above 6.0 kHz during onset, distinguishing turbulent unvoiced screaming from voiced vowel shouting.
- **Onset Spectral Flux:** First-order differential of spectral magnitudes across adjacent frames, capturing sudden acoustic disarray.

### 2.2 Medium-Scale Branch ($512 - 1024$ ms / Frames 16–32)
Designed to analyze speech articulation dynamics and syllabic cadence.
- **Consonant Closure Count ($N_{closure}$):** Number of acoustic dropouts where RMS energy falls below 15% of the local median while zero-crossing rate spikes, indicating consonant stop-closures (/p/, /t/, /k/) characteristic of speech.
- **Syllabic Cadence Modulation:** Energy envelope oscillation frequency within the $3–8$ Hz linguistic band.
- **Modulation Depth:** Variance of the filtered envelope, separating continuous phonation from modulated speech syllables.

### 2.3 Long-Scale Branch ($1024 - 2240$ ms / Frames 32–70)
Designed for evaluating sustained distress calls and background acoustic consistency.
- **Sustained Phonation Plateau:** Duration of unbroken vocal fold excitation exceeding 50% of peak energy.
- **Harmonic Correlation Plateau:** Frame-to-frame cross-correlation of spectral peaks, measuring pitch stability.
- **Linguistic Repetition Rate:** Autocorrelation peaks in the $150–350$ ms lag range, identifying repetitive chant/speech rhythm.

---

## 3. Context Uncertainty & Missing-Context Handling

A critical principle of Stage 8.9.19 is: **Missing temporal context is NOT evidence of non-screaming.**

When an acoustic event terminates after 350 ms:
1. The **Short-Scale Branch** receives full context: $c_{short} = 1.0, m_{short} = 1.0$.
2. The **Medium-Scale Branch** receives partial context: $c_{med} = 350 / 1024 = 0.34, m_{med} = 0.0$.
3. The **Long-Scale Branch** receives negligible context: $c_{long} = 350 / 2240 = 0.16, m_{long} = 0.0$.
4. **Missing-Scale Uncertainty:** $u_{long} = 1.0 - c_{long} = 0.84$.

Rather than allowing the zero-padded long branch to suppress the classification score, the adaptive fusion engine reads $u_{long}$ and shifts classification authority to the short-scale onset branch.

---

## 4. Empirical Evaluation by Duration Bracket

Performance of the Multi-Scale Router (Model C) vs. Baseline Pooled ($D_{v4}$) and Baseline Temporal CNN (Model B) across event durations:

| Duration Bracket | Test Cohort Count | Baseline $D_{v4}$ Recall | Model B (CNN) Recall | Model C (Multi-Scale) Recall | Model E (Attention) Recall |
|---|:---:|:---:|:---:|:---:|:---:|
| **$< 0.5$ s** | 0 | — | — | — | — |
| **$0.5 - 1.0$ s** | 13 | 92.31% | 84.62% | **100.0%** (13/13) | 84.62% (11/13) |
| **$1.0 - 1.5$ s** | 9 | 66.67% | 88.89% | **100.0%** (9/9) | 55.56% (5/9) |
| **$> 1.5$ s** | 56 | 76.79% | 62.50% | **89.29%** (50/56) | 50.00% (28/56) |
| **All Screams $\le 1.5$s** | 22 | 81.82% | 86.36% | **100.0%** (22/22) | 72.73% (16/22) |
| **Independent Short Cohort** | 14 | 92.86% | 85.71% | **100.0%** (14/14) | 85.71% (12/14) |

### Key Observations:
1. **Zero Misses on Short Screams:** Model C achieved 100% recall on all 22 screams with duration $\le 1.5$s in the held-out test split. The short-scale onset features reliably capture the explosive attack profile of brief distress calls without requiring long-context convolutional confirmation.
2. **Long-Scream Dilemma:** On sustained events ($>1.5$s), Model C achieved 89.29% recall, missing 6 screams that were either heavily reverberant or embedded in extreme festival music interference.
