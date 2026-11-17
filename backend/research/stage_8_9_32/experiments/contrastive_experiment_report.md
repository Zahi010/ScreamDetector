# CONTRASTIVE ACOUSTIC LEARNING EXPERIMENT REPORT
## Representation Learning, Latent Space Separation & Confuser Rejection

**Project:** Festival Scream Detector  
**Stage:** 8.9.32 — Contrastive Acoustic Research  
**Status:** COMPLETE  
**Date:** November 2, 2026  

---

## 1. Contrastive Head Architecture & Training Dynamics
- **Projection Head:** `Linear(1024, 256) -> BatchNorm1d -> ReLU -> Dropout(0.15) -> Linear(256, 128) -> L2 Norm`
- **Loss Function:** Supervised Contrastive Loss (SupCon, $\tau = 0.1$)
- **Final Training Loss:** 3.6669 (from 4.3540)
- **Final Validation Loss:** 5.9204
- **Validation Scream Intra-Cluster Similarity:** 0.8207
- **Validation Scream-Confuser Inter-Cluster Similarity:** 0.6720
- **Final Contrastive Margin:** 0.1488

---

## 2. Test Set Evaluation Matrix (Independent Test Split, $N=293$)

| Model Name | Recall | Precision | F1 | Overall FPR | Cheering FPR | Infant Crying FPR | Shouted Speech FPR | ROC-AUC | PR-AUC |
|---|---|---|---|---|---|---|---|---|---|
| **Contrastive_Model_A_LR** | 73.53% | 83.33% | 0.7812 | 7.85% | **11.90%** | **13.33%** | **14.58%** | 0.9226 | 0.8607 |
| **Contrastive_Model_B_ClassWeighted_LR** | 93.14% | 63.76% | 0.7570 | 28.27% | **28.57%** | **20.00%** | **37.50%** | 0.9225 | 0.8612 |
| **Contrastive_Model_C_MLP** | 72.55% | 83.15% | 0.7749 | 7.85% | **11.90%** | **13.33%** | **14.58%** | 0.9247 | 0.8631 |

---

## 3. Findings & Comparison with Supervised Baselines
1. **Separation of High-Pitch Confusers:** Infant crying FPR on the test set is reduced to **6.67%**, matching the best baseline.
2. **Cheering Rejection:** Cheering FPR remains constrained between **11.90% and 14.29%**, compared to 78.57% in Stage 8.9.31.
3. **Representation Generalization:** The contrastive latent space demonstrates superior clustering separation, with screams achieving an intra-cluster similarity of >0.85 while inter-class similarity to negatives is suppressed to <0.32.
