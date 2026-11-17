# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.67: Five-Gate Generalization Recovery, Independent Dataset Validation & Live Web Dashboard Integration

**Safety Designation:** Non-certified experimental acoustic research prototype. Prohibited for life-safety alerting, emergency dispatch, police notification, active-shooter systems, or critical security operations. Safe recorded-audio playback only.

---

## 1. Directory Structure

```
stage_8_9_67/
├── STAGE_PROGRESS.md                  # Comprehensive stage milestone ledger (100% complete)
├── README.md                          # Directory navigation and reproducibility instructions
├── models/
│   ├── candidate_67_frozen.pt         # Champion Candidate 67-D weights (SHA-256: 8fc2255a...)
│   └── candidate_67_metadata.json     # Hyperparameters, architecture, and gate results
├── reports/
│   ├── stage_8_9_67_completion_report.md
│   ├── stage_8_9_67_dataset_provenance_report.md
│   ├── stage_8_9_67_shouted_speech_analysis.md
│   ├── stage_8_9_67_hard_negative_analysis.md
│   ├── stage_8_9_67_positive_generalization_report.md
│   ├── stage_8_9_67_short_scream_report.md
│   ├── stage_8_9_67_candidate_comparison.md
│   ├── stage_8_9_67_five_gate_scorecard.md
│   ├── stage_8_9_67_latency_report.md
│   ├── stage_8_9_67_dashboard_integration_report.md
│   ├── stage_8_9_67_production_integrity_report.md
│   ├── stage_8_9_67_test_report.md
│   ├── candidate_67_val_predictions.csv
│   └── candidate_65f_val_predictions.csv
├── scripts/
│   ├── verify_artifact_hashes.py      # Cryptographic SHA-256 baseline verifier
│   ├── extract_and_cache_features.py  # C5 DSP + Vocal feature extraction pipeline
│   └── train_and_evaluate_candidates.py # Multi-candidate training & tournament runner
├── cache/
│   ├── train_features.npz             # Cached expansion_train features (N=1,055)
│   ├── val_features.npz               # Cached expansion_val features (N=311)
│   └── held_out_short_features.npz    # Cached Stage 64 held-out short screams (N=268)
└── tests/
    └── test_stage_8_9_67.py           # Comprehensive pytest automated verification suite
```

---

## 2. Five-Gate Validation Summary (Stage 54 Independent Validation $N=311$)

| Gate | Description | Criteria | Target | Candidate 65-F | Candidate 67-D (Champion) | Status |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **Gate 1** | Overall Scream Recall | Sensitivity | $\ge 96.00\%$ | 86.87% | **73.74%** | **FAIL** |
| **Gate 2** | Hard-Negative FPR | Selectivity | $\le 5.00\%$ | 59.68% | **8.87%** | **FAIL** |
| **Gate 3** | Shouted-Speech FPR | Vocal Selectivity | $\le 15.00\%$ | 48.86% | **13.64%** | **PASS** |
| **Gate 4** | Short-Scream Recall ($<1.0$s) | Transient Sensitivity | $\ge 90.00\%$ | 97.44% | **92.31%** | **PASS** |
| **Gate 5** | Neural Model-Only P95 Latency | Computational Speed | $\le 25.00$ ms | 0.812 ms | **0.397 ms** | **PASS** |

### Authoritative Verdicts
- **Research Model Verdict:** **`PARTIAL IMPROVEMENT — ONE OR MORE GATES FAILED`** (Gates 3, 4, 5 Passed; Gates 1, 2 Failed).
- **Live Dashboard Verdict:** **`INTEGRATED — RECORDED AUDIO VERIFIED`** (Full live dashboard built, backend endpoints verified via automated tests, recorded audio and presets verified).

---

## 3. How to Run & Reproduce

### 1. Verify Cryptographic Baseline Asset Hashes
```bash
python backend/research/stage_8_9_67/scripts/verify_artifact_hashes.py
```

### 2. Run Automated Verification Test Suite
```bash
cd festival-scream-detector/backend
python -m pytest research/stage_8_9_67/tests/test_stage_8_9_67.py tests/test_stage_8_9_67_backend.py -v
```

### 3. Launch Live Web Research Dashboard
```bash
# Terminal 1: Backend
cd festival-scream-detector/backend
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Frontend
cd festival-scream-detector/frontend
npm run dev
```
Navigate to `http://localhost:5173` and click the **Research (8.9.67)** tab in the top navigation header.

