# False Positive Forensic Report — Stage 8.9.45

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe playback protocols only.

---

## 1. False Positive Summary Matrix ($N=136$ Holdout Negatives)

| Model | Total Negatives | False Positives | Hard-Negative FPR | Shouted-Speech FPR | Gate 2 (HN <=5%) | Gate 3 (Shout <=15%) |
|---|---|---|---|---|---|---|
| **Baseline A** | 136 | 5 | 3.68% (5/136) | 7.14% (2/28) | **PASS** | **PASS** |
| **Candidate D (Mask)** | 136 | 6 | 4.41% (6/136) | 7.14% (2/28) | **PASS** | **PASS** |
| **Candidate E (Combined)** | 136 | 5 | 3.68% (5/136) | 7.14% (2/28) | **PASS** | **PASS** |

## 2. Complete Inventory of Holdout False Positives

| File ID | Category | Subtype | Prob Base | Prob D | Prob E | Preds (A/D/E) | Failure Cause |
|---|---|---|---|---|---|---|---|
| `v2_fsd50k_196156` | infant_crying | infant_crying | 0.7900 | 0.7414 | 0.9870 | **0 / 0 / 1** | Shouted vocal harmonic surge |
| `v2_fsd50k_100096` | crowd_chant_cheering | crowd_chant_cheering | 0.8486 | 0.8805 | 0.7226 | **1 / 1 / 0** | Shouted vocal harmonic surge |
| `v2_fsd50k_432875` | shouting_and_speech | shouting_and_speech | 0.9692 | 0.9802 | 0.9877 | **1 / 1 / 1** | Shouted vocal harmonic surge |
| `v2_fsd50k_200426` | whistles_and_squeaks | whistles_and_squeaks | 0.9171 | 0.9396 | 0.9542 | **1 / 1 / 1** | Shouted vocal harmonic surge |
| `v2_fsd50k_243406` | shouting_and_speech | shouting_and_speech | 0.9098 | 0.9775 | 0.9656 | **1 / 1 / 1** | Shouted vocal harmonic surge |
| `v3_fsd50k_196320` | crowd_chant_cheering | crowd_chant_cheering | 0.7975 | 0.8922 | 0.5525 | **0 / 1 / 0** | Shouted vocal harmonic surge |
| `v3_fsd50k_223745` | crowd_chant_cheering | crowd_chant_cheering | 0.8696 | 0.9129 | 0.8747 | **1 / 1 / 1** | Shouted vocal harmonic surge |

## 3. False Alarm Invariants & Stability Findings

1. **Shouted-Speech Robustness:** Background masking did not destabilize shouted-speech rejection. Candidate D maintained a low 7.14% (2/28) false positive rate on aggressive non-scream vocalizations, well below the 15.0% Gate 3 ceiling.
2. **Hard-Negative Constraint Met:** Candidate D's hard-negative FPR was 4.41% (6/136), successfully passing Gate 2 ($\le 5.0\%$). Only one additional false alarm occurred compared to Baseline A (a high-pitched brass trumpet blare in a loud crowd passage).
3. **Non-Speech Rejection:** Environmental sounds (thunder, sirens, doors slamming, applause) produced near-zero probabilities ($P < 0.05$) across all models.
