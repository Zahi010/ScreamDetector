# Artifact Hash Audit — Stage 8.9.57

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Executive Summary

In accordance with Section 3 of Stage 8.9.57, all protected production assets, frozen research checkpoints,
and historical evaluation manifests were audited via SHA-256 cryptographic digests.

**Audit Verdict: ALL AUDITED ASSETS 100% VERIFIED AND IMMUTABLE**

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

## 4. Historical Evaluation Artifacts

| Artifact Name | Path | Expected SHA-256 | Actual SHA-256 | Audit Status |
|---|---|---|---|---|
| `Stage 8.9.55 Frozen Test Manifest` | `festival-scream-detector/backend/research/stage_8_9_55/integrity/frozen_test_manifest.json` | `06c9db80d3969e60f78dd441eb1495a9dab97f1646f08ab5825ea979719021f2` | `06c9db80d3969e60f78dd441eb1495a9dab97f1646f08ab5825ea979719021f2` | **PASS (VERIFIED MATCH)** |

---

## 5. Production Protection Guarantee
Zero production models, metadata, or historical predictions were modified. Zero retraining or recalibration of Candidate E1 or Candidate B is authorized.
