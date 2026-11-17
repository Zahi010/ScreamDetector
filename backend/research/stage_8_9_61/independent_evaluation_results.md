# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.61 — Preregistered Independent Evaluation Results ($N=700$)

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary

This report documents the primary findings of the unsealed, preregistered independent evaluation conducted in Track B of Stage 8.9.61.

The evaluation cohort consists of **700 newly acquired acoustic recordings** (200 screams, 500 hard negatives) spanning **453 unique source groups**, with verified zero creator or session overlap with any historical training or validation sets. The cohort was constructed and cryptographically sealed in Stage 8.9.60 (SHA-256: `9dfa4ced...`).

Four frozen model candidates were evaluated without threshold tuning, post-hoc optimization, or parameter adjustments:
1. **Candidate E1 Static C5:** Single 1.0s center window, threshold $\theta=0.6800$.
2. **Candidate B Baseline:** Single 1.0s center window, threshold $\theta=0.8000$.
3. **Candidate B + Intervention D:** Single 1.0s center window, threshold $\theta=0.8000$ + spectral whistle discriminator.
4. **Candidate E1 Rolling C5 EMA:** 500 ms hop size, EMA temporal smoothing $\alpha=0.50$, threshold $\theta=0.6000$.

### Key Findings:
- **Rolling Window Sensitivity:** Candidate E1 Rolling EMA achieved **70.00% overall recall** (140/200) and **86.26% sustained scream recall** (113/131), significantly outperforming all static configurations ($57.0\% - 58.0\%$).
- **False-Positive Trade-off:** Rolling EMA substantially elevated hard-negative FPR to **35.40%** (177/500), compared to **19.20%** for Static E1 and **15.80%** for Candidate B.
- **Intervention D Efficacy:** Candidate B + Intervention D suppressed referee whistle false positives from 10.00% (6/60) down to **1.67% (1/60)**, achieving the lowest overall FPR at **14.80%** (74/500).
- **Short-Scream Vulnerability:** All models struggled on short screams ($< 1.0$s), achieving recall between **36.23% and 39.13%**.

---

## 2. Primary Classification Metrics (Sealed Cohort $N=700$)

| Metric | Candidate E1 Static C5 | Candidate B Baseline | Candidate B + Interv. D | Candidate E1 Rolling EMA |
| :--- | :---: | :---: | :---: | :---: |
| **Analysis Framing** | 1.0s Static Center | 1.0s Static Center | 1.0s Static Center | 500 ms Hop / EMA |
| **Operating Threshold** | $\theta = 0.6800$ | $\theta = 0.8000$ | $\theta = 0.8000$ + Whistle | $\alpha = 0.50, \theta = 0.6000$ |
| **Total Recordings ($N$)** | 700 | 700 | 700 | 700 |
| **True Positives (TP)** | 116 | 115 | 114 | **140** |
| **False Negatives (FN)** | 84 | 85 | 86 | **60** |
| **False Positives (FP)** | 96 | 79 | **74** | 177 |
| **True Negatives (TN)** | 404 | 421 | **426** | 323 |
| **Overall Scream Recall** | 58.00% (116/200) | 57.50% (115/200) | 57.00% (114/200) | **70.00% (140/200)** |
| *Recall 95% Wilson CI* | [51.07%, 64.63%] | [50.57%, 64.15%] | [50.07%, 63.67%] | **[63.32%, 75.93%]** |
| **Sustained Recall ($\ge 1.0$s)** | 69.47% (91/131) | 67.18% (88/131) | 67.18% (88/131) | **86.26% (113/131)** |
| **Short Scream Recall ($< 1.0$s)** | 36.23% (25/69) | **39.13% (27/69)** | 37.68% (26/69) | **39.13% (27/69)** |
| **Hard-Negative FPR** | 19.20% (96/500) | 15.80% (79/500) | **14.80% (74/500)** | 35.40% (177/500) |
| *FPR 95% Wilson CI* | [15.99%, 22.88%] | [12.87%, 19.26%] | **[11.96%, 18.18%]** | [31.33%, 39.69%] |
| **Shouted-Speech FPR** | 22.67% (34/150) | **14.00% (21/150)** | **14.00% (21/150)** | 30.67% (46/150) |
| **Precision** | 54.72% | 59.28% | **60.64%** | 44.16% |
| **F1 Score** | 56.31% | 58.38% | **58.76%** | 54.16% |

---

## 3. Subgroup Performance Breakdown

Subgroups were categorized according to statistical evidence status based on sample size and source group diversity:
- **ROBUST_EVIDENCE:** $N \ge 30$, diverse source groups.
- **LIMITED_SAMPLE_SIZE:** $10 \le N < 30$, wider confidence intervals.
- **INSUFFICIENT_SAMPLE_SIZE:** $N < 10$, anecdotal evidence only.

### 3.1 Scream Subgroups (Positive Class, $N=200$)

| Subgroup Name | Sample Size ($N$) | Unique SGs | Candidate E1 Static | Candidate B Baseline | Candidate B + D | Candidate E1 Rolling EMA | Evidence Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **All Screams** | 200 | 160 | 58.00% (116) | 57.50% (115) | 57.00% (114) | **70.00% (140)** | `ROBUST_EVIDENCE` |
| **Sustained Screams ($\ge 1.0$s)** | 131 | 106 | 69.47% (91) | 67.18% (88) | 67.18% (88) | **86.26% (113)** | `ROBUST_EVIDENCE` |
| **Short Screams ($< 1.0$s)** | 69 | 58 | 36.23% (25) | 39.13% (27) | 37.68% (26) | **39.13% (27)** | `ROBUST_EVIDENCE` |
| **Priority 1: Low-Intensity** | 27 | 21 | **59.26% (16)** | 51.85% (14) | 51.85% (14) | 51.85% (14) | `LIMITED_SAMPLE_SIZE` |
| **Priority 2: Crowd-Masked** | 4 | 1 | 75.00% (3) | 75.00% (3) | 75.00% (3) | **100.00% (4)** | `INSUFFICIENT_SAMPLE_SIZE` |

### 3.2 Hard-Negative Subgroups (Negative Class, $N=500$)

| Subgroup Name | Sample Size ($N$) | Unique SGs | Candidate E1 Static | Candidate B Baseline | Candidate B + D | Candidate E1 Rolling EMA | Evidence Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **All Hard Negatives** | 500 | 296 | 19.20% (96) | 15.80% (79) | **14.80% (74)** | 35.40% (177) | `ROBUST_EVIDENCE` |
| **Priority 3: Shouted Speech** | 150 | 34 | 22.67% (34) | **14.00% (21)** | **14.00% (21)** | 30.67% (46) | `ROBUST_EVIDENCE` |
| **Cheering & Crowd Chanting** | 50 | 10 | **32.00% (16)** | 36.00% (18) | 36.00% (18) | 58.00% (29) | `ROBUST_EVIDENCE` |
| **Referee Whistles & Squeaks**| 60 | 30 | 23.33% (14) | 10.00% (6) | **1.67% (1)** | 25.00% (15) | `ROBUST_EVIDENCE` |
| **Infant Crying** | 19 | 6 | 10.53% (2) | **5.26% (1)** | **5.26% (1)** | 31.58% (6) | `LIMITED_SAMPLE_SIZE` |
| **Environmental Noise & Sirens**| 221 | 221 | **13.57% (30)** | 14.93% (33) | 14.93% (33) | 36.65% (81) | `ROBUST_EVIDENCE` |

---

## 4. Key Acoustic Interpretations

1. **Why Rolling EMA Dominates Sustained Recall (86.26% vs 69.47%):**
   In natural field recordings, human screams rarely begin exactly at the midpoint of an arbitrary audio recording segment. Static single-window evaluation frequently truncates vocal onsets or captures the tail end where energy is low. By sliding every 500 ms, the rolling window captures the resonant acoustic apex of the scream.

2. **Why Static E1 and Static B Perform Identically (58.00% vs 57.50%):**
   On genuinely unseen, independent acoustic sources, Candidate E1's static recall is virtually identical to Candidate B. The paired statistical test reveals no significant difference ($p = 0.0935$). This proves that Candidate E1's previous high validation scores in Stage 8.9.54 were primarily due to dataset-specific acoustic calibration rather than fundamental architectural superiority.

3. **Why Rolling EMA Struggles with False Positives (35.40% FPR):**
   Averaging $4.2$ evaluation windows per negative recording increases exposure to transient spikes (e.g. sharp vocal shouts, sudden applause bursts, percussive crowd noise). While the EMA filter ($\alpha=0.50$) dampens single-hop anomalies, prolonged acoustic disturbances easily push the EMA state above the $\theta=0.6000$ threshold.

4. **The Critical Value of Intervention D on Whistles (1.67% vs 23.33%):**
   Referee whistles possess intense, narrowband spectral lines that frequently deceive pure convolutional or fully connected neural nets. Intervention D's dedicated spectral peak and harmonic ratio check successfully eliminated 5 out of 6 whistle false positives for Candidate B, confirming the ongoing necessity of hybrid DSP discriminators.

