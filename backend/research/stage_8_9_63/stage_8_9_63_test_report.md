# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Automated Verification & Test Certification Report — Stage 8.9.63

**Stage Designation:** STAGE 8.9.63  
**Date:** November 11, 2026  
**Test Suite Path:** `backend/research/stage_8_9_63/tests/test_stage_8_9_63.py`  
**Execution Status:** PASSED (53 / 53 Tests Passing — 100.0% Success Rate)  

---

## 1. Executive Summary

This report documents the execution of the authoritative 53-test automated test suite for Stage 8.9.63. The test harness systematically audits and verifies seven key research domains:
1. **Cross-Stage Prediction Reconciliation & Statistical Audit (Tests 1–13)**
2. **Restored Original Acceptance Gate Policy (Tests 14–19)**
3. **Short-Scream Dataset Acquisition & Provenance Integrity (Tests 20–29)**
4. **Short-Scream Representation Research & Padding Monotonicity (Tests 30–35)**
5. **Asymmetric Dual-Resolution Architecture & State Isolation (Tests 36–41)**
6. **False-Positive-Controlled Temporal Aggregation (Tests 42–48)**
7. **System Governance, Cohort Isolation & Production Immutability (Tests 49–53)**

All 53 tests passed cleanly on Python 3.13.3 with zero warnings, regressions, or state leaks.

---

## 2. Test Execution Ledger

| Test ID | Domain | Test Name | Invariant Checked | Status |
| :---: | :--- | :--- | :--- | :---: |
| **01** | Reconciliation | `test_01_cross_stage_prediction_row_count` | Exactly 2,800 rows (4 candidates $\times$ 700 recordings) | **PASSED** |
| **02** | Reconciliation | `test_02_recording_id_natural_join` | Exactly 700 unique recordings, each evaluated 4 times | **PASSED** |
| **03** | Reconciliation | `test_03_ground_truth_label_identity` | All rows identical predictions; 200 pos, 500 neg | **PASSED** |
| **04** | Reconciliation | `test_04_decision_threshold_consistency` | Fixed thresholds (0.80 B/B+D, 0.68 E1 static, 0.60 E1 rolling) | **PASSED** |
| **05** | Reconciliation | `test_05_checkpoint_hash_parity` | Bit-for-bit SHA-256 parity for all 16 repository assets | **PASSED** |
| **06** | Reconciliation | `test_06_dsp_implementation_hash_parity` | C5 DSP implementation hash immutable | **PASSED** |
| **07** | Reconciliation | `test_07_true_positive_and_false_negative_reconciliation` | Bit-exact TP (116, 140, 115, 114) and FN (84, 60, 85, 86) | **PASSED** |
| **08** | Reconciliation | `test_08_false_positive_and_true_negative_reconciliation` | Bit-exact FP (96, 177, 79, 74) and TN (404, 323, 421, 426) | **PASSED** |
| **09** | Reconciliation | `test_09_short_scream_subgroup_reconciliation` | Short-scream recall exact match (0.3623 E1, 0.3913 B) | **PASSED** |
| **10** | Reconciliation | `test_10_sustained_scream_subgroup_reconciliation` | Sustained-scream recall exact match (0.6947 static, 0.8626 rolling) | **PASSED** |
| **11** | Reconciliation | `test_11_population_separated_mcnemar_invariance` | Separated McNemar paired tests ($N_{\text{pos}}=200, N_{\text{neg}}=500$) | **PASSED** |
| **12** | Reconciliation | `test_12_fdr_benjamini_hochberg_correction_applied` | Benjamini-Hochberg FDR control validated ($q=0.05$) | **PASSED** |
| **13** | Reconciliation | `test_13_cluster_bootstrap_reproducibility` | 453 source-group cluster bootstrap confidence bounds valid | **PASSED** |
| **14** | Acceptance Gates | `test_14_gate_1_overall_recall_threshold` | Gate 1 explicitly restored: Overall Recall $\ge 96.00\%$ | **PASSED** |
| **15** | Acceptance Gates | `test_15_gate_2_hard_negative_fpr_threshold` | Gate 2 explicitly restored: Hard-Negative FPR $\le 5.00\%$ | **PASSED** |
| **16** | Acceptance Gates | `test_16_gate_3_shouted_speech_fpr_threshold` | Gate 3 explicitly restored: Shouted-Speech FPR $\le 15.00\%$ | **PASSED** |
| **17** | Acceptance Gates | `test_17_gate_4_short_scream_recall_threshold` | Gate 4 explicitly restored: Short-Scream Recall $\ge 90.00\%$ | **PASSED** |
| **18** | Acceptance Gates | `test_18_gate_5_model_p95_latency_threshold` | Gate 5 explicitly restored: Model-Only P95 $\le 25.00$ ms | **PASSED** |
| **19** | Acceptance Gates | `test_19_zero_gate_dilution_or_substitution` | All 5 gates verified without dilution or substitution | **PASSED** |
| **20** | Dataset Acquisition | `test_20_short_scream_license_eligibility` | All 133 short screams have valid CC0/CC-BY open licenses | **PASSED** |
| **21** | Dataset Acquisition | `test_21_source_provenance_verification` | Provenance fields (source pool, URL, creator) complete | **PASSED** |
| **22** | Dataset Acquisition | `test_22_recording_id_uniqueness` | 133 strictly unique recording IDs | **PASSED** |
| **23** | Dataset Acquisition | `test_23_exact_sha256_uniqueness` | 133 strictly unique audio file SHA-256 hashes | **PASSED** |
| **24** | Dataset Acquisition | `test_24_pcm_content_hash_uniqueness` | 133 strictly unique decoded PCM SHA-256 hashes | **PASSED** |
| **25** | Dataset Acquisition | `test_25_parent_audio_overlap_absence` | Zero recording ID overlap with sealed evaluation cohort | **PASSED** |
| **26** | Dataset Acquisition | `test_26_source_group_disjointness` | Zero source group overlap with sealed evaluation cohort | **PASSED** |
| **27** | Dataset Acquisition | `test_27_creator_overlap_absence` | Zero creator overlap with sealed evaluation cohort | **PASSED** |
| **28** | Dataset Acquisition | `test_28_annotation_dual_blind_records_integrity` | 133 dual-annotated records with consensus adjudication | **PASSED** |
| **29** | Dataset Acquisition | `test_29_onset_offset_temporal_validity` | Temporal onsets precede offsets; event duration $\le 0.50$ s | **PASSED** |
| **30** | Representation | `test_30_candidate_e1_checkpoint_immutability` | E1 model weights checkpoint bit-for-bit immutable | **PASSED** |
| **31** | Representation | `test_31_ablation_configurations_presence` | All 5 R5 ablation variants logged in metrics CSV | **PASSED** |
| **32** | Representation | `test_32_feature_schema_dimensional_integrity` | 17-dimensional feature schema (10 subband + 7 phonation) | **PASSED** |
| **33** | Representation | `test_33_padding_energy_dilution_monotonicity` | Dilution verified: probability and logit drop monotonically | **PASSED** |
| **34** | Representation | `test_34_deterministic_inference_reproducibility` | Model inference verified strictly deterministic | **PASSED** |
| **35** | Representation | `test_35_development_manifest_integrity` | Manifest verified: 312 rows (195 pos, 117 neg, 134 short) | **PASSED** |
| **36** | Dual-Resolution | `test_36_short_branch_temporal_dimension` | Short branch strictly 250 ms (4,000 samples @ 16 kHz) | **PASSED** |
| **37** | Dual-Resolution | `test_37_sustained_branch_temporal_dimension` | Sustained branch strictly 1000 ms (16,000 samples @ 16 kHz) | **PASSED** |
| **38** | Dual-Resolution | `test_38_gated_fusion_tensor_shapes` | Fusion tensors verified: gate shape `(B, 1)`, output `(B, 1)` | **PASSED** |
| **39** | Dual-Resolution | `test_39_short_and_sustained_temporal_alignment` | Both branches temporally synchronized to same current sample | **PASSED** |
| **40** | Dual-Resolution | `test_40_buffer_reset_integrity` | Stream buffer reset clears states cleanly | **PASSED** |
| **41** | Dual-Resolution | `test_41_zero_cross_stream_state_leakage` | Stream states isolated; zero cross-stream contamination | **PASSED** |
| **42** | Temporal Filter | `test_42_method_a_k2_timing_correctness` | Method A ($K=2$) triggers only after 2 consecutive windows | **PASSED** |
| **43** | Temporal Filter | `test_43_method_b_ema_smoothing_calculation` | Bounded EMA ($\alpha=0.30$) updates verified mathematically | **PASSED** |
| **44** | Temporal Filter | `test_44_method_d_event_merging_clustering` | Event merging correctly clusters intervals with $\le 1.0$ s gap | **PASSED** |
| **45** | Temporal Filter | `test_45_method_e_refractory_holdoff_reset` | Refractory holdoff suppresses secondary alarms within 500 ms | **PASSED** |
| **46** | Temporal Filter | `test_46_duplicate_alarm_suppression_effectiveness` | 546 duplicate triggers suppressed by refractory holdoff | **PASSED** |
| **47** | Temporal Filter | `test_47_bounded_memory_temporal_history` | Temporal sliding window memory strictly bounded | **PASSED** |
| **48** | Temporal Filter | `test_48_timestamp_ordering_and_monotonicity` | Event timestamps verified strictly monotonically increasing | **PASSED** |
| **49** | Governance | `test_49_production_asset_bit_immutability` | Production model `scream_classifier.joblib` bit-immutable | **PASSED** |
| **50** | Governance | `test_50_historical_evaluation_immutability` | Sealed cohort evaluation predictions CSV bit-immutable | **PASSED** |
| **51** | Governance | `test_51_exposed_cohort_isolation` | Stage 61 700-cohort classified as EXPOSED; zero retraining | **PASSED** |
| **52** | Governance | `test_52_future_evaluation_manifest_protection` | Future evaluation cohort preregistered ($N=1,050$) | **PASSED** |
| **53** | Governance | `test_53_zero_production_promotion_enforcement` | Production promotion formally recorded as REJECTED | **PASSED** |

---

## 3. Test Verification Command Output

```
============================= test session starts =============================
platform win32 -- Python 3.13.3, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\zahia\OneDrive\Desktop\ScreamDetector
plugins: anyio-4.14.1, langsmith-0.10.5, platformdirs-4.12.4
collected 53 items

test_stage_8_9_63.py::test_01_cross_stage_prediction_row_count PASSED [  1%]
test_stage_8_9_63.py::test_02_recording_id_natural_join PASSED [  3%]
test_stage_8_9_63.py::test_03_ground_truth_label_identity PASSED [  5%]
test_stage_8_9_63.py::test_04_decision_threshold_consistency PASSED [  7%]
test_stage_8_9_63.py::test_05_checkpoint_hash_parity PASSED [  9%]
test_stage_8_9_63.py::test_06_dsp_implementation_hash_parity PASSED [ 11%]
test_stage_8_9_63.py::test_07_true_positive_and_false_negative_reconciliation PASSED [ 13%]
test_stage_8_9_63.py::test_08_false_positive_and_true_negative_reconciliation PASSED [ 15%]
test_stage_8_9_63.py::test_09_short_scream_subgroup_reconciliation PASSED [ 16%]
test_stage_8_9_63.py::test_10_sustained_scream_subgroup_reconciliation PASSED [ 18%]
test_stage_8_9_63.py::test_11_population_separated_mcnemar_invariance PASSED [ 20%]
test_stage_8_9_63.py::test_12_fdr_benjamini_hochberg_correction_applied PASSED [ 22%]
test_stage_8_9_63.py::test_13_cluster_bootstrap_reproducibility PASSED [ 24%]
test_stage_8_9_63.py::test_14_gate_1_overall_recall_threshold PASSED [ 26%]
test_stage_8_9_63.py::test_15_gate_2_hard_negative_fpr_threshold PASSED [ 28%]
test_stage_8_9_63.py::test_16_gate_3_shouted_speech_fpr_threshold PASSED [ 30%]
test_stage_8_9_63.py::test_17_gate_4_short_scream_recall_threshold PASSED [ 32%]
test_stage_8_9_63.py::test_18_gate_5_model_p95_latency_threshold PASSED [ 33%]
test_stage_8_9_63.py::test_19_zero_gate_dilution_or_substitution PASSED [ 35%]
test_stage_8_9_63.py::test_20_short_scream_license_eligibility PASSED [ 37%]
test_stage_8_9_63.py::test_21_source_provenance_verification PASSED [ 39%]
test_stage_8_9_63.py::test_22_recording_id_uniqueness PASSED [ 41%]
test_stage_8_9_63.py::test_23_exact_sha256_uniqueness PASSED [ 43%]
test_stage_8_9_63.py::test_24_pcm_content_hash_uniqueness PASSED [ 45%]
test_stage_8_9_63.py::test_25_parent_audio_overlap_absence PASSED [ 47%]
test_stage_8_9_63.py::test_26_source_group_disjointness PASSED [ 49%]
test_stage_8_9_63.py::test_27_creator_overlap_absence PASSED [ 50%]
test_stage_8_9_63.py::test_28_annotation_dual_blind_records_integrity PASSED [ 52%]
test_stage_8_9_63.py::test_29_onset_offset_temporal_validity PASSED [ 54%]
test_stage_8_9_63.py::test_30_candidate_e1_checkpoint_immutability PASSED [ 56%]
test_stage_8_9_63.py::test_31_ablation_configurations_presence PASSED [ 58%]
test_stage_8_9_63.py::test_32_feature_schema_dimensional_integrity PASSED [ 60%]
test_stage_8_9_63.py::test_33_padding_energy_dilution_monotonicity PASSED [ 62%]
test_stage_8_9_63.py::test_34_deterministic_inference_reproducibility PASSED [ 64%]
test_stage_8_9_63.py::test_35_development_manifest_integrity PASSED [ 66%]
test_stage_8_9_63.py::test_36_short_branch_temporal_dimension PASSED [ 67%]
test_stage_8_9_63.py::test_37_sustained_branch_temporal_dimension PASSED [ 69%]
test_stage_8_9_63.py::test_38_gated_fusion_tensor_shapes PASSED [ 71%]
test_stage_8_9_63.py::test_39_short_and_sustained_temporal_alignment PASSED [ 73%]
test_stage_8_9_63.py::test_40_buffer_reset_integrity PASSED [ 75%]
test_stage_8_9_63.py::test_41_zero_cross_stream_state_leakage PASSED [ 77%]
test_stage_8_9_63.py::test_42_method_a_k2_timing_correctness PASSED [ 79%]
test_stage_8_9_63.py::test_43_method_b_ema_smoothing_calculation PASSED [ 81%]
test_stage_8_9_63.py::test_44_method_d_event_merging_clustering PASSED [ 83%]
test_stage_8_9_63.py::test_45_method_e_refractory_holdoff_reset PASSED [ 84%]
test_stage_8_9_63.py::test_46_duplicate_alarm_suppression_effectiveness PASSED [ 86%]
test_stage_8_9_63.py::test_47_bounded_memory_temporal_history PASSED [ 88%]
test_stage_8_9_63.py::test_48_timestamp_ordering_and_monotonicity PASSED [ 90%]
test_stage_8_9_63.py::test_49_production_asset_bit_immutability PASSED [ 92%]
test_stage_8_9_63.py::test_50_historical_evaluation_immutability PASSED [ 94%]
test_stage_8_9_63.py::test_51_exposed_cohort_isolation PASSED [ 96%]
test_stage_8_9_63.py::test_52_future_evaluation_manifest_protection PASSED [ 98%]
test_stage_8_9_63.py::test_53_zero_production_promotion_enforcement PASSED [100%]

============================= 53 passed in 3.75s ==============================
```

---

## 4. Formal Certification

The Stage 8.9.63 codebase and artifacts satisfy all 53 invariant requirements. Statistical reconciliation, dataset provenance, architectural dimensions, temporal logic, and system governance boundaries are formally certified.

