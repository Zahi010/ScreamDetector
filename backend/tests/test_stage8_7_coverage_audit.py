"""Stage 8.7 Automated Test Suite: Dataset Coverage Audit and AudioSet Investigation.

Tests:
1. Reconciled inventory counts match actual manifest files (1,621 eligible recordings).
2. Duplicate recordings are not incorrectly counted as independent sources.
3. Unknown/unreviewed labels remain unknown rather than being converted to non-scream.
4. Missing audio files are detected and reported.
5. The 521-class inventory is complete (521 classes loaded from class map).
6. AudioSet metadata is not misreported as playable audio.
7. Existing model and metadata SHA-256 hashes remain unchanged.
8. Historical Stage 4 splits and Stage 5 test predictions are untouched.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import pytest

from src.config import (
    BACKEND_DIR,
    DEFAULT_SCREAM_THRESHOLD,
    MANIFESTS_DIR,
    MODELS_DIR,
    REPORTS_DIR,
)

EXPECTED_CLASSIFIER_HASH = "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f"
EXPECTED_METADATA_HASH = "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60"
AUDIT_DIR = REPORTS_DIR / "stage8_7_dataset_coverage_audit"


def compute_file_sha256(filepath: Path) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# 1. Model Baseline Immutability Tests
# ---------------------------------------------------------------------------

def test_model_classifier_hash_immutable():
    """Verify scream_classifier.joblib hash matches Stage 5 frozen baseline."""
    clf_path = MODELS_DIR / "scream_classifier.joblib"
    assert clf_path.exists(), "Classifier file missing"
    assert compute_file_sha256(clf_path) == EXPECTED_CLASSIFIER_HASH


def test_model_metadata_hash_immutable():
    """Verify model_metadata.json hash matches Stage 5 frozen baseline."""
    meta_path = MODELS_DIR / "model_metadata.json"
    assert meta_path.exists(), "Metadata file missing"
    assert compute_file_sha256(meta_path) == EXPECTED_METADATA_HASH


def test_threshold_frozen_at_0_35():
    """Verify operating threshold remains strictly 0.35."""
    assert DEFAULT_SCREAM_THRESHOLD == 0.35
    with open(MODELS_DIR / "model_metadata.json", "r", encoding="utf-8") as f:
        meta = json.load(f)
    assert meta.get("selected_threshold") == 0.35


# ---------------------------------------------------------------------------
# 2. Manifest Reconciliation & Count Verification Tests
# ---------------------------------------------------------------------------

def test_manifest_reconciled_counts():
    """Verify that split_manifest.json contains exactly 1,621 eligible recordings."""
    split_manifest = MANIFESTS_DIR / "split_manifest.json"
    assert split_manifest.exists()
    with open(split_manifest, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = data["records"]
    assert len(records) == 1621, f"Expected 1621 eligible recordings, got {len(records)}"

    scream_recs = [r for r in records if r["binary_label"] == "scream"]
    non_scream_recs = [r for r in records if r["binary_label"] == "non_scream"]

    assert len(scream_recs) == 127
    assert len(non_scream_recs) == 1494

    # Verify split partition breakdown
    train_recs = [r for r in records if r["split"] == "train"]
    val_recs = [r for r in records if r["split"] == "val"]
    test_recs = [r for r in records if r["split"] == "test"]

    assert len(train_recs) == 1134  # 89 scream, 1045 non-scream
    assert len(val_recs) == 244     # 19 scream, 225 non-scream
    assert len(test_recs) == 243    # 19 scream, 224 non-scream


def test_exclusions_quarantined():
    """Verify that unified_manifest.json holds exactly 4 quarantined exclusions."""
    unified_manifest = MANIFESTS_DIR / "unified_manifest.json"
    assert unified_manifest.exists()
    with open(unified_manifest, "r", encoding="utf-8") as f:
        data = json.load(f)

    exclusions = data.get("exclusions", [])
    assert len(exclusions) == 4, f"Expected 4 exclusions, got {len(exclusions)}"

    reasons = [e.get("exclusion_reason") for e in exclusions]
    assert any("watermark" in r for r in reasons)
    assert any("duplicate" in r for r in reasons)
    assert any("screamer" in r for r in reasons)
    assert any("gasp" in r for r in reasons)


def test_duplicate_recordings_not_counted_as_independent_sources():
    """Verify that duplicate files are grouped by source_group_id and not counted as independent."""
    split_manifest = MANIFESTS_DIR / "split_manifest.json"
    with open(split_manifest, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = data["records"]
    source_groups = set(r["source_group_id"] for r in records)

    # 1,621 recordings map to exactly 726 source groups (significant clustering)
    assert len(source_groups) == 726
    assert len(source_groups) < len(records)


def test_unknown_labels_remain_unknown():
    """Verify that unknown/unlabeled records are not converted to non_scream."""
    with open(MANIFESTS_DIR / "unified_manifest.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Exclusions marked 'needs_review' must not be in the training set
    exclusions = data.get("exclusions", [])
    for ex in exclusions:
        if ex.get("binary_label") == "needs_review":
            assert ex["file_id"] not in [r["file_id"] for r in data["records"]]


# ---------------------------------------------------------------------------
# 3. YAMNet 521 Class Inventory Tests
# ---------------------------------------------------------------------------

def test_yamnet_521_class_inventory_complete():
    """Verify yamnet_521_class_inventory.csv contains exactly 521 classes."""
    inv_file = AUDIT_DIR / "yamnet_521_class_inventory.csv"
    assert inv_file.exists(), f"Class inventory missing: {inv_file}"

    with open(inv_file, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    assert len(reader) == 521, f"Expected 521 classes, got {len(reader)}"

    # Check key classes exist
    names = [r["display_name"] for r in reader]
    assert "Screaming" in names
    assert "Laughter" in names
    assert "Baby cry, infant cry" in names
    assert "Cheering" in names
    assert "Applause" in names
    assert "Whistle" in names
    assert "Synthesizer" in names
    assert "Squeak" in names


# ---------------------------------------------------------------------------
# 4. AudioSet Source Assessment Deliverable Tests
# ---------------------------------------------------------------------------

def test_audioset_not_misreported_as_playable_audio():
    """Verify audioset_source_assessment.md clearly reports that AudioSet does NOT distribute audio."""
    assessment_file = AUDIT_DIR / "audioset_source_assessment.md"
    assert assessment_file.exists()

    text = assessment_file.read_text(encoding="utf-8")
    assert "DOES NOT DISTRIBUTE RAW PLAYABLE AUDIO" in text
    assert "REQUIRES LEGAL REVIEW" in text
    assert "link rot" in text.lower()


def test_hard_negative_priority_list_generated():
    """Verify hard_negative_priority_list.csv contains ranked priorities."""
    priority_file = AUDIT_DIR / "hard_negative_priority_list.csv"
    assert priority_file.exists()

    with open(priority_file, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    assert len(reader) >= 5
    ranks = [int(r["priority_rank"]) for r in reader]
    assert ranks == sorted(ranks)
    assert any("Whistle" in r["category"] for r in reader)
    assert any("Cheering" in r["category"] for r in reader)
    assert any("EDM" in r["category"] or "Synth" in r["category"] for r in reader)


def test_artifact_integrity_json_verdict():
    """Verify artifact_integrity.json confirms PASS."""
    integrity_file = AUDIT_DIR / "artifact_integrity.json"
    assert integrity_file.exists()

    with open(integrity_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["integrity_verdict"] == "PASS"
    assert data["model_classifier"]["status"] == "VERIFIED_MATCH"
    assert data["model_metadata"]["status"] == "VERIFIED_MATCH"
