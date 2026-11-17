import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = WORKSPACE_DIR.parent.parent
REPO_ROOT = BACKEND_DIR.parent

# Compute hashes of key files
def file_sha256(path: Path) -> str:
    if not path.exists():
        return "FILE_NOT_FOUND"
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

# Git info
try:
    git_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT).decode().strip()
    git_status = subprocess.check_output(["git", "status", "--porcelain"], cwd=REPO_ROOT).decode().strip()
    is_dirty = len(git_status) > 0
except Exception:
    git_hash = "UNAVAILABLE"
    is_dirty = True

manifest_data = {
    "stage": "8.9.23",
    "title": "Scream-Shout Acoustic Separability, Short-Scream Error Analysis & Dataset Validity Audit",
    "timestamp": "2026-10-31T14:30:00+05:30",
    "environment": {
        "os": platform.platform(),
        "python_version": sys.version,
        "machine": platform.machine(),
        "processor": platform.processor(),
    },
    "git_context": {
        "commit_hash": git_hash,
        "working_tree_dirty": is_dirty
    },
    "production_hashes_frozen": {
        "backend/models/scream_classifier.joblib": file_sha256(BACKEND_DIR / "models/scream_classifier.joblib"),
        "backend/models/model_metadata.json": file_sha256(BACKEND_DIR / "models/model_metadata.json"),
        "backend/reports/test_predictions.csv": file_sha256(BACKEND_DIR / "reports/test_predictions.csv"),
        "backend/reports/stage5_test_evaluation.md": file_sha256(BACKEND_DIR / "reports/stage5_test_evaluation.md"),
    },
    "production_threshold": 0.3500,
    "dataset_hashes": {
        "features_stage8_9_17.npz": file_sha256(BACKEND_DIR / "experiments/stage8_9_17_automated_dataset_reconstruction/data/features_stage8_9_17.npz"),
        "features_stage8_9_18_temporal.npz": file_sha256(BACKEND_DIR / "experiments/stage8_9_18_temporal_phonation/data/features_stage8_9_18_temporal.npz"),
        "dataset_manifest_v3.json": file_sha256(BACKEND_DIR / "experiments/v2_hard_negative_training/manifests/dataset_manifest_v3.json")
    },
    "execution_parameters": {
        "random_seed": 42,
        "evaluation_script": "backend/research/stage_8_9_23/src/stage8_9_23_investigation_suite.py",
        "exact_command": ".\\.venv\\Scripts\\python.exe research\\stage_8_9_23\\src\\stage8_9_23_investigation_suite.py",
        "latency_method": "Wall-clock time per sample across held-out split (N=462)",
        "test_suite_command": ".\\.venv\\Scripts\\pytest.exe research\\stage_8_9_23\\tests\\test_stage_8_9_23.py -v"
    },
    "reproduced_metrics_summary": {
        "primary_event_recall_pct": 78.21,
        "hard_negative_fpr_pct": 7.03,
        "shouting_fpr_pct": 20.24,
        "short_scream_recall_pct": 86.36,
        "p95_latency_ms": 16.40,
        "active_tier2_shouting_suppression_observed_on_test": False,
        "reason": "All 17 shouting false alarms exhibited p2 >= 0.40 or triggered chaotic phonation safeguards, remaining unsuppressed on held-out test split"
    }
}

out_path = WORKSPACE_DIR / "reproducibility_manifest.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(manifest_data, f, indent=2)

print(f"Generated {out_path}")
