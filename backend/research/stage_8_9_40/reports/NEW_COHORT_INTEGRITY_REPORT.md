# Stage 8.9.40: New Independent Cohort Integrity & Acoustic Validation Report

**MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**

*This project is an experimental acoustic research system. It is not certified for life-safety alerting, emergency response, active shooter detection, autonomous police dispatch, or critical physical security deployments.*

---

## 1. Executive Summary

This report documents the structural, acoustic, and cryptographic validation of the Stage 8.9.40 New Independent Hard-Negative Evaluation Cohort. This cohort was established to test out-of-sample false-alarm rejection under rigorous acoustic conditions without retraining or modifying candidate model parameters.

All 145 recordings have been validated against strict signal processing standards, license eligibility criteria, and isolation protocols.

---

## 2. Cohort Specification & Manifest Provenance

- **Manifest Path:** `backend/research/stage_8_9_40/manifests/new_cohort_manifest.csv`
- **Audio Storage Directory:** `backend/research/stage_8_9_40/audio/hard_negatives/`
- **Total Recordings ($N$):** 145
- **Unique Source Groups ($N_{sg}$):** 79
- **Mean Duration:** 2.12 seconds (Range: 0.80 s – 4.50 s, Total Duration: 307.4 seconds)
- **Audio Format:** 16,000 Hz, 1-channel mono, 16-bit linear PCM WAV (`RIFF (little-endian) data, WAVE audio, Microsoft PCM, 16 bit, mono 16000 Hz`)

### Category Composition:
1. **Shouting & Speech:** 54 recordings (28 source groups, 37.2%)
2. **Crowd Chanting & Festival Cheering:** 30 recordings (16 source groups, 20.7%)
3. **Whistles, Screeches & PAs:** 21 recordings (12 source groups, 14.5%)
4. **Infant Crying & Babble:** 15 recordings (9 source groups, 10.3%)
5. **Sirens, Fireworks & Transients:** 15 recordings (8 source groups, 10.3%)
6. **General Environmental / Ambient Noise:** 10 recordings (6 source groups, 6.9%)

---

## 3. Cryptographic and Acoustic Integrity Verification

A verification script (`verify_new_cohort_isolation.py`) audited every entry in the manifest:

| Verification Check | Standard / Protocol | Audit Result | Status |
|---|---|:---:|:---:|
| **Physical File Presence** | All 145 files resolve on filesystem | 145 / 145 present | **PASS** |
| **Audio Header Decodability** | Verified via `soundfile` & `scipy.io.wavfile` | 145 / 145 valid | **PASS** |
| **Sample Rate Enforcement** | Exactly 16,000 Hz | 145 / 145 match | **PASS** |
| **Channel Count** | Exactly 1 (Mono) | 145 / 145 mono | **PASS** |
| **SHA-256 Waveform Hashes** | Recorded in manifest; tested for collisions | 0 collisions | **PASS** |
| **int16 PCM Frame Hashes** | Normalized linear frame byte verification | 0 collisions | **PASS** |
| **Missing / NaN Samples** | Checked for NaN, Inf, or empty audio buffers | 0 anomalies | **PASS** |

---

## 4. Complete Isolation From Historical & Expansion Partitions

Cross-referencing the 145 file IDs and 79 source-group IDs against all historical partitions confirmed:
- Shared with `v4_train`: **0**
- Shared with `v4_val`: **0**
- Shared with `v4_historical_test`: **0**
- Shared with `v4_reserved_expansion_test`: **0**
- Shared with `quarantine`: **0**

The cohort represents an uncompromised, unpolluted, and fully independent benchmark for assessing operational false positive rates.

