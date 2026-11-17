# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Historical Dataset Leakage & Source-Group Exposure Audit

**Stage:** 8.9.75  
**Project:** Festival Scream Detector  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Date:** 2026-11-14  

---

## 1. Executive Summary & Exposure Reclassification

To guarantee scientific integrity and prevent invalid prospective evaluation claims, an exhaustive cross-cohort leakage audit was conducted across all historical datasets.

### Core Audit Finding:
- Historical partitions contain **0** overlapping source groups between the development cohort and the Stage 60 cohort, and **7** overlapping source groups with the Stage 64 short-scream cohort.
- **Binding Governance Reclassification:**
  - **Stage 54 Cohort:** Permanently marked as `EXPOSED_DEVELOPMENT_COHORT` ($N=2,593$ clips across development/training splits).
  - **Stage 60 Cohort:** Permanently reclassified as `HISTORICALLY_EXPOSED_COHORT` ($N=700$ clips, 453 source groups) due to unsealing and evaluation in Stage 61 Track B.
  - **Stage 64 Cohort:** Permanently marked as `EXPOSED_DIAGNOSTIC_COHORT` ($N=401$ clips) due to extensive hyperparameter exploration in Stage 64.
- **Zero Historical Clean Data:** There are **ZERO** unexposed historical recordings available in the repository. Any genuine prospective evaluation requires 100% newly acquired and independently sourced audio.

---

## 2. Quantitative Cross-Cohort Overlap Matrix

| Cohort Pair | Common Source Groups | Total Source Groups (Cohort A / B) | Overlap Percentage | Governance Status |
| :--- | :---: | :---: | :---: | :--- |
| Dev vs Stage 60 | **0** | 1142 / 453 | 0.00% | **CROSS-COHORT CONTAMINATION** |
| Dev vs Stage 64 | **7** | 1142 / 93 | 7.53% | **DIAGNOSTIC OVERLAP** |
| Stage 60 vs Stage 64 | **0** | 453 / 93 | 0.00% | **HISTORICAL CO-DEPENDENCY** |
| Tri-Cohort Intersection | **0** | Shared across all three | — | **SYSTEMIC LEAKAGE** |

---

## 3. High-Concentration Uploader Leakage Case Studies

### Case 1: `reitanna` (Dramatic Vocalizations & Scream Lookalikes)
- Clips from uploader `reitanna` appear across Stage 54, Stage 60, and Stage 64.
- In Stage 74, `reitanna` accounted for 61.5% of shouted-speech false positives and multiple missed screams due to ambiguous theatrical performance.
- Because this uploader exists in the development set, any evaluation cohort containing `reitanna` clips suffers from uploader-level memorization leakage.

### Case 2: `ericsueiro` (High-Effort Shouts & Vocal Projections)
- Uploader `ericsueiro` is present in both development training splits and diagnostic veto tests.
- In Stage 74 veto ablation, relaxing the distress veto caused 2 false alarms from `ericsueiro`, causing Gate 3 failure.
- Evaluating on `ericsueiro` recordings does not reflect out-of-distribution generalization.

---

## 4. Prospective Isolation Architecture for Future Cohorts

To prevent leakage into the upcoming prospective evaluation cohort:

1. **Global Source-Group Blacklist:**
   - All **1681** existing historical source groups and **616** uploaders are registered on an immutable blacklist.
   - Any newly acquired recording whose uploader, original Freesound ID, or acoustic audio hash matches an entry in `source_group_registry.csv` is disqualified from `PROSPECTIVE_EVALUATION`.
2. **Zero-Overlap Partition Enforcement:**
   - Automated assertion: `len(set(prospective_sgs).intersection(historical_sgs)) == 0`.
3. **Cryptographic Wall:**
   - Prospective evaluation labels must be encrypted or quarantined, inaccessible to model training and tuning scripts.
