import hashlib
import json
import os
import sys

# MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

EXPECTED_HASHES = {
    "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
    "backend/research/stage_8_9_54/training/candidate_e_v954_weighted.pt": "37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564",
    "backend/research/stage_8_9_44/models/config_b_mask.pt": "f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378",
    "backend/research/stage_8_9_49/scripts/whistle_discriminator.py": "3d98aa7496c6ba89066cfa345a6d0c1ee3605c30821f869a049001c4ad4a8bd2",
    "backend/research/stage_8_9_57/dsp_implementations/c5_combined.py": "d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58",
    "backend/research/stage_8_9_57/scripts/benchmark_original_dsp.py": "192e928c6ea427737ef8a3ec4449c890c1d41f01d71c80cefde3f2a0363f5905",
    "backend/research/stage_8_9_55/integrity/frozen_test_manifest.json": "06c9db80d3969e60f78dd441eb1495a9dab97f1646f08ab5825ea979719021f2",
    "backend/research/stage_8_9_54/dataset/partition_manifest_verified.csv": "10563efcd5d607d1395f9db5ab1aa805a0d9ca39b9b4a64a710816d334caeb9e"
}

def compute_sha256(filepath):
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()

def main():
    print("Executing Stage 8.9.60 Artifact Hash Audit...")
    results = {}
    all_matched = True

    for rel_path, expected in EXPECTED_HASHES.items():
        abs_path = os.path.join(REPO_ROOT, rel_path)
        if not os.path.exists(abs_path):
            print(f"[ERROR] Missing file: {rel_path}")
            results[rel_path] = {"status": "MISSING", "expected": expected, "actual": None}
            all_matched = False
            continue
        
        actual = compute_sha256(abs_path)
        match = (actual.lower() == expected.lower())
        if not match:
            all_matched = False
            print(f"[FAIL] {rel_path}\n  Expected: {expected}\n  Actual:   {actual}")
        else:
            print(f"[PASS] {rel_path}: {actual[:16]}... Match")
        
        results[rel_path] = {
            "status": "MATCH" if match else "MISMATCH",
            "expected": expected,
            "actual": actual
        }

    out_json = os.path.join(REPO_ROOT, "backend/research/stage_8_9_60/artifact_hashes.json")
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved artifact hashes to {out_json}")

    if not all_matched:
        print("[FATAL] Hash mismatch detected! Aborting.")
        sys.exit(1)
    else:
        print("[SUCCESS] All protected production and research assets match bit-for-bit!")

if __name__ == "__main__":
    main()

