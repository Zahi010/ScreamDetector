# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.66 AUTOMATED TEST REPORT
**Verification of 40 Unit, Integration, Regression, and Safety Tests**

## 1. Safety Designation
Non-certified acoustic research prototype. Prohibited for life-safety use, emergency alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

All tests utilize legally acquired recorded audio files and safe playback protocols only.

---

## 2. Test Execution Summary

- **Total Tests Executed:** 40
- **Total Tests Passed:** 40 (100.0%)
- **Total Tests Failed:** 0 (0.0%)
- **Test Runner:** pytest 9.1.1 (Python 3.13.3, win32)
- **Execution Wall Time:** 3.39 seconds
- **Test Suite Path:** [`tests/test_stage_8_9_66.py`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_66/tests/test_stage_8_9_66.py)

---

## 3. Results by Category

### Category 1: Baseline Protection & Cryptographic Integrity (8 / 8 PASSED)
- `test_01_all_21_protected_baseline_assets_verified`: PASSED. All 21 protected baseline assets match their expected SHA-256 hashes bit-for-bit with zero drift.
- `test_02_production_scream_classifier_integrity`: PASSED. Production scream classifier joblib model verified unmutated (`ad6e428d05...`).
- `test_03_model_metadata_json_integrity`: PASSED. Production metadata JSON verified bit-exact (`30c1c75d81...`).
- `test_04_stage54_partition_manifest_integrity`: PASSED. Stage 54 verified partition manifest intact (`10563efcd5...`).
- `test_05_stage60_sealed_manifest_integrity`: PASSED. Stage 60 sealed evaluation manifest intact (`9dfa4ced36...`).
- `test_06_stage61_dev_manifest_integrity`: PASSED. Stage 61 rolling window development manifest intact (`bdf27fdf66...`).
- `test_07_c5_combined_dsp_integrity`: PASSED. C5 combined DSP preprocessor intact (`d73cd3bf4d...`).
- `test_08_stage64_dual_resolution_checkpoint_integrity`: PASSED. Stage 64 dual resolution checkpoint intact (`4374c5e4ab...`).

### Category 2: Candidate 65-F & Sust_D Reproduction & Gate Scorecard (8 / 8 PASSED)
- `test_09_candidate_65f_exact_confusion_matrix`: PASSED. Candidate 65-F reproduces exact confusion matrix: $TP=184, FN=11, FP=7, TN=110$.
- `test_10_candidate_65f_gate1_recall`: PASSED. Candidate 65-F Gate 1 recall = 94.36% (verified failing Gate 1 $\ge 96.0\%$).
- `test_11_candidate_65f_gate2_fpr`: PASSED. Candidate 65-F Gate 2 FPR = 5.98% (verified failing Gate 2 $\le 5.0\%$).
- `test_12_candidate_65f_gate3_shouted_speech_fpr`: PASSED. Candidate 65-F Gate 3 shouted-speech FPR = 20.0% (verified failing Gate 3 $\le 15.0\%$).
- `test_13_candidate_65f_gate4_short_scream_recall`: PASSED. Candidate 65-F Gate 4 short-scream recall = 98.50% (verified passing Gate 4 $\ge 90.0\%$).
- `test_14_sust_d_exact_confusion_matrix`: PASSED. Sust_D reproduces exact confusion matrix: $TP=192, FN=3, FP=68, TN=49$.
- `test_15_sust_d_gate2_catastrophic_failure`: PASSED. Sust_D catastrophic Gate 2 failure confirmed (FPR = 58.12% vs threshold $\le 5.0\%$).
- `test_16_sust_d_gate3_catastrophic_failure`: PASSED. Sust_D 100% false alarm rate on shouted speech confirmed (5 / 5 triggered).

### Category 3: Candidate Comparison, McNemar Significance & Ranking (8 / 8 PASSED)
- `test_17_four_candidate_comparison_csv_exists`: PASSED. Master comparison table exists with all 4 models.
- `test_18_candidate_65f_highest_f1_score`: PASSED. Candidate 65-F achieves highest F1 score (0.9534) among all evaluated candidates.
- `test_19_mcnemar_test_candidate_65f_vs_baseline`: PASSED. Candidate 65-F is statistically superior to Baseline Dual-Resolution ($\chi^2 = 16.06, p < 0.001$).
- `test_20_mcnemar_test_candidate_65f_vs_variant6`: PASSED. Candidate 65-F is statistically superior to Variant 6 ($\chi^2 = 5.26, p = 0.0218$).
- `test_21_mcnemar_test_candidate_65f_vs_sust_d`: PASSED. Candidate 65-F is statistically superior to Sust_D in classification accuracy ($\chi^2 = 39.19, p < 0.0001$).
- `test_22_variant6_recall_destruction`: PASSED. Variant 6 destroys 13 screams (recall drops to 87.69%).
- `test_23_baseline_high_false_alarm_rate`: PASSED. Baseline produces 25 false alarms (FPR = 21.37%).
- `test_24_candidate_selection_ranks_65f_first`: PASSED. Multi-criteria selection ranks Candidate 65-F as Rank 1 lead model.

### Category 4: Dataset Expansion, Annotators & Short Screams (8 / 8 PASSED)
- `test_25_shouted_speech_dataset_size`: PASSED. Shouted-speech dataset contains 529 recordings (exceeding $\ge 120$ target).
- `test_26_shouted_speech_source_groups`: PASSED. Shouted-speech dataset contains 160 independent source groups (exceeding $\ge 80$ target).
- `test_27_shouted_speech_cohens_kappa`: PASSED. Multi-annotator agreement Cohen's $\kappa = 0.9547 \ge 0.850$.
- `test_28_shouted_speech_fleiss_kappa`: PASSED. Multi-annotator agreement Fleiss' $\kappa = 0.9547 \ge 0.850$.
- `test_29_hard_negative_expansion_manifest_content`: PASSED. Hard-negative expansion manifest contains 462 recordings across 375 source groups.
- `test_30_expanded_recordings_legal_licenses`: PASSED. 100% of expanded recordings possess verified open licenses (CC0 or CC-BY).
- `test_31_short_scream_cohort_count_and_durations`: PASSED. Short-scream cohort contains exactly 401 sub-second screams ($\le 1.000$s).
- `test_32_short_scream_zero_leakage_sealed_and_train`: PASSED. ZERO leakage confirmed between the 401 short screams and Stage 60 sealed cohort or Stage 54 train partition.

### Category 5: Latency, Preregistration, Governance & Safety (8 / 8 PASSED)
- `test_33_latency_gate5_compliance`: PASSED. Gate 5 Neural P95 latency is $\le 0.971$ ms across 1, 2, 4, 8 streams (threshold $\le 25.0$ ms).
- `test_34_frozen_checkpoint_exists_and_matches_hash`: PASSED. Frozen model checkpoint exists and matches SHA-256 (`06a98025db...`).
- `test_35_freeze_metadata_json_completeness`: PASSED. Freeze metadata JSON specifies all hyperparameters, suppression thresholds, and gate statuses.
- `test_36_preregistration_protocol_contains_checkpoint_hash`: PASSED. Preregistration protocol document contains the frozen checkpoint hash.
- `test_37_clustered_power_analysis_minimum_power`: PASSED. Clustered power analysis confirms all 4 gates achieve statistical power $\ge 89\%$ on the reconciled cohort.
- `test_38_authoritative_readiness_decision`: PASSED. Formal readiness verdict is strictly `NOT READY FOR INDEPENDENT EVALUATION`.
- `test_39_mandatory_safety_designation_leads_every_markdown_file`: PASSED. All markdown files in stage 8.9.66 lead with `# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.` on line 1.
- `test_40_zero_production_promotion_verified`: PASSED. Production classifier is verified unpromoted and identical to baseline.

