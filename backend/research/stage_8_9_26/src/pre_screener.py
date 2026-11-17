"""Stage 1: Acoustic Pre-Screening Engine (Stage 8.9.26).

Purpose:
Rapidly identify potentially relevant acoustic regions before invoking computationally
heavier neural network classifiers (Model C, YAMNet, Model E).

Inexpensive features evaluated:
- RMS energy and Short-Time Frame Energy (dBFS)
- Adaptive noise floor tracking (10th percentile background energy)
- Spectral Flux (half-wave rectified spectral novelty)
- Zero Crossing Rate (ZCR)
- Spectral Centroid (brightness / center of mass)
- High-Band Energy Ratio (> 1.2 kHz energy vs total energy)

Design Constraints:
1. Conservative rejection: Only obvious digital silence, room tone, and low-energy non-vocal background noise
   are eliminated.
2. Sensitivity protection: Never reject quiet/distant screams or short startle shrieks (down to -6 dB SNR).
3. Zero-scream bottleneck: Pass rate on positive screams must be >= 98%.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, Tuple
import numpy as np
from scipy import signal


@dataclass
class PreScreeningResult:
    passed: bool
    rms_dbfs: float
    noise_floor_dbfs: float
    snr_estimate_db: float
    spectral_flux: float
    spectral_centroid_hz: float
    zcr: float
    high_band_ratio: float
    processing_time_ms: float
    rejection_reason: str = ""


class AcousticPreScreener:
    """Lightweight, low-latency pre-screener for streaming audio buffers."""

    def __init__(
        self,
        sample_rate: int = 16000,
        absolute_silence_threshold_db: float = -55.0,
        min_snr_threshold_db: float = 1.5,
        min_spectral_centroid_hz: float = 300.0,
    ):
        self.sample_rate = sample_rate
        self.silence_thresh_db = absolute_silence_threshold_db
        self.min_snr_db = min_snr_threshold_db
        self.min_centroid_hz = min_spectral_centroid_hz

    def process_waveform(self, wf: np.ndarray) -> PreScreeningResult:
        """Process a mono audio buffer (float32, normalized -1 to +1)."""
        t0 = time.perf_counter()
        if len(wf) == 0:
            return PreScreeningResult(
                passed=False,
                rms_dbfs=-100.0,
                noise_floor_dbfs=-100.0,
                snr_estimate_db=0.0,
                spectral_flux=0.0,
                spectral_centroid_hz=0.0,
                zcr=0.0,
                high_band_ratio=0.0,
                processing_time_ms=0.0,
                rejection_reason="EMPTY_BUFFER",
            )

        # 1. RMS Energy
        eps = 1e-9
        mean_sq = np.mean(wf ** 2)
        rms = np.sqrt(max(eps, mean_sq))
        rms_dbfs = float(20.0 * np.log10(rms))

        # 2. Zero Crossing Rate
        signs = np.sign(wf)
        signs[signs == 0] = 1
        zcr = float(np.mean(np.abs(np.diff(signs)) > 0))

        # 3. Short-time STFT analysis for spectral features
        n_fft = min(512, len(wf))
        if n_fft < 128:
            # Buffer too short for STFT, rely on time-domain metrics
            passed = rms_dbfs >= self.silence_thresh_db
            dt_ms = (time.perf_counter() - t0) * 1000.0
            return PreScreeningResult(
                passed=passed,
                rms_dbfs=rms_dbfs,
                noise_floor_dbfs=rms_dbfs,
                snr_estimate_db=0.0,
                spectral_flux=0.0,
                spectral_centroid_hz=1000.0 if passed else 0.0,
                zcr=zcr,
                high_band_ratio=0.5 if passed else 0.0,
                processing_time_ms=dt_ms,
                rejection_reason="" if passed else "SHORT_BUFFER_BELOW_SILENCE",
            )

        hop = n_fft // 2
        f, t_spec, Zxx = signal.stft(wf, fs=self.sample_rate, nperseg=n_fft, noverlap=hop)
        mag = np.abs(Zxx)  # (n_bins, n_frames)

        # Spectral Centroid per frame and mean
        freqs = f[:, np.newaxis]
        mag_sum = np.sum(mag, axis=0) + eps
        centroid_frames = np.sum(freqs * mag, axis=0) / mag_sum
        spectral_centroid_hz = float(np.mean(centroid_frames))

        # Spectral Flux (half-wave rectified onset novelty across frames)
        if mag.shape[1] > 1:
            diff = mag[:, 1:] - mag[:, :-1]
            rectified = np.maximum(0.0, diff)
            flux = float(np.mean(np.sum(rectified ** 2, axis=0)))
        else:
            flux = 0.0

        # Frame energies for adaptive noise floor tracking
        frame_energies = 20.0 * np.log10(np.sqrt(np.mean(mag ** 2, axis=0) + eps))
        noise_floor_dbfs = float(np.percentile(frame_energies, 15))
        peak_energy_dbfs = float(np.max(frame_energies))
        snr_est = max(0.0, peak_energy_dbfs - noise_floor_dbfs)

        # High-band energy ratio (power above 1200 Hz vs total power)
        cutoff_bin = int(round(1200.0 / (self.sample_rate / n_fft)))
        high_power = np.sum(mag[cutoff_bin:, :] ** 2)
        total_power = np.sum(mag ** 2) + eps
        high_band_ratio = float(high_power / total_power)

        # --- Decision Logic (Conservative) ---
        rejection_reason = ""
        # Rule 1: Absolute silence (digital silence or room tone < -55 dBFS with negligible flux)
        if rms_dbfs < self.silence_thresh_db and flux < 0.01:
            rejection_reason = "BELOW_ABSOLUTE_SILENCE_FLOOR"
            passed = False
        # Rule 2: Inaudible low-frequency rumble (centroid < 300 Hz, negligible high band, negligible flux)
        elif spectral_centroid_hz < self.min_centroid_hz and high_band_ratio < 0.05 and flux < 0.02:
            rejection_reason = "LOW_FREQUENCY_RUMBLE_WITHOUT_VOCAL_ENERGY"
            passed = False
        # Rule 3: Static stationary background without temporal dynamics (SNR estimate < 1.0 dB and flux < 0.005)
        elif snr_est < 1.0 and flux < 0.005 and rms_dbfs < -40.0:
            rejection_reason = "STATIONARY_INACTIVE_BACKGROUND"
            passed = False
        else:
            passed = True

        dt_ms = (time.perf_counter() - t0) * 1000.0
        return PreScreeningResult(
            passed=passed,
            rms_dbfs=rms_dbfs,
            noise_floor_dbfs=noise_floor_dbfs,
            snr_estimate_db=snr_est,
            spectral_flux=flux,
            spectral_centroid_hz=spectral_centroid_hz,
            zcr=zcr,
            high_band_ratio=high_band_ratio,
            processing_time_ms=dt_ms,
            rejection_reason=rejection_reason,
        )
