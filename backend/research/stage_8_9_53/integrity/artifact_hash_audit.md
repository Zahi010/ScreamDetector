# Artifact Hash Audit — Stage 8.9.53

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

---

## 1. Frozen Artifact Verification Table

| Artifact Name | Path | Status | Expected SHA-256 | Actual SHA-256 |
|---|---|---|---|---|
| `scream_classifier.joblib` | `backend\models\scream_classifier.joblib` | **PASS** | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` |
| `model_metadata.json` | `backend\models\model_metadata.json` | **PASS** | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` |
| `test_predictions.csv` | `backend\reports\test_predictions.csv` | **PASS** | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` |
| `stage5_test_evaluation.md` | `backend\reports\stage5_test_evaluation.md` | **PASS** | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` |
| `config_b_mask.pt` | `backend\research\stage_8_9_44\models\config_b_mask.pt` | **PASS** | `f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378` | `f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378` |
| `research_exp_candidate.pt` | `backend\research\stage_8_9_51\models\research_exp_candidate.pt` | **PASS** | `5ec5941448af4d3c77417a96e0ee5da5d8592ef5bc3c1103d3518378b37d13c1` | `5ec5941448af4d3c77417a96e0ee5da5d8592ef5bc3c1103d3518378b37d13c1` |

## 2. Freeze Status
All 4 canonical production assets and both research baseline checkpoints (`config_b_mask.pt` and `research_exp_candidate.pt`) match their bit-level cryptographic digests exactly. Zero modifications have occurred.
