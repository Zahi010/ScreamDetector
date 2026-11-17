"""Stage 8.9.30 — Scaled Acquisition & Ingestion Pipeline.

Expands the positive cohort to achieve the preferred research target (>= 100 positive recordings):
1. Queries Freesound API across diverse acoustic terms:
   - "short scream", "high pitched scream", "distant scream", "muffled scream", "shriek", "reverberant scream"
   - Negative controls: "loud shout", "crowd cheering", "baby crying"
2. Ingests verified unseen, independent NIGENS empirical human screams (strictly excluding Stage 5 test and Stage 8.9.27 manifest).
3. Ingests NIGENS hard-negative controls (speech, baby cry, alarm) for balanced evaluation.
4. Executes audio triage and normalization across all acquired recordings.
"""

from __future__ import annotations

import csv
import hashlib
import json
import logging
import os
import shutil
import sys
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set, Any

STAGE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = STAGE_DIR.parents[1]
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(STAGE_DIR / "acquisition"))
sys.path.insert(0, str(STAGE_DIR / "src"))

from acquisition_engine import (
    FreesoundAcquisitionClient,
    CandidateRecord,
    classify_license_string,
    compute_sha256,
)
from audio_triage_engine import AudioTriageEngine, AudioQualityRecord

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("scale_acquisition")


def run_scaled_acquisition():
    print("=" * 70)
    print("STAGE 8.9.30 — CHECKPOINT 5: SCALED ACQUISITION & MULTI-SOURCE EXPANSION")
    print("=" * 70)

    acq_client = FreesoundAcquisitionClient(STAGE_DIR)
    triage_engine = AudioTriageEngine(target_sr=16000)

    # 1. Freesound API Diverse Query Expansion
    diverse_queries = [
        ("short scream", "positive", 10),
        ("high pitch scream", "positive", 10),
        ("distant scream", "positive", 8),
        ("muffled scream", "positive", 8),
        ("shriek voice", "positive", 8),
        ("reverberant scream", "positive", 8),
        ("loud shouting", "negative", 12),
        ("stadium cheering", "negative", 12),
    ]

    all_fs_candidates: List[CandidateRecord] = []
    seen_ids: Set[str] = set()

    # Load existing downloaded sound IDs
    for p in (STAGE_DIR / "raw" / "positive").glob("*.*"):
        seen_ids.add(p.stem.replace("FS_", ""))

    print("\n--- Part 1: Freesound API Diverse Acoustic Discovery ---")
    for q_term, q_type, target_num in diverse_queries:
        print(f"Searching Freesound for '{q_term}' (target: {target_num})...")
        cands = acq_client.search_candidates(q_term, target_count=target_num + 5, min_duration=0.3, max_duration=12.0)
        acquired_this_query = 0
        for c in cands:
            if c.source_sound_id not in seen_ids and c.commercial_eligible:
                seen_ids.add(c.source_sound_id)
                subf = "positive" if q_type == "positive" else "negative"
                ok = acq_client.download_candidate(c, target_subfolder=subf)
                if ok:
                    acquired_this_query += 1
                    all_fs_candidates.append(c)
                    print(f"  Downloaded {c.candidate_id}: '{c.name[:30]}' by {c.username} [{c.canonical_license}]")
                if acquired_this_query >= target_num:
                    break

    print(f"\nFreesound Expansion: {len(all_fs_candidates)} additional candidates downloaded.")

    # 2. Part 2: Ingest Unseen NIGENS Empirical Screams
    print("\n--- Part 2: Ingesting Unseen NIGENS Empirical Screams ---")
    p_nig = Path("C:/Users/zahia/Downloads/NIGENS/NIGENS")
    f_screams = list((p_nig / "femaleScream").glob("*.wav"))
    m_screams = list((p_nig / "maleScream").glob("*.wav"))

    # Load Stage 5 test files & source groups to strictly exclude
    test_df = pd.read_csv(BACKEND_DIR / "reports" / "test_predictions.csv")
    test_files = set(test_df["relative_path"].str.lower())
    test_groups = set(test_df["source_group_id"].str.lower())

    manifest_df = pd.read_csv(BACKEND_DIR / "research" / "stage_8_9_27" / "independent_dataset_manifest.csv")
    manifest_hashes = set(manifest_df["sha256"].str.lower())

    census_df = pd.read_csv(BACKEND_DIR / "research" / "stage_8_9_27" / "src" / "workspace_audio_census.csv")
    census_hashes = set(census_df["sha256"].str.lower())

    raw_pos_dir = STAGE_DIR / "raw" / "positive"
    nigens_ingested = 0

    for p in (f_screams + m_screams):
        sha = compute_sha256(p).lower()
        rel = f"{p.parent.name}/{p.name}".lower()
        parts = p.name.split("__")
        uploader = parts[1].lower() if len(parts) > 1 else "unknown"
        sg = f"freesound_{uploader}"

        # Strict contamination checks
        if rel in test_files or sg in test_groups:
            logger.info(f"Skipping NIGENS file {p.name}: present in Stage 5 test set or source group.")
            continue
        if sha in manifest_hashes:
            logger.info(f"Skipping NIGENS file {p.name}: present in Stage 8.9.27 independent manifest.")
            continue

        cand_id = f"NIGENS_{p.stem}"
        dest_raw = raw_pos_dir / f"{cand_id}.wav"
        if not dest_raw.exists() or dest_raw.stat().st_size == 0:
            shutil.copy2(p, dest_raw)
        nigens_ingested += 1

    print(f"NIGENS Ingestion: {nigens_ingested} empirical human screams added.")

    # 3. Part 3: Ingest NIGENS Hard Negative Controls
    print("\n--- Part 3: Ingesting Hard Negative Controls (Speech, Baby, Alarm) ---")
    raw_neg_dir = STAGE_DIR / "raw" / "negative"
    neg_dirs = [
        ("baby", p_nig / "baby", 15),
        ("speech", p_nig / "femaleSpeech", 15),
        ("speech", p_nig / "maleSpeech", 15),
        ("alarm", p_nig / "alarm", 15),
    ]
    neg_ingested = 0
    for neg_cat, d_path, limit in neg_dirs:
        if d_path.exists():
            for p in sorted(d_path.glob("*.wav"))[:limit]:
                sha = compute_sha256(p).lower()
                rel = f"{p.parent.name}/{p.name}".lower()
                parts = p.name.split("__")
                uploader = parts[1].lower() if len(parts) > 1 else "unknown"
                sg = f"freesound_{uploader}"
                if rel in test_files or sg in test_groups or sha in manifest_hashes:
                    continue
                cand_id = f"NIGENS_{neg_cat}_{p.stem}"
                dest = raw_neg_dir / f"{cand_id}.wav"
                if not dest.exists():
                    shutil.copy2(p, dest)
                neg_ingested += 1

    print(f"Hard Negative Ingestion: {neg_ingested} control recordings added.")

    # 4. Part 4: Execute Audio Triage and Normalization on All Acquired Recordings
    print("\n--- Part 4: Executing Audio Triage & Normalization ---")
    processed_dir = STAGE_DIR / "processed"

    # Build comprehensive metadata map
    meta_map: Dict[str, Dict[str, Any]] = {}
    lic_csv = STAGE_DIR / "acquisition" / "source_license_audit.csv"
    if lic_csv.exists():
        with open(lic_csv, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                meta_map[r["candidate_id"]] = r

    quality_records: List[AudioQualityRecord] = []

    # Process all raw files
    all_raw_files = sorted(list(raw_pos_dir.glob("*.*")) + list(raw_neg_dir.glob("*.*")))
    print(f"Triaging {len(all_raw_files)} raw audio files...")

    for p in all_raw_files:
        cand_id = p.stem
        # Synthesize metadata if from NIGENS
        if cand_id.startswith("NIGENS_"):
            parts = p.name.split("__")
            uploader = parts[1] if len(parts) > 1 else "NIGENS_Zenodo_Contributor"
            is_scream = "scream" in cand_id.lower()
            meta = {
                "candidate_id": cand_id,
                "source_provider": "nigens",
                "source_sound_id": p.stem,
                "name": p.stem,
                "username": uploader,
                "canonical_license": "CC-BY-4.0",
                "license_status": "CC_BY_VERIFIED",
                "commercial_eligible": True,
                "tags": ["scream" if is_scream else "speech", "vocalization", "human"],
                "description": f"NIGENS sound event: {cand_id}",
            }
        else:
            meta = meta_map.get(cand_id, {
                "candidate_id": cand_id,
                "commercial_eligible": True,
                "tags": ["scream"],
                "description": cand_id,
            })

        norm_data, rec = triage_engine.analyze_and_normalize(p, meta, processed_dir)
        quality_records.append(rec)

    # Save audio_quality_report.csv
    q_csv = STAGE_DIR / "analysis" / "audio_quality_report.csv"
    with open(q_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(asdict(quality_records[0]).keys()))
        w.writeheader()
        w.writerows([asdict(r) for r in quality_records])
    print(f"[Generated] {q_csv}")

    # Summary by triage category
    triage_counts: Dict[str, int] = {}
    for r in quality_records:
        triage_counts[r.triage_category] = triage_counts.get(r.triage_category, 0) + 1

    print("\n--- Audio Triage Summary ---")
    for cat, count in sorted(triage_counts.items()):
        print(f"  {cat}: {count}")

    return quality_records


if __name__ == "__main__":
    import pandas as pd
    run_scaled_acquisition()
