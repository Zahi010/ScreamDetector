# Dataset & Partition Integrity Audit — Stage 8.9.44

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe playback protocols only.

---

## 1. Executive Summary

This audit establishes the empirical integrity, source-group isolation, and augmentation boundaries of the datasets utilized in Stage 8.9.44. Stage 8.9.44 investigated whether environmental acoustic transformations (Room Impulse Response convolution, distance attenuation, and calibrated background noise masking) applied to training data could improve the generalization of the `DualEncoderAcousticModel` on unseen authentic recording sources.

To prevent optimistic bias, data leakage, and training-test contamination, strict partitioning and augmentation discipline were enforced:
1. The base dataset (`dataset_manifest_v5.csv`, $N=1,914$) was partitioned strictly by `source_group_id` into four disjoint sets.
2. Augmentation was applied **strictly and exclusively** to the positive training set (`v5_train` positives, $N=401$).
3. The validation (`v5_validation`, $N=309$), development test (`v5_development_test`, $N=202$), and final holdout (`v5_final_holdout`, $N=205$) partitions remained **100% authentic, unaugmented, and unaltered**.

---

## 2. Partition Structure & Source-Group Isolation

The dataset manifest comprises 1,914 audio recordings across 728 distinct source groups:

| Partition | Total Clips | Positive Clips | Negative Clips | Source Groups | Augmentation Applied |
|---|---|---|---|---|---|
| `v5_train` | 1,198 | 401 (33.47%) | 797 (66.53%) | 442 | **YES (Positives only)** |
| `v5_validation` | 309 | 78 (25.24%) | 231 (74.76%) | 114 | **NO (100% Authentic)** |
| `v5_development_test` | 202 | 81 (40.10%) | 121 (59.90%) | 86 | **NO (100% Authentic)** |
| `v5_final_holdout` | 205 | 69 (33.66%) | 136 (66.34%) | 86 | **NO (100% Authentic)** |
| **Total** | **1,914** | **629 (32.86%)** | **1,285 (67.14%)** | **728** | — |

### Source-Group Pairwise Overlap Audit

Pairwise intersection of source group IDs between all partition pairs:

$$\text{Overlap}(S_i, S_j) = S_i \cap S_j = \emptyset \quad \forall i \neq j$$

| Partition Pair | Overlapping Source Groups | Overlapping Clips | Leakage Status |
|---|---|---|---|
| `v5_train` $\cap$ `v5_validation` | 0 | 0 | **ZERO LEAKAGE (PASS)** |
| `v5_train` $\cap$ `v5_development_test` | 0 | 0 | **ZERO LEAKAGE (PASS)** |
| `v5_train` $\cap$ `v5_final_holdout` | 0 | 0 | **ZERO LEAKAGE (PASS)** |
| `v5_validation` $\cap$ `v5_development_test` | 0 | 0 | **ZERO LEAKAGE (PASS)** |
| `v5_validation` $\cap$ `v5_final_holdout` | 0 | 0 | **ZERO LEAKAGE (PASS)** |
| `v5_development_test` $\cap$ `v5_final_holdout` | 0 | 0 | **ZERO LEAKAGE (PASS)** |

---

## 3. Augmentation Integrity & Provenance

Augmentation was conducted exclusively on the 401 authentic positive recordings in `v5_train`. Exactly 1,604 augmented WAV files were generated and cataloged in dedicated condition manifests:

| Condition Manifest | Transformation Pipeline | Source Clips | Augmented Clips | Audio Format |
|---|---|---|---|---|
| `augmented_manifest_condition_b.csv` | Synthetic RIR Convolution (Small, Medium, Hall, Outdoor) | 401 | 401 | 16 kHz Mono WAV |
| `augmented_manifest_condition_c.csv` | Distance Attenuation (Spherical Spreading + Air Absorption) | 401 | 401 | 16 kHz Mono WAV |
| `augmented_manifest_condition_d.csv` | Background Noise Masking (Crowd, Speech, Music at 3–12 dB SNR) | 401 | 401 | 16 kHz Mono WAV |
| `augmented_manifest_condition_e.csv` | Combined Multi-Stage Pipeline (RIR + Attenuation + Masking) | 401 | 401 | 16 kHz Mono WAV |
| **Total Augmented Cohort** | — | **401** | **1,604** | **16 kHz Mono WAV** |

### Integrity Checks
- **No Test Contamination:** Zero audio files from `v5_development_test` or `v5_final_holdout` were subjected to augmentation or included in feature extraction caches.
- **Audio Integrity:** All 1,604 generated WAV files verified on disk; spot-checks confirmed valid RIFF headers, non-zero audio samples, and strictly 16,000 Hz sample rates.
- **Cache Verification:** `augmented_features_v6.npz` (2.15 MB) stores extracted features for all 1,604 augmented samples across exact matrix shapes: `X_sem` $(1604, 1024)$, `X_acoust` $(1604, 6)$, `mask_acoust` $(1604, 6)$, and `X_subband` $(1604, 11)$.

---

## 4. Production Freeze Hash Verification

All production classifier artifacts remain strictly frozen. The four canonical SHA-256 hashes were audited before and after Stage 8.9.44 execution:

| Artifact | Canonical Expected SHA-256 | Actual Verified SHA-256 | Audit Status |
|---|---|---|---|
| `backend/models/scream_classifier.joblib` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | **MATCH (FROZEN)** |
| `backend/models/model_metadata.json` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | **MATCH (FROZEN)** |
| `backend/reports/test_predictions.csv` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | **MATCH (FROZEN)** |
| `backend/reports/stage5_test_evaluation.md` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | **MATCH (FROZEN)** |

---

## 5. Conclusion

The dataset architecture satisfies all prerequisites for scientific rigor, complete partition independence, and production immutability. All test benchmarks reflect true, unbiased generalization to independent acoustic recording sources.

