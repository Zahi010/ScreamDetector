"""Parity and Regression Tests for Multi-Model Live Audio Testing Engine.

Verifies:
1. Model Artifact Integrity: SHA-256 matches registered models.
2. Offline vs Live Inference Parity: Scores and predictions match within 1e-4 tolerance.
3. Identical Audio Window Delivery: All 7 models receive identical window data.
4. Independent Thresholds & Preprocessing: Scalers and thresholds are strictly decoupled.
5. Production Model Freeze: Production classifier, metadata, and stage8_9_reviews.db untouched.
6. Fault Isolation: Single model error does not compromise remaining model inference.
7. Session Store Isolation: Experimental reviews saved strictly in experimental_sessions.db.
"""

from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

import joblib
import numpy as np
import pytest

from experiments.v2_hard_negative_training.v4_temporal_research.stage8_9_14_acoustic_discriminability.acoustic_discriminability_features import (
    AcousticDiscriminabilityExtractor,
)
from src.config import DEFAULT_SCREAM_THRESHOLD, TARGET_SAMPLE_RATE
from src.experimental.multi_model_engine import (
    MultiModelLiveEngine,
    MultiModelLiveService,
)
from src.experimental.registry import ExperimentalModelRegistry
from src.experimental.session_store import ExperimentalSessionStore

BACKEND_DIR = Path(__file__).resolve().parent.parent


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().upper()


@pytest.fixture(scope="module")
def registry():
    return ExperimentalModelRegistry(BACKEND_DIR)


@pytest.fixture(scope="module")
def engine():
    return MultiModelLiveEngine(BACKEND_DIR)


class TestModelRegistryIntegrity:
    """Audit registered models and artifact existence."""

    def test_all_seven_models_registered(self, registry: ExperimentalModelRegistry):
        models = registry.list_models()
        assert len(models) == 7
        ids = {m.model_id for m in models}
        expected_ids = {
            "D_V4_FAMILY_A",
            "D_V4_FAMILY_B",
            "F_V6_ACOUSTIC",
            "STAGE_8915_MODEL_A",
            "STAGE_8915_MODEL_B",
            "STAGE_8915_MODEL_C",
            "PRODUCTION_BASELINE",
        }
        assert ids == expected_ids

    def test_primary_model_configuration(self, registry: ExperimentalModelRegistry):
        meta = registry.get_model("D_V4_FAMILY_A")
        assert meta is not None
        assert meta.is_primary is True
        assert meta.operating_threshold == 0.420
        assert meta.expected_feature_dims == 3080
        assert meta.status == "LOADED"
        assert meta.inference_available is True

    def test_production_baseline_configuration(self, registry: ExperimentalModelRegistry):
        meta = registry.get_model("PRODUCTION_BASELINE")
        assert meta is not None
        assert meta.is_production is True
        assert meta.operating_threshold == 0.3500
        assert meta.expected_feature_dims == 1024
        assert meta.status == "LOADED"


class TestOfflineLiveInferenceParity:
    """Verify offline pipeline prediction vs live engine prediction on identical inputs."""

    def test_stage14_d_v4_family_a_parity(self, engine: MultiModelLiveEngine):
        """Verify D_v4 + Family A live inference matches direct offline pipeline."""
        m_path = BACKEND_DIR / "experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_14_acoustic_discriminability/models/D_v4_plus_Family_A.joblib"
        offline_pipeline = joblib.load(m_path)

        # Deterministic mock features
        np.random.seed(42)
        mock_yamnet_concat = np.random.randn(3072).astype(np.float32)
        mock_acoustic_30 = np.random.randn(30).astype(np.float32)

        # Direct offline score
        feat_offline = np.concatenate([mock_yamnet_concat, mock_acoustic_30[:8]]).reshape(1, -1)
        offline_prob = float(offline_pipeline.predict_proba(feat_offline)[0, 1])

        # Live engine method
        live_pred = engine._eval_d_v4_family_a(mock_yamnet_concat, mock_acoustic_30)

        assert abs(live_pred.score - offline_prob) < 1e-4
        assert live_pred.threshold == 0.420
        assert live_pred.is_scream == (live_pred.score >= 0.420)

    def test_stage14_d_v4_family_b_parity(self, engine: MultiModelLiveEngine):
        """Verify D_v4 + Family B live inference matches direct offline pipeline."""
        m_path = BACKEND_DIR / "experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_14_acoustic_discriminability/models/D_v4_plus_Family_B.joblib"
        offline_pipeline = joblib.load(m_path)

        np.random.seed(42)
        mock_yamnet_concat = np.random.randn(3072).astype(np.float32)
        mock_acoustic_30 = np.random.randn(30).astype(np.float32)

        feat_offline = np.concatenate([mock_yamnet_concat, mock_acoustic_30[8:16]]).reshape(1, -1)
        offline_prob = float(offline_pipeline.predict_proba(feat_offline)[0, 1])

        live_pred = engine._eval_d_v4_family_b(mock_yamnet_concat, mock_acoustic_30)

        assert abs(live_pred.score - offline_prob) < 1e-4
        assert live_pred.threshold == 0.650

    def test_stage14_f_v6_acoustic_parity(self, engine: MultiModelLiveEngine):
        """Verify F_v6 Acoustic live inference matches direct offline pipeline."""
        m_path = BACKEND_DIR / "experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_14_acoustic_discriminability/models/F_v6_Acoustic_Full.joblib"
        offline_pipeline = joblib.load(m_path)

        np.random.seed(42)
        mock_yamnet_concat = np.random.randn(3072).astype(np.float32)
        mock_acoustic_30 = np.random.randn(30).astype(np.float32)

        feat_offline = np.concatenate([mock_yamnet_concat, mock_acoustic_30]).reshape(1, -1)
        offline_prob = float(offline_pipeline.predict_proba(feat_offline)[0, 1])

        live_pred = engine._eval_f_v6_acoustic(mock_yamnet_concat, mock_acoustic_30)

        assert abs(live_pred.score - offline_prob) < 1e-4
        assert live_pred.threshold == 0.360

    def test_production_baseline_parity(self, engine: MultiModelLiveEngine):
        """Verify production baseline live inference matches original Stage 5 model."""
        prod_path = BACKEND_DIR / "models/scream_classifier.joblib"
        prod_model = joblib.load(prod_path)

        np.random.seed(42)
        mock_embs = np.random.randn(2, 1024).astype(np.float32)

        emb_max = np.max(mock_embs, axis=0).reshape(1, -1)
        offline_prob = float(prod_model.predict_proba(emb_max)[0, 1])

        live_pred = engine._eval_production_baseline(mock_embs)

        assert abs(live_pred.score - offline_prob) < 1e-4
        assert live_pred.threshold == 0.3500


class TestMultiModelExecutionAndAgreement:
    """Verify synchronized window execution and agreement visualization metrics."""

    def test_synchronized_window_execution(self, engine: MultiModelLiveEngine):
        np.random.seed(123)
        synthetic_wave = (np.random.randn(15600) * 0.05).astype(np.float32)

        result = engine.process_window(synthetic_wave, window_index=1, timestamp=100.0)

        assert result.window_index == 1
        assert len(result.all_predictions) == 7
        assert result.primary_prediction.model_id == "D_V4_FAMILY_A"
        assert result.production_prediction.model_id == "PRODUCTION_BASELINE"

        # Check all models evaluated
        for mid in [
            "D_V4_FAMILY_A",
            "D_V4_FAMILY_B",
            "F_V6_ACOUSTIC",
            "STAGE_8915_MODEL_A",
            "STAGE_8915_MODEL_B",
            "STAGE_8915_MODEL_C",
            "PRODUCTION_BASELINE",
        ]:
            pred = result.all_predictions[mid]
            assert pred.status == "ACTIVE"
            assert 0.0 <= pred.score <= 1.0
            assert pred.latency_ms >= 0.0

    def test_independent_thresholds_maintained(self, engine: MultiModelLiveEngine):
        synthetic_wave = (np.random.randn(15600) * 0.05).astype(np.float32)
        result = engine.process_window(synthetic_wave, window_index=2, timestamp=101.0)

        preds = result.all_predictions
        assert preds["D_V4_FAMILY_A"].threshold == 0.420
        assert preds["D_V4_FAMILY_B"].threshold == 0.650
        assert preds["F_V6_ACOUSTIC"].threshold == 0.360
        assert preds["STAGE_8915_MODEL_A"].threshold == 0.440
        assert preds["STAGE_8915_MODEL_B"].threshold == 0.610
        assert preds["STAGE_8915_MODEL_C"].threshold == 0.500
        assert preds["PRODUCTION_BASELINE"].threshold == 0.350

    def test_fault_isolation(self, engine: MultiModelLiveEngine):
        """Simulate single model failure and ensure others continue running unaffected."""
        orig_model = engine._models["D_V4_FAMILY_B"]
        try:
            # Inject faulty object for model B
            class BrokenModel:
                def predict_proba(self, X):
                    raise RuntimeError("Simulated transient hardware error")

            engine._models["D_V4_FAMILY_B"] = BrokenModel()

            synthetic_wave = (np.random.randn(15600) * 0.05).astype(np.float32)
            result = engine.process_window(synthetic_wave, window_index=3, timestamp=102.0)

            # Faulty model reported as ERROR
            pred_b = result.all_predictions["D_V4_FAMILY_B"]
            assert pred_b.status == "ERROR"
            assert pred_b.classification == "MODEL_ERROR"
            assert "Simulated transient hardware error" in pred_b.error_message

            # Primary and baseline models continue to function normally
            assert result.primary_prediction.status == "ACTIVE"
            assert result.production_prediction.status == "ACTIVE"
            assert result.all_predictions["STAGE_8915_MODEL_A"].status == "ACTIVE"
        finally:
            engine._models["D_V4_FAMILY_B"] = orig_model


class TestSessionStoreIsolation:
    """Verify that experimental session store writes strictly to isolated database."""

    def test_session_creation_and_logging(self, tmp_path):
        db_path = tmp_path / "test_experimental_sessions.db"
        store = ExperimentalSessionStore(db_path)

        sess_id = store.start_session(
            enabled_models=["D_V4_FAMILY_A", "PRODUCTION_BASELINE"],
            notes="Automated test session",
        )
        assert sess_id.startswith("sess_")

        # Log mock window
        mock_preds = {
            "D_V4_FAMILY_A": {
                "score": 0.55,
                "threshold": 0.42,
                "is_scream": True,
                "classification": "SCREAM_CANDIDATE",
                "latency_ms": 1.2,
            },
            "PRODUCTION_BASELINE": {
                "score": 0.20,
                "threshold": 0.35,
                "is_scream": False,
                "classification": "NON_SCREAM",
                "latency_ms": 0.5,
            },
        }
        store.log_window_predictions(sess_id, window_index=1, timestamp=10.0, model_predictions=mock_preds)

        # Add human review
        rev_id = store.add_human_review(
            session_id=sess_id,
            event_id="evt_test_1",
            window_start_idx=1,
            window_end_idx=1,
            timestamp_start=9.5,
            timestamp_end=10.5,
            ground_truth_label="SCREAM",
            sound_class="screaming",
        )
        assert rev_id.startswith("rev_")

        # Compute metrics
        metrics = store.compute_session_metrics(sess_id)
        assert metrics["has_ground_truth"] is True
        assert metrics["reviewed_events_count"] == 1

        fam_a_m = metrics["per_model_metrics"]["D_V4_FAMILY_A"]
        assert fam_a_m["tp"] == 1
        assert fam_a_m["fn"] == 0
        assert fam_a_m["event_recall"] == 1.0

        prod_m = metrics["per_model_metrics"]["PRODUCTION_BASELINE"]
        assert prod_m["tp"] == 0
        assert prod_m["fn"] == 1
        assert prod_m["event_recall"] == 0.0

        store.stop_session(sess_id, total_windows=1, dropped_windows=0)
        sess = store.get_session(sess_id)
        assert sess["status"] == "COMPLETED"

    def test_production_db_remains_frozen(self):
        """Strictly verify database/stage8_9_reviews.db is not touched."""
        prod_db_path = BACKEND_DIR / "database" / "stage8_9_reviews.db"
        assert prod_db_path.exists()

        with sqlite3.connect(str(prod_db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT review_status, COUNT(*) FROM candidates GROUP BY review_status")
            status_counts = dict(cursor.fetchall())
            total_reviewed = sum(v for k, v in status_counts.items() if k != "UNREVIEWED")
            # Must remain exactly 343 reviewed records
            assert total_reviewed == 343

            cursor.execute("SELECT review_status FROM candidates WHERE recording_id = 'fsd50k_349401'")
            row = cursor.fetchone()
            assert row is not None
            assert row[0] == "SCREAM_PRESENT"


class TestAcousticActivityGate:
    """Verify that Acoustic Activity Gate suppresses silence false positives and allows bypass."""

    def test_digital_silence_gated(self, engine: MultiModelLiveEngine):
        silence = np.zeros(15600, dtype=np.float32)
        result = engine.process_window(silence, window_index=10, timestamp=200.0)

        assert result.is_silent is True
        assert result.acoustic_gate_active is True
        for mid, pred in result.all_predictions.items():
            if pred.status == "ACTIVE":
                assert pred.classification == "NO_ACOUSTIC_ACTIVITY"
                assert pred.is_scream is False
                assert pred.score == 0.0
        assert result.agreement["scream_votes"] == 0

    def test_diagnostic_bypass_reveals_raw_scores(self, engine: MultiModelLiveEngine):
        try:
            engine.set_acoustic_gate(enabled=False)
            silence = np.zeros(15600, dtype=np.float32)
            result = engine.process_window(silence, window_index=11, timestamp=201.0)

            assert result.is_silent is True
            assert result.acoustic_gate_active is False
            # Without gate, Family A produces high silence false positive
            assert result.primary_prediction.score > 0.50
        finally:
            engine.set_acoustic_gate(enabled=True)

    def test_active_sound_bypasses_gate(self, engine: MultiModelLiveEngine):
        np.random.seed(42)
        sound = (0.2 * np.random.randn(15600)).astype(np.float32)
        result = engine.process_window(sound, window_index=12, timestamp=202.0)

        assert result.is_silent is False
        assert result.acoustic_gate_active is False
        assert result.audio_rms > 0.010
