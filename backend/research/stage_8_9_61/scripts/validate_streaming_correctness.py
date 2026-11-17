#!/usr/bin/env python3
"""
STAGE 8.9.61 — Streaming & Boundary Correctness Validation Script
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
Verifies all 15 streaming, boundary, and memory invariants.
"""

import os
import sys
import time
import numpy as np
import scipy.signal as signal
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
STAGE57_DIR = REPO_ROOT / "backend" / "research" / "stage_8_9_57"
STAGE61_DIR = REPO_ROOT / "backend" / "research" / "stage_8_9_61"

sys.path.insert(0, str(STAGE57_DIR / "dsp_implementations"))
from c5_combined import extract_subband_vector_c5, extract_phonation_stats_c5

class StreamingRollingWindowBuffer:
    """
    Fixed-capacity ring buffer for 16,000 samples (1.0s at 16 kHz)
    with 8,000-sample (500 ms) hop advancement.
    """
    def __init__(self, capacity: int = 16000, hop_size: int = 8000):
        self.capacity = capacity
        self.hop_size = hop_size
        self.buffer = np.zeros(self.capacity, dtype=np.float32)
        self.total_samples_ingested = 0
        self.windows_emitted = 0
        self.last_timestamp = 0.0
        
    def reset(self):
        self.buffer.fill(0.0)
        self.total_samples_ingested = 0
        self.windows_emitted = 0
        self.last_timestamp = 0.0
        
    def push_chunk(self, chunk: np.ndarray) -> np.ndarray:
        """Pushes an 8,000-sample chunk, rolls the buffer, and returns the 16,000-sample window."""
        c = np.ascontiguousarray(chunk, dtype=np.float32)
        if len(c) < self.hop_size:
            padded = np.zeros(self.hop_size, dtype=np.float32)
            padded[:len(c)] = c
            c = padded
            
        # Shift buffer left by hop_size
        self.buffer[:-self.hop_size] = self.buffer[self.hop_size:]
        self.buffer[-self.hop_size:] = c[:self.hop_size]
        
        self.total_samples_ingested += len(c)
        self.windows_emitted += 1
        self.last_timestamp = (self.windows_emitted - 1) * (self.hop_size / 16000.0)
        
        return self.buffer.copy()

def main():
    print("=" * 80)
    print("STAGE 8.9.61: STREAMING & BOUNDARY CORRECTNESS VALIDATION")
    print("=" * 80)
    
    buf = StreamingRollingWindowBuffer()
    test_results = {}
    
    # Scenario 1: Consecutive 500 ms hops
    buf.reset()
    chunks = [np.full(8000, i + 1, dtype=np.float32) for i in range(5)]
    for c in chunks:
        buf.push_chunk(c)
    assert buf.windows_emitted == 5
    test_results["scenario_1_consecutive_hops"] = "PASS"
    print("[PASS] Scenario 1: Consecutive 500 ms hops")
    
    # Scenario 2: Overlapping audio windows
    buf.reset()
    c1 = np.ones(8000, dtype=np.float32)
    c2 = np.full(8000, 2.0, dtype=np.float32)
    w1 = buf.push_chunk(c1)
    w2 = buf.push_chunk(c2)
    assert np.array_equal(w2[:8000], c1) and np.array_equal(w2[8000:], c2)
    test_results["scenario_2_overlapping_windows"] = "PASS"
    print("[PASS] Scenario 2: Overlapping audio windows (50% overlap verified)")
    
    # Scenario 3: Recording start
    buf.reset()
    w_start = buf.push_chunk(c1)
    assert np.all(w_start[:8000] == 0.0) and np.all(w_start[8000:] == 1.0)
    test_results["scenario_3_recording_start"] = "PASS"
    print("[PASS] Scenario 3: Recording start (zero-padding on initial frame)")
    
    # Scenario 4 & 5: Recording end & partial final window
    short_chunk = np.full(3000, 5.0, dtype=np.float32)
    w_end = buf.push_chunk(short_chunk)
    assert len(w_end) == 16000
    assert np.all(w_end[8000:11000] == 5.0) and np.all(w_end[11000:] == 0.0)
    test_results["scenario_4_recording_end"] = "PASS"
    test_results["scenario_5_partial_final_window"] = "PASS"
    print("[PASS] Scenario 4 & 5: Recording end and partial final window padding")
    
    # Scenario 6: Silence followed by positive audio
    buf.reset()
    w_silence = buf.push_chunk(np.zeros(8000, dtype=np.float32))
    sine_pos = np.sin(2 * np.pi * 1000 * np.arange(8000) / 16000.0).astype(np.float32)
    w_pos = buf.push_chunk(sine_pos)
    sb_pos = extract_subband_vector_c5(w_pos)
    assert np.isfinite(sb_pos).all()
    test_results["scenario_6_silence_then_pos"] = "PASS"
    print("[PASS] Scenario 6: Silence followed by positive audio")
    
    # Scenario 7: Positive audio followed by silence
    w_post_silence = buf.push_chunk(np.zeros(8000, dtype=np.float32))
    assert np.array_equal(w_post_silence[:8000], sine_pos)
    assert np.all(w_post_silence[8000:] == 0.0)
    test_results["scenario_7_pos_then_silence"] = "PASS"
    print("[PASS] Scenario 7: Positive audio followed by silence (tail decay verified)")
    
    # Scenario 8: Abrupt amplitude changes
    buf.reset()
    c_quiet = np.full(8000, 1e-4, dtype=np.float32)
    c_loud = np.full(8000, 0.95, dtype=np.float32)
    w_abrupt = buf.push_chunk(c_quiet)
    w_abrupt2 = buf.push_chunk(c_loud)
    sb_abrupt = extract_subband_vector_c5(w_abrupt2)
    assert not np.isnan(sb_abrupt).any()
    test_results["scenario_8_abrupt_amplitude"] = "PASS"
    print("[PASS] Scenario 8: Abrupt amplitude step dynamics")
    
    # Scenario 9 & 10: Stream interruption and restart
    buf.reset()
    buf.push_chunk(c1)
    buf.reset()
    assert np.all(buf.buffer == 0.0) and buf.windows_emitted == 0
    w_restart = buf.push_chunk(c2)
    assert np.all(w_restart[:8000] == 0.0) and np.all(w_restart[8000:] == 2.0)
    test_results["scenario_9_interruption"] = "PASS"
    test_results["scenario_10_restart"] = "PASS"
    print("[PASS] Scenario 9 & 10: Stream interruption and clean restart")
    
    # Scenario 11 & 12: Recording boundary reset and alternating recordings
    recA_chunk = np.full(8000, 3.0, dtype=np.float32)
    recB_chunk = np.full(8000, 4.0, dtype=np.float32)
    buf.reset()
    buf.push_chunk(recA_chunk)
    buf.reset()
    w_alt = buf.push_chunk(recB_chunk)
    assert np.all(w_alt[:8000] == 0.0) and np.all(w_alt[8000:] == 4.0)
    test_results["scenario_11_boundary_reset"] = "PASS"
    test_results["scenario_12_alternating_recordings"] = "PASS"
    print("[PASS] Scenario 11 & 12: Recording boundary reset & zero cross-recording leakage")
    
    # Scenario 13: Repeated identical audio determinism
    buf.reset()
    buf.push_chunk(sine_pos)
    w_det1 = buf.push_chunk(sine_pos)
    sb1 = extract_subband_vector_c5(w_det1)
    buf.reset()
    buf.push_chunk(sine_pos)
    w_det2 = buf.push_chunk(sine_pos)
    sb2 = extract_subband_vector_c5(w_det2)
    assert np.array_equal(sb1, sb2)
    test_results["scenario_13_determinism"] = "PASS"
    print("[PASS] Scenario 13: Deterministic feature equivalence for identical inputs")
    
    # Scenario 14: Long continuous recorded-audio playback (300 hops = 150 seconds)
    buf.reset()
    for h in range(300):
        c_h = np.sin(2 * np.pi * 500 * (np.arange(8000) + h*8000) / 16000.0).astype(np.float32)
        w_h = buf.push_chunk(c_h)
        assert len(w_h) == 16000
    assert buf.windows_emitted == 300
    test_results["scenario_14_long_playback"] = "PASS"
    print("[PASS] Scenario 14: Long continuous recorded-audio playback (300 hops / 150s)")
    
    # Scenario 15: Concurrent independent streams (4 separate buffers)
    buffers = [StreamingRollingWindowBuffer() for _ in range(4)]
    for i in range(100):
        for b_idx, b in enumerate(buffers):
            chunk_b = np.full(8000, (b_idx + 1) * 1.0, dtype=np.float32)
            w_b = b.push_chunk(chunk_b)
            assert np.all(w_b[8000:] == (b_idx + 1) * 1.0)
    test_results["scenario_15_concurrent_streams"] = "PASS"
    print("[PASS] Scenario 15: Concurrent independent streams (zero cross-buffer interference)")
    
    print("\nAll 15 streaming correctness scenarios PASSED without error.")

if __name__ == "__main__":
    main()

