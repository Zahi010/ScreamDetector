import json
import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
MANIFEST_PATH = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_11_evaluation" / "stage8_9_11_dataset_manifest.json"

with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
    records = json.load(f)

val_missing = [r["file_id"] for r in records if r["split"] == "val" and not os.path.exists(r["workspace_audio_path"])]
test_missing = [r["file_id"] for r in records if r["split"] == "test" and not os.path.exists(r["workspace_audio_path"])]
train_missing = [r["file_id"] for r in records if r["split"] == "train" and not os.path.exists(r["workspace_audio_path"])]

print("Total records:", len(records))
print("Train missing:", len(train_missing))
print("Val missing:", len(val_missing))
print("Test missing:", len(test_missing))
