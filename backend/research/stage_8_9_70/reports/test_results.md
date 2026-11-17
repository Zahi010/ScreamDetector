# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Stage 8.9.70 — Automated Test Suite Execution Results

**Mandatory Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.  
**Test Suite Path:** `backend/research/stage_8_9_70/tests/test_stage_8_9_70.py`  
**Execution Environment:** Python 3.13.3, PyTest 9.1.1, Windows x64  
**Date:** 2026-11-14  
**Status:** **7 PASSED, 0 FAILED (100% Pass Rate)**

---

## 1. Test Summary Table

| Test Function | Target Specification Tested | Execution Duration | Status |
| :--- | :--- | :--- | :--- |
| `test_line1_safety_headers` | Verifies Line 1 mandatory safety header in every stage script, report, and test | 0.05s | **PASSED** |
| `test_protected_baseline_immutability` | Validates bit-for-bit SHA-256 match for all 4 protected production files | 0.04s | **PASSED** |
| `test_sealed_cohort_quarantine` | Ensures Stage 60 sealed cohort ($N=700$) manifest exists, is unread, and matches SHA-256 | 0.02s | **PASSED** |
| `test_candidate_checkpoints_exist_and_match_hashes` | Confirms Candidate 69-D and Candidate 70-D checkpoints exist and match hashes | 0.03s | **PASSED** |
| `test_candidate_70_metadata` | Verifies Candidate 70-D metadata JSON fields, thresholds, and performance numbers | 0.01s | **PASSED** |
| `test_required_reports_exist` | Validates existence and non-zero size of all 13 required stage reports and CSVs | 0.02s | **PASSED** |
| `test_latency_ceiling_gate5` | Verifies model forward pass satisfies Gate 5 latency ceiling ($\le 25.0$ ms) | 0.42s | **PASSED** |

---

## 2. Integrity Verification Details

### 2.1 Protected Baseline Files
All 4 production baseline files match their exact reference SHA-256 hashes:
- `backend/models/scream_classifier.joblib`: `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` [PASSED]
- `backend/models/model_metadata.json`: `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` [PASSED]
- `backend/reports/test_predictions.csv`: `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` [PASSED]
- `backend/reports/stage5_test_evaluation.md`: `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` [PASSED]

### 2.2 Quarantined Cohort
- `backend/research/stage_8_9_60/future_evaluation_manifest.json`: `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd` [PASSED]

### 2.3 Research Checkpoints
- Candidate 69-D: `d468b75ab12d5ef2b8577c18304e8c4ddaf78f3059b2c0395a1a3263ac6dd92c` [PASSED]
- Candidate 70-D: `40a162d1f9e34564a93c1b88fb2a290909ee4deb32e659bd21bcf9c2d3c44b6d` [PASSED]

---

## 3. Test Command
To re-run the complete test suite:
```powershell
python -m pytest backend/research/stage_8_9_70/tests/test_stage_8_9_70.py -v
```

