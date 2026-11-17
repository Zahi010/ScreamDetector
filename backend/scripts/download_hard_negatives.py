"""Automated Download & Acquisition of Eligible Hard Negatives (Stage 8.8).

Enforces:
1. Available host disk space check before downloading.
2. License filtering: only CC0 and CC BY approved for downstream use.
3. AudioSet metadata-only enforcement (strictly no YouTube scraping).
4. FSD50K storage warning & selective acquisition.
5. Resumable download manifest.
6. Permissive synthesis for offline pipeline validation.

Usage:
  python scripts/download_hard_negatives.py --dry-run
  python scripts/download_hard_negatives.py --source freesound --dry-run
  python scripts/download_hard_negatives.py --source audioset --metadata-only
  python scripts/download_hard_negatives.py --resume
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from src.config import (
    PROJECT_ROOT,
    STAGE8_8_DATASET_DIR,
    STAGE8_8_RAW_DIR,
    get_freesound_api_key,
    load_project_env,
)
from src.dataset.acquisition_client import AcquisitionPipeline, check_disk_space
from src.dataset.acquisition_types import DownloadStatus, LicenseStatus, TARGET_CATEGORIES

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("download_hard_negatives")


def main() -> int:
    parser = argparse.ArgumentParser(description="Download eligible hard-negative audio clips.")
    parser.add_argument(
        "--source",
        type=str,
        default="all",
        choices=["all", "fsd50k", "freesound", "audioset", "permissive"],
        help="Target source for acquisition (default: all).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate downloads, report planned storage requirements without fetching files.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume previously interrupted download session using existing manifest.",
    )
    parser.add_argument(
        "--metadata-only",
        action="store_true",
        help="Acquire metadata only without fetching waveforms (mandatory for AudioSet).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=30,
        help="Total acquisition limit.",
    )
    parser.add_argument(
        "--category",
        type=str,
        default=None,
        choices=list(TARGET_CATEGORIES.keys()),
        help="Filter downloads by target category.",
    )
    args = parser.parse_args()

    print("=" * 80)
    print("STAGE 8.8 — AUTOMATED HARD-NEGATIVE ACQUISITION & DOWNLOAD")
    print("=" * 80)

    # 1. Load environment and check disk space
    load_project_env(override=False)
    freesound_key = get_freesound_api_key()

    has_space, free_bytes, space_msg = check_disk_space(STAGE8_8_DATASET_DIR, min_required_bytes=500 * 1024 * 1024)
    print(f"Host Disk Space Check: {space_msg}")
    if not has_space and not args.dry_run:
        print("[ERROR] Cannot proceed with downloads due to critical disk space constraints.", file=sys.stderr)
        return 1

    pipeline = AcquisitionPipeline(freesound_api_key=freesound_key, dry_run=args.dry_run)

    # Make sure discovery records exist
    if not pipeline.candidates or not args.resume:
        print("\nDiscovering candidates across target sources...")
        pipeline.discover_freesound(limit_per_category=5)
        pipeline.discover_fsd50k()
        pipeline.discover_audioset()

    print(f"Total candidates in manifest: {len(pipeline.candidates)}")

    downloaded_count = 0
    skipped_license_count = 0
    metadata_only_count = 0

    # 2. Process AudioSet
    if args.source in ("all", "audioset"):
        print("\n--- Processing Source C: AudioSet ---")
        print("Note: AudioSet provides segment annotations and YouTube IDs only.")
        print("Scraping YouTube via yt-dlp is prohibited. Marking candidates as NOT_ACQUIRED.")
        for c in pipeline.candidates.values():
            if c.source_provider == "audioset":
                c.download_validation_status = DownloadStatus.NOT_ACQUIRED.value
                metadata_only_count += 1
        print(f"AudioSet candidates logged: {metadata_only_count} (Metadata Only, 0 bytes audio)")

    # 3. Process FSD50K
    if args.source in ("all", "fsd50k"):
        print("\n--- Processing Source A: FSD50K ---")
        print("Official dataset archive size: 14 GB (development audio).")
        free_gb = free_bytes / (1024 ** 3)
        print(f"Current available host disk space: {free_gb:.2f} GB.")
        if free_gb < 15.0:
            print("ALERT: Insufficient space for full 14 GB FSD50K extraction.")
            print("Enforcing selective per-recording metadata parsing and individual clip acquisition.")
        for c in pipeline.candidates.values():
            if c.source_provider == "fsd50k":
                if c.commercial_compatibility in (LicenseStatus.CC0_VERIFIED.value, LicenseStatus.CC_BY_VERIFIED.value):
                    if args.dry_run:
                        print(f"[DRY-RUN] Would acquire FSD50K clip {c.original_source_id} (~{c.duration_seconds * 0.15:.2f} MB)")
                else:
                    c.download_validation_status = DownloadStatus.SKIPPED_LICENSING.value
                    skipped_license_count += 1

        if not args.dry_run:
            print("Selectively acquiring verified CC0 / CC BY audio clips from E: to local collection...")
            fsd_acquired = pipeline.acquire_selected_fsd50k_audio(limit_per_category=min(args.limit, 20))
            print(f"Successfully acquired {fsd_acquired} verified FSD50K audio clips.")
            downloaded_count += fsd_acquired

    # 4. Process Freesound API
    if args.source in ("all", "freesound"):
        print("\n--- Processing Source B: Freesound ---")
        if not freesound_key:
            print("NOTICE: FREESOUND_API_KEY environment variable is not configured.")
            print("Setup instructions:")
            print("  1. Request an API key at https://freesound.org/help/developers/")
            print(f"  2. Add 'FREESOUND_API_KEY=your_key_here' to your project-root .env file ({PROJECT_ROOT / '.env'}).")
            print("  3. Running in verified dry-run simulation mode with deterministic seeds.")
        else:
            print(f"Freesound API key loaded successfully ({len(freesound_key)} chars, secret masked).")
        for c in pipeline.candidates.values():
            if c.source_provider == "freesound":
                if c.commercial_compatibility in (LicenseStatus.CC0_VERIFIED.value, LicenseStatus.CC_BY_VERIFIED.value):
                    if args.dry_run:
                        print(f"[DRY-RUN] Planned Freesound fetch: {c.recording_id} ({c.clip_license})")
                else:
                    c.download_validation_status = DownloadStatus.SKIPPED_LICENSING.value
                    skipped_license_count += 1

    # 5. Acquire Verified Permissive Samples (Offline Safety)
    if args.source in ("all", "permissive") and not args.dry_run:
        print("\n--- Acquiring Verified Permissive Samples (CC0) for Pipeline Validation ---")
        gen_count = pipeline.generate_synthetic_permissive_audio()
        print(f"Successfully generated and verified {gen_count} clean CC0 reference audio files in {STAGE8_8_RAW_DIR}.")
        downloaded_count += gen_count

    pipeline.save_manifest()

    print("\n" + "=" * 80)
    print("ACQUISITION & DOWNLOAD AUDIT SUMMARY:")
    print(f"Total Discovered Candidates   : {len(pipeline.candidates)}")
    print(f"Audio Files Downloaded/Stored : {downloaded_count}")
    print(f"Skipped Due to License        : {skipped_license_count}")
    print(f"Metadata-Only (AudioSet)      : {metadata_only_count}")
    print(f"Dry-Run Execution             : {args.dry_run}")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
