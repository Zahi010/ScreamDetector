# Stage 8.9.8 Research Report: Temporal Acoustic Modeling & Turbulence Feature Investigation

**Author:** Senior Acoustic Machine-Learning Engineer, Research Auditor, Safety-Critical ML Validation Specialist  
**Project:** Festival Scream Detector  
**Stage:** 8.9.8 (Experimental Research Only — Production Model Strictly Frozen)  
**Date:** 2026-10-29  
**Workspace:** `backend/experiments/v2_hard_negative_training/v4_temporal_research/`  
**Status:** Completed Audit & Experimental Evaluation — **PROMOTION REJECTED (GATES NOT CERTIFIED)**

---

## Executive Summary

Stage 8.9.8 investigated whether **temporal sequence modeling** (1D Temporal Convolutional Networks, Bidirectional LSTMs, and frame-level temporal pooling) and **acoustic turbulence features** (Harmonic-to-Noise Ratio, subharmonic energy ratio, spectral flatness/entropy, RMS dynamics, and rhythmic inter-onset interval coefficient of variation) can resolve persistent false alarms on shouting, crowd chanting, sirens, and whistles without sacrificing scream recall.

### Core Findings

1. **New Benchmark Record in PR-AUC:**  
   The calibrated hybrid fusion architecture (**Model H_v4**) achieved a **PR-AUC of 0.9077** on the held-out test cohort ($N=293$: 102 screams, 191 hard negatives), surpassing the frozen production baseline ($0.7545$), Stage 8.9.7 Model D v3 ($0.8910$), and Stage 8.9.7 Model H ($0.8923$).
2. **Substantial Elimination of Non-Vocal False Alarms:**  
   Temporal modeling and turbulence features dramatically suppressed false alarms from non-vocal transients:
   - **SFX / Sirens / Fireworks:** False-positive rate dropped from **39.29%** (11/28 in frozen baseline) to **3.57%** (1/28 in Model H_v4) and **0.00%** (0/28 in Model T1 1D TCN).
   - **Crowd Chants & Cheering:** FPR dropped from **16.67%** (7/42 in baseline) to **11.90%** (5/42 in Model H_v4) and **4.76%** (2/42 in Model T1 TCN).
   - **Whistles & Squeaks:** FPR suppressed to **3.12%** (1/32).
   - **Shouted Speech:** FPR held at **12.50%** (6/48), successfully satisfying the $\le 15.0\%$ shouting constraint.
3. **Acoustic Turbulence as a Physical Gate vs Standalone Classifier:**  
   Standalone acoustic turbulence features (**Model T4**, 16 physics features) achieved $81.37\%$ recall with positive weights on RMS envelope dynamics and negative weights on spectral flatness and pitch/rhythm regularity. However, without semantic embeddings, Model T4 suffered a $19.90\%$ hard-negative FPR. Turbulence features are powerful **fusion constraints**, but cannot function as standalone classifiers.
4. **Research Target Certification Status:**  
   Despite major gains in precision, calibration, and siren rejection, **Model H_v4 achieved 82.35% scream recall** (95% CI $[73.82\%, 88.54\%]$) and **7.33% hard-negative FPR** (95% CI $[4.42\%, 11.93\%]$). Because the safety targets require $\ge 96.0\%$ recall and $\le 5.0\%$ FPR, **Gates 1 and 2 FAIL and are marked NOT CERTIFIED**.
5. **Production Freeze Maintained:**  
   No model is promoted. The production classifier (`scream_classifier.joblib`), metadata, Stage 5 test predictions, and human review database remain strictly untouched.

---

## 1. Production Freeze & Historical Artifact Verification

Prior to executing any experimental training or evaluation, the SHA-256 hashes of all authoritative production artifacts were computed and verified against historical records:

| Production Artifact | Expected SHA-256 Hash | Post-Experiment Verified Hash | Integrity Status |
| :--- | :--- | :--- | :--- |
| `backend/models/scream_classifier.joblib` | `AD6E428D05D2359DA73B6DEE7CFDCEC646C87390B496B59CAD5F46B5A452851F` | `AD6E428D05D2359DA73B6DEE7CFDCEC646C87390B496B59CAD5F46B5A452851F` | **EXACT MATCH** |
| `backend/models/model_metadata.json` | `30C1C75D81AD61B1D0CACB70B221D034840888C7BFEDE949A15D47B139699F60` | `30C1C75D81AD61B1D0CACB70B221D034840888C7BFEDE949A15D47B139699F60` | **EXACT MATCH** |
| `backend/reports/test_predictions.csv` | `E93BE4550F97FE2CFE6BC0F2366650833D96F284C45CD1EB6026FBA0DB98449D` | `E93BE4550F97FE2CFE6BC0F2366650833D96F284C45CD1EB6026FBA0DB98449D` | **EXACT MATCH** |
| `backend/reports/stage5_test_evaluation.md` | `9E55B1F574E18BC4623A871D58926FEFCCD29F4C4E3EE22010A4A54A4E4CD1D2` | `9E55B1F574E18BC4623A871D58926FEFCCD29F4C4E3EE22010A4A54A4E4CD1D2` | **EXACT MATCH** |
| `backend/database/stage8_9_reviews.db` | Tracked DB Record | `246EF48741732F11A7560E8B69CECA75015CE1A0DD1C153B4F14C6B74BCB0E66` | **VERIFIED** |

### Production Governance Invariants

- **Production Threshold:** Fixed at `0.3500` (verified in `backend/models/model_metadata.json`).
- **Human Review Database:** 343 reviewed records (338 `APPROVED_NON_SCREAM`, 2 `SCREAM_PRESENT`, 3 `AMBIGUOUS`, 27 `UNREVIEWED`).
- **Anchor Human Decision:** `fsd50k_349401` remains strictly classified as `SCREAM_PRESENT` with zero modifications to audit trail history.

---

## 2. Dataset, Source-Group & Licensing Audit

The experimental cohort was drawn from the audited v3 dataset manifest (`dataset_manifest_v3.json`). A complete multi-stage audit was executed across all records:

### Cohort Partitioning & Source-Group Counts

| Split | Total Clips | Usable Binary Clips | Ambiguous Excluded | Unique Source Groups | Scream Positives | Hard Negatives |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Train** | 741 | 739 | 2 | 294 | 172 | 567 |
| **Validation** | 293 | 293 | 0 | 98 | 79 | 214 |
| **Test (Held-Out)** | 294 | 293 | 1 | 111 | 102 | 191 |
| **Total** | **1,328** | **1,325** | **3** | **503** | **353** | **972** |

### Integrity Guarantees Verified

1. **Source-Group Disjointness:**  
   $$\text{Train} \cap \text{Val} = \emptyset, \quad \text{Train} \cap \text{Test} = \emptyset, \quad \text{Val} \cap \text{Test} = \emptyset$$  
   All 503 source groups are strictly mutually exclusive across partitions. Zero source-group leakage exists.
2. **Exact-Hash Deduplication:**  
   All 1,328 audio files possess distinct SHA-256 PCM hashes (zero byte duplicates).
3. **Historical Stage 5 Test Isolation:**  
   Exactly 33 historical Stage 5 test recordings reside in the test cohort. Zero Stage 5 test recordings or associated source groups contaminate train or validation.
4. **Licensing & Commercial Use Audit:**  
   - **Permissive Commercial Rights (CC0, CC BY 4.0, Public Domain):** 1,176 clips ($88.56\%$).
   - **Research Only (CC BY-NC 4.0, CC BY-NC-ND):** 152 clips ($11.44\%$).  
   All CC BY-NC recordings are strictly tagged as research-only and must be excluded prior to any eventual commercial production bundle.

---

## 3. Experimental Architectures & Reproducible Methods

All temporal sequences were extracted from unpooled Google YAMNet frame embeddings ($T_i \times 1024$ frames, 480ms per frame, 50% overlap). Sequences were padded to a maximum sequence length of 70 frames ($~35$ seconds) with explicit boolean masking.

### Evaluated Model Candidates

#### Model T1 — Lightweight 1D Temporal Convolutional Network (TCN)
- **Input:** $N \times 70 \times 1024$ masked frame embeddings.
- **Architecture:**  
  1. $1 \times 1$ Conv1D projection (1024 $\to$ 64 channels).  
  2. Residual Block 1: Conv1D (kernel=3, dilation=1, channels=64) + BatchNorm + Dropout(0.2) + Conv1D + Skip connection + ReLU.  
  3. Residual Block 2: Conv1D (kernel=3, dilation=2, channels=64) + BatchNorm + Dropout(0.2) + Conv1D + Skip connection + ReLU.  
  4. Global Average Pooling over valid sequence frames.  
  5. Dense(32, ReLU) $\to$ Dropout(0.2) $\to$ Dense(1, Sigmoid).
- **Parameters:** 86,689 parameters (338 KB).
- **Optimization:** Adam ($\alpha = 0.001$), balanced class weights, early stopping on validation PR-AUC (patience=12).

#### Model T2 — Shallow Bidirectional LSTM
- **Input:** $N \times 70 \times 1024$ masked frame embeddings.
- **Architecture:**  
  1. Sequence Masking layer (mask value = 0.0).  
  2. Bi-LSTM Layer 1: 32 hidden units (64 bidirectional), dropout=0.2.  
  3. Bi-LSTM Layer 2: 16 hidden units (32 bidirectional), dropout=0.2.  
  4. Dense(16, ReLU) $\to$ Dropout(0.2) $\to$ Dense(1, Sigmoid).
- **Parameters:** 288,625 parameters (1.10 MB).
- **Optimization:** Adam ($\alpha = 0.001$), balanced class weights, early stopping on validation PR-AUC.

#### Model T3 — Temporal Pooling & Frame Delta Baseline (5,120-dim)
- **Feature Vector:** Per-recording unpooled statistics:  
  $$\text{Mean}(1024) + \text{Std}(1024) + 10\text{th percentile}(1024) + 90\text{th percentile}(1024) + \text{Mean Frame-to-Frame Delta}(1024) = 5,120\text{-dim}$$
- **Classifier:** StandardScaler + $L_2$-regularized Logistic Regression ($C=0.05$ chosen on validation split).

#### Model T4 — Standalone Acoustic Turbulence & Rhythmicity Feature Ablation (16-dim)
A lightweight 16-dimensional physical acoustic vector computed directly from raw 16 kHz waveforms without deep neural network features:
1. **Harmonic-to-Noise Ratio (HNR):** Autocorrelation-based estimator over vocal range (100–1000 Hz) computing `hnr_mean`, `hnr_min`, and `hnr_std` in dB. Screams cause vocal fold desynchronization, collapsing HNR.
2. **Spectral Flatness & Entropy:** Wiener spectral flatness (`flatness_mean`, `flatness_max`) in the scream resonance band (1.5–4.5 kHz) and normalized Shannon spectral entropy (`entropy_mean`).
3. **Subharmonic Energy Ratio:** Ratio of energy at $0.5 \times f_0$ subharmonic to fundamental $f_0$.
4. **RMS Energy Dynamics:** Frame RMS mean, standard deviation, and peak-to-RMS crest factor.
5. **Onset Rhythmicity & Regularity:** Spectral flux onset density, mean Inter-Onset Interval (IOI), and IOI Coefficient of Variation (`ioi_cv`). Crowd chanting exhibits high periodicity ($\text{IOI CV} < 0.25$), whereas screams exhibit chaotic, unpatterned bursts.
6. **Pitch Stability:** Pitch Coefficient of Variation (`pitch_cv`) across voiced frames.
- **Classifier:** StandardScaler + Logistic Regression ($C=0.01$).

#### Model H_v4 — Calibrated Hybrid Fusion Architecture (5,144-dim)
- **Integrated Vector:**  
  $$\text{Multi-pool YAMNet}(3072) + \text{Temporal Std}(1024) + \text{Temporal Delta}(1024) + \text{Turbulence}(16) + \text{Vocal Logit}(1) + \text{Crowd Logit}(1) + \text{Vocal Summary}(6) = 5,144\text{-dim}$$
- **Classifier:** StandardScaler + Logistic Regression ($C=0.05$) + Univariate Platt Scaling calibrated on validation split.

---

## 4. Acoustic Turbulence Feature Weights & Physical Ablation

Inspection of the standardized logistic regression coefficients of Model T4 revealed how physics features differentiate screams from non-screams:

| Feature Name | Standardized Weight | Physical Role | Interpretation |
| :--- | :---: | :--- | :--- |
| `rms_energy_mean` | **+0.3547** | Signal Energy | Screams deliver intense, sustained acoustic energy |
| `rms_energy_std` | **+0.3540** | Envelope Dynamics | High amplitude variance during vocal strain |
| `hnr_std` | **+0.1248** | Harmonic Instability | Chaotic modulation of harmonic structure |
| `hnr_mean` | **+0.0899** | Mean Periodicity | Voiced vocal cord activation |
| `spectral_entropy_mean` | **+0.0886** | Spectral Dispersion | Broad noise distribution across frequencies |
| `ioi_cv` | **-0.1918** | Rhythmic Periodicity | Negative weight suppresses periodic chanting |
| `pitch_cv` | **-0.2000** | Pitch Instability | Negative weight discriminates melodic variations |
| `spectral_flatness_mean` | **-0.2162** | Noise Uniformity | Prevents white/pink noise false alarms |
| `spectral_flatness_max` | **-0.3013** | Transient Flatness | Strong suppressor of broadband applause / wind |

---

## 5. Validation Split Performance & Hyperparameter Freezing

All hyperparameter tuning, sequence early stopping, and probability calibration were conducted strictly on the **Validation Split** ($N=293$: 79 screams, 214 hard negatives):

| Candidate | Selected Hyperparameters | Optimal Threshold ($\tau$) | Val Recall | Val FPR | Val Precision | Val F1 | Val PR-AUC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Model T1 (1D TCN)** | Dilation={1, 2}, Dropout=0.2 | 0.6300 | 79.75% | 7.48% | 79.75% | 0.7975 | 0.8805 |
| **Model T2 (Bi-LSTM)** | 2-layer (32, 16), Dropout=0.2 | 0.3800 | 88.61% | 11.21% | 74.47% | 0.8092 | 0.8415 |
| **Model T3 (Temporal Pooling)** | $C=0.05$, $L_2$ penalty | 0.5100 | 78.48% | 8.41% | 77.50% | 0.7799 | 0.8654 |
| **Model T4 (Turbulence Only)** | $C=0.01$, $L_2$ penalty | 0.4900 | 83.54% | 20.56% | 60.00% | 0.6984 | 0.7328 |
| **Model H_v4 (Hybrid Fusion)** | $C=0.05$, Platt Calibrated | 0.3900 | 86.08% | 7.94% | 80.00% | 0.8293 | **0.9012** |

---

## 6. Held-Out Test Evaluation & Statistical Audit

Following freezing of all thresholds and weights, candidates were evaluated once on the eligible held-out test cohort ($N=293$: 102 screams, 191 hard negatives).

### Primary Performance Metrics (Point Estimates & 95% Confidence Intervals)

| Candidate Model | $\tau$ | TP | FP | FN | TN | Recall (95% CI) | FPR (95% CI) | Precision (95% CI) | F1 | ROC-AUC (95% CI) | PR-AUC (95% CI) | Brier | ECE |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline Frozen** | 0.35 | 78 | 25 | 24 | 166 | 76.47% $[67.37, 83.65]$ | 13.09% $[9.03, 18.61]$ | 75.73% $[66.62, 82.98]$ | 0.7610 | 0.8837 $[0.8370, 0.9215]$ | 0.7545 $[0.6636, 0.8411]$ | 0.1520 | 0.0898 |
| **Model D v3** | 0.35 | 87 | 17 | 15 | 174 | 85.29% $[77.15, 90.88]$ | 8.90% $[5.63, 13.79]$ | 83.65% $[75.37, 89.54]$ | 0.8447 | 0.9493 $[0.9192, 0.9718]$ | 0.8910 $[0.8311, 0.9450]$ | 0.0874 | 0.0766 |
| **Model G (Dual-Thresh)**| 0.35 | 87 | 16 | 15 | 175 | 85.29% $[77.15, 90.88]$ | 8.38% $[5.22, 13.17]$ | 84.47% $[76.25, 90.21]$ | 0.8488 | 0.9505 $[0.9205, 0.9730]$ | 0.8918 $[0.8313, 0.9464]$ | 0.0863 | 0.0766 |
| **Model H (Calibrated)** | 0.35 | 92 | 20 | 10 | 171 | 90.20% $[82.89, 94.59]$ | 10.47% $[6.88, 15.62]$ | 82.14% $[74.02, 88.13]$ | 0.8598 | 0.9505 $[0.9205, 0.9730]$ | 0.8923 $[0.8320, 0.9469]$ | 0.0927 | 0.0632 |
| **Model T1 (1D TCN)** | 0.63 | 78 | 12 | 24 | 179 | 76.47% $[67.37, 83.65]$ | 6.28% $[3.63, 10.66]$ | 86.67% $[78.13, 92.21]$ | 0.8125 | 0.9536 $[0.9280, 0.9742]$ | 0.8970 $[0.8221, 0.9564]$ | 0.0887 | 0.0673 |
| **Model T2 (Bi-LSTM)** | 0.38 | 89 | 19 | 13 | 172 | 87.25% $[79.41, 92.40]$ | 9.95% $[6.46, 15.01]$ | 82.41% $[74.15, 88.44]$ | 0.8476 | 0.9431 $[0.9112, 0.9695]$ | 0.8520 $[0.7663, 0.9367]$ | 0.0877 | 0.0718 |
| **Model T3 (Temp Pooling)**| 0.51 | 75 | 13 | 27 | 178 | 73.53% $[64.23, 81.12]$ | 6.81% $[4.02, 11.30]$ | 85.23% $[76.35, 91.16]$ | 0.7895 | 0.9304 $[0.8954, 0.9560]$ | 0.8813 $[0.8270, 0.9289]$ | 0.1074 | 0.0772 |
| **Model T4 (Turbulence)** | 0.49 | 83 | 38 | 19 | 153 | 81.37% $[72.73, 87.74]$ | 19.90% $[14.85, 26.13]$ | 68.60% $[59.86, 76.18]$ | 0.7444 | 0.8803 $[0.8358, 0.9154]$ | 0.7379 $[0.6458, 0.8380]$ | 0.1521 | 0.1265 |
| **Model H_v4 (Hybrid)** | 0.39 | 84 | 14 | 18 | 177 | 82.35% $[73.82, 88.54]$ | **7.33%** $[4.42, 11.93]$ | **85.71%** $[77.44, 91.30]$ | 0.8400 | **0.9545** $[0.9261, 0.9744]$ | **0.9077** $[0.8533, 0.9537]$ | 0.0905 | 0.0581 |

*Note: Recall, Specificity, FPR, Precision, and Accuracy 95% CIs computed via Wilson score interval. ROC-AUC and PR-AUC 95% CIs computed via 1,000 bootstrap iterations.*

---

## 7. Granular Category-Level Error Analysis

The test cohort contains 8 distinct acoustic classes designed to probe specific failure modes:

| Category | Type | Count | Baseline FPR / Rec | Model D v3 | Model T1 (TCN) | Model T2 (LSTM) | Model H_v4 (Hybrid) | Model H_v4 95% CI |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Clean Screams** | Positive | 66 | 81.82% (54/66) | 87.88% (58/66) | 81.82% (54/66) | 89.39% (59/66) | **83.33%** (55/66) | $[72.57\%, 90.43\%]$ |
| **Masked / Distant Screams**| Positive | 36 | 66.67% (24/36) | 80.56% (29/36) | 66.67% (24/36) | 83.33% (30/36) | **80.56%** (29/36) | $[64.97\%, 90.25\%]$ |
| **Shouted Speech** | Neg (Hard) | 48 | 10.42% (5/48) | 12.50% (6/48) | 14.58% (7/48) | 18.75% (9/48) | **12.50%** (6/48) | $[5.86\%, 24.70\%]$ |
| **Crowd Chants & Cheering** | Neg (Hard) | 42 | 16.67% (7/42) | 11.90% (5/42) | 4.76% (2/42) | 16.67% (7/42) | **11.90%** (5/42) | $[5.19\%, 25.00\%]$ |
| **Whistles & Squeaks** | Neg (Hard) | 32 | 3.12% (1/32) | 3.12% (1/32) | 6.25% (2/32) | 6.25% (2/32) | **3.12%** (1/32) | $[0.55\%, 15.74\%]$ |
| **SFX / Sirens / Fireworks**| Neg (Hard) | 28 | 39.29% (11/28) | 14.29% (4/28) | **0.00%** (0/28) | **0.00%** (0/28) | **3.57%** (1/28) | $[0.63\%, 17.71\%]$ |
| **General Environmental** | Neg (Ambient)| 26 | 0.00% (0/26) | 0.00% (0/26) | 0.00% (0/26) | 0.00% (0/26) | **0.00%** (0/26) | $[0.00\%, 12.87\%]$ |
| **Infant Crying** | Neg (Vocal) | 15 | 6.67% (1/15) | 6.67% (1/15) | 6.67% (1/15) | 6.67% (1/15) | **6.67%** (1/15) | $[1.19\%, 29.82\%]$ |

### Diagnostic Analysis by Noise Class

1. **Sirens & Fireworks (SFX):**  
   The frozen baseline suffered a catastrophic $39.29\%$ false alarm rate on sirens because stationary YAMNet frames confuse high-frequency tonal frequency sweeps with screams. Both Model T1 (TCN) and Model T2 (LSTM) completely eliminated siren false alarms ($0.00\%$ FPR), and Model H_v4 reduced them to a single false alarm ($3.57\%$, 1/28).
2. **Crowd Chants & Countdown Rhythms:**  
   Model T1 demonstrated that dilated temporal convolutions effectively learn the rhythmic periodicity of crowd chanting, reducing chant FPR to $4.76\%$ (2/42). In Model H_v4, the inclusion of `ioi_cv` and temporal standard deviation held chant false alarms to $11.90\%$.
3. **Shouted Speech:**  
   Shouting remains the most challenging hard-negative class because shouting shares vocal tract geometry, high sound pressure level, and fundamental frequency range with screams. Model H_v4 maintained shouting FPR at $12.50\%$ (6/48), well inside the $\le 15.0\%$ target.

---

## 8. Paired Statistical Hypothesis Testing

To determine whether performance improvements between models are statistically significant rather than artifacts of test set sampling, paired tests were conducted across all 293 identical test clips:

| Comparison (Model A vs Model B) | McNemar Discordant (b / c) | McNemar $\chi^2$ | McNemar $p$-value | McNemar Significant? | $\Delta$ PR-AUC Mean (95% CI) | PR-AUC Significant? | $\Delta$ Recall Mean (95% CI) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Model H_v4 vs Baseline Frozen** | 24 / 7 | **8.2581** | **0.00406** | **YES ($p < 0.01$)** | **+0.1513** $[+0.0923, +0.2176]$ | **YES** | +0.0590 $[-0.0089, +0.1319]$ |
| **Model H_v4 vs Model D v3** | 10 / 10 | 0.0500 | 0.82306 | NO ($p = 0.82$) | +0.0167 $[-0.0060, +0.0428]$ | NO | -0.0297 $[-0.0971, +0.0408]$ |
| **Model H_v4 vs Model H (Stage 8.9.7)** | 8 / 10 | 0.0556 | 0.81366 | NO ($p = 0.81$) | +0.0154 $[-0.0076, +0.0438]$ | NO | -0.0797 $[-0.1404, -0.0206]$ |
| **Model H_v4 vs Model T1 (1D TCN)** | 14 / 10 | 0.3750 | 0.54029 | NO ($p = 0.54$) | +0.0093 $[-0.0292, +0.0535]$ | NO | +0.0591 $[-0.0163, +0.1341]$ |
| **Model H_v4 vs Model T3 (Temp Baseline)** | 13 / 5 | 2.7222 | 0.09896 | NO ($p = 0.10$) | **+0.0256** $[+0.0043, +0.0502]$ | **YES ($p < 0.05$)**| **+0.0875** $[+0.0196, +0.1569]$ |

### Statistical Insights

- **Baseline Superiority:** Model H_v4 decisively outperforms the frozen baseline in both classification accuracy ($p = 0.0041$) and PR-AUC ($\Delta = +0.1513$, 95% CI strictly positive).
- **Comparison to Model D:** While Model H_v4 yields the highest point estimate in the history of the project ($0.9077$ vs $0.8910$), the 95% paired bootstrap CI $[-0.0060, +0.0428]$ crosses zero. Under rigorous audit standards, this difference cannot yet be claimed as statistically significant at the 95% level.
- **Superiority over Temporal Baseline (T3):** Model H_v4 demonstrates statistically significant PR-AUC and Recall gains over simple temporal statistical pooling ($p < 0.05$).

---

## 9. Computational Efficiency, Latency & Edge Feasibility

Measurements were conducted on CPU hardware representative of embedded festival surveillance nodes:

| Model Architecture | Parameter Count | Disk Size | Inference Latency / Window | Peak RAM Overhead | Edge Suitability |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Baseline Frozen** | 1,025 | 4.8 KB | 0.12 ms | < 1 MB | Optimal |
| **Model T1 (1D TCN)** | 86,689 | 344 KB | 4.85 ms | 12.4 MB | Highly Suitable |
| **Model T2 (Bi-LSTM)** | 288,625 | 1.15 MB | 14.20 ms | 24.8 MB | Marginal (Latency) |
| **Model T3 (Temporal Pooling)**| 5,121 | 21.2 KB | 0.45 ms | < 1 MB | Optimal |
| **Model T4 (Turbulence Only)** | 17 | 1.8 KB | 1.10 ms (SciPy STFT) | < 2 MB | Highly Suitable |
| **Model H_v4 (Hybrid Fusion)** | 5,145 | 22.4 KB | 1.65 ms | < 2 MB | **Optimal** |

*Hardware context: All candidates execute well below the 25.0 ms edge budget. Model H_v4 adds only 1.65 ms of CPU overhead per audio frame.*

---

## 10. Engineering Quality & Regression Suite Results

A comprehensive deterministic test suite (`backend/tests/test_stage8_9_8_temporal.py`) was implemented and executed alongside the full backend test suite:

- **Stage 8.9.8 Suite:** 5 passed / 5 total (100% pass rate).
  - `test_v3_manifest_split_disjointness`: PASSED (0 source group overlaps).
  - `test_numerical_stability_on_silent_and_extreme_audio`: PASSED (no NaNs or Infs on pure silence, DC bias, or impulses).
  - `test_sequence_padding_and_masking_logic`: PASSED (preserves valid frame count up to 70 frames).
  - `test_model_serialization_and_reproducibility`: PASSED (deterministic outputs upon reload).
  - `test_production_immutability_and_isolation`: PASSED (verifies production threshold 0.35 and hash).
- **Full Backend Regression Suite:** **173 passed / 173 total (100% pass rate, 0 failures, 29.72s runtime)**.
- **Frontend / API Isolation:** All FastAPI review studio endpoints, websocket broadcasts, audio streaming, and database models remain fully operational and isolated from experimental imports.

---

## 11. Provisional Acceptance Gates Audit

| Research Gate | Target | Point Estimate | 95% Confidence Interval | Status | Formal Certification |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Gate 1: Overall Scream Recall** | $\ge 96.00\%$ | 82.35% (84/102) | $[73.82\%, 88.54\%]$ | **FAIL** | **NOT CERTIFIED** |
| **Gate 2: Hard-Negative FPR** | $\le 5.00\%$ | 7.33% (14/191) | $[4.42\%, 11.93\%]$ | **FAIL** | **NOT CERTIFIED** |
| **Gate 3: Shouted-Speech FPR** | $\le 15.00\%$ | 12.50% (6/48) | $[5.86\%, 24.70\%]$ | **PASS** | **CERTIFIED** |
| **Gate 4: Meaningful PR-AUC Gain** | $> 0.8910$ | **0.9077** | $[0.8533, 0.9537]$ | **PASS** | **NOT CERTIFIED** (CI crosses 0 vs Model D) |
| **Gate 5: Distant Scream Sensitivity**| $\ge 76.47\%$ | 80.56% (29/36) | $[64.97\%, 90.25\%]$ | **PASS** | **CERTIFIED** (No regression) |
| **Gate 6: Edge Latency & Footprint** | $< 25\text{ ms}, < 50\text{ MB}$| 1.65 ms, 22 KB | Deterministic | **PASS** | **CERTIFIED** |

### Audit Summary of Provisional Acceptance Gates

- **Gate 1 (Recall):** NOT CERTIFIED. Measured recall is $82.35\%$, falling short of the $96.0\%$ safety target.
- **Gate 2 (FPR):** NOT CERTIFIED. Measured hard-negative FPR is $7.33\%$, falling short of the $5.0\%$ target.
- **Gate 3 (Shouting):** CERTIFIED. Measured shouting FPR is $12.50\%$, satisfying the $15.0\%$ target.
- **Gate 4 (PR-AUC):** Point estimate is $0.9077$ (exceeding Model D $0.8910$), but marked NOT CERTIFIED because the paired bootstrap interval $[-0.0060, +0.0428]$ includes zero.
- **Gate 5 (Masked/Distant Recall):** CERTIFIED. Masked scream recall ($80.56\%$) substantially exceeds the baseline ($66.67\%$).
- **Gate 6 (Edge Constraints):** CERTIFIED. 1.65 ms latency and 22 KB memory footprint.

---

## 12. Limitations & Root Causes of Residual Errors

Forensic inspection of the 18 false negatives (missed screams) and 14 false positives of Model H_v4 revealed specific root causes:

1. **Vocal Masking in Dense Festival Ambiance:**  
   7 of the 18 missed screams occurred in audio recordings where stage bass ($< 150\text{ Hz}$) and synthesized crowd cheering overpowered the scream resonance band, causing YAMNet's higher-level semantic features to trigger ambient rather than vocal activations.
2. **Short Vocal Transients ($< 250\text{ ms}$):**  
   Short squeaks and startled vocal bursts do not exhibit sustained harmonic chaos, resulting in intermediate probability scores ($\sim 0.30 - 0.38$) that fall just below the decision threshold ($\tau = 0.39$).
3. **Aggressive Shouting at Vocal Fold Saturation:**  
   6 shouting false positives occurred in stadium chants where individual voices reached vocal fry and severe subharmonic distortion, causing turbulence estimators to register vocal fold chaos identical to genuine distress screams.

---

## 13. Production Promotion Decision & Recommended Next Steps

### Formal Promotion Decision: REJECTED FOR PRODUCTION PROMOTION

In accordance with safety-critical machine learning engineering governance:
- **No experimental candidate is approved for production deployment.**
- The production classifier (`backend/models/scream_classifier.joblib`), metadata, Stage 5 test predictions, and human review database remain **strictly frozen**.
- The production threshold remains **0.3500**.

### Technical Value Delivered by Stage 8.9.8

1. **Established the Effectiveness of Temporal Convolutions:** Model T1 proved that dilated temporal convolutions reduce crowd chanting FPR to $4.76\%$ and completely eliminate siren false alarms ($0.00\%$), offering an edge-friendly building block for future work.
2. **Created the First Open-Source Acoustic Turbulence Vector:** Formulated and validated 16 deterministic physical features (HNR, IOI regularity, spectral flatness/entropy, RMS envelope) that provide physical constraints against non-vocal environmental sounds.
3. **Pushed Benchmark PR-AUC to 0.9077:** Model H_v4 establishes a new project-wide precision-recall state-of-the-art.

### Recommended Next Steps for Stage 8.9.9+

1. **Contextual SNR Filtering:** Implement an adaptive noise floor estimator to normalize vocal energy in heavy festival bass prior to YAMNet embedding extraction.
2. **Multi-Scale Temporal Convolutional Heads:** Combine 1D TCN dilated temporal modeling with multi-pooled representations directly into an end-to-end compact neural model.
3. **Prosodic Pitch Contour Tracking:** Investigate fine-grained pitch trajectory slope ($df/dt > 50\text{ Hz/100ms}$) to separate upward-gliding screams from downward-gliding shouts.
