"""
Stage 8.9.22 - Part 5: Real-Time SNR Estimation & Noise-Floor Tracking Module

Implements multi-method SNR estimation:
1. Minimum Statistics Tracking (Martin 2001 style).
2. Quantile-based stationary noise-floor tracking (15th percentile).
3. VAD-gated background energy estimation.
4. Estimator reliability & confidence scoring (measuring consistency across methods).
5. Continuous and discrete SNR region categorization:
   - Low SNR (< 5.0 dB)
   - Intermediate SNR (5.0 - 10.0 dB)
   - High SNR (> 10.0 dB)
"""

from __future__ import annotations

import logging
from typing import Dict, Any, Tuple
import numpy as np

logger = logging.getLogger("snr_estimator")

class RealTimeSNREstimator:
    def __init__(self, sample_rate: int = 16000, frame_len_ms: float = 32.0, hop_len_ms: float = 16.0):
        self.sr = sample_rate
        self.frame_len = int(frame_len_ms * 1e-3 * self.sr) # 512 samples
        self.hop_len = int(hop_len_ms * 1e-3 * self.sr)     # 256 samples

    def estimate_snr(self, audio: np.ndarray) -> Dict[str, Any]:
        """
        Estimates signal-to-noise ratio and provides reliability diagnostics.
        """
        if len(audio) < self.frame_len:
            audio = np.pad(audio, (0, self.frame_len - len(audio)))

        n_frames = max(1, int((len(audio) - self.frame_len) / self.hop_len) + 1)
        frames = [audio[i * self.hop_len : i * self.hop_len + self.frame_len] for i in range(n_frames)]

        frame_rms = np.array([float(np.sqrt(np.mean(f**2))) for f in frames]) + 1e-9

        # -------------------------------------------------------------
        # Method 1: Quantile-based noise floor (15th percentile)
        # -------------------------------------------------------------
        noise_quantile = float(np.quantile(frame_rms, 0.15))

        # -------------------------------------------------------------
        # Method 2: Minimum statistics tracking (rolling buffer min)
        # -------------------------------------------------------------
        win_size = min(30, len(frame_rms))
        rolling_mins = [np.min(frame_rms[max(0, i - win_size + 1) : i + 1]) for i in range(len(frame_rms))]
        noise_min_stat = float(np.median(rolling_mins))

        # -------------------------------------------------------------
        # Method 3: VAD-Gated Noise Floor
        # -------------------------------------------------------------
        # Estimate spectral flat frames as background noise
        spec_flatnesses = []
        for f in frames:
            mag = np.abs(np.fft.rfft(f * np.hamming(len(f)))) + 1e-9
            geom_m = np.exp(np.mean(np.log(mag)))
            arith_m = np.mean(mag)
            spec_flatnesses.append(geom_m / arith_m)
        spec_flat_arr = np.array(spec_flatnesses)

        noise_frames = frame_rms[spec_flat_arr > 0.40]
        if len(noise_frames) > 3:
            noise_vad = float(np.mean(noise_frames))
        else:
            noise_vad = noise_quantile

        # Composite noise floor estimate
        noise_floor_rms = float(0.50 * noise_quantile + 0.30 * noise_min_stat + 0.20 * noise_vad)

        # Signal peak energy (90th percentile of frame RMS)
        sig_peak_rms = float(np.quantile(frame_rms, 0.90))

        # Spectral noise floor check for continuous tonal / harmonic signals
        full_fft = np.abs(np.fft.rfft(audio * np.hamming(len(audio)))) + 1e-9
        global_sf = float(np.exp(np.mean(np.log(full_fft))) / np.mean(full_fft))

        if noise_floor_rms > 0.70 * sig_peak_rms and global_sf < 0.20:
            # Tonal / harmonic signal is active continuously across the whole file.
            # Estimate noise floor from the lowest 25% spectral bins between harmonic peaks.
            sorted_bins = np.sort(full_fft**2)
            spec_noise_rms = float(np.sqrt(np.mean(sorted_bins[:max(5, int(0.20 * len(sorted_bins)))]))) / np.sqrt(len(audio))
            noise_floor_rms = max(1e-6, spec_noise_rms)

        # SNR calculation
        p_sig = max(1e-9, sig_peak_rms**2 - noise_floor_rms**2)
        p_noise = max(1e-9, noise_floor_rms**2)
        snr_linear = p_sig / p_noise
        snr_db = float(10.0 * np.log10(snr_linear))

        # Reliability metrics: Disagreement between quantile and min-stat
        disagreement = abs(noise_quantile - noise_min_stat) / (noise_floor_rms + 1e-6)
        estimator_reliability = float(np.clip(1.0 - disagreement, 0.20, 1.0))

        # Headroom and SNR confidence
        total_rms = float(np.sqrt(np.mean(audio**2))) + 1e-9
        peak_amp = float(np.max(np.abs(audio)))
        crest_db = float(20.0 * np.log10(max(peak_amp, 1e-6) / total_rms))

        snr_confidence = float(np.clip(estimator_reliability * (min(1.0, crest_db / 15.0)), 0.10, 1.0))

        # Routing Region (Initial thresholds: <5.0 Low, 5.0-10.0 Mid, >10.0 High)
        if snr_db < 5.0:
            routing_region = "LOW_SNR"
        elif snr_db <= 10.0:
            routing_region = "INTERMEDIATE_SNR"
        else:
            routing_region = "HIGH_SNR"

        # Continuous smooth routing weights: Sigmoid around 5 dB and 10 dB
        # weight_high_snr transitions smoothly from 0.0 to 1.0
        weight_high = float(1.0 / (1.0 + np.exp(-0.8 * (snr_db - 10.0))))
        weight_low = float(1.0 / (1.0 + np.exp(0.8 * (snr_db - 5.0))))
        weight_mid = float(np.clip(1.0 - weight_high - weight_low, 0.0, 1.0))

        return {
            "estimated_snr_db": round(snr_db, 2),
            "snr_confidence": round(snr_confidence, 4),
            "estimator_reliability": round(estimator_reliability, 4),
            "noise_floor_rms": round(noise_floor_rms, 6),
            "signal_peak_rms": round(sig_peak_rms, 6),
            "routing_region": routing_region,
            "weight_low": round(weight_low, 4),
            "weight_mid": round(weight_mid, 4),
            "weight_high": round(weight_high, 4),
            "crest_factor_db": round(crest_db, 2)
        }
