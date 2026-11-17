# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Stage 8.9.75 Reproducibility & Verification Instructions

**Project:** Festival Scream Detector  
**Stage:** 8.9.75 — Independent Dataset Acquisition, Annotation Protocol & Prospective Evaluation Preparation  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Date:** 2026-11-14  

---

## 1. System Requirements & Environment

- **Operating System:** Windows 10/11 x64 or Linux x64
- **Python Version:** Python 3.10 to 3.13 (Verified on Python 3.13.3)
- **Shell:** PowerShell or Bash
- **Dependencies:** `pandas`, `numpy`, `pytest`, `joblib`
- **Working Directory:** `c:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector`

---

## 2. Step-by-Step Reproduction Procedure

### Step 1: Protected Baseline Hash Verification
Verify that production assets and the frozen Candidate 71-D checkpoint are intact:
```powershell
python -c "
import hashlib
files = {
    'classifier': 'backend/models/scream_classifier.joblib',
    'metadata': 'backend/models/model_metadata.json',
    'predictions': 'backend/reports/test_predictions.csv',
    'evaluation': 'backend/reports/stage5_test_evaluation.md',
    'stage60_manifest': 'backend/research/stage_8_9_60/future_evaluation_manifest.json',
    'cand71_frozen': 'backend/research/stage_8_9_75/models/candidate_71_frozen.pt'
}
for k, p in files.items():
    with open(p, 'rb') as f:
        print(f'{k}: {hashlib.sha256(f.read()).hexdigest()[:12]}...')
"
```

### Step 2: Master Inventory & Lineage Building
Reconstruct `dataset_inventory.csv` and audit cross-cohort duplicates:
```powershell
python backend/research/stage_8_9_75/scripts/inventory_builder.py
python backend/research/stage_8_9_75/scripts/lineage_and_leakage_auditor.py
```
Outputs generated:
- `backend/research/stage_8_9_75/dataset_inventory.csv`
- `backend/research/stage_8_9_75/source_group_registry.csv`
- `backend/research/stage_8_9_75/duplicate_and_lineage_audit.md`
- `backend/research/stage_8_9_75/dataset_leakage_audit.md`

### Step 3: Gap Analysis & Diversity Metrics
Compute category distributions, HHI concentration, and target quotas:
```powershell
python backend/research/stage_8_9_75/scripts/gap_and_diversity_analyzer.py
```
Outputs generated:
- `backend/research/stage_8_9_75/acquisition_targets.csv`
- `backend/research/stage_8_9_75/dataset_gap_analysis.md`
- `backend/research/stage_8_9_75/source_diversity_report.md`

### Step 4: Acquisition Pipeline & License Quarantine
Execute metadata harvesting with uploader blacklist filtering:
```powershell
python backend/research/stage_8_9_75/scripts/acquire_manifest_and_provenance.py
```
Output generated:
- `backend/research/stage_8_9_75/acquisition_provenance_report.md`

### Step 5: Inter-Rater Reliability & Fixture Validation
Validate Cohen's Kappa, Fleiss' Kappa, and temporal IoU algorithms:
```powershell
python backend/research/stage_8_9_75/inter_rater_reliability.py
```
Output generated:
- `backend/research/stage_8_9_75/annotation_agreement_report.md`

### Step 6: Dataset Partition Manifest Generation
Construct isolated partitions and verify zero source-group overlap:
```powershell
python backend/research/stage_8_9_75/scripts/partition_builder.py
```
Output generated:
- `backend/research/stage_8_9_75/dataset_partition_manifest.json`

### Step 7: Automated Test Suite Execution
Execute the automated regression test suite:
```powershell
pytest backend/research/stage_8_9_75/tests/test_stage_8_9_75.py -v
```
All 11 tests must pass. Output generated:
- `backend/research/stage_8_9_75/test_results.md`

### Step 8: Cryptographic Hash Verification
Generate and verify SHA-256 digests for all deliverables:
```powershell
python backend/research/stage_8_9_75/scripts/verify_artifact_hashes.py
```
Outputs generated:
- `backend/research/stage_8_9_75/artifact_hashes.json`
- `backend/research/stage_8_9_75/artifact_hashes.sha256`

