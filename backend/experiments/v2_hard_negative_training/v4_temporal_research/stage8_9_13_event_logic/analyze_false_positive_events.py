"""Forensic Analysis of False-Positive Event Patterns for Stage 8.9.13.

Analyzes held-out test cohort negative recordings (N=198) across acoustic categories:
- Shouted speech and excited yelling
- Rhythmic crowd chants and cheering
- Sirens, alarms, and fireworks
- Whistles and squeaks
- Infant crying
- General environmental noise

Classifies false-positive event triggers into empirical acoustic failure modes:
1. "Isolated_Transient_Spike": exactly 1 window > tau
2. "Persistent_High_Resonance": >= 2 consecutive windows > tau (sustained vowel formant / chant)
3. "Repeated_Acoustic_Bursts": multiple non-adjacent windows > tau (rhythmic pulsing)
4. "True_Negative_Suppressed": cleanly rejected (all windows <= tau)

Outputs: `stage8_9_13_event_logic/false_positive_event_analysis.csv`.
"""

from __future__ import annotations

import csv
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("false_positive_analysis")

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))

STAGE11_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_11_evaluation"
STAGE12_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_12_runtime_research"
STAGE13_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_13_event_logic"
CACHE_PATH = STAGE12_DIR / "window_probabilities_cache.npz"
MANIFEST_PATH = STAGE11_DIR / "stage8_9_11_dataset_manifest.json"


def analyze_false_positive_patterns(threshold: float = 0.38) -> List[Dict[str, Any]]:
    logger.info("=================================================================")
    logger.info("STAGE 8.9.13: FALSE-POSITIVE EVENT PATTERN FORENSIC AUDIT")
    logger.info("=================================================================")

    # Load cache
    cache = np.load(CACHE_PATH, allow_pickle=True)
    test_seqs = cache["test_seqs"].item()

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        all_records = {r["file_id"]: r for r in json.load(f)}

    analysis_rows = []

    category_counts: Dict[str, Dict[str, int]] = {}

    for fid, item in test_seqs.items():
        if item["y_true"] != 0:
            continue  # Only negatives

        cat = item["category"]
        probs_d = item["probs_d"]
        probs_hv5 = item["probs_hv5"]
        n_windows = len(probs_d)
        dur = item["duration"]
        group_id = item["group_id"]

        meta = all_records.get(fid, {})
        title = meta.get("original_title", "Unknown")

        # Threshold crossings on D_v4
        pos_mask_d = (probs_d >= threshold)
        n_pos_d = int(np.sum(pos_mask_d))
        max_p_d = float(np.max(probs_d))
        mean_p_d = float(np.mean(probs_d))

        # Threshold crossings on H_v5_SNR
        pos_mask_hv5 = (probs_hv5 >= threshold)
        n_pos_hv5 = int(np.sum(pos_mask_hv5))
        max_p_hv5 = float(np.max(probs_hv5))
        mean_p_hv5 = float(np.mean(probs_hv5))

        # Calculate longest consecutive streak on D_v4
        streak = 0
        max_streak_d = 0
        for p in pos_mask_d:
            if p:
                streak += 1
                max_streak_d = max(max_streak_d, streak)
            else:
                streak = 0

        # Classify pattern on D_v4
        if n_pos_d == 0:
            trigger_pattern = "True_Negative_Suppressed"
            acoustic_failure_mode = "None (Correctly Rejected)"
        elif n_pos_d == 1:
            trigger_pattern = "Isolated_Transient_Spike"
            acoustic_failure_mode = "Transient non-scream noise burst or sharp consonant"
        elif max_streak_d >= 2:
            trigger_pattern = "Persistent_High_Resonance"
            acoustic_failure_mode = "Sustained vocal formant or tonal harmonic tracking"
        else:
            trigger_pattern = "Repeated_Acoustic_Bursts"
            acoustic_failure_mode = "Rhythmic chanting or periodic acoustic impulses"

        if cat not in category_counts:
            category_counts[cat] = {
                "Total": 0,
                "True_Negative_Suppressed": 0,
                "Isolated_Transient_Spike": 0,
                "Persistent_High_Resonance": 0,
                "Repeated_Acoustic_Bursts": 0,
            }
        category_counts[cat]["Total"] += 1
        category_counts[cat][trigger_pattern] += 1

        analysis_rows.append({
            "file_id": fid,
            "category": cat,
            "duration_sec": round(dur, 2),
            "n_windows": n_windows,
            "source_group_id": group_id,
            "max_prob_d_v4": round(max_p_d, 4),
            "mean_prob_d_v4": round(mean_p_d, 4),
            "pos_windows_d_v4": n_pos_d,
            "max_consecutive_streak_d_v4": max_streak_d,
            "trigger_pattern_d_v4": trigger_pattern,
            "acoustic_failure_mode": acoustic_failure_mode,
            "max_prob_h_v5": round(max_p_hv5, 4),
            "pos_windows_h_v5": n_pos_hv5,
            "sample_title": title[:60],
        })

    out_csv = STAGE13_DIR / "false_positive_event_analysis.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(analysis_rows[0].keys()))
        writer.writeheader()
        writer.writerows(analysis_rows)

    logger.info(f"Saved false-positive event analysis ({len(analysis_rows)} records) to {out_csv.name}")

    # Summary table
    logger.info("\nFalse-Positive Trigger Distribution by Category on Model D_v4 (Threshold = 0.38):")
    logger.info(f"{'Category':<25} | {'Total':<5} | {'Suppressed':<10} | {'Spike (1-win)':<14} | {'Persistent (>=2)':<16} | {'Repeated Bursts':<15}")
    logger.info("-" * 95)
    for cat, counts in category_counts.items():
        logger.info(
            f"{cat:<25} | {counts['Total']:<5} | {counts['True_Negative_Suppressed']:<10} | "
            f"{counts['Isolated_Transient_Spike']:<14} | {counts['Persistent_High_Resonance']:<16} | "
            f"{counts['Repeated_Acoustic_Bursts']:<15}"
        )

    return analysis_rows


if __name__ == "__main__":
    analyze_false_positive_patterns()
