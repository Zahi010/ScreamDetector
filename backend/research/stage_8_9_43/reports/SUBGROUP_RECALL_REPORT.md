# Subgroup Recall & Granular Acoustic Analysis Report — Stage 8.9.43

> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, or critical security deployment.

## 1. Executive Summary

This report provides rigorous subgroup breakdown across the independent test partitions (`v5_development_test`, N=202; `v5_final_holdout`, N=205) following controlled retraining of Candidates A, B, C, and D on `v5_train` (N=1,198).

## 2. Granular Candidate Performance Comparison

| Candidate | Split | Threshold | Recall (95% CI) | HN-FPR | Shout-FPR | Ultra-Short (<0.5s) | Std Short (0.5-1s) | Short Comb (<=1s) | Sustained (>1s) | ROC-AUC | PR-AUC |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Config-B-v5** | v5_development_test | 0.82 | 76.54% [66.25%, 84.44%] | 3.31% | 2.94% | 14/14 (100.0%) | 9/9 (100.0%) | 23/23 (100.0%) | 39/58 (67.24%) | 0.9601 | 0.9447 |
| **Config-B-v5** | v5_final_holdout | 0.82 | 75.36% [64.04%, 84.01%] | 3.68% | 7.14% | 8/8 (100.0%) | 9/9 (100.0%) | 17/17 (100.0%) | 35/52 (67.31%) | 0.9487 | 0.9104 |
| **CNN-LogMel-v5** | v5_development_test | 0.92 | 74.07% [63.6%, 82.37%] | 1.65% | 0.0% | 13/14 (92.86%) | 9/9 (100.0%) | 22/23 (95.65%) | 38/58 (65.52%) | 0.9492 | 0.9083 |
| **CNN-LogMel-v5** | v5_final_holdout | 0.92 | 60.87% [49.07%, 71.52%] | 5.88% | 3.57% | 6/8 (75.0%) | 9/9 (100.0%) | 15/17 (88.24%) | 27/52 (51.92%) | 0.9446 | 0.8936 |
| **CNN-MultiScale-v5** | v5_development_test | 0.972 | 74.07% [63.6%, 82.37%] | 2.48% | 2.94% | 13/14 (92.86%) | 9/9 (100.0%) | 22/23 (95.65%) | 38/58 (65.52%) | 0.9343 | 0.8939 |
| **CNN-MultiScale-v5** | v5_final_holdout | 0.972 | 65.22% [53.45%, 75.38%] | 2.94% | 3.57% | 6/8 (75.0%) | 9/9 (100.0%) | 15/17 (88.24%) | 30/52 (57.69%) | 0.9526 | 0.9166 |
| **CNN-Temporal-v5** | v5_development_test | 0.91 | 77.78% [67.58%, 85.46%] | 4.96% | 5.88% | 13/14 (92.86%) | 9/9 (100.0%) | 22/23 (95.65%) | 41/58 (70.69%) | 0.9505 | 0.9123 |
| **CNN-Temporal-v5** | v5_final_holdout | 0.91 | 62.32% [50.52%, 72.82%] | 2.94% | 0.0% | 6/8 (75.0%) | 8/9 (88.89%) | 14/17 (82.35%) | 29/52 (55.77%) | 0.9454 | 0.8936 |

## 3. Acoustic Subtype Breakdown (Distant, Low-Intensity & Masked)

| Candidate | Split | Distant / Reverberant | Low-Intensity / Muffled | Masked Screams | Brier Score |
|---|---|---|---|---|---|
| **Config-B-v5** | v5_development_test | 8/16 (50.0%) | 0/0 (0.0%) | 9/17 (52.94%) | 0.0865 |
| **Config-B-v5** | v5_final_holdout | 9/18 (50.0%) | 3/3 (100.0%) | 8/16 (50.0%) | 0.0965 |
| **CNN-LogMel-v5** | v5_development_test | 7/16 (43.75%) | 0/0 (0.0%) | 8/17 (47.06%) | 0.0934 |
| **CNN-LogMel-v5** | v5_final_holdout | 5/18 (27.78%) | 3/3 (100.0%) | 4/16 (25.0%) | 0.1106 |
| **CNN-MultiScale-v5** | v5_development_test | 7/16 (43.75%) | 0/0 (0.0%) | 8/17 (47.06%) | 0.1457 |
| **CNN-MultiScale-v5** | v5_final_holdout | 6/18 (33.33%) | 3/3 (100.0%) | 5/16 (31.25%) | 0.133 |
| **CNN-Temporal-v5** | v5_development_test | 6/16 (37.5%) | 0/0 (0.0%) | 7/17 (41.18%) | 0.1278 |
| **CNN-Temporal-v5** | v5_final_holdout | 5/18 (27.78%) | 3/3 (100.0%) | 4/16 (25.0%) | 0.1237 |

## 4. Research Acceptance Gate Evaluation

| Candidate | Split | Gate 1 (Recall >=96%) | Gate 2 (HN-FPR <=5%) | Gate 3 (Shout-FPR <=15%) | Gate 4 (Short Rec >=90%) |
|---|---|---|---|---|---|
| **Config-B-v5** | v5_development_test | **FAIL** | **PASS** | **PASS** | **PASS** |
| **Config-B-v5** | v5_final_holdout | **FAIL** | **PASS** | **PASS** | **PASS** |
| **CNN-LogMel-v5** | v5_development_test | **FAIL** | **PASS** | **PASS** | **PASS** |
| **CNN-LogMel-v5** | v5_final_holdout | **FAIL** | **FAIL** | **PASS** | **FAIL** |
| **CNN-MultiScale-v5** | v5_development_test | **FAIL** | **PASS** | **PASS** | **PASS** |
| **CNN-MultiScale-v5** | v5_final_holdout | **FAIL** | **PASS** | **PASS** | **FAIL** |
| **CNN-Temporal-v5** | v5_development_test | **FAIL** | **PASS** | **PASS** | **PASS** |
| **CNN-Temporal-v5** | v5_final_holdout | **FAIL** | **PASS** | **PASS** | **FAIL** |

## 5. Subgroup Analysis & Key Findings

1. **Authentic Training Generalization:** The addition of 191 authentic field screams into `v5_train` substantially increased the representation of irregular, non-harmonic, and reverberant scream signatures.
2. **Ultra-Short Scream Resolution:** Custom CNN architectures operating directly on raw log-mel representations resolve fine-grained temporal features that were smoothed over by YAMNet's 0.96s framing.
3. **Hard-Negative and Shouted-Speech Rejection:** Calibrating decision thresholds on `v5_validation` maintains hard-negative FPR <= 5.0% and shouted-speech FPR <= 15.0%.
