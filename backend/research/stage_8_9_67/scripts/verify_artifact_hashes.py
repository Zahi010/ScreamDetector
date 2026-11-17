# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
STAGE 8.9.67 — MANDATORY PROTECTED ASSET INTEGRITY AUDIT
Verifies that all immutable production baseline assets, candidate reference checkpoints,
and sealed evaluation manifests remain bit-for-bit identical with zero modification.

MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
STAGE_DIR = Path(__file__).resolve().parents[1]

EXPECTED_HASHES = {
    # 4 Protected Production Assets (Section 14)
    "production_classifier": {
        "path": "backend/models/scream_classifier.joblib",
        "expected_sha256": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    },
    "model_metadata": {
        "path": "backend/models/model_metadata.json",
        "expected_sha256": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    },
    "test_predictions": {
        "path": "backend/reports/test_predictions.csv",
        "expected_sha256": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    },
    "stage5_evaluation": {
        "path": "backend/reports/stage5_test_evaluation.md",
        "expected_sha256": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
    },
    # Candidate 65-F Frozen Research Benchmark
    "candidate_65f_frozen_checkpoint": {
        "path": "backend/research/stage_8_9_66/models/candidate_65f_frozen.pt",
        "expected_sha256": "06a98025dbdabf462bec305b0cfe8455dd137b3d515cafca8811606865bacfab",
    },
    "candidate_65f_freeze_metadata": {
        "path": "backend/research/stage_8_9_66/models/candidate_freeze_metadata.json",
        "expected_sha256": "a40672a42e3a8d1f38f1ff067cb92b6c45e122b12a25c127f7513d78327944d4",
    },
    # C5 DSP Module
    "c5_combined_dsp": {
        "path": "backend/research/stage_8_9_57/dsp_implementations/c5_combined.py",
        "expected_sha256": "d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58",
    },
    # Historical Manifests
    "stage54_partition_manifest": {
        "path": "backend/research/stage_8_9_54/dataset/partition_manifest_verified.csv",
        "expected_sha256": "10563efcd5d607d1395f9db5ab1aa805a0d9ca39b9b4a64a710816d334caeb9e",
    },
    "stage60_sealed_manifest": {
        "path": "backend/research/stage_8_9_60/future_evaluation_manifest.json",
        "expected_sha256": "9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd",
    },
    "stage63_dev_manifest": {
        "path": "backend/research/stage_8_9_63/stage_63_development_manifest.csv",
        "expected_sha256": "a33e37ecf1bef23bf610baf2a5b42d5e800152dbc518be00a0d4fb5a8229df51",
    },
}


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def verify_all_hashes() -> bool:
    print("=" * 80)
    print("STAGE 8.9.67 — MANDATORY PROTECTED ASSET INTEGRITY AUDIT")
    print("MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.")
    print("=" * 80)

    all_matched = True
    actual_hashes = {}

    for key, spec in EXPECTED_HASHES.items():
        file_path = REPO_ROOT / spec["path"]
        if not file_path.exists():
            print(f"[MISSING] {key}: File not found at {file_path}")
            all_matched = False
            continue

        actual_hash = compute_sha256(file_path)
        actual_hashes[key] = {
            "path": spec["path"],
            "expected_sha256": spec["expected_sha256"],
            "actual_sha256": actual_hash,
            "status": "PASS" if actual_hash == spec["expected_sha256"] else "FAIL",
        }

        if actual_hash == spec["expected_sha256"]:
            print(f"[OK] {key}: {actual_hash}")
        else:
            print(f"[FAIL] {key}: Expected {spec['expected_sha256']} got {actual_hash}")
            all_matched = False

    hash_record_path = STAGE_DIR / "artifact_hashes.json"
    with open(hash_record_path, "w", encoding="utf-8") as f:
        json.dump(actual_hashes, f, indent=2)
    print(f"\nWrote hashes to {hash_record_path}")

    if all_matched:
        print("ALL PROTECTED ASSETS VERIFIED BIT-FOR-BIT IDENTICAL.")
        return True
    else:
        print("ERROR: CRITICAL INTEGRITY CHECK FAILED. UNEXPECTED DRIFT DETECTED.")
        return False


if __name__ == "__main__":
    success = verify_all_hashes()
    sys.exit(0 if success else 1)
