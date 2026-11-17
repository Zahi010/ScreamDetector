"""Synchronize Stage 8.8 manifests (JSON and CSV) from the live SQLite review database."""

from __future__ import annotations

import csv
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from src.config import STAGE8_8_MANIFEST_CSV, STAGE8_8_MANIFEST_JSON
from src.database.review_store import get_review_store


def sync_manifest_files():
    store = get_review_store()
    with store._get_connection() as conn:
        rows = conn.execute("SELECT * FROM candidates ORDER BY recording_id ASC").fetchall()

    candidates = [dict(r) for r in rows]

    # Parse JSON list fields for JSON output
    for c in candidates:
        for fld in ("original_annotations", "unresolved_issues", "yamnet_top_classes", "yamnet_relevant_tags"):
            val = c.get(fld)
            if isinstance(val, str):
                try:
                    c[fld] = json.loads(val)
                except Exception:
                    c[fld] = []

    payload = {
        "version": "Stage_8.9.2_Hard_Negatives_Recovered",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total_candidates": len(candidates),
        "audio_available": sum(1 for c in candidates if c["has_audio"]),
        "candidates": candidates,
    }

    # Save JSON manifest
    STAGE8_8_MANIFEST_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(STAGE8_8_MANIFEST_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    # Save CSV manifest
    if candidates:
        fieldnames = [
            "recording_id", "source_provider", "original_source_id", "original_source_url",
            "local_path", "has_audio", "original_filename", "sha256_original", "sha256_derived",
            "original_creator", "original_title_description", "dataset_license", "clip_license",
            "commercial_compatibility", "retrieval_timestamp", "duration_seconds", "sample_rate",
            "channels", "proposed_category", "provisional_label", "review_status",
            "download_validation_status", "model_score", "model_alert", "triage_group", "triage_reason"
        ]
        with open(STAGE8_8_MANIFEST_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for c in candidates:
                writer.writerow(c)

    print(f"Manifests successfully synced: {len(candidates)} candidates, {payload['audio_available']} audio available.")


if __name__ == "__main__":
    sync_manifest_files()
