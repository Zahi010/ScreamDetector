# STAGE 8.9.30.1 — HISTORICAL CONTAMINATION & STAGE 5 AUDIT REPORT

**Project:** Festival Scream Detector  
**Stage:** 8.9.30.1  
**Operating Mode:** Historical Test Isolation & Contamination Forensics  
**Date:** November 2, 2026  
**Auditor:** Senior ML Evaluation Reviewer  

---

## 1. MISSION & SCOPE

To prevent circular evaluation and data leakage, the Stage 5 historical test cohort (`backend/reports/test_predictions.csv`, 100 recordings, 44 source groups) and historical dataset splits must remain strictly isolated from all new research cohorts.

This audit cross-referenced all 204 Stage 8.9.30 recordings against:
1. Exact file paths and relative paths in `backend/reports/test_predictions.csv`.
2. Exact SHA-256 hashes in `backend/research/stage_8_9_27/src/workspace_audio_census.csv` (1,281 audio files).
3. Source groups and uploader identities in Stage 5 test predictions.
4. Independent dataset manifest hashes in `backend/research/stage_8_9_27/independent_dataset_manifest.csv`.

---

## 2. AUDIT OF THE 9 QUARANTINED NIGENS OVERLAPS

In Stage 8.9.30, 9 NIGENS scream files in the raw download pool were reported as flagged and skipped due to overlap with Stage 5 test creators or file paths.

### Forensic Investigation of the 9 Quarantined Files:

| NIGENS Filename | Original Creator | Stage 5 Conflict Type | Quarantine Verification Status |
|---|---|---|---|
| `femaleScream/saraonsins__scream_1.wav` | `saraonsins` | Creator & stem in Stage 5 test set (`freesound_saraonsins`) | **CONFIRMED QUARANTINED (Excluded from manifest)** |
| `femaleScream/saraonsins__scream_2.wav` | `saraonsins` | Creator & stem in Stage 5 test set (`freesound_saraonsins`) | **CONFIRMED QUARANTINED (Excluded from manifest)** |
| `femaleScream/ellenskellington__screaming.wav` | `ellenskellington` | Source group in Stage 5 test set (`freesound_ellenskellington`) | **CONFIRMED QUARANTINED (Excluded from manifest)** |
| `femaleScream/annatabernero__scream.wav` | `annatabernero` | Source group in Stage 5 test set (`freesound_annatabernero`) | **CONFIRMED QUARANTINED (Excluded from manifest)** |
| `maleScream/gutturalgutfuck__scream.wav` | `gutturalgutfuck` | Source group in Stage 5 test set (`freesound_gutturalgutfuck`) | **CONFIRMED QUARANTINED (Excluded from manifest)** |
| `maleScream/gutturalgutfuck__shriek.wav` | `gutturalgutfuck` | Source group in Stage 5 test set (`freesound_gutturalgutfuck`) | **CONFIRMED QUARANTINED (Excluded from manifest)** |
| `maleScream/412328__inspectorj__scream.wav` | `inspectorj` | Overlaps Stage 8.9.27 independent baseline manifest | **CONFIRMED QUARANTINED (Excluded from manifest)** |
| `femaleScream/337207__audionautics__scream.wav` | `audionautics` | Overlaps Stage 8.9.27 independent baseline manifest | **CONFIRMED QUARANTINED (Excluded from manifest)** |
| `femaleScream/344154__soundholder__scream.wav` | `soundholder` | Overlaps Stage 8.9.27 independent baseline manifest | **CONFIRMED QUARANTINED (Excluded from manifest)** |

**Verification Finding:** None of these 9 overlapping recordings entered `recording_manifest.csv` or the processed evaluation cohort. The exclusion filter operated with 100% precision.

---

## 3. AUDIT OF THE 204 INGESTED RECORDINGS

Cross-referencing all 204 records in [historical_contamination_reaudit.csv](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_30_1/historical_contamination_reaudit.csv):
- Exact Stage 5 test prediction overlaps: **0 files (0.00%)**
- Exact Stage 5 source group collisions: **0 files (0.00%)**
- Exact Stage 8.9.27 baseline manifest collisions: **0 files (0.00%)**
- Historical workspace census hash collisions: **0 files (0.00%)**

### Conclusion:
The 204 recordings in Stage 8.9.30 and Stage 8.9.30.1 are **100% free of Stage 5 historical test contamination**.
