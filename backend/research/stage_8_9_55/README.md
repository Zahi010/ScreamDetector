# Stage 8.9.55: Fresh Independent Cohort Acquisition, Blind Evaluation & Candidate E1 vs Candidate B

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.  
> No live-fire experiments, autonomous emergency dispatch, external emergency alerts, or claims of life-safety efficacy.  
> No production promotion is authorized.

---

## 1. Directory Structure

```text
stage_8_9_55/
├── README.md                                    # Stage overview and directory map
├── STAGE_PROGRESS.md                            # Milestone execution log
├── final_stage_report.md                        # Master technical stage report
├── dataset/
│   ├── acquisition_manifest.csv                 # 450 newly acquired authentic recordings
│   ├── license_audit.csv                        # 100% CC0 / CC-BY commercial license audit
│   ├── label_adjudication.csv                   # Ground-truth taxonomy and adjudication audit
│   ├── label_quality_report.md                  # Inter-rater concordance and quality report
│   └── source_diversity_report.md               # 246 independent source groups breakdown
├── integrity/
│   ├── historical_exclusion_registry.csv        # 2,213 historical exclusions across prior stages
│   ├── historical_cohort_isolation_report.md    # Cryptographic isolation verification report
│   ├── frozen_test_manifest.json                # Cryptographically locked test cohort manifest
│   ├── preregistered_evaluation_config.json     # Pre-registered model operating points and gates
│   └── artifact_hash_audit.md                   # Cryptographic verification of protected assets
├── evaluation/
│   ├── candidate_e1_predictions.csv             # 450 recording predictions for Candidate E1 (theta=0.6800)
│   ├── candidate_b_predictions.csv              # 450 recording predictions for Candidate B (theta=0.8000)
│   ├── candidate_b_intervention_d_predictions.csv # 450 predictions for Candidate B + Intervention D
│   ├── independent_evaluation_report.md         # Primary classification metrics and findings
│   ├── subgroup_evaluation.md                   # Breakdown across 17 positive/negative subgroups
│   ├── paired_comparison.md                     # McNemar's test & 2,000-replicate cluster bootstrap
│   └── acceptance_gate_report.md                # 5-gate compliance audit on independent cohort
├── performance/
│   ├── latency_report.md                        # Four-regime latency and multi-stream throughput
│   └── runtime_profile.csv                      # Component execution percentiles and heap memory
├── tests/
│   ├── test_stage_8_9_55.py                     # 7-suite automated regression test suite
│   └── stage_8_9_55_test_report.md              # Test execution log (7/7 passed in 0.65s)
├── scripts/
│   ├── build_historical_exclusion_registry.py   # Phase A exclusion registry compilation
│   ├── curate_stage_8_9_55_cohort.py            # Phase B-E curation, adjudication & manifest freeze
│   ├── extract_stage_8_9_55_features.py         # Phase F YAMNet & subband feature extraction
│   ├── run_blind_evaluation.py                  # Phase F-J blind evaluation & bootstrap analysis
│   └── benchmark_latency.py                     # Phase K computational latency audit
└── features/
    └── stage_8_9_55_features.npz                # 450 feature tensors (1024-d, 6-d, 11-d)
```

---

## 2. Core Research Results Summary

| Model Under Evaluation | Operating Threshold | Scream Recall | Hard-Negative FPR | F1-Score | ROC-AUC | PR-AUC |
|---|---|---|---|---|---|---|
| **Candidate E1** (`candidate_e_v954_weighted.pt`) | $\theta = 0.6800$ | **72.67%** (109/150) | **6.33%** (19/300) | **78.42%** | **0.9201** | **0.8716** |
| **Candidate B** (`config_b_mask.pt`) | $\theta = 0.8000$ | **55.33%** (83/150) | **6.67%** (20/300) | **65.61%** | **0.8907** | **0.8139** |
| **Candidate B + Intervention D** | $\theta = 0.8000$ | **53.33%** (80/150) | **6.67%** (20/300) | **64.00%** | **0.8907** | **0.8139** |

- **Paired Superiority:** Candidate E1 achieved a **+17.33% recall margin** over Candidate B ($p = 0.00015$, 95% Cluster Bootstrap CI: **[+10.96%, +25.00%]**).
- **Sanctioned Verdict:** `CANDIDATE E1 INDEPENDENT GENERALIZATION SUPPORTED` (Both candidates fail strict operational acceptance gates).
- **Production Classifier:** Locked at $\theta = 0.3500$, SHA-256: `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f`.

