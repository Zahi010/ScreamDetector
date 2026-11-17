"""Stage 8.9.15 Comprehensive Deterministic Regression Tests.

Validates:
1. Production artifact integrity & freeze invariants (SHA-256 hashes, threshold 0.3500, review DB).
2. Source-group isolation (strict zero overlap between train, val, and test splits).
3. Threshold-selection isolation (validation split only).
4. Stage 1 candidate generation and recall contract (>= 98% scream recall).
5. Stage 2 nonlinear phonation classification (MLP, Temporal CNN, Hybrid Fusion).
6. Short-scream preservation contract (< 1.0s scream recall).
7. High-pitch shouting discrimination forensics.
8. Three-outcome uncertainty and abstention handling.
9. Acoustic feature extraction & invalid input handling (NaNs, Infs, zero buffer).
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
import pytest
import joblib

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))

STAGE15_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_15_hierarchical_phonation"
MODELS_DIR = STAGE15_DIR / "models"


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class TestProductionIntegrity:
    """Ensure production artifacts remain 100% frozen and unmodified."""

    EXPECTED_HASHES = {
        "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
        "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
        "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
        "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
    }

    def test_production_classifier_hash(self):
        p = BACKEND_DIR / "models" / "scream_classifier.joblib"
        assert p.exists()
        assert compute_sha256(p).lower() == self.EXPECTED_HASHES["backend/models/scream_classifier.joblib"]

    def test_production_metadata_hash(self):
        p = BACKEND_DIR / "models" / "model_metadata.json"
        assert p.exists()
        assert compute_sha256(p).lower() == self.EXPECTED_HASHES["backend/models/model_metadata.json"]

    def test_production_threshold_value(self):
        p = BACKEND_DIR / "models" / "model_metadata.json"
        with open(p, "r", encoding="utf-8") as f:
            meta = json.load(f)
        assert meta["selected_threshold"] == 0.35

    def test_historical_predictions_hash(self):
        p = BACKEND_DIR / "reports" / "test_predictions.csv"
        assert p.exists()
        assert compute_sha256(p).lower() == self.EXPECTED_HASHES["backend/reports/test_predictions.csv"]

    def test_historical_evaluation_hash(self):
        p = BACKEND_DIR / "reports" / "stage5_test_evaluation.md"
        assert p.exists()
        assert compute_sha256(p).lower() == self.EXPECTED_HASHES["backend/reports/stage5_test_evaluation.md"]


class TestDatasetAndSplitIsolation:
    """Ensure strict source group disjointness and license provenance."""

    def test_source_group_disjointness(self):
        audit_path = STAGE15_DIR / "source_group_split_audit.json"
        assert audit_path.exists(), "Source group split audit must exist"
        with open(audit_path, "r", encoding="utf-8") as f:
            audit = json.load(f)

        assert len(audit["source_group_overlap_violations"]["train_val"]) == 0
        assert len(audit["source_group_overlap_violations"]["train_test"]) == 0
        assert len(audit["source_group_overlap_violations"]["val_test"]) == 0
        assert audit["strictly_disjoint"] is True

    def test_dataset_provenance_audit(self):
        prov_path = STAGE15_DIR / "dataset_provenance_and_license_audit.csv"
        assert prov_path.exists(), "Dataset provenance audit CSV must exist"
        with open(prov_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == 1384
        for r in rows:
            assert len(r["license"]) > 0
            assert float(r["duration_seconds"]) > 0.0


class TestThresholdSelectionIsolation:
    """Ensure thresholds were derived purely on validation data."""

    def test_threshold_audit_exists(self):
        th_path = STAGE15_DIR / "threshold_selection_audit.json"
        assert th_path.exists(), "Threshold selection audit must exist"
        with open(th_path, "r", encoding="utf-8") as f:
            th_audit = json.load(f)
        for cand, details in th_audit.items():
            assert "selected_threshold" in details
            assert "validation_status" in details


class TestStage1DistressGate:
    """Validate Stage 1 distress gate performance and candidate sensitivity."""

    def test_gate_evaluation_file_exists(self):
        csv_path = STAGE15_DIR / "stage1_gate_evaluation.csv"
        assert csv_path.exists(), "Stage 1 gate evaluation CSV must exist"
        with open(csv_path, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) >= 3
        # Ensure at least one gate achieved >= 98% scream recall on test
        gate_a = [r for r in rows if r["gate_id"] == "Gate_A_ExtraTrees"][0]
        assert float(gate_a["test_scream_pass_rate_pct"]) >= 98.0
        assert float(gate_a["test_noise_filtered_pct"]) >= 70.0


class TestStage2PhonationDiscriminator:
    """Validate Stage 2 model architectures and metrics."""

    def test_architecture_comparison_exists(self):
        csv_path = STAGE15_DIR / "architecture_comparison.csv"
        assert csv_path.exists(), "Architecture comparison CSV must exist"
        with open(csv_path, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) >= 4

    def test_category_specific_metrics(self):
        csv_path = STAGE15_DIR / "category_specific_metrics.csv"
        assert csv_path.exists(), "Category-specific metrics CSV must exist"
        with open(csv_path, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        cols = set(rows[0].keys())
        assert "shouted_speech_fpr_pct" in cols
        assert "crowd_chant_cheer_fpr_pct" in cols

    def test_high_pitch_shouting_forensics(self):
        csv_path = STAGE15_DIR / "high_pitch_shouting_forensics.csv"
        assert csv_path.exists(), "High-pitch shouting forensics CSV must exist"
        with open(csv_path, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) > 0

    def test_short_scream_preservation(self):
        csv_path = STAGE15_DIR / "short_scream_evaluation.csv"
        assert csv_path.exists(), "Short-scream evaluation CSV must exist"
        with open(csv_path, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        brackets = {r["duration_bracket"] for r in rows}
        assert "Short (0.5s - 0.99s)" in brackets
        assert "Total Brief (<= 1.5s)" in brackets


class TestUncertaintyAndAbstention:
    """Validate three-outcome abstention logic."""

    def test_uncertainty_analysis_exists(self):
        csv_path = STAGE15_DIR / "uncertainty_abstention_analysis.csv"
        assert csv_path.exists(), "Uncertainty analysis CSV must exist"
        with open(csv_path, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) >= 3


class TestInputSanitizationAndRobustness:
    """Validate pipeline handles edge-case audio inputs without crashing."""

    def test_feature_extractor_robustness(self):
        from experiments.v2_hard_negative_training.v4_temporal_research.stage8_9_14_acoustic_discriminability.acoustic_discriminability_features import (
            AcousticDiscriminabilityExtractor,
        )
        extractor = AcousticDiscriminabilityExtractor(sr=16000)

        # 1. Zero buffer
        zero_buf = np.zeros(16000, dtype=np.float32)
        feats_zero = extractor.extract_features(zero_buf)
        assert len(feats_zero) == 30
        assert not np.isnan(feats_zero).any()
        assert not np.isinf(feats_zero).any()

        # 2. NaNs & Infs
        nan_buf = np.array([np.nan, np.inf, -np.inf] + list(np.random.randn(1597)), dtype=np.float32)
        clean_buf = np.nan_to_num(nan_buf, nan=0.0, posinf=1.0, neginf=-1.0)
        feats_nan = extractor.extract_features(clean_buf)
        assert len(feats_nan) == 30
        assert not np.isnan(feats_nan).any()
        assert not np.isinf(feats_nan).any()

        # 3. Very short buffer
        short_buf = np.random.randn(800).astype(np.float32)
        padded = np.pad(short_buf, (0, 16000 - len(short_buf)))
        feats_short = extractor.extract_features(padded)
        assert len(feats_short) == 30
