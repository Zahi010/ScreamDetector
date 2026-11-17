#!/usr/bin/env python3
"""
STAGE 8.9.61 — Baseline Asset Hash Verification
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import hashlib
import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE54_DIR = BACKEND_DIR / "research" / "stage_8_9_54"
STAGE55_DIR = BACKEND_DIR / "research" / "stage_8_9_55"
STAGE57_DIR = BACKEND_DIR / "research" / "stage_8_9_57"
STAGE60_DIR = BACKEND_DIR / "research" / "stage_8_9_60"
STAGE61_DIR = BACKEND_DIR / "research" / "stage_8_9_61"

EXPECTED_HASHES = {
    "production_classifier": {
        "path": str(BACKEND_DIR / "models" / "scream_classifier.joblib"),
        "expected": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f"
    },
    "model_metadata": {
        "path": str(BACKEND_DIR / "models" / "model_metadata.json"),
        "expected": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60"
    },
    "test_predictions": {
        "path": str(BACKEND_DIR / "reports" / "test_predictions.csv"),
        "expected": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d"
    },
    "stage5_evaluation": {
        "path": str(BACKEND_DIR / "reports" / "stage5_test_evaluation.md"),
        "expected": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2"
    },
    "candidate_e1_checkpoint": {
        "path": str(STAGE54_DIR / "training" / "candidate_e_v954_weighted.pt"),
        "expected": "37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564"
    },
    "candidate_b_checkpoint": {
        "path": str(BACKEND_DIR / "research" / "stage_8_9_44" / "models" / "config_b_mask.pt"),
        "expected": "f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378"
    },
    "intervention_d_code": {
        "path": str(BACKEND_DIR / "research" / "stage_8_9_49" / "scripts" / "whistle_discriminator.py"),
        "expected": "3d98aa7496c6ba89066cfa345a6d0c1ee3605c30821f869a049001c4ad4a8bd2"
    },
    "c5_combined_dsp": {
        "path": str(STAGE57_DIR / "dsp_implementations" / "c5_combined.py"),
        "expected": "d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58"
    },
    "original_e1_dsp": {
        "path": str(STAGE57_DIR / "scripts" / "benchmark_original_dsp.py"),
        "expected": "192e928c6ea427737ef8a3ec4449c890c1d41f01d71c80cefde3f2a0363f5905"
    },
    "frozen_test_manifest": {
        "path": str(STAGE55_DIR / "integrity" / "frozen_test_manifest.json"),
        "expected": "06c9db80d3969e60f78dd441eb1495a9dab97f1646f08ab5825ea979719021f2"
    },
    "stage54_partition_manifest": {
        "path": str(STAGE54_DIR / "dataset" / "partition_manifest_verified.csv"),
        "expected": "10563efcd5d607d1395f9db5ab1aa805a0d9ca39b9b4a64a710816d334caeb9e"
    },
    "future_evaluation_manifest": {
        "path": str(STAGE60_DIR / "future_evaluation_manifest.json"),
        "expected": "9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd"
    }
}

def sha256_file(path_str: str) -> str:
    sha = hashlib.sha256()
    with open(path_str, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()

def main():
    print("Executing Stage 8.9.61 Asset Hash Audit...")
    results = {}
    all_match = True

    for name, info in EXPECTED_HASHES.items():
        p = info["path"]
        exp = info["expected"]
        if not os.path.exists(p):
            print(f"[MISSING] {name} at {p}")
            results[name] = {"path": p, "expected": exp, "actual": "FILE_NOT_FOUND", "status": "FAIL"}
            all_match = False
            continue
        actual = sha256_file(p)
        match = (actual == exp)
        status = "MATCH" if match else "MISMATCH"
        if not match:
            all_match = False
            print(f"[MISMATCH] {name}!\n  Expected: {exp}\n  Actual:   {actual}")
        else:
            print(f"[OK] {name}: {actual}")
        results[name] = {"path": p, "expected": exp, "actual": actual, "status": status}

    out_json = STAGE61_DIR / "artifact_hashes.json"
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nArtifact hashes written to {out_json}")
    if not all_match:
        raise RuntimeError("One or more protected assets failed hash verification!")
    print("All 12 protected assets successfully verified.")

if __name__ == "__main__":
    main()

