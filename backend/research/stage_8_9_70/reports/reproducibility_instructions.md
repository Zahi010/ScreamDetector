# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Stage 8.9.70 — Reproducibility & Verification Instructions

**Mandatory Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.  
**Research Stage:** Stage 8.9.70  
**Target Environment:** Python 3.10+ / 3.13, PyTorch 2.0+, NumPy, Pandas, Joblib on Windows/Linux x64.

---

## 1. Overview

This document provides exact, end-to-end instructions for reproducing all Stage 8.9.70 results, tables, ablations, candidate checkpoints, and latency benchmarks from scratch.

---

## 2. Directory Layout & Working Directory

All commands must be executed from the repository root:
```powershell
cd C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector
```

All Stage 8.9.70 research assets reside strictly under:
`backend/research/stage_8_9_70/`

---

## 3. Step-by-Step Reproduction Pipeline

### Step 1: Verify Pre-Stage Baseline & Checkpoint Hashes
Confirm that baseline production assets and historical checkpoints are intact:
```powershell
python backend/research/stage_8_9_70/scripts/verify_artifact_hashes.py
```
Expected output: All 5 core integrity hashes match bit-for-bit.

### Step 2: Reproduce Candidate 69-D Metrics & False-Negative Re-Audit
Re-evaluate Candidate 69-D against the Stage 54 validation cohort and generate the multi-label false-negative breakdown:
```powershell
python backend/research/stage_8_9_70/scripts/generate_fn_reaudit.py
```
Output artifact: `backend/research/stage_8_9_70/reports/candidate69_false_negative_reaudit.csv` (26 rows).

### Step 3: Audit 268 Held-Out Short-Scream Provenance & Subgroups
Trace the provenance and evaluate duration subgroups on the 268-clip held-out cohort:
```powershell
python backend/research/stage_8_9_70/scripts/audit_268_recordings.py
```
Output artifact: `backend/research/stage_8_9_70/reports/short_scream_268_subgroup_results.csv` (4 rows).

### Step 4: Run Veto Simplification Ablations (Ablations A–G)
Run the full combinatorial ablation of the heuristic veto pipeline:
```powershell
python backend/research/stage_8_9_70/scripts/ablation_study.py
```
Output artifact: `backend/research/stage_8_9_70/reports/veto_ablation_results.csv` (7 rows).  
*Key finding:* Confirms that Ablation C (No HFCR Veto) produces identical predictions to Ablation A (Full 69-D) across all 311 validation recordings and 268 held-out recordings.

### Step 5: Execute Low-SNR & Reverberation Experiments & Candidate Tournament
Run the experimental interventions and candidate tournament:
```powershell
python backend/research/stage_8_9_70/scripts/run_experiments.py
```
Output artifacts:
- `backend/research/stage_8_9_70/reports/low_snr_experiment_results.csv`
- `backend/research/stage_8_9_70/reports/reverberation_experiment_results.csv`
- `backend/research/stage_8_9_70/reports/candidate_comparison.csv`
- `backend/research/stage_8_9_70/models/candidate_70_frozen.pt`
- `backend/research/stage_8_9_70/models/candidate_70_metadata.json`

### Step 6: Benchmark Model-Only & Complete Pipeline Latency
Measure CPU inference and streaming pipeline latency across 1,000 iterations:
```powershell
python backend/research/stage_8_9_70/scripts/run_latency_benchmark.py
```
Output artifact: `backend/research/stage_8_9_70/reports/latency_benchmark.md`.

### Step 7: Run Automated PyTest Verification Suite
Execute the Stage 8.9.70 test suite covering safety headers, protected hashes, candidate metrics, veto ablations, and sealed manifest quarantine:
```powershell
python -m pytest backend/research/stage_8_9_70/tests/test_stage_8_9_70.py -v
```

---

## 4. Hash Verification Registry

All generated artifacts, scripts, and model checkpoints are cataloged in:
- `backend/research/stage_8_9_70/reports/artifact_hashes.json`
- `backend/research/stage_8_9_70/reports/artifact_hashes.sha256`

