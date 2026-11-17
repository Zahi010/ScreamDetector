"""Extract and cache multi-pooling YAMNet features for Experimental Dataset v2.

Computes:
1. Max pooling (baseline representation, 1024-dim)
2. 90th percentile pooling (transient suppression, 1024-dim)
3. Mean pooling (steady-state background representation, 1024-dim)
4. Concatenated multi-pooling (max + 90th percentile + mean, 3072-dim)
5. YAMNet AudioSet prediction scores (mean across frames, 521-dim)

Caches features in `backend/experiments/v2_hard_negative_training/features/yamnet_features_v2.npz`.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import numpy as np

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.audio.preprocessor import load_audio
from src.config import TARGET_SAMPLE_RATE
from src.model.yamnet_loader import YAMNetLoader

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("extract_features_v2")

EXPERIMENT_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training"
MANIFEST_PATH = EXPERIMENT_DIR / "manifests" / "dataset_manifest_v2.json"
FEATURES_DIR = EXPERIMENT_DIR / "features"


def main():
    logger.info("Starting YAMNet Feature Extraction for Experimental Dataset v2...")
    if not MANIFEST_PATH.exists():
        logger.error(f"Manifest not found: {MANIFEST_PATH}")
        sys.exit(1)

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        records = json.load(f)

    logger.info(f"Loaded {len(records)} records from manifest.")
    yamnet = YAMNetLoader()

    FEATURES_DIR.mkdir(parents=True, exist_ok=True)
    out_npz_path = FEATURES_DIR / "yamnet_features_v2.npz"

    file_ids = []
    splits = []
    binary_labels = []
    categories = []
    source_groups = []

    features_max = []
    features_p90 = []
    features_mean = []
    features_concat = []
    yamnet_scores_mean = []

    success_count = 0
    fail_count = 0

    for i, r in enumerate(records):
        f_id = r["file_id"]
        audio_p = Path(r["workspace_audio_path"])
        if not audio_p.exists():
            audio_p = Path(r["source_path"])

        try:
            wf, _ = load_audio(audio_p, target_sr=TARGET_SAMPLE_RATE)
            preds, embs, _ = yamnet.infer(wf)

            # 1. Max pooling
            f_max = np.max(embs, axis=0)
            # 2. 90th percentile pooling
            f_p90 = np.percentile(embs, 90, axis=0)
            # 3. Mean pooling
            f_mean = np.mean(embs, axis=0)
            # 4. Concatenated pooling
            f_concat = np.concatenate([f_max, f_p90, f_mean], axis=0)
            # 5. YAMNet mean scores
            p_mean = np.mean(preds, axis=0)

            file_ids.append(f_id)
            splits.append(r["split"])
            binary_labels.append(r["binary_label"])
            categories.append(r["target_category"])
            source_groups.append(r["source_group_id"])

            features_max.append(f_max)
            features_p90.append(f_p90)
            features_mean.append(f_mean)
            features_concat.append(f_concat)
            yamnet_scores_mean.append(p_mean)

            success_count += 1
            if (i + 1) % 100 == 0 or (i + 1) == len(records):
                logger.info(f"Processed {i + 1}/{len(records)} files ({success_count} succeeded, {fail_count} failed)...")
        except Exception as e:
            logger.warning(f"Feature extraction failed for {f_id}: {e}")
            fail_count += 1

    # Save to compressed npz
    np.savez_compressed(
        out_npz_path,
        file_ids=np.array(file_ids),
        splits=np.array(splits),
        binary_labels=np.array(binary_labels),
        categories=np.array(categories),
        source_groups=np.array(source_groups),
        features_max=np.array(features_max, dtype=np.float32),
        features_p90=np.array(features_p90, dtype=np.float32),
        features_mean=np.array(features_mean, dtype=np.float32),
        features_concat=np.array(features_concat, dtype=np.float32),
        yamnet_scores_mean=np.array(yamnet_scores_mean, dtype=np.float32),
    )

    logger.info(f"Successfully cached features for {success_count} files to {out_npz_path}")
    logger.info(f"  features_max shape   : {np.array(features_max).shape}")
    logger.info(f"  features_p90 shape   : {np.array(features_p90).shape}")
    logger.info(f"  features_concat shape: {np.array(features_concat).shape}")


if __name__ == "__main__":
    main()
