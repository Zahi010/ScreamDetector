# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.65 — Protected Baseline Asset Integrity Audit Report

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary

Prior to initiating research in Stage 8.9.65, all 21 protected baseline assets—comprising production deployment artifacts, historical model checkpoints, verified DSP extractors, sealed evaluation manifests, and Stage 8.9.64 dual-resolution artifacts—were audited for cryptographic integrity via SHA-256 digests.

**Result: 21 of 21 assets verified bit-for-bit (100% compliance, 0 bit drift).**

The authoritative hashes are committed in [`artifact_hashes.json`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/artifact_hashes.json).

---

## 2. Production Asset Freeze Verification

```
Production Asset Hash Audit
┌──────────────────────────────────────────────┬──────────────────────────────────────────────────────────────────┬────────────┐
│ Protected Asset                              │ Authoritative SHA-256 Digest                                     │ Status     │
├──────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────┼────────────┤
│ backend/models/scream_classifier.joblib      │ ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f │ MATCH [OK] │
│ backend/models/model_metadata.json           │ 30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60 │ MATCH [OK] │
│ backend/reports/test_predictions.csv         │ e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d │ MATCH [OK] │
│ backend/reports/stage5_test_evaluation.md    │ 9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2 │ MATCH [OK] │
└──────────────────────────────────────────────┴──────────────────────────────────────────────────────────────────┴────────────┘
```

Zero modifications to production assets are authorized. All production assets remain strictly frozen.

