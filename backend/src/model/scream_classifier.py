"""Reusable Festival Scream Classifier Inference Module.

Provides end-to-end inference capabilities:
1. Feature-level prediction from 2,048-dim concatenated YAMNet embeddings or (N, 1024) frame sequences.
2. Raw waveform audio prediction with integrated YAMNet embedding extraction and pooling.
3. WAV file inference with robust error handling and metadata tracking.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import joblib
import numpy as np

from src.audio.preprocessor import load_audio
from src.config import (
    BACKEND_DIR,
    MODELS_DIR,
    TARGET_SAMPLE_RATE,
    YAMNet_EMBEDDING_DIM,
)
from src.model.yamnet_loader import YAMNetLoader

logger = logging.getLogger("scream_classifier")


class ModelNotLoadedError(Exception):
    """Raised when inference is attempted on an uninitialized classifier."""
    pass


class InvalidFeatureDimensionError(ValueError):
    """Raised when input feature dimensions do not match the expected model input."""
    pass


class FestivalScreamClassifier:
    """Production wrapper for custom festival scream classifier."""

    def __init__(
        self,
        model_path: Optional[Union[str, Path]] = None,
        metadata_path: Optional[Union[str, Path]] = None,
    ):
        """Initialize classifier, optionally loading model from specified paths."""
        self.model_path = Path(model_path) if model_path else (MODELS_DIR / "scream_classifier.joblib")
        self.metadata_path = Path(metadata_path) if metadata_path else (MODELS_DIR / "model_metadata.json")
        self.pipeline: Any = None
        self.metadata: Dict[str, Any] = {}
        self.threshold: float = 0.5
        self.expected_dim: int = YAMNet_EMBEDDING_DIM * 2  # 2048 by default
        self.feature_type: str = "clip_embedding"
        self._yamnet_loader: Optional[YAMNetLoader] = None

        if self.model_path.exists() and self.metadata_path.exists():
            self.load()

    def load(
        self,
        model_path: Optional[Union[str, Path]] = None,
        metadata_path: Optional[Union[str, Path]] = None,
    ) -> None:
        """Load trained pipeline and metadata configuration from disk."""
        if model_path:
            self.model_path = Path(model_path)
        if metadata_path:
            self.metadata_path = Path(metadata_path)

        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found at: {self.model_path}")
        if not self.metadata_path.exists():
            raise FileNotFoundError(f"Model metadata not found at: {self.metadata_path}")

        # Load metadata first
        with open(self.metadata_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

        self.threshold = float(self.metadata.get("selected_threshold", 0.5))
        self.feature_type = str(self.metadata.get("feature_representation", "clip_embedding"))
        if self.feature_type == "clip_embedding":
            self.expected_dim = YAMNet_EMBEDDING_DIM * 2  # 2048
        elif self.feature_type in ("mean_pooled", "max_pooled"):
            self.expected_dim = YAMNet_EMBEDDING_DIM  # 1024

        # Load scikit-learn pipeline
        self.pipeline = joblib.load(str(self.model_path))
        logger.info(
            f"Loaded {self.metadata.get('model_type')} pipeline from {self.model_path} "
            f"(threshold: {self.threshold:.3f}, expected_dim: {self.expected_dim})"
        )

    @property
    def is_loaded(self) -> bool:
        """Check if pipeline and metadata are successfully initialized."""
        return self.pipeline is not None and len(self.metadata) > 0

    def pool_frame_embeddings(self, frame_embeddings: np.ndarray) -> np.ndarray:
        """Pool (N_frames, 1024) sequence into the model's required feature vector."""
        if frame_embeddings.ndim != 2 or frame_embeddings.shape[1] != YAMNet_EMBEDDING_DIM:
            raise InvalidFeatureDimensionError(
                f"Expected frame embeddings of shape (N, {YAMNet_EMBEDDING_DIM}), got {frame_embeddings.shape}"
            )

        mean_p = np.mean(frame_embeddings, axis=0).astype(np.float32)
        max_p = np.max(frame_embeddings, axis=0).astype(np.float32)

        if self.feature_type == "clip_embedding":
            return np.concatenate([mean_p, max_p], axis=0)
        elif self.feature_type == "mean_pooled":
            return mean_p
        elif self.feature_type == "max_pooled":
            return max_p
        else:
            raise ValueError(f"Unsupported feature type: {self.feature_type}")

    def predict_features(
        self,
        features: np.ndarray,
        custom_threshold: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Predict scream probability and binary decision from feature representation.

        Args:
            features: 1D array of shape (D,) or 2D array of shape (1, D) matching expected_dim,
                      or 2D frame sequence of shape (N, 1024).
            custom_threshold: Optional override for decision threshold.

        Returns:
            Dict containing probability, binary decision, threshold, label, and metadata.
        """
        if not self.is_loaded:
            raise ModelNotLoadedError("Classifier must be loaded before calling predict_features().")

        threshold = custom_threshold if custom_threshold is not None else self.threshold

        # If passed frame-level sequence (N, 1024)
        if features.ndim == 2 and features.shape[1] == YAMNet_EMBEDDING_DIM:
            feat_vec = self.pool_frame_embeddings(features)
        elif features.ndim == 1:
            feat_vec = features
        elif features.ndim == 2 and features.shape[0] == 1:
            feat_vec = features[0]
        else:
            feat_vec = features

        # Automatic adaptation between 2048 (clip_embedding) and 1024 (mean/max)
        if feat_vec.ndim == 1 and feat_vec.shape[0] == YAMNet_EMBEDDING_DIM * 2:
            if self.feature_type == "max_pooled":
                feat_vec = feat_vec[YAMNet_EMBEDDING_DIM:]  # Second half is max_pooled
            elif self.feature_type == "mean_pooled":
                feat_vec = feat_vec[:YAMNet_EMBEDDING_DIM]  # First half is mean_pooled

        if feat_vec.ndim != 1 or feat_vec.shape[0] != self.expected_dim:
            raise InvalidFeatureDimensionError(
                f"Feature vector dimensionality mismatch: expected ({self.expected_dim},), "
                f"received {feat_vec.shape}"
            )

        if not np.isfinite(feat_vec).all():
            raise ValueError("Input feature vector contains non-finite values (NaN / Inf).")

        X = feat_vec.reshape(1, -1)
        # Predict probability for positive class (scream = 1)
        probs = self.pipeline.predict_proba(X)[0]
        prob_scream = float(probs[1])
        prob_non_scream = float(probs[0])
        is_scream = bool(prob_scream >= threshold)

        return {
            "scream_probability": prob_scream,
            "non_scream_probability": prob_non_scream,
            "is_scream": is_scream,
            "predicted_label": "scream" if is_scream else "non_scream",
            "threshold": threshold,
            "margin_to_threshold": prob_scream - threshold,
            "model_type": self.metadata.get("model_type", "Unknown"),
            "model_version": self.metadata.get("version", "v1.0.0"),
            "feature_representation": self.feature_type,
        }

    def predict_audio(
        self,
        waveform: np.ndarray,
        yamnet_loader: Optional[YAMNetLoader] = None,
        custom_threshold: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Perform end-to-end inference on a preprocessed 16kHz audio waveform.

        Args:
            waveform: 1D float32 array at 16,000 Hz.
            yamnet_loader: Optional loaded YAMNetLoader instance (cached if omitted).
            custom_threshold: Optional override for decision threshold.

        Returns:
            Dict containing scream prediction and YAMNet diagnostic priors.
        """
        if waveform.ndim != 1 or len(waveform) == 0:
            raise ValueError("Audio waveform must be a non-empty 1D array.")

        loader = yamnet_loader or self._get_yamnet_loader()
        scores, embeddings, _ = loader.infer(waveform)

        pooled_vector = self.pool_frame_embeddings(embeddings)
        pred = self.predict_features(pooled_vector, custom_threshold=custom_threshold)

        # Attach auxiliary acoustic diagnostics
        pred["audio_duration_seconds"] = round(len(waveform) / TARGET_SAMPLE_RATE, 3)
        pred["num_yamnet_frames"] = embeddings.shape[0]

        # Top 3 general YAMNet priors for comparison
        mean_scores = np.mean(scores, axis=0)
        top_indices = np.argsort(mean_scores)[::-1][:3]
        pred["yamnet_top_priors"] = [
            {"class_name": loader.class_names[idx], "score": round(float(mean_scores[idx]), 4)}
            for idx in top_indices
        ]

        return pred

    def predict_file(
        self,
        audio_path: Union[str, Path],
        yamnet_loader: Optional[YAMNetLoader] = None,
        custom_threshold: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Perform end-to-end inference on an audio file on disk."""
        target_path = Path(audio_path).resolve()
        if not target_path.exists():
            raise FileNotFoundError(f"Audio file not found: {target_path}")

        waveform, meta = load_audio(target_path, target_sr=TARGET_SAMPLE_RATE)
        pred = self.predict_audio(waveform, yamnet_loader=yamnet_loader, custom_threshold=custom_threshold)
        pred["audio_path"] = str(target_path)
        pred["filename"] = target_path.name
        pred["original_sample_rate"] = meta.original_sample_rate
        pred["original_channels"] = meta.original_channels
        return pred

    def _get_yamnet_loader(self) -> YAMNetLoader:
        """Get or initialize singleton YAMNetLoader."""
        if self._yamnet_loader is None:
            self._yamnet_loader = YAMNetLoader()
            self._yamnet_loader.load()
        return self._yamnet_loader
