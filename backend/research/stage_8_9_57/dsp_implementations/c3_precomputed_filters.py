"""
Stage 8.9.57: Experiment C3 — Precomputed Filter Coefficients
Implementation Identifier: E1_DSP_C3_PRECOMPUTED_FILTERS

Optimizations:
1. Precomputes numerator (b) and denominator (a) Butterworth polynomial coefficients
   at module initialization for fixed sampling rate sr=16000.
2. Completely eliminates the six repeated `signal.butter()` design calls on every window.
3. Retains original list comprehension frame RMS logic to isolate the precomputation gain.
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

IMPLEMENTATION_ID = "E1_DSP_C3_PRECOMPUTED_FILTERS"

# Precomputed filter coefficients at module load time (sr=16000, order=4)
SR_DEFAULT = 16000
NYQ_DEFAULT = SR_DEFAULT / 2.0
PRECOMPUTED_BA = [
    signal.butter(4, [f_low / NYQ_DEFAULT, min(0.999, f_high / NYQ_DEFAULT)], btype='band')
    for _, f_low, f_high in BANDS
]

def extract_subband_vector_c3(audio: np.ndarray, sr: int = 16000) -> np.ndarray:
    """Extracts 11-d subband vector using precomputed filter coefficients."""
    total_energy = float(np.sum(audio ** 2) + 1e-9)
    band_energies = []
    temp_vars = []

    hop = int(0.010 * sr)
    frame = int(0.025 * sr)
    n_frames = max(1, (len(audio) - frame) // hop + 1)

    for b, a in PRECOMPUTED_BA:
        filtered = signal.filtfilt(b, a, audio)
        band_energy = float(np.sum(filtered ** 2))
        band_energies.append(band_energy)
        frame_rms = [np.sqrt(np.mean(filtered[i*hop : i*hop + frame]**2) + 1e-9) for i in range(n_frames)]
        energy_std = float(np.std(frame_rms))
        energy_mean = float(np.mean(frame_rms))
        temp_vars.append(energy_std / (energy_mean + 1e-9))

    rel_energies = [be / total_energy for be in band_energies]
    low_e = band_energies[0] + band_energies[1] + 1e-9
    scream_band_e = band_energies[3] + band_energies[4] + 1e-9

    return np.array([
        rel_energies[0], rel_energies[1], rel_energies[2],
        rel_energies[3], rel_energies[4], rel_energies[5],
        temp_vars[0], temp_vars[3], temp_vars[4],
        scream_band_e / low_e,
        band_energies[5] / total_energy
    ], dtype=np.float32)

