"""Stage 8.9.29 Test Suite — Stream Isolation & Deterministic Scenarios."""

import sys
from pathlib import Path
import numpy as np
import pytest

STAGE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = STAGE_DIR.parents[1]
# STAGE_DIR set above
sys.path.insert(0, str(STAGE_DIR))

from streaming_manager import MultiStreamInferenceManager
from src.verify_stream_isolation import load_file_pcm


@pytest.fixture(scope="module")
def stream_mgr():
    return MultiStreamInferenceManager(backend="tensorflow")


def test_scenario_1_short_scream_vs_silence(stream_mgr):
    """Scenario 1: Stream A receives short scream; Stream B receives silence."""
    stream_mgr.reset_stream("test_s1_a")
    stream_mgr.reset_stream("test_s1_b")
    stream_mgr.register_stream("test_s1_a")
    stream_mgr.register_stream("test_s1_b")

    short_scream = load_file_pcm("backend/experiments/stage8_9_20_acoustic_discriminability/data/supplementary_short_screams/supp_short_scream_002_v3_fsd50k_182924.wav", max_sec=2.0)
    if len(short_scream) < 24000:
        pad = np.zeros(24000, dtype=np.float32)
        pad[:len(short_scream)] = short_scream
        short_scream = pad
    silence = np.zeros(len(short_scream), dtype=np.float32)

    _ = stream_mgr.ingest_chunk("test_s1_a", short_scream)
    _ = stream_mgr.ingest_chunk("test_s1_b", silence)

    assert len(stream_mgr.streams["test_s1_a"].emitted_alerts) >= 1
    assert len(stream_mgr.streams["test_s1_b"].emitted_alerts) == 0


def test_scenario_2_shout_vs_scream(stream_mgr):
    """Scenario 2: Stream A receives shouting; Stream B receives sustained scream."""
    stream_mgr.reset_stream("test_s2_a")
    stream_mgr.reset_stream("test_s2_b")
    stream_mgr.register_stream("test_s2_a")
    stream_mgr.register_stream("test_s2_b")

    shout = load_file_pcm("backend/experiments/v2_hard_negative_training/audio/shouting_and_speech/v2_fsd50k_254334.wav", max_sec=2.0)
    scream = load_file_pcm("backend/experiments/v2_hard_negative_training/audio/scream/v3_fsd50k_173070.wav", max_sec=6.0)

    _ = stream_mgr.ingest_chunk("test_s2_a", shout)
    _ = stream_mgr.ingest_chunk("test_s2_b", scream)

    assert len(stream_mgr.streams["test_s2_a"].emitted_alerts) == 0
    assert len(stream_mgr.streams["test_s2_b"].emitted_alerts) >= 1


def test_scenario_7_disconnect_independence(stream_mgr):
    """Scenario 7: Stream A disconnects while Stream B continues uninterrupted."""
    stream_mgr.reset_stream("test_s7_a")
    stream_mgr.reset_stream("test_s7_b")
    stream_mgr.register_stream("test_s7_a")
    stream_mgr.register_stream("test_s7_b")

    scream = load_file_pcm("backend/experiments/v2_hard_negative_training/audio/scream/v3_fsd50k_173070.wav", max_sec=4.0)

    _ = stream_mgr.ingest_chunk("test_s7_a", scream[:16000])
    stream_mgr.unregister_stream("test_s7_a")
    assert "test_s7_a" not in stream_mgr.streams

    _ = stream_mgr.ingest_chunk("test_s7_b", scream)
    assert len(stream_mgr.streams["test_s7_b"].emitted_alerts) >= 1
