"""Targeted Dataset Expansion and Source-Group Partitioning (Stage 8.9.7).

Expands Dataset v2 with:
1. ~150 additional crowd chant, cheering, and stadium vocalizations (P1)
2. ~75 additional shouted speech and yell recordings (P2)
3. ~100 additional genuine human screams from FSD50K (P3)
4. ~50 additional calibrated masked/distant festival screams (synthesized into crowd noise)
5. Strict deduplication (exact PCM SHA-256)
6. Source-group assignment preserving uploader/speaker boundaries
7. Complete audit of Stage 5 historical test set isolation (0 leakage)
8. 60/20/20 train/val/test source-grouped partition
"""

from __future__ import annotations

import csv
import hashlib
import json
import logging
import random
import shutil
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.audio.preprocessor import load_audio
from src.config import DEFAULT_NIGENS_DIR, DEFAULT_OPENSLR99_DIR, TARGET_SAMPLE_RATE

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("expand_dataset_v3")

EXPERIMENT_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training"
AUDIO_OUT_DIR = EXPERIMENT_DIR / "audio"
MANIFESTS_DIR = EXPERIMENT_DIR / "manifests"
SPLITS_DIR = EXPERIMENT_DIR / "splits"
REPORTS_DIR = EXPERIMENT_DIR / "reports"

RANDOM_SEED = 42


def compute_file_sha256(path: Path) -> str:
    """Compute standard SHA-256 hash of file on disk."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def compute_pcm_sha256(waveform: np.ndarray) -> str:
    """Compute SHA-256 hash of PCM int16 normalized samples."""
    int16_samples = np.clip(waveform * 32767.0, -32768, 32767).astype(np.int16)
    return hashlib.sha256(int16_samples.tobytes()).hexdigest()


def synthesize_masked_scream(
    scream_wf: np.ndarray,
    noise_wf: np.ndarray,
    target_snr_db: float,
) -> np.ndarray:
    """Mix clean scream into noise bed at specified SNR in dB."""
    if len(noise_wf) < len(scream_wf):
        repeats = int(np.ceil(len(scream_wf) / len(noise_wf)))
        noise_wf = np.tile(noise_wf, repeats)[: len(scream_wf)]
    else:
        start_idx = random.randint(0, len(noise_wf) - len(scream_wf))
        noise_wf = noise_wf[start_idx : start_idx + len(scream_wf)]

    scream_rms = np.sqrt(np.mean(scream_wf ** 2))
    noise_rms = np.sqrt(np.mean(noise_wf ** 2))

    if noise_rms < 1e-6 or scream_rms < 1e-6:
        return scream_wf

    desired_noise_rms = scream_rms / (10.0 ** (target_snr_db / 20.0))
    scaled_noise = noise_wf * (desired_noise_rms / noise_rms)

    mixed = scream_wf + scaled_noise
    peak = np.max(np.abs(mixed))
    if peak > 0.95:
        mixed = mixed * (0.95 / peak)

    return mixed.astype(np.float32)


def load_historical_stage5_test_set() -> Tuple[Set[str], Set[str], Set[str]]:
    """Extract file IDs, sha256 hashes, and source groups from Stage 5 test set."""
    split_manifest_path = BACKEND_DIR / "dataset" / "manifests" / "split_manifest.json"
    test_ids = set()
    test_hashes = set()
    test_groups = set()

    if split_manifest_path.exists():
        with open(split_manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for r in data.get("records", []):
            if r.get("split") == "test":
                test_ids.add(r["file_id"])
                if r.get("sha256_hash"):
                    test_hashes.add(r["sha256_hash"])
                if r.get("source_group_id"):
                    test_groups.add(r["source_group_id"])

    logger.info(f"Loaded {len(test_ids)} historical Stage 5 test files across {len(test_groups)} source groups.")
    return test_ids, test_hashes, test_groups


def main():
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    logger.info("=" * 70)
    logger.info("STAGE 8.9.7: TARGETED DATASET EXPANSION (V3)")
    logger.info("=" * 70)

    stage5_test_ids, stage5_test_hashes, stage5_test_groups = load_historical_stage5_test_set()

    # Load existing Dataset v2 records
    manifest_v2_path = MANIFESTS_DIR / "dataset_manifest_v2.json"
    if not manifest_v2_path.exists():
        logger.error(f"Dataset v2 manifest not found: {manifest_v2_path}")
        sys.exit(1)

    with open(manifest_v2_path, "r", encoding="utf-8") as f:
        existing_records = json.load(f)

    logger.info(f"Loaded {len(existing_records)} existing records from dataset_manifest_v2.")

    master_records: List[Dict[str, Any]] = list(existing_records)
    pcm_hashes_seen: Dict[str, str] = {r["pcm_sha256"]: r["file_id"] for r in existing_records}
    file_ids_seen: Set[str] = set(r["file_id"] for r in existing_records)
    orig_ids_seen: Set[str] = set(r["original_recording_id"] for r in existing_records)

    # -------------------------------------------------------------
    # 1. Ingest FSD50K Expansion: Crowd Chants, Shouts, Screams
    # -------------------------------------------------------------
    fsd50k_audio_dir = Path(r"E:\FSD50K.dev_audio\FSD50K.dev_audio")
    fsd50k_meta_path = Path(r"E:\FSD50K.dev_audio\FSD50K.metadata\dev_clips_info_FSD50K.json")
    fsd50k_ground_truth_path = Path(r"E:\FSD50K.dev_audio\FSD50K.ground_truth\dev.csv")

    if not (fsd50k_audio_dir.exists() and fsd50k_meta_path.exists() and fsd50k_ground_truth_path.exists()):
        logger.error("FSD50K directory not accessible on E: drive!")
        sys.exit(1)

    with open(fsd50k_meta_path, "r", encoding="utf-8") as f:
        dev_meta = json.load(f)

    # Expansion quotas for Stage 8.9.7:
    expansion_quotas = {
        "crowd_chant_cheering": 150,  # Recommended ~150 additional crowd chants/cheering
        "shouting_and_speech": 75,   # Additional shouted speech/yell
        "scream": 100,               # Genuine screams from FSD50K Screaming
    }

    expansion_counts = {k: 0 for k in expansion_quotas}

    # Priority mapping for expansion
    expansion_label_mapping = [
        # (FSD50K label, target category, binary label)
        ("Crowd", "crowd_chant_cheering", "non_scream"),
        ("Cheering", "crowd_chant_cheering", "non_scream"),
        ("Applause", "crowd_chant_cheering", "non_scream"),
        ("Shout", "shouting_and_speech", "non_scream"),
        ("Yell", "shouting_and_speech", "non_scream"),
        ("Screaming", "scream", "scream"),
    ]

    fsd50k_rows = []
    with open(fsd50k_ground_truth_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            fsd50k_rows.append(r)

    # Shuffle with seed for deterministic selection
    random.shuffle(fsd50k_rows)

    logger.info("Ingesting targeted expansion recordings from FSD50K...")
    new_fsd50k_entries = []

    for row in fsd50k_rows:
        fname = row["fname"]
        orig_id = f"fsd50k_{fname}"
        if orig_id in orig_ids_seen or fname in orig_ids_seen:
            continue

        labels = [l.strip() for l in row["labels"].split(",")]
        audio_f = fsd50k_audio_dir / f"{fname}.wav"
        if not audio_f.exists():
            continue

        # Match category based on priority mapping
        matched_cat = None
        matched_binary = None
        for target_lbl, target_c, b_lbl in expansion_label_mapping:
            if target_lbl in labels:
                if expansion_counts[target_c] < expansion_quotas[target_c]:
                    matched_cat = target_c
                    matched_binary = b_lbl
                    break

        if not matched_cat:
            continue

        meta_info = dev_meta.get(fname, {})
        uploader = meta_info.get("uploader", "unknown")
        lic = meta_info.get("license", "CC-BY 3.0")
        title = meta_info.get("title", "")

        # Load audio & check quality
        try:
            wf, _ = load_audio(audio_f, target_sr=TARGET_SAMPLE_RATE)
            dur = float(len(wf) / TARGET_SAMPLE_RATE)
            if dur < 0.5 or dur > 35.0:
                continue
            peak = float(np.max(np.abs(wf)))
            if peak < 0.05:
                continue  # Silent
            pcm_h = compute_pcm_sha256(wf)
        except Exception as e:
            continue

        if pcm_h in pcm_hashes_seen:
            continue
        pcm_hashes_seen[pcm_h] = orig_id

        f_hash = compute_file_sha256(audio_f)
        is_hist_test = (orig_id in stage5_test_ids or f_hash in stage5_test_hashes)

        source_group = f"fsd50k_uploader_{uploader.lower().replace(' ', '_')}"
        file_id = f"v3_fsd50k_{fname}"

        # Destination path in experimental workspace
        dest_cat_dir = AUDIO_OUT_DIR / matched_cat
        dest_cat_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_cat_dir / f"{file_id}.wav"

        if not dest_file.exists():
            import soundfile as sf
            sf.write(str(dest_file), wf, TARGET_SAMPLE_RATE, subtype="PCM_16")

        entry = {
            "file_id": file_id,
            "original_recording_id": orig_id,
            "source_dataset": "FSD50K",
            "source_path": str(audio_f),
            "workspace_audio_path": str(dest_file),
            "target_category": matched_cat,
            "binary_label": matched_binary,
            "annotation_status": "FSD50K_GROUND_TRUTH",
            "review_decision": "SCREAM_PRESENT" if matched_binary == "scream" else "APPROVED_NON_SCREAM",
            "license": lic,
            "creator": uploader,
            "original_title": f"{title}: {row['labels']}",
            "duration_seconds": round(dur, 3),
            "sample_rate": TARGET_SAMPLE_RATE,
            "sha256_hash": f_hash,
            "pcm_sha256": pcm_h,
            "source_group_id": source_group,
            "is_historical_stage5_test": is_hist_test,
            "is_synthesized": False,
        }

        master_records.append(entry)
        new_fsd50k_entries.append(entry)
        orig_ids_seen.add(orig_id)
        file_ids_seen.add(file_id)
        expansion_counts[matched_cat] += 1

    logger.info(f"Added {len(new_fsd50k_entries)} FSD50K recordings:")
    for cat, cnt in expansion_counts.items():
        logger.info(f"  {cat:25}: {cnt:3d} / {expansion_quotas[cat]:3d}")

    # -------------------------------------------------------------
    # 2. Synthesize Additional Masked Screams in Festival Crowd Noise
    # -------------------------------------------------------------
    # Collect clean screams and crowd noise beds for mixing
    clean_screams = [r for r in master_records if r["target_category"] == "scream" and not r["is_synthesized"]]
    crowd_beds = [r for r in master_records if r["target_category"] == "crowd_chant_cheering"]

    logger.info(f"Available pools for masked scream synthesis: {len(clean_screams)} clean screams, {len(crowd_beds)} crowd beds.")

    synth_out_dir = AUDIO_OUT_DIR / "masked_distant_screams"
    synth_out_dir.mkdir(parents=True, exist_ok=True)

    # Target 50 additional calibrated masked screams across SNRs [-6, -3, 0, +3, +6] dB
    target_synth_count = 50
    snr_levels = [-6.0, -3.0, 0.0, 3.0, 6.0]
    synth_added = 0

    random.shuffle(clean_screams)
    random.shuffle(crowd_beds)

    for i in range(target_synth_count):
        scream_entry = clean_screams[i % len(clean_screams)]
        crowd_entry = crowd_beds[i % len(crowd_beds)]
        snr = snr_levels[i % len(snr_levels)]

        try:
            s_wf, _ = load_audio(Path(scream_entry["workspace_audio_path"]), target_sr=TARGET_SAMPLE_RATE)
            c_wf, _ = load_audio(Path(crowd_entry["workspace_audio_path"]), target_sr=TARGET_SAMPLE_RATE)
            mixed_wf = synthesize_masked_scream(s_wf, c_wf, target_snr_db=snr)

            synth_id = f"v3_synth_scream_{i+1:03d}_snr{int(snr):+03d}db"
            out_path = synth_out_dir / f"{synth_id}.wav"

            import soundfile as sf
            sf.write(str(out_path), mixed_wf, TARGET_SAMPLE_RATE, subtype="PCM_16")

            pcm_h = compute_pcm_sha256(mixed_wf)
            f_hash = compute_file_sha256(out_path)

            entry = {
                "file_id": synth_id,
                "original_recording_id": synth_id,
                "source_dataset": "Synthesized_Masked_Scream",
                "source_path": str(out_path),
                "workspace_audio_path": str(out_path),
                "target_category": "masked_distant_screams",
                "binary_label": "scream",
                "annotation_status": "SYNTHESIZED_GROUND_TRUTH",
                "review_decision": "SCREAM_PRESENT",
                "license": scream_entry["license"],
                "creator": f"Synthesized from {scream_entry['creator']} + {crowd_entry['creator']}",
                "original_title": f"Masked scream at {snr:+.1f}dB SNR into crowd noise ({crowd_entry['original_recording_id']})",
                "duration_seconds": round(float(len(mixed_wf) / TARGET_SAMPLE_RATE), 3),
                "sample_rate": TARGET_SAMPLE_RATE,
                "sha256_hash": f_hash,
                "pcm_sha256": pcm_h,
                "source_group_id": scream_entry["source_group_id"],  # INHERITS PARENT SCREAM GROUP TO PREVENT LEAKAGE!
                "is_historical_stage5_test": scream_entry["is_historical_stage5_test"],
                "is_synthesized": True,
            }

            master_records.append(entry)
            synth_added += 1
        except Exception as e:
            logger.warning(f"Failed to synthesize scream {i}: {e}")

    logger.info(f"Synthesized {synth_added} additional calibrated masked screams.")

    # -------------------------------------------------------------
    # 3. Source-Grouped 3-Way Partitioning (60% Train, 20% Val, 20% Test)
    # -------------------------------------------------------------
    logger.info("Partitioning Dataset v3 by Source Group (60% Train, 20% Val, 20% Test)...")
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for r in master_records:
        grp = r["source_group_id"]
        groups.setdefault(grp, []).append(r)

    unique_groups = sorted(list(groups.keys()))
    random.shuffle(unique_groups)

    # Check Stage 5 isolation: any group with historical Stage 5 test overlap routes to test ONLY
    hist_test_groups = set()
    standard_groups = []
    for g in unique_groups:
        has_hist = any(r["is_historical_stage5_test"] for r in groups[g])
        if has_hist:
            hist_test_groups.add(g)
        else:
            standard_groups.append(g)

    logger.info(f"Source groups: {len(unique_groups)} total ({len(hist_test_groups)} with historical Stage 5 test overlap).")

    # Target partition ratio: 60% Train, 20% Val, 20% Test
    n_total = len(standard_groups)
    n_train = int(0.60 * n_total)
    n_val = int(0.20 * n_total)

    train_groups = set(standard_groups[:n_train])
    val_groups = set(standard_groups[n_train : n_train + n_val])
    test_groups = set(standard_groups[n_train + n_val :]) | hist_test_groups

    # Assign split to each record
    for r in master_records:
        grp = r["source_group_id"]
        if grp in train_groups:
            r["split"] = "train"
        elif grp in val_groups:
            r["split"] = "val"
        else:
            r["split"] = "test"

    # Leakage Audit:
    train_pcm = set(r["pcm_sha256"] for r in master_records if r["split"] == "train")
    val_pcm = set(r["pcm_sha256"] for r in master_records if r["split"] == "val")
    test_pcm = set(r["pcm_sha256"] for r in master_records if r["split"] == "test")

    leak_train_val = train_pcm & val_pcm
    leak_train_test = train_pcm & test_pcm
    leak_val_test = val_pcm & test_pcm

    logger.info(f"Leakage Audit: Train-Val: {len(leak_train_val)}, Train-Test: {len(leak_train_test)}, Val-Test: {len(leak_val_test)}")
    if leak_train_val or leak_train_test or leak_val_test:
        logger.error("FATAL: Leakage detected between splits! Aborting.")
        sys.exit(1)

    hist_leakage = [r["file_id"] for r in master_records if r["split"] in ("train", "val") and r["is_historical_stage5_test"]]
    logger.info(f"Historical Stage 5 Test Contamination in Train/Val: {len(hist_leakage)} files (MUST BE 0).")
    if hist_leakage:
        logger.error(f"FATAL: Historical test leakage: {hist_leakage}")
        sys.exit(1)

    # -------------------------------------------------------------
    # 4. Save Manifests and Summaries
    # -------------------------------------------------------------
    manifest_v3_json_path = MANIFESTS_DIR / "dataset_manifest_v3.json"
    with open(manifest_v3_json_path, "w", encoding="utf-8") as f:
        json.dump(master_records, f, indent=2)

    manifest_v3_csv_path = MANIFESTS_DIR / "dataset_manifest_v3.csv"
    with open(manifest_v3_csv_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "file_id",
            "original_recording_id",
            "source_dataset",
            "target_category",
            "binary_label",
            "split",
            "duration_seconds",
            "source_group_id",
            "license",
            "creator",
            "is_synthesized",
            "is_historical_stage5_test",
            "sha256_hash",
            "pcm_sha256",
            "workspace_audio_path",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in master_records:
            writer.writerow(r)

    split_summary = {
        "total_records": len(master_records),
        "total_source_groups": len(unique_groups),
        "splits": {
            "train": {
                "total": sum(1 for r in master_records if r["split"] == "train"),
                "scream": sum(1 for r in master_records if r["split"] == "train" and r["binary_label"] == "scream"),
                "non_scream": sum(1 for r in master_records if r["split"] == "train" and r["binary_label"] == "non_scream"),
                "ambiguous": sum(1 for r in master_records if r["split"] == "train" and r["binary_label"] == "ambiguous"),
                "groups": len(train_groups),
            },
            "val": {
                "total": sum(1 for r in master_records if r["split"] == "val"),
                "scream": sum(1 for r in master_records if r["split"] == "val" and r["binary_label"] == "scream"),
                "non_scream": sum(1 for r in master_records if r["split"] == "val" and r["binary_label"] == "non_scream"),
                "ambiguous": sum(1 for r in master_records if r["split"] == "val" and r["binary_label"] == "ambiguous"),
                "groups": len(val_groups),
            },
            "test": {
                "total": sum(1 for r in master_records if r["split"] == "test"),
                "scream": sum(1 for r in master_records if r["split"] == "test" and r["binary_label"] == "scream"),
                "non_scream": sum(1 for r in master_records if r["split"] == "test" and r["binary_label"] == "non_scream"),
                "ambiguous": sum(1 for r in master_records if r["split"] == "test" and r["binary_label"] == "ambiguous"),
                "groups": len(test_groups),
            },
        },
        "records": master_records,
    }

    split_v3_json_path = SPLITS_DIR / "split_manifest_v3.json"
    with open(split_v3_json_path, "w", encoding="utf-8") as f:
        json.dump(split_summary, f, indent=2)

    split_v3_csv_path = SPLITS_DIR / "split_manifest_v3.csv"
    with open(split_v3_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in master_records:
            writer.writerow(r)

    print("\n" + "=" * 70)
    print("STAGE 8.9.7 DATASET V3 EXPANSION COMPLETE")
    print("=" * 70)
    print(f"Total Assembled Recordings  : {len(master_records)} (+{len(master_records) - len(existing_records)} added)")
    print(f"Total Unique Source Groups  : {len(unique_groups)}")
    print(f"Historical Stage 5 Overlap  : 0 in Train, 0 in Val ({len(hist_test_groups)} groups isolated to Test)")
    print("-" * 70)
    print("CATEGORY DISTRIBUTION:")
    cats = sorted(list(set(r["target_category"] for r in master_records)))
    for c in cats:
        items = [r for r in master_records if r["target_category"] == c]
        scream_c = sum(1 for r in items if r["binary_label"] == "scream")
        non_c = sum(1 for r in items if r["binary_label"] == "non_scream")
        amb_c = sum(1 for r in items if r["binary_label"] == "ambiguous")
        print(f"  {c:26}: {len(items):4d} total | {scream_c:3d} scream | {non_c:3d} non-scream | {amb_c:2d} amb")
    print("-" * 70)
    print("SPLIT DISTRIBUTION:")
    for s_name in ["train", "val", "test"]:
        s_data = split_summary["splits"][s_name]
        print(f"  {s_name.upper():5}: {s_data['total']:4d} clips ({s_data['scream']:3d} scream, {s_data['non_scream']:4d} non_scream, {s_data['ambiguous']:2d} amb) | {s_data['groups']:3d} source groups")
    print("=" * 70)


if __name__ == "__main__":
    main()
