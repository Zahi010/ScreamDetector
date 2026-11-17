# Dataset Partition & Source-Group Independence Audit — Stage 8.9.44

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

---

## 1. Overview of Dataset Manifest v5

The dataset manifest [`dataset_manifest_v5.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_43/manifests/dataset_manifest_v5.csv) was audited to verify record counts, class distributions, and source-group isolation across all research partitions.

- **Total Audio Recordings:** 1,914
- **Total Positive Recordings:** 629
- **Total Negative Recordings:** 1,285
- **Unique Source Groups:** 728
- **Audio Sample Rate:** 16,000 Hz, single channel (mono)

## 2. Partition Summary & Class Balance

| Partition Name | Total Clips | Positive (Screams) | Negative (Non-Screams) | Source Groups | Partition Role |
|---|---|---|---|---|---|
| `v5_train` | 1,198 | 401 (33.47%) | 797 (66.53%) | 436 | Model parameter optimization & augmentation |
| `v5_validation` | 309 | 78 (25.24%) | 231 (74.76%) | 107 | Calibration & operating threshold selection |
| `v5_development_test` | 202 | 81 (40.10%) | 121 (59.90%) | 90 | Architectural comparison & research iteration |
| `v5_final_holdout` | 205 | 69 (33.66%) | 136 (66.34%) | 95 | Sealed independent generalization benchmark |
| **Total** | **1,914** | **629** | **1,285** | **728** | Complete dataset v5 |

## 3. Source-Group Pairwise Isolation Audit

To guarantee zero data leakage, source-group IDs were compared across all pairwise combinations of the four partitions:

| Partition A | Partition B | Source-Group Overlap Count | Leakage Status |
|---|---|---|---|
| `v5_train` | `v5_validation` | 0 | **STRICT ZERO LEAKAGE** |
| `v5_train` | `v5_development_test` | 0 | **STRICT ZERO LEAKAGE** |
| `v5_train` | `v5_final_holdout` | 0 | **STRICT ZERO LEAKAGE** |
| `v5_validation` | `v5_development_test` | 0 | **STRICT ZERO LEAKAGE** |
| `v5_validation` | `v5_final_holdout` | 0 | **STRICT ZERO LEAKAGE** |
| `v5_development_test` | `v5_final_holdout` | 0 | **STRICT ZERO LEAKAGE** |

## 4. Final Holdout Purity Confirmation

`v5_final_holdout` ($N=205$) contains:
- 69 authentic scream recordings across 40 positive source groups.
- 136 hard-negative recordings across 55 negative source groups.
- **Sealing Rule:** Neither model weights nor decision thresholds may be tuned on `v5_final_holdout`. All thresholds are determined strictly on `v5_validation`.

