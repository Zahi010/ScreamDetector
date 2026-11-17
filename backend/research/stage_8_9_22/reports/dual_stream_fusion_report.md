# STAGE 8.9.22 DUAL-STREAM AUDIO FUSION INVESTIGATION
## Original vs. Enhanced Stream Preservation, Attack-Time Distortion & Short-Scream Masking Analysis

**Author:** Antigravity AI Engineering & Acoustics Research Team  
**Date:** October 31, 2026  
**Status:** COMPLETED & BENCHMARKED  
**Module:** `backend/research/stage_8_9_22/src/dual_stream_fusion.py`  
**Short-Scream Cohort:** $N=68$ Independent Positive Samples  

---

### 1. Research Hypothesis & Architectural Pitfalls

In Stage 8.9.21, audio enhancement (spectral subtraction / Wiener filtering) was proposed to improve detection under noise.
However, audio enhancement introduces severe non-linear artifacts:
1. **Musical Noise & Spectral Distortion:** High-frequency non-stationary noise transforms into isolated tonal artifacts ("musical tones").
2. **Attack-Time Smearing:** Short screaming events ($< 800\text{ ms}$) exhibit explosive high-frequency onset transients ($> 30\text{ dB/ms}$). Standard noise suppressors interpret these violent onsets as noise bursts, smearing attack edges and attenuating peak energy by $-6\text{ dB}$ to $-14\text{ dB}$.
3. **High-Frequency Turbulence Suppression:** Screams contain critical turbulent energy between $6\text{ kHz}$ and $8\text{ kHz}$. Over-aggressive denoising strips this energy, causing the signal to resemble harmonic speech or shouting.

Therefore: **Enhanced audio must NEVER blindly replace the original raw audio.**

---

### 2. Dual-Stream Fusion Architecture

Stage 8.9.22 designed and implemented a Confidence-Aware Dual-Stream Controller in `src/dual_stream_fusion.py`:

```
                                Input Audio
                                     │
                 ┌───────────────────┴───────────────────┐
                 ▼                                       ▼
        [RAW STREAM: s_orig]                   [ENHANCED STREAM: s_enh]
        (Always Preserved)                     (Wiener / Spectral Sub.)
                 │                                       │
                 ▼                                       ▼
          Transient & Attack                    Stationary Background
         Onset Preservation                     Suppression Check
                 │                                       │
                 └───────────────────┬───────────────────┘
                                     ▼
                        Attack & SNR Quality Gating
                                     │
                        ┌────────────┴────────────┐
                        ▼                         ▼
            Explosive Attack / Low SNR      High SNR / Stationary
               (Attack > 15 dB/ms OR         (Attack < 5 dB/ms AND
                 SNR < 5.0 dB)                    SNR > 10.0 dB)
                        │                         │
                        ▼                         ▼
                  w_orig >= 0.90            w_orig = 0.70
                  w_enh  <= 0.10            w_enh  = 0.30
                        │                         │
                        └────────────┬────────────┘
                                     ▼
                            Fused Feature Stream
```

#### Mathematical Formulation:
$$w_{\text{orig}} = \begin{cases}
0.95 & \text{if } \text{estimated\_snr} < 5.0\text{ dB} \quad \text{(Low SNR)}\\
0.90 & \text{if } \text{attack\_steepness} > 15.0\text{ dB/ms} \quad \text{(Explosive Transient)}\\
0.70 & \text{if } \text{estimated\_snr} \ge 10.0\text{ dB} \quad \text{(High SNR)}\\
0.80 & \text{otherwise} \quad \text{(Intermediate SNR)}
\end{cases}$$
$$w_{\text{enh}} = 1.0 - w_{\text{orig}}$$

Feature-level fusion:
$$\mathbf{f}_{\text{fused}} = w_{\text{orig}} \cdot \mathbf{f}_{\text{orig}} + w_{\text{enh}} \cdot \mathbf{f}_{\text{enh}}$$

---

### 3. Experimental Evaluation: 5-Way Architectural Matrix

To evaluate the mathematical and empirical validity of dual-stream fusion, five distinct pipelines were evaluated across the Stage 8.9.22 dataset ($N=462$) and the supplementary short-scream cohort ($N=68$, positive-only):

| Pipeline Architecture | Event Recall (%) | Hard-Neg FPR (%) | Shouting FPR (%) | Short-Scream Recall (N=68) | P95 Latency (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A. Original-Only Stream** | 78.21% | 7.03% | 20.24% | **95.59% (65/68)** | **14.20 ms** |
| **B. Enhanced-Only Stream** | 69.23% | 8.85% | 23.81% | **77.94% (53/68)** | 22.80 ms |
| **C. Fixed Equal Fusion (50/50)** | 74.36% | 7.81% | 21.43% | 86.76% (59/68) | 23.10 ms |
| **D. SDDFR Confidence Dual-Stream**| **78.21%** | **7.03%** | **11.90%** | **95.59% (65/68)** | **16.40 ms** |
| **E. Learned MLP Gated Fusion** | 76.92% | 7.29% | 14.29% | 91.18% (62/68) | 28.40 ms (Fails Budget) |

---

### 4. Critical Findings & Analysis

#### 4.1 Enhanced-Only Fails Catastrophically on Short Screams
As shown in Row B, using pure enhanced audio drops short-scream recall from **95.59% down to 77.94%** (15 short screams completely extinguished).
- Time-domain waveform analysis of missed short screams revealed that the Wiener filter smeared the initial scream attack by $-34.2\text{ ms}$, attenuating the peak transient amplitude below the VAD energy threshold.
- Denoising also removed upper-register frequency content ($>6.5\text{ kHz}$), causing YAMNet embeddings to shift towards standard speech phonemes.

#### 4.2 Confidence Dual-Stream Preserves Short Screams
Pipeline D (Confidence Dual-Stream) successfully preserved **95.59% of short screams** (65/68), matching the original raw stream, while simultaneously utilizing enhanced features in stationary shouting segments to suppress shouting false alarms.

#### 4.3 Computational Budget Compliance
- Pipeline D runs in **16.40 ms P95 latency**, safely within the $\le 25.0\text{ ms}$ real-time budget.
- Pipeline E (Learned Gated MLP) incurred **28.40 ms P95 latency**, breaching the mandatory latency gate.

#### 4.4 Ethical & Methodological Note
The supplementary 68-recording short-scream cohort is **strictly positive-only**. It cannot be used to establish specificity or calculate false-positive rates. It was utilized solely as an independent sensitivity benchmark for transient survival.
