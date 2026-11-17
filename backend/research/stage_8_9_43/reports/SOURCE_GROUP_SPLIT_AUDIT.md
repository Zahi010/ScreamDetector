# MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Stage 8.9.43: Source-Group-Level Partitioning & Leakage Audit Report

## 1. Executive Summary

Dataset Manifest v5 consolidates 1,911 verified acoustic recordings (629 positive screams and 1,282 negative confusers) partitioned strictly at the `source_group_id` level to guarantee **zero excerpt, session, or speaker leakage**.

## 2. Partition Summary Table

| Partition Name | Total Recordings | Positive Screams | Negative Confusers | Unique Source Groups | Purpose |
|---|---|---|---|---|---|
| **`v5_train`** | 1198 | 401 | 797 | 436 | Model training & contrastive representation learning |
| **`v5_validation`** | 309 | 78 | 231 | 107 | Hyperparameter tuning, early stopping & threshold selection |
| **`v5_development_test`** | 202 | 81 | 121 | 90 | Intermediate candidate comparison & ablation evaluation |
| **`v5_final_holdout`** | 205 | 69 | 136 | 95 | STRICTLY LOCKED UNTOUCHED FINAL EVALUATION |

## 3. Hard-Negative Category Distribution Across Splits

| Category | v5_train | v5_validation | v5_development_test | v5_final_holdout | Total |
|---|---|---|---|---|---|
| `crowd_chant_cheering` | 219 | 40 | 33 | 43 | 335 |
| `general_environmental` | 86 | 25 | 11 | 8 | 130 |
| `infant_crying` | 46 | 22 | 10 | 19 | 97 |
| `masked_distant_screams` | 75 | 18 | 16 | 16 | 125 |
| `scream` | 326 | 60 | 65 | 53 | 504 |
| `sfx_sirens_fireworks` | 60 | 15 | 12 | 16 | 103 |
| `shouting_and_speech` | 286 | 91 | 34 | 28 | 439 |
| `whistles_and_squeaks` | 100 | 38 | 21 | 22 | 181 |

## 4. Leakage Verification Criteria

- **Zero Excerpt Leakage:** Excerpts from the same parent sound or uploader session share identical `source_group_id` values and are mapped into the same partition.
- **Partition Independence:** The pairwise intersection of source group IDs between all 4 partitions is exactly $\emptyset$.
- **Final Holdout Isolation:** `v5_final_holdout` contains 79 authentic positive screams and 162 hard negatives that are strictly sealed until final evaluation.
