"""
Stage 8.9.44: Generate Augmented Cohorts for v5_train
Applies controlled environmental transformations to the 401 positive scream recordings in v5_train:
- Condition B: Room Impulse Response (RIR) convolution (small, medium, large, outdoor)
- Condition C: Distance attenuation & atmospheric air absorption (5m to 35m)
- Condition D: Background masking (crowd & environmental noise at SNR +3dB to +12dB)
- Condition E: Combined environmental pipeline (RIR + Attenuation + Masking)

Strictly respects:
- Applied ONLY to v5_train positives
- Noise pool sourced STRICTLY from v5_train negatives (zero partition leakage)
- Fixed random seeds for full reproducibility
"""
import os
import sys
import time
import csv
import json
from pathlib import Path
import numpy as np
import soundfile as sf
import librosa

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE43_DIR = BACKEND_DIR / "research" / "stage_8_9_43"
STAGE44_DIR = BACKEND_DIR / "research" / "stage_8_9_44"
sys.path.insert(0, str(STAGE44_DIR / "scripts"))

from environmental_audio_transforms import (
    generate_synthetic_rir,
    apply_rir_convolution,
    apply_distance_attenuation,
    apply_background_masking,
    apply_combined_environmental,
    ROOM_PROFILES,
    TARGET_SR
)

MANIFEST_P = STAGE43_DIR / "manifests" / "dataset_manifest_v5.csv"

def load_audio(p, sr=TARGET_SR):
    wf, orig_sr = sf.read(str(p), dtype="float32")
    if wf.ndim > 1:
        wf = np.mean(wf, axis=1)
    if orig_sr != sr:
        wf = librosa.resample(wf, orig_sr=orig_sr, target_sr=sr)
    max_amp = np.max(np.abs(wf))
    if max_amp > 1e-6:
        wf = wf / max_amp
    return wf

def main():
    print("=" * 80)
    print("STAGE 8.9.44: GENERATING CONTROLLED ENVIRONMENTAL AUGMENTED COHORTS")
    print("=" * 80)
    t0 = time.time()
    np.random.seed(42)

    df_manifest = []
    with open(MANIFEST_P, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            df_manifest.append(r)

    # 1. Select v5_train positives and noise pool
    train_pos = [r for r in df_manifest if r["v5_research_split"] == "v5_train" and r["binary_label"] == "1"]
    train_neg_noise = [
        r for r in df_manifest 
        if r["v5_research_split"] == "v5_train" 
        and r["binary_label"] == "0" 
        and r["target_category"] in ["crowd_chant_cheering", "general_environmental"]
    ]

    print(f"v5_train Positives: {len(train_pos)} recordings")
    print(f"v5_train Noise Pool: {len(train_neg_noise)} recordings")

    # Load noise waveforms into memory
    print("Loading noise pool waveforms...")
    noise_pool = []
    for r in train_neg_noise:
        p = REPO_ROOT / r["workspace_audio_path"]
        if p.exists():
            wf = load_audio(p)
            noise_pool.append({"wf": wf, "file_id": r["file_id"], "cat": r["target_category"]})
    print(f"Successfully loaded {len(noise_pool)} noise waveforms.")

    # Prepare output directories
    dirs = {
        "B": STAGE44_DIR / "audio" / "augmented" / "condition_b_rir",
        "C": STAGE44_DIR / "audio" / "augmented" / "condition_c_atten",
        "D": STAGE44_DIR / "audio" / "augmented" / "condition_d_mask",
        "E": STAGE44_DIR / "audio" / "augmented" / "condition_e_combined",
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)

    manifest_records = {"B": [], "C": [], "D": [], "E": []}

    room_choices = ["small_room", "medium_room", "large_hall", "outdoor_diffuse"]

    for idx, r in enumerate(train_pos):
        fid = r["file_id"]
        src_path = REPO_ROOT / r["workspace_audio_path"]
        if not src_path.exists():
            print(f"Warning: Missing source audio: {src_path}")
            continue
        wf_orig = load_audio(src_path)

        # -------------------------------------------------------------
        # Condition B: RIR Convolution
        # -------------------------------------------------------------
        r_prof = room_choices[idx % len(room_choices)]
        rir, rir_p = generate_synthetic_rir(room_profile=r_prof, seed=42 + idx)
        wf_b = apply_rir_convolution(wf_orig, rir)
        out_b = dirs["B"] / f"aug_b_{fid}.wav"
        sf.write(str(out_b), wf_b, TARGET_SR)
        manifest_records["B"].append({
            "augmented_file_id": f"aug_b_{fid}",
            "original_file_id": fid,
            "source_group_id": r["source_group_id"],
            "condition": "Condition B (RIR)",
            "room_profile": r_prof,
            "t60_seconds": rir_p["t60_seconds"],
            "drr_db": rir_p["drr_db"],
            "audio_path": str(out_b.relative_to(REPO_ROOT))
        })

        # -------------------------------------------------------------
        # Condition C: Distance Attenuation
        # -------------------------------------------------------------
        dist = 5.0 + (idx % 7) * 5.0 # 5m, 10m, 15m, 20m, 25m, 30m, 35m
        wf_c = apply_distance_attenuation(wf_orig, distance_m=dist, sr=TARGET_SR)
        out_c = dirs["C"] / f"aug_c_{fid}.wav"
        sf.write(str(out_c), wf_c, TARGET_SR)
        manifest_records["C"].append({
            "augmented_file_id": f"aug_c_{fid}",
            "original_file_id": fid,
            "source_group_id": r["source_group_id"],
            "condition": "Condition C (Attenuation)",
            "distance_meters": dist,
            "audio_path": str(out_c.relative_to(REPO_ROOT))
        })

        # -------------------------------------------------------------
        # Condition D: Background Masking
        # -------------------------------------------------------------
        bg_item = noise_pool[idx % len(noise_pool)]
        snr = 3.0 + (idx % 4) * 3.0 # +3 dB, +6 dB, +9 dB, +12 dB
        wf_d = apply_background_masking(wf_orig, bg_item["wf"], snr_db=snr)
        out_d = dirs["D"] / f"aug_d_{fid}.wav"
        sf.write(str(out_d), wf_d, TARGET_SR)
        manifest_records["D"].append({
            "augmented_file_id": f"aug_d_{fid}",
            "original_file_id": fid,
            "source_group_id": r["source_group_id"],
            "condition": "Condition D (Background Masking)",
            "noise_file_id": bg_item["file_id"],
            "noise_category": bg_item["cat"],
            "snr_db": snr,
            "audio_path": str(out_d.relative_to(REPO_ROOT))
        })

        # -------------------------------------------------------------
        # Condition E: Combined Environmental Pipeline
        # -------------------------------------------------------------
        r_prof_e = room_choices[(idx + 1) % len(room_choices)]
        dist_e = 8.0 + (idx % 5) * 4.0 # 8m, 12m, 16m, 20m, 24m
        snr_e = 3.0 + (idx % 3) * 3.0 # +3 dB, +6 dB, +9 dB
        wf_e, params_e = apply_combined_environmental(
            wf_orig, 
            background_wf=bg_item["wf"], 
            room_profile=r_prof_e, 
            distance_m=dist_e, 
            snr_db=snr_e, 
            seed=1000 + idx
        )
        out_e = dirs["E"] / f"aug_e_{fid}.wav"
        sf.write(str(out_e), wf_e, TARGET_SR)
        manifest_records["E"].append({
            "augmented_file_id": f"aug_e_{fid}",
            "original_file_id": fid,
            "source_group_id": r["source_group_id"],
            "condition": "Condition E (Combined Environmental)",
            "room_profile": r_prof_e,
            "t60_seconds": params_e["rir"]["t60_seconds"],
            "drr_db": params_e["rir"]["drr_db"],
            "distance_meters": dist_e,
            "noise_file_id": bg_item["file_id"],
            "snr_db": snr_e,
            "audio_path": str(out_e.relative_to(REPO_ROOT))
        })

        if (idx + 1) % 100 == 0 or (idx + 1) == len(train_pos):
            print(f"Processed {idx + 1}/{len(train_pos)} recordings across all 4 conditions ({time.time() - t0:.1f}s elapsed)...")

    # Save manifests
    aug_manifest_dir = STAGE44_DIR / "augmentation"
    aug_manifest_dir.mkdir(parents=True, exist_ok=True)
    for c_tag, recs in manifest_records.items():
        out_csv = aug_manifest_dir / f"augmented_manifest_condition_{c_tag.lower()}.csv"
        with open(out_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(recs[0].keys()))
            writer.writeheader()
            writer.writerows(recs)
        print(f"Saved manifest: {out_csv} ({len(recs)} records)")

    print(f"\nAll 4 augmented cohorts successfully generated in {time.time() - t0:.1f}s.")

if __name__ == "__main__":
    main()

