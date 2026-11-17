"""
Stage 8.9.42: Production Freeze Verification Script
Checks the 4 mandatory production artifacts against their canonical SHA-256 hashes.
"""
import sys
import hashlib
from pathlib import Path

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"

EXPECTED_HASHES = {
    BACKEND_DIR / "models" / "scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    BACKEND_DIR / "models" / "model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    BACKEND_DIR / "reports" / "test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    BACKEND_DIR / "reports" / "stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
}

def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def main():
    print("=" * 80)
    print("STAGE 8.9.42: PRODUCTION FREEZE VERIFICATION")
    print("=" * 80)
    all_match = True

    for p, expected in EXPECTED_HASHES.items():
        if not p.exists():
            print(f"[MISSING] {p}")
            all_match = False
            continue
        actual = compute_sha256(p)
        match = (actual == expected)
        status = "MATCH" if match else "MISMATCH"
        print(f"[{status}] {p.name}")
        print(f"  Actual:   {actual}")
        print(f"  Expected: {expected}")
        if not match:
            all_match = False

    print("=" * 80)
    if all_match:
        print("ALL 4 PRODUCTION ARTIFACT HASHES VERIFIED: STRICT PRODUCTION FREEZE INTACT.")
        sys.exit(0)
    else:
        print("CRITICAL ALERT: PRODUCTION ARTIFACT HASH MISMATCH DETECTED!")
        sys.exit(1)

if __name__ == "__main__":
    main()

