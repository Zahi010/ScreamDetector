"""Stage 8.9.30 Test Suite — Acquisition & License Classification Validation."""

import csv
import sys
from pathlib import Path
import pytest

STAGE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = STAGE_DIR.parents[1]
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(STAGE_DIR / "acquisition"))

from acquisition_engine import classify_license_string


def test_license_classification_logic():
    """Verify license classifier correctly categorizes CC0, CC-BY, CC-BY-NC, and ARR."""
    # CC0 Public Domain
    can, stat, elig = classify_license_string("http://creativecommons.org/publicdomain/zero/1.0/")
    assert can == "CC0-1.0"
    assert stat == "CC0_VERIFIED"
    assert elig is True

    # CC-BY (Permissive)
    can, stat, elig = classify_license_string("https://creativecommons.org/licenses/by/4.0/")
    assert can == "CC-BY"
    assert stat == "CC_BY_VERIFIED"
    assert elig is True

    # CC-BY-NC (Non-commercial restricted)
    can, stat, elig = classify_license_string("https://creativecommons.org/licenses/by-nc/3.0/")
    assert can == "CC-BY-NC"
    assert stat == "NONCOMMERCIAL_ONLY"
    assert elig is False

    # All Rights Reserved
    can, stat, elig = classify_license_string("Copyright 2026, All Rights Reserved")
    assert can == "ARR"
    assert stat == "RESTRICTED"
    assert elig is False


def test_source_registry_artifact():
    """Verify source_registry.csv exists and defines authorized sources."""
    reg_path = STAGE_DIR / "acquisition" / "source_registry.csv"
    assert reg_path.exists(), f"Missing source registry at {reg_path}"
    with open(reg_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    assert len(reader) >= 2, "Must document at least Freesound API and NIGENS"
    sources = [r["source_id"] for r in reader]
    assert "freesound_api_v2" in sources


def test_no_api_keys_leaked_in_artifacts():
    """Verify no 40-character hex secrets or API tokens were printed in stage artifacts."""
    from src.config import get_freesound_api_key
    key = get_freesound_api_key()
    if not key or len(key) < 10:
        pytest.skip("No API key configured to audit against.")

    # Search all CSV, JSON, MD files in stage 8.9.30
    for ext in ["*.csv", "*.json", "*.md"]:
        for p in STAGE_DIR.rglob(ext):
            content = p.read_text(encoding="utf-8", errors="ignore")
            assert key not in content, f"CRITICAL: API key found in artifact {p}"
