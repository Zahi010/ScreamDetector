# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.69 — REPRODUCIBILITY INSTRUCTIONS & RUNBOOK

**Mandatory Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
Non-certified experimental acoustic research system. Not for emergency detection, autonomous dispatch, or critical security deployment.

---

## 1. Environment & Prerequisites

1. **Operating System:** Windows x64 (compatible with Linux/macOS Python environments).
2. **Python Environment:** Python 3.10+ (tested on Python 3.13.3).
3. **Core Dependencies:**
   ```bash
   pip install torch numpy scipy pandas scikit-learn pytest
   ```
4. **Node Environment (for Dashboard UI):**
   ```bash
   node >= 18.0.0
   npm >= 9.0.0
   ```

---

## 2. Step-by-Step Reproduction Pipeline

### Step 1: Verify Protected Assets & Cryptographic Hashes
Run the standalone verification script to confirm all baseline assets, historical models, and sealed evaluation manifest are bit-for-bit identical:
```powershell
python backend/research/stage_8_9_69/scripts/verify_artifact_hashes.py
```
*Expected Output:* `All protected and stage 69 artifacts successfully verified bit-for-bit identical.`

### Step 2: Execute Candidate Tournament & Champion Checkpoint Freeze
Run the full tournament script across Candidates 65-F, 67-D, 68-D, 69-A, 69-B, 69-C, and 69-D:
```powershell
python backend/research/stage_8_9_69/scripts/train_and_evaluate_stage69.py
```
This generates:
- `backend/research/stage_8_9_69/models/candidate_69_frozen.pt` (SHA-256: `d468b75ab12d5ef2b8577c18304e8c4ddaf78f3059b2c0395a1a3263ac6dd92c`)
- `backend/research/stage_8_9_69/models/candidate_69_metadata.json`
- `backend/research/stage_8_9_69/reports/candidate_comparison.csv`
- `backend/research/stage_8_9_69/reports/candidate_69_val_predictions.csv`
- `backend/research/stage_8_9_69/reports/gate_evaluation.md`
- `backend/research/stage_8_9_69/reports/latency_benchmark.md`

### Step 3: Run Comprehensive Automated Test Suite
Execute all 25 unit and integration tests:
```powershell
python -m pytest backend/research/stage_8_9_69/tests/test_stage_8_9_69.py -v
```
*Expected Output:* `25 passed in ~3.6s`.

### Step 4: Verify Dashboard Frontend Build
Compile the frontend to confirm dashboard compatibility:
```cmd
cd frontend
npm run build
```
*Expected Output:* `✓ built in ~250ms`.

---

## 3. Artifact Checksums

| Artifact Path | SHA-256 Checksum | Classification |
| :--- | :--- | :--- |
| `backend/research/stage_8_9_69/models/candidate_69_frozen.pt` | `d468b75ab12d5ef2b8577c18304e8c4ddaf78f3059b2c0395a1a3263ac6dd92c` | Champion Model Checkpoint |
| `backend/models/scream_classifier.joblib` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | Protected Production Baseline |
| `backend/research/stage_8_9_66/models/candidate_65f_frozen.pt` | `06a98025dbdabf462bec305b0cfe8455dd137b3d515cafca8811606865bacfab` | Historical Benchmark 65-F |
| `backend/research/stage_8_9_67/models/candidate_67_frozen.pt` | `8fc2255a337f1375870370216416b94d9c2003a2b8939dbee1301115f53a7b18` | Historical Champion 67-D |
| `backend/research/stage_8_9_68/models/candidate_68_frozen.pt` | `8a3b425a2885cfeeb4d9e6a64c04619949978cad5b55a8a5f60b5ee379949dc4` | Historical Candidate 68-D |
| `backend/research/stage_8_9_60/future_evaluation_manifest.json` | `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd` | Sealed Quarantine Manifest |

