#!/usr/bin/env python3
"""
STAGE 8.9.61 — Track A Experimental Candidate Freeze Script
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
Freezes experimental candidate configuration based exclusively on development data.
"""

import hashlib
import json
import os
import platform
import sys
from pathlib import Path
import torch

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE54_DIR = BACKEND_DIR / "research" / "stage_8_9_54"
STAGE44_DIR = BACKEND_DIR / "research" / "stage_8_9_44"
STAGE49_DIR = BACKEND_DIR / "research" / "stage_8_9_49"
STAGE57_DIR = BACKEND_DIR / "research" / "stage_8_9_57"
STAGE61_DIR = BACKEND_DIR / "research" / "stage_8_9_61"

def sha256_file(path_str: str) -> str:
    sha = hashlib.sha256()
    with open(path_str, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()

def main():
    print("Executing Phase A8: Track A Candidate Freeze...")
    
    # Hashes of implementation and checkpoints
    rw_script = STAGE61_DIR / "scripts" / "compare_temporal_aggregation.py"
    c5_script = STAGE57_DIR / "dsp_implementations" / "c5_combined.py"
    e1_ckpt = STAGE54_DIR / "training" / "candidate_e_v954_weighted.pt"
    b_ckpt = STAGE44_DIR / "models" / "config_b_mask.pt"
    d_code = STAGE49_DIR / "scripts" / "whistle_discriminator.py"
    dev_manifest = STAGE61_DIR / "rolling_window_development_manifest.csv"
    
    freeze_data = {
        "stage": "8.9.61",
        "phase": "TRACK_A_EXPERIMENTAL_CANDIDATE_FREEZE",
        "candidate_id": "E1_ROLLING_C5_STRATEGY_D",
        "candidate_description": "Candidate E1 Neural Classifier with Frozen C5 Combined DSP, 500ms Rolling Hop, and Exponential Moving Average Aggregation",
        "architecture_parameters": {
            "audio_window_duration_seconds": 1.0,
            "audio_window_samples": 16000,
            "hop_duration_seconds": 0.5,
            "hop_duration_samples": 8000,
            "window_overlap_ratio": 0.50,
            "sampling_rate_hz": 16000,
            "channels": "mono",
            "feature_normalization": "peak_normalization"
        },
        "temporal_aggregation_parameters": {
            "primary_strategy": "Strategy_D_Rolling_EMA",
            "alpha": 0.50,
            "decision_threshold": 0.6000,
            "baseline_e1_window_threshold": 0.6800,
            "secondary_investigated_strategies": [
                {"name": "Strategy_A_Independent", "threshold": 0.6800},
                {"name": "Strategy_B_Persistence_K2", "k": 2, "threshold": 0.6800},
                {"name": "Strategy_C_Hysteresis", "theta_high": 0.6800, "theta_low": 0.4000},
                {"name": "Strategy_E_Max_Window_W2", "w": 2, "threshold": 0.6800}
            ]
        },
        "artifact_hashes": {
            "rolling_window_inference_code_sha256": sha256_file(str(rw_script)),
            "c5_reference_dsp_sha256": sha256_file(str(c5_script)),
            "candidate_e1_checkpoint_sha256": sha256_file(str(e1_ckpt)),
            "candidate_b_checkpoint_sha256": sha256_file(str(b_ckpt)),
            "intervention_d_code_sha256": sha256_file(str(d_code)),
            "development_manifest_sha256": sha256_file(str(dev_manifest))
        },
        "benchmark_environment": {
            "os": platform.system(),
            "os_release": platform.release(),
            "python_version": sys.version.split()[0],
            "torch_version": torch.__version__,
            "psutil_available": True
        },
        "governance_rule": "FROZEN_BEFORE_TRACK_B_UNSEALING_NO_TEST_BASED_TUNING"
    }
    
    out_json = STAGE61_DIR / "rolling_window_candidate_freeze.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(freeze_data, f, indent=2)
    print(f"Saved candidate freeze to: {out_json}")
    
    freeze_sha = sha256_file(str(out_json))
    out_seal = STAGE61_DIR / "rolling_window_candidate_freeze.sha256"
    with open(out_seal, "w", encoding="utf-8") as f:
        f.write(f"{freeze_sha}  rolling_window_candidate_freeze.json\n")
    print(f"Saved candidate freeze SHA-256 seal to: {out_seal}")
    print(f"Candidate Freeze Digest: {freeze_sha}")

if __name__ == "__main__":
    main()
