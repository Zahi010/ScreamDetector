# Stage 8.9.43 — Authentic Positive-Class Dataset Expansion, Acoustic Domain-Shift Analysis & Controlled Model Retraining

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe playback protocols only.

---

## 1. Directory Structure

```
backend/research/stage_8_9_43/
├── ACQUISITION_PROVENANCE.csv             # Provenance, URLs, and licenses for 191 authentic screams
├── ANNOTATION_REVIEW.csv                  # Reviewer verification and consensus decisions
├── AUGMENTATION_EXPERIMENTS.csv           # 4-condition augmentation study metrics
├── CANDIDATE_COMPARISON_V5.csv            # Final comparison across all 4 candidates and 2 test splits
├── POSITIVE_DATASET_AUDIT.csv             # 15 acoustic features extracted from 495 positive clips
├── README.md                              # This file
├── STAGE_PROGRESS.md                      # Complete 10-phase milestone checklist and tracking
├── acquisition/                           # Raw acquisition manifests and query scripts
├── annotation/                            # Adjudication logs
├── audio/                                 # Normalized 16 kHz WAV audio files
│   └── positive/                          # 191 newly acquired authentic scream WAVs
├── augmentation/                          # Augmentation study config and summary
│   └── augmentation_summary.json
├── configs/                               # Calibrated candidate configurations and thresholds
│   ├── cnn_logmel_v5.json
│   ├── cnn_multiscale_v5.json
│   ├── cnn_temporal_v5.json
│   └── config_b_v5.json
├── domain_analysis/                       # Domain shift metrics and regression weights
│   └── acoustic_shift_metrics.json
├── features/                              # Precomputed feature caches
│   ├── logmel_v5_cache.npz                # 64-bin log-Mel spectrograms for all 1,914 clips (135 MB)
│   └── yamnet_v5_cache.npz                # 1024-d embeddings + phonation features (3.04 MB)
├── manifests/                             # Unified dataset manifest v5
│   └── dataset_manifest_v5.csv            # 1,914 recordings partitioned across 728 source groups
├── models/                                # Retrained PyTorch model checkpoints
│   ├── cnn_logmel_v5.pt                   # CustomLogMelCNN
│   ├── cnn_multiscale_v5.pt               # CustomMultiScaleCNN
│   ├── cnn_temporal_v5.pt                 # CustomTemporalCNN
│   └── config_b_v5.pt                     # DualEncoderAcousticModel
├── reports/                               # Full markdown research reports
│   ├── ACOUSTIC_DOMAIN_SHIFT_REPORT.md    # Acoustic feature analysis & domain classifier
│   ├── INFERENCE_BENCHMARK_V5.md          # 600-iteration latency & multi-stream benchmark
│   ├── SOURCE_GROUP_SPLIT_AUDIT.md        # Source-group isolation & partition audit
│   ├── STAGE_8_9_43_REPORT.md             # Master comprehensive stage report
│   └── SUBGROUP_RECALL_REPORT.md          # Granular subgroup & acoustic subtype analysis
├── results/                               # Machine-readable evaluation JSONs
│   ├── evaluation/
│   │   ├── candidate_eval_metrics.json
│   │   └── streaming_latency_benchmark.json
│   └── training/
│       └── candidate_training_summary.json
├── scripts/                               # Reproducible automation scripts
│   ├── audit_acoustic_domain_shift.py     # DSP feature extraction & domain classifier
│   ├── benchmark_streaming_v5.py          # 600-iteration streaming latency benchmark
│   ├── build_dataset_manifest_v5.py       # Source-group-stratified manifest partitioner
│   ├── evaluate_candidates_v5.py          # Independent evaluation and gate audit
│   ├── extract_v5_features.py             # Log-mel feature extractor
│   ├── extract_yamnet_v5.py               # YAMNet & subband feature extractor
│   ├── run_augmentation_study.py          # Controlled 4-condition augmentation experiment
│   ├── train_all_candidates_v5.py         # Retraining pipeline for all 4 candidates
│   └── verify_production_freeze.py        # Production freeze hash verifier
└── tests/                                 # Automated regression unit test suite
    ├── test_results.txt                   # Execution log (17/17 passed)
    └── test_stage_8_9_43.py               # 17 regression test cases
```

---

## 2. Key Results

| Candidate | Architecture | Features | Holdout Recall | 95% Wilson CI | Holdout HN-FPR | Shout-FPR | Short Scream Recall | P95 Latency | Gates Passed |
|---|---|---|---|---|---|---|---|---|---|
| **Config-B-v5** | DualEncoder | YAMNet + Phonation | **75.36%** | [64.04%, 84.01%] | **3.68%** | **7.14%** | **17/17 (100.0%)** | **0.47 ms** | **Gates 2, 3, 4, 5** (Gate 1 FAIL) |
| **CNN-LogMel-v5** | 2D CNN | 64-bin Log-Mel | 60.87% | [49.07%, 71.52%] | 5.88% | **3.57%** | 15/17 (88.24%) | **5.08 ms** | Gates 3, 5 |
| **CNN-MultiScale-v5**| MultiScale CNN | 64-bin Log-Mel | 65.22% | [53.45%, 75.38%] | **2.94%** | **3.57%** | 15/17 (88.24%) | **7.43 ms** | Gates 2, 3, 5 |
| **CNN-Temporal-v5** | Temporal CNN | 64-bin Log-Mel | 62.32% | [50.52%, 72.82%] | **2.94%** | **0.00%** | 14/17 (82.35%) | **10.70 ms** | Gates 2, 3, 5 |

---

## 3. How to Reproduce

1. **Verify Production Freeze:**
   ```powershell
   python backend/research/stage_8_9_43/scripts/verify_production_freeze.py
   ```
2. **Run Regression Unit Tests:**
   ```powershell
   python -m pytest backend/research/stage_8_9_43/tests/test_stage_8_9_43.py -v
   ```
3. **Run Independent Evaluation:**
   ```powershell
   python backend/research/stage_8_9_43/scripts/evaluate_candidates_v5.py
   ```
4. **Run Latency Benchmark:**
   ```powershell
   python backend/research/stage_8_9_43/scripts/benchmark_streaming_v5.py
   ```

