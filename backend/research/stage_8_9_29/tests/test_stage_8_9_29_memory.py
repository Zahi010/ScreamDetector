"""Stage 8.9.29 Test Suite — Memory & Resource Leak Investigation."""

import csv
import sys
from pathlib import Path
import pytest

STAGE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = STAGE_DIR.parents[1]
# STAGE_DIR set above


def test_memory_profile_csv_bounded():
    """Verify memory_profile.csv exists and shows bounded RSS memory."""
    csv_path = STAGE_DIR / "memory_profile.csv"
    assert csv_path.exists(), f"Memory profile CSV missing at {csv_path}"

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    assert len(reader) >= 3, "Memory profile should have multiple sampling points"

    rss_values = [float(r["memory_rss_mb"]) for r in reader]
    initial_rss = rss_values[0]
    final_rss = rss_values[-1]
    net_growth = final_rss - initial_rss

    # Memory growth over 60-min simulation must not exceed 50 MB
    assert net_growth < 50.0, f"Unbounded memory growth detected: {net_growth:.2f} MB"
