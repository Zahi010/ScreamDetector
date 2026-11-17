# Stage 8.9.38 — Research Split Report (v4)

**Project:** Festival Scream Detector  
**Stage:** 8.9.38 — Dataset Integration, Independent Cohort Construction & Controlled Retraining Preparation  
**Author:** Principal Acoustic AI Research Scientist & ML Validation Auditor  
**Date:** November 2026  
**Status:** Completed  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE

---

## 1. Unified Research Split Overview

Stage 8.9.38 constructed a comprehensive, source-group-isolated research split documented in [`research_split_v4.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_38/manifests/research_split_v4.csv).

The split design preserves historical continuity by leaving the original test set untouched while creating an independent, reserved expansion test cohort specifically designed to evaluate short screams and multi-talker crowd vocalizations.

### 1.1 Partition Summary

| Partition Identifier | Total Active Clips | Screams | Hard Negatives | Unique Source Groups | Mean Duration (s) | Total Audio (min) |
|---|---|---|---|---|---|---|
| **`v4_train`** | 820 | 180 | 640 | 324 | $3.25\text{ s}$ | $44.4\text{ min}$ |
| **`v4_val`** | 339 | 83 | 256 | 114 | $3.08\text{ s}$ | $17.4\text{ min}$ |
| **`v4_historical_test`** | 293 | 102 | 191 | 111 | $3.12\text{ s}$ | $15.2\text{ min}$ |
| **`v4_reserved_expansion_test`** | 102 | 65 | 37 | 49 | $1.28\text{ s}$ | $2.2\text{ min}$ |
| **`quarantined`** | 24 | 8 | 16 | 21 | $1.41\text{ s}$ | $0.6\text{ min}$ |
| **TOTAL** | **1,578** | **438** | **1,140** | **599** | **$3.03\text{ s}$** | **$79.8\text{ min}$** |

---

## 2. Category Distribution Per Partition

The table below breaks down active acoustic categories across all four research splits (excluding quarantined):

| Category | `v4_train` | `v4_val` | `v4_historical_test` | `v4_reserved_expansion_test` | Total Active |
|---|---|---|---|---|---|
| **`scream` (General)** | 144 | 53 | 66 | 0 | **263** |
| **`masked_distant_screams`** | 26 | 28 | 36 | 0 | **90** |
| **`short_screams` (New Expansion)** | 10 | 2 | 0 | **65** | **77** |
| **`shouting_and_speech`** | 197 | 88 | 48 | 18 | **351** |
| **`crowd_chant_cheering`** | 160 | 58 | 42 | 24 | **284** |
| **`whistles_and_squeaks`** | 88 | 33 | 32 | 3 | **156** |
| **`infant_crying`** | 48 | 23 | 15 | 2 | **88** |
| **`sfx_sirens_fireworks`** | 60 | 16 | 28 | 2 | **106** |
| **`general_environmental`** | 87 | 38 | 26 | 3 | **154** |
| **TOTAL ACTIVE CLIPS** | **820** | **339** | **293** | **102** | **1,554** |

---

## 3. Short-Scream Cohort Statistical Power

- In the historical test cohort (`v4_historical_test`), short screams ($< 1.0\text{ s}$) numbered only $N=5$, yielding a 95% Wilson confidence interval width $>40\%$.
- In the newly constructed `v4_reserved_expansion_test`, **65 independent short-scream recordings across 35 reserved source groups** are held out exclusively for testing.
- If a future retrained model achieves **$60/65$ ($92.31\%$) short-scream recall**, the resulting 95% Wilson CI will be **$[83.2\%, 96.7\%]$** (interval width narrowed from $43.4\%$ down to $13.5\%$).

---

## 4. Manifest Integrity Checksums

All manifests under [`manifests/`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_38/manifests/) were cryptographically hashed and logged in [`manifest_checksums.json`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_38/manifests/manifest_checksums.json):
- `dataset_manifest_v4.csv`: `27fb26137ea27f8d418bbf558f696be80ebefc5887854351a18e14490b78a469`
- `research_split_v4.csv`: `03bca0427301c40be157ba3b0df331d9b6fc52e6973ba524ee59bbce54e85934`
- `source_group_split_manifest.csv`: `4346bbdbbe5062b2fcba5ddab7e2017326ea0813f56bf35d7990ff52da241151`
- `label_manifest.csv`: `d3c114ce996df873919b359f13b63a0a38f45a05b2a0fb09e072a4c1ddf2cfa9`
- `license_manifest.csv`: `cfeb368798bf9b10373feeb6fb8a2214ae8cfd52a22da7847c94eb477651034c`
- `duplicate_manifest.csv`: `885149f1db754718c998319f37fe252062776c526d15a2a0eb90632b354ccba2`
