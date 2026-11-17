"""
Stage 8.9.41: Extract YAMNet and Acoustic Features for Positive Scream Cohort (N=57)
Executed via Python 3.11 virtualenv (with TensorFlow / TF Hub).
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

STAGE41_DIR = BACKEND_DIR / "research" / "stage_8_9_41"
MANIFEST_PATH = STAGE41_DIR / "manifests" / "stage_8_9_41_positive_manifest.csv"
OUT_NPZ_PATH = STAGE41_DIR / "results" / "positive_cohort_features.npz"

VOCAL_CLASS_INDICES = [0, 1, 2, 3, 6, 7, 8, 13, 14, 16, 17]
CROWD_CLASS_INDICES = [67, 68, 69]
SCREAM_CLASS_INDEX = 6

def main():
    print(f"Loading manifest: {MANIFEST_PATH}")
    rows = []
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    print(f"Total recordings to extract: {len(rows)}")

    print("Loading YAMNet model...")
    yamnet = YAMNetLoader()
    yamnet.load()

    X_sem_list = []
    X_acoust_list = []
    file_ids = []
    subtypes = []
    source_groups = []
    durations = []

    for idx, r in enumerate(rows):
        audio_path = REPO_ROOT / r["workspace_audio_path"]
        wf, _ = load_audio(audio_path, target_sr=TARGET_SAMPLE_RATE)
        preds, embs, _ = yamnet.infer(wf)

        # 1. Semantic feature: mean-pooled YAMNet embedding (1024-d)
        f_sem = np.mean(embs, axis=0).astype(np.float32)

        # 2. Phonation features (6-d)
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

        X_sem_list.append(f_sem)
        X_acoust_list.append(f_acoust)
        file_ids.append(r["file_id"])
        subtypes.append(r["acoustic_subtype"])
        source_groups.append(r["source_group_id"])
        durations.append(float(r["duration_seconds"]))

    X_sem = np.array(X_sem_list, dtype=np.float32)
    X_acoust = np.array(X_acoust_list, dtype=np.float32)
    mask_acoust = (~np.isnan(X_acoust) & (X_acoust > 0.0)).astype(np.float32)

    OUT_NPZ_PATH.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        OUT_NPZ_PATH,
        file_ids=np.array(file_ids),
        subtypes=np.array(subtypes),
        source_groups=np.array(source_groups),
        labels=np.ones(len(rows), dtype=np.int32), # All confirmed positive screams
        durations=np.array(durations, dtype=np.float32),
        X_sem=X_sem,
        X_acoust=X_acoust,
        mask_acoust=mask_acoust
    )

    print(f"\nSuccessfully extracted and cached features: {OUT_NPZ_PATH}")
    print(f"X_sem shape: {X_sem.shape}, X_acoust shape: {X_acoust.shape}")

if __name__ == "__main__":
    main()
