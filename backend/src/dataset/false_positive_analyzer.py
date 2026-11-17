"""Human-Verified False-Positive Analyzer (Stage 8.9.3).

Evaluates the frozen Festival Scream Detector classifier against human-reviewed
audio recordings, adhering strictly to:
1. Frozen classifier weights (SHA-256: ad6e428d05...) and metadata (SHA-256: 30c1c75d81...).
2. Fixed operating threshold of 0.35.
3. Strict human label ground truth:
   - Negative Class: APPROVED_NON_SCREAM (y_true = 0)
   - Positive Class: SCREAM_PRESENT (y_true = 1)
   - Excluded from binary metrics: AMBIGUOUS and EXCLUDED
4. Resumable inference that never overwrites human decisions or historical Stage 5 results.
5. Explicit statistical caveat regarding small positive sample sizes.
"""

from __future__ import annotations

import csv
import io
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple

import numpy as np
from sklearn.metrics import average_precision_score, confusion_matrix, roc_auc_score

from src.config import (
    DEFAULT_SCREAM_THRESHOLD,
    MODELS_DIR,
    STAGE8_8_PROCESSED_DIR,
)
from src.database.review_store import ReviewStore, get_review_store
from src.dataset.acquisition_evaluator import (
    EXPECTED_CLASSIFIER_SHA256,
    EXPECTED_METADATA_SHA256,
    FROZEN_THRESHOLD,
    compute_file_sha256,
    verify_frozen_model_artifacts,
)
from src.dataset.acquisition_types import ReviewStatus
from src.model.scream_classifier import FestivalScreamClassifier

logger = logging.getLogger("false_positive_analyzer")


class FalsePositiveAnalyzer:
    """Evaluates frozen classifier against human review decisions and computes binary metrics."""

    def __init__(self, store: Optional[ReviewStore] = None, threshold: float = FROZEN_THRESHOLD):
        self.store = store or get_review_store()
        self.threshold = threshold

        # Verify frozen model artifact integrity
        verified, audit = verify_frozen_model_artifacts()
        if not verified:
            raise RuntimeError(f"Frozen model artifact verification failed: {audit}")

        self._classifier: Optional[FestivalScreamClassifier] = None

    @property
    def classifier(self) -> FestivalScreamClassifier:
        """Lazy load frozen classifier singleton."""
        if self._classifier is None:
            self._classifier = FestivalScreamClassifier()
        return self._classifier

    def run_inference_on_reviewed(self, force_reevaluate: bool = False) -> Dict[str, Any]:
        """Evaluate reviewed recordings with usable audio.

        By default (force_reevaluate=False), skips recordings that already have
        a valid model_score in the database, making inference fully resumable.
        """
        verified, audit = verify_frozen_model_artifacts()
        if not verified:
            raise RuntimeError(f"Model integrity compromised prior to evaluation: {audit}")

        with self.store._get_connection() as conn:
            if force_reevaluate:
                query = """
                    SELECT recording_id, local_path, has_audio, review_status, model_score
                    FROM candidates
                    WHERE review_status IN ('APPROVED_NON_SCREAM', 'SCREAM_PRESENT', 'AMBIGUOUS')
                      AND has_audio = 1
                    ORDER BY recording_id ASC
                """
                rows = conn.execute(query).fetchall()
            else:
                # Resumable: only evaluate unscored reviewed recordings
                query = """
                    SELECT recording_id, local_path, has_audio, review_status, model_score
                    FROM candidates
                    WHERE review_status IN ('APPROVED_NON_SCREAM', 'SCREAM_PRESENT', 'AMBIGUOUS')
                      AND has_audio = 1
                      AND model_score IS NULL
                    ORDER BY recording_id ASC
                """
                rows = conn.execute(query).fetchall()

        evaluated_count = 0
        skipped_count = 0
        failed_count = 0
        alerts_count = 0
        results: List[Dict[str, Any]] = []

        logger.info("Found %d reviewed recordings needing classifier evaluation.", len(rows))

        for r in rows:
            rec_id = r["recording_id"]
            audio_path = self.store.get_secure_audio_path(rec_id)

            if not audio_path or not audio_path.is_file():
                logger.warning("Audio path missing or unresolvable for reviewed candidate '%s'", rec_id)
                failed_count += 1
                continue

            try:
                pred = self.classifier.predict_file(audio_path, custom_threshold=self.threshold)
                prob = float(pred["scream_probability"])
                alert = bool(pred["is_scream"])

                self.store.record_model_evaluation(
                    recording_id=rec_id,
                    model_score=prob,
                    is_alert=alert,
                    threshold=self.threshold,
                    artifact_hash=EXPECTED_CLASSIFIER_SHA256,
                    status="COMPLETED",
                )

                if alert:
                    alerts_count += 1
                evaluated_count += 1

                results.append({
                    "recording_id": rec_id,
                    "model_score": prob,
                    "is_alert": alert,
                    "status": "COMPLETED",
                })
            except Exception as e:
                logger.error("Inference failure for '%s': %s", rec_id, e)
                failed_count += 1
                self.store.record_model_evaluation(
                    recording_id=rec_id,
                    model_score=-1.0,
                    is_alert=False,
                    threshold=self.threshold,
                    artifact_hash=EXPECTED_CLASSIFIER_SHA256,
                    status=f"FAILED: {e}",
                )
                results.append({
                    "recording_id": rec_id,
                    "error": str(e),
                    "status": "FAILED",
                })

        return {
            "success": True,
            "evaluated_count": evaluated_count,
            "failed_count": failed_count,
            "alerts_count": alerts_count,
            "results": results,
        }

    def compute_evaluation_report(self) -> Dict[str, Any]:
        """Compute full false-positive analysis and valid classification metrics.

        Metrics are strictly computed against stored human decisions:
        - Negative: APPROVED_NON_SCREAM
        - Positive: SCREAM_PRESENT
        - AMBIGUOUS & EXCLUDED are reported separately and excluded from binary metrics.
        """
        verified, audit = verify_frozen_model_artifacts()

        with self.store._get_connection() as conn:
            # Query all candidates with their review status and model scores
            query = """
                SELECT
                    recording_id,
                    source_provider,
                    original_source_id,
                    original_title_description,
                    original_creator,
                    clip_license,
                    duration_seconds,
                    proposed_category,
                    review_status,
                    reviewer_notes,
                    reviewer_reason_code,
                    reviewed_at,
                    has_audio,
                    model_score,
                    model_alert,
                    triage_group,
                    triage_reason,
                    yamnet_top_classes,
                    yamnet_relevant_tags
                FROM candidates
                ORDER BY recording_id ASC
            """
            rows = conn.execute(query).fetchall()

        total_candidates = len(rows)
        audio_available_count = sum(1 for r in rows if r["has_audio"] == 1)

        # Count decisions across all records
        decision_counts = {
            "APPROVED_NON_SCREAM": 0,
            "SCREAM_PRESENT": 0,
            "AMBIGUOUS": 0,
            "EXCLUDED": 0,
            "UNREVIEWED": 0,
        }
        for r in rows:
            st = r["review_status"]
            decision_counts[st] = decision_counts.get(st, 0) + 1

        total_reviewed = (
            decision_counts["APPROVED_NON_SCREAM"]
            + decision_counts["SCREAM_PRESENT"]
            + decision_counts["AMBIGUOUS"]
            + decision_counts["EXCLUDED"]
        )

        # Missing score tracking
        missing_scores_count = sum(1 for r in rows if r["model_score"] is None)
        missing_audio_count = sum(1 for r in rows if r["has_audio"] == 0)
        reviewed_missing_scores = [
            r["recording_id"]
            for r in rows
            if r["review_status"] in ("APPROVED_NON_SCREAM", "SCREAM_PRESENT", "AMBIGUOUS")
            and r["model_score"] is None
        ]

        # Filter binary evaluation population:
        # Negative: APPROVED_NON_SCREAM
        # Positive: SCREAM_PRESENT
        # Usable audio and non-null model_score
        binary_records: List[Dict[str, Any]] = []
        ambiguous_records: List[Dict[str, Any]] = []
        unreviewed_records: List[Dict[str, Any]] = []

        false_positives: List[Dict[str, Any]] = []
        false_negatives: List[Dict[str, Any]] = []
        true_positives: List[Dict[str, Any]] = []
        true_negatives: List[Dict[str, Any]] = []

        # Breakdown accumulators
        category_breakdown: Dict[str, Dict[str, Any]] = {}
        source_breakdown: Dict[str, Dict[str, Any]] = {}

        y_true: List[int] = []
        y_scores: List[float] = []

        for r in rows:
            rec = dict(r)
            status = rec["review_status"]
            score = rec["model_score"]
            cat = rec["proposed_category"] or "unclassified"
            src = rec["source_provider"] or "unknown"

            # Parse prediction using frozen threshold
            pred_alert = (score >= self.threshold) if score is not None else None
            rec["predicted_label"] = "SCREAM" if pred_alert else "NON_SCREAM"
            rec["is_model_alert"] = pred_alert

            if status == "AMBIGUOUS":
                ambiguous_records.append(rec)
            elif status == "UNREVIEWED":
                unreviewed_records.append(rec)
            elif status in ("APPROVED_NON_SCREAM", "SCREAM_PRESENT"):
                if score is not None:
                    # Ground truth binary integer
                    gt = 1 if status == "SCREAM_PRESENT" else 0
                    y_true.append(gt)
                    y_scores.append(score)

                    # Determine confusion matrix category
                    if gt == 1:
                        if pred_alert:
                            rec["classification_outcome"] = "TP"
                            true_positives.append(rec)
                        else:
                            rec["classification_outcome"] = "FN"
                            false_negatives.append(rec)
                    else:  # gt == 0
                        if pred_alert:
                            rec["classification_outcome"] = "FP"
                            false_positives.append(rec)
                        else:
                            rec["classification_outcome"] = "TN"
                            true_negatives.append(rec)

                    binary_records.append(rec)

                    # Accumulate category breakdown
                    if cat not in category_breakdown:
                        category_breakdown[cat] = {
                            "category": cat,
                            "total_evaluated": 0,
                            "negatives": 0,
                            "positives": 0,
                            "true_negatives": 0,
                            "false_positives": 0,
                            "true_positives": 0,
                            "false_negatives": 0,
                            "scores": [],
                        }
                    cat_entry = category_breakdown[cat]
                    cat_entry["total_evaluated"] += 1
                    cat_entry["scores"].append(score)
                    if gt == 0:
                        cat_entry["negatives"] += 1
                        if pred_alert:
                            cat_entry["false_positives"] += 1
                        else:
                            cat_entry["true_negatives"] += 1
                    else:
                        cat_entry["positives"] += 1
                        if pred_alert:
                            cat_entry["true_positives"] += 1
                        else:
                            cat_entry["false_negatives"] += 1

                    # Accumulate source breakdown
                    if src not in source_breakdown:
                        source_breakdown[src] = {
                            "source": src,
                            "total_evaluated": 0,
                            "negatives": 0,
                            "positives": 0,
                            "true_negatives": 0,
                            "false_positives": 0,
                            "true_positives": 0,
                            "false_negatives": 0,
                            "scores": [],
                        }
                    src_entry = source_breakdown[src]
                    src_entry["total_evaluated"] += 1
                    src_entry["scores"].append(score)
                    if gt == 0:
                        src_entry["negatives"] += 1
                        if pred_alert:
                            src_entry["false_positives"] += 1
                        else:
                            src_entry["true_negatives"] += 1
                    else:
                        src_entry["positives"] += 1
                        if pred_alert:
                            src_entry["true_positives"] += 1
                        else:
                            src_entry["false_negatives"] += 1

        # Calculate metrics
        tp_count = len(true_positives)
        fn_count = len(false_negatives)
        tn_count = len(true_negatives)
        fp_count = len(false_positives)

        total_binary = len(binary_records)
        num_positives = tp_count + fn_count
        num_negatives = tn_count + fp_count

        precision = (tp_count / (tp_count + fp_count)) if (tp_count + fp_count) > 0 else 0.0
        recall = (tp_count / (tp_count + fn_count)) if (tp_count + fn_count) > 0 else 0.0
        specificity = (tn_count / (tn_count + fp_count)) if (tn_count + fp_count) > 0 else 0.0
        fpr = (fp_count / (tn_count + fp_count)) if (tn_count + fp_count) > 0 else 0.0
        fnr = (fn_count / (tp_count + fn_count)) if (tp_count + fn_count) > 0 else 0.0
        accuracy = ((tp_count + tn_count) / total_binary) if total_binary > 0 else 0.0
        f1_score = (
            (2.0 * precision * recall) / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )

        # Continuous curve metrics (ROC-AUC & PR-AUC)
        roc_auc: Optional[float] = None
        pr_auc: Optional[float] = None
        has_both_classes = (num_positives > 0 and num_negatives > 0)

        if has_both_classes and len(y_true) > 0:
            try:
                roc_auc = float(roc_auc_score(y_true, y_scores))
            except Exception as e:
                logger.warning("ROC-AUC computation failed: %s", e)
            try:
                pr_auc = float(average_precision_score(y_true, y_scores))
            except Exception as e:
                logger.warning("PR-AUC computation failed: %s", e)

        # Finalize category breakdown rates
        category_summary: List[Dict[str, Any]] = []
        for cat_k, cat_v in category_breakdown.items():
            scores = cat_v["scores"]
            n_neg = cat_v["negatives"]
            fps = cat_v["false_positives"]
            fpr_cat = (fps / n_neg) if n_neg > 0 else 0.0
            category_summary.append({
                "category": cat_k,
                "total_evaluated": cat_v["total_evaluated"],
                "negatives": n_neg,
                "positives": cat_v["positives"],
                "true_negatives": cat_v["true_negatives"],
                "false_positives": fps,
                "true_positives": cat_v["true_positives"],
                "false_negatives": cat_v["false_negatives"],
                "false_positive_rate": round(fpr_cat, 4),
                "mean_score": round(float(np.mean(scores)), 4) if scores else 0.0,
                "max_score": round(float(np.max(scores)), 4) if scores else 0.0,
            })
        category_summary.sort(key=lambda x: x["false_positives"], reverse=True)

        # Finalize source breakdown rates
        source_summary: List[Dict[str, Any]] = []
        for src_k, src_v in source_breakdown.items():
            scores = src_v["scores"]
            n_neg = src_v["negatives"]
            fps = src_v["false_positives"]
            fpr_src = (fps / n_neg) if n_neg > 0 else 0.0
            source_summary.append({
                "source": src_k,
                "total_evaluated": src_v["total_evaluated"],
                "negatives": n_neg,
                "positives": src_v["positives"],
                "true_negatives": src_v["true_negatives"],
                "false_positives": fps,
                "true_positives": src_v["true_positives"],
                "false_negatives": src_v["false_negatives"],
                "false_positive_rate": round(fpr_src, 4),
                "mean_score": round(float(np.mean(scores)), 4) if scores else 0.0,
                "max_score": round(float(np.max(scores)), 4) if scores else 0.0,
            })
        source_summary.sort(key=lambda x: x["false_positives"], reverse=True)

        # Statistical sample size caveat
        positive_sample_limitation = (
            num_positives < 30
        )  # standard rule of thumb for small sample statistical limitation
        limitation_flag = {
            "flagged": positive_sample_limitation,
            "positive_count": num_positives,
            "negative_count": num_negatives,
            "message": (
                f"CAUTION: Positive sample size in evaluated hard-negative queue is very small (N={num_positives}). "
                f"While the negative sample size (N={num_negatives}) provides high statistical power for Specificity "
                f"and False Positive Rate, metrics relying heavily on positive samples (Recall, Precision, F1-Score, "
                f"and PR-AUC) have wide confidence intervals and must be interpreted with caution."
                if positive_sample_limitation
                else "Sample sizes are sufficient for standard binomial inference."
            ),
        }

        # Format false positives and false negatives for clean reporting and audio playback
        def _format_error_item(item: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "recording_id": item["recording_id"],
                "source_provider": item["source_provider"],
                "proposed_category": item["proposed_category"],
                "original_title": item["original_title_description"],
                "creator": item["original_creator"],
                "license": item["clip_license"],
                "duration_seconds": item["duration_seconds"],
                "model_score": round(item["model_score"], 4) if item["model_score"] is not None else None,
                "model_alert": item["is_model_alert"],
                "predicted_label": item["predicted_label"],
                "human_label": item["review_status"],
                "reviewer_notes": item["reviewer_notes"],
                "reviewer_reason_code": item["reviewer_reason_code"],
                "classification_outcome": item.get("classification_outcome"),
                "has_audio": item["has_audio"] == 1,
            }

        sorted_fp = sorted(false_positives, key=lambda x: x["model_score"] or 0.0, reverse=True)
        sorted_fn = sorted(false_negatives, key=lambda x: x["model_score"] or 0.0, reverse=False)

        return {
            "evaluation_stage": "Stage 8.9.3 — Human-Verified False-Positive Analysis",
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "model_metadata": {
                "operating_threshold": self.threshold,
                "classifier_hash": EXPECTED_CLASSIFIER_SHA256,
                "metadata_hash": EXPECTED_METADATA_SHA256,
                "artifacts_verified": audit["verified"],
            },
            "dataset_audit": {
                "total_candidates": total_candidates,
                "audio_available": audio_available_count,
                "missing_audio": missing_audio_count,
                "missing_model_scores": missing_scores_count,
                "reviewed_missing_scores_count": len(reviewed_missing_scores),
                "reviewed_missing_scores_ids": reviewed_missing_scores,
                "total_human_decisions": total_reviewed,
                "decision_counts": decision_counts,
                "unreviewed_count": decision_counts["UNREVIEWED"],
            },
            "binary_evaluation": {
                "total_binary_evaluated": total_binary,
                "negative_count_approved": num_negatives,
                "positive_count_scream": num_positives,
                "excluded_ambiguous_count": len(ambiguous_records),
                "excluded_other_count": decision_counts["EXCLUDED"],
                "confusion_matrix": {
                    "true_positives": tp_count,
                    "false_negatives": fn_count,
                    "true_negatives": tn_count,
                    "false_positives": fp_count,
                },
                "metrics": {
                    "accuracy": round(accuracy, 4),
                    "precision": round(precision, 4),
                    "recall_sensitivity": round(recall, 4),
                    "specificity": round(specificity, 4),
                    "false_positive_rate": round(fpr, 4),
                    "false_negative_rate": round(fnr, 4),
                    "f1_score": round(f1_score, 4),
                    "roc_auc": round(roc_auc, 4) if roc_auc is not None else None,
                    "pr_auc": round(pr_auc, 4) if pr_auc is not None else None,
                },
                "statistical_limitation": limitation_flag,
            },
            "category_breakdown": category_summary,
            "source_breakdown": source_summary,
            "false_positives": [_format_error_item(x) for x in sorted_fp],
            "false_negatives": [_format_error_item(x) for x in sorted_fn],
            "ambiguous_records": [_format_error_item(x) for x in ambiguous_records],
        }

    def generate_evaluation_csv_stream(self) -> Generator[str, None, None]:
        """Generate streaming CSV containing all human labels, model scores, predictions, and error categories."""
        report = self.compute_evaluation_report()

        output = io.StringIO()
        writer = csv.writer(output)

        headers = [
            "recording_id",
            "source_provider",
            "proposed_category",
            "human_label",
            "model_score",
            "decision_threshold",
            "model_prediction",
            "error_category",
            "duration_seconds",
            "original_title",
            "reviewer_notes",
            "reviewer_reason_code",
            "license",
        ]
        writer.writerow(headers)
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)

        # Retrieve all candidate rows with details
        with self.store._get_connection() as conn:
            rows = conn.execute("""
                SELECT
                    recording_id, source_provider, proposed_category, review_status,
                    model_score, duration_seconds, original_title_description,
                    reviewer_notes, reviewer_reason_code, clip_license
                FROM candidates
                ORDER BY recording_id ASC
            """).fetchall()

        for r in rows:
            rec_id = r["recording_id"]
            src = r["source_provider"] or ""
            cat = r["proposed_category"] or ""
            human_label = r["review_status"]
            score = r["model_score"]
            score_str = f"{score:.4f}" if score is not None else "UNSCORED"

            pred_label = "SCREAM" if (score is not None and score >= self.threshold) else "NON_SCREAM"

            # Determine error category
            if human_label == "SCREAM_PRESENT":
                if score is not None:
                    error_cat = "TP (True Positive)" if score >= self.threshold else "FN (False Negative)"
                else:
                    error_cat = "SCREAM (Unscored)"
            elif human_label == "APPROVED_NON_SCREAM":
                if score is not None:
                    error_cat = "FP (False Positive)" if score >= self.threshold else "TN (True Negative)"
                else:
                    error_cat = "NON_SCREAM (Unscored)"
            elif human_label == "AMBIGUOUS":
                error_cat = "AMBIGUOUS (Excluded from binary)"
            elif human_label == "EXCLUDED":
                error_cat = "EXCLUDED (Excluded from binary)"
            else:
                error_cat = "UNREVIEWED"

            row_data = [
                rec_id,
                src,
                cat,
                human_label,
                score_str,
                str(self.threshold),
                pred_label,
                error_cat,
                f"{r['duration_seconds']:.2f}" if r["duration_seconds"] else "0.0",
                r["original_title_description"] or "",
                r["reviewer_notes"] or "",
                r["reviewer_reason_code"] or "",
                r["clip_license"] or "",
            ]
            writer.writerow(row_data)
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)


_analyzer_singleton: Optional[FalsePositiveAnalyzer] = None


def get_false_positive_analyzer() -> FalsePositiveAnalyzer:
    """Retrieve singleton instance of FalsePositiveAnalyzer."""
    global _analyzer_singleton
    if _analyzer_singleton is None:
        _analyzer_singleton = FalsePositiveAnalyzer()
    return _analyzer_singleton
