"""Hard-Negative Data Ingestion, Duplicate Detection, and Review Pipeline (Stage 6).

Implements:
1. Auditable ingestion of candidate hard-negative and genuine scream recordings.
2. Normalization to mono, 16 kHz, float32 without modifying original source files.
3. Content-hash computation (file SHA-256 and PCM SHA-256) and collision detection against existing datasets.
4. Source-group tracking to guarantee acoustic isolation across partitions.
5. Strict review status tracking ('pending_review', 'approved_non_scream', 'approved_scream', 'rejected_ambiguous').
6. License tracking and commercial use restriction auditing.
"""

from __future__ import annotations

import csv
import hashlib
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

from src.audio.preprocessor import load_audio
from src.config import (
    BACKEND_DIR,
    DATA_DIR,
    HARD_NEGATIVES_DIR,
    HARD_NEGATIVES_FALLBACK_DIR,
    HARD_NEGATIVES_MANIFEST,
    HARD_NEGATIVES_REVIEW_CSV,
    MANIFESTS_DIR,
    PROJECT_ROOT,
    TARGET_SAMPLE_RATE,
)

logger = logging.getLogger("hard_negatives")

# Standardized Hard-Negative Sound Taxonomy
HARD_NEGATIVE_CATEGORIES = {
    "festival_whistle": "Rave whistles, referee whistles, vuvuzelas, party noisemakers",
    "crowd_cheering": "Stadium applause, celebratory shouts, concert cheering, festival chants",
    "music_and_effects": "EDM bass drops, synth risers, distorted vocals, microphone feedback",
    "vocal_non_scream": "Crying, laughing, coughing, loud conversation, spoken shouting",
    "sfx_transients": "Sirens, bells, car horns, squeaky toys, electronic phone ringing",
    "environmental_noise": "Wind gusts, mic handling, cable pops, crowd murmur, outdoor rumble",
    "genuine_scream": "Verified distress vocalizations from newly collected sources",
}

REVIEW_STATUSES = {
    "pending_review": "Ingested but awaiting human listening verification. Kept out of training.",
    "approved_non_scream": "Human-verified as non-scream audio. Eligible for negative training set.",
    "approved_scream": "Human-verified as genuine distress scream. Eligible for positive training set.",
    "rejected_ambiguous": "Unclear acoustic intent, mixed cheer/scream, or licensing defect. Excluded.",
}

# Known non-commercial licenses requiring explicit flag
NON_COMMERCIAL_LICENSES = {"CC BY-NC 4.0", "CC BY-NC-ND 4.0", "CC BY-NC-SA 4.0", "NC"}


class DuplicateClipError(Exception):
    """Raised when an ingested file has an exact content hash collision with existing data."""
    pass


class InvalidCategoryError(ValueError):
    """Raised when a clip is categorized with an unrecognized sound event category."""
    pass


class IngestionValidationError(ValueError):
    """Raised when audio metadata or review constraints are violated."""
    pass


def compute_file_sha256(filepath: Path) -> str:
    """Compute SHA-256 hash of a file on disk."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def compute_pcm_sha256(waveform: np.ndarray) -> str:
    """Compute deterministic SHA-256 of int16-quantized PCM waveform data."""
    int16_samples = np.clip(waveform * 32767.0, -32768, 32767).astype(np.int16)
    return hashlib.sha256(int16_samples.tobytes()).hexdigest()


def load_existing_dataset_hashes(manifests_dir: Optional[Path] = None) -> Set[str]:
    """Collect all known SHA-256 hashes from existing dataset manifests to prevent duplicate ingestion."""
    m_dir = manifests_dir or MANIFESTS_DIR
    hashes: Set[str] = set()

    # 1. From dataset_manifest.json (Stage 3)
    ds_manifest = m_dir / "dataset_manifest.json"
    if ds_manifest.exists():
        try:
            with open(ds_manifest, "r", encoding="utf-8") as f:
                data = json.load(f)
            for r in data.get("records", []):
                if "sha256_hash" in r:
                    hashes.add(r["sha256_hash"])
        except Exception as e:
            logger.warning(f"Could not load hashes from {ds_manifest}: {e}")

    # 2. From split_manifest.json (Stage 4)
    split_manifest = m_dir / "split_manifest.json"
    if split_manifest.exists():
        try:
            with open(split_manifest, "r", encoding="utf-8") as f:
                data = json.load(f)
            for r in data.get("records", []):
                if "sha256_hash" in r:
                    hashes.add(r["sha256_hash"])
        except Exception as e:
            logger.warning(f"Could not load hashes from {split_manifest}: {e}")

    # 3. From hard_negatives_manifest.json (if previously created)
    hn_manifest = m_dir / "hard_negatives_manifest.json"
    if hn_manifest.exists():
        try:
            with open(hn_manifest, "r", encoding="utf-8") as f:
                data = json.load(f)
            for r in data.get("records", []):
                if "sha256_hash" in r:
                    hashes.add(r["sha256_hash"])
        except Exception as e:
            logger.warning(f"Could not load hashes from {hn_manifest}: {e}")

    return hashes


def infer_source_group(filepath: Path, sidecar_meta: Optional[Dict[str, Any]] = None) -> str:
    """Infer source-group identity to prevent recording pack leakage."""
    if sidecar_meta and sidecar_meta.get("source_group_id"):
        return str(sidecar_meta["source_group_id"]).strip()

    name = filepath.stem
    # 1. Freesound standard naming: {sound_id}__{author}__{title}
    if "__" in name:
        parts = name.split("__")
        if len(parts) >= 2:
            return f"freesound_{parts[1]}"

    # 2. Pack prefix matching
    m = re.match(r"^([A-Za-z0-9\-]+)[+_]", name)
    if m:
        return f"pack_{m.group(1)}"

    # Default to parent folder name + stem prefix
    return f"group_{filepath.parent.name}_{name[:8]}"


def ingest_audio_clip(
    wav_path: Path,
    existing_hashes: Set[str],
    category_override: Optional[str] = None,
    sidecar_meta: Optional[Dict[str, Any]] = None,
    check_duplicates: bool = True,
) -> Dict[str, Any]:
    """Ingest a single candidate WAV file into the hard-negative schema without altering original audio.

    Args:
        wav_path: Path to the WAV file.
        existing_hashes: Set of known SHA-256 hashes for collision detection.
        category_override: Explicit sound category from HARD_NEGATIVE_CATEGORIES.
        sidecar_meta: Optional pre-existing metadata dict.
        check_duplicates: If True, raises DuplicateClipError on exact hash collision.

    Returns:
        Dict adhering to the hard-negative record schema.
    """
    if not wav_path.exists():
        raise FileNotFoundError(f"Candidate audio file not found: {wav_path}")
    if wav_path.suffix.lower() != ".wav":
        raise IngestionValidationError(f"File must be a WAV file, got: {wav_path.suffix}")

    # Compute file-level SHA256
    file_sha256 = compute_file_sha256(wav_path)
    if check_duplicates and file_sha256 in existing_hashes:
        raise DuplicateClipError(
            f"File '{wav_path.name}' has exact SHA-256 hash collision ({file_sha256}) with an existing dataset clip."
        )

    # Normalize audio using existing preprocessing pipeline
    waveform, meta = load_audio(wav_path, target_sr=TARGET_SAMPLE_RATE)
    pcm_sha256 = compute_pcm_sha256(waveform)

    # Read companion sidecar JSON if present (e.g., clip.json or clip.wav.json)
    sidecar = sidecar_meta or {}
    if not sidecar:
        sidecar_candidate_1 = wav_path.with_suffix(".json")
        sidecar_candidate_2 = wav_path.parent / f"{wav_path.name}.json"
        for sc in [sidecar_candidate_1, sidecar_candidate_2]:
            if sc.exists():
                try:
                    with open(sc, "r", encoding="utf-8") as f:
                        sidecar = json.load(f)
                    break
                except Exception as e:
                    logger.warning(f"Could not parse sidecar JSON {sc}: {e}")

    # Determine category
    cat = category_override or sidecar.get("sound_category")
    if not cat:
        # Check if parent folder name matches a category
        parent_name = wav_path.parent.name.lower()
        if parent_name in HARD_NEGATIVE_CATEGORIES:
            cat = parent_name
        else:
            cat = "environmental_noise"  # Default generic fallback requiring review

    if cat not in HARD_NEGATIVE_CATEGORIES:
        raise InvalidCategoryError(
            f"Invalid category '{cat}'. Must be one of: {list(HARD_NEGATIVE_CATEGORIES.keys())}"
        )

    # Determine source group
    source_group = infer_source_group(wav_path, sidecar)

    # License and commercial use tracking
    license_str = str(sidecar.get("license", "Unspecified / Needs Verification")).strip()
    commercial_ok = sidecar.get("commercial_use_permitted")
    if commercial_ok is None:
        commercial_ok = False if any(nc in license_str.upper() for nc in ["-NC", "NON-COMMERCIAL", "NC-ND"]) else (license_str in ["CC0 1.0", "CC BY 4.0", "Public Domain"])

    proposed_label = "scream" if cat == "genuine_scream" else "non_scream"
    review_status = sidecar.get("review_status", "pending_review")
    if review_status not in REVIEW_STATUSES:
        review_status = "pending_review"

    # Slug for unique file_id
    clean_stem = re.sub(r"[^A-Za-z0-9_\-]", "_", wav_path.stem)
    file_id = f"hn_{cat}_{source_group}_{clean_stem}"

    record = {
        "file_id": file_id,
        "original_filename": wav_path.name,
        "source_path": str(wav_path.resolve()),
        "relative_to_root": str(wav_path.resolve().relative_to(PROJECT_ROOT)).replace("\\", "/") if PROJECT_ROOT in wav_path.resolve().parents else wav_path.name,
        "sha256_hash": file_sha256,
        "pcm_sha256": pcm_sha256,
        "sound_category": cat,
        "source": sidecar.get("source", "Local Ingestion"),
        "source_group_id": source_group,
        "license": license_str,
        "commercial_use_permitted": bool(commercial_ok),
        "duration_seconds": round(meta.duration_seconds, 3),
        "original_sample_rate": meta.original_sample_rate,
        "original_channels": meta.original_channels,
        "target_sample_rate": TARGET_SAMPLE_RATE,
        "num_samples": len(waveform),
        "peak_amplitude": round(meta.peak_amplitude, 4),
        "rms_energy": round(meta.rms_energy, 4),
        "proposed_label": proposed_label,
        "review_status": review_status,
        "label_confidence": sidecar.get("label_confidence", "medium"),
        "reviewer_notes": sidecar.get("reviewer_notes", "Awaiting listening review"),
        "reviewed_at": sidecar.get("reviewed_at", None),
        "reviewer_id": sidecar.get("reviewer_id", None),
        "ingested_at": datetime.now().isoformat(),
    }

    return record


def scan_and_ingest_hard_negatives(
    input_dirs: Optional[List[Path]] = None,
    manifest_path: Optional[Path] = None,
    review_csv_path: Optional[Path] = None,
    allow_empty: bool = True,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Scan candidate directories and ingest new audio files, generating review CSV and manifest."""
    dirs_to_check: List[Path] = []
    if input_dirs:
        dirs_to_check.extend(input_dirs)
    else:
        dirs_to_check.append(HARD_NEGATIVES_DIR)
        dirs_to_check.append(HARD_NEGATIVES_FALLBACK_DIR)

    target_manifest = manifest_path or HARD_NEGATIVES_MANIFEST
    target_csv = review_csv_path or HARD_NEGATIVES_REVIEW_CSV

    # Gather WAV files from all target directories
    discovered_wavs: List[Path] = []
    existing_dir_paths: List[Path] = []

    for d in dirs_to_check:
        if d.exists() and d.is_dir():
            existing_dir_paths.append(d)
            for wav in d.glob("**/*.wav"):
                if wav.name != ".gitkeep":
                    discovered_wavs.append(wav)

    summary = {
        "directories_checked": [str(p) for p in existing_dir_paths],
        "wav_files_found": len(discovered_wavs),
        "ingested_count": 0,
        "duplicates_skipped": 0,
        "errors": [],
    }

    # If empty, report honestly without fabricating
    if len(discovered_wavs) == 0:
        logger.info(f"Hard negative directories are currently empty: {[str(d) for d in existing_dir_paths]}")
        # Save empty/initial manifest with honest metadata
        target_manifest.parent.mkdir(parents=True, exist_ok=True)
        with open(target_manifest, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "metadata": {
                        "total_records": 0,
                        "approved_non_scream": 0,
                        "approved_scream": 0,
                        "pending_review": 0,
                        "rejected_ambiguous": 0,
                        "status": "empty_pending_collection",
                        "updated_at": datetime.now().isoformat(),
                    },
                    "records": [],
                },
                f,
                indent=2,
            )
        save_review_csv([], target_csv)
        return [], summary

    # Load existing hashes to prevent duplicates
    existing_hashes = load_existing_dataset_hashes()

    # Load previously ingested hard negatives to preserve reviews
    previous_reviews: Dict[str, Dict[str, Any]] = {}
    if target_manifest.exists():
        try:
            with open(target_manifest, "r", encoding="utf-8") as f:
                prev_data = json.load(f)
            for r in prev_data.get("records", []):
                previous_reviews[r["sha256_hash"]] = r
        except Exception as e:
            logger.warning(f"Could not load previous hard negatives manifest: {e}")

    records: List[Dict[str, Any]] = []

    for wav in sorted(discovered_wavs):
        file_sha = compute_file_sha256(wav)

        # Check if already in previous hard negatives manifest
        if file_sha in previous_reviews:
            # Preserve existing review decision
            records.append(previous_reviews[file_sha])
            continue

        # Check collision with baseline dataset
        if file_sha in existing_hashes:
            summary["duplicates_skipped"] += 1
            summary["errors"].append(f"Skipped duplicate: {wav.name} (SHA-256 collision with existing dataset)")
            continue

        try:
            rec = ingest_audio_clip(wav, existing_hashes=existing_hashes)
            records.append(rec)
            existing_hashes.add(file_sha)
            summary["ingested_count"] += 1
        except Exception as e:
            summary["errors"].append(f"Failed to ingest {wav.name}: {e}")

    # Save manifest and review CSV
    save_hard_negatives_manifest(records, target_manifest, target_csv)

    return records, summary


def save_review_csv(records: List[Dict[str, Any]], csv_path: Path) -> None:
    """Save review records into a human-editable CSV."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "file_id",
        "original_filename",
        "sound_category",
        "source_group_id",
        "license",
        "commercial_use_permitted",
        "duration_seconds",
        "proposed_label",
        "review_status",
        "label_confidence",
        "reviewer_notes",
        "reviewed_at",
        "reviewer_id",
        "source_path",
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            writer.writerow({k: r.get(k, "") for k in fieldnames})


def save_hard_negatives_manifest(
    records: List[Dict[str, Any]],
    manifest_path: Path,
    csv_path: Path,
) -> None:
    """Save hard-negative records to JSON manifest and review CSV."""
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    counts = {
        "total_records": len(records),
        "approved_non_scream": sum(1 for r in records if r.get("review_status") == "approved_non_scream"),
        "approved_scream": sum(1 for r in records if r.get("review_status") == "approved_scream"),
        "pending_review": sum(1 for r in records if r.get("review_status") == "pending_review"),
        "rejected_ambiguous": sum(1 for r in records if r.get("review_status") == "rejected_ambiguous"),
    }

    manifest_data = {
        "metadata": {
            **counts,
            "updated_at": datetime.now().isoformat(),
            "categories_supported": list(HARD_NEGATIVE_CATEGORIES.keys()),
            "review_statuses_supported": list(REVIEW_STATUSES.keys()),
        },
        "records": records,
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    save_review_csv(records, csv_path)


def load_approved_hard_negatives(
    manifest_path: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """Load only human-reviewed and approved recordings.

    Strictly excludes 'pending_review' and 'rejected_ambiguous'.
    """
    target = manifest_path or HARD_NEGATIVES_MANIFEST
    if not target.exists():
        return []

    with open(target, "r", encoding="utf-8") as f:
        data = json.load(f)

    approved = [
        r for r in data.get("records", [])
        if r.get("review_status") in ["approved_non_scream", "approved_scream"]
    ]
    return approved
