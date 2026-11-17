# Long-Context Cadence & Syllabic Modulation Analysis (Stage 8.9.24)

## Executive Summary

Stage 8.9.24 investigated whether speech-like shouting can be distinguished from continuous human screams by analyzing **temporal modulation spectra and syllabic cadence** over an extended temporal context (1.5 to 2.5 seconds).

This report documents the mechanics, modulation spectrum findings, and empirical suppression results of **Pathway B (Long-Context Cadence Pathway)**.

---

## 1. The Biomechanics of Speech Cadence vs Continuous Exhalation

Speech production fundamentally relies on alternating vocal tract constriction and release:
- Consonants require complete glottal, velar, or alveolar closure (plosives: /p/, /t/, /k/) or narrow constriction (fricatives: /s/, /f/).
- Vowels require an open resonant tract.
- As a consequence of natural human speech articulation rates, energy envelopes in spoken or shouted language exhibit **rhythmic amplitude modulation concentrated between 2 Hz and 8 Hz** (3 to 6 syllables per second), interspersed with brief vocal closure gaps (30 to 150 ms).

In contrast, human panic screams are **ballistic, non-linguistic aerodynamic releases**:
- The vocal tract is held in a wide-open horn configuration.
- The energy envelope rises rapidly to an intense plateau and remains uninterrupted until pulmonary pressure drops.
- There are no articulatory closures, yielding a modulation spectrum concentrated almost exclusively below 1 Hz with near-zero energy in the 4 to 8 Hz syllabic band.

---

## 2. Modulation Spectrum & Cadence Metric Findings

Comparing 78 screams and 84 shouts across the held-out test split:

| Metric | Human Screams (Median / IQR) | Shouted Speech (Median / IQR) | Effect Size (Cliff's $\delta$) | Mann-Whitney $p$-value |
|---|:---:|:---:|:---:|:---:|
| **Burst Continuity Ratio (BCR)** | **0.999** (0.153) | **0.315** (0.421) | **+0.7268** | $7.24 \times 10^{-16}$ |
| **Mean Burst Duration (ms)** | **640.6** (789.1) | **128.2** (256.8) | **+0.7241** | $1.87 \times 10^{-15}$ |
| **Vocal Closure Gap Count** | **2.0** (1.8) | **9.5** (8.2) | **-0.6795** | $5.38 \times 10^{-14}$ |
| **Energy Modulation Depth** | **2.36** (1.75) | **6.44** (6.77) | **-0.5894** | $9.73 \times 10^{-11}$ |
| **Syllabic Modulation Ratio (2-8 Hz)** | **0.216** (0.180) | **0.414** (0.319) | **-0.4536** | $6.38 \times 10^{-7}$ |

---

## 3. Shouting False Alarm Suppression Results

In Stage 8.9.23, the baseline classifier suffered 17 shouting false alarms (20.24% FPR). Pathway B was evaluated to determine how many of these 17 shouting triggers could be suppressed without compromising scream recall.

### 3.1 Multi-Syllabic Shouting (Suppressed)
Pathway B successfully identified and suppressed **4 multi-syllabic shouting false alarms**:
- `v2_fsd50k_341509` (17.6s, continuous shouting with 56 closure gaps, $\text{BCR} = 0.133$, $\text{SMR} = 0.553$): **SUPPRESSED**.
- `v2_fsd50k_321971` (2.85s, angry yelling with 10 closure gaps, $\text{BCR} = 0.278$, $\text{SMR} = 0.658$): **SUPPRESSED**.
- `v2_fsd50k_235191` (6.33s, repeated shouted phrase with 15 closure gaps, $\text{BCR} = 0.377$, $\text{SMR} = 0.450$): **SUPPRESSED**.
- `fsd50k_235191` (6.33s duplicate instance, 15 closure gaps, $\text{BCR} = 0.376$, $\text{SMR} = 0.448$): **SUPPRESSED**.

This reduced the Shouting False Positive Rate from **20.24% to 15.48%** (13 remaining FPs), moving performance within 0.48% of the project's strict 15.0% engineering gate.

### 3.2 The Monosyllabic Limit (Unsuppressed)
The remaining 13 shouting false positives could **not** be suppressed by temporal cadence analysis. Forensic inspection revealed the physical reason:
- Examples such as `v2_fsd50k_220823` (0.70s), `v2_fsd50k_432875` (0.56s), and `v2_fsd50k_220822` (0.75s) are **isolated monosyllabic yells** ("NO!", "HEY!").
- Because the vocalist sustains a single open vowel for 600–750 ms, there are **no consonant closure gaps** ($\text{Gap Count} \le 2$) and **no repeated syllabic modulation** ($\text{BCR} = 1.000$).
- **Scientific Conclusion**: A monosyllabic shouted vowel is temporally and envelope-wise identical to a scream of the same duration. Distinguishing monosyllabic shouting from screams requires phonetic/formant linguistics or semantic speech recognition, not temporal envelope dynamics.
