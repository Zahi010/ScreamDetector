# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.69 RESEARCH DIRECTORY

**Mandatory Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
Non-certified experimental acoustic research system. Not for emergency detection, autonomous dispatch, or critical security deployment.

---

## Directory Overview

This directory contains all research code, models, reports, and tests developed for **Stage 8.9.69**: "Noise-Robust Scream Representation, Residual False-Negative Recovery & Independent Generalization Audit".

### Structure
```
backend/research/stage_8_9_69/
├── README.md                                 # This file
├── artifact_hashes.json                      # Cryptographic SHA-256 hashes
├── artifact_hashes.sha256                    # Checksums in standard format
├── false_negative_forensic_analysis.csv      # Forensic analysis of Candidate 68-D false negatives (25 clips)
├── stage68_ablation_audit.csv                # Recording-level audit of Stage 68 ablation discrepancy (311 clips)
├── experiment_configurations/                # Tournament experiment configs (69-A, 69-B, 69-C, 69-D)
│   ├── candidate_69a_config.json
│   ├── candidate_69b_config.json
│   ├── candidate_69c_config.json
│   └── candidate_69d_config.json
├── models/                                   # Model checkpoints & metadata
│   ├── candidate_69_frozen.pt               # Champion model checkpoint (SHA-256: d468b75...)
│   └── candidate_69_metadata.json            # Model parameters and evaluation metrics
├── reports/                                  # Research analysis and evaluation reports
│   ├── candidate_comparison.csv              # Tournament metrics table
│   ├── candidate_69_val_predictions.csv      # Recording-level predictions on N=311 validation cohort
│   ├── dataset_manifest_audit.md             # Data independence and exposure classification
│   ├── gate_evaluation.md                    # Five-Gate scorecard with 95% bootstrap CIs
│   ├── latency_benchmark.md                  # Single-stream and 8-stream CPU latency benchmarks
│   ├── stage_8_9_69_completion_report.md     # Comprehensive stage completion report
│   ├── reproducibility_instructions.md       # Step-by-step reproduction guide
│   └── test_results.md                       # Automated test suite results (25/25 passed)
├── scripts/                                  # Execution & verification scripts
│   ├── train_and_evaluate_stage69.py         # Main tournament evaluation & checkpoint freezer
│   └── verify_artifact_hashes.py             # Hash verification utility
└── tests/                                    # Automated pytest suite
    └── test_stage_8_9_69.py                  # 25 comprehensive unit and integration tests
```

---

## Champion Model Summary: Candidate 69-D

- **Operating Threshold:** $\theta = 0.4920$
- **Recall:** 79.80% (79/99, recovers +5 screams over Candidate 68-D)
- **Shouted-Speech FPR:** 13.64% (12/88, strictly satisfies Gate 3 $\le 15.0\%$)
- **Hard-Negative FPR:** 8.06% (10/124)
- **Short-Scream Recall:** 92.31% (36/39, strictly satisfies Gate 4 $\ge 90.0\%$)
- **CPU P95 Latency:** 0.384 ms (single stream, strictly satisfies Gate 5 $\le 25.0$ ms)
- **Final Verdict:** `PARTIAL IMPROVEMENT — ONE OR MORE GATES FAILED` (Gates 1 & 2 remain failed).

