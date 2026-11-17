"""Stage 8.9.30.1 Test Suite — Contamination Exclusion and Partition Leakage."""

import csv
from pathlib import Path
import pytest

STAGE_30_1_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = STAGE_30_1_DIR.parents[1]


def test_zero_historical_stage5_contamination():
    """Verify zero overlap with Stage 5 test predictions or historical census."""
    contam_csv = STAGE_30_1_DIR / "historical_contamination_reaudit.csv"
    assert contam_csv.exists(), f"Missing contamination reaudit at {contam_csv}"

    with open(contam_csv, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 204
    for r in rows:
        assert r["is_stage5_test_overlap"] == "False", f"Contamination: {r['recording_id']} overlaps Stage 5!"
        assert r["is_stage8_9_27_manifest_overlap"] == "False", f"Overlap: {r['recording_id']} overlaps Stage 8.9.27!"
        assert r["contamination_status"] == "CLEAN_INDEPENDENT"


def test_zero_partition_leakage():
    """Verify zero cross-partition leakage across uploaders and multi-clip sessions."""
    leak_csv = STAGE_30_1_DIR / "partition_leakage_audit.csv"
    assert leak_csv.exists(), f"Missing partition leakage audit at {leak_csv}"

    with open(leak_csv, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for r in rows:
        assert r["cross_partition_leakage"] == "ZERO_LEAKAGE", f"Leakage detected for uploader: {r['uploader']}"
