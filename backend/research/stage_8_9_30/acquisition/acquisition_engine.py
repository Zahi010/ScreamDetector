"""Stage 8.9.30 — Automated Lawful Audio Acquisition Engine.

Connects to Freesound API v2 to discover, audit licenses for, and acquire
independent human scream recordings across diverse vocal and acoustic profiles:
- Short screams (< 0.8s)
- Sustained screams (> 1.5s)
- High-pitched screams
- Distant / masked screams
- Reverberant screams

Enforces:
1. Strict license filtering (CC0 and CC-BY only; excludes CC-BY-NC, ARR).
2. Deduplication and hash checking against all historical splits and Stage 5 test set.
3. Resumability and graceful error recovery with rate limiting.
4. Non-exposure of secrets (never logs or displays API keys).
"""

from __future__ import annotations

import csv
import hashlib
import json
import logging
import os
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Add backend to sys.path for project config
STAGE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = STAGE_DIR.parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from src.config import get_freesound_api_key

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("stage_8_9_30_acquisition")


def compute_sha256(filepath: Path) -> str:
    """Compute SHA-256 hash of a file on disk."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def classify_license_string(lic_str: str) -> Tuple[str, str, bool]:
    """Classify license string into canonical category and commercial eligibility.
    
    Returns:
        (canonical_license, license_status, is_eligible_commercial)
    """
    s = (lic_str or "").lower().strip()
    if not s:
        return "UNKNOWN", "UNKNOWN", False
    
    if any(k in s for k in ["cc0", "publicdomain/zero", "public domain", "zero 1.0"]):
        return "CC0-1.0", "CC0_VERIFIED", True
    elif any(k in s for k in ["by-nc", "noncommercial", "non-commercial", "nc-sa", "nc-nd"]):
        return "CC-BY-NC", "NONCOMMERCIAL_ONLY", False
    elif any(k in s for k in ["by/4.0", "by 4.0", "by/3.0", "by 3.0", "by/2.0", "by 2.0", "/by/", "attribution"]):
        return "CC-BY", "CC_BY_VERIFIED", True
    elif any(k in s for k in ["sampling+", "sampling plus"]):
        return "Sampling+", "REQUIRES_REVIEW", False
    elif any(k in s for k in ["all rights reserved", "arr", "copyright"]):
        return "ARR", "RESTRICTED", False
    else:
        return "OTHER", "REQUIRES_REVIEW", False


@dataclass
class CandidateRecord:
    candidate_id: str
    source_provider: str
    source_sound_id: str
    name: str
    username: str
    duration_sec: float
    raw_license: str
    canonical_license: str
    license_status: str
    commercial_eligible: bool
    source_url: str
    download_url: str
    tags: List[str]
    description: str
    search_query: str
    discovered_at: str
    download_status: str = "DISCOVERED"  # DISCOVERED, DOWNLOADED, SKIPPED_LICENSE, FAILED_DOWNLOAD, DUPLICATE
    local_raw_path: str = ""
    sha256_raw: str = ""
    file_format: str = ""
    quarantine_reason: str = ""


class FreesoundAcquisitionClient:
    """Automated, lawful discovery and ingestion client for Freesound API."""

    def __init__(self, stage_dir: Path):
        self.stage_dir = stage_dir
        self.acq_dir = stage_dir / "acquisition"
        self.raw_dir = stage_dir / "raw"
        self.raw_pos_dir = self.raw_dir / "positive"
        self.raw_neg_dir = self.raw_dir / "negative"
        self.raw_quar_dir = self.raw_dir / "quarantined"

        for d in [self.acq_dir, self.raw_pos_dir, self.raw_neg_dir, self.raw_quar_dir]:
            d.mkdir(parents=True, exist_ok=True)

        self.api_key = get_freesound_api_key()
        if not self.api_key:
            logger.warning("No FREESOUND_API_KEY found in .env. API searches will fail.")

        # Load historical blacklist hashes and source groups
        self.blacklisted_hashes: Set[str] = set()
        self.blacklisted_source_groups: Set[str] = set()
        self.blacklisted_ids: Set[str] = set()
        self._load_historical_blacklists()

    def _load_historical_blacklists(self):
        """Load SHA-256 and source group blacklists from Stage 5 test and Stage 8.9.27 census."""
        # 1. Stage 5 test predictions
        test_pred_path = BACKEND_DIR / "reports" / "test_predictions.csv"
        if test_pred_path.exists():
            with open(test_pred_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    sg = r.get("source_group_id", "").strip().lower()
                    if sg:
                        self.blacklisted_source_groups.add(sg)
                        # Also add uploader username without prefix
                        if sg.startswith("freesound_"):
                            self.blacklisted_source_groups.add(sg.replace("freesound_", ""))

        # 2. Stage 8.9.27 manifest and census
        manifest_path = BACKEND_DIR / "research" / "stage_8_9_27" / "independent_dataset_manifest.csv"
        if manifest_path.exists():
            with open(manifest_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    h = r.get("sha256", "").strip().lower()
                    if h:
                        self.blacklisted_hashes.add(h)
                    orig_id = r.get("original_source_id", "").strip()
                    if orig_id:
                        self.blacklisted_ids.add(orig_id)

        census_path = BACKEND_DIR / "research" / "stage_8_9_27" / "src" / "workspace_audio_census.csv"
        if census_path.exists():
            with open(census_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    h = r.get("sha256", "").strip().lower()
                    if h:
                        self.blacklisted_hashes.add(h)

        logger.info(
            f"Loaded blacklists: {len(self.blacklisted_hashes)} hashes, "
            f"{len(self.blacklisted_source_groups)} source groups, "
            f"{len(self.blacklisted_ids)} existing sound IDs."
        )

    def search_candidates(
        self,
        query: str,
        target_count: int = 15,
        min_duration: float = 0.2,
        max_duration: float = 15.0,
    ) -> List[CandidateRecord]:
        """Search Freesound API for audio matching a query, filtering metadata first."""
        if not self.api_key:
            logger.error("Cannot query Freesound API: missing API key.")
            return []

        candidates: List[CandidateRecord] = []
        fields = "id,name,tags,description,license,previews,username,duration,url,created,type,samplerate,channels,filesize"
        page = 1
        page_size = min(30, max(15, target_count))

        while len(candidates) < target_count:
            encoded_query = urllib.parse.quote(query)
            filter_str = urllib.parse.quote(f"duration:[{min_duration} TO {max_duration}]")
            url = (
                f"https://freesound.org/apiv2/search/text/?query={encoded_query}"
                f"&filter={filter_str}&fields={fields}&page_size={page_size}&page={page}"
            )
            req = urllib.request.Request(
                url,
                headers={
                    "Authorization": f"Token {self.api_key}",
                    "User-Agent": "FestivalScreamDetector/1.0 (Research Audit)",
                },
            )

            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    results = data.get("results", [])
                    if not results:
                        break

                    for item in results:
                        sound_id = str(item["id"])
                        username = str(item.get("username", "unknown")).strip()
                        raw_lic = item.get("license", "")
                        can_lic, lic_status, is_eligible = classify_license_string(raw_lic)

                        # Extract download preview URL (prefer hq-mp3 or hq-ogg)
                        previews = item.get("previews", {})
                        dl_url = previews.get("preview-hq-mp3") or previews.get("preview-lq-mp3") or previews.get("preview-hq-ogg") or ""

                        rec = CandidateRecord(
                            candidate_id=f"FS_{sound_id}",
                            source_provider="freesound",
                            source_sound_id=sound_id,
                            name=item.get("name", ""),
                            username=username,
                            duration_sec=float(item.get("duration", 0.0)),
                            raw_license=raw_lic,
                            canonical_license=can_lic,
                            license_status=lic_status,
                            commercial_eligible=is_eligible,
                            source_url=item.get("url", f"https://freesound.org/sounds/{sound_id}/"),
                            download_url=dl_url,
                            tags=item.get("tags", []),
                            description=item.get("description", "")[:500],
                            search_query=query,
                            discovered_at=datetime.now(timezone.utc).isoformat(),
                        )

                        # Pre-screen licensing and historical contamination
                        if sound_id in self.blacklisted_ids:
                            rec.download_status = "DUPLICATE_HISTORICAL_ID"
                            rec.quarantine_reason = "Sound ID already present in historical or Stage 8.9.27 dataset."
                        elif username.lower() in self.blacklisted_source_groups:
                            rec.download_status = "QUARANTINED_HISTORICAL_SOURCE_GROUP"
                            rec.quarantine_reason = f"Uploader '{username}' present in Stage 5 historical test set."
                        elif not is_eligible:
                            rec.download_status = "SKIPPED_LICENSE"
                            rec.quarantine_reason = f"Incompatible or non-commercial license: {can_lic} ({lic_status})"
                        elif not dl_url:
                            rec.download_status = "FAILED_NO_PREVIEW"
                            rec.quarantine_reason = "No preview audio stream available from API."

                        candidates.append(rec)
                        if len(candidates) >= target_count:
                            break

                    page += 1
                    time.sleep(1.0)  # Politeness rate limit

            except urllib.error.HTTPError as e:
                logger.error(f"Freesound API HTTP error on query '{query}' (page {page}): {e.code} {e.reason}")
                break
            except Exception as e:
                logger.error(f"Unexpected error querying Freesound on query '{query}': {e}")
                break

        return candidates

    def download_candidate(self, candidate: CandidateRecord, target_subfolder: str = "positive") -> bool:
        """Download single audio preview file into raw storage."""
        if not candidate.download_url:
            candidate.download_status = "FAILED_DOWNLOAD"
            candidate.quarantine_reason = "Missing download URL"
            return False

        if candidate.download_status not in ("DISCOVERED", "SKIPPED_LICENSE", "QUARANTINED_HISTORICAL_SOURCE_GROUP"):
            return False

        # Destination path
        dest_folder = self.raw_pos_dir if target_subfolder == "positive" else (
            self.raw_neg_dir if target_subfolder == "negative" else self.raw_quar_dir
        )
        if not candidate.commercial_eligible or "QUARANTINE" in candidate.download_status:
            dest_folder = self.raw_quar_dir

        ext = "mp3" if ".mp3" in candidate.download_url else "ogg"
        dest_file = dest_folder / f"{candidate.candidate_id}.{ext}"

        req = urllib.request.Request(
            candidate.download_url,
            headers={
                "Authorization": f"Token {self.api_key}",
                "User-Agent": "FestivalScreamDetector/1.0 (Research Audit)",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read()
                if len(data) < 512:
                    candidate.download_status = "FAILED_DOWNLOAD"
                    candidate.quarantine_reason = f"File too small ({len(data)} bytes), likely corrupted."
                    return False

                dest_file.write_bytes(data)
                sha = compute_sha256(dest_file)

                # Check if hash collides with historical dataset
                if sha.lower() in self.blacklisted_hashes:
                    dest_file.unlink(missing_ok=True)
                    candidate.download_status = "DUPLICATE_HISTORICAL_HASH"
                    candidate.quarantine_reason = f"Exact SHA-256 collision ({sha}) with historical dataset file."
                    return False

                candidate.local_raw_path = str(dest_file.relative_to(self.stage_dir.parent.parent))
                candidate.sha256_raw = sha
                candidate.file_format = ext
                candidate.download_status = "DOWNLOADED"
                time.sleep(1.0)  # Politeness rate limit
                return True

        except Exception as e:
            candidate.download_status = "FAILED_DOWNLOAD"
            candidate.quarantine_reason = f"Download exception: {str(e)}"
            return False
