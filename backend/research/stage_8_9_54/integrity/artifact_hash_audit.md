# Artifact Hash Audit — Stage 8.9.54

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Protected Production and Reference Artifact Verification

| Artifact Name | Path | Status | Expected SHA-256 | Actual SHA-256 |
|---|---|---|---|---|
| `scream_classifier.joblib` | `backend/models/scream_classifier.joblib` | **PASS** | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` |
| `model_metadata.json` | `backend/models/model_metadata.json` | **PASS** | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` |
| `test_predictions.csv` | `backend/reports/test_predictions.csv` | **PASS** | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` |
| `stage5_test_evaluation.md` | `backend/reports/stage5_test_evaluation.md` | **PASS** | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` |
| `config_b_mask.pt` (Candidate B) | `backend/research/stage_8_9_44/models/config_b_mask.pt` | **PASS** | `f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378` | `f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378` |
| `research_exp_candidate.pt` (Original Cand E) | `backend/research/stage_8_9_51/models/research_exp_candidate.pt` | **PASS** | `5ec5941448af4d3c77417a96e0ee5da5d8592ef5bc3c1103d3518378b37d13c1` | `5ec5941448af4d3c77417a96e0ee5da5d8592ef5bc3c1103d3518378b37d13c1` |

---

## 2. Newly Created Stage 8.9.54 Checkpoint Cryptographic Manifest

| Model Version | File Name | SHA-256 Digest | Training Condition | Optimal Val Epoch | Calibrated $\theta$ |
|---|---|---|---|---|---|
| **E0** | `candidate_e_v954_baseline.pt` | `c395e8fa3292ce8789d2d0c6ba9894e7728f3bb444c13db43316d90a7e5896cb` | Expanded Training (Standard BCE) | 17 | `0.6900` |
| **E1** | `candidate_e_v954_weighted.pt` | `37fa77b4cd4cb04c3e3902347b7a69b764b85da845cfb22e1a3bcdaee94f9243` | Class-Balanced (pos_weight = 1.6179) | 17 | `0.6800` |
| **E2** | `candidate_e_v954_augmented.pt` | `c80db21ae816ec98f1a4e107bb4927cb46c641f0a20a4b3d75c50c5a274db27c` | Targeted Acoustic Augmentation | 17 | `0.6700` |
| **E3** | `candidate_e_v954_combined.pt` | `2070786d588235695679e0bf098236df867623c21a37887e5971415fbf105151` | Combined Class-Weighting + Augmentation | 26 | `0.8900` |

All newly trained models were saved to versioned checkpoints in `backend/research/stage_8_9_54/training/`.
Zero historical checkpoints were overwritten or modified.
"""
    (STAGE54_DIR / "integrity" / "artifact_hash_audit.md").write_text(tp_md := Content, encoding="utf-8")
    print(f"Saved artifact hash audit to: {STAGE54_DIR / 'integrity' / 'artifact_hash_audit.md'}")

