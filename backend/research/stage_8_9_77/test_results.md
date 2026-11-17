# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Automated Regression Test Results & Verification Summary (Stage 8.9.77)

**Stage:** 8.9.77 — Independent Human Annotation Execution, Agreement Analysis, Adjudication & Prospective Cohort Qualification  
**Project:** Festival Scream Detector  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Test Execution Date:** 2026-11-14  
**Test Suite:** [`backend/research/stage_8_9_77/tests/test_stage_8_9_77.py`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_77/tests/test_stage_8_9_77.py)  
**Test Framework:** `pytest 9.1.1` on Python 3.13.3 (Windows x64)  
**Overall Verdict:** **12 PASSED / 0 FAILED (100% SUCCESS RATE)**  

---

## 1. Test Suite Execution Summary

| Test Case Identifier | Verification Objective | Outcome | Execution Time |
| :--- | :--- | :---: | :---: |
| `test_01_protected_production_hashes` | Bit-for-bit SHA-256 match for 4 production files + Stage 60 manifest | **PASSED** | 0.08s |
| `test_02_candidate_71_frozen_checkpoint` | SHA-256 integrity of Candidate 71-D frozen weights (`e431499...`) | **PASSED** | 0.04s |
| `test_03_stage76_discovery_arithmetic_reconciliation` | Exact reconciliation of 67 candidates: 26 downloaded + 41 quarantined | **PASSED** | 0.04s |
| `test_04_uploader_blacklist_reconciliation` | Reconciles 611 vs 612 uploaders (`unknown_creator` placeholder root cause) | **PASSED** | 0.04s |
| `test_05_historical_hash_coverage_audit` | Verifies 2,465 unique file hashes and 3,689 unique PCM hashes across 3,694 items | **PASSED** | 0.04s |
| `test_06_stage76_audio_integrity_verification` | Confirms all 26 WAV files exist, are 16 kHz mono, decodable, and hash-verified | **PASSED** | 0.08s |
| `test_07_annotation_assignment_double_blind_structure` | Confirms 52 assignment tasks staged (26 RATER_A, 26 RATER_B) with model blinding | **PASSED** | 0.04s |
| `test_08_no_model_predictions_in_review_queues` | Verifies zero model predictions or probabilities exist in reviewer assignment files | **PASSED** | 0.04s |
| `test_09_inter_rater_agreement_honest_block` | Validates agreement report honestly declares NOT CALCULATED without synthetic labels | **PASSED** | 0.04s |
| `test_10_adjudication_status_staged` | Confirms all 26 adjudication records staged in `AWAITING_INITIAL_HUMAN_RATINGS` | **PASSED** | 0.04s |
| `test_11_prospective_cohort_manifest_strictly_empty` | Verifies `prospective_evaluation_manifest.json` contains exactly 0 recordings | **PASSED** | 0.04s |
| `test_12_mandatory_safety_headers` | Confirms `# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.` on Line 1 | **PASSED** | 0.05s |

**Total Pytest Duration:** 0.63 seconds  

---

## 2. Frontend Build Verification

```
> frontend@0.0.0 build
> vite build

vite v8.3.5 building client environment for production...
transforming...
✓ 37 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.90 kB │ gzip:   0.48 kB
dist/assets/index-B0HPQvd6.css   85.33 kB │ gzip:  14.95 kB
dist/assets/index-xUPfriyM.js   450.72 kB │ gzip: 121.49 kB

✓ built in 193ms
```
**Frontend Status:** **CLEAN BUILD (0 errors, 0 warnings, 193 ms)**.

---

## 3. Production Asset Freeze Verification

| Protected Asset Path | Expected SHA-256 Digest | Status |
| :--- | :--- | :---: |
| `backend/models/scream_classifier.joblib` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | **BIT-FOR-BIT MATCH** |
| `backend/models/model_metadata.json` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | **BIT-FOR-BIT MATCH** |
| `backend/reports/test_predictions.csv` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | **BIT-FOR-BIT MATCH** |
| `backend/reports/stage5_test_evaluation.md` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | **BIT-FOR-BIT MATCH** |
| `backend/research/stage_8_9_60/future_evaluation_manifest.json` | `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd` | **BIT-FOR-BIT MATCH** |
| `backend/research/stage_8_9_77/models/candidate_71_frozen.pt` | `e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b` | **BIT-FOR-BIT MATCH** |

