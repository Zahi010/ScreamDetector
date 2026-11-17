"""Temporal Feature Extraction & Caching Pipeline (Stage 8.9.18).

Extracts and caches:
1. `features_temporal` (2804, 32): Complete 32-dim handcrafted temporal phonation vector
2. `features_family_a` (2804, 7): Phonation continuity & vocal closure gaps
3. `features_family_b` (2804, 6): Sub-band turbulence & spectral ratios
4. `features_family_c` (2804, 7): Temporal energy envelope & modulation
5. `features_family_d` (2804, 12): Spectral dynamics & transition flux
6. `features_seq_16` (2804, 70, 16): Short-time 16-dim temporal feature sequence for Model B (1D CNN)
7. `features_hybrid_3112` (2804, 3112): D_v4 (3080) concatenated with 32 Temporal features
8. Reuses Stage 8.9.17 feature cache (file_ids, splits, binary_labels, categories, source_groups, y_binary, features_d_v4).
"""

from __future__ import annotations

import csv
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import soundfile as sf

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = WORKSPACE_DIR.parent.parent

sys.path.insert(0, str(WORKSPACE_DIR / "src"))
from temporal_feature_extractor import TemporalPhonationExtractor, TEMPORAL_FEATURE_NAMES

logger = logging.getLogger("temporal_pipeline")


class TemporalFeaturePipeline:
    """Manages high-throughput temporal feature extraction, alignment, and disk caching."""

    def __init__(self, workspace_dir: Path = WORKSPACE_DIR):
        self.workspace_dir = workspace_dir
        self.backend_dir = workspace_dir.parent.parent
        self.data_dir = workspace_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.s17_cache_path = (
            self.backend_dir
            / "experiments"
            / "stage8_9_17_automated_dataset_reconstruction"
            / "data"
            / "features_stage8_9_17.npz"
        )
        self.s17_splits_manifest = (
            self.backend_dir
            / "experiments"
            / "stage8_9_17_automated_dataset_reconstruction"
            / "data"
            / "manifests"
            / "source_group_splits.csv"
        )
        self.cache_path = self.data_dir / "features_stage8_9_18_temporal.npz"

        self.extractor = TemporalPhonationExtractor(sr=16000)

    def extract_and_cache_all(self, force_recompute: bool = False) -> Dict[str, Any]:
        """Extract temporal features across all 2,804 records and fuse with Stage 8.9.17 representations."""
        if not force_recompute and self.cache_path.exists():
            logger.info("Loading cached Stage 8.9.18 temporal features from %s", self.cache_path)
            cached = np.load(self.cache_path, allow_pickle=True)
            return {k: cached[k] for k in cached.files}

        if not self.s17_cache_path.exists() or not self.s17_splits_manifest.exists():
            raise FileNotFoundError("Stage 8.9.17 cache or manifest missing.")

        logger.info("Loading base Stage 8.9.17 features and manifest...")
        s17_data = np.load(self.s17_cache_path, allow_pickle=True)
        file_ids = s17_data["file_ids"]
        splits = s17_data["splits"]
        binary_labels = s17_data["binary_labels"]
        categories = s17_data["canonical_categories"]
        source_groups = s17_data["source_groups"]
        y_binary = s17_data["y_binary"]
        features_d_v4 = s17_data["features_d_v4"]  # (2804, 3080)

        with open(self.s17_splits_manifest, "r", encoding="utf-8") as f:
            records = list(csv.DictReader(f))

        record_map = {r["file_id"]: r for r in records}
        n_records = len(file_ids)
        logger.info("Extracting temporal features for %d recordings...", n_records)

        # Allocate temporal arrays
        features_temporal = np.zeros((n_records, 32), dtype=np.float32)
        features_seq_16 = np.zeros((n_records, 70, 16), dtype=np.float32)
        durations = np.zeros(n_records, dtype=np.float32)

        t0 = time.time()
        for idx, fid in enumerate(file_ids):
            rec = record_map.get(str(fid))
            if not rec:
                continue

            abs_p = Path(rec["absolute_path"])
            if not abs_p.exists():
                abs_p = self.backend_dir.parent / rec["relative_path"]

            if not abs_p.exists():
                logger.warning("Audio file missing for %s: %s", fid, abs_p)
                continue

            try:
                data, sr = sf.read(str(abs_p), dtype="float32", always_2d=True)
                wf = np.mean(data, axis=1) if data.shape[1] > 1 else data[:, 0]

                if sr != 16000:
                    num_target = int(round(len(wf) * (16000.0 / sr)))
                    wf = np.interp(
                        np.linspace(0.0, 1.0, num_target, endpoint=False),
                        np.linspace(0.0, 1.0, len(wf), endpoint=False),
                        wf,
                    ).astype(np.float32)

                durations[idx] = float(len(wf) / 16000.0)

                # 1. 32-dim Handcrafted Temporal Vector
                t_vec = self.extractor.extract_temporal_features(wf)
                features_temporal[idx] = t_vec

                # 2. 70 x 16 Short-Time Sequence
                seq = self.extractor.extract_short_time_feature_sequence(wf, max_frames=70)
                features_seq_16[idx] = seq

            except Exception as e:
                logger.error("Error processing %s: %s", fid, e)

            if (idx + 1) % 500 == 0 or (idx + 1) == n_records:
                elapsed = time.time() - t0
                rate = (idx + 1) / max(0.1, elapsed)
                logger.info("Temporal extraction: %d/%d (%.1f%%) - %.1f files/sec", idx + 1, n_records, (idx + 1) / n_records * 100.0, rate)

        # Functional family slices
        # Family C: [0..6] (7)
        # Family D: [7..18] (12)
        # Family A: [19..25] (7)
        # Family B: [26..31] (6)
        features_family_c = features_temporal[:, :7]
        features_family_d = features_temporal[:, 7:19]
        features_family_a = features_temporal[:, 19:26]
        features_family_b = features_temporal[:, 26:32]

        # Hybrid fusion: D_v4 (3080) + Temporal (32) = 3112 dims
        features_hybrid_3112 = np.hstack([features_d_v4, features_temporal]).astype(np.float32)

        feature_dict = {
            "file_ids": file_ids,
            "splits": splits,
            "binary_labels": binary_labels,
            "canonical_categories": categories,
            "source_groups": source_groups,
            "y_binary": y_binary,
            "durations": durations,
            "features_d_v4": features_d_v4,
            "features_temporal": features_temporal,
            "features_family_a": features_family_a,
            "features_family_b": features_family_b,
            "features_family_c": features_family_c,
            "features_family_d": features_family_d,
            "features_seq_16": features_seq_16,
            "features_hybrid_3112": features_hybrid_3112,
        }

        np.savez_compressed(self.cache_path, **feature_dict)
        logger.info(
            "Temporal extraction complete! Saved cache to: %s (Shapes: Temporal=%s, Seq=%s, Hybrid=%s)",
            self.cache_path,
            features_temporal.shape,
            features_seq_16.shape,
            features_hybrid_3112.shape,
        )
        return feature_dict


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    pipe = TemporalFeaturePipeline()
    res = pipe.extract_and_cache_all()
    print("Stage 8.9.18 features successfully ready! Total records:", len(res["file_ids"]))
