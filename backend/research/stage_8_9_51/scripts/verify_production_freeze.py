"""
Stage 8.9.51: Production Freeze Verification Script
Verifies that canonical production artifacts and Candidate B checkpoint are bit-for-bit identical to frozen hashes.
"""
import hashlib
import sys
from pathlib import Path

REPO_ROOT = Path(r"c:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")

PRODUCTION_HASHES = {
    REPO_ROOT / "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    REPO_ROOT / "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    REPO_ROOT / "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    REPO_ROOT / "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
    REPO_ROOT / "backend/research/stage_8_9_44/models/config_b_mask.pt": "f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378"
}

def verify_freeze():
    print("=" * 80)
    print("STAGE 8.9.51: PRODUCTION & RESEARCH FREEZE VERIFICATION")
    print("=" * 80)
    mismatches = []
    for path, expected in PRODUCTION_HASHES.items():
        if not path.exists():
            print(f"[MISSING] {path.relative_to(REPO_ROOT)}")
            mismatches.append((str(path), expected, "FILE_NOT_FOUND"))
            continue
        with open(path, "rb") as f:
            actual = hashlib.sha256(f.read()).hexdigest()
        if actual == expected:
            print(f"[VERIFIED] {path.relative_to(REPO_ROOT)} -> {actual[:16]}...")
        else:
            print(f"[MISMATCH] {path.relative_to(REPO_ROOT)}")
            print(f"  Expected: {expected}")
            print(f"  Actual:   {actual}")
            mismatches.append((str(path), expected, actual))

    if mismatches:
        print(f"\nCRITICAL: {len(mismatches)} artifact(s) modified or missing!")
        return False
    else:
        print("\nALL PRODUCTION & RESEARCH CHECKPOINTS FULLY VERIFIED (100% BIT-FOR-BIT MATCH).")
        return True

if __name__ == "__main__":
    success = verify_freeze()
    sys.exit(0 if success else 1)

