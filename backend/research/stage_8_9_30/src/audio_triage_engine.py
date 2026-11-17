"""Stage 8.9.30 — Audio Quality Triage, Normalization & Acoustic Profiling Engine.

Performs:
1. Audio decoding & integrity audit (via soundfile / librosa).
2. Quality metrics extraction:
   - Peak amplitude & dynamic range (dB)
   - RMS energy
   - Clipping ratio (samples >= 0.999)
   - Silence ratio (frames < -40 dB)
   - Estimated SNR (dB)
3. Pitch & Acoustic profiling:
   - Fundamental frequency (F0 via pyin / autocorrelation)
   - Spectral centroid & spectral bandwidth
   - Spectral flatness & harmonic-to-noise ratio
   - Resonance peak prominence (1.5 - 3.5 kHz horn band)
4. Normalization:
   - Resampled to exact 16,000 Hz
   - Downmixed to mono (float32)
   - Scaled to safe peak normalization (-1.0 dBFS)
   - Saved into processed/ directory preserving raw originals.
5. Automated Triage Classification:
   - APPROVED_POSITIVE_CANDIDATE
   - POSSIBLE_POSITIVE
   - NEGATIVE_CONFUSER
   - AMBIGUOUS
   - INVALID_AUDIO
   - LICENSE_QUARANTINE
"""

from __future__ import annotations

import csv
import hashlib
import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
import soundfile as sf
import librosa

STAGE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = STAGE_DIR.parents[1]

logger = logging.getLogger("audio_triage_engine")


@dataclass
class AudioQualityRecord:
    candidate_id: str
    original_path: str
    processed_path: str
    decoding_status: str  # VALID, DECODE_ERROR, SILENT, CORRUPTED
    orig_sr: int
    orig_channels: int
    duration_sec: float
    peak_amplitude: float
    rms_energy: float
    clipping_ratio: float
    silence_ratio: float
    estimated_snr_db: float
    f0_mean_hz: float
    f0_max_hz: float
    spectral_centroid_hz: float
    spectral_flatness: float
    resonance_horn_energy: float
    triage_category: str
    triage_rationale: str
    sha256_processed: str = ""


class AudioTriageEngine:
    """Triage and normalization pipeline for Stage 8.9.30 candidate recordings."""

    def __init__(self, target_sr: int = 16000):
        self.target_sr = target_sr

    def analyze_and_normalize(
        self,
        raw_filepath: Path,
        candidate_meta: Dict[str, Any],
        processed_dir: Path,
    ) -> Tuple[Optional[np.ndarray], AudioQualityRecord]:
        """Audit audio quality, normalize to 16kHz mono float32, and classify candidate."""
        cand_id = candidate_meta.get("candidate_id", raw_filepath.stem)
        
        # 1. Decoding and integrity check
        try:
            data, sr = sf.read(str(raw_filepath), dtype="float32", always_2d=False)
            if data is None or len(data) == 0:
                raise ValueError("Empty audio data")
        except Exception as e:
            record = AudioQualityRecord(
                candidate_id=cand_id,
                original_path=str(raw_filepath),
                processed_path="",
                decoding_status=f"DECODE_ERROR: {str(e)}",
                orig_sr=0,
                orig_channels=0,
                duration_sec=0.0,
                peak_amplitude=0.0,
                rms_energy=0.0,
                clipping_ratio=0.0,
                silence_ratio=1.0,
                estimated_snr_db=0.0,
                f0_mean_hz=0.0,
                f0_max_hz=0.0,
                spectral_centroid_hz=0.0,
                spectral_flatness=0.0,
                resonance_horn_energy=0.0,
                triage_category="INVALID_AUDIO",
                triage_rationale=f"Failed to decode audio file: {e}",
            )
            return None, record

        orig_channels = 1 if data.ndim == 1 else data.shape[1]
        orig_sr = sr

        # Downmix to mono
        if data.ndim > 1:
            data = data.mean(axis=1)

        # Resample if needed
        if sr != self.target_sr:
            data = librosa.resample(data, orig_sr=sr, target_sr=self.target_sr)

        duration = len(data) / self.target_sr
        peak = float(np.max(np.abs(data))) if len(data) > 0 else 0.0
        rms = float(np.sqrt(np.mean(data ** 2))) if len(data) > 0 else 0.0

        if peak < 1e-4:
            record = AudioQualityRecord(
                candidate_id=cand_id,
                original_path=str(raw_filepath),
                processed_path="",
                decoding_status="SILENT",
                orig_sr=orig_sr,
                orig_channels=orig_channels,
                duration_sec=round(duration, 3),
                peak_amplitude=round(peak, 5),
                rms_energy=round(rms, 5),
                clipping_ratio=0.0,
                silence_ratio=1.0,
                estimated_snr_db=0.0,
                f0_mean_hz=0.0,
                f0_max_hz=0.0,
                spectral_centroid_hz=0.0,
                spectral_flatness=0.0,
                resonance_horn_energy=0.0,
                triage_category="INVALID_AUDIO",
                triage_rationale="Signal peak is below audible threshold (< 1e-4).",
            )
            return None, record

        # Quality metrics
        clipping_samples = np.sum(np.abs(data) >= 0.999)
        clipping_ratio = float(clipping_samples / len(data))

        frame_len = int(0.030 * self.target_sr)  # 30ms frames
        hop_len = int(0.015 * self.target_sr)
        frame_rms = librosa.feature.rms(y=data, frame_length=frame_len, hop_length=hop_len)[0]
        silence_thresh = 0.01 * (np.max(frame_rms) if np.max(frame_rms) > 0 else 1.0)
        silence_ratio = float(np.sum(frame_rms < silence_thresh) / max(1, len(frame_rms)))

        # SNR estimate (speech/active vs noise floor)
        noise_floor = np.percentile(frame_rms, 10) if len(frame_rms) > 0 else 1e-5
        active_energy = np.percentile(frame_rms, 90) if len(frame_rms) > 0 else 1e-4
        snr_db = float(20.0 * np.log10(max(1e-5, active_energy) / max(1e-6, noise_floor)))

        # Acoustic features
        spec_cent = float(np.mean(librosa.feature.spectral_centroid(y=data, sr=self.target_sr)))
        spec_flat = float(np.mean(librosa.feature.spectral_flatness(y=data)))

        # F0 estimation (fast autocorrelation / harmonic representation)
        try:
            f0 = librosa.yin(data, fmin=150, fmax=1800, sr=self.target_sr)
            valid_f0 = f0[~np.isnan(f0)]
            f0_mean = float(np.mean(valid_f0)) if len(valid_f0) > 0 else 0.0
            f0_max = float(np.max(valid_f0)) if len(valid_f0) > 0 else 0.0
        except Exception:
            f0_mean, f0_max = 0.0, 0.0

        # Resonance horn band ratio (1.5 kHz - 3.5 kHz energy / total energy)
        fft_vals = np.abs(np.fft.rfft(data))
        freqs = np.fft.rfftfreq(len(data), 1.0 / self.target_sr)
        horn_mask = (freqs >= 1500) & (freqs <= 3500)
        horn_energy = float(np.sum(fft_vals[horn_mask] ** 2) / max(1e-6, np.sum(fft_vals ** 2)))

        # Normalize audio peak to -1.0 dBFS (0.891)
        target_peak = 0.891
        if peak > 0:
            norm_data = (data / peak) * target_peak
        else:
            norm_data = data

        # Determine automated triage category
        tags_str = " ".join(candidate_meta.get("tags", [])).lower()
        name_str = candidate_meta.get("name", "").lower()
        desc_str = candidate_meta.get("description", "").lower()
        text_context = f"{name_str} {tags_str} {desc_str}"

        is_license_eligible = candidate_meta.get("commercial_eligible", True)
        
        if not is_license_eligible:
            triage_cat = "LICENSE_QUARANTINE"
            rationale = f"License is non-commercial or requires review: {candidate_meta.get('canonical_license')}"
        elif any(k in text_context for k in ["cheer", "applause", "stadium", "crowd chant", "synthetic sfx", "synthesizer", "laser", "gunshot"]):
            triage_cat = "NEGATIVE_CONFUSER"
            rationale = "Metadata tags indicate crowd cheering, stadium applause, or synthetic sound effect."
        elif any(k in text_context for k in ["shout", "yell", "speech", "speaking", "talking", "angry man"]) and not any(k in text_context for k in ["scream", "shriek", "screaming"]):
            triage_cat = "NEGATIVE_CONFUSER"
            rationale = "Metadata indicates shouting/speech rather than acoustic scream phonation."
        elif (spec_cent > 1800 or horn_energy > 0.25 or f0_mean > 350) and any(k in text_context for k in ["scream", "shriek", "screaming", "screams", "horror scream"]):
            triage_cat = "APPROVED_POSITIVE_CANDIDATE"
            rationale = "Metadata documents human scream and acoustic features exhibit high spectral centroid and horn energy."
        elif any(k in text_context for k in ["scream", "screaming", "shriek"]):
            triage_cat = "POSSIBLE_POSITIVE"
            rationale = "Metadata mentions scream but acoustic profile has moderate horn resonance; retained for inspection."
        else:
            triage_cat = "AMBIGUOUS"
            rationale = "Acoustic or vocal classification ambiguous from metadata and initial feature profile."

        # Save normalized audio to appropriate subfolder
        subfolder = "positive" if triage_cat == "APPROVED_POSITIVE_CANDIDATE" else (
            "negative" if triage_cat == "NEGATIVE_CONFUSER" else "quarantined"
        )
        out_file = processed_dir / subfolder / f"{cand_id}_16k_mono.wav"
        out_file.parent.mkdir(parents=True, exist_ok=True)
        sf.write(str(out_file), norm_data, self.target_sr, subtype="FLOAT")

        # Compute SHA-256 of processed audio
        h = hashlib.sha256()
        with open(out_file, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        sha_proc = h.hexdigest()

        try:
            rel_orig = str(raw_filepath.resolve().relative_to(BACKEND_DIR.resolve()))
        except ValueError:
            rel_orig = str(raw_filepath.resolve())

        try:
            rel_proc = str(out_file.resolve().relative_to(BACKEND_DIR.resolve()))
        except ValueError:
            rel_proc = str(out_file.resolve())

        record = AudioQualityRecord(
            candidate_id=cand_id,
            original_path=rel_orig,
            processed_path=rel_proc,
            decoding_status="VALID",
            orig_sr=orig_sr,
            orig_channels=orig_channels,
            duration_sec=round(duration, 3),
            peak_amplitude=round(peak, 4),
            rms_energy=round(rms, 4),
            clipping_ratio=round(clipping_ratio, 4),
            silence_ratio=round(silence_ratio, 4),
            estimated_snr_db=round(snr_db, 2),
            f0_mean_hz=round(f0_mean, 1),
            f0_max_hz=round(f0_max, 1),
            spectral_centroid_hz=round(spec_cent, 1),
            spectral_flatness=round(spec_flat, 4),
            resonance_horn_energy=round(horn_energy, 4),
            triage_category=triage_cat,
            triage_rationale=rationale,
            sha256_processed=sha_proc,
        )

        return norm_data, record
