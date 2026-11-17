# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Stage 8.9.74 — Reproducibility & Forensic Verification Instructions

**Mandatory Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.  
**Research Stage:** Stage 8.9.74  
**Target Execution Environment:** Python 3.10+ / 3.13, PyTorch 2.0+, NumPy, Pandas, Scikit-Learn on Windows / Linux x64.

---

## 1. System Setup & Working Directory

All commands must be executed from the repository root:
```powershell
cd C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector
```

All Stage 8.9.74 research assets reside strictly under:
`backend/research/stage_8_9_74/`

---

## 2. Step-by-Step Reproduction Pipeline

### Step 1: Pre-Stage Integrity Audit
Verify that the 4 production baseline assets, the Stage 60 manifest, and all historical candidate checkpoints are intact:
```powershell
python backend/research/stage_8_9_74/scripts/verify_artifact_hashes.py
```
Expected output: All protected baseline assets and historical checkpoints match bit-for-bit.

### Step 2: Execute Provenance Reconciliation & Forensic Audits
Generate candidate metric reconciliations, vocalization label review queues, distress veto case comparisons, and SNR-stratified analysis tables:
```powershell
python backend/research/stage_8_9_74/scripts/run_stage74_reconciliation.py
```
Outputs:
- `backend/research/stage_8_9_74/candidate_metric_reconciliation.csv`
- `backend/research/stage_8_9_74/vocalization_label_review.csv` (40 audited error rows)
- `backend/research/stage_8_9_74/annotation_ambiguity_summary.csv`
- `backend/research/stage_8_9_74/distress_veto_case_comparison.csv`
- `backend/research/stage_8_9_74/targeted_veto_ablation_results.csv`
- `backend/research/stage_8_9_74/snr_stratified_results.csv`

### Step 3: Run CPU Latency & Streaming Pipeline Benchmarks
Benchmark single-stream and multi-stream model inference latency as well as end-to-end downstream processing pipeline:
```powershell
python backend/research/stage_8_9_74/scripts/run_latency_benchmark.py
```
Outputs:
- `backend/research/stage_8_9_74/latency_benchmark.md`

### Step 4: Run Automated Regression Test Suite
Execute the 11-test automated regression suite:
```powershell
python -m pytest backend/research/stage_8_9_74/tests/test_stage_8_9_74.py -v
```
Expected output: 11 passed in < 4.0 seconds.

### Step 5: Verify Hash Catalog
Recompute and verify SHA-256 hashes for all Stage 8.9.74 artifacts:
```powershell
python backend/research/stage_8_9_74/scripts/verify_artifact_hashes.py
```

---

## 3. Strict Safety & Ethical Protocols

- **Prohibited Uses:** No deployment for emergency dispatch, autonomous alerts, police notification, active-shooter systems, or real-world security.
- **Audio Privacy:** Never commit or persist raw unconsented microphone recordings.
- **Data Integrity:** The Stage 60 cohort is classified as `CONFIRMED_PREVIOUSLY_ACCESSED` (evaluated in Stage 61) and must not be used as a pristine prospective test set.

