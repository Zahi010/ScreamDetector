# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.66.1 — CANDIDATE & PRODUCTION ARTIFACT INTEGRITY REPORT
**Cryptographic Verification of Model Checkpoints, DSP Modules, and Protected Production Assets**

## 1. Safety Designation
Non-certified acoustic research prototype. Prohibited for life-safety alerting, emergency dispatch, autonomous external response, police notification, active-shooter alerting, or critical security deployment.

All tests utilize legally acquired recorded audio files and safe playback protocols only.

---

## 2. Executive Summary
This audit evaluated the bit-level integrity of the frozen **Candidate 65-F** research checkpoint, its supporting inference and feature extraction pipelines, and the four protected baseline production assets.

### Verification Highlights:
- **Candidate 65-F Checkpoint:** Full SHA-256 retrieved and confirmed identical to the Stage 8.9.66 frozen artifact:
  `06a98025dbdabf462bec305b0cfe8455dd137b3d515cafca8811606865bacfab`
- **Zero Drift in Candidate 65-F:** Model architecture, weights, thresholds ($\tau = 0.4800$), and suppression constants remain 100% frozen with zero mutation.
- **Production Assets 100% Intact:** All four production baseline assets match their expected SHA-256 hashes bit-for-bit. Zero production promotion occurred.

---

## 3. Candidate 65-F Complete Cryptographic Record

The complete cryptographic record is cataloged in [`reports/candidate_65f_checkpoint_hash_record.json`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_66_1/reports/candidate_65f_checkpoint_hash_record.json):

| Component / Subsystem | Repository Path | Cryptographic SHA-256 Hash | Verification Status |
|---|---|---|---|
| **Frozen PyTorch Checkpoint** | `backend/research/stage_8_9_66/models/candidate_65f_frozen.pt` | `06a98025dbdabf462bec305b0cfe8455dd137b3d515cafca8811606865bacfab` | **MATCHED (Zero Drift)** |
| **Model Metadata & Threshold Record** | `backend/research/stage_8_9_66/models/candidate_freeze_metadata.json` | `a40672a42e3a8d1f38f1ff067cb92b6c45e122b12a25c127f7513d78327944d4` | **MATCHED** |
| **C5 DSP Preprocessor (Feature Engine)** | `backend/research/stage_8_9_57/dsp_implementations/c5_combined.py` | `d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58` | **MATCHED** |
| **Evaluation Inference Pipeline** | `backend/research/stage_8_9_66/scripts/reproduce_candidate_65f.py` | `f78d78161994a76a3f84ca87404dc5d180d6a06d219476029efbfa60cb9d4877` | **MATCHED** |
| **Candidate Freezing Script** | `backend/research/stage_8_9_66/scripts/freeze_evaluation_candidate.py` | `37c39d442774a7d84b1948d892bbb2ebea64c6916aa0b35a94cc69d0e8b2b909` | **MATCHED** |
| **Preregistration Trial Document** | `backend/research/stage_8_9_66/future_evaluation_preregistration.md` | `b8116f817c62baf72b0f9f2f41278dbf30c7158eb4e795b4388922d83b8839d0` | **MATCHED** |

---

## 4. Protected Production Asset Integrity Audit (Section 9)

In compliance with Section 9 of the stage charter, all four protected baseline assets were re-hashed and compared against their immutable baseline standards:

| Production Asset ID | Repository Path | Immutable Expected SHA-256 | Computed SHA-256 | Verification Result |
|---|---|---|---|---|
| **1. Production Scream Classifier** | `backend/models/scream_classifier.joblib` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | **PASS (BIT-EXACT)** |
| **2. Production Model Metadata** | `backend/models/model_metadata.json` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | **PASS (BIT-EXACT)** |
| **3. Historical Test Predictions** | `backend/reports/test_predictions.csv` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | **PASS (BIT-EXACT)** |
| **4. Stage 5 Evaluation Report** | `backend/reports/stage5_test_evaluation.md` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | **PASS (BIT-EXACT)** |

---

## 5. Parameter Immutability Confirmation

The Candidate 65-F checkpoint configuration was verified inside the PyTorch state dictionary:
- **Decision Threshold:** Fixed at $\tau = 0.4800$.
- **High-Confidence Bypass:** Fixed at $p \ge 0.8000$.
- **Branch Latent Cosine Agreement:** Fixed at $\text{sim}(z_s, z_l) > 0.4000$.
- **Whistle Harmonics-to-Noise Veto:** Fixed at $\text{HNR} > 12.00\text{ dB}$.
- **Whistle Spectral Flatness Veto:** Fixed at $\text{Flatness} < 0.0010$.
- **Narrow-band Attenuation Factor:** Multiplier $0.1500$.

Zero weights, gradients, or hyperparameters were altered during Stage 8.9.66.1.

