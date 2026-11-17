# Stage 8.9.54: Final Research Stage Report
## Candidate E Expanded-Data Retraining, Controlled Ablations & Generalization Preparation

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.  
> No live-fire experiments, autonomous emergency dispatch, external emergency alerts, or claims of life-safety efficacy.  
> No production promotion is authorized.

---

## 1. Executive Summary

Stage 8.9.54 tested the hypothesis that Candidate E's failure to generalize in Stage 8.9.53 stemmed from small-sample training exposure ($N=200$ Dev in Stage 8.9.51) rather than architectural deficiency.

Candidate E was retrained on the authentic **`expansion_train`** partition ($N=1,055$ recordings across 415 source groups) under four strictly controlled experimental conditions (E0, E1, E2, E3) and evaluated on **`expansion_val`** ($N=311$ recordings across 138 source groups) at validation-calibrated operating points.

### Primary Outcome:
**Expanded-data training substantially improved Candidate E's discriminative power.**
- On `expansion_val`, PR-AUC increased from **0.7040** (Original Candidate E) to **0.9224** (Candidate E1 Class-Balanced).
- ROC-AUC increased from **0.8794** to **0.9670**.
- Hard-negative FPR at the calibrated operating point was reduced by more than half, from **11.79%** down to **4.72%** (satisfying Gate 2 $\le 5.0\%$).
- Candidate E1's validation F1 score (**85.86%**) and PR-AUC (**0.9224**) are competitive with frozen Candidate B Baseline (F1: **86.01%**, PR-AUC: **0.9197**).
- However, Gate 1 (Scream Recall $\ge 96.0\%$) remains failed (82.83% achieved), and independent generalization remains officially unverified pending evaluation on a brand-new independent test cohort.

---

## 2. Answers to Mandated Stage Inquiries (Section 18)

### 1. Was the Stage 8.9.52/8.9.53 source-group discrepancy resolved?
**YES.** Physical manifest reconciliation established that the actual number of deduplicated source groups in `expansion_manifest.csv` is **693** (415 train, 138 val, 140 test). In Stage 8.9.52, summary text reported 705 source groups (423 train, 141 val, 141 test) based on pre-deduplication proportional estimates ($705 \times 0.60 = 423, 705 \times 0.20 = 141$). The discrepancy was a clerical reporting rounding error in the text; zero recordings or groups were missing or modified.

### 2. Was original Candidate E reproduced?
**YES.** Evaluated on the historical Stage 8.9.52 validation split ($N=120$), Candidate E (`research_exp_candidate.pt`) reproduced **120 / 120 (100.0%)** binary predictions with a maximum probability delta of `0.0000000000`, achieving identical 48/48 TP and 0/72 FP.

### 3. Did expanded-data training improve performance?
**YES, substantially.** On `expansion_val` ($N=311$), training on 1,055 authentic recordings elevated PR-AUC from 0.7040 to 0.9224 and ROC-AUC from 0.8794 to 0.9670. False alarms on cheering, whistles, and background noise plummeted from 25/212 (11.79%) down to 10/212 (4.72%).

### 4. Which augmentation strategy helped, if any?
Targeted conservative acoustic augmentation (E2/E3: mild crowd-noise injection, distant attenuation, subband jitter) provided enhanced stability and helped sustain recall on distant and crowd-masked screams, but the class-weighted unaugmented model (E1) achieved the highest overall validation PR-AUC (0.9224) and F1 (85.86%).

### 5. Did class balancing improve recall without unacceptable FPR?
**YES.** In `expansion_train`, the negative-to-positive ratio is 1.6179:1 (652 neg / 403 pos). Applying `pos_weight = 1.6179` in BCE loss allowed Candidate E1 to achieve **82.83% recall** (82 / 99) while maintaining **4.72% HN-FPR** (10 / 212), producing the highest F1 score (85.86%) among all Candidate E models.

### 6. Did short-scream recall improve?
**YES.** Candidate E1 achieved **94.87% recall** (37 / 39) on short screams (<1.0s) on `expansion_val`, comfortably exceeding the 90.0% acceptance gate requirement.

### 7. Did low-intensity and crowd-masked recall improve?
**YES.** Across all retrained models, crowd-masked scream recall improved from 64.3% (original) to **78.6%** (22 / 28), and low-intensity muffled scream recall reached **100.0%** (3 / 3, though small sample).

### 8. Did false positives increase?
**NO, false positives decreased dramatically.** On `expansion_val`, Original Candidate E generated 25 false positives (11.79% FPR). Retrained Candidate E1 produced only 10 false positives (4.72% FPR)—a 60% reduction in false alarms.

### 9. Does Candidate E outperform frozen Candidate B on validation?
**Candidate E1 performs competitively with Candidate B on validation, but does not definitively outperform it.**
- Candidate B Baseline: Recall **83.84%**, HN-FPR **5.19%**, Precision **88.30%**, F1 **86.01%**, PR-AUC **0.9197**.
- Candidate E1 (Class-Balanced): Recall **82.83%**, HN-FPR **4.72%**, Precision **89.13%**, F1 **85.86%**, PR-AUC **0.9224**.
Candidate E1 achieves slightly lower HN-FPR and slightly higher PR-AUC, while Candidate B detects 1 additional true positive. The difference is within normal statistical uncertainty.

### 10. Which original acceptance gates remain failed?
- **Gate 1 (Scream Recall $\ge 96.0\%$):** **FAILED** (82.83% achieved).
- **Gate 2 (Hard-Negative FPR $\le 5.0\%$):** **PASSED** (4.72% achieved).
- **Gate 3 (Shouted-Speech FPR $\le 15.0\%$):** **PASSED** (10.23% achieved).
- **Gate 4 (Short-Scream Recall $\ge 90.0\%$):** **PASSED** (94.87% achieved).
- **Gate 5 (Computational Latency P95 $\le 25.0$ ms):** **PASSED** (0.390 ms achieved).

### 11. Is a new independent cohort available?
**NOT YET.** The 366-recording Stage 8.9.53 cohort is now an evaluated historical benchmark and is strictly quarantined. A brand-new independent cohort (Stage 8.9.55 cohort: 400–500 authentic recordings across $\ge 150$ source groups) must be curated and verified before independent generalization can be claimed.

### 12. Were all protected artifacts preserved?
**YES, 100% BIT-FOR-BIT MATCH.** All 4 canonical production files and both historical checkpoints (`config_b_mask.pt` and `research_exp_candidate.pt`) match their cryptographic hashes exactly.

---

## 3. Comparative Validation Performance Matrix (`expansion_val`, N=311)

| Model Condition | Checkpoint File | Operating $\theta$ | Scream Recall (TP/99) | Hard-Neg FPR (FP/212) | Precision | F1 Score | PR-AUC | ROC-AUC |
|---|---|---|---|---|---|---|---|---|
| **Original Candidate E** | `research_exp_candidate.pt` | `0.4000` | 76.77% [67.5%, 84.0%] | 11.79% [8.1%, 16.8%] | 75.25% | 76.00% | 0.7040 | 0.8794 |
| **Candidate E0 (Baseline)** | `candidate_e_v954_baseline.pt` | `0.6900` | 79.80% [70.9%, 86.5%] | 4.72% [2.6%, 8.5%] | 88.76% | 84.04% | 0.9120 | 0.9658 |
| **Candidate E1 (Weighted)** | `candidate_e_v954_weighted.pt` | `0.6800` | **82.83%** [74.2%, 89.0%] | **4.72%** [2.6%, 8.5%] | **89.13%** | **85.86%** | **0.9224** | **0.9670** |
| **Candidate E2 (Augmented)**| `candidate_e_v954_augmented.pt` | `0.6700` | 77.78% [68.6%, 84.8%] | 4.72% [2.6%, 8.5%] | 88.51% | 82.80% | 0.9081 | 0.9618 |
| **Candidate E3 (Combined)** | `candidate_e_v954_combined.pt` | `0.8900` | 78.79% [69.7%, 85.7%] | 4.72% [2.6%, 8.5%] | 88.64% | 83.42% | 0.9060 | 0.9659 |
| **Candidate B Baseline** | `config_b_mask.pt` | `0.8000` | **83.84%** [75.4%, 89.8%] | **5.19%** [2.9%, 9.1%] | 88.30% | 86.01% | 0.9197 | 0.9653 |
| **Candidate B + Interv D** | `config_b_mask.pt` + Filter | `0.8000` | 82.83% [74.2%, 89.0%] | 5.19% [2.9%, 9.1%] | 88.17% | 85.42% | 0.9197 | 0.9653 |

---

## 4. Final Sanctioned Decision

### Outcome Selected:
**`EXPANDED-DATA TRAINING IMPROVED CANDIDATE E — INDEPENDENT TEST PENDING`**

### Technical Justification:
1. Training Candidate E on 1,055 authentic recordings in `expansion_train` resolved the acute overfitting previously observed when trained on only 200 clips.
2. At calibrated operating points on `expansion_val`, hard-negative FPR was reduced from 11.79% to 4.72%, short-scream recall reached 94.87%, and PR-AUC jumped from 0.7040 to 0.9224.
3. Candidate E1 now closely rivals Candidate B Baseline on validation data.
4. Independent test generalization cannot be claimed from validation improvements alone; an independent test cohort must be curated and evaluated.

---

## 5. Recommended Next Milestone (Stage 8.9.55)

1. **Curate Stage 8.9.55 Independent Test Cohort:** Acquire 400–500 authentic recordings from $\ge 150$ independent source groups under permissive commercial licensing.
2. **Execute Independent Head-to-Head Evaluation:** Evaluate retrained Candidate E1 ($\theta = 0.6800$) against frozen Candidate B Baseline ($\theta = 0.8000$) on the untouched Stage 8.9.55 cohort.
3. **Preserve Production Immutability:** Maintain all production assets in their frozen state.

