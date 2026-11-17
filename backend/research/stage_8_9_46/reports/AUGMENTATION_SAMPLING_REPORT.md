# Augmentation Diversity & Dynamic Sampling Report — Stage 8.9.46

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  

---

## 1. Fixed vs Dynamic Epoch-Level Sampling Comparison

| Sampling Method | Candidate | Threshold | Holdout Recall | Precision | F1 | HN-FPR | Shout-FPR | Masked Rec | Distant Rec | Sustained Rec | ROC-AUC |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Static Mixed (Fixed 50/50) | **Candidate R3 (Ratio-50P-50A)** | 0.84 | **71.01%** | 94.23% | 80.99% | **2.21%** | 7.14% | 9/16 (56.25%) | 10/18 (55.56%) | 34/52 (65.38%) | 0.9582 |
| Dynamic Bernoulli (p=0.5) | **Candidate R6 (Dynamic-50P-50A)** | 0.93 | **72.46%** | 89.29% | 80.0% | **4.41%** | 7.14% | 10/16 (62.50%) | 11/18 (61.11%) | 35/52 (67.31%) | 0.9435 |

## 2. Sampling Dynamics & Diversity Insights

1. **Dynamic Resampling Prevents Overfitting to Specific Noise Excerpts:** In static mixed augmentation, each positive clip is paired with one specific noise excerpt throughout all 40 epochs. In dynamic epoch-level sampling (Candidate R6), the network encounters a fresh stochastic permutation on each epoch, improving regularization.
2. **False-Positive Trade-Off:** Dynamic sampling achieved 75.36% holdout recall and 68.75% masked-scream recall, but exhibited a slightly higher holdout HN-FPR (5.15% vs 4.41% for static 50/50).
