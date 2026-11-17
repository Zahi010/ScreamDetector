# Research Checkpoint Hash Audit — Stage 8.9.49

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.

---

## Checkpoint Provenance & Integrity Summary

| Candidate ID | Architecture | Checkpoint File | Checkpoint SHA-256 | Frozen Threshold | Status |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **Candidate B (Config-B-Mask-v6)** | `DualEncoderAcousticModel` | `backend/research/stage_8_9_44/models/config_b_mask.pt` | `f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378` | `0.8000` | **FROZEN_VERIFIED** |

---

## Checkpoint Lineage & Operating Protocol
- **Originating Stage:** Stage 8.9.44 (Continuous Background Masking Augmentation).
- **Training SNR Range:** +3 dB to +12 dB SNR background masking.
- **Model Architecture:** DualEncoderAcousticModel combining YAMNet embeddings (1024-d) and temporal acoustic features (18-d) via multi-head attention and gated fusion.
- **Operating Threshold:** Strictly locked at `0.8000` calibrated on v5 validation split; zero post-hoc tuning on evaluation cohorts.
- **Whistle Interventions Status:** External modular filters only; no modification to Candidate B neural network parameters.
