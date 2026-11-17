#!/usr/bin/env python3
"""
STAGE 8.9.62 — Artifact Cryptographic Hash Verification Script
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE54_DIR = BACKEND_DIR / "research" / "stage_8_9_54"
STAGE57_DIR = BACKEND_DIR / "research" / "stage_8_9_57"
STAGE60_DIR = BACKEND_DIR / "research" / "stage_8_9_60"
STAGE61_DIR = BACKEND_DIR / "research" / "stage_8_9_61"
STAGE62_DIR = BACKEND_DIR / "research" / "stage_8_9_62"

EXPECTED_HASHES = {
    "production_classifier": {
        "path": BACKEND_DIR / "models" / "scream_classifier.joblib",
        "expected": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f"
    },
    "model_metadata": {
        "path": BACKEND_DIR / "models" / "model_metadata.json",
        "expected": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60"
    },
    "test_predictions": {
        "path": BACKEND_DIR / "reports" / "test_predictions.csv",
        "expected": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d"
    },
    "stage5_evaluation": {
        "path": BACKEND_DIR / "reports" / "stage5_test_evaluation.md",
        "expected": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2"
    },
    "candidate_e1_checkpoint": {
        "path": STAGE54_DIR / "training" / "candidate_e_v954_weighted.pt",
        "expected": "37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564"
    },
    "candidate_b_checkpoint": {
        "path": BACKEND_DIR / "research" / "stage_8_9_44" / "models" / "config_b_mask.pt",
        "expected": "f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378"
    },
    "intervention_d_code": {
        "path": BACKEND_DIR / "research" / "stage_8_9_49" / "scripts" / "whistle_discriminator.py",
        "expected": "3d98aa7496c6ba89066cfa345a6d0c1ee3605c30821f869a049001c4ad4a8bd2"
    },
    "c5_combined_dsp": {
        "path": STAGE57_DIR / "dsp_implementations" / "c5_combined.py",
        "expected": "d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58"
    },
    "original_e1_dsp": {
        "path": STAGE57_DIR / "scripts" / "benchmark_original_dsp.py",
        "expected": "192e928c6ea427737ef8a3ec4449c890c1d41f01d71c80cefde3f2a0363f5905"
    },
    "stage54_partition_manifest": {
        "path": STAGE54_DIR / "dataset" / "partition_manifest_verified.csv",
        "expected": "10563efcd5d607d1395f9db5ab1aa805a0d9ca39b9b4a64a710816d334caeb9e"
    },
    "future_evaluation_manifest": {
        "path": STAGE60_DIR / "future_evaluation_manifest.json",
        "expected": "9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd"
    },
    "duplicate_relationships": {
        "path": STAGE60_DIR / "duplicate_and_excerpt_relationships.csv",
        "expected": "f0e602520e2678b317c0cf82f15cb99304b965e477cec3abe21c6561a18d6dea"
    },
    "stage61_dev_manifest": {
        "path": STAGE61_DIR / "rolling_window_development_manifest.csv",
        "expected": "bdf27fdf663c722c4f312ab273839629884892b2ae1d17fa47e70981400d6e1c"
    },
    "stage61_candidate_freeze": {
        "path": STAGE61_DIR / "rolling_window_candidate_freeze.json",
        "expected": "a56982b014e12697982d927c917f1039de35c72b1dc20a1c9ac61dc74e2275df"
    },
    "stage61_preregistration": {
        "path": STAGE61_DIR / "independent_evaluation_preregistration.md",
        "expected": "f6a3c14a1ecd11d783d76f8f27352b577cdb3b6a3f9e4b0724e19f2d58b4248c"
    }
}

def sha256_file(path: Path) -> str:
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()

def main():
    print("Executing Stage 8.9.62 Asset Hash Audit...")
    audit_results = {}
    all_matched = True

    for name, data in EXPECTED_HASHES.items():
        p = data["path"]
        expected = data["expected"]
        if not p.exists():
            print(f"[MISSING] {name}: {p}")
            all_matched = False
            audit_results[name] = {"path": str(p), "status": "MISSING", "expected": expected}
            continue
        actual = sha256_file(p)
        if actual == expected:
            print(f"[OK] {name}: {actual}")
            audit_results[name] = {"path": str(p), "status": "OK", "sha256": actual}
        else:
            print(f"[MISMATCH] {name}: expected {expected}, got {actual}")
            all_matched = False
            audit_results[name] = {"path": str(p), "status": "MISMATCH", "expected": expected, "actual": actual}

    out_file = STAGE62_DIR / "artifact_hashes.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(audit_results, f, indent=2)

    print(f"\nArtifact hashes written to {out_file}")
    if all_matched:
        print("All protected assets successfully verified.")
    else:
        print("ERROR: One or more assets failed verification.")
        exit(1)

if __name__ == "__main__":
    main()
