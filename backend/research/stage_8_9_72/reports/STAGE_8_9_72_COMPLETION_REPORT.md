# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.72 COMPLETION REPORT: Acoustic Representation Generalization, Hard-Negative Discrimination & Prospective Evaluation Preparation

**Stage Identifier:** Stage 8.9.72  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Evaluation Date:** 2026-11-14  
**Project Directory:** [`festival-scream-detector/`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector)  
**Stage Directory:** [`backend/research/stage_8_9_72/`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_72)  
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

Stage 8.9.72 investigated the primary scientific question:
**"Can the model learn a more robust scream representation instead of depending on increasingly complex hand-crafted vetoes?"**

Building upon Candidate 71-D (which achieved 82.83% recall, 8.06% HN FPR, 14.77% shout FPR, and 94.87% short recall via flux-conditioned resonance rescue), Stage 8.9.72 executed:
1. **Independent Reproduction & Forensic Audit:** Bit-for-bit reproduction of Candidate 71-D across all metrics; full forensic audit of all 17 false negatives and all 10 hard-negative false positives.
2. **Rescue Mechanism Ablation:** Recording-level evaluation of unconditioned vs. flux-conditioned resonance rescue, proving that flux conditioning ($flux > 0.040$) eliminates 2 false alarms without losing true positives.
3. **Representation Learning Experiments:** Systematic investigation of five directions:
   - **Experiment A (Low-SNR Representation):** Noise-floor normalization recovered +1 low-intensity scream but elevated shouted-speech FPR to 18.18% (violating Gate 3).
   - **Experiment B (Multi-Resolution Fusion):** Bilinear cross-branch attention stabilized sustained events but added 0.12 ms latency without significant gain.
   - **Experiment C (Contrastive Learning):** Supervised Contrastive Loss (SupCon) compressed scream embeddings and reduced shouted FPR to 13.64%, but caused underconfidence on distant screams (recall dropped to 80.81%).
   - **Experiment D (Hard-Negative Multi-Task Discrimination):** An auxiliary 8-class categorical head taught the backbone to recognize infant crying and sirens, lowering hard-negative FPR to 7.26%, but reduced overall recall to 80.81%.
   - **Experiment E (Reverberation & Distance Robustness):** ISO 9613-1 atmospheric attenuation augmentation recovered synthetic distant screams (+1 TP) but induced mild speech false alarms under room reverberation.
4. **Core Scientific Finding:** Pure representation learning alone on 1,055 training samples cannot replace acoustic domain constraints. Screams and shouted speech share identical vocal tract physics and overlapping fundamental frequencies ($F_0$); auditory roughness (vocal fold chaos in 30–150 Hz) and dynamic spectral flux remain essential discriminators.
5. **Tournament Decision:** Candidate 71-D is retained as the frozen research champion. No model passed all five gates.

---

## 2. Five-Gate Quantitative Evaluation Scorecard

Evaluated against the exposed Stage 54 Validation Cohort ($N=311$, `EXPOSED_DEVELOPMENT_COHORT`) with 95% cluster-aware bootstrap confidence intervals ($B=2,000$ resamples across 138 source groups):

| Gate ID | Target Requirement | Metric Name | Candidate 67-D | Candidate 69-D | Candidate 70-D | Candidate 71-D (Frozen Champion) | 95% Bootstrap CI | Stage 72 Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Gate 1** | $\ge 96.0\%$ | Overall Scream Recall | 73.74% (73/99) | 79.80% (79/99) | 82.83% (82/99) | **82.83% (82/99)** | [74.00%, 91.25%] | **FAIL** |
| **Gate 2** | $\le 5.0\%$ | Hard-Negative FPR | 8.87% (11/124) | 8.06% (10/124) | 9.68% (12/124) | **8.06% (10/124)** | [2.83%, 14.29%] | **FAIL** |
| **Gate 3** | $\le 15.0\%$ | Shouted-Speech FPR | 13.64% (12/88) | 13.64% (12/88) | 14.77% (13/88) | **14.77% (13/88)** | [2.13%, 32.50%] | **PASS** |
| **Gate 4** | $\ge 90.0\%$ | Short-Scream Recall (< 1.0s) | 92.31% (36/39) | 92.31% (36/39) | 94.87% (37/39) | **94.87% (37/39)** | [86.21%, 100.00%] | **PASS** |
| **Gate 5** | $\le 25.0$ ms | Model CPU P95 Latency | 0.397 ms | 0.384 ms | 0.384 ms | **0.417 ms** | [0.380 ms, 0.450 ms] | **PASS** ($> 59\times$ Headroom) |

---

## 3. Cryptographic Baseline Verification

All protected baseline assets and historical checkpoints were verified bit-for-bit identical before and after Stage 8.9.72:

| Artifact Identifier | Expected SHA-256 | Observed SHA-256 | Status |
| :--- | :--- | :--- | :--- |
| `backend/models/scream_classifier.joblib` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | **MATCH** |
| `backend/models/model_metadata.json` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | **MATCH** |
| `backend/reports/test_predictions.csv` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | **MATCH** |
| `backend/reports/stage5_test_evaluation.md` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | **MATCH** |
| `backend/research/stage_8_9_60/future_evaluation_manifest.json` | `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd` | `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd` | **MATCH (QUARANTINED)** |
| `backend/research/stage_8_9_71/models/candidate_71_frozen.pt` | `e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b` | `e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b` | **MATCH (FROZEN)** |

---

## 4. Detailed Forensic Audits

### 4.1 False Negative Forensics ($N=17$)
Analysis of the 17 missed screams documented in [`candidate71_false_negative_forensics.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_72/reports/candidate71_false_negative_forensics.csv) identified four distinct failure clusters:
1. **Crowd-Masking & Low-SNR Screams (7 clips):**
   Synthetic screams mixed at $-6$ dB, $-3$ dB, and $0$ dB SNR (`v2_synth_008`, `v2_synth_015`, `v2_synth_019`, `v2_synth_068`, `v3_synth_007`, `v3_synth_011`, `v3_synth_034`). Background noise masks the high-frequency harmonics, dropping raw neural confidence to $0.33$–$0.44$.
2. **Hand-Crafted Veto Collateral Suppression (3 clips):**
   - `273153__hoerspielwerkstatt-hef__child-scream2` (2 segments) has raw probability $0.574$ and $0.572$, but is suppressed by `distress_veto` because child screams exhibit low roughness ($0.0189 < 0.022$).
   - `fsd50k_220658` and `fsd50k_219882` suppressed by `flux_veto` due to low spectral flux ($< 0.036$).
3. **Low-Intensity & Boundary Gasps (5 clips):**
   Acoustic vocalizations with moderate intensity (`ULJI_15_5_0_12_0_0_0`, `242607__reitanna__gasp-oooh`, `242644__reitanna__another-surprised-oooh`, `336537__chrillz3r__scream-frightened`).
4. **Sub-Threshold Resonance Rescues (2 clips):**
   `fsd50k_144338` (raw 0.410 $\to$ final 0.445) and `v3_synth_046` (raw 0.466). Rescued by $+0.035$, but fell just short of the 0.4920 operating threshold.

### 4.2 Hard-Negative False Positive Forensics ($N=10$)
Analysis of the 10 false alarms documented in [`candidate71_false_positive_forensics.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_72/reports/candidate71_false_positive_forensics.csv) identified three primary acoustic categories:
1. **Infant Crying (3 clips):** `fsd50k_154428`, `fsd50k_343976`, `fsd50k_344030`. Physiological infant distress triggers genuine vocal roughness ($0.023$–$0.055$) and high-frequency flux, perfectly mimicking screams.
2. **Resonant Whistle Bursts (3 clips):** `src_v5_parent_0104`, `0108`, `0116`. Whistle bursts with extreme high-frequency ratios ($HF > 43.0$). Attempting to veto them with heuristic rules destroyed 17–21 genuine held-out short screams.
3. **Sirens & SFX (2 clips):** `fsd50k_184623`, `fsd50k_34280`. Frequency sweeps with roughness $0.27$–$0.28$.
4. **Crowd & Environmental (2 clips):** `fsd50k_83199` (crowd chant, final prob 0.505) and `fs_369001` (environmental noise, final prob 0.563).

---

## 5. Rescue Mechanism Ablation Audit

Evaluating the flux-conditioned resonance rescue mechanism across 6 configurations in [`rescue_mechanism_ablation.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_72/reports/rescue_mechanism_ablation.csv):
- **Candidate 71-D (Full, $flux > 0.040$):** TP = 82/99 (82.83%), HN FP = 10/124 (8.06%), Shout FP = 13/88 (14.77%).
- **Without Rescue:** TP collapses to 79/99 (79.80%), losing 3 true screams; short recall collapses to 36/39.
- **Unconditioned Rescue (Candidate 70-D):** TP = 82/99, but HN FP rises to 12/124 (9.68%) due to rescuing 2 stationary non-screams.
- **Permissive Flux ($flux > 0.020$):** HN FP rises to 12/124 (too permissive).
- **Restrictive Flux ($flux > 0.060$):** TP drops to 80/99 (suppresses 2 genuine screams).
- **Learned Continuous Scaling:** TP = 80/99, HN FP = 10/124, Shout FP = 14/88.

**Conclusion:** Flux conditioning at 0.040 represents the mathematically optimal operating threshold on development data, resolving the 2 false alarms without losing true positive recall.

---

## 6. Multi-Candidate Tournament Comparison Matrix

Comprehensive comparison across all historical and Stage 72 candidates in [`candidate_comparison.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_72/reports/candidate_comparison.csv):

| Candidate Identifier | Architecture & Core Innovations | Overall Recall | HN FPR | Shout FPR | Short Recall | Latency P95 | Tournament Outcome |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Candidate 67-D** | Dual-Res Gated + 2-Veto (Whistle + Distress) | 73.74% (73/99) | 8.87% (11/124) | 13.64% (12/88) | 92.31% (36/39) | 0.397 ms | Historical Baseline |
| **Candidate 68-D** | Dual-Res Gated + 4-Veto (SNR Adaptive) | 74.75% (74/99) | 7.26% (9/124) | 13.64% (12/88) | 92.31% (36/39) | 0.409 ms | Historical Baseline |
| **Candidate 69-D** | Dual-Res Gated + Conditioned Multi-Veto | 79.80% (79/99) | 8.06% (10/124) | 13.64% (12/88) | 92.31% (36/39) | 0.384 ms | Historical Baseline |
| **Candidate 70-D** | Dual-Res Gated + Streamlined 3-Veto & Rescue | 82.83% (82/99) | 9.68% (12/124) | 14.77% (13/88) | 94.87% (37/39) | 0.384 ms | Previous Champion |
| **Candidate 71-D** | **Dual-Res Gated + Flux-Conditioned Rescue** | **82.83% (82/99)** | **8.06% (10/124)** | **14.77% (13/88)** | **94.87% (37/39)** | **0.417 ms** | **ACTIVE CHAMPION (Retained)** |
| **Candidate 72-A** | Dual-Res + Low-SNR Noise-Floor Norm | 83.84% (83/99) | 10.48% (13/124) | 18.18% (16/88) | 94.87% (37/39) | 0.388 ms | Rejected (Gate 3 FPR Violation) |
| **Candidate 72-B** | Dual-Res + Supervised Contrastive Loss | 80.81% (80/99) | 8.06% (10/124) | 13.64% (12/88) | 92.31% (36/39) | 0.384 ms | Research Candidate (-2 TP Recall) |
| **Candidate 72-C** | Multi-Task Hard-Negative Categorical Head | 80.81% (80/99) | 7.26% (9/124) | 13.64% (12/88) | 92.31% (36/39) | 0.392 ms | Research Candidate (-2 TP Recall) |

---

## 7. Latency & Streaming Pipeline Benchmarks

Evaluated on local CPU in [`latency_benchmark.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_72/reports/latency_benchmark.md):
- **Model-Only P95 Latency (Gate 5):** **0.417 ms** (single stream), **0.441 ms** (8 streams concurrent). Exceeds the 25.0 ms ceiling by **$59.9\times$**. **GATE 5 PASSED**.
- **Complete Downstream Pipeline P95:** **17.22 ms** (16 kHz audio window $\to$ DSP $\to$ Neural forward $\to$ Veto logic). Operates **$14.5\times$ faster** than the 250.0 ms audio-hop deadline.

---

## 8. Automated Regression Test Suite

All 15 regression tests in [`test_stage_8_9_72.py`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_72/tests/test_stage_8_9_72.py) passed with 100% compliance:
- Artifact Integrity: All hashes match; protected baselines identical.
- Prediction Correctness: Deterministic inference, rescue logic, distress veto.
- Dataset Quarantine: Zero source-group leakage; sealed manifest quarantined.
- Streaming: Zero-padding on short events (< 250 ms) verified.
- Dashboard: Model switching and Five-Gate scorecard verified.

Full test report: [`test_results.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_72/reports/test_results.md).

---

## 9. Final Decision & Next Steps

1. **Gate Acceptance:** Gates 1 (82.83% vs $\ge 96.0\%$) and Gate 2 (8.06% vs $\le 5.0\%$) remain unmet.
2. **Champion Retention:** Candidate 71-D is retained as the active research champion.
3. **Definitive Research Verdict:** **`PARTIAL IMPROVEMENT — ONE OR MORE GATES FAILED`**.
4. **Safety Ruling:** No production promotion is authorized.

