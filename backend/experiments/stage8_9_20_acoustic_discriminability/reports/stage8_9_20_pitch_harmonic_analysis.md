# Stage 8.9.20 Pitch & Harmonic Analysis Report: Fundamental Frequency, Perturbation Metrics & Formant Structure

**Status:** COMPLETE — RESEARCH EXPERIMENTATION STAGE  
**Candidate Status:** REJECTED — RESEARCH ONLY  
**Author:** Computational Acoustics Specialist & Senior Audio AI Researcher  

---

## 1. Physical Acoustic Foundations

To separate genuine panic screams from intentional human shouting, we examined the physical dynamics of the vocal tract and vocal fold biomechanics:

```
+---------------------------------------------------------------------------------------------------+
|  Acoustic Dimension             | Shouted Speech & Vowels           | Genuine Panic Screams       |
+---------------------------------+:----------------------------------+:----------------------------+
|  Primary Vocal Mode             | Modal Phonation / High Subglottal | Desynchronized Biphonation  |
|  Fundamental Frequency (F0)    | 180 – 350 Hz (Male/Female)        | 550 – 1100 Hz (Elevated)    |
|  Pitch Period Jitter            | Low (< 2.5% period variation)     | Severe (> 8.0% or chaotic)  |
|  Amplitude Shimmer              | Low (< 4.5% amplitude variation)  | Severe (> 12.0% modulation) |
|  Harmonic-to-Noise Ratio (HNR)  | High (14 – 22 dB, Harmonic peaks) | Low (0 – 7 dB, High Noise)  |
|  First Formant (F1)             | Stable vowel pole (500 – 850 Hz)  | Elevated / Shifted (>1 kHz) |
|  Formant Trajectory Stability   | Stable vowel formant tracks       | Erratic or Collapsing Poles |
|  Pitch Tracker Reliability      | High (> 85% Voiced Frames)        | Low (< 30% Voiced Frames)   |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Empirical Statistical Comparison

Measured across held-out test recordings (78 screams vs. 84 shouting files):

| Feature Descriptor | Shouted Speech Mean (Std) | Genuine Screams Mean (Std) | Separability p-value | Acoustic Diagnostic Power |
|---|:---:|:---:|:---:|:---:|
| **Fundamental Frequency ($F_0$)** | 242 Hz (55 Hz) | 684 Hz (148 Hz) | $p < 0.0001$ | High in near-field clean audio |
| **Pitch Jitter Ratio** | 0.021 (0.008) | 0.084 (0.035) | $p < 0.0001$ | **Critical discriminator** |
| **Amplitude Shimmer Ratio** | 0.042 (0.015) | 0.145 (0.052) | $p < 0.0001$ | **Critical discriminator** |
| **Harmonic-to-Noise Ratio (HNR)** | 16.8 dB (3.8 dB) | 4.2 dB (5.5 dB) | $p < 0.0001$ | **Primary shout identifier** |
| **First Formant ($F_1$)** | 745 Hz (82 Hz) | 1042 Hz (185 Hz) | $p < 0.001$ | Distinct vowel cavity resonance |
| **Formant Dispersion ($F_2 - F_1$)** | 655 Hz (140 Hz) | 1558 Hz (320 Hz) | $p < 0.0001$ | Distinguishes static vowels |
| **Voiced Frame Ratio ($P_{voiced}$)** | 0.74 (0.16) | 0.28 (0.21) | $p < 0.0001$ | Pitch failure indicator |
| **Pitch Tracking Failure Rate** | 4.8% | **58.9%** | $p < 0.0001$ | **Scream signature flag** |

---

## 3. The Pitch Tracking Failure Paradox

A critical discovery in Stage 8.9.20 is that **pitch tracking algorithms (autocorrelation, Yin) fail on 58.9% of genuine screams**:
- When vocal folds undergo chaotic non-linear bifurcations under extreme adrenaline arousal, periodic harmonic vibration collapses into a broadband noise-like excitation.
- Standard pitch trackers report zero pitch or unvoiced frames.
- *Engineering Principle:* In our detector, **pitch tracking failure is treated as positive evidence for screams**, provided high-frequency turbulence and rapid onset energy are detected simultaneously.
- When an acoustic event is loud, has rapid onset, but fails periodic pitch estimation ($pitch\_failure\_flag == 1$), it is strongly indicative of unvoiced scream turbulence rather than speech.

---

## 4. Sustained Shouted Vowels ("NOOO!", "HEYYY!")

Spectrographic dissection of the 18 shouting false alarms from Stage 8.9.19 revealed:
- When humans shout sustained vowels (*"NOOO!"*, *"HEYYY!"*), they hold vocal tract resonances steady for 400–800 ms.
- Their LPC formant poles remain rigidly locked: $F_1 \approx 720$ Hz, $F_2 \approx 1350$ Hz ($F_2 - F_1 \approx 630$ Hz).
- By incorporating **Formant Dispersion and HNR verification** in Model B, shouting false alarms were reduced from **20.24% down to 14.29%**, passing Gate 3 for the first time on a pure acoustic model!
