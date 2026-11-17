"""
Stage 8.9.43: Extract Log-Mel Spectrograms for All 1,914 Clips in Dataset Manifest v5
Runs via Python 3.13 (librosa, soundfile, numpy).
Saves to backend/research/stage_8_9_43/features/logmel_v5_cache.npz.
"""
import os
import sys
import time
import csv
from pathlib import Path
import numpy as np
import librosa
import soundfile as sf

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE43_DIR = BACKEND_DIR / "research" / "stage_8_9_43"

MANIFEST_P = STAGE43_DIR / "manifests" / "dataset_manifest_v5.csv"
OUT_NPZ = STAGE43_DIR / "features" / "logmel_v5_cache.npz"

TARGET_SR = 16000
N_MELS = 64
N_FFT = 1024
HOP_LENGTH = 256
FMIN = 125.0
FMAX = 7500.0

def load_and_preprocess(audio_path, target_sr=TARGET_SR):
    wf, orig_sr = sf.read(str(audio_path), dtype="float32")
    if wf.ndim > 1:
        wf = np.mean(wf, axis=1)
    if orig_sr != target_sr:
        wf = librosa.resample(wf, orig_sr=orig_sr, target_sr=target_sr)
    max_amp = np.max(np.abs(wf))
    if max_amp > 1e-6:
        wf = wf / max_amp
    return wf

def extract_logmel(wf, sr=TARGET_SR):
    if len(wf) < N_FFT:
        wf = np.pad(wf, (0, N_FFT - len(wf)), mode="constant")
    mel = librosa.feature.melspectrogram(
        y=wf, sr=sr, n_fft=N_FFT, hop_length=HOP_LENGTH,
        n_mels=N_MELS, fmin=FMIN, fmax=FMAX, power=2.0
    )
    logmel = librosa.power_to_db(mel, ref=np.max, top_db=80.0)
    logmel_norm = (logmel + 40.0) / 40.0
    return logmel_norm.astype(np.float32)

def main():
    print("=" * 80)
    print("STAGE 8.9.43: EXTRACTING LOG-MEL SPECTROGRAMS FOR MANIFEST V5")
    print("=" * 80)
    t0 = time.time()

    records = []
    with open(MANIFEST_P, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            records.append(r)

    print(f"Total recordings to extract: {len(records)}")

    file_ids = []
    splits = []
    labels = []
    categories = []
    subtypes = []
    source_groups = []
    durations = []
    logmel_dict = {}

    missing = 0
    for idx, r in enumerate(records):
        fid = r["file_id"]
        rel_path = r["workspace_audio_path"]
        audio_path = REPO_ROOT / rel_path
        if not audio_path.exists():
            print(f"Missing: {audio_path}")
            missing += 1
            continue

        wf = load_and_preprocess(audio_path)
        lmel = extract_logmel(wf)

        file_ids.append(fid)
        splits.append(r["v5_research_split"])
        labels.append(int(r["binary_label"]))
        categories.append(r.get("target_category", ""))
        subtypes.append(r.get("acoustic_subtype", ""))
        source_groups.append(r.get("source_group_id", ""))
        durations.append(float(r.get("duration_seconds", len(wf)/TARGET_SR)))
        logmel_dict[fid] = lmel

        if (idx + 1) % 300 == 0 or (idx + 1) == len(records):
            print(f"Extracted {idx + 1}/{len(records)} spectrograms ({time.time() - t0:.1f}s elapsed)...")

    OUT_NPZ.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        OUT_NPZ,
        file_ids=np.array(file_ids),
        splits=np.array(splits),
        labels=np.array(labels, dtype=np.int32),
        categories=np.array(categories),
        subtypes=np.array(subtypes),
        source_groups=np.array(source_groups),
        durations=np.array(durations, dtype=np.float32),
        **{f"logmel_{fid}": logmel_dict[fid] for fid in file_ids}
    )
    sz_mb = OUT_NPZ.stat().st_size / (1024 * 1024)
    print(f"\nSaved Log-Mel cache: {OUT_NPZ} ({sz_mb:.2f} MB, {len(file_ids)} clips in {time.time() - t0:.1f}s)")

if __name__ == "__main__":
    main()

