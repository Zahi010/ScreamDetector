"""
Stage 8.9.42: Extract Frame-Level YAMNet Predictions and Embeddings
Runs via Python 3.11 virtualenv (with TensorFlow / TF Hub).
Saves per-clip frame arrays to NPZ for downstream temporal pooling analysis.
"""
import os
import sys
import csv
from pathlib import Path
import numpy as np
import soundfile as sf

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from src.audio.preprocessor import load_audio
from src.config import TARGET_SAMPLE_RATE
from src.model.yamnet_loader import YAMNetLoader

STAGE40_DIR = BACKEND_DIR / "research" / "stage_8_9_40"
STAGE41_DIR = BACKEND_DIR / "research" / "stage_8_9_41"
STAGE42_DIR = BACKEND_DIR / "research" / "stage_8_9_42"

pos_manifest = STAGE41_DIR / "manifests" / "stage_8_9_41_positive_manifest.csv"
neg_manifest = STAGE40_DIR / "manifests" / "new_cohort_manifest.csv"
OUT_NPZ = STAGE42_DIR / "results" / "yamnet_frames_cache.npz"

def compute_frame_rms(waveform, n_frames, window_size=15360, hop_size=7680):
    rms_list = []
    for i in range(n_frames):
        start = i * hop_size
        end = start + window_size
        chunk = waveform[start:min(end, len(waveform))]
        rms = float(np.sqrt(np.mean(chunk**2))) if len(chunk) > 0 else 1e-6
        rms_list.append(max(rms, 1e-6))
    return np.array(rms_list, dtype=np.float32)

def main():
    print("=" * 80)
    print("STAGE 8.9.42: EXTRACTING RAW YAMNET FRAMES (Python 3.11 / TF)")
    print("=" * 80)

    pos_rows = []
    with open(pos_manifest, "r", encoding="utf-8") as f:
        pos_rows = list(csv.DictReader(f))

    neg_rows = []
    with open(neg_manifest, "r", encoding="utf-8") as f:
        neg_rows = list(csv.DictReader(f))

    print(f"Loaded {len(pos_rows)} positive rows and {len(neg_rows)} negative rows.")

    yamnet = YAMNetLoader()
    yamnet.load()

    all_items = [(r, 1) for r in pos_rows] + [(r, 0) for r in neg_rows]

    file_ids = []
    labels = []
    subtypes = []
    categories = []
    durations = []
    n_frames_list = []
    frame_rms_dict = {}
    preds_dict = {}
    embs_dict = {}

    for idx, (r, is_pos) in enumerate(all_items):
        fid = r["file_id"]
        rel_path = r["workspace_audio_path"]
        audio_path = REPO_ROOT / rel_path
        dur = float(r["duration_seconds"])
        subtype = r.get("acoustic_subtype", "")
        cat = r.get("target_category", "")

        wf, _ = load_audio(audio_path, target_sr=TARGET_SAMPLE_RATE)
        scores, embs, _ = yamnet.infer(wf)

        n_frames = len(embs)
        rms = compute_frame_rms(wf, n_frames)

        file_ids.append(fid)
        labels.append(is_pos)
        subtypes.append(subtype)
        categories.append(cat)
        durations.append(dur)
        n_frames_list.append(n_frames)

        preds_dict[fid] = scores.astype(np.float32)
        embs_dict[fid] = embs.astype(np.float32)
        frame_rms_dict[fid] = rms

        if (idx + 1) % 50 == 0 or (idx + 1) == len(all_items):
            print(f"Extracted {idx + 1}/{len(all_items)} audio files...")

    OUT_NPZ.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        OUT_NPZ,
        file_ids=np.array(file_ids),
        labels=np.array(labels, dtype=np.int32),
        subtypes=np.array(subtypes),
        categories=np.array(categories),
        durations=np.array(durations, dtype=np.float32),
        n_frames=np.array(n_frames_list, dtype=np.int32),
        **{f"preds_{fid}": preds_dict[fid] for fid in file_ids},
        **{f"embs_{fid}": embs_dict[fid] for fid in file_ids},
        **{f"rms_{fid}": frame_rms_dict[fid] for fid in file_ids}
    )
    print(f"\nSaved raw frames cache: {OUT_NPZ} ({OUT_NPZ.stat().st_size / (1024*1024):.2f} MB)")

if __name__ == "__main__":
    main()

