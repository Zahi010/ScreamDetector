"""Audio Quality Control, Deduplication, and Normalization Module (Stage 8.8).

Performs:
1. Integrity checks: unreadable audio, zero-length, sample rate, channels, NaN/inf.
2. Signal checks: digital clipping (>= 0.999), near-silence (RMS < 0.0001), duration bounds.
3. Content-based duplicate detection (file SHA-256 and PCM SHA-256) and collision auditing against existing datasets.
4. Standardization to mono 16 kHz float32 in `processed/` without modifying raw files.
"""

from __future__ import annotations

import csv
import hashlib
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np
import soundfile as sf

from src.audio.preprocessor import load_audio
from src.config import (
    MANIFESTS_DIR,
    STAGE8_8_DATASET_DIR,
    STAGE8_8_PROCESSED_DIR,
    STAGE8_8_REPORTS_DIR,
    TARGET_SAMPLE_RATE,
)
from src.dataset.acquisition_types import (
    AcquisitionCandidate,
    DownloadStatus,
    ReviewStatus,
)

logger = logging.getLogger("acquisition_validator")


@dataclass
class QualityCheckResult:
    """Detailed quality validation outcome for a single audio file."""
    recording_id: str
    is_valid: bool
    status: str
    duration_seconds: float
    sample_rate: int
    channels: int
    rms_energy: float
    peak_amplitude: float
    clipping_detected: bool
    silence_detected: bool
    has_nan_or_inf: bool
    file_sha256: str
    pcm_sha256: str
    is_exact_duplicate: bool
    duplicate_of: Optional[str]
    is_historical_collision: bool
    derived_path: Optional[str]
    derived_sha256: Optional[str]
    rejection_reasons: List[str]


def compute_file_sha256(filepath: Path) -> str:
    """Compute SHA-256 hash of a file on disk."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def compute_pcm_sha256(waveform: np.ndarray) -> str:
    """Compute deterministic SHA-256 of int16-quantized PCM waveform data."""
    int16_samples = np.clip(waveform * 32767.0, -32768, 32767).astype(np.int16)
    return hashlib.sha256(int16_samples.tobytes()).hexdigest()


def load_historical_dataset_hashes(manifests_dir: Optional[Path] = None) -> Set[str]:
    """Collect all known SHA-256 hashes from existing Stage 3/4/6 datasets to prevent leakage."""
    m_dir = manifests_dir or MANIFESTS_DIR
    hashes: Set[str] = set()

    # 1. Stage 3 dataset_manifest.json
    ds_manifest = m_dir / "dataset_manifest.json"
    if ds_manifest.exists():
        try:
            with open(ds_manifest, "r", encoding="utf-8") as f:
                data = json.load(f)
                records = data if isinstance(data, list) else data.get("recordings", [])
                for rec in records:
                    h = rec.get("file_sha256") or rec.get("sha256_hash") or rec.get("sha256")
                    if h:
                        hashes.add(h.lower())
        except Exception as e:
            logger.warning(f"Could not load hashes from {ds_manifest}: {e}")

    # 2. Stage 6 hard_negatives_manifest.json
    hn_manifest = m_dir / "hard_negatives_manifest.json"
    if hn_manifest.exists():
        try:
            with open(hn_manifest, "r", encoding="utf-8") as f:
                data = json.load(f)
                records = data if isinstance(data, list) else data.get("recordings", [])
                for rec in records:
                    h = rec.get("file_sha256") or rec.get("source_sha256") or rec.get("sha256")
                    if h:
                        hashes.add(h.lower())
        except Exception as e:
            logger.warning(f"Could not load hashes from {hn_manifest}: {e}")

    return hashes


class AudioQualityValidator:
    """Audits audio quality and performs deduplication and derivative generation."""

    def __init__(
        self,
        processed_dir: Optional[Path] = None,
        min_duration_sec: float = 0.3,
        max_duration_sec: float = 60.0,
        silence_rms_threshold: float = 0.0001,
        clipping_threshold: float = 0.999,
    ):
        self.processed_dir = processed_dir or STAGE8_8_PROCESSED_DIR
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.min_duration_sec = min_duration_sec
        self.max_duration_sec = max_duration_sec
        self.silence_rms_threshold = silence_rms_threshold
        self.clipping_threshold = clipping_threshold

        self.historical_hashes = load_historical_dataset_hashes()
        self.seen_file_hashes: Dict[str, str] = {}  # sha256 -> recording_id
        self.seen_pcm_hashes: Dict[str, str] = {}   # pcm_sha256 -> recording_id

    def validate_and_process(
        self,
        candidate: AcquisitionCandidate,
    ) -> QualityCheckResult:
        """Validate audio file quality, detect duplicates, and generate 16kHz mono derivative."""
        rejection_reasons: List[str] = []

        # If audio was not acquired (e.g. AudioSet metadata-only)
        if candidate.download_validation_status == DownloadStatus.NOT_ACQUIRED.value or not candidate.local_path:
            return QualityCheckResult(
                recording_id=candidate.recording_id,
                is_valid=False,
                status=DownloadStatus.NOT_ACQUIRED.value,
                duration_seconds=0.0,
                sample_rate=0,
                channels=0,
                rms_energy=0.0,
                peak_amplitude=0.0,
                clipping_detected=False,
                silence_detected=False,
                has_nan_or_inf=False,
                file_sha256="",
                pcm_sha256="",
                is_exact_duplicate=False,
                duplicate_of=None,
                is_historical_collision=False,
                derived_path=None,
                derived_sha256=None,
                rejection_reasons=["Audio was not acquired (metadata-only candidate)."],
            )

        audio_path = Path(candidate.local_path)
        if not audio_path.exists():
            return QualityCheckResult(
                recording_id=candidate.recording_id,
                is_valid=False,
                status=DownloadStatus.FAILED_DOWNLOAD.value,
                duration_seconds=0.0,
                sample_rate=0,
                channels=0,
                rms_energy=0.0,
                peak_amplitude=0.0,
                clipping_detected=False,
                silence_detected=False,
                has_nan_or_inf=False,
                file_sha256="",
                pcm_sha256="",
                is_exact_duplicate=False,
                duplicate_of=None,
                is_historical_collision=False,
                derived_path=None,
                derived_sha256=None,
                rejection_reasons=[f"File does not exist on disk: {audio_path}"],
            )

        # 1. File SHA-256 and duplicate checks
        file_sha = compute_file_sha256(audio_path)
        candidate.sha256_original = file_sha

        is_exact_dup = False
        duplicate_of: Optional[str] = None
        if file_sha in self.seen_file_hashes:
            is_exact_dup = True
            duplicate_of = self.seen_file_hashes[file_sha]
            rejection_reasons.append(f"Exact file hash duplicate of candidate {duplicate_of}.")
        else:
            self.seen_file_hashes[file_sha] = candidate.recording_id

        # Historical dataset collision check
        is_historical = file_sha.lower() in self.historical_hashes
        if is_historical:
            rejection_reasons.append("Historical dataset collision: file hash exists in Stage 4/5/6 splits.")

        # 2. Audio reading and signal checks
        try:
            waveform, sr = sf.read(str(audio_path), dtype="float32")
        except Exception as e:
            return QualityCheckResult(
                recording_id=candidate.recording_id,
                is_valid=False,
                status=DownloadStatus.FLAGGED_QUALITY.value,
                duration_seconds=0.0,
                sample_rate=0,
                channels=0,
                rms_energy=0.0,
                peak_amplitude=0.0,
                clipping_detected=False,
                silence_detected=False,
                has_nan_or_inf=False,
                file_sha256=file_sha,
                pcm_sha256="",
                is_exact_duplicate=is_exact_dup,
                duplicate_of=duplicate_of,
                is_historical_collision=is_historical,
                derived_path=None,
                derived_sha256=None,
                rejection_reasons=[f"Unreadable or corrupted audio file: {e}"],
            )

        channels = 1 if waveform.ndim == 1 else waveform.shape[1]
        num_frames = len(waveform) if waveform.ndim == 1 else waveform.shape[0]

        if num_frames == 0 or sr <= 0:
            return QualityCheckResult(
                recording_id=candidate.recording_id,
                is_valid=False,
                status=DownloadStatus.FLAGGED_QUALITY.value,
                duration_seconds=0.0,
                sample_rate=sr,
                channels=channels,
                rms_energy=0.0,
                peak_amplitude=0.0,
                clipping_detected=False,
                silence_detected=True,
                has_nan_or_inf=False,
                file_sha256=file_sha,
                pcm_sha256="",
                is_exact_duplicate=is_exact_dup,
                duplicate_of=duplicate_of,
                is_historical_collision=is_historical,
                derived_path=None,
                derived_sha256=None,
                rejection_reasons=["Zero-duration or invalid sample rate."],
            )

        duration_sec = num_frames / float(sr)

        # Check for NaN / Inf
        has_nan_inf = bool(np.isnan(waveform).any() or np.isinf(waveform).any())
        if has_nan_inf:
            rejection_reasons.append("Audio contains NaN or Infinite sample values.")

        # Flatten / convert to mono for metrics
        if waveform.ndim > 1:
            mono_waveform = np.mean(waveform, axis=1)
        else:
            mono_waveform = waveform

        peak_amp = float(np.max(np.abs(mono_waveform))) if len(mono_waveform) > 0 else 0.0
        rms = float(np.sqrt(np.mean(mono_waveform ** 2))) if len(mono_waveform) > 0 else 0.0

        clipping = peak_amp >= self.clipping_threshold
        if clipping:
            rejection_reasons.append(f"Digital clipping detected (peak amplitude {peak_amp:.4f} >= {self.clipping_threshold}).")

        silence = rms < self.silence_rms_threshold
        if silence:
            rejection_reasons.append(f"Near-silence detected (RMS energy {rms:.6f} < {self.silence_rms_threshold}).")

        if duration_sec < self.min_duration_sec:
            rejection_reasons.append(f"Duration too short ({duration_sec:.2f}s < {self.min_duration_sec}s).")
        elif duration_sec > self.max_duration_sec:
            rejection_reasons.append(f"Duration exceeds maximum allowed ({duration_sec:.2f}s > {self.max_duration_sec}s).")

        # PCM hash check
        pcm_sha = compute_pcm_sha256(mono_waveform)
        if pcm_sha in self.seen_pcm_hashes and not is_exact_dup:
            duplicate_of = self.seen_pcm_hashes[pcm_sha]
            rejection_reasons.append(f"Identical acoustic PCM data to candidate {duplicate_of}.")
        else:
            self.seen_pcm_hashes[pcm_sha] = candidate.recording_id

        # 3. Generate standardized 16kHz mono derivative
        derived_path_str: Optional[str] = None
        derived_sha: Optional[str] = None
        is_clean = len(rejection_reasons) == 0

        try:
            # Use project's canonical preprocessor load_audio
            proc_waveform, proc_meta = load_audio(audio_path, target_sr=TARGET_SAMPLE_RATE)
            derived_file = self.processed_dir / f"{candidate.recording_id}_16k_mono.wav"
            sf.write(str(derived_file), proc_waveform, TARGET_SAMPLE_RATE)
            derived_path_str = str(derived_file)
            derived_sha = compute_file_sha256(derived_file)
            candidate.sha256_derived = derived_sha
        except Exception as e:
            rejection_reasons.append(f"Failed to generate standardized 16kHz derivative: {e}")
            is_clean = False

        status = DownloadStatus.VALIDATED_CLEAN.value if is_clean else DownloadStatus.FLAGGED_QUALITY.value
        candidate.download_validation_status = status
        candidate.duration_seconds = duration_sec
        candidate.sample_rate = sr
        candidate.channels = channels
        if duplicate_of:
            candidate.duplicate_or_source_group = f"duplicate_of_{duplicate_of}"
        if rejection_reasons:
            candidate.unresolved_issues.extend(rejection_reasons)

        return QualityCheckResult(
            recording_id=candidate.recording_id,
            is_valid=is_clean,
            status=status,
            duration_seconds=duration_sec,
            sample_rate=sr,
            channels=channels,
            rms_energy=rms,
            peak_amplitude=peak_amp,
            clipping_detected=clipping,
            silence_detected=silence,
            has_nan_or_inf=has_nan_inf,
            file_sha256=file_sha,
            pcm_sha256=pcm_sha,
            is_exact_duplicate=is_exact_dup,
            duplicate_of=duplicate_of,
            is_historical_collision=is_historical,
            derived_path=derived_path_str,
            derived_sha256=derived_sha,
            rejection_reasons=rejection_reasons,
        )
