"""
Stage 8.9.45: Extract YAMNet and Subband Features for Optimized Augmented Cohorts
Extracts features for all 2,005 augmented positive audio clips (401 clips x 5 conditions: C, D, E, F, G).
Must be run via Python 3.11 (backend/.venv/Scripts/python.exe).
Saves to backend/research/stage_8_9_45/features/augmented_features_v7.npz.

MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
import os
import sys
import time
import csv
from pathlib import Path
import numpy as np
import soundfile as sf
import scipy.signal as signal

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from src.audio.preprocessor import load_audio
from src.config import TARGET_SAMPLE_RATE
from src.model.yamnet_loader import YAMNetLoader

STAGE45_DIR = BACKEND_DIR / "research" / "stage_8_9_45"
OUT_NPZ = STAGE45_DIR / "features" / "augmented_features_v7.npz"

VOCAL_CLASS_INDICES = [0, 1, 2, 3, 6, 7, 8, 13, 14, 16, 17]
CROWD_CLASS_INDICES = [67, 68, 69]
SCREAM_CLASS_INDEX = 6

BANDS = [
    ("Band1_300_800Hz", 300, 800),
    ("Band2_800_1500Hz", 800, 1500),
    ("Band3_1500_2000Hz", 1500, 2000),
    ("Band4_2000_3000Hz", 2000, 3000),
    ("Band5_3000_4000Hz", 3000, 4000),
    ("Band6_4000_6000Hz", 4000, 6000)
]

def extract_subband_vector(audio, sr=16000):
    nyq = sr / 2.0
    total_energy = np.sum(audio ** 2) + 1e-9
    band_energies = []
    temp_vars = []
    
    for b_name, f_low, f_high in BANDS:
        low_norm = f_low / nyq
        high_norm = min(0.999, f_high / nyq)
        b, a = signal.butter(4, [low_norm, high_norm], btype='band')
        filtered = signal.filtfilt(b, a, audio)
        
        band_energy = float(np.sum(filtered ** 2))
        band_energies.append(band_energy)
        
        hop = int(0.010 * sr)
        frame = int(0.025 * sr)
        n_frames = max(1, (len(filtered) - frame) // hop + 1)
        frame_rms = [np.sqrt(np.mean(filtered[i*hop:i*hop+frame]**2) + 1e-9) for i in range(n_frames)]
        energy_std = float(np.std(frame_rms))
        energy_mean = float(np.mean(frame_rms))
        temp_var = energy_std / (energy_mean + 1e-9)
        temp_vars.append(temp_var)
        
    rel_energies = [be / total_energy for be in band_energies]
    low_e = band_energies[0] + band_energies[1] + 1e-9
    scream_band_e = band_energies[3] + band_energies[4] + 1e-9
    scream_band_to_vocal_ratio = float(scream_band_e / low_e)
    high_band_whistle_ratio = float(band_energies[5] / total_energy)
    
    vec = [
        float(rel_energies[0]),
        float(rel_energies[1]),
        float(rel_energies[2]),
        float(rel_energies[3]),
        float(rel_energies[4]),
        float(rel_energies[5]),
        float(temp_vars[0]),
        float(temp_vars[3]),
        float(temp_vars[4]),
        scream_band_to_vocal_ratio,
        high_band_whistle_ratio
    ]
    return np.array(vec, dtype=np.float32)

def main():
    print("=" * 80)
    print("STAGE 8.9.45: EXTRACTING YAMNET FEATURES FOR OPTIMIZED AUGMENTED COHORTS")
    print("=" * 80)
    t0 = time.time()

    yamnet = YAMNetLoader()
    yamnet.load()

    aug_conditions = ["c", "d", "e", "f", "g"]
    all_fids = []
    all_orig_fids = []
    all_sgs = []
    all_conds = []

    X_sem_list = []
    X_acoust_list = []
    mask_acoust_list = []
    X_subband_list = []

    for c in aug_conditions:
        manifest_p = STAGE45_DIR / "augmentation" / f"augmented_manifest_condition_{c}.csv"
        with open(manifest_p, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        print(f"\nProcessing Condition {c.upper()} ({len(rows)} clips)...")

        for idx, r in enumerate(rows):
            fid = r["augmented_file_id"]
            orig_fid = r["original_file_id"]
            sg = r["source_group_id"]
            audio_p = REPO_ROOT / r["audio_path"]

            wf, sr = load_audio(audio_p, target_sr=TARGET_SAMPLE_RATE)
            preds, embs, _ = yamnet.infer(wf)

            f_sem = np.mean(embs, axis=0).astype(np.float32)

            vocal_frames = np.max(preds[:, VOCAL_CLASS_INDICES], axis=1)
            crowd_frames = np.max(preds[:, CROWD_CLASS_INDICES], axis=1)
            scream_frames = preds[:, SCREAM_CLASS_INDEX]

            f_ac = np.array([
                float(np.max(vocal_frames)),
                float(np.mean(vocal_frames)),
                float(np.max(crowd_frames)),
                float(np.mean(crowd_frames)),
                float(np.max(scream_frames)),
                float(np.mean(scream_frames)),
            ], dtype=np.float32)

            m_ac = (~np.isnan(f_ac) & (f_ac > 0.0)).astype(np.float32)
            f_sb = extract_subband_vector(wf, sr=TARGET_SAMPLE_RATE)

            all_fids.append(fid)
            all_orig_fids.append(orig_fid)
            all_sgs.append(sg)
            all_conds.append(c.upper())

            X_sem_list.append(f_sem)
            X_acoust_list.append(f_ac)
            mask_acoust_list.append(m_ac)
            X_subband_list.append(f_sb)

            if (idx + 1) % 100 == 0 or (idx + 1) == len(rows):
                print(f"  Condition {c.upper()}: Processed {idx + 1}/{len(rows)} clips ({time.time() - t0:.1f}s elapsed)...")

    OUT_NPZ.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        OUT_NPZ,
        file_ids=np.array(all_fids),
        original_file_ids=np.array(all_orig_fids),
        source_groups=np.array(all_sgs),
        conditions=np.array(all_conds),
        X_sem=np.array(X_sem_list, dtype=np.float32),
        X_acoust=np.array(X_acoust_list, dtype=np.float32),
        mask_acoust=np.array(mask_acoust_list, dtype=np.float32),
        X_subband=np.array(X_subband_list, dtype=np.float32)
    )
    sz_mb = OUT_NPZ.stat().st_size / (1024 * 1024)
    print(f"\nSaved Augmented Features Cache: {OUT_NPZ} ({sz_mb:.2f} MB, {len(all_fids)} clips in {time.time() - t0:.1f}s)")

if __name__ == "__main__":
    main()

