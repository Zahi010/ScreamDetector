# Stage 8.9.54: Candidate E Expanded-Data Retraining, Controlled Ablations & Generalization Preparation

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.  
> No live-fire experiments, autonomous emergency dispatch, external emergency alerts, or claims of life-safety efficacy.  
> No production promotion is authorized.

---

## 1. Directory Structure

```text
stage_8_9_54/
├── README.md                                    # Stage overview and directory map
├── STAGE_PROGRESS.md                            # Milestone execution log
├── final_stage_report.md                        # Master technical stage report
├── dataset/
│   ├── dataset_integrity_report.md              # SG discrepancy investigation and partition topology
│   ├── source_group_reconciliation.csv          # 693 source groups classified across splits
│   ├── partition_manifest_verified.csv          # 1,732 authentic verified recordings
│   └── license_audit.md                         # 100% commercial-permissive licensing audit
├── baseline/
│   └── original_candidate_e_reproduction.md     # 120/120 bit-for-bit reproduction of original model
├── training/
│   ├── training_configuration.json              # Checkpoint metadata, seeds, and hyperparameters
│   ├── training_history.csv                     # Epoch-by-epoch loss and accuracy metrics
│   ├── candidate_e_v954_baseline.pt             # E0: Expanded baseline model
│   ├── candidate_e_v954_weighted.pt             # E1: Class-balanced model (Best Model)
│   ├── candidate_e_v954_augmented.pt            # E2: Acoustic augmented model
│   └── candidate_e_v954_combined.pt             # E3: Combined weighted + augmented model
├── evaluation/
│   ├── validation_predictions.csv               # 311 recording-level predictions across all 7 models
│   ├── threshold_sweep.csv                      # Threshold sweeps on expansion_val
│   ├── candidate_comparison.md                  # Comprehensive multi-candidate performance matrix
│   ├── subgroup_evaluation.md                   # Breakdown across 16 acoustic subgroups
│   ├── error_analysis.md                        # False positive and false negative case studies
│   └── acceptance_gate_report.md                # Gate compliance on validation data
├── performance/
│   ├── latency_report.md                        # Four-regime latency and throughput audit
│   └── runtime_profile.csv                      # Model and DSP execution percentiles
├── integrity/
│   ├── artifact_hash_audit.md                   # Cryptographic hashes of all 10 checkpoints/artifacts
│   ├── checkpoint_manifest.json                 # JSON manifest of trained checkpoints
│   └── historical_test_isolation.md             # Quarantine of Stage 8.9.53 cohort and Stage 8.9.55 plan
├── tests/
│   ├── test_stage_8_9_54.py                     # 15-test automated regression and verification suite
│   └── stage_8_9_54_test_report.md              # Pytest report (15/15 passed)
├── scripts/
│   ├── reconcile_source_groups.py               # Phase A discrepancy resolution
│   ├── reproduce_original_candidate_e.py        # Phase B bit-for-bit baseline reproduction
│   ├── extract_expansion_train_val_features.py  # Feature extraction for 1,366 recordings
│   ├── train_candidate_e_experiments.py         # E0-E3 retraining, threshold sweep, evaluation
│   └── benchmark_latency.py                     # Latency and runtime profiling
└── features/
    ├── expansion_train_features.npz             # 1,055 training feature tensors
    └── expansion_val_features.npz               # 311 validation feature tensors
```

---

## 2. Headline Results on `expansion_val` (N=311)

| Model Condition | Threshold $\theta$ | Scream Recall | Hard-Negative FPR | Precision | F1 Score | PR-AUC | ROC-AUC |
|---|---|---|---|---|---|---|---|
| **Candidate E (Original)** | `0.4000` | 76.77% (76/99) | 11.79% (25/212) | 75.25% | 76.00% | 0.7040 | 0.8794 |
| **Candidate E0 (Baseline)** | `0.6900` | 79.80% (79/99) | 4.72% (10/212) | 88.76% | 84.04% | 0.9120 | 0.9658 |
| **Candidate E1 (Weighted)** | `0.6800` | **82.83%** (82/99) | **4.72%** (10/212) | **89.13%** | **85.86%** | **0.9224** | **0.9670** |
| **Candidate E2 (Augmented)**| `0.6700` | 77.78% (77/99) | 4.72% (10/212) | 88.51% | 82.80% | 0.9081 | 0.9618 |
| **Candidate E3 (Combined)** | `0.8900` | 78.79% (78/99) | 4.72% (10/212) | 88.64% | 83.42% | 0.9060 | 0.9659 |
| **Candidate B Baseline** | `0.8000` | **83.84%** (83/99) | 5.19% (11/212) | 88.30% | 86.01% | 0.9197 | 0.9653 |
| **Candidate B + Interv D** | `0.8000` | 82.83% (82/99) | 5.19% (11/212) | 88.17% | 85.42% | 0.9197 | 0.9653 |

---

## 3. Governance Conclusion
- **Sanctioned Decision:** **`EXPANDED-DATA TRAINING IMPROVED CANDIDATE E — INDEPENDENT TEST PENDING`**
- Training on the 1,055 authentic expansion clips solved Candidate E's small-sample overfitting, cutting validation false alarms from 11.79% to 4.72% while boosting PR-AUC from 0.7040 to 0.9224.
- However, independent generalization is unverified until tested on a brand-new independent test cohort (Stage 8.9.55).
- All production and baseline artifacts remain **100% frozen**.

