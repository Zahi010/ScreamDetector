"""Stage 8.8 Data Types, Enums, and Manifest Schemas for Hard-Negative Acquisition.

Provides:
1. Standardized taxonomy matching Stage 8.7 gap analysis.
2. Verified licensing status constants and classifiers.
3. Review status lifecycle definitions.
4. AcquisitionCandidate dataclass and serialization helpers.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class LicenseStatus(str, Enum):
    """Allowed licensing statuses for candidate recordings."""
    CC0_VERIFIED = "CC0_VERIFIED"
    CC_BY_VERIFIED = "CC_BY_VERIFIED"
    NONCOMMERCIAL_ONLY = "NONCOMMERCIAL_ONLY"
    RESTRICTED = "RESTRICTED"
    UNKNOWN = "UNKNOWN"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"


class ReviewStatus(str, Enum):
    """Human review statuses."""
    UNREVIEWED = "UNREVIEWED"
    APPROVED_NON_SCREAM = "APPROVED_NON_SCREAM"
    SCREAM_PRESENT = "SCREAM_PRESENT"
    AMBIGUOUS = "AMBIGUOUS"
    EXCLUDED = "EXCLUDED"


class DownloadStatus(str, Enum):
    """Acquisition and download status."""
    DISCOVERED = "DISCOVERED"
    DOWNLOADED = "DOWNLOADED"
    SKIPPED_LICENSING = "SKIPPED_LICENSING"
    NOT_ACQUIRED = "NOT_ACQUIRED"
    FAILED_DOWNLOAD = "FAILED_DOWNLOAD"
    VALIDATED_CLEAN = "VALIDATED_CLEAN"
    FLAGGED_QUALITY = "FLAGGED_QUALITY"
    DUPLICATE_COLLISION = "DUPLICATE_COLLISION"


# Standardized Target Categories (Stage 8.7 Gaps)
TARGET_CATEGORIES: Dict[str, Dict[str, Any]] = {
    "whistles_and_squeaks": {
        "title": "Whistles and High-Pitched Squeaks",
        "description": "Slide whistles, referee whistles, rave whistles, squeaky toys, high-pitched transients",
        "priority": 1,
        "target_count": 30,
        "keywords": ["whistle", "referee whistle", "rave whistle", "slide whistle", "squeak", "squeaky toy"],
    },
    "crowd_cheering_applause": {
        "title": "Crowd Cheering, Chanting & Applause",
        "description": "Stadium applause, concert crowd cheering, group chants, excited festival crowd",
        "priority": 2,
        "target_count": 40,
        "keywords": ["cheering", "applause", "stadium cheering", "concert crowd", "crowd chanting", "excited crowd"],
    },
    "edm_and_synthesizers": {
        "title": "EDM, Synthesizer Risers & Bass Drops",
        "description": "Synthesizer pitch sweeps, risers, bass drops, electronic music elements",
        "priority": 3,
        "target_count": 35,
        "keywords": ["edm", "synthesizer riser", "synth sweep", "bass drop", "electronic music", "riser"],
    },
    "shouting_and_speech": {
        "title": "Shouting, Excited Speech & MC Vocals",
        "description": "Excited crowd speech, shouting, loud cheering vocalizations, amplified vocals",
        "priority": 4,
        "target_count": 25,
        "keywords": ["shout", "excited crowd", "amplified vocals", "yell", "cheer vocalization"],
    },
    "vuvuzelas_and_horns": {
        "title": "Vuvuzelas, Stadium Horns & Party Blowers",
        "description": "Stadium air horns, vuvuzelas, party horns, sustained harmonic noisemakers",
        "priority": 5,
        "target_count": 20,
        "keywords": ["vuvuzela", "stadium horn", "air horn", "party horn", "horn"],
    },
    "fireworks_pyrotechnics": {
        "title": "Fireworks, Screechers & Pyrotechnics",
        "description": "Aerial fireworks, whistling rockets, stage pyrotechnics, explosions",
        "priority": 6,
        "target_count": 20,
        "keywords": ["fireworks", "pyrotechnics", "rocket whistle", "firecracker"],
    },
    "wind_and_mic_noise": {
        "title": "Microphone Wind Noise & Handling",
        "description": "Wind rumble on microphone capsule, pops, cable handling, transducer noise",
        "priority": 7,
        "target_count": 20,
        "keywords": ["wind noise", "microphone handling", "mic wind", "cable pop"],
    },
    "infant_crying_archival": {
        "title": "Infant Crying & Tantrums (Ethical Archival)",
        "description": "Archival recordings of crying; strictly non-distress or consented public archives",
        "priority": 8,
        "target_count": 15,
        "keywords": ["infant crying", "baby cry"],
    },
    "sfx_sirens_ringing": {
        "title": "Sirens, Bells & Electronic Ringing",
        "description": "Alarm sirens, emergency vehicle sirens, electronic phone rings, bells",
        "priority": 9,
        "target_count": 15,
        "keywords": ["siren", "alarm", "electronic ringing", "bell", "buzzer"],
    },
}


def classify_license(raw_license: str, license_url: str = "") -> LicenseStatus:
    """Classify raw license string and URL into canonical LicenseStatus."""
    text = f"{raw_license} {license_url}".lower().strip()

    if not text:
        return LicenseStatus.UNKNOWN

    # Check for CC0 / Public Domain
    if any(k in text for k in ["cc0", "public domain", "zero 1.0", "zero", "creativecommons.org/publicdomain/zero"]):
        return LicenseStatus.CC0_VERIFIED

    # Check for Non-Commercial restrictions
    if any(k in text for k in ["nc", "non-commercial", "noncommercial", "by-nc", "by-nc-sa", "by-nc-nd"]):
        return LicenseStatus.NONCOMMERCIAL_ONLY

    # Check for Sampling+ which requires specific use analysis
    if "sampling+" in text or "sampling plus" in text:
        return LicenseStatus.REQUIRES_REVIEW

    # Check for CC BY variants (without NC)
    if any(k in text for k in ["cc-by", "cc by", "by 3.0", "by 4.0", "by 2.0", "by 2.5", "attribution", "/by/", "by/"]):
        return LicenseStatus.CC_BY_VERIFIED

    # Check for all rights reserved / proprietary
    if any(k in text for k in ["all rights reserved", "arr", "copyright", "proprietary"]):
        return LicenseStatus.RESTRICTED

    return LicenseStatus.REQUIRES_REVIEW


@dataclass
class AcquisitionCandidate:
    """Full provenance and metadata record for discovered and acquired audio."""
    recording_id: str
    source_provider: str  # fsd50k, freesound, audioset, esc50, etc.
    original_source_id: str
    original_source_url: str
    local_path: Optional[str] = None
    original_filename: str = ""
    sha256_original: str = ""
    sha256_derived: str = ""
    original_creator: str = ""
    original_title_description: str = ""
    dataset_license: str = ""
    clip_license: str = ""
    license_url_evidence: str = ""
    attribution_text: str = ""
    commercial_compatibility: str = LicenseStatus.UNKNOWN.value
    retrieval_timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    duration_seconds: float = 0.0
    sample_rate: int = 0
    channels: int = 0
    original_annotations: List[str] = field(default_factory=list)
    proposed_category: str = ""
    provisional_label: str = "non_scream"  # non_scream, scream, or ambiguous
    label_confidence_status: str = "unverified_source_label"
    review_status: str = ReviewStatus.UNREVIEWED.value
    duplicate_or_source_group: str = ""
    download_validation_status: str = DownloadStatus.DISCOVERED.value
    unresolved_issues: List[str] = field(default_factory=list)
    # Model evaluation fields
    model_score: Optional[float] = None
    model_alert: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary."""
        d = dataclasses.asdict(self)
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AcquisitionCandidate:
        """Construct record from dictionary."""
        # Sanitize list fields if stored as strings
        clean_data = dict(data)
        if isinstance(clean_data.get("original_annotations"), str):
            clean_data["original_annotations"] = [
                x.strip() for x in clean_data["original_annotations"].split(";") if x.strip()
            ]
        if isinstance(clean_data.get("unresolved_issues"), str):
            clean_data["unresolved_issues"] = [
                x.strip() for x in clean_data["unresolved_issues"].split(";") if x.strip()
            ]
        return cls(**{k: v for k, v in clean_data.items() if k in cls.__dataclass_fields__})
