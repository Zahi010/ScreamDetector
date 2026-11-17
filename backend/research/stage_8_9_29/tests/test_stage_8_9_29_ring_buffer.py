"""Stage 8.9.29 Test Suite — Audio Ring Buffer Implementation & Boundary Tests."""

import sys
from pathlib import Path
import numpy as np
import pytest

STAGE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = STAGE_DIR.parents[1]
# STAGE_DIR set above
sys.path.insert(0, str(STAGE_DIR))

from ring_buffer_implementation import AudioRingBuffer


def test_ring_buffer_exact_sample_fidelity():
    """Verify extracted windows match offline reference slicing with 0.0 error."""
    sr = 16000
    win_len = 15600
    hop_len = 4000
    dur = 4.0
    total_samples = int(sr * dur)

    t = np.linspace(0, dur, total_samples, endpoint=False, dtype=np.float32)
    signal = 0.5 * np.sin(2 * np.pi * 1500 * t) + 0.2 * np.sin(2 * np.pi * 3200 * t)

    # Reference windows
    ref_windows = []
    idx = 0
    for start in range(0, total_samples - win_len + 1, hop_len):
        ref_windows.append(signal[start : start + win_len].copy())
        idx += 1

    rb = AudioRingBuffer(sample_rate=sr, window_sec=0.975, hop_sec=0.250, capacity_sec=2.5)

    # Ingest in irregular chunk sizes
    extracted = []
    rng = np.random.RandomState(42)
    pos = 0
    while pos < total_samples:
        sz = rng.randint(100, 3000)
        chunk = signal[pos : pos + sz]
        extracted.extend(rb.ingest(chunk))
        pos += sz

    assert len(extracted) == len(ref_windows), f"Window count mismatch: {len(extracted)} vs {len(ref_windows)}"

    for i, (w_ref, (_, s_act, e_act, w_act)) in enumerate(zip(ref_windows, extracted)):
        max_diff = float(np.max(np.abs(w_ref - w_act)))
        assert max_diff == 0.0, f"Sample discrepancy in window {i}: {max_diff}"
        assert abs(s_act - (i * 0.25)) < 1e-6
        assert abs(e_act - (i * 0.25 + 0.975)) < 1e-6


def test_ring_buffer_chunk_sizes_invariance():
    """Verify diverse chunk sizes (160, 320, 800, 1600, 4000, 4096) produce identical windows."""
    sr = 16000
    dur = 3.0
    total_samples = int(sr * dur)
    t = np.linspace(0, dur, total_samples, endpoint=False, dtype=np.float32)
    signal = np.sin(2 * np.pi * 2000 * t).astype(np.float32)

    chunk_sizes = [160, 320, 800, 1600, 4000, 4096]
    baseline_windows = None

    for sz in chunk_sizes:
        rb = AudioRingBuffer(sample_rate=sr, window_sec=0.975, hop_sec=0.250, capacity_sec=4.0)
        windows = []
        for p in range(0, total_samples, sz):
            windows.extend(rb.ingest(signal[p : p + sz]))

        win_arrays = [w[3] for w in windows]
        if baseline_windows is None:
            baseline_windows = win_arrays
        else:
            assert len(win_arrays) == len(baseline_windows)
            for wb, wa in zip(baseline_windows, win_arrays):
                assert np.array_equal(wb, wa)


def test_ring_buffer_reset():
    """Verify ring buffer resets cleanly to initial state."""
    rb = AudioRingBuffer(sample_rate=16000, capacity_sec=2.0)
    _ = rb.ingest(np.ones(16000, dtype=np.float32))
    assert rb.total_samples_ingested == 16000

    rb.reset()
    assert rb.total_samples_ingested == 0
    assert rb.window_counter == 0
    assert rb._available == 0
    assert np.all(rb._storage == 0.0)


def test_ring_buffer_bounded_memory():
    """Verify ring buffer storage memory is strictly bounded and does not reallocate."""
    rb = AudioRingBuffer(sample_rate=16000, capacity_sec=4.0)
    initial_bytes = rb._storage.nbytes
    assert initial_bytes == 16000 * 4 * 4  # 4 seconds * 16000 * 4 bytes = 256,000 bytes

    # Stream 100,000 samples through
    chunk = np.random.randn(4000).astype(np.float32)
    for _ in range(25):
        _ = rb.ingest(chunk)

    assert rb._storage.nbytes == initial_bytes
