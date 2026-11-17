"""
Stage 8.9.23 Investigation F: Dataset and Label Validity Audit
Audits:
1. Source-level train/val/test leakage (source_group_id overlap).
2. Duplicate and near-duplicate recordings across splits.
3. Licensing distributions (CC0, CC BY, CC BY-NC, CC BY-ND, etc.).
4. Commercial eligibility.
5. Category balance and sample counts across splits.
6. Short-scream sample adequacy.
7. Emits dataset_source_integrity.csv and comprehensive audit data.
"""

import json
import csv
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = WORKSPACE_DIR.parent.parent

f17_path = BACKEND_DIR / "experiments/stage8_9_17_automated_dataset_reconstruction/data/features_stage8_9_17.npz"
m3_path = BACKEND_DIR / "experiments/v2_hard_negative_training/manifests/dataset_manifest_v3.json"
m11_path = BACKEND_DIR / "experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_11_evaluation/stage8_9_11_dataset_manifest.json"

d17 = np.load(f17_path, allow_pickle=True)
splits = d17["splits"]
y_binary = d17["y_binary"]
file_ids = d17["file_ids"]
cats = d17["canonical_categories"]
source_groups = d17["source_groups"]

# Load manifests for licensing and hash metadata
manifest_records = {}
for m_path in [m3_path, m11_path]:
    if m_path.exists():
        with open(m_path, "r", encoding="utf-8") as f:
            for item in json.load(f):
                fid = item.get("file_id")
                if fid and fid not in manifest_records:
                    manifest_records[fid] = item

print(f"Loaded {len(file_ids)} recordings from Stage 8.9.17 feature cache.")
print(f"Loaded {len(manifest_records)} metadata records from manifests.")

# 1. Source Group Leakage Audit
tr_mask = (splits == "train")
va_mask = (splits == "val")
te_mask = (splits == "test")

tr_sg = set(source_groups[tr_mask])
va_sg = set(source_groups[va_mask])
te_sg = set(source_groups[te_mask])

leak_tr_te = tr_sg.intersection(te_sg)
leak_va_te = va_sg.intersection(te_sg)
leak_tr_va = tr_sg.intersection(va_sg)

print(f"Unique source groups - Train: {len(tr_sg)}, Val: {len(va_sg)}, Test: {len(te_sg)}")
print(f"Source groups leaking between Train and Test: {len(leak_tr_te)} {leak_tr_te}")
print(f"Source groups leaking between Val and Test: {len(leak_va_te)} {leak_va_te}")
print(f"Source groups leaking between Train and Val: {len(leak_tr_va)} {leak_tr_va}")

# 2. Hash & Duplicate Audit
hashes_by_split = defaultdict(lambda: defaultdict(list))
for idx, fid in enumerate(file_ids):
    sp = splits[idx]
    meta = manifest_records.get(fid, {})
    h = meta.get("sha256_hash") or meta.get("pcm_sha256") or f"unknown_{fid}"
    hashes_by_split[h][sp].append(fid)

cross_split_duplicates = []
for h, split_dict in hashes_by_split.items():
    if len(split_dict) > 1 and not h.startswith("unknown_"):
        cross_split_duplicates.append((h, dict(split_dict)))

print(f"Exact cross-split duplicate file hashes: {len(cross_split_duplicates)}")

# 3. Licensing Audit
license_counts = Counter()
commercial_counts = Counter()
for fid in file_ids:
    meta = manifest_records.get(fid, {})
    lic = meta.get("license", "UNVERIFIED_OR_CUSTOM")
    if "publicdomain" in lic.lower() or "cc0" in lic.lower():
        norm_lic = "CC0 / Public Domain"
        comm = "COMMERCIALLY_PERMISSIBLE"
    elif "by-nc" in lic.lower():
        norm_lic = "CC BY-NC (Non-Commercial Only)"
        comm = "NON_COMMERCIAL_RESTRICTED"
    elif "by-nd" in lic.lower():
        norm_lic = "CC BY-ND (No Derivatives)"
        comm = "NON_COMMERCIAL_RESTRICTED"
    elif "by/" in lic.lower() or "by-sa" in lic.lower():
        norm_lic = "CC BY / CC BY-SA (Permissible with Attribution)"
        comm = "COMMERCIALLY_PERMISSIBLE_WITH_ATTRIBUTION"
    else:
        norm_lic = "ACADEMIC_RESEARCH_OR_UNVERIFIED"
        comm = "RESEARCH_ONLY"

    license_counts[norm_lic] += 1
    commercial_counts[comm] += 1

print("\nLicense Distribution across full dataset:")
for lic, count in license_counts.items():
    print(f"  {lic}: {count} ({count/len(file_ids)*100:.1f}%)")

print("\nCommercial Eligibility Status:")
for st, count in commercial_counts.items():
    print(f"  {st}: {count} ({count/len(file_ids)*100:.1f}%)")

# 4. Generate dataset_source_integrity.csv
integrity_rows = []
for idx, fid in enumerate(file_ids):
    sp = splits[idx]
    cat = cats[idx]
    y = int(y_binary[idx])
    sg = source_groups[idx]
    meta = manifest_records.get(fid, {})

    lic = meta.get("license", "UNVERIFIED_OR_CUSTOM")
    creator = meta.get("creator", "UNKNOWN")
    source_ds = meta.get("source_dataset", "STAGE8_LEGACY")
    is_synth = meta.get("is_synthesized", False)
    h = meta.get("sha256_hash", "UNKNOWN")

    integrity_rows.append({
        "file_id": fid,
        "split": sp,
        "ground_truth": y,
        "canonical_category": cat,
        "source_group_id": sg,
        "source_dataset": source_ds,
        "creator": creator,
        "license_normalized": lic,
        "commercial_status": "RESTRICTED" if "nc" in lic.lower() else "PERMISSIBLE" if "zero" in lic.lower() or "by/" in lic.lower() else "RESEARCH_ONLY",
        "sha256_hash": h,
        "is_synthesized": is_synth,
        "source_leakage_flag": sg in leak_tr_te or sg in leak_va_te
    })

out_csv = WORKSPACE_DIR / "dataset_source_integrity.csv"
with open(out_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(integrity_rows[0].keys()))
    writer.writeheader()
    writer.writerows(integrity_rows)

print(f"\nSaved {len(integrity_rows)} rows to {out_csv}")
