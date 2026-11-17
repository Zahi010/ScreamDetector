import hashlib
import json
from pathlib import Path
import pytest
import numpy as np
import joblib

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent
STAGE_DIR = BACKEND_DIR / "research" / "stage_8_9_25"
MODELS_DIR = STAGE_DIR / "models"

AUTHORITATIVE_HASHES = {
    "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2"
}

def test_production_artifact_hashes():
    """Verify that all 4 production artifacts match the authoritative SHA-256 hashes exactly."""
    for rel_path, expected_hash in AUTHORITATIVE_HASHES.items():
        full_path = BACKEND_DIR.parent / rel_path
        assert full_path.exists(), f"Production artifact missing: {full_path}"
        with open(full_path, "rb") as f:
            computed_hash = hashlib.sha256(f.read()).hexdigest()
        assert computed_hash == expected_hash, f"Hash mismatch for {rel_path}: expected {expected_hash}, got {computed_hash}"

def test_production_threshold_preserved():
    """Verify that the production decision threshold is strictly 0.3500."""
    metadata_path = BACKEND_DIR / "models" / "model_metadata.json"
    with open(metadata_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    assert meta.get("selected_threshold") == 0.35, "Production threshold must remain 0.3500"

def test_stage_deliverables_exist():
    """Verify that all required Stage 8.9.25 deliverables exist on disk."""
    expected_files = [
        STAGE_DIR / "STAGE_8_9_25_COMPLETION_REPORT.md",
        STAGE_DIR / "architecture_comparison.csv",
        STAGE_DIR / "phonetic_discriminability_report.md",
        STAGE_DIR / "feature_ablation_results.csv",
        STAGE_DIR / "category_error_analysis.csv",
        STAGE_DIR / "short_scream_analysis.md",
        STAGE_DIR / "latency_benchmark.csv",
        STAGE_DIR / "dataset_integrity_report.md",
        STAGE_DIR / "production_integrity_verification.json",
        MODELS_DIR / "model_configs.json",
        MODELS_DIR / "model_a_yamnet_baseline.joblib",
        MODELS_DIR / "model_b_2d_cnn.keras",
        MODELS_DIR / "model_c_temporal_1d_cnn.keras",
        MODELS_DIR / "model_d_yamnet_temporal_fusion.joblib",
        MODELS_DIR / "model_e_hybrid_multimodal.joblib"
    ]
    for p in expected_files:
        assert p.exists(), f"Required deliverable file is missing: {p}"

def test_dataset_integrity_verification():
    """Verify dataset integrity report confirms 0% cross-split leakage."""
    report_path = STAGE_DIR / "dataset_integrity_report.md"
    assert report_path.exists()
    content = report_path.read_text(encoding="utf-8")
    assert "0.00% leakage" in content
    assert "0" in content and "duplicates across splits" in content

def test_model_loading_and_inference():
    """Verify that all candidate models can be loaded and perform inference correctly."""
    # Model A: Logistic Regression on (1, 1024)
    model_a = joblib.load(MODELS_DIR / "model_a_yamnet_baseline.joblib")
    dummy_a = np.zeros((2, 1024), dtype=np.float32)
    pred_a = model_a.predict_proba(dummy_a)[:, 1]
    assert len(pred_a) == 2
    assert np.all((pred_a >= 0.0) & (pred_a <= 1.0))

    # Keras models
    import keras
    # Model B: 2D CNN on (64, 128, 1)
    model_b = keras.models.load_model(MODELS_DIR / "model_b_2d_cnn.keras")
    dummy_b = np.zeros((2, 64, 128, 1), dtype=np.float32)
    pred_b = model_b.predict(dummy_b, verbose=0).flatten()
    assert len(pred_b) == 2
    assert np.all((pred_b >= 0.0) & (pred_b <= 1.0))

    # Model C: Temporal 1D CNN on (70, 16)
    model_c = keras.models.load_model(MODELS_DIR / "model_c_temporal_1d_cnn.keras")
    dummy_c = np.zeros((2, 70, 16), dtype=np.float32)
    pred_c = model_c.predict(dummy_c, verbose=0).flatten()
    assert len(pred_c) == 2
    assert np.all((pred_c >= 0.0) & (pred_c <= 1.0))

    # Model D: YAMNet + Temp Prob (1025)
    model_d = joblib.load(MODELS_DIR / "model_d_yamnet_temporal_fusion.joblib")
    dummy_d = np.zeros((2, 1025), dtype=np.float32)
    pred_d = model_d.predict_proba(dummy_d)[:, 1]
    assert len(pred_d) == 2
    assert np.all((pred_d >= 0.0) & (pred_d <= 1.0))

    # Model E: Hybrid (1024 + 1 + 1 + 32 = 1058)
    model_e = joblib.load(MODELS_DIR / "model_e_hybrid_multimodal.joblib")
    dummy_e = np.zeros((2, 1058), dtype=np.float32)
    pred_e = model_e.predict_proba(dummy_e)[:, 1]
    assert len(pred_e) == 2
    assert np.all((pred_e >= 0.0) & (pred_e <= 1.0))

def test_acceptance_gate_enforcement():
    """Verify that all research candidates are marked REJECTED (Research Only) in comparison table."""
    import csv
    comp_file = STAGE_DIR / "architecture_comparison.csv"
    assert comp_file.exists()
    with open(comp_file, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 6
    for row in rows:
        verdict = row["engineering_gate_verdict"]
        assert "REJECTED" in verdict, f"Candidate {row['architecture_candidate']} should be rejected: {verdict}"

if __name__ == "__main__":
    pytest.main(["-v", __file__])
