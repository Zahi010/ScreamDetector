# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.66 — REPOSITORY INVENTORY
**Inventory of Datasets, Checkpoints, Manifests, and Code Assets**

## 1. Safety Designation
Non-certified acoustic research prototype. Prohibited for life-safety use, autonomous dispatch, emergency alerting, or live-fire testing.

---

## 2. Inventory by Category

### A. Protected Baseline Models and Production Assets
- `backend/models/scream_classifier.joblib`: Production baseline classifier (RandomForest 5-feature baseline).
- `backend/models/model_metadata.json`: Production baseline feature thresholds and hyperparameters.
- `backend/reports/test_predictions.csv`: Production baseline test cohort predictions (N=105).
- `backend/research/stage_8_9_54/training/candidate_e_v954_weighted.pt`: Single-resolution Candidate E1 neural network checkpoint.
- `backend/research/stage_8_9_44/models/config_b_mask.pt`: Candidate B acoustic mask model checkpoint.
- `backend/research/stage_8_9_64/models/stage63_dual_resolution_gated.pt`: Dual-resolution gated model checkpoint.

### B. DSP and Feature Extraction Assets
- `backend/research/stage_8_9_57/dsp_implementations/c5_combined.py`: Bit-exact optimized C5 subband and phonation DSP module.
- `backend/research/stage_8_9_49/scripts/whistle_discriminator.py`: Narrow-band tonal and whistle discriminator.

### C. Historical Cohort Manifests
- `backend/research/stage_8_9_54/dataset/partition_manifest_verified.csv`: Stage 54 3-way partition manifest.
- `backend/research/stage_8_9_60/future_evaluation_manifest.json`: Stage 60 sealed evaluation cohort manifest (N=700).
- `backend/research/stage_8_9_60/duplicate_and_excerpt_relationships.csv`: Stage 60 duplicate recording audit records.
- `backend/research/stage_8_9_61/rolling_window_development_manifest.csv`: Stage 61 development cohort manifest (N=312).
- `backend/research/stage_8_9_63/stage_63_development_manifest.csv`: Stage 63 development manifest (N=312).
- `backend/research/stage_8_9_63/short_scream_acquisition_manifest.csv`: Stage 63 short-scream acquisition manifest.
- `backend/research/stage_8_9_64/stage_64_short_scream_manifest.csv`: Stage 64 401 short-scream manifest.

### D. Stage 8.9.66 Research Pipeline Scripts
- `scripts/verify_artifact_hashes.py`: Cryptographic hash verification of 21 protected baseline assets.
- `scripts/reproduce_candidate_65f.py`: Exact reproduction and gate assessment of Candidate 65-F.
- `scripts/reproduce_sust_d.py`: Complete evaluation and gate assessment of Sust_D with Soft-OR fusion.
- `scripts/compare_four_candidates.py`: Four-candidate head-to-head comparison and McNemar tests.
- `scripts/audit_shouted_speech_data.py`: Shouted-speech dataset expansion and hard negative audit.
- `scripts/audit_short_scream_partitions.py`: Partition history, creator overlap, and duration audit of 401 short screams.
- `scripts/audit_evaluation_cohort_history.py`: Historical audit of 240/810 vs 550/500 cohort designs.
- `scripts/run_clustered_power_analysis.py`: Clustered statistical power analysis with intra-cluster correlation.
- `scripts/select_evaluation_candidate.py`: Selection protocol for the lead candidate.
- `scripts/freeze_evaluation_candidate.py`: Model checkpoint freezing and metadata serialization.
- `scripts/verify_preregistration.py`: Verification of preregistration compliance.
- `scripts/run_latency_benchmarks.py`: Multithreaded neural-only latency benchmarking (1, 2, 4, 8 streams).
- `tests/test_stage_8_9_66.py`: 40-test automated pytest verification suite.

---

## 3. Storage and Directory Map
```
backend/research/stage_8_9_66/
├── STAGE_PROGRESS.md
├── artifact_hash_audit.md
├── repository_inventory.md
├── artifact_hashes.json
├── models/
│   ├── candidate_65f_frozen.pt
│   └── candidate_freeze_metadata.json
├── scripts/
│   ├── verify_artifact_hashes.py
│   ├── reproduce_candidate_65f.py
│   ├── reproduce_sust_d.py
│   ├── compare_four_candidates.py
│   ├── audit_shouted_speech_data.py
│   ├── audit_short_scream_partitions.py
│   ├── audit_evaluation_cohort_history.py
│   ├── run_clustered_power_analysis.py
│   ├── select_evaluation_candidate.py
│   ├── freeze_evaluation_candidate.py
│   ├── verify_preregistration.py
│   └── run_latency_benchmarks.py
└── tests/
    └── test_stage_8_9_66.py
```

