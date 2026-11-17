import os
import sys
import json
import csv
import hashlib
from pathlib import Path
import numpy as np
import soundfile as sf
import scipy.signal as signal

BACKEND_DIR = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector\backend")
sys.path.insert(0, str(BACKEND_DIR))

from src.audio.preprocessor import load_audio
from src.config import TARGET_SAMPLE_RATE
from src.model.yamnet_loader import YAMNetLoader

STAGE_DIR = BACKEND_DIR / "research" / "stage_8_9_39"
CACHE_DIR = STAGE_DIR / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR = STAGE_DIR / "results" / "training"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# AudioSet class indices in YAMNet
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
        
        # Temporal energy variation
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
        float(rel_energies[0]), # Band1_300_800Hz_rel_energy
        float(rel_energies[1]), # Band2_800_1500Hz_rel_energy
        float(rel_energies[2]), # Band3_1500_2000Hz_rel_energy
        float(rel_energies[3]), # Band4_2000_3000Hz_rel_energy
        float(rel_energies[4]), # Band5_3000_4000Hz_rel_energy
        float(rel_energies[5]), # Band6_4000_6000Hz_rel_energy
        float(temp_vars[0]),    # Band1_300_800Hz_temp_var
        float(temp_vars[3]),    # Band4_2000_3000Hz_temp_var
        float(temp_vars[4]),    # Band5_3000_4000Hz_temp_var
        scream_band_to_vocal_ratio,
        high_band_whistle_ratio
    ]
    return np.array(vec, dtype=np.float32)

def main():
    print("=" * 80)
    print("STAGE 8.9.39: COMPREHENSIVE FEATURE EXTRACTION & CACHING")
    print("=" * 80)

    # 1. Load manifest and existing cache
    split_csv = BACKEND_DIR / "research" / "stage_8_9_38" / "manifests" / "research_split_v4.csv"
    with open(split_csv, "r", encoding="utf-8") as f:
        df_split = list(csv.DictReader(f))
    print(f"Loaded research_split_v4.csv: {len(df_split)} records.")

    hist_npz_path = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "features" / "yamnet_features_v3.npz"
    hist_npz = np.load(hist_npz_path, allow_pickle=True)
    hist_fids = {fid: idx for idx, fid in enumerate(hist_npz['file_ids'])}
    print(f"Loaded historical yamnet_features_v3.npz: {len(hist_fids)} records.")

    hist_sb_path = BACKEND_DIR / "research" / "stage_8_9_35" / "frequency_analysis" / "subband_feature_analysis.csv"
    with open(hist_sb_path, "r", encoding="utf-8") as f:
        hist_sb_rows = list(csv.DictReader(f))
    
    hist_sb_dict = {}
    for r in hist_sb_rows:
        vec = [
            float(r['Band1_300_800Hz_rel_energy']),
            float(r['Band2_800_1500Hz_rel_energy']),
            float(r['Band3_1500_2000Hz_rel_energy']),
            float(r['Band4_2000_3000Hz_rel_energy']),
            float(r['Band5_3000_4000Hz_rel_energy']),
            float(r['Band6_4000_6000Hz_rel_energy']),
            float(r['Band1_300_800Hz_temp_var']),
            float(r['Band4_2000_3000Hz_temp_var']),
            float(r['Band5_3000_4000Hz_temp_var']),
            float(r['scream_band_to_vocal_ratio']),
            float(r['high_band_whistle_ratio'])
        ]
        hist_sb_dict[r['file_id']] = np.array(vec, dtype=np.float32)
    print(f"Loaded historical subband features: {len(hist_sb_dict)} records.")

    # Initialize YAMNet for new recordings
    yamnet = None

    all_file_ids = []
    all_splits = []
    all_labels = []
    all_categories = []
    all_source_groups = []

    X_sem_list = []
    X_acoust_list = []
    X_subband_list = []

    print("\nProcessing all 1,578 records...")
    for idx, r in enumerate(df_split):
        fid = r['file_id']
        split = r['v4_research_split']
        label = 1 if r['binary_label'] == 'scream' else 0
        cat = r['target_category']
        sg = r['source_group_id']

        if fid in hist_fids and fid in hist_sb_dict:
            # Retrieve from historical cache
            h_idx = hist_fids[fid]
            f_sem = hist_npz['features_mean'][h_idx].astype(np.float32)
            f_acoust = hist_npz['vocal_features'][h_idx].astype(np.float32)
            f_sb = hist_sb_dict[fid]
        else:
            # Extract fresh from audio file
            if yamnet is None:
                print("Initializing YAMNet for expansion records...")
                yamnet = YAMNetLoader()
                yamnet.load()

            audio_path = Path(r['workspace_audio_path'])
            if not audio_path.is_absolute():
                audio_path = BACKEND_DIR.parent / r['workspace_audio_path']

            wf, _ = load_audio(audio_path, target_sr=TARGET_SAMPLE_RATE)
            preds, embs, _ = yamnet.infer(wf)

            f_sem = np.mean(embs, axis=0).astype(np.float32)

            vocal_frames = np.max(preds[:, VOCAL_CLASS_INDICES], axis=1)
            crowd_frames = np.max(preds[:, CROWD_CLASS_INDICES], axis=1)
            scream_frames = preds[:, SCREAM_CLASS_INDEX]

            f_acoust = np.array([
                float(np.max(vocal_frames)),
                float(np.mean(vocal_frames)),
                float(np.max(crowd_frames)),
                float(np.mean(crowd_frames)),
                float(np.max(scream_frames)),
                float(np.mean(scream_frames)),
            ], dtype=np.float32)

            # Subband features from raw audio
            raw_audio, sr = sf.read(str(audio_path))
            if raw_audio.ndim > 1:
                raw_audio = np.mean(raw_audio, axis=1)
            f_sb = extract_subband_vector(raw_audio, sr=sr)

        all_file_ids.append(fid)
        all_splits.append(split)
        all_labels.append(label)
        all_categories.append(cat)
        all_source_groups.append(sg)

        X_sem_list.append(f_sem)
        X_acoust_list.append(f_acoust)
        X_subband_list.append(f_sb)

        if (idx + 1) % 300 == 0 or (idx + 1) == len(df_split):
            print(f"  Processed {idx + 1}/{len(df_split)} records...")

    X_sem = np.array(X_sem_list, dtype=np.float32)
    X_acoust = np.array(X_acoust_list, dtype=np.float32)
    mask_acoust = (~np.isnan(X_acoust) & (X_acoust > 0.0)).astype(np.float32)
    X_acoust_safe = np.nan_to_num(X_acoust, nan=0.0)
    X_subband = np.array(X_subband_list, dtype=np.float32)

    all_file_ids = np.array(all_file_ids)
    all_splits = np.array(all_splits)
    all_labels = np.array(all_labels, dtype=np.int32)
    all_categories = np.array(all_categories)
    all_source_groups = np.array(all_source_groups)

    print(f"\nFeature Extraction Complete:")
    print(f"  X_sem shape:     {X_sem.shape} (dim=1024)")
    print(f"  X_acoust shape:  {X_acoust_safe.shape} (dim=6)")
    print(f"  mask_acoust shape:{mask_acoust.shape} (dim=6)")
    print(f"  X_subband shape: {X_subband.shape} (dim=11)")
    print(f"  Labels:          {np.sum(all_labels == 1)} screams, {np.sum(all_labels == 0)} negatives")

    # Fit learned normalization stats STRICTLY on v4_train only
    train_mask = (all_splits == 'v4_train')
    print(f"\nFitting normalization statistics on v4_train cohort ONLY (N={np.sum(train_mask)})...")
    
    sem_train_mean = np.mean(X_sem[train_mask], axis=0)
    sem_train_std = np.std(X_sem[train_mask], axis=0) + 1e-8
    
    acoust_train_mean = np.mean(X_acoust_safe[train_mask], axis=0)
    acoust_train_std = np.std(X_acoust_safe[train_mask], axis=0) + 1e-8

    subband_train_mean = np.mean(X_subband[train_mask], axis=0)
    subband_train_std = np.std(X_subband[train_mask], axis=0) + 1e-8

    norm_stats = {
        "fitting_split": "v4_train",
        "n_samples": int(np.sum(train_mask)),
        "sem_mean": sem_train_mean.tolist()[:10],
        "sem_std": sem_train_std.tolist()[:10],
        "acoust_mean": acoust_train_mean.tolist(),
        "acoust_std": acoust_train_std.tolist(),
        "subband_mean": subband_train_mean.tolist(),
        "subband_std": subband_train_std.tolist()
    }
    with open(RESULTS_DIR / "feature_norm_stats.json", "w", encoding="utf-8") as f:
        json.dump(norm_stats, f, indent=2)
    print(f"Normalization stats saved to: {RESULTS_DIR / 'feature_norm_stats.json'}")

    # Save complete unified feature cache
    out_npz = CACHE_DIR / "stage_8_9_39_features.npz"
    np.savez_compressed(
        out_npz,
        file_ids=all_file_ids,
        splits=all_splits,
        labels=all_labels,
        categories=all_categories,
        source_groups=all_source_groups,
        X_sem=X_sem,
        X_acoust=X_acoust_safe,
        mask_acoust=mask_acoust,
        X_subband=X_subband
    )
    print(f"Unified feature cache saved to: {out_npz}")
    file_size_mb = os.path.getsize(out_npz) / (1024 * 1024)
    print(f"Cache file size: {file_size_mb:.2f} MB")

    # Save feature configuration hash
    with open(out_npz, "rb") as f:
        cache_hash = hashlib.sha256(f.read()).hexdigest()
    print(f"Feature Cache SHA-256: {cache_hash}")

    config_info = {
        "feature_cache_path": str(out_npz),
        "feature_cache_sha256": cache_hash,
        "n_records": len(all_file_ids),
        "split_counts": {s: int(np.sum(all_splits == s)) for s in np.unique(all_splits)},
        "semantic_dim": 1024,
        "phonation_dim": 12,
        "subband_dim": 11,
        "normalization_fitted_on": "v4_train_only"
    }
    with open(STAGE_DIR / "config" / "feature_config.json", "w", encoding="utf-8") as f:
        json.dump(config_info, f, indent=2)
    print("Feature configuration recorded.")

if __name__ == "__main__":
    main()
