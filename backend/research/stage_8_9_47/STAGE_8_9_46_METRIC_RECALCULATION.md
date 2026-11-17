# Stage 8.9.46 Metric & Provenance Recalculation Audit

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.

---

## 1. Executive Summary & Verification Objectives

Prior to acquiring or evaluating a new independent evaluation cohort in Stage 8.9.47, an exhaustive recalculation audit of Stage 8.9.46 was conducted directly against raw prediction arrays and dataset manifests.

### Key Audit Findings:
1. **Candidate R5 Holdout Verification:** Exact match confirmed. Observed counts on `v5_final_holdout` ($N=205$): **52 TP, 17 FN, 3 FP, 133 TN**. Recall = 75.36% (52/69), Precision = 94.55% (52/55), F1 = 83.87%, Hard-Negative FPR = **2.21% (3/136)**, Shouted-Speech FPR = 7.14% (1/14).
2. **Candidate R3 Holdout Verification:** Exact match confirmed. Observed counts on `v5_final_holdout` ($N=205$): **49 TP, 20 FN, 3 FP, 133 TN**. Recall = 71.01% (49/69), Precision = 94.23% (49/52), F1 = 80.99%, Hard-Negative FPR = **2.21% (3/136)**, Shouted-Speech FPR = 7.14% (1/14).
3. **Denominators Reconciled:** All 10 candidates were evaluated on identical, sealed test sets: `v5_development_test` ($N=202$: 81 screams, 121 negatives) and `v5_final_holdout` ($N=205$: 69 screams, 136 negatives).
4. **Validation-Only Operating Points:** Operating thresholds ($	heta^*_{\text{R5}} = 0.8700$, $	heta^*_{\text{R3}} = 0.8400$, $	heta^*_{\text{R1}} = 0.8700$) were calibrated strictly on `v5_validation` ($N=309$: 117 screams, 192 negatives) to satisfy $\text{HN-FPR} \le 5.0\%$. Zero holdout test labels were inspected during threshold selection.
5. **Source-Group Integrity Audit:** The 95 unseen source groups in `v5_final_holdout` exhibit **zero overlap** with training ($0/728$), validation ($0/124$), or development test ($0/82$). Multi-clip clusters (e.g. `fsd50k_uploader_xtrgamr` with 17 clips, `reinsamba` with 9 clips) prove that source groups represent genuine acoustic creators/uploaders rather than arbitrary file identifiers.

---

## 2. Recalculated Holdout Metrics Table (v5_final_holdout, N=205)

| Candidate Configuration | $\theta^*$ | TP | FN | FP | TN | Recall (95% CI) | Precision | F1 | HN-FPR | Shout FPR | Short Rec | Masked Rec | Distant Rec | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Candidate R5 (Ratio-0P-100A)** | 0.8700 | 52 | 17 | 3 | 133 | 75.36% [64.04%, 84.01%] | 94.55% | 83.87% | 2.21% | 7.14% | 17/17 (100.0%) | 10/16 (62.50%) | 11/18 (61.11%) | 0.9487 |
| **Candidate R3 (Ratio-50P-50A)** | 0.8400 | 49 | 20 | 3 | 133 | 71.01% [59.43%, 80.38%] | 94.23% | 80.99% | 2.21% | 7.14% | 15/17 (88.2%) | 9/16 (56.25%) | 10/18 (55.56%) | 0.9582 |
| **Candidate R1 (Ratio-100P-0A)** | 0.8700 | 51 | 18 | 6 | 130 | 73.91% [62.49%, 82.81%] | 89.47% | 80.95% | 4.41% | 7.14% | 16/17 (94.1%) | 9/16 (56.25%) | 10/18 (55.56%) | 0.9488 |
| **Candidate R2 (Ratio-75P-25A)** | 0.9000 | 49 | 20 | 4 | 132 | 71.01% [59.43%, 80.38%] | 92.45% | 80.33% | 2.94% | 7.14% | 16/17 (94.1%) | 7/16 (43.75%) | 8/18 (44.44%) | 0.9519 |
| **Candidate R4 (Ratio-25P-75A)** | 0.7600 | 52 | 17 | 9 | 127 | 75.36% [64.04%, 84.01%] | 85.25% | 80.00% | 6.62% | 10.71% | 17/17 (100.0%) | 10/16 (62.50%) | 11/18 (61.11%) | 0.9506 |
| **Candidate R6 (Dynamic-50P-50A)** | 0.9300 | 50 | 19 | 6 | 130 | 72.46% [60.95%, 81.61%] | 89.29% | 80.00% | 4.41% | 7.14% | 15/17 (88.2%) | 10/16 (62.50%) | 11/18 (61.11%) | 0.9435 |
| **Candidate A (Config-B Baseline)** | 0.6500 | 52 | 17 | 5 | 131 | 75.36% [64.04%, 84.01%] | 91.23% | 82.54% | 3.68% | 7.14% | 17/17 (100.0%) | 8/16 (50.00%) | 9/18 (50.00%) | 0.9487 |
| **Candidate B (Config-B Mask-v6)** | 0.8000 | 50 | 19 | 6 | 130 | 72.46% [60.95%, 81.61%] | 89.29% | 80.00% | 4.41% | 7.14% | 17/17 (100.0%) | 11/16 (68.75%) | 12/18 (66.67%) | 0.9531 |
| **Candidate F (Config-B MaskEarlyRIR)** | 0.8200 | 52 | 17 | 8 | 128 | 75.36% [64.04%, 84.01%] | 86.67% | 80.62% | 5.88% | 10.71% | 16/17 (94.1%) | 12/16 (75.00%) | 13/18 (72.22%) | 0.9519 |
| **Candidate G (Config-B ProbMixed-v7)** | 0.8500 | 52 | 17 | 7 | 129 | 75.36% [64.04%, 84.01%] | 88.14% | 81.25% | 5.15% | 10.71% | 17/17 (100.0%) | 11/16 (68.75%) | 12/18 (66.67%) | 0.9474 |

---

## 3. Recalculated Development Test Metrics Table (v5_development_test, N=202)

| Candidate Configuration | $\theta^*$ | TP | FN | FP | TN | Recall (95% CI) | Precision | F1 | HN-FPR | Shout FPR | Short Rec | Masked Rec | Distant Rec | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Candidate R5 (Ratio-0P-100A)** | 0.8700 | 67 | 14 | 5 | 116 | 82.72% [73.05%, 89.42%] | 93.06% | 87.58% | 4.13% | 2.94% | 23/23 (100.0%) | 12/17 (70.59%) | 11/16 (68.75%) | 0.9633 |
| **Candidate R3 (Ratio-50P-50A)** | 0.8400 | 65 | 16 | 3 | 118 | 80.25% [70.30%, 87.46%] | 95.59% | 87.25% | 2.48% | 0.00% | 23/23 (100.0%) | 10/17 (58.82%) | 9/16 (56.25%) | 0.9657 |
| **Candidate R1 (Ratio-100P-0A)** | 0.8700 | 69 | 12 | 3 | 118 | 85.19% [75.87%, 91.32%] | 95.83% | 90.20% | 2.48% | 0.00% | 23/23 (100.0%) | 11/17 (64.71%) | 10/16 (62.50%) | 0.9683 |
| **Candidate R2 (Ratio-75P-25A)** | 0.9000 | 67 | 14 | 4 | 117 | 82.72% [73.05%, 89.42%] | 94.37% | 88.16% | 3.31% | 2.94% | 23/23 (100.0%) | 11/17 (64.71%) | 10/16 (62.50%) | 0.9640 |
| **Candidate R4 (Ratio-25P-75A)** | 0.7600 | 66 | 15 | 7 | 114 | 81.48% [71.67%, 88.44%] | 90.41% | 85.71% | 5.79% | 0.00% | 23/23 (100.0%) | 12/17 (70.59%) | 11/16 (68.75%) | 0.9646 |
| **Candidate R6 (Dynamic-50P-50A)** | 0.9300 | 62 | 19 | 3 | 118 | 76.54% [66.25%, 84.44%] | 95.38% | 84.93% | 2.48% | 0.00% | 21/23 (91.3%) | 11/17 (64.71%) | 10/16 (62.50%) | 0.9744 |
| **Candidate A (Config-B Baseline)** | 0.6500 | 62 | 19 | 4 | 117 | 76.54% [66.25%, 84.44%] | 93.94% | 84.35% | 3.31% | 2.94% | 23/23 (100.0%) | 9/17 (52.94%) | 8/16 (50.00%) | 0.9601 |
| **Candidate B (Config-B Mask-v6)** | 0.8000 | 64 | 17 | 4 | 117 | 79.01% [68.93%, 86.46%] | 94.12% | 85.91% | 3.31% | 0.00% | 23/23 (100.0%) | 11/17 (64.71%) | 10/16 (62.50%) | 0.9667 |
| **Candidate F (Config-B MaskEarlyRIR)** | 0.8200 | 67 | 14 | 3 | 118 | 82.72% [73.05%, 89.42%] | 95.71% | 88.74% | 2.48% | 0.00% | 23/23 (100.0%) | 12/17 (70.59%) | 11/16 (68.75%) | 0.9686 |
| **Candidate G (Config-B ProbMixed-v7)** | 0.8500 | 64 | 17 | 4 | 117 | 79.01% [68.93%, 86.46%] | 94.12% | 85.91% | 3.31% | 0.00% | 23/23 (100.0%) | 11/17 (64.71%) | 10/16 (62.50%) | 0.9667 |

---

## 4. Source-Group Independence & Lineage Breakdown

- **Total Unique Source Groups in Holdout:** 95
- **Single-Recording Source Groups:** 44
- **Multi-Recording Source Groups:** 51 (largest cluster: 17 recordings)
- **Cross-Partition Overlap:** Exactly 0 collisions across train, validation, and development test partitions.

---

## 5. Audit Conclusion

The Stage 8.9.46 metric audit is verified with 100% numerical concordance. Candidates R5 and R3 are certified as reproducible baselines with frozen validation thresholds of `0.8700` and `0.8400` respectively.
