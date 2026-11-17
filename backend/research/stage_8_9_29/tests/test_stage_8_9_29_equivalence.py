"""Stage 8.9.29 Test Suite — Regression & Numerical Equivalence Validation."""

import json
import sys
from pathlib import Path
import numpy as np
import pytest

STAGE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = STAGE_DIR.parents[1]
# STAGE_DIR set above
sys.path.insert(0, str(STAGE_DIR))

from streaming_manager import MultiStreamInferenceManager


def test_ring_buffer_zero_drift_equivalence():
    """Verify single-stream ring buffer matches direct window slicing with 0.0 numerical drift."""
    mgr = MultiStreamInferenceManager(backend="tensorflow")

    # Generate synthetic 2-second audio
    sr = 16000
    t = np.linspace(0, 2.0, 32000, endpoint=False, dtype=np.float32)
    audio = 0.3 * np.sin(2 * np.pi * 2200.0 * t) + 0.1 * np.random.randn(32000).astype(np.float32)

    # Direct reference window
    win_ref = audio[:15600]
    mgr.register_stream("s_direct")
    res_direct = mgr.process_window("s_direct", 0, 0.0, 0.975, win_ref)

    # Ring buffer window
    mgr.register_stream("s_ring")
    res_ring = mgr.ingest_chunk("s_ring", audio)

    # First extracted window must match direct reference identically
    assert len(res_ring) > 0
    delta = abs(res_direct.final_score - res_ring[0].final_score)
    assert delta < 1e-6, f"Numerical drift detected: {delta}"
    assert res_direct.classification == res_ring[0].classification


def test_multi_stream_zero_cross_talk():
    """Verify concurrent streaming introduces 0 cross-talk score contamination."""
    mgr = MultiStreamInferenceManager(backend="tensorflow")
    mgr.register_stream("s_clean")
    mgr.register_stream("s_interfere")

    clean_tone = 0.2 * np.sin(2 * np.pi * 1000.0 * np.linspace(0, 2.0, 32000, endpoint=False, dtype=np.float32))
    noise = np.random.randn(32000).astype(np.float32) * 0.5

    # Run clean tone in isolation
    mgr.reset_stream("s_clean")
    res_iso = mgr.ingest_chunk("s_clean", clean_tone)

    # Run clean tone with heavy concurrent noise on sibling stream
    mgr.reset_stream("s_clean")
    mgr.reset_stream("s_interfere")
    _ = mgr.ingest_chunk("s_interfere", noise)
    res_concurrent = mgr.ingest_chunk("s_clean", clean_tone)

    assert len(res_iso) == len(res_concurrent)
    for w_iso, w_cnc in zip(res_iso, res_concurrent):
        delta = abs(w_iso.final_score - w_cnc.final_score)
        assert delta < 1e-6, f"Cross-talk interference detected: {delta}"
        assert w_iso.classification == w_cnc.classification
