"""Unit and integration tests for Stage 8.9.3 Human-Verified False-Positive Analysis.

Verifies:
1. Frozen classifier weights, metadata hash, and threshold (0.35) preservation.
2. Ground truth human labels strictly preserved (338 APPROVED_NON_SCREAM, 2 SCREAM_PRESENT, 3 AMBIGUOUS).
3. AMBIGUOUS decisions strictly excluded from binary classification metrics.
4. Calculation of confusion matrix (TP, FP, TN, FN), rates, and continuous AUC metrics.
5. Breakdown of false positives by sound category and source provider.
6. API endpoints: /api/review/evaluation/report, /api/review/evaluation/run, /api/review/evaluation/export.csv.
"""

import csv
import hashlib
import io
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.config import DEFAULT_SCREAM_THRESHOLD, MODELS_DIR
from src.database.review_store import get_review_store
from src.dataset.acquisition_evaluator import (
    EXPECTED_CLASSIFIER_SHA256,
    EXPECTED_METADATA_SHA256,
    FROZEN_THRESHOLD,
    verify_frozen_model_artifacts,
)
from src.dataset.false_positive_analyzer import get_false_positive_analyzer

client = TestClient(app)


def test_frozen_model_hashes_and_threshold_preserved():
    """CRITICAL: Ensure model weights, metadata SHA-256, and threshold 0.35 remain unmodified."""
    clf_path = MODELS_DIR / "scream_classifier.joblib"
    meta_path = MODELS_DIR / "model_metadata.json"

    assert clf_path.exists(), "scream_classifier.joblib must exist"
    assert meta_path.exists(), "model_metadata.json must exist"

    clf_sha = hashlib.sha256(clf_path.read_bytes()).hexdigest()
    meta_sha = hashlib.sha256(meta_path.read_bytes()).hexdigest()

    assert clf_sha == EXPECTED_CLASSIFIER_SHA256, f"Classifier hash changed! {clf_sha}"
    assert meta_sha == EXPECTED_METADATA_SHA256, f"Metadata hash changed! {meta_sha}"
    assert FROZEN_THRESHOLD == 0.35
    assert DEFAULT_SCREAM_THRESHOLD == 0.35

    verified, audit = verify_frozen_model_artifacts()
    assert verified is True
    assert audit["classifier_sha256_match"] is True
    assert audit["metadata_sha256_match"] is True


def test_human_labels_ground_truth_integrity():
    """Verify human decisions are exactly as stored and not derived from triage groups."""
    store = get_review_store()
    with store._get_connection() as conn:
        counts = dict(conn.execute(
            "SELECT review_status, COUNT(*) as cnt FROM candidates GROUP BY review_status"
        ).fetchall())

    assert counts.get("APPROVED_NON_SCREAM") == 338, f"Expected 338 approved, got {counts.get('APPROVED_NON_SCREAM')}"
    assert counts.get("SCREAM_PRESENT") == 2, f"Expected 2 screams, got {counts.get('SCREAM_PRESENT')}"
    assert counts.get("AMBIGUOUS") == 3, f"Expected 3 ambiguous, got {counts.get('AMBIGUOUS')}"
    assert counts.get("EXCLUDED", 0) == 0, f"Expected 0 excluded, got {counts.get('EXCLUDED')}"
    assert counts.get("UNREVIEWED") == 27, f"Expected 27 unreviewed, got {counts.get('UNREVIEWED')}"

    total_reviewed = counts.get("APPROVED_NON_SCREAM", 0) + counts.get("SCREAM_PRESENT", 0) + counts.get("AMBIGUOUS", 0)
    assert total_reviewed == 343, f"Expected 343 human decisions, got {total_reviewed}"


def test_classifier_scores_completeness():
    """Verify that all 343 reviewed recordings with audio have a valid model score."""
    analyzer = get_false_positive_analyzer()
    report = analyzer.compute_evaluation_report()

    audit = report["dataset_audit"]
    assert audit["total_candidates"] == 370
    assert audit["audio_available"] == 343
    assert audit["missing_audio"] == 27
    assert audit["total_human_decisions"] == 343
    assert audit["reviewed_missing_scores_count"] == 0, "No reviewed recordings should be missing model scores"
    assert audit["missing_model_scores"] == 27, "Only unacquired audio candidates should be missing scores"


def test_binary_metrics_calculation_human_labels_only():
    """Verify calculation of confusion matrix and metrics from human labels."""
    analyzer = get_false_positive_analyzer()
    report = analyzer.compute_evaluation_report()

    binary = report["binary_evaluation"]
    assert binary["total_binary_evaluated"] == 340
    assert binary["negative_count_approved"] == 338
    assert binary["positive_count_scream"] == 2
    assert binary["excluded_ambiguous_count"] == 3
    assert binary["excluded_other_count"] == 0

    cm = binary["confusion_matrix"]
    assert cm["true_positives"] == 1
    assert cm["false_negatives"] == 1
    assert cm["true_negatives"] == 296
    assert cm["false_positives"] == 42
    assert (cm["true_positives"] + cm["false_negatives"] + cm["true_negatives"] + cm["false_positives"]) == 340

    m = binary["metrics"]
    expected_acc = round(297 / 340, 4)
    expected_spec = round(296 / 338, 4)
    expected_fpr = round(42 / 338, 4)
    expected_rec = round(1 / 2, 4)
    expected_prec = round(1 / 43, 4)

    assert m["accuracy"] == expected_acc
    assert m["specificity"] == expected_spec
    assert m["false_positive_rate"] == expected_fpr
    assert m["recall_sensitivity"] == expected_rec
    assert m["precision"] == expected_prec
    assert m["roc_auc"] is not None
    assert m["pr_auc"] is not None
    assert 0.0 <= m["roc_auc"] <= 1.0
    assert 0.0 <= m["pr_auc"] <= 1.0

    # Verify statistical limitation is explicitly flagged
    assert binary["statistical_limitation"]["flagged"] is True
    assert binary["statistical_limitation"]["positive_count"] == 2
    assert "small" in binary["statistical_limitation"]["message"].lower()


def test_category_and_source_breakdown():
    """Verify false-positive categorization and source attribution."""
    analyzer = get_false_positive_analyzer()
    report = analyzer.compute_evaluation_report()

    cat_breakdown = report["category_breakdown"]
    assert len(cat_breakdown) > 0

    # shouting_and_speech should have highest number of FPs
    shouting_cat = next((c for c in cat_breakdown if c["category"] == "shouting_and_speech"), None)
    assert shouting_cat is not None
    assert shouting_cat["false_positives"] == 18
    assert shouting_cat["false_positive_rate"] > 0.50

    src_breakdown = report["source_breakdown"]
    assert len(src_breakdown) > 0
    fsd50k_src = next((s for s in src_breakdown if s["source"] == "fsd50k"), None)
    assert fsd50k_src is not None
    assert fsd50k_src["false_positives"] == 40


def test_api_evaluation_report_endpoint():
    """Test GET /api/review/evaluation/report."""
    res = client.get("/api/review/evaluation/report")
    assert res.status_code == 200
    data = res.json()

    assert data["evaluation_stage"] == "Stage 8.9.3 — Human-Verified False-Positive Analysis"
    assert data["model_metadata"]["operating_threshold"] == 0.35
    assert data["model_metadata"]["artifacts_verified"] is True
    assert data["binary_evaluation"]["total_binary_evaluated"] == 340
    assert data["binary_evaluation"]["confusion_matrix"]["false_positives"] == 42
    assert len(data["false_positives"]) == 42
    assert len(data["false_negatives"]) == 1
    assert len(data["ambiguous_records"]) == 3


def test_api_evaluation_run_endpoint():
    """Test POST /api/review/evaluation/run returns success and is resumable."""
    res = client.post("/api/review/evaluation/run", json={"force_reevaluate": False})
    assert res.status_code == 200
    data = res.json()

    assert data["success"] is True
    # Since all recordings are scored, resumable run should evaluate 0 additional recordings
    assert data["evaluated_count"] == 0
    assert data["failed_count"] == 0


def test_api_evaluation_export_csv_endpoint():
    """Test GET /api/review/evaluation/export.csv returns valid CSV stream."""
    res = client.get("/api/review/evaluation/export.csv")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert "human_verified_evaluation_report.csv" in res.headers.get("content-disposition", "")

    reader = csv.reader(io.StringIO(res.text))
    rows = list(reader)
    header = rows[0]
    assert "recording_id" in header
    assert "human_label" in header
    assert "model_score" in header
    assert "error_category" in header
    assert len(rows) == 371  # header + 370 recordings
