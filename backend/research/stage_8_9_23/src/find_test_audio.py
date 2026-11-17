import sys
from pathlib import Path
import numpy as np

BACKEND_DIR = Path(__file__).resolve().parents[3]
f17_path = BACKEND_DIR / "experiments/stage8_9_17_automated_dataset_reconstruction/data/features_stage8_9_17.npz"
d17 = np.load(f17_path, allow_pickle=True)
splits = d17["splits"]
te = (splits == "test")
file_ids = d17["file_ids"][te]

print(f"Sample test file IDs: {file_ids[:10]}")

# Let's search for some of these files in dataset/ or experiments/
matches = 0
audio_dirs = [
    BACKEND_DIR / "dataset",
    BACKEND_DIR / "dataset/stage8_8_hard_negatives",
    BACKEND_DIR / "experiments",
    BACKEND_DIR / "experiments/v2_hard_negative_training",
    BACKEND_DIR.parent / "data",
]

# Check existing files
found = {}
for root in audio_dirs:
    if root.exists():
        for ext in ["*.wav", "*.flac", "*.ogg", "*.mp3"]:
            for p in root.rglob(ext):
                stem = p.stem
                found[stem] = p

print(f"Total audio files found across repository: {len(found)}")
matched_ids = [fid for fid in file_ids if fid in found]
print(f"Test split files matching local audio: {len(matched_ids)} / {len(file_ids)}")

if len(matched_ids) > 0:
    print(f"Example match: {matched_ids[0]} -> {found[matched_ids[0]]}")
