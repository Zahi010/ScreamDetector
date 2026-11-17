# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Stage 8.9.72 Automated Regression Test Results & Audit Log

**Project:** Festival Scream Detector  
**Stage:** 8.9.72  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Date of Execution:** 2026-11-14  
**Test Suite File:** [test_stage_8_9_72.py](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_72/tests/test_stage_8_9_72.py)  
**Execution Environment:** Windows 11 (Python 3.13.3, pytest 9.1.1, PyTorch CPU)  
**Overall Outcome:** 15 PASSED, 0 FAILED (100% Pass Rate in 3.52 seconds)

---

## 1. Executive Summary

The automated regression test suite for Stage 8.9.72 rigorously evaluates:
1. **Model & Artifact Governance:** Immutability of baseline production files, sealed evaluation manifest quarantine, and bit-level freeze of candidate weights.
2. **Prediction Correctness & Veto Logic:** Fixed-recording inference parity, flux-conditioned resonance rescue suppression of false alarms, and vocal feature ablation fidelity.
3. **Dataset Quarantine & Provenance:** Zero overlap across source groups between Stage 54 validation cohort and held-out short scream cohorts.
4. **Streaming Buffer Boundaries:** Zero-padding integrity on ultra-short audio segments (< 250 ms) and downstream processing throughput.
5. **Dashboard Service Integration:** Live model switching, candidate registry metadata, session CSV exports, and Five-Gate scorecard fidelity.

---

## 2. Test Execution Ledger

| Test # | Test Case Identifier | Group / Category | Assertions Evaluated | Outcome | Execution Latency |
|---|---|---|---|---|---|
| 1 | `test_line1_safety_headers` | Governance & Compliance | Verifies line 1 of every markdown, script, and test file in Stage 8.9.72 reads `# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.` | **PASS** | < 0.05 s |
| 2 | `test_protected_baseline_immutability` | Governance & Compliance | Cryptographic SHA-256 verification of 4 production baseline assets (`scream_classifier.joblib`, `model_metadata.json`, `test_predictions.csv`, `stage5_test_evaluation.md`) | **PASS** | < 0.05 s |
| 3 | `test_sealed_cohort_quarantine` | Governance & Compliance | Cryptographic verification of Stage 60 sealed cohort manifest (`9dfa4ced...`) to guarantee 0% inspection or evaluation leakage | **PASS** | < 0.02 s |
| 4 | `test_candidate_checkpoints_exist_and_match_hashes` | Model Integrity | Verifies physical existence and SHA-256 match for Candidate 71-D (`e4314990...`) | **PASS** | 0.05 s |
| 5 | `test_fixed_recording_inference_parity` | Prediction Correctness | Deterministic inference check across fixed synthetic audio vectors ensuring identical probabilities across multiple evaluations | **PASS** | 0.35 s |
| 6 | `test_rescue_mechanism_ablation_logic` | Veto & Rescue Logic | Validates that stationary non-screams (flux $\le 0.040$) are NOT rescued by resonance rescue, while dynamic acoustic events (flux $> 0.040$) receive rescue increment | **PASS** | 0.01 s |
| 7 | `test_vocal_distress_veto_effect` | Veto & Rescue Logic | Validates that low-roughness harmonic sound bursts undergo 80% suppression factor ($0.20\times$) | **PASS** | 0.01 s |
| 8 | `test_dataset_source_group_disjointness` | Dataset Provenance | Asserts that Stage 54 validation cohort (N=311) and held-out short scream dataset (N=268) share exactly 0 source groups | **PASS** | 0.02 s |
| 9 | `test_required_reports_exist` | Artifact Completeness | Verifies presence and non-zero byte size of all required technical reports and experiment outcome CSVs | **PASS** | < 0.02 s |
| 10 | `test_latency_ceiling_gate5` | Performance Benchmarks | Validates single-stream neural inference latency P95 is $\le 25.0$ ms (actual: 0.417 ms) | **PASS** | 0.12 s |
| 11 | `test_streaming_buffer_short_event_padding` | Streaming Engine | Asserts audio buffers shorter than 250 ms (e.g., 100 ms burst) are correctly zero-padded to 4,000 samples and feature extraction succeeds | **PASS** | 0.03 s |
| 12 | `test_complete_pipeline_execution` | Streaming Engine | Verifies end-to-end downstream processing on a 1-second audio window via `ResearchService.evaluate_audio_window` | **PASS** | 0.04 s |
| 13 | `test_research_service_candidate_registry` | UI & Service Integration | Asserts `ResearchService` correctly initializes models with Candidate 71-D as `ACTIVE_RESEARCH_CHAMPION` | **PASS** | 1.85 s |
| 14 | `test_dashboard_model_switching` | UI & Service Integration | Verifies programmatic switching between model identifiers, updating active model state without silent fallbacks | **PASS** | 0.45 s |
| 15 | `test_dashboard_evaluation_summary` | UI & Service Integration | Verifies `get_evaluation_summary()` populates all 5 acceptance gates with Candidate 71-D results and correctly reports research verdict | **PASS** | 0.01 s |

---

## 3. Cryptographic Baseline Verification

- `backend/models/scream_classifier.joblib`: `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` (MATCH)
- `backend/models/model_metadata.json`: `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` (MATCH)
- `backend/reports/test_predictions.csv`: `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` (MATCH)
- `backend/reports/stage5_test_evaluation.md`: `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` (MATCH)
- `backend/research/stage_8_9_60/future_evaluation_manifest.json`: `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd` (MATCH)
- `backend/research/stage_8_9_71/models/candidate_71_frozen.pt`: `e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b` (MATCH)

---

## 4. Conclusion & Certification

All 15 regression tests passed with 100% compliance.
Certified by: Senior Research Systems Engineer  
Status: **PASSED (15/15)**

