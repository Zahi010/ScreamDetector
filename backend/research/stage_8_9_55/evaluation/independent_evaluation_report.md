# Independent Evaluation Report — Stage 8.9.55

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Executive Summary & Core Research Findings

Stage 8.9.55 executed a rigorous blind evaluation of **Candidate E1** (expanded class-weighted checkpoint `candidate_e_v954_weighted.pt`, frozen $\theta = 0.6800$) against **Candidate B** (frozen reference baseline `config_b_mask.pt`, frozen $\theta = 0.8000$) and **Candidate B + Intervention D** on a genuinely new, untouched evaluation cohort of **450 authentic recordings across 246 independent source groups**.

### Primary Research Question:
*Does Candidate E1's improvement on the Stage 8.9.54 validation partition generalize to previously unseen recordings and source groups?*

### Finding:
**Candidate E1 demonstrated robust generalization on the fresh cohort**, delivering **72.67% recall** (109/150) and **6.33% hard-negative FPR** (19/300), compared to Candidate B's **55.33% recall** and **6.67% hard-negative FPR**.

---

## 2. Primary Classification Metrics (Frozen Operating Points)

| Metric | Candidate E1 ($\theta=0.6800$) | Candidate B ($\theta=0.8000$) | Candidate B + Intervention D |
|---|---|---|---|
| **True Positives (TP)** | **109** / 150 | **83** / 150 | **80** / 150 |
| **False Positives (FP)** | **19** / 300 | **20** / 300 | **20** / 300 |
| **True Negatives (TN)** | **281** / 300 | **280** / 300 | **280** / 300 |
| **False Negatives (FN)** | **41** / 150 | **67** / 150 | **70** / 150 |
| **Scream Recall** | **72.67%** [65.04%, 79.17%] | **55.33%** [47.34%, 63.06%] | **53.33%** [45.37%, 61.13%] |
| **Hard-Negative FPR** | **6.33%** [4.09%, 9.68%] | **6.67%** [4.36%, 10.07%] | **6.67%** [4.36%, 10.07%] |
| **Precision** | **85.16%** [77.98%, 90.29%] | **80.58%** [71.90%, 87.06%] | **80.00%** [71.12%, 86.66%] |
| **Specificity** | **93.67%** [90.32%, 95.91%] | **93.33%** [89.93%, 95.64%] | **93.33%** [89.93%, 95.64%] |
| **F1-Score** | **78.42%** | **65.61%** | **64.00%** |
| **Accuracy** | **86.67%** [83.21%, 89.50%] | **80.67%** [76.76%, 84.05%] | **80.00%** [76.06%, 83.43%] |
| **ROC-AUC** | **0.9201** | **0.8907** | **0.8907** |
| **PR-AUC** | **0.8716** | **0.8139** | **0.8139** |
| **Brier Score** | **0.0998** | **0.1318** | **0.1318** |
| **ECE** | **0.0550** | **0.0650** | **0.0650** |

---

## 3. Provenance & Isolation Verification
- Total recordings evaluated: **450**
- Independent source groups: **246** (77 positive SGs, 191 negative SGs)
- Commercial license compliance: **100% CC0 / CC-BY**
- Overlap with historical training/val/test partitions: **0 collisions (verified via SHA-256 and PCM digests)**
- Ground-truth label adjudication: **100% concordant**
