"""Stage 8.9.29 Test Suite — Multi-Stream Concurrency & Manager Tests."""

import csv
import sys
from pathlib import Path
import numpy as np
import pytest

STAGE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = STAGE_DIR.parents[1]
# STAGE_DIR set above
sys.path.insert(0, str(STAGE_DIR))

from streaming_manager import MultiStreamInferenceManager


def test_multi_stream_registration_lifecycle():
    """Verify stream contexts can be dynamically registered, reset, and closed."""
    mgr = MultiStreamInferenceManager(backend="tensorflow")

    # Register 4 streams
    for i in range(4):
        ctx = mgr.register_stream(f"stream_{i}")
        assert ctx.is_active is True
        assert ctx.stream_id == f"stream_{i}"

    assert len(mgr.streams) == 4

    # Reset stream 1
    mgr.reset_stream("stream_1")
    assert mgr.streams["stream_1"].windows_processed == 0

    # Unregister stream 2
    mgr.unregister_stream("stream_2")
    assert "stream_2" not in mgr.streams
    assert len(mgr.streams) == 3


def test_concurrency_benchmark_csv_deliverable():
    """Verify concurrency_benchmark_results.csv exists and satisfies single-stream 25ms gate."""
    csv_path = STAGE_DIR / "concurrency_benchmark_results.csv"
    assert csv_path.exists(), f"Benchmark CSV missing at {csv_path}"

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    assert len(reader) >= 4, "Must benchmark 1, 2, 4, 8 streams"

    # Single stream must pass 25ms computational gate
    row_1 = [r for r in reader if int(r["concurrent_streams"]) == 1][0]
    p95_compute = float(row_1["compute_p95_ms"])
    assert p95_compute <= 25.0, f"Single stream failed 25ms gate: {p95_compute} ms"
    assert int(row_1["dropped_windows"]) == 0
