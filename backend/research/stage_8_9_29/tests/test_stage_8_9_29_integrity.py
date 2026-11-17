"""Stage 8.9.29 Test Suite — Production Freeze & Integrity Verification."""

import hashlib
import json
from pathlib import Path
import pytest

STAGE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = STAGE_DIR.parents[1]
# STAGE_DIR set above

AUTHORITATIVE_HASHES = {
    "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
}


def test_production_artifacts_sha256():
    """Verify all 4 production artifacts match authoritative SHA-256 hashes 100%."""
    for rel_path, expected_hash in AUTHORITATIVE_HASHES.items():
        p = BACKEND_DIR.parent / rel_path
        if not p.exists():
            p = BACKEND_DIR / rel_path
        assert p.exists(), f"Production artifact missing: {rel_path}"
        actual_hash = hashlib.sha256(p.read_bytes()).hexdigest()
        assert actual_hash == expected_hash, (
            f"Production artifact hash mismatch for {rel_path}:\n"
            f"Expected: {expected_hash}\nActual:   {actual_hash}"
        )


def test_production_threshold_exact():
    """Verify production threshold is strictly locked at 0.3500."""
    meta_path = BACKEND_DIR / "models" / "model_metadata.json"
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    assert meta["selected_threshold"] == 0.35, f"Threshold drift detected: {meta['selected_threshold']}"


def test_production_verification_artifact():
    """Verify production_integrity_verification.json exists and certifies freeze."""
    v_path = STAGE_DIR / "production_integrity_verification.json"
    assert v_path.exists(), "Verification artifact missing"
    with open(v_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["overall_integrity_verified"] is True
    assert data["production_status"] == "STRICTLY_FROZEN"
    assert data["decision_threshold_exact"] == 0.35
