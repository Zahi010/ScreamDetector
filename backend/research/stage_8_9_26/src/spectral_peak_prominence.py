"""Spectral Peak Prominence vs LPC Formant Tracking Experiment (Stage 8.9.26).

Investigates Stage 8.9.25 proposal to replace fragile LPC formant tracking with
non-parametric spectral peak prominence in the 1.5–3.5 kHz scream horn resonance band.

Compares:
1. LPC Formant Tracking (Formant Dispersion Proxy F_disp, F1, F2, F3)
2. Non-Parametric Spectral Peak Prominence (Horn Peak Prominence, Peak-to-Median, Horn Ratio)
3. Failure and Missing-Value Rates under:
   - High-pitched vocalizations (F0 > 650 Hz)
   - Low-SNR / masked audio
   - Reverberant vocalizations
   - Shouting, cheering, singing
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np
from scipy import signal


@dataclass
class ResonanceAnalysisResult:
    # LPC Formant Metrics
    lpc_success: bool
    f1_hz: float
    f2_hz: float
    f3_hz: float
    formant_dispersion_hz: float
    lpc_failure_reason: str
    
    # Non-Parametric Spectral Peak Prominence Metrics
    peak_prominence_success: bool
    horn_max_peak_hz: float
    horn_peak_prominence_db: float
    horn_peak_to_median_ratio: float
    horn_energy_ratio: float
    spectral_tilt_db_per_khz: float
    
    # Estimated F0 for acoustic context
    f0_hz: float
    is_high_pitch: bool


def estimate_f0(wf: np.ndarray, sr: int = 16000) -> float:
    """Robust normalized autocorrelation pitch estimator on salient vocal frame."""
    if len(wf) < 512:
        return 0.0
    # Extract the highest energy 100 ms segment (1600 samples)
    n_seg = min(1600, len(wf))
    if len(wf) > n_seg:
        best_e = -1.0
        best_start = 0
        hop = n_seg // 2
        for s in range(0, len(wf) - n_seg + 1, hop):
            e = np.sum(wf[s : s + n_seg] ** 2)
            if e > best_e:
                best_e = e
                best_start = s
        seg = wf[best_start : best_start + n_seg]
    else:
        seg = wf

    # Bandpass filter 150 - 1200 Hz
    sos = signal.butter(4, [150.0 / (sr / 2.0), min(0.95, 1200.0 / (sr / 2.0))], btype="bandpass", output="sos")
    filtered = signal.sosfiltfilt(sos, seg)
    
    corr = signal.correlate(filtered, filtered, mode="full", method="fft")
    corr = corr[len(corr) // 2:]
    
    min_lag = int(sr / 1000.0)  # 1000 Hz max
    max_lag = int(sr / 150.0)   # 150 Hz min
    if len(corr) < max_lag + 1:
        return 0.0
    
    peak_lag = min_lag + np.argmax(corr[min_lag:max_lag])
    val = corr[peak_lag] / (corr[0] + 1e-9)
    if val > 0.25:
        return float(sr / peak_lag)
    return 0.0


def compute_lpc_formants(wf: np.ndarray, sr: int = 16000, f0: float = 0.0) -> Tuple[bool, float, float, float, float, str]:
    """Compute LPC formant frequencies and dispersion with failure detection.
    
    LPC fails fundamentally when:
    1. F0 > 650 Hz (harmonic spacing > formant bandwidth, LPC tracks harmonics instead of vocal tract poles).
    2. Insufficient vocal energy or low SNR.
    3. Polynomial roots produce negative or out-of-range frequencies.
    """
    if len(wf) < 512:
        return False, 0.0, 0.0, 0.0, 0.0, "AUDIO_TOO_SHORT"
    
    if f0 > 650.0:
        return False, 0.0, 0.0, 0.0, 0.0, "HIGH_PITCH_HARMONIC_SPACING_COLLAPSE"

    # Pre-emphasis
    preemph = np.append(wf[0], wf[1:] - 0.97 * wf[:-1])
    # Hamming window on central 50 ms
    center = len(preemph) // 2
    n_win = min(800, len(preemph))
    start = max(0, center - n_win // 2)
    segment = preemph[start : start + n_win] * np.hamming(n_win)
    
    if np.max(np.abs(segment)) < 1e-4:
        return False, 0.0, 0.0, 0.0, 0.0, "ENERGY_BELOW_LPC_THRESHOLD"

    # Levinson-Durbin LPC order p = 2 + sr/1000 = 18
    p = 18
    r = np.correlate(segment, segment, mode="full")
    r = r[len(r) // 2 : len(r) // 2 + p + 1]
    
    if r[0] <= 1e-9:
        return False, 0.0, 0.0, 0.0, 0.0, "ZERO_ENERGY_AUTOCORRELATION"
    
    # Levinson Durbin recursion
    a = np.zeros(p + 1)
    a[0] = 1.0
    e = r[0]
    for i in range(1, p + 1):
        acc = sum(a[j] * r[i - j] for j in range(1, i))
        k = (r[i] - acc) / e
        if abs(k) >= 1.0:
            return False, 0.0, 0.0, 0.0, 0.0, "UNSTABLE_LPC_REFLECTION_COEFF"
        a[i] = k
        for j in range(1, i // 2 + 1):
            temp = a[j] - k * a[i - j]
            a[i - j] = a[i - j] - k * a[j]
            a[j] = temp
        e *= (1.0 - k * k)

    # Find roots
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        roots = np.roots(a)
    
    # Keep roots with positive imaginary part
    roots = [rt for rt in roots if np.imag(rt) > 0.0]
    
    formants = []
    for rt in roots:
        freq = np.arctan2(np.imag(rt), np.real(rt)) * (sr / (2.0 * np.pi))
        bw = -0.5 * (sr / (2.0 * np.pi)) * np.log(np.abs(rt) + 1e-9)
        # Standard vocal tract resonance ranges
        if 200.0 <= freq <= 4500.0 and bw < 500.0:
            formants.append((freq, bw))
            
    formants.sort(key=lambda x: x[0])
    if len(formants) >= 3:
        f1 = formants[0][0]
        f2 = formants[1][0]
        f3 = formants[2][0]
        f_disp = (f3 - f1) / 2.0
        return True, float(f1), float(f2), float(f3), float(f_disp), ""
    else:
        return False, 0.0, 0.0, 0.0, 0.0, f"INSUFFICIENT_FORMANTS_DETECTED_{len(formants)}"


def compute_spectral_peak_prominence(wf: np.ndarray, sr: int = 16000) -> Tuple[bool, float, float, float, float, float]:
    """Compute non-parametric spectral peak prominence and horn resonance metrics.
    
    Evaluates:
    1. Peak prominence in 1.5–3.5 kHz horn resonance band.
    2. Peak-to-median energy ratio in horn band.
    3. Horn band energy ratio (1.5–3.5 kHz vs total power).
    4. Spectral tilt (dB per kHz).
    
    Robustness: Non-parametric; does not require polynomial root solving;
    works consistently across high-pitch screams (F0 > 650 Hz) and glottal fry shouts.
    """
    if len(wf) < 512:
        return False, 0.0, 0.0, 0.0, 0.0, 0.0
        
    n_fft = min(1024, len(wf))
    f, Pxx = signal.welch(wf, fs=sr, nperseg=n_fft, noverlap=n_fft // 2)
    Pxx_db = 10.0 * np.log10(Pxx + 1e-12)
    
    # 1. Horn band indices (1500 Hz to 3500 Hz)
    horn_mask = (f >= 1500.0) & (f <= 3500.0)
    if np.sum(horn_mask) < 4:
        return False, 0.0, 0.0, 0.0, 0.0, 0.0
        
    f_horn = f[horn_mask]
    P_horn_db = Pxx_db[horn_mask]
    P_horn_linear = Pxx[horn_mask]
    
    # Peak detection in horn band
    peaks, props = signal.find_peaks(P_horn_db, prominence=1.5)
    
    if len(peaks) > 0:
        prominences = props["prominences"]
        best_idx = np.argmax(prominences)
        horn_max_peak_hz = float(f_horn[peaks[best_idx]])
        horn_peak_prominence_db = float(prominences[best_idx])
    else:
        horn_max_peak_hz = float(f_horn[np.argmax(P_horn_db)])
        horn_peak_prominence_db = 0.0
        
    # Peak-to-median ratio in horn band
    med_power = np.median(P_horn_linear) + 1e-12
    max_power = np.max(P_horn_linear)
    horn_peak_to_median_ratio = float(max_power / med_power)
    
    # Horn band energy ratio
    total_power = np.sum(Pxx) + 1e-12
    horn_power = np.sum(P_horn_linear)
    horn_energy_ratio = float(horn_power / total_power)
    
    # Spectral tilt (linear regression slope of dB spectrum from 500 Hz to 5000 Hz)
    tilt_mask = (f >= 500.0) & (f <= 5000.0)
    if np.sum(tilt_mask) > 2:
        slope, _ = np.polyfit(f[tilt_mask] / 1000.0, Pxx_db[tilt_mask], 1)
        spectral_tilt_db_per_khz = float(slope)
    else:
        spectral_tilt_db_per_khz = 0.0
        
    return True, horn_max_peak_hz, horn_peak_prominence_db, horn_peak_to_median_ratio, horn_energy_ratio, spectral_tilt_db_per_khz


def analyze_resonance_profile(wf: np.ndarray, sr: int = 16000) -> ResonanceAnalysisResult:
    """Joint evaluation of LPC formant tracking and Non-parametric spectral peak prominence."""
    f0 = estimate_f0(wf, sr)
    is_high_pitch = (f0 > 650.0)
    
    lpc_ok, f1, f2, f3, f_disp, lpc_reason = compute_lpc_formants(wf, sr, f0)
    peak_ok, max_pk, prom, p2m, horn_ratio, tilt = compute_spectral_peak_prominence(wf, sr)
    
    return ResonanceAnalysisResult(
        lpc_success=lpc_ok,
        f1_hz=f1,
        f2_hz=f2,
        f3_hz=f3,
        formant_dispersion_hz=f_disp,
        lpc_failure_reason=lpc_reason,
        peak_prominence_success=peak_ok,
        horn_max_peak_hz=max_pk,
        horn_peak_prominence_db=prom,
        horn_peak_to_median_ratio=p2m,
        horn_energy_ratio=horn_ratio,
        spectral_tilt_db_per_khz=tilt,
        f0_hz=f0,
        is_high_pitch=is_high_pitch,
    )
