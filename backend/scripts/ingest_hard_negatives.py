"""Hard-Negative Audio Ingestion Script (Stage 6).

Scans candidate hard-negative audio directories, validates audio parameters,
computes content hashes, checks for duplicate recordings against existing datasets,
and updates hard_negatives_manifest.json and hard_negatives_review.csv.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from src.config import (
    HARD_NEGATIVES_DIR,
    HARD_NEGATIVES_FALLBACK_DIR,
    HARD_NEGATIVES_MANIFEST,
    HARD_NEGATIVES_REVIEW_CSV,
    REPORTS_DIR,
)
from src.dataset.hard_negatives import (
    HARD_NEGATIVE_CATEGORIES,
    REVIEW_STATUSES,
    scan_and_ingest_hard_negatives,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("ingest_hard_negatives")


def generate_data_review_summary_report(
    records: List[Dict[str, Any]],
    summary: Dict[str, Any],
    report_path: Path,
) -> None:
    """Generate Markdown report summarizing the state of the hard-negative dataset."""
    report_path.parent.mkdir(parents=True, exist_ok=True)

    status_counts = {k: sum(1 for r in records if r.get("review_status") == k) for k in REVIEW_STATUSES}
    category_counts = {k: sum(1 for r in records if r.get("sound_category") == k) for k in HARD_NEGATIVE_CATEGORIES}

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Stage 6 Hard-Negative Data Ingestion & Review Audit\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")

        f.write("## 1. Directory & Ingestion Summary\n\n")
        f.write(f"- **Primary Ingestion Directory**: `{HARD_NEGATIVES_DIR}`\n")
        f.write(f"- **Fallback Ingestion Directory**: `{HARD_NEGATIVES_FALLBACK_DIR}`\n")
        f.write(f"- **Total Discovered WAV Files**: **{summary['wav_files_found']}**\n")
        f.write(f"- **Successfully Ingested**: **{summary['ingested_count']}**\n")
        f.write(f"- **Duplicates Skipped (Hash Collisions)**: **{summary['duplicates_skipped']}**\n\n")

        if len(records) == 0:
            f.write("> [!NOTE]\n")
            f.write("> **Empty Ingestion Directory Status**:\n")
            f.write("> Currently, 0 external hard-negative audio files have been placed into the ingestion directories. ")
            f.write("In accordance with project methodology, no synthetic or fabricated files were generated to simulate data. ")
            f.write("Model retraining is safely blocked until real, human-reviewed recordings are ingested.\n\n")

        f.write("---\n\n")
        f.write("## 2. Review Status Breakdown\n\n")
        f.write("| Review Status | Description | Count |\n")
        f.write("| :--- | :--- | :--- |\n")
        for st_name, desc in REVIEW_STATUSES.items():
            f.write(f"| **`{st_name}`** | {desc} | {status_counts.get(st_name, 0)} |\n")
        f.write(f"| **Total** | All tracked hard-negative records | **{len(records)}** |\n\n")

        f.write("---\n\n")
        f.write("## 3. Acoustic Category Breakdown\n\n")
        f.write("| Category | Description | Ingested Count |\n")
        f.write("| :--- | :--- | :--- |\n")
        for cat_name, desc in HARD_NEGATIVE_CATEGORIES.items():
            f.write(f"| **`{cat_name}`** | {desc} | {category_counts.get(cat_name, 0)} |\n")

        f.write("\n---\n\n")
        f.write("## 4. Licensing and Rights Audit\n\n")
        f.write("All ingested hard-negative audio must carry explicit licensing tags. OpenSLR 99 and NIGENS carry **CC BY-NC-ND 4.0** licenses, ")
        f.write("which prohibit commercial deployment and derivative distribution. New hard negatives must prioritize permissive licenses:\n")
        f.write("- **Commercial-Safe**: Creative Commons Zero (`CC0 1.0`), Public Domain, or Attribution (`CC BY 4.0`).\n")
        f.write("- **Research-Only**: Non-Commercial (`CC BY-NC 4.0`) or ShareAlike (`CC BY-SA 4.0`) must be flagged as non-commercial.\n\n")

        if records:
            f.write("### Tracked Licenses in Manifest\n\n")
            license_counts: Dict[str, int] = {}
            for r in records:
                lic = r.get("license", "Unknown")
                license_counts[lic] = license_counts.get(lic, 0) + 1
            for lic, cnt in sorted(license_counts.items(), key=lambda x: x[1], reverse=True):
                f.write(f"- `{lic}`: {cnt} clips\n")
            f.write("\n")

        f.write("---\n\n")
        f.write("## 5. Next Steps for Data Collection\n\n")
        f.write("To populate hard negatives:\n")
        f.write("1. Place candidate WAV files into `data/raw/hard_negatives/<category>/`.\n")
        f.write("2. Run `python backend/scripts/ingest_hard_negatives.py` to index and hash them.\n")
        f.write("3. Review clips using `python backend/scripts/review_hard_negatives.py` to approve or reject.\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest and hash candidate hard-negative audio files.")
    parser.add_argument("--input-dir", type=str, default=None, help="Optional custom folder of WAV files.")
    parser.add_argument("--manifest", type=str, default=None, help="Custom manifest output path.")
    parser.add_argument("--review-csv", type=str, default=None, help="Custom review CSV output path.")
    args = parser.parse_args()

    print("=" * 75)
    print("STAGE 6 — HARD-NEGATIVE DATA INGESTION & AUDIT")
    print("=" * 75)

    custom_dirs = [Path(args.input_dir).resolve()] if args.input_dir else None
    target_manifest = Path(args.manifest).resolve() if args.manifest else HARD_NEGATIVES_MANIFEST
    target_csv = Path(args.review_csv).resolve() if args.review_csv else HARD_NEGATIVES_REVIEW_CSV

    print(f"\n[Step 1/3] Scanning target directories for candidate audio...")
    records, summary = scan_and_ingest_hard_negatives(
        input_dirs=custom_dirs,
        manifest_path=target_manifest,
        review_csv_path=target_csv,
    )

    print(f"  - Directories checked:   {summary['directories_checked']}")
    print(f"  - WAV files discovered:  {summary['wav_files_found']}")
    print(f"  - Newly ingested clips:  {summary['ingested_count']}")
    print(f"  - Duplicates skipped:    {summary['duplicates_skipped']}")

    if summary["errors"]:
        print("\n[Ingestion Notices]:")
        for err in summary["errors"]:
            print(f"  - {err}")

    # Generate Audit Report
    print(f"\n[Step 2/3] Writing manifests and review CSV...")
    print(f"  - Manifest JSON:         {target_manifest}")
    print(f"  - Review CSV:            {target_csv}")

    report_path = REPORTS_DIR / "stage6_data_review_summary.md"
    print(f"\n[Step 3/3] Generating data review summary report...")
    generate_data_review_summary_report(records, summary, report_path)
    print(f"  - Summary Report:        {report_path}")

    print("\n" + "=" * 75)
    if len(records) == 0:
        print("[STATUS] Ingestion pipeline verified. Hard-negative directories are currently empty.")
        print("         Follow the instructions in the report to place candidate recordings.")
    else:
        approved_count = sum(1 for r in records if r.get("review_status") in ["approved_non_scream", "approved_scream"])
        pending_count = sum(1 for r in records if r.get("review_status") == "pending_review")
        print(f"[STATUS] Ingestion complete. Tracked: {len(records)} | Approved: {approved_count} | Pending: {pending_count}")
    print("=" * 75 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
