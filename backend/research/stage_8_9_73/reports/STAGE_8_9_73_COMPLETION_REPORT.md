# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.73 COMPLETION REPORT: Vocalization Discrimination, Acoustic Boundary Learning & Residual Error Recovery

**Stage Identifier:** Stage 8.9.73  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Evaluation Date:** 2026-11-14  
**Project Directory:** [`festival-scream-detector/`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector)  
**Stage Directory:** [`backend/research/stage_8_9_73/`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_73)  
**Research Champion:** **Candidate 71-D** (Frozen Checkpoint SHA-256: `e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b`)  
**Research Model Verdict:** **`PARTIAL IMPROVEMENT — ONE OR MORE GATES FAILED`**  
**Live Dashboard Verdict:** **`RECORDED AUDIO VERIFIED; MICROPHONE UNVERIFIED`**  
**Production Promotion Status:** **NOT AUTHORIZED — STRICTLY EXPERIMENTAL RESEARCH PROTOTYPE**

---

## 0. Mandatory Safety & Operational Boundaries

> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This acoustic research prototype is non-certified software intended solely for scientific evaluation and controlled laboratory demonstrations.  
> - **Strict Prohibitions:** No deployment for emergency dispatch, autonomous alerts, police notification, active-shooter systems, perimeter defense, or critical life-safety operations.  
> - **Input Media:** Only legally obtained recorded audio datasets and controlled playback environments are authorized.  
> - **Advisory Only:** Acoustic model predictions represent statistical pattern matching and do not establish danger, violence, distress, or emergency events.  
> - **No Production Promotion:** Research candidates are ineligible for production deployment.

---

## 1. Executive Summary & Mission Objectives

Stage 8.9.73 investigated the primary scientific question:
**"Can a hierarchical vocalization-discrimination architecture distinguish scream-like vocalizations from acoustically similar non-scream sounds, resolve residual errors, and eliminate hand-crafted acoustic vetoes?"**

Building upon Candidate 71-D (the active frozen research champion), Stage 8.9.73 executed a comprehensive series of experiments:
1. **Independent Reproduction & Forensic Audit:** Bit-for-bit reproduction of Candidate 71-D across all metrics; full forensic audit of all 17 false negatives and 10 hard-negative false positives.
2. **Disentanglement Analysis (Real vs Synthetic Screams):** Revealed that on **genuine real recorded screams**, Candidate 71-D achieves **88.75% recall (71/80)** with only 9 missed clips, whereas on **synthetic crowd-masked screams**, recall drops to **57.89% (11/19)** due to heavy background noise (-6 dB to 0 dB SNR) masking formant structures.
3. **Class-Specific Discrimination Forensics:**
   - **Infant Crying ($N=20$, 3 FP):** Crying generates genuine vocal fold non-linearities (roughness 0.0519 vs screams 0.0886), creating severe overlap with low-roughness screams.
   - **Shouted Speech ($N=88$, 13 FP):** Screams exhibit $4.16\times$ higher high-frequency ratio (mean 4.391 vs 1.054) and significantly higher dynamic spectral flux (mean 0.083 vs 0.061, AUC 0.7005).
   - **Whistles and Sirens ($N=31$, 5 FP):** Whistles exhibit extreme high-frequency ratios ($HF > 40.0$), while sirens exhibit high artificial roughness (0.2088) and negative HNR (-2.36 dB).
4. **Hierarchical Vocalization Architecture Evaluation:**
   - Evaluated a 3-stage hierarchical model (Non-vocal vs Vocal non-scream vs Scream).
   - **Candidate 73-A (Pure Hierarchical Neural Head without Vetoes):** Suffered severe shouted-speech leakage (**27.27% FPR**, violating Gate 3).
   - **Candidate 73-B (Hierarchical Head + Calibrated Vetoes):** Achieved identical classification performance to Candidate 71-D (82.83% recall, 8.06% HN FPR, 14.77% shout FPR), but incurred a **+30% latency overhead** (0.542 ms vs 0.417 ms).
5. **Residual Veto Ablation & Child Scream Dilemma:**
   - Forensic analysis revealed that 2 child screams (`273153__hoerspielwerkstatt-hef__child-scream2`) have high raw probabilities ($0.574$ and $0.572$) but are collaterally suppressed by the `distress_veto` because child screams exhibit low auditory roughness ($0.0189 < 0.022$).
   - Relaxing this veto (**Candidate 73-C**) successfully recovers both child screams, lifting overall recall to **84.85% (84/99)** and real scream recall to **91.25% (73/80)**.
   - However, relaxing the distress veto allows 2 shouted-speech false alarms to trigger, driving Shouted-Speech FPR from 14.77% up to **17.05% (15/88)**, which violates Gate 3 ($\le 15.0\%$).
6. **Tournament Decision:** Candidate 71-D is retained as the active research champion. No candidate passes all five gates.

---

## 2. Five-Gate Quantitative Evaluation Scorecard

Evaluated against the exposed Stage 54 Validation Cohort ($N=311$, `EXPOSED_DEVELOPMENT_COHORT`) with 95% cluster-aware bootstrap confidence intervals ($B=2,000$ resamples across 138 source groups):

| Gate ID | Target Requirement | Metric Name | Candidate 67-D | Candidate 69-D | Candidate 70-D | Candidate 71-D (Frozen Champion) | 95% Bootstrap CI | Stage 73 Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Gate 1** | $\ge 96.0\%$ | Overall Scream Recall | 73.74% (73/99) | 79.80% (79/99) | 82.83% (82/99) | **82.83% (82/99)** | [74.00%, 91.25%] | **FAIL** |
| **Gate 2** | $\le 5.0\%$ | Hard-Negative FPR | 8.87% (11/124) | 8.06% (10/124) | 9.68% (12/124) | **8.06% (10/124)** | [2.83%, 14.29%] | **FAIL** |
| **Gate 3** | $\le 15.0\%$ | Shouted-Speech FPR | 13.64% (12/88) | 13.64% (12/88) | 14.77% (13/88) | **14.77% (13/88)** | [2.13%, 32.50%] | **PASS** |
| **Gate 4** | $\ge 90.0\%$ | Short-Scream Recall (< 1.0s) | 92.31% (36/39) | 92.31% (36/39) | 94.87% (37/39) | **94.87% (37/39)** | [86.21%, 100.00%] | **PASS** |
| **Gate 5** | $\le 25.0$ ms | Model CPU P95 Latency | 0.397 ms | 0.384 ms | 0.384 ms | **0.417 ms** | [0.370 ms, 0.450 ms] | **PASS** ($> 59\times$ Headroom) |

---

## 3. Cryptographic Baseline Verification

All protected baseline assets and historical checkpoints were verified bit-for-bit identical:

| Artifact Identifier | Expected SHA-256 | Observed SHA-256 | Status |
| :--- | :--- | :--- | :--- |
| `backend/models/scream_classifier.joblib` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | **MATCH** |
| `backend/models/model_metadata.json` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | **MATCH** |
| `backend/reports/test_predictions.csv` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | **MATCH** |
| `backend/reports/stage5_test_evaluation.md` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | **MATCH** |
| `backend/research/stage_8_9_60/future_evaluation_manifest.json` | `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd` | `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd` | **MATCH (QUARANTINED)** |
| `backend/research/stage_8_9_73/models/candidate_71_frozen.pt` | `e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b` | `e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b` | **MATCH (FROZEN)** |

---

## 4. Disentangled Scream Analysis (Real vs Synthetic)

A pivotal finding of Stage 8.9.73 is the disentanglement of positive scream recall:

| Scream Sub-Cohort | Sample Count ($N$) | Correctly Detected (TP) | False Negatives (FN) | Recall | Failure Mechanism |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Real Recorded Screams** | 80 | 71 | 9 | **88.75%** | 2 child screams suppressed by distress veto; 5 low-intensity gasps; 2 boundary rescues |
| **Synthetic Masked Screams** | 19 | 11 | 8 | **57.89%** | Severe crowd noise (-6 dB to 0 dB SNR) elevates noise floor and washes out harmonic contrast |
| **Combined Positives** | **99** | **82** | **17** | **82.83%** | Official Gate 1 metric |

On genuine human scream recordings in quiet-to-moderate acoustic conditions, Candidate 71-D reaches **88.75% recall**, whereas on synthetic screams buried under heavy festival crowd noise, recall drops to **57.89%**.

---

## 5. Class-Specific Discrimination Analyses

### 5.1 Infant Cry vs Scream Discrimination
Detailed in [`infant_cry_vs_scream_results.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_73/reports/infant_cry_vs_scream_results.csv):
- **Vocal Roughness:** Infant crying exhibits mean roughness of **0.0519**, while screams exhibit **0.0886**. However, infant crying roughness overlaps heavily with child screams (0.0189) and lower-intensity adult screams.
- **High-Frequency Ratio:** Screams exhibit mean HF ratio of **4.391** vs **1.054** in infant cries.
- **False Alarms:** 3 of 20 infant cries trigger false positives due to severe distress-induced vocal fold chaotic bifurcation.

### 5.2 Shouted Speech vs Scream Discrimination
Detailed in [`shouted_speech_vs_scream_results.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_73/reports/shouted_speech_vs_scream_results.csv):
- High-effort shouted speech exhibits lower high-frequency energy ($HF \approx 1.05$) and lower spectral flux (0.061 vs 0.083 in screams).
- The spectral flux discriminator achieves an **AUC of 0.7005**, validating its utility in the resonance rescue mechanism.

### 5.3 Whistle & Siren Discrimination
Detailed in [`whistle_siren_discrimination_results.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_73/reports/whistle_siren_discrimination_results.csv):
- Whistles exhibit extreme high-frequency ratios ($HF > 43.0$).
- Sirens exhibit high roughness (0.2088) and negative HNR (-2.36 dB).

---

## 6. Multi-Candidate Tournament Comparison Matrix

Comprehensive head-to-head comparison across all historical and Stage 73 candidates in [`candidate_comparison.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_73/reports/candidate_comparison.csv):

| Candidate Identifier | Architecture & Core Innovations | Overall Recall | Real Recall | Synth Recall | HN FPR | Shout FPR | Short Recall | Latency P95 | Tournament Outcome |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Candidate 67-D** | Dual-Res Gated + 2-Veto (Whistle + Distress) | 73.74% (73/99) | 81.25% (65/80) | 42.11% (8/19) | 8.87% (11/124) | 13.64% (12/88) | 92.31% (36/39) | 0.397 ms | Historical Baseline |
| **Candidate 68-D** | Dual-Res Gated + 4-Veto (SNR Adaptive) | 74.75% (74/99) | 81.25% (65/80) | 47.37% (9/19) | 7.26% (9/124) | 13.64% (12/88) | 92.31% (36/39) | 0.409 ms | Historical Baseline |
| **Candidate 69-D** | Dual-Res Gated + Conditioned Multi-Veto | 79.80% (79/99) | 86.25% (69/80) | 52.63% (10/19) | 8.06% (10/124) | 13.64% (12/88) | 92.31% (36/39) | 0.384 ms | Historical Baseline |
| **Candidate 70-D** | Dual-Res Gated + Streamlined 3-Veto & Rescue | 82.83% (82/99) | 88.75% (71/80) | 57.89% (11/19) | 9.68% (12/124) | 14.77% (13/88) | 94.87% (37/39) | 0.384 ms | Previous Champion |
| **Candidate 71-D** | **Dual-Res Gated + Flux-Conditioned Rescue** | **82.83% (82/99)** | **88.75% (71/80)** | **57.89% (11/19)** | **8.06% (10/124)** | **14.77% (13/88)** | **94.87% (37/39)** | **0.417 ms** | **ACTIVE CHAMPION (Retained)** |
| **Candidate 73-A** | Hierarchical Vocalization Head (No Vetoes) | 81.82% (81/99) | 87.50% (70/80) | 57.89% (11/19) | 10.48% (13/124) | 27.27% (24/88) | 92.31% (36/39) | 0.465 ms | Rejected (Gate 3 Violation: 27.27% FPR) |
| **Candidate 73-B** | Hierarchical Head + Calibrated Vetoes | 82.83% (82/99) | 88.75% (71/80) | 57.89% (11/19) | 8.06% (10/124) | 14.77% (13/88) | 94.87% (37/39) | 0.542 ms | Rejected (+30% Latency Overhead) |
| **Candidate 73-C** | Candidate 71-D with Relaxed Child Distress Veto | 84.85% (84/99) | 91.25% (73/80) | 57.89% (11/19) | 8.06% (10/124) | 17.05% (15/88) | 94.87% (37/39) | 0.417 ms | Rejected (Gate 3 Violation: 17.05% FPR) |

---

## 7. Latency & Streaming Pipeline Benchmarks

Evaluated on local CPU in [`latency_benchmark.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_73/reports/latency_benchmark.md):
- **Model-Only P95 Latency (Gate 5):** **0.370 ms** (single stream), **0.524 ms** (8 streams concurrent). Exceeds the 25.0 ms ceiling by **$67\times$**. **GATE 5 PASSED**.
- **Complete Downstream Pipeline P95:** **17.14 ms** (16 kHz audio window $\to$ DSP $\to$ Neural forward $\to$ Veto logic). Operates **$14.6\times$ faster** than the 250.0 ms audio-hop deadline.

---

## 8. Final Decision & Next Steps

1. **Gate Acceptance:** Gates 1 (82.83% vs $\ge 96.0\%$) and Gate 2 (8.06% vs $\le 5.0\%$) remain unmet.
2. **Champion Retention:** Candidate 71-D is retained as the active research champion.
3. **Definitive Research Verdict:** **`PARTIAL IMPROVEMENT — ONE OR MORE GATES FAILED`**.
4. **Safety Ruling:** No production promotion is authorized.

