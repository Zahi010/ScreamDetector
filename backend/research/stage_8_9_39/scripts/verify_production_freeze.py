import hashlib
from pathlib import Path

BACKEND_DIR = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector\backend")

EXPECTED_PROD_HASHES = {
    "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
}

print("Production Freeze Audit:")
for rel_path, exp_hash in EXPECTED_PROD_HASHES.items():
    p = BACKEND_DIR.parent / rel_path
    with open(p, "rb") as f:
        actual = hashlib.sha256(f.read()).hexdigest()
    match = (actual == exp_hash)
    print(f"  {rel_path}: {'MATCH' if match else 'MISMATCH'}")
    assert match, f"MISMATCH on {rel_path}"
print("All 4 production artifacts verified 100% intact.")
