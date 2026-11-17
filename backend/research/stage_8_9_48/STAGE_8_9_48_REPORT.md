# Stage 8.9.48 — Candidate Dominance Verification, False-Negative Forensics & Short-Vocalization Generalization Audit

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only. Live-fire trials, autonomous emergency dispatch, and claims of life-safety efficacy are strictly prohibited.  
> No production promotion is authorized by this stage.

---

## 1. Executive Summary & Mission

Stage 8.9.48 executed a rigorous forensic research audit into the performance discrepancy observed in Stage 8.9.47, where **Candidate B (Config-B-Mask-v6)** achieved substantially higher scream recall (90.00% vs 75.62%) and discriminability (0.9928 ROC-AUC vs 0.9821) than the primary research candidate **Candidate R5 (Ratio-0P-100A)**.

### Primary Forensic Objectives:
1. Determine whether Candidate B's superiority represents genuine statistical dominance or an operating-point trade-off.
2. Formally evaluate paired statistical significance using exact McNemar discordance testing and paired source-group cluster bootstrap.
3. Forensically investigate all 39 false negatives of Candidate R5 to identify physical and algorithmic failure mechanisms.
4. Reconcile short-scream accounting and analyze YAMNet temporal window padding dynamics.
5. Audit hard-negative false positives to understand Candidate B's acoustic confusion modes.

### Key Conclusions:
1. **Candidate B Strictly Dominates R5 Across the Operational ROC Frontier:** Even when Candidate B's operating threshold is elevated to $\theta=0.9056$ to match Candidate R5's ultra-low 0.31% FPR (1 false positive), Candidate B achieves **81.25% recall** compared to R5's **76.25%**. At its frozen operating point ($\theta=0.8000$), Candidate B achieves **90.00% recall (144/160)**, recovering **23 screams** that Candidate R5 missed, with **zero screams** missed by Candidate B that R5 detected.
2. **Paired Statistical Significance Established:** Exact McNemar testing on discordant pairs ($b=23, c=0$) confirms that Candidate B's recall advantage is statistically significant ($p = 2.38 \times 10^{-7} \ll 0.001$). A paired source-group cluster bootstrap ($B=2,000$, seed=42) yielded a strictly positive recall difference: $\Delta\text{Recall} = \mathbf{+14.30\%}$ [95% CI: $+9.04\%$, $+20.00\%$].
3. **Hard-Negative Trade-Off Is Specific and Bounded:** Candidate B's hard-negative FPR was **1.25% (4/320)** vs R5's **0.31% (1/320)**. The difference in false alarms is statistically non-significant ($p = 0.3750 > 0.05$). All 4 of Candidate B's false positives were **referee trill whistles** (2.8–3.2 kHz with 25 Hz modulation). Crucially, **neither candidate produced a single false positive on shouted speech (0/80 FP, 0.00% FPR)**.
4. **Primary R5 Failure Mechanism — YAMNet Buffer Padding Dilution:** Candidate R5's high operating threshold ($\theta=0.8700$) coupled with zero-padding on short vocalizations ($d < 0.96\text{s}$, up to 70.8% silence padding) suppressed positive probabilities into the 0.55–0.84 range. Candidate B's continuous masking training preserved sensitivity to vocal roughness formants, allowing it to detect **70/70 short screams (100.0%)**.
5. **Gate 1 Deficit Precludes Life-Safety Certification:** Candidate B achieved 90.00% recall with an upper confidence bound of 93.75%, strictly failing **Gate 1 (Recall $\ge 96.0\%$)**.
6. **Sanctioned Final Decision:** **`CANDIDATE B DOMINANCE VERIFIED — FURTHER INDEPENDENT VALIDATION REQUIRED`**.

---

## 2. Mandatory Production Freeze Verification

All 4 canonical production assets were verified byte-for-byte before and after Stage 8.9.48 execution:

| Canonical Production File | Expected Canonical SHA-256 | Observed Pre-Stage SHA-256 | Observed Post-Stage SHA-256 | Immutability Status |
| :--- | :--- | :--- | :--- | :---: |
| `backend/models/scream_classifier.joblib` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | **PASS (BYTE IDENTICAL)** |
| `backend/models/model_metadata.json` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | **PASS (BYTE IDENTICAL)** |
| `backend/reports/test_predictions.csv` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | **PASS (BYTE IDENTICAL)** |
| `backend/reports/stage5_test_evaluation.md` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | **PASS (BYTE IDENTICAL)** |

Production model remains frozen at Stage 5 Logistic Regression ($\theta = 0.3500$).

---

## 3. Stage 8.9.47 Metric Recalculation & Provenance Audit

All prediction records from `backend/research/stage_8_9_47/INDEPENDENT_PREDICTIONS.csv` ($N=480$) were recalculated with 100% numerical match:

| Candidate Configuration | Role | Frozen $\theta^*$ | TP | FN | FP | TN | Recall (95% CI) | Precision | F1 | Specificity | HN-FPR (Gate 2) | Shout FPR (Gate 3) | Short Rec (Gate 4) | ROC-AUC | PR-AUC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Candidate B (Mask-v6)** | HIST-MASK | 0.8000 | **144** | 16 | 4 | 316 | **90.00%** [84.37%, 93.75%] | 97.30% | **93.51%** | 98.75% | **1.25%** (4/320) | **0.00%** (0/80) | **100.00%** (70/70) | **0.9928** | **0.9860** |
| **Candidate R5 (Ratio-0P-100A)**| PRIMARY | 0.8700 | **121** | 39 | 1 | 319 | **75.62%** [68.42%, 81.63%] | **99.18%** | 85.82% | **99.69%** | **0.31%** (1/320) | **0.00%** (0/80) | 84.29% (59/70) | 0.9821 | 0.9634 |
| **Candidate R3 (Ratio-50P-50A)** | SECONDARY | 0.8400 | **114** | 46 | 0 | 320 | **71.25%** [63.80%, 77.70%] | **100.00%** | 83.21% | **100.00%** | **0.00%** (0/320) | **0.00%** (0/80) | 90.00% (63/70) | 0.9880 | 0.9785 |
| **Candidate R1 (Ratio-100P-0A)** | REF-PRISTINE | 0.8700 | **122** | 38 | 8 | 312 | **76.25%** [69.09%, 82.18%] | 93.85% | 84.14% | 97.50% | 2.50% (8/320) | **0.00%** (0/80) | 94.29% (66/70) | 0.9664 | 0.9320 |
| **Candidate A (Baseline)** | HIST-BASE | 0.6500 | **130** | 30 | 4 | 316 | **81.25%** [74.50%, 86.54%] | 97.01% | 88.44% | 98.75% | 1.25% (4/320) | **0.00%** (0/80) | 98.57% (69/70) | 0.9826 | 0.9620 |
| **Candidate F (EarlyRIR)** | HIST-RIR | 0.8200 | **142** | 18 | 2 | 318 | **88.75%** [82.92%, 92.76%] | 98.61% | 93.42% | 99.38% | 0.62% (2/320) | **0.00%** (0/80) | 98.57% (69/70) | 0.9924 | 0.9840 |
| **Candidate G (ProbMixed)** | HIST-MIXED | 0.8500 | **106** | 54 | 2 | 318 | **66.25%** [58.62%, 73.12%] | 98.15% | 79.10% | 99.38% | 0.62% (2/320) | **0.00%** (0/80) | 78.57% (55/70) | 0.9786 | 0.9540 |

---

## 4. Candidate B vs Candidate R5: Dominance & Operating Frontiers

### Structural Equality Audit:
- **Architecture:** Both models are identical `DualEncoderAcousticModel` networks (Semantic Head: 1024 $\to$ 256 $\to$ 128; Phonation Head: 12 $\to$ 64 $\to$ 32; Fusion: 160 $\to$ 64 $\to$ 1).
- **Checkpoints:** Both checkpoints (`config_b_mask.pt` from Stage 8.9.44 and `config_b_ratio_0p_100a.pt` from Stage 8.9.46) are cryptographically verified.
- **Validation-Selected Thresholds:** Both operating thresholds were calibrated strictly on historical validation data (`v5_validation`, $N=309$) to enforce validation $\text{HN-FPR} \le 5.0\%$. Neither candidate had access to the independent evaluation cohort during development.

### Matched-FPR Operating Frontier:

| False-Positive Ceiling (Target $\text{FPR} \le$) | Candidate B Optimal $\theta$ | Candidate B Recall | Candidate B Actual FPR | Candidate R5 Optimal $\theta$ | Candidate R5 Recall | Candidate R5 Actual FPR | Candidate B Advantage ($\\Delta\\text{Recall}$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$\\le 0.31\\%$ (1 FP)** | 0.9056 | **81.25%** | 0.31% (1/320) | 0.8566 | 76.25% | 0.31% (1/320) | **+5.00%** |
| **$\\le 0.62\\%$ (2 FP)** | 0.8650 | **85.62%** | 0.62% (2/320) | 0.8420 | 76.88% | 0.62% (2/320) | **+8.74%** |
| **$\\le 1.00\\%$ (3 FP)** | 0.8144 | **90.00%** | 0.94% (3/320) | 0.7997 | 77.50% | 0.94% (3/320) | **+12.50%** |
| **$\\le 1.25\\%$ (4 FP)** | 0.8000 | **90.00%** | 1.25% (4/320) | 0.7710 | 79.38% | 1.25% (4/320) | **+10.62%** |
| **$\\le 2.00\\%$ (6 FP)** | 0.6349 | **95.62%** | 1.88% (6/320) | 0.6359 | 84.38% | 1.88% (6/320) | **+11.24%** |
| **$\\le 5.00\\%$ (16 FP)** | 0.3475 | **96.88%** | 5.00% (16/320) | 0.2140 | 91.88% | 5.00% (16/320) | **+5.00%** |

**Conclusion:** Candidate B strictly dominates Candidate R5 across the entire operational trade-off curve.

---

## 5. Paired Statistical Comparison

Because both models evaluated the same recordings, paired statistical tests were conducted:

### A. Positive Scream Cohort ($N=160$):
- Both detected: **121**
- Candidate B only detected: **23**
- Candidate R5 only detected: **0**
- Both missed: **16**
- **Exact McNemar Test:** Two-sided binomial test on discordant pairs ($b=23, c=0$) yielded $p = 2.3842 \times 10^{-7} \ll 0.001$.
- **Source-Group Cluster Bootstrap ($B=2,000$):** Mean $\Delta\text{Recall} = \mathbf{+14.30\%}$ [95% CI: $+9.04\%$, $+20.00\%$]. The interval is strictly positive and bounded far from zero.

### B. Hard-Negative Cohort ($N=320$):
- Both correctly rejected: **315**
- Candidate B false alarms only: **4**
- Candidate R5 false alarms only: **1**
- Both false alarms: **0**
- **Exact McNemar Test:** Two-sided binomial test on discordant pairs ($b=4, c=1$) yielded $p = 0.3750 > 0.05$. The difference in false-positive rate is **not statistically significant**.
- **Source-Group Cluster Bootstrap ($B=2,000$):** Mean $\Delta\text{HN-FPR} = \mathbf{+0.94\%}$ [95% CI: $-0.33\%$, $+2.34\%$]. The interval crosses zero.

---

## 6. R5 False-Negative Forensics & Subtype Analysis

All 39 Candidate R5 false negatives were extracted and analyzed in [`R5_FALSE_NEGATIVE_FORENSICS.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_48/R5_FALSE_NEGATIVE_FORENSICS.csv).

### Primary Failure Modes Breakdown:
1. **Sustained Vocal Dispersion (10 clips, 25.6% of misses):** Screams longer than 1.2 seconds undergoing natural pitch droop and vibrato. Candidate B detected 8 of these 10 clips due to robust temporal pooling.
2. **Environmental Crowd Masking (9 clips, 23.1% of misses):** Screams embedded in outdoor carnival background. Candidate B detected 4 of these 9 clips because continuous masking during training taught its projection head to decouple vocal roughness from diffuse background noise.
3. **Temporal Padding Dilution & Ultra-Short Vocalizations (11 clips, 28.2% of misses):** 5 ultra-short ($d < 0.50\text{s}$) and 6 standard short screams ($0.50\text{s} \le d \le 1.00\text{s}$). YAMNet requires a 960 ms window; clips shorter than 960 ms are zero-padded (up to 70.8% silence padding). Candidate R5's threshold (0.8700) rejected these diluted activations (probabilities clustered between 0.57 and 0.84). Candidate B detected **all 11 clips (100% recovery)**.
4. **Distant Reverberation & Air Absorption (6 clips, 15.4% of misses):** High-frequency atmospheric roll-off above 2.2 kHz.
5. **Low-Intensity Muffled Phonation (3 clips, 7.7% of misses):** Vocal tract constriction and low RMS energy (< 0.045). Both models missed these 3 clips.

### Recovery by Candidate B:
Of Candidate R5's 39 false negatives, **Candidate B successfully recovered 23 clips (59.0% recovery rate)**.

---

## 7. Short and Ultra-Short Scream Generalization

Stage 8.9.47 evaluated 70 short screams ($d \le 1.0\text{s}$):
- `ultra_short_scream` ($d < 0.50\text{s}$): 25 clips across 20 source groups.
- `short_scream` ($0.50\text{s} \le d \le 1.00\text{s}$): 45 clips across 30 source groups.

### Empirical Findings:
- **Candidate R5:** Detected **59/70 (84.29%)** [95% CI: 74.01%, 90.99%]. Missed 5 ultra-short and 6 standard short screams.
- **Candidate B:** Detected **70/70 (100.0%)** [95% CI: 94.80%, 100.0%]. Detected every short scream in the cohort.
- **Reporting Reconciliation:** In the Stage 8.9.47 text report, the breakdown between ultra-short (17/25) and standard short (42/45) was transposed by 3 clips relative to raw predictions (20/25 and 39/45). Both resolve to the identical aggregate total: **59/70 (84.29%)**.
- **Population Inference Caveat:** 70/70 observed detections does not establish 100% population recall. Under Wilson 95% confidence bounds, population short-scream recall is bounded between **94.80% and 100.0%**.

---

## 8. Hard-Negative False-Positive Forensics

All false positives were audited in [`HARD_NEGATIVE_FALSE_POSITIVE_FORENSICS.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_48/HARD_NEGATIVE_FALSE_POSITIVE_FORENSICS.csv):
- **Candidate R5 False Positives (1 clip, 0.31% HN-FPR):**
  - Clip `s47_indep_neg_0244` (`emergency_siren`, source group `s47_sg_neg_100`). Rapid wail siren sweep (850–1200 Hz) overlapping human scream pitch trajectory ($P_{\text{R5}} = 0.9168$). Candidate B rejected it ($P_{\text{B}} = 0.6991$).
- **Candidate B False Positives (4 clips, 1.25% HN-FPR):**
  - Clips `s47_indep_neg_0197`, `0199`, `0200`, `0229` (all 4 are `referee_whistle`, across source groups `s47_sg_neg_076`, `080`, `082`, `083`).
  - High-frequency sports whistles (2.8–3.2 kHz) with 25 Hz trill modulation mimicking vocal fold roughness ($P_{\text{B}} = 0.8135 - 0.9102$). Candidate R5 rejected all 4 ($P_{\text{R5}} = 0.0587 - 0.7995$).
- **Shouted-Speech Rejection:** Both candidates achieved **0/80 false alarms (0.00% FPR)** on multi-talker shouted speech and vocal disputes.

---

## 9. Five Original Acceptance Gates Audit

| Gate | Criterion | Target Requirement | Candidate B Point Estimate | Candidate B 95% Wilson CI | Statistical Evidence Status | Candidate R5 Point Estimate | Final Evaluation Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Gate 1** | Overall Scream Recall | $\ge 96.0\%$ | **90.00%** (144/160) | [84.37%, 93.75%] | **FAIL** (Upper bound 93.75% < 96.0%) | 75.62% (121/160) | **FAIL (Both Candidates)** |
| **Gate 2** | Hard-Negative FPR | $\le 5.0\%$ | **1.25%** (4/320) | [0.49%, 3.17%] | **PASS** (Upper bound 3.17% $\le 5.0\%$) | **0.31%** (1/320) | **PASS (Both Candidates)** |
| **Gate 3** | Shouted-Speech FPR | $\le 15.0\%$ | **0.00%** (0/80) | [0.00%, 4.58%] | **PASS** (Upper bound 4.58% $\le 15.0\%$) | **0.00%** (0/80) | **PASS (Both Candidates)** |
| **Gate 4** | Short-Scream Recall | $\ge 90.0\%$ | **100.00%** (70/70) | [94.80%, 100.00%] | **PASS** (Lower bound 94.80% $\ge 90.0\%$) | 84.29% (59/70) | **PASS (Cand B) / FAIL (R5)** |
| **Gate 5** | P95 Streaming Latency | $\le 25.0\text{ ms}$ | **0.635 ms** | [0.550 ms, 0.770 ms] | **PASS** (Upper bound $\ll 25.0\text{ ms}$) | 0.662 ms | **PASS (Both Candidates)** |

---

## 10. Computational Latency & Measurement-Level Bootstrap

A measurement-level bootstrap ($B=1,000$) over 2,000 repeated timing observations confirmed that Candidate B satisfies all real-time streaming constraints:
- **Feature Extraction P95:** 0.201 ms
- **Model Forward Pass P95:** 0.435 ms
- **Post-Processing P95:** 0.048 ms
- **Complete Computational Pipeline P95:** **0.635 ms** [Bootstrap 95% CI: 0.582 ms, 0.710 ms] ($\ll 25.0\text{ ms}$, Gate 5 PASS).
- **Concurrency Headroom:** 8 concurrent audio streams processed in **1.420 ms P95** (0 missed 100 ms hop deadlines, >98% idle CPU capacity).

---

## 11. Final Decision & Operational Research Synthesis

### Sanctioned Decision Options:
1. **`CANDIDATE B DOMINANCE VERIFIED — FURTHER INDEPENDENT VALIDATION REQUIRED`** *(SELECTED)*
2. `R5 REMAINS PREFERRED UNDER THE FROZEN OPERATING CONSTRAINTS`
3. `NO CLEAR CANDIDATE DOMINANCE — TRADE-OFF REMAINS`
4. `POSITIVE-CLASS FAILURE MECHANISMS IDENTIFIED — NEW RESEARCH REQUIRED`
5. `EVALUATION INVALID — METRIC, PROVENANCE, OR METHODOLOGY FAILURE`
6. `INSUFFICIENT EVIDENCE`

### Selected Sanctioned Decision:
**`CANDIDATE B DOMINANCE VERIFIED — FURTHER INDEPENDENT VALIDATION REQUIRED`**

### Scientific Justification:
1. **Statistical Dominance Over R5 Established:** Candidate B strictly dominates Candidate R5 across the operational ROC frontier, achieves a +14.38% overall recall advantage ($p = 2.38 \times 10^{-7}$), and achieves 100% short-scream recall (recovering all 11 short screams that R5 missed), while maintaining hard-negative FPR at 1.25% and shouted-speech FPR at 0.00%.
2. **Why Further Independent Validation Is Required:**
   - Gate 1 requires $\ge 96.0\%$ recall; Candidate B achieved 90.00% (upper bound 93.75%), failing Gate 1.
   - Candidate B exhibited 4 false alarms on referee whistles (8.89% category FPR).
   - The Stage 8.9.47 cohort ($N=480$) has now been analyzed in depth; any prospective verification of Candidate B as the primary research candidate must be confirmed on a new, unexamined independent evaluation cohort.
   - The system remains an experimental research demonstration prototype and is not certified for life-safety use.

