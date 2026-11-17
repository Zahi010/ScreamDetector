# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Stage 8.9.76 Reproducibility & Verification Instructions

**Project:** Festival Scream Detector  
**Stage:** 8.9.76 — Independent Audio Acquisition, Double-Blind Annotation & Label Adjudication  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Date:** 2026-11-14  

---

## 1. System Requirements & Environment

- **Operating System:** Windows 10/11 x64 or Linux x64
- **Python Version:** Python 3.10 to 3.13 (Tested on Python 3.13.3)
- **Audio Libraries:** `soundfile`, `scipy`, `numpy`, `pandas`, `pytest`
- **Shell:** PowerShell or Bash
- **Working Directory:** `c:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector`

---

## 2. Step-by-Step Reproduction Procedure

### Step 1: Protected Baseline Hash Verification
Verify all 6 baseline production and checkpoint hashes:
```powershell
python -c "
import hashlib
files = {
    'classifier': 'backend/models/scream_classifier.joblib',
    'metadata': 'backend/models/model_metadata.json',
    'predictions': 'backend/reports/test_predictions.csv',
    'evaluation': 'backend/reports/stage5_test_evaluation.md',
    'stage60_manifest': 'backend/research/stage_8_9_60/future_evaluation_manifest.json',
    'cand71_frozen': 'backend/research/stage_8_9_76/models/candidate_71_frozen.pt'
}
for k, p in files.items():
    with open(p, 'rb') as f:
        print(f'{k}: {hashlib.sha256(f.read()).hexdigest()[:12]}...')
"
```

### Step 2: Canonical Taxonomy Reconciliation
Inspect and validate the two-tier hierarchical taxonomy (19 primary categories, 6 scream subcategories, 24 leaf classes):
```powershell
python -c "
import json
with open('backend/research/stage_8_9_76/canonical_taxonomy.json', 'r') as f:
    t = json.load(f)
print('Primary Categories:', len(t['primary_categories']))
print('Scream Subcategories:', len(t['scream_subcategories']))
print('Flattened Leaf Classes:', len(t['flattened_leaf_classes']))
"
```

### Step 3: Controlled Audio Acquisition & Lineage Audit
Execute candidate discovery, blacklist filtering (612 historical uploaders), license verification, and 16 kHz mono WAV conversion within the 500 MB quota:
```powershell
python backend/research/stage_8_9_76/scripts/candidate_auditor_and_harvester.py
python backend/research/stage_8_9_76/scripts/lineage_and_progress_builder.py
```
Generated outputs:
- `backend/research/stage_8_9_76/candidate_audit.csv`
- `backend/research/stage_8_9_76/acquisition_decision_log.csv`
- `backend/research/stage_8_9_76/acquisition_provenance.csv`
- `backend/research/stage_8_9_76/acquired_source_group_registry.csv`
- `backend/research/stage_8_9_76/source_lineage_audit.csv`
- `backend/research/stage_8_9_76/acquisition_progress.csv`

### Step 4: Double-Blind Review Queue Staging
Stage assignment tasks for Rater A and Rater B with model predictions stripped:
```powershell
python backend/research/stage_8_9_76/scripts/annotation_workflow_builder.py
```
Generated outputs:
- `backend/research/stage_8_9_76/annotation_assignment_manifest.csv`
- `backend/research/stage_8_9_76/annotation_session_log.csv`
- `backend/research/stage_8_9_76/prospective_cohort_manifest.json`
- `backend/research/stage_8_9_76/evaluation_access_log.csv`

### Step 5: Automated Test Suite Execution
Execute the automated regression test suite:
```powershell
pytest backend/research/stage_8_9_76/tests/test_stage_8_9_76.py -v
```
All 12 tests must pass. Output generated:
- `backend/research/stage_8_9_76/test_results.md`

### Step 6: Frontend Production Build Verification
Verify the frontend builds cleanly without errors:
```powershell
cmd.exe /c "npm --prefix festival-scream-detector/frontend run build"
```

### Step 7: Cryptographic Artifact Hash Verification
Generate and verify SHA-256 digests for all deliverables:
```powershell
python backend/research/stage_8_9_76/scripts/verify_artifact_hashes.py
```
Outputs generated:
- `backend/research/stage_8_9_76/artifact_hashes.json`
- `backend/research/stage_8_9_76/artifact_hashes.sha256`

