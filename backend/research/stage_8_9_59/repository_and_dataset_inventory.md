# Repository and Dataset Inventory Audit — Stage 8.9.59

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. Not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. No production promotion is authorized.

---

## 1. Executive Summary

In Phase A of Stage 8.9.59, a comprehensive inventory of all datasets, manifests, audio assets, partitions, and license metadata was conducted across the repository. A total of **7,407 recording manifest entries** spanning 6 major project dataset collections were audited.

Every dataset was forensically analyzed for:
- Verified recording and source group counts.
- Positive/negative class balances and mixed-label source groups.
- Audio duration distribution (min, mean, max, percentiles).
- Declared licenses and commercial deployment eligibility.
- Missing audio files and metadata gaps.

---

## 2. Dataset Collection Inventory Matrix

| Dataset Collection Name | Relative Manifest Path | Total Recordings | Positive Class | Hard Negatives | Unique Source Groups | Positive SGs | Negative SGs | Mixed SGs | Mean Duration |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Core Split Manifest (v1)** | `backend/dataset/manifests/split_manifest.csv` | 1,621 | 127 | 1,494 | 726 | 59 | 644 | 23 | 11.59s |
| **Stage 8.9.17 Reconstructed** | `backend/experiments/stage8_9_17_automated_dataset_reconstruction/.../reconstructed_dataset_manifest.csv` | 2,804 | 550 | 2,254 | 955 | 156 | 748 | 51 | 7.66s |
| **Stage 8.9.47 Independent Cohort** | `backend/research/stage_8_9_47/INDEPENDENT_COHORT_MANIFEST.csv` | 480 | 160 | 320 | 220 | 105 | 115 | 0 | 1.60s |
| **Stage 8.9.49 Whistle Dev** | `backend/research/stage_8_9_49/WHISTLE_DEVELOPMENT_MANIFEST.csv` | 320 | 128 | 192 | 160 | 64 | 96 | 0 | 1.20s |
| **Stage 8.9.54 Expansion Corpus** | `backend/research/stage_8_9_54/dataset/partition_manifest_verified.csv` | 1,732 | 604 | 1,128 | 693 | 210 | 471 | 12 | 5.97s |
| **Stage 8.9.55 Acquisition Cohort** | `backend/research/stage_8_9_55/dataset/acquisition_manifest.csv` | 450 | 0 | 450 | 246 | 0 | 246 | 0 | 8.41s |

---

## 3. Detailed Partition Breakdown of Stage 8.9.54 Expansion Corpus ($N=1,732$)

The primary research expansion corpus (`partition_manifest_verified.csv`) is partitioned into three strictly isolated subsets:

### 3.1 `expansion_train` ($N=1,055$)
- **Positive Recordings:** 403 (Screams)
- **Negative Recordings:** 652 (Hard Negatives)
- **Unique Source Groups:** 415 (Positive: 128, Negative: 280, Mixed: 7)
- **Duration Profile:** Min 0.13s, Mean 6.32s, Max 550.79s
- **Purpose:** Used for training retrained Candidate E variants (E0–E3) in Stage 8.9.54.

### 3.2 `expansion_val` ($N=311$)
- **Positive Recordings:** 99 (Authentic Screams)
- **Negative Recordings:** 212 (Hard Negatives)
- **Unique Source Groups:** 138 (Positive: 41, Negative: 94, Mixed: 3)
- **Duration Profile:** Min 0.25s, Mean 4.88s, Max 182.40s
- **Acoustic Subgroup Breakdown:**
  - Positive Screams ($N=99$): 15 Ultra-Short (<0.5s), 24 Standard-Short (0.5–1.0s), 60 Sustained ($\ge 1.0$s), 19 Crowd-Masked/Distant.
  - Hard Negatives ($N=212$): 88 Shouted Speech, 37 Cheering/Crowd Chants, 36 General Environmental, 22 Whistles/Squeaks, 20 Infant Crying, 9 Emergency Sirens/SFX.
- **Purpose:** Frozen development validation set used for model selection, threshold calibration, and DSP optimization benchmarking.

### 3.3 `expansion_reserved_test` ($N=366$)
- **Positive Recordings:** 102 (Screams)
- **Negative Recordings:** 264 (Hard Negatives)
- **Unique Source Groups:** 140 (Positive: 41, Negative: 97, Mixed: 2)
- **Duration Profile:** Min 0.31s, Mean 5.86s, Max 196.02s
- **Status:** Quarantined reserved test cohort. Preserved without tuning or retraining in Stage 8.9.59.

---

## 4. Source Group & Excerpt Audit

- **Total Unique Source Groups in Corpus:** 693.
- **Multi-crop Parent Recordings:** 132 parent recordings have multiple excerpt clips ($N=311$ total clips derived from parent recordings).
- **Cross-Partition Excerpt Leakage:** Exactly **0** multi-crop recordings cross partition boundaries. All crops belonging to a parent recording are strictly isolated within the same partition.
- **Cross-Partition Source Group Leakage:** **0** source groups overlap between `expansion_train`, `expansion_val`, and `expansion_reserved_test`.
- **Cross-Partition Hash Leakage:** **0** exact file hashes or PCM hashes overlap between partitions.

---

## 5. License & Commercial Eligibility Summary

- **CC0 / Public Domain:** 858 recordings (49.54%) — Unrestricted commercial use without attribution requirement.
- **CC BY (Attribution):** 874 recordings (50.46%) — Commercially eligible with appropriate creator attribution.
- **Quarantined Non-Commercial / All Rights Reserved:** **0 recordings** in Stage 8.9.54 expansion corpus.

