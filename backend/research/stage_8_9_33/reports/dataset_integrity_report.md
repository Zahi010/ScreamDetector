# STAGE 8.9.33 — DATASET INTEGRITY, COHORT RECONCILIATION & PROVENANCE REPORT

**Project:** Festival Scream Detector  
**Stage:** 8.9.33 — Dual-Objective Optimization, Hard-Negative Discrimination & Independent Validation  
**Operating Mode:** Offline-First Research & Dataset Forensics Audit  
**Production Status:** STRICTLY FROZEN (Production Threshold: `0.3500`)  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  

---

## 1. PHASE ZERO AUDIT: COHORT RECONCILIATION

Historical documentation across Stages 8.9.27 through 8.9.32 cited varying cohort sizes, category counts, and negative distributions. Phase Zero reconciled every cited evaluation dataset against underlying filesystem artifacts.

### 1.1 Complete Historical Cohort Crosswalk

| Cohort Identifier | Historical Stage | Total ($N$) | Screams | Negatives | Source Groups | Role & Historical Purpose | Cross-Cohort Overlap | Reconciled Status |
|---|---|---:|---:|---:|---:|---|---|---|
| **STAGE_8_9_27_BLIND_COHORT** | Stage 8.9.27 | 295 | 55 | 240 | 272 | Early blind benchmark evaluation | Disjoint | RECONCILED |
| **STAGE_8_9_30_RAW_ACQUISITION**| Stage 8.9.30 | 204 | 137 | 67 | 49 | Raw acquired dataset prior to audit | Superseded by 8.9.30.1 | RECONCILED |
| **STAGE_8_9_30_1_AUDITED_COHORT**| Stage 8.9.30.1 / 8.9.31 | 204 | 106 | 98 | 49 | Audited empirical cohort (re-labelled) | 0 overlap with 8.9.32 Test | RECONCILED |
| **STAGE_8_9_32_HELD_OUT_TEST** | Stage 8.9.32 / 8.9.33 | 293 | 102 | 191 | 111 | Authoritative independent test split | 0 overlap with 8.9.30.1 | RECONCILED |
| **FORENSIC_DIAGNOSTIC_COHORT** | Stage 8.9.30.2 / 8.9.31 | 6 | 6 | 0 | 5 | Ring-buffer underflow forensic test | Diagnostic subset of 8.9.30.1 | RECONCILED |

---

## 2. RESOLUTION OF CATEGORY COUNT DISCREPANCIES

Historical reports presented confusing discrepancies:
- **Crowd Cheering:** 28 vs 42
- **Infant Crying:** 14 vs 15
- **Shouted Speech:** 2 vs 48
- **Total Hard Negatives:** 98 vs 191

### 2.1 The Root Cause: Disjoint Datasets
Forensic file-hash analysis confirmed that these counts originate from **two completely distinct evaluation cohorts**:

1. **Cohort 1 ($N=204$):** Evaluated in Stage 8.9.30.1 and Stage 8.9.31.
   - Contains: 28 cheering, 14 infant crying, 2 shouting, 23 music/applause, 31 synthetic/transient = 98 hard negatives.
2. **Cohort 2 ($N=293$):** Held-out test split of the 1,328-sample multi-source dataset (`dataset_manifest_v3.csv`), evaluated in Stage 8.9.32 and Stage 8.9.33.
   - Contains: 42 cheering, 15 infant crying, 48 shouting, 86 sirens/whistles/transients = 191 hard negatives.

Cross-referencing audio file SHA-256 hashes proved that there is **exact 0.0% overlap (0 files in common)** between Cohort 1 and Cohort 2. The discrepancies were not errors of miscounting; they were reports from different benchmarks.

### 2.2 Category Crosswalk Table

| Standardized Category | Stage 8.9.31 Audited ($N=204$) | Stage 8.9.32/33 Independent Test ($N=293$) | Full v3 Corpus ($N=1,328$) | Evidence for Negative Label |
|---|---:|---:|---:|---|
| **scream (Positive)** | 106 | 102 | 353 | Verified human phonation of high distress/terror |
| **crowd_chant_cheering** | 28 | 42 | 192 | Collective stadium cheering, football chants, applause |
| **infant_crying** | 14 | 15 | 72 | Audited neonatal crying, pediatric fussing |
| **shouting_and_speech** | 2 | 48 | 218 | Loud vocal commands, sports coaching, theatrical speech |
| **music_and_singing** | 23 | 24 | 114 | Studio tracks, festival brass, vocal performances |
| **sirens_and_alarms** | 12 | 26 | 126 | Emergency vehicle sirens, smoke detectors, horns |
| **whistles_and_squeaks** | 19 | 36 | 253 | High-frequency referee whistles, dog toys, brake squeal |
| **Total Negatives** | **98** | **191** | **975** | Independent audio verification and review |

---

## 3. PARTITION ISOLATION & LEAKAGE PREVENTION

### 3.1 Source-Group Disjoint Splitting
To prevent data leakage caused by acoustic similarities among recordings from the same uploader, session, or capture device, partitioning was performed strictly at the **source-group level**:
- **Training Partition ($N=739$):** 338 unique source groups.
- **Validation Partition ($N=293$):** 112 unique source groups.
- **Independent Test Partition ($N=293$):** 111 unique source groups.

**Mathematical Leakage Check:**
$$\text{Train} \cap \text{Val} = \emptyset, \quad \text{Train} \cap \text{Test} = \emptyset, \quad \text{Val} \cap \text{Test} = \emptyset$$
Zero source groups, sessions, or recording IDs cross partition boundaries.

### 3.2 Licensing and Provenance Audit
All recordings within the active research manifest (`dataset_manifest_v3.csv`) are licensed permissively:
- Creative Commons Zero (CC0 1.0): 38.4%
- Creative Commons Attribution (CC-BY 4.0 / 3.0): 42.1%
- Creative Commons Attribution-ShareAlike (CC-BY-SA): 14.2%
- NIGENS Academic Non-Commercial: 5.3%

Zero proprietary, unverified, or copyright-infringing audio files exist in the active training, validation, or test partitions.
