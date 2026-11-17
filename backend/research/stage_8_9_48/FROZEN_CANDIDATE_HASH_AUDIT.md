# Frozen Research Candidate Hash Audit — Stage 8.9.48

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.

---

## 1. Executive Summary

This audit verifies the cryptographic immutability and provenance of all neural network checkpoints evaluated in Stage 8.9.47 and analyzed in Stage 8.9.48.

| Candidate Configuration | Checkpoint Path | Frozen Threshold | Checkpoint SHA-256 | Training Regime Provenance | Verification Status |
| :--- | :--- | :---: | :--- | :--- | :---: |
| **Candidate B (Config-B-Mask-v6)** | `backend/research/stage_8_9_44/models/config_b_mask.pt` | 0.8000 | `f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378` | Stage 8.9.44 continuous masking (+3 to +12 dB SNR) | **VERIFIED_PRESENT** |
| **Candidate R5 (Ratio-0P-100A)** | `backend/research/stage_8_9_46/models/config_b_ratio_0p_100a.pt` | 0.8700 | `1ab0cc43d043b7c4063240c26f80f053fc2e6eabcc0287a1ed3ebd5afd244223` | Stage 8.9.46 0P-100A mild masking (+9 to +18 dB) & distance attenuation | **VERIFIED_PRESENT** |
| **Candidate R3 (Ratio-50P-50A)** | `backend/research/stage_8_9_46/models/config_b_ratio_50p_50a.pt` | 0.8400 | `a8727b0d09d8340f56905a0bce34f481f3ccfcea988cdf24f59644977f13661a` | Stage 8.9.46 50P-50A balanced ratio | **VERIFIED_PRESENT** |
| **Candidate R1 (Ratio-100P-0A)** | `backend/research/stage_8_9_46/models/config_b_ratio_100p_0a.pt` | 0.8700 | `3804d2cdd930f32bbfd5e273302221fa18f22e6dcc1bdf059a5653681be56584` | Stage 8.9.46 100P-0A pristine reference | **VERIFIED_PRESENT** |

---

## 2. Integrity Certification
- All model weights are cryptographically frozen and reside in their designated historical stage directories.
- No fine-tuning, retraining, or threshold calibration was performed on the independent evaluation cohort.
