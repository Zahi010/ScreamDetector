"""Automated Feature Extraction & Caching Pipeline (Stage 8.9.17).

Extracts high-fidelity representations preserving exact mathematical parity with D_v4:
- Multi-pooled YAMNet embeddings [max, p10, mean] (3 x 1024 = 3072 dims).
- Family A acoustic features (8 dims: Spectral flatness, crest, harmonic ratio, flux, roughness, RMS, HF ratio, temporal crest).
- Model D_v4 feature vector: [YAMNet (3072), Family A (8)] = 3080 dims.
- Model E full feature vector: [YAMNet (3072), Full Acoustic (30)] = 3102 dims.

Reuses historical precomputed features where available, accelerating extraction to seconds.
"""

from __future__ import annotations

import csv
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import soundfile as sf

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = WORKSPACE_DIR.parent.parent

# Add backend and acoustic extractor to path
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_14_acoustic_discriminability"))

from acoustic_discriminability_features import AcousticDiscriminabilityExtractor
from src.model.yamnet_loader import YAMNetLoader

logger = logging.getLogger("feature_pipeline")


class FeatureExtractionPipeline:
    """Orchestrates feature extraction and caching for reconstructed dataset."""

    def __init__(self, workspace_dir: Path = WORKSPACE_DIR):
        self.workspace_dir = workspace_dir
        self.backend_dir = workspace_dir.parent.parent
        self.data_dir = workspace_dir / "data"
        self.manifest_path = self.data_dir / "manifests" / "source_group_splits.csv"
        self.cache_path = self.data_dir / "features_stage8_9_17.npz"

        self.acoustic_extractor = AcousticDiscriminabilityExtractor(sr=16000)
        self.yamnet_loader: Optional[YAMNetLoader] = None

    def _get_yamnet_loader(self) -> YAMNetLoader:
        """Lazy load YAMNet inference engine."""
        if self.yamnet_loader is None:
            logger.info("Initializing YAMNetLoader...")
            self.yamnet_loader = YAMNetLoader()
            self.yamnet_loader.load()
            logger.info("YAMNetLoader ready.")
        return self.yamnet_loader

    def load_cached_stage14_features(self) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
        """Index precomputed features from Stage 8.9.14 cache for instant reuse."""
        stage14_cache = (
            self.backend_dir
            / "experiments"
            / "v2_hard_negative_training"
            / "v4_temporal_research"
            / "stage8_9_14_acoustic_discriminability"
            / "stage8_9_14_acoustic_features.npz"
        )
        if not stage14_cache.exists():
            logger.warning("Stage 14 cache not found at %s", stage14_cache)
            return {}

        logger.info("Loading precomputed Stage 14 features for cache acceleration...")
        data = np.load(stage14_cache, allow_pickle=True)
        f_ids = data["file_ids"]
        y_feats = data["features_yamnet"]      # (1384, 3072)
        ac_feats = data["features_acoustic"]   # (1384, 30)

        precomputed: Dict[str, Tuple[np.ndarray, np.ndarray]] = {}
        for fid, y_f, ac_f in zip(f_ids, y_feats, ac_feats):
            precomputed[str(fid)] = (y_f.astype(np.float32), ac_f.astype(np.float32))

        logger.info("Indexed %d precomputed Stage 14 feature records.", len(precomputed))
        return precomputed

    def extract_features_for_all(self, force_recompute: bool = False) -> Dict[str, Any]:
        """Extract or load complete feature representations for all records in split manifest."""
        if not force_recompute and self.cache_path.exists():
            logger.info("Loading cached Stage 8.9.17 features from %s", self.cache_path)
            cached = np.load(self.cache_path, allow_pickle=True)
            return {k: cached[k] for k in cached.files}

        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Splits manifest missing: {self.manifest_path}")

        with open(self.manifest_path, "r", encoding="utf-8") as f:
            records = list(csv.DictReader(f))

        n_records = len(records)
        logger.info("Extracting features for %d dataset records...", n_records)

        precomputed = self.load_cached_stage14_features()

        file_ids = np.array([r["file_id"] for r in records], dtype=object)
        splits = np.array([r["split"] for r in records], dtype=object)
        binary_labels = np.array([r["binary_label"] for r in records], dtype=object)
        canonical_categories = np.array([r["canonical_category"] for r in records], dtype=object)
        source_groups = np.array([r["source_group_id"] for r in records], dtype=object)
        y_binary = np.array([1 if r["binary_label"] == "scream" else 0 for r in records], dtype=np.int32)

        # Feature matrix allocations
        features_yamnet = np.zeros((n_records, 3072), dtype=np.float32)
        features_acoustic = np.zeros((n_records, 30), dtype=np.float32)

        cache_hits = 0
        cache_misses = 0

        t0 = time.time()
        for idx, r in enumerate(records):
            fid = r["file_id"]
            orig_id = r.get("original_id", fid)

            # Check cache hits
            hit = precomputed.get(fid) or precomputed.get(orig_id)
            if hit is not None:
                features_yamnet[idx] = hit[0]
                features_acoustic[idx] = hit[1]
                cache_hits += 1
                continue

            cache_misses += 1
            # Load audio
            abs_path = Path(r["absolute_path"])
            if not abs_path.exists():
                abs_path = self.workspace_dir / r["relative_path"]
            if not abs_path.exists():
                abs_path = self.backend_dir.parent / r["relative_path"]

            if not abs_path.exists():
                logger.error("Audio file missing for record %s: %s", fid, abs_path)
                continue

            try:
                data, sr = sf.read(str(abs_path), dtype="float32", always_2d=True)
                if data.shape[1] > 1:
                    wf = np.mean(data, axis=1)
                else:
                    wf = data[:, 0]

                if sr != 16000:
                    num_target = int(round(len(wf) * (16000.0 / sr)))
                    wf = np.interp(
                        np.linspace(0.0, 1.0, num_target, endpoint=False),
                        np.linspace(0.0, 1.0, len(wf), endpoint=False),
                        wf,
                    ).astype(np.float32)

                # Ensure minimum length
                if len(wf) < 320:
                    wf = np.pad(wf, (0, 320 - len(wf)), mode="constant")

                # 1. YAMNet multi-pool features
                yamnet = self._get_yamnet_loader()
                _, embs, _ = yamnet.infer(wf)

                if len(embs) == 0:
                    f_yamnet = np.zeros(3072, dtype=np.float32)
                else:
                    f_mean = np.mean(embs, axis=0)
                    f_max = np.max(embs, axis=0)
                    f_p10 = np.percentile(embs, 10, axis=0)
                    f_yamnet = np.concatenate([f_max, f_p10, f_mean]).astype(np.float32)

                # 2. Acoustic discriminability features (30 dims)
                f_ac = self.acoustic_extractor.extract_features(wf)

                features_yamnet[idx] = f_yamnet
                features_acoustic[idx] = f_ac

            except Exception as e:
                logger.error("Error processing %s (%s): %s", fid, abs_path, e)

            if (idx + 1) % 250 == 0 or (idx + 1) == n_records:
                elapsed = time.time() - t0
                rate = (idx + 1) / max(0.1, elapsed)
                logger.info(
                    "Feature progress: %d/%d (%.1f%%) | Hits: %d, Misses: %d | Rate: %.1f files/sec",
                    idx + 1,
                    n_records,
                    (idx + 1) / n_records * 100.0,
                    cache_hits,
                    cache_misses,
                    rate,
                )

        # Construct derived feature sets
        # D_v4 Family A: YAMNet (3072) + Acoustic Family A (8) = 3080 dims
        features_family_a = features_acoustic[:, :8]
        features_d_v4 = np.hstack([features_yamnet, features_family_a])

        # Candidate E: YAMNet (3072) + All Acoustic (30) = 3102 dims
        features_candidate_e = np.hstack([features_yamnet, features_acoustic])

        feature_dict = {
            "file_ids": file_ids,
            "splits": splits,
            "binary_labels": binary_labels,
            "canonical_categories": canonical_categories,
            "source_groups": source_groups,
            "y_binary": y_binary,
            "features_yamnet": features_yamnet,
            "features_acoustic": features_acoustic,
            "features_family_a": features_family_a,
            "features_d_v4": features_d_v4,
            "features_candidate_e": features_candidate_e,
        }

        # Save compressed cache
        np.savez_compressed(self.cache_path, **feature_dict)
        logger.info(
            "Feature extraction complete! Saved cache to: %s (Shapes: D_v4=%s, Cand_E=%s)",
            self.cache_path,
            features_d_v4.shape,
            features_candidate_e.shape,
        )
        return feature_dict


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    pipe = FeatureExtractionPipeline()
    feats = pipe.extract_features_for_all()
    print("Features ready! Total records:", len(feats["file_ids"]))
