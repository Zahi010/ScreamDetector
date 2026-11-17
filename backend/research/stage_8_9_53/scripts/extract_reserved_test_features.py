"""
Stage 8.9.53: Feature Extraction Script for Reserved Test Cohort
Extracts YAMNet semantic embeddings (1024-d), acoustic frame statistics (6-d),
phonation masks (6-d), and subband filterbank features (11-d) for all 366 recordings
in the verified independent reserved test cohort.
Must be run with backend/.venv/Scripts/python.exe (TensorFlow/TF-Hub environment).
Emits:
- backend/research/stage_8_9_53/features/reserved_test_features.npz
"""
import sys
import os
import time
import csv
from pathlib import Path
import numpy as np
import soundfile as sf
import scipy.signal as signal

REPO_ROOT = Path(r"c:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE53_DIR = BACKEND_DIR / "research" / "stage_8_9_53"
FEATURES_DIR = STAGE53_DIR / "features"
FEATURES_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(BACKEND_DIR))
from src.audio.preprocessor import load_audio
from src.config import TARGET_SAMPLE_RATE
from src.model.yamnet_loader import YAMNetLoader

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
    print("STAGE 8.9.53: EXTRACTING FEATURES FOR INDEPENDENT RESERVED TEST COHORT")
    print("=" * 80)
    
    manifest_p = STAGE53_DIR / "evaluation" / "reserved_test_manifest_verified.csv"
    if not manifest_p.exists():
        raise FileNotFoundError(f"Missing verified manifest: {manifest_p}")
        
    with open(manifest_p, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        records = list(reader)
    print(f"Loaded {len(records)} clips to extract.")
    
    print("Loading YAMNet model...")
    t0 = time.time()
    yamnet = YAMNetLoader()
    yamnet.load()
    print(f"YAMNet loaded in {time.time()-t0:.2f}s")
    
    file_ids = []
    orig_file_ids = []
    source_groups = []
    target_categories = []
    primary_labels = []
    subtype_tags = []
    licenses = []
    durations = []
    binary_labels = []
    
    X_sem_list = []
    X_acoust_list = []
    X_subband_list = []
    
    start_time = time.time()
    for idx, r in enumerate(records):
        fid = r["expansion_file_id"]
        rel_p = r["workspace_audio_path"]
        audio_path = REPO_ROOT / rel_p
        
        # 1. YAMNet audio loading and inference
        wf, sr = load_audio(audio_path, target_sr=TARGET_SAMPLE_RATE)
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
        
        # 2. Subband features from raw audio
        raw_audio, sr_raw = sf.read(str(audio_path))
        if raw_audio.ndim > 1:
            raw_audio = np.mean(raw_audio, axis=1)
        f_sb = extract_subband_vector(raw_audio, sr=sr_raw)
        
        file_ids.append(fid)
        orig_file_ids.append(r["original_file_id"])
        source_groups.append(r["source_group_id"])
        target_categories.append(r["target_category"])
        primary_labels.append(r["primary_label"])
        subtype_tags.append(str(r["subtype_tags"]))
        licenses.append(r["license"])
        durations.append(float(r["actual_duration_seconds"]))
        binary_labels.append(int(r["binary_label"]))
        
        X_sem_list.append(f_sem)
        X_acoust_list.append(f_acoust)
        X_subband_list.append(f_sb)
        
        if (idx + 1) % 50 == 0 or (idx + 1) == len(records):
            elapsed = time.time() - start_time
            rate = (idx + 1) / elapsed
            print(f"  Processed {idx + 1}/{len(records)} clips ({rate:.2f} clips/s, {elapsed:.1f}s elapsed)...")
            
    X_sem = np.array(X_sem_list, dtype=np.float32)
    X_acoust = np.array(X_acoust_list, dtype=np.float32)
    mask_acoust = (~np.isnan(X_acoust) & (X_acoust > 0.0)).astype(np.float32)
    X_subband = np.array(X_subband_list, dtype=np.float32)
    labels = np.array(binary_labels, dtype=np.int32)
    
    out_npz = FEATURES_DIR / "reserved_test_features.npz"
    np.savez_compressed(
        out_npz,
        file_ids=np.array(file_ids),
        original_file_ids=np.array(orig_file_ids),
        source_groups=np.array(source_groups),
        target_categories=np.array(target_categories),
        primary_labels=np.array(primary_labels),
        subtype_tags=np.array(subtype_tags),
        licenses=np.array(licenses),
        durations=np.array(durations),
        labels=labels,
        X_sem=X_sem,
        X_acoust=X_acoust,
        mask_acoust=mask_acoust,
        X_subband=X_subband
    )
    print(f"\nSuccessfully extracted and saved features to: {out_npz}")
    print(f"  X_sem shape:      {X_sem.shape}")
    print(f"  X_acoust shape:   {X_acoust.shape}")
    print(f"  mask_acoust shape:{mask_acoust.shape}")
    print(f"  X_subband shape:  {X_subband.shape}")
    print(f"  Total time:       {time.time()-start_time:.1f}s")

if __name__ == "__main__":
    main()
