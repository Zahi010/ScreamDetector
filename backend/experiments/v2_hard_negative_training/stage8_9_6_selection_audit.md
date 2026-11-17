# Stage 8.9.6 — Formal Candidate Selection and Independent Evaluation Audit

**Role:** Senior Machine-Learning Validation Engineer  
**Workspace:** `backend/experiments/v2_hard_negative_training/`  
**Evaluation Status:** **Formal Candidate Audit Completed — NO Candidate Approved for Production**  
**Audit Date:** 2026-10-29  

---

## Executive Summary

Stage 8.9.6 executes an independent validation audit of the 5 experimental candidate models developed in Stage 8.9.5 against the pre-declared safety, reliability, and acoustic performance criteria. 

The audit independently recomputed all confusion matrices, continuous ROC/PR curves, Wilson score confidence intervals, and per-category false positive rates on the identical held-out test cohort (**189 binary evaluated recordings: 59 screams, 130 non-screams**, plus 1 quarantined ambiguous recording).

### Key Audit Findings

1. **Production Immutability Verified (100% Match):**
   The production classifier (`backend/models/scream_classifier.joblib`), metadata (`backend/models/model_metadata.json`), Stage 5 test predictions, and the SQLite review database were verified bit-for-bit against their authoritative SHA-256 hashes. Zero production files or review decisions were altered.
2. **Audit Verdict: NO CANDIDATE QUALIFIES for Production Deployment:**
   None of the 5 candidates satisfy the three pre-declared provisional acceptance criteria:
   - **Criterion 1 (Recall $\ge 96.0\%$):** **FAILED.** The highest recall achieved was **84.75%** (Model B), with a 95% confidence interval of $[73.5\%, 91.8\%]$. Even the optimistic upper bound falls 4.2 percentage points short of the life-safety target.
   - **Criterion 2 (Hard-Negative FPR $\le 5.0\%$):** **FAILED.** The lowest hard-negative FPR achieved was **16.15%** (Model A and Model D), more than triple the allowable 5.0% false alarm ceiling.
   - **Criterion 3 (Shouting FPR $\le 15.0\%$):** **FAILED.** While shouting false alarms were reduced by over 60% compared to Stage 8.9.3 ($52.94\%$), the best shouting FPR achieved was **20.93%** (Model A and Model D), exceeding the 15.0% threshold.
3. **Statistical Uncertainty & Sample Size Limitations:**
   With $N = 59$ positive screams in the held-out test cohort, the 95% confidence interval for recall spans $18.3$ percentage points ($[73.5\%, 91.8\%]$ for Model B). This cohort size is statistically incapable of certifying a $\ge 96.0\%$ recall guarantee at a 95% confidence level. A minimum of $\approx 250 - 300$ held-out screams would be required to statistically certify $\ge 96\%$ recall with a margin of error $\le \pm 2.0\%$.
4. **Methodological Inconsistency Detected in Model E:**
   Models A, B, C, and D were evaluated at the standard operational threshold of $0.35$. Model E (Two-Stage Hierarchical Gating) was evaluated at an arbitrary threshold of $0.25$ because the product of probabilities $P(\text{Vocal}) \times P(\text{Scream} \mid \text{Vocal})$ was uncalibrated. This uncalibrated threshold selection represents a methodological flaw in Model E's reporting.
5. **Label Integrity Confirmed:**
   The experimental relabeling of `fsd50k_349401` ("The crowd shouted Countdown") as `crowd_chant_cheering` (`non_scream`) exists exclusively in the versioned experimental manifest (`dataset_manifest_v2.json`). In the production review database (`database/stage8_9_reviews.db`), `fsd50k_349401` remains strictly `SCREAM_PRESENT`.

---

## 1. Production Integrity and Authoritative Hash Verification

The production classifier, metadata, historical Stage 5 benchmarks, and review database were audited before and after analysis:

| Artifact Path | Expected SHA-256 | Actual SHA-256 | Status |
| :--- | :--- | :--- | :--- |
| `backend/models/scream_classifier.joblib` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | **VERIFIED MATCH** |
| `backend/models/model_metadata.json` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | **VERIFIED MATCH** |
| `backend/reports/test_predictions.csv` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | **VERIFIED MATCH** |
| `backend/reports/stage5_test_evaluation.md` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | **VERIFIED MATCH** |

### SQLite Review Database Audit
- Total reviewed recordings in `database/stage8_9_reviews.db`: **343** (338 approved non-scream, 2 scream present, 3 ambiguous).
- `fsd50k_349401` recorded status: `SCREAM_PRESENT` (Proposed category: `crowd_cheering_applause`).
- Audit history count for `fsd50k_349401`: **0 modified records**.
- **Conclusion:** The database and append-only audit trail remain 100% intact and uncorrupted.

---

## 2. Evaluation Methodology Audit

An inspection of the training and evaluation codebase (`train_candidate_models.py`, `build_experimental_dataset.py`, and `extract_features_v2.py`) was conducted:

```
Methodology Compliance Audit
========================================================================================================
Audit Checkpoint                    Status      Validation Findings
--------------------------------------------------------------------------------------------------------
Data Leakage Prevention             PASSED      Train, Val, and Test splits are strictly disjoint across
                                                all 415 source groups (0 shared PCM hashes or groups).
Stage 5 Historical Isolation        PASSED      0 Stage 5 test recordings appear in Train or Val splits.
Validation-Only Tuning              PASSED      Hyperparameter C=0.05 for Model B was selected via grid
                                                sweep strictly on the validation partition.
Continuous Metric Computation       PASSED      ROC-AUC and PR-AUC were correctly calculated from continuous
                                                probabilities, not binarized predictions.
Threshold Selection Consistency     FAILED      Models A-D used threshold 0.35; Model E used an arbitrary
                                                uncalibrated threshold of 0.25 without cross-validation.
Input Feature Parity                PASSED      All models consume standardized 16kHz mono audio processed
                                                through the frozen Google YAMNet feature extractor.
Confusion Matrix Reconciliation     PASSED      All reported TP, FP, FN, TN values reconcile 100% with
                                                accuracy, precision, recall, specificity, and FPR.
========================================================================================================
```

---

## 3. Independently Recomputed Benchmark Metrics

The metrics for all five candidate architectures were recomputed from raw continuous model outputs on the held-out test split ($N = 189$ binary evaluated samples: 59 screams, 130 non-screams). The complete prediction log is exported to [`reports/stage8_9_6_test_predictions.csv`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/reports/stage8_9_6_test_predictions.csv).

```
Independently Audited Candidate Metrics on Held-Out Test Cohort (N=189)
========================================================================================================================
Model Architecture        Thresh   TP   FP   FN   TN    Accuracy   Precision  Recall     Specificity  Hard-Neg FPR  PR-AUC
------------------------------------------------------------------------------------------------------------------------
Model_A_Baseline_LR       0.350    42   21   17   109   79.89%     66.67%     71.19%     83.85%       16.15%        0.7539
Model_B_Regularized_LR    0.350    50   26    9   104   81.48%     65.79%     84.75%     80.00%       20.00%        0.7750
Model_C_P90_LR            0.350    48   26   11   104   80.42%     64.86%     81.36%     80.00%       20.00%        0.7717
Model_D_Concat_LR         0.350    45   21   14   109   81.48%     68.18%     76.27%     83.85%       16.15%        0.7878
Model_E_Hierarchical      0.250    42   24   17   106   78.31%     63.64%     71.19%     81.54%       18.46%        0.7191
========================================================================================================================
```

---

## 4. Confidence Intervals and Statistical Uncertainty Analysis

To prevent false certainty, 95% confidence intervals were computed for all key performance metrics. Wilson score intervals were used for binomial proportions ($N_{\text{pos}} = 59, N_{\text{neg}} = 130$), and 1,000 bootstrap iterations were used for AUC metrics. The complete table is exported to [`reports/stage8_9_6_confidence_intervals.csv`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/reports/stage8_9_6_confidence_intervals.csv).

```
95% Confidence Intervals for Candidate Models
========================================================================================================
Model Architecture        Metric              Point Estimate  95% Confidence Interval    Margin of Error
--------------------------------------------------------------------------------------------------------
Model_A_Baseline_LR       Recall              71.19%          [58.60%, 81.24%]           ± 11.32%
                          Hard-Negative FPR   16.15%          [10.84%, 23.36%]           ±  6.26%
                          Precision           66.67%          [54.34%, 77.08%]           ± 11.37%
                          PR-AUC              0.7539          [0.6341, 0.8524]           ±  0.1091
--------------------------------------------------------------------------------------------------------
Model_B_Regularized_LR    Recall              84.75%          [73.51%, 91.80%]           ±  9.15%
                          Hard-Negative FPR   20.00%          [14.04%, 27.67%]           ±  6.81%
                          Precision           65.79%          [54.60%, 75.46%]           ± 10.43%
                          PR-AUC              0.7750          [0.6620, 0.8655]           ±  0.1017
--------------------------------------------------------------------------------------------------------
Model_C_P90_LR            Recall              81.36%          [69.64%, 89.28%]           ±  9.82%
                          Hard-Negative FPR   20.00%          [14.04%, 27.67%]           ±  6.81%
                          Precision           64.86%          [53.46%, 74.80%]           ± 10.67%
                          PR-AUC              0.7717          [0.6580, 0.8687]           ±  0.1053
--------------------------------------------------------------------------------------------------------
Model_D_Concat_LR         Recall              76.27%          [64.03%, 85.30%]           ± 10.63%
                          Hard-Negative FPR   16.15%          [10.84%, 23.36%]           ±  6.26%
                          Precision           68.18%          [56.24%, 78.18%]           ± 10.97%
                          PR-AUC              0.7878          [0.6750, 0.8712]           ±  0.0981
--------------------------------------------------------------------------------------------------------
Model_E_Hierarchical      Recall              71.19%          [58.60%, 81.24%]           ± 11.32%
                          Hard-Negative FPR   18.46%          [12.74%, 25.99%]           ±  6.62%
                          Precision           63.64%          [51.55%, 74.22%]           ± 11.33%
                          PR-AUC              0.7191          [0.5920, 0.8315]           ±  0.1197
========================================================================================================
```

> [!CAUTION]
> **Statistical Significance & Sample Size Warning:**
> With 59 positive screams in the test set, the 95% confidence interval for Model B's recall is $[73.5\%, 91.8\%]$. While Model B's observed point estimate ($84.75\%$) represents a marked improvement over baseline Model A ($71.19\%$), the overlapping confidence intervals ($[58.6\%, 81.2\%]$ vs $[73.5\%, 91.8\%]$) demonstrate that small sample variance is substantial. It is statistically impossible to prove a $96\%$ recall guarantee with $N=59$.

---

## 5. Detailed Per-Category False Positive Rates and Denominators

The performance of each candidate was decomposed across the 8 acoustic categories in the held-out test cohort. The full breakdown is exported to [`reports/stage8_9_6_category_metrics.csv`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/reports/stage8_9_6_category_metrics.csv).

```
Category Breakdown: Test Samples, Positive Recalls, and Negative FPRs
========================================================================================================================
Category                    Total  Pos  Neg  Model A (Base)  Model B (Reg)   Model C (P90)   Model D (Concat) Model E (Hier)
------------------------------------------------------------------------------------------------------------------------
scream (clean)               40    40    0   Recall: 75.00%  Recall: 90.00%  Recall: 87.50%  Recall: 82.50%   Recall: 77.50%
masked_distant_screams       19    19    0   Recall: 63.16%  Recall: 73.68%  Recall: 68.42%  Recall: 63.16%   Recall: 57.89%
shouting_and_speech          43     0   43   FPR   : 20.93%  FPR   : 25.58%  FPR   : 25.58%  FPR   : 20.93%   FPR   : 27.91%
whistles_and_squeaks         29     0   29   FPR   : 10.34%  FPR   : 10.34%  FPR   : 20.69%  FPR   : 13.79%   FPR   :  3.45%
infant_crying                18     0   18   FPR   : 16.67%  FPR   : 22.22%  FPR   : 11.11%  FPR   : 11.11%   FPR   : 27.78%
sfx_sirens_fireworks         16     0   16   FPR   :  0.00%  FPR   :  6.25%  FPR   :  6.25%  FPR   :  6.25%   FPR   :  0.00%
crowd_chant_cheering         15     0   15   FPR   : 40.00%  FPR   : 46.67%  FPR   : 33.33%  FPR   : 33.33%   FPR   : 40.00%
general_environmental         9     0    9   FPR   :  0.00%  FPR   :  0.00%  FPR   : 11.11%  FPR   :  0.00%   FPR   :  0.00%
========================================================================================================================
```

---

## 6. Comprehensive Review of Candidate Trade-offs

### 1. Model B (Regularized Logistic Regression, $C=0.05$)
- **Strengths:** Achieves the highest recall across both clean screams (**90.00%**) and masked screams in festival noise (**73.68%**), producing the highest overall recall (**84.75%**).
- **Weaknesses:** Easing the $L_2$ regularization penalty increases susceptibility to false alarms. Overall hard-negative FPR rises to **20.00%** (26 false alarms on 130 non-screams), and shouting FPR rises to **25.58%**.
- **Verdict:** Unacceptable for deployment due to high false alarm rate.

### 2. Model D (Multi-Pooling Concatenation, 3072-dim)
- **Strengths:** Best overall PR-AUC (**0.7878**) and highest precision (**68.18%**). Equal lowest hard-negative FPR (**16.15%**) and lowest shouting FPR (**20.93%**). Incorporating steady-state mean background features significantly aids in noise rejection.
- **Weaknesses:** Recall drops to **76.27%** (14 missed screams out of 59). On masked screams, recall is only $63.16\%$.
- **Verdict:** Promising noise suppression architecture, but insufficient scream sensitivity.

### 3. Model E (Two-Stage Hierarchical Gating)
- **Strengths:** The front-end vocal gating filter eliminates non-vocal sounds with exceptional effectiveness: whistle/squeak FPR drops to **3.45%** (1 FP out of 29), and siren/firework FPR is **0.00%**.
- **Weaknesses:** Suffers from compound probability degradation ($P(\text{Vocal}) \times P(\text{Scream} \mid \text{Vocal})$). If a distant scream embedded in loud festival music is misclassified by the front-end as non-vocal, it is irreversibly lost. Consequently, masked scream recall drops to **57.89%**, and overall recall drops to **71.19%**.
- **Verdict:** Two-stage gating is too aggressive against masked screams and suffers from uncalibrated threshold selection.

### 4. Cross-Model Failure Modes (Crowd Chanting & Shouting)
- Across all five architectures, **crowd chanting remains an unsolved failure mode** ($33.33\% - 46.67\%$ FPR). The multi-voice acoustic power of unison crowds repeatedly triggers scream weights.
- Shouting FPR ($20.93\% - 27.91\%$) remains above the $15.0\%$ threshold, although it represents a major improvement over Stage 8.9.3's $52.94\%$.

---

## 7. Label Integrity and Annotation Rule Findings

1. **`fsd50k_349401` Relabeling Audit:**
   The experimental relabeling of `fsd50k_349401` ("The crowd shouted Countdown") as `crowd_chant_cheering` (`non_scream`) is isolated exclusively to the experimental dataset manifest. In the original human-review database (`database/stage8_9_reviews.db`), it remains `SCREAM_PRESENT`. The historical audit history has zero modifications.
2. **Evaluation of Annotation Rules (Fixed $F_0 > 600\text{ Hz}$ Guideline):**
   The Stage 8.9.5 guideline suggested $F_0 > 600\text{ Hz}$ as a hallmark of screams. Validation testing revealed that low-register adult male screams frequently exhibit fundamental frequencies between $350\text{ Hz} - 550\text{ Hz}$ with strong resonant harmonics in the $1.5 - 3.0\text{ kHz}$ band. A rigid $F_0 > 600\text{ Hz}$ rule would cause false rejections of legitimate male screams.
   - **Recommendation:** Revise the annotation guideline to treat $F_0$ as supporting evidence rather than a mandatory cutoff. Emphasize non-linear vocal fold phenomena (subharmonics, roughness) and absence of phonetic word articulation.

---

## 8. Formal Candidate Selection Decision

### Pre-Declared Provisional Acceptance Goals vs Best Achieved

| Performance Dimension | Pre-Declared Provisional Goal | Best Candidate Point Estimate | 95% Confidence Interval | Compliance Status |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Scream Recall** | $\ge \mathbf{96.0\%}$ | **84.75%** (Model B) | $[73.51\%, 91.80\%]$ | **FAILED** |
| **Hard-Negative FPR** | $\le \mathbf{5.0\%}$ | **16.15%** (Model A, D) | $[10.84\%, 23.36\%]$ | **FAILED** |
| **Shouting & Speech FPR** | $\le \mathbf{15.0\%}$ | **20.93%** (Model A, D) | $[11.30\%, 35.10\%]$ | **FAILED** |
| **Whistle & Squeak FPR** | $\le \mathbf{5.0\%}$ | **3.45%** (Model E) | $[0.61\%, 17.20\%]$ | **PASSED (Model E only)** |
| **Sirens & Fireworks FPR** | $\le \mathbf{5.0\%}$ | **0.00%** (Model A, E) | $[0.00\%, 19.38\%]$ | **PASSED (Model A, E)** |

### Formal Decision
**NO CANDIDATE QUALIFIES FOR FORMAL PROMOTION OR PRODUCTION DEPLOYMENT.**

The operational scream detector in production (`backend/models/scream_classifier.joblib`) must remain active at its frozen threshold of `0.3500`. Replacing or altering the production model at this stage would fail life-safety sensitivity requirements ($\approx 15\%$ missed screams) and introduce excessive false alarms in noisy crowd environments.

---

## 9. Recommended Next Engineering Steps (Roadmap for Stage 8.9.7+)

To close the gap between current candidate performance and the target operational specifications, the following controlled improvements are recommended:

1. **Hybrid Architecture (Multi-Pooling + Soft Vocal Gating):**
   Combine Model D's multi-pooling representation (3072-d) with Model E's vocal gating. Rather than multiplying uncalibrated probabilities, concatenate the vocal gating logit directly into a calibrated linear or tree-based ensemble.
2. **Targeted Acquisition of Crowd Chants & Countdown Audio:**
   Crowd chanting remains the highest source of false alarms ($33 - 46\%$ FPR). Acquire 150 additional unison stadium chants, concert countdowns, and festival crowd sing-alongs to populate the hard-negative training space.
3. **Calibrated Threshold Optimization via Cost-Benefit Loss:**
   Rather than applying ad-hoc thresholds ($0.35$ or $0.25$), formulate an explicit Bayes decision rule:
   $$\text{Alert if } P(\text{Scream}|x) \ge \tau^* = \frac{C_{\text{FP}}}{C_{\text{FP}} + C_{\text{FN}}}$$
   Calibrate $\tau^*$ strictly on the validation partition using isotonic regression or Platt scaling.
4. **Expand Held-Out Scream Benchmark ($N_{\text{pos}} \ge 250$):**
   Acquire and verify 200 additional diverse screams (female, male, child, distant, masked at $-6\text{ dB}$ to $+6\text{ dB}$) in the held-out test split to provide the statistical power necessary to prove $\ge 96\%$ recall with narrow confidence intervals ($\pm 2\%$).

---

## 10. Explicit Confirmation of Immutability

- **Production Model:** `backend/models/scream_classifier.joblib` (SHA-256: `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f`) remains **100% frozen and active**.
- **Production Metadata:** `backend/models/model_metadata.json` (SHA-256: `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60`) remains **100% frozen**.
- **Operational Threshold:** Preserved strictly at `0.3500`.
- **Review Database:** All 343 human review records and append-only audit histories remain unaltered.

*No model changes, replacements, or fine-tuning will occur without explicit user review and written instruction.*
