# Stage 8.9.53: Candidate E Independent Evaluation, Subgroup Robustness & Research Acceptance Audit

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.  
> No live-fire experiments, autonomous emergency dispatch, external emergency alerts, or claims of life-safety efficacy.  
> No production promotion is authorized.

---

## 1. Directory Structure

```text
stage_8_9_53/
├── README.md                                        # Stage guide and directory map
├── STAGE_PROGRESS.md                                # Milestone tracking and execution log
├── final_stage_report.md                            # Comprehensive technical stage report
├── evaluation/
│   ├── reserved_test_audit.md                       # Phase A: Physical and statistical audit of test cohort
│   ├── reserved_test_manifest_verified.csv          # Phase A: 366 verified evaluation records
│   ├── candidate_e_independent_predictions.csv      # Phase B: 366 raw predictions for Candidate E
│   ├── candidate_e_independent_evaluation.md       # Phase C: Full metrics, CIs, and gate status
│   ├── reference_model_comparison.md               # Phase D: Candidate E vs Candidate B vs Interv D
│   └── source_group_statistics.md                   # Phase D: Cluster bootstrap resampling (1,000 iter)
├── error_analysis/
│   ├── false_negatives.csv                          # Phase E: 38 missed screams forensic records
│   ├── false_positives.csv                          # Phase E: 43 false alarms forensic records
│   ├── subgroup_error_analysis.md                   # Phase E: Acoustic failure taxonomies
│   └── acoustic_association_analysis.md             # Phase E: Statistical and physical attribution
├── performance/
│   ├── latency_report.md                            # Phase F: Four-regime latency and throughput audit
│   └── runtime_profile.csv                          # Phase F: Benchmarked execution percentiles
├── integrity/
│   ├── artifact_hash_audit.md                       # Pre-evaluation freeze hash audit (6 artifacts)
│   ├── checkpoint_verification.md                   # Architecture and checkpoint verification
│   └── test_cohort_integrity.md                     # Source-group isolation and duplicate audit
├── tests/
│   ├── test_stage_8_9_53.py                         # 12-test automated regression and verification suite
│   └── stage_8_9_53_test_report.md                  # Test execution logs (12/12 passed)
├── scripts/
│   ├── verify_integrity_and_freezes.py              # Cryptographic and split isolation verification
│   ├── audit_reserved_test_cohort.py                # Physical decoding and manifest validation
│   ├── extract_reserved_test_features.py            # YAMNet & subband DSP feature extraction
│   ├── evaluate_candidate_e_and_baselines.py        # Complete inference, bootstrap, and statistical tests
│   └── benchmark_runtime_latency.py                 # Latency, memory, and scaling benchmarks
└── features/
    └── reserved_test_features.npz                   # Extracted 1024-d, 6-d, and 11-d feature tensors
```

---

## 2. Headline Results Summary

| Model | Operating Threshold | Scream Recall | Hard-Negative FPR | F1 Score | McNemar vs Baseline | Gate Compliance |
|---|---|---|---|---|---|---|
| **Candidate E** | $\theta = 0.4000$ | **62.75%** (64/102) | **16.29%** (43/264) | **61.24%** | $\chi^2 = 28.21, p < 0.0001$ | **FAILS (3 of 5)** |
| **Candidate B Baseline** | $\theta = 0.8000$ | **71.57%** (73/102) | **1.89%** (5/264) | **81.11%** | Baseline | **FAILS Gate 1, 4** |
| **Candidate B + Interv D**| $\theta = 0.8000$ | **71.57%** (73/102) | **1.89%** (5/264) | **81.11%** | $p = 1.000$ | **FAILS Gate 1, 4** |

---

## 3. Governance Conclusion
- **Sanctioned Decision:** `CANDIDATE E GENERALIZATION NOT SUPPORTED`
- Candidate E exhibited severe validation overfitting on its small development set ($N=200$). When exposed to the genuinely untouched independent cohort ($N=366$), recall dropped to 62.75% and HN-FPR surged to 16.29%. Candidate B demonstrated superior generalizability across both recall and false positive rejection.
- Production classifier remains **100% frozen** at Stage 5 Logistic Regression ($\theta = 0.3500$).

