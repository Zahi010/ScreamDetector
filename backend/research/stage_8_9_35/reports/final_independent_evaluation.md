# Stage 8.9.35 — Final Independent Scientific Evaluation Report

**Stage:** 8.9.35 — Final Scientific Audit & Gate Verification  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Status:** Strictly Isolated Research  
**Authoritative Cohort:** Independent Held-Out Test Split ($N=293$, 102 screams, 191 hard negatives, 111 source groups)  
**Artifact References:**
- `backend/research/stage_8_9_35/evaluation/candidate_acceptance_matrix.csv`
- `backend/research/stage_8_9_35/evaluation/candidate_comparison.csv`
- `backend/research/stage_8_9_35/predictions/test_predictions_stage8_9_35.csv`

---

## 1. Evaluation Integrity Protocol

To prevent methodological bias and historical data contamination:
1. **Identical Test Cohort:** Evaluated strictly on the frozen $N=293$ held-out test cohort established in Stage 8.9.33 and audited in Stage 8.9.34. No source groups from training or validation overlap with this test set.
2. **Threshold Immutability:** Operating threshold for Candidate D was chosen strictly on the validation partition ($N=293$) and frozen at **$\theta^* = 0.43$** prior to scoring the test cohort. No post-hoc threshold tuning was conducted on the test cohort.
3. **No Synthetic Mixing:** Simulated spatial audio data from Track B was completely isolated. The empirical evaluation contains zero synthetic spatial recordings.
4. **Spatial Hardware Ground Truth:** Because the edge device has a single INMP441 microphone and all 293 test files are monophonic, physical multichannel spatial performance is certified as **NOT EVALUABLE**.

---

## 2. Predefined Acceptance Gate Scorecard

To qualify for production promotion consideration, a single research candidate must simultaneously satisfy all five predefined acceptance gates:

| Acceptance Gate | Required Threshold | Dual-Encoder Baseline | Subband RF (Cand B) | Subband LR (Cand C) | Multi-Pathway Fusion (Cand D) | Candidate D Gate Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Gate 1: Overall Scream Recall** | $\ge 96.00\%$ | 82.35% (84/102) | 73.53% (75/102) | 77.45% (79/102) | **89.22% (91/102)** | **FAIL (-6.78%)** |
| **Gate 2: Hard-Negative FPR** | $\le 5.00\%$ | 6.28% (12/191) | 14.14% (27/191) | 24.08% (46/191) | **9.95% (19/191)** | **FAIL (+4.95%)** |
| **Gate 3: Shouted-Speech FPR** | $\le 15.00\%$ | 8.33% (4/48) | 16.67% (8/48) | 18.75% (9/48) | **14.58% (7/48)** | **PASS** |
| **Gate 4: Short-Scream Recall** | $\ge 90.00\%$ | 80.00% (4/5) | 40.00% (2/5) | 60.00% (3/5) | **100.00% (5/5)\*** | **PASS\*** |
| **Gate 5: Computational P95** | $\le 25.00\text{ ms}$ | 18.57 ms | 18.57 ms | 18.57 ms | **19.31 ms** | **PASS** |
| **Simultaneous Gate Pass?** | **All 5 Must Pass** | **FAIL (3/5)** | **FAIL (1/5)** | **FAIL (1/5)** | **FAIL (3/5)** | **REJECTED** |

*\*Note on Gate 4: Sample size is limited to $N=5$ instances in the held-out test cohort. While 5/5 screams were detected, this sample size is statistically insufficient to prove population recall $\ge 90\%$ at 95% confidence.*

---

## 3. Detailed Comparative Performance Metrics

| Evaluation Metric | Baseline Dual-Encoder | Subband RF (Cand B) | Subband LR (Cand C) | Multi-Pathway Fusion (Cand D) |
| :--- | :---: | :---: | :---: | :---: |
| **True Positives (TP)** | 84 | 75 | 79 | **91** |
| **False Negatives (FN)** | 18 | 27 | 23 | **11** |
| **False Positives (FP)** | **12** | 27 | 46 | 19 |
| **True Negatives (TN)** | **179** | 164 | 145 | 172 |
| **Sensitivity / Recall** | 82.35% | 73.53% | 77.45% | **89.22%** |
| **Specificity** | **93.72%** | 85.86% | 75.92% | 90.05% |
| **Precision** | **87.50%** | 73.53% | 63.20% | 82.73% |
| **F1-Score** | 0.8485 | 0.7353 | 0.6960 | **0.8585** |
| **ROC-AUC** | 0.9285 | 0.8525 | 0.8335 | **0.9374** |
| **PR-AUC** | 0.8717 | 0.7593 | 0.7279 | **0.8762** |
| **Infant-Cry FPR** | 6.67% (1/15) | 6.67% (1/15) | 6.67% (1/15) | 6.67% (1/15) |
| **Crowd-Cheering FPR** | **11.90% (5/42)** | 16.67% (7/42) | 38.10% (16/42) | 16.67% (7/42) |
| **Shouted-Speech FPR** | **8.33% (4/48)** | 16.67% (8/48) | 18.75% (9/48) | 14.58% (7/48) |
| **Whistle & Siren FPR** | **0.00% (0/18)** | 5.56% (1/18) | 11.11% (2/18) | **0.00% (0/18)** |
| **Other High-Energy FPR** | **8.82% (6/68)** | 10.29% (7/68) | 16.18% (11/68) | 10.29% (7/68) |

---

## 4. Scientific Audit Analysis

### A. Advances Delivered by Multi-Pathway Fusion (Candidate D)
1. **Significant Sensitivity Gain:**
   - Recall increased from 82.35% to 89.22% (+6.87%), successfully detecting 91 out of 102 screams. The model recovered 7 screams that the baseline missed entirely.
2. **Short-Scream Detection:**
   - Candidate D achieved 100.0% detection on short screams (5/5), leveraging instantaneous Butterworth band energy ratios to compensate for temporal pooling dilution.
3. **Whistle & Siren Immunity:**
   - The high-frequency whistle ratio head ($B_6 / (B_4+B_5)$) successfully achieved 0.00% false alarms on whistles and emergency sirens, rejecting synthetic acoustic interference.
4. **Real-Time Efficiency:**
   - Despite processing three multi-modal pathways, computational P95 was 19.31 ms, well beneath the 25.00 ms budget.

### B. Persistent Scientific Deficiencies
1. **Gate 1 Failure (Recall < 96%):**
   - 11 screams in the test set remain undetected. These missed screams primarily consist of low-energy, muffled, or reverberant distant screams where acoustic energy fails to breach the $\theta^* = 0.43$ threshold.
2. **Gate 2 Failure (HN-FPR > 5%):**
   - Candidate D generated 19 false alarms across the 191 hard negatives (9.95% FPR). These false alarms were driven by high-energy crowd cheering (7 false positives) and excited shouted speech (7 false positives). The physical resonance of multiple simultaneous cheering spectators generates aggregate harmonic energy in the 2–3 kHz band that triggers the subband head.

---

## 5. Formal Scientific Determination

In strict accordance with the mandatory evaluation framework:
- Candidate D failed Gate 1 (89.22% vs. 96.00% required).
- Candidate D failed Gate 2 (9.95% vs. 5.00% required).
- A candidate cannot be certified if any single gate fails.
- Therefore, the official determination for Stage 8.9.35 is:

### **REJECTED FOR PRODUCTION — RESEARCH ONLY**
