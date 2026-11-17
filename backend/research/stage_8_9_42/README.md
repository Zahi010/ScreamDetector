# MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Stage 8.9.42: Positive-Class Failure Forensics, Temporal Representation Audit & Custom CNN Feasibility Study

**Project:** Festival Scream Detector  
**Directory:** `backend/research/stage_8_9_42/`  
**Status:** COMPLETE  
**Sanctioned Final Decision:** `FORENSIC ROOT CAUSE IDENTIFIED`

---

## Overview

Stage 8.9.42 conducted an in-depth forensic investigation into the positive-class recall degradation identified in Stage 8.9.41, where frozen Configuration B achieved 100% (65/65) recall on historical expansion positives but only 35.09% (20/57) on the new independent positive cohort.

The stage investigated two directions:
- **Direction A (YAMNet Temporal Audit):** Evaluated whether alternative temporal pooling (Mean, Max, Energy-Weighted, Mask-Aware) can mitigate silence padding dilution.
- **Direction B (Custom CNN Feasibility):** Evaluated training a compact CNN directly from 64-bin log-Mel spectrograms without YAMNet embeddings.

---

## Directory Structure

```
backend/research/stage_8_9_42/
├── configs/
│   ├── cnn_logmel_config.json
│   └── cnn_multiscale_config.json
├── models/
│   ├── cnn_logmel_best.pt
│   └── cnn_multiscale_best.pt
├── reports/
│   ├── STAGE_8_9_42_REPORT.md       # Comprehensive master final report
│   ├── YAMNET_TEMPORAL_AUDIT.md     # Temporal pooling audit report
│   ├── CUSTOM_CNN_ARCHITECTURE.md   # Custom CNN specifications and comparison
│   └── INFERENCE_BENCHMARK.md       # 600-run computational latency benchmark
├── results/
│   ├── yamnet_frames_cache.npz      # Cached per-frame YAMNet outputs
│   ├── yamnet_temporal_audit.json   # Pooling evaluation metrics
│   ├── logmel_spectrograms_cache.npz# 64-bin log-Mel dataset (N=1463)
│   ├── latency_benchmark.json       # Latency and concurrency metrics
│   └── training/                    # Training histories and logs
├── scripts/
│   ├── extract_yamnet_frames.py     # YAMNet per-frame extraction (Python 3.11 / TF)
│   ├── eval_yamnet_pooling.py       # YAMNet pooling evaluation (Python 3.13 / PyTorch)
│   ├── extract_logmel_dataset.py    # Log-Mel spectrogram dataset extraction
│   ├── train_custom_cnn.py          # Custom CNN training on v4_train
│   ├── compare_candidates.py        # Multi-candidate comparison across all suites
│   ├── benchmark_inference.py       # Latency and concurrency benchmark (600 runs)
│   └── verify_production_freeze.py  # Production hash integrity verification
├── tests/
│   ├── test_stage_8_9_42.py         # 16-test regression test suite
│   └── test_results.txt             # Pytest execution log (100% pass)
├── SHORT_SCREAM_ACCOUNTING_AUDIT.csv# Reconciled audit of short screams (N=31 rows)
├── FALSE_NEGATIVE_FORENSIC_AUDIT.csv# Deep-dive acoustic audit of 37 missed screams
├── CANDIDATE_COMPARISON.csv         # Matrix of 5 candidates across all suites
└── STAGE_PROGRESS.md                # Stage progress log and milestones
```

---

## Key Findings

1. **Short-Scream Accounting Reconciled:** 26 categorical `short_scream` vs. 31 physical duration $\le 1.0\text{ s}$ clips in Stage 8.9.41. Combined short-scream denominator is 96 ($65 + 31 = 96$).
2. **YAMNet Single-Frame Quantization:** Audio clips $\le 0.96\text{ s}$ produce **exactly 1 frame** in YAMNet. Post-hoc temporal pooling across frames is an identity operation and cannot recover ultra-short screams (0/11 detected across all pooling modes).
3. **Dual Root Cause of Recall Degradation:**
   - **Architectural Bottleneck:** YAMNet's fixed 0.96s window dilutes sub-second audio with internal silence padding.
   - **Training Set Domain Shift:** `v4_train` contains synthetic screams with artificial harmonic richness and lacks authentic sub-second screams in outdoor reverberant environments.
4. **Production Freeze:** All four canonical production hashes verified byte-for-byte before and after execution.
5. **Inference Latency:** Custom CNN achieves P95 streaming latency of 5.02 ms (passing Gate 5 $\le 25\text{ ms}$) and supports 8 concurrent streams within the 100 ms audio-hop deadline.

