"""
Standalone feature extractor for Stage 8.9.40 using Python 3.11 .venv (TensorFlow + YAMNet + SoundFile + Scipy).
Extracts:
- X_sem (1024-d YAMNet mean embeddings)
- X_acoust (6-d max/mean vocal, crowd, scream class probabilities)
- mask_acoust (6-d validity mask)
- X_subband (11-d frequency subband energy ratios, temporal variances, scream-to-vocal ratio, whistle ratio)
Saves compressed .npz to backend/research/stage_8_9_40/results/new_cohort_features.npz.
"""
import os
import sys
import csv
import hashlib
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

STAGE40_DIR = BACKEND_DIR / "research" / "stage_8_9_40"
MANIFEST_PATH = STAGE40_DIR / "manifests" / "new_cohort_manifest.csv"
OUT_NPZ_PATH = STAGE40_DIR / "results" / "new_cohort_features.npz"

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
    print("=" * 70)
    print("STAGE 8.9.40: NEW COHORT FEATURE EXTRACTION (YAMNet + DSP)")
    print("=" * 70)

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Loaded {len(rows)} rows from {MANIFEST_PATH}")

    yamnet = YAMNetLoader()
    yamnet.load()

    file_ids = []
    categories = []
    source_groups = []
    durations = []

    X_sem_list = []
    X_acoust_list = []
    X_subband_list = []

    for idx, r in enumerate(rows):
        audio_path = REPO_ROOT / r["workspace_audio_path"]
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

        raw_audio, sr_raw = sf.read(str(audio_path))
        if raw_audio.ndim > 1:
            raw_audio = np.mean(raw_audio, axis=1)
        f_sb = extract_subband_vector(raw_audio, sr=sr_raw)

        file_ids.append(r["file_id"])
        categories.append(r["target_category"])
        source_groups.append(r["source_group_id"])
        durations.append(float(r["duration_seconds"]))

        X_sem_list.append(f_sem)
        X_acoust_list.append(f_acoust)
        X_subband_list.append(f_sb)

        if (idx + 1) % 30 == 0 or (idx + 1) == len(rows):
            print(f"  Processed {idx + 1}/{len(rows)} clips...")

    X_sem = np.array(X_sem_list, dtype=np.float32)
    X_acoust = np.array(X_acoust_list, dtype=np.float32)
    mask_acoust = (~np.isnan(X_acoust) & (X_acoust > 0.0)).astype(np.float32)
    X_subband = np.array(X_subband_list, dtype=np.float32)

    labels = np.zeros(len(file_ids), dtype=np.int32) # All hard negatives

    OUT_NPZ_PATH.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        OUT_NPZ_PATH,
        file_ids=np.array(file_ids),
        categories=np.array(categories),
        source_groups=np.array(source_groups),
        labels=labels,
        durations=np.array(durations, dtype=np.float32),
        X_sem=X_sem,
        X_acoust=X_acoust,
        mask_acoust=mask_acoust,
        X_subband=X_subband
    )

    print(f"\nSaved {len(file_ids)} feature vectors to {OUT_NPZ_PATH}")
    print("=" * 70)

if __name__ == "__main__":
    main()

