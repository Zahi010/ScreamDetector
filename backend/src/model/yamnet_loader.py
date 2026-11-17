"""Pretrained YAMNet Model Loader and AudioSet Inference Wrapper.

Loads Google's pretrained YAMNet model from TensorFlow Hub, extracts 1,024-dimensional
frame embeddings, and provides AudioSet classification outputs.

CRITICAL DISTINCTION:
Pretrained YAMNet outputs 521 general AudioSet categories (including general 'Screaming',
'Laughter', 'Speech', 'Music', etc.). These are broad acoustic priors.
Our downstream custom festival classifier will consume the 1,024-dimensional embeddings
trained specifically on the curated festival/distress dataset.
"""

from __future__ import annotations

import csv
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# Suppress TF oneDNN informational spam
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

try:
    import tensorflow as tf
    import tensorflow_hub as hub
except ImportError:
    tf = None
    hub = None

from src.config import YAMNet_EMBEDDING_DIM, YAMNet_TFHUB_HANDLE

logger = logging.getLogger(__name__)


class YAMNetLoader:
    """Encapsulates YAMNet loading, inference, embedding extraction, and AudioSet mapping."""

    def __init__(self, model_handle: Optional[str] = None) -> None:
        """Initialize YAMNetLoader.

        Args:
            model_handle: URL or local path to YAMNet SavedModel.
                          Defaults to YAMNet_TFHUB_HANDLE.
        """
        self.model_handle = model_handle or YAMNet_TFHUB_HANDLE
        self._model = None
        self._class_names: List[str] = []

    def load(self) -> None:
        """Load YAMNet model into memory and load AudioSet class names.

        Raises:
            RuntimeError: If model cannot be downloaded or initialized.
        """
        if self._model is not None:
            return

        if hub is None or tf is None:
            logger.warning("TensorFlow / TF-Hub not installed in current environment.")
            return

        logger.info("Loading YAMNet model from: %s", self.model_handle)
        try:
            self._model = hub.load(self.model_handle)
            self._load_class_map()
            logger.info(
                "YAMNet loaded successfully (%d AudioSet classes).",
                len(self._class_names),
            )
        except Exception as e:
            logger.error("Failed to load YAMNet from %s: %s", self.model_handle, e)
            raise RuntimeError(f"YAMNet loading failed: {e}") from e

    def _load_class_map(self) -> None:
        """Read official AudioSet 521 class names from the YAMNet model asset."""
        try:
            # model.class_map_path() returns a tf.Tensor pointing to yamnet_class_map.csv
            class_map_path_tensor = self._model.class_map_path()
            csv_path = class_map_path_tensor.numpy().decode("utf-8")
            class_names: List[str] = []
            with open(csv_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    class_names.append(row["display_name"])
            self._class_names = class_names
        except Exception as e:
            logger.warning("Could not read class_map from model asset: %s. Using index labels.", e)
            self._class_names = [f"AudioSet_Class_{i}" for i in range(521)]

    @property
    def is_loaded(self) -> bool:
        """Check if model is currently loaded."""
        return self._model is not None

    @property
    def class_names(self) -> List[str]:
        """Return list of AudioSet class display names."""
        return list(self._class_names)

    def infer(
        self, waveform: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Run YAMNet inference on a 1D mono 16 kHz float32 waveform.

        Args:
            waveform: 1D numpy array of audio samples at 16 kHz.

        Returns:
            Tuple of:
                scores: (N_frames, 521) AudioSet class probabilities.
                embeddings: (N_frames, 1024) feature embeddings.
                spectrogram: (N_spectrogram_frames, 64) log mel spectrogram.

        Raises:
            RuntimeError: If model is not loaded.
            ValueError: If input waveform is invalid or empty.
        """
        if not self.is_loaded:
            self.load()

        if waveform.ndim != 1:
            raise ValueError(
                f"Expected 1D waveform, got shape {waveform.shape} with {waveform.ndim} dims."
            )
        if len(waveform) == 0:
            raise ValueError("Input waveform is empty.")

        waveform_tensor = tf.convert_to_tensor(waveform, dtype=tf.float32)
        scores_tf, embeddings_tf, spectrogram_tf = self._model(waveform_tensor)

        scores = scores_tf.numpy()
        embeddings = embeddings_tf.numpy()
        spectrogram = spectrogram_tf.numpy()

        # Enforce embedding dimension integrity
        if embeddings.ndim == 2 and embeddings.shape[1] != YAMNet_EMBEDDING_DIM:
            raise ValueError(
                f"Unexpected embedding dimension: {embeddings.shape[1]}, expected {YAMNet_EMBEDDING_DIM}"
            )

        return scores, embeddings, spectrogram

    def extract_embeddings(self, waveform: np.ndarray) -> np.ndarray:
        """Extract only the 1,024-dimensional frame embeddings for downstream classifier use.

        Args:
            waveform: 1D numpy array of audio samples at 16 kHz.

        Returns:
            embeddings: (N_frames, 1024) float32 numpy array.
        """
        _, embeddings, _ = self.infer(waveform)
        return embeddings

    def predict_top_k(
        self, waveform: np.ndarray, k: int = 5
    ) -> List[Dict[str, Any]]:
        """Predict top-k AudioSet classes averaged over the audio duration.

        NOTE: These predictions reflect pretrained AudioSet categories, NOT the
        custom festival scream classifier.

        Args:
            waveform: 1D mono 16 kHz float32 audio.
            k: Number of top classes to return (default: 5).

        Returns:
            List of dictionaries sorted by score descending:
                [
                    {
                        "class_index": int,
                        "display_name": str,
                        "mean_score": float,
                        "max_score": float,
                    },
                    ...
                ]
        """
        scores, _, _ = self.infer(waveform)

        # Average class scores across all frames
        mean_scores = np.mean(scores, axis=0)
        max_scores = np.max(scores, axis=0)

        # Get indices sorted descending by mean score
        top_indices = np.argsort(mean_scores)[::-1][:k]

        results = []
        for idx in top_indices:
            name = (
                self._class_names[idx]
                if idx < len(self._class_names)
                else f"AudioSet_Class_{idx}"
            )
            results.append(
                {
                    "class_index": int(idx),
                    "display_name": name,
                    "mean_score": round(float(mean_scores[idx]), 4),
                    "max_score": round(float(max_scores[idx]), 4),
                }
            )

        return results
