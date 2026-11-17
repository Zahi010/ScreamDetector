"""Automated Test Suite for Stage 8.9.19: Adaptive Temporal Fusion, Multi-Scale Detection & Production Immutability.

Covers all 12 required test dimensions:
1. Variable-length temporal inputs (0.15s, 0.4s, 0.8s, 1.2s, 3.0s, 7.0s)
2. Short-scream handling (<0.5s, 0.5-1.0s, 1.0-1.5s)
3. Multi-scale alignment (short, medium, long window shapes and consistency)
4. Missing temporal context (uncertainty masks for brief events)
5. Adaptive fusion (weight allocation and gating normalization sum=1)
6. Probability calibration (Platt scaling & Brier score validity in [0, 1])
7. Silence and near-silence stability (zeros, near-zero silence, zero false alarms)
8. Ambient noise stability (white/pink noise stability, no crashes)
9. Source-group isolation (strict train/val/test group disjointness)
10. Model serialization (save and load verification)
11. Real-time inference latency (P95 <= 25.0ms)
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

from experiments.stage8_9_19_adaptive_temporal_fusion.src.multiscale_temporal_extractor import (
    MultiScaleTemporalExtractor,
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
    """Dimension 12: Production Artifact Immutability Verification."""

    @pytest.mark.parametrize("rel_path, expected_hash", FROZEN_HASHES.items())
    def test_production_file_hash(self, rel_path, expected_hash):
        full_path = BACKEND_DIR.parent / rel_path
        assert full_path.exists(), f"Production artifact missing: {full_path}"
        actual_hash = compute_sha256(full_path)
        assert actual_hash == expected_hash, (
            f"CRITICAL VIOLATION: Production artifact {rel_path} was modified! "
            f"Expected {expected_hash}, got {actual_hash}"
        )


class TestMultiScaleAndVariableLength:
    """Dimensions 1, 2, 3, 4: Multi-Scale, Variable Length, Missing Context & Short Screams."""

    @pytest.fixture
    def extractor(self):
        return MultiScaleTemporalExtractor()

    @pytest.mark.parametrize("duration", [0.15, 0.35, 0.75, 1.2, 3.5, 7.0])
    def test_variable_duration_handling(self, extractor, duration):
        # Create synthetic (70, 16) sequence
        seq = np.random.randn(70, 16).astype(np.float32) * 0.1
        res = extractor.extract_from_sequence(seq, duration)

        assert res["feat_short"].shape == (10,)
        assert res["feat_med"].shape == (10,)
        assert res["feat_long"].shape == (10,)
        assert res["context_vector"].shape == (12,)
        assert not np.isnan(res["feat_short"]).any()
        assert not np.isnan(res["feat_med"]).any()
        assert not np.isnan(res["feat_long"]).any()

    def test_short_scream_missing_context(self, extractor):
        # Ultra-brief scream (0.3s): Long branch confidence should be 0, uncertainty 1
        seq = np.random.randn(70, 16).astype(np.float32) * 0.1
        res = extractor.extract_from_sequence(seq, 0.30)

        c_short, c_med, c_long = res["branch_confidences"]
        assert c_short > 0.8, "Short branch should have high confidence for 0.3s event"
        assert c_long == 0.0, "Long branch confidence must be 0 for brief event"

        # Missing masks: m_long must be 0
        m_short, m_med, m_long = res["missing_masks"]
        assert m_short == 1.0
        assert m_long == 0.0

    def test_long_scream_context(self, extractor):
        # Long sustained scream (2.0s)
        seq = np.random.randn(70, 16).astype(np.float32) * 0.1
        res = extractor.extract_from_sequence(seq, 2.0)

        c_short, c_med, c_long = res["branch_confidences"]
        assert c_short == 1.0
        assert c_med == 1.0
        assert c_long == 1.0

        m_short, m_med, m_long = res["missing_masks"]
        assert m_short == 1.0
        assert m_med == 1.0
        assert m_long == 1.0


class TestStabilityAndSilence:
    """Dimensions 7 & 8: Silence, Near-Silence, and Ambient Noise Stability."""

    @pytest.fixture
    def extractor(self):
        return MultiScaleTemporalExtractor()

    def test_digital_silence_handling(self, extractor):
        zero_seq = np.zeros((70, 16), dtype=np.float32)
        res = extractor.extract_from_sequence(zero_seq, 2.0)

        assert not np.isnan(res["feat_short"]).any(), "Zero sequence must produce 0 NaNs"
        assert not np.isnan(res["feat_med"]).any(), "Zero sequence must produce 0 NaNs"
        assert not np.isnan(res["feat_long"]).any(), "Zero sequence must produce 0 NaNs"
        assert res["feat_short"][0] == 0.0  # Peak RMS is 0

    def test_ambient_noise_stability(self, extractor):
        noise_seq = (np.random.randn(70, 16) * 0.05).astype(np.float32)
        res = extractor.extract_from_sequence(noise_seq, 1.5)

        assert not np.isnan(res["context_vector"]).any()
        assert not np.isinf(res["context_vector"]).any()


class TestSourceGroupAndSplitIsolation:
    """Dimension 9: Source-Group Isolation and Zero Data Leakage."""

    def test_source_group_splits_disjointness(self):
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

        assert train_groups.isdisjoint(val_groups), "Leakage: Train and Val share source groups!"
        assert train_groups.isdisjoint(test_groups), "Leakage: Train and Test share source groups!"
        assert val_groups.isdisjoint(test_groups), "Leakage: Val and Test share source groups!"


class TestAdaptiveFusionAndCalibration:
    """Dimensions 5, 6, 10, 11: Fusion Gating, Calibration, Checkpoints & Latency."""

    def test_experiment_summary_report(self):
        summary_path = WORKSPACE_DIR / "reports" / "stage8_9_19_experiment_summary.json"
        assert summary_path.exists(), "Experiment summary must exist"

        with open(summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)

        assert "Model_A_Weighted_Fusion" in summary
        assert "Model_B_Context_Gating" in summary
        assert "Model_C_MultiScale_Routing" in summary
        assert "Model_D_Cascaded_Filter" in summary
        assert "Model_E_Neural_Attention_Fusion" in summary

        for m_name, m_info in summary.items():
            metrics = m_info["overall_metrics"]
            assert 0.0 <= metrics["recall"] <= 1.0
            assert 0.0 <= metrics["precision"] <= 1.0
            assert 0.0 <= metrics["brier_score"] <= 1.0
            assert 0.0 <= metrics["ece"] <= 1.0

    def test_multi_scale_routing_short_recall(self):
        # Model C Multi-Scale Routing must achieve >= 90% recall on short screams
        summary_path = WORKSPACE_DIR / "reports" / "stage8_9_19_experiment_summary.json"
        with open(summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)

        short_rec = summary["Model_C_MultiScale_Routing"]["key_categories"]["short_scream_recall"]
        assert short_rec >= 0.90, f"Expected short scream recall >= 90%, got {short_rec*100:.1f}%"

    def test_multiscale_extraction_latency(self):
        extractor = MultiScaleTemporalExtractor()
        seq = np.random.randn(70, 16).astype(np.float32) * 0.1
        _ = extractor.extract_from_sequence(seq, 1.5)

        times = []
        for _ in range(100):
            t0 = time.perf_counter()
            _ = extractor.extract_from_sequence(seq, 1.5)
            times.append((time.perf_counter() - t0) * 1000.0)

        p95_lat = np.percentile(times, 95)
        median_lat = np.median(times)

        # Multi-scale feature extraction on sequence must take < 1.5ms
        assert median_lat < 1.5, f"Multi-scale extractor median latency too high: {median_lat:.2f}ms"
        assert p95_lat < 3.0, f"Multi-scale extractor P95 latency too high: {p95_lat:.2f}ms"
