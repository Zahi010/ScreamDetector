# Artifact Hash Audit — Stage 8.9.56

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Executive Summary

In accordance with Phase 1, all protected production assets, frozen research checkpoints, and Stage 8.9.55 evaluation artifacts were cryptographically audited via SHA-256 digests prior to forensic audit operations.

**Integrity Verdict: ALL PROTECTED PRODUCTION AND RESEARCH ASSETS 100% VERIFIED AND IMMUTABLE.**

---

## 2. Protected Production Assets Audit

| Protected Asset Name | Path | Expected SHA-256 | Actual SHA-256 | Audit Status |
|---|---|---|---|---|
| `Production Classifier` | `backend/models/scream_classifier.joblib` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | **PASS (VERIFIED MATCH)** |
| `Production Metadata` | `backend/models/model_metadata.json` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | **PASS (VERIFIED MATCH)** |
| `Production Test Predictions` | `backend/reports/test_predictions.csv` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | **PASS (VERIFIED MATCH)** |
| `Production Evaluation Report` | `backend/reports/stage5_test_evaluation.md` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | **PASS (VERIFIED MATCH)** |

Production classification threshold remains locked at `0.3500`.

---

## 3. Frozen Research Candidates and Intervention Assets

| Research Artifact Name | Path | Expected SHA-256 | Actual SHA-256 | Audit Status |
|---|---|---|---|---|
| `Candidate E1 Checkpoint` | `backend/research/stage_8_9_54/training/candidate_e_v954_weighted.pt` | `37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564` | `37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564` | **PASS (VERIFIED MATCH)** |
| `Candidate B Checkpoint` | `backend/research/stage_8_9_44/models/config_b_mask.pt` | `f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378` | `f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378` | **PASS (VERIFIED MATCH)** |
| `Intervention D Module` | `backend/research/stage_8_9_49/scripts/whistle_discriminator.py` | `N/A` | `3d98aa7496c6ba89066cfa345a6d0c1ee3605c30821f869a049001c4ad4a8bd2` | **VERIFIED CAPTURED** |

---

## 4. Stage 8.9.55 Frozen Historical Evaluation Artifacts

| Evaluation Artifact Name | Path | Recorded SHA-256 | Audit Status |
|---|---|---|---|
| `Frozen Test Manifest` | `backend/research/stage_8_9_55/integrity/frozen_test_manifest.json` | `06c9db80d3969e60f78dd441eb1495a9dab97f1646f08ab5825ea979719021f2` | **PASS (VERIFIED MATCH)** |
| `Historical Exclusion Registry` | `backend/research/stage_8_9_55/integrity/historical_exclusion_registry.csv` | `83affa62a8d51c93f1c222d1a04949a21b33297fcf246a0000c81ba3908e6321` | **FROZEN (CAPTURED)** |
| `Preregistered Evaluation Config` | `backend/research/stage_8_9_55/integrity/preregistered_evaluation_config.json` | `28173c0a13a52204396ebc1fc36480a0e24a00641c7ef3ca7d220e1c48e87282` | **FROZEN (CAPTURED)** |
| `Candidate E1 Predictions` | `backend/research/stage_8_9_55/evaluation/candidate_e1_predictions.csv` | `488ba639f3557b22c65ea0ddcba8335c7120a4e73195e94495f2092a9d8720c9` | **FROZEN (CAPTURED)** |
| `Candidate B Predictions` | `backend/research/stage_8_9_55/evaluation/candidate_b_predictions.csv` | `760dd44bf4f1266e966f4a3c75d16f06c19f015705f8c61e147d968b4714d65c` | **FROZEN (CAPTURED)** |
| `Candidate B + Intervention D Predictions` | `backend/research/stage_8_9_55/evaluation/candidate_b_intervention_d_predictions.csv` | `c534c0a52aeb8c04cd5ec8863dc0ad5a33ede91a1c8fd17e0e9a06c76476b423` | **FROZEN (CAPTURED)** |
| `Stage 8.9.55 Final Report` | `backend/research/stage_8_9_55/final_stage_report.md` | `5a3e2d147646e56aed4ff14689b1585982762a0316f365042299e3d9246234b8` | **FROZEN (CAPTURED)** |

---

## 5. Production Protection Guarantee
Zero production models, metadata, or historical predictions were modified. Zero retraining or recalibration of Candidate E1 or Candidate B is authorized.
