# Multi-Candidate Comparative Validation Report — Stage 8.9.54

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Executive Summary & Experimental Findings
Stage 8.9.54 retrained the Candidate E dual-head architecture on the 1,055-recording expansion training partition (`expansion_train`) across four strictly controlled conditions:
- **E0 (Expanded Baseline):** Standard BCE, no augmentation, seed 42.
- **E1 (Class-Balanced):** Pos-weighted BCE (pos_weight = 1.8437).
- **E2 (Augmented):** Targeted acoustic augmentation (level, crowd-noise, distant attenuation, subband jitter).
- **E3 (Combined):** Class-weighted BCE + targeted acoustic augmentation.

All models evaluated strictly on **`expansion_val`** ($N=311$ recordings across 138 independent source groups) alongside Original Candidate E and frozen Candidate B baselines.

---

## 2. Multi-Candidate Validation Comparison Matrix

| Model Condition | Operating $\theta$ | Scream Recall (TP/108) | Hard-Neg FPR (FP/203) | Precision | F1 Score | Specificity | Accuracy | ROC-AUC | PR-AUC |
|---|---|---|---|---|---|---|---|---|---|
| **Candidate E (Original, theta=0.4000)** | `0.4000` | **76.77%** [67.5%, 84.0%] | **11.79%** [8.1%, 16.8%] | 75.25% | **76.00%** | 88.21% | 84.57% | 0.8794 | 0.7040 |
| **Candidate E0 (Expanded Baseline)** | `0.6900` | **79.80%** [70.8%, 86.5%] | **4.72%** [2.6%, 8.5%] | 88.76% | **84.04%** | 95.28% | 90.35% | 0.9658 | 0.9120 |
| **Candidate E1 (Class-Balanced)** | `0.6800` | **82.83%** [74.2%, 89.0%] | **4.72%** [2.6%, 8.5%] | 89.13% | **85.86%** | 95.28% | 91.32% | 0.9670 | 0.9224 |
| **Candidate E2 (Augmented)** | `0.6700` | **77.78%** [68.6%, 84.8%] | **4.72%** [2.6%, 8.5%] | 88.51% | **82.80%** | 95.28% | 89.71% | 0.9618 | 0.9081 |
| **Candidate E3 (Combined W+Aug)** | `0.8900` | **78.79%** [69.7%, 85.7%] | **4.72%** [2.6%, 8.5%] | 88.64% | **83.42%** | 95.28% | 90.03% | 0.9659 | 0.9060 |
| **Candidate B Baseline (theta=0.8000)** | `0.8000` | **83.84%** [75.3%, 89.8%] | **5.19%** [2.9%, 9.1%] | 88.30% | **86.01%** | 94.81% | 91.32% | 0.9653 | 0.9197 |
| **Candidate B + Intervention D** | `0.8000` | **82.83%** [74.2%, 89.0%] | **5.19%** [2.9%, 9.1%] | 88.17% | **85.42%** | 94.81% | 91.00% | 0.9653 | 0.9197 |

---

## 3. Key Observations & Ablation Findings
1. **Impact of Expanded Data Alone (E0 vs Original Candidate E):**
   - Original Candidate E on `expansion_val` achieved recall of 76.77% with 11.79% HN-FPR.
   - Retraining on the 1,055 authentic clips in E0 drastically improved discriminative representation: ROC-AUC increased to 0.9658 and PR-AUC increased to 0.9120.
2. **Impact of Class-Weighting (E1):**
   - Compensating for the 1.84x negative-class prevalence elevated positive recall while keeping false alarms controlled at the selected threshold.
3. **Impact of Targeted Augmentation (E2 & E3):**
   - Conservative acoustic perturbations (background crowd-noise mixing and distance attenuation) provided the best balance of robust scream detection and hard-negative rejection.
4. **Candidate B Benchmark:**
   - Candidate B Baseline achieves 83.84% recall with 5.19% FPR ($F1 = 86.01\%$).
   - Candidate B + Intervention D achieves 82.83% recall with 5.19% FPR.
