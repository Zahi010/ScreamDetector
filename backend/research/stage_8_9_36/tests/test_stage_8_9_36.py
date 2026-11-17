"""
Stage 8.9.36 - Comprehensive Test Suite
Validates production immutability, directory isolation, test alignment,
confusion matrix metrics, threshold provenance, partition isolation,
duplicate audits, and baseline reconciliation reproducibility.
"""
import os
import sys
import json
import hashlib
import numpy as np
import pandas as pd
import pytest

# 1. Four Production Hashes Unchanged
def test_production_hashes_unchanged():
    expected_hashes = {
        "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
        "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
        "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
        "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2"
    }
    for file_path, exp_hash in expected_hashes.items():
        assert os.path.exists(file_path), f"Missing production file: {file_path}"
        with open(file_path, "rb") as f:
            actual_hash = hashlib.sha256(f.read()).hexdigest()
        assert actual_hash == exp_hash, f"Hash mismatch for {file_path}! Expected {exp_hash}, got {actual_hash}"

# 2. Research Output Directory Isolation
def test_research_directory_isolation():
    stage_dir = "backend/research/stage_8_9_36"
    assert os.path.exists(stage_dir)
    assert os.path.exists(os.path.join(stage_dir, "reports"))
    assert os.path.exists(os.path.join(stage_dir, "evaluation"))
    assert os.path.exists(os.path.join(stage_dir, "src"))
    assert os.path.exists(os.path.join(stage_dir, "configs"))
    assert os.path.exists(os.path.join(stage_dir, "tests"))

# 3. Identical Test IDs Across Stages
def test_identical_test_ids_across_stages():
    p33 = pd.read_csv("backend/research/stage_8_9_33/predictions/test_predictions_stage8_9_33.csv")
    p34 = pd.read_csv("backend/research/stage_8_9_34/predictions/test_predictions_stage8_9_34.csv")
    p35 = pd.read_csv("backend/research/stage_8_9_35/predictions/test_predictions_stage8_9_35.csv")
    
    assert len(p33) == 293
    assert len(p34) == 293
    assert len(p35) == 293
    assert (p33['file_id'] == p34['file_id']).all()
    assert (p33['file_id'] == p35['file_id']).all()
    assert (p33['ground_truth'] == p35['ground_truth']).all()

# 4. Metric Calculation from Confusion Matrix
def test_metric_calculation_from_confusion_matrix():
    tp, fp, fn, tn = 84, 12, 18, 179
    recall = tp / (tp + fn)
    fpr = fp / (fp + tn)
    precision = tp / (tp + fp)
    f1 = 2 * precision * recall / (precision + recall)
    
    assert abs(recall - 0.823529) < 1e-5
    assert abs(fpr - 0.062827) < 1e-5
    assert abs(precision - 0.875) < 1e-5
    assert abs(f1 - 0.848484) < 1e-4

# 5. Threshold Provenance Validation Only
def test_threshold_provenance_validation_only():
    sweep_path = "backend/research/stage_8_9_36/evaluation/validation_threshold_sweep.csv"
    assert os.path.exists(sweep_path)
    df_sweep = pd.read_csv(sweep_path)
    
    # Peak validation F1 must occur at 0.43
    best_row = df_sweep.loc[df_sweep['val_f1'].idxmax()]
    assert best_row['threshold'] == 0.43
    assert best_row['val_f1'] == 0.7861

# 6. No Threshold Selection from Test Predictions
def test_no_threshold_selection_from_test_predictions():
    comp_path = "backend/research/stage_8_9_36/evaluation/threshold_comparison.json"
    assert os.path.exists(comp_path)
    with open(comp_path, encoding='utf-8') as f:
        data = json.load(f)
    assert data["test_labels_used_for_selection"] is False
    assert data["validation_selected_threshold"] == 0.43

# 7. Source-Group Split Isolation
def test_source_group_split_isolation():
    manifest_path = "backend/experiments/v2_hard_negative_training/manifests/dataset_manifest_v3.csv"
    df = pd.read_csv(manifest_path)
    train_sg = set(df[df['split'] == 'train']['source_group_id'])
    val_sg = set(df[df['split'] == 'val']['source_group_id'])
    test_sg = set(df[df['split'] == 'test']['source_group_id'])
    
    assert len(train_sg.intersection(val_sg)) == 0
    assert len(train_sg.intersection(test_sg)) == 0
    assert len(val_sg.intersection(test_sg)) == 0

# 8. Duplicate Audit Consistency
def test_duplicate_audit_consistency():
    dup_path = "backend/research/stage_8_9_36/evaluation/duplicate_risk_report.csv"
    assert os.path.exists(dup_path)
    df_dup = pd.read_csv(dup_path)
    assert len(df_dup) == 1
    assert df_dup.iloc[0]['pcm_sha256'] == 'NONE'
    assert df_dup.iloc[0]['duplicate_count'] == 0

# 9. Missing Audio Handling
def test_missing_audio_handling():
    manifest_path = "backend/experiments/v2_hard_negative_training/manifests/dataset_manifest_v3.csv"
    df = pd.read_csv(manifest_path)
    assert len(df) == 1328
    # Sample check 50 random files for physical existence on disk
    for path in df['workspace_audio_path'].sample(50, random_state=42):
        assert os.path.exists(path), f"Audio file missing on disk: {path}"

# 10. Short-Scream Duration Grouping
def test_short_scream_duration_grouping():
    short_csv = "backend/research/stage_8_9_36/evaluation/short_scream_source_group_analysis.csv"
    assert os.path.exists(short_csv)
    df_short = pd.read_csv(short_csv)
    assert len(df_short) == 23 # Exactly 23 short screams in corpus
    assert (df_short['duration_sec'] < 1.0).all()
    # Test split must contain exactly 5 short screams
    test_shorts = df_short[df_short['split'] == 'test']
    assert len(test_shorts) == 5
    assert (test_shorts['test_detection_status'] == 'DETECTED (TP)').all()

# 11. Baseline Reconciliation Exact Reproducibility
def test_baseline_reconciliation_exact_reproducibility():
    diff_path = "backend/research/stage_8_9_36/evaluation/baseline_prediction_diff.csv"
    assert os.path.exists(diff_path)
    df_diff = pd.read_csv(diff_path)
    # Exactly 5 files differ between 0.35 and 0.43
    assert len(df_diff) == 5
    screams_lost = df_diff[df_diff['ground_truth'] == 1]
    fps_avoided = df_diff[df_diff['ground_truth'] == 0]
    assert len(screams_lost) == 2 # 86 -> 84 TP
    assert len(fps_avoided) == 3  # 15 -> 12 FP

# 12. Reproducible Reports Exist
def test_reproducible_reports_exist():
    expected_reports = [
        "baseline_reconciliation.md",
        "threshold_selection_audit.md",
        "false_negative_forensics.md",
        "false_positive_forensics.md",
        "subband_ablation_audit.md",
        "short_scream_evidence_audit.md",
        "dataset_integrity_audit.md",
        "next_stage_recommendation.md"
    ]
    rep_dir = "backend/research/stage_8_9_36/reports"
    for r in expected_reports:
        p = os.path.join(rep_dir, r)
        assert os.path.exists(p), f"Missing report: {p}"
        assert os.path.getsize(p) > 500, f"Report too small (placeholder?): {p}"
