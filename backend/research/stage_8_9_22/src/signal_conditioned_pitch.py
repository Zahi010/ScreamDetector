"""
Stage 8.9.22 - Part 4: Signal-Conditioned Pitch Failure & Vocal Activity Analysis

Implements:
1. Signal-conditioned pitch tracking failure:
   high_energy_pitch_failure = failed_high_energy_vocal_frames / eligible_high_energy_vocal_frames
2. Excludes low-energy background silence and digital dropouts from the denominator.
3. Distinguishes chaotic phonation collapse from unvoiced speech and poor signal quality (clipping/dropouts).
4. Adaptive energy thresholding vs fixed 0.15 RMS baseline.
5. Minimum observation criteria and confidence scoring.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, Tuple
import numpy as np

logger = logging.getLogger("signal_conditioned_pitch")

class SignalConditionedPitchTracker:
    def __init__(self, sample_rate: int = 16000, frame_len_ms: float = 40.0, hop_len_ms: float = 10.0):
        self.sr = sample_rate
        self.frame_len = int(frame_len_ms * 1e-3 * self.sr) # 640 samples
        self.hop_len = int(hop_len_ms * 1e-3 * self.sr)     # 160 samples
        self.min_lag = int(self.sr / 1000.0) # 1000 Hz ceiling
        self.max_lag = int(self.sr / 80.0)   # 80 Hz floor

    def compute_frame_vocal_activity(self, frame: np.ndarray) -> float:
        """
        Estimates probability that frame contains human vocal activity [0.0, 1.0].
        Uses energy concentration in the 300 - 3400 Hz telephone/vocal band
        relative to sub-bass (<150 Hz) and ultra-high (>5000 Hz).
        """
        mag = np.abs(np.fft.rfft(frame * np.hamming(len(frame)), n=512))
        freqs = np.fft.rfftfreq(512, 1.0 / self.sr)

        vocal_mask = (freqs >= 300.0) & (freqs <= 3400.0)
        tot_energy = np.sum(mag**2) + 1e-9
        vocal_energy = np.sum(mag[vocal_mask]**2)

        ratio = vocal_energy / tot_energy
        # Sigmoid scaling
        prob = 1.0 / (1.0 + np.exp(-10.0 * (ratio - 0.45)))
        return float(np.clip(prob, 0.0, 1.0))

    def analyze_audio(
        self,
        audio: np.ndarray,
        fixed_rms_thresh: float = 0.15,
        adaptive_rms: bool = True
    ) -> Dict[str, Any]:
        """
        Extracts signal-conditioned pitch metrics, clipping, dropouts, and failure statistics.
        """
        if len(audio) < self.frame_len:
            audio = np.pad(audio, (0, self.frame_len - len(audio)))

        # Normalize headroom
        peak_amp = float(np.max(np.abs(audio)))
        if peak_amp > 1e-6:
            norm_audio = audio / peak_amp
        else:
            norm_audio = audio.copy()

        n_frames = max(1, int((len(norm_audio) - self.frame_len) / self.hop_len) + 1)
        frames = [norm_audio[i * self.hop_len : i * self.hop_len + self.frame_len] for i in range(n_frames)]

        frame_rms_list = []
        frame_conf_list = []
        frame_f0_list = []
        frame_vad_list = []
        frame_clipped_list = []
        frame_dropout_list = []

        for f in frames:
            f_rms = float(np.sqrt(np.mean(f**2)))
            frame_rms_list.append(f_rms)

            is_clipped = bool(np.max(np.abs(f)) >= 0.98)
            is_dropout = bool(f_rms < 1e-4)
            frame_clipped_list.append(is_clipped)
            frame_dropout_list.append(is_dropout)

            vad_p = self.compute_frame_vocal_activity(f)
            frame_vad_list.append(vad_p)

            if is_dropout:
                frame_conf_list.append(0.0)
                frame_f0_list.append(0.0)
                continue

            # Normalized Autocorrelation
            w = f * np.hamming(len(f))
            acorr = np.correlate(w, w, mode='full')[len(w) - 1:]
            if acorr[0] < 1e-6:
                frame_conf_list.append(0.0)
                frame_f0_list.append(0.0)
                continue

            norm_acorr = acorr / acorr[0]
            search = norm_acorr[self.min_lag : self.max_lag]
            if len(search) == 0:
                frame_conf_list.append(0.0)
                frame_f0_list.append(0.0)
                continue

            pk_idx = np.argmax(search) + self.min_lag
            pk_val = float(norm_acorr[pk_idx])
            frame_conf_list.append(pk_val)

            if pk_val >= 0.40:
                f0 = self.sr / float(pk_idx)
                frame_f0_list.append(f0)
            else:
                frame_f0_list.append(0.0)

        f_rms_arr = np.array(frame_rms_list)
        f_conf_arr = np.array(frame_conf_list)
        f_f0_arr = np.array(frame_f0_list)
        f_vad_arr = np.array(frame_vad_list)
        f_clip_arr = np.array(frame_clipped_list)
        f_drop_arr = np.array(frame_dropout_list)

        # -------------------------------------------------------------
        # Determine Energy Threshold
        # -------------------------------------------------------------
        if adaptive_rms:
            # Use 60th percentile of active non-dropout frames
            active_rms = f_rms_arr[~f_drop_arr]
            if len(active_rms) > 0:
                effective_rms_thresh = float(max(0.05, min(0.30, np.quantile(active_rms, 0.60))))
            else:
                effective_rms_thresh = fixed_rms_thresh
        else:
            effective_rms_thresh = fixed_rms_thresh

        # -------------------------------------------------------------
        # 1. Raw Pitch Failure (ungated)
        # -------------------------------------------------------------
        raw_pitch_failure_rate = float(np.mean(f_f0_arr == 0.0))

        # -------------------------------------------------------------
        # 2. High-Energy Pitch Failure (energy gated only)
        # -------------------------------------------------------------
        high_energy_mask = (f_rms_arr >= effective_rms_thresh) & (~f_drop_arr)
        n_high_energy = int(np.sum(high_energy_mask))

        if n_high_energy >= 3:
            he_failed = np.sum((f_f0_arr == 0.0) & high_energy_mask)
            high_energy_pitch_failure = float(he_failed / n_high_energy)
            he_confidence = float(min(1.0, n_high_energy / 15.0))
        else:
            high_energy_pitch_failure = 0.0
            he_confidence = 0.0

        # -------------------------------------------------------------
        # 3. High-Energy Vocal Pitch Failure (energy + VAD gated)
        # -------------------------------------------------------------
        vocal_he_mask = high_energy_mask & (f_vad_arr >= 0.40) & (~f_clip_arr)
        n_vocal_he = int(np.sum(vocal_he_mask))

        if n_vocal_he >= 3:
            vocal_he_failed = np.sum((f_f0_arr == 0.0) & vocal_he_mask)
            high_energy_vocal_pitch_failure = float(vocal_he_failed / n_vocal_he)
            vocal_confidence = float(min(1.0, n_vocal_he / 10.0))
            is_available = True
        else:
            high_energy_vocal_pitch_failure = 0.0
            vocal_confidence = 0.0
            is_available = False

        # -------------------------------------------------------------
        # 4. Voiced Pitch Dynamics & Discontinuity
        # -------------------------------------------------------------
        voiced_f0 = f_f0_arr[f_f0_arr > 0]
        if len(voiced_f0) > 1:
            f0_deltas = np.abs(np.diff(voiced_f0))
            discontinuity_rate = float(np.mean(f0_deltas > 100.0))
            f0_mean = float(np.mean(voiced_f0))
            f0_std = float(np.std(voiced_f0))
            f0_cv = float(f0_std / (f0_mean + 1e-6))
        else:
            discontinuity_rate = 0.0
            f0_mean = 0.0
            f0_std = 0.0
            f0_cv = 0.0

        # Quality metrics
        clipping_ratio = float(np.mean(f_clip_arr))
        dropout_ratio = float(np.mean(f_drop_arr))
        mean_pitch_conf = float(np.mean(f_conf_arr))

        return {
            "raw_pitch_failure_rate": round(raw_pitch_failure_rate, 4),
            "high_energy_pitch_failure": round(high_energy_pitch_failure, 4),
            "high_energy_vocal_pitch_failure": round(high_energy_vocal_pitch_failure, 4),
            "effective_rms_thresh": round(effective_rms_thresh, 4),
            "eligible_vocal_he_frames": n_vocal_he,
            "vocal_confidence": round(vocal_confidence, 4),
            "is_available": is_available,
            "discontinuity_rate": round(discontinuity_rate, 4),
            "f0_mean": round(f0_mean, 2),
            "f0_std": round(f0_std, 2),
            "f0_cv": round(f0_cv, 4),
            "clipping_ratio": round(clipping_ratio, 4),
            "dropout_ratio": round(dropout_ratio, 4),
            "mean_pitch_conf": round(mean_pitch_conf, 4)
        }
