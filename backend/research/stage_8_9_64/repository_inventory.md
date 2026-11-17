# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Repository Asset Inventory & Path Mapping — Stage 8.9.64

**Stage Designation:** STAGE 8.9.64  
**Date:** November 12, 2026  
**Status:** COMPLETE — ALL PROTECTED ASSETS ACCOUNTED FOR  

---

## 1. Executive Summary

This inventory documents all protected baseline production models, historical research checkpoints, signal processing modules, dataset manifests, and previous stage research assets audited at the inception of Stage 8.9.64.

Strict immutability boundaries are maintained: no production model, historical checkpoint, reference DSP extractor, or sealed evaluation manifest may be modified, overwritten, or retrained.

---

## 2. Protected Baseline Assets

| Identifier | Description | Absolute / Relative Path | Status |
| :--- | :--- | :--- | :---: |
| `production_classifier` | Production random forest audio classifier | `backend/models/scream_classifier.joblib` | **FROZEN** |
| `model_metadata` | Metadata and threshold configuration for production | `backend/models/model_metadata.json` | **FROZEN** |
| `test_predictions` | Historical baseline test predictions | `backend/reports/test_predictions.csv` | **FROZEN** |
| `stage5_evaluation` | Stage 5 authoritative test report | `backend/reports/stage5_test_evaluation.md` | **FROZEN** |
| `candidate_e1_checkpoint` | Candidate E1 neural network weights | `backend/research/stage_8_9_54/training/candidate_e_v954_weighted.pt` | **FROZEN** |
| `candidate_b_checkpoint` | Candidate B frozen reference model | `backend/research/stage_8_9_44/models/config_b_mask.pt` | **FROZEN** |
| `intervention_d_code` | Whistle discriminator intervention module | `backend/research/stage_8_9_49/scripts/whistle_discriminator.py` | **FROZEN** |
| `c5_combined_dsp` | Optimized C5 subband and phonation DSP | `backend/research/stage_8_9_57/dsp_implementations/c5_combined.py` | **FROZEN** |
| `original_e1_dsp` | Unoptimized Candidate E1 baseline DSP | `backend/research/stage_8_9_57/scripts/benchmark_original_dsp.py` | **FROZEN** |
| `stage54_partition_manifest` | Stage 54 verified partition manifest | `backend/research/stage_8_9_54/dataset/partition_manifest_verified.csv` | **FROZEN** |
| `stage60_sealed_manifest` | Sealed evaluation cohort manifest (700 clips)| `backend/research/stage_8_9_60/future_evaluation_manifest.json` | **FROZEN** |
| `duplicate_relationships` | Duplicate and excerpt audit relationships | `backend/research/stage_8_9_60/duplicate_and_excerpt_relationships.csv` | **FROZEN** |
| `stage61_dev_manifest` | Stage 61 development manifest | `backend/research/stage_8_9_61/rolling_window_development_manifest.csv` | **FROZEN** |
| `stage61_candidate_freeze` | Stage 61 rolling window candidate freeze | `backend/research/stage_8_9_61/rolling_window_candidate_freeze.json` | **FROZEN** |
| `stage61_preregistration` | Stage 61 evaluation preregistration plan | `backend/research/stage_8_9_61/independent_evaluation_preregistration.md` | **FROZEN** |
| `stage61_sealed_predictions` | Stage 61 evaluation predictions (700 clips) | `backend/research/stage_8_9_61/sealed_cohort_predictions.csv` | **FROZEN** |
| `stage63_dev_manifest` | Stage 63 development manifest (312 clips) | `backend/research/stage_8_9_63/stage_63_development_manifest.csv` | **FROZEN** |
| `stage63_short_manifest` | Stage 63 short-scream acquisition manifest (133)| `backend/research/stage_8_9_63/short_scream_acquisition_manifest.csv` | **FROZEN** |

---

## 3. Directory Mapping for Stage 8.9.64

Stage 8.9.64 operates exclusively within its isolated research directory:
```
backend/research/stage_8_9_64/
├── models/                     # Experimental checkpoints and weights
├── scripts/                    # Specialized audit and ablation scripts
├── tests/                      # Automated 52-test invariant verification suite
├── artifact_hashes.json        # Authoritative SHA-256 asset register
├── STAGE_PROGRESS.md           # Real-time milestone tracker
└── *.md, *.csv                 # Phase reports and empirical data artifacts
```

