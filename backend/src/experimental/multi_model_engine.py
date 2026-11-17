"""Multi-Model Live Inference Engine and Audio Testing Lab.

Orchestrates real-time simultaneous testing of multiple experimental scream detection models:
1. Primary Experimental Model: D_v4 + Family A (Stage 8.9.14 Acoustic Discriminability, Threshold: 0.420)
2. Comparison Candidates:
   - D_v4 + Family B (Stage 8.9.14 Spectral Dynamics, Threshold: 0.650)
   - F_v6 Acoustic Full (Stage 8.9.14 30 Features, Threshold: 0.360)
   - Stage 8.9.15 Model A (Compact Regularized MLP, Threshold: 0.440)
   - Stage 8.9.15 Model B (Temporal 1D Dilated CNN, Threshold: 0.610)
   - Stage 8.9.15 Model C (Hierarchical Hybrid Fusion, Threshold: 0.500)
3. Production Reference: Production Baseline (Stage 5 Logistic Regression, Threshold: 0.3500)

Architecture Principles:
- Shared feature extraction: Single YAMNet pass + Single vectorized acoustic extraction per window.
- Isolated model evaluation: Each model receives identical audio windows with its own trained scaler,
  threshold, decision margin, and latency tracking.
- Zero production mutation: Never touches production artifacts or database/stage8_9_reviews.db.
- Fault isolation: If any model fails, error state is logged and remaining models continue running.
- Safety & Backpressure: Stale window detection, bounded buffering, dropped window tracking.
"""

from __future__ import annotations

import asyncio
import logging
import os
import threading
import time
import sys
from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import joblib
import numpy as np

# Suppress TF oneDNN spam
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

import tensorflow as tf
from tensorflow import keras

from experiments.v2_hard_negative_training.v4_temporal_research.stage8_9_14_acoustic_discriminability.acoustic_discriminability_features import (
    AcousticDiscriminabilityExtractor,
)
from src.config import (
    DEFAULT_SCREAM_THRESHOLD,
    TARGET_SAMPLE_RATE,
    YAMNet_FRAME_SECONDS,
    YAMNet_HOP_SECONDS,
)
from src.detector.audio_buffer import RollingAudioBuffer
from src.detector.mic_capture import MicrophoneCapture
from src.experimental.registry import ExperimentalModelRegistry, ModelMetadata
from src.experimental.session_store import ExperimentalSessionStore
from src.model.yamnet_loader import YAMNetLoader

logger = logging.getLogger("multi_model_engine")
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


@dataclass
class SingleModelPrediction:
    """Prediction result from an individual model for a single audio window."""
    model_id: str
    display_name: str
    stage: str
    score: float
    threshold: float
    decision_margin: float
    is_scream: bool
    classification: str  # SCREAM_CANDIDATE, NON_SCREAM, UNCERTAIN, MODEL_ERROR, NO_ACOUSTIC_ACTIVITY
    latency_ms: float
    status: str          # ACTIVE, ERROR, DISABLED
    error_message: Optional[str] = None
    raw_score: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SynchronizedWindowResult:
    """Synchronized multi-model predictions for a single audio window."""
    window_index: int
    timestamp: float
    iso_timestamp: str
    audio_rms: float
    audio_peak: float
    is_clipping: bool
    is_silent: bool
    acoustic_gate_active: bool
    shared_feature_latency_ms: float
    total_latency_ms: float
    primary_prediction: SingleModelPrediction
    production_prediction: SingleModelPrediction
    all_predictions: Dict[str, SingleModelPrediction]
    agreement: Dict[str, Any]
    dropped_windows_total: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "window_index": self.window_index,
            "timestamp": self.timestamp,
            "iso_timestamp": self.iso_timestamp,
            "audio_rms": round(self.audio_rms, 6),
            "audio_peak": round(self.audio_peak, 4),
            "is_clipping": self.is_clipping,
            "is_silent": self.is_silent,
            "acoustic_gate_active": self.acoustic_gate_active,
            "shared_feature_latency_ms": round(self.shared_feature_latency_ms, 2),
            "total_latency_ms": round(self.total_latency_ms, 2),
            "primary_prediction": self.primary_prediction.to_dict(),
            "production_prediction": self.production_prediction.to_dict(),
            "all_predictions": {k: v.to_dict() for k, v in self.all_predictions.items()},
            "agreement": self.agreement,
            "dropped_windows_total": self.dropped_windows_total,
        }


class MultiModelLiveEngine:
    """Core multi-model inference pipeline executing on identical audio windows."""

    def __init__(
        self,
        backend_dir: Optional[Path] = None,
        yamnet_loader: Optional[YAMNetLoader] = None,
        acoustic_extractor: Optional[AcousticDiscriminabilityExtractor] = None,
        acoustic_gate_enabled: bool = True,
        acoustic_gate_rms_threshold: float = 0.0035,
        acoustic_gate_peak_threshold: float = 0.010,
    ):
        self.backend_dir = backend_dir or BACKEND_DIR
        self.registry = ExperimentalModelRegistry(self.backend_dir)
        self.yamnet_loader = yamnet_loader or YAMNetLoader()
        self.acoustic_extractor = acoustic_extractor or AcousticDiscriminabilityExtractor(sr=TARGET_SAMPLE_RATE)
        self.acoustic_gate_enabled = acoustic_gate_enabled
        self.acoustic_gate_rms_threshold = acoustic_gate_rms_threshold
        self.acoustic_gate_peak_threshold = acoustic_gate_peak_threshold

        # Loaded model artifact instances
        self._models: Dict[str, Any] = {}
        self._scalers: Dict[str, Any] = {}
        self._model_errors: Dict[str, str] = {}

        # Enabled toggle per model (default all enabled)
        self.enabled_models: Dict[str, bool] = {
            m.model_id: True for m in self.registry.list_models()
        }

        # Stacking feature indices for Stage 8.9.15 Model C
        self._stage15_top_indices = [11, 23, 17, 26, 10, 2]

        self._load_all_models()

    def set_acoustic_gate(
        self,
        enabled: bool,
        rms_threshold: Optional[float] = None,
        peak_threshold: Optional[float] = None,
    ) -> None:
        """Configure acoustic activity gate settings for live testing or diagnostic mode."""
        self.acoustic_gate_enabled = bool(enabled)
        if rms_threshold is not None:
            self.acoustic_gate_rms_threshold = float(rms_threshold)
        if peak_threshold is not None:
            self.acoustic_gate_peak_threshold = float(peak_threshold)

    def _load_all_models(self) -> None:
        """Load all model checkpoints and scalers into memory."""
        logger.info("Initializing Multi-Model Live Engine models...")

        # 1. Ensure YAMNet is loaded
        if not self.yamnet_loader.is_loaded:
            logger.info("Loading shared Google YAMNet backbone...")
            self.yamnet_loader.load()

        # Paths
        s14_dir = self.backend_dir / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_14_acoustic_discriminability" / "models"
        s15_dir = self.backend_dir / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_15_hierarchical_phonation" / "models"
        prod_path = self.backend_dir / "models" / "scream_classifier.joblib"

        # Load Stage 8.9.14 Models
        try:
            self._models["D_V4_FAMILY_A"] = joblib.load(s14_dir / "D_v4_plus_Family_A.joblib")
            logger.info("Loaded Primary Model: D_v4 + Family A")
        except Exception as e:
            logger.error("Failed to load D_v4_plus_Family_A: %s", e)
            self._model_errors["D_V4_FAMILY_A"] = str(e)

        try:
            self._models["D_V4_FAMILY_B"] = joblib.load(s14_dir / "D_v4_plus_Family_B.joblib")
            logger.info("Loaded Comparison Candidate: D_v4 + Family B")
        except Exception as e:
            logger.error("Failed to load D_v4_plus_Family_B: %s", e)
            self._model_errors["D_V4_FAMILY_B"] = str(e)

        try:
            self._models["F_V6_ACOUSTIC"] = joblib.load(s14_dir / "F_v6_Acoustic_Full.joblib")
            logger.info("Loaded Comparison Candidate: F_v6 Acoustic Full")
        except Exception as e:
            logger.error("Failed to load F_v6_Acoustic_Full: %s", e)
            self._model_errors["F_V6_ACOUSTIC"] = str(e)

        # Load Stage 8.9.15 Models and Scalers
        try:
            self._scalers["s15_feature_scaler"] = joblib.load(s15_dir / "stage8_9_15_feature_scaler.joblib")
            self._scalers["s15_acoustic_scaler"] = joblib.load(s15_dir / "stage8_9_15_acoustic_scaler.joblib")
            self._scalers["s15_fusion_scaler"] = joblib.load(s15_dir / "stage8_9_15_fusion_scaler.joblib")

            self._models["STAGE_8915_GATE_A"] = joblib.load(s15_dir / "Gate_A_ExtraTrees.joblib")
            self._models["STAGE_8915_MODEL_A"] = joblib.load(s15_dir / "Model_A_Compact_MLP.joblib")
            self._models["STAGE_8915_MODEL_B"] = keras.models.load_model(s15_dir / "Model_B_Temporal_CNN.keras")
            self._models["STAGE_8915_MODEL_C"] = joblib.load(s15_dir / "Model_C_Hierarchical_Fusion.joblib")
            logger.info("Loaded Stage 8.9.15 Models A, B, C and Gate A")
        except Exception as e:
            logger.error("Failed to load Stage 8.9.15 models: %s", e)
            self._model_errors["STAGE_8915_MODEL_A"] = str(e)
            self._model_errors["STAGE_8915_MODEL_B"] = str(e)
            self._model_errors["STAGE_8915_MODEL_C"] = str(e)

        # Load Production Baseline
        try:
            self._models["PRODUCTION_BASELINE"] = joblib.load(prod_path)
            logger.info("Loaded Production Baseline (Stage 5 LR)")
        except Exception as e:
            logger.error("Failed to load Production Baseline: %s", e)
            self._model_errors["PRODUCTION_BASELINE"] = str(e)

    def set_model_enabled(self, model_id: str, enabled: bool) -> bool:
        """Enable or disable a model for live comparison."""
        if model_id in self.enabled_models:
            self.enabled_models[model_id] = bool(enabled)
            return True
        return False

    def get_models_overview(self) -> List[Dict[str, Any]]:
        """Return full metadata, loading status, and runtime toggles for all models."""
        overview = []
        for meta in self.registry.list_models():
            m_dict = meta.to_dict()
            m_dict["is_enabled"] = self.enabled_models.get(meta.model_id, True)
            if meta.model_id in self._model_errors:
                m_dict["status"] = "ERROR"
                m_dict["error_message"] = self._model_errors[meta.model_id]
                m_dict["inference_available"] = False
            else:
                m_dict["status"] = "LOADED"
                m_dict["inference_available"] = True
            overview.append(m_dict)
        return overview

    def extract_shared_features(
        self, waveform: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Extract shared YAMNet and acoustic feature representations from audio window.

        Returns:
            embs: Raw frame embeddings (T, 1024)
            features_concat: 3,072-dim multi-pooled YAMNet vector [f_max, f_p10, f_mean]
            acoustic_30: 30-dim acoustic discriminability vector
            spectrogram: (N_frames, 64) log-mel spectrogram
        """
        # DC offset removal & sanitation
        clean_wave = np.nan_to_num(waveform, nan=0.0, posinf=1.0, neginf=-1.0)
        clean_wave = clean_wave - np.mean(clean_wave)

        # YAMNet inference
        _, embs, spectrogram = self.yamnet_loader.infer(clean_wave)

        # Multi-pooling in exact trained order: [f_max, f_p10, f_mean]
        f_max = np.max(embs, axis=0)
        f_p10 = np.percentile(embs, 10, axis=0)
        f_mean = np.mean(embs, axis=0)
        features_concat = np.concatenate([f_max, f_p10, f_mean]).astype(np.float32)

        # 30-dim acoustic discriminability features
        acoustic_30 = self.acoustic_extractor.extract_features(clean_wave).astype(np.float32)

        return embs, features_concat, acoustic_30, spectrogram

    def process_window(
        self,
        waveform: np.ndarray,
        window_index: int,
        timestamp: float,
        dropped_windows_total: int = 0,
    ) -> SynchronizedWindowResult:
        """Run all enabled models on the single incoming audio window."""
        t_start = time.perf_counter()

        # Audio signal metrics
        rms = float(np.sqrt(np.mean(waveform ** 2) + 1e-12))
        peak = float(np.max(np.abs(waveform)))
        is_clipping = peak >= 0.99
        is_silent = bool(rms < self.acoustic_gate_rms_threshold and peak < self.acoustic_gate_peak_threshold)
        acoustic_gate_active = bool(is_silent and self.acoustic_gate_enabled)

        predictions: Dict[str, SingleModelPrediction] = {}

        if acoustic_gate_active:
            # Bypass heavy feature extraction and neural inference on silence
            shared_feat_latency_ms = 0.0
            for meta in self.registry.list_models():
                mid = meta.model_id
                if not self.enabled_models.get(mid, True):
                    predictions[mid] = self._disabled_pred(meta)
                elif mid in self._model_errors:
                    predictions[mid] = self._error_pred(meta, self._model_errors[mid])
                else:
                    predictions[mid] = SingleModelPrediction(
                        model_id=mid,
                        display_name=meta.display_name,
                        stage=meta.stage,
                        score=0.0,
                        threshold=meta.operating_threshold,
                        decision_margin=-meta.operating_threshold,
                        is_scream=False,
                        classification="NO_ACOUSTIC_ACTIVITY",
                        latency_ms=0.0,
                        status="ACTIVE",
                        error_message=None,
                        raw_score=0.0,
                    )
        else:
            # Step 1: Extract shared features
            t_feat_start = time.perf_counter()
            embs, features_concat, acoustic_30, _ = self.extract_shared_features(waveform)
            shared_feat_latency_ms = (time.perf_counter() - t_feat_start) * 1000.0

            # Step 2: Evaluate individual models
            # --- 1. Primary Model: D_v4 + Family A (Stage 8.9.14) ---
            predictions["D_V4_FAMILY_A"] = self._eval_d_v4_family_a(features_concat, acoustic_30)

            # --- 2. Comparison: D_v4 + Family B (Stage 8.9.14) ---
            predictions["D_V4_FAMILY_B"] = self._eval_d_v4_family_b(features_concat, acoustic_30)

            # --- 3. Comparison: F_v6 Acoustic Full (Stage 8.9.14) ---
            predictions["F_V6_ACOUSTIC"] = self._eval_f_v6_acoustic(features_concat, acoustic_30)

            # --- 4. Comparison: Stage 8.9.15 Model A (Compact MLP) ---
            predictions["STAGE_8915_MODEL_A"] = self._eval_stage15_model_a(features_concat, acoustic_30)

            # --- 5. Comparison: Stage 8.9.15 Model B (Temporal Dilated CNN) ---
            predictions["STAGE_8915_MODEL_B"] = self._eval_stage15_model_b(embs, acoustic_30)

            # --- 6. Comparison: Stage 8.9.15 Model C (Learned Hybrid Fusion) ---
            predictions["STAGE_8915_MODEL_C"] = self._eval_stage15_model_c(
                features_concat,
                acoustic_30,
                mlp_pred=predictions["STAGE_8915_MODEL_A"],
                tcn_pred=predictions["STAGE_8915_MODEL_B"],
            )

            # --- 7. Reference: Production Baseline (Stage 5 LR) ---
            predictions["PRODUCTION_BASELINE"] = self._eval_production_baseline(embs)

        total_latency_ms = (time.perf_counter() - t_start) * 1000.0

        # Step 3: Compute Model Agreement
        active_preds = [p for p in predictions.values() if p.status == "ACTIVE"]
        scream_count = sum(1 for p in active_preds if p.is_scream)
        non_scream_count = sum(1 for p in active_preds if not p.is_scream and p.classification in ("NON_SCREAM", "NO_ACOUSTIC_ACTIVITY"))
        uncertain_count = sum(1 for p in active_preds if p.classification == "UNCERTAIN")

        primary_p = predictions["D_V4_FAMILY_A"]
        prod_p = predictions["PRODUCTION_BASELINE"]

        agreement = {
            "total_active_models": len(active_preds),
            "scream_votes": scream_count,
            "non_scream_votes": non_scream_count,
            "uncertain_votes": uncertain_count,
            "disagreement_detected": (scream_count > 0 and non_scream_count > 0),
            "primary_prediction": primary_p.classification,
            "production_prediction": prod_p.classification,
            "primary_vs_production_divergence": (primary_p.is_scream != prod_p.is_scream),
        }

        iso_ts = datetime.fromtimestamp(timestamp).isoformat()

        return SynchronizedWindowResult(
            window_index=window_index,
            timestamp=timestamp,
            iso_timestamp=iso_ts,
            audio_rms=rms,
            audio_peak=peak,
            is_clipping=is_clipping,
            is_silent=is_silent,
            acoustic_gate_active=acoustic_gate_active,
            shared_feature_latency_ms=shared_feat_latency_ms,
            total_latency_ms=total_latency_ms,
            primary_prediction=primary_p,
            production_prediction=prod_p,
            all_predictions=predictions,
            agreement=agreement,
            dropped_windows_total=dropped_windows_total,
        )

    # -------------------------------------------------------------------------
    # Individual Model Evaluation Helpers
    # -------------------------------------------------------------------------

    def _eval_d_v4_family_a(self, features_concat: np.ndarray, acoustic_30: np.ndarray) -> SingleModelPrediction:
        meta = self.registry.get_model("D_V4_FAMILY_A")
        if not self.enabled_models.get("D_V4_FAMILY_A", True):
            return self._disabled_pred(meta)
        if "D_V4_FAMILY_A" not in self._models:
            return self._error_pred(meta, self._model_errors.get("D_V4_FAMILY_A", "Model not loaded"))

        t0 = time.perf_counter()
        try:
            # 3,080 dims: 3,072 YAMNet + 8 Family A
            feat = np.concatenate([features_concat, acoustic_30[:8]]).reshape(1, -1)
            score = float(self._models["D_V4_FAMILY_A"].predict_proba(feat)[0, 1])
            lat = (time.perf_counter() - t0) * 1000.0
            return self._build_pred(meta, score, lat)
        except Exception as e:
            lat = (time.perf_counter() - t0) * 1000.0
            return self._error_pred(meta, str(e), lat)

    def _eval_d_v4_family_b(self, features_concat: np.ndarray, acoustic_30: np.ndarray) -> SingleModelPrediction:
        meta = self.registry.get_model("D_V4_FAMILY_B")
        if not self.enabled_models.get("D_V4_FAMILY_B", True):
            return self._disabled_pred(meta)
        if "D_V4_FAMILY_B" not in self._models:
            return self._error_pred(meta, self._model_errors.get("D_V4_FAMILY_B", "Model not loaded"))

        t0 = time.perf_counter()
        try:
            # 3,080 dims: 3,072 YAMNet + 8 Family B (indices 8:16)
            feat = np.concatenate([features_concat, acoustic_30[8:16]]).reshape(1, -1)
            score = float(self._models["D_V4_FAMILY_B"].predict_proba(feat)[0, 1])
            lat = (time.perf_counter() - t0) * 1000.0
            return self._build_pred(meta, score, lat)
        except Exception as e:
            lat = (time.perf_counter() - t0) * 1000.0
            return self._error_pred(meta, str(e), lat)

    def _eval_f_v6_acoustic(self, features_concat: np.ndarray, acoustic_30: np.ndarray) -> SingleModelPrediction:
        meta = self.registry.get_model("F_V6_ACOUSTIC")
        if not self.enabled_models.get("F_V6_ACOUSTIC", True):
            return self._disabled_pred(meta)
        if "F_V6_ACOUSTIC" not in self._models:
            return self._error_pred(meta, self._model_errors.get("F_V6_ACOUSTIC", "Model not loaded"))

        t0 = time.perf_counter()
        try:
            # 3,102 dims: 3,072 YAMNet + 30 Acoustic
            feat = np.concatenate([features_concat, acoustic_30]).reshape(1, -1)
            score = float(self._models["F_V6_ACOUSTIC"].predict_proba(feat)[0, 1])
            lat = (time.perf_counter() - t0) * 1000.0
            return self._build_pred(meta, score, lat)
        except Exception as e:
            lat = (time.perf_counter() - t0) * 1000.0
            return self._error_pred(meta, str(e), lat)

    def _eval_stage15_model_a(self, features_concat: np.ndarray, acoustic_30: np.ndarray) -> SingleModelPrediction:
        meta = self.registry.get_model("STAGE_8915_MODEL_A")
        if not self.enabled_models.get("STAGE_8915_MODEL_A", True):
            return self._disabled_pred(meta)
        if "STAGE_8915_MODEL_A" not in self._models or "s15_feature_scaler" not in self._scalers:
            return self._error_pred(meta, self._model_errors.get("STAGE_8915_MODEL_A", "Model not loaded"))

        t0 = time.perf_counter()
        try:
            feat_raw = np.concatenate([features_concat, acoustic_30]).reshape(1, -1)
            feat_scaled = self._scalers["s15_feature_scaler"].transform(feat_raw)
            score = float(self._models["STAGE_8915_MODEL_A"].predict_proba(feat_scaled)[0, 1])
            lat = (time.perf_counter() - t0) * 1000.0
            return self._build_pred(meta, score, lat)
        except Exception as e:
            lat = (time.perf_counter() - t0) * 1000.0
            return self._error_pred(meta, str(e), lat)

    def _eval_stage15_model_b(self, embs: np.ndarray, acoustic_30: np.ndarray) -> SingleModelPrediction:
        meta = self.registry.get_model("STAGE_8915_MODEL_B")
        if not self.enabled_models.get("STAGE_8915_MODEL_B", True):
            return self._disabled_pred(meta)
        if "STAGE_8915_MODEL_B" not in self._models or "s15_acoustic_scaler" not in self._scalers:
            return self._error_pred(meta, self._model_errors.get("STAGE_8915_MODEL_B", "Model not loaded"))

        t0 = time.perf_counter()
        try:
            seq_padded = np.zeros((1, 70, 1024), dtype=np.float32)
            n_frames = min(70, embs.shape[0])
            seq_padded[0, :n_frames, :] = embs[:n_frames, :]

            ac_scaled = self._scalers["s15_acoustic_scaler"].transform(acoustic_30.reshape(1, -1))
            score = float(self._models["STAGE_8915_MODEL_B"]([seq_padded, ac_scaled], training=False).numpy()[0, 0])
            lat = (time.perf_counter() - t0) * 1000.0
            return self._build_pred(meta, score, lat)
        except Exception as e:
            lat = (time.perf_counter() - t0) * 1000.0
            return self._error_pred(meta, str(e), lat)

    def _eval_stage15_model_c(
        self,
        features_concat: np.ndarray,
        acoustic_30: np.ndarray,
        mlp_pred: SingleModelPrediction,
        tcn_pred: SingleModelPrediction,
    ) -> SingleModelPrediction:
        meta = self.registry.get_model("STAGE_8915_MODEL_C")
        if not self.enabled_models.get("STAGE_8915_MODEL_C", True):
            return self._disabled_pred(meta)
        if (
            "STAGE_8915_MODEL_C" not in self._models
            or "STAGE_8915_GATE_A" not in self._models
            or "s15_fusion_scaler" not in self._scalers
        ):
            return self._error_pred(meta, self._model_errors.get("STAGE_8915_MODEL_C", "Model not loaded"))

        t0 = time.perf_counter()
        try:
            # Stage 1 Gate prob
            feat_raw = np.concatenate([features_concat, acoustic_30]).reshape(1, -1)
            feat_scaled = self._scalers["s15_feature_scaler"].transform(feat_raw)
            gate_prob = float(self._models["STAGE_8915_GATE_A"].predict_proba(feat_scaled)[0, 1])

            # Intermediate Model A and Model B probs
            mlp_prob = mlp_pred.score if mlp_pred.status == "ACTIVE" else 0.0
            tcn_prob = tcn_pred.score if tcn_pred.status == "ACTIVE" else 0.0

            # Top 6 acoustic features
            top_feats = acoustic_30[self._stage15_top_indices].reshape(1, -1)

            # 9-dim stacking input: [gate_prob, mlp_prob, tcn_prob, top_6_feats]
            fusion_in = np.hstack([[gate_prob], [mlp_prob], [tcn_prob], top_feats.flatten()]).reshape(1, -1)
            fusion_scaled = self._scalers["s15_fusion_scaler"].transform(fusion_in)

            score = float(self._models["STAGE_8915_MODEL_C"].predict_proba(fusion_scaled)[0, 1])
            lat = (time.perf_counter() - t0) * 1000.0
            return self._build_pred(meta, score, lat)
        except Exception as e:
            lat = (time.perf_counter() - t0) * 1000.0
            return self._error_pred(meta, str(e), lat)

    def _eval_production_baseline(self, embs: np.ndarray) -> SingleModelPrediction:
        meta = self.registry.get_model("PRODUCTION_BASELINE")
        if not self.enabled_models.get("PRODUCTION_BASELINE", True):
            return self._disabled_pred(meta)
        if "PRODUCTION_BASELINE" not in self._models:
            return self._error_pred(meta, self._model_errors.get("PRODUCTION_BASELINE", "Model not loaded"))

        t0 = time.perf_counter()
        try:
            # 1,024 dims: max-pooled YAMNet embedding
            emb_max = np.max(embs, axis=0).reshape(1, -1)
            score = float(self._models["PRODUCTION_BASELINE"].predict_proba(emb_max)[0, 1])
            lat = (time.perf_counter() - t0) * 1000.0
            return self._build_pred(meta, score, lat)
        except Exception as e:
            lat = (time.perf_counter() - t0) * 1000.0
            return self._error_pred(meta, str(e), lat)

    # -------------------------------------------------------------------------
    # Prediction Constructors
    # -------------------------------------------------------------------------

    def _build_pred(self, meta: ModelMetadata, score: float, latency_ms: float) -> SingleModelPrediction:
        th = meta.operating_threshold
        margin = score - th
        is_scream = score >= th

        if is_scream:
            classification = "SCREAM_CANDIDATE"
        elif abs(margin) <= 0.05:
            classification = "UNCERTAIN"
        else:
            classification = "NON_SCREAM"

        return SingleModelPrediction(
            model_id=meta.model_id,
            display_name=meta.display_name,
            stage=meta.stage,
            score=round(score, 4),
            threshold=th,
            decision_margin=round(margin, 4),
            is_scream=is_scream,
            classification=classification,
            latency_ms=round(latency_ms, 2),
            status="ACTIVE",
            error_message=None,
            raw_score=round(score, 4),
        )

    def _error_pred(self, meta: ModelMetadata, err_msg: str, latency_ms: float = 0.0) -> SingleModelPrediction:
        return SingleModelPrediction(
            model_id=meta.model_id,
            display_name=meta.display_name,
            stage=meta.stage,
            score=0.0,
            threshold=meta.operating_threshold,
            decision_margin=-meta.operating_threshold,
            is_scream=False,
            classification="MODEL_ERROR",
            latency_ms=round(latency_ms, 2),
            status="ERROR",
            error_message=err_msg,
        )

    def _disabled_pred(self, meta: ModelMetadata) -> SingleModelPrediction:
        return SingleModelPrediction(
            model_id=meta.model_id,
            display_name=meta.display_name,
            stage=meta.stage,
            score=0.0,
            threshold=meta.operating_threshold,
            decision_margin=0.0,
            is_scream=False,
            classification="DISABLED",
            latency_ms=0.0,
            status="DISABLED",
            error_message="Model disabled in Multi-Model Lab configuration",
        )


class MultiModelLiveService:
    """Thread-safe live streaming service managing shared microphone capture & multi-model testing."""

    def __init__(
        self,
        engine: Optional[MultiModelLiveEngine] = None,
        session_store: Optional[ExperimentalSessionStore] = None,
        sample_rate: int = TARGET_SAMPLE_RATE,
        window_duration_seconds: float = YAMNet_FRAME_SECONDS,  # 0.975s
        hop_duration_seconds: float = YAMNet_HOP_SECONDS,      # 0.4875s
    ):
        self.engine = engine or MultiModelLiveEngine()
        self.session_store = session_store or ExperimentalSessionStore()
        self.sample_rate = sample_rate
        self.window_samples = int(round(window_duration_seconds * sample_rate))
        self.hop_samples = int(round(hop_duration_seconds * sample_rate))

        # Shared audio buffer (15s capacity)
        self.buffer = RollingAudioBuffer(
            sample_rate=self.sample_rate,
            max_duration_seconds=15.0,
        )

        # Microphone capture & worker thread
        self.mic: Optional[MicrophoneCapture] = None
        self._worker_thread: Optional[threading.Thread] = None
        self._is_running: bool = False
        self._lock = threading.Lock()
        self._mic_status: str = "stopped"
        self._mic_error: Optional[str] = None
        self._selected_device_index: Optional[int] = None

        # Session tracking
        self.active_session_id: Optional[str] = None
        self.window_counter: int = 0
        self.dropped_windows_total: int = 0
        self.start_time: Optional[float] = None

        # Recent windows buffer for UI history (last 100 windows)
        self._history_lock = threading.Lock()
        self._window_history: deque[SynchronizedWindowResult] = deque(maxlen=100)

        # Event tracking state for multi-model live lab
        self._active_event: Optional[Dict[str, Any]] = None
        self._event_history: List[Dict[str, Any]] = []

        # WebSocket / listener subscriptions
        self._subscribers: Set[Callable[[Dict[str, Any]], None]] = set()

    def get_status(self) -> Dict[str, Any]:
        """Return runtime status of the multi-model live lab."""
        with self._lock:
            return {
                "is_running": self._is_running,
                "mic_status": self._mic_status,
                "mic_error": self._mic_error,
                "selected_device_index": self._selected_device_index,
                "active_session_id": self.active_session_id,
                "window_counter": self.window_counter,
                "dropped_windows_total": self.dropped_windows_total,
                "buffer_stats": {
                    "total_samples_written": self.buffer.total_samples_written,
                    "buffered_samples": self.buffer.buffered_samples,
                    "buffered_seconds": round(self.buffer.buffered_seconds, 2),
                    "dropped_samples": self.buffer.dropped_samples,
                    "capacity_seconds": 15.0,
                },
                "enabled_models": self.engine.enabled_models,
                "acoustic_gate": {
                    "enabled": self.engine.acoustic_gate_enabled,
                    "rms_threshold": self.engine.acoustic_gate_rms_threshold,
                    "peak_threshold": self.engine.acoustic_gate_peak_threshold,
                },
                "uptime_seconds": round(time.time() - self.start_time, 2) if (self._is_running and self.start_time) else 0.0,
            }

    def subscribe(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Register listener for live window results."""
        self._subscribers.add(callback)

    def unsubscribe(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Unregister listener."""
        self._subscribers.discard(callback)

    def _broadcast(self, msg: Dict[str, Any]) -> None:
        """Dispatch message to all subscribers."""
        for cb in list(self._subscribers):
            try:
                cb(msg)
            except Exception as e:
                logger.warning("Error dispatching to subscriber: %s", e)

    def start_testing(self, device_index: Optional[int] = None) -> Dict[str, Any]:
        """Start shared microphone capture and multi-model inference worker."""
        with self._lock:
            if self._is_running:
                return {"success": True, "message": "Already running", "status": self.get_status()}

            self.window_counter = 0
            self.dropped_windows_total = 0
            self.start_time = time.time()
            self._selected_device_index = device_index
            self.buffer.clear()

            # Initialize microphone capture
            try:
                self.mic = MicrophoneCapture(
                    on_audio_chunk=self._on_audio_chunk,
                    device_index=device_index,
                    sample_rate=self.sample_rate,
                    block_duration_ms=50.0,  # 50 ms chunks for low latency
                )
                self.mic.start()
                self._mic_status = "active"
                self._mic_error = None
            except Exception as e:
                logger.warning("Could not initialize microphone: %s. Entering synthetic/stream-ready mode.", e)
                self.mic = None
                self._mic_status = "unavailable"
                self._mic_error = str(e)

            self._is_running = True
            self._worker_thread = threading.Thread(
                target=self._worker_loop,
                name="MultiModelInferenceWorker",
                daemon=True,
            )
            self._worker_thread.start()

        self._broadcast({"type": "multimodel_status_changed", "status": self.get_status()})
        return {"success": True, "status": self.get_status()}

    def stop_testing(self) -> Dict[str, Any]:
        """Stop microphone capture and inference worker."""
        with self._lock:
            if not self._is_running:
                return {"success": True, "message": "Already stopped", "status": self.get_status()}

            self._is_running = False
            self._mic_status = "stopped"

            if self.mic:
                try:
                    self.mic.stop()
                except Exception as e:
                    logger.warning("Error stopping mic: %s", e)
                self.mic = None

        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=2.0)

        # Finalize any ongoing active event
        self._close_active_event_if_open()

        # If a session was active, close it
        if self.active_session_id:
            self.session_store.stop_session(
                self.active_session_id,
                total_windows=self.window_counter,
                dropped_windows=self.dropped_windows_total,
            )

        self._broadcast({"type": "multimodel_status_changed", "status": self.get_status()})
        return {"success": True, "status": self.get_status()}

    def _on_audio_chunk(self, chunk: np.ndarray) -> None:
        """Callback invoked by MicrophoneCapture on new audio frame."""
        self.buffer.write(chunk)

    def feed_audio(self, samples: np.ndarray) -> None:
        """Manually push audio samples into the shared buffer (e.g. for synthetic testing)."""
        self.buffer.write(samples)

    def _worker_loop(self) -> None:
        """Continuous background inference loop processing shared rolling windows."""
        logger.info("Multi-model live inference worker loop started.")

        while self._is_running:
            try:
                # Check for available audio windows in the shared buffer
                n_available = self.buffer.available_windows(self.window_samples, self.hop_samples)

                if n_available == 0:
                    time.sleep(0.01)
                    continue

                # Stale-window rejection: If backlog > 3 windows, drop oldest to maintain live freshness
                if n_available > 3:
                    skip_count = n_available - 1
                    for _ in range(skip_count):
                        _ = self.buffer.read_window(self.window_samples, self.hop_samples)
                        self.dropped_windows_total += 1
                    logger.warning("Backpressure detected: dropped %d stale windows.", skip_count)

                # Read next fresh window
                waveform = self.buffer.read_window(self.window_samples, self.hop_samples)
                if waveform is None:
                    time.sleep(0.01)
                    continue

                now_ts = time.time()
                self.window_counter += 1

                # Execute multi-model inference
                result: SynchronizedWindowResult = self.engine.process_window(
                    waveform=waveform,
                    window_index=self.window_counter,
                    timestamp=now_ts,
                    dropped_windows_total=self.dropped_windows_total,
                )

                # Store in recent history
                with self._history_lock:
                    self._window_history.append(result)

                # Track events for UI Event History
                self._update_event_state(result)

                # Persist to SQLite session database if an experimental session is active
                if self.active_session_id:
                    self.session_store.log_window_predictions(
                        session_id=self.active_session_id,
                        window_index=result.window_index,
                        timestamp=result.timestamp,
                        model_predictions={k: v.to_dict() for k, v in result.all_predictions.items()},
                    )

                # Broadcast window result to WebSocket subscribers
                self._broadcast({
                    "type": "multimodel_window_result",
                    "data": result.to_dict(),
                })

            except Exception as e:
                logger.error("Error in multi-model inference worker: %s", e, exc_info=True)
                time.sleep(0.05)

        logger.info("Multi-model live inference worker loop terminated.")

    def _update_event_state(self, result: SynchronizedWindowResult) -> None:
        """Update detection event lifecycle for the Live Event History table."""
        # Use Primary Model (D_v4 + Family A) as the reference candidate event trigger
        is_alarm = result.primary_prediction.is_scream
        score = result.primary_prediction.score

        if is_alarm:
            if self._active_event is None:
                # Start new candidate event
                self._active_event = {
                    "event_id": f"evt_{uuid_hex(8)}",
                    "session_id": self.active_session_id or "untracked",
                    "start_time": result.iso_timestamp,
                    "end_time": None,
                    "window_start_idx": result.window_index,
                    "window_end_idx": result.window_index,
                    "peak_score": score,
                    "primary_prediction": result.primary_prediction.classification,
                    "models_in_agreement": [k for k, p in result.all_predictions.items() if p.is_scream],
                    "verification_status": "UNVERIFIED",
                    "duration_seconds": 0.4875,
                }
            else:
                # Update existing active event
                self._active_event["window_end_idx"] = result.window_index
                if score > self._active_event["peak_score"]:
                    self._active_event["peak_score"] = score
                self._active_event["duration_seconds"] = round(
                    (result.window_index - self._active_event["window_start_idx"] + 1) * 0.4875, 2
                )
        else:
            if self._active_event is not None:
                # Event resolved
                self._close_active_event_if_open(end_iso=result.iso_timestamp)

    def _close_active_event_if_open(self, end_iso: Optional[str] = None) -> None:
        """Close active event and move to event history."""
        if self._active_event:
            self._active_event["end_time"] = end_iso or datetime.now().isoformat()
            self._event_history.insert(0, dict(self._active_event))
            if len(self._event_history) > 100:
                self._event_history.pop()
            self._broadcast({"type": "multimodel_event_resolved", "event": self._active_event})
            self._active_event = None

    def get_window_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Return most recent synchronized window predictions."""
        with self._history_lock:
            items = list(self._window_history)[-limit:]
            return [it.to_dict() for it in items]

    def get_event_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Return candidate events for operator review."""
        return self._event_history[:limit]


def uuid_hex(length: int = 8) -> str:
    """Generate short random hex identifier."""
    import uuid
    return uuid.uuid4().hex[:length]
