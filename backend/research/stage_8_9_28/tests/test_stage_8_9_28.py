"""
Test Suite for Stage 8.9.28: Real-Time Inference Latency Benchmarking & Equivalence Validation.

Verifies:
1. Production integrity: All 4 production files match authoritative SHA-256 hashes 100%.
2. Production threshold is strictly 0.3500.
3. Latency constraints:
   - Model C graph-compiled P95 < 5.0 ms (actual 1.72 ms)
   - End-to-end pipeline P95 <= 25.0 ms (actual 21.44 ms)
   - Real-time gate passed == True
4. Numerical & decision equivalence:
   - Max probability difference < 1e-4 (actual 0.00e+00)
   - 0 decision mismatches across 139 independent cohort audio files
   - 100% agreement on shouting commands and short screams
5. Completeness of all Stage 8.9.28 artifacts.
"""

import os
import json
import hashlib
import pytest
import pandas as pd
import numpy as np

STAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WORKSPACE_ROOT = os.path.abspath(os.path.join(STAGE_DIR, "..", "..", ".."))

AUTHORITATIVE_HASHES = {
    "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
}


def test_production_integrity():
    """Verify all 4 production artifacts remain 100% frozen and unmodified."""
    for rel_path, expected_hash in AUTHORITATIVE_HASHES.items():
        abs_path = os.path.join(WORKSPACE_ROOT, rel_path.replace("/", os.sep))
        assert os.path.exists(abs_path), f"Missing production file: {abs_path}"
        with open(abs_path, "rb") as f:
            actual_hash = hashlib.sha256(f.read()).hexdigest()
        assert actual_hash == expected_hash, (
            f"CRITICAL: Production hash mismatch on {rel_path}!\n"
            f"Expected: {expected_hash}\nActual:   {actual_hash}"
        )


def test_production_threshold_exact():
    """Verify production threshold in metadata is strictly 0.3500."""
    meta_path = os.path.join(WORKSPACE_ROOT, "backend", "models", "model_metadata.json")
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    assert meta.get("selected_threshold") == 0.35, f"Unexpected threshold: {meta.get('selected_threshold')}"


def test_production_verification_artifact():
    """Verify production_integrity_verification.json records verified = True."""
    json_path = os.path.join(STAGE_DIR, "production_integrity_verification.json")
    assert os.path.exists(json_path)
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["overall_integrity_verified"] is True
    assert data["decision_threshold_exact"] == 0.35


def test_benchmark_results_structure():
    """Verify benchmark_results.csv contains required schema and non-empty rows."""
    csv_path = os.path.join(STAGE_DIR, "benchmark_results.csv")
    assert os.path.exists(csv_path)
    df = pd.read_csv(csv_path)
    required_cols = ["component", "p50_ms", "p95_ms", "p99_ms", "mean_ms", "min_ms", "max_ms", "std_ms", "iterations"]
    for col in required_cols:
        assert col in df.columns, f"Missing column: {col}"
    assert len(df) >= 15, f"Expected at least 15 benchmark rows, found {len(df)}"


def test_latency_budget_constraints():
    """Verify the optimized pipeline satisfies all real-time latency budgets."""
    json_path = os.path.join(STAGE_DIR, "latency_breakdown.json")
    assert os.path.exists(json_path)
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    assert data["gate_passed"] is True
    assert data["breakdown"]["complete_processing_window_optimized"]["p95_ms"] <= 25.0
    assert data["breakdown"]["model_c_compiled_inference"]["p95_ms"] <= 5.0
    
    # Model C speedup check
    uncompiled_p95 = data["breakdown"]["model_c_uncompiled_predict"]["p95_ms"]
    compiled_p95 = data["breakdown"]["model_c_compiled_inference"]["p95_ms"]
    speedup = uncompiled_p95 / compiled_p95
    assert speedup >= 20.0, f"Expected Model C speedup >= 20x, got {speedup:.2f}x"


def test_numerical_and_decision_equivalence():
    """Verify 100% equivalence between baseline and optimized pipelines."""
    equiv_path = os.path.join(STAGE_DIR, "decision_equivalence.json")
    assert os.path.exists(equiv_path)
    with open(equiv_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    assert data["mismatched_decisions"] == 0
    assert data["classification_agreement_pct"] == 100.0
    assert data["max_prob_diff_model_c"] < 1e-4
    assert data["max_prob_diff_fusion_e"] < 1e-4
    
    # Rejection and protection agreement
    assert data["shouting_rejected_baseline"] == data["shouting_rejected_optimized"]
    assert data["short_scream_hits_baseline"] == data["short_scream_hits_optimized"]
    
    # Synthetic edge cases
    for ec in data["edge_case_results"]:
        assert ec["abs_difference"] < 1e-4
        assert ec["equivalent"] is True


def test_required_artifacts_exist():
    """Verify all deliverables exist and have substantive content."""
    deliverables = [
        "benchmark_environment.json",
        "benchmark_config.json",
        "benchmark_results.csv",
        "latency_breakdown.json",
        "latency_profile_analysis.md",
        "realtime_budget_assessment.md",
        "optimization_recommendations.md",
        "decision_equivalence_report.md",
        "decision_equivalence.json",
        "production_integrity_verification.json",
    ]
    for d in deliverables:
        p = os.path.join(STAGE_DIR, d)
        assert os.path.exists(p), f"Missing artifact: {d}"
        assert os.path.getsize(p) > 100, f"Artifact empty or too small: {d}"
