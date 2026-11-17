# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.63 — Artifact Cryptographic Hash Verification Report

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Audit Overview

This document certifies the initial cryptographic hash audit for Stage 8.9.63, executed using [`scripts/verify_artifact_hashes.py`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_63/scripts/verify_artifact_hashes.py).

- **Execution Date:** 2026-11-11
- **Audit Tool:** SHA-256 standard cryptographic digest
- **Audit Target:** 16 critical assets (production models, historical checkpoints, DSP modules, and sealed evaluation records)
- **Result:** **100% MATCH — ZERO BIT DRIFT DETECTED**

---

## 2. Cryptographic Hash Ledger

```json
{
  "production_classifier": {
    "path": "backend/models/scream_classifier.joblib",
    "sha256": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "status": "VERIFIED"
  },
  "model_metadata": {
    "path": "backend/models/model_metadata.json",
    "sha256": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "status": "VERIFIED"
  },
  "test_predictions": {
    "path": "backend/reports/test_predictions.csv",
    "sha256": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    "status": "VERIFIED"
  },
  "stage5_evaluation": {
    "path": "backend/reports/stage5_test_evaluation.md",
    "sha256": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
    "status": "VERIFIED"
  },
  "candidate_e1_checkpoint": {
    "path": "backend/research/stage_8_9_54/training/candidate_e_v954_weighted.pt",
    "sha256": "37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564",
    "status": "VERIFIED"
  },
  "candidate_b_checkpoint": {
    "path": "backend/research/stage_8_9_44/models/config_b_mask.pt",
    "sha256": "f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378",
    "status": "VERIFIED"
  },
  "intervention_d_code": {
    "path": "backend/research/stage_8_9_49/scripts/whistle_discriminator.py",
    "sha256": "3d98aa7496c6ba89066cfa345a6d0c1ee3605c30821f869a049001c4ad4a8bd2",
    "status": "VERIFIED"
  },
  "c5_combined_dsp": {
    "path": "backend/research/stage_8_9_57/dsp_implementations/c5_combined.py",
    "sha256": "d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58",
    "status": "VERIFIED"
  },
  "original_e1_dsp": {
    "path": "backend/research/stage_8_9_57/scripts/benchmark_original_dsp.py",
    "sha256": "192e928c6ea427737ef8a3ec4449c890c1d41f01d71c80cefde3f2a0363f5905",
    "status": "VERIFIED"
  },
  "stage54_partition_manifest": {
    "path": "backend/research/stage_8_9_54/dataset/partition_manifest_verified.csv",
    "sha256": "10563efcd5d607d1395f9db5ab1aa805a0d9ca39b9b4a64a710816d334caeb9e",
    "status": "VERIFIED"
  },
  "stage60_sealed_manifest": {
    "path": "backend/research/stage_8_9_60/future_evaluation_manifest.json",
    "sha256": "9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd",
    "status": "VERIFIED"
  },
  "duplicate_relationships": {
    "path": "backend/research/stage_8_9_60/duplicate_and_excerpt_relationships.csv",
    "sha256": "f0e602520e2678b317c0cf82f15cb99304b965e477cec3abe21c6561a18d6dea",
    "status": "VERIFIED"
  },
  "stage61_dev_manifest": {
    "path": "backend/research/stage_8_9_61/rolling_window_development_manifest.csv",
    "sha256": "bdf27fdf663c722c4f312ab273839629884892b2ae1d17fa47e70981400d6e1c",
    "status": "VERIFIED"
  },
  "stage61_candidate_freeze": {
    "path": "backend/research/stage_8_9_61/rolling_window_candidate_freeze.json",
    "sha256": "a56982b014e12697982d927c917f1039de35c72b1dc20a1c9ac61dc74e2275df",
    "status": "VERIFIED"
  },
  "stage61_preregistration": {
    "path": "backend/research/stage_8_9_61/independent_evaluation_preregistration.md",
    "sha256": "f6a3c14a1ecd11d783d76f8f27352b577cdb3b6a3f9e4b0724e19f2d58b4248c",
    "status": "VERIFIED"
  },
  "stage61_sealed_predictions": {
    "path": "backend/research/stage_8_9_61/sealed_cohort_predictions.csv",
    "sha256": "707e73ca412d3e641ebdf9ff3a447723c46058bd2bbdc5b5eed473fdf42a3689",
    "status": "VERIFIED"
  }
}
```

---

## 3. Governance Finding

All protected assets are identical to their historical references. No drift, corruption, or unauthorized modification has occurred.

