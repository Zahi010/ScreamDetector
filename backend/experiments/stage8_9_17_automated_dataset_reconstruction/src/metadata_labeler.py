"""Automated Metadata-Driven Labeling and Quality Validation Pipeline (Stage 8.9.17).

Transforms disparate audio dataset metadata (FSD50K ground truth, NIGENS, OpenSLR99,
and existing Stage 8.9 records) into standardized project categories with zero manual intervention.

Rules:
1. Ground-truth dataset metadata is the primary label; YAMNet is secondary.
2. Ambiguous recordings are assigned AMBIGUOUS_AUTO_LABEL and quarantined.
3. Commercial eligibility is enforced (CC0 and CC BY eligible; CC BY-NC quarantined).
4. Audio validation verifies duration >= 0.5s, no NaN/inf, valid RMS/peak.
5. Duplicates detected via audio content hash.
"""

from __future__ import annotations

import csv
import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np
import soundfile as sf

logger = logging.getLogger("metadata_labeler")

TARGET_SAMPLE_RATE = 16000

# Canonical Project Categories
CATEGORY_MAPPINGS = {
    # Positives
    "SCREAM_STANDARD": {"binary_label": "scream", "is_scream": True, "description": "Human distress scream (adult/general)"},
    "SHORT_SCREAM": {"binary_label": "scream", "is_scream": True, "description": "Short duration scream (<1.2s)"},
    "SUSTAINED_SCREAM": {"binary_label": "scream", "is_scream": True, "description": "Extended duration scream (>=1.2s)"},
    "DISTANT_MASKED_SCREAM": {"binary_label": "scream", "is_scream": True, "description": "Reverberant or crowd-masked distant scream"},

    # Negatives - Vocal Confusers
    "INFANT_CRYING": {"binary_label": "non_scream", "is_scream": False, "description": "Infant and baby crying / wailing (high F0 500-750 Hz)"},
    "CHILD_ADULT_CRYING": {"binary_label": "non_scream", "is_scream": False, "description": "Child and adult crying and sobbing"},
    "SHOUTING_EXCITED_SPEECH": {"binary_label": "non_scream", "is_scream": False, "description": "Vocal shouting, yelling, sports shouting, excited speech"},
    "CHILD_SPEECH": {"binary_label": "non_scream", "is_scream": False, "description": "Child speech and toddler vocalizations"},
    "SPEECH_NORMAL": {"binary_label": "non_scream", "is_scream": False, "description": "Conversational speech, whispering, narration"},
    "LAUGHTER": {"binary_label": "non_scream", "is_scream": False, "description": "Laughter, giggling, chuckling"},
    "CROWD_CHEERING": {"binary_label": "non_scream", "is_scream": False, "description": "Festival and stadium crowd cheering, chanting, applause"},
    "MUSIC_SINGING": {"binary_label": "non_scream", "is_scream": False, "description": "Singing, vocals, instruments, festival music"},

    # Negatives - Acoustic Confusers & Ambience
    "SILENCE_DIGITAL": {"binary_label": "non_scream", "is_scream": False, "description": "Exact digital zeros (RMS 0.0)"},
    "SILENCE_NEAR_ZERO": {"binary_label": "non_scream", "is_scream": False, "description": "Low-level background noise (-100 dBFS to -52 dBFS)"},
    "AMBIENT_ROOM": {"binary_label": "non_scream", "is_scream": False, "description": "Indoor room tone, subtle HVAC, quiet room acoustics"},
    "AMBIENT_OUTDOOR": {"binary_label": "non_scream", "is_scream": False, "description": "Environmental wind, traffic, rain, nature ambience"},
    "WHISTLE": {"binary_label": "non_scream", "is_scream": False, "description": "Referee, security, and human whistling"},
    "SIREN_ALARM": {"binary_label": "non_scream", "is_scream": False, "description": "Emergency vehicle sirens and acoustic alarms"},
    "ANIMAL_VOCALIZATION": {"binary_label": "non_scream", "is_scream": False, "description": "Dog barking, bird chirping, animal sounds"},
    "MECHANICAL_NOISE": {"binary_label": "non_scream", "is_scream": False, "description": "Engines, tools, impacts, electrical noise"},

    # Ambiguous
    "AMBIGUOUS_AUTO_LABEL": {"binary_label": "ambiguous", "is_scream": False, "description": "Ambiguous or conflicting metadata"},
}


def compute_audio_hash(waveform: np.ndarray) -> str:
    """Compute MD5 hash of quantized 16-bit PCM representation for duplicate detection."""
    # Scale to int16 range
    clipped = np.clip(waveform, -1.0, 1.0)
    int16_bytes = (clipped * 32767).astype(np.int16).tobytes()
    return hashlib.md5(int16_bytes).hexdigest()


def compute_file_hash(file_path: Path) -> str:
    """Compute fast SHA-256/MD5 chunk hash of audio file for duplicate detection."""
    h = hashlib.md5()
    with open(file_path, "rb") as f:
        # Hash header and first 64KB
        chunk = f.read(65536)
        h.update(chunk)
        # Also include file size
        h.update(str(file_path.stat().st_size).encode())
    return h.hexdigest()


def validate_audio_metadata(
    file_path: Path, min_duration: float = 0.5
) -> Dict[str, Any]:
    """Fast inspection of audio file header without full PCM memory decode."""
    report = {
        "valid": False,
        "error": None,
        "duration_seconds": 0.0,
        "sample_rate": 0,
        "channels": 0,
        "file_size": 0,
        "content_hash": "",
    }
    if not file_path.exists():
        report["error"] = "File does not exist"
        return report

    try:
        info = sf.info(str(file_path))
        report["sample_rate"] = info.samplerate
        report["channels"] = info.channels
        report["duration_seconds"] = round(info.duration, 4)
        report["file_size"] = file_path.stat().st_size

        if info.duration < min_duration:
            report["error"] = f"Duration {info.duration:.2f}s < minimum {min_duration:.2f}s"
            return report

        report["content_hash"] = compute_file_hash(file_path)
        report["valid"] = True
        return report
    except Exception as e:
        report["error"] = f"Audio header error: {str(e)}"
        return report


def validate_and_load_audio(
    file_path: Path, target_sr: int = TARGET_SAMPLE_RATE, min_duration: float = 0.5
) -> Tuple[Optional[np.ndarray], Dict[str, Any]]:
    """Inspect and load audio file with rigorous quality and corruption checks.

    Returns:
        (waveform, quality_report)
    """
    report = {
        "valid": False,
        "error": None,
        "duration_seconds": 0.0,
        "sample_rate": 0,
        "channels": 0,
        "audio_rms": 0.0,
        "audio_peak": 0.0,
        "is_clipping": False,
        "content_hash": "",
    }

    if not file_path.exists():
        report["error"] = "File does not exist"
        return None, report

    try:
        info = sf.info(str(file_path))
        report["sample_rate"] = info.samplerate
        report["channels"] = info.channels
        report["duration_seconds"] = round(info.duration, 4)

        if info.duration < min_duration:
            report["error"] = f"Duration {info.duration:.2f}s < minimum {min_duration:.2f}s"
            return None, report

        data, sr = sf.read(str(file_path), dtype="float32", always_2d=True)

        # Convert to mono
        if data.shape[1] > 1:
            mono = np.mean(data, axis=1)
        else:
            mono = data[:, 0]

        # Resample if needed
        if sr != target_sr:
            # Linear interpolation resampling for fast deterministic validation
            num_target_samples = int(round(len(mono) * (target_sr / sr)))
            mono = np.interp(
                np.linspace(0.0, 1.0, num_target_samples, endpoint=False),
                np.linspace(0.0, 1.0, len(mono), endpoint=False),
                mono,
            ).astype(np.float32)

        # Check for NaN / Inf
        if np.isnan(mono).any() or np.isinf(mono).any():
            report["error"] = "Waveform contains NaN or Inf values"
            return None, report

        rms = float(np.sqrt(np.mean(mono ** 2) + 1e-12))
        peak = float(np.max(np.abs(mono))) if len(mono) > 0 else 0.0

        report["audio_rms"] = round(rms, 6)
        report["audio_peak"] = round(peak, 4)
        report["is_clipping"] = peak >= 0.999
        report["content_hash"] = compute_audio_hash(mono)
        report["valid"] = True
        return mono, report

    except Exception as e:
        report["error"] = f"Audio decode error: {str(e)}"
        return None, report


class MetadataLabeler:
    """Maps dataset metadata to canonical categories with automated ambiguity rejection."""

    @staticmethod
    def map_fsd50k_labels(labels: List[str], duration: float, clip_info: Dict[str, Any]) -> str:
        """Map FSD50K multi-labels and duration to canonical project category."""
        labels_lower = [l.strip().lower() for l in labels]
        title_tags = (clip_info.get("title", "") + " " + " ".join(clip_info.get("tags", []))).lower()

        # 1. Scream check
        if any("scream" in l for l in labels_lower):
            if duration < 1.2:
                return "SHORT_SCREAM"
            elif duration >= 3.0:
                return "SUSTAINED_SCREAM"
            else:
                return "SCREAM_STANDARD"

        # 2. Infant / Baby Crying
        if any("crying" in l or "sobbing" in l for l in labels_lower):
            if any(k in title_tags for k in ["baby", "infant", "toddler", "newborn"]):
                return "INFANT_CRYING"
            else:
                return "CHILD_ADULT_CRYING"

        # 3. Shouting & Yelling
        if any(l in ["shout", "yell"] for l in labels_lower):
            return "SHOUTING_EXCITED_SPEECH"

        # 4. Child Speech
        if any("child_speech" in l for l in labels_lower):
            return "CHILD_SPEECH"

        # 5. Crowd & Cheering
        if any(l in ["cheering", "crowd", "applause"] for l in labels_lower):
            return "CROWD_CHEERING"

        # 6. Laughter
        if any("laughter" in l for l in labels_lower):
            return "LAUGHTER"

        # 7. Normal Speech / Whispering
        if any(l in ["speech", "whispering", "female_speech_and_woman_speaking", "male_speech_and_man_speaking"] for l in labels_lower):
            return "SPEECH_NORMAL"

        # 8. Music & Singing
        if any("singing" in l or "music" in l for l in labels_lower):
            return "MUSIC_SINGING"

        # 9. Sirens & Alarms
        if any(l in ["siren", "alarm"] for l in labels_lower):
            return "SIREN_ALARM"

        # 10. Ambient Outdoor & Wind
        if any(l in ["wind", "traffic_noise_and_roadway_noise", "water", "rain", "thunderstorm"] for l in labels_lower):
            return "AMBIENT_OUTDOOR"

        # 11. Animals
        if any("animal" in l or "bark" in l for l in labels_lower):
            return "ANIMAL_VOCALIZATION"

        return "AMBIGUOUS_AUTO_LABEL"

    @staticmethod
    def map_license_status(license_str: str) -> Tuple[str, bool]:
        """Determine commercial eligibility from license URL or string."""
        lic = license_str.lower()
        if "zero" in lic or "cc0" in lic or "publicdomain" in lic:
            return "COMMERCIALLY_ELIGIBLE", True
        elif "by/3.0" in lic or "by/4.0" in lic or "by/2.0" in lic or "cc-by" in lic or "cc by" in lic:
            return "COMMERCIALLY_ELIGIBLE", True
        elif "by-nc" in lic or "noncommercial" in lic or "nc" in lic:
            return "QUARANTINED_NC", False
        elif "sampling" in lic:
            return "QUARANTINED_SAMPLING_PLUS", False
        else:
            return "UNKNOWN_LICENSE", False
