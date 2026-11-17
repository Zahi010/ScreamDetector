# Model Training Provenance & Checkpoint Verification Audit

## 1. Executive Summary

All 10 experimental and production baseline checkpoints were inventoried, cryptographically hashed, and verified against training source code and manifests.

## 2. Model Provenance Table

| Model ID | Stage | Checkpoint Path | Exists | SHA-256 (Prefix) | Architecture | Dimensions | Threshold | Provenance Status |
|---|---|---|---|---|---|---|---|---|
| `D_v4_Baseline` | Stage 8.9.11 / Stage 8.9.14 | `experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_11_evaluation/models/model_d_v4.joblib` | True | `d679036ecd135612...` | dict | 3072 | 0.42 | **VERIFIED_TRAINED** |
| `D_v4_plus_Family_A` | Stage 8.9.14 | `experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_14_acoustic_discriminability/models/D_v4_plus_Family_A.joblib` | True | `92feaa72713180b2...` | Pipeline | 3080 | 0.42 | **VERIFIED_TRAINED** |
| `D_v4_plus_Family_B` | Stage 8.9.14 | `experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_14_acoustic_discriminability/models/D_v4_plus_Family_B.joblib` | True | `76209d4fb70aae50...` | Pipeline | 3080 | 0.65 | **VERIFIED_TRAINED** |
| `F_v6_Acoustic_Full` | Stage 8.9.14 | `experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_14_acoustic_discriminability/models/F_v6_Acoustic_Full.joblib` | True | `55ea5c596a1d0f89...` | Pipeline | 3102 | 0.36 | **VERIFIED_TRAINED** |
| `Gate_A_ExtraTrees` | Stage 8.9.15 | `experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_15_hierarchical_phonation/models/Gate_A_ExtraTrees.joblib` | True | `be5c7561e5f21769...` | ExtraTreesClassifier | 3102 | 0.28 | **VERIFIED_TRAINED** |
| `Model_A_Compact_MLP` | Stage 8.9.15 | `experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_15_hierarchical_phonation/models/Model_A_Compact_MLP.joblib` | True | `99b317f10518cb67...` | MLPClassifier | 3102 | 0.44 | **VERIFIED_TRAINED** |
| `Model_B_Temporal_CNN` | Stage 8.9.15 | `experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_15_hierarchical_phonation/models/Model_B_Temporal_CNN.keras` | True | `b368845e9536758a...` | KerasModel | 1024 | 0.61 | **VERIFIED_TRAINED** |
| `Model_C_Hierarchical_Fusion` | Stage 8.9.15 | `experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_15_hierarchical_phonation/models/Model_C_Hierarchical_Fusion.joblib` | True | `908410e983c0570b...` | LogisticRegression | 9 | 0.5 | **VERIFIED_TRAINED** |
| `Model_C_Gated_Cascade` | Stage 8.9.15 | `experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_15_hierarchical_phonation/models/Model_C_Hierarchical_Fusion.joblib` | True | `908410e983c0570b...` | LogisticRegression | 9 | 0.24 | **VERIFIED_TRAINED** |
| `PRODUCTION_BASELINE` | Production (Stage 5) | `models/scream_classifier.joblib` | True | `ad6e428d05d2359d...` | Pipeline | 1024 | 0.35 | **VERIFIED_TRAINED** |

## 3. Provenance Findings

1. **Stage 8.9.14 Artifacts**: Checkpoints `D_v4_plus_Family_A.joblib`, `D_v4_plus_Family_B.joblib`, and `F_v6_Acoustic_Full.joblib` were trained by `run_stage8_9_14_ablation_and_evaluation.py` on the 1,384-file Stage 8.9.11 dataset manifest.
2. **Stage 8.9.15 Artifacts**: `Gate_A_ExtraTrees.joblib`, `Model_A_Compact_MLP.joblib`, `Model_B_Temporal_CNN.keras`, and `Model_C_Hierarchical_Fusion.joblib` were trained by `train_and_evaluate_stage15.py`.
3. **Production Baseline**: `scream_classifier.joblib` remains completely frozen and its SHA-256 hash matches the authoritative specification exactly.
