# Stage 8.9.11 — Commercially Eligible Data Acquisition and Preregistered Model Evaluation Report

**Operating Mode:** Controlled Experimental Development Only. Production remains strictly frozen.  
**Auditor Roles:** Senior Acoustic ML Engineer, Independent Safety-Critical Evaluation Auditor.  
**Date of Audit:** October 29, 2026  
**Status:** COMPLETE — RIGOROUS AUDIT CONCLUDED (PRODUCTION UNMODIFIED)

---

## 1. Executive Summary & Final Verdict

Stage 8.9.11 executed the preregistered research protocol established in Stage 8.9.10 on a completely clean, commercially eligible dataset expanded with verified permissive audio assets. All four preregistered candidate models were implemented, tuned strictly on validation data, and evaluated exactly once on the held-out test split.

### Critical Research & Audit Findings

1. **Validation Feasibility Constraint Violation:**
   Under the preregistered protocol, candidate models were required to find an operational threshold $\tau^*$ on validation data satisfying **BOTH**:
   $$\text{Recall}_{\text{scream}} \ge 96.0\% \quad \text{AND} \quad \text{FPR}_{\text{hard\_negative}} \le 5.0\%$$
   **None of the four candidate models (`D_v4`, `T1_v4`, `H_v4_Commercial`, `H_v5_SNR`) achieved both constraints simultaneously on validation data.** Consequently, following the preregistered protocol without deviation:
   $$\textbf{ALL CANDIDATE MODELS ARE CLASSIFIED AS INFEASIBLE AND CANNOT BE PROMOTED.}$$
   Operating thresholds were frozen at their best-achievable research trade-offs prior to single-shot test evaluation.

2. **Held-Out Test Set Performance (Single-Shot Evaluation):**
   - **Candidate D_v4 (Baseline Linear Fusion, $\tau^* = 0.3800$):**
     - Recall: **89.91%** (95% CI: [83.6%, 95.7%]) — **Gate 1 FAILED** (Target $\ge 96.0\%$)
     - Hard-Negative FPR: **7.07%** (95% CI: [3.1%, 11.8%]) — **Gate 2 FAILED** (Target $\le 5.0\%$)
     - Shouted-Speech FPR: **11.90%** — **Gate 3 PASSED** (Target $\le 15.0\%$)
     - PR-AUC: **0.9198** (95% CI: [0.8530, 0.9714])
   - **Candidate T1_v4 (Dilated 1D TCN, $\tau^* = 0.5300$):**
     - Recall: **85.32%** (95% CI: [75.8%, 93.9%]) — **Gate 1 FAILED**
     - Hard-Negative FPR: **8.08%** (95% CI: [4.4%, 12.8%]) — **Gate 2 FAILED**
     - Shouted-Speech FPR: **11.90%** — **Gate 3 PASSED**
     - PR-AUC: **0.8855** (95% CI: [0.7889, 0.9657])
   - **Candidate H_v4_Commercial (Hybrid Acoustic Fusion, $\tau^* = 0.4200$):**
     - Recall: **78.90%** (95% CI: [69.0%, 88.0%]) — **Gate 1 FAILED**
     - Hard-Negative FPR: **7.07%** (95% CI: [3.4%, 11.3%]) — **Gate 2 FAILED**
     - Shouted-Speech FPR: **9.52%** — **Gate 3 PASSED** (20% relative reduction in shouting false alarms)
     - PR-AUC: **0.8949** (95% CI: [0.7993, 0.9537])
   - **Candidate H_v5_SNR (Context-Aware Hybrid with Dynamic SNR, $\tau^* = 0.5100$):**
     - Recall: **77.98%** (95% CI: [67.4%, 87.3%]) — **Gate 1 FAILED**
     - Hard-Negative FPR: **5.05%** (95% CI: [1.9%, 8.8%]) — **Gate 2 BORDERLINE / UNCERTAIN**
     - Shouted-Speech FPR: **9.52%** — **Gate 3 PASSED**
     - PR-AUC: **0.9273** (95% CI: [0.8650, 0.9720]) — **Highest PR-AUC overall**

3. **Runtime & Latency Feasibility:**
   - **Classifier-Only Latency:** **3.330 ms** median (p95: 3.729 ms) — Well within edge budget.
   - **Full End-to-End Pipeline Latency:** **60.076 ms** median (p95: 68.961 ms) — **Exceeds the 25.0 ms instantaneous edge budget** due to unoptimized SciPy STFT and Welch periodogram feature calculation (Stage 4 = 39.31 ms). In a 500 ms rolling window, it consumes 12.0% of the hop period.
   - Serialized model artifact size on disk is **142.41 KB**.

4. **Production Protection Confirmation:**
   - Production model, metadata, test predictions, report, and review database remain **100% bit-identical and strictly frozen**.
   - Operating threshold remains fixed at **`0.3500`**.
   - All 173 backend regression tests passed with zero regressions.

**Final Certification Decision:** **NOT CERTIFIED. Production remains frozen. No model promotion is permitted.**

---

## 2. Mandatory Readiness Gate Audit

Before initiating data ingestion or model training, the Stage 8.9.11 readiness gate was independently executed via [`verify_readiness_gate.py`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_11_evaluation/verify_readiness_gate.py).

### 2.1 Production Immutability Verification

| Artifact Path | Authoritative SHA-256 | Verified SHA-256 | Status |
| :--- | :--- | :--- | :--- |
| `backend/models/scream_classifier.joblib` | `AD6E428D05D2359DA73B6DEE7CFDCEC646C87390B496B59CAD5F46B5A452851F` | `AD6E428D05D2359DA73B6DEE7CFDCEC646C87390B496B59CAD5F46B5A452851F` | **EXACT MATCH** |
| `backend/models/model_metadata.json` | `30C1C75D81AD61B1D0CACB70B221D034840888C7BFEDE949A15D47B139699F60` | `30C1C75D81AD61B1D0CACB70B221D034840888C7BFEDE949A15D47B139699F60` | **EXACT MATCH** |
| `backend/reports/test_predictions.csv` | `E93BE4550F97FE2CFE6BC0F2366650833D96F284C45CD1EB6026FBA0DB98449D` | `E93BE4550F97FE2CFE6BC0F2366650833D96F284C45CD1EB6026FBA0DB98449D` | **EXACT MATCH** |
| `backend/reports/stage5_test_evaluation.md` | `9E55B1F574E18BC4623A871D58926FEFCCD29F4C4E3EE22010A4A54A4E4CD1D2` | `9E55B1F574E18BC4623A871D58926FEFCCD29F4C4E3EE22010A4A54A4E4CD1D2` | **EXACT MATCH** |
| `backend/database/stage8_9_reviews.db` | Bit-identical check on 343 reviewed records | 338 Approved Non-Scream, 2 Scream Present, 3 Ambiguous; Anchor `fsd50k_349401` = `SCREAM_PRESENT` | **EXACT MATCH** |
| **Operating Threshold** | `0.3500` | `0.3500` (in `model_metadata.json`) | **EXACT MATCH** |

### 2.2 License Audit & Historical Quarantine
- All 1,167 baseline recordings in `commercially_eligible_manifest.json` were cross-checked against the 161 quarantined entries in `restricted_recordings_audit.csv`. **Zero quarantine leakage detected.**
- Stated licenses in the eligible cohort comprise exclusively CC0 (55.5%), CC BY 3.0 (36.2%), and CC BY 4.0 (8.3%). Zero non-commercial or Sampling+ licenses admitted.
- Source-group disjointness verified: $\text{TrainGroups} \cap \text{ValGroups} = \emptyset$, $\text{TrainGroups} \cap \text{TestGroups} = \emptyset$, $\text{ValGroups} \cap \text{TestGroups} = \emptyset$.
- Historical Stage 5 test quarantine: 0 Stage 5 recordings or source groups present in Train or Validation splits.

Audit ledger saved to [`stage8_9_11_readiness_audit.json`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_11_evaluation/stage8_9_11_readiness_audit.json).

---

## 3. Targeted Data Acquisition & Expanded Commercial Manifest

In accordance with [`targeted_data_acquisition_plan.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_10_readiness/targeted_data_acquisition_plan.md), targeted permissive recordings were acquired from FSD50K dev audio (verified CC0 / CC BY) and calibrated synthetic mixing was executed:

### 3.1 Acquired Recordings Breakdown

| Category | Target Groups | Acquired Groups | Target Clips | Acquired Clips | Verified License | Acquisition Method |
| :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| `shouting_and_speech` | 37 | **37** | 60 | **49** | CC0, CC BY 3.0/4.0 | Direct FSD50K Ingestion (Shout, Yell, Speech) |
| `crowd_chant_cheering` | 25 | **25** | 50 | **38** | CC0, CC BY 3.0/4.0 | Direct FSD50K Ingestion (Crowd, Applause) |
| `scream` | 18 | **18** | 36 | **30** | CC0, CC BY 3.0/4.0 | Direct FSD50K Ingestion (Screaming) |
| `masked_distant_screams`| 20 | **20** | 40 | **40** | Derived CC0/CC BY | Calibrated synthetic mixing at -6 to +3 dB SNR |
| `whistles_and_squeaks` | 12 | **12** | 24 | **16** | CC0, CC BY 3.0/4.0 | Direct FSD50K Ingestion (Squeak, Whistle) |
| `sfx_sirens_fireworks` | 12 | **12** | 24 | **13** | CC0, CC BY 3.0/4.0 | Direct FSD50K Ingestion (Siren, Fireworks, Alarm) |
| `infant_crying` | 13 | **13** | 17 | **14** | CC0, CC BY 3.0/4.0 | Direct FSD50K Ingestion (Crying_and_sobbing) |
| `general_environmental` | 12 | **12** | 24 | **17** | CC0, CC BY 3.0/4.0 | Direct FSD50K Ingestion (Environmental noise) |
| **ACQUIRED TOTAL** | **149** | **149** | **275** | **217** | **100% Permissive** | Full Attribution Tracked |

All 217 new recordings were converted to 16 kHz mono PCM 16-bit and saved into [`stage8_9_11_evaluation/audio/`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_11_evaluation/audio/). Complete provenance is codified in [`stage8_9_11_acquisition_manifest.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_11_evaluation/stage8_9_11_acquisition_manifest.csv).

### 3.2 Unified Stage 8.9.11 Dataset Balance

Combining the 1,167 baseline eligible recordings with the 217 newly acquired recordings yields **1,384 recordings across 593 independent source groups**:

```
Stage 8.9.11 Unified Category Breakdown
======================================================================
shouting_and_speech      [████████████████████████████  ] 281 clips (160 train, 79 val, 42 test)
scream                   [████████████████████████      ] 245 clips (121 train, 58 val, 66 test)
crowd_chant_cheering     [████████████████████████      ] 242 clips (154 train, 45 val, 43 test)
masked_distant_screams   [████████████████              ] 161 clips ( 80 train, 38 val, 43 test)
whistles_and_squeaks     [████████████████              ] 157 clips ( 93 train, 31 val, 33 test)
general_environmental    [█████████████                 ] 132 clips ( 65 train, 35 val, 32 test)
sfx_sirens_fireworks     [█████████                     ]  91 clips ( 43 train, 15 val, 33 test)
infant_crying            [███████                       ]  75 clips ( 41 train, 19 val, 15 test)
----------------------------------------------------------------------
TOTAL UNIFIED COHORT     [██████████████████████████████] 1,384 clips (757 train, 320 val, 307 test)
```

- **Split Disjointness:** Train (351 source groups), Val (116 source groups), Test (126 source groups). Zero group overlap.
- Codified in [`stage8_9_11_dataset_manifest.json`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_11_evaluation/stage8_9_11_dataset_manifest.json) and [`stage8_9_11_category_balance.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_11_evaluation/stage8_9_11_category_balance.csv).

---

## 4. Preregistered Model Candidate Architectures

Four candidate models were implemented in [`train_and_evaluate_stage11.py`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_11_evaluation/train_and_evaluate_stage11.py):

1. **Candidate D_v4 (Baseline Linear Fusion):**
   - 3,072-dim multi-pooled YAMNet embeddings (mean, max, p10).
   - $L_2$-regularized Logistic Regression ($C=0.1$ selected on validation) + Platt Scaling calibration.
2. **Candidate T1_v4 (Dilated 1D Temporal Convolutional Network):**
   - $N \times 70 \times 1024$ masked frame embeddings.
   - 1D Conv projection (64 filters) + 2 Dilated Residual Blocks (dilations 1, 2) + Global Average Pooling + Dense(32) + Sigmoid.
   - Trained with Adam optimizer and validation PR-AUC early stopping.
3. **Candidate H_v4_Commercial (Calibrated Hybrid Fusion):**
   - 5,144-dim representation: Multi-pool YAMNet (3,072) + Temporal std (1,024) + Temporal frame delta (1,024) + 16 Acoustic Turbulence features + Vocal/Crowd logits (2) + Vocal summary (6).
   - $L_2$-regularized Logistic Regression ($C=0.05$ selected on validation) + Platt Scaling calibration.
4. **Candidate H_v5_SNR (Context-Aware Hybrid Fusion):**
   - 5,148-dim representation: 5,144 dims from `H_v4` augmented with 4 adaptive SNR features ($E_{<150\text{Hz}}/E_{\text{total}}$, Band-SNR $1.5-4.5\text{ kHz}$, Noise floor, Crest ratio).
   - $L_2$-regularized Logistic Regression ($C=0.05$ selected on validation) + Platt Scaling calibration.

---

## 5. Threshold Selection & Validation Feasibility Audit

In accordance with Section 5 of the evaluation protocol:
- Thresholds were searched exclusively on the Validation Split ($N=320$: 96 screams, 224 non-screams).
- **Rule:** Operational threshold must satisfy $\text{Recall} \ge 96.0\%$ AND $\text{FPR} \le 5.0\%$.

| Candidate Model | Feasible Thresholds Found ($\text{Rec}\ge 96\%, \text{FPR}\le 5\%$) | Validation Feasibility Verdict | Locked Research Threshold ($\tau^*$) | Validation Recall at $\tau^*$ | Validation FPR at $\tau^*$ | Validation F1 at $\tau^*$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Model D_v4** | **0** | **INFEASIBLE** | `0.3800` | 89.58% | 7.59% | 0.8866 |
| **Model T1_v4** | **0** | **INFEASIBLE** | `0.5300` | 85.42% | 8.04% | 0.8542 |
| **Model H_v4_Commercial** | **0** | **INFEASIBLE** | `0.4200` | 82.29% | 6.70% | 0.8541 |
| **Model H_v5_SNR** | **0** | **INFEASIBLE** | `0.5100` | 81.25% | 5.36% | 0.8571 |

**Audit Determination:** No candidate was able to reach the safety-critical 96% recall target while suppressing hard-negative false alarms below 5% on independent validation recordings. All four candidates are formally **INFEASIBLE**. Decision thresholds were frozen in [`preregistered_candidate_thresholds.json`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_11_evaluation/preregistered_candidate_thresholds.json) before evaluating the test set.

---

## 6. Single-Shot Held-Out Test Evaluation & Statistical Comparison

The held-out test cohort ($N = 307$: 109 screams, 198 non-screams) was evaluated **exactly once** using locked research thresholds:

### 6.1 Test Metrics & Research Acceptance Gates

| Metric / Gate | Research Target | Model D_v4 | Model T1_v4 | Model H_v4_Commercial | Model H_v5_SNR | Best Candidate |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Locked Threshold ($\tau^*$)** | Validation-tuned | `0.3800` | `0.5300` | `0.4200` | `0.5100` | — |
| **Gate 1: Overall Scream Recall** | $\ge \mathbf{96.00\%}$ | 89.91% (FAILED) | 85.32% (FAILED) | 78.90% (FAILED) | 77.98% (FAILED) | D_v4 (89.91%) |
| *95% Bootstrap CI (Recall)* | $[90.0\%, 100\%]$ | [83.6%, 95.7%] | [75.8%, 93.9%] | [69.0%, 88.0%] | [67.4%, 87.3%] | D_v4 |
| **Gate 2: Hard-Negative FPR** | $\le \mathbf{5.00\%}$ | 7.07% (FAILED) | 8.08% (FAILED) | 7.07% (FAILED) | **5.05%** (BORDERLINE) | **H_v5_SNR (5.05%)** |
| *95% Bootstrap CI (FPR)* | $[0.0\%, 8.0\%]$ | [3.1%, 11.8%] | [4.4%, 12.8%] | [3.4%, 11.3%] | **[1.9%, 8.8%]** | **H_v5_SNR** |
| **Gate 3: Shouted-Speech FPR** | $\le \mathbf{15.00\%}$ | **11.90% (PASS)** | **11.90% (PASS)** | **9.52% (PASS)** | **9.52% (PASS)** | **H_v4 & H_v5 (9.52%)** |
| **PR-AUC** | Higher | 0.9198 | 0.8855 | 0.8949 | **0.9273** | **H_v5_SNR (0.9273)** |
| *95% Bootstrap CI (PR-AUC)* | — | [0.8530, 0.9714] | [0.7889, 0.9657] | [0.7993, 0.9537] | [0.8650, 0.9720] | **H_v5_SNR** |
| **ROC-AUC** | Higher | 0.9564 | 0.9412 | 0.9511 | **0.9570** | **H_v5_SNR (0.9570)** |
| **Precision** | Higher | 0.8750 | 0.8532 | 0.8600 | **0.8947** | **H_v5_SNR (0.8947)** |
| **F1 Score** | Higher | **0.8869** | 0.8532 | 0.8229 | 0.8333 | **D_v4 (0.8869)** |
| **Brier Calibration Score** | Lower | 0.0811 | 0.0884 | 0.0825 | **0.0795** | **H_v5_SNR (0.0795)** |
| **Final Acceptance Status** | All gates met | **NOT CERTIFIED** | **NOT CERTIFIED** | **NOT CERTIFIED** | **NOT CERTIFIED** | **NONE** |

### 6.2 Category-Level Detection Breakdown

| Acoustic Category | Total Test Clips | D_v4 False Alarms / Misses | T1_v4 False Alarms / Misses | H_v4_Commercial | H_v5_SNR |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `scream` (Clean Positives) | 66 clips | 5 misses (92.4% rec) | 9 misses (86.4% rec) | 12 misses (81.8% rec) | 13 misses (80.3% rec) |
| `masked_distant_screams` (Positives) | 43 clips | 6 misses (86.0% rec) | 7 misses (83.7% rec) | 11 misses (74.4% rec) | 11 misses (74.4% rec) |
| `shouting_and_speech` (Negatives) | 42 clips | 5 false alarms (11.9% FPR) | 5 false alarms (11.9% FPR) | **4 false alarms (9.5% FPR)** | **4 false alarms (9.5% FPR)** |
| `crowd_chant_cheering` (Negatives) | 43 clips | 5 false alarms (11.6% FPR) | 6 false alarms (14.0% FPR) | 5 false alarms (11.6% FPR) | **4 false alarms (9.3% FPR)** |
| `infant_crying` (Negatives) | 15 clips | 3 false alarms (20.0% FPR) | 3 false alarms (20.0% FPR) | 2 false alarms (13.3% FPR) | **1 false alarm (6.7% FPR)** |
| `whistles_and_squeaks` (Negatives) | 33 clips | 1 false alarm (3.0% FPR) | 2 false alarms (6.1% FPR) | 1 false alarm (3.0% FPR) | 1 false alarm (3.0% FPR) |
| `sfx_sirens_fireworks` (Negatives) | 33 clips | **0 false alarms (0.0% FPR)** | **0 false alarms (0.0% FPR)** | **0 false alarms (0.0% FPR)** | **0 false alarms (0.0% FPR)** |
| `general_environmental` (Negatives) | 32 clips | **0 false alarms (0.0% FPR)** | **0 false alarms (0.0% FPR)** | **0 false alarms (0.0% FPR)** | **0 false alarms (0.0% FPR)** |

### 6.3 Paired Statistical Hypothesis Testing vs. Baseline D_v4

To evaluate whether architectural enhancements represent statistically significant differences rather than random sampling fluctuations:

- **Paired McNemar Test (Edwards Continuity Correction):**
  - Model T1_v4 vs D_v4: $\chi^2 = 1.8947, p = 0.1687$ (Not statistically significant).
  - Model H_v4_Commercial vs D_v4: $\chi^2 = 5.0435, p = 0.0247$ (Nominal $p < 0.05$, but not significant under Holm-Bonferroni $\alpha' = 0.0125$).
  - Model H_v5_SNR vs D_v4: $\chi^2 = 3.3684, p = 0.0665$ (Not statistically significant).
- **Cluster Bootstrap Delta PR-AUC (1,000 iterations at source-group level):**
  - $\Delta\text{PR-AUC}(\text{H\_v5} - \text{D\_v4}) = +0.0075$ (95% CI: $[-0.0384, +0.0521]$). Because the 95% confidence interval spans zero, **the gain in PR-AUC is not statistically significant at $\alpha = 0.05$**.

Complete predictions are saved in [`stage8_9_11_test_predictions.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_11_evaluation/stage8_9_11_test_predictions.csv).

---

## 7. Real-World Operational Exposure & Prevalence Modeling

Because the held-out test cohort contains an artificially enriched hard-negative ratio ($N_{\text{pos}}=109, N_{\text{neg}}=198$, positive prevalence $\approx 35.5\%$), reported benchmark precision ($\approx 89.5\%$) does not reflect live festival conditions.

### Modeled Operational Scenarios (Continuous 10-Hour Festival Surveillance = 72,000 Frames)

| Operational Scenario | Assumed Scream Prevalence ($\pi$) | Model D_v4 Effective PPV | Model D_v4 Daily False Alarms | Model H_v5_SNR Effective PPV | Model H_v5_SNR Daily False Alarms |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Realistic Ambient Surveillance** | $10^{-4}$ (1 scream / 1.4 hours) | **0.13%** (1 true in 787 alerts) | **5,089 alarms** (509/hr) | **0.15%** (1 true in 648 alerts) | **3,635 alarms** (364/hr) |
| **Elevated Incident Festival Zone** | $10^{-3}$ (1 scream / 8 minutes) | **1.25%** (1 true in 80 alerts) | **5,085 alarms** (509/hr) | **1.52%** (1 true in 66 alerts) | **3,632 alarms** (363/hr) |

> [!CAUTION]
> **Operational Reality:** A 5.05% frame-level false positive rate produces **363 false alarms per hour** without multi-frame state-machine hysteresis and cooldown suppression. Frame-level classifiers alone cannot be deployed directly to sound emergency alarms.

---

## 8. Standardized End-to-End Latency & Edge Footprint Results

Empirical measurement across 50 timed iterations on a 1.0s audio window (16 kHz PCM) on the edge target runtime:

```
Pipeline Latency Profile (Median: 60.08 ms)
+----------------------------------------------------------------------------------------------------+
| [0.13ms] 16-bit PCM Ingestion                                                                      |
| [3.47ms] Resampling & DC Filter                                                                    |
| [██████████] 10.28ms (17.1%) YAMNet Feature Extraction                                             |
| [██████████████████████████████████████] 39.31ms (65.4%) Turbulence STFT & Welch Periodogram       |
| [███] 3.33ms (5.5%) Classifier & Platt Calibration                                                |
| [0.10ms] State Machine & JSON Alert                                                                |
+----------------------------------------------------------------------------------------------------+
Target Budget (25.0ms): [█████████████████████████---------------------------------------------------] 25.0 ms
Actual Latency (60.08ms): [████████████████████████████████████████████████████████████] 60.08 ms (EXCEEDS BUDGET)
```

- **Classifier-Only Latency:** **3.330 ms** (p95: 3.729 ms) — PASSES edge latency target.
- **Full End-to-End Latency:** **60.076 ms** (p95: 68.961 ms) — **FAILS instantaneous 25.0 ms budget**.
- **Cause:** Stage 4 (Turbulence STFT + Welch spectral SNR features) accounts for 65.4% of execution time (39.31 ms).
- **Hop Feasibility:** In a streaming pipeline with a 500 ms hop interval, 60.08 ms consumes **12.0%** of available buffer time, proving real-time feasibility on a 500 ms rolling schedule, but failing an instantaneous sub-25ms response requirement.
- **Memory & Storage Footprint:** Peak process heap delta is 1.25 MB; serialized model file `model_h_v5_snr.joblib` is **142.41 KB** on disk.

Detailed measurements codified in [`end_to_end_latency_results.json`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_11_evaluation/reports/end_to_end_latency_results.json).

---

## 9. Deliverables Inventory

All artifacts for Stage 8.9.11 are saved in [`backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_11_evaluation/`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_11_evaluation/):

1. [`stage8_9_11_readiness_audit.json`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_11_evaluation/stage8_9_11_readiness_audit.json) — Readiness gate verification ledger.
2. [`stage8_9_11_acquisition_manifest.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_11_evaluation/stage8_9_11_acquisition_manifest.csv) — 217 acquired recordings with full attribution, source URLs, and PCM hashes.
3. [`stage8_9_11_dataset_manifest.json`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_11_evaluation/stage8_9_11_dataset_manifest.json) — Unified dataset manifest of 1,384 recordings across 593 source groups.
4. [`stage8_9_11_category_balance.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_11_evaluation/stage8_9_11_category_balance.csv) — Category balance matrix across splits.
5. [`preregistered_candidate_thresholds.json`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_11_evaluation/preregistered_candidate_thresholds.json) — Frozen validation threshold selection records.
6. [`stage8_9_11_test_predictions.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_11_evaluation/stage8_9_11_test_predictions.csv) — Held-out test set continuous probabilities for all 4 candidates.
7. [`stage8_9_11_evaluation_metrics.json`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_11_evaluation/stage8_9_11_evaluation_metrics.json) — Metrics, bootstrap CIs, McNemar tests, category breakdowns, and operational prevalence models.
8. [`end_to_end_latency_results.json`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_11_evaluation/reports/end_to_end_latency_results.json) — Stage-by-stage latency profile.
9. [User-Facing Artifact](file:///C:/Users/zahia/.gemini/antigravity-ide/brain/ac3bc657-c5b1-4cc2-baf6-be57b0544e4d/stage8_9_11_evaluation_audit.md) — Executive governance summary.

---

## 10. Final Decision & Stop Condition Status

### Summary Checklist Against Acceptance Targets:
- **Recall $\ge 96.00\%$:** **NOT MET** by any candidate (Best: D_v4 at 89.91% [83.6%, 95.7%]; H_v5_SNR at 77.98% [67.4%, 87.3%]).
- **Hard-Negative FPR $\le 5.00\%$:** **NOT MET** with certified certainty (Best: H_v5_SNR point estimate 5.05%, 95% CI upper bound 8.8%).
- **Shouted-Speech FPR $\le 15.00\%$:** **MET** by all candidates (H_v4 and H_v5 reached 9.52%).

### Strict Mandate Compliance:
- **No candidate is promoted to production.**
- **Production models, metadata, thresholds, database, and historical test sets remain 100% frozen and bit-identical.**
- **Production operating threshold remains locked at `0.3500`.**

The Stage 8.9.11 audit is complete. Execution is paused awaiting your explicit instructions.
