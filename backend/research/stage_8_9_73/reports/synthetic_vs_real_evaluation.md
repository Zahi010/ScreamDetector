# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Synthetic versus Real Acoustic Evidence & Disentanglement Analysis

**Stage Identifier:** Stage 8.9.73  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Evaluation Date:** 2026-11-14  
**Evaluated Cohort:** Stage 54 Validation Screams ($N=99$: 80 Genuine Real Screams, 19 Synthetic Masked Screams)

---

## 1. Executive Summary & Core Finding

In compliance with Stage 8.9.73 guidelines, acoustic evidence is strictly disentangled into genuine recorded audio versus synthetic audio mixtures.

### Disentangled Performance Breakdown

| Audio Domain | Sample Size ($N$) | Detected (TP) | Missed (FN) | Recall Rate | Primary Failure Mode |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Genuine Recorded Screams** | 80 | **71** | **9** | **88.75%** | Low-roughness child screams & boundary gasps |
| **Synthetic Masked Screams** | 19 | **11** | **8** | **57.89%** | Heavy crowd noise masking at -6dB to 0dB SNR |
| **Combined Aggregate** | **99** | **82** | **17** | **82.83%** | Combined development benchmark (Gate 1) |

---

## 2. Real Recorded Screams Analysis ($N=80$)

- On natural recorded human screams in the validation cohort, Candidate 71-D achieves **88.75% recall (71/80)**.
- **The 9 Missed Real Screams:**
  1. `273153__hoerspielwerkstatt-hef__child-scream2` (2 segments): Genuine child scream. Correctly identified by the raw neural model ($prob = 0.574$ and $0.572$), but suppressed by the distress veto because child screams possess lower auditory roughness ($0.0189 < 0.022$).
  2. `fsd50k_220658` and `fsd50k_219882`: Suppressed by flux veto due to stationary spectral energy ($flux < 0.036$).
  3. `ULJI_15_5_0_12_0_0_0` and `fsd50k_144338`: Rescued by latent resonance rescue ($+0.035$), but fell just short of the 0.4920 threshold ($0.4498$ and $0.4454$).
  4. `242607__reitanna__gasp-oooh`, `242644__reitanna__another-surprised-oooh`, `336537__chrillz3r__scream-frightened`: Moderate-intensity vocalizations with neural underconfidence ($0.38$–$0.41$).

---

## 3. Synthetic Masked Screams Analysis ($N=19$)

- All 19 synthetic scream samples represent clean human screams synthetically combined with crowd noise at calibrated SNRs ($-6$ dB, $-3$ dB, $0$ dB, $+3$ dB, $+6$ dB).
- Candidate 71-D detected 11 of 19 (57.89%).
- **The 8 Missed Synthetic Screams:**
  - `v2_synth_008` ($-6$ dB SNR): raw prob $0.336$
  - `v2_synth_015` ($0$ dB SNR): raw prob $0.388$
  - `v2_synth_019` ($0$ dB SNR): raw prob $0.337$
  - `v2_synth_068` ($-6$ dB SNR): raw prob $0.409$
  - `v3_synth_007` ($-3$ dB SNR): raw prob $0.440$
  - `v3_synth_011` ($-6$ dB SNR): raw prob $0.380$
  - `v3_synth_034` ($+3$ dB SNR): raw prob $0.421$
  - `v3_synth_046` ($-6$ dB SNR): raw prob $0.467$
- **Acoustic Reality:** None of the synthetic misses were caused by veto suppressions (active veto: `none`). Background noise elevates the noise floor, attenuating the spectral contrast of high-frequency vocal formants and lowering raw neural activation.

---

## 4. Scientific Policy on Synthetic Evidence

1. **Controlled Benchmarking Only:** Synthetic mixtures provide valuable controlled stress-testing for SNR degradation curves, but **cannot be used as a proxy for real-world out-of-distribution generalization**.
2. **Strict Metric Separation:** Future validation reports must report genuine recorded recall and synthetic masked recall as independent columns to avoid obfuscating true vocalization performance.
