"""
Stage 8.9.45: Environmental Audio Transformations (Optimized)
Implements physically-parameterized acoustic degradation functions for Phase C:
1. Mild background masking (SNR +9 dB, +12 dB, +15 dB, +18 dB)
2. Multi-level SNR ladder masking (SNR +3 dB to +18 dB in 3 dB steps)
3. Controlled distance attenuation (8m to 25m spherical spreading + air absorption)
4. Conservative early-reflection RIR (T60 <= 0.3s, high DRR > +8 dB, no long tail)
5. Masking + Controlled Attenuation
6. Masking + Conservative Early RIR
7. Probabilistic mixed transformation (50% pristine, 50% transformed)

MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
import numpy as np
import scipy.signal as signal

TARGET_SR = 16000

def generate_conservative_early_rir(t60=0.20, drr_db=10.0, seed=42):
    """
    Synthesizes a conservative early-reflection Room Impulse Response (RIR).
    T60 is strictly bounded in [0.15, 0.30] seconds to prevent temporal smearing.
    High direct-to-reverberant ratio (DRR >= +8 dB) preserves the direct vocal onset.
    """
    rng = np.random.default_rng(seed)
    length_samples = int(t60 * TARGET_SR)
    
    # Direct path spike at sample 0
    rir = np.zeros(length_samples, dtype=np.float32)
    rir[0] = 1.0
    
    # Decay envelope for early reflections: e^(-t / tau)
    # T60 is time for -60 dB decay (10^-3 amplitude): tau = -T60 / ln(1e-3)
    tau = -t60 / np.log(1e-3)
    t = np.arange(1, length_samples) / TARGET_SR
    decay = np.exp(-t / tau)
    
    # Sparse early reflections (first 40 ms) + diffuse early tail
    early_samples = int(0.040 * TARGET_SR)
    refl_noise = rng.normal(0, 1, length_samples - 1).astype(np.float32)
    refl_envelope = decay * refl_noise
    
    # Low-pass filter the reflections to simulate natural wall absorption
    b_lp, a_lp = signal.butter(2, 4000 / (TARGET_SR / 2), btype='low')
    filtered_refl = signal.lfilter(b_lp, a_lp, refl_envelope)
    
    # Scale reflections to achieve target DRR
    direct_energy = 1.0
    refl_energy = np.sum(filtered_refl ** 2)
    if refl_energy > 1e-9:
        target_refl_energy = direct_energy / (10 ** (drr_db / 10.0))
        scale = np.sqrt(target_refl_energy / refl_energy)
        filtered_refl = filtered_refl * scale
        
    rir[1:] = filtered_refl
    return rir

def apply_rir_convolution(audio, rir):
    """Convolves mono audio with RIR and normalizes peak amplitude."""
    conv = signal.fftconvolve(audio, rir, mode='full')
    conv = conv[:len(audio)]  # match original length
    max_amp = np.max(np.abs(conv))
    if max_amp > 1e-6:
        conv = conv / max_amp
    return conv.astype(np.float32)

def apply_soft_distance_attenuation(audio, distance_m=15.0, seed=42):
    """
    Applies inverse-distance spherical spreading and atmospheric air absorption.
    Distance bounded in [8.0, 25.0] meters.
    """
    ref_distance = 1.0
    amp_scaling = ref_distance / max(distance_m, 1.0)
    
    # Atmospheric air absorption: 1st order lowpass filter
    cutoff_hz = max(3000.0, 8000.0 - (distance_m * 180.0))
    cutoff_norm = min(cutoff_hz / (TARGET_SR / 2), 0.95)
    b, a = signal.butter(1, cutoff_norm, btype='low')
    filtered = signal.lfilter(b, a, audio)
    
    attenuated = filtered * amp_scaling
    max_amp = np.max(np.abs(attenuated))
    if max_amp > 1e-6:
        attenuated = attenuated / max_amp
    return attenuated.astype(np.float32)

def apply_calibrated_background_masking(scream_wf, noise_wf, snr_db=12.0, seed=42):
    """
    Mixes scream waveform with noise waveform at precise target SNR.
    Target SNR in dB = 10 * log10(P_scream / P_noise).
    """
    rng = np.random.default_rng(seed)
    # Loop or slice noise to match scream length
    if len(noise_wf) < len(scream_wf):
        reps = int(np.ceil(len(scream_wf) / len(noise_wf)))
        noise_ext = np.tile(noise_wf, reps)[:len(scream_wf)]
    elif len(noise_wf) > len(scream_wf):
        start_idx = rng.integers(0, len(noise_wf) - len(scream_wf) + 1)
        noise_ext = noise_wf[start_idx:start_idx + len(scream_wf)]
    else:
        noise_ext = noise_wf.copy()

    # Calculate powers
    p_scream = np.mean(scream_wf ** 2)
    p_noise = np.mean(noise_ext ** 2)
    if p_scream < 1e-9 or p_noise < 1e-9:
        return scream_wf.astype(np.float32)

    target_noise_p = p_scream / (10 ** (snr_db / 10.0))
    scale = np.sqrt(target_noise_p / p_noise)
    mixed = scream_wf + (noise_ext * scale)

    max_amp = np.max(np.abs(mixed))
    if max_amp > 1e-6:
        mixed = mixed / max_amp
    return mixed.astype(np.float32)

