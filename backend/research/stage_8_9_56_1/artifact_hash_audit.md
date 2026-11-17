# Artifact Hash Audit — Stage 8.9.56.1

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Executive Summary

In accordance with Phase 1 & 9 of Stage 8.9.56.1, all protected production assets, frozen research checkpoints,
Stage 8.9.55 frozen evaluation artifacts, and Stage 8.9.56 audit records were audited via SHA-256 digests.

**Audit Status: ALL AUDITED ASSETS 100% VERIFIED AND IMMUTABLE**

---

## 2. Protected Production Assets Audit

| Protected Asset Name | Path | Expected SHA-256 | Actual SHA-256 | Audit Status |
|---|---|---|---|---|
| `Production Classifier` | `festival-scream-detector/backend/models/scream_classifier.joblib` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | **PASS (VERIFIED MATCH)** |
| `Production Metadata` | `festival-scream-detector/backend/models/model_metadata.json` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | **PASS (VERIFIED MATCH)** |
| `Production Test Predictions` | `festival-scream-detector/backend/reports/test_predictions.csv` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | **PASS (VERIFIED MATCH)** |
| `Production Evaluation Report` | `festival-scream-detector/backend/reports/stage5_test_evaluation.md` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | **PASS (VERIFIED MATCH)** |

Production classification threshold remains locked at `0.3500`.

---

## 3. Frozen Research Candidates and Intervention Assets

| Research Artifact Name | Path | Expected SHA-256 | Actual SHA-256 | Audit Status |
|---|---|---|---|---|
| `Candidate E1 Checkpoint` | `festival-scream-detector/backend/research/stage_8_9_54/training/candidate_e_v954_weighted.pt` | `37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564` | `37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564` | **PASS (VERIFIED MATCH)** |
| `Candidate B Checkpoint` | `festival-scream-detector/backend/research/stage_8_9_44/models/config_b_mask.pt` | `f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378` | `f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378` | **PASS (VERIFIED MATCH)** |
| `Intervention D Module` | `festival-scream-detector/backend/research/stage_8_9_49/scripts/whistle_discriminator.py` | `3d98aa7496c6ba89066cfa345a6d0c1ee3605c30821f869a049001c4ad4a8bd2` | `3d98aa7496c6ba89066cfa345a6d0c1ee3605c30821f869a049001c4ad4a8bd2` | **PASS (VERIFIED MATCH)** |

---

## 4. Stage 8.9.55 Frozen Historical Evaluation Artifacts

| Evaluation Artifact Name | Path | Recorded SHA-256 | Actual SHA-256 | Audit Status |
|---|---|---|---|---|
| `Stage 8.9.55 Frozen Test Manifest` | `festival-scream-detector/backend/research/stage_8_9_55/integrity/frozen_test_manifest.json` | `06c9db80d3969e60f78dd441eb1495a9dab97f1646f08ab5825ea979719021f2` | `06c9db80d3969e60f78dd441eb1495a9dab97f1646f08ab5825ea979719021f2` | **PASS (VERIFIED MATCH)** |
| `Historical Exclusion Registry` | `festival-scream-detector/backend/research/stage_8_9_55/integrity/historical_exclusion_registry.csv` | `83affa62a8d51c93f1c222d1a04949a21b33297fcf246a0000c81ba3908e6321` | `83affa62a8d51c93f1c222d1a04949a21b33297fcf246a0000c81ba3908e6321` | **PASS (VERIFIED MATCH)** |
| `Preregistered Evaluation Config` | `festival-scream-detector/backend/research/stage_8_9_55/integrity/preregistered_evaluation_config.json` | `28173c0a13a52204396ebc1fc36480a0e24a00641c7ef3ca7d220e1c48e87282` | `28173c0a13a52204396ebc1fc36480a0e24a00641c7ef3ca7d220e1c48e87282` | **PASS (VERIFIED MATCH)** |
| `Candidate E1 Predictions` | `festival-scream-detector/backend/research/stage_8_9_55/evaluation/candidate_e1_predictions.csv` | `488ba639f3557b22c65ea0ddcba8335c7120a4e73195e94495f2092a9d8720c9` | `488ba639f3557b22c65ea0ddcba8335c7120a4e73195e94495f2092a9d8720c9` | **PASS (VERIFIED MATCH)** |
| `Candidate B Predictions` | `festival-scream-detector/backend/research/stage_8_9_55/evaluation/candidate_b_predictions.csv` | `760dd44bf4f1266e966f4a3c75d16f06c19f015705f8c61e147d968b4714d65c` | `760dd44bf4f1266e966f4a3c75d16f06c19f015705f8c61e147d968b4714d65c` | **PASS (VERIFIED MATCH)** |
| `Candidate B + Intervention D Predictions` | `festival-scream-detector/backend/research/stage_8_9_55/evaluation/candidate_b_intervention_d_predictions.csv` | `c534c0a52aeb8c04cd5ec8863dc0ad5a33ede91a1c8fd17e0e9a06c76476b423` | `c534c0a52aeb8c04cd5ec8863dc0ad5a33ede91a1c8fd17e0e9a06c76476b423` | **PASS (VERIFIED MATCH)** |
| `Stage 8.9.55 Final Report` | `festival-scream-detector/backend/research/stage_8_9_55/final_stage_report.md` | `5a3e2d147646e56aed4ff14689b1585982762a0316f365042299e3d9246234b8` | `5a3e2d147646e56aed4ff14689b1585982762a0316f365042299e3d9246234b8` | **PASS (VERIFIED MATCH)** |

---

## 5. Stage 8.9.56 Audit Artifacts Baseline

| Audit Artifact Name | Path | Recorded SHA-256 | Audit Status |
|---|---|---|---|
| `Stage 8.9.56 Latency Component Measurements` | `festival-scream-detector/backend/research/stage_8_9_56/latency_component_measurements.csv` | `7e41f6d6b1a2ea1cac4e1271fa68a84d4ea7fe60d53b3e70b205c92590f1e6c8` | **VERIFIED CAPTURED** |
| `Stage 8.9.56 Acceptance Gate Reconciliation` | `festival-scream-detector/backend/research/stage_8_9_56/acceptance_gate_reconciliation.md` | `736b4e98c16ce9f61910453748918719a9c6abdeeaddc32b3b4a2aea7d6940c5` | **VERIFIED CAPTURED** |
| `Stage 8.9.56 Final Report` | `festival-scream-detector/backend/research/stage_8_9_56/final_stage_report.md` | `dd19d9495750ef250a7c0b172b367e9353472b54a2139008d84975bf6d6be3b7` | **VERIFIED CAPTURED** |

---

## 6. Production Protection Guarantee
Zero production models, metadata, or historical predictions were modified. Zero retraining or recalibration of Candidate E1 or Candidate B is authorized.
