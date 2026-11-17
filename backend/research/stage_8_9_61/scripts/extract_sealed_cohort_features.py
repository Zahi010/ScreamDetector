#!/usr/bin/env python3
"""
STAGE 8.9.61 — Sealed Cohort Feature Extractor (N=700)
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
Must be run with backend/.venv/Scripts/python.exe (TensorFlow/YAMNet environment).
"""

import json
import os
import sys
import time
from pathlib import Path
import numpy as np
import soundfile as sf
import scipy.signal as signal

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE60_DIR = BACKEND_DIR / "research" / "stage_8_9_60"
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
    peak = float(np.max(np.abs(window_audio)) + 1e-9)
    norm_audio = (window_audio / peak).astype(np.float32)
    
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
    
    f_sb = extract_subband_vector_c5(norm_audio)
    mask_acoust = (~np.isnan(f_acoust) & (f_acoust > 0.0)).astype(np.float32)
    
    return f_sem, f_acoust, mask_acoust, f_sb

def main():
    print("=" * 80)
    print("STAGE 8.9.61: EXTRACTING SEALED COHORT FEATURES (N=700)")
    print("=" * 80)
    
    manifest_p = STAGE60_DIR / "future_evaluation_manifest.json"
    with open(manifest_p, "r", encoding="utf-8") as f:
        m_data = json.load(f)
    records = m_data["recordings"]
    print(f"Loaded {len(records)} recordings from sealed manifest.")
    
    print("Initializing YAMNet...")
    yamnet = YAMNetLoader()
    print("YAMNet ready.")
    
    HOP_SAMPLES = 8000   # 500 ms
    WIN_SAMPLES = 16000  # 1.0 s
    
    results = {}
    start_time = time.time()
    
    for idx, r in enumerate(records):
        rec_id = r["recording_id"]
        rel_p = r["workspace_audio_path"]
        audio_path = REPO_ROOT / rel_p
        
        wf, sr = load_audio(audio_path, target_sr=TARGET_SAMPLE_RATE)
        if len(wf) == 0:
            wf = np.zeros(WIN_SAMPLES, dtype=np.float32)
            
        # 1. Extract static center 1.0s window features
        if len(wf) <= WIN_SAMPLES:
            w_static = np.zeros(WIN_SAMPLES, dtype=np.float32)
            w_static[:len(wf)] = wf
        else:
            mid = len(wf) // 2
            start_static = max(0, mid - WIN_SAMPLES // 2)
            w_static = wf[start_static:start_static + WIN_SAMPLES]
            if len(w_static) < WIN_SAMPLES:
                padded = np.zeros(WIN_SAMPLES, dtype=np.float32)
                padded[:len(w_static)] = w_static
                w_static = padded
                
        sem_static, ac_static, mask_static, sb_static = extract_single_window_features(w_static, yamnet)
        
        # 2. Extract rolling windows with 500 ms hop
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
            remainder = len(wf) - start
            if remainder >= 4000:
                partial = np.zeros(WIN_SAMPLES, dtype=np.float32)
                partial[:remainder] = wf[start:]
                windows.append(partial)
                hop_times.append(start / SR_DEFAULT)
                
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
            "source_group_id": r["source_group_id"],
            "binary_label": int(r["binary_label"]),
            "target_category": str(r["target_category"]),
            "subcategory": str(r["subcategory"]),
            "duration": float(r["duration_seconds"]),
            "workspace_audio_path": rel_p,
            # Static features
            "sem_static": sem_static,
            "acoust_static": ac_static,
            "mask_static": mask_static,
            "subband_static": sb_static,
            # Rolling features
            "n_hops": len(windows),
            "hop_times": hop_times,
            "sem_rolling": np.array(win_sem, dtype=np.float32),
            "acoust_rolling": np.array(win_ac, dtype=np.float32),
            "mask_rolling": np.array(win_mask, dtype=np.float32),
            "subband_rolling": np.array(win_sb, dtype=np.float32)
        }
        
        if (idx + 1) % 50 == 0 or (idx + 1) == len(records):
            elapsed = time.time() - start_time
            print(f"  Processed {idx + 1}/{len(records)} ({elapsed:.1f}s elapsed, {(idx+1)/elapsed:.2f} recs/s)...")
            
    out_npz = EXP_DIR / "sealed_cohort_features.npz"
    np.savez_compressed(out_npz, data=results)
    print(f"\nSaved sealed cohort features to: {out_npz}")
    print(f"Total time elapsed: {time.time() - start_time:.2f}s")

if __name__ == "__main__":
    main()

