# Stage 8.9.2 — Missing Hard-Negative Audio Recovery Audit Report

**Date:** 2026-10-28  
**Project:** Festival Scream Detector (`C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector`)  
**Scope:** Investigation, audit, local recovery from `E:\FSD50K.dev_audio`, Freesound API acquisition, dashboard integration, and strict human review preservation.

---

## Executive Summary

Prior to Stage 8.9.2, the Festival Scream Detector review database contained 370 total discovered hard-negative candidates, of which:
- **Audio Available:** 185
- **Reviewed by Human:** 185 (181 Approved Non-Scream, 2 Scream Present, 2 Ambiguous)
- **Missing Audio:** 185 (50.0% of discovered candidates)

Following the Stage 8.9.2 recovery workflow:
- **Total Candidates:** 370
- **Audio Available:** **343** (+158 newly recovered recordings, **92.7% audio availability**)
- **Missing Audio:** **27** (7.3% unrecoverable due to licensing or source unavailability)
- **Completed Human Reviews Preserved:** **185 / 185 (100% strictly intact)**
  - `APPROVED_NON_SCREAM`: 181
  - `SCREAM_PRESENT`: 2
  - `AMBIGUOUS`: 2
- **Newly Recovered Pending Review:** 158 (All automatically triaged via Stage 8.9.1 engine, none auto-approved)

---

## 1. Breakdown of the 185 Missing Recordings by Source

The 185 missing recordings originated from three distinct source providers during Stage 8.8 acquisition:

| Source Provider | Missing Count | % of Missing | Primary Reason for Prior Missing Status |
| :--- | :---: | :---: | :--- |
| **FSD50K** | **144** | 77.8% | Files were stored in nested subdirectories on `E:\` (`FSD50K.dev_audio` and `FSD50K.eval_audio\FSD50K.eval_audio`), whereas the previous path resolver only checked top-level `E:\FSD50K.dev_audio\<id>.wav`. |
| **AudioSet** | **22** | 11.9% | Candidate ontology metadata discovered via AudioSet segment links. Direct YouTube downloading is legally restricted under YouTube Terms of Service and underlying copyright. |
| **Freesound** | **19** | 10.3% | Discovered during Stage 8.8 text search/curation, but automated download was never triggered during initial pipeline run. |
| **Total** | **185** | **100.0%** | — |

---

## 2. Recovery Audit & Results

### A. FSD50K Dataset on E: Drive (`E:\FSD50K.dev_audio`)
- **Indexed Ground Truth:** 51,197 files across official `dev.csv` (40,960) and `eval.csv` (10,237).
- **Found on E: Disk:** **139 recordings**.
- **Copied to Local Raw Dataset:** 139 files copied to `backend/dataset/stage8_8_hard_negatives/raw/fsd50k/` (approx. 28.4 MB).
- **Integrity & Zero-Mutation:** All original FSD50K files on `E:\` were accessed in **read-only mode**. No files were moved, renamed, modified, or deleted from `E:`.
- **Validation:** Every copied WAV file was decoded using `soundfile`, duration and channel metadata were calculated, and SHA-256 hashes were recorded in the database.

### B. Freesound API Acquisition
- **API Key Authentication:** Successfully authenticated to Freesound API v2 using the configured `FREESOUND_API_KEY` loaded from the project-root `.env`.
- **Licence Compliance:** All 19 Freesound recordings possess verified **CC0** (11 clips) or **CC-BY** (8 clips) licences, meeting the commercial intended-use criteria.
- **Downloaded:** **19 recordings** downloaded via official preview endpoints, decoded to float32 waveforms, converted to clean 16-bit PCM WAV, and stored in `backend/dataset/stage8_8_hard_negatives/raw/freesound/`.
- **Rate-Limiting:** Enforced respectful 0.4s inter-request backoff, avoiding API rate-limiting or errors.

### C. Unrecoverable Recordings (27 Total)
1. **AudioSet (22 recordings):**
   - Candidate IDs: `audioset_Y-0w9e1k8-M`, `audioset_Y12ffv_001_Q`, etc.
   - Status: Marked as `LICENCE_RESTRICTED` in `download_validation_status`.
   - Reason: AudioSet provides video segment timestamp metadata only. Mass-scraping underlying YouTube videos violates YouTube TOS Section 5.B and lacks confirmed redistributable licensing.
2. **FSD50K Synthetic Seeds (5 recordings):**
   - Candidate IDs: `fsd50k_412301`, `fsd50k_412302`, `fsd50k_412303`, `fsd50k_412304`, `fsd50k_412305`.
   - Status: Marked as `SOURCE_UNAVAILABLE` in `download_validation_status`.
   - Reason: These 5 IDs were placeholder demonstration seeds used during initial pipeline development prior to full dataset extraction, and do not exist in the official FSD50K release ground-truth archive on `E:`.

---

## 3. Dashboard and Triage Integration (Task 4)

1. **Missing Audio Recovery Panel (`MissingAudioRecoveryPanel.jsx`):**
   - Displays real-time live audit counters:
     - Missing recordings by source (FSD50K, Freesound, AudioSet)
     - Existing elsewhere on disk (139)
     - Eligible Freesound API (19)
     - Licence restricted (22)
     - Source unavailable (5)
     - Total recovered audio (343)
     - Human reviews preserved (185)
   - Features a controlled **"Recover Missing Audio"** action with live progress feedback, error handling, cancellation, and resumability.
   - Includes full provenance details table and safety guarantee alerts.
2. **Review Studio Integration:**
   - Added **"Missing Audio Recovery"** button in `ReviewSummaryCards.jsx` toolbar.
   - Wired modal into `ReviewStudio.jsx` with automatic queue refresh.
3. **Automated Acoustic Triage Integration:**
   - Every single newly recovered recording immediately underwent Stage 8.9.1 acoustic analysis via `AutomatedTriageEngine`.
   - Each recovered file received frozen scream classifier scoring (threshold 0.35), YAMNet top prior classes, acoustic tag detection, and clipping/silence metrics.
   - Newly recovered clips are immediately sorted and visible in the Review Studio queue with playback enabled.

---

## 4. Preservation of Historical Work (Task 5)

| Invariant Checked | Expected Value | Verified Actual | Status |
| :--- | :---: | :---: | :---: |
| Completed Human Reviews | 185 | 185 | **PASS** |
| `APPROVED_NON_SCREAM` Decisions | 181 | 181 | **PASS** |
| `SCREAM_PRESENT` Decisions | 2 | 2 | **PASS** |
| `AMBIGUOUS` Decisions | 2 | 2 | **PASS** |
| Newly Recovered Auto-Approval | 0 auto-approved (all UNREVIEWED) | 0 auto-approved | **PASS** |
| Scream Classifier Hash | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | **PASS** |
| Model Metadata Hash | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | **PASS** |
| Operating Threshold | 0.35 | 0.35 | **PASS** |
| Stage 4 & Stage 5 Datasets | Unmodified | Unmodified | **PASS** |

---

## 5. Updated Dashboard Totals Comparison

| Metric | Before Stage 8.9.2 | After Stage 8.9.2 | Net Change |
| :--- | :---: | :---: | :---: |
| **Total Discovered Candidates** | 370 | 370 | 0 |
| **Audio Available on Disk** | 185 | **343** | **+158** (+85.4%) |
| **Audio Missing** | 185 | **27** | **-158** (-85.4%) |
| **Total Human Reviewed** | 185 | **185** | **0 (Preserved)** |
| **Approved Non-Scream** | 181 | **181** | **0 (Preserved)** |
| **Scream Present** | 2 | **2** | **0 (Preserved)** |
| **Ambiguous Decisions** | 2 | **2** | **0 (Preserved)** |
| **Pending Human Review** | 185 | **185** | **0 (Preserved)** |

---

## 6. Verification Test Summary
- **Backend Recovery Test Suite (`test_stage8_9_2_recovery.py`):** 7 / 7 passed.
- **Review Studio Test Suite (`test_stage8_9_review_studio.py` & `test_stage8_9_1_triage.py`):** 29 / 29 passed.
- **Complete Backend Pytest Suite:** **160 / 160 passed** in 257.77s.
- **Frontend Vitest Suite:** **23 / 23 passed**.
- **Frontend Production Bundle:** Built cleanly with Vite in 221ms.
