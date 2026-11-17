"""Extract and cache multi-pooling YAMNet features for Expanded Dataset v3 (Stage 8.9.7).

Computes:
1. Max pooling (1024-dim)
2. 90th percentile pooling (1024-dim)
3. Mean pooling (1024-dim)
4. Concatenated multi-pooling: [max, p90, mean] (3072-dim)
5. YAMNet mean AudioSet scores (521-dim)
6. Vocal and Crowd acoustic summary features:
   - vocal_prob_max / mean (across speech, shout, yell, scream, cry)
   - crowd_prob_max / mean (across crowd, cheer, applause)
   - scream_yamnet_max / mean (YAMNet raw class 6)

Caches output in `backend/experiments/v2_hard_negative_training/features/yamnet_features_v3.npz`.
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
logger = logging.getLogger("extract_features_v3")

EXPERIMENT_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training"
MANIFEST_PATH = EXPERIMENT_DIR / "manifests" / "dataset_manifest_v3.json"
FEATURES_DIR = EXPERIMENT_DIR / "features"

# AudioSet class indices in YAMNet
VOCAL_CLASS_INDICES = [0, 1, 2, 3, 6, 7, 8, 13, 14, 16, 17]
CROWD_CLASS_INDICES = [67, 68, 69]
SCREAM_CLASS_INDEX = 6


def main():
    logger.info("Starting YAMNet Feature Extraction for Expanded Dataset v3...")
    if not MANIFEST_PATH.exists():
        logger.error(f"Manifest not found: {MANIFEST_PATH}")
        sys.exit(1)

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        records = json.load(f)

    logger.info(f"Loaded {len(records)} records from manifest v3.")
    yamnet = YAMNetLoader()

    FEATURES_DIR.mkdir(parents=True, exist_ok=True)
    out_npz_path = FEATURES_DIR / "yamnet_features_v3.npz"

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
    vocal_features = []  # [vocal_max, vocal_mean, crowd_max, crowd_mean, scream_max, scream_mean]

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

            # 6. Specific vocal and crowd summary features
            vocal_frames = np.max(preds[:, VOCAL_CLASS_INDICES], axis=1)
            crowd_frames = np.max(preds[:, CROWD_CLASS_INDICES], axis=1)
            scream_frames = preds[:, SCREAM_CLASS_INDEX]

            v_feat = np.array([
                float(np.max(vocal_frames)),
                float(np.mean(vocal_frames)),
                float(np.max(crowd_frames)),
                float(np.mean(crowd_frames)),
                float(np.max(scream_frames)),
                float(np.mean(scream_frames)),
            ], dtype=np.float32)

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
            vocal_features.append(v_feat)

            success_count += 1
            if (i + 1) % 100 == 0 or (i + 1) == len(records):
                logger.info(f"Processed {i + 1}/{len(records)} recordings...")

        except Exception as e:
            logger.warning(f"Failed to extract features for {f_id} ({audio_p}): {e}")
            fail_count += 1

    logger.info(f"Feature extraction completed: {success_count} succeeded, {fail_count} failed.")

    # Convert to numpy arrays
    data_dict = {
        "file_ids": np.array(file_ids),
        "splits": np.array(splits),
        "binary_labels": np.array(binary_labels),
        "categories": np.array(categories),
        "source_groups": np.array(source_groups),
        "features_max": np.array(features_max, dtype=np.float32),
        "features_p90": np.array(features_p90, dtype=np.float32),
        "features_mean": np.array(features_mean, dtype=np.float32),
        "features_concat": np.array(features_concat, dtype=np.float32),
        "yamnet_scores_mean": np.array(yamnet_scores_mean, dtype=np.float32),
        "vocal_features": np.array(vocal_features, dtype=np.float32),
    }

    np.savez_compressed(out_npz_path, **data_dict)
    logger.info(f"Saved compressed feature cache to {out_npz_path}")
    logger.info(f"Cache keys: {list(data_dict.keys())}")
    logger.info(f"Total extracted samples: {len(file_ids)}")


if __name__ == "__main__":
    main()
