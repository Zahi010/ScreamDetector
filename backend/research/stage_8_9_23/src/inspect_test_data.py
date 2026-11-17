import sys
from pathlib import Path
import numpy as np

BACKEND_DIR = Path(__file__).resolve().parents[3]
f17_path = BACKEND_DIR / "experiments/stage8_9_17_automated_dataset_reconstruction/data/features_stage8_9_17.npz"
f18_path = BACKEND_DIR / "experiments/stage8_9_18_temporal_phonation/data/features_stage8_9_18_temporal.npz"

d17 = np.load(f17_path, allow_pickle=True)
d18 = np.load(f18_path, allow_pickle=True)

splits = d17["splits"]
te = (splits == "test")

print(f"Total dataset size: {len(splits)}")
print(f"Test split size: {np.sum(te)}")
print("Test categories count:")
cats = d17["canonical_categories"][te]
y = d17["y_binary"][te].astype(int)
file_ids = d17["file_ids"][te]
source_groups = d17["source_groups"][te]

unique_cats, counts = np.unique(cats, return_counts=True)
for c, cnt in zip(unique_cats, counts):
    print(f"  {c}: {cnt}")

print(f"Test screams (y=1): {np.sum(y == 1)}")
print(f"Test negatives (y=0): {np.sum(y == 0)}")
print(f"Test shouting count: {np.sum(cats == 'SHOUTING_EXCITED_SPEECH')}")
print(f"Test unique source groups: {len(np.unique(source_groups))}")
