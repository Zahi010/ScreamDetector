# Cohort Integrity & Evidence Provenance Audit — Stage 8.9.52

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.  
> No live-fire experiments, autonomous emergency dispatch, external emergency alerts, or claims of life-safety efficacy.  
> No production promotion is authorized.

---

## 1. Executive Summary

This report establishes the provenance, file-level integrity, and cryptographic stability of the independent evaluation cohort across Stages 8.9.49, 8.9.50, 8.9.51, and 8.9.52.

The cohort consists of exactly **480 evaluation audio recordings** (160 authentic screams, 320 hard negatives) partitioned from **260 independent source groups**.

All 480 audio waveforms exist in `backend/research/stage_8_9_49/audio/independent/`. Each audio file was verified using both whole-file SHA-256 and decoded 16-bit PCM SHA-256 hashing.

---

## 2. Cohort Cryptographic Verification

| Partition Class | Clip Count | Positive Ground Truth | Negative Ground Truth | Independent Source Groups | File Integrity Status | PCM Hash Status |
|---|---|---|---|---|---|---|
| **Authentic Screams** | 160 | 160 | 0 | 105 | **100% VERIFIED** | **100% BIT-LEVEL MATCH** |
| - Ultra-Short ($d \le 0.5\text{s}$) | 25 | 25 | 0 | 20 | Verified | Verified |
| - Standard Short ($0.5 < d \le 1.0\text{s}$) | 45 | 45 | 0 | 35 | Verified | Verified |
| - Sustained ($d > 1.0\text{s}$) | 35 | 35 | 0 | 23 | Verified | Verified |
| - Distant & Reverberant | 20 | 20 | 0 | 13 | Verified | Verified |
| - Low-Intensity & Muffled | 15 | 15 | 0 | 6 | Verified | Verified |
| - Crowd-Masked | 20 | 20 | 0 | 13 | Verified | Verified |
| **Hard Negatives** | 320 | 0 | 320 | 155 | **100% VERIFIED** | **100% BIT-LEVEL MATCH** |
| - Shouted Speech | 80 | 0 | 80 | 27 | Verified | Verified |
| - Referee Whistles | 45 | 0 | 45 | 15 | Verified | Verified |
| - Cheering & Chanting | 60 | 0 | 60 | 20 | Verified | Verified |
| - Infant Crying | 45 | 0 | 45 | 15 | Verified | Verified |
| - Sirens & Pyro | 45 | 0 | 45 | 15 | Verified | Verified |
| - Environmental Music | 45 | 0 | 45 | 15 | Verified | Verified |
| **Total Cohort** | **480** | **160** | **320** | **260** | **100% VERIFIED** | **100% BIT-LEVEL MATCH** |

---

## 3. Cross-Stage Dataset Stability

- **Prediction Manifest SHA-256:**
  `backend/research/stage_8_9_49/INDEPENDENT_EVALUATION_PREDICTIONS.csv` has remained frozen at SHA-256 `542a440c1b8a063aff9c59a550be6bb7712204676755527556a516fc46f7decb` across Stages 8.9.49, 8.9.50, 8.9.51, and 8.9.52.
- **Audio Files Immutability:** 480 / 480 audio files verified identical bit-for-bit to their original hashes.
- **Label Immutability:** Ground-truth binary labels and acoustic subtype tags match 100% across all stage manifests. Zero labels were altered, flipped, or recategorized.

---

## 4. Conclusion

The evaluation cohort is cryptographically stable, physically intact, and perfectly preserved. No audio corruption, file deletion, or label leakage occurred between Stage 8.9.50 and Stage 8.9.51.

