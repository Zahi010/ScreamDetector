# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Stage 8.9.73 — Reproducibility & Forensic Verification Instructions

**Mandatory Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.  
**Research Stage:** Stage 8.9.73  
**Target Execution Environment:** Python 3.10+ / 3.13, PyTorch 2.0+, NumPy, Pandas, Scikit-Learn on Windows / Linux x64.

---

## 1. System Setup & Working Directory

All commands must be executed from the repository root:
```powershell
cd C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector
```

All Stage 8.9.73 research assets reside strictly under:
`backend/research/stage_8_9_73/`

---

## 2. Step-by-Step Reproduction Pipeline

### Step 1: Pre-Stage Integrity Audit
Verify that the 4 production baseline assets, the quarantined sealed prospective manifest, and all historical candidate checkpoints are intact:
```powershell
python backend/research/stage_8_9_73/scripts/verify_artifact_hashes.py
```
Expected output: All protected baseline assets and historical checkpoints match bit-for-bit.

### Step 2: Reproduce Candidate 71-D & Execute Vocalization Discrimination Experiments
Re-evaluate Candidate 71-D across all statistical dimensions, audit all 17 false negatives and 10 false positives, evaluate hierarchical vocalization discrimination, run infant cry and shouted speech discrimination analyses, and execute residual veto ablations:
```powershell
python backend/research/stage_8_9_73/scripts/run_stage73_experiments.py
```
Outputs:
- `backend/research/stage_8_9_73/reports/candidate71_reproduction_audit.md`
- `backend/research/stage_8_9_73/reports/candidate71_false_negative_forensics.csv` (17 forensic rows)
- `backend/research/stage_8_9_73/reports/candidate71_false_positive_forensics.csv` (10 forensic rows)
- `backend/research/stage_8_9_73/reports/hierarchical_architecture_design.md`
- `backend/research/stage_8_9_73/reports/vocalization_discrimination_results.csv`
- `backend/research/stage_8_9_73/reports/infant_cry_vs_scream_results.csv`
- `backend/research/stage_8_9_73/reports/shouted_speech_vs_scream_results.csv`
- `backend/research/stage_8_9_73/reports/whistle_siren_discrimination_results.csv`
- `backend/research/stage_8_9_73/reports/residual_veto_ablation_results.csv`
- `backend/research/stage_8_9_73/reports/synthetic_vs_real_evaluation.md`
- `backend/research/stage_8_9_73/reports/candidate_comparison.csv`

### Step 3: Run CPU Latency & Streaming Pipeline Benchmarks
Benchmark single-stream and multi-stream model inference latency as well as end-to-end downstream processing pipeline:
```powershell
python backend/research/stage_8_9_73/scripts/run_latency_benchmark.py
```
Outputs:
- `backend/research/stage_8_9_73/reports/latency_benchmark.md`

### Step 4: Run Automated Regression Test Suite
Execute the 17-test automated regression suite:
```powershell
python -m pytest backend/research/stage_8_9_73/tests/test_stage_8_9_73.py -v
```
Expected output: 17 passed in < 4.0 seconds.

### Step 5: Verify Hash Catalog
Recompute and verify SHA-256 hashes for all Stage 8.9.73 artifacts:
```powershell
python backend/research/stage_8_9_73/scripts/verify_artifact_hashes.py
```

---

## 3. Strict Safety & Ethical Protocols

- **Prohibited Uses:** No deployment for emergency dispatch, autonomous alerts, police notification, active-shooter systems, or real-world security.
- **Audio Privacy:** Never commit or persist raw unconsented microphone recordings.
- **Data Integrity:** The Stage 60 sealed cohort ($N=700$, SHA-256 `9dfa4ced...`) must remain quarantined, locked, and unopened.

