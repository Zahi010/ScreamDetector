# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
# Stage 8.9.68 — Cryptographic Hash Verification & Dataset Pipeline Integrity Report

**Stage:** 8.9.68 — SNR-Adaptive Roughness Calibration, Recall Recovery & Multi-Class Generalization  
**Scope:** Forensic Auditing of Production Assets, Frozen Checkpoints, Sealed Manifests & Dataset Splits  
**Safety Notice:** Experimental acoustic prototype. Not certified for life-safety alerting, emergency dispatch, or security response.

---

## 1. Executive Summary

This report provides the authoritative cryptographic integrity audit for Stage 8.9.68. Strict governance rules mandate that baseline production models, historical research checkpoints, and sealed evaluation manifests must remain immutable bit-for-bit.

All SHA-256 hashes were calculated directly from binary disk reads using standard SHA-256 digests. Every protected artifact matches its reference signature perfectly with **zero corruption, zero mutation, and zero unauthorized unsealing**.

---

## 2. Protected Baseline Production Assets (Section 12)

The 4 protected production files established in Stage 5 were verified at stage initiation and confirmed unchanged upon stage completion:

| Artifact Path | Reference SHA-256 Digest | Stage 68 Verified Digest | Integrity Status |
| :--- | :--- | :--- | :--- |
| `backend/models/scream_classifier.joblib` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | **VERIFIED BIT-FOR-BIT** |
| `backend/models/model_metadata.json` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | **VERIFIED BIT-FOR-BIT** |
| `backend/reports/test_predictions.csv` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | **VERIFIED BIT-FOR-BIT** |
| `backend/reports/stage5_test_evaluation.md` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | **VERIFIED BIT-FOR-BIT** |

---

## 3. Frozen Research Candidate Checkpoints & DSP Assets

Historical research models and foundational DSP algorithms are preserved for comparative benchmarking:

| Research Artifact Description | Artifact Relative Path | Verified SHA-256 Digest | Role in Stage 68 |
| :--- | :--- | :--- | :--- |
| **Candidate 65-F Checkpoint** | `backend/research/stage_8_9_66/models/candidate_65f_frozen.pt` | `06a98025dbdabf462bec305b0cfe8455dd137b3d515cafca8811606865bacfab` | Historical Benchmark (Gate 3 Failure Ref) |
| **Candidate 67-D Checkpoint** | `backend/research/stage_8_9_67/models/candidate_67_frozen.pt` | `8fc2255a337f1375870370216416b94d9c2003a2b8939dbee1301115f53a7b18` | Previous Champion (Baseline Reference) |
| **Candidate 68-D Checkpoint** | `backend/research/stage_8_9_68/models/candidate_68_frozen.pt` | `8a3b425a2885cfeeb4d9e6a64c04619949978cad5b55a8a5f60b5ee379949dc4` | **Active Research Champion** |
| **C5 Combined DSP Script** | `backend/research/stage_8_9_57/dsp_implementations/c5_combined.py` | `d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58` | Dual-Resolution Subband Feature Extractor |

---

## 4. Sealed Evaluation Cohort Isolation Status

The Stage 60 sealed evaluation cohort ($N=700$, 200 screams, 500 negatives across 453 independent source groups) represents the project's permanent blind benchmark:

- **Manifest File:** `backend/research/stage_8_9_60/future_evaluation_manifest.json`
- **Verified SHA-256:** `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd`
- **Quarantine Check:** Confirmed. The manifest was audited without unsealing or evaluating Candidate 68 on its recordings.
- **Zero-Leakage Assurance:** No features or audio files from the sealed cohort were extracted or used during Stage 68 training, calibration, or tournament selection.

---

## 5. Stage 54 Partition Integrity & Disjointness

- **Manifest Path:** `backend/research/stage_8_9_54/dataset/partition_manifest_verified.csv`
- **SHA-256:** `10563efcd5d607d1395f9db5ab1aa805a0d9ca39b9b4a64a710816d334caeb9e`
- **Training Source Groups ($N=415$):** 1,055 audio recordings.
- **Validation Source Groups ($N=138$):** 311 audio recordings (99 screams, 212 negatives).
- **Source Group Intersection:** Exactly **0** overlapping source groups.
- **Exposure Classification:** `VALIDATION_EXPOSED`. Results on this cohort serve as developmental model-selection evidence, not untouched blind testing.

---

## 6. Artifact Links

- Hash Index: [artifact_hashes.json](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_68/artifact_hashes.json)
- Checkpoint Metadata: [candidate_68_metadata.json](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_68/models/candidate_68_metadata.json)
- Test Suite: [test_stage_8_9_68.py](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_68/tests/test_stage_8_9_68.py)

