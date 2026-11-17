# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Stage 8.9.74 Automated Regression Test Results & Audit Log

**Project:** Festival Scream Detector  
**Stage:** 8.9.74  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Date of Execution:** 2026-11-14  
**Test Suite File:** [test_stage_8_9_74.py](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_74/tests/test_stage_8_9_74.py)  
**Execution Environment:** Windows 11 (Python 3.13.3, pytest 9.1.1, PyTorch CPU)  
**Overall Outcome:** 11 PASSED, 0 FAILED (100% Pass Rate in 3.56 seconds)

---

## 1. Executive Summary

The automated regression test suite for Stage 8.9.74 rigorously evaluates:
1. **Model & Artifact Governance:** Immutability of baseline production files, Stage 60 evaluation manifest integrity, historical Stage 61 prediction verification, and bit-level freeze of Candidate 71-D checkpoint.
2. **Prediction Parity & Reproduction:** Deterministic reproduction of Candidate 71-D metrics on the exposed validation cohort (exact numerators and denominators: 82/99 recall, 10/124 HN FPR, 13/88 shout FPR, 37/39 short recall, 71/80 real recall, 11/19 synthetic recall).
3. **Child Scream Veto Trace:** Exact acoustic feature boundaries ($roughness < 0.022$ and $hf\_ratio < 0.050$) triggering distress veto suppression.
4. **Source-Group Accounting & Data Leakage:** Exact source group counts (47 Pos, 69 HN, 28 Shout, 138 total unique) and zero leakage between synthetic validation audio and training sets.
5. **Streaming Buffer & Inference Latency:** Model CPU P95 latency ceiling ($\le 25.0$ ms) and end-to-end downstream processing pipeline execution.
6. **Dashboard Service Integration:** Candidate registry status as `ACTIVE_RESEARCH_CHAMPION` and operational designation `RECORDED AUDIO VERIFIED; MICROPHONE UNVERIFIED`.

---

## 2. Test Execution Ledger

| Test # | Test Case Identifier | Group / Category | Assertions Evaluated | Outcome | Execution Latency |
|---|---|---|---|---|---|
| 1 | `test_line1_safety_headers` | Governance & Compliance | Verifies line 1 of every markdown and python file in Stage 8.9.74 reads `# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.` | **PASS** | < 0.05 s |
| 2 | `test_protected_baseline_immutability` | Governance & Compliance | Cryptographic SHA-256 verification of 4 production baseline assets (`scream_classifier.joblib`, `model_metadata.json`, `test_predictions.csv`, `stage5_test_evaluation.md`) | **PASS** | < 0.05 s |
| 3 | `test_candidate_71_checkpoint_freeze` | Model Integrity | Verifies physical existence and SHA-256 match for Candidate 71-D (`e4314990...`) | **PASS** | 0.05 s |
| 4 | `test_stage_60_manifest_integrity_and_prediction_trace` | Provenance Audit | Cryptographic verification of Stage 60 manifest (`9dfa4ced...`) and confirmation that historical Stage 61 prediction file exists with exactly 2,801 lines | **PASS** | 0.02 s |
| 5 | `test_candidate_71d_reproduction_metrics` | Prediction Parity | Bit-for-bit reproduction of all Candidate 71-D counts: 82 TP, 17 FN, 10 HN FP, 13 Shout FP, 37 Short TP, 71 Real TP, 11 Synth TP | **PASS** | 0.65 s |
| 6 | `test_child_scream_distress_veto_trace` | Forensic Analysis | Validates that child screams exhibit $roughness < 0.022$ and $hf\_ratio < 0.050$, triggering distress veto suppression | **PASS** | 0.02 s |
| 7 | `test_source_group_accounting` | Dataset Provenance | Asserts that validation partition contains exactly 47 Pos SGs, 69 HN SGs, 28 Shout SGs, and 138 total unique SGs | **PASS** | 0.02 s |
| 8 | `test_zero_synthetic_to_train_leakage` | Dataset Provenance | Asserts zero clip ID overlap and zero source group overlap between synthetic validation screams and the training partition | **PASS** | 0.05 s |
| 9 | `test_latency_ceiling_gate5` | Performance Benchmarks | Validates single-stream neural inference latency P95 is $\le 25.0$ ms (actual: 0.392 ms) | **PASS** | 0.12 s |
| 10 | `test_complete_pipeline_execution` | Streaming Engine | Verifies end-to-end downstream processing on a 1-second audio window via `ResearchService.evaluate_audio_window` | **PASS** | 0.04 s |
| 11 | `test_dashboard_model_selection_and_status` | UI & Service Integration | Asserts `ResearchService` correctly initializes Candidate 71-D as `ACTIVE_RESEARCH_CHAMPION` at threshold 0.4920 | **PASS** | 1.85 s |

---

## 3. Cryptographic Baseline Verification

- `backend/models/scream_classifier.joblib`: `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` (MATCH)
- `backend/models/model_metadata.json`: `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` (MATCH)
- `backend/reports/test_predictions.csv`: `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` (MATCH)
- `backend/reports/stage5_test_evaluation.md`: `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` (MATCH)
- `backend/research/stage_8_9_60/future_evaluation_manifest.json`: `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd` (MATCH)
- `backend/research/stage_8_9_74/models/candidate_71_frozen.pt`: `e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b` (MATCH)

---

## 4. Conclusion & Certification

All 11 regression tests passed with 100% compliance.
Certified by: Senior Research Systems & Quality Engineer  
Status: **PASSED (11/11)**

