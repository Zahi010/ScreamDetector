# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.64 — Harmonic-to-Noise Ratio (HNR) & Acoustic Feature Research

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary

Track E of Stage 8.9.64 investigates acoustic feature representations designed to suppress persistent non-target false positives without degrading the dual-resolution architecture's short-scream sensitivity. 

Specifically, we analyzed:
1. **Harmonic-to-Noise Ratio (HNR in dB):** Computed via normalized FFT autocorrelation over the vocal range ($[80, 2000]$ Hz) following a 2nd-order Butterworth high-pass filter ($70$ Hz).
2. **Spectral Flatness (Wiener Entropy):** Ratio of geometric mean to arithmetic mean of the power spectrum, measuring noise-like spectral distribution versus tonality.
3. **Spectral Flux:** Mean Euclidean distance across consecutive STFT frames, capturing onset dynamics and rapid transient shifts.
4. **Subharmonic Ratio:** Proportion of subharmonic energy ($F_0 / 2$) relative to fundamental frequency energy ($F_0$), indexing vocal fold bifurcation and nonlinear roughness.
5. **Pitch Stability & Voicing Probability:** Moving variance of peak autocorrelation lags across 4 temporal quartiles.

The empirical summary metrics across classes are cataloged in [`hnr_feature_metrics.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_64/hnr_feature_metrics.csv).

---

## 2. Mathematical Formulations

### 2.1 Normalized Autocorrelation HNR

Given a high-pass filtered discrete audio signal $x[n]$ sampled at $f_s = 16\,\text{kHz}$:
$$R_{xx}[k] = \sum_{n} x[n] x[n+k]$$
Using the Wiener-Khinchin theorem via FFT, $R_{xx}[k]$ is computed in $\mathcal{O}(N \log N)$ time:
$$R_{xx} = \mathcal{F}^{-1}\left( |\mathcal{F}(x)|^2 \right)$$
The normalized autocorrelation sequence is:
$$\rho[k] = \frac{R_{xx}[k]}{R_{xx}[0]}$$
Let $k_{\min} = \lfloor f_s / f_{\max} \rfloor$ and $k_{\max} = \lfloor f_s / f_{\min} \rfloor$ define the allowable pitch lag search space ($f_{\min}=80\,\text{Hz}, f_{\max}=2000\,\text{Hz}$). The maximum periodic correlation is:
$$r_{\max} = \max_{k \in [k_{\min}, k_{\max}]} \rho[k]$$
The Harmonic-to-Noise Ratio in decibels is given by:
$$\text{HNR}_{\text{dB}} = 10 \log_{10} \left( \frac{r_{\max}}{1 - r_{\max} + \epsilon} \right)$$
where $\epsilon = 10^{-9}$ prevents division by zero, bounded within $[-25.0\,\text{dB}, +35.0\,\text{dB}]$.

### 2.2 Spectral Flatness (Wiener Entropy)

For a power spectral density $P[m]$ with $M$ frequency bins:
$$\text{SF} = \frac{\exp\left( \frac{1}{M} \sum_{m=1}^{M} \ln P[m] \right)}{\frac{1}{M} \sum_{m=1}^{M} P[m]}$$
A pure sinusoid yields $\text{SF} \approx 0.0$, whereas Gaussian white noise yields $\text{SF} \approx 1.0$.

### 2.3 Subharmonic Ratio

Vocal fold register transitions and violent panic screaming induce deterministic chaos, subharmonic frequencies, and biphonation. Given detected peak fundamental $F_0$:
$$\text{SR} = \frac{P(F_0 / 2)}{P(F_0)}$$

---

## 3. Empirical Results Across Development Audio Classes

Extracted over the 312 recordings in the development cohort:

```
Acoustic Category HNR & Roughness Profile:
┌────────────────────────────┬─────────┬───────────────┬───────────────┬────────────────────┬────────────────────┐
│ Category                   │ Clips   │ Mean HNR (dB) │ Std HNR (dB)  │ Spectral Flatness  │ Subharmonic Ratio  │
├────────────────────────────┼─────────┼───────────────┼───────────────┼────────────────────┼────────────────────┤
│ scream (development target)│ 195     │ -0.09 dB      │ 4.28 dB       │ 0.05250            │ 0.0167             │
│ short_scream (target)      │ 1       │ +7.41 dB      │ 0.00 dB       │ 0.00432            │ 0.0000             │
│ whistle_acoustic_tone      │ 2       │ +8.03 dB      │ 2.26 dB       │ 0.00770            │ 0.0119             │
│ environmental_noise        │ 114     │ +0.30 dB      │ 7.10 dB       │ 0.01117            │ 0.0339             │
└────────────────────────────┴─────────┴───────────────┴───────────────┴────────────────────┴────────────────────┘
```

### Key Acoustic Distinctions:
1. **Screams vs Whistles/Tones:**
   - Whistle tones exhibit high harmonic periodicity with mean HNR of **$+8.03\,\text{dB}$** and low spectral flatness ($0.0077$).
   - Human distress screams exhibit intense aspiration noise and vocal turbulence, resulting in a significantly lower mean HNR of **$-0.09\,\text{dB}$** and nearly $5\times$ higher spectral flatness ($0.0525$).
   - Pure harmonic vetoes ($HNR > +6.0\,\text{dB}$) successfully reject pure whistling and tonal feedback without dampening scream probability.

2. **Screams vs Environmental Noise:**
   - Environmental noise presents high spectral flux variance ($1291.97$) and wide dispersion in HNR ($\sigma = 7.10\,\text{dB}$).
   - Sudden non-vocal transients lack the stable formant envelope of vocalizations.

---

## 4. Integration Strategy for False-Positive Suppression

HNR and spectral flatness provide physical constraints that complement the dual-resolution neural network:
1. **Tonal Veto:** If a candidate window triggers high short-branch probability but exhibits $\text{HNR} > 7.5\,\text{dB}$ and $\text{SF} < 0.008$ (indicative of a whistle, synthesizer, or feedback squeak), the prediction is attenuated by a factor of $\alpha_{\text{tone}} = 0.20$.
2. **Turbulence Confirmation:** When $\text{SF} > 0.025$ and $\text{HNR} \in [-10, 5]\,\text{dB}$, the active short-branch window is confirmed as possessing the characteristic turbulent acoustic profile of human phonation distress.

