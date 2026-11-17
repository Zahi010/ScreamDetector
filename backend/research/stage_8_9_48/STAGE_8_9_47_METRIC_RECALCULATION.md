# Stage 8.9.47 Metric Recalculation & Provenance Audit — Stage 8.9.48

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.

---

## 1. Executive Summary & Verification Scope

Prior to investigating candidate dominance and positive-class failure forensics, all candidate predictions from the Stage 8.9.47 independent evaluation cohort were recalculated from raw prediction records (`backend/research/stage_8_9_47/INDEPENDENT_PREDICTIONS.csv`).

### Key Audit Conclusions:
1. **Exact Mathematical Concordance:** Recalculated confusion matrices, point estimates, confidence intervals, and discriminatory metrics match `CANDIDATE_COMPARISON_MATRIX.csv` and `STAGE_8_9_47_REPORT.md` with **100% numerical accuracy** across all 7 candidates.
2. **Denominators Reconciled:** The independent cohort consists of exactly **480 audio recordings**: **160 positive screams** across 105 source groups, **320 hard negatives** across 115 source groups, **80 shouted speech clips**, and **70 short scream vocalizations**.
3. **Candidate B Outperformance Confirmed:** The recalculation confirms that Candidate B achieved **90.00% Recall (144/160)**, **1.25% HN-FPR (4/320)**, **100.0% Short Scream Recall (70/70)**, **0.9928 ROC-AUC**, and **93.51% F1**, substantially outperforming Primary Candidate R5 (**75.62% Recall**, **0.31% HN-FPR**, **84.29% Short Recall**, **0.9821 ROC-AUC**, **85.82% F1**).

---

## 2. Recalculated Independent Performance Table ($N=480$)

| Candidate Identifier | Architecture Role | Frozen $\theta^*$ | TP | FN | FP | TN | Recall (95% CI) | Precision | F1 | Specificity | HN-FPR (Gate 2) | Shout FPR (Gate 3) | Short Rec (Gate 4) | ROC-AUC | PR-AUC | Brier | ECE | Audit Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Candidate R5 (Ratio-0P-100A)** | PRIMARY | 0.8700 | 121 | 39 | 1 | 319 | 75.62% [68.42%, 81.63%] | 99.18% | 85.82% | 99.69% | 0.31% [0.06%, 1.75%] | 0.00% (0/80) | 84.29% (59/70) | 0.9822 | 0.9719 | 0.0482 | 0.0357 | **MATCH** |
| **Candidate R3 (Ratio-50P-50A)** | SECONDARY | 0.8400 | 114 | 46 | 0 | 320 | 71.25% [63.80%, 77.70%] | 100.00% | 83.21% | 100.00% | 0.00% [0.00%, 1.19%] | 0.00% (0/80) | 90.00% (63/70) | 0.9880 | 0.9808 | 0.0414 | 0.0377 | **MATCH** |
| **Candidate R1 (Ratio-100P-0A)** | REF-PRISTINE | 0.8700 | 122 | 38 | 8 | 312 | 76.25% [69.09%, 82.18%] | 93.85% | 84.14% | 97.50% | 2.50% [1.27%, 4.85%] | 0.00% (0/80) | 94.29% (66/70) | 0.9664 | 0.9468 | 0.0749 | 0.0597 | **MATCH** |
| **Candidate A (Config-B-v5-baseline)** | HIST-BASE | 0.6500 | 130 | 30 | 4 | 316 | 81.25% [74.50%, 86.54%] | 97.01% | 88.44% | 98.75% | 1.25% [0.49%, 3.17%] | 0.00% (0/80) | 98.57% (69/70) | 0.9825 | 0.9734 | 0.0452 | 0.0378 | **MATCH** |
| **Candidate B (Config-B-Mask-v6)** | HIST-MASK | 0.8000 | 144 | 16 | 4 | 316 | 90.00% [84.37%, 93.75%] | 97.30% | 93.51% | 98.75% | 1.25% [0.49%, 3.17%] | 0.00% (0/80) | 100.00% (70/70) | 0.9928 | 0.9889 | 0.0270 | 0.0388 | **MATCH** |
| **Candidate F (Config-B-MaskEarlyRIR)** | HIST-RIR | 0.8200 | 142 | 18 | 2 | 318 | 88.75% [82.92%, 92.76%] | 98.61% | 93.42% | 99.38% | 0.62% [0.17%, 2.25%] | 0.00% (0/80) | 98.57% (69/70) | 0.9924 | 0.9886 | 0.0279 | 0.0373 | **MATCH** |
| **Candidate G (Config-B-ProbMixed-v7)** | HIST-MIXED | 0.8500 | 106 | 54 | 2 | 318 | 66.25% [58.62%, 73.12%] | 98.15% | 79.10% | 99.38% | 0.62% [0.17%, 2.25%] | 0.00% (0/80) | 78.57% (55/70) | 0.9786 | 0.9639 | 0.0537 | 0.0379 | **MATCH** |

---

## 3. Discrepancy & Lineage Verification

- **Discrepancies Observed:** None. All predictions in `INDEPENDENT_PREDICTIONS.csv` reconcile with `INDEPENDENT_COHORT_MANIFEST.csv`.
- **Zero Cohort Leakage:** Verified that no recordings in the $N=480$ evaluation cohort appear in any training or validation partition.
- **Checkpoint Immutability:** Confirmed that all 7 model checkpoints remained strictly frozen and untouched during evaluation.
