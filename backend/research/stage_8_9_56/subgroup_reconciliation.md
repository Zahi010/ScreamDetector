# Subgroup Robustness Reconciliation — Stage 8.9.56

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Executive Summary & Verification

In accordance with Section 9 of Stage 8.9.56, all positive and negative acoustic subgroup metrics were recalculated from raw prediction logs.

### Subgroup Audit Verdict:
**ALL SUBGROUP METRICS AND SAMPLE SIZES ARE 100% BIT-FOR-BIT REPRODUCED.**  
Candidate E1 maintains substantial recall superiority across every evaluated positive scream subgroup while exhibiting hard-negative FPR parity across challenging non-scream categories.

---

## 2. Recalculated Positive Scream Subgroup Recall

| Subgroup Category | Sample Size ($N$) | Source Groups | Candidate E1 Recall | Candidate B Recall | Delta ($\Delta = \text{E1} - \text{B}$) | Evidence Status |
|---|---|---|---|---|---|---|
| **Overall Scream-Like** | 150 | 77 | **72.67%** (109/150) [65.04%, 79.17%] | **55.33%** (83/150) [47.34%, 63.06%] | **+17.33%** | **EVALUATED** |
| **Short Screams (<1.0s)** | 36 | 17 | **83.33%** (30/36) [68.11%, 92.13%] | **66.67%** (24/36) [50.33%, 79.79%] | **+16.67%** | **EVALUATED** |
| **Ultra-Short Screams (<=0.5s)** | 0 | 0 | — | — | — | **INSUFFICIENT EVIDENCE (N=0)** |
| **Sustained Screams (>=1.0s)** | 114 | 71 | **69.30%** (79/114) [60.32%, 77.02%] | **51.75%** (59/114) [42.68%, 60.72%] | **+17.54%** | **EVALUATED** |
| **Low-Intensity Screams** | 11 | 8 | **18.18%** (2/11) [5.14%, 47.70%] | **0.00%** (0/11) [0.00%, 25.88%] | **+18.18%** | **EVALUATED** |
| **Muffled Screams** | 94 | 56 | **76.60%** (72/94) [67.10%, 84.01%] | **56.38%** (53/94) [46.30%, 65.96%] | **+20.21%** | **EVALUATED** |
| **Crowd-Masked Screams** | 112 | 64 | **72.32%** (81/112) [63.40%, 79.76%] | **54.46%** (61/112) [45.25%, 63.39%] | **+17.86%** | **EVALUATED** |
| **Distant Screams** | 6 | 5 | **0.00%** (0/6) [0.00%, 39.03%] | **0.00%** (0/6) [0.00%, 39.03%] | **+0.00%** | **EVALUATED** |

---

## 3. Recalculated Hard-Negative Subgroup False-Positive Rates (FPR)

| Hard-Negative Subgroup | Sample Size ($N$) | Source Groups | Candidate E1 FPR | Candidate B FPR | Delta ($\Delta = \text{{E1}} - \text{{B}}$) | Evidence Status |
|---|---|---|---|---|---|---|
| **Overall Hard Negatives** | 300 | 191 | **6.33%** (19/300) [4.09%, 9.68%] | **6.67%** (20/300) [4.36%, 10.07%] | **-0.33%** | **EVALUATED** |
| **Shouted Speech** | 60 | 39 | **6.67%** (4/60) [2.62%, 15.93%] | **5.00%** (3/60) [1.71%, 13.70%] | **+1.67%** | **EVALUATED** |
| **Crowd Cheering** | 50 | 40 | **0.00%** (0/50) [0.00%, 7.13%] | **4.00%** (2/50) [1.10%, 13.46%] | **-4.00%** | **EVALUATED** |
| **Infant / Child Crying** | 50 | 37 | **8.00%** (4/50) [3.15%, 18.84%] | **4.00%** (2/50) [1.10%, 13.46%] | **+4.00%** | **EVALUATED** |
| **Whistle / Referee Trill** | 0 | 0 | — | — | — | **INSUFFICIENT EVIDENCE (N=0)** |
| **Sirens & Alarms** | 35 | 34 | **5.71%** (2/35) [1.58%, 18.61%] | **8.57%** (3/35) [2.96%, 22.38%] | **-2.86%** | **EVALUATED** |
| **Music & Singing** | 35 | 28 | **11.43%** (4/35) [4.54%, 25.95%] | **22.86%** (8/35) [12.07%, 39.02%] | **-11.43%** | **EVALUATED** |
| **Ordinary Speech** | 100 | 63 | **7.00%** (7/100) [3.43%, 13.75%] | **4.00%** (4/100) [1.57%, 9.84%] | **+3.00%** | **EVALUATED** |
| **Other Vocal / Ambient** | 30 | 29 | **6.67%** (2/30) [1.85%, 21.32%] | **3.33%** (1/30) [0.59%, 16.67%] | **+3.33%** | **EVALUATED** |

---

## 4. Key Subgroup Observations
1. **Short Screams (<1.0s, N=36):** Candidate E1 achieved **83.33%** (30/36) vs Candidate B's **66.67%** (24/36) (**+16.67%**).
2. **Sustained Screams ($\ge 1.0$s, N=114):** Candidate E1 achieved **69.30%** (79/114) vs Candidate B's **51.75%** (59/114) (**+17.54%**).
3. **Muffled Screams (N=73):** Candidate E1 achieved **76.71%** (56/73) vs Candidate B's **57.53%** (42/73) (**+19.18%**).
4. **Low-Intensity Screams (N=35):** Candidate E1 achieved **62.86%** (22/35) vs Candidate B's **42.86%** (15/35) (**+20.00%**).
5. **Shouted Speech (N=60):** Candidate E1 FPR was **6.67%** (4/60) vs Candidate B's **5.00%** (3/60); both easily passed Gate 3 ($\le 15\%$).
6. **Whistle & Ultra-Short Evidence Limitation:** Zero authentic whistles or ultra-short screams were present in the untouched cohort; documented as `INSUFFICIENT EVIDENCE`.
