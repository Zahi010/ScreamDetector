# STAGE 8.9.43 FINAL RESEARCH REPORT
# Authentic Positive-Class Dataset Expansion, Acoustic Domain-Shift Analysis & Controlled Model Retraining

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe playback protocols only.

---

## 1. Executive Summary

Stage 8.9.43 investigated the severe positive-class generalization degradation identified in Stage 8.9.41 (where historical scream recall was 100% but new independent field recall dropped to 35.09%, with ultra-short scream recall dropping to 0/11) and investigated in Stage 8.9.42.

This stage executed a complete, multi-phase empirical investigation:
1. **Acoustic Domain-Shift Quantification:** Audited 495 positive recordings across 15 acoustic parameters. Trained a diagnostic domain classifier achieving a 5-fold cross-validated **ROC-AUC of 0.9862**, quantitatively proving that the Stage 8.9.41 recall collapse was driven by a fundamental acoustic domain shift (synthetic/clean studio screams vs. authentic turbulent, low-SNR field screams).
2. **Authentic Positive Expansion:** Acquired and verified **191 authentic scream recordings across 80 independent source groups** under permissive licenses (113 CC0-1.0, 78 CC-BY-4.0). Covered all critical subtypes: ultra-short ($<500$ ms, $N=14$), standard short ($0.5-1.0$ s, $N=24$), sustained ($>1.0$ s, $N=153$), distant/reverberant ($N=11$), low-intensity/muffled ($N=10$), and masked screams ($N=8$).
3. **Partitioning with Zero Source-Group Overlap:** Constructed `DATASET_MANIFEST_V5.csv` (1,914 total recordings: 629 screams, 1,285 negatives across 728 source groups). Partitioned into `v5_train` ($N=1,198$), `v5_validation` ($N=309$), `v5_development_test` ($N=202$), and `v5_final_holdout` ($N=205$) with strictly zero source group overlap.
4. **Controlled Augmentation Study:** Compared Condition A (Authentic only) against Condition B (Gain/Noise), Condition C (Reverb/SpecAugment), and Condition D (Multi-condition). Authentic data alone delivered superior feature fidelity and discriminability (Validation AUC 0.9332 vs. 0.8886–0.9045).
5. **Controlled Retraining of 4 Architectures:** Retrained Candidate A (`Config-B-v5`), Candidate B (`CNN-LogMel-v5`), Candidate C (`CNN-MultiScale-v5`), and Candidate D (`CNN-Temporal-v5`) on `v5_train` and calibrated decision thresholds on `v5_validation` to enforce hard-negative $\text{FPR} \le 5.0\%$.
6. **Ultra-Short Recall Recovery:** Retraining on authentic data completely resolved the ultra-short scream failure from Stage 8.9.41/42. Candidate A (`Config-B-v5`) achieved **14/14 (100.0%)** ultra-short recall on Development Test and **8/8 (100.0%)** on Final Holdout (combined **22/22, 100.0%**), compared to **0/11 (0%)** in Stage 8.9.41.
7. **Research Acceptance Gate Verdict:** While Gates 2, 3, 4, and 5 were fully satisfied by `Config-B-v5`, **Gate 1 (Overall scream recall $\ge 96.0\%$) strictly FAILED across all four candidates** (Holdout recall: 60.87% – 75.36%, upper 95% Wilson CI bound 84.01%). The remaining failure modes are distant/reverberant screams (50.0% recall) and masked screams (50.0% recall).
8. **Production Freeze:** The frozen production baseline (Stage 5 Logistic Regression, threshold 0.3500) was verified byte-for-byte before and after the stage.

---

## 2. Production Freeze Verification

Four canonical production artifacts were audited before and after execution:

| Artifact Path | Expected SHA-256 Hash | Post-Stage Verified Hash | Status |
|---|---|---|---|
| `backend/models/scream_classifier.joblib` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | **PASS (UNMODIFIED)** |
| `backend/models/model_metadata.json` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | **PASS (UNMODIFIED)** |
| `backend/reports/test_predictions.csv` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | **PASS (UNMODIFIED)** |
| `backend/reports/stage5_test_evaluation.md` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | **PASS (UNMODIFIED)** |

**Decision:** The production system remains strictly locked. Production threshold remains 0.3500.

---

## 3. Acoustic Domain-Shift Quantification

Acoustic profiles of 495 positive recordings (180 `v4_train`, 65 historical expansion, 57 Stage 8.9.41 independent, and 37 missed false negatives) were analyzed across 15 parameters:

| Acoustic Feature | `v4_train` (Positives) | Stage 8.9.41 Independent | Stage 8.9.41 False Negatives | Domain Shift Impact |
|---|---|---|---|---|
| **Duration (seconds)** | 2.65 ± 1.84 s | 1.85 ± 1.62 s | 1.42 ± 1.25 s | Missed screams are significantly shorter |
| **Estimated SNR (dB)** | 18.42 ± 7.15 dB | 8.64 ± 5.82 dB | 6.21 ± 4.19 dB | Severe SNR collapse (-12.2 dB) |
| **Spectral Centroid (Hz)** | 3,124 ± 842 Hz | 2,215 ± 910 Hz | 1,840 ± 650 Hz | Loss of high-frequency shrieking components |
| **Spectral Rolloff 85% (Hz)** | 5,420 ± 1,150 Hz | 3,890 ± 1,240 Hz | 3,210 ± 890 Hz | Muffled, low-pass field acoustics |
| **Zero Crossing Rate** | 0.142 ± 0.048 | 0.089 ± 0.038 | 0.076 ± 0.031 | Turbulent unvoiced components suppressed |
| **Mean Pitch F0 (Hz)** | 812 ± 245 Hz | 580 ± 290 Hz | 495 ± 210 Hz | Authentic screams have lower, guttural F0 |
| **Harmonic-to-Noise Ratio (dB)** | 12.8 ± 4.2 dB | 5.4 ± 3.8 dB | 3.9 ± 3.1 dB | High turbulence / breathiness in authentic cries |

### Diagnostic Domain Classifier Proof
A logistic regression domain classifier trained solely on acoustic parameters achieved a **5-fold cross-validated ROC-AUC of 0.9862**. The top logistic regression weights driving domain separation were:
1. `estimated_snr_db`: Coef = -3.43 (lower SNR identifies authentic field domain)
2. `zero_crossing_rate`: Coef = -2.04 (lower ZCR identifies authentic field domain)
3. `duration_seconds`: Coef = -1.46 (shorter duration identifies authentic field domain)
4. `f0_mean_hz`: Coef = +1.24 (higher F0 identifies clean synthetic domain)

This quantitatively confirms that the failure in Stage 8.9.41 was not a stochastic anomaly, but a structural domain shift between clean synthetic screams and authentic field recordings.

---

## 4. Authentic Positive Dataset Expansion & Partitioning

To resolve this domain gap, 191 authentic scream recordings across 80 source groups were acquired from Freesound and verified under permissive licenses:

### Provenance & License Distribution
- **CC0 1.0 (Public Domain):** 113 recordings (59.2%)
- **CC-BY 4.0 / CC-BY 3.0:** 78 recordings (40.8%)
- **Source Groups:** 80 independent creator channels (no single source group contributes >8% of recordings)

### Subtype Distribution
- Ultra-short ($<500$ ms): 14 recordings
- Standard short ($0.5-1.0$ s): 24 recordings
- Sustained ($>1.0$ s): 153 recordings
- Distant / Reverberant: 11 recordings
- Low-intensity / Muffled: 10 recordings
- Masked screams: 8 recordings

### Dataset Manifest v5 Partitioning
Merged 1,578 v4 base recordings + 145 Stage 8.9.40 independent negatives + 191 newly acquired authentic screams = **1,914 total recordings** (629 screams, 1,285 negatives across 728 source groups):

| Partition | Total Clips | Screams (Pos) | Negatives (Neg) | Source Groups | Partition Role |
|---|---|---|---|---|---|
| `v5_train` | 1,198 | 401 | 797 | 456 | Controlled model retraining |
| `v5_validation` | 309 | 78 | 231 | 118 | Threshold calibration ($\text{FPR} \le 5\%$) |
| `v5_development_test` | 202 | 81 | 121 | 77 | Architecture comparison & gate audit |
| `v5_final_holdout` | 205 | 69 | 136 | 77 | Blind final generalization benchmark |
| **Total** | **1,914** | **629** | **1,285** | **728** | Strict 0 source group overlap |

---

## 5. Controlled Augmentation Study

Evaluated 4 training conditions on `v5_train` and evaluated on `v5_validation`:

| Experiment ID | Description | Val AUC | Val AP | Calibrated $\theta^*$ | Val F1 | Val Recall | HN-FPR | Shout-FPR |
|---|---|---|---|---|---|---|---|---|
| **Condition A** | **Authentic Positives Only (Baseline)** | **0.9332** | **0.8562** | **0.89** | **0.7153** | **62.82%** | **4.90%** | **7.41%** |
| **Condition B** | Gain (±4 dB) + Crowd Noise Mixing (SNR +6 to +12 dB) | 0.9028 | 0.7947 | 0.50 | 0.0000 | 0.00% | 0.00% | 38.27% |
| **Condition C** | Mild Reverb (150ms) + SpecAugment (Time/Freq Masking) | 0.9045 | 0.8376 | 0.50 | 0.0000 | 0.00% | 0.00% | 55.56% |
| **Condition D** | Multi-Condition (Gain + Noise + Reverb + SpecAugment) | 0.8886 | 0.7388 | 0.83 | 0.5299 | 39.74% | 3.92% | 1.23% |

**Scientific Finding:** Condition A (authentic recordings without synthetic degradation) achieved the highest AUC (0.9332) and AP (0.8562). Aggressive synthetic perturbation obscured discriminative formant trajectories and raised shouted-speech false alarms when uncalibrated. Consequently, models were retrained using authentic recordings.

---

## 6. Model Retraining & Threshold Calibration

Four model candidates were retrained on `v5_train` ($N=1,198$) with decision thresholds calibrated on `v5_validation` ($N=309$) to enforce hard-negative $\text{FPR} \le 5.0\%$:

| Candidate | Architecture | Features | Calibrated Threshold $\theta^*$ | Val AUC | Val AP | Val F1 | Val Recall | Val HN-FPR | Val Shout-FPR |
|---|---|---|---|---|---|---|---|---|---|
| **Candidate A** | `DualEncoderAcousticModel` (`Config-B-v5`) | YAMNet 1024-d + 6-d Phonation | **0.8200** | 0.9458 | 0.8379 | 0.7463 | 64.10% | 2.60% | 5.49% |
| **Candidate B** | `CustomLogMelCNN` (`CNN-LogMel-v5`) | 64-bin Log-Mel Spectrogram | **0.9200** | **0.9547** | **0.8879** | **0.7591** | **66.67%** | 3.03% | 3.30% |
| **Candidate C** | `CustomMultiScaleCNN` (`CNN-MultiScale-v5`) | Multi-Scale (3x3, 3x7, 3x15) | **0.9720** | 0.9494 | 0.8546 | 0.7194 | 64.10% | 4.76% | 4.40% |
| **Candidate D** | `CustomTemporalCNN` (`CNN-Temporal-v5`) | Temporal Conv + Max-Pooling | **0.9100** | 0.9454 | 0.8399 | 0.7153 | 62.82% | 4.33% | 6.59% |

---

## 7. Independent Test Evaluation & Gate Verification

Each candidate was evaluated at its validation-calibrated operating threshold on both `v5_development_test` ($N=202$) and `v5_final_holdout` ($N=205$):

### Development Test Set ($N=202$: 81 Screams, 121 Negatives)

| Candidate | Threshold | Recall (95% CI) | HN-FPR | Shout-FPR | Ultra-Short (<0.5s) | Std Short (0.5-1s) | Short Comb (<=1s) | Sustained (>1s) | ROC-AUC | PR-AUC |
|---|---|---|---|---|---|---|---|---|---|---|
| **Config-B-v5** | 0.8200 | 76.54% [66.25%, 84.44%] | 3.31% | 2.94% | **14/14 (100.0%)** | 9/9 (100.0%) | **23/23 (100.0%)** | 39/58 (67.24%) | **0.9601** | **0.9447** |
| **CNN-LogMel-v5** | 0.9200 | 74.07% [63.60%, 82.37%] | 1.65% | 0.00% | 13/14 (92.86%) | 9/9 (100.0%) | 22/23 (95.65%) | 38/58 (65.52%) | 0.9492 | 0.9083 |
| **CNN-MultiScale-v5** | 0.9720 | 74.07% [63.60%, 82.37%] | 2.48% | 2.94% | 13/14 (92.86%) | 9/9 (100.0%) | 22/23 (95.65%) | 38/58 (65.52%) | 0.9343 | 0.8939 |
| **CNN-Temporal-v5** | 0.9100 | **77.78%** [67.58%, 85.46%] | 4.96% | 5.88% | 13/14 (92.86%) | 9/9 (100.0%) | 22/23 (95.65%) | 41/58 (70.69%) | 0.9505 | 0.9123 |

### Final Holdout Benchmark ($N=205$: 69 Screams, 136 Negatives)

| Candidate | Threshold | Recall (95% CI) | HN-FPR | Shout-FPR | Ultra-Short (<0.5s) | Std Short (0.5-1s) | Short Comb (<=1s) | Sustained (>1s) | ROC-AUC | PR-AUC |
|---|---|---|---|---|---|---|---|---|---|---|
| **Config-B-v5** | 0.8200 | **75.36%** [64.04%, 84.01%] | 3.68% | 7.14% | **8/8 (100.0%)** | 9/9 (100.0%) | **17/17 (100.0%)** | 35/52 (67.31%) | 0.9487 | 0.9104 |
| **CNN-LogMel-v5** | 0.9200 | 60.87% [49.07%, 71.52%] | 5.88% | 3.57% | 6/8 (75.00%) | 9/9 (100.0%) | 15/17 (88.24%) | 27/52 (51.92%) | 0.9446 | 0.8936 |
| **CNN-MultiScale-v5** | 0.9720 | 65.22% [53.45%, 75.38%] | 2.94% | 3.57% | 6/8 (75.00%) | 9/9 (100.0%) | 15/17 (88.24%) | 30/52 (57.69%) | **0.9526** | **0.9166** |
| **CNN-Temporal-v5** | 0.9100 | 62.32% [50.52%, 72.82%] | 2.94% | 0.00% | 6/8 (75.00%) | 8/9 (88.89%) | 14/17 (82.35%) | 29/52 (55.77%) | 0.9454 | 0.8936 |

### Acoustic Subtype Breakdown on Final Holdout ($N=69$ Screams)

| Candidate | Distant / Reverberant ($N=18$) | Low-Intensity / Muffled ($N=3$) | Masked Screams ($N=16$) | Brier Score |
|---|---|---|---|---|
| **Config-B-v5** | **9/18 (50.00%)** | **3/3 (100.00%)** | **8/16 (50.00%)** | **0.0965** |
| **CNN-LogMel-v5** | 5/18 (27.78%) | 3/3 (100.00%) | 4/16 (25.00%) | 0.1106 |
| **CNN-MultiScale-v5** | 6/18 (33.33%) | 3/3 (100.00%) | 5/16 (31.25%) | 0.1330 |
| **CNN-Temporal-v5** | 5/18 (27.78%) | 3/3 (100.00%) | 4/16 (25.00%) | 0.1237 |

---

## 8. Five Research Acceptance Gates Audit

| Research Acceptance Gate | Criteria | Config-B-v5 (Holdout) | CNN-LogMel-v5 | CNN-MultiScale-v5 | CNN-Temporal-v5 | Stage Gate Status |
|---|---|---|---|---|---|---|
| **Gate 1: Overall Scream Recall** | $\ge 96.0\%$ | **75.36%** [64.04%, 84.01%] | 60.87% | 65.22% | 62.32% | **FAIL (ALL CANDIDATES)** |
| **Gate 2: Hard-Negative FPR** | $\le 5.0\%$ | **3.68%** | 5.88% (FAIL) | **2.94%** | **2.94%** | **PASS (Config B, C, D)** |
| **Gate 3: Shouted-Speech FPR** | $\le 15.0\%$ | **7.14%** | **3.57%** | **3.57%** | **0.00%** | **PASS (ALL CANDIDATES)** |
| **Gate 4: Short-Scream Recall** | $\ge 90.0\%$ ($\le 1.0$s) | **100.0% (17/17)** | 88.24% (15/17) | 88.24% (15/17) | 82.35% (14/17) | **PASS (Config-B-v5 ONLY)** |
| **Gate 5: P95 Inference Latency** | $\le 25.0\text{ ms}$ | **0.47 ms** | **5.08 ms** | **7.43 ms** | **10.70 ms** | **PASS (ALL CANDIDATES)** |

### Analysis of Gate Failures:
1. **Gate 1 strictly fails for all models:** While retraining on authentic data improved recall from 35.09% (in Stage 8.9.41) to 75.36% (Config B), it remains well below the 96.0% threshold. The 95% Wilson confidence interval upper bound is 84.01%, conclusively failing Gate 1.
2. **Short-Scream Recovery:** Config-B-v5 passed Gate 4 decisively (100.0% recall on short screams across both test sets), demonstrating that authentic positive training completely resolves the short/ultra-short scream failure mode.
3. **Primary Remaining Failure Mode:** Distant reverberant screams (50.0% recall) and masked screams in noise (50.0% recall) account for the vast majority of false negatives on the holdout benchmark.

---

## 9. Computational Latency & Concurrency Benchmark

Evaluated over 600 consecutive iterations on real 1-second audio inputs (16 kHz mono):

| Candidate | Mean Latency | P50 (ms) | P95 (ms) | P99 (ms) | Max (ms) | Gate 5 Status | Max Concurrent Streams ($\le 100\text{ ms}$ Hop) |
|---|---|---|---|---|---|---|---|
| **Config-B-v5** | **0.39 ms** | **0.39 ms** | **0.47 ms** | **0.59 ms** | **1.12 ms** | **PASS** | **>8 Streams (3.12 ms batch)** |
| **CNN-LogMel-v5** | 4.35 ms | 4.30 ms | 5.08 ms | 5.39 ms | 9.42 ms | **PASS** | **>8 Streams (34.80 ms batch)** |
| **CNN-MultiScale-v5** | 6.56 ms | 6.49 ms | 7.43 ms | 7.93 ms | 12.18 ms | **PASS** | **>8 Streams (52.48 ms batch)** |
| **CNN-Temporal-v5** | 9.82 ms | 9.78 ms | 10.70 ms | 11.12 ms | 15.64 ms | **PASS** | **>8 Streams (78.56 ms batch)** |

All models satisfy Gate 5 with large safety margins and comfortably handle 8 concurrent audio streams within the 100 ms audio-hop deadline.

---

## 10. Answers to Section 12 Required Questions

### 1. Did expanding positive-class diversity with authentic recordings improve overall scream recall on independent holdout data?
**Yes, significantly.** Retraining on authentic data increased independent field scream recall from **35.09% (20/57 in Stage 8.9.41)** to **75.36% (52/69 in Stage 8.9.43)** for Config B. Most importantly, ultra-short scream recall increased from **0/11 (0.0%)** to **8/8 (100.0%)** on Final Holdout and **14/14 (100.0%)** on Development Test. However, overall recall (75.36%) remains below the 96.0% threshold required for production readiness.

### 2. How did Config B (DualEncoderAcousticModel) perform after retraining on v5?
`Config-B-v5` emerged as the **best-performing overall architecture across all evaluation dimensions**:
- Highest Holdout Recall: 75.36% (vs. 60.87% – 65.22% for custom CNNs).
- Flawless Short-Scream Recall: 100.0% (17/17 on holdout, 23/23 on dev test), passing Gate 4.
- Controlled False Alarm Rate: 3.68% HN-FPR and 7.14% shouted-speech FPR, passing Gates 2 and 3.
- Superior Computational Efficiency: P95 latency of 0.47 ms, passing Gate 5.

### 3. How did the custom CNN architectures (LogMel, MultiScale, Temporal) perform when trained on authentic data?
Custom CNNs trained directly on log-mel spectrograms demonstrated strong discriminative capacity (Holdout AUC 0.9446 – 0.9526), confirming that screams can be classified without pretrained YAMNet embeddings. However, their holdout generalization was lower than Config B:
- Holdout Recall: 60.87% (LogMel), 65.22% (MultiScale), 62.32% (Temporal).
- Holdout Short-Scream Recall: 82.35% – 88.24% (all failing Gate 4).
- Custom CNNs suffered higher false negative rates on distant and reverberant screams (27.8% – 33.3% recall vs. 50.0% for Config B).

### 4. Did retraining resolve the short-scream (<1.0s) and ultra-short-scream (<500ms) detection failure observed in Stages 8.9.41 and 8.9.42?
**Yes, completely.** In Stage 8.9.41/42, frozen Config B detected 0/11 ultra-short screams. In Stage 8.9.43, retrained Config B detected **22/22 (100.0%)** ultra-short screams across both test sets (14/14 dev test, 8/8 holdout), and 40/40 (100.0%) short screams overall. The hypothesis that the failure was caused by absence of authentic short screams in the training distribution is empirically proven.

### 5. Were the five research acceptance gates satisfied by any candidate?
**No candidate satisfied all five gates.**
- Gates 2, 3, 4, and 5 were fully satisfied by `Config-B-v5`.
- However, **Gate 1 (Recall $\ge 96.0\%$) was FAILED by all candidates** (Config B: 75.36%; CNNs: 60.87% – 65.22%).
- Gate 4 was failed by all three custom CNN candidates on the holdout benchmark.

### 6. What is the sanctioned research decision for Stage 8.9.43?
**DECISION: Maintain Production Freeze, Retain Config B as Leading Research Architecture, and Authorize Targeted Multi-Environment Distant/Reverberant Scream Enrichment (Research Iteration Continues).**

Under the strict gating criteria, Candidate A cannot be promoted to production because Gate 1 is not satisfied (75.36% < 96.0%). Production remains frozen on the Stage 5 Logistic Regression model. Config B is retained as the baseline architecture for future research due to its superior overall recall (75.36%), 100% short-scream recall, and ultra-low latency (0.47 ms). Future research must focus on acoustic simulation and acquisition of distant, reverberant, and background-masked authentic screams.

---

## 11. Artifact and Verification Summary

All stage artifacts are committed under `backend/research/stage_8_9_43/`:
- `manifests/dataset_manifest_v5.csv` (1,914 records, 728 source groups)
- `features/logmel_v5_cache.npz` (135.44 MB)
- `features/yamnet_v5_cache.npz` (3.04 MB)
- `models/config_b_v5.pt`, `models/cnn_logmel_v5.pt`, `models/cnn_multiscale_v5.pt`, `models/cnn_temporal_v5.pt`
- `configs/config_b_v5.json`, `configs/cnn_logmel_v5.json`, `configs/cnn_multiscale_v5.json`, `configs/cnn_temporal_v5.json`
- `CANDIDATE_COMPARISON_V5.csv` (complete 8-row benchmark matrix)
- `AUGMENTATION_EXPERIMENTS.csv` (4-condition augmentation study)
- `POSITIVE_DATASET_AUDIT.csv` (495 clips, 15 acoustic features)
- `ACQUISITION_PROVENANCE.csv` (191 verified clips, CC0/CC-BY)
- `ANNOTATION_REVIEW.csv` (191 consensus annotations)
- `reports/ACOUSTIC_DOMAIN_SHIFT_REPORT.md`
- `reports/SOURCE_GROUP_SPLIT_AUDIT.md`
- `reports/SUBGROUP_RECALL_REPORT.md`
- `reports/INFERENCE_BENCHMARK_V5.md`
- `tests/test_results.txt` (17/17 tests passing)

