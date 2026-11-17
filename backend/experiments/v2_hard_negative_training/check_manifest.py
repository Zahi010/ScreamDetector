import json
from pathlib import Path
from collections import Counter

manifest_path = Path("experiments/v2_hard_negative_training/manifests/dataset_manifest_v2.json")
with open(manifest_path, "r", encoding="utf-8") as f:
    records = json.load(f)

print(f"Total records in dataset_manifest_v2: {len(records)}")

cat_counts = Counter(r.get("target_category") for r in records)
split_counts = Counter(r.get("split") for r in records)
binary_counts = Counter(r.get("binary_label") for r in records)
source_datasets = Counter(r.get("source_dataset") for r in records)

print("\n--- Target Categories ---")
for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
    print(f"  {cat:30}: {count:4d}")

print("\n--- Splits ---")
for s, count in sorted(split_counts.items()):
    print(f"  {s:10}: {count:4d}")

print("\n--- Binary Labels ---")
for b, count in sorted(binary_counts.items()):
    print(f"  {b:15}: {count:4d}")

print("\n--- Source Datasets ---")
for src, count in sorted(source_datasets.items()):
    print(f"  {src:30}: {count:4d}")
