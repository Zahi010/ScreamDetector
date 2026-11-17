# STAGE 8.9.30.1 — DUPLICATE FORENSICS & SOURCE INDEPENDENCE SUMMARY

**Project:** Festival Scream Detector  
**Stage:** 8.9.30.1  
**Operating Mode:** Dataset Forensics & Independent Source Verification  
**Date:** November 2, 2026  
**Auditor:** Senior ML Research Engineer & Audio Forensics Specialist  

---

## 1. EXECUTIVE FORENSIC SUMMARY

Stage 8.9.30 reported 204 acquired audio recordings across 49 source groups. However, forensic analysis revealed that the 49-group number was an artifact of an uploader-parsing defect in `evaluate_and_audit.py`, which defaulted 76 Freesound sounds to a single `fs_user_freesound_user` group and 56 NIGENS files to `nigens_zenodo`.

When audited against underlying Freesound API metadata and Zenodo origin archives:
- **Total Audio Files Audited:** 204
- **Exact File Checksum Duplicates (SHA-256):** 0
- **Exact Quantized PCM Hash Duplicates:** 0
- **Unique True Audio Uploaders / Creators:** 81
- **Reconciled Source Groups / Session Clusters:** 87
- **Independent Genuine Positive Scream Source Groups:** 49

**Critical Audit Conclusion:** The 137 reported positive scream recordings do **NOT** represent 137 independent positive sources. They represent at most 49 independent scream sources, with multiple multi-clip recording sessions originating from the same performers.

---

## 2. MULTI-CLIP SESSION & EXCERPT CLUSTERING FORENSICS

While no exact byte-for-byte duplicates were detected, extensive near-duplicate and multi-clip session relationships were identified:

| Creator / Uploader | Clip Count | Category | Representative Clip Titles | Independence Assessment |
|---|---:|---|---|---|
| `todorrobot` | 9 | Stadium Cheering | `Fernando Escobar 20240915`, `Good sportsmanship 20240915` | Multi-clip excerpt of same high school football game broadcast. |
| `jorickhoofd` | 9 | Speech / Scream | `Scream - male 01`, `Scream - male 02`, `Angry male voice` | Same voice actor recorded in identical acoustic vocal booth. |
| `julius_galla` | 8 | Screams / Shouts | `Girl scream 01.wav` through `Girl scream 08.wav` | Consecutive takes from single recording session of one female actor. |
| `WelvynZPorterSamples` | 6 | Shouted War Cries | `Male Yelling out a War Cry 1`, `4`, `5`, `7`, `8`, `9` | Single male performer performing variations of war cry with identical artificial reverb. |
| `JohnsonBrandEditing` | 4 | Genuine Screams | `Scream 1.wav`, `Scream 2.wav`, `Scream 3.wav`, `Scream 4.wav` | Sound library takes from single studio recording session. |
| `MrFossy` | 4 | Death Screams | `Voice_AdultMale_DeathScreams_01` to `04` | Male voice artist performing video-game death vocalizations in one session. |
| `kevp888` | 2 | Stadium Ambience | `240414_191448_IT_Supporters...`, `240414_192357-1...` | Two excerpts from single basketball game in Florence. |
| `arjanvanhoorn0181` | 2 | Genuine Screams | `young-girl-screaming-1`, `young-girl-screaming-2` | Consecutive takes of same child performer. |
| `missozzy` | 2 | Genuine Screams | `female-scream-01`, `female-scream-02` | Consecutive takes of same female vocalist. |

### Implications for Machine Learning:
1. **Intra-Session Correlation:** Multi-clip takes from the same voice actor share vocal tract morphology, fundamental frequency registers, and room impulse responses.
2. **Data Leakage Risk:** If multi-clip takes from `julius_galla` or `MrFossy` were randomly split between train and test, the test set would measure memorization of the speaker's timbre rather than generalized scream detection.
3. **Partition Requirement:** All multi-clip sessions must be quarantined or assigned as an atomic block to a single partition.

---

## 3. EVIDENCE-BASED INDEPENDENCE TABLE

| Metric Category | Count | Forensic Validation Evidence |
|---|---:|---|
| **Total Processed Recordings** | 204 | Verified readable 16kHz mono Float32 audio files |
| **Unique Audio Streams** | 204 | Distinct PCM waveforms verified |
| **Exact Byte Collisions** | 0 | [duplicate_reaudit.csv](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_30_1/duplicate_reaudit.csv) |
| **Unique True Uploaders** | 81 | [source_independence_audit.csv](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_30_1/source_independence_audit.csv) |
| **Reconciled Source Groups** | 87 | [source_group_reconciliation.csv](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_30_1/source_group_reconciliation.csv) |
| **Single-Clip Independent Sources** | 56 | Uploaders contributing exactly one recording |
| **Multi-Clip Correlated Sessions** | 31 | Uploaders contributing 2 or more correlated takes |
| **Confirmed Independent Scream Sources** | 49 | Unique source groups providing genuine human screams |
