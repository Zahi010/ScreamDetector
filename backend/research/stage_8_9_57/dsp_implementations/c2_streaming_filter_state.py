"""
Stage 8.9.57: Experiment C2 — Persistent Streaming Filter States
Implementation Identifier: E1_DSP_C2_STREAMING_FILTER_STATE

Optimizations:
1. Replaces forward-backward zero-phase `filtfilt` with forward-only Second-Order Sections (`sosfilt`).
2. Retains persistent filter state `zi` across contiguous sliding audio windows.
3. Provides explicit `reset()` API to guarantee zero state contamination across independent clips or streams.
4. Eliminates boundary padding transients on streaming hops.
"""
from typing import List, Optional
import numpy as np
import scipy.signal as signal

BANDS = [
    ("Band1_300_800Hz", 300, 800),
    ("Band2_800_1500Hz", 800, 1500),
    ("Band3_1500_2000Hz", 1500, 2000),
    ("Band4_2000_3000Hz", 2000, 3000),
    ("Band5_3000_4000Hz", 3000, 4000),
    ("Band6_4000_6000Hz", 4000, 6000)
]

IMPLEMENTATION_ID = "E1_DSP_C2_STREAMING_FILTER_STATE"

class StreamingFilterbankC2:
    """Encapsulates persistent streaming state for the 6-band subband filterbank."""

    def __init__(self, sr: int = 16000):
        self.sr = sr
        self.nyq = sr / 2.0
        self.hop = int(0.010 * sr)
        self.frame = int(0.025 * sr)
        self.filters_sos = []
        self.zi_states: List[np.ndarray] = []

        # Precompute 4th-order Butterworth SOS filters
        for b_name, f_low, f_high in BANDS:
            low_norm = f_low / self.nyq
            high_norm = min(0.999, f_high / self.nyq)
            sos = signal.butter(4, [low_norm, high_norm], btype='band', output='sos')
            self.filters_sos.append(sos)
            # Initialize filter state to zeros
            zi = signal.sosfilt_zi(sos) * 0.0
            self.zi_states.append(zi)

    def reset(self) -> None:
        """Resets all persistent filter states to zero (prevents cross-stream contamination)."""
        self.zi_states = [signal.sosfilt_zi(sos) * 0.0 for sos in self.filters_sos]

    def process_window(self, audio: np.ndarray) -> np.ndarray:
        """Processes an audio window, updating persistent filter states."""
        total_energy = float(np.sum(audio ** 2) + 1e-9)
        band_energies = np.empty(6, dtype=np.float32)
        temp_vars = np.empty(3, dtype=np.float32)
        tv_map = {0: 0, 3: 1, 4: 2}

        for idx, sos in enumerate(self.filters_sos):
            # Forward-only filtering with persistent state
            filtered, self.zi_states[idx] = signal.sosfilt(sos, audio, zi=self.zi_states[idx])
            band_energies[idx] = float(np.sum(filtered ** 2))

            if idx in tv_map:
                windows = np.lib.stride_tricks.sliding_window_view(filtered, self.frame)[::self.hop]
                frame_rms = np.sqrt(np.mean(windows ** 2, axis=1) + 1e-9)
                e_std = float(np.std(frame_rms))
                e_mean = float(np.mean(frame_rms))
                temp_vars[tv_map[idx]] = e_std / (e_mean + 1e-9)

        rel_energies = band_energies / total_energy
        low_e = band_energies[0] + band_energies[1] + 1e-9
        scream_band_e = band_energies[3] + band_energies[4] + 1e-9

        return np.array([
            rel_energies[0], rel_energies[1], rel_energies[2],
            rel_energies[3], rel_energies[4], rel_energies[5],
            temp_vars[0], temp_vars[1], temp_vars[2],
            scream_band_e / low_e,
            band_energies[5] / total_energy
        ], dtype=np.float32)

