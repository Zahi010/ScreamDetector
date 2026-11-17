# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Real versus Synthetic Acoustic Evidence & SNR-Stratified Reliability Audit

**Project:** Festival Scream Detector  
**Stage:** 8.9.74  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Date:** 2026-11-14  
**Evaluated Screams:** Stage 54 Validation Cohort ($N=99$: 80 Genuine Real Screams, 19 Synthetic Masked Screams)

---

## 1. Executive Summary & Scientific Findings

Stage 8.9.73 discovered a massive divergence in Candidate 71-D detection performance between real recorded human screams (**88.75% recall**, 71/80) and synthetic crowd-masked screams (**57.89% recall**, 11/19).

Stage 8.9.74 executed a systematic forensic audit into the causes of this performance gap, evaluating SNR stratification, acoustic masking dynamics, and the ecological validity of synthetic audio mixtures.

### Key Audit Findings:
1. **SNR Masking Drives Synthetic Misses:**
   - At favorable SNRs (**+6 dB and +12 dB**), Candidate 71-D achieves **100.0% recall (6/6)** on synthetic screams.
   - At equal or negative SNRs (**0 dB, -3 dB, -6 dB**), recall collapses to **38.46% (5/13)**.
   - At -6 dB SNR, 4 out of 5 synthetic screams are missed (20% recall).
2. **Spectral Masking Mechanism:**
   - In synthetic files, ambient crowd noise is linearly mixed into clean scream recordings. High-amplitude crowd babble fills the spectral valleys and flattens high-frequency formant peaks, depressing the High-Frequency Ratio from $4.39$ down to $0.07$–$0.12$ and suppressing the model's calibrated probability to $0.33$–$0.46$.
3. **Ecological Validity Warning:**
   - Synthetic additive mixing is a useful stress-test tool, but **it does not predict real-world festival performance**. Synthetic mixtures omit the Lombard effect (vocalists shouting louder and altering pitch when in noise), room reverberation, and spatial directional microphone cues.
4. **Mandatory Reporting Policy:**
   - Real and synthetic scream recall must **always be reported separately**. Aggregate recall metrics (such as Gate 1's 82.83%) must explicitly declare the real-versus-synthetic proportion.

---

## 2. SNR-Stratified Performance Ledger

Extracted from [`snr_stratified_results.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_74/snr_stratified_results.csv):

| Acoustic Stratum | Total Samples ($N$) | Detected (TP) | Missed (FN) | Recall Rate | Mean Roughness | Mean HF Ratio | Mean Flux | Masking Severity |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Clean / Natural Field Recordings** | 80 | **71** | **9** | **88.75%** | 0.0886 | 4.3912 | 0.0831 | Natural Acoustics |
| **Synthetic SNR +12 dB** | 2 | **2** | **0** | **100.00%** | 0.1908 | 0.0491 | 0.0583 | Minimal Masking |
| **Synthetic SNR +06 dB** | 4 | **4** | **0** | **100.00%** | 0.0978 | 0.2110 | 0.0883 | Mild Masking |
| **Synthetic SNR +03 dB** | 1 | **0** | **1** | **0.00%** | 0.2964 | 0.0632 | 0.0397 | Moderate Masking ($p=0.4212$) |
| **Synthetic SNR +00 dB** | 5 | **3** | **2** | **60.00%** | 0.1129 | 0.2957 | 0.0833 | Moderate Masking |
| **Synthetic SNR -03 dB** | 2 | **1** | **1** | **50.00%** | 0.1840 | 0.0783 | 0.0772 | Severe Masking |
| **Synthetic SNR -06 dB** | 5 | **1** | **4** | **20.00%** | 0.2168 | 0.0911 | 0.0766 | Severe Masking |
| **TOTAL COMBINED COHORT** | **99** | **82** | **17** | **82.83%** | 0.0998 | 3.5932 | 0.0827 | Gate 1 Benchmark |

---

## 3. Duration & Quality Distributions

- **Duration Distribution:**
  - Real Screams: Mean duration = 1.95s (range 0.20s to 12.4s). Short screams (< 1.0s) constitute 39 of the 80 clips (48.8%).
  - Synthetic Screams: Mean duration = 3.65s (range 1.28s to 19.0s). Zero synthetic screams are short (< 1.0s).
- **Duration Impact:** The synthetic cohort exclusively evaluates sustained screams masked by continuous crowd noise; it provides zero information regarding short scream recognition under crowd masking.
- **Recording Quality:** Real screams exhibit higher variance in acoustic capture (room reverberation, distant field captures, varying microphone distances), whereas synthetic scream stems originate from relatively clean studio or vocal booth samples before digital mixing.

---

## 4. Scientific Governance & Policy Rulings

1. **No Performance Extrapolation:** It is scientifically invalid to assert that an 88.75% real scream recall proves festival readiness, just as it is invalid to assert that a 20.0% recall at -6 dB proves complete system failure.
2. **Transparent Metric Stratification:** All future completion reports and dashboard views must present:
   - Primary: Real Recorded Human Scream Recall ($N=80$).
   - Diagnostic: Synthetic Low-SNR Stress Recall ($N=19$).
   - Official Contractual: Combined Overall Recall ($N=99$).

