"""Audit and investigate the 185 missing hard-negative audio recordings."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
import sys

# Ensure backend root is in sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from src.config import (
    BACKEND_DIR,
    FSD50K_DIR,
    PROJECT_ROOT,
    STAGE8_8_MANIFEST_JSON,
    STAGE8_8_RAW_DIR,
    get_freesound_api_key,
)
from src.database.review_store import get_review_store

# Candidate FSD50K subdirectories on E:
FSD50K_SEARCH_DIRS = [
    Path(r"E:\FSD50K.dev_audio"),
    Path(r"E:\FSD50K.dev_audio\FSD50K.dev_audio"),
    Path(r"E:\FSD50K.dev_audio\FSD50K.eval_audio"),
    Path(r"E:\FSD50K.dev_audio\FSD50K.eval_audio\FSD50K.eval_audio"),
]

GROUND_TRUTH_DIR = Path(r"E:\FSD50K.dev_audio\FSD50K.ground_truth")


def load_fsd50k_ground_truth():
    gt_ids = set()
    for csv_file in ["dev.csv", "eval.csv"]:
        p = GROUND_TRUTH_DIR / csv_file
        if p.is_file():
            with open(p, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    fname = row.get("fname")
                    if fname:
                        gt_ids.add(str(fname).strip())
    return gt_ids


def audit_missing():
    store = get_review_store()
    with store._get_connection() as conn:
        rows = conn.execute("""
            SELECT
                recording_id, source_provider, original_source_id,
                original_source_url, local_path, has_audio,
                original_filename, dataset_license, clip_license,
                commercial_compatibility, proposed_category,
                download_validation_status, unresolved_issues, review_status
            FROM candidates
            WHERE has_audio = 0
            ORDER BY source_provider, recording_id
        """).fetchall()

    missing_candidates = [dict(r) for r in rows]
    total_missing = len(missing_candidates)
    print(f"==================================================")
    print(f"STAGE 8.9.2 AUDIT: MISSING CANDIDATE RECORDINGS")
    print(f"==================================================")
    print(f"Total Missing in Database: {total_missing}")

    by_source = defaultdict(list)
    for c in missing_candidates:
        by_source[c["source_provider"]].append(c)

    print("\nMissing Count by Source:")
    for src, items in by_source.items():
        print(f"  - {src}: {len(items)}")

    # Ground truth lookup
    gt_ids = load_fsd50k_ground_truth()
    print(f"\nFSD50K Ground Truth Loaded from E: {len(gt_ids)} files indexed across dev.csv and eval.csv")

    # 1. Investigate FSD50K
    fsd_items = by_source.get("fsd50k", [])
    fsd_found_on_disk = {}
    fsd_not_on_disk = []

    for c in fsd_items:
        orig_id = str(c["original_source_id"])
        found_path = None
        for sdir in FSD50K_SEARCH_DIRS:
            target = sdir / f"{orig_id}.wav"
            if target.is_file():
                found_path = target
                break

        in_gt = orig_id in gt_ids
        if found_path:
            fsd_found_on_disk[c["recording_id"]] = {
                "orig_id": orig_id,
                "found_path": found_path,
                "in_ground_truth": in_gt,
                "candidate": c,
            }
        else:
            fsd_not_on_disk.append({
                "orig_id": orig_id,
                "in_ground_truth": in_gt,
                "candidate": c,
            })

    print(f"\n1. FSD50K Investigation ({len(fsd_items)} items):")
    print(f"  - Found on E: drive: {len(fsd_found_on_disk)}")
    print(f"  - NOT found on E: drive: {len(fsd_not_on_disk)}")
    for item in fsd_not_on_disk:
        c = item["candidate"]
        print(f"    Missing ID: {c['recording_id']} (orig_id: {c['original_source_id']}, in_gt={item['in_ground_truth']}, cat={c['proposed_category']}, lic={c['commercial_compatibility']})")

    # 2. Investigate Freesound
    fs_items = by_source.get("freesound", [])
    freesound_api_key = get_freesound_api_key()
    has_api_key = bool(freesound_api_key)
    print(f"\n2. Freesound Investigation ({len(fs_items)} items):")
    print(f"  - API Key Present: {has_api_key}")
    
    fs_lic_groups = defaultdict(list)
    for c in fs_items:
        fs_lic_groups[c["commercial_compatibility"]].append(c)

    for lic, items in fs_lic_groups.items():
        print(f"  - License '{lic}': {len(items)} items")
        for it in items:
            print(f"      Item: {it['recording_id']} (orig_id: {it['original_source_id']}, cat: {it['proposed_category']}, lic: {it['commercial_compatibility']})")

    # Probe Freesound API for first item
    if has_api_key and fs_items:
        import urllib.request
        import soundfile as sf
        sample_id = fs_items[0]["original_source_id"]
        print(f"\n  Probing Freesound API for sound ID {sample_id}...")
        url = f"https://freesound.org/apiv2/sounds/{sample_id}/?token={freesound_api_key}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "FestivalScreamDetector/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                preview_mp3 = data.get("previews", {}).get("preview-hq-mp3")
                print(f"    API Sound Name: {data.get('name')}")
                print(f"    API License: {data.get('license')}")
                print(f"    Preview HQ MP3: {preview_mp3}")
                if preview_mp3:
                    # Test downloading 32KB
                    req_audio = urllib.request.Request(preview_mp3, headers={"User-Agent": "FestivalScreamDetector/1.0"})
                    with urllib.request.urlopen(req_audio, timeout=10) as a_resp:
                        audio_bytes = a_resp.read()
                        print(f"    Downloaded Preview Bytes: {len(audio_bytes)}")
                        import io
                        try:
                            data, sr = sf.read(io.BytesIO(audio_bytes))
                            print(f"    Soundfile decoded successfully! Shape: {data.shape}, Sample Rate: {sr}")
                        except Exception as decode_err:
                            print(f"    Soundfile decode error: {decode_err}")
        except Exception as e:
            print(f"    API Probe failed: {e}")


    # 3. Investigate AudioSet
    as_items = by_source.get("audioset", [])
    print(f"\n3. AudioSet Investigation ({len(as_items)} items):")
    as_lic_groups = defaultdict(list)
    for c in as_items:
        as_lic_groups[c["commercial_compatibility"]].append(c)
    for lic, items in as_lic_groups.items():
        print(f"  - License '{lic}': {len(items)} items")
        for it in items[:2]:
            print(f"      Example: {it['recording_id']} (orig_id: {it['original_source_id']}, cat: {it['proposed_category']})")

    # 4. Summary of recovery classifications
    print(f"\n4. Recovery Audit Classification Summary:")
    print(f"  [A] Existing Elsewhere on Disk (E: drive FSD50K nested folders): {len(fsd_found_on_disk)}")
    print(f"  [B] Never Downloaded / Eligible for Freesound API: {len(fs_items)}")
    print(f"  [C] Licence Restricted / YouTube Terms (AudioSet): {len(as_items)}")
    print(f"  [D] Source Unavailable / FSD50K non-existent ID: {len(fsd_not_on_disk)}")
    print(f"  Total Accounted For: {len(fsd_found_on_disk) + len(fs_items) + len(as_items) + len(fsd_not_on_disk)} / {total_missing}")



if __name__ == "__main__":
    audit_missing()

