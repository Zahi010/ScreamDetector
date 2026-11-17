# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.66 RESEARCH SUITE
**Independent Evaluation Readiness, Candidate Generalization Audit & Final Model Freeze**

## 1. Safety Designation
Non-certified acoustic research prototype. Prohibited for life-safety use, emergency alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

All tests utilize legally acquired recorded audio files and safe playback protocols only.

---

## 2. Directory Map & Quick Navigation

```
backend/research/stage_8_9_66/
├── STAGE_PROGRESS.md                            <- Live status ledger of all 8 tracks
├── README.md                                    <- This navigational overview
├── artifact_hash_audit.md                       <- Bit-exact verification of 21 baseline assets
├── artifact_hashes.json                         <- Cryptographic manifest of protected baselines
├── repository_inventory.md                      <- Full directory and asset catalog
│
├── candidate_65f_reproduction.md                <- Track A: Candidate 65-F reproduction report
├── candidate_65f_predictions.csv                <- Track A: Per-recording predictions (N=312)
│
├── sust_d_complete_evaluation.md                <- Track B: Sust_D complete audit report
├── sust_d_confusion_matrix.csv                  <- Track B: Sust_D confusion matrix & gates
├── sust_d_fusion_analysis.md                    <- Track B: Mathematical analysis of Soft-OR
├── sust_d_predictions.csv                       <- Track B: Per-recording predictions (N=312)
│
├── four_candidate_comparison.md                 <- Track C: Head-to-head comparison & McNemar tests
├── four_candidate_comparison.csv                <- Track C: Master performance scorecard
│
├── shouted_speech_acquisition_report.md         <- Track D: Shouted-speech dataset expansion report
├── shouted_speech_manifest.csv                  <- Track D: 529 shouted-speech files (160 source groups)
├── shouted_speech_annotation_records.csv        <- Track D: Multi-annotator agreement records
├── shouted_speech_annotation_report.md          <- Track D: Cohen's & Fleiss' kappa reliability report
├── hard_negative_expansion_manifest.csv         <- Track D: 462 hard-negative files (375 source groups)
├── hard_negative_expansion_report.md            <- Track D: Whistle, cheer, and tone diversity report
│
├── short_scream_partition_audit.md              <- Track E: Lineage and zero-leakage audit (401 screams)
├── short_scream_duration_audit.md               <- Track E: Sub-second duration stratum report
├── short_scream_partition_audit.csv             <- Track E: 401 short-scream partition records
│
├── evaluation_cohort_history_audit.md           <- Track F: Historical audit of cohort allocations
├── evaluation_sample_size_reanalysis.md         <- Track F: Clustered power analysis report
├── final_evaluation_design_proposal.md          <- Track F: Reconciled N=1,050 evaluation specification
├── evaluation_cohort_allocation.csv             <- Track F: Stratification table across designs
├── sample_size_sensitivity_analysis.csv         <- Track F: Power sweep across cluster sizes & ICC
│
├── candidate_selection_report.md                <- Track G: Multi-criteria ranking and selection
├── candidate_freeze_report.md                   <- Track G: Checkpoint locking and serialization
├── future_evaluation_preregistration.md         <- Track G: Preregistration protocol and frozen hash
├── independent_evaluation_readiness_report.md   <- Track H: Formal readiness verdict (NOT READY)
│
├── latency_benchmarks.csv                       <- Multi-stream latency benchmarks (1, 2, 4, 8 streams)
├── latency_and_engineering_report.md            <- Gate 5 engineering certification report
│
├── models/
│   ├── candidate_65f_frozen.pt                  <- Frozen PyTorch model checkpoint
│   └── candidate_freeze_metadata.json           <- Hyperparameter and metadata record
│
├── scripts/
│   ├── verify_artifact_hashes.py                <- 21-asset integrity verification
│   ├── reproduce_candidate_65f.py               <- Candidate 65-F reproduction
│   ├── reproduce_sust_d.py                      <- Sust_D complete audit
│   ├── compare_four_candidates.py               <- 4-candidate benchmark & McNemar
│   ├── audit_shouted_speech_data.py             <- Track D dataset expansion & agreement
│   ├── audit_short_scream_partitions.py         <- Track E short scream audit
│   ├── audit_evaluation_cohort_history.py       <- Track F cohort history
│   ├── run_clustered_power_analysis.py          <- Track F clustered power sweep
│   ├── select_evaluation_candidate.py           <- Track G candidate selection
│   ├── freeze_evaluation_candidate.py           <- Track G model freeze
│   ├── verify_preregistration.py                <- Track G preregistration verification
│   └── run_latency_benchmarks.py                <- Multi-stream latency benchmark
│
└── tests/
    └── test_stage_8_9_66.py                     <- 40-test automated verification suite
```

---

## 3. Executive Findings

1. **Reproduction Confirmed:** Candidate 65-F reproduces bit-for-bit ($TP=184, FN=11, FP=7, TN=110, F1=0.9534$).
2. **Sust_D Rejection:** Sust_D achieves 98.46% recall via Soft-OR fusion, but collapses in specificity with 58.12% FPR and 100% shouted-speech FPR.
3. **Dataset Expansion:** Assembled 529 shouted-speech files (160 source groups, $\kappa=0.9547$) and 462 hard negatives (375 source groups).
4. **Short Screams Zero Leakage:** The 401 short screams have 0% overlap with the Stage 60 sealed cohort and Stage 54 train partition.
5. **Readiness Verdict:** `NOT READY FOR INDEPENDENT EVALUATION` due to narrow development gate misses (Gate 1 Recall 94.36% vs 96.00%, Gate 2 FPR 5.98% vs 5.00%, Gate 3 Shouted FPR 20.0% vs 15.0%).

