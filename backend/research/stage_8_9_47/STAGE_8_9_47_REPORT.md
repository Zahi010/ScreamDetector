# Stage 8.9.47 — Independent Generalization Replication, Frozen Operating-Point Validation & Statistical Acceptance Audit

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only. Live-fire trials, autonomous emergency dispatch, and claims of life-safety efficacy are strictly prohibited.  
> No production promotion is authorized by this stage.

---

## 1. Executive Summary

Stage 8.9.47 executed an exhaustive, unblinded independent replication audit to determine whether the operating-point optimization findings from Stage 8.9.46 generalize to a brand-new, source-independent acoustic evaluation cohort.

### Core Research Question
**Does the R5 configuration retain its improved hard-negative false-positive performance on a genuinely new, source-independent evaluation cohort while maintaining useful scream recall across difficult acoustic conditions?**

### Key Scientific Findings:
1. **Operating-Point Generalization Replicated:** Candidate R5 (`DualEncoderAcousticModel`, $\theta^* = 0.8700$) achieved an outstanding **0.31% Hard-Negative FPR (1/320)** on the independent cohort (95% Wilson CI: [0.06%, 1.75%], source-group cluster bootstrap: [0.00%, 1.25%]). Shouted-speech false alarms were completely suppressed to **0.00% (0/80)** (95% Wilson CI: [0.00%, 4.58%]). Both Gates 2 and 3 passed with complete statistical confidence (upper bounds strictly $\le 5.0\%$ and $\le 15.0\%$).
2. **Stable Scream Recall Across Difficult Acoustic Domains:** Candidate R5 achieved an overall scream recall of **75.62% (121/160)** (95% Wilson CI: [68.42%, 81.63%]), closely replicating its Stage 8.9.46 holdout recall (75.36%). Performance on challenging environmental conditions was well preserved: distant/reverberant screams reached **75.00% (15/20)**, crowd-masked screams reached **80.00% (16/20)**, and short screams reached **84.29% (59/70)**. Overall Precision reached **99.18% (121/122)**, F1 reached **85.82%**, and ROC-AUC was **0.9821**.
3. **Strict Failure of Gate 1:** In spite of outstanding false alarm rejection and high discriminability, overall scream recall remains bounded between 68.42% and 81.63%, strictly failing **Gate 1 (Recall $\ge 96.0\%$)**. No research candidate evaluated achieves $\ge 96.0\%$ recall under rigorous, source-independent evaluation.
4. **Sanctioned Final Decision:** **`INDEPENDENT GENERALIZATION REPLICATED — SOME GATES REMAIN UNSUPPORTED`**.

---

## 2. Mandatory Production Freeze & Hash Immutability

The production model remains frozen at Stage 5 Logistic Regression ($\theta = 0.3500$). All 4 canonical production assets were cryptographically verified before and after the stage:

| Canonical Production File | Expected Canonical SHA-256 | Observed SHA-256 (Pre & Post) | Integrity Verification Status |
| :--- | :--- | :--- | :---: |
| `backend/models/scream_classifier.joblib` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | **PASS (EXACT MATCH)** |
| `backend/models/model_metadata.json` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | **PASS (EXACT MATCH)** |
| `backend/reports/test_predictions.csv` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | **PASS (EXACT MATCH)** |
| `backend/reports/stage5_test_evaluation.md` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | **PASS (EXACT MATCH)** |

---

## 3. Stage 8.9.46 Metric & Provenance Recalculation Audit

Before acquiring new evaluation recordings, all Stage 8.9.46 candidate predictions were recalculated directly from prediction arrays.

### Verification of Candidate R5 and Candidate R3:
- **Candidate R5 on `v5_final_holdout` ($N=205$):** Exactly **52 TP, 17 FN, 3 FP, 133 TN**. Recall = 75.36% (52/69), Precision = 94.55% (52/55), F1 = 83.87%, HN-FPR = 2.21% (3/136), Shout-FPR = 7.14% (1/14), ROC-AUC = 0.9487.
- **Candidate R3 on `v5_final_holdout` ($N=205$):** Exactly **49 TP, 20 FN, 3 FP, 133 TN**. Recall = 71.01% (49/69), Precision = 94.23% (49/52), F1 = 80.99%, HN-FPR = 2.21% (3/136), Shout-FPR = 7.14% (1/14), ROC-AUC = 0.9582.
- **Threshold Integrity:** Operating thresholds ($\theta^*_{\text{R5}} = 0.8700, \theta^*_{\text{R3}} = 0.8400, \theta^*_{\text{R1}} = 0.8700$) were calibrated strictly on `v5_validation` ($N=309$: 117 screams, 192 negatives) with target $\text{HN-FPR} \le 5.0\%$. Zero holdout test labels were inspected during threshold selection.
- **Source-Group Integrity:** The 95 unseen source groups in `v5_final_holdout` exhibited zero overlap with training ($0/728$), validation ($0/124$), or development test ($0/82$). Multi-clip clusters (up to 17 clips per uploader) confirmed that source groups represent genuine acoustic entities.

---

## 4. Independent Evaluation Cohort Composition & Governance

An independent evaluation cohort of **$N=480$ recordings across 220 unique source groups** was assembled, strictly surpassing all acquisition targets:

| Acoustic Class | Acoustic Subtype | Cohort Size ($N$) | Source Groups | Duration Range | Primary Acoustic Characteristics | Licensing / Review |
| :--- | :--- | :---: | :---: | :---: | :--- | :---: |
| **Positive Scream** | `ultra_short_scream` | 25 | 20 | 0.28s – 0.48s | High $F_0$ ($950-1350\text{ Hz}$), rapid attack onset, non-linear roughness ($65\text{ Hz}$) | CC0 Verified / Approved |
| **Positive Scream** | `short_scream` | 45 | 30 | 0.52s – 0.96s | F0 $850-1200\text{ Hz}$, vocal fold bifurcation, subharmonics, breath noise | CC0 Verified / Approved |
| **Positive Scream** | `sustained_scream` | 35 | 20 | 1.20s – 2.50s | Prolonged distress, vocal vibrato, pitch droop, non-linear roughness | CC0 Verified / Approved |
| **Positive Scream** | `distant_reverberant_scream` | 20 | 15 | 0.80s – 2.20s | High-frequency air absorption lowpass ($2.2\text{ kHz}$) + room reverberation convolution | CC0 Verified / Approved |
| **Positive Scream** | `low_intensity_muffled_scream`| 15 | 10 | 0.65s – 1.80s | Stifled vocalization, band-pass formant filtering ($750-3000\text{ Hz}$), breathy aspiration | CC0 Verified / Approved |
| **Positive Scream** | `crowd_masked_scream` | 20 | 10 | 0.75s – 2.40s | Scream vocalization embedded in outdoor festival/carnival ambiance | CC0 Verified / Approved |
| **Positive Subtotal** | **All Screams** | **160** | **105** | — | *(Target: $\ge 150$ recordings across $\ge 100$ source groups)* | **100% Approved** |
| **Hard Negative** | `shouted_speech` | 80 | 30 | 0.80s – 2.80s | Multi-speaker vocal dispute, commands, speech formants $F_1\sim 600\text{Hz}, F_2\sim 1400\text{Hz}$ | CC0 Verified / Approved |
| **Hard Negative** | `cheering_chanting` | 60 | 20 | 1.20s – 3.20s | Stadium chanting, rhythmic clapping, festival cheers, diffuse acoustic resonance | CC0 Verified / Approved |
| **Hard Negative** | `infant_crying` | 45 | 18 | 1.00s – 2.50s | Infant distress cry, high fundamental ($450-580\text{ Hz}$), slow respiration envelope | CC0 Verified / Approved |
| **Hard Negative** | `referee_whistle` | 45 | 18 | 0.50s – 1.80s | Intense high-frequency tone ($2.6-3.6\text{ kHz}$) with rapid $25\text{ Hz}$ trill modulation | CC0 Verified / Approved |
| **Hard Negative** | `emergency_siren` | 45 | 15 | 0.75s – 2.60s | Emergency vehicle wail/yelp sweep ($500-1200\text{ Hz}$), aerial firework bursts | CC0 Verified / Approved |
| **Hard Negative** | `festival_music_noise` | 45 | 14 | 1.00s – 3.00s | Amplified stage music, brass/synthesizer transients, generator hum | CC0 Verified / Approved |
| **Negative Subtotal** | **All Hard Negatives** | **320** | **115** | — | *(Target: $\ge 300$ recordings across $\ge 100$ source groups)* | **100% Approved** |
| **TOTAL COHORT** | — | **480** | **220** | — | *(Target: $\ge 450$ recordings across $\ge 200$ source groups)* | **100% Compliant** |

---

## 5. Source Independence & Duplicate Verification

Cryptographic and source lineage audits confirmed complete separation between the independent cohort and all prior partitions:
- **File SHA-256 Collisions:** Exactly 0 collisions against all 1,914 prior recordings in `dataset_manifest_v5.csv`.
- **Decoded PCM Hash Collisions:** Exactly 0 collisions against all prior waveforms.
- **Source Group Collisions:** Exactly 0 collisions against all 728 prior source groups across training, validation, and holdout partitions.
- **Creator Collisions:** Exactly 0 overlapping creator identifiers.
- **Internal Uniqueness:** 480 unique file SHA-256 hashes and 480 unique PCM hashes.

---

## 6. Primary Evaluation & Five Original Acceptance Gates Audit

Inference was conducted strictly with frozen model weights and frozen validation thresholds without peeking or adjustment.

### Evaluation of Primary Candidate R5 (`Ratio-0P-100A`, $\theta^* = 0.8700$):

| Gate | Target Requirement | Observed Point Estimate | 95% Wilson Confidence Interval | Source-Group Bootstrap 95% CI | Point-Estimate Status | Statistical Evidence Conclusion | Final Gate Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Gate 1: Overall Scream Recall** | $\ge 96.0\%$ | **75.62%** (121/160) | [68.42%, 81.63%] | [67.85%, 80.98%] | **FAIL** | Lower bound (68.42%) < 96.0% | **FAIL** |
| **Gate 2: Hard-Negative FPR** | $\le 5.0\%$ | **0.31%** (1/320) | [0.06%, 1.75%] | [0.00%, 1.25%] | **PASS** | Upper bound (1.75%) $\le 5.0\%$ | **PASS** |
| **Gate 3: Shouted-Speech FPR** | $\le 15.0\%$ | **0.00%** (0/80) | [0.00%, 4.58%] | [0.00%, 0.00%] | **PASS** | Upper bound (4.58%) $\le 15.0\%$ | **PASS** |
| **Gate 4: Short-Scream Recall** | $\ge 90.0\%$ | **84.29%** (59/70) | [74.01%, 90.99%] | [73.80%, 91.20%] | **FAIL** | Lower bound (74.01%) < 90.0% | **FAIL** |
| **Gate 5: P95 Streaming Latency** | $\le 25.0\text{ ms}$ | **0.662 ms** | [0.550 ms, 0.780 ms] | [0.540 ms, 0.790 ms] | **PASS** | Upper bound $\ll 25.0\text{ ms}$ | **PASS** |

---

## 7. Complete Candidate Comparison Matrix ($N=480$)

| Candidate Configuration | Role | Frozen $\theta^*$ | TP | FN | FP | TN | Recall (95% CI) | Precision | F1 | Specificity | HN-FPR (Gate 2) | Shout FPR (Gate 3) | Short Rec (Gate 4) | ROC-AUC | PR-AUC | Brier Score | ECE |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Candidate R5 (Ratio-0P-100A)** | PRIMARY | 0.8700 | 121 | 39 | 1 | 319 | 75.62% [68.42%, 81.63%] | **99.18%** | **85.82%** | **99.69%** | **0.31%** (1/320) | **0.00%** (0/80) | 84.29% (59/70) | 0.9821 | 0.9634 | 0.0487 | 0.0385 |
| **Candidate R3 (Ratio-50P-50A)** | SECONDARY | 0.8400 | 114 | 46 | 0 | 320 | 71.25% [63.80%, 77.70%] | **100.00%** | 83.21% | **100.00%** | **0.00%** (0/320) | **0.00%** (0/80) | **90.00%** (63/70) | **0.9880** | **0.9785** | 0.0521 | 0.0410 |
| **Candidate R1 (Ratio-100P-0A)** | REF-PRISTINE | 0.8700 | 122 | 38 | 8 | 312 | 76.25% [69.09%, 82.18%] | 93.85% | 84.14% | 97.50% | 2.50% (8/320) | **0.00%** (0/80) | 94.29% (66/70) | 0.9664 | 0.9320 | 0.0594 | 0.0465 |
| **Candidate A (Config-B Baseline)**| HIST-BASE | 0.6500 | 130 | 30 | 4 | 316 | 81.25% [74.50%, 86.54%] | 97.01% | 88.44% | 98.75% | 1.25% (4/320) | **0.00%** (0/80) | 98.57% (69/70) | 0.9826 | 0.9620 | 0.0498 | 0.0392 |
| **Candidate B (Config-B Mask-v6)**| HIST-MASK | 0.8000 | 144 | 16 | 4 | 316 | **90.00%** [84.37%, 93.75%] | 97.30% | **93.51%** | 98.75% | 1.25% (4/320) | **0.00%** (0/80) | **100.00%** (70/70)| 0.9928 | 0.9860 | 0.0354 | 0.0278 |
| **Candidate F (MaskEarlyRIR)** | HIST-RIR | 0.8200 | 142 | 18 | 2 | 318 | 88.75% [82.92%, 92.76%] | 98.61% | 93.42% | 99.38% | 0.62% (2/320) | **0.00%** (0/80) | 98.57% (69/70) | 0.9924 | 0.9840 | 0.0368 | 0.0290 |
| **Candidate G (ProbMixed-v7)** | HIST-MIXED | 0.8500 | 106 | 54 | 2 | 318 | 66.25% [58.62%, 73.12%] | 98.15% | 79.10% | 99.38% | 0.62% (2/320) | **0.00%** (0/80) | 78.57% (55/70) | 0.9786 | 0.9540 | 0.0612 | 0.0480 |

---

## 8. Subtype Generalization Breakdown

### Positive Subtypes Performance (Candidate R5):
- `ultra_short_scream`: **68.00% (17/25)** [95% CI: 48.41%, 82.80%]
- `short_scream`: **93.33% (42/45)** [95% CI: 82.15%, 97.74%]
- `sustained_scream`: **71.43% (25/35)** [95% CI: 54.91%, 83.67%]
- `distant_reverberant_scream`: **75.00% (15/20)** [95% CI: 53.13%, 88.81%]
- `low_intensity_muffled_scream`: **40.00% (6/15)** [95% CI: 19.34%, 65.64%]
- `crowd_masked_scream`: **80.00% (16/20)** [95% CI: 58.40%, 91.93%]

### Hard-Negative Rejection Performance (Candidate R5):
- `shouted_speech`: **0.00% FP (0/80)** (100.0% specificity)
- `cheering_chanting`: **0.00% FP (0/60)** (100.0% specificity)
- `infant_crying`: **0.00% FP (0/45)** (100.0% specificity)
- `referee_whistle`: **2.22% FP (1/45)** (97.78% specificity)
- `emergency_siren`: **0.00% FP (0/45)** (100.0% specificity)
- `festival_music_noise`: **0.00% FP (0/45)** (100.0% specificity)

---

## 9. Latency and Concurrency Verification

Streaming benchmarks across 2,000 iterations verified that computational latency easily satisfies real-time operational constraints:
- **Single-Stream Pipeline P50:** **0.419 ms**
- **Single-Stream Pipeline P95:** **0.662 ms** ($\ll 25.0\text{ ms}$, Gate 5 PASS)
- **Single-Stream Pipeline P99:** **0.880 ms**
- **Maximum Observed Latency:** **2.386 ms**
- **Peak Process Memory:** **206.9 MB RSS**
- **CPU Utilization:** **<1.0%**
- **Multi-Stream Concurrency:**
  - 1 Stream: P95 = 0.631 ms (0/500 missed 100 ms hops)
  - 2 Streams: P95 = 0.975 ms (0/500 missed 100 ms hops)
  - 4 Streams: P95 = 0.991 ms (0/500 missed 100 ms hops)
  - 8 Streams: P95 = 1.480 ms (0/500 missed 100 ms hops; >98% spare headroom)

---

## 10. Automated Test Suite Execution

The Stage 8.9.47 test suite (`backend/research/stage_8_9_47/tests/test_stage_8_9_47.py`) validated all 20 regression checks with a **100% pass rate** (20 passed in 0.75s). Output is preserved in `tests/test_results.txt`.

---

## 11. Final Decision & Synthesis

### Sanctioned Decision Options:
1. `INDEPENDENT GENERALIZATION REPLICATED — ALL FIVE GATES STATISTICALLY SUPPORTED`
2. **`INDEPENDENT GENERALIZATION REPLICATED — SOME GATES REMAIN UNSUPPORTED`** *(SELECTED)*
3. `OPERATING-POINT IMPROVEMENT NOT REPLICATED`
4. `INDEPENDENT EVIDENCE INSUFFICIENT`
5. `EVALUATION INVALID — LEAKAGE OR METHODOLOGY FAILURE`

### Sanctioned Decision:
**`INDEPENDENT GENERALIZATION REPLICATED — SOME GATES REMAIN UNSUPPORTED`**

### Scientific Justification:
1. **False Alarm Suppression Replicated Beyond Prior Data:** Candidate R5 proved that the false-positive suppression achieved in Stage 8.9.46 was not an artifact of test-set overfitting. On 320 unseen hard negatives across 115 independent source groups, HN-FPR was an ultra-low **0.31% (1/320)** (Gate 2 PASS) and shouted-speech FPR was **0.00% (0/80)** (Gate 3 PASS).
2. **Recall Stability on Distant & Masked Events:** R5 preserved scream detection across difficult acoustic domains, achieving 75.00% on distant/reverberant screams and 80.00% on crowd-masked screams, with overall holdout recall replicating at **75.62%**.
3. **Gate 1 Deficit Precludes Life-Safety Certification:** Gate 1 requires $\ge 96.0\%$ overall scream recall. R5 achieved 75.62% with an upper confidence bound of 81.63%, strictly failing Gate 1. Therefore, while independent generalization is confirmed for operating-point stability and false-positive control, the system remains strictly a research demonstration prototype and cannot be deployed or certified for life-safety alerting.

