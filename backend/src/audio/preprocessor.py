"""Audio Preprocessor Module.

Handles loading, channel conversion (mono), resampling to 16 kHz,
and normalization to float32 in [-1.0, 1.0] for YAMNet model ingestion.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import numpy as np
import scipy.signal
import soundfile as sf


@dataclass
class AudioMetadata:
    """Metadata describing the loaded audio file and its transformation."""
    file_path: str
    original_sample_rate: int
    target_sample_rate: int
    original_channels: int
    duration_seconds: float
    num_samples: int
    peak_amplitude: float
    rms_energy: float


def resample_audio(
    waveform: np.ndarray,
    orig_sr: int,
    target_sr: int = 16000,
) -> np.ndarray:
    """Resample 1D audio waveform to target sample rate using polyphase filtering.

    Args:
        waveform: 1D numpy array of audio samples.
        orig_sr: Original sampling rate in Hz.
        target_sr: Target sampling rate in Hz (default: 16000).

    Returns:
        Resampled 1D numpy array in float32.
    """
    if orig_sr == target_sr:
        return waveform.astype(np.float32)

    # Compute greatest common divisor to minimize filter orders
    gcd = math.gcd(orig_sr, target_sr)
    up = target_sr // gcd
    down = orig_sr // gcd

    resampled = scipy.signal.resample_poly(waveform, up, down).astype(np.float32)
    return resampled


def ensure_mono_float32(audio_data: np.ndarray) -> np.ndarray:
    """Convert audio data to 1D mono float32 normalized in [-1.0, 1.0].

    Args:
        audio_data: Numpy array of audio samples (1D or 2D).

    Returns:
        1D float32 numpy array.
    """
    # If 2D (channels, samples) or (samples, channels), average channels
    if audio_data.ndim > 1:
        # soundfile returns (samples, channels)
        if audio_data.shape[0] < audio_data.shape[1] and audio_data.shape[0] <= 8:
            # (channels, samples) orientation
            audio_data = np.mean(audio_data, axis=0)
        else:
            # (samples, channels) orientation
            audio_data = np.mean(audio_data, axis=1)

    # Normalize integer types if needed
    if np.issubdtype(audio_data.dtype, np.integer):
        max_val = np.iinfo(audio_data.dtype).max
        audio_data = audio_data.astype(np.float32) / float(max_val)
    else:
        audio_data = audio_data.astype(np.float32)

    # Clip to avoid numeric overflow beyond [-1.0, 1.0]
    np.clip(audio_data, -1.0, 1.0, out=audio_data)
    return audio_data


def load_audio(
    file_path: str | Path,
    target_sr: int = 16000,
) -> Tuple[np.ndarray, AudioMetadata]:
    """Load an audio file, convert to mono 16 kHz float32, and compute metadata.

    Args:
        file_path: Path to the audio file (WAV, FLAC, OGG, etc.).
        target_sr: Desired sampling rate in Hz (default: 16000).

    Returns:
        Tuple of (preprocessed_waveform, AudioMetadata).

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If audio cannot be read or is empty.
    """
    path = Path(file_path).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Audio file not found: {path}")

    # Read audio with soundfile
    data, orig_sr = sf.read(str(path), dtype="float32", always_2d=False)
    if data.size == 0:
        raise ValueError(f"Audio file is empty: {path}")

    orig_channels = 1 if data.ndim == 1 else data.shape[1]

    # Convert to mono float32
    mono_audio = ensure_mono_float32(data)

    # Resample to target sample rate (16 kHz for YAMNet)
    waveform = resample_audio(mono_audio, orig_sr, target_sr)

    # Compute descriptive metrics
    duration = float(len(waveform)) / float(target_sr)
    peak_amp = float(np.max(np.abs(waveform))) if len(waveform) > 0 else 0.0
    rms = float(np.sqrt(np.mean(waveform**2))) if len(waveform) > 0 else 0.0

    metadata = AudioMetadata(
        file_path=str(path),
        original_sample_rate=orig_sr,
        target_sample_rate=target_sr,
        original_channels=orig_channels,
        duration_seconds=round(duration, 3),
        num_samples=len(waveform),
        peak_amplitude=round(peak_amp, 4),
        rms_energy=round(rms, 4),
    )

    return waveform, metadata


def generate_synthetic_tone(
    freq_hz: float = 440.0,
    duration_seconds: float = 1.0,
    sr: int = 16000,
    amplitude: float = 0.5,
) -> np.ndarray:
    """Generate a pure sine tone for pipeline validation without external files.

    Args:
        freq_hz: Frequency in Hertz.
        duration_seconds: Duration in seconds.
        sr: Sample rate in Hz.
        amplitude: Peak amplitude in [0.0, 1.0].

    Returns:
        1D float32 numpy array.
    """
    t = np.linspace(0.0, duration_seconds, int(sr * duration_seconds), endpoint=False, dtype=np.float32)
    waveform = (amplitude * np.sin(2.0 * np.pi * freq_hz * t)).astype(np.float32)
    return waveform


def generate_synthetic_chirp(
    start_hz: float = 500.0,
    end_hz: float = 3000.0,
    duration_seconds: float = 1.0,
    sr: int = 16000,
    amplitude: float = 0.5,
) -> np.ndarray:
    """Generate a logarithmic frequency chirp simulating sudden high-pitch acoustic energy.

    Args:
        start_hz: Initial frequency in Hz.
        end_hz: Final frequency in Hz.
        duration_seconds: Duration in seconds.
        sr: Sample rate in Hz.
        amplitude: Peak amplitude.

    Returns:
        1D float32 numpy array.
    """
    t = np.linspace(0.0, duration_seconds, int(sr * duration_seconds), endpoint=False, dtype=np.float32)
    chirp = scipy.signal.chirp(t, f0=start_hz, t1=duration_seconds, f1=end_hz, method="logarithmic")
    waveform = (amplitude * chirp).astype(np.float32)
    return waveform
