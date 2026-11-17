"""Analyze all short recordings (< 1.5s and < 1.0s) in stage8_9_11_dataset_manifest.csv."""
import csv
from pathlib import Path
from collections import Counter, defaultdict

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
MANIFEST_PATH = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_11_evaluation" / "stage8_9_11_dataset_manifest.csv"

def analyze_short_events():
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Total manifest rows: {len(rows)}")

    durations = [float(r["duration_seconds"]) for r in rows]
    under_1s = [r for r in rows if float(r["duration_seconds"]) < 1.0]
    under_1_5s = [r for r in rows if float(r["duration_seconds"]) < 1.5]

    print(f"Total recordings < 1.0s: {len(under_1s)}")
    print(f"Total recordings < 1.5s: {len(under_1_5s)}")

    cat_counts_under_1s = Counter(r["target_category"] for r in under_1s)
    print("\nRecordings < 1.0s by category:")
    for cat, count in sorted(cat_counts_under_1s.items()):
        print(f"  {cat:25s}: {count}")

    cat_split_under_1s = Counter((r["target_category"], r["split"]) for r in under_1s)
    print("\nRecordings < 1.0s by category and split:")
    for (cat, split), count in sorted(cat_split_under_1s.items()):
        print(f"  {cat:25s} | {split:5s}: {count}")

    # Screams under 1.0s
    screams_under_1s = [r for r in under_1s if "scream" in r["target_category"].lower()]
    print(f"\nScreams < 1.0s details (Total={len(screams_under_1s)}):")
    for r in screams_under_1s:
        print(f"  ID={r['file_id']:45s} | split={r['split']:5s} | cat={r['target_category']:22s} | dur={float(r['duration_seconds']):.3f}s | src={r['source_group_id']:30s} | synth={r.get('is_synthesized', False)}")

    # Check source groups for screams under 1.0s
    src_groups = Counter(r["source_group_id"] for r in screams_under_1s)
    print("\nSource groups for screams < 1.0s:")
    for sg, cnt in src_groups.items():
        print(f"  {sg}: {cnt}")

if __name__ == "__main__":
    analyze_short_events()
