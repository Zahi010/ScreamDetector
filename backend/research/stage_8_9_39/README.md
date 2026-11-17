# Stage 8.9.39 — Controlled Retraining, Expanded Dataset Evaluation & Independent Generalization Audit

**Project:** Festival Scream Detector  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Stage Status:** Completed  
**Final Stage Decision:** `RETRAINING IMPROVED PERFORMANCE — INDEPENDENT EVIDENCE STILL INSUFFICIENT`

---

## 1. Directory Structure

```text
stage_8_9_39/
├── README.md                                    # This project directory roadmap
├── STAGE_PROGRESS.md                            # Execution milestone tracking log
├── cache/
│   └── stage_8_9_39_features.npz                # Extracted YAMNet, phonation, and subband features
├── checkpoints/
│   ├── config_b/
│   │   ├── best_model.pt                        # PyTorch weights for DualEncoderAcousticModel
│   │   └── platt_calibrator.joblib              # Fitted Platt scaling calibrator
│   └── config_d/
│       ├── best_model.pt                        # PyTorch weights for MultiPathwayFusionModel
│       └── platt_calibrator.joblib              # Fitted Platt scaling calibrator
├── config/
│   ├── feature_config.json                      # Feature extraction dimensions and cache checksum
│   └── threshold_config.json                    # Frozen validation-selected operating thresholds
├── plots/                                       # 12 publication-quality research figures
│   ├── 01_training_and_validation_loss_curves.png
│   ├── 02_validation_f1_vs_epoch.png
│   ├── 03_validation_pr_curves.png
│   ├── 04_validation_roc_curves.png
│   ├── 05_threshold_vs_recall_plots.png
│   ├── 06_threshold_vs_hard_negative_fpr_plots.png
│   ├── 07_threshold_vs_shouted_speech_fpr_plots.png
│   ├── 08_confusion_matrices.png
│   ├── 09_calibration_reliability_diagrams.png
│   ├── 10_category_level_false_positive_plots.png
│   ├── 11_historical_vs_expansion_benchmark_comparison.png
│   └── 12_latency_distribution_plots.png
├── predictions/
│   ├── expansion_test/                          # Predictions on v4_reserved_expansion_test (N=102)
│   ├── historical_test/                         # Predictions on v4_historical_test (N=293)
│   └── validation/                              # Predictions on v4_val (N=339)
├── reports/                                     # 9 comprehensive markdown research reports
│   ├── STAGE_8_9_39_FINAL_REPORT.md             # Master stage report with answers to 10 key questions
│   ├── CONFIG_B_TRAINING_REPORT.md              # Configuration B retraining and convergence audit
│   ├── CONFIG_D_TRAINING_REPORT.md              # Configuration D retraining and convergence audit
│   ├── THRESHOLD_AND_CALIBRATION_REPORT.md      # Validation threshold sweeps and Platt calibration
│   ├── HISTORICAL_BENCHMARK_REPORT.md           # Evaluation on v4_historical_test (View A & View B)
│   ├── EXPANSION_GENERALIZATION_REPORT.md       # Primary independent test on v4_reserved_expansion_test
│   ├── ERROR_ANALYSIS_REPORT.md                 # Failure mode breakdown and 44-clip human review queue
│   ├── LATENCY_REPORT.md                        # Computational latency and 100ms hop budget audit
│   └── PRODUCTION_INTEGRITY_REPORT.md           # Cryptographic SHA-256 verification of production freeze
├── results/
│   ├── audits/                                  # Pretraining integrity audit outputs
│   ├── calibration/                             # Calibration metrics and reliability diagram bins
│   ├── latency/                                 # Latency distributions and benchmarking summary
│   ├── metrics/                                 # Benchmark evaluation results and review queue
│   ├── thresholds/                              # Validation threshold sweeps and operating points
│   └── training/                                # Training histories and feature normalization stats
├── scripts/                                     # Reproducible execution scripts
│   ├── pretraining_integrity_audit.py
│   ├── extract_stage_8_9_39_features.py
│   ├── train_config_b.py
│   ├── train_config_d.py
│   ├── threshold_sweep.py
│   ├── calibration_audit.py
│   ├── evaluate_historical_test.py
│   ├── evaluate_expansion_test.py
│   ├── latency_benchmark.py
│   ├── error_analysis.py
│   ├── generate_all_plots.py
│   └── verify_production_freeze.py
└── tests/
    ├── test_stage_8_9_39.py                     # 15 automated unit tests
    └── test_results.txt                         # Test execution log (15 passed, 0 failed)
```

---

## 2. Key Results at a Glance

| Benchmark Cohort | Metric | Candidate B ($\theta = 0.24$) | Candidate D ($\theta = 0.34$) |
|---|---|---|---|
| **Reserved Expansion Test ($N=102$)** | Scream Recall | **100.0%** (65/65) [94.4%, 100.0%] | **100.0%** (65/65) [94.4%, 100.0%] |
| *(Primary Independent Test)* | Hard-Negative FPR | **0.0%** (0/37) [0.0%, 9.4%] | **0.0%** (0/37) [0.0%, 9.4%] |
| | Shouted-Speech FPR | **0.0%** (0/16) [0.0%, 19.4%] | **0.0%** (0/16) [0.0%, 19.4%] |
| | Short-Scream Recall | **100.0%** (65/65) [94.4%, 100.0%] | **100.0%** (65/65) [94.4%, 100.0%] |
| **Historical Test ($N=293$)** | View A Recall (Orig) | **87.25%** (89/102) [79.4%, 92.4%] | **83.33%** (85/102) [74.9%, 89.3%] |
| *(Cross-Stage Continuity)* | View B Recall (Adjud) | **89.00%** (89/100) [81.4%, 93.8%] | **85.00%** (85/100) [76.7%, 90.7%] |
| | View A Hard-Neg FPR | **12.04%** (23/191) [8.2%, 17.4%] | **13.09%** (25/191) [9.0%, 18.6%] |
| **Computational Latency** | CPU P95 Latency | **0.516 ms** (Gate limit: 25.0 ms) | **0.678 ms** (Gate limit: 25.0 ms) |

---

## 3. Mandatory Research Safety Notice

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
This software is an experimental machine learning prototype developed solely for acoustic research. It has not been evaluated, verified, or certified for life-critical, emergency, tactical dispatch, or personal protection deployments.

