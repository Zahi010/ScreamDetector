"""
Stage 8.9.43: Extract YAMNet and Subband Features for Dataset Manifest v5
Reuses existing caches:
- stage_8_9_39_features.npz (1,578 historical clips)
- new_cohort_features.npz (145 independent negatives from Stage 8.9.40)
Freshly extracts remaining 191 authentic positive scream clips via YAMNetLoader and subband filters.
Saves unified cache to:
backend/research/stage_8_9_43/features/yamnet_v5_cache.npz
Must be executed with backend/.venv/Scripts/python.exe (Python 3.11 with TF & YAMNet).
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

STAGE43_DIR = BACKEND_DIR / "research" / "stage_8_9_43"
MANIFEST_P = STAGE43_DIR / "manifests" / "dataset_manifest_v5.csv"
OUT_NPZ = STAGE43_DIR / "features" / "yamnet_v5_cache.npz"

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
    print("STAGE 8.9.43: EXTRACTING YAMNET & SUBBAND FEATURES FOR MANIFEST V5")
    print("=" * 80)
    t0 = time.time()

    # Load caches
    cache39_p = BACKEND_DIR / "research" / "stage_8_9_39" / "cache" / "stage_8_9_39_features.npz"
    c39 = np.load(cache39_p, allow_pickle=True)
    c39_map = {fid: idx for idx, fid in enumerate(c39["file_ids"])}
    print(f"Loaded Stage 8.9.39 cache: {len(c39_map)} items.")

    cache40_p = BACKEND_DIR / "research" / "stage_8_9_40" / "results" / "new_cohort_features.npz"
    c40 = np.load(cache40_p, allow_pickle=True)
    c40_map = {fid: idx for idx, fid in enumerate(c40["file_ids"])}
    print(f"Loaded Stage 8.9.40 cache: {len(c40_map)} items.")

    # Read manifest v5
    with open(MANIFEST_P, "r", encoding="utf-8") as f:
        records = list(csv.DictReader(f))
    print(f"Loaded Manifest v5: {len(records)} records.")

    yamnet = None
    all_fids = []
    all_splits = []
    all_labels = []
    all_categories = []
    all_subtypes = []
    all_source_groups = []
    all_durations = []

    X_sem_list = []
    X_acoust_list = []
    mask_acoust_list = []
    X_subband_list = []

    reused_count = 0
    fresh_count = 0

    for idx, r in enumerate(records):
        fid = r["file_id"]
        orig_id = r.get("original_recording_id", "")
        split = r["v5_research_split"]
        label = int(r["binary_label"])
        cat = r.get("target_category", "")
        subtype = r.get("acoustic_subtype", "")
        sg = r.get("source_group_id", "")
        dur = float(r.get("duration_seconds", 0.0))

        if fid in c39_map:
            c_idx = c39_map[fid]
            f_sem = c39["X_sem"][c_idx]
            f_ac = c39["X_acoust"][c_idx]
            m_ac = c39["mask_acoust"][c_idx]
            f_sb = c39["X_subband"][c_idx]
            reused_count += 1
        elif orig_id in c39_map:
            c_idx = c39_map[orig_id]
            f_sem = c39["X_sem"][c_idx]
            f_ac = c39["X_acoust"][c_idx]
            m_ac = c39["mask_acoust"][c_idx]
            f_sb = c39["X_subband"][c_idx]
            reused_count += 1
        elif fid in c40_map:
            c_idx = c40_map[fid]
            f_sem = c40["X_sem"][c_idx]
            f_ac = c40["X_acoust"][c_idx]
            m_ac = c40["mask_acoust"][c_idx]
            f_sb = c40["X_subband"][c_idx]
            reused_count += 1
        elif orig_id in c40_map:
            c_idx = c40_map[orig_id]
            f_sem = c40["X_sem"][c_idx]
            f_ac = c40["X_acoust"][c_idx]
            m_ac = c40["mask_acoust"][c_idx]
            f_sb = c40["X_subband"][c_idx]
            reused_count += 1
        else:
            # Fresh extraction
            if yamnet is None:
                print("Loading YAMNet model for fresh extraction...")
                yamnet = YAMNetLoader()
                yamnet.load()

            audio_path = REPO_ROOT / r["workspace_audio_path"]
            wf, sr = load_audio(audio_path, target_sr=TARGET_SAMPLE_RATE)
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
            fresh_count += 1

        all_fids.append(fid)
        all_splits.append(split)
        all_labels.append(label)
        all_categories.append(cat)
        all_subtypes.append(subtype)
        all_source_groups.append(sg)
        all_durations.append(dur)

        X_sem_list.append(f_sem)
        X_acoust_list.append(f_ac)
        mask_acoust_list.append(m_ac)
        X_subband_list.append(f_sb)

        if (idx + 1) % 300 == 0 or (idx + 1) == len(records):
            print(f"Processed {idx + 1}/{len(records)} records (Reused: {reused_count}, Fresh: {fresh_count})...")

    OUT_NPZ.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        OUT_NPZ,
        file_ids=np.array(all_fids),
        splits=np.array(all_splits),
        labels=np.array(all_labels, dtype=np.int32),
        categories=np.array(all_categories),
        subtypes=np.array(all_subtypes),
        source_groups=np.array(all_source_groups),
        durations=np.array(all_durations, dtype=np.float32),
        X_sem=np.array(X_sem_list, dtype=np.float32),
        X_acoust=np.array(X_acoust_list, dtype=np.float32),
        mask_acoust=np.array(mask_acoust_list, dtype=np.float32),
        X_subband=np.array(X_subband_list, dtype=np.float32)
    )
    sz_mb = OUT_NPZ.stat().st_size / (1024 * 1024)
    print(f"\nSaved YAMNet cache: {OUT_NPZ} ({sz_mb:.2f} MB, {len(all_fids)} clips in {time.time() - t0:.1f}s)")
    print(f"Reused: {reused_count}, Freshly extracted: {fresh_count}")

if __name__ == "__main__":
    main()
