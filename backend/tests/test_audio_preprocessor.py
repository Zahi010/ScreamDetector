"""Unit tests for the audio preprocessor module."""

import numpy as np
import pytest

from src.audio.preprocessor import (
    ensure_mono_float32,
    generate_synthetic_chirp,
    generate_synthetic_tone,
    resample_audio,
)


def test_synthetic_tone_generation():
    """Verify generated tone has exact sample count, 1D shape, and correct amplitude range."""
    sr = 16000
    duration = 1.0
    waveform = generate_synthetic_tone(freq_hz=440.0, duration_seconds=duration, sr=sr, amplitude=0.5)

    assert waveform.ndim == 1
    assert len(waveform) == int(sr * duration)
    assert waveform.dtype == np.float32
    assert np.max(np.abs(waveform)) <= 0.5001


def test_synthetic_chirp_generation():
    """Verify generated chirp signal has valid duration, shape, and bounds."""
    sr = 16000
    duration = 0.5
    chirp = generate_synthetic_chirp(start_hz=300.0, end_hz=2000.0, duration_seconds=duration, sr=sr)

    assert chirp.ndim == 1
    assert len(chirp) == int(sr * duration)
    assert chirp.dtype == np.float32
    assert np.max(np.abs(chirp)) <= 1.0


def test_ensure_mono_float32_from_stereo():
    """Verify 2D stereo audio is properly averaged into 1D mono float32."""
    # 2 channels, 1000 samples
    stereo = np.ones((1000, 2), dtype=np.float32)
    stereo[:, 0] = 0.8
    stereo[:, 1] = 0.4

    mono = ensure_mono_float32(stereo)
    assert mono.ndim == 1
    assert len(mono) == 1000
    assert mono.dtype == np.float32
    assert np.allclose(mono, 0.6, atol=1e-5)


def test_ensure_mono_float32_int16_normalization():
    """Verify int16 audio data is converted and normalized to [-1.0, 1.0]."""
    raw_int16 = np.array([-32768, 0, 16384, 32767], dtype=np.int16)
    converted = ensure_mono_float32(raw_int16)

    assert converted.dtype == np.float32
    assert np.isclose(converted[0], -1.0, atol=1e-4)
    assert np.isclose(converted[1], 0.0, atol=1e-4)
    assert np.isclose(converted[2], 0.5, atol=1e-3)
    assert np.isclose(converted[3], 1.0, atol=1e-4)


def test_resample_audio():
    """Verify polyphase resampling accurately alters length according to sample rate ratio."""
    # 1 second of 48,000 Hz audio
    sr_orig = 48000
    sr_target = 16000
    audio_48k = generate_synthetic_tone(freq_hz=440.0, duration_seconds=1.0, sr=sr_orig)
    assert len(audio_48k) == 48000

    audio_16k = resample_audio(audio_48k, orig_sr=sr_orig, target_sr=sr_target)
    assert len(audio_16k) == 16000
    assert audio_16k.dtype == np.float32
