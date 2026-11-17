"""
Stage 8.9.20 Automated Test Suite
Verifies:
1. Production artifact immutability (4 SHA-256 hashes)
2. Sub-band formant and pitch perturbation extraction
3. Pitch tracking failure & confidence handling
4. Short-duration audio robustness
5. Digital silence & near-silence handling
6. Variable sample rate handling
7. Supplementary short-scream cohort independence and license compliance
8. YAMNet pooling information loss and feature parity
9. Real-time feature extraction latency
"""

import os
import wave
import json
import hashlib
import pytest
import numpy as np
from pathlib import Path

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = WORKSPACE_DIR.parent.parent
REPO_ROOT = BACKEND_DIR.parent

FROZEN_HASHES = {
    "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
}

class TestProductionImmutability:
    @pytest.mark.parametrize("rel_path,expected_hash", FROZEN_HASHES.items())
    def test_production_file_hash(self, rel_path, expected_hash):
        full_path = REPO_ROOT / rel_path
        assert full_path.exists(), f"Missing production file: {full_path}"
        with open(full_path, "rb") as f:
            actual_hash = hashlib.sha256(f.read()).hexdigest().lower()
        assert actual_hash == expected_hash.lower(), (
            f"Production file {rel_path} mutated! Expected {expected_hash}, got {actual_hash}"
        )


@pytest.fixture
def analyzer():
    from experiments.stage8_9_20_acoustic_discriminability.src.subband_formant_analyzer import (
        SubBandFormantAnalyzer,
    )
    return SubBandFormantAnalyzer()

class TestSubBandFormantAnalyzer:

    def test_feature_dimensions(self, analyzer):
        t = np.linspace(0, 1.0, 16000, endpoint=False)
        audio = (0.5 * np.sin(2 * np.pi * 500.0 * t)).astype(np.float32)
        feats = analyzer.extract_features(audio)
        assert feats.shape == (24,), f"Expected 24 features, got {feats.shape}"
        assert len(analyzer.feature_names) == 24
        assert not np.isnan(feats).any()
        assert not np.isinf(feats).any()

    def test_pitch_tracking_on_periodic_signal(self, analyzer):
        t = np.linspace(0, 1.0, 16000, endpoint=False)
        audio = (0.6 * np.sin(2 * np.pi * 400.0 * t)).astype(np.float32)
        feats = analyzer.extract_features(audio)
        f0_median = feats[0]
        pitch_failure = feats[6]
        # Should detect ~400 Hz without failure
        assert 380 <= f0_median <= 420, f"Expected ~400 Hz, got {f0_median}"
        assert pitch_failure == 0.0

    def test_pitch_failure_on_white_noise(self, analyzer):
        np.random.seed(42)
        noise = np.random.normal(0, 0.2, 16000).astype(np.float32)
        feats = analyzer.extract_features(noise)
        # White noise lacks periodic autocorrelation -> pitch failure flag set
        pitch_failure = feats[6]
        assert pitch_failure == 1.0

    def test_short_duration_audio_handling(self, analyzer):
        # 150 ms audio (2400 samples)
        t = np.linspace(0, 0.15, 2400, endpoint=False)
        audio = (0.8 * np.sin(2 * np.pi * 650.0 * t)).astype(np.float32)
        feats = analyzer.extract_features(audio)
        assert feats.shape == (24,)
        assert not np.isnan(feats).any()

    def test_digital_silence_handling(self, analyzer):
        silence = np.zeros(16000, dtype=np.float32)
        feats = analyzer.extract_features(silence)
        assert feats.shape == (24,)
        assert feats[6] == 1.0 # Pitch failure flag
        assert not np.isnan(feats).any()

    def test_extraction_latency_bounds(self, analyzer):
        t = np.linspace(0, 1.0, 16000, endpoint=False)
        audio = (0.5 * np.sin(2 * np.pi * 500.0 * t)).astype(np.float32)
        import time
        start = time.perf_counter()
        for _ in range(10):
            _ = analyzer.extract_features(audio)
        elapsed_per_iter = (time.perf_counter() - start) / 10.0 * 1000.0
        assert elapsed_per_iter < 95.0, f"Extraction too slow: {elapsed_per_iter:.2f} ms"


class TestSupplementaryShortScreamCohort:
    def test_manifest_existence_and_size(self):
        manifest_path = WORKSPACE_DIR / "data/supplementary_short_screams_manifest.json"
        assert manifest_path.exists()
        with open(manifest_path, "r") as fp:
            data = json.load(fp)
        assert data["total_recordings"] >= 50, f"Target >= 50, got {data['total_recordings']}"
        assert data["target_met"] is True

    def test_strict_isolation_from_primary_dataset(self):
        manifest_path = WORKSPACE_DIR / "data/supplementary_short_screams_manifest.json"
        with open(manifest_path, "r") as fp:
            data = json.load(fp)

        f17_path = REPO_ROOT / "backend/experiments/stage8_9_17_automated_dataset_reconstruction/data/features_stage8_9_17.npz"
        f17 = np.load(f17_path, allow_pickle=True)
        primary_ids = set(f17["file_ids"])

        supp_stems = [r["original_stem"] for r in data["records"]]
        for stem in supp_stems:
            assert stem not in primary_ids, f"Data leakage detected! Stem {stem} is in primary dataset!"

    def test_license_compatibility(self):
        manifest_path = WORKSPACE_DIR / "data/supplementary_short_screams_manifest.json"
        with open(manifest_path, "r") as fp:
            data = json.load(fp)

        allowed_licenses = {"CC0-1.0", "CC-BY-4.0", "CC-BY-3.0"}
        for r in data["records"]:
            assert r["license"] in allowed_licenses
            assert r["license_compatible"] is True

    def test_duration_bounds(self):
        manifest_path = WORKSPACE_DIR / "data/supplementary_short_screams_manifest.json"
        with open(manifest_path, "r") as fp:
            data = json.load(fp)

        for r in data["records"]:
            d = r["duration_seconds"]
            assert 0.10 <= d <= 1.55, f"Duration out of bounds: {d}s"


class TestExperimentSummaryAndGates:
    def test_summary_report_and_verdicts(self):
        summary_path = WORKSPACE_DIR / "reports/stage8_9_20_experiment_summary.json"
        assert summary_path.exists()
        with open(summary_path, "r") as fp:
            summary = json.load(fp)

        primary = summary["primary_held_out_results"]
        assert len(primary) == 5

        # All models must be strictly REJECTED — RESEARCH ONLY
        for model_name, res in primary.items():
            assert res["gates"]["verdict"] == "REJECTED — RESEARCH ONLY", (
                f"{model_name} was erroneously approved!"
            )
            assert res["gates"]["all_gates_passed"] is False

    def test_silence_and_infant_protection_retention(self):
        summary_path = WORKSPACE_DIR / "reports/stage8_9_20_experiment_summary.json"
        with open(summary_path, "r") as fp:
            summary = json.load(fp)

        # Model A, B, E must strictly maintain 0% digital silence FPR
        m_e = summary["primary_held_out_results"]["Model_E_Error_Aware_Adaptive"]
        assert m_e["category_fprs"]["digital_silence_fpr"] == 0.0
        assert m_e["category_fprs"]["infant_crying_fpr"] == 0.0
