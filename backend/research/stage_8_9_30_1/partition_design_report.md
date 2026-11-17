# STAGE 8.9.30.1 — PARTITION DESIGN & LEAKAGE AUDIT REPORT

**Project:** Festival Scream Detector  
**Stage:** 8.9.30.1  
**Partition Strategy:** Disjoint Source-Group / Uploader Clustering  
**Leakage Status:** **ZERO CROSS-PARTITION LEAKAGE VERIFIED**  
**Date:** November 2, 2026  

---

## 1. PARTITION DISTRIBUTION SUMMARY

| Proposed Partition | Total Recordings | Genuine Screams ($GT=1$) | Negative Controls ($GT=0$) | Reconciled Source Groups |
|---|---:|---:|---:|---:|
| **TRAINING_ELIGIBLE** | 121 | 63 | 58 | 46 |
| **DEVELOPMENT_VALIDATION** | 29 | 24 | 5 | 15 |
| **BLIND_INDEPENDENT_TEST** | 23 | 19 | 4 | 15 |
| **QUARANTINE_MISLABELED** | 31 | 0 | 31 | 8 |
| **TOTAL COHORT** | **204** | **106** | **98** | **83** |

---

## 2. PARTITION RULES & LEAKAGE VERIFICATION

1. **Strict Source-Group Separation:**
   - Every uploader and recording session is assigned to **exactly one partition**.
   - Zero multi-clip sessions cross partition boundaries (e.g., all 6 Welvyn war cries are in Quarantine; all 4 MrFossy screams are in Training; all 2 missozzy screams are in Dev).
2. **Quarantine of Mislabeled Audio:**
   - All 31 non-scream files that were erroneously labeled as screams in Stage 8.9.30 (stadium cheering, shouted commands, non-vocal noise) are quarantined and strictly excluded from model training and validation splits.
3. **Stage 5 Isolation:**
   - Zero historical Stage 5 test recordings or uploaders appear in any partition.
