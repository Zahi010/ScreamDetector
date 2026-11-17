# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
STAGE 8.9.74 — ARTIFACT HASH VERIFICATION SCRIPT
Computes and verifies SHA-256 integrity hashes for all Stage 8.9.74 artifacts,
checkpoints, reports, scripts, and ensures baseline production immutability.

MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
STAGE_DIR = Path(__file__).resolve().parents[1]

PROTECTED_BASELINE_HASHES = {
    "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
    "backend/research/stage_8_9_60/future_evaluation_manifest.json": "9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd",
    "backend/research/stage_8_9_74/models/candidate_71_frozen.pt": "e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b",
}

def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def verify_all():
    print("=" * 80)
    print("STAGE 8.9.74 ARTIFACT HASH VERIFICATION")
    print("=" * 80)

    # 1. Verify Protected Baseline Files
    print("\n1. Verifying Protected Baseline Files (Immutability Check):")
    for rel_path, expected_hash in PROTECTED_BASELINE_HASHES.items():
        full_path = REPO_ROOT / rel_path
        if not full_path.exists():
            raise FileNotFoundError(f"Protected file missing: {full_path}")
        actual_hash = compute_sha256(full_path)
        assert actual_hash == expected_hash, f"CORRUPTION DETECTED in {rel_path}! Expected {expected_hash}, got {actual_hash}"
        print(f"  [OK] {rel_path}: {actual_hash[:16]}... matches expected.")

    # 2. Compute and Record Hashes for all Stage 74 Artifacts
    print("\n2. Cataloging Stage 8.9.74 Artifact Hashes:")
    stage74_hashes = {}
    sha256_lines = []

    # All files under stage_8_9_74
    for p in sorted(STAGE_DIR.rglob("*")):
        if p.is_file() and p.name not in ["artifact_hashes.json", "artifact_hashes.sha256"] and "__pycache__" not in str(p):
            rel_str = str(p.relative_to(REPO_ROOT)).replace("\\", "/")
            h = compute_sha256(p)
            stage74_hashes[rel_str] = h
            sha256_lines.append(f"{h}  {rel_str}")
            print(f"  [FILE] {p.name}: {h}")

    # Save to JSON and sha256 in stage directory and reports
    for out_dir in [STAGE_DIR, STAGE_DIR / "reports"]:
        json_path = out_dir / "artifact_hashes.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(stage74_hashes, f, indent=2)
        print(f"\nWrote catalog to {json_path}")

        sha256_path = out_dir / "artifact_hashes.sha256"
        with open(sha256_path, "w", encoding="utf-8") as f:
            f.write("\n".join(sha256_lines) + "\n")
        print(f"Wrote SHA256 file to {sha256_path}")

if __name__ == "__main__":
    verify_all()

