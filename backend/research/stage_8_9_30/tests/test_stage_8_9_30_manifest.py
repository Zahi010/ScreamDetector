"""Stage 8.9.30 Test Suite — Manifest Integrity & Production Freeze Verification."""

import hashlib
import json
import sys
from pathlib import Path
import pytest

STAGE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = STAGE_DIR.parents[1]
sys.path.insert(0, str(BACKEND_DIR))

EXPECTED_PRODUCTION_HASHES = {
    "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
}


def test_production_artifacts_sha256():
    """Verify all four authoritative production artifacts remain 100% frozen."""
    for rel_path, expected_hash in EXPECTED_PRODUCTION_HASHES.items():
        p = BACKEND_DIR / rel_path.replace("backend/", "")
        assert p.exists(), f"Production artifact missing: {p}"
        actual_hash = hashlib.sha256(p.read_bytes()).hexdigest().lower()
        assert actual_hash == expected_hash, f"CRITICAL: Production hash mismatch for {rel_path}!"


def test_production_decision_threshold_exact():
    """Verify production threshold remains strictly 0.3500."""
    meta_path = BACKEND_DIR / "models" / "model_metadata.json"
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    thresh = float(meta.get("selected_threshold", 0.0))
    assert thresh == 0.3500, f"Production threshold altered: {thresh}"


def test_manifest_lock_checksum():
    """Verify dataset_manifest_lock.json cryptographic checksum matches recording_manifest.csv."""
    lock_file = STAGE_DIR / "dataset_manifest_lock.json"
    if not lock_file.exists():
        pytest.skip("dataset_manifest_lock.json not yet generated.")

    rec_manifest = STAGE_DIR / "metadata" / "recording_manifest.csv"
    assert rec_manifest.exists(), f"Missing recording manifest at {rec_manifest}"

    with open(lock_file, "r", encoding="utf-8") as f:
        lock_data = json.load(f)

    expected_sha = lock_data["manifest_sha256"]
    actual_sha = hashlib.sha256(rec_manifest.read_bytes()).hexdigest()
    assert actual_sha == expected_sha, f"Manifest checksum mismatch: {actual_sha} vs {expected_sha}"
