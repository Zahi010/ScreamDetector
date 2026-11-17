"""Human Review Queue and Labeling Workflow (Stage 8.8).

Manages:
1. Priority-based sorting of candidate recordings for human listening review.
2. Review statuses: UNREVIEWED, APPROVED_NON_SCREAM, SCREAM_PRESENT, AMBIGUOUS, EXCLUDED.
3. Queue sorting by:
   - Category Priority (Stage 8.7 gap rank)
   - License Confidence (CC0_VERIFIED / CC_BY_VERIFIED first)
   - Audio Quality (VALIDATED_CLEAN first)
   - Duplicate Status (unique recordings first)
   - Model Scream Score (high score prioritized for inspection, without setting label).
4. Exporting review queue CSV and updating review manifests.
"""

from __future__ import annotations

import csv
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.config import (
    STAGE8_8_APPROVED_DIR,
    STAGE8_8_METADATA_DIR,
    STAGE8_8_REJECTED_DIR,
    STAGE8_8_REVIEW_DIR,
)
from src.dataset.acquisition_types import (
    AcquisitionCandidate,
    DownloadStatus,
    LicenseStatus,
    ReviewStatus,
    TARGET_CATEGORIES,
)

logger = logging.getLogger("acquisition_reviewer")

LICENSE_PRIORITY_ORDER = {
    LicenseStatus.CC0_VERIFIED.value: 1,
    LicenseStatus.CC_BY_VERIFIED.value: 2,
    LicenseStatus.REQUIRES_REVIEW.value: 3,
    LicenseStatus.NONCOMMERCIAL_ONLY.value: 4,
    LicenseStatus.RESTRICTED.value: 5,
    LicenseStatus.UNKNOWN.value: 6,
}


def compute_review_priority_score(c: AcquisitionCandidate) -> Tuple[int, int, int, int, float]:
    """Calculate tuple for sorting review priority (lower is higher priority).

    Sort order:
    1. Category Priority (1 = Whistle, 2 = Cheering, 3 = EDM, etc.)
    2. License Priority (1 = CC0, 2 = CC_BY, etc.)
    3. Audio Quality (1 = VALIDATED_CLEAN / DOWNLOADED, 2 = FLAGGED, 3 = NOT_ACQUIRED)
    4. Duplicate Status (1 = Unique, 2 = Duplicate)
    5. Inverted Model Score (-model_score so highest probability comes first)
    """
    cat_info = TARGET_CATEGORIES.get(c.proposed_category, {})
    cat_rank = cat_info.get("priority", 99)

    lic_rank = LICENSE_PRIORITY_ORDER.get(c.commercial_compatibility, 99)

    qual_rank = 1 if c.download_validation_status in (
        DownloadStatus.VALIDATED_CLEAN.value, DownloadStatus.DOWNLOADED.value
    ) else (2 if c.download_validation_status == DownloadStatus.FLAGGED_QUALITY.value else 3)

    dup_rank = 2 if (c.duplicate_or_source_group and "duplicate" in c.duplicate_or_source_group.lower()) else 1

    inv_score = -(c.model_score or 0.0)

    return (cat_rank, lic_rank, qual_rank, dup_rank, inv_score)


class ReviewQueueManager:
    """Builds and manages human-review queue for acquired recordings."""

    def __init__(self, candidates: Dict[str, AcquisitionCandidate]):
        self.candidates = candidates

    def get_sorted_queue(self) -> List[AcquisitionCandidate]:
        """Return candidates sorted by human-review priority."""
        # Focus queue on acquired audio first, but include all
        return sorted(self.candidates.values(), key=compute_review_priority_score)

    def export_queue_csv(self, output_path: Path) -> int:
        """Export review queue CSV sorted by inspection priority."""
        sorted_candidates = self.get_sorted_queue()
        fieldnames = [
            "queue_position",
            "recording_id",
            "proposed_category",
            "priority_rank",
            "commercial_compatibility",
            "download_validation_status",
            "model_score",
            "model_alert",
            "review_status",
            "duration_seconds",
            "original_creator",
            "original_title_description",
            "clip_license",
            "unresolved_issues",
        ]

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for idx, c in enumerate(sorted_candidates, start=1):
                cat_info = TARGET_CATEGORIES.get(c.proposed_category, {})
                writer.writerow({
                    "queue_position": idx,
                    "recording_id": c.recording_id,
                    "proposed_category": c.proposed_category,
                    "priority_rank": cat_info.get("priority", 99),
                    "commercial_compatibility": c.commercial_compatibility,
                    "download_validation_status": c.download_validation_status,
                    "model_score": f"{c.model_score:.4f}" if c.model_score is not None else "N/A",
                    "model_alert": "ALERT" if c.model_alert else "CLEAR" if c.model_alert is not None else "N/A",
                    "review_status": c.review_status,
                    "duration_seconds": f"{c.duration_seconds:.2f}",
                    "original_creator": c.original_creator,
                    "original_title_description": c.original_title_description[:80],
                    "clip_license": c.clip_license,
                    "unresolved_issues": "; ".join(c.unresolved_issues),
                })

        return len(sorted_candidates)

    def update_label(
        self,
        recording_id: str,
        new_status: str,
        reviewer_notes: str = "",
    ) -> bool:
        """Update review status for a specific candidate.

        Valid statuses: UNREVIEWED, APPROVED_NON_SCREAM, SCREAM_PRESENT, AMBIGUOUS, EXCLUDED.
        """
        valid_statuses = {s.value for s in ReviewStatus}
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid review status: '{new_status}'. Allowed: {valid_statuses}")

        if recording_id not in self.candidates:
            logger.warning(f"Recording ID '{recording_id}' not found in candidates.")
            return False

        c = self.candidates[recording_id]
        c.review_status = new_status
        if reviewer_notes:
            c.unresolved_issues.append(f"Reviewer note ({datetime.now(timezone.utc).isoformat()}): {reviewer_notes}")

        # Update local file placement if approved/rejected
        if new_status == ReviewStatus.APPROVED_NON_SCREAM.value and c.local_path:
            target = STAGE8_8_APPROVED_DIR / Path(c.local_path).name
            if Path(c.local_path).exists() and not target.exists():
                import shutil
                shutil.copy2(c.local_path, target)
        elif new_status in (ReviewStatus.SCREAM_PRESENT.value, ReviewStatus.EXCLUDED.value) and c.local_path:
            target = STAGE8_8_REJECTED_DIR / Path(c.local_path).name
            if Path(c.local_path).exists() and not target.exists():
                import shutil
                shutil.copy2(c.local_path, target)

        return True
