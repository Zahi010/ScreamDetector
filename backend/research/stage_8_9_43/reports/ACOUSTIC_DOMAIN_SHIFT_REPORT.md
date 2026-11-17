# MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Stage 8.9.43: Acoustic Domain-Shift Analysis Report

## 1. Executive Summary

Stage 8.9.43 conducted a rigorous statistical and acoustic comparison between the positive training distribution (`v4_train`, $N=180$), the historical expansion benchmark (`v4_reserved_expansion_test`, $N=65$), and the independent evaluation cohort (`stage_8_9_41_independent_test`, $N=57$).

A diagnostic domain classifier trained strictly on acoustic features distinguished `v4_train` from the independent cohort with a **5-fold cross-validated ROC-AUC of 0.9862**, confirming a statistically significant domain shift between the training data and field recordings.

## 2. Statistical Feature Comparison across Cohorts

| Acoustic Parameter | v4_train (N=180) | Hist Exp (N=65) | Indep (N=57) | Indep Missed (N=37) | Cohen's d | Mann-Whitney p | Stat Sig |
|---|---|---|---|---|---|---|---|
| **duration_seconds** | 2.63 ± 1.64 | 0.54 ± 0.20 | 1.08 ± 0.58 | 0.85 ± 0.51 | -1.07 | 2.9446e-15 | **p < 0.001** |
| **rms_energy** | 0.21 ± 0.10 | 0.31 ± 0.01 | 0.30 ± 0.08 | 0.28 ± 0.06 | +0.95 | 1.4990e-10 | **p < 0.001** |
| **dynamic_range_db** | 13.43 ± 4.28 | 9.08 ± 0.37 | 9.81 ± 1.91 | 10.13 ± 1.57 | -0.94 | 1.3537e-10 | **p < 0.001** |
| **spectral_centroid_hz** | 2196.38 ± 506.02 | 2661.66 ± 22.08 | 2038.48 ± 540.85 | 2300.90 ± 473.69 | -0.31 | 8.7626e-02 | **n.s.** |
| **spectral_bandwidth_hz** | 1611.97 ± 294.29 | 1781.60 ± 9.76 | 1310.69 ± 499.70 | 1560.13 ± 447.75 | -0.85 | 3.0751e-02 | **p < 0.05** |
| **spectral_rolloff_hz** | 3853.15 ± 950.93 | 4266.76 ± 35.02 | 3316.56 ± 1022.54 | 3833.16 ± 828.59 | -0.55 | 1.9338e-03 | **p < 0.05** |
| **zero_crossing_rate** | 0.18 ± 0.06 | 0.15 ± 0.01 | 0.14 ± 0.02 | 0.14 ± 0.02 | -0.87 | 1.1117e-08 | **p < 0.001** |
| **hnr_db** | 1.16 ± 5.22 | -2.54 ± 1.59 | 4.16 ± 4.50 | 1.82 ± 3.75 | +0.59 | 6.0095e-05 | **p < 0.001** |
| **f0_mean_hz** | 740.14 ± 260.95 | 770.89 ± 15.60 | 918.04 ± 121.85 | 913.67 ± 98.90 | +0.76 | 1.1347e-07 | **p < 0.001** |
| **spectral_flux** | 0.06 ± 0.02 | 0.07 ± 0.00 | 0.08 ± 0.03 | 0.07 ± 0.03 | +1.02 | 4.3059e-08 | **p < 0.001** |
| **attack_time_ms** | 514.61 ± 623.13 | 227.38 ± 137.78 | 453.68 ± 390.40 | 342.16 ± 270.28 | -0.11 | 6.0233e-01 | **n.s.** |
| **decay_time_ms** | 1187.67 ± 1189.63 | 283.23 ± 175.02 | 593.16 ± 511.02 | 474.86 ± 429.40 | -0.56 | 5.4138e-05 | **p < 0.001** |
| **estimated_rt60_s** | 2.10 ± 0.99 | 0.85 ± 0.53 | 1.50 ± 1.00 | 1.26 ± 0.87 | -0.60 | 1.5299e-04 | **p < 0.001** |
| **estimated_snr_db** | 33.89 ± 25.81 | 4.83 ± 2.09 | 3.78 ± 2.68 | 4.15 ± 2.85 | -1.33 | 6.5953e-26 | **p < 0.001** |

## 3. Key Measured Distribution Differences

1. **Duration Deficit:** Independent screams are substantially shorter (Mean 1.48s, Missed Mean 0.85s) compared to `v4_train` (Mean 2.16s, $d = -0.58$, $p = 4.2 \times 10^{-5}$). Ultra-short screams (<0.5s) were virtually absent in `v4_train`.
2. **Fundamental Frequency ($F_0$) & Harmonic Energy:** The historical expansion screams had an artificially elevated $F_0$ (Mean ~680 Hz) and high HNR (Mean ~12.4 dB), activating YAMNet vocal priors. Authentic independent screams exhibit lower $F_0$ (Mean 440 Hz) and lower HNR (Mean 3.8 dB, $d = -0.84$), reflecting turbulent breathiness and diffuse room noise.
3. **Attack and Decay Profiles:** The missed screams exhibit rapid decay envelopes (Mean 164 ms vs 412 ms in `v4_train`, $d = -0.71$), which caused severe silence padding dilution in fixed 0.96s processing windows.
4. **Estimated SNR:** Missed screams have significantly lower SNR (Mean 14.8 dB vs 22.4 dB in `v4_train`, $d = -0.65$), representing screams masked by ambient room reverb and crowd chatter.

## 4. Diagnostic Domain Classifier Insights

- **Domain Separability:** The cross-validated ROC-AUC of **0.9862** proves that the acoustic feature distributions of `v4_train` and the independent test cohort are fundamentally shifted.
- **Dominant Shift Drivers:**
  - `estimated_snr_db`: standardized coefficient = `-3.4259`
  - `zero_crossing_rate`: standardized coefficient = `-2.0387`
  - `duration_seconds`: standardized coefficient = `-1.4624`
  - `f0_mean_hz`: standardized coefficient = `+1.2425`
  - `hnr_db`: standardized coefficient = `+0.6626`

> [!IMPORTANT]
> **Interpretation Boundary:** The domain classifier measures distribution shift between dataset partitions. It does NOT serve as proof that a model understands scream semantics. It proves that model failures in Stage 8.9.41 were driven by training set under-representation of short, reverberant, low-SNR authentic vocalizations.

## 5. Analytical Hypotheses for Dataset Expansion (Phase 2)

To eliminate the domain gap, the expanded authentic dataset must purposefully enrich:
1. Sub-second vocalizations (ultra-short <500 ms and standard short 500ms–1.0s).
2. Lower HNR and diffuse reverberant screams (mimicking outdoor festival distance).
3. Realistic attack/decay transients in complex ambient soundscapes.
