# Checkpoint Verification — Stage 8.9.53

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Model Checkpoint Cryptographic Audits

### Candidate E (Research Dual-Branch Classifier)
- **Path:** `backend/research/stage_8_9_51/models/research_exp_candidate.pt`
- **SHA-256:** `5ec5941448af4d3c77417a96e0ee5da5d8592ef5bc3c1103d3518378b37d13c1`
- **Integrity Status:** **VERIFIED (100% BIT-FOR-BIT MATCH)**
- **Operating Threshold:** `theta = 0.4000` (frozen from Stage 8.9.51 / Stage 8.9.52 validation)
- **Architecture:**
  - Semantic Projection: `1024 -> 128` (Linear + ReLU + Dropout 0.20)
  - Subband/Acoustic Projection: `(6*2 + 11) = 23 -> 64` (Linear + ReLU + Dropout 0.15)
  - Sigmoid Dynamic Gate: `(128 + 64) = 192 -> 32` (Linear + Sigmoid)
  - Classification Head: `192 -> 64 -> 1` (Linear + ReLU + Linear)
- **Normalization:** Raw concatenated feature projections; no test-set fitting, no external scaler.

### Candidate B (Mask-v6 Dual-Branch Baseline)
- **Path:** `backend/research/stage_8_9_44/models/config_b_mask.pt`
- **SHA-256:** `f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378`
- **Integrity Status:** **VERIFIED (100% BIT-FOR-BIT MATCH)**
- **Operating Threshold:** `theta = 0.8000` (frozen reference baseline)

### Production Classifier (Stage 5 Reference)
- **Path:** `backend/models/scream_classifier.joblib`
- **SHA-256:** `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f`
- **Integrity Status:** **VERIFIED (100% BIT-FOR-BIT MATCH)**
- **Operating Threshold:** `theta = 0.3500`
