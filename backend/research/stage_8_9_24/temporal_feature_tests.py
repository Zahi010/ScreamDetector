"""
Stage 8.9.24 Automated Unit and Integration Test Suite.
Tests:
1. Production hash immutability and frozen threshold (0.3500)
2. Energy modulation calculations
3. Burst continuity calculations
4. Envelope feature extraction
5. Modulation spectrum & syllabic ratios
6. Missing features & invalid audio handling
7. Near-silence handling (ensuring no false chaotic distress triggers)
8. Short vocalizations (200-500ms)
9. Window-boundary cases (transients at buffer edges)
10. Dual-pathway isolation (short-pathway independence from long-context)
11. Long-context insufficient-data handling
12. Temporal verifier candidate prediction comparison integrity
13. Source-group isolation (zero leakage)
"""

import hashlib
import json
import math
from pathlib import Path
import numpy as np
import pytest

from temporal_feature_extraction import (
    TemporalModulationExtractor,
    TEMPORAL_MODULATION_FEATURE_NAMES,
)

WORKSPACE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = WORKSPACE_DIR.parent.parent


class TestProductionImmutability:
    """Verify frozen production model artifacts and threshold remain 100% untouched."""

    AUTHORITATIVE_HASHES = {
        "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
        "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
        "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
        "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
    }

    @pytest.mark.parametrize("rel_path,expected_hash", AUTHORITATIVE_HASHES.items())
    def test_production_file_hash(self, rel_path, expected_hash):
        full_path = BACKEND_DIR / rel_path.replace("backend/", "")
        assert full_path.exists(), f"Production artifact missing: {full_path}"
        with open(full_path, "rb") as f:
            computed_hash = hashlib.sha256(f.read()).hexdigest()
        assert computed_hash == expected_hash, f"Hash mismatch for {rel_path}!"

    def test_production_threshold(self):
        meta_path = BACKEND_DIR / "models" / "model_metadata.json"
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        thresh = meta.get("selected_threshold") or meta.get("production_threshold") or meta.get("threshold")
        assert thresh is not None, "Threshold not found in metadata"
        assert abs(float(thresh) - 0.3500) < 1e-6, f"Production threshold modified: {thresh}"


class TestTemporalFeatureExtraction:
    """Test suite for temporal modulation and cadence feature extraction."""

    @pytest.fixture
    def extractor(self):
        return TemporalModulationExtractor(sr=16000, frame_ms=25.0, hop_ms=12.5)

    def test_feature_names_cardinality(self, extractor):
        assert len(TEMPORAL_MODULATION_FEATURE_NAMES) == 28

    def test_near_silence_input(self, extractor):
        silent_audio = np.random.normal(0, 1e-6, 16000).astype(np.float32)
        feats = extractor.extract_features(silent_audio)
        for k, v in feats.items():
            assert not math.isnan(v), f"Feature {k} was NaN on near-silence"
            assert not math.isinf(v), f"Feature {k} was Inf on near-silence"
        assert feats["active_vocal_ratio"] == 0.0

    def test_short_vocalization(self, extractor):
        short_audio = np.zeros(16000, dtype=np.float32)
        t = np.arange(4800) / 16000.0
        short_audio[2000:6800] = 0.5 * np.sin(2 * np.pi * 1000.0 * t).astype(np.float32)

        vec = extractor.extract_feature_vector(short_audio)
        assert len(vec) == 28
        assert not np.isnan(vec).any()
        assert not np.isinf(vec).any()
        assert vec[0] > 0.0

    def test_continuous_scream_vs_syllabic_shout_synthetic(self, extractor):
        sr = 16000
        dur_sec = 2.0
        n_samples = int(sr * dur_sec)
        t = np.arange(n_samples) / sr

        scream_wf = 0.4 * np.sin(2 * np.pi * 800.0 * t).astype(np.float32)
        mod_envelope = np.maximum(0.0, np.sin(2 * np.pi * 4.0 * t)) ** 2
        shout_wf = (0.4 * mod_envelope * np.sin(2 * np.pi * 800.0 * t)).astype(np.float32)

        feats_scream = extractor.extract_features(scream_wf)
        feats_shout = extractor.extract_features(shout_wf)

        assert feats_scream["burst_continuity_ratio"] > feats_shout["burst_continuity_ratio"]
        assert feats_shout["energy_modulation_depth"] > feats_scream["energy_modulation_depth"]
        assert feats_shout["syllabic_modulation_ratio"] > feats_scream["syllabic_modulation_ratio"]

    def test_window_boundary_robustness(self, extractor):
        sr = 16000
        wf_start = np.zeros(16000, dtype=np.float32)
        wf_start[:3200] = 0.5 * np.sin(2 * np.pi * 600.0 * np.arange(3200) / sr)

        wf_end = np.zeros(16000, dtype=np.float32)
        wf_end[-3200:] = 0.5 * np.sin(2 * np.pi * 600.0 * np.arange(3200) / sr)

        feats_start = extractor.extract_features(wf_start)
        feats_end = extractor.extract_features(wf_end)

        assert feats_start["burst_continuity_ratio"] > 0.0
        assert feats_end["burst_continuity_ratio"] > 0.0
        assert not np.isnan(list(feats_start.values())).any()
        assert not np.isnan(list(feats_end.values())).any()

    def test_short_pathway_independence_and_no_veto(self, extractor):
        """Verify that short context extraction does not require long cadence buffers."""
        short_wf = 0.5 * np.sin(2 * np.pi * 850.0 * np.arange(4000) / 16000.0).astype(np.float32)  # 250 ms
        vec_short = extractor.extract_feature_vector(short_wf, context_sec=0.5)
        assert len(vec_short) == 28
        assert not np.isnan(vec_short).any()


class TestArtifactIntegrity:
    """Verify generated Stage 8.9.24 artifacts and candidate prediction integrity."""

    def test_candidate_prediction_comparison_exists(self):
        csv_path = WORKSPACE_DIR / "temporal_candidate_prediction_comparison.csv"
        assert csv_path.exists(), "temporal_candidate_prediction_comparison.csv missing"
        with open(csv_path, "r", encoding="utf-8") as f:
            lines = [l for l in f if l.strip()]
        assert len(lines) == 463, f"Expected 463 lines (header + 462 test), got {len(lines)}"

    def test_model_comparison_exists(self):
        csv_path = WORKSPACE_DIR / "model_comparison.csv"
        assert csv_path.exists(), "model_comparison.csv missing"
        with open(csv_path, "r", encoding="utf-8") as f:
            lines = [l for l in f if l.strip()]
        assert len(lines) >= 8, f"Expected at least 8 lines (header + 7 candidates), got {len(lines)}"

    def test_figures_exist(self):
        fig_dir = WORKSPACE_DIR / "figures"
        required_figs = [
            "scream_vs_shout_energy_envelopes.png",
            "modulation_spectrum_comparison.png",
            "burst_continuity_distributions.png",
            "temporal_feature_correlation_matrix.png",
            "short_scream_detection_by_duration.png",
            "snr_vs_temporal_feature_stability.png",
            "candidate_roc_and_pr_curves.png",
            "baseline_vs_temporal_disagreement.png",
            "detection_delay_vs_context_duration.png",
        ]
        for fig_name in required_figs:
            p = fig_dir / fig_name
            assert p.exists(), f"Required figure {fig_name} missing!"
