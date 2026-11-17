"""
Stage 8.9.48: Production Freeze Hash Verification Script
Validates all 4 canonical production assets byte-for-byte against expected SHA-256 hashes.
Generates:
- backend/research/stage_8_9_48/PRODUCTION_HASH_AUDIT.md
- backend/research/stage_8_9_48/reports/PRODUCTION_HASH_AUDIT.md
"""
import hashlib
import sys
from pathlib import Path

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE48_DIR = BACKEND_DIR / "research" / "stage_8_9_48"
REPORTS_DIR = STAGE48_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HASHES = {
    "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
}

def verify_hashes(stage_label="PRE-STAGE"):
    print("=" * 80)
    print(f"PRODUCTION FREEZE VERIFICATION — {stage_label}")
    print("=" * 80)
    
    results = {}
    all_passed = True
    
    for rel_path, expected_hash in EXPECTED_HASHES.items():
        full_path = REPO_ROOT / rel_path
        if not full_path.exists():
            print(f"[FAIL] MISSING: {rel_path}")
            results[rel_path] = {"status": "MISSING", "actual": None, "expected": expected_hash}
            all_passed = False
            continue
        
        actual_hash = hashlib.sha256(full_path.read_bytes()).hexdigest()
        is_match = (actual_hash == expected_hash)
        status = "MATCH" if is_match else "MISMATCH"
        if not is_match:
            all_passed = False
        
        print(f"[{status}] {rel_path}")
        print(f"  Expected: {expected_hash}")
        print(f"  Actual:   {actual_hash}")
        results[rel_path] = {"status": status, "actual": actual_hash, "expected": expected_hash}

    status_str = "VERIFIED PASS (ALL HASHES MATCH EXACTLY)" if all_passed else "INTEGRITY BREACH / MISMATCH DETECTED"

    report_lines = [
        f"# Production Freeze Hash Audit — Stage 8.9.48 ({stage_label})",
        "",
        "> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  ",
        "> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  ",
        "> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.",
        "",
        "---",
        "",
        "## 1. Executive Summary",
        "",
        "This audit verifies that the frozen production model (Stage 5 Logistic Regression, threshold `0.3500`) and its associated evaluation artifacts remain completely unmodified and byte-identical before and throughout Stage 8.9.48.",
        "",
        f"- **Audit Status:** **{status_str}**",
        "- **Production Architecture:** Logistic Regression on 1024-dim YAMNet Embeddings",
        "- **Production Threshold:** `0.3500` (FROZEN)",
        "",
        "---",
        "",
        "## 2. Canonical Hash Verification Table",
        "",
        "| Production Artifact | Expected Canonical SHA-256 | Actual Observed SHA-256 | Status |",
        "| :--- | :--- | :--- | :---: |",
        f"| `backend/models/scream_classifier.joblib` | `{EXPECTED_HASHES['backend/models/scream_classifier.joblib']}` | `{results['backend/models/scream_classifier.joblib']['actual']}` | **{results['backend/models/scream_classifier.joblib']['status']}** |",
        f"| `backend/models/model_metadata.json` | `{EXPECTED_HASHES['backend/models/model_metadata.json']}` | `{results['backend/models/model_metadata.json']['actual']}` | **{results['backend/models/model_metadata.json']['status']}** |",
        f"| `backend/reports/test_predictions.csv` | `{EXPECTED_HASHES['backend/reports/test_predictions.csv']}` | `{results['backend/reports/test_predictions.csv']['actual']}` | **{results['backend/reports/test_predictions.csv']['status']}** |",
        f"| `backend/reports/stage5_test_evaluation.md` | `{EXPECTED_HASHES['backend/reports/stage5_test_evaluation.md']}` | `{results['backend/reports/stage5_test_evaluation.md']['actual']}` | **{results['backend/reports/stage5_test_evaluation.md']['status']}** |",
        "",
        "---",
        "",
        "## 3. Immutability Protocol & Boundary Guarantees",
        "",
        "1. **Isolation of Research Checkpoints:** All Stage 8.9.47 and Stage 8.9.48 checkpoints, calibrators, and analysis records reside strictly under `backend/research/` and do not touch `backend/models/`.",
        "2. **Threshold Segregation:** The production operating threshold remains fixed at `0.3500`. Research candidate thresholds (Candidate B: 0.8000, Candidate R5: 0.8700) are isolated within research configuration manifests.",
        "3. **Emergency Brake:** Any modification to canonical production files halts execution immediately."
    ]
    
    report_text = "\n".join(report_lines) + "\n"
    out_file1 = STAGE48_DIR / "PRODUCTION_HASH_AUDIT.md"
    out_file2 = REPORTS_DIR / "PRODUCTION_HASH_AUDIT.md"
    out_file1.write_text(report_text, encoding="utf-8")
    out_file2.write_text(report_text, encoding="utf-8")
    print(f"\nAudit report successfully written to: {out_file1}")
    
    if not all_passed:
        print("\nERROR: Production hash mismatch. Stage execution halted.")
        sys.exit(1)
    else:
        print("\nSUCCESS: All production hashes verified.")

if __name__ == "__main__":
    verify_hashes("PRE-STAGE")

