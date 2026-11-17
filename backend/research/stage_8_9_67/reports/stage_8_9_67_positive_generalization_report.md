# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.67 POSITIVE GENERALIZATION REPORT: Distress Detection Recall, Failure Taxonomy & Gate 1 Trade-Off Analysis

**Safety Designation:** Non-certified experimental acoustic research prototype. Prohibited for life-safety alerting, emergency dispatch, police notification, active-shooter systems, or critical security operations. Safe recorded-audio playback only.

---

## 1. Executive Summary & Objective

A robust acoustic detector must reliably identify screams across diverse human speakers (children, adult females, adult males), varied emotional states (panic, surprise, fear), and challenging acoustic channels (reverberant spaces, distant sound sources, background crowd noise).

Gate 1 mandates an overall scream recall of **$\ge 96.00\%$** on previously unobserved source groups.

In Stage 8.9.67, Candidate 67-D achieved an overall recall of **73.74% (73 true detections out of 99 screams)** on the source-group-independent Stage 54 validation set.

This report documents:
1. Empirical recall across all evaluated candidates on independent validation screams ($N=99$).
2. The architectural trade-off between false-positive suppression (Gate 3 recovery) and scream sensitivity.
3. A granular forensic taxonomy of the 26 False Negatives produced by Candidate 67-D.
4. An actionable roadmap for recovering $\ge 96.0\%$ recall in Stage 8.9.68.

---

## 2. Positive Recall Across Evaluated Candidates ($N=99$)

| Candidate ID | True Positives (TP) | False Negatives (FN) | Overall Recall (%) | Gate 1 Status ($\ge 96.0\%$) |
| :--- | :---: | :---: | :---: | :---: |
| **Candidate 65-F (Ref)** | 86 | 13 | **86.87%** | FAILED (-9.13% under target) |
| **Candidate 67-A (Base Retrain)** | 78 | 21 | **78.79%** | FAILED (-17.21% under target) |
| **Candidate 67-B (Vocal Fusion)** | 74 | 25 | **74.75%** | FAILED (-21.25% under target) |
| **Candidate 67-C (Contrastive Penalty)** | 78 | 21 | **78.79%** | FAILED (-17.21% under target) |
| **Candidate 67-D (Champion Veto)** | **73** | **26** | **73.74%** | **FAILED (-22.26% under target)** |

### Gate 1 Determination
Candidate 67-D achieved **73.74% recall**, missing the 96.00% target by 22.26 percentage points.
**Gate 1 is formally FAILED.**

---

## 3. The Selectivity vs. Sensitivity Trade-Off

The primary objective of Stage 8.9.67 was to resolve the catastrophic shouted-speech false alarm crisis inherited from Candidate 65-F (where 48.86% of shouted speech was classified as screams).

To suppress shouted speech from 48.86% down to 13.64% (passing Gate 3), Candidate 67-D tightened decision criteria through:
1. High-frequency energy concentration ratio gating ($\text{HFCR} > -0.2$).
2. Minimum auditory envelope roughness thresholding ($R \ge 0.015$).
3. Multi-stage neural probability veto ($p \ge 0.45$).

While this successfully filtered out smooth, harmonic vocal yelling, it introduced collateral sensitivity losses: screams that were distant, reverberant, or low-intensity were rejected because their acoustic roughness was diluted by the environment.

```
       Sensitivity (Recall)
         ▲
 100% ───┼───────────────────────────────────────────── (Target Gate 1: 96.0%)
         │
  86.9% ─┼────────── Candidate 65-F (High recall, but 48.9% Shouted FPR!)
         │
  78.8% ─┼────────── Candidate 67-C
  73.7% ─┼────────── Candidate 67-D (Clean 13.6% Shouted FPR, but 73.7% Recall)
         │
   0% ───┴─────────────────────────────────────────────► Selectivity (FPR Suppression)
```

---

## 4. Forensic Taxonomy of the 26 False Negatives

A detailed acoustic examination of the 26 missed screams revealed four primary failure categories:

| Failure Category | Misses ($N$) | Percentage | Primary Acoustic Cause |
| :--- | :---: | :---: | :--- |
| **1. Distant / Low-SNR Screams** | 14 | 53.8% | Ambient background noise fills the envelope troughs, reducing measured roughness below $R < 0.015$. |
| **2. Reverberant / Hall Acoustics** | 6 | 23.1% | Room impulse response reflects diffuse energy, smoothing the 30–150 Hz envelope modulations. |
| **3. Low-Pitch Adult Male Screams** | 4 | 15.4% | Fundamental frequency below 400 Hz with weaker upper formant resonance ($< 2.5$ kHz). |
| **4. Breath-Depleted Screams** | 2 | 7.7% | Vocalist runs out of pulmonary air, causing the scream to decay into a chaotic whisper with low acoustic energy. |
| **Total Misses** | **26** | **100.0%** | |

### Acoustic Analysis of Category 1: Distant / Low-SNR Screams (14 clips)
When a scream occurs at a distance of 15 to 30 meters in an open festival space:
- Direct-to-reverberant ratio drops below 0 dB.
- Ambient crowd murmur and background pink noise provide continuous acoustic power across all frequency bands.
- The Hilbert transform envelope does not drop to zero between vocal fold glottal pulses; rather, noise floors elevate the trough.
- As a result, the computed modulation depth in the 30–150 Hz band drops from typical clean values ($0.08–0.15$) to $0.009–0.013$.
- Candidate 67-D's static roughness veto ($R < 0.015$) fires, incorrectly rejecting the clip.

### Acoustic Analysis of Category 2: Reverberant Hall Acoustics (6 clips)
In indoor or sheltered festival stages with reverberation time $RT_{60} > 1.2$ seconds, sound reflections arrive within 5 to 50 ms. These reflections superimpose out-of-phase onto the primary wave, acting as an acoustic low-pass filter on the temporal envelope and destroying high-frequency roughness.

---

## 5. Architectural Path to Reaching 96% Recall in Stage 8.9.68

To recover the 26 false negatives without compromising shouted-speech rejection:
1. **Dynamic Noise-Floor Adjusted Roughness:** Instead of an absolute roughness threshold ($R \ge 0.015$), normalize roughness against local channel SNR:
   $$R_{\text{norm}} = R \times \left(1.0 + \frac{1.0}{\max(\text{SNR}_{\text{est}}, 0.1)}\right)$$
2. **Multi-Scale Temporal Branching:** Add an intermediate 500 ms branch to capture screams whose onsets have clear roughness before room reverberation builds up.
3. **Adaptive Low-Frequency Energy Weighting:** Compensate for male screams by evaluating energy in the 1.5–3.5 kHz band rather than strictly above 2.5 kHz.

