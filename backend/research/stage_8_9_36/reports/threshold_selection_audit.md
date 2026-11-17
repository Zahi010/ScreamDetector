# Stage 8.9.36 — Threshold & Operating-Point Audit Report

**Stage:** 8.9.36 — Deep Error Forensics & Validation Audit  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Dimension:** Methodology, Provenance, and Trade-Offs of Threshold Selection ($\theta^* = 0.4300$ vs. Historical/Production $\theta = 0.3500$)  
**Audit Artifacts:**
- Validation Sweep CSV: `backend/research/stage_8_9_36/evaluation/validation_threshold_sweep.csv`
- Threshold Comparison JSON: `backend/research/stage_8_9_36/evaluation/threshold_comparison.json`

---

## 1. Executive Summary & Provenance Verification

In Stage 8.9.35, research Candidate D (`MultiPathwayFusionModel`) was evaluated at an operating threshold of **$\theta^* = 0.4300$**, differing from the frozen production threshold of **$\theta = 0.3500$** and earlier research baselines.

An audit was conducted to verify whether this threshold:
1. Was selected strictly from validation data without test-set leakage.
2. Adhered to standard statistical learning protocols.
3. Successfully navigated the recall vs. false-positive trade-off.

### **Audit Verdict:**
- **PROVENANCE VERIFIED — METHODOLOGICALLY SOUND:** The threshold $\theta^* = 0.4300$ was selected **strictly on the independent validation split ($N=293$, 79 screams, 214 hard negatives)** by maximizing validation F1-score ($\text{Val } F_1 = 0.7861$).
- **ZERO TEST LEAKAGE:** Zero test-set labels or test predictions were used in threshold determination.
- **PRODUCTION THRESHOLD PRESERVED:** The production threshold remains strictly frozen at **$0.3500$**.

---

## 2. Validation Split Threshold Sweep Analysis

The validation partition was swept across $\theta \in [0.20, 0.60]$ in $0.01$ increments. Below is the behavior around key operating regions:

| Operating Threshold $\theta$ | Val Recall | Val HN-FPR | Val Precision | Val Specificity | Val $F_1$-Score | Val Shout-FPR | Val Cry-FPR | Status / Significance |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **0.25** | 88.61% | 20.56% | 61.40% | 79.44% | 0.7254 | 17.57% | 10.53% | High sensitivity, excessive false alarms |
| **0.30** | 88.61% | 17.76% | 64.81% | 82.24% | 0.7487 | 14.86% | 10.53% | Sub-optimal precision |
| **0.35 (Production Reference)** | 87.34% | 14.95% | 68.32% | 85.05% | 0.7667 | 13.51% | 5.26% | Historical reference point |
| **0.40** | 86.08% | 13.55% | 70.10% | 86.45% | 0.7727 | 13.51% | 5.26% | Approaching peak efficiency |
| **0.41** | 86.08% | 12.62% | 71.58% | 87.38% | 0.7816 | 13.51% | 5.26% | Sharp false alarm reduction |
| **0.42** | 86.08% | 12.62% | 71.58% | 87.38% | 0.7816 | 13.51% | 5.26% | False alarms held constant |
| **0.43 (Frozen Research $\theta^*$)**| **86.08%** | **12.15%** | **72.34%** | **87.85%** | **0.7861** | **12.16%** | **5.26%** | **Global Maximum Validation $F_1$** |
| **0.44** | 83.54% | 12.15% | 71.74% | 87.85% | 0.7719 | 12.16% | 5.26% | Recall cliffs (-2.54%), F1 drops |
| **0.45** | 83.54% | 11.68% | 72.53% | 88.32% | 0.7765 | 12.16% | 5.26% | Ineffective trade-off |
| **0.50** | 78.48% | 11.68% | 71.26% | 88.32% | 0.7470 | 12.16% | 5.26% | Unacceptable recall suppression |

---

## 3. Impact of Operating Threshold on Test Cohort ($N=293$)

To understand the empirical consequences of operating point selection, Candidate D's predictions on the independent test set were computed at both $\theta = 0.3500$ and $\theta = 0.4300$:

| Metric | Candidate D at $\theta = 0.3500$ | Candidate D at $\theta = 0.4300$ (Frozen) | Operating Shift Impact |
| :--- | :---: | :---: | :--- |
| **True Positives (TP)** | 93 / 102 | 91 / 102 | -2 screams detected |
| **False Negatives (FN)** | 9 / 102 | 11 / 102 | +2 screams missed |
| **False Positives (FP)** | 28 / 191 | 19 / 191 | **-9 false alarms eliminated** |
| **True Negatives (TN)** | 163 / 191 | 172 / 191 | +9 correct rejections |
| **Overall Scream Recall** | **91.18%** | **89.22%** | Recall reduced by -1.96% |
| **Hard-Negative FPR** | **14.66%** | **9.95%** | **FPR reduced by -4.71% (32% relative drop)** |
| **Shouted-Speech FPR** | **16.67% (8/48)** | **14.58% (7/48)** | **Gate 3 passed ($\le 15\%$) at 0.43; failed at 0.35** |
| **Infant-Cry FPR** | 6.67% (1/15) | 6.67% (1/15) | Identical (1 cry false positive) |
| **Crowd-Cheering FPR** | 23.81% (10/42) | 16.67% (7/42) | Cheering false alarms dropped by 30% |
| **Precision** | 76.86% | 82.73% | Precision improved by +5.87% |
| **F1-Score** | 0.8341 | 0.8585 | Overall F1 improved by +0.0244 |

---

## 4. Key Scientific Insights

1. **Gate 3 Compliance Depended on $\theta = 0.43$:**
   - Had the model been operated at $\theta = 0.3500$, Shouted-Speech FPR would have been **16.67%**, failing Gate 3 ($\le 15.00\%$). Raising the threshold to 0.43 brought Shout-FPR down to **14.58%**, allowing Gate 3 to pass.
2. **The Convexity Cliff at 0.44:**
   - In validation data, $\theta = 0.43$ sits directly at an inflection point. Beyond 0.43, recall drops steeply from 86.08% to 83.54% with zero reduction in false positives. Thus, 0.43 represents the mathematically optimal operating threshold on validation data.
3. **Threshold vs. Model Limitation:**
   - Adjusting the threshold merely slides along the ROC curve: at 0.35, recall is 91.18% but HN-FPR is 14.66%; at 0.43, recall is 89.22% but HN-FPR is 9.95%.
   - **Crucial Deduction:** No threshold exists on this ROC curve that can simultaneously achieve Recall $\ge 96.00\%$ and HN-FPR $\le 5.00\%$. The failure to pass both gates is an intrinsic representation limitation, not a threshold tuning defect.
