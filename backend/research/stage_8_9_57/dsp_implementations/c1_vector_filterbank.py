"""
Stage 8.9.57: Experiment C1 — Vectorized Filterbank
Implementation Identifier: E1_DSP_C1_VECTOR_FILTERBANK

Optimizations:
1. Vectorizes frame RMS extraction using `np.lib.stride_tricks.sliding_window_view`.
2. Eliminates dead computation: only computes frame RMS and temporal variance
   for Bands 0, 3, and 4 (which are actually used in the 11-d output vector),
   skipping Bands 1, 2, and 5.
3. Preserves exact Butterworth filter order (4) and forward-backward zero-phase `filtfilt`.
4. Keeps in-loop filter design to isolate vectorization benefits.
"""
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

IMPLEMENTATION_ID = "E1_DSP_C1_VECTOR_FILTERBANK"

def extract_subband_vector_c1(audio: np.ndarray, sr: int = 16000) -> np.ndarray:
    """Extracts 11-d subband vector using vectorized sliding window RMS for needed bands."""
    nyq = sr / 2.0
    total_energy = float(np.sum(audio ** 2) + 1e-9)
    band_energies = np.empty(6, dtype=np.float32)
    temp_vars = np.empty(3, dtype=np.float32) # Indices 0, 3, 4
    tv_map = {0: 0, 3: 1, 4: 2}

    hop = int(0.010 * sr)   # 160 samples
    frame = int(0.025 * sr) # 400 samples

    for idx, (b_name, f_low, f_high) in enumerate(BANDS):
        low_norm = f_low / nyq
        high_norm = min(0.999, f_high / nyq)
        b, a = signal.butter(4, [low_norm, high_norm], btype='band')
        filtered = signal.filtfilt(b, a, audio)
        band_energies[idx] = float(np.sum(filtered ** 2))

        # Vectorized RMS only for bands where temporal variance is used
        if idx in tv_map:
            windows = np.lib.stride_tricks.sliding_window_view(filtered, frame)[::hop]
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

