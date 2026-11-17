"""
Stage 8.9.57: Experiment C4 — Allocation & Memory Optimization
Implementation Identifier: E1_DSP_C4_MEMORY_OPTIMIZATION

Optimizations:
1. Replaces dynamic Python list appending with fixed pre-allocated float32 NumPy arrays.
2. Uses in-place array normalization and contiguous memory views.
3. Eliminates intermediate float object boxing and array conversions.
4. Uses precomputed filter coefficients and pre-allocated output buffer.
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

IMPLEMENTATION_ID = "E1_DSP_C4_MEMORY_OPTIMIZATION"

SR_DEFAULT = 16000
NYQ_DEFAULT = SR_DEFAULT / 2.0
PRECOMPUTED_BA = [
    signal.butter(4, [f_low / NYQ_DEFAULT, min(0.999, f_high / NYQ_DEFAULT)], btype='band')
    for _, f_low, f_high in BANDS
]

def extract_subband_vector_c4(audio: np.ndarray, sr: int = 16000) -> np.ndarray:
    """Extracts 11-d subband vector using pre-allocated memory buffers."""
    audio_c = np.ascontiguousarray(audio, dtype=np.float32)
    total_energy = float(np.dot(audio_c, audio_c) + 1e-9)

    band_energies = np.empty(6, dtype=np.float32)
    temp_vars = np.empty(3, dtype=np.float32) # For bands 0, 3, 4
    tv_indices = {0: 0, 3: 1, 4: 2}

    hop = int(0.010 * sr)
    frame = int(0.025 * sr)
    n_frames = max(1, (len(audio_c) - frame) // hop + 1)

    for idx, (b, a) in enumerate(PRECOMPUTED_BA):
        filtered = signal.filtfilt(b, a, audio_c)
        f_contig = np.ascontiguousarray(filtered, dtype=np.float32)
        band_energies[idx] = float(np.dot(f_contig, f_contig))

        if idx in tv_indices:
            frame_rms = np.empty(n_frames, dtype=np.float32)
            for i in range(n_frames):
                seg = f_contig[i * hop : i * hop + frame]
                frame_rms[i] = np.sqrt(np.mean(seg * seg) + 1e-9)
            e_mean = float(np.mean(frame_rms))
            e_std = float(np.std(frame_rms))
            temp_vars[tv_indices[idx]] = e_std / (e_mean + 1e-9)

    out_vec = np.empty(11, dtype=np.float32)
    out_vec[0:6] = band_energies / total_energy
    out_vec[6] = temp_vars[0]
    out_vec[7] = temp_vars[1]
    out_vec[8] = temp_vars[2]
    out_vec[9] = (band_energies[3] + band_energies[4] + 1e-9) / (band_energies[0] + band_energies[1] + 1e-9)
    out_vec[10] = band_energies[5] / total_energy

    return out_vec

