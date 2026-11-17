# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.61 — FINAL STAGE REPORT: Rolling-Window DSP Research, Temporal Aggregation Validation & Preregistered Independent Evaluation

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary

Stage 8.9.61 successfully executed a dual-track acoustic research program:
- **Track A (Development & Engineering Validation):** Reconciled the Stage 8.9.60 acquisition accounting discrepancy, verified cross-partition creator independence, created an unexposed development cohort ($N=187$, 180 unique source groups), implemented an online circular `StreamingRollingWindowBuffer` (1.0s window, 500 ms hop), benchmarked five temporal aggregation strategies, validated 15 streaming boundary and isolation scenarios, established multi-stream real-time latency across 1, 2, 4, and 8 streams, and locked candidate parameters in `rolling_window_candidate_freeze.json`.
- **Track B (Preregistered Independent Evaluation):** Authored and sealed the preregistration protocol (`independent_evaluation_preregistration.md`), unsealed the sealed evaluation cohort ($N=700$ recordings, 200 screams, 500 hard negatives, 453 source groups), executed blind evaluation of four frozen candidate configurations, performed inferential statistical testing using 2,000 source-group clustered bootstrap iterations and paired McNemar tests, evaluated the project's five foundational acceptance gates, and conducted a cryptographic audit of all repository assets.

### Headline Findings:
1. **Continuous Windowing Solves Sustained Scream Truncation:**
   On the unexposed 700-recording evaluation cohort, `Candidate_E1_Rolling_C5_EMA` achieved **86.26% sustained scream recall** (113/131) and **70.00% overall recall** (140/200), compared to **69.47% sustained** (91/131) and **58.00% overall** (116/200) for static center-window extraction. The $+12.00\%$ overall recall boost is highly statistically significant (McNemar $\chi^2 = 25.92, p = 3.56 \times 10^{-7}$).
2. **Multiple-Testing Penalty Inflates False Positives:**
   Advancing the analysis window across continuous audio chunks increased exposure to transient background distractors. The hard-negative false positive rate jumped from **19.20% (static)** to **35.40% (rolling)**, and shouted-speech FPR increased from **22.67% to 30.67%**.
3. **Static Equivalence Between E1 and Baseline B:**
   On static 1.0s evaluation, Candidate E1 (58.00% recall, 19.20% FPR) and Candidate B (57.50% recall, 15.80% FPR) are statistically indistinguishable (McNemar $p = 0.0935$).
4. **Intervention D Provides Essential Whistle Rejection:**
   Candidate B combined with Intervention D suppressed referee whistle false alarms from 10.00% down to **1.67% (1/60)**, achieving the lowest overall FPR at **14.80%** (74/500).
5. **Acceptance Gate Verdict & Promotion Status:**
   **No candidate passes all five acceptance gates.** All candidates fail Gate 1 ($\ge 96\%$ recall), Gate 2 ($\le 5\%$ hard-negative FPR), and Gate 4 ($\ge 90\%$ short-scream recall). **Zero production promotion is authorized.** All production model files remain frozen. The system remains strictly an experimental research prototype.

---

## 2. Track A: Development Engineering & Strategy Optimization

### 2.1 Accounting Reconciliation & Creator Independence
Stage 8.9.61 formally reconciled the 56-recording and 31-source-group accounting discrepancy from Stage 8.9.60:
- **Recordings:** 87 short/ultra-short screams ($< 1.0$s) omitted from priority categories in Stage 60 minus 31 multi-category records (27 low-intensity and 4 crowd-masked screams with duration $\ge 1.0$s double-counted in Priority 4) equals exactly 56 net recordings ($962 - 906 = 56$).
- **Source Groups:** 62 exclusive source groups from omitted recordings minus 31 overlapping source groups equals exactly 31 net source groups ($633 - 602 = 31$).
- **Creator Audit:** Cross-partition identity comparison confirmed that the 453 source groups in the sealed evaluation cohort share **0 creator IDs** with any historical training (`expansion_train`), validation (`expansion_val`), or development cohorts.

### 2.2 Temporal Aggregation Comparison ($N=187$ Development Cohort)
Evaluating five temporal aggregation strategies on the unexposed development manifest ($N=187$, 70 screams, 117 negatives) established the following trade-offs:

| Strategy | Framing / Decision Rule | Overall Recall | Sustained Recall | Hard-Negative FPR | F1 Score |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Strategy A** | Max Pooling ($\theta=0.6800$) | 87.14% | 98.39% | 47.86% | 65.24% |
| **Strategy B** | Persistence ($K=2, \theta=0.6500$) | 75.71% | 85.48% | 26.50% | 68.83% |
| **Strategy C** | Hysteresis ($0.70 / 0.45$) | 82.86% | 93.55% | 34.19% | 69.05% |
| **Strategy D** | **Rolling EMA ($\alpha=0.50, \theta=0.6000$)** | **84.29%** | **95.16%** | **37.61%** | **68.21%** |
| **Strategy E** | Static Center Window ($\theta=0.6800$) | 61.43% | 70.97% | 17.09% | 64.66% |

Strategy D (Rolling EMA) was selected and sealed in `rolling_window_candidate_freeze.json` (SHA-256: `a56982b0...`).

### 2.3 Streaming Invariants & Multi-Stream Latency
- The `StreamingRollingWindowBuffer` passed all **15 streaming, boundary, and state-isolation test scenarios** with 100% compliance.
- Multi-stream latency profiling demonstrated that processing 8 concurrent audio feeds requires only **59.50 ms P95** batch turnaround time, consuming **11.90%** of the 500 ms frame window budget. Across 1,200 timed iterations, there were **0 deadline misses**, **0 dropped windows**, and **0 buffer overruns**.

---

## 3. Track B: Preregistered Independent Evaluation ($N=700$)

### 3.1 Primary Classification Metrics Summary

| Evaluation Metric | Candidate E1 Static C5 | Candidate B Baseline | Candidate B + Interv. D | Candidate E1 Rolling EMA |
| :--- | :---: | :---: | :---: | :---: |
| **Analysis Framing** | 1.0s Static Center | 1.0s Static Center | 1.0s Static Center | 500 ms Hop / EMA |
| **Operating Threshold** | $\theta = 0.6800$ | $\theta = 0.8000$ | $\theta = 0.8000$ + Whistle | $\alpha=0.50, \theta=0.6000$ |
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
| **Referee Whistles FPR** | 23.33% (14/60) | 10.00% (6/60) | **1.67% (1/60)** | 25.00% (15/60) |
| **Precision** | 54.72% | 59.28% | **60.64%** | 44.16% |
| **F1 Score** | 56.31% | 58.38% | **58.76%** | 54.16% |

---

## 4. Statistical Significance & Clustered Bootstrap Analysis

Results from 2,000 source-group clustered bootstrap iterations ($N=453$ clusters) and paired McNemar contingency tests:

1. **Candidate E1 Rolling EMA vs Candidate B Baseline:**
   - Recall Difference: **$+12.42\%$** (95% CI: $[+6.60\%, +18.54\%]$).
   - FPR Difference: **$+19.63\%$** (95% CI: $[+16.25\%, +23.45\%]$).
   - McNemar Test: Discordant pairs $b=37, c=110, \chi^2 = 35.27, p = 2.87 \times 10^{-9}$ (Statistically Significant).
2. **Candidate E1 Rolling EMA vs Candidate E1 Static C5:**
   - Recall Difference: **$+12.00\%$** (95% CI: $[+7.28\%, +17.13\%]$).
   - FPR Difference: **$+16.29\%$** (95% CI: $[+12.65\%, +20.32\%]$).
   - McNemar Test: Discordant pairs $b=32, c=89, \chi^2 = 25.92, p = 3.56 \times 10^{-7}$ (Statistically Significant).
3. **Candidate E1 Static C5 vs Candidate B Baseline:**
   - Recall Difference: **$+0.42\%$** (95% CI: $[-4.67\%, +5.74\%]$).
   - FPR Difference: **$+3.34\%$** (95% CI: $[+0.34\%, +6.47\%]$).
   - McNemar Test: Discordant pairs $b=32, c=48, \chi^2 = 2.81, p = 0.0935$ (**Not Statistically Significant**).

---

## 5. Acceptance Gate Scorecard

| Gate Number | Requirement Target | Best Candidate Performance | Compliance Status |
| :---: | :--- | :--- | :---: |
| **Gate 1** | Overall Scream Recall $\ge 96.00\%$ | 70.00% (140/200) — E1 Rolling EMA | ❌ **FAILED BY ALL** (Gap: -26.00%) |
| **Gate 2** | Hard-Negative FPR $\le 5.00\%$ | 14.80% (74/500) — Candidate B + D | ❌ **FAILED BY ALL** (Gap: +9.80%) |
| **Gate 3** | Shouted-Speech FPR $\le 15.00\%$ | 14.00% (21/150) — Candidate B Baseline & B+D | ✅ **PASSED BY CANDIDATE B** |
| **Gate 4** | Short-Scream Recall $\ge 90.00\%$ | 39.13% (27/69) — Candidate B & E1 Rolling | ❌ **FAILED BY ALL** (Gap: -50.87%) |
| **Gate 5** | Model Inference P95 $\le 25.00$ ms | 0.48 ms — Candidate E1 Static | ✅ **PASSED BY ALL** |

---

## 6. Cryptographic Integrity & Quality Assurance

- **Automated Tests:** 35/35 automated invariant tests passed in 5.02s (100% pass rate).
- **Baseline Immutability:** All 12 baseline protected assets verified bit-for-bit identical to historical digests:
  - Production Classifier: `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f`
  - Candidate E1 Weights: `37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564`
  - Candidate B Weights: `f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378`
  - Sealed Manifest: `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd`
- **Zero Retraining / Sweeping:** No neural network weights were trained, tuned, or recalibrated.

---

## 7. Final Stage Sign-Off

Stage 8.9.61 is officially closed. The research conclusively proves that rolling-window temporal framing overcomes the boundary truncation defect of static center windows, elevating sustained scream recall to 86.26%. However, because continuous streaming significantly amplifies false alarms (35.40% FPR), and short cries remain diluted in 1.0s STFT windows, the prototype cannot satisfy life-safety requirements.

**FINAL PROMOTION DECISION: DENIED.**
**SYSTEM STATUS: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**

