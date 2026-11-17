"""Unit and integration tests for YAMNetLoader and embedding integrity."""

import numpy as np
import pytest

from src.audio.preprocessor import generate_synthetic_tone
from src.config import YAMNet_EMBEDDING_DIM, YAMNet_NUM_CLASSES
from src.model.yamnet_loader import YAMNetLoader


@pytest.fixture(scope="module")
def loaded_yamnet():
    """Shared YAMNet loader fixture to avoid reloading model weights for every test."""
    loader = YAMNetLoader()
    loader.load()
    return loader


def test_yamnet_load_and_classes(loaded_yamnet):
    """Verify YAMNet model is loaded and AudioSet class vocabulary is present."""
    assert loaded_yamnet.is_loaded is True
    assert len(loaded_yamnet.class_names) == YAMNet_NUM_CLASSES
    # Verify common AudioSet classes are present
    assert "Screaming" in loaded_yamnet.class_names
    assert "Speech" in loaded_yamnet.class_names
    assert "Music" in loaded_yamnet.class_names


def test_yamnet_inference_shapes(loaded_yamnet):
    """Verify inference output shapes on 1.0 second 16 kHz tone."""
    tone = generate_synthetic_tone(freq_hz=1000.0, duration_seconds=1.0, sr=16000)
    scores, embeddings, spectrogram = loaded_yamnet.infer(tone)

    # 1.0s audio yields 2 frames (0.975s window with 0.4875s hop)
    assert scores.ndim == 2
    assert scores.shape[1] == YAMNet_NUM_CLASSES
    assert embeddings.ndim == 2
    assert embeddings.shape[1] == YAMNet_EMBEDDING_DIM
    assert spectrogram.ndim == 2
    assert spectrogram.shape[1] == 64  # 64 mel frequency bins


def test_yamnet_extract_embeddings_dimension(loaded_yamnet):
    """Verify standalone embedding extractor returns exactly (N, 1024)."""
    tone = generate_synthetic_tone(freq_hz=500.0, duration_seconds=1.5, sr=16000)
    emb = loaded_yamnet.extract_embeddings(tone)

    assert isinstance(emb, np.ndarray)
    assert emb.ndim == 2
    assert emb.shape[1] == YAMNet_EMBEDDING_DIM
    assert emb.shape[0] >= 2


def test_yamnet_predict_top_k(loaded_yamnet):
    """Verify top-k predictions formatting and probability bounds."""
    tone = generate_synthetic_tone(freq_hz=440.0, duration_seconds=1.0, sr=16000)
    top_k = loaded_yamnet.predict_top_k(tone, k=5)

    assert len(top_k) == 5
    for item in top_k:
        assert "class_index" in item
        assert "display_name" in item
        assert "mean_score" in item
        assert "max_score" in item
        assert 0.0 <= item["mean_score"] <= 1.0
        assert 0.0 <= item["max_score"] <= 1.0

    # Ensure results are sorted descending
    mean_scores = [item["mean_score"] for item in top_k]
    assert mean_scores == sorted(mean_scores, reverse=True)


def test_yamnet_invalid_inputs(loaded_yamnet):
    """Verify appropriate exceptions are raised on invalid inputs."""
    # 2D input should raise ValueError
    with pytest.raises(ValueError):
        loaded_yamnet.infer(np.zeros((16000, 2), dtype=np.float32))

    # Empty input should raise ValueError
    with pytest.raises(ValueError):
        loaded_yamnet.infer(np.array([], dtype=np.float32))
