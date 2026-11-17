# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.69 — AUTOMATED TEST SUITE EXECUTION & VERIFICATION REPORT

**Mandatory Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

---

## 1. Test Suite Summary

- **Test Suite Path:** `backend/research/stage_8_9_69/tests/test_stage_8_9_69.py`
- **Execution Timestamp:** 2026-11-13 23:58:12 UTC+5:30
- **Test Framework:** pytest 9.1.1 (Python 3.13.3, win32)
- **Total Tests Collected:** 25
- **Tests Passed:** 25 (100%)
- **Tests Failed:** 0 (0%)
- **Execution Duration:** 3.58 seconds

---

## 2. Test Execution Breakdown by Category

### Group 1: Safety Headers & Designations (2/2 Passed)
- `test_line_1_safety_header_all_stage_files`: **PASSED**. Confirmed that line 1 of every markdown and python file under `backend/research/stage_8_9_69/` strictly matches `# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.`.
- `test_research_service_safety_header`: **PASSED**. Verified presence in `backend/src/research_service.py`.

### Group 2: Protected Baseline & Historical Checkpoint Immutability (7/7 Passed)
- `test_protected_baseline_classifier_joblib_hash`: **PASSED** (`ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f`).
- `test_protected_baseline_model_metadata_hash`: **PASSED** (`30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60`).
- `test_protected_baseline_test_predictions_hash`: **PASSED** (`e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d`).
- `test_protected_baseline_stage5_evaluation_hash`: **PASSED** (`9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2`).
- `test_historical_candidate_65f_frozen_hash`: **PASSED** (`06a98025dbdabf462bec305b0cfe8455dd137b3d515cafca8811606865bacfab`).
- `test_historical_candidate_67_frozen_hash`: **PASSED** (`8fc2255a337f1375870370216416b94d9c2003a2b8939dbee1301115f53a7b18`).
- `test_historical_candidate_68_frozen_hash`: **PASSED** (`8a3b425a2885cfeeb4d9e6a64c04619949978cad5b55a8a5f60b5ee379949dc4`).

### Group 3: Sealed Cohort Isolation & Provenance (2/2 Passed)
- `test_sealed_evaluation_manifest_integrity`: **PASSED** (`9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd`). Confirmed quarantined and locked.
- `test_source_group_disjointness_across_partitions`: **PASSED**. Confirmed 0 source-group overlap between train, val, and test.

### Group 4: Candidate 69-D Model Checkpoint & Architecture (4/4 Passed)
- `test_candidate_69_frozen_checkpoint_exists`: **PASSED**.
- `test_candidate_69_checkpoint_sha256`: **PASSED** (`d468b75ab12d5ef2b8577c18304e8c4ddaf78f3059b2c0395a1a3263ac6dd92c`).
- `test_candidate_69_metadata_json`: **PASSED**.
- `test_candidate_69_checkpoint_contents`: **PASSED**. Correct heuristics parameters and thresholds stored.

### Group 5: Veto Activation & Rescue Policy Logic (3/3 Passed)
- `test_hfcr_veto_conditioned_on_roughness`: **PASSED**. Fires on deep vowel speech, rescues rough screams.
- `test_flux_veto_hf_bypass`: **PASSED**. Bypasses high-frequency scream events ($hf\_ratio > 1.0$).
- `test_calibrated_vocal_distress_veto`: **PASSED**. Rescues high-pitched/child scream `77AY` ($R \ge 0.022$).

### Group 6: Tournament Scorecard & Gate Verification (2/2 Passed)
- `test_tournament_results_csv_exists`: **PASSED**.
- `test_candidate_69d_gate_metrics`: **PASSED**. Validated TP=79, FN=20, Recall=79.80%, Shout FP=12, Shout FPR=13.64%, HN FP=10, HN FPR=8.06%, Short TP=36, Short Recall=92.31%.

### Group 7: Latency Compliance (1/1 Passed)
- `test_model_latency_under_ceiling`: **PASSED**. P95 latency is 0.384 ms single stream and 0.511 ms 8 streams, well under 25.0 ms ceiling.

### Group 8: ResearchService Live Backend Integration (4/4 Passed)
- `test_research_service_active_model_candidate_69`: **PASSED**.
- `test_research_service_candidate_69_registered`: **PASSED**.
- `test_research_service_candidate_69_inference`: **PASSED**.
- `test_research_service_evaluation_summary_gates`: **PASSED**.

