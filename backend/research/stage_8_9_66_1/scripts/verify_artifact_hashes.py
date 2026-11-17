#!/usr/bin/env python3
"""
STAGE 8.9.66.1 — Mandatory Protected Artifact Integrity Audit
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
This system is an experimental acoustic research prototype and is not certified for life-safety use.
"""

import hashlib
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
STAGE66_1_DIR = SCRIPT_DIR.parent
RESEARCH_DIR = STAGE66_1_DIR.parent
BACKEND_DIR = RESEARCH_DIR.parent
REPO_ROOT = BACKEND_DIR.parent

ARTIFACT_MANIFEST = {
    # 4 Core Production Assets (Section 9)
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

    # Candidate 65-F Frozen Checkpoint & Metadata (Section 8)
    "candidate_65f_frozen_checkpoint": {
        "path": RESEARCH_DIR / "stage_8_9_66" / "models" / "candidate_65f_frozen.pt",
        "expected": "06a98025dbdabf462bec305b0cfe8455dd137b3d515cafca8811606865bacfab"
    },
    "candidate_65f_freeze_metadata": {
        "path": RESEARCH_DIR / "stage_8_9_66" / "models" / "candidate_freeze_metadata.json",
        "expected": "a40672a42e3a8d1f38f1ff067cb92b6c45e122b12a25c127f7513d78327944d4"
    },

    # Historical Key Reference Checkpoints and Implementations
    "candidate_e1_checkpoint": {
        "path": RESEARCH_DIR / "stage_8_9_54" / "training" / "candidate_e_v954_weighted.pt",
        "expected": "37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564"
    },
    "c5_combined_dsp": {
        "path": RESEARCH_DIR / "stage_8_9_57" / "dsp_implementations" / "c5_combined.py",
        "expected": "d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58"
    },
    "stage54_partition_manifest": {
        "path": RESEARCH_DIR / "stage_8_9_54" / "dataset" / "partition_manifest_verified.csv",
        "expected": "10563efcd5d607d1395f9db5ab1aa805a0d9ca39b9b4a64a710816d334caeb9e"
    },
    "stage60_sealed_manifest": {
        "path": RESEARCH_DIR / "stage_8_9_60" / "future_evaluation_manifest.json",
        "expected": "9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd"
    },
    "stage61_dev_manifest": {
        "path": RESEARCH_DIR / "stage_8_9_61" / "rolling_window_development_manifest.csv",
        "expected": "bdf27fdf663c722c4f312ab273839629884892b2ae1d17fa47e70981400d6e1c"
    },
    "stage63_dev_manifest": {
        "path": RESEARCH_DIR / "stage_8_9_63" / "stage_63_development_manifest.csv",
        "expected": "a33e37ecf1bef23bf610baf2a5b42d5e800152dbc518be00a0d4fb5a8229df51"
    },
    "stage64_dual_res_checkpoint": {
        "path": RESEARCH_DIR / "stage_8_9_64" / "models" / "stage63_dual_resolution_gated.pt",
        "expected": "4374c5e4abb36e999ee863ae8dcd478f8bfb4e39968331120a211fe181572e34"
    },
    "stage64_short_manifest": {
        "path": RESEARCH_DIR / "stage_8_9_64" / "stage_64_short_scream_manifest.csv",
        "expected": "658ae11fc79154960c6e675ac184ac126808c01c250d0ff354d4bd26a3f04e5b"
    }
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def verify_all_protected_assets():
    print("=" * 80)
    print("STAGE 8.9.66.1 — MANDATORY PROTECTED ASSET INTEGRITY AUDIT")
    print("MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.")
    print("=" * 80)

    results = {}
    all_ok = True

    for name, item in ARTIFACT_MANIFEST.items():
        p = item["path"]
        exp = item["expected"]
        if not p.exists():
            print(f"[MISSING] {name}: {p}")
            all_ok = False
            results[name] = {"path": str(p), "status": "MISSING", "expected": exp, "actual": None}
            continue

        act = sha256_file(p)
        if exp is not None and act != exp:
            print(f"[MUTATED] {name}: expected {exp}, got {act}")
            all_ok = False
            results[name] = {"path": str(p), "status": "MUTATED", "expected": exp, "actual": act}
        else:
            print(f"[OK] {name}: {act}")
            results[name] = {"path": str(p), "status": "OK", "expected": exp, "actual": act}

    # Save to artifact_hashes.json
    out_json = STAGE66_1_DIR / "artifact_hashes.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nWrote hashes to {out_json}")

    if all_ok:
        print("ALL PROTECTED ASSETS VERIFIED BIT-FOR-BIT IDENTICAL.")
    else:
        print("CRITICAL: ONE OR MORE PROTECTED ASSETS FAILED INTEGRITY VERIFICATION!")
    return all_ok


if __name__ == "__main__":
    if not verify_all_protected_assets():
        sys.exit(1)
