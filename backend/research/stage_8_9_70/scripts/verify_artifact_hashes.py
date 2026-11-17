# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
STAGE 8.9.70 — ARTIFACT HASH VERIFICATION SCRIPT
Computes and verifies SHA-256 integrity hashes for all Stage 8.9.70 artifacts,
checkpoints, reports, scripts, and ensures baseline production immutability.

MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
STAGE_DIR = Path(__file__).resolve().parents[1]
REPORTS_DIR = STAGE_DIR / "reports"

PROTECTED_BASELINE_HASHES = {
    "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
    "backend/research/stage_8_9_60/future_evaluation_manifest.json": "9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd",
}

HISTORICAL_CANDIDATE_HASHES = {
    "backend/research/stage_8_9_66/models/candidate_65f_frozen.pt": "06a98025dbdabf462bec305b0cfe8455dd137b3d515cafca8811606865bacfab",
    "backend/research/stage_8_9_67/models/candidate_67_frozen.pt": "8fc2255a337f1375870370216416b94d9c2003a2b8939dbee1301115f53a7b18",
    "backend/research/stage_8_9_68/models/candidate_68_frozen.pt": "8a3b425a2885cfeeb4d9e6a64c04619949978cad5b55a8a5f60b5ee379949dc4",
    "backend/research/stage_8_9_69/models/candidate_69_frozen.pt": "d468b75ab12d5ef2b8577c18304e8c4ddaf78f3059b2c0395a1a3263ac6dd92c",
}

def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def verify_all():
    print("=" * 80)
    print("STAGE 8.9.70 ARTIFACT HASH VERIFICATION")
    print("=" * 80)

    # 1. Verify Protected Baseline Files
    print("\n1. Verifying Protected Baseline Files (Immutability Check):")
    for rel_path, expected_hash in PROTECTED_BASELINE_HASHES.items():
        full_path = REPO_ROOT / rel_path
        if not full_path.exists():
            raise FileNotFoundError(f"Protected file missing: {full_path}")
        actual_hash = compute_sha256(full_path)
        assert actual_hash == expected_hash, f"CORRUPTION DETECTED in {rel_path}!"
        print(f"  [OK] {rel_path}: {actual_hash[:16]}... matches expected.")

    # 2. Verify Historical Checkpoints
    print("\n2. Verifying Historical Checkpoints:")
    for rel_path, expected_hash in HISTORICAL_CANDIDATE_HASHES.items():
        full_path = REPO_ROOT / rel_path
        if not full_path.exists():
            print(f"  [WARN] Checkpoint not present: {rel_path}")
            continue
        actual_hash = compute_sha256(full_path)
        assert actual_hash == expected_hash, f"Checkpoint hash mismatch in {rel_path}!"
        print(f"  [OK] {rel_path}: {actual_hash[:16]}... matches expected.")

    # 3. Compute and Record Hashes for all Stage 70 Artifacts
    print("\n3. Cataloging Stage 8.9.70 Artifact Hashes:")
    stage70_hashes = {}
    sha256_lines = []

    # Models
    models_dir = STAGE_DIR / "models"
    for p in sorted(models_dir.glob("*")):
        if p.is_file():
            rel_str = str(p.relative_to(REPO_ROOT)).replace("\\", "/")
            h = compute_sha256(p)
            stage70_hashes[rel_str] = h
            sha256_lines.append(f"{h}  {rel_str}")
            print(f"  [MODEL] {p.name}: {h}")

    # Reports
    for p in sorted(REPORTS_DIR.glob("*")):
        if p.is_file() and p.name not in ["artifact_hashes.json", "artifact_hashes.sha256"]:
            rel_str = str(p.relative_to(REPO_ROOT)).replace("\\", "/")
            h = compute_sha256(p)
            stage70_hashes[rel_str] = h
            sha256_lines.append(f"{h}  {rel_str}")
            print(f"  [REPORT] {p.name}: {h}")

    # Scripts
    scripts_dir = STAGE_DIR / "scripts"
    for p in sorted(scripts_dir.glob("*.py")):
        if p.is_file():
            rel_str = str(p.relative_to(REPO_ROOT)).replace("\\", "/")
            h = compute_sha256(p)
            stage70_hashes[rel_str] = h
            sha256_lines.append(f"{h}  {rel_str}")
            print(f"  [SCRIPT] {p.name}: {h}")

    # Tests
    tests_dir = STAGE_DIR / "tests"
    for p in sorted(tests_dir.glob("*.py")):
        if p.is_file():
            rel_str = str(p.relative_to(REPO_ROOT)).replace("\\", "/")
            h = compute_sha256(p)
            stage70_hashes[rel_str] = h
            sha256_lines.append(f"{h}  {rel_str}")
            print(f"  [TEST] {p.name}: {h}")

    # Save to JSON and sha256
    json_path = REPORTS_DIR / "artifact_hashes.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(stage70_hashes, f, indent=2)
    print(f"\nWrote catalog to {json_path}")

    sha256_path = REPORTS_DIR / "artifact_hashes.sha256"
    with open(sha256_path, "w", encoding="utf-8") as f:
        f.write("\n".join(sha256_lines) + "\n")
    print(f"Wrote SHA256 file to {sha256_path}")

if __name__ == "__main__":
    verify_all()

