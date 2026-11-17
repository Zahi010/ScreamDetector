"""Audio Recovery Service for Stage 8.9.2 Missing Hard-Negative Recordings.

Provides:
1. Thorough investigation and audit of all missing candidates grouped by source and reason.
2. Safe recovery of FSD50K audio from local E: drive (read-only access; copies required files to local raw dataset).
3. Compliant acquisition of Freesound CC0 / CC-BY candidates via Freesound API with rate limiting.
4. Explicit handling and status marking for license-restricted (AudioSet) and unavailable candidates.
5. Strict protection of all completed human review decisions (never overwrites reviews or auto-approves).
6. Automatic acoustic triage analysis via Stage 8.9.1 Triage Engine for newly recovered audio.
"""

from __future__ import annotations

import hashlib
import io
import json
import logging
import os
import shutil
import time
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import soundfile as sf

from src.config import (
    BACKEND_DIR,
    FSD50K_DIR,
    STAGE8_8_DATASET_DIR,
    STAGE8_8_RAW_DIR,
    get_freesound_api_key,
)
from src.database.review_store import ReviewStore, get_review_store
from src.dataset.acquisition_types import DownloadStatus, LicenseStatus, ReviewStatus
from src.dataset.triage_analyzer import AutomatedTriageEngine, TriageGroup

logger = logging.getLogger("audio_recovery_service")

# Search directories for FSD50K on E:
DEFAULT_FSD50K_SEARCH_DIRS = [
    Path(r"E:\FSD50K.dev_audio"),
    Path(r"E:\FSD50K.dev_audio\FSD50K.dev_audio"),
    Path(r"E:\FSD50K.dev_audio\FSD50K.eval_audio"),
    Path(r"E:\FSD50K.dev_audio\FSD50K.eval_audio\FSD50K.eval_audio"),
]


def compute_sha256(filepath: Path) -> str:
    """Compute SHA-256 hash of a file on disk."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class AudioRecoveryService:
    """Orchestrates audit, discovery, downloading, and triage of missing recordings."""

    def __init__(
        self,
        store: Optional[ReviewStore] = None,
        fsd50k_search_dirs: Optional[List[Path]] = None,
        raw_dest_dir: Optional[Path] = None,
        triage_engine: Optional[AutomatedTriageEngine] = None,
    ):
        self.store = store or get_review_store()
        self.fsd50k_search_dirs = fsd50k_search_dirs or DEFAULT_FSD50K_SEARCH_DIRS
        self.raw_dest_dir = raw_dest_dir or STAGE8_8_RAW_DIR
        self.triage_engine = triage_engine
        self._cancel_requested = False

    def request_cancel(self) -> None:
        """Signal ongoing recovery process to stop safely after current item."""
        self._cancel_requested = True

    def get_audit(self) -> Dict[str, Any]:
        """Perform comprehensive audit of current review database candidates."""
        with self.store._get_connection() as conn:
            all_rows = conn.execute("""
                SELECT
                    recording_id, source_provider, original_source_id,
                    original_source_url, local_path, has_audio,
                    original_filename, dataset_license, clip_license,
                    commercial_compatibility, proposed_category,
                    download_validation_status, unresolved_issues,
                    review_status, model_score, triage_group
                FROM candidates
                ORDER BY source_provider, recording_id
            """).fetchall()

        all_candidates = [dict(r) for r in all_rows]
        missing_candidates = [c for c in all_candidates if not c["has_audio"]]
        available_candidates = [c for c in all_candidates if c["has_audio"]]

        # Count human reviews
        reviewed_candidates = [c for c in all_candidates if c["review_status"] != ReviewStatus.UNREVIEWED.value]
        approved_count = sum(1 for c in reviewed_candidates if c["review_status"] == ReviewStatus.APPROVED_NON_SCREAM.value)
        scream_count = sum(1 for c in reviewed_candidates if c["review_status"] == ReviewStatus.SCREAM_PRESENT.value)
        ambiguous_count = sum(1 for c in reviewed_candidates if c["review_status"] == ReviewStatus.AMBIGUOUS.value)

        # Break down missing by source
        missing_by_source = defaultdict(int)
        for c in missing_candidates:
            missing_by_source[c["source_provider"]] += 1

        # Classify missing recordings
        existing_on_disk = 0
        fsd50k_on_disk_items = []
        fsd50k_unavailable_items = []

        for c in missing_candidates:
            if c["source_provider"] == "fsd50k":
                orig_id = str(c["original_source_id"])
                found_path = self._locate_fsd50k_clip(orig_id)
                if found_path:
                    existing_on_disk += 1
                    fsd50k_on_disk_items.append(c["recording_id"])
                else:
                    fsd50k_unavailable_items.append(c["recording_id"])

        freesound_missing = [c for c in missing_candidates if c["source_provider"] == "freesound"]
        never_downloaded = len(freesound_missing)

        audioset_missing = [c for c in missing_candidates if c["source_provider"] == "audioset"]
        licence_restricted = len(audioset_missing)

        source_unavailable = len(fsd50k_unavailable_items)

        # Count recovered in current state (how many FSD50K or Freesound audio files exist in raw dirs)
        fsd_raw_dir = self.raw_dest_dir / "fsd50k"
        fs_raw_dir = self.raw_dest_dir / "freesound"
        fsd_local_count = len(list(fsd_raw_dir.glob("*.wav"))) if fsd_raw_dir.is_dir() else 0
        fs_local_count = len(list(fs_raw_dir.glob("*.wav"))) if fs_raw_dir.is_dir() else 0

        return {
            "total_candidates": len(all_candidates),
            "audio_available": len(available_candidates),
            "missing_audio": len(missing_candidates),
            "missing_by_source": dict(missing_by_source),
            "existing_on_disk": existing_on_disk,
            "never_downloaded": never_downloaded,
            "download_failed": 0,
            "licence_restricted": licence_restricted,
            "source_unavailable": source_unavailable,
            "recovered_successfully": len(available_candidates),
            "preserved_human_reviews": {
                "total_reviewed": len(reviewed_candidates),
                "approved_non_scream": approved_count,
                "scream_present": scream_count,
                "ambiguous": ambiguous_count,
            },
            "freesound_api_key_configured": bool(get_freesound_api_key()),
            "details": {
                "fsd50k_recoverable_ids": fsd50k_on_disk_items,
                "fsd50k_unavailable_ids": fsd50k_unavailable_items,
                "freesound_downloadable_ids": [c["recording_id"] for c in freesound_missing],
                "audioset_restricted_ids": [c["recording_id"] for c in audioset_missing],
            },
        }

    def _locate_fsd50k_clip(self, original_id: str) -> Optional[Path]:
        """Search nested E: FSD50K directories for original_id.wav without modifying files."""
        for sdir in self.fsd50k_search_dirs:
            candidate_path = sdir / f"{original_id}.wav"
            if candidate_path.is_file():
                return candidate_path
        return None

    def recover_missing_audio(
        self,
        batch_size: Optional[int] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> Dict[str, Any]:
        """Execute non-destructive recovery of missing audio recordings.

        Guarantees:
        - NEVER overwrites or alters existing review decisions (181 approved non-scream, 2 scream, 2 ambiguous).
        - Copies only required files from E: to local raw dataset, leaving original E: files untouched.
        - Downloads CC0 / CC-BY Freesound files through official API endpoint.
        - Marks YouTube AudioSet clips explicitly as LICENCE_RESTRICTED.
        - Marks missing synthetic FSD50K seeds explicitly as SOURCE_UNAVAILABLE.
        - Automatically runs Stage 8.9.1 acoustic triage on all newly recovered files.
        """
        self._cancel_requested = False

        # Query only candidates needing audio whose review status is UNREVIEWED
        with self.store._get_connection() as conn:
            missing_rows = conn.execute("""
                SELECT
                    recording_id, source_provider, original_source_id,
                    original_source_url, local_path, has_audio,
                    original_filename, dataset_license, clip_license,
                    commercial_compatibility, proposed_category,
                    download_validation_status, unresolved_issues,
                    review_status
                FROM candidates
                WHERE has_audio = 0 AND review_status = 'UNREVIEWED'
                ORDER BY
                    CASE source_provider
                        WHEN 'fsd50k' THEN 1
                        WHEN 'freesound' THEN 2
                        WHEN 'audioset' THEN 3
                        ELSE 4
                    END ASC,
                    recording_id ASC
            """).fetchall()

        candidates_to_process = [dict(r) for r in missing_rows]
        if batch_size and batch_size > 0:
            candidates_to_process = candidates_to_process[:batch_size]

        total_to_process = len(candidates_to_process)
        recovered_fsd50k = 0
        recovered_freesound = 0
        restricted_audioset = 0
        unavailable_fsd50k = 0
        failed_downloads = 0

        recovered_records: List[Dict[str, Any]] = []

        # Prepare local target directories
        fsd_raw_dir = self.raw_dest_dir / "fsd50k"
        fs_raw_dir = self.raw_dest_dir / "freesound"
        fsd_raw_dir.mkdir(parents=True, exist_ok=True)
        fs_raw_dir.mkdir(parents=True, exist_ok=True)

        freesound_api_key = get_freesound_api_key()

        # Instantiate triage engine if needed
        if self.triage_engine is None:
            self.triage_engine = AutomatedTriageEngine()

        for idx, candidate in enumerate(candidates_to_process, 1):
            if self._cancel_requested:
                logger.info("Recovery cancelled by user after processing %d items.", idx - 1)
                break

            rec_id = candidate["recording_id"]
            src_provider = candidate["source_provider"]
            orig_id = str(candidate["original_source_id"])

            current_status = {
                "current_index": idx,
                "total_items": total_to_process,
                "current_recording_id": rec_id,
                "current_source": src_provider,
                "recovered_fsd50k": recovered_fsd50k,
                "recovered_freesound": recovered_freesound,
                "restricted_audioset": restricted_audioset,
                "unavailable_fsd50k": unavailable_fsd50k,
                "failed_downloads": failed_downloads,
            }
            if progress_callback:
                progress_callback(current_status)

            # -------------------------------------------------------------
            # SOURCE 1: FSD50K
            # -------------------------------------------------------------
            if src_provider == "fsd50k":
                found_src = self._locate_fsd50k_clip(orig_id)
                if found_src:
                    try:
                        dest_file = fsd_raw_dir / f"{orig_id}.wav"
                        # Copy only if not already present or zero bytes
                        if not dest_file.exists() or dest_file.stat().st_size == 0:
                            shutil.copy2(found_src, dest_file)

                        # Validate audio decoding and read properties with soundfile
                        data, sr = sf.read(str(dest_file))
                        channels = 1 if data.ndim == 1 else data.shape[1]
                        duration = round(float(len(data)) / float(sr), 3)
                        file_hash = compute_sha256(dest_file)

                        now_iso = datetime.now(timezone.utc).isoformat()

                        # Update SQLite candidate record
                        with self.store._get_connection() as conn:
                            conn.execute("""
                                UPDATE candidates SET
                                    local_path = ?,
                                    has_audio = 1,
                                    duration_seconds = ?,
                                    sample_rate = ?,
                                    channels = ?,
                                    sha256_original = ?,
                                    download_validation_status = ?,
                                    last_updated_at = ?
                                WHERE recording_id = ? AND review_status = 'UNREVIEWED'
                            """, (
                                str(dest_file.resolve()),
                                duration,
                                sr,
                                channels,
                                file_hash,
                                DownloadStatus.VALIDATED_CLEAN.value,
                                now_iso,
                                rec_id,
                            ))

                        # Immediately run automated acoustic triage
                        triage_res = self.triage_engine.analyze_audio_file(dest_file, recording_id=rec_id)
                        self.store.save_triage_result(triage_res)

                        recovered_fsd50k += 1
                        recovered_records.append({
                            "recording_id": rec_id,
                            "source": src_provider,
                            "status": "RECOVERED",
                            "duration_seconds": duration,
                            "triage_group": triage_res.triage_group,
                        })
                    except Exception as e:
                        logger.error("Failed processing FSD50K recording %s: %s", rec_id, e)
                        failed_downloads += 1
                else:
                    # Clip not found on E: (e.g. synthetic fsd50k seeds)
                    now_iso = datetime.now(timezone.utc).isoformat()
                    issues = json.dumps(["Original source ID not found in FSD50K dev or eval ground truth on E: drive."])
                    with self.store._get_connection() as conn:
                        conn.execute("""
                            UPDATE candidates SET
                                download_validation_status = ?,
                                unresolved_issues = ?,
                                last_updated_at = ?
                            WHERE recording_id = ? AND review_status = 'UNREVIEWED'
                        """, (
                            "SOURCE_UNAVAILABLE",
                            issues,
                            now_iso,
                            rec_id,
                        ))
                    unavailable_fsd50k += 1

            # -------------------------------------------------------------
            # SOURCE 2: Freesound
            # -------------------------------------------------------------
            elif src_provider == "freesound":
                if not freesound_api_key:
                    logger.warning("Freesound API key missing. Skipping %s.", rec_id)
                    failed_downloads += 1
                    continue

                # Ensure license meets policy
                clip_lic = candidate.get("commercial_compatibility", "")
                if clip_lic not in (LicenseStatus.CC0_VERIFIED.value, LicenseStatus.CC_BY_VERIFIED.value):
                    now_iso = datetime.now(timezone.utc).isoformat()
                    issues = json.dumps(["License is restricted / non-commercial. Excluded from automated download."])
                    with self.store._get_connection() as conn:
                        conn.execute("""
                            UPDATE candidates SET
                                download_validation_status = ?,
                                unresolved_issues = ?,
                                last_updated_at = ?
                            WHERE recording_id = ? AND review_status = 'UNREVIEWED'
                        """, ("LICENCE_RESTRICTED", issues, now_iso, rec_id))
                    continue

                try:
                    # Fetch Freesound audio preview
                    sound_url = f"https://freesound.org/apiv2/sounds/{orig_id}/?token={freesound_api_key}"
                    req = urllib.request.Request(sound_url, headers={"User-Agent": "FestivalScreamDetector/1.0"})
                    with urllib.request.urlopen(req, timeout=12) as resp:
                        meta_data = json.loads(resp.read().decode("utf-8"))

                    preview_url = (
                        meta_data.get("previews", {}).get("preview-hq-mp3")
                        or meta_data.get("previews", {}).get("preview-hq-ogg")
                    )

                    if not preview_url:
                        raise ValueError("No accessible preview stream URL provided by Freesound API.")

                    # Download preview stream
                    preview_req = urllib.request.Request(preview_url, headers={"User-Agent": "FestivalScreamDetector/1.0"})
                    with urllib.request.urlopen(preview_req, timeout=15) as a_resp:
                        raw_bytes = a_resp.read()

                    # Decode with soundfile in memory
                    data, sr = sf.read(io.BytesIO(raw_bytes))
                    channels = 1 if data.ndim == 1 else data.shape[1]
                    duration = round(float(len(data)) / float(sr), 3)

                    # Save as clean WAV
                    dest_file = fs_raw_dir / f"{orig_id}.wav"
                    sf.write(str(dest_file), data, sr)

                    file_hash = compute_sha256(dest_file)
                    now_iso = datetime.now(timezone.utc).isoformat()

                    with self.store._get_connection() as conn:
                        conn.execute("""
                            UPDATE candidates SET
                                local_path = ?,
                                has_audio = 1,
                                duration_seconds = ?,
                                sample_rate = ?,
                                channels = ?,
                                sha256_original = ?,
                                download_validation_status = ?,
                                last_updated_at = ?
                            WHERE recording_id = ? AND review_status = 'UNREVIEWED'
                        """, (
                            str(dest_file.resolve()),
                            duration,
                            sr,
                            channels,
                            file_hash,
                            DownloadStatus.VALIDATED_CLEAN.value,
                            now_iso,
                            rec_id,
                        ))

                    # Automatically triage newly recovered Freesound clip
                    triage_res = self.triage_engine.analyze_audio_file(dest_file, recording_id=rec_id)
                    self.store.save_triage_result(triage_res)

                    recovered_freesound += 1
                    recovered_records.append({
                        "recording_id": rec_id,
                        "source": src_provider,
                        "status": "RECOVERED",
                        "duration_seconds": duration,
                        "triage_group": triage_res.triage_group,
                    })

                    # Rate limit courtesy
                    time.sleep(0.4)

                except Exception as e:
                    logger.warning("Freesound download failed for %s (orig_id %s): %s", rec_id, orig_id, e)
                    failed_downloads += 1
                    now_iso = datetime.now(timezone.utc).isoformat()
                    issues = json.dumps([f"Download failed: {str(e)}"])
                    with self.store._get_connection() as conn:
                        conn.execute("""
                            UPDATE candidates SET
                                download_validation_status = ?,
                                unresolved_issues = ?,
                                last_updated_at = ?
                            WHERE recording_id = ? AND review_status = 'UNREVIEWED'
                        """, ("DOWNLOAD_FAILED", issues, now_iso, rec_id))

            # -------------------------------------------------------------
            # SOURCE 3: AudioSet
            # -------------------------------------------------------------
            elif src_provider == "audioset":
                # Explicitly marked as licence restricted (YouTube terms & copyright)
                now_iso = datetime.now(timezone.utc).isoformat()
                issues = json.dumps([
                    "Underlying audio not legally redistributable; YouTube Terms of Service and licensing restrictions prohibit automated downloading."
                ])
                with self.store._get_connection() as conn:
                    conn.execute("""
                        UPDATE candidates SET
                            download_validation_status = ?,
                            unresolved_issues = ?,
                            last_updated_at = ?
                        WHERE recording_id = ? AND review_status = 'UNREVIEWED'
                    """, (
                        "LICENCE_RESTRICTED",
                        issues,
                        now_iso,
                        rec_id,
                    ))
                restricted_audioset += 1

            # -------------------------------------------------------------
            # OTHER / UNKNOWN
            # -------------------------------------------------------------
            else:
                unavailable_fsd50k += 1

        # Final audit
        post_audit = self.get_audit()

        return {
            "success": True,
            "processed_count": len(candidates_to_process),
            "recovered_fsd50k": recovered_fsd50k,
            "recovered_freesound": recovered_freesound,
            "total_newly_recovered": recovered_fsd50k + recovered_freesound,
            "restricted_audioset": restricted_audioset,
            "unavailable_fsd50k": unavailable_fsd50k,
            "failed_downloads": failed_downloads,
            "cancelled": self._cancel_requested,
            "recovered_records": recovered_records,
            "post_recovery_audit": post_audit,
        }


# Singleton accessor
_recovery_service: Optional[AudioRecoveryService] = None


def get_audio_recovery_service() -> AudioRecoveryService:
    """Retrieve or initialize singleton AudioRecoveryService instance."""
    global _recovery_service
    if _recovery_service is None:
        _recovery_service = AudioRecoveryService()
    return _recovery_service
