"""
Stage 8.9.43: Production Freeze Verification Script
Checks SHA-256 hashes of the four canonical production files against the required golden hashes.
"""
import hashlib
from pathlib import Path

BACKEND_DIR = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector\backend")

EXPECTED = {
    BACKEND_DIR / "models" / "scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    BACKEND_DIR / "models" / "model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    BACKEND_DIR / "reports" / "test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    BACKEND_DIR / "reports" / "stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
}

def verify():
    print("=" * 80)
    print("STAGE 8.9.43: VERIFYING PRODUCTION FREEZE HASHES")
    print("=" * 80)
    all_ok = True
    for p, exp_hash in EXPECTED.items():
        if not p.exists():
            print(f"FAILED: {p.name} does not exist!")
            all_ok = False
            continue
        act_hash = hashlib.sha256(p.read_bytes()).hexdigest()
        if act_hash == exp_hash:
            print(f"PASS: {p.name} matches canonical hash: {act_hash}")
        else:
            print(f"FAIL: {p.name} MISMATCH! Expected {exp_hash}, got {act_hash}")
            all_ok = False
    if all_ok:
        print("\nALL PRODUCTION FREEZE INVARIANTS INTACT. PRODUCTION SYSTEM UNMODIFIED.")
    else:
        print("\nCRITICAL FAILURE: PRODUCTION SYSTEM WAS MODIFIED!")
        exit(1)

if __name__ == "__main__":
    verify()

