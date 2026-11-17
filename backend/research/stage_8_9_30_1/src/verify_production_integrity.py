"""Verify post-audit production freeze integrity for Stage 8.9.30.1."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

STAGE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = STAGE_DIR.parents[1]

EXPECTED = {
    "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
}

def verify_production_freeze():
    results = {}
    all_match = True
    for rel_path, exp_hash in EXPECTED.items():
        p = BACKEND_DIR / rel_path.replace("backend/", "")
        actual_hash = hashlib.sha256(p.read_bytes()).hexdigest().lower()
        matches = (actual_hash == exp_hash)
        if not matches:
            all_match = False
        results[rel_path] = {
            "expected_sha256": exp_hash,
            "actual_sha256": actual_hash,
            "verified_intact": matches,
        }

    out_data = {
        "stage": "8.9.30.1",
        "verification_timestamp": datetime.now(timezone.utc).isoformat(),
        "production_freeze_status": "STRICTLY_FROZEN_VERIFIED" if all_match else "BREACH_DETECTED",
        "production_threshold": 0.3500,
        "artifacts": results,
    }

    out_file = STAGE_DIR / "production_integrity_verification.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2)

    print("Post-Audit Production Freeze Status:", out_data["production_freeze_status"])
    for k, v in results.items():
        print(f"  {k}: {v['actual_sha256'][:16]}... intact={v['verified_intact']}")

    return all_match

if __name__ == "__main__":
    verify_production_freeze()
