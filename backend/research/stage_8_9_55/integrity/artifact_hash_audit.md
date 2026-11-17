# Artifact Hash Audit — Stage 8.9.55

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Protected Production and Reference Artifact Verification

| Artifact Name | Path | Status | Expected SHA-256 | Actual SHA-256 |
|---|---|---|---|---|
| `scream_classifier.joblib` | `backend/models/scream_classifier.joblib` | **PASS** | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` |
| `model_metadata.json` | `backend/models/model_metadata.json` | **PASS** | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` |
| `test_predictions.csv` | `backend/reports/test_predictions.csv` | **PASS** | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` |
| `stage5_test_evaluation.md` | `backend/reports/stage5_test_evaluation.md` | **PASS** | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` |
| `config_b_mask.pt` (Candidate B) | `backend/research/stage_8_9_44/models/config_b_mask.pt` | **PASS** | `f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378` | `f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378` |
| `candidate_e_v954_weighted.pt` (Candidate E1) | `backend/research/stage_8_9_54/training/candidate_e_v954_weighted.pt` | **PASS** | `37fa77b4cd4cb04c3e3902347b7a69b764b85da845cfb22e1a3bcdaee94f9243` | `37fa77b4cd4cb04c3e3902347b7a69b764b85da845cfb22e1a3bcdaee94f9243` |

---

## 2. Stage 8.9.55 Cohort & Evaluation Integrity Manifest

| Artifact Name | Relative Path | SHA-256 Digest | Status |
|---|---|---|---|
| `frozen_test_manifest.json` | `backend/research/stage_8_9_55/integrity/frozen_test_manifest.json` | `06c9db80d3969e60f78dd441eb1495a9dab97f1646f08ab5825ea979719021f2` | **LOCKED & QUARANTINED** |
| `historical_exclusion_registry.csv` | `backend/research/stage_8_9_55/integrity/historical_exclusion_registry.csv` | `83affa62a8d51c93f1c222d1a04949a21b33297fcf246a0000c81ba3908e6321` | **LOCKED (2,213 exclusions)** |
| `preregistered_evaluation_config.json` | `backend/research/stage_8_9_55/integrity/preregistered_evaluation_config.json` | `28173c0a13a52204396ebc1fc36480a0e24a00641c7ef3ca7d220e1c48e87282` | **PRE-REGISTERED** |

Zero production assets or historical research checkpoints were modified.
