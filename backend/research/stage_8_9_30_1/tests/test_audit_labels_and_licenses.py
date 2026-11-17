"""Stage 8.9.30.1 Test Suite — Label Consistency and License Eligibility."""

import csv
from pathlib import Path
import pytest

STAGE_30_1_DIR = Path(__file__).resolve().parent.parent


def test_positive_label_consistency():
    """Verify label audit correctly separates genuine screams from mislabeled non-scream noise."""
    pl_csv = STAGE_30_1_DIR / "positive_label_audit.csv"
    assert pl_csv.exists(), f"Missing positive label audit at {pl_csv}"

    with open(pl_csv, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 204

    confirmed_pos = [r for r in rows if r["audited_label_status"] == "CONFIRMED_POSITIVE"]
    pos_cand = [r for r in rows if r["audited_label_status"] == "POSITIVE_CANDIDATE"]
    rejected = [r for r in rows if r["audited_label_status"] == "REJECTED_POSITIVE_LABEL"]
    negatives = [r for r in rows if r["audited_label_status"] == "CONFIRMED_NEGATIVE"]

    assert len(confirmed_pos) == 75
    assert len(pos_cand) == 31
    assert len(rejected) == 31
    assert len(negatives) == 67

    # Net genuine screams
    assert len(confirmed_pos) + len(pos_cand) == 106

    # Verify all rejected positive labels have non-empty rationale documenting why they were rejected
    for r in rejected:
        assert int(r["audited_ground_truth"]) == 0
        assert len(r["label_rationale"]) > 10, "Rejected label must have clear rationale"


def test_license_commercial_eligibility():
    """Verify all 204 recordings are permissive CC0 or CC-BY with zero non-commercial files."""
    lic_csv = STAGE_30_1_DIR / "license_reaudit.csv"
    assert lic_csv.exists(), f"Missing license reaudit at {lic_csv}"

    with open(lic_csv, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 204

    allowed_licenses = {"CC0-1.0", "CC-BY-3.0", "CC-BY-4.0", "CC-BY"}
    for r in rows:
        assert r["canonical_license"] in allowed_licenses, f"Disallowed license: {r['canonical_license']}"
        assert r["commercial_eligibility"] == "ELIGIBLE_COMMERCIAL"
        assert "nc" not in r["canonical_license"].lower(), "Non-commercial license detected!"
