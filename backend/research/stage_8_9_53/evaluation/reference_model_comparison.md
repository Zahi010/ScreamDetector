# Reference Model Comparison Report — Stage 8.9.53

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Multi-Candidate Performance Matrix

All three models evaluated on the exact same **366 independent recordings** across 140 source groups:

| Performance Metric | Candidate B Baseline ($\theta=0.8000$) | Candidate B + Intervention D | Candidate E ($\theta=0.4000$) |
|---|---|---|---|
| **True Positives (TP)** | 73 / 102 | 73 / 102 | **64 / 102** |
| **False Negatives (FN)** | 29 / 102 | 29 / 102 | **38 / 102** |
| **True Negatives (TN)** | 259 / 264 | 259 / 264 | **221 / 264** |
| **False Positives (FP)** | 5 / 264 | 5 / 264 | **43 / 264** |
| **Overall Scream Recall** | 71.57% [62.16%, 79.42%] | 71.57% [62.16%, 79.42%] | **62.75% [53.06%, 71.51%]** |
| **Hard-Negative FPR** | 1.89% [0.81%, 4.36%] | 1.89% [0.81%, 4.36%] | **16.29% [12.32%, 21.22%]** |
| **Precision** | 93.59% [85.86%, 97.23%] | 93.59% [85.86%, 97.23%] | **59.81% [50.34%, 68.61%]** |
| **F1 Score** | 81.11% | 81.11% | **61.24%** |
| **Specificity** | 98.11% | 98.11% | **83.71%** |
| **Accuracy** | 90.71% | 90.71% | **77.87%** |
| **ROC-AUC** | 0.9746 | 0.9746 | **0.8128** |
| **PR-AUC** | 0.9392 | 0.9392 | **0.6609** |
| **Brier Score** | 0.0629 | 0.0629 | **0.1704** |
| **ECE** | 0.0589 | 0.0589 | **0.1474** |

---

## 2. Subgroup Direct Comparison

| Subgroup | Denom | Cand B Baseline | Cand B + Interv D | Candidate E |
|---|---|---|---|---|
| **All Authentic Screams** | 102 | 73 (71.57%) | 73 (71.57%) | **64 (62.75%)** |
| **Short Screams (<1.0s)** | 22 | 20 (90.91%) | 20 (90.91%) | **19 (86.36%)** |
| **Ultra-Short Screams (<0.5s)** | 8 | 8 (100.00%) | 8 (100.00%) | **7 (87.50%)** |
| **Standard-Short Screams (0.5-1.0s)** | 14 | 12 (85.71%) | 12 (85.71%) | **12 (85.71%)** |
| **Low-Intensity / Muffled Screams** | 3 | 3 (100.00%) | 3 (100.00%) | **3 (100.00%)** |
| **Crowd-Masked Screams** | 29 | 24 (82.76%) | 24 (82.76%) | **21 (72.41%)** |
| **Sustained Screams (>=1.0s)** | 80 | 53 (66.25%) | 53 (66.25%) | **45 (56.25%)** |
| **All Hard Negatives** | 264 | 5 (1.89%) | 5 (1.89%) | **43 (16.29%)** |
| **Shouted Speech** | 111 | 2 (1.80%) | 2 (1.80%) | **9 (8.11%)** |
| **Crowd Cheering / Chanting** | 55 | 1 (1.82%) | 1 (1.82%) | **17 (30.91%)** |
| **Whistles and Squeaks** | 32 | 1 (3.12%) | 1 (3.12%) | **9 (28.12%)** |
| **Other Vocalizations / Environmental** | 40 | 0 (0.00%) | 0 (0.00%) | **7 (17.50%)** |

---

## 3. Paired Statistical Comparisons (McNemar's Tests)

### Candidate E vs. Candidate B Baseline
- **Overall Concordance:** Chi-square = 28.2133, $p = 1.0865e-07$ (Statistically Significant)
  - Discordant pairs: Candidate E correct & Candidate B wrong ($n_{10}$) = **14**; Candidate B correct & Candidate E wrong ($n_{01}$) = **61**.
- **Positive-Class Concordance:** Chi-square = 2.2069, $p = 1.3739e-01$ (E correct / B wrong = 10, B correct / E wrong = 19).
- **Negative-Class Concordance:** Chi-square = 29.7609, $p = 4.8876e-08$ (E correct / B wrong = 4, B correct / E wrong = 42).

### Candidate E vs. Candidate B + Intervention D
- **Overall Concordance:** Chi-square = 28.2133, $p = 1.0865e-07$ (Statistically Significant)
  - Discordant pairs: Candidate E correct & D wrong ($n_{10}$) = **14**; D correct & Candidate E wrong ($n_{01}$) = **61**.
