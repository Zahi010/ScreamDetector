import time
import numpy as np
from pathlib import Path
from scipy import signal

import sys
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))
from src.config import TARGET_SAMPLE_RATE
from experiments.v2_hard_negative_training.v4_temporal_research.extract_temporal_and_turbulence_features import (
    compute_frame_hnr,
    compute_spectral_features,
    compute_envelope_and_rhythm_features,
    compute_pitch_cv,
    extract_16_turbulence_features,
)
from experiments.v2_hard_negative_training.v4_temporal_research.stage8_9_11_evaluation.extract_stage8_9_11_features import (
    compute_snr_features,
)

# Realistic 1-second 16kHz audio
np.random.seed(42)
t = np.linspace(0, 1.0, 16000, endpoint=False)
waveform = (0.3 * np.sin(2 * np.pi * 1000 * t) + 0.1 * np.random.randn(len(t))).astype(np.float32)

print("Profiling subcomponents over 50 iterations...")

# Warmup
for _ in range(10):
    extract_16_turbulence_features(waveform, sr=TARGET_SAMPLE_RATE)
    compute_snr_features(waveform, sr=TARGET_SAMPLE_RATE)

# 1. HNR
t0 = time.perf_counter()
for _ in range(50):
    frame_len = 1024
    hop_len = 512
    n_frames = (len(waveform) - frame_len) // hop_len + 1
    hnr_list = [compute_frame_hnr(waveform[i*hop_len : i*hop_len + frame_len], sr=TARGET_SAMPLE_RATE) for i in range(min(n_frames, 100))]
t_hnr = (time.perf_counter() - t0) * 1000 / 50

# 2. Spectral features
t0 = time.perf_counter()
for _ in range(50):
    compute_spectral_features(waveform, sr=TARGET_SAMPLE_RATE)
t_spectral = (time.perf_counter() - t0) * 1000 / 50

# 3. Envelope and rhythm features
t0 = time.perf_counter()
for _ in range(50):
    compute_envelope_and_rhythm_features(waveform, sr=TARGET_SAMPLE_RATE)
t_envelope = (time.perf_counter() - t0) * 1000 / 50

# 4. Pitch CV
t0 = time.perf_counter()
for _ in range(50):
    compute_pitch_cv(waveform, sr=TARGET_SAMPLE_RATE)
t_pitch = (time.perf_counter() - t0) * 1000 / 50

# 5. SNR features
t0 = time.perf_counter()
for _ in range(50):
    compute_snr_features(waveform, sr=TARGET_SAMPLE_RATE)
t_snr = (time.perf_counter() - t0) * 1000 / 50

print(f"HNR (autocorrelation frames):       {t_hnr:.2f} ms")
print(f"Spectral features (STFT 1024):       {t_spectral:.2f} ms")
print(f"Envelope & rhythm (RMS loop+STFT512):{t_envelope:.2f} ms")
print(f"Pitch CV (np.correlate loop):        {t_pitch:.2f} ms")
print(f"SNR features (Welch PSD):            {t_snr:.2f} ms")
print(f"Total Stage 4 Time:                  {t_hnr + t_spectral + t_envelope + t_pitch + t_snr:.2f} ms")
