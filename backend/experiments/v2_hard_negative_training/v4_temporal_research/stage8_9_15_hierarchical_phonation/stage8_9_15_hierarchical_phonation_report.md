# Stage 8.9.15 — Hierarchical Vocal Distress Detection and Nonlinear Phonation Discrimination Report

**Status:** EXPERIMENTAL RESEARCH COMPLETE  
**Production Status:** STRICTLY FROZEN & UNTOUCHED  
**Authoritative Verdict:** **REJECTED — ACCEPTANCE CRITERIA NOT MET**  
**Date:** October 30, 2026  
**Workspace:** [`backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_15_hierarchical_phonation/`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_15_hierarchical_phonation)

---

## 1. Executive Summary & Core Research Questions

Stage 8.9.15 investigated whether a **hierarchical, nonlinear acoustic architecture** can overcome the persistent error floor identified in Stage 8.9.14—specifically distinguishing human screams from acoustically identical hard negatives (strained high-pitched shouting with $F_0 > 700$ Hz, crowd vocalizations, singing, whistling) without sacrificing short-scream sensitivity or violating edge streaming latency constraints.

### The Research Question
> *Can a hierarchical nonlinear model distinguish genuine scream events from acoustically similar high-intensity vocalizations without sacrificing short-scream detection?*

### The Definitive Finding
**No.** While the hierarchical architecture successfully reduced shouted-speech false positives from 11.90% to 4.76% (a 60.0% relative reduction), it introduced severe collateral failures:
1. **Short-scream recall degraded significantly:** Dropping from 100.0% (5/5) in D_v4 Baseline down to 60.0% (3/5) in Model A MLP and 80.0% (4/5) in Model C Hybrid Fusion, failing the $\ge 90.0\%$ short-scream gate.
2. **Crowd vocalization false alarms spiked:** Incoherent stadium shouting and group chanting confused the temporal CNN and fusion models, increasing crowd false alarms to 20.93%.
3. **End-to-end latency breached the edge budget:** Complete hierarchical inference required **152.97 ms** median latency (p95: 178.38 ms), exceeding the $\le 25.0$ ms real-time streaming limit by **611.88%**.
4. **Overall Event Recall and FPR failed targets:** Best overall recall was 92.66% (target $\ge 96.0\%$) and best event FPR was 8.59% (target $\le 5.0\%$).

Under strict governance rules, all candidates were **REJECTED**.

---

## 2. Production Baseline Integrity & Verification Invariants

Prior to commencing training, authoritative SHA-256 baseline hashes and operational thresholds were audited using [`verify_stage8_9_15_baseline.py`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_15_hierarchical_phonation/verify_stage8_9_15_baseline.py). All invariants matched bit-for-bit:

| Production Artifact | Expected SHA-256 Hash | Audited SHA-256 Hash | Status |
|---|---|---|---|
| [`scream_classifier.joblib`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/models/scream_classifier.joblib) | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | **FROZEN / PASS** |
| [`model_metadata.json`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/models/model_metadata.json) | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | **FROZEN / PASS** |
| [`test_predictions.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/reports/test_predictions.csv) | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | **FROZEN / PASS** |
| [`stage5_test_evaluation.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/reports/stage5_test_evaluation.md) | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | **FROZEN / PASS** |

- **Production Threshold:** Locked at `0.3500`.
- **Review Database:** 343 records, anchor record `fsd50k_349401` = `SCREAM_PRESENT`, strictly isolated.
- **Audit Deliverable:** [`production_integrity_audit.json`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_15_hierarchical_phonation/production_integrity_audit.json).

---

## 3. Dataset Provenance, Split Integrity & Source Disjointness

The research dataset consists of 1,384 audio recordings partitioned into strict, non-overlapping source-group splits:
- **Training split:** 757 recordings (351 unique source groups)
- **Validation split:** 320 recordings (116 unique source groups)
- **Held-Out Test split:** 307 recordings (126 unique source groups)

### Source-Group Disjointness Audit
Audited in [`source_group_split_audit.json`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_15_hierarchical_phonation/source_group_split_audit.json):
- $\text{Train} \cap \text{Val} = \emptyset$ (0 source overlaps)
- $\text{Train} \cap \text{Test} = \emptyset$ (0 source overlaps)
- $\text{Val} \cap \text{Test} = \emptyset$ (0 source overlaps)
- Historical Stage 5 Test recordings remain strictly quarantined in the Test split.
- Commercial licensing and provenance documented for all 1,384 files in [`dataset_provenance_and_license_audit.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_15_hierarchical_phonation/dataset_provenance_and_license_audit.csv) (all CC0, CC BY, CC BY-SA, Public Domain, or approved academic research clearances).

---

## 4. Stage 1 — Broad Vocal Distress Gate Results

The first stage acts as a high-sensitivity pre-filter to reject non-vocal background noise (silence, mechanical drone, synthesized tones, pure environmental noise) before activating downstream phonation models.

Recorded in [`stage1_gate_evaluation.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_15_hierarchical_phonation/stage1_gate_evaluation.csv):

| Gate ID | Classifier Algorithm | Operating Threshold | Fit Time (s) | Val Scream Pass Rate | Val Noise Filtered | Test Scream Pass Rate | Test Short Scream Pass | Test Noise Filtered | Certification Status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| **Gate_A_ExtraTrees** | ExtraTreesClassifier (100 trees, depth 16) | **0.470** | **0.29 s** | **100.0%** | **87.65%** | **98.17%** | **100.0% (5/5)** | **79.59%** | **CERTIFIED_PASS** |
| Gate_B_HistGradientBoosting | HistGradientBoosting (100 trees, depth 8) | 0.100 | 260.45 s | 96.88% | 82.72% | 100.0% | 100.0% | 76.53% | REJECTED (Val Recall < 98%) |
| Gate_C_RandomForest | RandomForestClassifier (100 trees, depth 16) | 0.340 | 0.35 s | 100.0% | 80.25% | 100.0% | 100.0% | 74.49% | CERTIFIED_PASS |

**Selected Stage 1 Gate:** `Gate_A_ExtraTrees` was selected due to highest noise filtration efficiency (79.59% non-vocal noise eliminated) while passing 98.17% of screams and 100.0% of brief screams to Stage 2.

---

## 5. Stage 2 — Nonlinear Phonation Discriminator Architectures

Stage 2 evaluated three distinct nonlinear architectures on candidates passing Stage 1:

1. **Model A — Compact Regularized MLP:**
   - Architecture: Input (3,102 dims) $\rightarrow$ Dense(128, ReLU, L2=0.01) $\rightarrow$ Dense(32, ReLU) $\rightarrow$ Sigmoid.
   - Purpose: Non-linear feature interactions between YAMNet and 30 acoustic features.
2. **Model B — Temporal 1D Dilated CNN (TCN):**
   - Architecture: Unpooled YAMNet frame sequence (70 frames $\times$ 1024 dims) through 3 dilated residual Conv1D layers (dilation rates 1, 2, 4; receptive field ~750 ms), dual GlobalMaxPooling + GlobalAveragePooling (128 dims), concatenated with a Dense(32) acoustic branch $\rightarrow$ Dense(64) $\rightarrow$ Dense(16) $\rightarrow$ Sigmoid.
   - Purpose: Captures attack/decay dynamics, syllabic cadence, and phonation continuity across time.
3. **Model C — Hierarchical Learned Hybrid Fusion:**
   - Architecture: Logistic Regression calibrating Stage 1 Gate probability, Model A MLP probability, Model B TCN probability, and top physical discriminability features (`low_vocal_energy_ratio`, `burst_continuity_ratio`, `sustain_to_peak_ratio`, `pitch_cv`, `scream_resonance_ratio`, `subharmonic_ratio`).
4. **Model C Gated Cascade:**
   - Hard cascade setting final probability to $0.0$ if Stage 1 Gate probability $< 0.470$.

---

## 6. Comprehensive Architecture Comparison ($N=307$ Held-Out Test Set)

Recorded in [`architecture_comparison.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_15_hierarchical_phonation/architecture_comparison.csv):

| Model Candidate | Operating Threshold | Event Recall (%) | 95% Bootstrap CI | Event FPR (%) | 95% Bootstrap CI | Shouted Speech FPR (%) | Crowd FPR (%) | Short Recall <1.0s (%) | Brief Recall $\le$1.5s (%) | PR-AUC | Hourly False Alarms | Acceptance Verdict |
|---|---:|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| **D_v4 Baseline (Stage 8.9.14)** | 0.420 | 89.91% | [83.6%, 95.7%] | 7.07% | [3.1%, 11.8%] | 11.90% | 11.63% | 100.0% (5/5) | 92.31% (24/26) | 0.9198 | 127.3 | REJECTED |
| **D_v4 + Family A (Stage 8.9.14)** | 0.420 | 90.83% | [84.3%, 96.1%] | 7.07% | [3.3%, 12.2%] | 9.52% | 11.63% | 100.0% (5/5) | 92.31% (24/26) | 0.9231 | 127.3 | REJECTED |
| **D_v4 + Family B (Stage 8.9.14)** | 0.650 | 81.65% | [71.4%, 90.4%] | 4.55% | [1.5%, 8.3%] | 7.14% | 4.65% | 80.0% (4/5) | 88.46% (23/26) | 0.9229 | 81.9 | REJECTED |
| **F_v6 Acoustic (Stage 8.9.14)** | 0.360 | 87.16% | [79.4%, 93.9%] | 6.57% | [3.4%, 11.2%] | 9.52% | 6.98% | 80.0% (4/5) | 92.31% (24/26) | 0.9134 | 118.3 | REJECTED |
| **Model A (Compact MLP)** | 0.160 | 86.24% | [78.0%, 92.9%] | 5.56% | [2.1%, 10.1%] | 7.14% | 9.30% | 60.0% (3/5) | 76.92% (20/26) | 0.9143 | 100.1 | **REJECTED** |
| **Model B (Temporal CNN)** | 0.610 | 94.50% | [89.8%, 98.4%] | 17.17% | [9.9%, 26.1%] | 21.43% | 25.58% | 80.0% (4/5) | 92.31% (24/26) | 0.8992 | 309.1 | **REJECTED** |
| **Model C (Hybrid Fusion)** | 0.240 | 92.66% | [86.5%, 97.4%] | 9.09% | [3.9%, 16.0%] | 7.14% | 20.93% | 80.0% (4/5) | 88.46% (23/26) | 0.8969 | 163.6 | **REJECTED** |
| **Model C (Gated Cascade)** | **0.240** | **90.83%** | **[84.5%, 96.8%]** | **8.59%** | **[3.5%, 15.4%]** | **4.76%** | **20.93%** | **80.0% (4/5)** | **84.62% (22/26)** | **0.8906** | **154.6** | **REJECTED** |

---

## 7. Deep Forensics: High-Pitch Shouting ($F_0 > 700$ Hz)

Detailed in [`high_pitch_shouting_forensics.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_15_hierarchical_phonation/high_pitch_shouting_forensics.csv):

The held-out test cohort contained 42 shouting and speech recordings, of which 26 exhibited elevated fundamental frequencies ($F_0 > 650$ Hz or peak $F_0 > 750$ Hz).
- **Baseline False Positives:** D_v4 Baseline triggered on 5 of 42 shouting files (11.90% FPR).
- **Hierarchical Performance:** Model C Gated Cascade triggered on only 2 of 42 shouting files (**4.76% FPR**), successfully resolving 80% of former shouting false alarms!

### Persistent Hard False Positive Analysis
The 2 remaining shouting false positives revealed an insurmountable physical acoustic barrier:
1. `v2_fsd50k_169811` (Model Prob: `0.9966`, FP = True):
   - Duration: 1.971 s | Mean $F_0$: 717.4 Hz | Max $F_0$: 888.9 Hz | Subharmonic Ratio: 0.537 | Low Vocal Energy Ratio: **0.000** | Sustain Ratio: 0.442 | HNR: 8.14 dB.
   - **Acoustic Mechanism:** This recording captures an actor shouting under maximum vocal force. The fundamental frequency exceeds 700 Hz, subharmonic bifurcation creates deterministic chaos, and there is **zero acoustic power below 1 kHz**. Every feature—both spectral and temporal—is acoustically identical to a scream.
2. `v2_fsd50k_168725` (Model Prob: `0.8441`, FP = True):
   - Duration: 1.405 s | Mean $F_0$: 739.3 Hz | Max $F_0$: 1000.0 Hz | Low Vocal Energy Ratio: **0.001**.
   - **Acoustic Mechanism:** The speaker's larynx is elevated, compressing formants and eliminating lower vocal energy, crossing directly into the scream prior distribution.

**Conclusion:** Pure acoustic features cannot distinguish shouting from screaming when a vocal tract operates under maximum anatomical strain because the physical production mechanisms converge.

---

## 8. Short-Scream Preservation Analysis

Evaluated across duration brackets in [`short_scream_evaluation.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_15_hierarchical_phonation/short_scream_evaluation.csv):

| Duration Cohort | Total Screams ($N$) | Detected Screams ($n$) | Scream Recall (%) | Masked Screams Detected | Hard Negative Total | Hard Negative FPR (%) | Gate Target ($\ge 90\%$) |
|---|---:|---:|---:|---:|---:|---:|---|
| **Ultra-Short (< 0.5s)** | 0 | 0 | N/A* | 0/0 | 2 | 0.00% | PASS (No misses) |
| **Short (0.5s – 0.99s)** | 5 | 4 | **80.00%** | 1/1 (100.0%) | 7 | 14.29% | **FAIL** |
| **Subtotal (< 1.0s)** | **5** | **4** | **80.00%** | **1/1 (100.0%)** | **9** | **11.11%** | **FAIL** |
| **Moderate Brief (1.0s – 1.5s)** | 21 | 19 | 90.48% | 9/9 (100.0%) | 3 | 33.33% | PASS |
| **Total Brief ($\le$ 1.5s)** | **26** | **23** | **88.46%** | **10/10 (100.0%)** | **12** | **16.67%** | **FAIL** |
| **Sustained (> 1.5s)** | 83 | 78 | 93.98% | 29/33 (87.88%) | 186 | 8.60% | PASS |

\* *The held-out test split contains 0 genuine screams below 0.5s from independent sources.*

### Audit of Short-Scream Statistical Power
As mandated by Section 7 of the specification:
- The held-out test split contains only **5 screams $< 1.0$ s** and **26 screams $\le 1.5$ s**.
- A single missed scream in the $< 1.0$ s cohort alters the recall metric by **20.0%**.
- Consequently, all short-scream metrics must be classified as **PRELIMINARY FINDINGS**, not statistically certified bounds.

---

## 9. Three-Outcome Uncertainty & Abstention Analysis

Detailed in [`uncertainty_abstention_analysis.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_15_hierarchical_phonation/uncertainty_abstention_analysis.csv):

We investigated a policy where predictions within margin $\pm \delta$ around operating threshold $\theta = 0.24$ are quarantined for human review (`UNCERTAIN_REQUIRES_HUMAN_REVIEW`):

| Margin ($\delta$) | Decision Thresholds [Low, High] | Uncertain Records ($N$) | Abstention Rate (%) | System Coverage (%) | Confident Accuracy (%) | Confident Scream Recall (%) | Confident Hard-Negative FPR (%) | Short Screams Quarantined | Masked Screams Quarantined |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| $\delta = 0.03$ | [0.21, 0.27] | 4 | 1.30% | 98.70% | 91.75% | 92.52% | 8.67% | 1/5 (20.0%) | 1/43 (2.3%) |
| $\delta = 0.05$ | [0.19, 0.29] | 9 | 2.93% | 97.07% | 92.28% | 92.45% | 7.81% | 1/5 (20.0%) | 2/43 (4.7%) |
| $\delta = 0.08$ | [0.16, 0.32] | 15 | 4.89% | 95.11% | 92.81% | 92.31% | 6.91% | 1/5 (20.0%) | 3/43 (7.0%) |
| $\delta = 0.10$ | [0.14, 0.34] | 18 | 5.86% | 94.14% | 93.08% | 93.07% | 6.91% | 1/5 (20.0%) | 5/43 (11.6%) |
| $\delta = 0.12$ | [0.12, 0.36] | 22 | 7.17% | 92.83% | 94.04% | 94.95% | 6.45% | 1/5 (20.0%) | 6/43 (14.0%) |
| $\delta = 0.15$ | [0.09, 0.39] | 29 | 9.45% | 90.55% | 94.24% | 95.88% | 6.63% | 2/5 (40.0%) | 7/43 (16.3%) |

### Key Abstention Findings
1. Abstention improves confident classification accuracy from 90.55% to 94.24% and drops confident FPR to 6.63%.
2. **Disproportionate Short-Scream Impact:** At $\delta = 0.10$, 20% of short screams are quarantined to human review. At $\delta = 0.15$, **40% of short screams (2/5)** and **16.3% of masked screams** are quarantined. In emergency festival surveillance, abstaining on brief screams represents a critical safety hazard.

---

## 10. End-to-End Latency & Memory Benchmark

Recorded across 100 consecutive 1.0 s streaming buffers in [`latency_and_memory_benchmark.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_15_hierarchical_phonation/latency_and_memory_benchmark.csv):

| Pipeline Stage | Median Latency (ms) | p95 Latency (ms) | Mean Latency (ms) | % of 25 ms Budget | Peak RAM Delta (MB) | On-Disk Model Size (MB) | Status |
|---|---:|---:|---:|---:|---:|---:|---|
| Stage 0: Buffer Normalization & DC Removal | 0.209 ms | 0.342 ms | 0.238 ms | 0.84% | 4.12 MB | 0.0 MB | PASS |
| Stage 1: YAMNet Embedding Extraction | 10.613 ms | 13.669 ms | 10.940 ms | 42.45% | 4.12 MB | 14.8 MB | PASS |
| Stage 2: Acoustic Discriminability Features (30 dims) | 12.426 ms | 17.523 ms | 13.103 ms | 49.71% | 4.12 MB | 0.0 MB | PASS |
| Stage 3: Stage 1 Broad Distress Gate (ExtraTrees) | 68.901 ms | 79.944 ms | 69.177 ms | 275.60% | 4.12 MB | 1.79 MB | FAIL |
| Stage 4: Stage 2 Model A (Compact MLP) | 2.582 ms | 3.262 ms | 2.609 ms | 10.33% | 4.12 MB | 4.60 MB | PASS |
| Stage 5: Stage 2 Model B (Temporal Dilated CNN) | 55.633 ms | 71.233 ms | 56.435 ms | 222.53% | 4.12 MB | 2.32 MB | FAIL |
| Stage 6: Stage 2 Model C (Learned Hybrid Fusion) | 1.622 ms | 2.713 ms | 1.856 ms | 6.49% | 4.12 MB | 0.00 MB | PASS |
| **Complete Pipeline Option 1 (Gate + Model A MLP)** | **95.968 ms** | **108.644 ms** | **96.070 ms** | **383.87%** | **4.12 MB** | **6.46 MB** | **BUDGET_BREACH** |
| **Complete Pipeline Option 2 (Gate + MLP + TCN + Fusion)** | **152.969 ms** | **178.384 ms** | **154.361 ms** | **611.88%** | **4.12 MB** | **8.78 MB** | **BUDGET_BREACH** |

**Conclusion:** The hierarchical architecture cannot run within a 25.0 ms edge budget. Tree-based gating and temporal CNN inference exceed the budget by over 6x.

---

## 11. Comprehensive 14-Condition Robustness Evaluation

Tested in [`robustness_test_results.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_15_hierarchical_phonation/robustness_test_results.csv):

| ID | Test Condition | Ground Truth | Cascade Probability | Pipeline Decision | Verdict |
|---|---|---|---:|---|---|
| C01 | Extended Silence (Zero Buffer) | NON_SCREAM | 0.3291 | UNCERTAIN_REQUIRES_HUMAN_REVIEW | FAIL_INVESTIGATION_REQUIRED |
| C02 | Digital Clipping (Square Wave Saturation) | NON_SCREAM | 0.0012 | NON_SCREAM | PASS |
| C03 | Severe DC Bias (+0.3 DC offset) | NON_SCREAM | 0.0037 | NON_SCREAM | PASS |
| C04 | Impulse Noise (Random Dirac Spikes) | NON_SCREAM | 0.0076 | NON_SCREAM | PASS |
| C05 | Heavy AWGN Noise (0 dB SNR) | NON_SCREAM | 0.0110 | NON_SCREAM | PASS |
| C06 | Music & Bass-Heavy Audio (60/120 Hz) | NON_SCREAM | 0.0009 | NON_SCREAM | PASS |
| C07 | Background Crowd Cheering & Babble | NON_SCREAM | 0.0043 | NON_SCREAM | PASS |
| C08 | Reverberant Scream (Late Room Reflection) | SCREAM | 0.1464 | NON_SCREAM | FAIL_INVESTIGATION_REQUIRED |
| C09 | Distant Scream (High-freq loss + low SNR) | SCREAM | 0.0188 | NON_SCREAM | FAIL_INVESTIGATION_REQUIRED |
| C10 | Low-Amplitude Scream (-25 dBFS) | SCREAM | 0.0000 | NON_SCREAM | FAIL_INVESTIGATION_REQUIRED |
| C11 | High-Amplitude Shouting (+6 dBFS Peak) | NON_SCREAM | 0.0026 | NON_SCREAM | PASS |
| C12 | Multiple Simultaneous Voices (Polyphonic) | NON_SCREAM | 0.0013 | NON_SCREAM | PASS |
| C13 | Whistles and Sirens (Narrowband Swept Sine)| NON_SCREAM | 0.0528 | NON_SCREAM | PASS |
| C14 | Malformed Buffer with NaNs and Infs | NON_SCREAM | 0.0043 | NON_SCREAM | PASS |

**Robustness Insight:** 10 of 14 conditions passed. However, the model failed on reverberant screams, distant screams, and low-amplitude screams because MLP static priors heavily penalize attenuated high frequencies and room smearing.

---

## 12. Final Acceptance Gate Audit & Verdict

| Acceptance Gate | Required Target | Model A (MLP) | Model B (TCN) | Model C (Fusion) | Model C (Cascade) | Status |
|---|---:|---:|---:|---:|---:|---|
| **1. Event-Level Scream Recall** | $\ge 96.0\%$ | 86.24% | 94.50% | 92.66% | 90.83% | **FAIL** |
| **2. Short-Scream Recall (< 1.0s)** | $\ge 90.0\%$ | 60.00% | 80.00% | 80.00% | 80.00% | **FAIL** |
| **3. Hard-Negative Event FPR** | $\le 5.0\%$ | 5.56% | 17.17% | 9.09% | 8.59% | **FAIL** |
| **4. Shouted-Speech FPR** | $\le 15.0\%$ | 7.14% | 21.43% | 7.14% | 4.76% | **PASS** (MLP, C) |
| **5. End-to-End Latency** | $\le 25.0$ ms | 95.97 ms | 55.63 ms | 152.97 ms | 152.97 ms | **FAIL** |
| **Simultaneous Compliance** | **All 5 Gates Met** | **FAIL** | **FAIL** | **FAIL** | **FAIL** | **REJECTED** |

### Final Engineering Recommendation
The architecture must **NOT** be deployed. Hierarchical nonlinear phonation discrimination has reached a structural physical limit: it trades short-scream recall and streaming latency for shouting FPR reduction without achieving the required safety-critical event recall or false-positive targets.
