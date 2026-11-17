# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.67 PRODUCTION INTEGRITY REPORT: Protected Asset Audit, Cryptographic Verification & Sealed Cohort Isolation

**Safety Designation:** Non-certified experimental acoustic research prototype. Prohibited for life-safety alerting, emergency dispatch, police notification, active-shooter systems, or critical security operations. Safe recorded-audio playback only.

---

## 1. Executive Summary & Integrity Certification

A core requirement of Stage 8.9.67 governance is the absolute preservation of protected baseline production assets, historical research benchmarks, and the sealed evaluation cohort. Under no circumstances may research experiments overwrite baseline weights, modify historical evaluation reports, or contaminate sealed evaluation cohorts.

This report provides the formal cryptographic hash audit verifying:
1. All four protected baseline production assets match their authoritative SHA-256 signatures bit-for-bit.
2. The historical Candidate 65-F benchmark checkpoint and C5 DSP reference remain unaltered.
3. The Stage 60 sealed evaluation manifest remains cryptographically sealed with zero leakage.
4. Production promotion has NOT occurred.

---

## 2. Protected Baseline Production Asset Audit (Section 14 Compliance)

The four protected production assets established in Stage 5 were verified via cryptographic SHA-256 hashing:

| Asset Description | File Path | Expected SHA-256 Hash | Observed SHA-256 Hash | Status |
| :--- | :--- | :--- | :--- | :---: |
| **Production Model Weights** | `backend/models/scream_classifier.joblib` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | **VERIFIED UNMODIFIED** |
| **Model Metadata** | `backend/models/model_metadata.json` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | **VERIFIED UNMODIFIED** |
| **Test Predictions CSV** | `backend/reports/test_predictions.csv` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | **VERIFIED UNMODIFIED** |
| **Stage 5 Evaluation Report**| `backend/reports/stage5_test_evaluation.md` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | **VERIFIED UNMODIFIED** |

### Integrity Assessment
All four baseline files have matching SHA-256 digests. Zero bytes have been altered or overwritten.

---

## 3. Historical Benchmark & Reference Artifact Integrity

| Reference Asset Description | File Path | Expected SHA-256 Hash | Observed SHA-256 Hash | Status |
| :--- | :--- | :--- | :--- | :---: |
| **Candidate 65-F Frozen Checkpoint** | `backend/research/stage_8_9_66/models/candidate_65f_frozen.pt` | `06a98025dbdabf462bec305b0cfe8455dd137b3d515cafca8811606865bacfab` | `06a98025dbdabf462bec305b0cfe8455dd137b3d515cafca8811606865bacfab` | **VERIFIED UNMODIFIED** |
| **C5 DSP Optimized Module** | `backend/research/stage_8_9_57/dsp_implementations/c5_combined.py` | `d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58` | `d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58` | **VERIFIED UNMODIFIED** |

---

## 4. Sealed Evaluation Cohort Isolation Audit

The 700-recording evaluation cohort constructed in Stage 8.9.60 represents the prospective benchmark for final system validation.

| Metric / Parameter | Value | Compliance Status |
| :--- | :--- | :---: |
| **Manifest Path** | `backend/research/stage_8_9_60/future_evaluation_manifest.json` | Verified |
| **Expected SHA-256** | `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd` | Verified |
| **Observed SHA-256** | `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd` | **MATCH (SEALED)** |
| **Total Cohort Size** | 700 recordings (200 screams, 500 hard negatives) | Verified |
| **Training Set Overlap**| **0 files (0.00%)** | **PASSED (ZERO LEAKAGE)** |
| **Validation Set Overlap**| **0 files (0.00%)** | **PASSED (ZERO LEAKAGE)** |

---

## 5. Candidate 67-D Checkpoint Governance

The newly trained Candidate 67-D model is frozen under cryptographic governance:
- **Model Path:** `backend/research/stage_8_9_67/models/candidate_67_frozen.pt`
- **SHA-256 Hash:** `8fc2255a337f1375870370216416b94d9c2003a2b8939dbee1301115f53a7b18`
- **Metadata Path:** `backend/research/stage_8_9_67/models/candidate_67_metadata.json`
- **Architecture:** `DualResolutionVocalNet_MultiStageVeto` (9,985 parameters)
- **Deployment Status:** **RESEARCH DEMONSTRATION ONLY — NOT PROMOTED TO PRODUCTION**

---

## 6. Formal Integrity Conclusion

Production integrity is 100% intact. All experimental code, newly trained weights, and telemetry caches are strictly partitioned within `backend/research/stage_8_9_67/`. The production baseline continues to operate with its original frozen Logistic Regression model without alteration.
