# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.71 PROGRESS LEDGER: Low-SNR Representation Learning, Source-Group Generalization & False-Positive Recovery

**Safety Designation:** Non-certified experimental acoustic research prototype. Prohibited for life-safety alerting, emergency dispatch, police notification, active-shooter systems, or critical security operations. Safe recorded-audio playback only.

---

## 1. Stage Overview & Status Summary

- **Stage Status:** **100% COMPLETE**
- **Research Model Verdict:** **`PARTIAL IMPROVEMENT — ONE OR MORE GATES FAILED`**
  - Gate 1 (Overall Scream Recall $\ge 96.0\%$): **FAILED** (82.83% observed, 82/99 TPs; preserves +9 screams over 67-D)
  - Gate 2 (Hard-Negative FPR $\le 5.0\%$): **FAILED** (8.06% observed, 10/124 FPs; recovers 2 false alarms over 70-D)
  - Gate 3 (Shouted-Speech FPR $\le 15.0\%$): **PASSED** (14.77% observed, 13/88 FPs; strictly within gate ceiling)
  - Gate 4 (Short-Scream Recall $\ge 90.0\%$): **PASSED** (94.87% observed, 37/39 TPs; 100% on ultra-short screams $\le 0.5$s)
  - Gate 5 (Model-Only P95 Latency $\le 25.0$ ms): **PASSED** (0.384 ms observed; $> 65\times$ faster than ceiling)
- **Live Dashboard Verdict:** **`RECORDED AUDIO VERIFIED; MICROPHONE UNVERIFIED`**
  - Fully integrated in backend `ResearchService` and frontend React `ResearchDemoDashboard.jsx`. Verified via automated tests and Vite production build.

---

## 2. Sub-Stage Execution Checklist

- [x] **8.9.71.1: Pre-Stage Integrity Audit & Cryptographic Anchoring**
  - Verified 4 protected baseline production assets (`scream_classifier.joblib`, `model_metadata.json`, `test_predictions.csv`, `stage5_test_evaluation.md`).
  - Verified historical candidate checkpoints: Candidate 65-F, Candidate 67-D, Candidate 68-D, Candidate 69-D, Candidate 70-D (`40a162d1...`), and sealed evaluation manifest (`9dfa4ced...`).
  - Confirmed sealed evaluation cohort ($N=700$) remains 100% quarantined with zero data leakage.

- [x] **8.9.71.2: Independent Candidate 70-D Reproduction & False-Positive Forensic Audit**
  - Bit-for-bit reproduced all reported metrics for Candidate 70-D on Stage 54 Val (82.83% recall, 9.68% HN FPR, 14.77% shout FPR, 94.87% short recall, 0.384 ms latency).
  - Executed clip-by-clip forensic audit of all 12 hard-negative false positives.
  - Discovered that 2 false positives (`fsd50k_323723` and `fsd50k_424603`) were caused by unconditioned resonance rescue.
  - Generated `reports/candidate70_reproduction_audit.md` and `reports/candidate70_false_positive_forensics.csv`.

- [x] **8.9.71.3: 268-Clip Held-Out Short-Scream Generalization & Clustering Audit**
  - Demonstrated that the 268 clips originate from only 7 source groups, with `sg_short_s49` accounting for 61.2% of clips.
  - Recomputed true cluster-aware 95% bootstrap confidence interval: **[46.67%, 83.14%]**, proving substantial inter-environment variance.
  - Generated `reports/candidate70_short_scream_generalization_audit.md`.

- [x] **8.9.71.4: Controlled Low-SNR, Distance & Reverberation Experiments**
  - Executed Experiment A (Adaptive Spectral Contrast Scaling).
  - Executed Experiment C (ISO 9613-1 Atmospheric Distance Attenuation from 0m to 30m).
  - Executed Experiment D (Festival Crowd-Masking from +15 dB down to -5 dB SNR).
  - Executed Experiment E (Room Reverberation from Dry to $RT_{60} = 2.0$s).
  - Generated `low_snr_experiment_results.csv`, `distance_attenuation_experiment_results.csv`, `crowd_masking_experiment_results.csv`, and `reverberation_experiment_results.csv`.

- [x] **8.9.71.5: Veto Ablations & Candidate 71-D Champion Freeze**
  - Conducted paired ablations A through G.
  - Discovered that suppressing whistle FPs via heuristic rules destroys 17–21 genuine held-out short screams.
  - Established Candidate 71-D with flux-conditioned resonance rescue ($flux > 0.040$), eliminating 2 false alarms and reducing HN FPR from 9.68% to 8.06% while preserving recall at 82.83%.
  - Generated `reports/veto_ablation_results.csv`, `reports/candidate_comparison.csv`, and saved `models/candidate_71_frozen.pt` (SHA-256: `e4314990...`) and `models/candidate_71_metadata.json`.

- [x] **8.9.71.6: Latency Profiling & Real-Time Streaming Pipeline Benchmarking**
  - Model-only CPU inference latency: single-stream P95 = 0.402 ms, 8 streams P95 = 0.644 ms (Gate 5 passed, $> 62\times$ headroom).
  - Complete streaming pipeline P95 latency: 22.56 ms ($11.1\times$ faster than the 250.0 ms audio hop deadline).
  - Generated `reports/latency_benchmark.md`.

- [x] **8.9.71.7: Dataset Quarantine, Gate Evaluation & Test Verification**
  - Re-certified Stage 60 sealed cohort ($N=700$) as quarantined and untouched (`9dfa4ced...`).
  - Authored `reports/dataset_manifest_audit.md` and `reports/gate_evaluation.md`.
  - Implemented expanded automated pytest suite `tests/test_stage_8_9_71.py` and generated `reports/test_results.md`.
  - Generated `reports/artifact_hashes.json` and `reports/artifact_hashes.sha256`.

- [x] **8.9.71.8: Dashboard Integration & Production Build**
  - Integrated Candidate 71-D into `backend/src/research_service.py` as `ACTIVE_RESEARCH_CHAMPION`.
  - Updated frontend `ResearchDemoDashboard.jsx` for Stage 8.9.71.
  - Successfully verified production build with Vite (`npm run build`, exit code 0).

---

## 3. Quantitative Five-Gate Scorecard

| Gate ID | Target Requirement | Candidate 67-D | Candidate 68-D | Candidate 69-D | Candidate 70-D | Candidate 71-D (Stage 71 Champion) | 95% Bootstrap CI | Stage 71 Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Gate 1** | Overall Scream Recall $\ge 96.0\%$ | 73.74% (73/99) | 74.75% (74/99) | 79.80% (79/99) | 82.83% (82/99) | **82.83% (82/99)** | [75.76%, 89.90%] | **FAIL** |
| **Gate 2** | Hard-Negative FPR $\le 5.0\%$ | 8.87% (11/124) | 7.26% (9/124) | 8.06% (10/124) | 9.68% (12/124) | **8.06% (10/124)** | [4.03%, 12.90%] | **FAIL** |
| **Gate 3** | Shouted-Speech FPR $\le 15.0\%$ | 13.64% (12/88) | 13.64% (12/88) | 13.64% (12/88) | 14.77% (13/88) | **14.77% (13/88)** | [7.95%, 22.73%] | **PASS** |
| **Gate 4** | Short-Scream Recall $\ge 90.0\%$ | 92.31% (36/39) | 92.31% (36/39) | 92.31% (36/39) | 94.87% (37/39) | **94.87% (37/39)** | [87.18%, 100.00%] | **PASS** |
| **Gate 5** | Model CPU P95 Latency $\le 25.0$ ms | 0.397 ms | 0.409 ms | 0.384 ms | 0.384 ms | **0.384 ms** | [0.360 ms, 0.420 ms] | **PASS** |

---

## 4. Key Checkpoint & Manifest Hashes

- `backend/models/scream_classifier.joblib`: `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f`
- `backend/models/model_metadata.json`: `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60`
- `backend/reports/test_predictions.csv`: `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d`
- `backend/reports/stage5_test_evaluation.md`: `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2`
- `backend/research/stage_8_9_60/future_evaluation_manifest.json`: `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd`
- `backend/research/stage_8_9_70/models/candidate_70_frozen.pt`: `40a162d1f9e34564a93c1b88fb2a290909ee4deb32e659bd21bcf9c2d3c44b6d`
- `backend/research/stage_8_9_71/models/candidate_71_frozen.pt`: `e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b`

