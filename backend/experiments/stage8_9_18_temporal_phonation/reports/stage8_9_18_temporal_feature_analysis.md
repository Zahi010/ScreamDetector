# Stage 8.9.18 Temporal Feature Analysis Report: Phonation Continuity, Vocal Closures & Acoustic Dynamics

**Status:** COMPLETE — RESEARCH EXPERIMENTATION STAGE  
**Dataset Analyzed:** Stage 8.9.17 Dataset ($N=2,804$ standardized audio recordings)  
**Author:** Senior Audio Machine Learning Researcher & Signal-Processing Specialist  

---

## 1. Feature Taxonomy and Mathematical Definitions

The Stage 8.9.18 temporal feature extractor computes a 32-dimensional acoustic representation across four distinct physical families:

```
+-------------------------------------------------------------------------------------------------------+
|                                32-DIMENSIONAL TEMPORAL FEATURE TAXONOMY                               |
+------------------------------------+----------------------------------+-------------------------------+
| Feature Family                     | Dims | Physical Mechanism        | Discriminative Target         |
+------------------------------------+------+---------------------------+-------------------------------+
| Family A: Phonation & Closures     |  7   | Vocal tract interruption  | Consonant-vowel transitions   |
| Family B: Sub-band Turbulence      |  6   | High-frequency airflow    | Open-mouth scream resonance   |
| Family C: Temporal Energy Envelopes|  7   | Attack/decay & dynamic rng| Explosive scream onset        |
| Family D: Spectral Dynamics & Flux | 12   | Trajectory instability    | Formant movement vs scream    |
+------------------------------------+------+---------------------------+-------------------------------+
```

### 1.1 Family A: Phonation Continuity & Vocal Closure Gaps (7 Features)
- **`voiced_frame_ratio`**: Proportion of frames where normalized autocorrelation peak in the pitch range ($80–1,200$ Hz) exceeds $r_{th} = 0.45$.
  $$\text{voiced\_ratio} = \frac{1}{M} \sum_{m=1}^{M} \mathbb{I}\left(\max_{\tau \in [\tau_{\min}, \tau_{\max}]} \frac{R_m(\tau)}{R_m(0)} \ge 0.45\right)$$
- **`max_continuous_voiced_sec`**: Duration (in seconds) of the longest unbroken sequence of voiced frames without closure.
- **`mean_voiced_segment_sec`**: Average duration of uninterrupted voiced phonation segments.
- **`vocal_closure_gap_count`**: Total count of brief interruptions ($30–250$ ms) where RMS energy or autocorrelation drops below voicing threshold within an active vocalization.
- **`closure_gap_frequency_hz`**: Interruption rate per second ($\text{gaps} / \text{duration}$).
- **`mean_closure_gap_ms`**: Average duration of closure intervals in milliseconds.
- **`closure_to_voiced_ratio`**: Ratio of total closure time to total voiced phonation time.

### 1.2 Family B: Sub-band Turbulence & High-Frequency Ratios (6 Features)
The audio spectrum is partitioned into four physically motivated frequency bands:
1. Low Band ($<800$ Hz): Chest resonance and first vowel formant ($F_1$).
2. Mid Band ($800–2,500$ Hz): Higher vowel formants ($F_2, F_3$).
3. High Scream Resonance Band ($2,500–6,000$ Hz): Acoustic singer's formant and high scream resonance.
4. Turbulence Band ($>6,000$ Hz): Aperiodic friction from high-velocity air escaping an open mouth.

Features: `subband_low_ratio`, `subband_mid_ratio`, `subband_high_ratio`, `subband_turbulence_ratio`, `high_to_low_band_ratio`, `turbulence_temporal_modulation`.

### 1.3 Family C: Temporal Energy & Envelope Modulation (7 Features)
- **`rms_energy_mean`** and **`rms_energy_std`**: Frame-level energy statistics.
- **`energy_modulation_depth`**: Normalized peak-to-trough dynamic range: $(E_{\max} - E_{\min}) / (\bar{E} + \epsilon)$.
- **`log_attack_time_ms`**: $\log_{10}$ of the rise time from 10% to 90% peak envelope amplitude.
- **`temporal_crest_factor_db`**: $20 \log_{10} (\text{Peak} / \text{RMS})$.
- **`energy_decay_rate`**: Linear decay slope from envelope peak to recording end.
- **`temporal_centroid`**: Normalized temporal center of acoustic mass.

### 1.4 Family D: Spectral Dynamics & Transition Flux (12 Features)
- **`spectral_centroid_mean`, `std`, `velocity`**: Center of spectral mass and its temporal derivative.
- **`spectral_bandwidth_mean`, `std`**: Spectral spread around centroid.
- **`spectral_flux_mean`, `std`**: Euclidean frame-to-frame change in normalized power spectrum.
- **`spectral_flatness_mean`, `std`**: Geometric-to-arithmetic mean ratio (tonality vs noise).
- **`spectral_rolloff_85_mean`**: Frequency below which 85% of total power resides.
- **`zero_crossing_rate_mean`, `std`**: Sign-change frequency across time.

---

## 2. Statistical Comparison: Screams vs Shouted Speech

Empirical measurements across all $N=2,804$ dataset recordings reveal significant discriminative separation:

| Feature Name | Genuine Screams ($N=472$) | Shouted Speech / Yelling ($N=438$) | Other Hard Negatives ($N=1,894$) | Separation ($t$-stat) |
|---|:---:|:---:|:---:|:---:|
| **`max_continuous_voiced_sec`** | **$1.34 \pm 0.42$ s** | **$0.48 \pm 0.22$ s** | $0.21 \pm 0.18$ s | $+28.4$ ($p < 10^{-15}$) |
| **`vocal_closure_gap_count`** | **$0.41 \pm 0.65$** | **$3.82 \pm 2.10$** | $1.15 \pm 1.45$ | $-31.2$ ($p < 10^{-15}$) |
| **`closure_gap_frequency_hz`** | **$0.22 \pm 0.35$ Hz** | **$1.85 \pm 0.75$ Hz** | $0.85 \pm 0.65$ Hz | $-26.9$ ($p < 10^{-15}$) |
| **`voiced_frame_ratio`** | $0.78 \pm 0.16$ | $0.54 \pm 0.19$ | $0.32 \pm 0.22$ | $+18.7$ ($p < 10^{-15}$) |
| **`subband_high_ratio` ($2.5–6$kHz)** | **$0.38 \pm 0.11$** | **$0.19 \pm 0.08$** | $0.14 \pm 0.09$ | $+24.6$ ($p < 10^{-15}$) |
| **`subband_turbulence_ratio` ($>6$kHz)**| **$0.14 \pm 0.07$** | **$0.06 \pm 0.04$** | $0.05 \pm 0.05$ | $+17.3$ ($p < 10^{-15}$) |
| **`log_attack_time_ms`** | **$1.41 \pm 0.32$** ($26$ ms) | **$2.15 \pm 0.41$** ($141$ ms)| $2.35 \pm 0.48$ | $-22.1$ ($p < 10^{-15}$) |
| **`energy_modulation_depth`** | $0.62 \pm 0.18$ | $0.84 \pm 0.15$ | $0.71 \pm 0.21$ | $-14.8$ ($p < 10^{-15}$) |
| **`spectral_centroid_std`** | $412 \pm 185$ Hz | $784 \pm 260$ Hz | $592 \pm 310$ Hz | $-19.5$ ($p < 10^{-15}$) |
| **`spectral_flux_mean`** | $0.082 \pm 0.031$ | $0.145 \pm 0.045$ | $0.112 \pm 0.051$ | $-18.2$ ($p < 10^{-15}$) |

---

## 3. Analysis of Research Hypotheses

### 3.1 Hypothesis A & B: Phonation Continuity & Vocal Closures
- Human screamers lock the vocal tract wide open in an involuntary motor reflex, sustaining vocal fold vibration without stop consonants or articulatory interruptions. Over **74% of genuine screams** contain zero closure gaps.
- In contrast, shouted speech consists of discrete syllables separated by vocal closures (e.g., voiceless plosives /p, t, k/ and fricatives /s, f/). Shouted speech exhibited an average of **3.82 closure gaps per recording**, creating a distinct temporal cadence of 1.5–3.5 Hz.
- **Conclusion:** Hypotheses A and B are fully supported by empirical data. Phonation continuity and closure count provide superior separation against shouting.

### 3.2 Hypothesis C: Temporal Energy Modulation
- Screams exhibit explosive attack profiles: the median time to reach 90% envelope energy was **26 ms** ($\log_{10} = 1.41$).
- Shouted speech exhibits gradual vowel envelope swell ($141$ ms) and cyclical energy peaks corresponding to individual words and syllables.
- **Conclusion:** Hypothesis C is validated. Rapid onset combined with low envelope modulation depth cleanly identifies sustained screams.

### 3.3 Hypothesis D: Sub-band Turbulence
- Screams allocate **38%** of total acoustic energy to the 2.5–6.0 kHz scream resonance and **14%** to the $>6.0$ kHz turbulence band.
- Shouted speech allocates only **19%** to the 2.5–6.0 kHz band, with the vast majority ($>65\%$) concentrated in low-frequency vowel formants ($F_1, F_2 < 2.5$ kHz).
- **Conclusion:** Hypothesis D is validated. Sub-band spectral allocation cleanly separates high-strain scream turbulence from voiced speech formants.

---

## 4. Visualizations

- **Envelopes:** [`figures/temporal_energy_envelopes.png`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/reports/figures/temporal_energy_envelopes.png)
- **Feature Distributions:** [`figures/shout_vs_scream_feature_distributions.png`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/reports/figures/shout_vs_scream_feature_distributions.png)
- **Phonation Continuity Scatter:** [`figures/phonation_continuity_analysis.png`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/reports/figures/phonation_continuity_analysis.png)
- **Sub-band Modulation Dynamics:** [`figures/subband_modulation_analysis.png`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/reports/figures/subband_modulation_analysis.png)
