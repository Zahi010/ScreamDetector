import csv
import json
from pathlib import Path
from collections import Counter

manifest_path = Path("experiments/v2_hard_negative_training/manifests/dataset_manifest_v2.json")
with open(manifest_path, "r", encoding="utf-8") as f:
    existing_records = json.load(f)

existing_orig_ids = set(r["original_recording_id"] for r in existing_records)
existing_pcm = set(r["pcm_sha256"] for r in existing_records)
print(f"Existing dataset records: {len(existing_records)} ({len(existing_orig_ids)} unique original IDs)")

fsd50k_ground_truth_path = Path(r"E:\FSD50K.dev_audio\FSD50K.ground_truth\dev.csv")
fsd50k_meta_path = Path(r"E:\FSD50K.dev_audio\FSD50K.metadata\dev_clips_info_FSD50K.json")
fsd50k_audio_dir = Path(r"E:\FSD50K.dev_audio\FSD50K.dev_audio")

with open(fsd50k_meta_path, "r", encoding="utf-8") as f:
    dev_meta = json.load(f)

target_labels = {
    "Crowd": "crowd_chant_cheering",
    "Cheering": "crowd_chant_cheering",
    "Applause": "crowd_chant_cheering",
    "Shout": "shouting_and_speech",
    "Yell": "shouting_and_speech",
    "Screaming": "scream",
}

available_pool = {k: [] for k in target_labels}

with open(fsd50k_ground_truth_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        fname = row["fname"]
        labels = [l.strip() for l in row["labels"].split(",")]
        
        # Check if file exists on disk
        wav_path = fsd50k_audio_dir / f"{fname}.wav"
        if not wav_path.exists():
            continue
            
        # Check if already in dataset
        if fname in existing_orig_ids or f"fsd50k_{fname}" in existing_orig_ids:
            continue
            
        for l in labels:
            if l in available_pool:
                available_pool[l].append((fname, row, dev_meta.get(fname, {})))

print("\n--- Available FSD50K Candidates not yet in dataset ---")
for l, items in available_pool.items():
    print(f"  {l:20}: {len(items):4d} clips available on disk")
