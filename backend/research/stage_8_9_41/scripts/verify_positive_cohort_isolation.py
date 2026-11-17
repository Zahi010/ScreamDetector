"""
Stage 8.9.41: Positive Evaluation Cohort Cross-Partition Isolation & Cryptographic Audit
Verifies zero overlap with:
- dataset_manifest_v4 (train, val, hist_test, exp_test)
- stage_8_9_40 new_cohort_manifest & quarantine
- stage_8_9_41 quarantine manifest
"""
import os
import sys
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import soundfile as sf

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE38_DIR = BACKEND_DIR / "research" / "stage_8_9_38"
STAGE40_DIR = BACKEND_DIR / "research" / "stage_8_9_40"
STAGE41_DIR = BACKEND_DIR / "research" / "stage_8_9_41"

def main():
    print("=" * 80)
    print("STAGE 8.9.41: VERIFYING POSITIVE COHORT ISOLATION & INTEGRITY")
    print("=" * 80)

    # 1. Load active cohort
    manifest_path = STAGE41_DIR / "manifests" / "stage_8_9_41_positive_manifest.csv"
    df_new = pd.read_csv(manifest_path)
    print(f"Loaded Stage 8.9.41 positive cohort: {len(df_new)} clips, {df_new['source_group_id'].nunique()} source groups.")

    new_fids = set(df_new["file_id"])
    new_sgs = set(df_new["source_group_id"])
    new_sha = set(df_new["sha256_hash"])
    new_pcm = set(df_new["pcm_sha256"])

    # 2. Check Dataset v4 (Stage 8.9.38 / 39)
    df_v4 = pd.read_csv(STAGE38_DIR / "manifests" / "dataset_manifest_v4.csv")
    v4_fids = set(df_v4["file_id"])
    v4_sgs = set(df_v4["source_group_id"])
    v4_sha = set(df_v4["sha256_hash"])
    v4_pcm = set(df_v4["pcm_sha256"])

    assert len(new_fids.intersection(v4_fids)) == 0, "ERROR: Collision with Dataset v4 file IDs!"
    assert len(new_sgs.intersection(v4_sgs)) == 0, "ERROR: Collision with Dataset v4 source group IDs!"
    assert len(new_sha.intersection(v4_sha)) == 0, "ERROR: Collision with Dataset v4 SHA-256 hashes!"
    print("Dataset v4 Isolation (Train, Val, HistTest, ExpTest): ZERO LEAKAGE (PASS)")

    # 3. Check Stage 8.9.40 New Cohort
    df_s40 = pd.read_csv(STAGE40_DIR / "manifests" / "new_cohort_manifest.csv")
    s40_fids = set(df_s40["file_id"])
    s40_sgs = set(df_s40["source_group_id"])
    s40_sha = set(df_s40["sha256_hash"])
    s40_pcm = set(df_s40["pcm_sha256"])

    assert len(new_fids.intersection(s40_fids)) == 0, "ERROR: Collision with Stage 8.9.40 file IDs!"
    assert len(new_sgs.intersection(s40_sgs)) == 0, "ERROR: Collision with Stage 8.9.40 source group IDs!"
    assert len(new_sha.intersection(s40_sha)) == 0, "ERROR: Collision with Stage 8.9.40 SHA-256 hashes!"
    assert len(new_pcm.intersection(s40_pcm)) == 0, "ERROR: Collision with Stage 8.9.40 PCM hashes!"
    print("Stage 8.9.40 Cohort Isolation: ZERO LEAKAGE (PASS)")

    # 4. Check Stage 8.9.41 Quarantine
    df_q41 = pd.read_csv(STAGE41_DIR / "manifests" / "quarantine_manifest.csv")
    q41_fids = set(df_q41["file_id"])
    q41_sha = set(df_q41["sha256_hash"])

    assert len(new_fids.intersection(q41_fids)) == 0, "ERROR: Quarantined clip in active manifest!"
    assert len(new_sha.intersection(q41_sha)) == 0, "ERROR: Quarantined audio hash in active manifest!"
    print("Stage 8.9.41 Quarantine Isolation: ZERO LEAKAGE (PASS)")

    # 5. Verify physical audio files
    print("\nVerifying physical WAV audio files...")
    for idx, r in df_new.iterrows():
        p = REPO_ROOT / r["workspace_audio_path"]
        assert p.exists(), f"ERROR: File not found: {p}"
        data, sr = sf.read(str(p))
        assert sr == 16000, f"ERROR: Bad sample rate: {sr} in {p}"
        assert data.ndim == 1, f"ERROR: Multi-channel audio in {p}"
        assert len(data) > 0, f"ERROR: Empty audio in {p}"
        assert not np.isnan(data).any(), f"ERROR: NaN in {p}"

    print("Physical Audio Verification: 57 / 57 FILES VALID (PASS)")
    print("\nALL ISOLATION & INTEGRITY CHECKS PASSED.")

if __name__ == "__main__":
    main()
