"""
Stage 8.9.45: Generate Optimized Augmented Audio Cohorts
Generates augmented training audio files for Conditions C, D, E, F, G from v5_train positives (N=401):
- Condition C: Mild background masking (SNRs: +9, +12, +15, +18 dB)
- Condition D: Multi-level background masking ladder (SNRs: +3, +6, +9, +12, +15, +18 dB)
- Condition E: Background masking with controlled distance attenuation (10m - 25m)
- Condition F: Background masking with conservative early-reflection RIR (T60 <= 0.3s)
- Condition G: Probabilistic mixed augmentation (50% pristine, 50% transformed)

MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
import os
import sys
import time
import csv
from pathlib import Path
import numpy as np
import soundfile as sf
import librosa

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE43_DIR = BACKEND_DIR / "research" / "stage_8_9_43"
STAGE45_DIR = BACKEND_DIR / "research" / "stage_8_9_45"

sys.path.insert(0, str(STAGE45_DIR / "scripts"))
from environmental_audio_transforms_v7 import (
    generate_conservative_early_rir,
    apply_rir_convolution,
    apply_soft_distance_attenuation,
    apply_calibrated_background_masking,
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
    print("STAGE 8.9.45: GENERATING OPTIMIZED AUGMENTED TRAINING COHORTS")
    print("=" * 80)
    t0 = time.time()
    np.random.seed(142)

    df_manifest = []
    with open(MANIFEST_P, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            df_manifest.append(r)

    train_pos = [r for r in df_manifest if r["v5_research_split"] == "v5_train" and r["binary_label"] == "1"]
    train_neg_noise = [
        r for r in df_manifest 
        if r["v5_research_split"] == "v5_train" 
        and r["binary_label"] == "0" 
        and r["target_category"] in ["crowd_chant_cheering", "general_environmental"]
    ]

    print(f"v5_train Positives: {len(train_pos)} recordings")
    print(f"v5_train Noise Pool: {len(train_neg_noise)} recordings")

    print("Loading noise pool waveforms into memory...")
    noise_pool = []
    for r in train_neg_noise:
        p = REPO_ROOT / r["workspace_audio_path"]
        if p.exists():
            wf = load_audio(p)
            noise_pool.append({"wf": wf, "file_id": r["file_id"], "cat": r["target_category"]})
    print(f"Successfully loaded {len(noise_pool)} noise waveforms.")

    dirs = {
        "C": STAGE45_DIR / "audio" / "augmented" / "condition_c_mild_mask",
        "D": STAGE45_DIR / "audio" / "augmented" / "condition_d_multisnr",
        "E": STAGE45_DIR / "audio" / "augmented" / "condition_e_mask_atten",
        "F": STAGE45_DIR / "audio" / "augmented" / "condition_f_mask_early_rir",
        "G": STAGE45_DIR / "audio" / "augmented" / "condition_g_prob_mixed",
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)

    manifest_records = {"C": [], "D": [], "E": [], "F": [], "G": []}

    mild_snrs = [9.0, 12.0, 15.0, 18.0]
    multi_snrs = [3.0, 6.0, 9.0, 12.0, 15.0, 18.0]
    distances = [10.0, 15.0, 20.0, 25.0]

    for idx, r in enumerate(train_pos):
        fid = r["file_id"]
        src_path = REPO_ROOT / r["workspace_audio_path"]
        if not src_path.exists():
            print(f"Warning: Missing source audio: {src_path}")
            continue
        wf_orig = load_audio(src_path)

        noise_idx = (idx * 7 + 3) % len(noise_pool)
        noise_sample = noise_pool[noise_idx]["wf"]

        # -------------------------------------------------------------
        # Condition C: Mild Masking (SNR +9 to +18 dB)
        # -------------------------------------------------------------
        snr_c = mild_snrs[idx % len(mild_snrs)]
        wf_c = apply_calibrated_background_masking(wf_orig, noise_sample, snr_db=snr_c, seed=100 + idx)
        out_c = dirs["C"] / f"aug_c_{fid}.wav"
        sf.write(str(out_c), wf_c, TARGET_SR)
        manifest_records["C"].append({
            "augmented_file_id": f"aug_c_{fid}",
            "original_file_id": fid,
            "source_group_id": r["source_group_id"],
            "condition": "C_MildMask",
            "snr_db": snr_c,
            "audio_path": str(out_c.relative_to(REPO_ROOT))
        })

        # -------------------------------------------------------------
        # Condition D: Multi-level SNR Ladder (+3 to +18 dB)
        # -------------------------------------------------------------
        snr_d = multi_snrs[idx % len(multi_snrs)]
        wf_d = apply_calibrated_background_masking(wf_orig, noise_sample, snr_db=snr_d, seed=200 + idx)
        out_d = dirs["D"] / f"aug_d_{fid}.wav"
        sf.write(str(out_d), wf_d, TARGET_SR)
        manifest_records["D"].append({
            "augmented_file_id": f"aug_d_{fid}",
            "original_file_id": fid,
            "source_group_id": r["source_group_id"],
            "condition": "D_MultiSNR",
            "snr_db": snr_d,
            "audio_path": str(out_d.relative_to(REPO_ROOT))
        })

        # -------------------------------------------------------------
        # Condition E: Mild Masking + Controlled Distance Attenuation
        # -------------------------------------------------------------
        dist_e = distances[idx % len(distances)]
        snr_e = mild_snrs[(idx + 1) % len(mild_snrs)]
        wf_atten = apply_soft_distance_attenuation(wf_orig, distance_m=dist_e, seed=300 + idx)
        wf_e = apply_calibrated_background_masking(wf_atten, noise_sample, snr_db=snr_e, seed=350 + idx)
        out_e = dirs["E"] / f"aug_e_{fid}.wav"
        sf.write(str(out_e), wf_e, TARGET_SR)
        manifest_records["E"].append({
            "augmented_file_id": f"aug_e_{fid}",
            "original_file_id": fid,
            "source_group_id": r["source_group_id"],
            "condition": "E_MaskAtten",
            "distance_m": dist_e,
            "snr_db": snr_e,
            "audio_path": str(out_e.relative_to(REPO_ROOT))
        })

        # -------------------------------------------------------------
        # Condition F: Mild Masking + Conservative Early RIR
        # -------------------------------------------------------------
        t60_f = 0.18 + (idx % 3) * 0.05  # 0.18s, 0.23s, 0.28s
        rir_f = generate_conservative_early_rir(t60=t60_f, drr_db=10.0, seed=400 + idx)
        wf_rir = apply_rir_convolution(wf_orig, rir_f)
        snr_f = mild_snrs[(idx + 2) % len(mild_snrs)]
        wf_f = apply_calibrated_background_masking(wf_rir, noise_sample, snr_db=snr_f, seed=450 + idx)
        out_f = dirs["F"] / f"aug_f_{fid}.wav"
        sf.write(str(out_f), wf_f, TARGET_SR)
        manifest_records["F"].append({
            "augmented_file_id": f"aug_f_{fid}",
            "original_file_id": fid,
            "source_group_id": r["source_group_id"],
            "condition": "F_MaskEarlyRIR",
            "t60_s": t60_f,
            "snr_db": snr_f,
            "audio_path": str(out_f.relative_to(REPO_ROOT))
        })

        # -------------------------------------------------------------
        # Condition G: Probabilistic Mixed Augmentation (50% pristine, 50% transformed)
        # -------------------------------------------------------------
        # Every even index: keep pristine unaugmented audio!
        # Every odd index: alternate between C, E, and F
        if idx % 2 == 0:
            wf_g = wf_orig.copy()
            cond_desc = "Pristine_Clean"
        else:
            sub_choice = (idx // 2) % 3
            if sub_choice == 0:
                wf_g = wf_c.copy()
                cond_desc = f"Transformed_MildMask_{snr_c}dB"
            elif sub_choice == 1:
                wf_g = wf_e.copy()
                cond_desc = f"Transformed_MaskAtten_{dist_e}m_{snr_e}dB"
            else:
                wf_g = wf_f.copy()
                cond_desc = f"Transformed_MaskEarlyRIR_{t60_f}s_{snr_f}dB"
        out_g = dirs["G"] / f"aug_g_{fid}.wav"
        sf.write(str(out_g), wf_g, TARGET_SR)
        manifest_records["G"].append({
            "augmented_file_id": f"aug_g_{fid}",
            "original_file_id": fid,
            "source_group_id": r["source_group_id"],
            "condition": "G_ProbMixed",
            "variant": cond_desc,
            "audio_path": str(out_g.relative_to(REPO_ROOT))
        })

    # Save manifests
    mf_dir = STAGE45_DIR / "augmentation"
    mf_dir.mkdir(parents=True, exist_ok=True)
    for cond_key, records in manifest_records.items():
        cond_csv = mf_dir / f"augmented_manifest_condition_{cond_key.lower()}.csv"
        with open(cond_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
            writer.writeheader()
            writer.writerows(records)
        print(f"Saved {len(records)} records to {cond_csv.name}")

    print(f"\nCohort Generation Complete in {time.time() - t0:.2f}s.")

if __name__ == "__main__":
    main()

