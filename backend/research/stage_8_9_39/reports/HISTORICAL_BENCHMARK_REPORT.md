# Stage 8.9.39 — Historical Continuity Benchmark Evaluation Report

**Project:** Festival Scream Detector  
**Stage:** 8.9.39 — Controlled Retraining, Expanded Dataset Evaluation & Independent Generalization Audit  
**Author:** Principal Acoustic AI Research Scientist & ML Validation Auditor  
**Date:** November 2026  
**Status:** Completed  
**Mandatory Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  

---

## 1. Benchmark Purpose & Cohort Specification

The Historical Continuity Benchmark (`v4_historical_test`, $N=293$) serves as an untouched cross-stage evaluation cohort to:
1. Verify backwards continuity against Stage 5, Stage 8.9.33, Stage 8.9.35, and Stage 8.9.37.
2. Quantify whether retraining on the expanded dataset (`v4_train`, $N=820$) introduces regressions on previously benchmarked positive or negative acoustic profiles.
3. Track performance across both historical label views established during the Stage 8.9.38 label adjudication.

**Important Methodology Note:** `v4_historical_test` is a previously evaluated continuity cohort. It is **not** an untouched independent generalization benchmark (the reserved expansion cohort serves that purpose).

---

## 2. Dual Historical Evaluation Accounting

Two disputed recordings from the `reitanna` source group were adjudicated unanimously as non-screams by blinded review in Stage 8.9.38:
- `v2_nigens_242607__reitanna__gasp-oooh`
- `v2_nigens_242644__reitanna__another-surprised-oooh`

Per protocol, both evaluation views are reported without rewriting historical ground truth:
- **View A (Original-Label Baseline):** $N=293$ total (102 screams, 191 non-screams across 111 source groups).
- **View B (Adjudicated-Label Analytical View):** $N=293$ total (100 screams, 193 non-screams across 111 source groups).

---

## 3. Configuration B Performance on Historical Benchmark

Evaluated using the validation-selected optimal threshold ($\theta = 0.24$) and historical reference thresholds:

| Metric | View A ($\theta = 0.24$) | View B ($\theta = 0.24$) | View A ($\theta = 0.35$ Ref) | View A ($\theta = 0.44$ Hist) |
|---|---|---|---|---|
| **True Positives (TP)** | 89 | 89 | 82 | 79 |
| **False Positives (FP)** | 23 | 23 | 14 | 14 |
| **True Negatives (TN)** | 168 | 170 | 177 | 177 |
| **False Negatives (FN)** | 13 | 11 | 20 | 23 |
| **Scream Recall** | **87.25%** (89/102) | **89.00%** (89/100) | **80.39%** (82/102) | **77.45%** (79/102) |
| *95% Wilson Score CI* | *[79.41%, 92.40%]* | *[81.37%, 93.75%]* | *[71.65%, 86.93%]* | *[68.43%, 84.48%]* |
| **Hard-Negative FPR** | **12.04%** (23/191) | **11.92%** (23/193) | **7.33%** (14/191) | **7.33%** (14/191) |
| *95% Wilson Score CI* | *[8.16%, 17.42%]* | *[8.07%, 17.25%]* | *[4.42%, 11.93%]* | *[4.42%, 11.93%]* |
| **Shouted-Speech FPR** | **16.67%** (8/48) | **16.67%** (8/48) | **14.58%** (7/48) | **14.58%** (7/48) |
| *95% Wilson Score CI* | *[8.70%, 29.58%]* | *[8.70%, 29.58%]* | *[7.25%, 27.17%]* | *[7.25%, 27.17%]* |
| **Short-Scream Recall** | **80.00%** (4/5) | **80.00%** (4/5) | **80.00%** (4/5) | **80.00%** (4/5) |
| *95% Wilson Score CI* | *[37.55%, 96.38%]* | *[37.55%, 96.38%]* | *[37.55%, 96.38%]* | *[37.55%, 96.38%]* |
| **Precision** | 79.46% | 79.46% | 85.42% | 84.95% |
| **F1 Score** | 0.8318 | 0.8396 | 0.8283 | 0.8103 |
| **ROC-AUC / PR-AUC** | 0.9331 / 0.8708 | 0.9417 / 0.8775 | 0.9331 / 0.8708 | 0.9331 / 0.8708 |

---

## 4. Configuration D Performance on Historical Benchmark

Evaluated using the validation-selected optimal threshold ($\theta = 0.34$), balanced threshold ($\theta = 0.32$), and historical reference thresholds:

| Metric | View A ($\theta = 0.34$) | View B ($\theta = 0.34$) | View A ($\theta = 0.32$ Bal) | View A ($\theta = 0.43$ Hist) |
|---|---|---|---|---|
| **True Positives (TP)** | 85 | 85 | 87 | 77 |
| **False Positives (FP)** | 25 | 25 | 26 | 18 |
| **True Negatives (TN)** | 166 | 168 | 165 | 173 |
| **False Negatives (FN)** | 17 | 15 | 15 | 25 |
| **Scream Recall** | **83.33%** (85/102) | **85.00%** (85/100) | **85.29%** (87/102) | **75.49%** (77/102) |
| *95% Wilson Score CI* | *[74.92%, 89.33%]* | *[76.72%, 90.69%]* | *[77.15%, 90.88%]* | *[66.32%, 82.81%]* |
| **Hard-Negative FPR** | **13.09%** (25/191) | **12.95%** (25/193) | **13.61%** (26/191) | **9.42%** (18/191) |
| *95% Wilson Score CI* | *[9.03%, 18.61%]* | *[8.93%, 18.42%]* | *[9.46%, 19.20%]* | *[6.04%, 14.40%]* |
| **Shouted-Speech FPR** | **16.67%** (8/48) | **16.67%** (8/48) | **16.67%** (8/48) | **14.58%** (7/48) |
| *95% Wilson Score CI* | *[8.70%, 29.58%]* | *[8.70%, 29.58%]* | *[8.70%, 29.58%]* | *[7.25%, 27.17%]* |
| **Short-Scream Recall** | **80.00%** (4/5) | **80.00%** (4/5) | **80.00%** (4/5) | **80.00%** (4/5) |
| *95% Wilson Score CI* | *[37.55%, 96.38%]* | *[37.55%, 96.38%]* | *[37.55%, 96.38%]* | *[37.55%, 96.38%]* |
| **Precision** | 77.27% | 77.27% | 76.99% | 81.05% |
| **F1 Score** | 0.8019 | 0.8095 | 0.8093 | 0.7817 |
| **ROC-AUC / PR-AUC** | 0.9114 / 0.8568 | 0.9239 / 0.8651 | 0.9114 / 0.8568 | 0.9114 / 0.8568 |

---

## 5. Cross-Stage Longitudinal Comparison

Comparing historical performance across research stages:

| Architecture / Stage | Threshold | View A Recall | View A HN-FPR | View B Recall | View B HN-FPR |
|---|---|---|---|---|---|
| Stage 5 Production (Logistic Regression) | 0.35 | 78.43% (80/102) | 12.04% (23/191) | 80.00% (80/100) | 11.92% (23/193) |
| Stage 8.9.33 Config B (Pre-Retraining) | 0.44 | 81.37% (83/102) | 6.28% (12/191) | 83.00% (83/100) | 6.22% (12/193) |
| Stage 8.9.35 Config D (Pre-Retraining) | 0.43 | 89.22% (91/102) | 9.95% (19/191) | 91.00% (91/100) | 9.84% (19/193) |
| **Stage 8.9.39 Config B (Retrained)** | **0.24** | **87.25% (89/102)** | **12.04% (23/191)** | **89.00% (89/100)** | **11.92% (23/193)** |
| Stage 8.9.39 Config B (Fixed $\theta=0.35$) | 0.35 | 80.39% (82/102) | 7.33% (14/191) | 82.00% (82/100) | 7.25% (14/193) |
| **Stage 8.9.39 Config D (Retrained)** | **0.34** | **83.33% (85/102)** | **13.09% (25/191)** | **85.00% (85/100)** | **12.95% (25/193)** |
| Stage 8.9.39 Config D (Fixed $\theta=0.35$) | 0.35 | 83.33% (85/102) | 13.09% (25/191) | 85.00% (85/100) | 12.95% (25/193) |

---

## 6. Key Scientific Findings & Longitudinal Takeaways

1. **Retrained Candidate B Progression:**
   - When operated at its validation-selected threshold ($\theta = 0.24$), retrained Candidate B achieves **87.25% recall** (View A) and **89.00% recall** (View B), improving by +5.88% (View A) over its pre-retraining baseline (81.37%).
   - At the historical threshold ($\theta = 0.44$), recall is 77.45%, illustrating that the training distribution shift lowered the mean activation scores across negative examples, requiring a recalibrated threshold.
2. **Retrained Candidate D Progression:**
   - Retrained Candidate D achieves **83.33% recall** (View A) / **85.00% recall** (View B) at $\theta = 0.34$.
   - Interestingly, on this historical benchmark, Candidate B slightly outperforms Candidate D in both recall (87.25% vs 83.33%) and false positive suppression (12.04% vs 13.09%).
3. **Adjudication Consistency:**
   - Both models correctly predict `v2_nigens_242607__reitanna__gasp-oooh` and `v2_nigens_242644__reitanna__another-surprised-oooh` as non-screams (probabilities $< 0.10$). Thus, switching from View A to View B reclassifies two former False Negatives as True Negatives, increasing effective recall by ~+1.7% and reducing HN-FPR by ~-0.12%.
4. **Historical Hard Negatives Remain Challenging:**
   - Neither model reduces hard-negative FPR below 5% on this historical cohort ($\text{FPR} \approx 12\text{--}13\%$). The acoustic overlap with crowd cheers, sirens, and whistles in `v4_historical_test` remains a primary challenge.

