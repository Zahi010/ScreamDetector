"""Stage 8.9.29 Test Suite — Continuous Streaming Stress Test Validation."""

import csv
import sys
from pathlib import Path
import pytest

STAGE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = STAGE_DIR.parents[1]
# STAGE_DIR set above


def test_stress_test_results_csv():
    """Verify continuous streaming stress test results exist with zero dropped windows."""
    csv_path = STAGE_DIR / "stress_test_results.csv"
    assert csv_path.exists(), f"Stress test CSV missing at {csv_path}"

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    assert len(reader) >= 3, "Must include short, medium, and extended tests"

    for row in reader:
        expected = int(row["expected_windows"])
        processed = int(row["processed_windows"])
        dropped = int(row["dropped_windows"])
        # Account for 3-hop window priming (12 windows across 4 streams)
        assert abs(processed - expected) <= 12, f"Window discrepancy in {row['test_name']}: {processed} vs {expected}"
        assert dropped == 0, f"Dropped windows detected in {row['test_name']}: {dropped}"
        assert row["memory_leak_detected"] == "False", f"Memory leak detected in {row['test_name']}"
