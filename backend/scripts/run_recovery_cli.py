"""CLI script to run and verify Missing Audio Recovery (Stage 8.9.2)."""

from __future__ import annotations

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from src.dataset.audio_recovery_service import get_audio_recovery_service


def main():
    service = get_audio_recovery_service()
    
    print("=" * 70)
    print("STAGE 8.9.2 — MISSING AUDIO RECOVERY EXECUTION")
    print("=" * 70)

    print("\n[Step 1] Auditing initial missing candidate status...")
    pre_audit = service.get_audit()
    print(f"  Total Candidates in DB    : {pre_audit['total_candidates']}")
    print(f"  Audio Available           : {pre_audit['audio_available']}")
    print(f"  Missing Audio             : {pre_audit['missing_audio']}")
    print(f"  Missing by Source         : {pre_audit['missing_by_source']}")
    print(f"  Existing on E: Disk       : {pre_audit['existing_on_disk']}")
    print(f"  Never Downloaded (FS)     : {pre_audit['never_downloaded']}")
    print(f"  Licence Restricted (AS)   : {pre_audit['licence_restricted']}")
    print(f"  Source Unavailable (Seed) : {pre_audit['source_unavailable']}")
    print(f"  Preserved Reviews         : {pre_audit['preserved_human_reviews']}")

    print("\n[Step 2] Executing recovery workflow...")
    def on_progress(p):
        if p["current_index"] % 25 == 0 or p["current_index"] == p["total_items"]:
            print(f"  Progress: {p['current_index']}/{p['total_items']} - "
                  f"FSD50K: {p['recovered_fsd50k']}, Freesound: {p['recovered_freesound']}, "
                  f"Restricted: {p['restricted_audioset']}, Unavailable: {p['unavailable_fsd50k']}")

    res = service.recover_missing_audio(progress_callback=on_progress)

    print("\n[Step 3] Recovery Finished:")
    print(f"  Processed Count           : {res['processed_count']}")
    print(f"  Recovered FSD50K          : {res['recovered_fsd50k']}")
    print(f"  Recovered Freesound       : {res['recovered_freesound']}")
    print(f"  Total Newly Recovered     : {res['total_newly_recovered']}")
    print(f"  Restricted (AudioSet)     : {res['restricted_audioset']}")
    print(f"  Unavailable (Seeds)       : {res['unavailable_fsd50k']}")
    print(f"  Failed Downloads          : {res['failed_downloads']}")

    post_audit = res["post_recovery_audit"]
    print("\n[Step 4] Updated Dashboard Totals:")
    print(f"  Total Candidates          : {post_audit['total_candidates']}")
    print(f"  Audio Available           : {post_audit['audio_available']}")
    print(f"  Missing Audio             : {post_audit['missing_audio']}")
    print(f"  Preserved Reviews Check   : {post_audit['preserved_human_reviews']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
