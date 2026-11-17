"""Automated Discovery of Candidate Hard Negatives (Stage 8.8).

Searches and catalogues candidates across:
1. FSD50K official ontology and per-clip license metadata
2. Freesound API (or verified seed bank in dry-run mode)
3. AudioSet ontology and segment mappings (metadata-only discovery)

Usage:
  python scripts/discover_hard_negatives.py --dry-run
  python scripts/discover_hard_negatives.py --source freesound --limit 20
  python scripts/discover_hard_negatives.py --source fsd50k
  python scripts/discover_hard_negatives.py --source audioset
  python scripts/discover_hard_negatives.py --source all
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

from src.config import STAGE8_8_METADATA_DIR, get_freesound_api_key, load_project_env
from src.dataset.acquisition_client import AcquisitionPipeline
from src.dataset.acquisition_types import TARGET_CATEGORIES

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("discover_hard_negatives")


def main() -> int:
    parser = argparse.ArgumentParser(description="Discover candidate hard-negative audio from external datasets.")
    parser.add_argument(
        "--source",
        type=str,
        default="all",
        choices=["all", "freesound", "fsd50k", "audioset"],
        help="Data source to query (default: all).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run discovery in dry-run mode without external live network calls.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Max candidates to discover per query/category.",
    )
    parser.add_argument(
        "--category",
        type=str,
        default=None,
        choices=list(TARGET_CATEGORIES.keys()),
        help="Optional specific category filter.",
    )
    args = parser.parse_args()

    load_project_env(override=False)
    freesound_key = get_freesound_api_key()

    print("=" * 80)
    print("STAGE 8.8 — AUTOMATED HARD-NEGATIVE DISCOVERY")
    print("=" * 80)
    print(f"Target Source   : {args.source}")
    print(f"Dry-Run Mode    : {args.dry_run}")
    print(f"Per-Cat Limit   : {args.limit}")
    print(f"Category Filter : {args.category or 'All Categories'}")
    print(f"Freesound Key   : {'Configured (' + str(len(freesound_key)) + ' chars, masked)' if freesound_key else 'Missing (Dry-Run Seeds Active)'}")
    print("-" * 80)

    pipeline = AcquisitionPipeline(freesound_api_key=freesound_key, dry_run=args.dry_run)
    cats = [args.category] if args.category else None

    total_discovered = 0

    if args.source in ("all", "freesound"):
        print("\n[1/3] Querying Freesound...")
        fs_candidates = pipeline.discover_freesound(categories=cats, limit_per_category=args.limit)
        print(f"      Discovered {len(fs_candidates)} Freesound candidates.")
        total_discovered += len(fs_candidates)

    if args.source in ("all", "fsd50k"):
        print("\n[2/3] Querying FSD50K Metadata & Ontology...")
        fsd_candidates = pipeline.discover_fsd50k()
        print(f"      Discovered {len(fsd_candidates)} FSD50K candidates.")
        total_discovered += len(fsd_candidates)

    if args.source in ("all", "audioset"):
        print("\n[3/3] Querying AudioSet Ontology & Segments (Metadata Only)...")
        as_candidates = pipeline.discover_audioset()
        print(f"      Discovered {len(as_candidates)} AudioSet candidates (Marked NOT_ACQUIRED).")
        total_discovered += len(as_candidates)

    manifest_json = STAGE8_8_METADATA_DIR / "stage8_8_manifest.json"
    manifest_csv = STAGE8_8_METADATA_DIR / "stage8_8_manifest.csv"

    print("\n" + "=" * 80)
    print(f"DISCOVERY SUMMARY:")
    print(f"Total Candidates Discovered: {total_discovered}")
    print(f"Total In Manifest          : {len(pipeline.candidates)}")
    print(f"Manifest JSON Saved To     : {manifest_json}")
    print(f"Manifest CSV Saved To      : {manifest_csv}")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
