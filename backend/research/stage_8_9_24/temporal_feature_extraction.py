"""
Stage 8.9.24: Temporal Modulation & Syllabic Cadence Feature Extractor.

Extracts multi-resolution temporal features:
A. Energy Envelope Dynamics (RMS, modulation depth, temporal std, kurtosis, skewness, crest factor, attack/decay)
B. Modulation Spectrum & Syllabic Cadence (0.5-20 Hz envelope FFT, 1-8 Hz speech bands, entropy, periodicity)
C. Burst Continuity & Closure Intervals (burst continuity ratio, burst count, gap durations, active vocal ratio)
D. Boundary & Noise Robustness (safely handles short transients, near-silence, clipping)
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
from scipy import signal, stats

TARGET_SAMPLE_RATE = 16000

# Canonical feature names
TEMPORAL_MODULATION_FEATURE_NAMES = [
    # Envelope Dynamics (12)
    "rms_energy_mean",
    "rms_energy_std",
    "rms_energy_max",
    "energy_modulation_depth",
    "energy_cv",
    "envelope_kurtosis",
    "envelope_skewness",
    "envelope_crest_factor_db",
    "attack_time_ms",
    "decay_time_ms",
    "energy_slope",
    "energy_discontinuity_var",
    
    # Modulation Spectrum & Syllabic Cadence (8)
    "dominant_modulation_freq_hz",
    "modulation_energy_0_5_to_2hz",
    "modulation_energy_2_to_4hz",
    "modulation_energy_4_to_8hz",
    "modulation_energy_8_to_16hz",
    "syllabic_modulation_ratio",  # (2-8 Hz) / (0.5-20 Hz)
    "modulation_entropy",
    "temporal_regularity_autocorr",
    
    # Burst Continuity & Vocal Closure (8)
    "burst_continuity_ratio",
    "energy_burst_count",
    "mean_burst_duration_ms",
    "max_burst_duration_ms",
    "mean_inter_burst_interval_ms",
    "vocal_closure_gap_count",
    "active_vocal_ratio",
    "sustain_to_peak_ratio"
]


class TemporalModulationExtractor:
    """Multi-resolution temporal modulation and syllabic cadence feature extractor."""

    def __init__(
        self,
        sr: int = TARGET_SAMPLE_RATE,
        frame_ms: float = 25.0,
        hop_ms: float = 12.5,
    ):
        self.sr = sr
        self.frame_len = int(round(sr * (frame_ms / 1000.0)))
        self.hop_len = int(round(sr * (hop_ms / 1000.0)))
        self.window = signal.windows.hann(self.frame_len, sym=False).astype(np.float32)

    def extract_features(
        self,
        waveform: np.ndarray,
        context_sec: Optional[float] = None,
    ) -> Dict[str, float]:
        """Extract complete 28-dimensional temporal modulation feature dictionary."""
        # 1. Sanitize waveform
        wf = np.nan_to_num(waveform, nan=0.0, posinf=1.0, neginf=-1.0).astype(np.float32)
        if len(wf) == 0:
            return {name: 0.0 for name in TEMPORAL_MODULATION_FEATURE_NAMES}

        # Remove DC offset
        wf = wf - float(np.mean(wf))
        n_samples = len(wf)

        # Context truncation if requested
        if context_sec is not None and context_sec > 0:
            max_samples = int(round(context_sec * self.sr))
            if n_samples > max_samples:
                wf = wf[:max_samples]
                n_samples = max_samples

        # Check for near-silence
        rms_total = float(np.sqrt(np.mean(wf ** 2) + 1e-12))
        if n_samples < self.frame_len or rms_total < 1e-5:
            res = {name: 0.0 for name in TEMPORAL_MODULATION_FEATURE_NAMES}
            res["active_vocal_ratio"] = 0.0
            return res

        # 2. Vectorized short-time framing
        n_frames = (n_samples - self.frame_len) // self.hop_len + 1
        if n_frames < 2:
            # Pad to at least 2 frames
            pad_len = 2 * self.frame_len
            wf = np.pad(wf, (0, max(0, pad_len - n_samples)), mode="constant")
            n_samples = len(wf)
            n_frames = (n_samples - self.frame_len) // self.hop_len + 1

        shape = (n_frames, self.frame_len)
        strides = (wf.strides[0] * self.hop_len, wf.strides[0])
        frames = np.lib.stride_tricks.as_strided(wf, shape=shape, strides=strides)

        # Apply window
        windowed = frames * self.window

        # Short-time frame RMS envelope
        frame_rms = np.sqrt(np.mean(windowed ** 2, axis=1) + 1e-12).astype(np.float32)
        fps = self.sr / self.hop_len  # Envelope sampling rate (e.g. 80 Hz for 12.5 ms hop)

        # -------------------------------------------------------------
        # Part A: Energy Envelope Dynamics
        # -------------------------------------------------------------
        rms_mean = float(np.mean(frame_rms))
        rms_std = float(np.std(frame_rms))
        rms_max = float(np.max(frame_rms))
        rms_min = float(np.min(frame_rms))

        energy_mod_depth = float((rms_max - rms_min) / (rms_mean + 1e-6))
        energy_cv = float(rms_std / (rms_mean + 1e-6))

        # Kurtosis and Skewness of energy envelope
        if rms_std > 1e-7:
            env_kurt = float(stats.kurtosis(frame_rms, fisher=True))
            env_skew = float(stats.skew(frame_rms))
        else:
            env_kurt = 0.0
            env_skew = 0.0

        peak_amp = float(np.max(np.abs(wf)))
        crest_factor_db = float(20.0 * math.log10(max(peak_amp, 1e-6) / max(rms_mean, 1e-6)))

        # Attack & Decay times
        idx_max = int(np.argmax(frame_rms))
        thresh_10 = 0.10 * rms_max
        thresh_90 = 0.90 * rms_max
        pre_peak = frame_rms[: idx_max + 1]
        i10_arr = np.where(pre_peak >= thresh_10)[0]
        i90_arr = np.where(pre_peak >= thresh_90)[0]
        i10 = int(i10_arr[0]) if len(i10_arr) > 0 else 0
        i90 = int(i90_arr[0]) if len(i90_arr) > 0 else idx_max
        attack_time_ms = float(max(1.0, (i90 - i10) * (self.hop_len / self.sr) * 1000.0))

        post_peak = frame_rms[idx_max:]
        if len(post_peak) > 1:
            decay_time_ms = float((len(post_peak) - 1) * (self.hop_len / self.sr) * 1000.0)
            energy_slope = float((post_peak[0] - post_peak[-1]) / max(0.01, decay_time_ms / 1000.0))
        else:
            decay_time_ms = 0.0
            energy_slope = 0.0

        # Energy discontinuities: variance of 2nd derivative of envelope
        if n_frames > 3:
            d2_env = np.diff(frame_rms, n=2)
            energy_disc_var = float(np.var(d2_env))
        else:
            energy_disc_var = 0.0

        # -------------------------------------------------------------
        # Part B: Modulation Spectrum & Syllabic Cadence (0.5 - 20 Hz)
        # -------------------------------------------------------------
        # Subtract mean envelope to focus on modulation AC components
        env_ac = frame_rms - rms_mean
        n_fft_mod = 256
        if len(env_ac) < n_fft_mod:
            env_ac_padded = np.pad(env_ac, (0, n_fft_mod - len(env_ac)), mode="constant")
        else:
            env_ac_padded = env_ac[:n_fft_mod]

        mod_fft = np.abs(np.fft.rfft(env_ac_padded, n=n_fft_mod))
        mod_freqs = np.fft.rfftfreq(n_fft_mod, d=1.0 / fps)

        # Frequency bands for syllabic analysis
        idx_05_2 = np.where((mod_freqs >= 0.5) & (mod_freqs < 2.0))[0]
        idx_2_4 = np.where((mod_freqs >= 2.0) & (mod_freqs < 4.0))[0]
        idx_4_8 = np.where((mod_freqs >= 4.0) & (mod_freqs < 8.0))[0]
        idx_8_16 = np.where((mod_freqs >= 8.0) & (mod_freqs < 16.0))[0]
        idx_total = np.where((mod_freqs >= 0.5) & (mod_freqs <= 20.0))[0]

        total_mod_energy = float(np.sum(mod_fft[idx_total] ** 2) + 1e-12)
        e_05_2 = float(np.sum(mod_fft[idx_05_2] ** 2))
        e_2_4 = float(np.sum(mod_fft[idx_2_4] ** 2))
        e_4_8 = float(np.sum(mod_fft[idx_4_8] ** 2))
        e_8_16 = float(np.sum(mod_fft[idx_8_16] ** 2))

        # Dominant modulation frequency
        if len(idx_total) > 0:
            dom_idx = idx_total[int(np.argmax(mod_fft[idx_total]))]
            dom_freq = float(mod_freqs[dom_idx])
        else:
            dom_freq = 0.0

        # Syllabic modulation ratio: (2-8 Hz) energy divided by total modulation energy
        syllabic_ratio = float((e_2_4 + e_4_8) / total_mod_energy)

        # Modulation spectrum entropy (flatness of modulation distribution)
        p_mod = (mod_fft[idx_total] ** 2) / total_mod_energy
        p_mod = p_mod[p_mod > 0]
        mod_entropy = float(-np.sum(p_mod * np.log2(p_mod + 1e-12)) / max(1.0, math.log2(len(idx_total) + 1e-6)))

        # Temporal regularity via normalized autocorrelation of frame RMS
        if n_frames > 8:
            ac = signal.correlate(env_ac, env_ac, mode="full")
            ac = ac[len(ac) // 2 :]
            ac_norm = ac / (ac[0] + 1e-12)
            # Search for syllabic periodicity between 100 ms and 600 ms
            min_lag = int(0.100 * fps)
            max_lag = min(len(ac_norm) - 1, int(0.600 * fps))
            if max_lag > min_lag:
                reg_peak = float(np.max(ac_norm[min_lag : max_lag + 1]))
            else:
                reg_peak = 0.0
        else:
            reg_peak = 0.0

        # -------------------------------------------------------------
        # Part C: Burst Continuity & Vocal Closures
        # -------------------------------------------------------------
        # Vocal activity threshold: 15% of peak RMS or minimum 0.015
        vocal_thresh = max(0.015, 0.15 * rms_max)
        is_active = (frame_rms >= vocal_thresh).astype(int)
        active_ratio = float(np.mean(is_active))

        # Run-length encoding of bursts and gaps
        bursts_len = []
        gaps_len = []
        curr_state = is_active[0]
        curr_count = 1
        for v in is_active[1:]:
            if v == curr_state:
                curr_count += 1
            else:
                if curr_state == 1:
                    bursts_len.append(curr_count)
                else:
                    gaps_len.append(curr_count)
                curr_state = v
                curr_count = 1
        if curr_state == 1:
            bursts_len.append(curr_count)
        else:
            gaps_len.append(curr_count)

        frame_duration_ms = (self.hop_len / self.sr) * 1000.0

        burst_count = len(bursts_len)
        if burst_count > 0:
            mean_burst_ms = float(np.mean(bursts_len) * frame_duration_ms)
            max_burst_ms = float(np.max(bursts_len) * frame_duration_ms)
            burst_continuity = float(np.max(bursts_len) / (np.sum(bursts_len) + 1e-6))
        else:
            mean_burst_ms = 0.0
            max_burst_ms = 0.0
            burst_continuity = 0.0

        gap_count = len(gaps_len)
        if gap_count > 0:
            mean_gap_ms = float(np.mean(gaps_len) * frame_duration_ms)
        else:
            mean_gap_ms = 0.0

        # Sustain-to-peak ratio: median energy of active frames / peak energy
        active_energies = frame_rms[is_active == 1]
        if len(active_energies) > 0:
            sustain_to_peak = float(np.median(active_energies) / max(1e-6, rms_max))
        else:
            sustain_to_peak = 0.0

        return {
            "rms_energy_mean": rms_mean,
            "rms_energy_std": rms_std,
            "rms_energy_max": rms_max,
            "energy_modulation_depth": energy_mod_depth,
            "energy_cv": energy_cv,
            "envelope_kurtosis": env_kurt,
            "envelope_skewness": env_skew,
            "envelope_crest_factor_db": crest_factor_db,
            "attack_time_ms": attack_time_ms,
            "decay_time_ms": decay_time_ms,
            "energy_slope": energy_slope,
            "energy_discontinuity_var": energy_disc_var,
            "dominant_modulation_freq_hz": dom_freq,
            "modulation_energy_0_5_to_2hz": e_05_2,
            "modulation_energy_2_to_4hz": e_2_4,
            "modulation_energy_4_to_8hz": e_4_8,
            "modulation_energy_8_to_16hz": e_8_16,
            "syllabic_modulation_ratio": syllabic_ratio,
            "modulation_entropy": mod_entropy,
            "temporal_regularity_autocorr": reg_peak,
            "burst_continuity_ratio": burst_continuity,
            "energy_burst_count": float(burst_count),
            "mean_burst_duration_ms": mean_burst_ms,
            "max_burst_duration_ms": max_burst_ms,
            "mean_inter_burst_interval_ms": mean_gap_ms,
            "vocal_closure_gap_count": float(gap_count),
            "active_vocal_ratio": active_ratio,
            "sustain_to_peak_ratio": sustain_to_peak,
        }

    def extract_feature_vector(
        self,
        waveform: np.ndarray,
        context_sec: Optional[float] = None,
    ) -> np.ndarray:
        """Return features as a numpy array in canonical order."""
        feat_dict = self.extract_features(waveform, context_sec=context_sec)
        return np.array([feat_dict[k] for k in TEMPORAL_MODULATION_FEATURE_NAMES], dtype=np.float32)
