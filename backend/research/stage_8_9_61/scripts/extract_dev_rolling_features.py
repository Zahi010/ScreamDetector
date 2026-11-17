#!/usr/bin/env python3
"""
STAGE 8.9.61 — Development Cohort Rolling-Window Feature Extractor
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
Must be run with backend/.venv/Scripts/python.exe (TensorFlow/YAMNet environment).
"""

import os
import sys
import time
import json
import csv
from pathlib import Path
import numpy as np
import soundfile as sf
import scipy.signal as signal

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE61_DIR = BACKEND_DIR / "research" / "stage_8_9_61"
EXP_DIR = STAGE61_DIR / "rolling_window_experiments"
EXP_DIR.mkdir(parents=True, exist_ok=True)

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

SR_DEFAULT = 16000
NYQ_DEFAULT = SR_DEFAULT / 2.0
HOP_DEFAULT = int(0.010 * SR_DEFAULT)
FRAME_DEFAULT = int(0.025 * SR_DEFAULT)

PRECOMPUTED_BA = [
    signal.butter(4, [f_low / NYQ_DEFAULT, min(0.999, f_high / NYQ_DEFAULT)], btype='band')
    for _, f_low, f_high in BANDS
]

def extract_subband_vector_c5(audio_c: np.ndarray) -> np.ndarray:
    total_energy = float(np.dot(audio_c, audio_c) + 1e-9)
    band_energies = np.empty(6, dtype=np.float32)
    temp_vars = np.empty(3, dtype=np.float32)
    tv_map = {0: 0, 3: 1, 4: 2}

    for idx, (b, a) in enumerate(PRECOMPUTED_BA):
        filtered = signal.filtfilt(b, a, audio_c)
        band_energies[idx] = float(np.dot(filtered, filtered))
        if idx in tv_map:
            windows = np.lib.stride_tricks.sliding_window_view(filtered, FRAME_DEFAULT)[::HOP_DEFAULT]
            frame_rms = np.sqrt(np.mean(windows ** 2, axis=1) + 1e-9)
            e_mean = float(np.mean(frame_rms))
            e_std = float(np.std(frame_rms))
            temp_vars[tv_map[idx]] = e_std / (e_mean + 1e-9)

    out_vec = np.empty(11, dtype=np.float32)
    out_vec[0:6] = band_energies / total_energy
    out_vec[6] = temp_vars[0]
    out_vec[7] = temp_vars[1]
    out_vec[8] = temp_vars[2]
    low_e = band_energies[0] + band_energies[1] + 1e-9
    scream_band_e = band_energies[3] + band_energies[4] + 1e-9
    out_vec[9] = scream_band_e / low_e
    out_vec[10] = band_energies[5] / total_energy
    return out_vec

def extract_single_window_features(window_audio: np.ndarray, yamnet: YAMNetLoader):
    """
    Extracts features for a single 1.0-second (16,000 samples) window.
    window_audio must have length 16000 float32.
    """
    # 1. Normalization
    peak = float(np.max(np.abs(window_audio)) + 1e-9)
    norm_audio = (window_audio / peak).astype(np.float32)
    
    # 2. YAMNet inference
    preds, embs, _ = yamnet.infer(norm_audio)
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
    
    # 3. C5 Subband features
    f_sb = extract_subband_vector_c5(norm_audio)
    
    mask_acoust = (~np.isnan(f_acoust) & (f_acoust > 0.0)).astype(np.float32)
    
    return f_sem, f_acoust, mask_acoust, f_sb

def main():
    print("=" * 80)
    print("STAGE 8.9.61: EXTRACTING ROLLING-WINDOW FEATURES FOR DEV COHORT (N=187)")
    print("=" * 80)
    
    dev_csv = STAGE61_DIR / "rolling_window_development_manifest.csv"
    with open(dev_csv, mode="r", encoding="utf-8") as f:
        records = list(csv.DictReader(f))
    print(f"Loaded {len(records)} eligible development recordings.")
    
    print("Initializing YAMNet...")
    yamnet = YAMNetLoader()
    print("YAMNet ready.")
    
    HOP_SAMPLES = 8000   # 500 ms
    WIN_SAMPLES = 16000  # 1.0 s
    
    results = {}
    start_time = time.time()
    
    for idx, row in enumerate(records):
        rec_id = row["recording_id"]
        rel_p = row["workspace_audio_path"]
        audio_path = REPO_ROOT / rel_p
        
        # Load audio at 16 kHz
        wf, sr = load_audio(audio_path, target_sr=TARGET_SAMPLE_RATE)
        if len(wf) == 0:
            wf = np.zeros(WIN_SAMPLES, dtype=np.float32)
            
        # Segment into rolling windows with 500 ms hop
        # Pad if shorter than 1.0s
        if len(wf) < WIN_SAMPLES:
            padded = np.zeros(WIN_SAMPLES, dtype=np.float32)
            padded[:len(wf)] = wf
            windows = [padded]
            hop_times = [0.0]
        else:
            windows = []
            hop_times = []
            start = 0
            while start + WIN_SAMPLES <= len(wf):
                windows.append(wf[start:start + WIN_SAMPLES])
                hop_times.append(start / SR_DEFAULT)
                start += HOP_SAMPLES
            # Handle remainder if significant
            remainder = len(wf) - start
            if remainder >= 4000: # at least 250 ms
                partial = np.zeros(WIN_SAMPLES, dtype=np.float32)
                partial[:remainder] = wf[start:]
                windows.append(partial)
                hop_times.append(start / SR_DEFAULT)
                
        # Extract features for each window
        win_sem = []
        win_ac = []
        win_mask = []
        win_sb = []
        
        for w in windows:
            s, a, m, sb = extract_single_window_features(w, yamnet)
            win_sem.append(s)
            win_ac.append(a)
            win_mask.append(m)
            win_sb.append(sb)
            
        results[rec_id] = {
            "recording_id": rec_id,
            "source_group_id": row["source_group_id"],
            "binary_label": int(row["binary_label"]),
            "target_category": str(row["target_category"]),
            "subcategory": str(row["subcategory"]),
            "duration": float(row["duration_seconds"]),
            "n_hops": len(windows),
            "hop_times": hop_times,
            "sem": np.array(win_sem, dtype=np.float32),
            "acoust": np.array(win_ac, dtype=np.float32),
            "mask": np.array(win_mask, dtype=np.float32),
            "subband": np.array(win_sb, dtype=np.float32)
        }
        
        if (idx + 1) % 25 == 0 or (idx + 1) == len(records):
            elapsed = time.time() - start_time
            print(f"  Processed {idx + 1}/{len(records)} ({elapsed:.1f}s elapsed, {(idx+1)/elapsed:.2f} recs/s)...")
            
    out_npz = EXP_DIR / "dev_rolling_features.npz"
    np.savez_compressed(out_npz, data=results)
    print(f"\nSaved development rolling features to: {out_npz}")
    print(f"Total time elapsed: {time.time() - start_time:.2f}s")

if __name__ == "__main__":
    main()
