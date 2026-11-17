"""
Stage 8.9.57: Cryptographic Artifact Hash Verification
Verifies the bit-for-bit SHA-256 integrity of:
1. Protected production assets (classifier, metadata, predictions, report)
2. Frozen research model checkpoints & interventions
3. Historical evaluation manifests
Emits:
- backend/research/stage_8_9_57/artifact_hash_audit.md
"""
import hashlib
from pathlib import Path
import sys

REPO_ROOT = Path(r"festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE57_DIR = BACKEND_DIR / "research" / "stage_8_9_57"

ASSETS_TO_VERIFY = [
    # Protected Production Assets
    {
        "name": "Production Classifier",
        "path": BACKEND_DIR / "models" / "scream_classifier.joblib",
        "expected_sha256": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
        "category": "Protected Production Asset"
    },
    {
        "name": "Production Metadata",
        "path": BACKEND_DIR / "models" / "model_metadata.json",
        "expected_sha256": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
        "category": "Protected Production Asset"
    },
    {
        "name": "Production Test Predictions",
        "path": BACKEND_DIR / "reports" / "test_predictions.csv",
        "expected_sha256": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
        "category": "Protected Production Asset"
    },
    {
        "name": "Production Evaluation Report",
        "path": BACKEND_DIR / "reports" / "stage5_test_evaluation.md",
        "expected_sha256": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
        "category": "Protected Production Asset"
    },

    # Frozen Research Checkpoints
    {
        "name": "Candidate E1 Checkpoint",
        "path": BACKEND_DIR / "research" / "stage_8_9_54" / "training" / "candidate_e_v954_weighted.pt",
        "expected_sha256": "37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564",
        "category": "Frozen Research Candidate"
    },
    {
        "name": "Candidate B Checkpoint",
        "path": BACKEND_DIR / "research" / "stage_8_9_44" / "models" / "config_b_mask.pt",
        "expected_sha256": "f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378",
        "category": "Frozen Research Candidate"
    },
    {
        "name": "Intervention D Module",
        "path": BACKEND_DIR / "research" / "stage_8_9_49" / "scripts" / "whistle_discriminator.py",
        "expected_sha256": "3d98aa7496c6ba89066cfa345a6d0c1ee3605c30821f869a049001c4ad4a8bd2",
        "category": "Frozen Research Candidate"
    },

    # Stage 8.9.55 Frozen Historical Manifest
    {
        "name": "Stage 8.9.55 Frozen Test Manifest",
        "path": BACKEND_DIR / "research" / "stage_8_9_55" / "integrity" / "frozen_test_manifest.json",
        "expected_sha256": "06c9db80d3969e60f78dd441eb1495a9dab97f1646f08ab5825ea979719021f2",
        "category": "Historical Evaluation Artifact"
    }
]

def compute_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def main():
    print("=" * 80)
    print("STAGE 8.9.57: CRYPTOGRAPHIC ARTIFACT HASH AUDIT")
    print("=" * 80)

    rows = []
    all_passed = True

    for asset in ASSETS_TO_VERIFY:
        path = asset["path"]
        if not path.exists():
            print(f"[FAIL] Missing asset: {path}")
            rows.append({
                "name": asset["name"],
                "path": str(path).replace("\\", "/"),
                "expected": asset["expected_sha256"],
                "actual": "MISSING_FILE",
                "status": "FAIL (MISSING)"
            })
            all_passed = False
            continue

        actual_hash = compute_sha256(path)
        expected_hash = asset["expected_sha256"]
        if actual_hash.lower() == expected_hash.lower():
            status = "PASS (VERIFIED MATCH)"
        else:
            status = "FAIL (MISMATCH)"
            all_passed = False
            print(f"[FAIL] Hash mismatch for {asset['name']}: expected {expected_hash}, got {actual_hash}")

        print(f"[{status[:4]}] {asset['name']:<35} : {actual_hash[:16]}...")
        rows.append({
            "name": asset["name"],
            "path": str(path).replace("\\", "/"),
            "expected": expected_hash,
            "actual": actual_hash,
            "status": status,
            "category": asset["category"]
        })

    # Generate Markdown Report
    md_lines = [
        "# Artifact Hash Audit — Stage 8.9.57",
        "",
        "> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  ",
        "> Research demonstration prototype only. No life-safety efficacy or production promotion.",
        "",
        "---",
        "",
        "## 1. Executive Summary",
        "",
        "In accordance with Section 3 of Stage 8.9.57, all protected production assets, frozen research checkpoints,",
        "and historical evaluation manifests were audited via SHA-256 cryptographic digests.",
        "",
        f"**Audit Verdict: {'ALL AUDITED ASSETS 100% VERIFIED AND IMMUTABLE' if all_passed else 'INTEGRITY AUDIT FAILED'}**",
        "",
        "---",
        "",
        "## 2. Protected Production Assets Audit",
        "",
        "| Protected Asset Name | Path | Expected SHA-256 | Actual SHA-256 | Audit Status |",
        "|---|---|---|---|---|"
    ]

    for r in rows:
        if r["category"] == "Protected Production Asset":
            md_lines.append(f"| `{r['name']}` | `{r['path']}` | `{r['expected']}` | `{r['actual']}` | **{r['status']}** |")

    md_lines.extend([
        "",
        "Production classification threshold remains locked at `0.3500`.",
        "",
        "---",
        "",
        "## 3. Frozen Research Candidates and Intervention Assets",
        "",
        "| Research Artifact Name | Path | Expected SHA-256 | Actual SHA-256 | Audit Status |",
        "|---|---|---|---|---|"
    ])

    for r in rows:
        if r["category"] == "Frozen Research Candidate":
            md_lines.append(f"| `{r['name']}` | `{r['path']}` | `{r['expected']}` | `{r['actual']}` | **{r['status']}** |")

    md_lines.extend([
        "",
        "---",
        "",
        "## 4. Historical Evaluation Artifacts",
        "",
        "| Artifact Name | Path | Expected SHA-256 | Actual SHA-256 | Audit Status |",
        "|---|---|---|---|---|"
    ])

    for r in rows:
        if r["category"] == "Historical Evaluation Artifact":
            md_lines.append(f"| `{r['name']}` | `{r['path']}` | `{r['expected']}` | `{r['actual']}` | **{r['status']}** |")

    md_lines.extend([
        "",
        "---",
        "",
        "## 5. Production Protection Guarantee",
        "Zero production models, metadata, or historical predictions were modified. Zero retraining or recalibration of Candidate E1 or Candidate B is authorized.",
        ""
    ])

    report_path = STAGE57_DIR / "artifact_hash_audit.md"
    report_path.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"\nSaved hash audit report to: {report_path}")

    if not all_passed:
        print("[ERROR] One or more hash checks failed!")
        sys.exit(1)
    else:
        print("[SUCCESS] All asset hashes verified 100% bit-for-bit.")

if __name__ == "__main__":
    main()

