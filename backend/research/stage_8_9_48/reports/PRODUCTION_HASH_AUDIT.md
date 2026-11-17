# Production Freeze Hash Audit — Stage 8.9.48 (PRE-STAGE)

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.

---

## 1. Executive Summary

This audit verifies that the frozen production model (Stage 5 Logistic Regression, threshold `0.3500`) and its associated evaluation artifacts remain completely unmodified and byte-identical before and throughout Stage 8.9.48.

- **Audit Status:** **VERIFIED PASS (ALL HASHES MATCH EXACTLY)**
- **Production Architecture:** Logistic Regression on 1024-dim YAMNet Embeddings
- **Production Threshold:** `0.3500` (FROZEN)

---

## 2. Canonical Hash Verification Table

| Production Artifact | Expected Canonical SHA-256 | Actual Observed SHA-256 | Status |
| :--- | :--- | :--- | :---: |
| `backend/models/scream_classifier.joblib` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | **MATCH** |
| `backend/models/model_metadata.json` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | **MATCH** |
| `backend/reports/test_predictions.csv` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | **MATCH** |
| `backend/reports/stage5_test_evaluation.md` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | **MATCH** |

---

## 3. Immutability Protocol & Boundary Guarantees

1. **Isolation of Research Checkpoints:** All Stage 8.9.47 and Stage 8.9.48 checkpoints, calibrators, and analysis records reside strictly under `backend/research/` and do not touch `backend/models/`.
2. **Threshold Segregation:** The production operating threshold remains fixed at `0.3500`. Research candidate thresholds (Candidate B: 0.8000, Candidate R5: 0.8700) are isolated within research configuration manifests.
3. **Emergency Brake:** Any modification to canonical production files halts execution immediately.
