"""
Stage 8.9.44: Production Freeze Verification Script
Checks the SHA-256 hashes of the 4 canonical production artifacts against the frozen baselines.

MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
import hashlib
import sys
from pathlib import Path

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"

EXPECTED_HASHES = {
    "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
}

def verify_freeze():
    print("=" * 70)
    print("STAGE 8.9.44: VERIFYING PRODUCTION FREEZE HASHES")
    print("=" * 70)
    all_match = True
    for rel_path, expected_hash in EXPECTED_HASHES.items():
        file_path = REPO_ROOT / rel_path
        if not file_path.exists():
            print(f"[FAIL] Missing file: {rel_path}")
            all_match = False
            continue
        with open(file_path, "rb") as f:
            actual_hash = hashlib.sha256(f.read()).hexdigest()
        if actual_hash == expected_hash:
            print(f"[PASS] {rel_path}: {actual_hash[:16]}... matches expected.")
        else:
            print(f"[FAIL] {rel_path} MISMATCH!")
            print(f"  Expected: {expected_hash}")
            print(f"  Actual:   {actual_hash}")
            all_match = False
    print("=" * 70)
    if all_match:
        print("PRODUCTION FREEZE VERIFIED: ALL HASHES MATCH EXACTLY.")
        return 0
    else:
        print("PRODUCTION FREEZE COMPROMISED!")
        return 1

if __name__ == "__main__":
    sys.exit(verify_freeze())

