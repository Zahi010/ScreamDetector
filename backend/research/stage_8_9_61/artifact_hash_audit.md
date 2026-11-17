# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.61 — Artifact Cryptographic Hash Audit & Repository Integrity

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary

This report documents the cryptographic integrity audit of all protected project assets, baseline models, historical research artifacts, and newly generated Stage 8.9.61 evaluation files.

To prevent silent model drift, unauthorized retraining, or data tampering, SHA-256 message digests are computed and verified automatically at stage entry, during test execution, and at stage sign-off. All 12 baseline protected artifacts matched their expected reference digests bit-for-bit, confirming absolute repository stability.

---

## 2. Baseline Protected Artifacts Verification (12 Assets)

| Asset Identifier & Relative Path | Expected Reference SHA-256 | Verified Stage 8.9.61 SHA-256 | Verification Status |
| :--- | :--- | :--- | :---: |
| **Production Model**<br>`backend/models/scream_classifier.joblib` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | **VERIFIED IDENTICAL** |
| **Production Metadata**<br>`backend/models/model_metadata.json` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | **VERIFIED IDENTICAL** |
| **Historical Test Predictions**<br>`backend/reports/test_predictions.csv` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | **VERIFIED IDENTICAL** |
| **Historical Evaluation Report**<br>`backend/reports/stage5_test_evaluation.md` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | **VERIFIED IDENTICAL** |
| **Candidate E1 Checkpoint**<br>`backend/research/stage_8_9_54/training/candidate_e_v954_weighted.pt` | `37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564` | `37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564` | **VERIFIED IDENTICAL** |
| **Candidate B Checkpoint**<br>`backend/research/stage_8_9_44/models/config_b_mask.pt` | `f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378` | `f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378` | **VERIFIED IDENTICAL** |
| **Intervention D Script**<br>`backend/research/stage_8_9_49/scripts/whistle_discriminator.py` | `3d98aa7496c6ba89066cfa345a6d0c1ee3605c30821f869a049001c4ad4a8bd2` | `3d98aa7496c6ba89066cfa345a6d0c1ee3605c30821f869a049001c4ad4a8bd2` | **VERIFIED IDENTICAL** |
| **C5 Combined Implementation**<br>`backend/research/stage_8_9_57/dsp_implementations/c5_combined.py` | `d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58` | `d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58` | **VERIFIED IDENTICAL** |
| **Original DSP Benchmark**<br>`backend/research/stage_8_9_57/scripts/benchmark_original_dsp.py` | `192e928c6ea427737ef8a3ec4449c890c1d41f01d71c80cefde3f2a0363f5905` | `192e928c6ea427737ef8a3ec4449c890c1d41f01d71c80cefde3f2a0363f5905` | **VERIFIED IDENTICAL** |
| **Historical Partition Manifest**<br>`backend/research/stage_8_9_54/dataset/partition_manifest_verified.csv` | `10563efcd5d607d1395f9db5ab1aa805a0d9ca39b9b4a64a710816d334caeb9e` | `10563efcd5d607d1395f9db5ab1aa805a0d9ca39b9b4a64a710816d334caeb9e` | **VERIFIED IDENTICAL** |
| **Sealed Evaluation Manifest**<br>`backend/research/stage_8_9_60/future_evaluation_manifest.json` | `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd` | `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd` | **VERIFIED IDENTICAL** |
| **Duplicate Relationships CSV**<br>`backend/research/stage_8_9_60/duplicate_and_excerpt_relationships.csv` | `b2b4ca10ec3f357f8ad86b49265f4ea6c2ce80153beea0f9ca2eb2dbe4a3ff2e` | `b2b4ca10ec3f357f8ad86b49265f4ea6c2ce80153beea0f9ca2eb2dbe4a3ff2e` | **VERIFIED IDENTICAL** |

---

## 3. Newly Generated Stage 8.9.61 Cryptographic Seals

The governance protocol required formal seals prior to unsealing the independent cohort:

1. **Development Manifest Seal:**
   - File: `backend/research/stage_8_9_61/rolling_window_development_manifest.csv`
   - SHA-256: `bdf27fdf663c722c4f312ab273839629884892b2ae1d17fa47e70981400d6e1c`
   - Status: Sealed prior to Track A feature extraction.

2. **Track A Candidate Freeze Seal:**
   - File: `backend/research/stage_8_9_61/rolling_window_candidate_freeze.json`
   - SHA-256: `a56982b014e12697982d927c917f1039de35c72b1dc20a1c9ac61dc74e2275df`
   - Status: Sealed prior to Track B evaluation.

3. **Preregistration Document Seal:**
   - File: `backend/research/stage_8_9_61/independent_evaluation_preregistration.md`
   - SHA-256: `f6a3c14a1ecd11d783d76f8f27352b577cdb3b6a3f9e4b0724e19f2d58b4248c`
   - Status: Sealed and committed prior to evaluating any model on the 700 sealed recordings.

---

## 4. Audit Conclusion

All cryptographic hashes match their documented baselines exactly. There is zero evidence of artifact tampering, file corruption, or unauthorized model mutation.

