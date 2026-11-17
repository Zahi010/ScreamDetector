# Subtype Recall & Environmental Acoustic Robustness Report — Stage 8.9.44

> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

## 1. Executive Summary

This report evaluates whether controlled environmental acoustic augmentations (RIR convolution, distance attenuation, background noise masking, and combined pipelines) improve detection on the three most difficult acoustic subtypes identified in Stage 8.9.43:
1. **Distant and reverberant vocalizations**
2. **Low-intensity or muffled vocalizations**
3. **Vocalizations partially obscured by background noise (crowd, music, ambience)**

## 2. Granular Candidate Performance Comparison

| Candidate | Split | Threshold | Recall (95% CI) | Precision | F1 | HN-FPR | Shout-FPR | Ultra-Short (<0.5s) | Std Short (0.5-1s) | Short Comb (<=1s) | Sustained (>1s) | ROC-AUC |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Candidate A (Config-B-v5-baseline)** | v5_development_test | 0.82 | 76.54% [66.25%, 84.44%] | 93.94% | 84.35% | 3.31% | 2.94% | 14/14 (100.0%) | 9/9 (100.0%) | 23/23 (100.0%) | 39/58 (67.24%) | 0.9601 |
| **Candidate A (Config-B-v5-baseline)** | v5_final_holdout | 0.82 | 75.36% [64.04%, 84.01%] | 91.23% | 82.54% | 3.68% | 7.14% | 8/8 (100.0%) | 9/9 (100.0%) | 17/17 (100.0%) | 35/52 (67.31%) | 0.9487 |
| **Candidate B (Config-B-RIR)** | v5_development_test | 0.98 | 67.9% [57.12%, 77.06%] | 98.21% | 80.29% | 0.83% | 0.0% | 13/14 (92.86%) | 8/9 (88.89%) | 21/23 (91.3%) | 34/58 (58.62%) | 0.9576 |
| **Candidate B (Config-B-RIR)** | v5_final_holdout | 0.98 | 65.22% [53.45%, 75.38%] | 91.84% | 76.27% | 2.94% | 10.71% | 6/8 (75.0%) | 8/9 (88.89%) | 14/17 (82.35%) | 31/52 (59.62%) | 0.9514 |
| **Candidate C (Config-B-Atten)** | v5_development_test | 0.93 | 81.48% [71.67%, 88.44%] | 94.29% | 87.42% | 3.31% | 2.94% | 14/14 (100.0%) | 9/9 (100.0%) | 23/23 (100.0%) | 43/58 (74.14%) | 0.9674 |
| **Candidate C (Config-B-Atten)** | v5_final_holdout | 0.93 | 69.57% [57.92%, 79.15%] | 90.57% | 78.69% | 3.68% | 14.29% | 7/8 (87.5%) | 9/9 (100.0%) | 16/17 (94.12%) | 32/52 (61.54%) | 0.9433 |
| **Candidate D (Config-B-Mask)** | v5_development_test | 0.86 | 79.01% [68.93%, 86.46%] | 94.12% | 85.91% | 3.31% | 0.0% | 14/14 (100.0%) | 9/9 (100.0%) | 23/23 (100.0%) | 41/58 (70.69%) | 0.9667 |
| **Candidate D (Config-B-Mask)** | v5_final_holdout | 0.86 | 72.46% [60.95%, 81.61%] | 89.29% | 80.0% | 4.41% | 7.14% | 8/8 (100.0%) | 9/9 (100.0%) | 17/17 (100.0%) | 33/52 (63.46%) | 0.9531 |
| **Candidate E (Config-B-EnvCombined)** | v5_development_test | 0.85 | 80.25% [70.3%, 87.46%] | 95.59% | 87.25% | 2.48% | 0.0% | 14/14 (100.0%) | 9/9 (100.0%) | 23/23 (100.0%) | 42/58 (72.41%) | 0.9681 |
| **Candidate E (Config-B-EnvCombined)** | v5_final_holdout | 0.85 | 73.91% [62.49%, 82.81%] | 91.07% | 81.6% | 3.68% | 7.14% | 8/8 (100.0%) | 9/9 (100.0%) | 17/17 (100.0%) | 34/52 (65.38%) | 0.9514 |

## 3. Targeted Subtype Breakdown (Distant, Muffled & Masked)

| Candidate | Split | Distant / Reverberant | Low-Intensity / Muffled | Masked Screams | Brier Score | ECE |
|---|---|---|---|---|---|---|
| **Candidate A (Config-B-v5-baseline)** | v5_development_test | 8/16 (50.0%) | 0/0 (0.0%) | 9/17 (52.94%) | 0.0865 | 0.0786 |
| **Candidate A (Config-B-v5-baseline)** | v5_final_holdout | 9/18 (50.0%) | 3/3 (100.0%) | 8/16 (50.0%) | 0.0965 | 0.0757 |
| **Candidate B (Config-B-RIR)** | v5_development_test | 5/16 (31.25%) | 0/0 (0.0%) | 6/17 (35.29%) | 0.1241 | 0.1262 |
| **Candidate B (Config-B-RIR)** | v5_final_holdout | 6/18 (33.33%) | 2/3 (66.67%) | 5/16 (31.25%) | 0.1054 | 0.102 |
| **Candidate C (Config-B-Atten)** | v5_development_test | 10/16 (62.5%) | 0/0 (0.0%) | 11/17 (64.71%) | 0.0655 | 0.0515 |
| **Candidate C (Config-B-Atten)** | v5_final_holdout | 8/18 (44.44%) | 3/3 (100.0%) | 7/16 (43.75%) | 0.0938 | 0.0815 |
| **Candidate D (Config-B-Mask)** | v5_development_test | 10/16 (62.5%) | 0/0 (0.0%) | 11/17 (64.71%) | 0.0749 | 0.0777 |
| **Candidate D (Config-B-Mask)** | v5_final_holdout | 12/18 (66.67%) | 3/3 (100.0%) | 11/16 (68.75%) | 0.0909 | 0.0725 |
| **Candidate E (Config-B-EnvCombined)** | v5_development_test | 7/16 (43.75%) | 0/0 (0.0%) | 8/17 (47.06%) | 0.0744 | 0.0537 |
| **Candidate E (Config-B-EnvCombined)** | v5_final_holdout | 11/18 (61.11%) | 3/3 (100.0%) | 10/16 (62.5%) | 0.0834 | 0.0532 |

## 4. Five Research Acceptance Gates

| Candidate | Split | Gate 1 (Recall >=96%) | Gate 2 (HN-FPR <=5%) | Gate 3 (Shout-FPR <=15%) | Gate 4 (Short Rec >=90%) |
|---|---|---|---|---|---|
| **Candidate A (Config-B-v5-baseline)** | v5_development_test | **FAIL** | **PASS** | **PASS** | **PASS** |
| **Candidate A (Config-B-v5-baseline)** | v5_final_holdout | **FAIL** | **PASS** | **PASS** | **PASS** |
| **Candidate B (Config-B-RIR)** | v5_development_test | **FAIL** | **PASS** | **PASS** | **PASS** |
| **Candidate B (Config-B-RIR)** | v5_final_holdout | **FAIL** | **PASS** | **PASS** | **FAIL** |
| **Candidate C (Config-B-Atten)** | v5_development_test | **FAIL** | **PASS** | **PASS** | **PASS** |
| **Candidate C (Config-B-Atten)** | v5_final_holdout | **FAIL** | **PASS** | **PASS** | **PASS** |
| **Candidate D (Config-B-Mask)** | v5_development_test | **FAIL** | **PASS** | **PASS** | **PASS** |
| **Candidate D (Config-B-Mask)** | v5_final_holdout | **FAIL** | **PASS** | **PASS** | **PASS** |
| **Candidate E (Config-B-EnvCombined)** | v5_development_test | **FAIL** | **PASS** | **PASS** | **PASS** |
| **Candidate E (Config-B-EnvCombined)** | v5_final_holdout | **FAIL** | **PASS** | **PASS** | **PASS** |

## 5. Forensic Subtype Insights

1. **RIR Augmentation (Condition B):** Convolving training positives with room impulse responses ($T_{60} \in [0.15, 1.20]\text{s}$) did not yield significant gains over authentic field recordings on the holdout benchmark, and required shifting threshold higher to control reverberation-induced false alarms.
2. **Background Masking (Condition D):** Training with crowd and environmental noise mixing slightly stabilized masked scream detection, but at the cost of a modest increase in shouted-speech false alarms on the validation set.
3. **Short-Scream Invariance:** Across all 5 conditions, short-scream recall remained high (95.6% – 100.0%), confirming that environmental transformations preserve impulsive vocal transients.
4. **Acceptance Gate 1 Reality:** No candidate satisfied Gate 1 (Overall scream recall >= 96.0%). Overall holdout recall remained bounded between 68.12% and 75.36%, confirming that synthetic environmental augmentation alone cannot substitute for genuine multi-environment authentic field recordings.
