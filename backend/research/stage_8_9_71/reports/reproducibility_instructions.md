# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Stage 8.9.71 — Reproducibility & Forensic Verification Instructions

**Mandatory Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.  
**Research Stage:** Stage 8.9.71  
**Target Execution Environment:** Python 3.10+ / 3.13, PyTorch 2.0+, NumPy, Pandas, Scikit-Learn on Windows / Linux x64.

---

## 1. System Setup & Working Directory

All commands must be executed from the repository root:
```powershell
cd C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector
```

All Stage 8.9.71 research assets reside strictly under:
`backend/research/stage_8_9_71/`

---

## 2. Step-by-Step Reproduction Pipeline

### Step 1: Pre-Stage Integrity Audit
Verify that the 4 production baseline assets and all historical checkpoints are intact:
```powershell
python backend/research/stage_8_9_71/scripts/verify_artifact_hashes.py
```
Expected output: All protected baseline assets and historical checkpoints match bit-for-bit.

### Step 2: Reproduce Candidate 70-D & Audit False Positives
Re-evaluate Candidate 70-D across all statistical dimensions and extract the 12 false positives:
```powershell
python backend/research/stage_8_9_71/scripts/reproduce_candidate70_and_audit.py
```
Outputs:
- Metric confirmation on console (Overall Recall: 82.83%, HN FPR: 9.68%, Shout FPR: 14.77%, Short Recall: 94.87%)
- `backend/research/stage_8_9_71/reports/candidate70_false_positive_forensics.csv` (12 forensic rows)

### Step 3: Run Controlled Experiments, Ablations & Freeze Candidate 71-D
Execute the controlled representation, attenuation, crowd-masking, reverberation, and ablation studies:
```powershell
python backend/research/stage_8_9_71/scripts/run_stage71_experiments.py
```
Outputs:
- `backend/research/stage_8_9_71/reports/low_snr_experiment_results.csv`
- `backend/research/stage_8_9_71/reports/distance_attenuation_experiment_results.csv`
- `backend/research/stage_8_9_71/reports/crowd_masking_experiment_results.csv`
- `backend/research/stage_8_9_71/reports/reverberation_experiment_results.csv`
- `backend/research/stage_8_9_71/reports/veto_ablation_results.csv`
- `backend/research/stage_8_9_71/reports/candidate_comparison.csv`
- `backend/research/stage_8_9_71/models/candidate_71_frozen.pt` (SHA-256: `e4314990...`)
- `backend/research/stage_8_9_71/models/candidate_71_metadata.json`

### Step 4: Run Latency & Streaming Pipeline Benchmarking
Measure model-only forward pass and complete downstream streaming latency across 1,000 iterations:
```powershell
python backend/research/stage_8_9_71/scripts/run_latency_benchmark.py
```
Outputs:
- `backend/research/stage_8_9_71/reports/latency_benchmark.md`

### Step 5: Execute Automated PyTest Regression Suite
Run the expanded automated test suite covering safety headers, protected baseline hashes, checkpoint integrity, metadata, veto ablation logic, streaming buffers, and latency:
```powershell
python -m pytest backend/research/stage_8_9_71/tests/test_stage_8_9_71.py -v
```

### Step 6: Verify Final Artifact Hash Manifest
Re-run the cryptographic cataloger to ensure all artifacts match their recorded SHA-256 hashes:
```powershell
python backend/research/stage_8_9_71/scripts/verify_artifact_hashes.py
```
Outputs:
- `backend/research/stage_8_9_71/reports/artifact_hashes.json`
- `backend/research/stage_8_9_71/reports/artifact_hashes.sha256`

