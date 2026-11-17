"""Dataset manifest building, leakage-safe splitting, and integrity validation."""

from src.dataset.split_builder import (
    build_unified_manifest,
    create_leakage_safe_splits,
    verify_no_leakage,
    save_unified_and_split_manifests,
    generate_stage4_summary_report,
)
from src.dataset.verifier import (
    verify_manifests_and_cache,
    VerificationError,
)
from src.dataset.feature_loader import (
    load_dataset_split,
)
from src.dataset.hard_negatives import (
    HARD_NEGATIVE_CATEGORIES,
    REVIEW_STATUSES,
    DuplicateClipError,
    InvalidCategoryError,
    IngestionValidationError,
    ingest_audio_clip,
    scan_and_ingest_hard_negatives,
    load_approved_hard_negatives,
    save_review_csv,
    save_hard_negatives_manifest,
)

__all__ = [
    "build_unified_manifest",
    "create_leakage_safe_splits",
    "verify_no_leakage",
    "save_unified_and_split_manifests",
    "generate_stage4_summary_report",
    "verify_manifests_and_cache",
    "VerificationError",
    "load_dataset_split",
    "HARD_NEGATIVE_CATEGORIES",
    "REVIEW_STATUSES",
    "DuplicateClipError",
    "InvalidCategoryError",
    "IngestionValidationError",
    "ingest_audio_clip",
    "scan_and_ingest_hard_negatives",
    "load_approved_hard_negatives",
    "save_review_csv",
    "save_hard_negatives_manifest",
]
