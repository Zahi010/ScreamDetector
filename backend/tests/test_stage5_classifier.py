"""Unit and Regression Tests for Stage 5 Custom Scream Classifier.

Validates:
1. Model artifact serialization and deserialization with FestivalScreamClassifier.
2. Input feature shape verification and automatic dimension adaptation.
3. Probability output bounds [0.0, 1.0] and label mapping consistency.
4. Deterministic evaluation for identical feature inputs.
5. Strict prevention of split leakage and detection of injected contamination.
6. End-to-end waveform prediction and auxiliary diagnostic extraction.
"""

from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pytest

from src.audio.preprocessor import generate_synthetic_chirp, generate_synthetic_tone
from src.config import MODELS_DIR, YAMNet_EMBEDDING_DIM
from src.dataset import verify_manifests_and_cache
from src.dataset.split_builder import LeakageError, verify_no_leakage
from src.model.scream_classifier import (
    FestivalScreamClassifier,
    InvalidFeatureDimensionError,
    ModelNotLoadedError,
)


@pytest.fixture
def classifier() -> FestivalScreamClassifier:
    """Fixture providing loaded FestivalScreamClassifier instance."""
    clf = FestivalScreamClassifier()
    assert clf.is_loaded, "Trained model or metadata not loaded. Run train_classifier.py first."
    return clf


def test_model_serialization_and_metadata_integrity(classifier: FestivalScreamClassifier):
    """Verify that model artifact and metadata JSON are present and structurally valid."""
    model_path = MODELS_DIR / "scream_classifier.joblib"
    meta_path = MODELS_DIR / "model_metadata.json"

    assert model_path.exists(), f"Model file missing: {model_path}"
    assert meta_path.exists(), f"Metadata file missing: {meta_path}"

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert meta["model_type"] in ["LogisticRegression", "SupportVectorMachine", "MultiLayerPerceptron"]
    assert "validation_metrics" in meta
    assert "roc_auc" in meta["validation_metrics"]
    assert "pr_auc" in meta["validation_metrics"]
    assert 0.0 <= meta["selected_threshold"] <= 1.0
    assert meta["class_mapping"] == {"0": "non_scream", "1": "scream"}
    assert "manifest_hashes" in meta
    assert len(meta["manifest_hashes"]["split_manifest"]) == 64
    assert len(meta["manifest_hashes"]["embedding_manifest"]) == 64


def test_feature_dimensionality_handling(classifier: FestivalScreamClassifier):
    """Test shape validation and dimension adaptation for 1024, 2048, and (N, 1024) inputs."""
    # 1. Expected dimension (1024 if max_pooled)
    vec_1024 = np.zeros((YAMNet_EMBEDDING_DIM,), dtype=np.float32)
    res_1024 = classifier.predict_features(vec_1024)
    assert "scream_probability" in res_1024
    assert isinstance(res_1024["is_scream"], bool)

    # 2. 2048-dim concatenated clip_embedding (should be adapted automatically)
    vec_2048 = np.zeros((YAMNet_EMBEDDING_DIM * 2,), dtype=np.float32)
    res_2048 = classifier.predict_features(vec_2048)
    assert "scream_probability" in res_2048

    # 3. 2D frame embeddings sequence (N, 1024)
    frames = np.random.randn(8, YAMNet_EMBEDDING_DIM).astype(np.float32)
    res_frames = classifier.predict_features(frames)
    assert "scream_probability" in res_frames

    # 4. Invalid dimension should raise InvalidFeatureDimensionError
    invalid_vec = np.zeros((512,), dtype=np.float32)
    with pytest.raises(InvalidFeatureDimensionError):
        classifier.predict_features(invalid_vec)


def test_probability_outputs_and_bounds(classifier: FestivalScreamClassifier):
    """Verify probability outputs reside in [0.0, 1.0] and sum to ~1.0."""
    rng = np.random.RandomState(42)
    vec = rng.randn(YAMNet_EMBEDDING_DIM).astype(np.float32)
    res = classifier.predict_features(vec)

    p_scream = res["scream_probability"]
    p_non_scream = res["non_scream_probability"]

    assert 0.0 <= p_scream <= 1.0
    assert 0.0 <= p_non_scream <= 1.0
    assert pytest.approx(p_scream + p_non_scream, abs=1e-5) == 1.0

    # Decision logic
    if p_scream >= res["threshold"]:
        assert res["is_scream"] is True
        assert res["predicted_label"] == "scream"
    else:
        assert res["is_scream"] is False
        assert res["predicted_label"] == "non_scream"


def test_deterministic_predictions(classifier: FestivalScreamClassifier):
    """Ensure identical feature inputs produce bitwise identical probability outputs."""
    rng = np.random.RandomState(999)
    vec = rng.randn(YAMNet_EMBEDDING_DIM).astype(np.float32)

    res1 = classifier.predict_features(vec)
    res2 = classifier.predict_features(vec)

    assert res1["scream_probability"] == res2["scream_probability"]
    assert res1["margin_to_threshold"] == res2["margin_to_threshold"]
    assert res1["is_scream"] == res2["is_scream"]


def test_pre_training_verification_clean():
    """Verify pre-training manifest and cache integrity passes cleanly."""
    res = verify_manifests_and_cache(check_array_finiteness=False)
    assert res["status"] == "verified_clean"
    assert res["total_records"] == 1621
    assert res["leakage_detected"] is False
    assert res["excluded_recordings_confirmed_absent"] is True


def test_leakage_detector_catches_contamination():
    """Verify that verify_no_leakage raises LeakageError upon injected group or hash collision."""
    clean_splits = {
        "train": [
            {"source_group_id": "group_A", "sha256_hash": "hash_1"},
            {"source_group_id": "group_B", "sha256_hash": "hash_2"},
        ],
        "val": [
            {"source_group_id": "group_C", "sha256_hash": "hash_3"},
        ],
        "test": [
            {"source_group_id": "group_D", "sha256_hash": "hash_4"},
        ],
    }
    assert verify_no_leakage(clean_splits) is True

    # Inject source group leakage between train and test
    contaminated_group_splits = {
        "train": [
            {"source_group_id": "group_A", "sha256_hash": "hash_1"},
        ],
        "val": [
            {"source_group_id": "group_B", "sha256_hash": "hash_2"},
        ],
        "test": [
            {"source_group_id": "group_A", "sha256_hash": "hash_3"},  # group_A leaked!
        ],
    }
    with pytest.raises(LeakageError, match="SOURCE GROUP LEAKAGE DETECTED"):
        verify_no_leakage(contaminated_group_splits)

    # Inject exact hash collision between val and test
    contaminated_hash_splits = {
        "train": [
            {"source_group_id": "group_A", "sha256_hash": "hash_1"},
        ],
        "val": [
            {"source_group_id": "group_B", "sha256_hash": "hash_2"},
        ],
        "test": [
            {"source_group_id": "group_C", "sha256_hash": "hash_2"},  # hash_2 leaked!
        ],
    }
    with pytest.raises(LeakageError, match="CONTENT HASH LEAKAGE DETECTED"):
        verify_no_leakage(contaminated_hash_splits)


def test_end_to_end_waveform_inference(classifier: FestivalScreamClassifier):
    """Test full inference pipeline from synthetic waveform to probability and YAMNet priors."""
    waveform = generate_synthetic_tone(freq_hz=440.0, duration_seconds=1.0)
    res = classifier.predict_audio(waveform)

    assert "scream_probability" in res
    assert "is_scream" in res
    assert "threshold" in res
    assert "yamnet_top_priors" in res
    assert isinstance(res["yamnet_top_priors"], list)
    assert len(res["yamnet_top_priors"]) > 0
    assert "audio_duration_seconds" in res
    assert res["audio_duration_seconds"] == 1.0
