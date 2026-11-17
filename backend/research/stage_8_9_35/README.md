# STAGE 8.9.35 — SPATIAL AUDIO RESEARCH, FREQUENCY-SUBBAND DISCRIMINATION & MULTI-PATHWAY FUSION

**Project:** Festival Scream Detector  
**Stage:** 8.9.35  
**Status:** **COMPLETED (RESEARCH AUDIT FINALIZED)**  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Production Status:** STRICTLY FROZEN (Decision Threshold: 0.3500)  
**Execution Timestamp:** November 2, 2026  
**Final Determination:** **REJECTED FOR PRODUCTION — RESEARCH ONLY**  

---

## 1. Executive Summary & Objective

Stage 8.9.35 conducted a comprehensive scientific investigation into frequency-subband representations (300–800 Hz, 800–1,500 Hz, 1,500–2,000 Hz, 2,000–3,000 Hz, 3,000–4,000 Hz, 4,000–6,000 Hz) and spatial audio processing (inter-channel time difference, delay-and-sum beamforming simulation) to determine whether a multi-pathway architecture can simultaneously pass all five predefined acceptance gates:

| Acceptance Gate | Required Threshold | Baseline Dual-Encoder | Multi-Pathway Fusion (Cand D) | Candidate D Result |
| :--- | :---: | :---: | :---: | :---: |
| **Gate 1: Overall Scream Recall** | $\ge 96.00\%$ | 82.35% (84/102) | **89.22% (91/102)** | **FAIL (-6.78%)** |
| **Gate 2: Hard-Negative FPR** | $\le 5.00\%$ | 6.28% (12/191) | **9.95% (19/191)** | **FAIL (+4.95%)** |
| **Gate 3: Shouted-Speech FPR** | $\le 15.00\%$ | 8.33% (4/48) | **14.58% (7/48)** | **PASS** |
| **Gate 4: Short-Scream Recall (<1.0s)** | $\ge 90.00\%$ | 80.00% (4/5) | **100.00% (5/5)\*** | **PASS\*** |
| **Gate 5: Computational P95 Latency** | $\le 25.00\text{ ms}$ | 18.57 ms | **19.31 ms** | **PASS** |

*\*Note on Gate 4: Sample size is limited to $N=5$ in the independent test cohort; while 5/5 screams were detected, this is statistically under-sampled.*

---

## 2. Key Scientific Findings

1. **Hardware & Corpus Monophonic Constraint:**
   - The documented edge hardware employs a single INMP441 omnidirectional I2S microphone (1 mono channel). Physical beamforming is physically impossible on single-microphone hardware without adding a physical array ($N \ge 2$).
   - 100% of all 1,328 recordings in the corpus (and all 293 in the held-out test cohort) are monophonic (1 channel, 16 kHz).
   - In accordance with scientific integrity rules, physical spatial audio performance on the empirical cohort is classified as **NOT EVALUABLE**.
2. **Frequency Subband Dynamics:**
   - Screams exhibit concentrated energy in 800–1,500 Hz (46.2%) and 2,000–3,000 Hz (11.0%), producing a high $(B_4+B_5)/B_1$ ratio (30.56) compared to cheering (0.28) and shouted speech (0.38).
   - Infant crying closely mirrors scream spectra in static frequency bands (ratio 28.79), confirming that static frequency band analysis alone cannot differentiate crying from screams without temporal pause tracking.
3. **Multi-Pathway Fusion Trade-Off:**
   - Combining deep semantic YAMNet embeddings (1024-d), phonation features (6-d + 6-d mask), and subband features (11-d) in `MultiPathwayFusionModel` increased scream recall to **89.22%** (detecting 91 of 102 screams, a +6.87% advance over baseline).
   - However, the increased sensitivity elevated Hard-Negative false positives to **9.95%** (19/191), driven by harmonic resonance in crowd cheering (7 FP) and shouted speech (7 FP), failing Gate 2 ($\le 5.00\%$).
4. **Spatial Array Simulation (Track B):**
   - Controlled 2-element array simulation ($d = 50\text{ mm}$) showed theoretical SNR enhancements of $+2.1\text{ dB}$ to $+2.7\text{ dB}$.
   - However, at $-5\text{ dB}$ SNR, phase instability induced a **22.5% risk of false steering**, causing Delay-and-Sum beamforming to attenuate the true target by $-1.8\text{ dB}$ to $-3.4\text{ dB}$.
5. **Real-Time Efficiency & Concurrency:**
   - Pipeline P95 inference latency was 19.31 ms (well under the 25.00 ms Gate 5 budget).
   - Multi-stream concurrency testing across 1, 2, 4, and 8 concurrent audio streams incurred **zero 100 ms audio-hop deadline misses**.

---

## 3. Directory Structure & Deliverables

All artifacts are isolated under `backend/research/stage_8_9_35/`:

```
stage_8_9_35/
├── README.md
├── STAGE_PROGRESS.md
├── configs/
│   └── stage_8_9_35_config.json
├── frequency_analysis/
│   └── subband_feature_analysis.csv (1,328 recordings)
├── spatial_analysis/
│   └── spatial_experiment_results.csv (Simulated ULA, GCC-PHAT, DAS)
├── training/
│   ├── mp_fusion_training_history.csv
│   └── validation_threshold_sweep.csv
├── models/
│   └── mp_fusion_model.pt
├── predictions/
│   └── test_predictions_stage8_9_35.csv (N=293 held-out predictions)
├── evaluation/
│   ├── candidate_acceptance_matrix.csv
│   ├── candidate_comparison.csv
│   ├── frequency_feature_results.csv
│   └── short_scream_duration_breakdown.csv
├── performance/
│   ├── latency_distribution.csv
│   └── concurrency_benchmark.csv
├── tests/
│   ├── test_stage_8_9_35.py (10 automated unit & regression tests)
│   └── test_results.txt (10/10 passed)
├── src/
│   ├── reproduce_and_audit_channels.py
│   ├── run_phase1_subband_analysis.py
│   ├── run_phase3_spatial_simulation.py
│   ├── train_and_evaluate_stage8_9_35.py
│   └── run_phase8_performance.py
└── reports/
    ├── stage_8_9_35_executive_summary.md
    ├── stage_8_9_34_reproduction.md
    ├── frequency_band_comparison.md
    ├── subband_feature_analysis.md
    ├── spatial_audio_feasibility.md
    ├── spatial_simulation_report.md
    ├── spatial_frequency_fusion.md
    ├── robustness_report.md
    ├── short_scream_validation.md
    ├── performance_benchmark.md
    ├── final_independent_evaluation.md
    └── production_integrity_report.md
```

---

## 4. Production Immutability Verification

All four frozen production artifacts remain 100% byte-for-byte immutable:
- `backend/models/scream_classifier.joblib`: `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f`
- `backend/models/model_metadata.json`: `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60`
- `backend/reports/test_predictions.csv`: `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d`
- `backend/reports/stage5_test_evaluation.md`: `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2`

---

## 5. Official Determination

Because Candidate D (`MultiPathwayFusionModel`) failed Gate 1 (89.22% vs. $\ge 96.00\%$) and Gate 2 (9.95% vs. $\le 5.00\%$), it cannot be promoted to production.

Official Determination:
### **REJECTED FOR PRODUCTION — RESEARCH ONLY**
