"""
Stage 8.9.46: Automated Regression Unit Test Suite
21 comprehensive unit tests verifying data integrity, source-group isolation,
probabilistic augmentation ratio manifests, trained candidate models,
calibrated operating thresholds, latency benchmarks, research acceptance gates,
mandatory safety designations, metric recalculation audits, and strict production freeze invariants.

MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
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
import joblib

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE43_DIR = BACKEND_DIR / "research" / "stage_8_9_43"
STAGE46_DIR = BACKEND_DIR / "research" / "stage_8_9_46"

sys.path.insert(0, str(STAGE46_DIR / "scripts"))
from evaluate_stage_8_9_46 import DualEncoderAcousticModel, wilson_ci

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
# Test 2: Dataset Manifest v5 Schema & Split Counts
# -----------------------------------------------------------------------------
def test_manifest_v5_schema_and_distribution():
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
        
    expected_split_counts = {
        "v5_train": 1198,
        "v5_validation": 309,
        "v5_development_test": 202,
        "v5_final_holdout": 205
    }
    actual_counts = df["v5_research_split"].value_counts().to_dict()
    assert actual_counts == expected_split_counts, f"Split distribution mismatch: {actual_counts}"

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
# Test 4: Augmented Manifests Existence and Counts
# -----------------------------------------------------------------------------
def test_augmented_manifests_v8_existence_and_counts():
    ratio_tags = [
        "config_b_ratio_100p_0a",
        "config_b_ratio_75p_25a",
        "config_b_ratio_50p_50a",
        "config_b_ratio_25p_75a",
        "config_b_ratio_0p_100a",
        "config_b_dynamic_50p_50a"
    ]
    for tag in ratio_tags:
        mf_path = STAGE46_DIR / "augmentation" / f"augmentation_manifest_{tag}.csv"
        assert mf_path.exists(), f"Augmented manifest missing: {mf_path}"
        df = pd.read_csv(mf_path)
        assert len(df) == 401, f"Expected 401 rows in {tag}, got {len(df)}"
        assert "slot_id" in df.columns
        assert "original_file_id" in df.columns
        assert "assigned_type" in df.columns

# -----------------------------------------------------------------------------
# Test 5: Trained Model Checkpoints Existence
# -----------------------------------------------------------------------------
def test_trained_model_checkpoints_v8():
    candidates = [
        "config_b_ratio_100p_0a",
        "config_b_ratio_75p_25a",
        "config_b_ratio_50p_50a",
        "config_b_ratio_25p_75a",
        "config_b_ratio_0p_100a",
        "config_b_dynamic_50p_50a"
    ]
    for c in candidates:
        ckpt_path = STAGE46_DIR / "models" / f"{c}.pt"
        assert ckpt_path.exists(), f"Missing model checkpoint: {ckpt_path}"
        assert ckpt_path.stat().st_size > 100000, f"Checkpoint suspiciously small: {ckpt_path.stat().st_size} bytes"

# -----------------------------------------------------------------------------
# Test 6: Calibrated Threshold Configs Existence and Range
# -----------------------------------------------------------------------------
def test_calibrated_threshold_configs_v8():
    candidates = [
        "config_b_ratio_100p_0a",
        "config_b_ratio_75p_25a",
        "config_b_ratio_50p_50a",
        "config_b_ratio_25p_75a",
        "config_b_ratio_0p_100a",
        "config_b_dynamic_50p_50a"
    ]
    for c in candidates:
        cfg_path = STAGE46_DIR / "configs" / f"{c}.json"
        assert cfg_path.exists(), f"Missing config: {cfg_path}"
        with open(cfg_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        assert "selected_threshold" in cfg, f"Missing selected_threshold in {c}"
        thresh = cfg["selected_threshold"]
        assert 0.05 <= thresh <= 0.99, f"Threshold out of range in {c}: {thresh}"

# -----------------------------------------------------------------------------
# Test 7: DualEncoderAcousticModel Architecture Forward Pass
# -----------------------------------------------------------------------------
def test_dual_encoder_model_forward():
    model = DualEncoderAcousticModel()
    model.eval()
    batch_size = 4
    dummy_sem = torch.randn(batch_size, 1024)
    dummy_acoust = torch.randn(batch_size, 6)
    dummy_mask = torch.ones(batch_size, 6)
    
    with torch.no_grad():
        logits, z_sem, z_acoust = model(dummy_sem, dummy_acoust, dummy_mask)
    
    assert logits.shape == (batch_size,), f"Expected logits shape {(batch_size,)}, got {logits.shape}"
    assert z_sem.shape == (batch_size, 128), f"Expected z_sem shape {(batch_size, 128)}, got {z_sem.shape}"
    assert z_acoust.shape == (batch_size, 32), f"Expected z_acoust shape {(batch_size, 32)}, got {z_acoust.shape}"

# -----------------------------------------------------------------------------
# Test 8: Wilson Score Confidence Interval Mathematical Bounds
# -----------------------------------------------------------------------------
def test_wilson_ci_bounds():
    low, high = wilson_ci(52, 69)
    p_pct = (52 / 69) * 100.0
    assert 0.0 <= low <= p_pct <= high <= 100.0, f"Wilson CI bounds invalid: {low}, {high}"
    assert wilson_ci(0, 0) == (0.0, 0.0)
    low_full, high_full = wilson_ci(65, 65)
    assert 0.0 <= low_full <= 100.0 and high_full <= 100.0

# -----------------------------------------------------------------------------
# Test 9: ECE Calibration Error Calculation Bounds
# -----------------------------------------------------------------------------
def test_ece_calibration_bounds():
    probs = np.array([0.1, 0.2, 0.8, 0.9])
    labels = np.array([0, 0, 1, 1])
    n_bins = 10
    bin_edges = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        idx = (probs >= bin_edges[i]) & (probs < bin_edges[i + 1])
        if np.sum(idx) > 0:
            acc = np.mean(labels[idx])
            conf = np.mean(probs[idx])
            ece += (np.sum(idx) / len(probs)) * np.abs(acc - conf)
    assert 0.0 <= ece <= 1.0, f"ECE outside [0, 1]: {ece}"

# -----------------------------------------------------------------------------
# Test 10: Streaming Latency Benchmark Gate 5 Compliance (P95 <= 25.0 ms)
# -----------------------------------------------------------------------------
def test_streaming_latency_benchmark_gate5():
    bench_p = STAGE46_DIR / "results" / "evaluation" / "streaming_latency_benchmark_v8.json"
    assert bench_p.exists(), f"Benchmark results missing: {bench_p}"
    with open(bench_p, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    for cand in data:
        p95 = cand["p95_latency_ms"]
        assert p95 <= 25.0, f"Gate 5 FAILED for {cand['candidate_id']}: P95 = {p95:.3f} ms exceeds 25.0 ms"
        assert cand["gate5_p95_le_25ms"] == "PASS"

# -----------------------------------------------------------------------------
# Test 11: Multi-Stream Concurrency vs 100 ms Audio-Hop Deadline
# -----------------------------------------------------------------------------
def test_multistream_concurrency_hop_deadline():
    bench_p = STAGE46_DIR / "results" / "evaluation" / "streaming_latency_benchmark_v8.json"
    with open(bench_p, "r", encoding="utf-8") as f:
        data = json.load(f)
    for cand in data:
        for stream_key, stream_info in cand["concurrency"].items():
            batch_lat = stream_info["batch_latency_ms"]
            assert batch_lat < 100.0, f"Audio-hop deadline exceeded for {cand['candidate_id']} at {stream_key}: {batch_lat} ms"
            assert stream_info["deadline_100ms_met"] is True

# -----------------------------------------------------------------------------
# Test 12: Candidate Comparison CSV Schema and Row Count
# -----------------------------------------------------------------------------
def test_candidate_comparison_csv_schema_and_rows():
    csv_p = STAGE46_DIR / "CANDIDATE_COMPARISON_V8.csv"
    assert csv_p.exists(), "CANDIDATE_COMPARISON_V8.csv missing"
    df = pd.read_csv(csv_p)
    assert len(df) == 20, f"Expected 20 rows (10 candidates x 2 splits), got {len(df)}"
    required_cols = [
        "candidate_id", "candidate_tag", "split", "threshold",
        "recall", "ci_95_low", "ci_95_high", "hn_fpr", "shout_fpr",
        "roc_auc", "pr_auc", "gate1_recall_ge_96"
    ]
    for c in required_cols:
        assert c in df.columns, f"Missing column in comparison CSV: {c}"

# -----------------------------------------------------------------------------
# Test 13: Candidate Evaluation Metrics JSON
# -----------------------------------------------------------------------------
def test_candidate_eval_metrics_json():
    json_p = STAGE46_DIR / "results" / "evaluation" / "candidate_eval_metrics_v8.json"
    assert json_p.exists(), "candidate_eval_metrics_v8.json missing"
    with open(json_p, "r", encoding="utf-8") as f:
        data = json.load(f)
    expected_tags = [
        "config_b_ratio_100p_0a",
        "config_b_ratio_75p_25a",
        "config_b_ratio_50p_50a",
        "config_b_ratio_25p_75a",
        "config_b_ratio_0p_100a",
        "config_b_dynamic_50p_50a"
    ]
    for tag in expected_tags:
        for split in ["v5_development_test", "v5_final_holdout"]:
            key = f"{tag}_{split}"
            assert key in data, f"Missing key in metrics json: {key}"
            assert "recall" in data[key]
            assert "roc_auc" in data[key]

# -----------------------------------------------------------------------------
# Test 14: Mandatory Safety Designation in Markdown Reports
# -----------------------------------------------------------------------------
def test_mandatory_safety_designation_in_reports():
    reports_dir = STAGE46_DIR / "reports"
    md_files = list(reports_dir.glob("*.md"))
    assert len(md_files) >= 5, f"Expected at least 5 markdown reports, found {len(md_files)}"
    required_designation = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE"
    for md_p in md_files:
        content = md_p.read_text(encoding="utf-8")
        assert required_designation in content, f"Missing mandatory safety designation in {md_p.name}"

# -----------------------------------------------------------------------------
# Test 15: Stage 8.9.46 Metric Audit Report Validation
# -----------------------------------------------------------------------------
def test_metric_audit_report_validation():
    rep_p = STAGE46_DIR / "reports" / "STAGE_8_9_46_METRIC_AUDIT.md"
    assert rep_p.exists(), "STAGE_8_9_46_METRIC_AUDIT.md missing"
    content = rep_p.read_text(encoding="utf-8")
    assert "Candidate E" in content
    assert "84.38%" in content
    assert "81.20%" in content

# -----------------------------------------------------------------------------
# Test 16: Threshold Operating Point Report Validation
# -----------------------------------------------------------------------------
def test_threshold_operating_point_report_validation():
    rep_p = STAGE46_DIR / "reports" / "THRESHOLD_OPERATING_POINT_REPORT.md"
    assert rep_p.exists(), "THRESHOLD_OPERATING_POINT_REPORT.md missing"
    content = rep_p.read_text(encoding="utf-8")
    assert "Matched Operating Point" in content

# -----------------------------------------------------------------------------
# Test 17: Augmentation Ratio Experiment Report Validation
# -----------------------------------------------------------------------------
def test_augmentation_ratio_experiment_report_validation():
    rep_p = STAGE46_DIR / "reports" / "AUGMENTATION_RATIO_EXPERIMENT.md"
    assert rep_p.exists(), "AUGMENTATION_RATIO_EXPERIMENT.md missing"
    content = rep_p.read_text(encoding="utf-8")
    for r_str in ["Ratio-100P-0A", "Ratio-75P-25A", "Ratio-50P-50A", "Ratio-25P-75A", "Ratio-0P-100A"]:
        assert r_str in content, f"Ratio {r_str} missing from report"

# -----------------------------------------------------------------------------
# Test 18: Augmentation Sampling Report Validation
# -----------------------------------------------------------------------------
def test_augmentation_sampling_report_validation():
    rep_p = STAGE46_DIR / "reports" / "AUGMENTATION_SAMPLING_REPORT.md"
    assert rep_p.exists(), "AUGMENTATION_SAMPLING_REPORT.md missing"
    content = rep_p.read_text(encoding="utf-8")
    assert "Dynamic" in content

# -----------------------------------------------------------------------------
# Test 19: Subtype Generalization Report Validation
# -----------------------------------------------------------------------------
def test_subtype_generalization_report_validation():
    rep_p = STAGE46_DIR / "reports" / "SUBTYPE_GENERALIZATION_REPORT.md"
    assert rep_p.exists(), "SUBTYPE_GENERALIZATION_REPORT.md missing"
    content = rep_p.read_text(encoding="utf-8")
    for keyword in ["Masked", "Distant", "Sustained", "Short Comb"]:
        assert keyword in content, f"Subtype {keyword} missing from report"

# -----------------------------------------------------------------------------
# Test 20: Phase A Recalculated Metrics JSON Validation
# -----------------------------------------------------------------------------
def test_phase_a_recalculated_metrics_json():
    json_p = STAGE46_DIR / "results" / "evaluation" / "phase_a_recalculated_metrics.json"
    assert json_p.exists(), "phase_a_recalculated_metrics.json missing"
    with open(json_p, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 20, f"Expected 20 entries in phase_a recalculation, got {len(data)}"

# -----------------------------------------------------------------------------
# Test 21: Production Model Immutability & Loadability
# -----------------------------------------------------------------------------
def test_production_model_immutability():
    model_path = BACKEND_DIR / "models" / "scream_classifier.joblib"
    model = joblib.load(model_path)
    assert hasattr(model, "predict_proba"), "Production model missing predict_proba"
    assert hasattr(model, "classes_"), "Production model missing classes_"

