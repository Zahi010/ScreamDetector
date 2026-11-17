import hashlib
import json
import os
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

# MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE54_DIR = BACKEND_DIR / "research" / "stage_8_9_54"
STAGE55_DIR = BACKEND_DIR / "research" / "stage_8_9_55"
STAGE57_DIR = BACKEND_DIR / "research" / "stage_8_9_57"
STAGE58_DIR = BACKEND_DIR / "research" / "stage_8_9_58"
STAGE59_DIR = BACKEND_DIR / "research" / "stage_8_9_59"
STAGE60_DIR = BACKEND_DIR / "research" / "stage_8_9_60"

def sha256_file(path: Path) -> str:
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()

# 1. Production asset hash immutability
def test_01_production_asset_hashes():
    prod_hashes = {
        BACKEND_DIR / "models" / "scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
        BACKEND_DIR / "models" / "model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
        BACKEND_DIR / "reports" / "test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
        BACKEND_DIR / "reports" / "stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2"
    }
    for p, expected in prod_hashes.items():
        assert p.exists()
        assert sha256_file(p) == expected

# 2. Candidate E1 checkpoint immutability
def test_02_candidate_e1_checkpoint_hash():
    e1_path = STAGE54_DIR / "training" / "candidate_e_v954_weighted.pt"
    assert e1_path.exists()
    assert sha256_file(e1_path) == "37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564"

# 3. Candidate B checkpoint immutability
def test_03_candidate_b_checkpoint_hash():
    b_path = BACKEND_DIR / "research" / "stage_8_9_44" / "models" / "config_b_mask.pt"
    assert b_path.exists()
    assert sha256_file(b_path) == "f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378"

# 4. Intervention D immutability
def test_04_intervention_d_hash():
    d_path = BACKEND_DIR / "research" / "stage_8_9_49" / "scripts" / "whistle_discriminator.py"
    assert d_path.exists()
    assert sha256_file(d_path) == "3d98aa7496c6ba89066cfa345a6d0c1ee3605c30821f869a049001c4ad4a8bd2"

# 5. C5 implementation immutability
def test_05_c5_implementation_hash():
    c5_path = STAGE57_DIR / "dsp_implementations" / "c5_combined.py"
    assert c5_path.exists()
    assert sha256_file(c5_path) == "d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58"

# 6. Original E1 DSP immutability
def test_06_original_e1_dsp_hash():
    orig_path = STAGE57_DIR / "scripts" / "benchmark_original_dsp.py"
    assert orig_path.exists()
    assert sha256_file(orig_path) == "192e928c6ea427737ef8a3ec4449c890c1d41f01d71c80cefde3f2a0363f5905"

# 7. Frozen historical manifest immutability
def test_07_frozen_manifest_immutability():
    man54 = STAGE54_DIR / "dataset" / "partition_manifest_verified.csv"
    assert sha256_file(man54) == "10563efcd5d607d1395f9db5ab1aa805a0d9ca39b9b4a64a710816d334caeb9e"
    man55 = STAGE55_DIR / "integrity" / "frozen_test_manifest.json"
    assert sha256_file(man55) == "06c9db80d3969e60f78dd441eb1495a9dab97f1646f08ab5825ea979719021f2"

# 8. New recording ID uniqueness
def test_08_recording_id_uniqueness():
    acq = pd.read_csv(STAGE60_DIR / "acquisition_manifest.csv")
    assert acq["recording_id"].nunique() == len(acq)

# 9. Audio SHA-256 uniqueness
def test_09_audio_sha256_uniqueness():
    acq = pd.read_csv(STAGE60_DIR / "acquisition_manifest.csv")
    assert acq["audio_sha256"].nunique() == len(acq)

# 10. PCM duplicate detection
def test_10_pcm_duplicate_detection():
    acq = pd.read_csv(STAGE60_DIR / "acquisition_manifest.csv")
    assert acq["pcm_sha256"].nunique() == len(acq)

# 11. Near-duplicate audit
def test_11_near_duplicate_audit():
    with open(STAGE60_DIR / "duplicate_audit_summary.json") as f:
        summary = json.load(f)
    assert summary["historical_exclusion_file_collisions"] == 0
    assert summary["historical_exclusion_pcm_collisions"] == 0
    assert summary["duplicate_detection_status"] == "CLEAN_ZERO_LEAKAGE"

# 12. Excerpt/parent relationships
def test_12_excerpt_parent_relationships():
    dup_df = pd.read_csv(STAGE60_DIR / "duplicate_and_excerpt_relationships.csv")
    assert len(dup_df) > 0
    assert "parent_recording_id" in dup_df.columns

# 13. Creator-level isolation
def test_13_creator_level_isolation():
    cs_df = pd.read_csv(STAGE60_DIR / "creator_session_inventory.csv")
    assert len(cs_df) > 0
    assert cs_df["creator_uploader"].nunique() == len(cs_df)

# 14. Session-level isolation
def test_14_session_level_isolation():
    acq = pd.read_csv(STAGE60_DIR / "acquisition_manifest.csv")
    assert acq["recording_session_id"].notna().all()

# 15. Source-group isolation
def test_15_source_group_isolation():
    with open(STAGE60_DIR / "source_independence_summary.json") as f:
        summary = json.load(f)
    assert summary["source_group_overlap"]["train_overlap_count"] == 0
    assert summary["source_group_overlap"]["val_overlap_count"] == 0
    assert summary["source_group_overlap"]["test_overlap_count"] == 0

# 16. License verification completeness
def test_16_license_verification_completeness():
    acq = pd.read_csv(STAGE60_DIR / "acquisition_manifest.csv")
    assert acq["license"].notna().all()
    valid_licenses = ["CC0", "CC-BY", "CC BY", "Public Domain", "CC BY 4.0", "CC0 1.0 Universal", "CC-BY-4.0"]
    assert acq["license"].apply(lambda x: any(v.lower() in str(x).lower() for v in valid_licenses)).all()

# 17. Attribution metadata completeness
def test_17_attribution_metadata_completeness():
    acq = pd.read_csv(STAGE60_DIR / "acquisition_manifest.csv")
    assert acq["attribution_text"].notna().all()
    assert (acq["attribution_text"].str.len() > 10).all()

# 18. Recording duration validation
def test_18_recording_duration_validation():
    acq = pd.read_csv(STAGE60_DIR / "acquisition_manifest.csv")
    assert (acq["duration_seconds"] > 0.05).all()

# 19. Audio decoding validation
def test_19_audio_decoding_validation():
    qual = pd.read_csv(STAGE60_DIR / "audio_quality_metrics.csv")
    assert (qual["file_exists"] == True).all()
    assert (qual["rms_energy"] >= 0.0).all()

# 20. Annotation completeness
def test_20_annotation_completeness():
    ann = pd.read_csv(STAGE60_DIR / "annotation_records.csv")
    assert len(ann) == 962
    assert ann["adjudicated_label"].notna().all()

# 21. Dual-annotation recording coverage
def test_21_dual_annotation_coverage():
    ann = pd.read_csv(STAGE60_DIR / "annotation_records.csv")
    assert ann["reviewer_1_label"].notna().all()
    assert ann["reviewer_2_label"].notna().all()

# 22. Disagreement and adjudication preservation
def test_22_disagreement_preservation():
    dis = pd.read_csv(STAGE60_DIR / "annotation_disagreements.csv")
    assert len(dis) > 0
    assert "adjudication_rationale" in dis.columns

# 23. Category denominator consistency
def test_23_category_denominator_consistency():
    acq = pd.read_csv(STAGE60_DIR / "acquisition_manifest.csv")
    pos = acq[acq["binary_label"] == 1]
    neg = acq[acq["binary_label"] == 0]
    assert len(pos) + len(neg) == len(acq)
    assert len(pos) == 298
    assert len(neg) == 664

# 24. Acquisition target calculations
def test_24_acquisition_target_calculations():
    cov = pd.read_csv(STAGE60_DIR / "acquisition_coverage_matrix.csv")
    assert len(cov) == 8
    assert (cov["target_recordings"] > 0).all()

# 25. Verified eligible recording counts
def test_25_verified_eligible_recording_counts():
    acq = pd.read_csv(STAGE60_DIR / "acquisition_manifest.csv")
    assert len(acq) == 962

# 26. Sealed cohort independence
def test_26_sealed_cohort_independence():
    with open(STAGE60_DIR / "future_evaluation_manifest.json") as f:
        cohort = json.load(f)
    assert cohort["total_recordings"] == 700
    assert cohort["positive_recordings"] == 200
    assert cohort["negative_recordings"] == 500
    assert cohort["unique_source_groups"] >= 370

# 27. Sealed manifest hash verification
def test_27_sealed_manifest_hash_verification():
    json_path = STAGE60_DIR / "future_evaluation_manifest.json"
    sha_path = STAGE60_DIR / "future_evaluation_manifest.sha256"
    assert json_path.exists()
    assert sha_path.exists()
    computed = sha256_file(json_path)
    with open(sha_path) as f:
        recorded = f.read().strip().split()[0]
    assert computed.lower() == recorded.lower()

# 28. Sealed label access restrictions
def test_28_sealed_label_access_restrictions():
    with open(STAGE60_DIR / "future_evaluation_manifest.json") as f:
        cohort = json.load(f)
    assert "RESTRICTED ACCESS" in cohort["governance_rule"]
    assert cohort["cohort_status"] == "SEALED_CRYPTOGRAPHICALLY_FROZEN"

# 29. No model training
def test_29_no_model_training():
    new_models = list(STAGE60_DIR.glob("**/*.pt")) + list(STAGE60_DIR.glob("**/*.joblib"))
    assert len(new_models) == 0

# 30. No threshold changes
def test_30_no_threshold_changes():
    meta_path = BACKEND_DIR / "models" / "model_metadata.json"
    with open(meta_path) as f:
        meta = json.load(f)
    assert meta["selected_threshold"] == 0.35 # Production threshold locked

# 31. No modification of C5
def test_31_no_modification_of_c5():
    c5_path = STAGE57_DIR / "dsp_implementations" / "c5_combined.py"
    assert sha256_file(c5_path) == "d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58"

# 32. No modification of production artifacts
def test_32_no_modification_of_production_artifacts():
    prod_clf = BACKEND_DIR / "models" / "scream_classifier.joblib"
    assert sha256_file(prod_clf) == "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f"

