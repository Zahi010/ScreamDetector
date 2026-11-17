# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.65 — Repository Inventory & Checkpoint Catalog

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary

This inventory documents the protected baseline checkpoints, feature extractors, historical evaluation manifests, and Stage 8.9.64 artifacts preserved for Stage 8.9.65 research.

---

## 2. Protected Baseline Assets & Models

```
Repository Assets Inventory
┌──────────────────────────────────────┬────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────────┐
│ Asset Name                           │ File Path                                              │ SHA-256 Digest                                                   │
├──────────────────────────────────────┼────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────┤
│ Production Classifier                │ backend/models/scream_classifier.joblib                │ ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f │
│ Production Metadata                  │ backend/models/model_metadata.json                     │ 30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60 │
│ Production Test Predictions          │ backend/reports/test_predictions.csv                   │ e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d │
│ Production Stage 5 Report            │ backend/reports/stage5_test_evaluation.md              │ 9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2 │
│ Candidate E1 Checkpoint (Stage 54)   │ backend/research/stage_8_9_54/training/candidate_e...  │ 37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564 │
│ Candidate B Checkpoint (Stage 44)    │ backend/research/stage_8_9_44/models/config_b_mask.pt  │ f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378 │
│ Intervention D Whistle Code          │ backend/research/stage_8_9_49/scripts/whistle_disc...  │ 3d98aa7496c6ba89066cfa345a6d0c1ee3605c30821f869a049001c4ad4a8bd2 │
│ C5 Combined DSP Extractor            │ backend/research/stage_8_9_57/dsp_implementations/c... │ d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58 │
│ Original Candidate E1 DSP            │ backend/research/stage_8_9_57/scripts/benchmark_ori... │ 192e928c6ea427737ef8a3ec4449c890c1d41f01d71c80cefde3f2a0363f5905 │
│ Stage 54 Partition Manifest          │ backend/research/stage_8_9_54/dataset/partition_ma...  │ 10563efcd5d607d1395f9db5ab1aa805a0d9ca39b9b4a64a710816d334caeb9e │
│ Stage 60 Sealed Manifest             │ backend/research/stage_8_9_60/future_evaluation_ma...  │ 9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd │
│ Duplicate Relationships              │ backend/research/stage_8_9_60/duplicate_and_excerp...  │ f0e602520e2678b317c0cf82f15cb99304b965e477cec3abe21c6561a18d6dea │
│ Stage 61 Dev Manifest                │ backend/research/stage_8_9_61/rolling_window_devel...  │ bdf27fdf663c722c4f312ab273839629884892b2ae1d17fa47e70981400d6e1c │
│ Stage 61 Candidate Freeze            │ backend/research/stage_8_9_61/rolling_window_candi...  │ a56982b014e12697982d927c917f1039de35c72b1dc20a1c9ac61dc74e2275df │
│ Stage 61 Preregistration             │ backend/research/stage_8_9_61/independent_evaluati...  │ f6a3c14a1ecd11d783d76f8f27352b577cdb3b6a3f9e4b0724e19f2d58b4248c │
│ Stage 61 Sealed Predictions          │ backend/research/stage_8_9_61/sealed_cohort_predic...  │ 707e73ca412d3e641ebdf9ff3a447723c46058bd2bbdc5b5eed473fdf42a3689 │
│ Stage 63 Dev Manifest                │ backend/research/stage_8_9_63/stage_63_development...  │ a33e37ecf1bef23bf610baf2a5b42d5e800152dbc518be00a0d4fb5a8229df51 │
│ Stage 63 Short Manifest              │ backend/research/stage_8_9_63/short_scream_acquisi...  │ bf7e2fe9f290c83be23750b683e89c13e738739322f9a4badf13dcd4b937e0c2 │
│ Stage 64 Dual-Res Checkpoint         │ backend/research/stage_8_9_64/models/stage63_dual_...  │ 4374c5e4abb36e999ee863ae8dcd478f8bfb4e39968331120a211fe181572e34 │
│ Stage 64 Short Scream Manifest       │ backend/research/stage_8_9_64/stage_64_short_screa...  │ 658ae11fc79154960c6e675ac184ac126808c01c250d0ff354d4bd26a3f04e5b │
│ Stage 64 Reproduction CSV            │ backend/research/stage_8_9_64/dual_resolution_repr...  │ f59dd0f84ba51c950738a4d414e01f1354e838257d2a568c40b946b134da1670 │
└──────────────────────────────────────┴────────────────────────────────────────────────────────┴──────────────────────────────────────────────────────────────────┘
```

