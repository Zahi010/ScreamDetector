# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.66 — PROTECTED ARTIFACT HASH AUDIT
**Baseline Integrity Verification Report**

## 1. Safety Designation
Non-certified acoustic research prototype. This system is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

All tests utilize legally acquired recorded audio files and safe playback protocols only.

---

## 2. Audit Summary
Before conducting research in Stage 8.9.66, all 21 protected baseline assets across previous stages (production assets, checkpoints, historical manifests, and sealed cohorts) were verified for bit-for-bit cryptographic integrity using SHA-256.

- **Total Protected Assets:** 21
- **Assets Matched:** 21 / 21 (100.0%)
- **Drift / Mutations Detected:** 0
- **Status:** **ALL 21 ARTIFACTS VERIFIED BIT-FOR-BIT IDENTICAL**

---

## 3. Detailed Cryptographic Manifest

| Asset ID | File Path | Expected SHA-256 | Computed SHA-256 | Verification Status |
|---|---|---|---|---|
| `production_classifier` | `backend/models/scream_classifier.joblib` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | PASS |
| `model_metadata` | `backend/models/model_metadata.json` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | PASS |
| `test_predictions` | `backend/reports/test_predictions.csv` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | PASS |
| `stage5_evaluation` | `backend/reports/stage5_test_evaluation.md` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | PASS |
| `candidate_e1_checkpoint` | `backend/research/stage_8_9_54/training/candidate_e_v954_weighted.pt` | `37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564` | `37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564` | PASS |
| `candidate_b_checkpoint` | `backend/research/stage_8_9_44/models/config_b_mask.pt` | `f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378` | `f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378` | PASS |
| `intervention_d_code` | `backend/research/stage_8_9_49/scripts/whistle_discriminator.py` | `3d98aa7496c6ba89066cfa345a6d0c1ee3605c30821f869a049001c4ad4a8bd2` | `3d98aa7496c6ba89066cfa345a6d0c1ee3605c30821f869a049001c4ad4a8bd2` | PASS |
| `c5_combined_dsp` | `backend/research/stage_8_9_57/dsp_implementations/c5_combined.py` | `d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58` | `d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58` | PASS |
| `original_e1_dsp` | `backend/research/stage_8_9_57/scripts/benchmark_original_dsp.py` | `192e928c6ea427737ef8a3ec4449c890c1d41f01d71c80cefde3f2a0363f5905` | `192e928c6ea427737ef8a3ec4449c890c1d41f01d71c80cefde3f2a0363f5905` | PASS |
| `stage54_partition_manifest` | `backend/research/stage_8_9_54/dataset/partition_manifest_verified.csv` | `10563efcd5d607d1395f9db5ab1aa805a0d9ca39b9b4a64a710816d334caeb9e` | `10563efcd5d607d1395f9db5ab1aa805a0d9ca39b9b4a64a710816d334caeb9e` | PASS |
| `stage60_sealed_manifest` | `backend/research/stage_8_9_60/future_evaluation_manifest.json` | `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd` | `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd` | PASS |
| `duplicate_relationships` | `backend/research/stage_8_9_60/duplicate_and_excerpt_relationships.csv` | `f0e602520e2678b317c0cf82f15cb99304b965e477cec3abe21c6561a18d6dea` | `f0e602520e2678b317c0cf82f15cb99304b965e477cec3abe21c6561a18d6dea` | PASS |
| `stage61_dev_manifest` | `backend/research/stage_8_9_61/rolling_window_development_manifest.csv` | `bdf27fdf663c722c4f312ab273839629884892b2ae1d17fa47e70981400d6e1c` | `bdf27fdf663c722c4f312ab273839629884892b2ae1d17fa47e70981400d6e1c` | PASS |
| `stage61_candidate_freeze` | `backend/research/stage_8_9_61/rolling_window_candidate_freeze.json` | `a56982b014e12697982d927c917f1039de35c72b1dc20a1c9ac61dc74e2275df` | `a56982b014e12697982d927c917f1039de35c72b1dc20a1c9ac61dc74e2275df` | PASS |
| `stage61_preregistration` | `backend/research/stage_8_9_61/independent_evaluation_preregistration.md` | `f6a3c14a1ecd11d783d76f8f27352b577cdb3b6a3f9e4b0724e19f2d58b4248c` | `f6a3c14a1ecd11d783d76f8f27352b577cdb3b6a3f9e4b0724e19f2d58b4248c` | PASS |
| `stage61_sealed_predictions` | `backend/research/stage_8_9_61/sealed_cohort_predictions.csv` | `707e73ca412d3e641ebdf9ff3a447723c46058bd2bbdc5b5eed473fdf42a3689` | `707e73ca412d3e641ebdf9ff3a447723c46058bd2bbdc5b5eed473fdf42a3689` | PASS |
| `stage63_dev_manifest` | `backend/research/stage_8_9_63/stage_63_development_manifest.csv` | `a33e37ecf1bef23bf610baf2a5b42d5e800152dbc518be00a0d4fb5a8229df51` | `a33e37ecf1bef23bf610baf2a5b42d5e800152dbc518be00a0d4fb5a8229df51` | PASS |
| `stage63_short_manifest` | `backend/research/stage_8_9_63/short_scream_acquisition_manifest.csv` | `bf7e2fe9f290c83be23750b683e89c13e738739322f9a4badf13dcd4b937e0c2` | `bf7e2fe9f290c83be23750b683e89c13e738739322f9a4badf13dcd4b937e0c2` | PASS |
| `stage64_dual_res_checkpoint` | `backend/research/stage_8_9_64/models/stage63_dual_resolution_gated.pt` | `4374c5e4abb36e999ee863ae8dcd478f8bfb4e39968331120a211fe181572e34` | `4374c5e4abb36e999ee863ae8dcd478f8bfb4e39968331120a211fe181572e34` | PASS |
| `stage64_short_manifest` | `backend/research/stage_8_9_64/stage_64_short_scream_manifest.csv` | `658ae11fc79154960c6e675ac184ac126808c01c250d0ff354d4bd26a3f04e5b` | `658ae11fc79154960c6e675ac184ac126808c01c250d0ff354d4bd26a3f04e5b` | PASS |
| `stage64_reproduction_csv` | `backend/research/stage_8_9_64/dual_resolution_reproduction.csv` | `f59dd0f84ba51c950738a4d414e01f1354e838257d2a568c40b946b134da1670` | `f59dd0f84ba51c950738a4d414e01f1354e838257d2a568c40b946b134da1670` | PASS |

---

## 4. Conclusion
All historical reference assets remain unmutated and authentic. All research experiments conducted in Stage 8.9.66 are isolated to this stage's directory without altering baseline artifacts.

