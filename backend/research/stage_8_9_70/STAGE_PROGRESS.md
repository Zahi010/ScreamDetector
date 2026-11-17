# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.70 PROGRESS LEDGER: Generalization Audit, Veto Simplification & Low-SNR Scream Recovery

**Safety Designation:** Non-certified experimental acoustic research prototype. Prohibited for life-safety alerting, emergency dispatch, police notification, active-shooter systems, or critical security operations. Safe recorded-audio playback only.

---

## 1. Stage Overview & Status Summary

- **Stage Status:** **100% COMPLETE**
- **Research Model Verdict:** **`PARTIAL IMPROVEMENT — ONE OR MORE GATES FAILED`**
  - Gate 1 (Overall Scream Recall $\ge 96.0\%$): **FAILED** (82.83% observed, 82/99 TPs; recovers +3 screams over 69-D and +9 over 67-D)
  - Gate 2 (Hard-Negative FPR $\le 5.0\%$): **FAILED** (9.68% observed, 12/124 FPs)
  - Gate 3 (Shouted-Speech FPR $\le 15.0\%$): **PASSED** (14.77% observed, 13/88 FPs; strictly within gate ceiling)
  - Gate 4 (Short-Scream Recall $\ge 90.0\%$): **PASSED** (94.87% observed, 37/39 TPs; 100% on ultra-short screams $\le 0.5$s)
  - Gate 5 (Model-Only P95 Latency $\le 25.0$ ms): **PASSED** (0.384 ms observed; $> 65\times$ faster than ceiling)
- **Live Dashboard Verdict:** **`RECORDED AUDIO VERIFIED; MICROPHONE UNVERIFIED`**
  - Fully integrated in backend `ResearchService` and frontend React `ResearchDemoDashboard.jsx`. Verified via automated tests and Vite production build.

---

## 2. Sub-Stage Execution Checklist

- [x] **8.9.70.1: Pre-Stage Integrity Audit & Cryptographic Anchoring**
  - Verified 4 protected baseline production assets (`scream_classifier.joblib`, `model_metadata.json`, `test_predictions.csv`, `stage5_test_evaluation.md`).
  - Verified historical candidate checkpoints: Candidate 65-F (`06a98025db...`), Candidate 67-D (`8fc2255a33...`), Candidate 68-D (`8a3b425a28...`), Candidate 69-D (`d468b75ab1...`), and sealed evaluation manifest (`9dfa4ced36...`).
  - Confirmed sealed evaluation cohort ($N=700$) remains 100% quarantined with zero data leakage.

- [x] **8.9.70.2: Independent Candidate 69-D Reproduction & False-Negative Re-Audit**
  - Bit-for-bit reproduced all reported metrics for Candidate 69-D on Stage 54 Val (79.80% recall, 8.06% HN FPR, 13.64% shout FPR, 92.31% short recall, 0.384 ms latency).
  - Executed multi-label forensic re-audit of the 26 historical false negatives:
    - 73.1% (19/26) suffer from diffuse reverberation smearing ($RT_{60} > 1.2$s).
    - 69.2% (18/26) exhibit raw neural underconfidence ($p_{\text{raw}} < 0.4920$).
    - 42.3% (11/26) exhibit both simultaneously.
    - Only 15.4% (4/26) were missed due to active heuristic vetoes.
  - Generated `reports/candidate69_reproduction_audit.md` and `reports/candidate69_false_negative_reaudit.csv`.

- [x] **8.9.70.3: 268-Clip Held-Out Short-Scream Provenance & Subgroup Performance Audit**
  - Traced exact lineage from `stage_64_short_scream_manifest.csv` ($N=401$) minus Stage 63 dev cohort ($N=133$) $\to$ net $N=268$ held-out clips across 7 source groups.
  - Duration breakdown: 0–250ms (100.0%, 1/1), 250–500ms (73.13%, 49/67), 500–1000ms (53.00%, 106/200) $\to$ Total 58.21% (156/268).
  - Isolated root cause: **83.9% of misses (94/112)** have $p_{\text{raw}} < 0.4920$ caused by acoustic distance and low SNR (mean 2.4 dB in `sg_short_supp`).
  - Generated `reports/short_scream_268_provenance_audit.md` and `reports/short_scream_268_subgroup_results.csv`.

- [x] **8.9.70.4: Systematic Veto Simplification Ablations (A through G)**
  - Executed full combinatorial ablation study across all 311 validation recordings and 268 held-out recordings.
  - Discovered that Ablation C (No HFCR Veto) yields **zero prediction differences** compared to Full Candidate 69-D, proving the HFCR roll-off veto is 100% redundant when flux and vocal distress vetoes are active.
  - Confirmed flux veto is non-negotiable (removing it causes shouted FPR to collapse to 21.59%).
  - Confirmed whistle veto is essential (removing it degrades hard-negative FPR to 11.29%).
  - Generated `reports/veto_ablation_results.csv`.

- [x] **8.9.70.5: Low-SNR & Reverberation Interventions & Candidate Tournament**
  - Evaluated low-SNR flatness compensation, high-frequency energy conservation, asymmetric direct-path biasing, and resonance agreement rescue.
  - Established Candidate 70-D as the stage champion:
    - Overall recall: **82.83%** (82/99, +3 screams over 69-D, +9 over 67-D)
    - Hard-negative FPR: **9.68%** (12/124)
    - Shouted-speech FPR: **14.77%** (13/88, strictly $\le 15.0\%$, Gate 3 PASS)
    - Short-scream recall: **94.87%** (37/39, Gate 4 PASS)
    - Held-out short-scream recall: **58.96%** (158/268)
  - Generated `reports/low_snr_experiment_results.csv`, `reports/reverberation_experiment_results.csv`, `reports/candidate_comparison.csv`, and saved `models/candidate_70_frozen.pt` (SHA-256: `40a162d1...`) and `models/candidate_70_metadata.json`.

- [x] **8.9.70.6: Latency Profiling & Real-Time Streaming Pipeline Benchmarking**
  - Model-only CPU inference latency: single-stream P95 = 0.384 ms, 8 streams P95 = 0.376 ms (Gate 5 passed, $> 65\times$ headroom).
  - Complete streaming pipeline P95 latency: 16.66 ms ($15.0\times$ faster than the 250.0 ms audio hop deadline).
  - Generated `reports/latency_benchmark.md`.

- [x] **8.9.70.7: Dataset Quarantine, Gate Evaluation & Test Verification**
  - Formally designated Stage 54 Val as `EXPOSED_DEVELOPMENT_COHORT`.
  - Re-certified Stage 60 sealed cohort ($N=700$) as quarantined and untouched (`9dfa4ced...`).
  - Authored `reports/dataset_manifest_audit.md` and `reports/gate_evaluation.md` (with 95% bootstrap CIs).
  - Implemented automated pytest suite `tests/test_stage_8_9_70.py` (7/7 passed, 100%) and generated `reports/test_results.md`.
  - Generated `reports/artifact_hashes.json` and `reports/artifact_hashes.sha256`.

- [x] **8.9.70.8: Dashboard Integration & Production Build**
  - Integrated Candidate 70-D into `backend/src/research_service.py` as `ACTIVE_RESEARCH_CHAMPION`.
  - Updated frontend `ResearchDemoDashboard.jsx` for Stage 8.9.70.
  - Successfully verified production build with Vite (`npm run build`, exit code 0).

---

## 3. Quantitative Five-Gate Scorecard

| Gate ID | Target Requirement | Candidate 67-D | Candidate 68-D | Candidate 69-D | Candidate 70-D (Stage 70 Champion) | 95% Bootstrap CI | Stage 70 Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Gate 1** | Overall Scream Recall $\ge 96.0\%$ | 73.74% (73/99) | 74.75% (74/99) | 79.80% (79/99) | **82.83% (82/99)** | [75.76%, 89.90%] | **FAIL** |
| **Gate 2** | Hard-Negative FPR $\le 5.0\%$ | 8.87% (11/124) | 7.26% (9/124) | 8.06% (10/124) | **9.68% (12/124)** | [4.84%, 15.32%] | **FAIL** |
| **Gate 3** | Shouted-Speech FPR $\le 15.0\%$ | 13.64% (12/88) | 13.64% (12/88) | 13.64% (12/88) | **14.77% (13/88)** | [7.95%, 22.73%] | **PASS** |
| **Gate 4** | Short-Scream Recall $\ge 90.0\%$ | 92.31% (36/39) | 92.31% (36/39) | 92.31% (36/39) | **94.87% (37/39)** | [87.18%, 100.00%] | **PASS** |
| **Gate 5** | Model CPU P95 Latency $\le 25.0$ ms | 0.397 ms | 0.409 ms | 0.384 ms | **0.384 ms** | [0.360 ms, 0.420 ms] | **PASS** |

---

## 4. Key Checkpoint & Manifest Hashes

- `backend/models/scream_classifier.joblib`: `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f`
- `backend/models/model_metadata.json`: `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60`
- `backend/reports/test_predictions.csv`: `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d`
- `backend/reports/stage5_test_evaluation.md`: `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2`
- `backend/research/stage_8_9_60/future_evaluation_manifest.json`: `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd`
- `backend/research/stage_8_9_69/models/candidate_69_frozen.pt`: `d468b75ab12d5ef2b8577c18304e8c4ddaf78f3059b2c0395a1a3263ac6dd92c`
- `backend/research/stage_8_9_70/models/candidate_70_frozen.pt`: `40a162d1f9e34564a93c1b88fb2a290909ee4deb32e659bd21bcf9c2d3c44b6d`

