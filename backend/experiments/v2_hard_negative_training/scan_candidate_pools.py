"""Scan candidate audio pools across FSD50K, Stage 8.8 reviewed recordings, OpenSLR99, and NIGENS.

Audits candidate counts, licenses, and verifies file accessibility on disk.
"""

from __future__ import annotations

import csv
import json
import logging
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.config import DEFAULT_NIGENS_DIR, DEFAULT_OPENSLR99_DIR, FSD50K_DIR

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("scan_candidate_pools")


def main():
    logger.info("Scanning available candidate audio pools for Stage 8.9.5...")

    # 1. Stage 8.9 Reviewed database
    db_path = BACKEND_DIR / "database" / "stage8_9_reviews.db"
    reviewed_candidates = []
    if db_path.exists():
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM candidates WHERE local_path IS NOT NULL AND local_path != ''")
        for r in cur.fetchall():
            d = dict(r)
            p = Path(d["local_path"])
            if not p.is_absolute():
                p = BACKEND_DIR / p
            if p.exists():
                d["resolved_audio_path"] = str(p)
                reviewed_candidates.append(d)
        conn.close()
    logger.info(f"Stage 8.9 Review Database: {len(reviewed_candidates)} usable reviewed audio files with local audio on disk.")

    # Breakdown by category
    cat_counts = {}
    for c in reviewed_candidates:
        cat = c["proposed_category"] or "unclassified"
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    for cat, count in sorted(cat_counts.items()):
        logger.info(f"  Stage 8.9: {cat:30}: {count:3d} clips")

    # 2. OpenSLR99 and NIGENS Screams
    openslr_dir = Path(DEFAULT_OPENSLR99_DIR)
    openslr_screams = list((openslr_dir / "screaming").glob("*.wav")) if (openslr_dir / "screaming").exists() else []
    logger.info(f"OpenSLR99 Screaming: {len(openslr_screams)} files at {openslr_dir / 'screaming'}")

    nigens_dir = Path(DEFAULT_NIGENS_DIR)
    nigens_female_screams = list((nigens_dir / "femaleScream").glob("*.wav")) if (nigens_dir / "femaleScream").exists() else []
    nigens_male_screams = list((nigens_dir / "maleScream").glob("*.wav")) if (nigens_dir / "maleScream").exists() else []
    logger.info(f"NIGENS Screams: {len(nigens_female_screams)} female, {len(nigens_male_screams)} male at {nigens_dir}")

    # 3. FSD50K Dev Audio
    fsd50k_audio_dir = Path(r"E:\FSD50K.dev_audio\FSD50K.dev_audio")
    fsd50k_meta_path = Path(r"E:\FSD50K.dev_audio\FSD50K.metadata\dev_clips_info_FSD50K.json")
    fsd50k_ground_truth_path = Path(r"E:\FSD50K.dev_audio\FSD50K.ground_truth\dev.csv")

    fsd50k_available = fsd50k_audio_dir.exists() and fsd50k_meta_path.exists() and fsd50k_ground_truth_path.exists()
    logger.info(f"FSD50K Dev Audio repository present on E: drive: {fsd50k_available}")

    if fsd50k_available:
        with open(fsd50k_meta_path, "r", encoding="utf-8") as f:
            dev_meta = json.load(f)
        logger.info(f"FSD50K Metadata loaded: {len(dev_meta)} clip records.")

        target_fsd50k_classes = {
            "Screaming": "scream",
            "Shout": "shouting_and_speech",
            "Yell": "shouting_and_speech",
            "Speech": "shouting_and_speech",
            "Child_speech_and_kid_speaking": "shouting_and_speech",
            "Squeak": "whistles_and_squeaks",
            "Alarm": "sfx_sirens_fireworks",
            "Siren": "sfx_sirens_fireworks",
            "Fireworks": "sfx_sirens_fireworks",
            "Crying_and_sobbing": "infant_crying",
            "Crowd": "crowd_chant_cheering",
            "Applause": "crowd_chant_cheering",
            "Cheering": "crowd_chant_cheering",
        }

        fsd50k_candidates_by_class = {c: [] for c in target_fsd50k_classes}

        with open(fsd50k_ground_truth_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                fname = row["fname"]
                labels = [l.strip() for l in row["labels"].split(",")]
                audio_file = fsd50k_audio_dir / f"{fname}.wav"
                if audio_file.exists():
                    clip_meta = dev_meta.get(fname, {})
                    for tc in target_fsd50k_classes:
                        if tc in labels:
                            fsd50k_candidates_by_class[tc].append({
                                "fname": fname,
                                "path": str(audio_file),
                                "labels": labels,
                                "meta": clip_meta,
                            })

        for tc, clips in fsd50k_candidates_by_class.items():
            mapped_cat = target_fsd50k_classes[tc]
            logger.info(f"  FSD50K: {tc:30} -> {mapped_cat:25}: {len(clips):4d} WAV files confirmed on disk")


if __name__ == "__main__":
    main()
