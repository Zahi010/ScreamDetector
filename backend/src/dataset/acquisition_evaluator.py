"""Frozen Model Evaluation on Acquired Hard Negatives (Stage 8.8).

Runs the frozen Stage 5 classifier (Logistic Regression, threshold 0.35)
on newly acquired hard-negative recordings without modifying weights,
threshold, or historical splits.
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np

from src.audio.preprocessor import load_audio
from src.config import (
    DEFAULT_SCREAM_THRESHOLD,
    MODELS_DIR,
    STAGE8_8_PROCESSED_DIR,
    STAGE8_8_REPORTS_DIR,
    TARGET_SAMPLE_RATE,
)
from src.dataset.acquisition_types import (
    AcquisitionCandidate,
    DownloadStatus,
    ReviewStatus,
)
from src.model.scream_classifier import FestivalScreamClassifier

logger = logging.getLogger("acquisition_evaluator")

EXPECTED_CLASSIFIER_SHA256 = "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f"
EXPECTED_METADATA_SHA256 = "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60"
FROZEN_THRESHOLD = 0.35


def compute_file_sha256(filepath: Path) -> str:
    """Compute SHA-256 hash of a file on disk."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def verify_frozen_model_artifacts() -> Tuple[bool, Dict[str, Any]]:
    """Verify integrity of classifier artifact and metadata."""
    clf_path = MODELS_DIR / "scream_classifier.joblib"
    meta_path = MODELS_DIR / "model_metadata.json"

    clf_sha = compute_file_sha256(clf_path) if clf_path.exists() else ""
    meta_sha = compute_file_sha256(meta_path) if meta_path.exists() else ""

    clf_match = (clf_sha == EXPECTED_CLASSIFIER_SHA256)
    meta_match = (meta_sha == EXPECTED_METADATA_SHA256)
    threshold_match = (DEFAULT_SCREAM_THRESHOLD == FROZEN_THRESHOLD)

    all_ok = clf_match and meta_match and threshold_match

    audit = {
        "verified": all_ok,
        "classifier_path": str(clf_path),
        "classifier_sha256": clf_sha,
        "expected_classifier_sha256": EXPECTED_CLASSIFIER_SHA256,
        "classifier_sha256_match": clf_match,
        "metadata_path": str(meta_path),
        "metadata_sha256": meta_sha,
        "expected_metadata_sha256": EXPECTED_METADATA_SHA256,
        "metadata_sha256_match": meta_match,
        "operating_threshold": DEFAULT_SCREAM_THRESHOLD,
        "expected_threshold": FROZEN_THRESHOLD,
        "threshold_match": threshold_match,
    }
    return all_ok, audit


class AcquiredAudioEvaluator:
    """Evaluates acquired clips using frozen YAMNet + Logistic Regression."""

    def __init__(self, threshold: float = FROZEN_THRESHOLD):
        self.threshold = threshold
        verified, audit = verify_frozen_model_artifacts()
        if not verified:
            raise RuntimeError(f"Frozen model artifact verification failed: {audit}")

        self.classifier = FestivalScreamClassifier()

    def evaluate_candidate(
        self,
        candidate: AcquisitionCandidate,
    ) -> Tuple[Optional[float], Optional[bool]]:
        """Run frozen inference on a candidate audio file.

        Returns (score, alert_flag). Returns (None, None) if audio not acquired.
        """
        # Candidate must have valid audio
        audio_target: Optional[Path] = None
        if candidate.sha256_derived and STAGE8_8_PROCESSED_DIR.exists():
            derived_file = STAGE8_8_PROCESSED_DIR / f"{candidate.recording_id}_16k_mono.wav"
            if derived_file.exists():
                audio_target = derived_file

        if not audio_target and candidate.local_path:
            raw_path = Path(candidate.local_path)
            if raw_path.exists():
                audio_target = raw_path

        if not audio_target:
            return None, None

        try:
            result = self.classifier.predict_file(audio_target, custom_threshold=self.threshold)
            prob = float(result["scream_probability"])
            alert = bool(result["is_scream"])

            candidate.model_score = prob
            candidate.model_alert = alert
            return prob, alert
        except Exception as e:
            logger.warning(f"Inference failed for {candidate.recording_id}: {e}")
            return None, None

    def evaluate_all(
        self,
        candidates: List[AcquisitionCandidate],
    ) -> Dict[str, Any]:
        """Evaluate all eligible candidates and compile category-level report."""
        category_stats: Dict[str, Dict[str, Any]] = {}
        all_evaluations: List[Dict[str, Any]] = []

        for c in candidates:
            score, alert = self.evaluate_candidate(c)
            cat = c.proposed_category or "unclassified"

            if cat not in category_stats:
                category_stats[cat] = {
                    "total_acquired": 0,
                    "unique_sources": set(),
                    "reviewed_non_scream": 0,
                    "unreviewed_or_ambiguous": 0,
                    "model_alerts": 0,
                    "confirmed_false_positives": 0,
                    "scores": [],
                    "top_alerts": [],
                }

            if score is not None:
                category_stats[cat]["total_acquired"] += 1
                source_grp = c.duplicate_or_source_group or c.original_creator or c.recording_id
                category_stats[cat]["unique_sources"].add(source_grp)

                if c.review_status == ReviewStatus.APPROVED_NON_SCREAM.value:
                    category_stats[cat]["reviewed_non_scream"] += 1
                    if alert:
                        category_stats[cat]["confirmed_false_positives"] += 1
                else:
                    category_stats[cat]["unreviewed_or_ambiguous"] += 1

                if alert:
                    category_stats[cat]["model_alerts"] += 1
                    category_stats[cat]["top_alerts"].append({
                        "recording_id": c.recording_id,
                        "title": c.original_title_description[:80],
                        "score": round(score, 4),
                        "review_status": c.review_status,
                        "license": c.clip_license,
                    })

                category_stats[cat]["scores"].append(score)

                all_evaluations.append({
                    "recording_id": c.recording_id,
                    "category": cat,
                    "model_score": round(score, 4),
                    "model_alert": alert,
                    "review_status": c.review_status,
                    "commercial_compatibility": c.commercial_compatibility,
                })

        # Summarize category metrics
        summary_by_cat: Dict[str, Any] = {}
        total_audio_evaluated = 0
        total_alerts = 0
        total_confirmed_fp = 0
        total_reviewed_negatives = 0

        for cat, stats in category_stats.items():
            scores = stats["scores"]
            n_reviewed = stats["reviewed_non_scream"]
            n_fp = stats["confirmed_false_positives"]
            fpr_reviewed = (n_fp / n_reviewed) if n_reviewed > 0 else None

            sorted_alerts = sorted(stats["top_alerts"], key=lambda x: x["score"], reverse=True)

            summary_by_cat[cat] = {
                "total_audio_clips": stats["total_acquired"],
                "unique_source_groups": len(stats["unique_sources"]),
                "reviewed_non_scream_count": n_reviewed,
                "unreviewed_or_ambiguous_count": stats["unreviewed_or_ambiguous"],
                "model_alerts_at_0_35": stats["model_alerts"],
                "confirmed_false_positives_reviewed": n_fp,
                "false_positive_rate_reviewed": round(fpr_reviewed, 4) if fpr_reviewed is not None else "N/A (unreviewed)",
                "score_distribution": {
                    "min": round(float(np.min(scores)), 4) if scores else None,
                    "max": round(float(np.max(scores)), 4) if scores else None,
                    "mean": round(float(np.mean(scores)), 4) if scores else None,
                    "median": round(float(np.median(scores)), 4) if scores else None,
                },
                "top_alerts": sorted_alerts[:5],
                "unreviewed_alert_notice": "Alerts on unreviewed clips are candidate vulnerabilities for inspection, NOT confirmed ground-truth false positives.",
            }

            total_audio_evaluated += stats["total_acquired"]
            total_alerts += stats["model_alerts"]
            total_confirmed_fp += n_fp
            total_reviewed_negatives += n_reviewed

        overall_report = {
            "evaluation_stage": "Stage 8.8 Hard-Negative Baseline Inference",
            "model_metadata": {
                "operating_threshold": self.threshold,
                "classifier_hash": EXPECTED_CLASSIFIER_SHA256,
                "metadata_hash": EXPECTED_METADATA_SHA256,
            },
            "total_audio_clips_evaluated": total_audio_evaluated,
            "total_model_alerts": total_alerts,
            "total_reviewed_non_scream": total_reviewed_negatives,
            "total_confirmed_false_positives": total_confirmed_fp,
            "by_category": summary_by_cat,
        }

        return overall_report
