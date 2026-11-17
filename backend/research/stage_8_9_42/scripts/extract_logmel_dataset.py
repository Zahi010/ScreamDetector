"""
Stage 8.9.42: Extract 64-bin Log-Mel Spectrograms for All Research Splits
Runs via Python 3.13 (librosa, soundfile, numpy).
Extracts:
1. v4_train (N=820)
2. v4_val (N=339)
3. v4_reserved_expansion_test (N=102)
4. Stage 8.9.40 Independent Negatives (N=145)
5. Stage 8.9.41 Independent Positives (N=57)
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
STAGE38_DIR = BACKEND_DIR / "research" / "stage_8_9_38"
STAGE40_DIR = BACKEND_DIR / "research" / "stage_8_9_40"
STAGE41_DIR = BACKEND_DIR / "research" / "stage_8_9_41"
STAGE42_DIR = BACKEND_DIR / "research" / "stage_8_9_42"

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
    # Peak normalize
    max_amp = np.max(np.abs(wf))
    if max_amp > 1e-6:
        wf = wf / max_amp
    return wf

def extract_logmel(wf, sr=TARGET_SR):
    if len(wf) < N_FFT:
        # Minimum padding if shorter than FFT window
        pad_len = N_FFT - len(wf)
        wf = np.pad(wf, (0, pad_len), mode="constant")
    mel = librosa.feature.melspectrogram(
        y=wf, sr=sr, n_fft=N_FFT, hop_length=HOP_LENGTH,
        n_mels=N_MELS, fmin=FMIN, fmax=FMAX, power=2.0
    )
    logmel = librosa.power_to_db(mel, ref=np.max, top_db=80.0)
    # Normalize to roughly [-1.0, 1.0] range (top_db is 80dB, so (-80 to 0) -> [-1, 1])
    logmel_norm = (logmel + 40.0) / 40.0
    return logmel_norm.astype(np.float32)

def main():
    print("=" * 80)
    print("STAGE 8.9.42: EXTRACTING LOG-MEL SPECTROGRAM DATASET")
    print("=" * 80)

    t0 = time.time()
    all_clips = []

    # 1. v4 Splits (v4_train, v4_val, v4_reserved_expansion_test)
    v4_manifest = STAGE38_DIR / "manifests" / "research_split_v4.csv"
    with open(v4_manifest, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            split = r["v4_research_split"]
            if split in ["v4_train", "v4_val", "v4_reserved_expansion_test"]:
                audio_p = Path(r["workspace_audio_path"])
                all_clips.append({
                    "file_id": r["file_id"],
                    "split": split,
                    "binary_label": 1 if r["binary_label"] == "scream" else 0,
                    "target_category": r.get("target_category", ""),
                    "acoustic_subtype": r.get("acoustic_subtype", ""),
                    "source_group_id": r.get("source_group_id", ""),
                    "duration_seconds": float(r["duration_seconds"]),
                    "audio_path": audio_p
                })

    # 2. Stage 8.9.40 Independent Negatives
    stage40_manifest = STAGE40_DIR / "manifests" / "new_cohort_manifest.csv"
    with open(stage40_manifest, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            audio_p = REPO_ROOT / r["workspace_audio_path"]
            all_clips.append({
                "file_id": r["file_id"],
                "split": "stage40_hard_neg",
                "binary_label": 0,
                "target_category": r.get("target_category", ""),
                "acoustic_subtype": r.get("acoustic_subtype", ""),
                "source_group_id": r.get("source_group_id", ""),
                "duration_seconds": float(r["duration_seconds"]),
                "audio_path": audio_p
            })

    # 3. Stage 8.9.41 Independent Positives
    stage41_manifest = STAGE41_DIR / "manifests" / "stage_8_9_41_positive_manifest.csv"
    with open(stage41_manifest, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            audio_p = REPO_ROOT / r["workspace_audio_path"]
            all_clips.append({
                "file_id": r["file_id"],
                "split": "stage41_pos",
                "binary_label": 1,
                "target_category": "screaming_and_shriek",
                "acoustic_subtype": r.get("acoustic_subtype", ""),
                "source_group_id": r.get("source_group_id", ""),
                "duration_seconds": float(r["duration_seconds"]),
                "audio_path": audio_p
            })

    print(f"Total clips to extract: {len(all_clips)}")
    split_counts = {}
    for c in all_clips:
        split_counts[c["split"]] = split_counts.get(c["split"], 0) + 1
    for s, count in split_counts.items():
        print(f"  {s}: {count} clips")

    # Extract spectrograms
    file_ids = []
    splits = []
    labels = []
    categories = []
    subtypes = []
    source_groups = []
    durations = []
    logmel_dict = {}

    for idx, c in enumerate(all_clips):
        fid = c["file_id"]
        wf = load_and_preprocess(c["audio_path"])
        lmel = extract_logmel(wf)

        file_ids.append(fid)
        splits.append(c["split"])
        labels.append(c["binary_label"])
        categories.append(c["target_category"])
        subtypes.append(c["acoustic_subtype"])
        source_groups.append(c["source_group_id"])
        durations.append(c["duration_seconds"])
        logmel_dict[fid] = lmel

        if (idx + 1) % 250 == 0 or (idx + 1) == len(all_clips):
            print(f"Extracted {idx + 1}/{len(all_clips)} spectrograms ({time.time() - t0:.1f}s elapsed)...")

    out_npz = STAGE42_DIR / "results" / "logmel_spectrograms_cache.npz"
    out_npz.parent.mkdir(parents=True, exist_ok=True)
    print(f"\nSaving compressed cache to: {out_npz}...")
    np.savez_compressed(
        out_npz,
        file_ids=np.array(file_ids),
        splits=np.array(splits),
        labels=np.array(labels, dtype=np.int32),
        categories=np.array(categories),
        subtypes=np.array(subtypes),
        source_groups=np.array(source_groups),
        durations=np.array(durations, dtype=np.float32),
        **{f"logmel_{fid}": logmel_dict[fid] for fid in file_ids}
    )
    sz_mb = out_npz.stat().st_size / (1024 * 1024)
    print(f"Log-Mel dataset extracted and cached successfully: {sz_mb:.2f} MB in {time.time() - t0:.1f} seconds.")

if __name__ == "__main__":
    main()

