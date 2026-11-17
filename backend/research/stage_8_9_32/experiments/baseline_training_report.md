# BASELINE RESEARCH MODELS TRAINING & EVALUATION REPORT
## Supervised Baselines on Source-Group-Independent Partitions ($N=1,325$)

**Project:** Festival Scream Detector  
**Stage:** 8.9.32 — Baseline Engineering  
**Focus:** Supervised Baseline Models (LR, Weighted LR, Random Forest, MLP)  
**Status:** COMPLETE  
**Date:** November 2, 2026

---

## 1. Executive Summary & Experimental Setup

To establish rigorous benchmarks before evaluating contrastive representation learning, four supervised baseline models were trained on 1024-dimensional mean-pooled YAMNet embeddings using the strictly source-group-separated dataset partition:

- **Training Partition:** 739 recordings (172 genuine screams, 567 hard negatives)
- **Validation Partition:** 293 recordings (79 genuine screams, 214 hard negatives)
- **Independent Test Partition:** 293 recordings (102 genuine screams, 191 hard negatives)
- **Source Groups:** 503 distinct source groups with 0 cross-split speaker or session leakage.

---

## 2. Comparative Evaluation Matrix (Evaluated on Independent Test Partition, Threshold = 0.3500)

| Model Architecture | Test Recall | Test Precision | Test F1 | Test Overall FPR | Cheering FPR | Infant Crying FPR | Shouted Speech FPR | Test ROC-AUC | Test PR-AUC |
|---|---|---|---|---|---|---|---|---|---|
| **Baseline A: Logistic Regression ($C=1.0$)** | 79.41% (81/102) | 81.82% (81/99) | 0.8060 | **9.42% (18/191)** | 14.29% (6/42) | **6.67% (1/15)** | 7.94% (5/63) | 0.9389 | 0.8931 |
| **Baseline B: Class-Weighted LR** | **90.20% (92/102)** | 76.03% (92/121) | **0.8251** | 15.18% (29/191) | 16.67% (7/42) | 13.33% (2/15) | 14.29% (9/63) | **0.9412** | **0.9015** |
| **Baseline C: Random Forest (100 trees)** | 81.37% (83/102) | **84.69% (83/98)** | 0.8300 | **7.85% (15/191)** | **11.90% (5/42)** | 13.33% (2/15) | **6.35% (4/63)** | 0.9371 | 0.8874 |
| **Baseline D: MLP (256-128)** | 73.53% (75/102) | 72.82% (75/103) | 0.7317 | 14.66% (28/191) | 16.67% (7/42) | 13.33% (2/15) | 12.70% (8/63) | 0.9059 | 0.8341 |

---

## 3. Key Observations & Milestone Findings

1. **Massive Reduction in Confuser False Alarms:**
   - In the frozen Stage 8.9.31 baseline (which lacked diverse hard-negative training), Cheering FPR was **$78.57\%$** and Infant Crying FPR was **$85.71\%$**.
   - Incorporating hard negatives into supervised training reduces Cheering FPR down to **$11.90\% - 14.29\%$** and Crying FPR down to **$6.67\% - 13.33\%$**—a **$5\times$ to $10\times$ improvement** in acoustic specificity!
2. **High Recall with Class-Weighting:**
   - Baseline B achieves **$90.20\%$ test recall**, providing the first supervised model to cross the $90\%$ recall mark on independent test data while maintaining hard-negative FPR at $15.18\%$.
3. **Random Forest Specificity:**
   - Baseline C achieves the lowest overall hard-negative FPR ($7.85\%$) and lowest Cheering FPR ($11.90\%$).

These models serve as the formal benchmarks for Phase 5 contrastive learning.
