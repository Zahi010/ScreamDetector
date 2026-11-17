#!/usr/bin/env python3
"""
STAGE 8.9.66 — Protected Baseline Asset Integrity Audit
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE54_DIR = BACKEND_DIR / "research" / "stage_8_9_54"
STAGE57_DIR = BACKEND_DIR / "research" / "stage_8_9_57"
STAGE60_DIR = BACKEND_DIR / "research" / "stage_8_9_60"
STAGE61_DIR = BACKEND_DIR / "research" / "stage_8_9_61"
STAGE62_DIR = BACKEND_DIR / "research" / "stage_8_9_62"
STAGE63_DIR = BACKEND_DIR / "research" / "stage_8_9_63"
STAGE64_DIR = BACKEND_DIR / "research" / "stage_8_9_64"
STAGE65_DIR = BACKEND_DIR / "research" / "stage_8_9_65"
STAGE66_DIR = BACKEND_DIR / "research" / "stage_8_9_66"

PROTECTED_ASSETS = {
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
    "stage60_sealed_manifest": {
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
    },
    "stage61_sealed_predictions": {
        "path": STAGE61_DIR / "sealed_cohort_predictions.csv",
        "expected": "707e73ca412d3e641ebdf9ff3a447723c46058bd2bbdc5b5eed473fdf42a3689"
    },
    "stage63_dev_manifest": {
        "path": STAGE63_DIR / "stage_63_development_manifest.csv",
        "expected": "a33e37ecf1bef23bf610baf2a5b42d5e800152dbc518be00a0d4fb5a8229df51"
    },
    "stage63_short_manifest": {
        "path": STAGE63_DIR / "short_scream_acquisition_manifest.csv",
        "expected": "bf7e2fe9f290c83be23750b683e89c13e738739322f9a4badf13dcd4b937e0c2"
    },
    "stage64_dual_res_checkpoint": {
        "path": STAGE64_DIR / "models" / "stage63_dual_resolution_gated.pt",
        "expected": "4374c5e4abb36e999ee863ae8dcd478f8bfb4e39968331120a211fe181572e34"
    },
    "stage64_short_manifest": {
        "path": STAGE64_DIR / "stage_64_short_scream_manifest.csv",
        "expected": "658ae11fc79154960c6e675ac184ac126808c01c250d0ff354d4bd26a3f04e5b"
    },
    "stage64_reproduction_csv": {
        "path": STAGE64_DIR / "dual_resolution_reproduction.csv",
        "expected": "f59dd0f84ba51c950738a4d414e01f1354e838257d2a568c40b946b134da1670"
    }
}

def sha256_file(path: Path) -> str:
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()

compute_sha256 = sha256_file
ARTIFACT_MANIFEST = PROTECTED_ASSETS

def main():
    print("=" * 80)
    print("STAGE 8.9.66 — MANDATORY PROTECTED ASSET INTEGRITY AUDIT")
    print("=" * 80)

    all_passed = True
    computed_hashes = {}

    for name, asset in PROTECTED_ASSETS.items():
        p = asset["path"]
        expected = asset["expected"]

        if not p.exists():
            print(f"[MISSING] {name}: {p}")
            all_passed = False
            continue

        actual = sha256_file(p)
        computed_hashes[name] = {
            "path": str(p),
            "sha256": actual,
            "expected": expected
        }

        if actual != expected:
            print(f"[DRIFT DETECTED] {name} ({p.name})")
            print(f"  Expected: {expected}")
            print(f"  Actual:   {actual}")
            all_passed = False
        else:
            print(f"[OK] {name}: {actual}")

    # Write output to stage_8_9_66 directory
    out_json = STAGE66_DIR / "artifact_hashes.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(computed_hashes, f, indent=2)
    print(f"\nWrote hashes to {out_json}")

    if not all_passed:
        print("\nFATAL: Protected artifact integrity check failed. Halting.")
        sys.exit(1)
    else:
        print("\nAll protected assets successfully verified bit-for-bit.")
        print("ALL 21 ARTIFACTS VERIFIED BIT-FOR-BIT IDENTICAL")

if __name__ == "__main__":
    main()

