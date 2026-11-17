"""
Stage 8.9.49: Pre-Stage & Post-Stage Production Freeze Verification Script
Verifies that the canonical production assets are 100% byte-for-byte identical to their frozen hashes.
"""
import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE_DIR = BACKEND_DIR / "research" / "stage_8_9_49"

CANONICAL_HASHES = {
    "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
}

def verify_production_freeze(stage_name="PRE-STAGE"):
    print("=" * 80)
    print(f"PRODUCTION FREEZE VERIFICATION — {stage_name}")
    print("=" * 80)
    all_ok = True
    audit_lines = [
        f"# Production Freeze Audit Report — Stage 8.9.49 ({stage_name})",
        "",
        "> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  ",
        "> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  ",
        "> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.",
        "",
        "---",
        "",
        "## Production Asset Verification Summary",
        "",
        "| Production Asset | Expected SHA-256 | Actual SHA-256 | Status |",
        "| :--- | :--- | :--- | :---: |"
    ]
    
    for rel_path, expected_hash in CANONICAL_HASHES.items():
        full_path = REPO_ROOT / rel_path
        if not full_path.exists():
            print(f"[MISSING] {rel_path}")
            audit_lines.append(f"| `{rel_path}` | `{expected_hash}` | `FILE NOT FOUND` | **FAILED** |")
            all_ok = False
            continue
        with open(full_path, "rb") as f:
            actual_hash = hashlib.sha256(f.read()).hexdigest()
        if actual_hash == expected_hash:
            print(f"[MATCH] {rel_path}")
            print(f"  Expected: {expected_hash}")
            print(f"  Actual:   {actual_hash}")
            audit_lines.append(f"| `{rel_path}` | `{expected_hash}` | `{actual_hash}` | **MATCH** |")
        else:
            print(f"[MISMATCH] {rel_path}")
            print(f"  Expected: {expected_hash}")
            print(f"  Actual:   {actual_hash}")
            audit_lines.append(f"| `{rel_path}` | `{expected_hash}` | `{actual_hash}` | **MISMATCH** |")
            all_ok = False
            
    audit_lines.extend([
        "",
        "---",
        "",
        "## Production Integrity Constraints",
        "- **Production Model:** Frozen at Stage 5 Logistic Regression (`scream_classifier.joblib`).",
        "- **Production Operating Threshold:** Locked at `0.3500`.",
        "- **Candidate B Role:** Experimental research candidate only; not deployed or active in production.",
        "- **Whistle Discrimination Interventions:** Experimental research filters only; isolated from production inference.",
        f"- **Verification Outcome:** {'SUCCESS: 100% byte-for-byte immutability confirmed.' if all_ok else 'CRITICAL FAILURE: Production files modified or missing.'}"
    ])
    
    out_path = STAGE_DIR / "PRODUCTION_HASH_AUDIT.md"
    rep_path = STAGE_DIR / "reports" / "PRODUCTION_HASH_AUDIT.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(audit_lines) + "\n")
    with open(rep_path, "w", encoding="utf-8") as f:
        f.write("\n".join(audit_lines) + "\n")
        
    print(f"\nAudit report successfully written to: {out_path}")
    if not all_ok:
        raise RuntimeError("Production freeze check failed!")
    print("\nSUCCESS: All production hashes verified.")

if __name__ == "__main__":
    verify_production_freeze("PRE-STAGE")

