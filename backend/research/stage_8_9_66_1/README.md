# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.66.1 — CANDIDATE 65-F DATA PROVENANCE AUDIT, UNSEEN-DATA VERIFICATION & INDEPENDENT EVALUATION READINESS

## 1. Safety Designation
Non-certified acoustic research prototype. Prohibited for life-safety alerting, emergency dispatch, autonomous external response, police notification, active-shooter alerting, or critical security deployment.

All experiments utilize legally acquired recorded audio files and safe playback protocols only.

---

## 2. Executive Overview

Stage 8.9.66.1 is a **strictly audit-only stage**. It investigates whether Candidate 65-F's reported performance in Stage 8.9.66 represents genuine generalization to previously unseen recordings and source groups or whether it is a development benchmark result.

### Authoritative Final Verdicts:
- **Lineage Classification:** **OPTION B — HISTORICAL DEVELOPMENT RESULTS ONLY**  
  Candidate 65-F was trained directly on the $N=312$ development cohort, its threshold $\tau=0.48$ was tuned on it, and its selective suppression heuristics were designed specifically against false alarms within that cohort.
- **Evaluation Readiness:** **NOT READY FOR INDEPENDENT EVALUATION**  
  Controlled frozen inference on $N=111$ verified out-of-development shouted-speech files revealed an empirical false positive rate of **44.14% (49 / 111)** (95% CI: **[35.26%, 53.42%]**). This represents a catastrophic failure of **Gate 3** (allowable $\le 15.00\%$, excess of **+29.14%**). The sealed cohort remains 100% locked to prevent expenditure of irreplaceable evaluation assets on an unready candidate.

---

## 3. Directory Layout

```
stage_8_9_66_1/
├── STAGE_PROGRESS.md                               # Stage progress and track status ledger
├── README.md                                       # Directory documentation and guide
├── artifact_hashes.json                            # Cryptographic baseline hash record
├── reports/
│   ├── stage_8_9_66_1_completion_report.md         # Master Stage Completion Report
│   ├── stage_8_9_66_1_candidate_provenance_audit.md# Sub-stage 8.9.66.1.2: Lineage reconstruction
│   ├── stage_8_9_66_1_n312_cohort_classification.md# Sub-stage 8.9.66.1.3: N=312 role categorization
│   ├── stage_8_9_66_1_source_group_leakage_audit.md# Sub-stage 8.9.66.1.4: Source group overlap matrix
│   ├── stage_8_9_66_1_expanded_negative_provenance.md# Sub-stage 8.9.66.1.5: Exposure & frozen inference
│   ├── stage_8_9_66_1_sealed_cohort_integrity.md   # Sub-stage 8.9.66.1.6: Sealed cohort governance
│   ├── stage_8_9_66_1_candidate_artifact_integrity.md# Sub-stage 8.9.66.1.7: Cryptographic audit
│   ├── stage_8_9_66_1_independent_evaluation_readiness.md# Sub-stage 8.9.66.1.8: Readiness decision
│   ├── stage_8_9_66_1_test_report.md               # 30-test automated verification test report
│   ├── artifact_inventory.csv                      # Complete 36-artifact cryptographic inventory
│   ├── recording_source_group_overlap_matrix.csv   # Pairwise recording & source-group overlap matrix
│   ├── dataset_exposure_classification.csv         # Exposure audit for 991 negative recordings
│   ├── candidate_65f_checkpoint_hash_record.json   # Candidate 65-F parameter & checkpoint ledger
│   └── frozen_inference_shouted_speech_predictions.csv # Predictions on 111 unseen shouted speech files
├── scripts/
│   ├── build_artifact_inventory.py                 # Catalogs repository artifacts and calculates SHA-256
│   ├── verify_artifact_hashes.py                   # Verifies bit-for-bit integrity of protected baselines
│   └── run_stage_8_9_66_1_audits.py                # Executes overlap analysis, exposure classification, & inference
└── tests/
    └── test_stage_8_9_66_1.py                      # 30-test automated pytest verification suite
```

---

## 4. Key Documents & Artifact Links

- **Master Completion Report:** [`reports/stage_8_9_66_1_completion_report.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_66_1/reports/stage_8_9_66_1_completion_report.md)
- **Independent Evaluation Readiness Assessment:** [`reports/stage_8_9_66_1_independent_evaluation_readiness.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_66_1/reports/stage_8_9_66_1_independent_evaluation_readiness.md)
- **Unseen Shouted-Speech Predictions:** [`reports/frozen_inference_shouted_speech_predictions.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_66_1/reports/frozen_inference_shouted_speech_predictions.csv)
- **Exposure Classification:** [`reports/dataset_exposure_classification.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_66_1/reports/dataset_exposure_classification.csv)
- **Pairwise Overlap Matrix:** [`reports/recording_source_group_overlap_matrix.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_66_1/reports/recording_source_group_overlap_matrix.csv)
- **Automated Verification Test Suite:** [`tests/test_stage_8_9_66_1.py`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_66_1/tests/test_stage_8_9_66_1.py)

