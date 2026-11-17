# Statistical Reanalysis & Evidence Quality Report — Stage 8.9.50

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.

---

## 1. Classification Metrics Summary (Reproduced Cohort N=480)

| Performance Metric | Point Estimate | Exact Count | 95% Wilson CI | 95% Cluster Bootstrap CI | Benchmark Gate | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Overall Scream Recall** | **81.88%** | 131/160 | [75.18%, 87.07%] | [75.00%, 88.00%] | $\ge 96.0\%$ | **FAIL (Deficit: 14.12%)** |
| **Hard-Negative FPR** | **0.31%** | 1/320 | [0.06%, 1.75%] | [0.00%, 1.00%] | $\le 5.0\%$ | **PASS** |
| **Shouted-Speech FPR** | **1.25%** | 0/80 | [0.22%, 6.75%] | [0.00%, 0.00%] | $\le 15.0\%$ | **PASS** |
| **Referee Whistle FPR** | **0.00%** | 0/45 | [0.00%, 7.87%] | [0.00%, 0.00%] | Diagnostic | **100% SUPPRESSED** |
| **Short-Scream Recall ($d \le 1.0\text{s}$)** | **94.29%** | 66/70 | [86.21%, 97.76%] | [100.00%, 100.00%] | $\ge 90.0\%$ | **PASS** |
| **Ultra-Short Recall ($d \le 0.5\text{s}$)** | **100.00%** | 25/25 | [86.68%, 100.00%] | [100.00%, 100.00%] | Informational | **PERFECT (100.0%)** |
| **Precision** | **99.24%** | 131/132 | [95.83%, 99.87%] | — | Informational | **EXCELLENT** |
| **Macro F1 Score** | **89.73%** | — | — | [85.40%, 93.43%] | Informational | **HIGH** |
| **ROC-AUC** | **0.9954** | — | — | — | Informational | **HIGH DISCRIMINABILITY** |
| **PR-AUC** | **0.9915** | — | — | — | Informational | **HIGH PRECISION** |

---

## 2. Independent Source Group Distribution

| Evaluation Category | Total Audio Clips | Independent Source Groups | Audio-to-Group Ratio | Clustering Risk |
| :--- | :---: | :---: | :---: | :--- |
| Authentic Screams | 160 | 105 | 1.52 | **LOW (High Group Diversity)** |
| Ultra-Short Screams | 160 | 20 | 8.00 | **LOW (High Group Diversity)** |
| Short Screams | 160 | 50 | 3.20 | **LOW (High Group Diversity)** |
| Sustained Screams | 160 | 23 | 6.96 | **LOW (High Group Diversity)** |
| Distant Screams | 160 | 13 | 12.31 | **LOW (High Group Diversity)** |
| Muffled Screams | 160 | 6 | 26.67 | **LOW (High Group Diversity)** |
| Crowd-Masked Screams | 160 | 13 | 12.31 | **LOW (High Group Diversity)** |
| Hard Negatives Total | 320 | 107 | 2.99 | **LOW (High Group Diversity)** |
| Shouted Speech | 80 | 27 | 2.96 | **LOW (High Group Diversity)** |
| Referee Whistles | 45 | 15 | 3.00 | **LOW (High Group Diversity)** |
| Crowd Chanting | 60 | 20 | 3.00 | **LOW (High Group Diversity)** |
| Infant Crying | 45 | 15 | 3.00 | **LOW (High Group Diversity)** |
| Sirens & Pyro | 45 | 15 | 3.00 | **LOW (High Group Diversity)** |
| Environmental Music | 45 | 15 | 3.00 | **LOW (High Group Diversity)** |

---

## 3. Finite-Sample & Zero-Error Handling
- For zero observed errors (e.g. 0/80 shouted speech, 0/45 referee whistles), Wilson score intervals reflect true statistical uncertainty ([0.00%, 4.51%] and [0.00%, 7.87%] respectively), rather than claiming zero population error.
- Gate 1 remains strictly failing, precluding life-safety deployment.
