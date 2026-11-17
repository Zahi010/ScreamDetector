"""Stage 8.9.30.1 Test Suite — Duplicate Detection and Source Independence."""

import csv
from pathlib import Path
import pytest

STAGE_30_1_DIR = Path(__file__).resolve().parent.parent


def test_zero_duplicate_collisions():
    """Verify duplicate re-audit detected zero exact SHA-256 or PCM collisions."""
    dup_csv = STAGE_30_1_DIR / "duplicate_reaudit.csv"
    assert dup_csv.exists(), f"Missing duplicate reaudit file at {dup_csv}"

    with open(dup_csv, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    assert len(reader) == 204, f"Expected 204 audited recordings, found {len(reader)}"
    for r in reader:
        assert r["duplicate_type"] == "NONE", f"Duplicate detected for recording {r['recording_id']}"
        assert r["action"] == "KEEP_UNIQUE"


def test_source_independence_reconciliation():
    """Verify source independence audit resolves unique uploaders and clusters multi-clip sessions."""
    si_csv = STAGE_30_1_DIR / "source_independence_audit.csv"
    assert si_csv.exists(), f"Missing source independence audit at {si_csv}"

    with open(si_csv, "r", encoding="utf-8") as f:
        si_rows = list(csv.DictReader(f))

    assert len(si_rows) == 81, f"Expected 81 unique uploaders, found {len(si_rows)}"
    multi_clip_users = [r["uploader"] for r in si_rows if r["multi_clip_session"] == "True"]
    assert "welvynzportersamples" in multi_clip_users, "WelvynZPorterSamples must be identified as multi-clip session"
    assert "todorrobot" in multi_clip_users, "todorrobot must be identified as multi-clip session"
