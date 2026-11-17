"""Stage 8.9.14 Vectorized Acoustic Discriminability Feature Extractor.

Extracts 30 acoustically grounded features across 4 distinct families:
- Family A (8 features): Harmonicity and Vocal Turbulence (HNR, Subharmonic, Spectral Flatness, Spectral Entropy)
- Family B (8 features): Spectral Dynamics and Formant Bandwidth (Centroid, Bandwidth, Scream Resonance 1.5-3.5 kHz, Low Vocal Ratio, Spectral Flux, Centroid Slope)
- Family C (8 features): Temporal Energy and Envelope Dynamics (Log Attack Time, Sustain Ratio, Crest Factor, Kurtosis, Onset Gradient, Decay Rate, Burst Continuity)
- Family D (6 features): Pitch and Voicing Irregularity (Mean F0, Max F0, Pitch CV, Voicing Confidence, Jitter, Pitch Breaks)

Pure NumPy/SciPy implementation. Robust against silence, clipping, DC offset, and non-finite values.
"""

from __future__ import annotations

from typing import Dict, List, Tuple
import numpy as np
from scipy import signal

TARGET_SAMPLE_RATE = 16000

FAMILY_A_NAMES = [
    "hnr_mean_db",
    "hnr_min_db",
    "subharmonic_ratio",
    "harmonic_energy_ratio",
    "spectral_flatness_mean",
    "spectral_flatness_max",
    "spectral_entropy_mean",
    "spectral_entropy_variance",
]

FAMILY_B_NAMES = [
    "spectral_centroid_mean",
    "spectral_bandwidth_mean",
    "scream_resonance_ratio",
    "low_vocal_energy_ratio",
    "high_freq_rolloff_ratio",
    "spectral_flux_mean",
    "spectral_flux_max",
    "spectral_centroid_slope",
]

FAMILY_C_NAMES = [
    "log_attack_time",
    "sustain_to_peak_ratio",
    "envelope_crest_factor",
    "envelope_kurtosis",
    "max_onset_gradient",
    "decay_rate_db_per_sec",
    "energy_temporal_std",
    "burst_continuity_ratio",
]

FAMILY_D_NAMES = [
    "f0_mean_hz",
    "f0_max_hz",
    "pitch_cv",
    "voicing_confidence",
    "pitch_jitter_local",
    "pitch_break_rate",
]

ALL_FEATURE_NAMES = FAMILY_A_NAMES + FAMILY_B_NAMES + FAMILY_C_NAMES + FAMILY_D_NAMES


class AcousticDiscriminabilityExtractor:
    """High-throughput acoustic feature extractor for scream vs. hard-negative discrimination."""

    def __init__(self, sr: int = TARGET_SAMPLE_RATE):
        self.sr = sr
        self.frame_len = 1024  # 64 ms at 16 kHz
        self.hop_len = 512     # 32 ms hop
        self.min_lag = int(sr / 1000)  # 16 samples -> 1000 Hz
        self.max_lag = int(sr / 90)    # 177 samples -> 90 Hz
        self.n_fft = 2048
        self.window = signal.windows.hann(self.frame_len, sym=False)

    def extract_features(self, waveform: np.ndarray) -> np.ndarray:
        """Extract complete 30-dim acoustic discriminability vector from waveform."""
        # Clean waveform of DC offset and non-finite values
        waveform = np.nan_to_num(waveform, nan=0.0, posinf=1.0, neginf=-1.0).astype(np.float32)
        waveform = waveform - np.mean(waveform)

        n_samples = len(waveform)
        if n_samples < 320:
            return np.zeros(30, dtype=np.float32)

        rms_global = float(np.sqrt(np.mean(waveform ** 2) + 1e-12))
        if rms_global < 1e-6:
            # Extreme silence
            return np.zeros(30, dtype=np.float32)

        # Slice frames
        n_frames = (n_samples - self.frame_len) // self.hop_len + 1
        if n_frames <= 0:
            # Pad short buffer
            pad_len = self.frame_len - n_samples
            waveform = np.pad(waveform, (0, pad_len), mode="constant")
            n_frames = 1

        shape = (n_frames, self.frame_len)
        strides = (waveform.strides[0] * self.hop_len, waveform.strides[0])
        frames = np.lib.stride_tricks.as_strided(waveform, shape=shape, strides=strides)

        windowed_frames = frames * self.window
        frame_energies = np.sum(windowed_frames ** 2, axis=1)

        # ---------------------------------------------------------------------
        # 1. FFT Magnitude Spectrum across frames
        # ---------------------------------------------------------------------
        spec = np.abs(np.fft.rfft(windowed_frames, n=self.n_fft, axis=1))  # (n_frames, 1025)
        power_spec = spec ** 2
        freqs = np.fft.rfftfreq(self.n_fft, d=1.0 / self.sr)

        # ---------------------------------------------------------------------
        # 2. Vectorized Autocorrelation for Pitch, Voicing & HNR
        # ---------------------------------------------------------------------
        fx = np.fft.rfft(frames, n=self.n_fft, axis=1)
        rx = np.fft.irfft(fx * np.conj(fx), n=self.n_fft, axis=1)[:, : self.max_lag + 1]
        rx_0 = np.maximum(1e-7, rx[:, 0:1])
        r_norm = rx / rx_0

        search_region = r_norm[:, self.min_lag : self.max_lag + 1]
        best_lags = np.argmax(search_region, axis=1) + self.min_lag
        max_peaks = np.max(search_region, axis=1)

        f0_per_frame = []
        hnr_per_frame = []
        voicing_per_frame = []

        for i in range(n_frames):
            if frame_energies[i] < 1e-7:
                hnr_per_frame.append(-20.0)
                voicing_per_frame.append(0.0)
                f0_per_frame.append(0.0)
                continue

            r_max = float(max_peaks[i])
            voicing_per_frame.append(max(0.0, min(1.0, r_max)))

            # HNR in dB: 10 * log10(R_max / (1 - R_max))
            if r_max >= 0.999:
                hnr_db = 30.0
            elif r_max <= 0.01:
                hnr_db = -20.0
            else:
                hnr_db = float(10.0 * np.log10(r_max / max(1e-6, 1.0 - r_max)))
            hnr_per_frame.append(max(-20.0, min(35.0, hnr_db)))

            if r_max > 0.35:
                f0_hz = float(self.sr / best_lags[i])
                f0_per_frame.append(f0_hz)
            else:
                f0_per_frame.append(0.0)

        hnr_arr = np.array(hnr_per_frame, dtype=np.float32)
        voicing_arr = np.array(voicing_per_frame, dtype=np.float32)
        f0_arr = np.array(f0_per_frame, dtype=np.float32)

        # =====================================================================
        # FAMILY A: Harmonicity and Vocal Turbulence (8 features)
        # =====================================================================
        hnr_mean = float(np.mean(hnr_arr))
        hnr_min = float(np.min(hnr_arr))

        # Subharmonic & Harmonic ratios via power spectrum
        # Subharmonic energy around F0/2 vs F0
        voiced_f0 = f0_arr[f0_arr > 0]
        if len(voiced_f0) > 0:
            median_f0 = float(np.median(voiced_f0))
            f0_bin = int(round(median_f0 / (self.sr / self.n_fft)))
            sub_bin = max(1, int(round(f0_bin / 2.0)))
            f0_bin = min(self.n_fft // 2, max(2, f0_bin))

            sub_energy = float(np.mean(power_spec[:, max(0, sub_bin - 2) : sub_bin + 3]))
            f0_energy = float(np.mean(power_spec[:, max(0, f0_bin - 2) : f0_bin + 3]) + 1e-12)
            subharmonic_ratio = float(sub_energy / f0_energy)

            # Harmonics (2*F0, 3*F0, 4*F0)
            harm_energy = 0.0
            for h_mult in [2, 3, 4]:
                h_bin = int(round(h_mult * f0_bin))
                if h_bin < self.n_fft // 2:
                    harm_energy += float(np.mean(power_spec[:, max(0, h_bin - 2) : h_bin + 3]))
            total_power = float(np.mean(np.sum(power_spec, axis=1)) + 1e-12)
            harmonic_energy_ratio = float(harm_energy / total_power)
        else:
            subharmonic_ratio = 0.0
            harmonic_energy_ratio = 0.0

        # Spectral Flatness: Geometric mean / Arithmetic mean
        power_spec_safe = np.maximum(1e-12, power_spec)
        geo_mean = np.exp(np.mean(np.log(power_spec_safe), axis=1))
        arith_mean = np.mean(power_spec_safe, axis=1)
        flatness_per_frame = geo_mean / (arith_mean + 1e-12)
        spectral_flatness_mean = float(np.mean(flatness_per_frame))
        spectral_flatness_max = float(np.max(flatness_per_frame))

        # Spectral Entropy: Normalized Shannon entropy
        psd_norm = power_spec_safe / np.sum(power_spec_safe, axis=1, keepdims=True)
        entropy_per_frame = -np.sum(psd_norm * np.log2(psd_norm), axis=1) / np.log2(power_spec.shape[1])
        spectral_entropy_mean = float(np.mean(entropy_per_frame))
        spectral_entropy_variance = float(np.var(entropy_per_frame))

        feat_fam_a = [
            hnr_mean,
            hnr_min,
            subharmonic_ratio,
            harmonic_energy_ratio,
            spectral_flatness_mean,
            spectral_flatness_max,
            spectral_entropy_mean,
            spectral_entropy_variance,
        ]

        # =====================================================================
        # FAMILY B: Spectral Dynamics and Formants (8 features)
        # =====================================================================
        # Spectral Centroid & Bandwidth
        sum_power = np.sum(power_spec, axis=1, keepdims=True) + 1e-12
        centroids = np.sum(power_spec * freqs, axis=1, keepdims=True) / sum_power
        bandwidths = np.sqrt(np.sum(power_spec * ((freqs - centroids) ** 2), axis=1, keepdims=True) / sum_power)

        spectral_centroid_mean = float(np.mean(centroids))
        spectral_bandwidth_mean = float(np.mean(bandwidths))

        # Band Energy Ratios
        scream_mask = (freqs >= 1500.0) & (freqs <= 3500.0)
        low_vocal_mask = (freqs < 1000.0)
        high_rolloff_mask = (freqs > 4500.0)

        scream_band_energy = float(np.sum(power_spec[:, scream_mask]))
        low_vocal_energy = float(np.sum(power_spec[:, low_vocal_mask]))
        high_rolloff_energy = float(np.sum(power_spec[:, high_rolloff_mask]))
        total_spec_energy = float(np.sum(power_spec) + 1e-12)

        scream_resonance_ratio = float(scream_band_energy / total_spec_energy)
        low_vocal_energy_ratio = float(low_vocal_energy / total_spec_energy)
        high_freq_rolloff_ratio = float(high_rolloff_energy / total_spec_energy)

        # Spectral Flux: frame-to-frame change in normalized magnitude
        spec_norm = spec / (np.linalg.norm(spec, axis=1, keepdims=True) + 1e-12)
        if n_frames > 1:
            flux_per_frame = np.linalg.norm(np.diff(spec_norm, axis=0), axis=1)
            spectral_flux_mean = float(np.mean(flux_per_frame))
            spectral_flux_max = float(np.max(flux_per_frame))
        else:
            spectral_flux_mean = 0.0
            spectral_flux_max = 0.0

        # Centroid slope across duration
        if n_frames > 2:
            time_axis = np.linspace(0, 1, n_frames)
            centroid_flat = centroids.flatten()
            slope, _ = np.polyfit(time_axis, centroid_flat, 1)
            spectral_centroid_slope = float(slope / 1000.0)  # scale
        else:
            spectral_centroid_slope = 0.0

        feat_fam_b = [
            spectral_centroid_mean,
            spectral_bandwidth_mean,
            scream_resonance_ratio,
            low_vocal_energy_ratio,
            high_freq_rolloff_ratio,
            spectral_flux_mean,
            spectral_flux_max,
            spectral_centroid_slope,
        ]

        # =====================================================================
        # FAMILY C: Temporal Energy and Envelope Dynamics (8 features)
        # =====================================================================
        # High resolution envelope (10 ms frames, 5 ms hop)
        env_frame = int(self.sr * 0.010)
        env_hop = int(self.sr * 0.005)
        n_env = (n_samples - env_frame) // env_hop + 1
        if n_env > 1:
            shape_env = (n_env, env_frame)
            strides_env = (waveform.strides[0] * env_hop, waveform.strides[0])
            env_frames = np.lib.stride_tricks.as_strided(waveform, shape=shape_env, strides=strides_env)
            env_rms = np.sqrt(np.mean(env_frames ** 2, axis=1) + 1e-12)

            peak_idx = int(np.argmax(env_rms))
            peak_val = float(env_rms[peak_idx])

            # Attack time: time from 10% peak to 90% peak
            t_90 = peak_idx * 5.0  # ms
            t_10 = 0.0
            thresh_10 = 0.10 * peak_val
            for j in range(peak_idx, -1, -1):
                if env_rms[j] <= thresh_10:
                    t_10 = j * 5.0
                    break
            attack_time_ms = max(1.0, t_90 - t_10)
            log_attack_time = float(np.log10(attack_time_ms + 1.0))

            # Sustain to peak ratio
            sustain_energy = float(np.mean(env_rms[peak_idx:])) if peak_idx < n_env - 1 else peak_val
            sustain_to_peak_ratio = float(sustain_energy / max(1e-6, peak_val))

            # Max onset gradient (diff in dB/ms)
            env_diff = np.diff(env_rms)
            max_onset_gradient = float(np.max(env_diff) / (peak_val + 1e-6))

            # Decay rate (dB per second from peak to end)
            if peak_idx < n_env - 2:
                time_after_peak = (n_env - peak_idx) * 0.005  # sec
                end_val = float(np.mean(env_rms[-3:]))
                decay_db = 20.0 * np.log10(max(1e-4, peak_val) / max(1e-4, end_val))
                decay_rate_db_per_sec = float(decay_db / max(0.05, time_after_peak))
            else:
                decay_rate_db_per_sec = 0.0

            # Burst continuity: fraction of frames within 10 dB of peak
            thresh_10db = peak_val * 0.3162
            burst_continuity_ratio = float(np.mean(env_rms >= thresh_10db))
        else:
            log_attack_time = 1.0
            sustain_to_peak_ratio = 1.0
            max_onset_gradient = 0.0
            decay_rate_db_per_sec = 0.0
            burst_continuity_ratio = 1.0

        # Crest Factor & Kurtosis
        peak_amp = float(np.max(np.abs(waveform)))
        envelope_crest_factor = float(peak_amp / (rms_global + 1e-6))

        centered = waveform - np.mean(waveform)
        m4 = np.mean(centered ** 4)
        m2 = np.mean(centered ** 2) + 1e-12
        envelope_kurtosis = float(m4 / (m2 ** 2) - 3.0)

        energy_temporal_std = float(np.std(frame_energies) / (np.mean(frame_energies) + 1e-6))

        feat_fam_c = [
            log_attack_time,
            sustain_to_peak_ratio,
            envelope_crest_factor,
            envelope_kurtosis,
            max_onset_gradient,
            decay_rate_db_per_sec,
            energy_temporal_std,
            burst_continuity_ratio,
        ]

        # =====================================================================
        # FAMILY D: Pitch and Voicing Irregularity (6 features)
        # =====================================================================
        if len(voiced_f0) > 0:
            f0_mean_hz = float(np.mean(voiced_f0))
            f0_max_hz = float(np.max(voiced_f0))
            f0_std_hz = float(np.std(voiced_f0))
            pitch_cv = float(f0_std_hz / (f0_mean_hz + 1e-5))

            # Pitch jitter: relative period perturbation
            if len(voiced_f0) > 2:
                periods = 1.0 / voiced_f0
                jitter = float(np.mean(np.abs(np.diff(periods))) / (np.mean(periods) + 1e-6))
            else:
                jitter = 0.0
        else:
            f0_mean_hz = 0.0
            f0_max_hz = 0.0
            pitch_cv = 0.0
            jitter = 0.0

        voicing_confidence = float(np.mean(voicing_arr))

        # Pitch breaks: transitions between voiced and unvoiced
        voiced_binary = (f0_arr > 0).astype(int)
        if len(voiced_binary) > 1:
            pitch_break_rate = float(np.mean(np.abs(np.diff(voiced_binary))))
        else:
            pitch_break_rate = 0.0

        feat_fam_d = [
            f0_mean_hz,
            f0_max_hz,
            pitch_cv,
            voicing_confidence,
            jitter,
            pitch_break_rate,
        ]

        # Combined 30-dim vector
        all_features = feat_fam_a + feat_fam_b + feat_fam_c + feat_fam_d
        vec = np.nan_to_num(np.array(all_features, dtype=np.float32), nan=0.0, posinf=1e4, neginf=-1e4)
        return vec

    def extract_family(self, waveform: np.ndarray, family: str) -> np.ndarray:
        """Extract a specific feature family: 'A', 'B', 'C', or 'D'."""
        full_vec = self.extract_features(waveform)
        if family.upper() == "A":
            return full_vec[:8]
        elif family.upper() == "B":
            return full_vec[8:16]
        elif family.upper() == "C":
            return full_vec[16:24]
        elif family.upper() == "D":
            return full_vec[24:30]
        else:
            raise ValueError(f"Unknown family: {family}")
