"""Unit tests for Stage 4 unified manifest generation, leakage-safe splits, and embedding caching."""

import json
import numpy as np
import pytest
import soundfile as sf
from pathlib import Path

from src.dataset.split_builder import (
    LeakageError,
    build_unified_manifest,
    create_leakage_safe_splits,
    verify_no_leakage,
)
from scripts.extract_embeddings import is_cache_entry_valid


def test_unified_manifest_exclusions(tmp_path):
    """Verify that records tagged with review_flags or needs_review are excluded."""
    # Create dummy stage 3 manifest
    records = [
        {
            "file_id": "clean_scream",
            "dataset_name": "Test",
            "relative_path": "clean_scream.wav",
            "binary_label": "scream",
            "review_flags": [],
            "sha256_hash": "hash1",
            "source_group_id": "speaker_1",
        },
        {
            "file_id": "review_file",
            "dataset_name": "Test",
            "relative_path": "review.wav",
            "binary_label": "needs_review",
            "review_flags": ["some_review_flag"],
            "sha256_hash": "hash2",
            "source_group_id": "speaker_2",
        },
        {
            "file_id": "dup_copy",
            "dataset_name": "Test",
            "relative_path": "dup.wav",
            "binary_label": "non_scream",
            "review_flags": ["exact_file_duplicate_copy"],
            "sha256_hash": "hash3",
            "source_group_id": "speaker_3",
        },
    ]
    st3_path = tmp_path / "stage3_manifest.json"
    with open(st3_path, "w", encoding="utf-8") as f:
        json.dump(records, f)

    eligible, excluded = build_unified_manifest(st3_path, verify_file_integrity=False)

    assert len(eligible) == 1
    assert eligible[0]["file_id"] == "clean_scream"
    assert len(excluded) == 2
    ex_ids = [x["file_id"] for x in excluded]
    assert "review_file" in ex_ids
    assert "dup_copy" in ex_ids


def test_leakage_safe_split_isolation():
    """Verify source-group isolation: all recordings sharing a group stay in the same split."""
    records = []
    # 10 groups, each group having 3 records (some scream, some non-scream)
    for g_idx in range(10):
        gid = f"group_{g_idx}"
        for r_idx in range(3):
            lbl = "scream" if g_idx < 4 else "non_scream"
            records.append({
                "file_id": f"file_{g_idx}_{r_idx}",
                "binary_label": lbl,
                "source_group_id": gid,
                "sha256_hash": f"hash_{g_idx}_{r_idx}",
            })

    splits = create_leakage_safe_splits(records, seed=42)

    train_groups = set(r["source_group_id"] for r in splits["train"])
    val_groups = set(r["source_group_id"] for r in splits["val"])
    test_groups = set(r["source_group_id"] for r in splits["test"])

    # Overlaps must be completely empty
    assert len(train_groups & val_groups) == 0
    assert len(train_groups & test_groups) == 0
    assert len(val_groups & test_groups) == 0

    # Total groups preserved
    assert len(train_groups | val_groups | test_groups) == 10

    # verify_no_leakage returns True
    assert verify_no_leakage(splits) is True


def test_leakage_detection_raises_error():
    """Verify that verify_no_leakage raises LeakageError if groups or hashes bleed across splits."""
    leaking_splits = {
        "train": [
            {"file_id": "f1", "source_group_id": "group_A", "sha256_hash": "hash1"},
            {"file_id": "f2", "source_group_id": "group_B", "sha256_hash": "hash2"},
        ],
        "val": [
            {"file_id": "f3", "source_group_id": "group_A", "sha256_hash": "hash3"},  # Leaking group_A!
        ],
        "test": [
            {"file_id": "f4", "source_group_id": "group_C", "sha256_hash": "hash4"},
        ],
    }

    with pytest.raises(LeakageError):
        verify_no_leakage(leaking_splits)


def test_cache_validation_and_invalidation(tmp_path):
    """Verify is_cache_entry_valid checks finite values, shapes, and hash matches."""
    npz_file = tmp_path / "test_cache.npz"

    frames = np.random.randn(5, 1024).astype(np.float32)
    mean_p = np.mean(frames, axis=0).astype(np.float32)
    max_p = np.max(frames, axis=0).astype(np.float32)
    clip_p = np.concatenate([mean_p, max_p])

    meta = {
        "source_sha256": "correct_hash",
        "model_handle": "https://tfhub.dev/google/yamnet/1",
    }

    # 1. Valid archive
    np.savez_compressed(
        str(npz_file),
        frame_embeddings=frames,
        mean_pooled=mean_p,
        max_pooled=max_p,
        clip_embedding=clip_p,
        metadata=json.dumps(meta),
    )
    assert is_cache_entry_valid(npz_file, expected_sha256="correct_hash") is True

    # 2. Invalidation on hash mismatch
    assert is_cache_entry_valid(npz_file, expected_sha256="altered_hash") is False

    # 3. Invalidation on non-finite values (NaN / Inf)
    frames_nan = frames.copy()
    frames_nan[0, 0] = np.nan
    np.savez_compressed(
        str(npz_file),
        frame_embeddings=frames_nan,
        mean_pooled=mean_p,
        max_pooled=max_p,
        clip_embedding=clip_p,
        metadata=json.dumps(meta),
    )
    assert is_cache_entry_valid(npz_file, expected_sha256="correct_hash") is False


def test_changed_file_detection(tmp_path):
    """Verify that build_unified_manifest fails if file content changed after Stage 3."""
    dummy_wav = tmp_path / "test.wav"
    sf.write(str(dummy_wav), np.zeros(1600, dtype=np.float32), 16000)

    # Initial hash
    with open(dummy_wav, "rb") as f:
        orig_hash = "stale_hash_that_does_not_match"

    record = [
        {
            "file_id": "test_audio",
            "dataset_name": "OpenSLR99",
            "relative_path": "test.wav",
            "binary_label": "scream",
            "review_flags": [],
            "sha256_hash": orig_hash,
            "source_group_id": "spk1",
        }
    ]
    st3_path = tmp_path / "stage3.json"
    with open(st3_path, "w", encoding="utf-8") as f:
        json.dump(record, f)

    with pytest.raises(RuntimeError):
        build_unified_manifest(st3_path, openslr_dir=tmp_path, nigens_dir=tmp_path, verify_file_integrity=True)
