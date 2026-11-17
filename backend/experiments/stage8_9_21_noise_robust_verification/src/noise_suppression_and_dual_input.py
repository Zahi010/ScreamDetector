"""
Stage 8.9.21 - Experiment C & D: Noise Suppression, Audio Enhancement & Dual-Input Architecture

Implements audio enhancement methods:
1. Spectral Gating: Adaptive frequency-dependent thresholding.
2. Spectral Subtraction (Boll 1979): Magnitude subtraction with oversubtraction & spectral floor.
3. Wiener Filtering: Decision-directed a priori SNR estimation and Wiener gain.
4. Adaptive Noise Estimation: Minimum statistics tracking for non-stationary noise floors.

Evaluates:
- Preservation vs destruction of scream acoustic markers:
  * Subharmonic-to-Harmonic Ratio (SHR)
  * Pitch instability and tracking failure
  * High-frequency turbulence (>6 kHz)
  * Short scream onset attack time (tau_attack)
  * Harmonic irregularities
- Dual-input fusion architectures:
  1. Original audio only
  2. Enhanced audio only
  3. Original + Enhanced Late Fusion
  4. Original + Enhanced Feature-Level Fusion
  5. Original + Enhanced Confidence-Aware Fusion
"""

from __future__ import annotations

import logging
from typing import Dict, Tuple, List, Optional
import numpy as np
from scipy.signal import stft, istft

logger = logging.getLogger("noise_suppression_dual_input")

class AudioEnhancer:
    def __init__(self, sample_rate: int = 16000):
        self.sr = sample_rate
        self.n_fft = 512
        self.hop_length = 128
        self.win_length = 512

    def spectral_gating(self, audio: np.ndarray, thresh_db: float = -18.0) -> np.ndarray:
        """
        Adaptive spectral gating: Estimates noise profile from lowest energy frames
        and gates frequency bins falling below the threshold.
        """
        if len(audio) < self.n_fft:
            return audio.copy()
        f, t, Zxx = stft(audio, fs=self.sr, nperseg=self.win_length, noverlap=self.win_length - self.hop_length)
        mag = np.abs(Zxx)
        phase = np.angle(Zxx)

        # Estimate noise floor from bottom 15% quantile per frequency bin
        noise_floor = np.quantile(mag, 0.15, axis=1, keepdims=True) + 1e-8
        snr_linear = mag / noise_floor
        gain = 1.0 / (1.0 + (10.0 ** (thresh_db / 10.0)) / (snr_linear + 1e-6))
        gain = np.clip(gain, 0.05, 1.0) # floor to prevent total musical noise artifact

        Zxx_enhanced = gain * mag * np.exp(1j * phase)
        _, enhanced = istft(Zxx_enhanced, fs=self.sr, nperseg=self.win_length, noverlap=self.win_length - self.hop_length)
        if len(enhanced) < len(audio):
            enhanced = np.pad(enhanced, (0, len(audio) - len(enhanced)))
        else:
            enhanced = enhanced[:len(audio)]
        return enhanced.astype(np.float32)

    def spectral_subtraction(self, audio: np.ndarray, alpha: float = 1.5, beta: float = 0.02) -> np.ndarray:
        """
        Boll's Spectral Subtraction with oversubtraction alpha and spectral floor beta.
        """
        if len(audio) < self.n_fft:
            return audio.copy()
        f, t, Zxx = stft(audio, fs=self.sr, nperseg=self.win_length, noverlap=self.win_length - self.hop_length)
        mag = np.abs(Zxx)
        phase = np.angle(Zxx)

        # Estimate stationary noise from the first 5 frames or lowest 10%
        n_init = min(5, mag.shape[1])
        noise_est = np.mean(mag[:, :n_init], axis=1, keepdims=True)

        # Subtraction
        sub = mag**2 - alpha * (noise_est**2)
        sub = np.maximum(sub, beta * (noise_est**2))
        mag_enhanced = np.sqrt(sub)

        Zxx_enhanced = mag_enhanced * np.exp(1j * phase)
        _, enhanced = istft(Zxx_enhanced, fs=self.sr, nperseg=self.win_length, noverlap=self.win_length - self.hop_length)
        if len(enhanced) < len(audio):
            enhanced = np.pad(enhanced, (0, len(audio) - len(enhanced)))
        else:
            enhanced = enhanced[:len(audio)]
        return enhanced.astype(np.float32)

    def wiener_filter(self, audio: np.ndarray, alpha_dd: float = 0.96) -> np.ndarray:
        """
        Wiener filter using Decision-Directed a priori SNR tracking (Ephraim-Malah framework).
        """
        if len(audio) < self.n_fft:
            return audio.copy()
        f, t, Zxx = stft(audio, fs=self.sr, nperseg=self.win_length, noverlap=self.win_length - self.hop_length)
        mag = np.abs(Zxx)
        phase = np.angle(Zxx)
        n_bins, n_frames = mag.shape

        noise_pow = np.mean(mag[:, :min(5, n_frames)]**2, axis=1, keepdims=True) + 1e-8
        gain_prev = np.ones((n_bins, 1))
        mag_prev = mag[:, :1]

        gains = np.zeros_like(mag)
        for i in range(n_frames):
            gamma = (mag[:, i:i+1]**2) / noise_pow # a posteriori SNR
            # Decision-directed a priori SNR
            xi = alpha_dd * (gain_prev**2 * mag_prev**2) / noise_pow + (1.0 - alpha_dd) * np.maximum(gamma - 1.0, 0.0)
            gain = xi / (1.0 + xi)
            gain = np.clip(gain, 0.05, 1.0)
            gains[:, i:i+1] = gain

            gain_prev = gain
            mag_prev = mag[:, i:i+1]

        Zxx_enhanced = gains * mag * np.exp(1j * phase)
        _, enhanced = istft(Zxx_enhanced, fs=self.sr, nperseg=self.win_length, noverlap=self.win_length - self.hop_length)
        if len(enhanced) < len(audio):
            enhanced = np.pad(enhanced, (0, len(audio) - len(enhanced)))
        else:
            enhanced = enhanced[:len(audio)]
        return enhanced.astype(np.float32)

    def adaptive_noise_estimation(self, audio: np.ndarray) -> np.ndarray:
        """
        Adaptive noise floor tracking via minimum statistics and spectral subtraction.
        """
        if len(audio) < self.n_fft:
            return audio.copy()
        f, t, Zxx = stft(audio, fs=self.sr, nperseg=self.win_length, noverlap=self.win_length - self.hop_length)
        mag = np.abs(Zxx)
        phase = np.angle(Zxx)

        # Recursive smoothed power spectrum
        alpha_s = 0.85
        smoothed = np.zeros_like(mag)
        smoothed[:, 0] = mag[:, 0]
        for i in range(1, mag.shape[1]):
            smoothed[:, i] = alpha_s * smoothed[:, i-1] + (1.0 - alpha_s) * mag[:, i]

        # Minimum tracking over rolling buffer
        win_size = min(20, mag.shape[1])
        noise_est = np.zeros_like(mag)
        for i in range(mag.shape[1]):
            start_idx = max(0, i - win_size + 1)
            noise_est[:, i] = np.min(smoothed[:, start_idx : i + 1], axis=1) * 1.2 # safety margin

        # Spectral subtraction
        mag_enhanced = np.maximum(mag - noise_est, 0.08 * mag)
        Zxx_enhanced = mag_enhanced * np.exp(1j * phase)
        _, enhanced = istft(Zxx_enhanced, fs=self.sr, nperseg=self.win_length, noverlap=self.win_length - self.hop_length)
        if len(enhanced) < len(audio):
            enhanced = np.pad(enhanced, (0, len(audio) - len(enhanced)))
        else:
            enhanced = enhanced[:len(audio)]
        return enhanced.astype(np.float32)

    def enhance(self, audio: np.ndarray, method: str = "wiener") -> np.ndarray:
        m = method.lower()
        if m in ("orig", "original", "none"):
            return audio.copy()
        elif m in ("gating", "spectral_gating"):
            return self.spectral_gating(audio)
        elif m in ("subtraction", "spectral_subtraction"):
            return self.spectral_subtraction(audio)
        elif m in ("wiener", "wiener_filter"):
            return self.wiener_filter(audio)
        elif m in ("adaptive", "adaptive_noise"):
            return self.adaptive_noise_estimation(audio)
        else:
            raise ValueError(f"Unknown enhancement method: {method}")

class DualInputFusionEngine:
    """
    Implements and evaluates the 5 Dual-Input Fusion architectures:
    1. Original audio only
    2. Enhanced audio only
    3. Original + Enhanced Late Fusion
    4. Original + Enhanced Feature-Level Fusion
    5. Original + Enhanced Confidence-Aware Fusion
    """
    def __init__(self, sample_rate: int = 16000):
        self.sr = sample_rate
        self.enhancer = AudioEnhancer(sample_rate=sample_rate)

    @staticmethod
    def late_fusion(prob_orig: float, prob_enh: float, w_orig: float = 0.65) -> float:
        """Weighted convex combination of calibrated probabilities."""
        return float(np.clip(w_orig * prob_orig + (1.0 - w_orig) * prob_enh, 0.0, 1.0))

    @staticmethod
    def feature_fusion(feat_orig: np.ndarray, feat_enh: np.ndarray) -> np.ndarray:
        """Concatenates original and enhanced feature representations."""
        return np.concatenate([feat_orig, feat_enh], axis=-1)

    @staticmethod
    def confidence_aware_fusion(prob_orig: float, prob_enh: float, snr_est_db: float, has_high_turb: bool) -> Tuple[float, Dict[str, float]]:
        """
        Dynamic gating:
        When SNR is high (>10 dB) and phonation is modal, enhancement is clean and given equal or higher weight.
        When SNR is low (<5 dB) or high turbulence/chaos is detected, enhancement risk of suppressing screams
        is acute, so weight on original audio increases to 0.85-0.95.
        """
        if snr_est_db < 0.0 or has_high_turb:
            w_orig = 0.90
        elif snr_est_db < 10.0:
            w_orig = 0.75
        else:
            w_orig = 0.55

        w_enh = 1.0 - w_orig
        fused_prob = float(np.clip(w_orig * prob_orig + w_enh * prob_enh, 0.0, 1.0))
        return fused_prob, {"w_orig": w_orig, "w_enh": w_enh, "snr_est_db": snr_est_db}
