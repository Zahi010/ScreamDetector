"""Feature and Label Loader for Cached YAMNet Embeddings.

Provides structured access to cached feature representations:
- 'clip_embedding': 2,048-dimensional concatenation of mean-pooled and max-pooled vectors.
- 'mean_pooled': 1,024-dimensional mean across frames.
- 'max_pooled': 1,024-dimensional max across frames.
- 'frame_embeddings': sequence of (N_frames, 1024) arrays per recording.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Literal, Tuple, Union

import numpy as np
from src.config import EMBEDDINGS_DIR, MANIFESTS_DIR

FeatureType = Literal["clip_embedding", "mean_pooled", "max_pooled", "frame_embeddings"]


def load_dataset_split(
    split: str,
    feature_type: FeatureType = "clip_embedding",
    manifest_path: Path | None = None,
    cache_base_dir: Path | None = None,
) -> Tuple[Union[np.ndarray, List[np.ndarray]], np.ndarray, List[Dict[str, Any]]]:
    """Load cached features, binary labels, and recording metadata for a given partition.

    Args:
        split: 'train', 'val', or 'test'.
        feature_type: 'clip_embedding' (2048), 'mean_pooled' (1024), 'max_pooled' (1024),
                      or 'frame_embeddings' (variable length sequences).
        manifest_path: Path to split_manifest.json.
        cache_base_dir: Base directory containing split subdirectories of .npz files.

    Returns:
        X: Feature array of shape (N, D) for pooled features, or list of (N_i, 1024) arrays for frame features.
        y: Binary integer labels (0 = non_scream, 1 = scream) of shape (N,).
        metadata: List of recording metadata dicts.
    """
    manifest_file = manifest_path or (MANIFESTS_DIR / "split_manifest.json")
    cache_dir = cache_base_dir or EMBEDDINGS_DIR

    if not manifest_file.exists():
        raise FileNotFoundError(f"Split manifest not found: {manifest_file}")

    with open(manifest_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = [r for r in data.get("records", []) if r.get("split") == split]
    if not records:
        raise ValueError(f"No records found for split '{split}' in manifest {manifest_file}")

    split_cache_dir = cache_dir / split
    if not split_cache_dir.exists():
        raise FileNotFoundError(f"Split cache directory missing: {split_cache_dir}")

    features_list: List[np.ndarray] = []
    labels_list: List[int] = []
    metadata_list: List[Dict[str, Any]] = []

    for r in records:
        file_id = r["file_id"]
        npz_file = split_cache_dir / f"{file_id}.npz"
        if not npz_file.exists():
            raise FileNotFoundError(f"Missing cache file: {npz_file}")

        with np.load(str(npz_file)) as npz_data:
            feat = npz_data[feature_type]
            features_list.append(feat)

        binary_label = 1 if r["binary_label"] == "scream" else 0
        labels_list.append(binary_label)
        metadata_list.append(
            {
                "file_id": file_id,
                "dataset_name": r["dataset_name"],
                "relative_path": r["relative_path"],
                "binary_label": r["binary_label"],
                "source_group_id": r["source_group_id"],
                "duration_seconds": r["duration_seconds"],
                "split": split,
            }
        )

    y = np.array(labels_list, dtype=np.int32)

    if feature_type == "frame_embeddings":
        return features_list, y, metadata_list

    X = np.stack(features_list, axis=0).astype(np.float32)
    return X, y, metadata_list
