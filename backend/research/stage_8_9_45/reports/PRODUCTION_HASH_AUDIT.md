# Production Freeze Hash Audit — Stage 8.9.45

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe playback protocols only.

---

## 1. Executive Summary

This audit establishes the pre-stage production freeze verification for Stage 8.9.45. The production model remains the frozen Stage 5 Logistic Regression model trained on YAMNet embeddings with an operating threshold of 0.3500.

All four canonical production artifacts were audited byte-for-byte prior to any experimentation in Stage 8.9.45.

---

## 2. Hash Verification Matrix

| Production Artifact | Expected Canonical SHA-256 | Actual Verified SHA-256 | Pre-Stage Audit Status |
|---|---|---|---|
| `backend/models/scream_classifier.joblib` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | **MATCH (FROZEN)** |
| `backend/models/model_metadata.json` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | **MATCH (FROZEN)** |
| `backend/reports/test_predictions.csv` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | **MATCH (FROZEN)** |
| `backend/reports/stage5_test_evaluation.md` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | **MATCH (FROZEN)** |

---

## 3. Invariant Guarantees

1. The production classifier and its inference thresholds remain completely decoupled from research experimentation.
2. No research models, features, checkpoints, or configs in `backend/research/stage_8_9_45/` modify or overwrite any file in `backend/models/` or `backend/reports/`.
3. These hashes will be re-audited post-stage to verify that zero production mutations occurred during Stage 8.9.45.

