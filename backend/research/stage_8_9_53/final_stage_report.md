# Stage 8.9.53: Final Research Stage Report
## Candidate E Independent Evaluation, Subgroup Robustness & Research Acceptance Audit

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.  
> No live-fire experiments, autonomous emergency dispatch, external emergency alerts, or claims of life-safety efficacy.  
> No production promotion is authorized.

---

## 1. Executive Summary & Core Research Findings

Stage 8.9.53 conducted an independent evaluation of Candidate E (`research_exp_candidate.pt`, SHA-256: `5ec5941448af4d3c77417a96e0ee5da5d8592ef5bc3c1103d3518378b37d13c1`) on the previously quarantined **`expansion_reserved_test`** cohort ($N=366$ recordings across 140 independent source groups).

Candidate E was evaluated in a fully frozen configuration at its validation-selected threshold $\theta = 0.4000$ without retraining, fine-tuning, recalibration, or threshold tuning.

### Primary Question Answered:
**Does Candidate E's reported 100% validation recall and 0% validation hard-negative FPR generalize to the previously quarantined, source-group-independent expansion test cohort?**

**Answer: NO. Candidate E's validation performance did not generalize.**
- On the independent reserved test cohort, Candidate E achieved an **overall scream recall of 62.75%** (64 / 102) [Wilson 95% CI: 53.06%, 71.51%] and a **hard-negative FPR of 16.29%** (43 / 264) [Wilson 95% CI: 12.32%, 21.22%].
- Candidate E experienced severe validation overfitting arising from its small development cohort ($N=200$ Dev, $N=120$ Val in Stage 8.9.51).
- In direct comparison on the exact same 366 recordings, the frozen **Candidate B Baseline substantially outperformed Candidate E**, achieving **71.57% recall** (73 / 102) with only **1.89% hard-negative FPR** (5 / 264) and an F1 score of **81.11%** vs Candidate E's **61.24%**.
- Paired McNemar testing demonstrated Candidate B's superiority over Candidate E with extreme statistical significance ($\chi^2 = 28.2133, p = 1.0865 \times 10^{-7}$). Candidate B was correct when Candidate E was wrong on 61 recordings, whereas Candidate E was correct when Candidate B was wrong on only 14 recordings.
- Candidate E failed three of the five research acceptance gates (Gates 1, 2, and 4).

---

## 2. Pre-Evaluation Integrity & Freeze Audit

Before unquarantining test features or calculating metrics, all ten pre-evaluation integrity requirements were verified:

| Check # | Integrity Pre-Condition | Verified Reality | Status |
|---|---|---|---|
| 1 | Candidate E Checkpoint SHA-256 | `5ec5941448af4d3c77417a96e0ee5da5d8592ef5bc3c1103d3518378b37d13c1` | **PASS** |
| 2 | Stage 8.9.52 Validation Checkpoint SHA-256 | Bit-for-bit cryptographic match (`5ec59414...`) | **PASS** |
| 3 | Preprocessing & Feature Extraction Code | Verified YAMNet polyphase resampler + subband filterbank | **PASS** |
| 4 | Normalization Parameters Fit | Raw linear projections inside model weights; no test fitting | **PASS** |
| 5 | Reserved Test Manifest Unchanged | Exactly 366 rows in verified CSV | **PASS** |
| 6 | Source-Group Disjointness (Train) | 0 overlapping source groups with `expansion_train` or `dev` | **PASS** |
| 7 | Source-Group Disjointness (Val) | 0 overlapping source groups with `expansion_val` or `val` | **PASS** |
| 8 | Audio & PCM Hash Collisions | 0 duplicate file SHA-256 or PCM hash collisions | **PASS** |
| 9 | Permissive IP Licensing | 100% CC0 / CC-BY; 0 NC or Sampling+ licenses | **PASS** |
| 10 | Threshold Provenance | Selected strictly from validation split ($\theta = 0.4000$) | **PASS** |

### Production Classifier Immobility:
All four canonical production assets remain **100% bit-for-bit frozen**:
- `backend/models/scream_classifier.joblib`: `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f`
- `backend/models/model_metadata.json`: `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60`
- `backend/reports/test_predictions.csv`: `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d`
- `backend/reports/stage5_test_evaluation.md`: `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2`

---

## 3. Reserved Test Cohort Composition (Phase A)

The verified evaluation denominator consists of **exactly 366 recordings**:
- **Authentic Screams (Positive, Class 1):** 102 recordings (27.87%) across 41 source groups.
- **Hard Negatives (Class 0):** 264 recordings (72.13%) across 104 source groups.
- **Total Unique Source Groups:** 140 independent source groups (mean 2.61 recordings/group).
- **Audio Decode Status:** 366 / 366 successfully decoded (0 corruption or I/O failures).
- **Ambiguous / Quarantined Recordings:** 0 excluded.

> [!NOTE]
> Physical manifest reconciliation confirmed 140 distinct source groups and a 102/264 positive/negative split, resolving typographical approximations from the Stage 8.9.52 markdown summary text.

---

## 4. Multi-Candidate Independent Performance Comparison (Phases B, C, D)

All three evaluated configurations operated on the identical 366 recordings at their frozen thresholds:

| Performance Metric | Candidate B Baseline ($\theta = 0.8000$) | Candidate B + Intervention D | Candidate E ($\theta = 0.4000$) |
|---|---|---|---|
| **True Positives (TP)** | 73 / 102 | 73 / 102 | **64 / 102** |
| **False Negatives (FN)** | 29 / 102 | 29 / 102 | **38 / 102** |
| **True Negatives (TN)** | 259 / 264 | 259 / 264 | **221 / 264** |
| **False Positives (FP)** | 5 / 264 | 5 / 264 | **43 / 264** |
| **Overall Scream Recall** | **71.57%** [62.16%, 79.42%] | **71.57%** [62.16%, 79.42%] | **62.75%** [53.06%, 71.51%] |
| **Hard-Negative FPR** | **1.89%** [0.81%, 4.36%] | **1.89%** [0.81%, 4.36%] | **16.29%** [12.32%, 21.22%] |
| **Precision** | **93.59%** [85.86%, 97.23%] | **93.59%** [85.86%, 97.23%] | **59.81%** [50.34%, 68.61%] |
| **Specificity** | **98.11%** | **98.11%** | **83.71%** |
| **F1 Score** | **81.11%** | **81.11%** | **61.24%** |
| **Accuracy** | **90.71%** (332 / 366) | **90.71%** (332 / 366) | **77.87%** (285 / 366) |
| **ROC-AUC** | **0.9746** | **0.9746** | **0.8128** |
| **PR-AUC** | **0.9392** | **0.9392** | **0.6609** |
| **Brier Score** | **0.0629** | **0.0629** | **0.1704** |
| **Expected Calibration Error (ECE)** | **0.0589** | **0.0589** | **0.1474** |

---

## 5. Subgroup Metrics Breakdown

Non-mutually exclusive real-world acoustic subgroups evaluated across all three models:

| Acoustic Subgroup | Class | Denom | Unique SGs | Candidate B Baseline | Candidate B + Interv D | Candidate E |
|---|---|---|---|---|---|---|
| **All Authentic Screams** | Pos | 102 | 41 | 73 (71.57%) | 73 (71.57%) | **64 (62.75%)** |
| **Short Screams (<1.0s)** | Pos | 22 | 13 | 16 (72.73%) | 16 (72.73%) | **19 (86.36%)** |
| **Ultra-Short Screams (<0.5s)** | Pos | 8 | 7 | 4 (50.00%) | 4 (50.00%) | **7 (87.50%)** * |
| **Standard-Short Screams (0.5-1.0s)** | Pos | 14 | 11 | 12 (85.71%) | 12 (85.71%) | **12 (85.71%)** |
| **Low-Intensity / Muffled Screams** | Pos | 3 | 2 | 2 (66.67%) | 2 (66.67%) | **3 (100.00%)** * |
| **Crowd-Masked Screams** | Pos | 29 | 16 | 21 (72.41%) | 21 (72.41%) | **21 (72.41%)** |
| **Sustained Screams ($\ge 1.0$s)** | Pos | 80 | 30 | 57 (71.25%) | 57 (71.25%) | **45 (56.25%)** |
| **All Hard Negatives** | Neg | 264 | 104 | 5 (1.89%) | 5 (1.89%) | **43 (16.29%)** |
| **Shouted Speech** | Neg | 111 | 34 | 1 (0.90%) | 1 (0.90%) | **9 (8.11%)** |
| **Crowd Cheering / Chanting** | Neg | 55 | 30 | 0 (0.00%) | 0 (0.00%) | **17 (30.91%)** |
| **Whistles and Squeaks** | Neg | 32 | 18 | 4 (12.50%) | 4 (12.50%) | **9 (28.12%)** |
| **Infant Crying** | Neg | 26 | 15 | 0 (0.00%) | 0 (0.00%) | **1 (3.85%)** |
| **Other Vocalizations / Environmental**| Neg | 40 | 23 | 0 (0.00%) | 0 (0.00%) | **7 (17.50%)** |

*\* Denotes subgroups with $N < 10$ flagged as INSUFFICIENT EVIDENCE.*

---

## 6. Source-Group Cluster Bootstrap & Significance Testing

### Cluster Resampling (1,000 Iterations)
Accounting for intra-source correlation:
- **Candidate E Scream Recall:** Mean = 63.30% [95% CI: 51.64%, 74.67%]
- **Candidate E Hard-Negative FPR:** Mean = 16.53% [95% CI: 10.82%, 23.19%]
- **Candidate B Scream Recall:** Mean = 71.84% [95% CI: 61.35%, 81.18%]
- **Candidate B Hard-Negative FPR:** Mean = 1.91% [95% CI: 0.65%, 4.02%]

### McNemar's Paired Statistical Significance Tests
- **Candidate E vs Candidate B (Overall):** $\chi^2 = 28.2133, p = 1.0865 \times 10^{-7}$ (**Statistically Significant** in favor of Candidate B).
- **Candidate E vs Candidate B (Hard Negatives):** $\chi^2 = 36.0250, p = 1.948 \times 10^{-9}$ (Candidate B produces vastly fewer false alarms).
- **Candidate E vs Candidate B (Positives):** $\chi^2 = 2.2500, p = 0.1336$ (Difference in positive recall alone is not statistically significant, but Candidate B detects more screams: 73 vs 64).

---

## 7. Forensic Error Analysis (Phase E)

- **Candidate E Missed Screams (38 False Negatives):**
  - Missed screams are primarily concentrated in sustained, lower-register authentic screams where background crowd murmur or lower fundamental frequency caused the gated MLP to depress logits below 0.4000.
  - While Candidate E improved recall on ultra-short screams (7/8 vs 4/8 for Candidate B), it suffered severe degradation on sustained screams (45/80 = 56.25% vs Candidate B's 57/80 = 71.25%).
- **Candidate E False Alarms (43 False Positives):**
  - Candidate E generated 43 false alarms across diverse categories: 17 crowd cheering/chanting clips (30.91% FPR), 9 whistles (28.12% FPR), 9 shouted speech (8.11% FPR), 7 environmental sound effects, and 1 infant cry.
  - The dynamic residual sigmoid gate between YAMNet and subband features over-amplified high-frequency subband ratios, triggering false alarms whenever cheering crowds or synthetic squeaks exhibited energy in the 2–4 kHz band.

---

## 8. Latency and Runtime Audit (Phase F)

Four decoupled timing regimes were benchmarked:
1. **Regime 1: Model-Only Latency:** Candidate E P50 = 0.257 ms, **P95 = 0.390 ms**, P99 = 0.489 ms.
2. **Regime 2: Feature Extraction Latency:** Subband filterbank P50 = 33.337 ms, **P95 = 39.379 ms**.
3. **Regime 3: Window Accumulation Latency:** 960.0 ms physical audio buffering.
4. **Regime 4: Operational Onset Delay:** 960 ms + 39.7 ms = ~1,000 ms.
- **Concurrent Scaling:** Single stream throughput = 3,574 fps; 8-stream throughput = 19,384 fps.
- **Memory Footprint:** Peak process memory = 13.82 MB (Candidate E model memory = ~1.2 MB).

---

## 9. Research Acceptance Gate Evaluation (Phase G)

| Gate | Criterion | Requirement | Candidate E Result | Gate Status |
|---|---|---|---|---|
| **Gate 1** | Overall Scream Recall | $\ge 96.0\%$ | **62.75%** [53.06%, 71.51%] | **FAIL** |
| **Gate 2** | Hard-Negative FPR | $\le 5.0\%$ | **16.29%** [12.32%, 21.22%] | **FAIL** |
| **Gate 3** | Shouted-Speech FPR | $\le 15.0\%$ | **8.11%** [4.32%, 14.69%] | **PASS** |
| **Gate 4** | Short-Scream Recall | $\ge 90.0\%$ | **86.36%** [66.67%, 95.25%] | **FAIL** |
| **Gate 5** | Computational Latency | P95 $\le 25.0$ ms | **0.390 ms** (Model P95) | **PASS** |

**Gate Compliance Verdict:** Candidate E **FAILS 3 of the 5 acceptance gates**.

---

## 10. Sanctioned Final Decision & Next Milestone Recommendation

### Sanctioned Decision Selected:
**`CANDIDATE E GENERALIZATION NOT SUPPORTED`**

### Technical Justification:
1. Candidate E's reported 100% validation recall and 0% validation FPR was an artifact of severe overfitting on the tiny historical development cohort ($N=200$).
2. On the untouched 140-source-group independent test cohort ($N=366$), Candidate E's recall collapsed to 62.75% and its hard-negative FPR exploded to 16.29%.
3. The frozen reference baseline (Candidate B) statistically significantly dominated Candidate E ($p = 1.08 \times 10^{-7}$), achieving 71.57% recall with only 1.89% HN-FPR.
4. Candidate E fails three mandatory research acceptance gates.

### Recommended Next Milestone:
**A separately approved Candidate E retraining experiment utilizing the 1,055-recording expansion training partition (`expansion_train`) and data augmentation, or preserving Candidate B as the superior baseline architecture.**
- Candidate E was originally trained on only 200 clips in Stage 8.9.51 and never saw the 1,055 expansion training clips curated in Stage 8.9.52.
- Before considering any further architecture modifications, Candidate E (or an improved dual-encoder variant) should be retrained on the full `expansion_train` partition with environmental background masking and tuned on `expansion_val`.
- Production classifier remains **100% frozen** at Stage 5 Logistic Regression ($\theta = 0.3500$).

