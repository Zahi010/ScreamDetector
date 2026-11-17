"""Stage 8.9.30 Test Suite — Audio Quality Triage & Normalization Validation."""

import sys
from pathlib import Path
import numpy as np
import pytest
import soundfile as sf

STAGE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = STAGE_DIR.parents[1]
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(STAGE_DIR / "src"))

from audio_triage_engine import AudioTriageEngine


def test_audio_normalization_and_peak_scaling(tmp_path):
    """Verify triage engine normalizes arbitrary sample rate and channels to 16kHz mono float32."""
    engine = AudioTriageEngine(target_sr=16000)

    # Create synthetic 44.1kHz stereo test audio (2 seconds)
    sr_orig = 44100
    t = np.linspace(0, 2.0, int(sr_orig * 2.0), endpoint=False, dtype=np.float32)
    stereo_audio = np.stack([0.4 * np.sin(2 * np.pi * 1000 * t), 0.2 * np.sin(2 * np.pi * 2000 * t)], axis=1)

    raw_test_file = tmp_path / "raw_test.wav"
    sf.write(str(raw_test_file), stereo_audio, sr_orig)

    norm_data, record = engine.analyze_and_normalize(
        raw_test_file,
        candidate_meta={"candidate_id": "TEST_001", "commercial_eligible": True, "tags": ["scream"]},
        processed_dir=tmp_path / "processed",
    )

    assert norm_data is not None
    assert record.decoding_status == "VALID"
    assert record.orig_sr == 44100
    assert record.orig_channels == 2
    assert abs(record.duration_sec - 2.0) < 0.05
    assert len(norm_data) == int(16000 * 2.0)
    # Peak amplitude after normalization should be ~0.891 (-1.0 dBFS)
    peak_norm = float(np.max(np.abs(norm_data)))
    assert abs(peak_norm - 0.891) < 1e-3


def test_silent_audio_rejection(tmp_path):
    """Verify silent audio is classified as INVALID_AUDIO."""
    engine = AudioTriageEngine(target_sr=16000)

    silent_audio = np.zeros(16000, dtype=np.float32)
    raw_silent = tmp_path / "silent.wav"
    sf.write(str(raw_silent), silent_audio, 16000)

    norm_data, record = engine.analyze_and_normalize(
        raw_silent,
        candidate_meta={"candidate_id": "TEST_SILENT", "commercial_eligible": True},
        processed_dir=tmp_path / "processed",
    )

    assert norm_data is None
    assert record.triage_category == "INVALID_AUDIO"
