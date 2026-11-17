"""Stage 8.9.30.1 Test Suite — Baseline Reproducibility and Production Freeze."""

import csv
import hashlib
import json
from pathlib import Path
import pytest

STAGE_30_1_DIR = Path(__file__).resolve().parent.parent
STAGE_30_DIR = Path("backend/research/stage_8_9_30")
BACKEND_DIR = STAGE_30_1_DIR.parents[1]

EXPECTED_PRODUCTION_HASHES = {
    "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
}


def test_baseline_evaluation_metric_reproducibility():
    """Verify baseline evaluation recalculation matches reported numbers mathematically."""
    eval_csv = STAGE_30_DIR / "evaluation" / "frozen_baseline_evaluation.csv"
    if not eval_csv.exists():
        eval_csv = STAGE_30_DIR / "frozen_baseline_evaluation.csv"
    assert eval_csv.exists(), f"Missing evaluation CSV at {eval_csv}"

    with open(eval_csv, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 204

    pos = [r for r in rows if int(r["ground_truth"]) == 1]
    neg = [r for r in rows if int(r["ground_truth"]) == 0]

    assert len(pos) == 137
    assert len(neg) == 67

    tp = sum(1 for r in pos if int(r["predicted_binary"]) == 1)
    fn = sum(1 for r in pos if int(r["predicted_binary"]) == 0)
    fp = sum(1 for r in neg if int(r["predicted_binary"]) == 1)
    tn = sum(1 for r in neg if int(r["predicted_binary"]) == 0)

    assert tp == 114
    assert fn == 23
    assert fp == 30
    assert tn == 37

    recall_pct = (tp / len(pos)) * 100.0
    fpr_pct = (fp / len(neg)) * 100.0

    assert abs(recall_pct - 83.21) < 0.05
    assert abs(fpr_pct - 44.78) < 0.05


def test_dataset_lock_checksum():
    """Verify stage_8_9_30_1_dataset_lock.sha256 matches the actual JSON file."""
    lock_json = STAGE_30_1_DIR / "stage_8_9_30_1_dataset_lock.json"
    lock_sha = STAGE_30_1_DIR / "stage_8_9_30_1_dataset_lock.sha256"

    assert lock_json.exists(), f"Missing lock JSON at {lock_json}"
    assert lock_sha.exists(), f"Missing lock SHA at {lock_sha}"

    expected_sha = lock_sha.read_text(encoding="utf-8").strip().split()[0]
    actual_sha = hashlib.sha256(lock_json.read_bytes()).hexdigest()

    assert actual_sha == expected_sha, f"Checksum mismatch: {actual_sha} vs {expected_sha}"


def test_production_artifacts_strict_freeze():
    """Verify all 4 production artifacts remain byte-for-byte frozen with threshold 0.3500."""
    for rel_path, exp_hash in EXPECTED_PRODUCTION_HASHES.items():
        p = BACKEND_DIR / rel_path.replace("backend/", "")
        assert p.exists(), f"Missing production artifact at {p}"
        actual_hash = hashlib.sha256(p.read_bytes()).hexdigest().lower()
        assert actual_hash == exp_hash, f"CRITICAL: Production hash mismatch for {rel_path}!"

    meta_file = BACKEND_DIR / "models" / "model_metadata.json"
    with open(meta_file, "r", encoding="utf-8") as f:
        meta = json.load(f)
    thresh = float(meta.get("selected_threshold", 0.0))
    assert thresh == 0.3500, f"Production threshold modified: {thresh}"
