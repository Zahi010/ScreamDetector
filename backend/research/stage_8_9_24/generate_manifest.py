"""
Stage 8.9.24 Reproducibility Manifest Generator.
Records:
- Platform & dependency environment
- Frozen production artifact hashes
- Dataset hashes
- Latency and metric benchmarks
"""

import hashlib
import json
import platform
import sys
from pathlib import Path

WORKSPACE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = WORKSPACE_DIR.parent.parent

def file_sha256(path: Path) -> str:
    if not path.exists():
        return "FILE_NOT_FOUND"
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

manifest = {
    "stage": "8.9.24",
    "title": "Temporal Modulation & Syllabic Cadence Verification",
    "timestamp": "2026-10-31T15:00:00+05:30",
    "environment": {
        "os": platform.platform(),
        "python_version": sys.version,
        "machine": platform.machine(),
        "processor": platform.processor(),
    },
    "production_hashes_frozen": {
        "backend/models/scream_classifier.joblib": file_sha256(BACKEND_DIR / "models/scream_classifier.joblib"),
        "backend/models/model_metadata.json": file_sha256(BACKEND_DIR / "models/model_metadata.json"),
        "backend/reports/test_predictions.csv": file_sha256(BACKEND_DIR / "reports/test_predictions.csv"),
        "backend/reports/stage5_test_evaluation.md": file_sha256(BACKEND_DIR / "reports/stage5_test_evaluation.md"),
    },
    "production_threshold": 0.3500,
    "dataset_hashes": {
        "features_stage8_9_18_temporal.npz": file_sha256(BACKEND_DIR / "experiments/stage8_9_18_temporal_phonation/data/features_stage8_9_18_temporal.npz"),
        "source_group_splits.csv": file_sha256(BACKEND_DIR / "experiments/stage8_9_17_automated_dataset_reconstruction/data/manifests/source_group_splits.csv"),
    },
    "execution_parameters": {
        "random_seed": 42,
        "test_suite_command": ".\\.venv\\Scripts\\pytest.exe research\\stage_8_9_24\\temporal_feature_tests.py -v",
        "sample_rate": 16000,
        "frame_ms": 25.0,
        "hop_ms": 12.5,
    },
    "audited_metrics_summary": {
        "candidate_a_recall_pct": 78.21,
        "candidate_a_shouting_fpr_pct": 20.24,
        "candidate_a_hard_neg_fpr_pct": 7.03,
        "candidate_a_short_scream_recall_pct": 86.36,
        "candidate_g_recall_pct": 80.77,
        "candidate_g_shouting_fpr_pct": 15.48,
        "candidate_g_hard_neg_fpr_pct": 5.99,
        "candidate_g_short_scream_recall_pct": 86.36,
        "computational_latency_p95_ms": 2.42,
        "gate_status": "REJECTED (Research Only)",
    }
}

out_path = WORKSPACE_DIR / "reproducibility_manifest.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

print(f"Generated {out_path}")
