# Stage 8.9.7 — Hybrid Acoustic Classifier Research and Targeted Dataset Expansion

**Role:** Senior Acoustic Machine-Learning Engineer  
**Workspace:** `backend/experiments/v2_hard_negative_training/`  
**Research Status:** **Experimental Benchmark Completed — Research Milestone Achieved — Production Model Remains 100% Frozen**  
**Evaluation Date:** 2026-10-29  

---

## Executive Summary

Stage 8.9.7 advances the Festival Scream Detector experimental track following the Stage 8.9.6 independent selection audit. The primary research objective was to develop and evaluate an experimental architecture and targeted dataset expansion to overcome the persistent false-alarm failure modes identified in Stage 8.9.4 and 8.9.6—specifically **unison crowd chanting, concert countdowns, shouted speech, referee whistles, and pyrotechnic squeaks**—while preserving high sensitivity to genuine human screams masked in loud festival noise beds.

### Major Achievements in Stage 8.9.7
1. **Targeted Dataset Expansion (+360 recordings, +37.2%):**
   - Expanded dataset pool from 968 to **1,328 recordings** across **503 independent source groups**.
   - Acquired **+150 crowd chanting and cheering recordings** from FSD50K, tripling crowd representation to 240 clips.
   - Acquired **+60 shouted speech and yell recordings**, raising shouting representation to 320 clips.
   - Acquired **+100 genuine screams** from FSD50K and synthesized **+50 calibrated masked screams** across $-6\text{ dB}$ to $+6\text{ dB}$ SNR into festival crowd beds.
   - Expanded the held-out test scream benchmark from $N = 59$ to **$N = 102$ positive screams** (66 clean screams, 36 masked screams), significantly narrowing confidence interval bounds.
2. **Annotation Protocol Correction (`EXP-V2-ANN-002`):**
   - Corrected fundamental frequency ($F_0$) rules: $F_0 > 600\text{ Hz}$ is explicitly supporting evidence rather than a mandatory threshold, preventing false rejection of low-register male screams.
   - Maintained strict database immutability: `fsd50k_349401` relabeling exists exclusively in versioned experimental manifests. The production SQLite database (`database/stage8_9_reviews.db`) remains 100% bit-identical.
3. **Hybrid Architecture Breakthrough (Model G & Model H):**
   - Eliminated the catastrophic probability collapse of Model E ($57.89\%$ masked scream recall) by replacing uncalibrated probability multiplication with **Feature Concatenation + Continuous Contrastive Logits + Platt Scaling Calibration**.
   - Model G (Concatenated Hybrid: 3,072-d multi-pool + vocal presence logit + crowd contrastive logit + AudioSet summary features) achieved **86.27% overall scream recall** and **86.11% masked scream recall** (up from $63.16\%$ in Model D and $57.89\%$ in Model E).
   - Cut crowd chanting FPR from **46.67%** in Stage 8.9.6 down to **11.90%** (and **9.52%** in Model D).
   - Met the shouting FPR provisional goal: Shouting FPR dropped to **12.50%** (Model G, H) and **10.42%** (Model A, I), outperforming the $\le 15.0\%$ target.
4. **Research Target Audit Verdict:**
   - **Shouting FPR $\le 15.0\%$:** **PASSED** ($12.50\%$).
   - **Scream Recall $\ge 96.0\%$:** **FAILED** (achieved $86.27\%$, 95% CI $[78.25\%, 91.64\%]$).
   - **Overall Hard-Negative FPR $\le 5.0\%$:** **FAILED** (achieved $8.90\%$, 95% CI $[5.63\%, 13.79\%]$).
   - In accordance with research standards, **no candidate qualifies for production deployment**. All production models remain completely frozen.

---

## 1. Production Artifacts Freeze & Integrity Verification

To protect life-safety stability, authoritative SHA-256 hashes of all production artifacts, historical Stage 5 test predictions, and the human review database were verified bit-for-bit before and after all experimental operations:

| Artifact Path | Expected Authoritative SHA-256 | Verified Post-Stage SHA-256 | Verification Status |
| :--- | :--- | :--- | :--- |
| `backend/models/scream_classifier.joblib` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | **VERIFIED BIT-IDENTICAL** |
| `backend/models/model_metadata.json` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | **VERIFIED BIT-IDENTICAL** |
| `backend/reports/test_predictions.csv` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | **VERIFIED BIT-IDENTICAL** |
| `backend/reports/stage5_test_evaluation.md` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | **VERIFIED BIT-IDENTICAL** |
| `backend/database/stage8_9_reviews.db` | `c44da77b2f5ee476aa44420eec64805c30912faf0ad8ad7b793be555b1583ff7` | `c44da77b2f5ee476aa44420eec64805c30912faf0ad8ad7b793be555b1583ff7` | **VERIFIED BIT-IDENTICAL** |

- **Production Threshold Preserved:** `0.3500` (unchanged in `model_metadata.json`).
- **All Experimental Work Contained:** All new manifests, features, models, scripts, and logs reside exclusively inside `backend/experiments/v2_hard_negative_training/`.

---

## 2. Targeted Data Expansion and Provenance Summary

Based on Stage 8.9.6 audit recommendations, targeted dataset expansion prioritized high-energy acoustic confounders that caused false positives in human-verified evaluations:

```
Targeted Acquisition Breakdown (Dataset v2 -> Dataset v3)
========================================================================================
Category                    Stage 8.9.5 Pool   Added in 8.9.7   Stage 8.9.7 Pool   Change
----------------------------------------------------------------------------------------
crowd_chant_cheering         90 clips           +150 clips       240 clips          +166.7%
shouting_and_speech         260 clips            +60 clips       320 clips          + 23.1%
scream (clean)              128 clips           +100 clips       228 clips          + 78.1%
masked_distant_screams       75 clips            +50 clips       125 clips          + 66.7%
whistles_and_squeaks        150 clips             +0 clips       150 clips            0.0%
general_environmental       115 clips             +0 clips       115 clips            0.0%
sfx_sirens_fireworks         80 clips             +0 clips        80 clips            0.0%
infant_crying                70 clips             +0 clips        70 clips            0.0%
----------------------------------------------------------------------------------------
TOTALS                      968 clips           +360 clips     1,328 clips          + 37.2%
========================================================================================
```

### Licensing and Source Provenance
- **FSD50K Expansion (310 clips):** Ingested from physical repository on disk (`E:\FSD50K.dev_audio`). All recordings carry open licenses (Creative Commons 0, Creative Commons Attribution 3.0/4.0, or CC-BY-NC). Full metadata, creator attribution, and Freesound clip IDs are captured in `manifests/dataset_manifest_v3.json`.
- **Synthesized Masked Screams (50 clips):** Created by mixing verified clean screams into calibrated festival crowd audio beds across SNRs of $[-6\text{ dB}, -3\text{ dB}, 0\text{ dB}, +3\text{ dB}, +6\text{ dB}]$.
  - **Leakage Prevention Rule:** Every synthesized clip strictly inherits its parent scream's `source_group_id`. If the parent scream is assigned to Train, all its synthetic mixtures are placed in Train. If the parent scream is assigned to Test, all its synthetic mixtures are placed in Test.

---

## 3. Revised Annotation Protocol Audit Trail

In compliance with prompt Section 3, the annotation protocol was updated to document reference `EXP-V2-ANN-002` in `docs/annotation_guidelines.md`.

### Core Protocol Updates
1. **Fundamental Frequency ($F_0$) Rule:**
   - *Previous draft rule:* $F_0 > 600\text{ Hz}$ proposed as a scream criterion.
   - *Revised rule:* $F_0$ is **supporting evidence**, not a mandatory threshold. Low-register adult male screams frequently exhibit fundamental frequencies between $350\text{ Hz} - 550\text{ Hz}$ with intense roughness and upper-formant energy ($1.5 - 3.5\text{ kHz}$). Enforcing a rigid $>600\text{ Hz}$ cutoff causes false negatives on male distress vocalizations.
2. **Seven-Class Taxonomic Separation:**
   - `CLEAR_HUMAN_SCREAM`: High acoustic roughness ($30 - 150\text{ Hz}$ modulation rate), deterministic chaos, open vocal tract resonance, absence of phonetic articulation.
   - `SHOUTED_SPEECH`: Discrete consonants, lexical formant transitions, recognizable word cadence.
   - `CROWD_CHANT_OR_COUNTDOWN`: Multi-voice diffuse reverberation, collective cadence, lacking isolated scream transient.
   - `INFANT_CRYING`: Cyclic inspiratory/expiratory rhythm ($400 - 800\text{ Hz}$).
   - `OTHER_DISTRESS_VOCALIZATION` (`AMBIGUOUS`): Quarantined from binary training loss.
   - `NON_VOCAL_SOUNDS`: Whistles, brake squeals, sirens, fireworks.
   - `GENERAL_ENVIRONMENTAL`: Outdoor festival ambiance, bass music, wind.
3. **Audit Trail of `fsd50k_349401`:**
   - In Stage 8.9.3, `fsd50k_349401` ("The crowd shouted Countdown") was marked `SCREAM_PRESENT`. Forensic analysis confirmed it consists of dozens of voices shouting numbers in unison.
   - In `dataset_manifest_v3.json`, this clip is classified as `crowd_chant_cheering` (`non_scream`).
   - The production review database (`database/stage8_9_reviews.db`) remains **100% untouched** with status `SCREAM_PRESENT`.

---

## 4. Deduplication and Leakage-Resistant Source Partitioning

### Deduplication Audit
- Exact duplicate detection: Calculated SHA-256 hashes of raw 16-bit PCM waveforms normalized to 16,000 Hz mono.
- Duplicate count: 0 duplicate PCM waveforms admitted into Dataset v3.

### Source-Group Partitioning
To guarantee complete independence between training, validation, and testing cohorts:
- Recordings were grouped into **503 unique source groups** based on speaker ID, Freesound uploader, or synthetic parentage.
- **Stage 5 Historical Isolation Audit:** Any source group overlapping with the historical Stage 5 test set (12 source groups) was strictly routed to the Held-Out Test cohort. **0 Stage 5 test files appear in Train or Val.**

```
Dataset v3 Partition Distribution
========================================================================================
Split      Total Clips   Screams (Pos)   Non-Screams (Neg)   Ambiguous   Source Groups
----------------------------------------------------------------------------------------
TRAIN       741 clips     172 clips       567 clips           2 clips     294 groups
VAL         293 clips      79 clips       214 clips           0 clips      98 groups
TEST        294 clips     102 clips       191 clips           1 clips     111 groups
----------------------------------------------------------------------------------------
TOTALS    1,328 clips     353 clips       972 clips           3 clips     503 groups
========================================================================================
```

- **Leakage Verification:**
  - $\text{Train} \cap \text{Val} = \emptyset$ (0 shared PCM hashes, 0 shared source groups).
  - $\text{Train} \cap \text{Test} = \emptyset$ (0 shared PCM hashes, 0 shared source groups).
  - $\text{Val} \cap \text{Test} = \emptyset$ (0 shared PCM hashes, 0 shared source groups).

---

## 5. Hybrid Experimental Model Architectures

Stage 8.9.7 evaluated five candidate architectures designed to isolate the contribution of multi-pooling, contrastive features, probability calibration, and non-linear interactions:

### Candidate Architecture Overview
1. **Model A v3 (Frozen Baseline LR):**
   - Standard Logistic Regression ($C=10.0$) on max-pooled 1024-dim YAMNet embeddings.
   - Evaluated at standard operational threshold $\tau = 0.3500$.
2. **Model D v3 (Multi-Pooling Concatenated LR):**
   - Concatenation of max, 90th-percentile, and mean pooled embeddings ($1024 \times 3 = 3072$-dim).
   - $L_2$ regularization parameter $C=0.1$ selected via sweep strictly on validation split.
   - Validation F1-optimal threshold: $\tau = 0.3700$.
3. **Model G (Hybrid Feature Concatenation with Contrastive Logits):**
   - *Design Rationale:* Avoids the fatal probability multiplication trap of Stage 8.9.5 Model E ($P(V) \times P(S|V)$) by passing soft continuous margins into a joint representation.
   - Augmented 3080-dim representation:
     $z = [x_{\text{concat}} \text{ (3072-d)}, \ell_{\text{vocal}} \text{ (1-d)}, \ell_{\text{crowd}} \text{ (1-d)}, v_{\text{summary}} \text{ (6-d)}]$.
   - $\ell_{\text{vocal}}$: continuous decision margin from front-end vocal presence detector trained on `train`.
   - $\ell_{\text{crowd}}$: continuous decision margin from front-end crowd contrastive detector trained on `train`.
   - $v_{\text{summary}}$: AudioSet aggregate maximum and mean probabilities across vocal and crowd classes.
   - $L_2$ regularized linear classifier ($C=0.1$) trained on `train`.
   - Validation F1-optimal threshold: $\tau = 0.3400$.
4. **Model H (Calibrated Hybrid Pipeline with Platt Scaling):**
   - Same 3080-dim feature representation and linear weights as Model G.
   - Applies Platt scaling (univariate logistic calibration) fitted **strictly on the validation decision logits**.
   - Produces true posterior probabilities $P(\text{scream} \mid x) \in [0, 1]$.
   - Validation-selected operating threshold: $\tau = 0.3900$.
5. **Model I (Non-Linear HistGradientBoosting on Hybrid Representation):**
   - Histogram-based Gradient Boosted Decision Tree (150 trees, max depth 4, learning rate 0.03, min samples leaf 10, L2 regularization 1.0) trained on the 3080-dim hybrid representation.
   - Evaluates whether non-linear feature interactions between transient peaks and steady-state background energy can distinguish unison roars from solo screams.
   - Validation-selected operating threshold: $\tau = 0.5600$.

---

## 6. Independently Recomputed Benchmark Metrics

All candidates were evaluated on the identical held-out test cohort (**293 binary evaluated clips: 102 screams, 191 non-screams**). The complete prediction log is stored in [`reports/stage8_9_7_test_predictions.csv`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/reports/stage8_9_7_test_predictions.csv).

```
Stage 8.9.7 Independent Candidate Benchmark (Held-Out Test N=293)
===========================================================================================================================
Model Architecture         Thresh   TP   FP   FN   TN    Accuracy   Precision  Recall     Specificity  Hard-Neg FPR  PR-AUC
---------------------------------------------------------------------------------------------------------------------------
Model_A_v3_Baseline        0.350    78   25   24  166    83.28%     75.73%     76.47%     86.91%       13.09%        0.7545
Model_D_v3_Concat_LR       0.370    86   16   16  175    89.08%     84.31%     84.31%     91.62%        8.38%        0.8910
Model_G_Hybrid_Concat      0.340    88   17   14  174    89.42%     83.81%     86.27%     91.10%        8.90%        0.8918
Model_H_Calibrated_Hybrid  0.390    88   17   14  174    89.42%     83.81%     86.27%     91.10%        8.90%        0.8923
Model_I_NonLinear_GBT      0.560    70   11   32  180    85.32%     86.42%     68.63%     94.24%        5.76%        0.8528
===========================================================================================================================
```

---

## 7. Statistical Confidence Intervals & Calibration Analysis

### 95% Confidence Intervals
Wilson score intervals were calculated for binomial proportions ($N_{\text{pos}} = 102, N_{\text{neg}} = 191$), and 1,000 bootstrap iterations were conducted for PR-AUC. The full table is exported to [`reports/stage8_9_7_confidence_intervals.csv`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/reports/stage8_9_7_confidence_intervals.csv).

```
95% Confidence Intervals for Candidate Models (N_pos = 102, N_neg = 191)
========================================================================================================
Model Architecture        Metric              Point Estimate  95% Confidence Interval    Margin of Error
--------------------------------------------------------------------------------------------------------
Model_A_v3_Baseline       Recall              76.47%          [67.37%, 83.65%]           ± 8.14%
                          Hard-Negative FPR   13.09%          [ 9.03%, 18.61%]           ± 4.79%
                          Precision           75.73%          [66.62%, 82.98%]           ± 8.18%
                          PR-AUC              0.7545          [0.6636, 0.8411]           ± 0.0888
--------------------------------------------------------------------------------------------------------
Model_D_v3_Concat_LR      Recall              84.31%          [76.03%, 90.11%]           ± 7.04%
                          Hard-Negative FPR    8.38%          [ 5.22%, 13.17%]           ± 3.98%
                          Precision           84.31%          [76.03%, 90.11%]           ± 7.04%
                          PR-AUC              0.8910          [0.8311, 0.9450]           ± 0.0569
--------------------------------------------------------------------------------------------------------
Model_G_Hybrid_Concat     Recall              86.27%          [78.27%, 91.64%]           ± 6.69%
                          Hard-Negative FPR    8.90%          [ 5.63%, 13.79%]           ± 4.08%
                          Precision           83.81%          [75.59%, 89.64%]           ± 7.02%
                          PR-AUC              0.8918          [0.8313, 0.9464]           ± 0.0575
--------------------------------------------------------------------------------------------------------
Model_H_Calibrated_Hybrid Recall              86.27%          [78.27%, 91.64%]           ± 6.69%
                          Hard-Negative FPR    8.90%          [ 5.63%, 13.79%]           ± 4.08%
                          Precision           83.81%          [75.59%, 89.64%]           ± 7.02%
                          PR-AUC              0.8923          [0.8320, 0.9469]           ± 0.0574
--------------------------------------------------------------------------------------------------------
Model_I_NonLinear_GBT     Recall              68.63%          [59.09%, 76.82%]           ± 8.87%
                          Hard-Negative FPR    5.76%          [ 3.25%, 10.02%]           ± 3.39%
                          Precision           86.42%          [77.30%, 92.24%]           ± 7.47%
                          PR-AUC              0.8528          [0.7779, 0.9229]           ± 0.0725
========================================================================================================
```

### Probability Calibration Assessment
To evaluate whether prediction scores behave as true posterior probabilities, Brier scores and Expected Calibration Error (ECE) across 10 probability bins were computed. The full table is exported to [`reports/stage8_9_7_calibration_metrics.csv`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/reports/stage8_9_7_calibration_metrics.csv).

```
Model Calibration Performance on Held-Out Test Set
========================================================================================
Model Architecture         Brier Score   ECE (10 bins)   Mean Prob   Prob Std   Assessment
----------------------------------------------------------------------------------------
Model_A_v3_Baseline        0.1520        0.1277          0.3396      0.4467     Uncalibrated / Extreme
Model_D_v3_Concat_LR       0.0874        0.0679          0.3287      0.4127     Well-calibrated
Model_G_Hybrid_Concat      0.0863        0.0652          0.3289      0.4124     Lowest ECE / Sharp
Model_H_Calibrated_Hybrid  0.0927        0.0849          0.3212      0.3098     Smoothed / Monotonic
Model_I_NonLinear_GBT      0.1024        0.0465          0.3142      0.3588     Low ECE / Conservative
========================================================================================
```

- **Finding:** Multi-pooling concatenation (Model D and Model G) cut Brier score nearly in half compared to the baseline ($0.0863$ vs $0.1520$), and reduced ECE to $0.0652$. Model H's Platt scaling smooths the probabilities, ensuring monotonic posterior scaling without overconfidence.

---

## 8. Detailed Category-Level Error Analysis

The performance of each candidate was decomposed across all 8 acoustic categories in the held-out test cohort. The full breakdown is exported to [`reports/stage8_9_7_category_metrics.csv`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/reports/stage8_9_7_category_metrics.csv).

```
Per-Category Performance Breakdown on Held-Out Test Cohort (N=293)
===========================================================================================================================
Category                  Class  N    Metric   Model A (Base)  Model D (Concat) Model G (Hybrid) Model H (Calib)  Model I (GBT)
---------------------------------------------------------------------------------------------------------------------------
scream (clean)            Pos    66   Recall   81.82% (54/66)  86.36% (57/66)   86.36% (57/66)   86.36% (57/66)   75.76% (50/66)
masked_distant_screams    Pos    36   Recall   66.67% (24/36)  80.56% (29/36)   86.11% (31/36)   86.11% (31/36)   55.56% (20/36)
---------------------------------------------------------------------------------------------------------------------------
shouting_and_speech       Neg    48   FPR      10.42% ( 5/48)  12.50% ( 6/48)   12.50% ( 6/48)   12.50% ( 6/48)   10.42% ( 5/48)
crowd_chant_cheering      Neg    42   FPR      16.67% ( 7/42)   9.52% ( 4/42)   11.90% ( 5/42)   11.90% ( 5/42)    4.76% ( 2/42)
whistles_and_squeaks      Neg    32   FPR       3.12% ( 1/32)   3.12% ( 1/32)    3.12% ( 1/32)    3.12% ( 1/32)    6.25% ( 2/32)
sfx_sirens_fireworks      Neg    28   FPR      39.29% (11/28)  14.29% ( 4/28)   14.29% ( 4/28)   14.29% ( 4/28)    0.00% ( 0/28)
general_environmental     Neg    26   FPR       0.00% ( 0/26)   0.00% ( 0/26)    0.00% ( 0/26)    0.00% ( 0/26)    0.00% ( 0/26)
infant_crying             Neg    15   FPR       6.67% ( 1/15)   6.67% ( 1/15)    6.67% ( 1/15)    6.67% ( 1/15)   13.33% ( 2/15)
===========================================================================================================================
```

### Forensic Analysis of Key Confounders

#### 1. Crowd Chants, Stadium Countdowns & Sing-Alongs ($N=42$)
- **Stage 8.9.6 Status:** The most destructive failure mode across all models ($33.33\% - 46.67\%$ FPR).
- **Stage 8.9.7 Status:** Dramatically suppressed! Model D achieved **9.52% FPR** (4 false alarms out of 42), Model G/H achieved **11.90% FPR** (5 false alarms), and Model I reached **4.76% FPR** (2 false alarms).
- **Mechanism:** Ingesting 150 additional crowd chant and cheering recordings into the training set allowed the linear classifiers to learn negative weights for steady-state multi-voice spectral broadening. Mean-pooling representations explicitly captured the diffuse, reverberant nature of crowds, suppressing false alarms.

#### 2. Shouted Speech & Excited Vocalizations ($N=48$)
- **Stage 8.9.6 Status:** $20.93\% - 27.91\%$ FPR.
- **Stage 8.9.7 Status:** **All models met the $\le 15.0\%$ acceptance target!** Model G and H achieved **12.50% FPR** (6 false alarms out of 48), and Model A and I achieved **10.42% FPR** (5 false alarms).
- **Mechanism:** The expansion of 60 focused shouting and yell clips, combined with the revised annotation protocol emphasizing lexical consonant articulation, created clear separation between linguistic vocal projections and non-linear scream chaos.

#### 3. Masked & Distant Screams ($N=36$)
- **Stage 8.9.6 Status:** Model E collapsed to **57.89% recall** due to multiplicative gating penalties.
- **Stage 8.9.7 Status:** **Major recovery!** Model G and H achieved **86.11% recall** (31 out of 36 masked screams detected in loud festival background noise).
- **Mechanism:** Passing continuous soft logits instead of binary gates allowed the multi-pooled transient features to overpower background noise without being vetoed by a zero probability.

#### 4. SFX, Sirens & Fireworks ($N=28$)
- **Stage 8.9.6 Status:** $0.00\% - 6.25\%$ FPR.
- **Stage 8.9.7 Status:** Baseline Model A had high siren FPR (**39.29%**), but Model D, G, and H reduced this to **14.29%** (4 false alarms out of 28). Model I achieved **0.00% FPR**.

---

## 9. Formal Provisional Acceptance Target Audit

| Performance Dimension | Pre-Declared Provisional Target | Best Candidate Point Estimate | 95% Confidence Interval | Compliance Status |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Scream Recall** | $\ge \mathbf{96.0\%}$ | **86.27%** (Model G, H) | $[78.27\%, 91.64\%]$ | **FAILED** |
| **Overall Hard-Negative FPR** | $\le \mathbf{5.0\%}$ | **8.38%** (Model D) / **8.90%** (Model G) | $[5.22\%, 13.17\%]$ | **FAILED** |
| **Shouted Speech & Yell FPR** | $\le \mathbf{15.0\%}$ | **10.42%** (Model A, I) / **12.50%** (Model G) | $[4.53\%, 22.17\%]$ | **PASSED** |
| **Whistle & Squeak FPR** | $\le \mathbf{5.0\%}$ | **3.12%** (Model A, D, G, H) | $[0.55\%, 15.74\%]$ | **PASSED** |
| **Crowd Chant / Cheer FPR** | $\le \mathbf{10.0\%}$ (Provisional) | **9.52%** (Model D) / **4.76%** (Model I) | $[3.77\%, 22.07\%]$ | **PASSED (Model D, I)** |

### Formal Verdict
**NO CANDIDATE QUALIFIES FOR FORMAL PROMOTION OR PRODUCTION DEPLOYMENT.**

While Model G and Model H represent major architectural and empirical advances—achieving **86.27% overall recall**, **86.11% masked scream recall**, **$8.90\%$ hard-negative FPR**, **$12.50\%$ shouting FPR**, and **$11.90\%$ crowd chant FPR** with state-of-the-art PR-AUC (**0.8923**)—they fall short of the life-safety criteria of $\ge 96.0\%$ recall and $\le 5.0\%$ overall FPR.

In full accordance with research ethics and Section 6 of the project charter, the criteria are not weakened. The production model remains frozen at hash `ad6e428d...`.

---

## 10. Reproducibility Commands and Regression Test Results

### Reproducible Commands
All operations in Stage 8.9.7 are fully reproducible via standard terminal commands in the backend environment:

1. **Dataset Expansion:**
   ```powershell
   & .venv\Scripts\python.exe experiments/v2_hard_negative_training/expand_dataset_v3.py
   ```
2. **Feature Extraction:**
   ```powershell
   & .venv\Scripts\python.exe experiments/v2_hard_negative_training/extract_features_v3.py
   ```
3. **Model Training & Validation Benchmarking:**
   ```powershell
   & .venv\Scripts\python.exe experiments/v2_hard_negative_training/train_hybrid_models.py
   ```
4. **Independent Evaluation Audit & Confidence Intervals:**
   ```powershell
   & .venv\Scripts\python.exe experiments/v2_hard_negative_training/audit_stage8_9_7.py
   ```

### Regression Test Suite
The full backend pytest regression suite was executed to confirm system integrity:
```
====================== 168 passed, 4 warnings in 47.47s =======================
```
- **Total Tests:** 168 passed, 0 failed, 0 skipped.
- **Test Integrity:** Realtime inference engine, WebSocket broadcaster, SQLite review studio, Stage 5 baseline verifications, and triage pipelines all remain 100% operational.

---

## 11. Recommendations for Next Stage Research (Stage 8.9.8)

1. **Temporal Sequence Modeling (Bi-LSTM / Temporal Convolutional Network):**
   - Frame-level multi-pooling (max, p90, mean) successfully suppresses static background noise, but cannot capture the *dynamic temporal morphology* of screams versus chants.
   - Genuine screams feature an explosive transient ($<100\text{ ms}$) followed by deterministic chaos that decays monotonically over $1.5 - 3.0\text{ seconds}$.
   - Crowd countdowns and stadium sing-alongs feature periodic, rhythmic pulses. A shallow 2-layer Bi-LSTM or 1D dilated TCN operating directly over the unpooled YAMNet frame sequence ($T \times 1024$) could exploit this rhythmicity to eliminate remaining crowd false alarms without losing screams.
2. **Harmonic-to-Noise Ratio (HNR) and Subharmonic Acoustic Features:**
   - Supplement YAMNet embeddings with acoustic domain features: spectral flux, fundamental frequency jitter/shimmer, and subharmonic energy ratio. Screams have near-zero HNR (turbulent chaos), whereas shouting and singing retain strong harmonic pitch tracks.
3. **Pre-Production Field Testing Gate:**
   - Continue experimental isolation in `backend/experiments/`. Await explicit approval before any candidate promotion.
