"""
Stage 8.9.43: Automated Regression Unit Test Suite
17 comprehensive unit tests verifying data integrity, source-group isolation, 
model architecture forward passes, metric calculation bounds, benchmark gates,
mandatory safety designations, and strict production freeze invariants.
"""
import os
import sys
import json
import hashlib
from pathlib import Path
import pytest
import numpy as np
import pandas as pd
import torch

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE43_DIR = BACKEND_DIR / "research" / "stage_8_9_43"
sys.path.insert(0, str(STAGE43_DIR / "scripts"))

from evaluate_candidates_v5 import (
    DualEncoderAcousticModel,
    CustomLogMelCNN,
    CustomMultiScaleCNN,
    CustomTemporalCNN,
    wilson_ci
)

# -----------------------------------------------------------------------------
# Test 1: Production Freeze Hash Invariants
# -----------------------------------------------------------------------------
def test_production_freeze_hashes():
    expected_hashes = {
        BACKEND_DIR / "models" / "scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
        BACKEND_DIR / "models" / "model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
        BACKEND_DIR / "reports" / "test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
        BACKEND_DIR / "reports" / "stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
    }
    for file_path, expected_hash in expected_hashes.items():
        assert file_path.exists(), f"Production freeze file missing: {file_path}"
        with open(file_path, "rb") as f:
            actual_hash = hashlib.sha256(f.read()).hexdigest()
        assert actual_hash == expected_hash, f"Hash mismatch for {file_path.name}: expected {expected_hash}, got {actual_hash}"

# -----------------------------------------------------------------------------
# Test 2: Dataset Manifest v5 Schema & Total Row Count
# -----------------------------------------------------------------------------
def test_manifest_v5_schema_and_count():
    manifest_p = STAGE43_DIR / "manifests" / "dataset_manifest_v5.csv"
    assert manifest_p.exists(), "dataset_manifest_v5.csv does not exist"
    df = pd.read_csv(manifest_p)
    assert len(df) == 1914, f"Expected 1,914 rows, got {len(df)}"
    required_cols = [
        "file_id", "binary_label", "v5_research_split", "source_group_id",
        "target_category", "workspace_audio_path", "license"
    ]
    for col in required_cols:
        assert col in df.columns, f"Missing required column: {col}"

# -----------------------------------------------------------------------------
# Test 3: Source-Group-Level Partition Isolation (Zero Leakage)
# -----------------------------------------------------------------------------
def test_source_group_isolation():
    manifest_p = STAGE43_DIR / "manifests" / "dataset_manifest_v5.csv"
    df = pd.read_csv(manifest_p)
    splits = ["v5_train", "v5_validation", "v5_development_test", "v5_final_holdout"]
    sg_sets = {s: set(df[df["v5_research_split"] == s]["source_group_id"].dropna().unique()) for s in splits}
    for i in range(len(splits)):
        for j in range(i + 1, len(splits)):
            overlap = sg_sets[splits[i]].intersection(sg_sets[splits[j]])
            assert len(overlap) == 0, f"Source group overlap detected between {splits[i]} and {splits[j]}: {overlap}"

# -----------------------------------------------------------------------------
# Test 4: Positive Dataset Audit Row Count & Columns
# -----------------------------------------------------------------------------
def test_positive_dataset_audit():
    p = STAGE43_DIR / "POSITIVE_DATASET_AUDIT.csv"
    assert p.exists(), "POSITIVE_DATASET_AUDIT.csv missing"
    df = pd.read_csv(p)
    assert len(df) == 495, f"Expected 495 rows, got {len(df)}"
    assert "estimated_snr_db" in df.columns
    assert "f0_mean_hz" in df.columns

# -----------------------------------------------------------------------------
# Test 5: Acquisition Provenance Completeness & Licenses
# -----------------------------------------------------------------------------
def test_acquisition_provenance():
    p = STAGE43_DIR / "ACQUISITION_PROVENANCE.csv"
    assert p.exists(), "ACQUISITION_PROVENANCE.csv missing"
    df = pd.read_csv(p)
    assert len(df) == 191, f"Expected 191 acquired screams, got {len(df)}"
    # All licenses must be permissive (CC0, CC-BY)
    for lic in df["license_identifier"].unique():
        assert ("CC0" in lic or "CC-BY" in lic or "CC BY" in lic or "Public Domain" in lic), f"Unverified license: {lic}"

# -----------------------------------------------------------------------------
# Test 6: Annotation Review Verification
# -----------------------------------------------------------------------------
def test_annotation_review():
    p = STAGE43_DIR / "ANNOTATION_REVIEW.csv"
    assert p.exists(), "ANNOTATION_REVIEW.csv missing"
    df = pd.read_csv(p)
    assert len(df) == 191, f"Expected 191 annotations, got {len(df)}"
    assert (df["adjudication_status"] == "APPROVED").all()

# -----------------------------------------------------------------------------
# Test 7: LogMel Cache Existence & Shape
# -----------------------------------------------------------------------------
def test_logmel_cache():
    p = STAGE43_DIR / "features" / "logmel_v5_cache.npz"
    assert p.exists(), "logmel_v5_cache.npz missing"
    data = np.load(p, allow_pickle=True)
    assert len(data["file_ids"]) == 1914
    sample_fid = data["file_ids"][0]
    sample_mel = data[f"logmel_{sample_fid}"]
    assert sample_mel.shape[0] == 64, f"Expected 64 mel bins, got {sample_mel.shape[0]}"

# -----------------------------------------------------------------------------
# Test 8: YAMNet Cache Existence & Dimensions
# -----------------------------------------------------------------------------
def test_yamnet_cache():
    p = STAGE43_DIR / "features" / "yamnet_v5_cache.npz"
    assert p.exists(), "yamnet_v5_cache.npz missing"
    data = np.load(p, allow_pickle=True)
    assert len(data["file_ids"]) == 1914
    assert data["X_sem"].shape == (1914, 1024)
    assert data["X_acoust"].shape == (1914, 6)

# -----------------------------------------------------------------------------
# Test 9: Model Checkpoints Existence
# -----------------------------------------------------------------------------
def test_model_checkpoints():
    ckpts = ["config_b_v5.pt", "cnn_logmel_v5.pt", "cnn_multiscale_v5.pt", "cnn_temporal_v5.pt"]
    for ckpt in ckpts:
        p = STAGE43_DIR / "models" / ckpt
        assert p.exists(), f"Model checkpoint missing: {p}"

# -----------------------------------------------------------------------------
# Test 10: Model Configs Existence & Calibrated Thresholds
# -----------------------------------------------------------------------------
def test_model_configs():
    configs = ["config_b_v5.json", "cnn_logmel_v5.json", "cnn_multiscale_v5.json", "cnn_temporal_v5.json"]
    for cfg in configs:
        p = STAGE43_DIR / "configs" / cfg
        assert p.exists(), f"Config missing: {p}"
        with open(p, "r", encoding="utf-8") as f:
            d = json.load(f)
        assert 0.0 < d["selected_threshold"] < 1.0

# -----------------------------------------------------------------------------
# Test 11: Forward Pass Forward Shape Verification
# -----------------------------------------------------------------------------
def test_forward_pass_shapes():
    # 1. DualEncoderAcousticModel
    m_a = DualEncoderAcousticModel()
    m_a.eval()
    with torch.no_grad():
        out, z_s, z_a = m_a(torch.randn(2, 1024), torch.randn(2, 6), torch.ones(2, 6))
    assert out.shape == (2,)

    # 2. CustomLogMelCNN
    m_b = CustomLogMelCNN()
    m_b.eval()
    with torch.no_grad():
        out_b = m_b(torch.randn(2, 1, 64, 64))
    assert out_b.shape == (2,)

    # 3. CustomMultiScaleCNN
    m_c = CustomMultiScaleCNN()
    m_c.eval()
    with torch.no_grad():
        out_c = m_c(torch.randn(2, 1, 64, 64))
    assert out_c.shape == (2,)

    # 4. CustomTemporalCNN
    m_d = CustomTemporalCNN()
    m_d.eval()
    with torch.no_grad():
        out_d = m_d(torch.randn(2, 1, 64, 64))
    assert out_d.shape == (2,)

# -----------------------------------------------------------------------------
# Test 12: Wilson Score Interval Mathematical Invariants
# -----------------------------------------------------------------------------
def test_wilson_ci_bounds():
    low, high = wilson_ci(50, 100)
    assert 0.0 <= low <= 50.0 <= high <= 100.0
    low_0, high_0 = wilson_ci(0, 50)
    assert low_0 == 0.0 and high_0 > 0.0
    low_100, high_100 = wilson_ci(50, 50)
    assert high_100 >= 99.9 and low_100 < 100.0

# -----------------------------------------------------------------------------
# Test 13: Augmentation Study Schema & Row Count
# -----------------------------------------------------------------------------
def test_augmentation_study_results():
    p = STAGE43_DIR / "AUGMENTATION_EXPERIMENTS.csv"
    assert p.exists(), "AUGMENTATION_EXPERIMENTS.csv missing"
    df = pd.read_csv(p)
    assert len(df) == 4, f"Expected 4 augmentation conditions, got {len(df)}"
    assert "val_auc" in df.columns
    assert "selected_threshold" in df.columns

# -----------------------------------------------------------------------------
# Test 14: Streaming Latency Benchmark Gate 5 Compliance
# -----------------------------------------------------------------------------
def test_latency_benchmark_gate5():
    p = STAGE43_DIR / "results" / "evaluation" / "streaming_latency_benchmark.json"
    assert p.exists(), "streaming_latency_benchmark.json missing"
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 4
    for b in data:
        assert b["p95_latency_ms"] <= 25.0, f"Gate 5 violated: {b['candidate_id']} P95={b['p95_latency_ms']}ms > 25ms"
        assert b["gate5_p95_le_25ms"] == "PASS"

# -----------------------------------------------------------------------------
# Test 15: Candidate Comparison CSV Schema & Record Count
# -----------------------------------------------------------------------------
def test_candidate_comparison_csv():
    p = STAGE43_DIR / "CANDIDATE_COMPARISON_V5.csv"
    assert p.exists(), "CANDIDATE_COMPARISON_V5.csv missing"
    df = pd.read_csv(p)
    assert len(df) == 8, f"Expected 8 evaluations (4 candidates x 2 splits), got {len(df)}"
    assert "gate1_recall_ge_96" in df.columns
    assert "gate2_hn_fpr_le_5" in df.columns
    assert "gate3_shout_fpr_le_15" in df.columns
    assert "gate4_short_recall_ge_90" in df.columns

# -----------------------------------------------------------------------------
# Test 16: Mandatory Safety Designation in Markdown Reports
# -----------------------------------------------------------------------------
def test_mandatory_safety_designations():
    reports = [
        STAGE43_DIR / "reports" / "ACOUSTIC_DOMAIN_SHIFT_REPORT.md",
        STAGE43_DIR / "reports" / "SOURCE_GROUP_SPLIT_AUDIT.md",
        STAGE43_DIR / "reports" / "SUBGROUP_RECALL_REPORT.md",
        STAGE43_DIR / "reports" / "INFERENCE_BENCHMARK_V5.md"
    ]
    mandatory_phrase = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE."
    for rep in reports:
        assert rep.exists(), f"Report missing: {rep}"
        with open(rep, "r", encoding="utf-8") as f:
            content = f.read()
        assert mandatory_phrase in content, f"Mandatory safety designation missing in {rep.name}"

# -----------------------------------------------------------------------------
# Test 17: Production Classifier Unmodified in Backend
# -----------------------------------------------------------------------------
def test_production_classifier_unmodified():
    p = BACKEND_DIR / "models" / "scream_classifier.joblib"
    assert p.exists()
    assert hashlib.sha256(p.read_bytes()).hexdigest() == "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f"
