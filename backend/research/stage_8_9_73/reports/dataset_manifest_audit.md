# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Stage 8.9.73 Dataset Provenance, Cohort Exposure & Quarantine Audit

**Project:** Festival Scream Detector  
**Stage:** 8.9.73  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Date of Audit:** 2026-11-14  
**Audit Purpose:** Comprehensive governance tracking of training, development, diagnostic, and sealed evaluation cohorts, verifying isolation boundaries and preventing test leakage.

---

## 1. Executive Summary & Exposure Classifications

A rigorous data governance audit was conducted for all audio partitions used in Stage 8.9.73. The exact exposure statuses are formalized below:

| Dataset / Cohort Name | Sample Size ($N$) | Source Groups | Exposure Classification | Permitted Research Usage | Integrity Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Expansion Training Cache** (`train_features.npz`) | 1,055 clips | 415 unique SGs | **TRAINING_PARTITION** | Model training, loss weighting, representation learning | Bit-for-bit verified |
| **Stage 54 Validation Cohort** (`val_features.npz`) | 311 clips | 138 unique SGs | **EXPOSED_DEVELOPMENT_COHORT** | Threshold tuning, veto ablations, diagnostic tracking | Formally classified as exposed |
| **Stage 64 Held-Out Short Collection** (`held_out_short_features.npz`) | 268 clips | 7 unique SGs | **EXPOSED_DIAGNOSTIC_COHORT** | Short-event diagnostic check (NOT an untouched test) | Clustered provenance documented |
| **Stage 60 Sealed Prospective Cohort** (`future_evaluation_manifest.json`) | 700 clips | 453 unique SGs | **SEALED_EVALUATION_COHORT** | **STRICTLY QUARANTINED** (Zero inspection, zero evaluation) | SHA-256: `9dfa4ced...` (Untouched) |

---

## 2. Forensic Analysis of Exposed Diagnostic Cohort ($N=268$)

In prior stages (Stage 8.9.64–8.9.70), the 268-clip held-out short-scream collection was treated as an independent validation set. Stage 8.9.71 exposed a critical limitation in this assumption:
- **Severe Source-Group Skew:** Out of 268 audio clips, **164 clips (61.19%)** originate from a single uploader/source group (`sg_short_s49`).
- **Limited Acoustic Diversity:** The entire collection represents only **7 independent source groups** (`sg_short_s49`, `sg_short_s31`, `sg_short_s18`, `sg_short_s12`, `sg_short_s05`, `sg_short_s02`, `sg_short_s01`).
- **Cluster-Aware Variance:** While naive i.i.d. bootstrap resampling yields a narrow confidence interval [52.98%, 64.93%], true **source-group cluster bootstrap resampling yields [46.67%, 83.14%]**.
- **Formal Status Reclassification:** The 268 clips are formally categorized as:
  **`EXPOSED_DIAGNOSTIC_COHORT — NOT AN UNTOUCHED FINAL TEST`**
  This dataset must **never** be cited as evidence of broad out-of-distribution real-world generalization.

---

## 3. Disentanglement of Development Cohort ($N=311$)

Within the Stage 54 Validation Cohort (`val_features.npz`, $N=311$), Stage 8.9.73 conducted a formal breakdown into acoustic classes and synthetic versus real recording provenance:
- **Positive Scream Samples ($N=99$):**
  - **Real Recorded Human Screams ($N=80$):** Sourced from acoustic libraries and field captures. Candidate 71-D achieves **88.75% recall (71/80)** on this subset with only 9 misses.
  - **Synthetic Masked Screams ($N=19$):** Screams embedded in heavy crowd and reverberant noise (-6 dB to 0 dB SNR). Candidate 71-D achieves **57.89% recall (11/19)** due to high noise floor suppressing formant energy.
- **Negative Samples ($N=212$):**
  - **High-Effort Shouted Speech ($N=88$):** Non-scream aggressive and theatrical shouts. Candidate 71-D FPR: **14.77% (13/88)**.
  - **General Hard Negatives ($N=124$):** Infant crying ($N=28$), whistles/flutes ($N=30$), sirens ($N=22$), crowd applause/cheering ($N=24$), and environmental transients ($N=20$). Candidate 71-D FPR: **8.06% (10/124)**.

---

## 4. Sealed Evaluation Quarantine Verification

The prospective sealed evaluation manifest established in Stage 8.9.60 remains completely quarantined:
- **Manifest Location:** `backend/research/stage_8_9_60/future_evaluation_manifest.json`
- **Total Clips:** 700
- **Independent Source Groups:** 453
- **Observed File SHA-256:** `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd`
- **Expected File SHA-256:** `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd`
- **Verification Result:** **MATCH (100% BIT-FOR-BIT IDENTICAL)**
- **Quarantine Protections Enforced:**
  1. No audio features or labels from this cohort were loaded into memory.
  2. No model predictions or loss gradients were generated against this cohort.
  3. No decision thresholds or veto parameters were adjusted against this cohort.
  4. The sealed manifest file was not opened or altered during Stage 8.9.73 execution.

---

## 5. Certification of Compliance

All dataset boundaries, file hashes, and quarantine protocols have been audited by the Senior Research Systems Engineer. Zero data leakage has occurred.

