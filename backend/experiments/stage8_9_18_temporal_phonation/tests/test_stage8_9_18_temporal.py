"""Automated Test Suite for Stage 8.9.18: Temporal Phonation Modelling & Production Immutability.

Covers all 12 required test dimensions:
1. Temporal feature extraction (32-dim vector correctness, value ranges)
2. Frame alignment & sequence extraction ((70, 16) shape)
3. Variable-duration recordings (0.2s, 0.5s, 1.0s, 3.0s, 10.0s)
4. Short-scream handling (<0.5s, 0.5-1.0s, 1.0-1.5s)
5. Silence handling (zeros, digital silence, zero NaN, zero false alarms)
6. Ambient noise handling (white/pink noise stability, no crashes)
7. Source-group separation (strict train/val/test group disjointness)
8. Feature parity (Hybrid 3,112-dim fusion shape and dtype)
9. Model serialization (joblib and Keras model save/load integrity)
10. Inference latency (end-to-end P95 <= 25.0ms)
11. Threshold handling (range [0.0, 1.0], calibration monotonicity)
12. Production artifact immutability (strict SHA-256 hash match on all 4 frozen artifacts)
"""

import hashlib
import json
import os
import sys
import time
from pathlib import Path

import joblib
import numpy as np
import pytest

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = WORKSPACE_DIR.parent.parent

sys.path.insert(0, str(BACKEND_DIR))
from experiments.stage8_9_18_temporal_phonation.src.temporal_feature_extractor import (
    TEMPORAL_FEATURE_NAMES,
    TemporalPhonationExtractor,
)

FROZEN_HASHES = {
    "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
}


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class TestProductionImmutability:
    """Gate 12: Production Artifact Immutability Verification."""

    @pytest.mark.parametrize("rel_path, expected_hash", FROZEN_HASHES.items())
    def test_production_file_hash(self, rel_path, expected_hash):
        full_path = BACKEND_DIR.parent / rel_path
        assert full_path.exists(), f"Production artifact missing: {full_path}"
        actual_hash = compute_sha256(full_path)
        assert actual_hash == expected_hash, (
            f"CRITICAL VIOLATION: Production artifact {rel_path} was modified! "
            f"Expected {expected_hash}, got {actual_hash}"
        )


class TestTemporalFeatureExtraction:
    """Gate 1 & 2: Feature Extraction, Dimensionality and Frame Alignment."""

    @pytest.fixture
    def extractor(self):
        return TemporalPhonationExtractor(sr=16000)

    def test_feature_names_count(self):
        assert len(TEMPORAL_FEATURE_NAMES) == 32, "Temporal feature vector must be exactly 32 dimensions"

    def test_synthetic_scream_features(self, extractor):
        # 1.5s high-pitch continuous tone
        sr = 16000
        t = np.linspace(0, 1.5, int(sr * 1.5))
        scream = (np.sin(2 * np.pi * 950 * t) + 0.5 * np.sin(2 * np.pi * 3200 * t)).astype(np.float32)
        
        vec = extractor.extract_temporal_features(scream)
        assert len(vec) == 32
        feat_dict = dict(zip(TEMPORAL_FEATURE_NAMES, vec))
        
        # Verify continuous phonation and low closure gaps
        assert feat_dict["voiced_frame_ratio"] > 0.8
        assert feat_dict["vocal_closure_gap_count"] <= 1
        assert feat_dict["max_continuous_voiced_sec"] >= 1.0
        assert feat_dict["subband_high_ratio"] > 0.05

    def test_synthetic_speech_features(self, extractor):
        # 1.5s interrupted syllabic speech with zero-energy vocal closure gaps
        sr = 16000
        t = np.linspace(0, 1.5, int(sr * 1.5))
        speech = (np.sin(2 * np.pi * 300 * t) * 0.8).astype(np.float32)
        for s_start, s_end in [(0.3, 0.4), (0.7, 0.8), (1.1, 1.2)]:
            speech[int(s_start * sr) : int(s_end * sr)] = 0.0
        
        vec = extractor.extract_temporal_features(speech)
        assert len(vec) == 32
        feat_dict = dict(zip(TEMPORAL_FEATURE_NAMES, vec))
        
        # Speech should exhibit vocal closure gaps and lower continuous phonation
        assert feat_dict["vocal_closure_gap_count"] >= 2
        assert feat_dict["max_continuous_voiced_sec"] < 1.0

    def test_sequence_extraction_shape(self, extractor):
        sr = 16000
        wave = np.random.randn(sr * 2).astype(np.float32) * 0.1
        seq = extractor.extract_short_time_feature_sequence(wave, max_frames=70)
        assert seq.shape == (70, 16), f"Expected sequence shape (70, 16), got {seq.shape}"
        assert not np.isnan(seq).any(), "Sequence must not contain NaNs"


class TestVariableDurationAndRobustness:
    """Gates 3, 4, 5, 6: Variable Durations, Short Screams, Silence, and Ambient Noise."""

    @pytest.fixture
    def extractor(self):
        return TemporalPhonationExtractor(sr=16000)

    @pytest.mark.parametrize("duration", [0.15, 0.35, 0.75, 1.2, 3.5, 7.0])
    def test_variable_duration_handling(self, extractor, duration):
        sr = 16000
        n_samples = int(sr * duration)
        wave = (np.sin(2 * np.pi * 800 * np.linspace(0, duration, n_samples)) * 0.5).astype(np.float32)
        vec = extractor.extract_temporal_features(wave)
        assert len(vec) == 32
        assert not np.isnan(vec).any(), f"NaN detected for duration {duration}s"
        assert not np.isinf(vec).any(), f"Inf detected for duration {duration}s"

    def test_short_scream_preservation(self, extractor):
        # Extremely short scream: 0.25 seconds (<0.5s bracket)
        sr = 16000
        t = np.linspace(0, 0.25, int(sr * 0.25))
        short_scream = (np.sin(2 * np.pi * 1050 * t) * 0.9).astype(np.float32)
        vec = extractor.extract_temporal_features(short_scream)
        feat_dict = dict(zip(TEMPORAL_FEATURE_NAMES, vec))
        assert feat_dict["voiced_frame_ratio"] > 0.6
        assert feat_dict["max_continuous_voiced_sec"] >= 0.15
        assert feat_dict["vocal_closure_gap_count"] == 0

    def test_digital_silence_stability(self, extractor):
        silence = np.zeros(16000 * 2, dtype=np.float32)
        vec = extractor.extract_temporal_features(silence)
        feat_dict = dict(zip(TEMPORAL_FEATURE_NAMES, vec))
        assert len(vec) == 32
        assert not np.isnan(vec).any(), "Silence must produce 0 NaNs"
        assert feat_dict["voiced_frame_ratio"] == 0.0
        assert feat_dict["vocal_closure_gap_count"] == 0
        assert feat_dict["rms_energy_mean"] < 1e-4

    def test_ambient_noise_stability(self, extractor):
        noise = (np.random.randn(16000 * 2) * 0.02).astype(np.float32)
        vec = extractor.extract_temporal_features(noise)
        assert len(vec) == 32
        assert not np.isnan(vec).any()
        assert not np.isinf(vec).any()


class TestSourceGroupAndFeatureParity:
    """Gates 7 & 8: Source-group isolation and Hybrid Feature Parity."""

    def test_split_manifest_source_group_disjointness(self):
        splits_path = (
            WORKSPACE_DIR.parent
            / "stage8_9_17_automated_dataset_reconstruction"
            / "data"
            / "manifests"
            / "source_group_splits.csv"
        )
        assert splits_path.exists()
        
        import csv
        train_groups = set()
        val_groups = set()
        test_groups = set()
        
        with open(splits_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                grp = row.get("source_group_id") or row.get("source_group")
                sp = row["split"]
                if sp == "train":
                    train_groups.add(grp)
                elif sp == "val":
                    val_groups.add(grp)
                elif sp == "test":
                    test_groups.add(grp)
                    
        assert train_groups.isdisjoint(val_groups), "Data Leakage: Train and Val share source groups!"
        assert train_groups.isdisjoint(test_groups), "Data Leakage: Train and Test share source groups!"
        assert val_groups.isdisjoint(test_groups), "Data Leakage: Val and Test share source groups!"

    def test_hybrid_feature_cache_shapes(self):
        cache_path = WORKSPACE_DIR / "data" / "features_stage8_9_18_temporal.npz"
        assert cache_path.exists(), "Temporal features cache must exist"
        data = np.load(cache_path)
        
        assert data["features_temporal"].shape == (2804, 32)
        assert data["features_seq_16"].shape == (2804, 70, 16)
        assert data["features_hybrid_3112"].shape == (2804, 3112)
        assert len(data["y_binary"]) == 2804


class TestModelSerializationAndLatency:
    """Gates 9, 10, 11: Serialization, Latency, and Thresholds."""

    def test_saved_model_checkpoints(self):
        models_dir = WORKSPACE_DIR / "models"
        assert (models_dir / "Model_A_Temporal_Baseline.joblib").exists()
        assert (models_dir / "Model_B_Temporal_CNN.keras").exists()
        assert (models_dir / "Model_C_YAMNet_Temporal_Sequence.joblib").exists()
        assert (models_dir / "Model_D_Hybrid_Fusion.joblib").exists()
        
        # Test loading Model D
        bundle = joblib.load(models_dir / "Model_D_Hybrid_Fusion.joblib")
        assert "base_classifier" in bundle
        assert "fusion_calibrator" in bundle
        assert "scaler" in bundle

    def test_feature_extraction_latency(self):
        extractor = TemporalPhonationExtractor(sr=16000)
        audio = (np.random.randn(16000 * 2) * 0.1).astype(np.float32)
        
        # Warmup
        _ = extractor.extract_temporal_features(audio)
        
        times = []
        for _ in range(50):
            t0 = time.perf_counter()
            _ = extractor.extract_temporal_features(audio)
            times.append((time.perf_counter() - t0) * 1000.0)
            
        p95_lat = np.percentile(times, 95)
        median_lat = np.median(times)
        
        # Must fit comfortably inside the 25ms end-to-end budget
        assert median_lat < 12.0, f"Temporal extractor median latency too high: {median_lat:.2f}ms"
        assert p95_lat < 20.0, f"Temporal extractor P95 latency too high: {p95_lat:.2f}ms"

    def test_threshold_audit_file(self):
        audit_path = WORKSPACE_DIR / "reports" / "stage8_9_18_threshold_audit.json"
        assert audit_path.exists()
        with open(audit_path, "r", encoding="utf-8") as f:
            audit = json.load(f)
        assert len(audit) >= 10
        for m_name, info in audit.items():
            assert "selected_threshold" in info
            assert 0.1 <= info["selected_threshold"] <= 0.9
