# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Automated Regression Test Results & Verification Summary

**Stage:** 8.9.75  
**Project:** Festival Scream Detector  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Test Execution Date:** 2026-11-14  
**Test Suite:** [`backend/research/stage_8_9_75/tests/test_stage_8_9_75.py`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75/tests/test_stage_8_9_75.py)  
**Test Framework:** `pytest 9.1.1` on Python 3.13.3 (Windows x64)  
**Overall Verdict:** **11 PASSED / 0 FAILED (100% SUCCESS RATE)**  

---

## 1. Test Suite Execution Summary

| Test Case Identifier | Category | Verification Objective | Outcome | Execution Time |
| :--- | :--- | :--- | :---: | :---: |
| `test_01_protected_production_hashes` | Immutability | Bit-for-bit SHA-256 match for 4 production files + Stage 60 manifest | **PASSED** | 0.08s |
| `test_02_candidate_71_frozen_checkpoint` | Immutability | SHA-256 integrity of Candidate 71-D frozen weights (`e431499...`) | **PASSED** | 0.04s |
| `test_03_dataset_inventory_completeness` | Provenance | Master inventory contains >=3000 records with valid columns | **PASSED** | 0.12s |
| `test_04_source_group_registry_integrity` | Provenance | Registry contains >=1500 source groups and multi-cohort leak flags | **PASSED** | 0.09s |
| `test_05_synthetic_lineage_tracking` | Lineage | 100% of synthetic recordings have traceable parent recording IDs | **PASSED** | 0.05s |
| `test_06_partition_zero_source_group_overlap` | Governance | Strict 0% source-group leakage across TRAINING, DEV, PROSPECTIVE | **PASSED** | 0.08s |
| `test_07_evaluation_access_log_integrity` | Audit | Audit log preserves chronological access events across all stages | **PASSED** | 0.02s |
| `test_08_annotation_schema_validity` | Annotation | Draft-07 compliance, 19 primary categories, required fields | **PASSED** | 0.03s |
| `test_09_inter_rater_reliability_algorithms` | Statistics | Mathematical accuracy of Cohen's Kappa, Fleiss' Kappa, and IoU | **PASSED** | 0.06s |
| `test_10_mandatory_safety_headers` | Compliance | Line 1 of all .md and .py files contains mandatory safety header | **PASSED** | 0.05s |
| `test_11_all_required_deliverables_present` | Integrity | All Stage 75 deliverables verified present in directory | **PASSED** | 0.03s |

---

## 2. Protected Production Asset Hash Audit

| Asset Path | Expected SHA-256 Hash | Actual Runtime Hash | Status |
| :--- | :--- | :--- | :---: |
| `backend/models/scream_classifier.joblib` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | **MATCH** |
| `backend/models/model_metadata.json` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | **MATCH** |
| `backend/reports/test_predictions.csv` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | **MATCH** |
| `backend/reports/stage5_test_evaluation.md` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | **MATCH** |
| `backend/research/stage_8_9_60/future_evaluation_manifest.json` | `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd` | `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd` | **MATCH** |
| `stage_8_9_75/models/candidate_71_frozen.pt` | `e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b` | `e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b` | **MATCH** |

---

## 3. Test Suite Conclusion

All 11 automated verification tests passed with zero errors or warnings. Partition isolation, synthetic lineage inheritance, schema integrity, and baseline asset immutability are fully satisfied.

