"""Automated Audio Quality Control & Deduplication Validation (Stage 8.8).

Runs:
1. Signal integrity audit (NaNs, Infs, clipping, silence, duration bounds).
2. Content hash deduplication (exact SHA-256 and PCM audio collisions).
3. Historical dataset leakage audit against Stage 4/5/6 splits.
4. Generates standardized 16 kHz mono float32 derivatives.
5. Emits `audio_quality_report.csv` and `duplicate_report.csv`.

Usage:
  python scripts/validate_hard_negatives.py
"""

from __future__ import annotations

import csv
import logging
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from src.config import STAGE8_8_PROCESSED_DIR, STAGE8_8_REPORTS_DIR
from src.dataset.acquisition_client import AcquisitionPipeline
from src.dataset.acquisition_validator import AudioQualityValidator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("validate_hard_negatives")


def main() -> int:
    print("=" * 80)
    print("STAGE 8.8 — AUDIO QUALITY CONTROL & DEDUPLICATION AUDIT")
    print("=" * 80)

    pipeline = AcquisitionPipeline()
    if not pipeline.candidates:
        print("[WARNING] No candidates found in manifest. Running discovery first...")
        pipeline.discover_freesound()
        pipeline.discover_fsd50k()
        pipeline.discover_audioset()

    validator = AudioQualityValidator(processed_dir=STAGE8_8_PROCESSED_DIR)

    quality_rows = []
    duplicate_rows = []

    clean_count = 0
    flagged_count = 0
    not_acquired_count = 0
    dup_count = 0

    print(f"Auditing {len(pipeline.candidates)} candidates...")

    for c in pipeline.candidates.values():
        res = validator.validate_and_process(c)

        if res.status == "NOT_ACQUIRED":
            not_acquired_count += 1
        elif res.is_valid:
            clean_count += 1
        else:
            flagged_count += 1

        if res.is_exact_duplicate or res.duplicate_of:
            dup_count += 1
            duplicate_rows.append({
                "recording_id": c.recording_id,
                "file_sha256": res.file_sha256,
                "pcm_sha256": res.pcm_sha256,
                "is_exact_duplicate": res.is_exact_duplicate,
                "duplicate_of": res.duplicate_of or "N/A",
                "is_historical_collision": res.is_historical_collision,
                "resolution": "Flagged as duplicate, preserved in manifest without deletion.",
            })

        quality_rows.append({
            "recording_id": c.recording_id,
            "status": res.status,
            "is_valid": res.is_valid,
            "duration_sec": f"{res.duration_seconds:.2f}",
            "sample_rate": res.sample_rate,
            "channels": res.channels,
            "rms_energy": f"{res.rms_energy:.6f}",
            "peak_amplitude": f"{res.peak_amplitude:.4f}",
            "clipping_detected": res.clipping_detected,
            "silence_detected": res.silence_detected,
            "has_nan_inf": res.has_nan_or_inf,
            "file_sha256": res.file_sha256,
            "pcm_sha256": res.pcm_sha256,
            "derived_file": Path(res.derived_path).name if res.derived_path else "None",
            "derived_sha256": res.derived_sha256 or "None",
            "rejection_reasons": "; ".join(res.rejection_reasons),
        })

    # Save manifest updates
    pipeline.save_manifest()

    # Generate CSV Reports
    STAGE8_8_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    quality_csv = STAGE8_8_REPORTS_DIR / "audio_quality_report.csv"
    dup_csv = STAGE8_8_REPORTS_DIR / "duplicate_report.csv"

    if quality_rows:
        with open(quality_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(quality_rows[0].keys()))
            writer.writeheader()
            writer.writerows(quality_rows)

    with open(dup_csv, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "recording_id", "file_sha256", "pcm_sha256", "is_exact_duplicate",
            "duplicate_of", "is_historical_collision", "resolution",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        if duplicate_rows:
            writer.writerows(duplicate_rows)

    print("\n" + "=" * 80)
    print("QUALITY CONTROL & DEDUPLICATION SUMMARY:")
    print(f"Total Candidates Evaluated    : {len(pipeline.candidates)}")
    print(f"Validated Clean (Waveforms)   : {clean_count}")
    print(f"Flagged Quality Issues        : {flagged_count}")
    print(f"Metadata-Only (Not Acquired)  : {not_acquired_count}")
    print(f"Duplicates Detected           : {dup_count}")
    print(f"Quality Report Saved To       : {quality_csv}")
    print(f"Duplicate Report Saved To     : {dup_csv}")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
