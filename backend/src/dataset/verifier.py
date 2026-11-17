"""Dataset and Embedding Integrity Verifier for Stage 5 Training and Evaluation.

Validates that:
1. Every embedding in the cache corresponds to the expected recording, label, and split.
2. Source groups and content hashes do not cross partition boundaries (zero leakage).
3. The four known excluded recordings remain strictly excluded.
4. All cached features exist, load without corruption, and contain strictly finite values.
5. Cache and split manifests are fully synchronized with zero discrepancies.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np
from src.config import (
    BACKEND_DIR,
    EMBEDDINGS_DIR,
    MANIFESTS_DIR,
    YAMNet_EMBEDDING_DIM,
)
from src.dataset.split_builder import verify_no_leakage

logger = logging.getLogger("dataset_verifier")

# Explicit list of excluded recording patterns from Stages 3 and 4
EXCLUDED_PATTERNS = [
    "Fire_Loop12_SFX-KIT",
    "Alarm+8001_04.wm",
    "GunScreamer+1012_47_2",
    "HUMAN-GASP_GEN-HDF-15016",
]


class VerificationError(Exception):
    """Raised when training/evaluation input verification fails."""
    pass


def verify_manifests_and_cache(
    split_manifest_path: Optional[Path] = None,
    embedding_manifest_path: Optional[Path] = None,
    embeddings_base_dir: Optional[Path] = None,
    check_array_finiteness: bool = True,
) -> Dict[str, Any]:
    """Perform exhaustive pre-training integrity verification.

    Returns:
        Dict with summary counts and verification status.

    Raises:
        VerificationError: If any condition fails.
    """
    split_path = split_manifest_path or (MANIFESTS_DIR / "split_manifest.json")
    emb_path = embedding_manifest_path or (MANIFESTS_DIR / "embedding_manifest.json")
    cache_dir = embeddings_base_dir or EMBEDDINGS_DIR

    if not split_path.exists():
        raise VerificationError(f"Split manifest missing: {split_path}")
    if not emb_path.exists():
        raise VerificationError(f"Embedding manifest missing: {emb_path}")
    if not cache_dir.exists():
        raise VerificationError(f"Embeddings directory missing: {cache_dir}")

    with open(split_path, "r", encoding="utf-8") as f:
        split_data = json.load(f)
    with open(emb_path, "r", encoding="utf-8") as f:
        emb_data = json.load(f)

    split_records: List[Dict[str, Any]] = split_data.get("records", [])
    emb_records: List[Dict[str, Any]] = emb_data.get("embeddings", [])

    if len(split_records) == 0:
        raise VerificationError("Split manifest has zero records.")
    if len(split_records) != len(emb_records):
        raise VerificationError(
            f"Record count mismatch: split manifest has {len(split_records)}, "
            f"embedding manifest has {len(emb_records)}"
        )

    # 1. Index records by file_id
    split_by_id = {r["file_id"]: r for r in split_records}
    emb_by_id = {e["file_id"]: e for e in emb_records}

    if set(split_by_id.keys()) != set(emb_by_id.keys()):
        missing_in_emb = set(split_by_id.keys()) - set(emb_by_id.keys())
        missing_in_split = set(emb_by_id.keys()) - set(split_by_id.keys())
        raise VerificationError(
            f"Manifest ID disagreement! Missing in embedding manifest: {len(missing_in_emb)}, "
            f"missing in split manifest: {len(missing_in_split)}"
        )

    # 2. Check each record matches label, split, source group
    for file_id, s_rec in split_by_id.items():
        e_rec = emb_by_id[file_id]
        if s_rec["split"] != e_rec["split"]:
            raise VerificationError(
                f"Split mismatch for {file_id}: split manifest={s_rec['split']}, "
                f"emb manifest={e_rec['split']}"
            )
        if s_rec["binary_label"] != e_rec["binary_label"]:
            raise VerificationError(
                f"Label mismatch for {file_id}: split manifest={s_rec['binary_label']}, "
                f"emb manifest={e_rec['binary_label']}"
            )
        if s_rec["source_group_id"] != e_rec["source_group_id"]:
            raise VerificationError(
                f"Source group mismatch for {file_id}: split manifest={s_rec['source_group_id']}, "
                f"emb manifest={e_rec['source_group_id']}"
            )

    # 3. Check excluded recordings remain strictly excluded
    for file_id in split_by_id.keys():
        for pat in EXCLUDED_PATTERNS:
            if pat in file_id:
                raise VerificationError(
                    f"Excluded recording '{file_id}' (matches '{pat}') is present in dataset splits!"
                )

    # 4. Confirm zero data leakage between partitions
    splits_dict: Dict[str, List[Dict[str, Any]]] = {"train": [], "val": [], "test": []}
    for r in split_records:
        s = r["split"]
        if s in splits_dict:
            splits_dict[s].append(r)
        else:
            raise VerificationError(f"Unexpected split name '{s}' for record {r['file_id']}")

    verify_no_leakage(splits_dict)

    # 5. Verify physical cache files on disk
    expected_dim = YAMNet_EMBEDDING_DIM
    total_finite_checked = 0
    split_file_counts = {"train": 0, "val": 0, "test": 0}
    split_scream_counts = {"train": 0, "val": 0, "test": 0}

    for file_id, s_rec in split_by_id.items():
        split = s_rec["split"]
        split_file_counts[split] += 1
        if s_rec["binary_label"] == "scream":
            split_scream_counts[split] += 1

        npz_path = cache_dir / split / f"{file_id}.npz"
        if not npz_path.exists():
            raise VerificationError(f"Cache file missing on disk: {npz_path}")

        if check_array_finiteness:
            try:
                with np.load(str(npz_path)) as data:
                    # Check keys
                    for k in ["frame_embeddings", "mean_pooled", "max_pooled", "clip_embedding", "metadata"]:
                        if k not in data.files:
                            raise VerificationError(f"Cache file {npz_path} missing array key '{k}'")

                    frames = data["frame_embeddings"]
                    mean_p = data["mean_pooled"]
                    max_p = data["max_pooled"]
                    clip_emb = data["clip_embedding"]

                    # Shape checks
                    if frames.ndim != 2 or frames.shape[1] != expected_dim:
                        raise VerificationError(
                            f"Invalid frame embedding shape in {npz_path}: {frames.shape}, "
                            f"expected (*, {expected_dim})"
                        )
                    if mean_p.shape != (expected_dim,):
                        raise VerificationError(f"Invalid mean_pooled shape: {mean_p.shape}")
                    if max_p.shape != (expected_dim,):
                        raise VerificationError(f"Invalid max_pooled shape: {max_p.shape}")
                    if clip_emb.shape != (expected_dim * 2,):
                        raise VerificationError(f"Invalid clip_embedding shape: {clip_emb.shape}")

                    # Finiteness checks
                    if not np.isfinite(frames).all():
                        raise VerificationError(f"Non-finite values found in frame_embeddings: {npz_path}")
                    if not np.isfinite(clip_emb).all():
                        raise VerificationError(f"Non-finite values found in clip_embedding: {npz_path}")

                    total_finite_checked += 1
            except Exception as e:
                if isinstance(e, VerificationError):
                    raise
                raise VerificationError(f"Error loading cache file {npz_path}: {e}") from e

    summary = {
        "status": "verified_clean",
        "total_records": len(split_records),
        "split_counts": split_file_counts,
        "scream_counts": split_scream_counts,
        "cache_files_checked": total_finite_checked,
        "leakage_detected": False,
        "excluded_recordings_confirmed_absent": True,
    }
    return summary
