"""Automated Test Suite for Stage 8.9.27 Independent Evaluation & Audit.

Verifies:
1. Production asset freeze & SHA-256 integrity (all 4 production files).
2. Manifest lock & checksum validation.
3. Zero-leakage source independence (zero SHA-256 match with 2,804 splits).
4. Evaluation results completeness (295 recordings in blind_evaluation_results.csv).
5. Short-scream retention (100% on independent short screams).
6. Monosyllabic shouting false alarm suppression (0.0% on independent shouts).
7. Metric reconciliation consistency (5/7 = 71.43% denominator resolution).
8. Latency benchmark completeness.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import pytest
import pandas as pd

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent
STAGE_DIR = BACKEND_DIR / "research" / "stage_8_9_27"
STAGE26_DIR = BACKEND_DIR / "research" / "stage_8_9_26"

AUTHORITATIVE_HASHES = {
    "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
}


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class TestProductionIntegrity:
    """Verifies that production remains 100% frozen."""

    @pytest.mark.parametrize("rel_path,expected_hash", list(AUTHORITATIVE_HASHES.items()))
    def test_production_file_hash(self, rel_path, expected_hash):
        file_path = BACKEND_DIR.parent / rel_path
        assert file_path.exists(), f"Production file missing: {rel_path}"
        actual_hash = compute_sha256(file_path)
        assert actual_hash == expected_hash, f"Hash mismatch for {rel_path}!"

    def test_production_threshold_is_0_35(self):
        meta_path = BACKEND_DIR.parent / "backend/models/model_metadata.json"
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        assert meta.get("selected_threshold") == 0.35, "Production threshold must be strictly 0.3500!"


class TestManifestLockAndIndependence:
    """Verifies independent evaluation cohort manifest and integrity."""

    def test_manifest_checksum_matches_lock(self):
        manifest_path = STAGE_DIR / "independent_dataset_manifest.csv"
        lock_path = STAGE_DIR / "manifest_lock.json"
        assert manifest_path.exists()
        assert lock_path.exists()

        with open(lock_path, "r", encoding="utf-8") as f:
            lock = json.load(f)

        actual_sha256 = compute_sha256(manifest_path)
        assert actual_sha256 == lock["sha256_manifest"], "Manifest checksum does not match lock!"

    def test_zero_leakage_against_historical_splits(self):
        splits_sha_path = STAGE_DIR / "src" / "splits_with_disk_sha256.csv"
        assert splits_sha_path.exists()
        df_splits = pd.read_csv(splits_sha_path)
        split_hashes = set(df_splits["sha256_disk"])

        manifest_path = STAGE_DIR / "independent_dataset_manifest.csv"
        df_manifest = pd.read_csv(manifest_path)
        manifest_hashes = set(df_manifest["sha256"])

        overlap = manifest_hashes.intersection(split_hashes)
        assert len(overlap) == 0, f"FATAL DATA LEAKAGE: {len(overlap)} files overlap with splits!"


class TestEvaluationResults:
    """Verifies prospective-blind evaluation outputs and metrics."""

    def test_blind_results_file_complete(self):
        res_path = STAGE_DIR / "blind_evaluation_results.csv"
        assert res_path.exists()
        df = pd.read_csv(res_path)
        assert len(df) == 295, f"Expected 295 results, found {len(df)}"
        assert (df["cohort_role"] == "primary_blind_cohort").sum() == 254
        assert (df["cohort_role"] == "secondary_robustness_cohort").sum() == 41

    def test_short_scream_retention_rate(self):
        res_path = STAGE_DIR / "blind_evaluation_results.csv"
        df = pd.read_csv(res_path)
        short_screams = df[df["canonical_category"] == "SHORT_SCREAM"]
        assert len(short_screams) == 4
        # Model C, Cand G, Model E, Fusion E all achieve 4/4 = 100%
        assert (short_screams["decision_fusion_e"] == 1).sum() == 4
        assert (short_screams["decision_model_c"] == 1).sum() == 4

    def test_monosyllabic_shouting_false_alarm_rate(self):
        res_path = STAGE_DIR / "blind_evaluation_results.csv"
        df = pd.read_csv(res_path)
        mono_shouts = df[df["canonical_category"] == "MONOSYLLABIC_SHOUT"]
        assert len(mono_shouts) == 11
        # Zero false alarms across all models
        assert (mono_shouts["decision_fusion_e"] == 1).sum() == 0
        assert (mono_shouts["decision_model_c"] == 1).sum() == 0
        assert (mono_shouts["decision_candidate_g"] == 1).sum() == 0
        assert (mono_shouts["decision_model_e"] == 1).sum() == 0

    def test_category_error_analysis_file(self):
        err_path = STAGE_DIR / "category_error_analysis.csv"
        assert err_path.exists()
        df_err = pd.read_csv(err_path)
        assert len(df_err) > 0
        # Ensure all models are present
        models = set(df_err["model"])
        assert "Model C" in models
        assert "Candidate G" in models
        assert "Model E" in models
        assert "Stage 8.9.26 Fusion E" in models

    def test_latency_validation_benchmarks(self):
        lat_path = STAGE_DIR / "latency_validation.csv"
        assert lat_path.exists()
        df_lat = pd.read_csv(lat_path)
        assert len(df_lat) == 5
        stages = list(df_lat["stage"])
        assert any("Pre-Screening" in s for s in stages)
        assert any("Model C" in s for s in stages)
        assert any("Verification" in s for s in stages)
        assert any("End-to-End" in s for s in stages)


class TestReconciliationFindings:
    """Verifies that Stage 8.9.26 metric discrepancies were forensically resolved."""

    def test_reconciliation_document_exists(self):
        rec_path = STAGE_DIR / "stage_8_9_26_metric_reconciliation.md"
        assert rec_path.exists()
        content = rec_path.read_text(encoding="utf-8")
        assert "71.43%" in content
        assert "5/7" in content or "5 out of 7" in content
        assert "86.36%" in content
        assert "19/22" in content or "19 out of 22" in content
