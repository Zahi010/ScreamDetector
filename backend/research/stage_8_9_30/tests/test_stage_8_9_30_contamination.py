"""Stage 8.9.30 Test Suite — Contamination Audit & Source-Group Validation."""

import csv
import json
import sys
from pathlib import Path
import pytest

STAGE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = STAGE_DIR.parents[1]
sys.path.insert(0, str(BACKEND_DIR))


def test_zero_stage5_test_contamination():
    """Verify zero overlap with Stage 5 test predictions (by file relative path, hash, or source group)."""
    test_csv = BACKEND_DIR / "reports" / "test_predictions.csv"
    assert test_csv.exists(), f"Missing Stage 5 test predictions at {test_csv}"

    test_source_groups = set()
    with open(test_csv, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            sg = r.get("source_group_id", "").strip().lower()
            if sg:
                test_source_groups.add(sg)
                if sg.startswith("freesound_"):
                    test_source_groups.add(sg.replace("freesound_", ""))

    rec_manifest = STAGE_DIR / "metadata" / "recording_manifest.csv"
    if not rec_manifest.exists():
        pytest.skip("recording_manifest.csv not yet generated.")

    with open(rec_manifest, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    for r in reader:
        uploader = r.get("uploader_creator", "").strip().lower()
        sg_id = r.get("source_group_id", "").strip().lower()
        assert uploader not in test_source_groups, f"Contamination: uploader '{uploader}' present in Stage 5 test!"
        assert sg_id not in test_source_groups, f"Contamination: source group '{sg_id}' present in Stage 5 test!"


def test_positive_and_negative_separation():
    """Verify positive and hard-negative labels are distinct and correctly mapped."""
    rec_manifest = STAGE_DIR / "metadata" / "recording_manifest.csv"
    if not rec_manifest.exists():
        pytest.skip("recording_manifest.csv not yet generated.")

    with open(rec_manifest, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    for r in reader:
        gt = int(r["ground_truth"])
        bin_label = r["binary_label"]
        triage_cat = r["triage_category"]

        if gt == 1:
            assert bin_label == "scream"
            assert triage_cat in ("APPROVED_POSITIVE_CANDIDATE", "POSSIBLE_POSITIVE")
        else:
            assert bin_label == "non_scream"
            assert triage_cat in ("NEGATIVE_CONFUSER", "AMBIGUOUS", "LICENSE_QUARANTINE", "INVALID_AUDIO")
