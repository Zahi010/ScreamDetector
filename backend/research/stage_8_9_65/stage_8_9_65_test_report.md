# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Stage 8.9.65 Automated Verification Suite Test Report

## 1. Executive Summary

This report documents the formal execution of the **53-Test Automated Invariant Verification Suite** (`tests/test_stage_8_9_65.py`) for Stage 8.9.65.

The test suite validates architectural integrity, reproduction accuracy, gate definitions, data integrity, regression boundaries, and engineering limits.

### Overall Results
- **Test Suite Path:** `backend/research/stage_8_9_65/tests/test_stage_8_9_65.py`
- **Total Tests Executed:** 53
- **Passed:** 53
- **Failed:** 0
- **Pass Rate:** **100.0%**
- **Execution Runtime:** $4.34 \text{ s}$

---

## 2. Granular Category Breakdown

| Category # | Verification Category | Tests | Status | Key Properties Verified |
| :---: | :--- | :---: | :---: | :--- |
| **1** | **Gate Integrity & Definitions** | 1–8 | **8/8 PASSED** | Gate 1 ($\ge 96\%$), Gate 2 ($\le 5\%$), Gate 3 ($\le 15\%$ shouted FPR), Gate 4 ($\ge 90\%$ short recall), Gate 5 ($\le 25\text{ ms}$). Rejection of missing metrics, bad denominators, and mixed cohorts. |
| **2** | **Prediction & Asset Integrity** | 9–15 | **7/7 PASSED** | 21/21 protected assets bit-for-bit verified. Exact Baseline ($184, 11, 25, 92$) and Variant 6 ($171, 24, 5, 112$) reproduction. Exact 13 positive failures. McNemar significance ($p < 0.001$). |
| **3** | **Selective False-Positive Suppression** | 16–22 | **7/7 PASSED** | Candidates 65-A through 65-F evaluated. Candidate 65-F recovers 100% baseline recall ($94.36\%$), reduces FPs by $>70\%$ ($\text{FPR} \le 6.0\%$), and achieves top F1 ($0.9534$) and PR-AUC ($0.9785$). |
| **4** | **Sustained & Short Events** | 23–31 | **9/9 PASSED** | 6 sustained experiments verified. Short scream evaluation across all 401 recordings. Candidate 65-F achieves $96.51\%$ short recall and $99.16\%$ ultra-short recall. Gate 4 passes on all 7 horizons. |
| **5** | **Temporal Aggregation** | 32–36 | **5/5 PASSED** | All 7 aggregation strategies verified. Raw max achieves top recall ($94.36\%$), hysteresis achieves lowest FPR ($10.26\%$), Rolling EMA achieves top PR-AUC ($0.9632$). |
| **6** | **Dataset & Governance Integrity** | 37–44 | **8/8 PASSED** | Cohort strictly $N=312$ across 258 clusters. Clustered bootstrap ($B=2,000$) 95% CI lower bound for short screams exceeds $95.0\%$. $N=1,050$ future cohort achieves $>90\%$ power across all 4 gates. |
| **7** | **Engineering, Latency & Governance** | 45–53 | **9/9 PASSED** | Multi-stream latency profiled for 1, 2, 4, 8 streams (P95 $\le 0.931\text{ ms}$, Gate 5 PASS). Zero production promotion verified. Line 1 mandatory safety header verified on all markdown files. |

---

## 3. Test Invariant Traceability Matrix

```
Test 01: test_01_authoritative_gate1_definition ........................ PASSED
Test 02: test_02_authoritative_gate2_definition ........................ PASSED
Test 03: test_03_authoritative_gate3_definition ........................ PASSED
Test 04: test_04_authoritative_gate4_definition ........................ PASSED
Test 05: test_05_authoritative_gate5_definition ........................ PASSED
Test 06: test_06_scorecard_rejects_missing_metrics ..................... PASSED
Test 07: test_07_scorecard_rejects_inconsistent_denominators ........... PASSED
Test 08: test_08_scorecard_rejects_mixed_cohorts ....................... PASSED
Test 09: test_09_bit_level_hash_verification ........................... PASSED
Test 10: test_10_baseline_reproduction_confusion_matrix ................ PASSED
Test 11: test_11_variant6_reproduction_confusion_matrix ................ PASSED
Test 12: test_12_paired_prediction_transitions_consistency ............. PASSED
Test 13: test_13_positive_failure_inventory_count ...................... PASSED
Test 14: test_14_mcnemar_recall_degradation_significance ............... PASSED
Test 15: test_15_mcnemar_fpr_reduction_significance .................... PASSED
Test 16: test_16_selective_suppression_ablation_candidates_count ....... PASSED
Test 17: test_17_candidate_65f_recovers_baseline_recall ................ PASSED
Test 18: test_18_candidate_65f_false_positive_reduction ................ PASSED
Test 19: test_19_candidate_65f_recovers_all_13_v6_failures ............. PASSED
Test 20: test_20_candidate_65f_highest_f1_score ........................ PASSED
Test 21: test_21_candidate_65f_highest_pr_auc .......................... PASSED
Test 22: test_22_candidate_65f_whistle_false_positives_controlled ...... PASSED
Test 23: test_23_sustained_branch_ablation_file_exists ................. PASSED
Test 24: test_24_sust_d_confidence_or_recall_lift ...................... PASSED
Test 25: test_25_short_scream_cohort_sample_size ....................... PASSED
Test 26: test_26_candidate_65f_short_scream_recall ..................... PASSED
Test 27: test_27_candidate_65f_ultra_short_recall ...................... PASSED
Test 28: test_28_candidate_65f_passes_gate4_on_all_horizons ............ PASSED
Test 29: test_29_net_recall_gain_over_variant6 ......................... PASSED
Test 30: test_30_gating_weight_correlation_with_duration ............... PASSED
Test 31: test_31_threshold_calibration_sweep_coverage .................. PASSED
Test 32: test_32_event_aggregation_file_exists ......................... PASSED
Test 33: test_33_raw_window_highest_sensitivity ........................ PASSED
Test 34: test_34_asymmetric_hysteresis_lowest_fpr ...................... PASSED
Test 35: test_35_rolling_ema_highest_pr_auc ............................ PASSED
Test 36: test_36_method_f_full_stack_f1 ................................ PASSED
Test 37: test_37_development_cohort_denominators ....................... PASSED
Test 38: test_38_development_cohort_unique_source_groups ............... PASSED
Test 39: test_39_clustered_bootstrap_metrics_file_exists ............... PASSED
Test 40: test_40_clustered_bootstrap_short_scream_ci ................... PASSED
Test 41: test_41_shouted_speech_diagnostic_sample_size ................. PASSED
Test 42: test_42_future_evaluation_power_analysis_exists ............... PASSED
Test 43: test_43_future_evaluation_sample_size ......................... PASSED
Test 44: test_44_future_evaluation_statistical_power ................... PASSED
Test 45: test_45_latency_benchmarks_file_exists ........................ PASSED
Test 46: test_46_model_only_neural_p95_latency ......................... PASSED
Test 47: test_47_gate5_pass_flag_true .................................. PASSED
Test 48: test_48_complete_pipeline_p95_latency ......................... PASSED
Test 49: test_49_memory_rss_bounded .................................... PASSED
Test 50: test_50_zero_production_promotion ............................. PASSED
Test 51: test_51_mandatory_safety_designation_on_line1 ................. PASSED
Test 52: test_52_scorecard_rejects_missing_gate3_definition ............ PASSED
Test 53: test_53_no_life_safety_claims ................................. PASSED
```

---

## 4. Final Verification Statement

The entire Stage 8.9.65 implementation has undergone rigorous, automated regression verification. All 53 assertions hold true, confirming bit-level reproducibility, gate integrity, and zero drift.

---

## 5. Artifact Links
- Test Suite Script: [test_stage_8_9_65.py](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/tests/test_stage_8_9_65.py)
- Final Stage Report: [final_stage_report.md](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/final_stage_report.md)

