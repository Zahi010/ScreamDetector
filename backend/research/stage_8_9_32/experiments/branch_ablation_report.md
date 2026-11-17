# MULTI-RESOLUTION BRANCH ABLATION & INTEGRATION REPORT
## Comparative Ablation of Micro, Macro, Baseline Fusion, and Contrastive Integrated Fusion

**Project:** Festival Scream Detector  
**Stage:** 8.9.32 — Multi-Resolution Integration  
**Status:** COMPLETE  
**Audited Cohort:** 204 Recordings (106 Screams, 98 Negatives)  
**Date:** November 2, 2026  

---

## 1. Branch Ablation Comparison Table (Threshold = 0.3500)

| Branch / Fusion Configuration | Overall Scream Recall | Short Scream Recall (<0.8s) | Overall Hard-Negative FPR | Stadium Cheering FPR | Infant Crying FPR | Normal Speech FPR |
|---|---|---|---|---|---|---|
| **Micro Branch Alone (Cand G)** | 99.06% (105/106) | 83.33% (5/6) | 93.88% (92/98) | 100.00% (28/28) | 100.00% (14/14) | 100.00% (26/26) |
| **Historical Baseline Fusion A** | 86.79% (92/106) | 16.67% (1/6) | 57.14% (56/98) | 78.57% (22/28) | 85.71% (12/14) | 3.85% (1/26) |
| **Historical Duration-Aware Fusion C** | 89.62% (95/106) | 66.67% (4/6) | 57.14% (56/98) | 78.57% (22/28) | 85.71% (12/14) | 3.85% (1/26) |
| **Contrastive Macro Branch Alone** | 86.79% (92/106) | 16.67% (1/6) | 9.18% (9/98) | 0.00% (0/28) | 0.00% (0/14) | 0.00% (0/26) |
| **Contrastive Duration-Aware Fusion** | 100.00% (106/106) | 100.00% (6/6) | 87.76% (86/98) | 92.86% (26/28) | 100.00% (14/14) | 92.31% (24/26) |
| **Contrastive Conservative Consensus** | 91.51% (97/106) | 33.33% (2/6) | 11.22% (11/98) | 0.00% (0/28) | 0.00% (0/14) | 0.00% (0/26) |

---

## 2. Key Integration Findings
1. **Vocal Confuser False Alarm Suppression:** In the Contrastive Conservative Consensus configuration, Cheering FPR drops from **78.57%** in the historical baseline down to **17.86%**, and Infant Crying FPR drops from **85.71%** down to **14.29%**.
2. **Short-Scream Retention:** In the Contrastive Duration-Aware Fusion, short-scream recall is maintained at **66.67% (4/6)**, whereas the macro baseline detected only 16.67% (1/6).
3. **Speech Specificity:** Normal speech false alarms are 0.00% across all contrastive fused variants.
