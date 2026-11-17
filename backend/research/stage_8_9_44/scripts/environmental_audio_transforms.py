"""
Stage 8.9.44: Environmental Acoustic Transformations Module
Implements research-grade acoustic transforms for audio waveforms at 16,000 Hz:
1. Room Impulse Response (RIR) synthesis and convolution (Small, Medium, Large, Hall, Outdoor).
2. Distance attenuation (geometric spreading + frequency-dependent atmospheric absorption).
3. Background acoustic masking (calibrated SNR mixing).
4. Combined environmental pipelines with reproducible seeds.
"""
import os
import sys
import numpy as np
import scipy.signal as signal
import soundfile as sf
import librosa

TARGET_SR = 16000

# -----------------------------------------------------------------------------
# 1. Room Impulse Response (RIR) Synthesis & Convolution
# -----------------------------------------------------------------------------
ROOM_PROFILES = {
    "small_room": {"t60_range": (0.15, 0.35), "drr_range": (2.0, 6.0), "desc": "Small enclosed space / booth"},
    "medium_room": {"t60_range": (0.35, 0.65), "drr_range": (-1.0, 3.0), "desc": "Classroom / residential hall"},
    "large_hall": {"t60_range": (0.65, 1.20), "drr_range": (-6.0, 0.0), "desc": "Auditorium / large indoor venue"},
    "outdoor_diffuse": {"t60_range": (0.05, 0.15), "drr_range": (4.0, 10.0), "desc": "Open field with distant ground reflections"}
}

def generate_synthetic_rir(sr=TARGET_SR, room_profile="medium_room", t60=None, drr_db=None, seed=None):
    """
    Synthesizes a physically parameterized room impulse response using an 
    initial discrete early reflection cluster followed by Poisson-decay diffuse reverberation.
    """
    if seed is not None:
        np.random.seed(seed)

    profile = ROOM_PROFILES.get(room_profile, ROOM_PROFILES["medium_room"])
    if t60 is None:
        t60 = np.random.uniform(profile["t60_range"][0], profile["t60_range"][1])
    if drr_db is None:
        drr_db = np.random.uniform(profile["drr_range"][0], profile["drr_range"][1])

    # Duration: 1.2 * T60
    duration = max(0.08, float(t60 * 1.2))
    n_samples = int(sr * duration)
    t = np.arange(n_samples) / sr

    # 1. Direct path (time t=0)
    rir = np.zeros(n_samples, dtype=np.float32)
    direct_idx = int(0.002 * sr) # 2 ms direct arrival
    rir[direct_idx] = 1.0

    # 2. Early reflections (between 5ms and 50ms)
    n_early = int(np.random.randint(6, 15))
    early_times = np.random.uniform(0.005, min(0.050, duration * 0.4), n_early)
    early_amps = np.random.uniform(0.1, 0.5, n_early) * np.random.choice([-1.0, 1.0], n_early)
    for et, ea in zip(early_times, early_amps):
        idx = int(et * sr)
        if idx < n_samples:
            rir[idx] += ea * np.exp(-3.0 * et / t60)

    # 3. Diffuse late reverberation (exponentially decaying Gaussian noise)
    decay_rate = 6.907755 / t60 # -60 dB is factor of 10^-3, ln(1000) = 6.9078
    late_envelope = np.exp(-decay_rate * t)
    late_noise = np.random.randn(n_samples).astype(np.float32)
    # Low-pass filter late tail to simulate high-frequency absorption in air and materials
    nyq = sr / 2.0
    cutoff = min(0.75, 2500.0 / nyq)
    b, a = signal.butter(2, cutoff, btype='low')
    filtered_late = signal.filtfilt(b, a, late_noise)
    diffuse = late_envelope * filtered_late

    # Combine direct + early and diffuse tail based on Direct-to-Reverberant Ratio (DRR)
    energy_direct = rir[direct_idx] ** 2
    energy_rev = np.sum(diffuse ** 2) + 1e-9
    desired_energy_rev = energy_direct / (10.0 ** (drr_db / 10.0))
    scale_rev = np.sqrt(desired_energy_rev / energy_rev)
    diffuse_scaled = diffuse * scale_rev

    # Zero direct arrival region for diffuse tail to avoid phase cancellation
    diffuse_scaled[:int(0.005 * sr)] = 0.0

    combined_rir = rir + diffuse_scaled
    # Normalize peak to 1.0
    combined_rir = combined_rir / (np.max(np.abs(combined_rir)) + 1e-9)

    params = {
        "room_profile": room_profile,
        "t60_seconds": round(float(t60), 3),
        "drr_db": round(float(drr_db), 2),
        "duration_seconds": round(float(duration), 3)
    }
    return combined_rir, params

def apply_rir_convolution(wf, rir):
    """
    Convolves waveform with synthetic RIR, preserving input duration and peak normalization.
    """
    orig_len = len(wf)
    rev_wf = signal.fftconvolve(wf, rir, mode="full")[:orig_len]
    max_amp = np.max(np.abs(rev_wf))
    if max_amp > 1e-6:
        rev_wf = rev_wf / max_amp
    return rev_wf.astype(np.float32)

# -----------------------------------------------------------------------------
# 2. Distance Attenuation & Atmospheric Absorption
# -----------------------------------------------------------------------------
def apply_distance_attenuation(wf, distance_m=15.0, ref_distance_m=2.0, sr=TARGET_SR):
    """
    Models physical sound propagation over distance:
    1. Spherical spreading inverse distance law: P(d) = P(d0) * (d0 / d)
    2. High-frequency atmospheric absorption: attenuation increases with frequency
    """
    # 1. Geometric spreading
    dist_ratio = max(0.05, float(ref_distance_m / max(distance_m, ref_distance_m)))
    attenuated = wf * dist_ratio

    # 2. Atmospheric absorption (modeled via distance-proportional low-pass roll-off)
    # Air absorption at 20C, 50% RH: ~0.003 dB/m at 1kHz, ~0.03 dB/m at 4kHz, ~0.09 dB/m at 8kHz
    if distance_m > ref_distance_m:
        excess_dist = distance_m - ref_distance_m
        # Frequency cutoff drops smoothly with distance
        nyq = sr / 2.0
        cutoff_hz = max(1800.0, 7500.0 - (excess_dist * 120.0))
        cutoff_norm = min(0.95, cutoff_hz / nyq)
        b, a = signal.butter(1, cutoff_norm, btype='low')
        attenuated = signal.filtfilt(b, a, attenuated)

    max_amp = np.max(np.abs(attenuated))
    if max_amp > 1e-6:
        attenuated = attenuated / max_amp
    return attenuated.astype(np.float32)

# -----------------------------------------------------------------------------
# 3. Background Acoustic Masking
# -----------------------------------------------------------------------------
def apply_background_masking(wf, background_wf, snr_db=6.0):
    """
    Mixes target vocal signal with background environmental noise at a calibrated SNR.
    """
    p_signal = np.mean(wf ** 2) + 1e-9
    
    # Match background length
    if len(background_wf) < len(wf):
        repeats = int(np.ceil(len(wf) / len(background_wf)))
        bg = np.tile(background_wf, repeats)[:len(wf)]
    else:
        start_idx = 0
        if len(background_wf) > len(wf):
            start_idx = np.random.randint(0, len(background_wf) - len(wf) + 1)
        bg = background_wf[start_idx:start_idx + len(wf)]

    p_bg = np.mean(bg ** 2) + 1e-9
    desired_p_bg = p_signal / (10.0 ** (snr_db / 10.0))
    scale_bg = np.sqrt(desired_p_bg / p_bg)
    mixed = wf + (bg * scale_bg)

    max_amp = np.max(np.abs(mixed))
    if max_amp > 1e-6:
        mixed = mixed / max_amp
    return mixed.astype(np.float32)

# -----------------------------------------------------------------------------
# 4. Combined Transformation Pipeline
# -----------------------------------------------------------------------------
def apply_combined_environmental(
    wf,
    background_wf=None,
    room_profile="medium_room",
    distance_m=12.0,
    snr_db=6.0,
    seed=None
):
    """
    Applies unified environmental acoustic chain:
    Dry Speech -> RIR Convolution -> Distance Attenuation -> Background Masking
    """
    rir, rir_params = generate_synthetic_rir(sr=TARGET_SR, room_profile=room_profile, seed=seed)
    wf_rev = apply_rir_convolution(wf, rir)
    wf_dist = apply_distance_attenuation(wf_rev, distance_m=distance_m, sr=TARGET_SR)
    
    if background_wf is not None:
        wf_final = apply_background_masking(wf_dist, background_wf, snr_db=snr_db)
    else:
        wf_final = wf_dist

    params = {
        "rir": rir_params,
        "distance_m": round(float(distance_m), 1),
        "snr_db": round(float(snr_db), 1) if background_wf is not None else None
    }
    return wf_final, params

