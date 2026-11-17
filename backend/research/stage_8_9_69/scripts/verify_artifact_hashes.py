# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
STAGE 8.9.69 — ARTIFACT HASH VERIFICATION SCRIPT
Verifies cryptographic SHA-256 hashes for all critical baseline models,
checkpoints, evaluation manifests, and stage deliverables.

MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
STAGE_DIR = Path(__file__).resolve().parents[1]

EXPECTED_HASHES = {
    # 4 Protected Baseline Production Assets
    "production_classifier_joblib": (
        REPO_ROOT / "backend/models/scream_classifier.joblib",
        "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f"
    ),
    "production_model_metadata": (
        REPO_ROOT / "backend/models/model_metadata.json",
        "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60"
    ),
    "production_test_predictions": (
        REPO_ROOT / "backend/reports/test_predictions.csv",
        "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d"
    ),
    "production_stage5_eval_report": (
        REPO_ROOT / "backend/reports/stage5_test_evaluation.md",
        "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2"
    ),
    # Historical Frozen Research Candidates
    "candidate_65f_frozen": (
        REPO_ROOT / "backend/research/stage_8_9_66/models/candidate_65f_frozen.pt",
        "06a98025dbdabf462bec305b0cfe8455dd137b3d515cafca8811606865bacfab"
    ),
    "candidate_67_frozen": (
        REPO_ROOT / "backend/research/stage_8_9_67/models/candidate_67_frozen.pt",
        "8fc2255a337f1375870370216416b94d9c2003a2b8939dbee1301115f53a7b18"
    ),
    "candidate_68_frozen": (
        REPO_ROOT / "backend/research/stage_8_9_68/models/candidate_68_frozen.pt",
        "8a3b425a2885cfeeb4d9e6a64c04619949978cad5b55a8a5f60b5ee379949dc4"
    ),
    # Stage 60 Sealed Cohort Manifest (Strictly Quarantined)
    "stage60_sealed_evaluation_manifest": (
        REPO_ROOT / "backend/research/stage_8_9_60/future_evaluation_manifest.json",
        "9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd"
    ),
    # Stage 8.9.69 Champion Checkpoint
    "candidate_69_frozen": (
        STAGE_DIR / "models/candidate_69_frozen.pt",
        "d468b75ab12d5ef2b8577c18304e8c4ddaf78f3059b2c0395a1a3263ac6dd92c"
    ),
}


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def verify_all_artifacts():
    print("=" * 80)
    print("STAGE 8.9.69 — CRYPTOGRAPHIC SHA-256 HASH VERIFICATION")
    print("MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.")
    print("=" * 80)

    results = {}
    all_passed = True

    for name, (path, expected) in EXPECTED_HASHES.items():
        if not path.exists():
            print(f"[-] MISSING: {name} at {path}")
            results[name] = {"status": "MISSING", "path": str(path)}
            all_passed = False
            continue

        actual = compute_sha256(path)
        if actual.lower() == expected.lower():
            print(f"[+] VERIFIED: {name:35} -> {actual[:16]}... OK")
            results[name] = {"status": "VERIFIED", "path": str(path), "sha256": actual}
        else:
            print(f"[!] MISMATCH: {name}\n    Expected: {expected}\n    Actual:   {actual}")
            results[name] = {"status": "MISMATCH", "expected": expected, "actual": actual}
            all_passed = False

    # Save artifact hashes json in stage directory
    out_json = STAGE_DIR / "artifact_hashes.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nWrote verification results to {out_json}")

    # Also write artifact_hashes.sha256
    out_sha = STAGE_DIR / "artifact_hashes.sha256"
    with open(out_sha, "w", encoding="utf-8") as f:
        for name, data in results.items():
            if data.get("sha256"):
                f.write(f"{data['sha256']}  {Path(data['path']).name} ({name})\n")
    print(f"Wrote SHA256 manifest to {out_sha}")

    if not all_passed:
        raise ValueError("One or more artifact cryptographic hashes failed verification!")

    print("\nAll protected and stage 69 artifacts successfully verified bit-for-bit identical.")
    return True


if __name__ == "__main__":
    verify_all_artifacts()

