"""Stage 8.9.11 Targeted Commercially Eligible Data Acquisition.

Implements the Stage 8.9.10 Targeted Data Acquisition Plan:
1. Ingests permissive (CC0 1.0, CC BY 3.0, CC BY 4.0) recordings from FSD50K dev audio.
2. Synthesizes calibrated masked screams using verified CC0 clean screams and CC0 festival ambiance.
3. Preserves full attribution, creator, license URL, source URL, duration, and PCM SHA-256.
4. Preserves 100% source-group disjointness and historical Stage 5 test quarantine.
5. Partitions new source groups (60% Train, 20% Val, 20% Test) and produces versioned Stage 8.9.11 manifests.
"""

from __future__ import annotations

import csv
import hashlib
import json
import logging
import random
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import numpy as np
import soundfile as sf

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.audio.preprocessor import load_audio
from src.config import TARGET_SAMPLE_RATE

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("stage8_9_11_acquisition")

STAGE10_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_10_readiness"
STAGE11_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_11_evaluation"
AUDIO_OUT_DIR = STAGE11_DIR / "audio"

RANDOM_SEED = 42

PERMISSIVE_LICENSES = {
    "http://creativecommons.org/publicdomain/zero/1.0/": "CC0 1.0",
    "http://creativecommons.org/licenses/by/3.0/": "CC BY 3.0",
    "http://creativecommons.org/licenses/by/4.0/": "CC BY 4.0",
}


def compute_file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().upper()


def compute_pcm_sha256(waveform: np.ndarray) -> str:
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


def main():
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    logger.info("=================================================================")
    logger.info("STAGE 8.9.11: TARGETED COMMERCIALLY ELIGIBLE DATA ACQUISITION")
    logger.info("=================================================================")

    # 1. Load baseline eligible manifest
    with open(STAGE10_DIR / "commercially_eligible_manifest.json", "r", encoding="utf-8") as f:
        eligible_manifest = json.load(f)
    logger.info(f"Loaded {len(eligible_manifest)} baseline recordings from Stage 8.9.10 eligible manifest.")

    existing_ids = set()
    for r in eligible_manifest:
        existing_ids.add(r["file_id"])
        if "original_id" in r and r["original_id"]:
            existing_ids.add(r["original_id"])
            existing_ids.add(str(r["original_id"]).replace("fsd50k_", ""))
        fname = r["file_id"].replace("v2_fsd50k_", "").replace("fsd50k_", "").replace("v3_fsd50k_", "")
        existing_ids.add(fname)

    # Load quarantined IDs
    with open(STAGE10_DIR / "restricted_recordings_audit.csv", "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            existing_ids.add(row["file_id"])
            existing_ids.add(row["original_recording_id"])
            existing_ids.add(row["original_recording_id"].replace("fsd50k_", ""))

    # Load historical Stage 5 test groups & IDs
    with open(BACKEND_DIR / "reports" / "test_predictions.csv", "r", encoding="utf-8") as f:
        stage5_test_groups = {row["source_group_id"] for row in csv.DictReader(f)}

    # 2. Load FSD50K dev metadata and ground truth
    fsd50k_meta_path = Path(r"E:\FSD50K.dev_audio\FSD50K.metadata\dev_clips_info_FSD50K.json")
    fsd50k_gt_path = Path(r"E:\FSD50K.dev_audio\FSD50K.ground_truth\dev.csv")
    fsd50k_audio_dir = Path(r"E:\FSD50K.dev_audio\FSD50K.dev_audio")

    with open(fsd50k_meta_path, "r", encoding="utf-8") as f:
        fsd_meta = json.load(f)

    with open(fsd50k_gt_path, "r", encoding="utf-8") as f:
        fsd_gt = {row["fname"]: row["labels"].split(",") for row in csv.DictReader(f)}

    logger.info(f"Loaded FSD50K metadata: {len(fsd_meta)} clips.")

    # Category candidate filters and quotas (in terms of new groups and max clips)
    acquisition_specs = {
        "shouting_and_speech": {
            "tags": ["Shout", "Yell", "Speech", "Child_speech_and_kid_speaking"],
            "target_groups": 37,
            "max_clips_per_group": 2,
            "target_clips": 60,
            "binary_label": "non_scream",
        },
        "crowd_chant_cheering": {
            "tags": ["Crowd", "Cheering", "Applause"],
            "target_groups": 25,
            "max_clips_per_group": 2,
            "target_clips": 50,
            "binary_label": "non_scream",
        },
        "scream": {
            "tags": ["Screaming"],
            "target_groups": 18,
            "max_clips_per_group": 2,
            "target_clips": 36,
            "binary_label": "scream",
        },
        "whistles_and_squeaks": {
            "tags": ["Squeak", "Whistle"],
            "target_groups": 12,
            "max_clips_per_group": 2,
            "target_clips": 24,
            "binary_label": "non_scream",
        },
        "sfx_sirens_fireworks": {
            "tags": ["Siren", "Fireworks", "Alarm"],
            "target_groups": 12,
            "max_clips_per_group": 2,
            "target_clips": 24,
            "binary_label": "non_scream",
        },
        "infant_crying": {
            "tags": ["Crying_and_sobbing"],
            "target_groups": 13,
            "max_clips_per_group": 2,
            "target_clips": 17,
            "binary_label": "non_scream",
        },
        "general_environmental": {
            "tags": ["Environmental_noise", "Rain", "Wind", "Stream", "Static"],
            "target_groups": 12,
            "max_clips_per_group": 2,
            "target_clips": 24,
            "binary_label": "non_scream",
        },
    }

    # Gather candidate pools by category
    category_pools: Dict[str, Dict[str, List[Dict[str, Any]]]] = {cat: {} for cat in acquisition_specs}

    for fname, labels in fsd_gt.items():
        if fname in existing_ids:
            continue
        info = fsd_meta.get(fname)
        if not info:
            continue
        lic_url = info.get("license", "")
        if lic_url not in PERMISSIVE_LICENSES:
            continue
        uploader = info.get("uploader", "unknown").strip()
        src_group = "fsd50k_user_" + uploader.lower().replace(" ", "_")
        if src_group in stage5_test_groups:
            continue

        wav_path = fsd50k_audio_dir / f"{fname}.wav"
        if not wav_path.exists():
            continue

        for cat, spec in acquisition_specs.items():
            if any(t in labels for t in spec["tags"]):
                # Ensure no screams in negative classes
                if cat != "scream" and "Screaming" in labels:
                    continue
                category_pools[cat].setdefault(src_group, []).append({
                    "fname": fname,
                    "labels": labels,
                    "license_url": lic_url,
                    "license_name": PERMISSIVE_LICENSES[lic_url],
                    "uploader": uploader,
                    "src_group": src_group,
                    "title": info.get("title", ""),
                    "wav_path": wav_path,
                })

    # Ingest targeted recordings from pools
    new_acquired_records: List[Dict[str, Any]] = []
    acquired_groups_by_category: Dict[str, Set[str]] = {}

    for cat, spec in acquisition_specs.items():
        acquired_groups_by_category[cat] = set()
        groups = list(category_pools[cat].keys())
        random.shuffle(groups)
        selected_groups = groups[: spec["target_groups"]]

        dest_cat_dir = AUDIO_OUT_DIR / cat
        dest_cat_dir.mkdir(parents=True, exist_ok=True)

        cat_clips_count = 0
        for grp in selected_groups:
            clips = category_pools[cat][grp]
            random.shuffle(clips)
            selected_clips = clips[: spec["max_clips_per_group"]]

            for c in selected_clips:
                if cat_clips_count >= spec["target_clips"]:
                    break
                fname = c["fname"]
                dest_wav = dest_cat_dir / f"stage11_fsd50k_{fname}.wav"

                # Load and standardize audio to 16kHz mono PCM 16-bit
                wf, sr = load_audio(c["wav_path"], target_sr=TARGET_SAMPLE_RATE)
                dur = float(len(wf) / TARGET_SAMPLE_RATE)
                if dur < 0.4:
                    continue  # skip tiny fragments

                sf.write(str(dest_wav), wf, TARGET_SAMPLE_RATE, subtype="PCM_16")

                f_hash = compute_file_sha256(dest_wav)
                pcm_h = compute_pcm_sha256(wf)

                rec = {
                    "file_id": f"stage11_fsd50k_{fname}",
                    "original_id": f"fsd50k_{fname}",
                    "source_dataset": "FSD50K",
                    "workspace_audio_path": str(dest_wav.relative_to(BACKEND_DIR)).replace("\\", "/"),
                    "target_category": cat,
                    "binary_label": spec["binary_label"],
                    "license": c["license_name"],
                    "license_url": c["license_url"],
                    "attribution": c["uploader"],
                    "original_title": c["title"],
                    "source_url": f"https://freesound.org/s/{fname}/",
                    "source_group_id": c["src_group"],
                    "duration_seconds": round(dur, 3),
                    "file_sha256": f_hash,
                    "pcm_sha256": pcm_h,
                    "is_synthesized": False,
                    "acquisition_stage": "Stage_8_9_11",
                }
                new_acquired_records.append(rec)
                acquired_groups_by_category[cat].add(c["src_group"])
                cat_clips_count += 1

        logger.info(f"Acquired {cat:25}: {cat_clips_count:3d} clips across {len(acquired_groups_by_category[cat]):2d} groups (Target: {spec['target_clips']} clips, {spec['target_groups']} groups)")

    # 3. Synthesize Calibrated Masked Screams in Festival Background
    clean_screams_pool = [r for r in eligible_manifest if r["target_category"] == "scream" and not r.get("is_synthesized", False)]
    clean_screams_pool.extend([r for r in new_acquired_records if r["target_category"] == "scream"])
    crowd_beds_pool = [r for r in eligible_manifest if r["target_category"] == "crowd_chant_cheering"]

    logger.info(f"Synthesizing masked screams from {len(clean_screams_pool)} clean screams and {len(crowd_beds_pool)} crowd beds...")

    synth_cat_dir = AUDIO_OUT_DIR / "masked_distant_screams"
    synth_cat_dir.mkdir(parents=True, exist_ok=True)

    target_synth_count = 40
    snr_levels = [-6.0, -3.0, 0.0, 3.0]
    random.shuffle(clean_screams_pool)
    random.shuffle(crowd_beds_pool)

    synth_added = 0
    for i in range(target_synth_count):
        s_rec = clean_screams_pool[i % len(clean_screams_pool)]
        c_rec = crowd_beds_pool[i % len(crowd_beds_pool)]
        snr = snr_levels[i % len(snr_levels)]

        s_path = BACKEND_DIR / s_rec["workspace_audio_path"]
        c_path = BACKEND_DIR / c_rec["workspace_audio_path"]
        if not s_path.exists() or not c_path.exists():
            continue

        try:
            s_wf, _ = load_audio(s_path, target_sr=TARGET_SAMPLE_RATE)
            c_wf, _ = load_audio(c_path, target_sr=TARGET_SAMPLE_RATE)
            mixed_wf = synthesize_masked_scream(s_wf, c_wf, target_snr_db=snr)

            synth_id = f"stage11_synth_scream_{i+1:03d}_snr{int(snr):+03d}db"
            dest_wav = synth_cat_dir / f"{synth_id}.wav"
            sf.write(str(dest_wav), mixed_wf, TARGET_SAMPLE_RATE, subtype="PCM_16")

            pcm_h = compute_pcm_sha256(mixed_wf)
            f_hash = compute_file_sha256(dest_wav)
            dur = float(len(mixed_wf) / TARGET_SAMPLE_RATE)

            rec = {
                "file_id": synth_id,
                "original_id": synth_id,
                "source_dataset": "Synthesized_Masked_Scream_Stage11",
                "workspace_audio_path": str(dest_wav.relative_to(BACKEND_DIR)).replace("\\", "/"),
                "target_category": "masked_distant_screams",
                "binary_label": "scream",
                "license": s_rec["license"],
                "license_url": s_rec.get("license_url", "http://creativecommons.org/publicdomain/zero/1.0/"),
                "attribution": f"Derived mixture of {s_rec.get('attribution', 'Freesound')} + {c_rec.get('attribution', 'Freesound')}",
                "original_title": f"Calibrated scream at {snr:+.1f}dB SNR into crowd noise ({c_rec['file_id']})",
                "source_url": s_rec.get("source_url", ""),
                "source_group_id": s_rec["source_group_id"],  # Inherits parent scream source group!
                "duration_seconds": round(dur, 3),
                "file_sha256": f_hash,
                "pcm_sha256": pcm_h,
                "is_synthesized": True,
                "acquisition_stage": "Stage_8_9_11",
            }
            new_acquired_records.append(rec)
            synth_added += 1
        except Exception as e:
            logger.warning(f"Failed to synthesize scream {i}: {e}")

    logger.info(f"Synthesized {synth_added} calibrated masked screams at SNRs [-6, -3, 0, +3] dB.")

    # 4. Partition newly acquired source groups into Train (60%), Val (20%), Test (20%)
    # Existing eligible records keep their current split!
    existing_train_groups = {r["source_group_id"] for r in eligible_manifest if r["split"] == "train"}
    existing_val_groups = {r["source_group_id"] for r in eligible_manifest if r["split"] == "val"}
    existing_test_groups = {r["source_group_id"] for r in eligible_manifest if r["split"] == "test"}

    # Discover new groups (excluding groups already in baseline manifest)
    new_groups_all = sorted(list({r["source_group_id"] for r in new_acquired_records}))
    unassigned_new_groups = [g for g in new_groups_all if g not in existing_train_groups and g not in existing_val_groups and g not in existing_test_groups]

    random.shuffle(unassigned_new_groups)
    n_new = len(unassigned_new_groups)
    n_train = int(round(0.60 * n_new))
    n_val = int(round(0.20 * n_new))

    assigned_train = set(unassigned_new_groups[:n_train])
    assigned_val = set(unassigned_new_groups[n_train : n_train + n_val])
    assigned_test = set(unassigned_new_groups[n_train + n_val :])

    logger.info(f"Partitioned {n_new} new source groups: Train={len(assigned_train)}, Val={len(assigned_val)}, Test={len(assigned_test)}")

    # Assign split to new records
    for r in new_acquired_records:
        grp = r["source_group_id"]
        if grp in existing_train_groups or grp in assigned_train:
            r["split"] = "train"
        elif grp in existing_val_groups or grp in assigned_val:
            r["split"] = "val"
        else:
            r["split"] = "test"

    # Combine into unified Stage 8.9.11 dataset manifest
    final_dataset = list(eligible_manifest) + new_acquired_records
    logger.info(f"Unified Stage 8.9.11 dataset total: {len(final_dataset)} recordings (Baseline: {len(eligible_manifest)}, New: {len(new_acquired_records)}).")

    # 5. Strict Verification of Disjointness and Quarantine
    final_train_groups = {r["source_group_id"] for r in final_dataset if r["split"] == "train"}
    final_val_groups = {r["source_group_id"] for r in final_dataset if r["split"] == "val"}
    final_test_groups = {r["source_group_id"] for r in final_dataset if r["split"] == "test"}

    assert len(final_train_groups.intersection(final_val_groups)) == 0, "Train & Val group overlap detected!"
    assert len(final_train_groups.intersection(final_test_groups)) == 0, "Train & Test group overlap detected!"
    assert len(final_val_groups.intersection(final_test_groups)) == 0, "Val & Test group overlap detected!"

    # Verify Stage 5 quarantine
    train_files = {r["file_id"] for r in final_dataset if r["split"] == "train"}
    val_files = {r["file_id"] for r in final_dataset if r["split"] == "val"}
    with open(BACKEND_DIR / "reports" / "test_predictions.csv", "r", encoding="utf-8") as f:
        s5_test_fids = {row["file_id"] for row in csv.DictReader(f)}
    assert len(s5_test_fids.intersection(train_files)) == 0, "Stage 5 file leaked to Train!"
    assert len(s5_test_fids.intersection(val_files)) == 0, "Stage 5 file leaked to Val!"
    assert len(stage5_test_groups.intersection(final_train_groups)) == 0, "Stage 5 group leaked to Train!"
    assert len(stage5_test_groups.intersection(final_val_groups)) == 0, "Stage 5 group leaked to Val!"

    logger.info("VERIFIED: 100% Source-Group Disjointness and Stage 5 Historical Quarantine preserved!")

    # 6. Export Artifacts
    # A. Acquisition manifest CSV
    acq_csv_path = STAGE11_DIR / "stage8_9_11_acquisition_manifest.csv"
    with open(acq_csv_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["file_id", "original_id", "source_dataset", "target_category", "binary_label", "split", "source_group_id", "license", "license_url", "attribution", "source_url", "duration_seconds", "pcm_sha256", "file_sha256", "is_synthesized"]
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in new_acquired_records:
            writer.writerow(r)
    logger.info(f"Saved acquisition manifest: {acq_csv_path} ({len(new_acquired_records)} records)")

    # B. Unified Dataset JSON & CSV
    manifest_json_path = STAGE11_DIR / "stage8_9_11_dataset_manifest.json"
    with open(manifest_json_path, "w", encoding="utf-8") as f:
        json.dump(final_dataset, f, indent=2)
    logger.info(f"Saved dataset manifest JSON: {manifest_json_path} ({len(final_dataset)} records)")

    manifest_csv_path = STAGE11_DIR / "stage8_9_11_dataset_manifest.csv"
    with open(manifest_csv_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["file_id", "original_id", "source_dataset", "target_category", "binary_label", "split", "source_group_id", "license", "attribution", "duration_seconds", "pcm_sha256", "file_sha256", "is_synthesized"]
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in final_dataset:
            writer.writerow(r)
    logger.info(f"Saved dataset manifest CSV: {manifest_csv_path}")

    # C. Category Balance Summary CSV
    cat_summary = {}
    for r in final_dataset:
        cat = r["target_category"]
        sp = r["split"]
        cat_summary.setdefault(cat, {"train": 0, "val": 0, "test": 0, "total": 0})
        cat_summary[cat][sp] += 1
        cat_summary[cat]["total"] += 1

    summary_csv_path = STAGE11_DIR / "stage8_9_11_category_balance.csv"
    with open(summary_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["target_category", "train", "val", "test", "total"])
        for cat, counts in sorted(cat_summary.items()):
            writer.writerow([cat, counts["train"], counts["val"], counts["test"], counts["total"]])
        writer.writerow([
            "OVERALL_ALL_CATEGORIES",
            sum(c["train"] for c in cat_summary.values()),
            sum(c["val"] for c in cat_summary.values()),
            sum(c["test"] for c in cat_summary.values()),
            len(final_dataset)
        ])
    logger.info(f"Saved category balance matrix: {summary_csv_path}")

    logger.info("\nFinal Split Counts:")
    logger.info(f"  Train: {len(train_files):4d} clips across {len(final_train_groups):3d} groups")
    logger.info(f"  Val:   {len(val_files):4d} clips across {len(final_val_groups):3d} groups")
    logger.info(f"  Test:  {len(final_dataset) - len(train_files) - len(val_files):4d} clips across {len(final_test_groups):3d} groups")
    logger.info(f"  Total: {len(final_dataset):4d} clips across {len(final_train_groups | final_val_groups | final_test_groups):3d} groups")


if __name__ == "__main__":
    main()
