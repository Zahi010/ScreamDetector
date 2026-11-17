# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
STAGE 8.9.68 — MANDATORY PROTECTED ASSET INTEGRITY AUDIT
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
    # 4 Protected Production Assets (Section 12)
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
    # Candidate 67-D Frozen Research Champion
    "candidate_67d_frozen_checkpoint": {
        "path": "backend/research/stage_8_9_67/models/candidate_67_frozen.pt",
        "expected_sha256": "8fc2255a337f1375870370216416b94d9c2003a2b8939dbee1301115f53a7b18",
    },
    # C5 Combined DSP
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
}


def sha256_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def run_audit() -> bool:
    print("=" * 80)
    print("STAGE 8.9.68 — MANDATORY PROTECTED ASSET INTEGRITY AUDIT")
    print("MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.")
    print("=" * 80)

    all_matched = True
    actual_hashes = {}

    for name, item in EXPECTED_HASHES.items():
        p = REPO_ROOT / item["path"]
        if not p.exists():
            print(f"[FAIL - MISSING FILE] {name}: {p}")
            all_matched = False
            continue

        observed = sha256_file(p)
        expected = item["expected_sha256"]
        actual_hashes[name] = {"path": str(p), "sha256": observed}

        if observed == expected:
            print(f"[OK] {name}: {observed}")
        else:
            print(f"[FAIL - MISMATCH] {name}:")
            print(f"     Expected: {expected}")
            print(f"     Observed: {observed}")
            all_matched = False

    out_file = STAGE_DIR / "artifact_hashes.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(actual_hashes, f, indent=2)
    print(f"\nWrote hashes to {out_file}")

    if all_matched:
        print("ALL PROTECTED ASSETS VERIFIED BIT-FOR-BIT IDENTICAL.")
    else:
        print("INTEGRITY VIOLATION DETECTED!")
    return all_matched


if __name__ == "__main__":
    success = run_audit()
    sys.exit(0 if success else 1)

