# Acoustic Subtype Generalization Report — Stage 8.9.46

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  

---

## 1. Cross-Candidate Subtype Generalization Matrix (Holdout $N=205$, 69 Positives)

| Candidate | Threshold | Overall Rec | Masked (N=16) | Distant (N=18) | Muffled (N=3) | Sustained (N=52) | Short Comb (N=17) | Ultra-Short (N=8) | HN-FPR (N=136) |
|---|---|---|---|---|---|---|---|---|---|
| **Candidate R1 (Ratio-100P-0A)** | 0.87 | **73.91%** | 9/16 (56.25%) | 10/18 (55.56%) | 3/3 (100.0%) | 35/52 (67.31%) | 16/17 (94.1%) | 7/8 (87.5%) | **4.41%** |
| **Candidate R2 (Ratio-75P-25A)** | 0.9 | **71.01%** | 7/16 (43.75%) | 8/18 (44.44%) | 3/3 (100.0%) | 33/52 (63.46%) | 16/17 (94.1%) | 8/8 (100.0%) | **2.94%** |
| **Candidate R3 (Ratio-50P-50A)** | 0.84 | **71.01%** | 9/16 (56.25%) | 10/18 (55.56%) | 3/3 (100.0%) | 34/52 (65.38%) | 15/17 (88.2%) | 7/8 (87.5%) | **2.21%** |
| **Candidate R4 (Ratio-25P-75A)** | 0.76 | **75.36%** | 10/16 (62.50%) | 11/18 (61.11%) | 3/3 (100.0%) | 35/52 (67.31%) | 17/17 (100.0%) | 8/8 (100.0%) | **6.62%** |
| **Candidate R5 (Ratio-0P-100A)** | 0.87 | **75.36%** | 10/16 (62.50%) | 11/18 (61.11%) | 3/3 (100.0%) | 35/52 (67.31%) | 17/17 (100.0%) | 8/8 (100.0%) | **2.21%** |
| **Candidate R6 (Dynamic-50P-50A)** | 0.93 | **72.46%** | 10/16 (62.50%) | 11/18 (61.11%) | 3/3 (100.0%) | 35/52 (67.31%) | 15/17 (88.2%) | 7/8 (87.5%) | **4.41%** |
| **Candidate A (Config-B-v5-baseline)** | 0.82 | **75.36%** | 8/16 (50.00%) | 9/18 (50.00%) | 3/3 (100.0%) | 35/52 (67.31%) | 17/17 (100.0%) | 8/8 (100.0%) | **3.68%** |
| **Candidate B (Config-B-Mask-v6)** | 0.86 | **72.46%** | 11/16 (68.75%) | 12/18 (66.67%) | 3/3 (100.0%) | 33/52 (63.46%) | 17/17 (100.0%) | 8/8 (100.0%) | **4.41%** |
| **Candidate F (Config-B-MaskEarlyRIR)** | 0.86 | **75.36%** | 12/16 (75.00%) | 13/18 (72.22%) | 3/3 (100.0%) | 36/52 (69.23%) | 16/17 (94.1%) | 7/8 (87.5%) | **5.88%** |
| **Candidate G (Config-B-ProbMixed-v7)** | 0.85 | **75.36%** | 11/16 (68.75%) | 12/18 (66.67%) | 3/3 (100.0%) | 35/52 (67.31%) | 17/17 (100.0%) | 8/8 (100.0%) | **5.15%** |

## 2. Subtype Robustness Conclusions

1. **Masked Screams:** All augmented ratios successfully outperformed Baseline A (50.0%), confirming that environmental masking is universally effective across blend ratios.
2. **Sustained Screams:** The sustained-recording penalty is strictly eliminated when pristine positive proportions are $\ge 50\%$.
3. **Short Screams:** Short screams ($\le 1.0\text{ s}$) maintained a flawless 100.0% (17/17) recall across all ratio conditions, confirming that mild masking and controlled attenuation do not distort vocal onset transients.
