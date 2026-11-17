#!/usr/bin/env python3
"""
STAGE 8.9.66 — Track G: Preregistration Compliance & Checkpoint Verification
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
This system is an experimental acoustic research prototype and is not certified for life-safety use.
"""

import hashlib
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
STAGE66_DIR = SCRIPT_DIR.parent
MODELS_DIR = STAGE66_DIR / "models"
RESEARCH_DIR = STAGE66_DIR.parent


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def verify_preregistration():
    print("=" * 80)
    print("STAGE 8.9.66 — TRACK G: PREREGISTRATION COMPLIANCE VERIFICATION")
    print("MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.")
    print("=" * 80)

    # 1. Verify frozen checkpoint
    ckpt_path = MODELS_DIR / "candidate_65f_frozen.pt"
    assert ckpt_path.exists(), f"Missing frozen checkpoint: {ckpt_path}"
    actual_hash = sha256_file(ckpt_path)
    print(f"Checkpoint Path: {ckpt_path.name}")
    print(f"Computed SHA-256: {actual_hash}")

    # 2. Verify metadata JSON
    meta_path = MODELS_DIR / "candidate_freeze_metadata.json"
    assert meta_path.exists(), f"Missing metadata JSON: {meta_path}"
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert meta["checkpoint_sha256"] == actual_hash, (
        f"Metadata hash mismatch! Expected {meta['checkpoint_sha256']} got {actual_hash}"
    )
    print("Checkpoint hash matches metadata record perfectly.")

    # 3. Verify preregistration document
    prereg_doc = STAGE66_DIR / "future_evaluation_preregistration.md"
    assert prereg_doc.exists(), f"Missing preregistration document: {prereg_doc}"
    with open(prereg_doc, "r", encoding="utf-8") as f:
        doc_text = f.read()

    assert "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE." in doc_text, "Missing safety header!"
    assert actual_hash in doc_text, "Preregistration doc does not contain frozen checkpoint hash!"
    print("Preregistration markdown document verified compliant.")

    # 4. Verify C5 DSP
    c5_path = RESEARCH_DIR / "stage_8_9_57" / "dsp_implementations" / "c5_combined.py"
    assert c5_path.exists(), f"Missing C5 DSP: {c5_path}"
    c5_hash = sha256_file(c5_path)
    expected_c5 = "d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58"
    assert c5_hash == expected_c5, f"C5 DSP hash mismatch! Got {c5_hash}"
    print("C5 DSP implementation verified intact and bit-exact.")

    print("\nALL PREREGISTRATION CHECKS PASSED: READY FOR REPRODUCIBLE INDEPENDENT TRIAL.")
    return True


if __name__ == "__main__":
    verify_preregistration()

