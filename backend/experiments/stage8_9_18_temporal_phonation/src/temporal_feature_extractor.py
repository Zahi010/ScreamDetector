"""High-Throughput Temporal Phonation, Syllabic Cadence & Sub-band Turbulence Feature Extractor (Stage 8.9.18).

Specifically addresses Shout-vs-Scream discrimination by quantifying:
- Hypothesis A (Phonation continuity): Screams exhibit continuous open-vocal-tract phonation; shouting consists of segmented syllabic bursts.
- Hypothesis B (Vocal closure gaps): Shouting contains frequent consonant closure gaps (30-150ms); screams do not.
- Hypothesis C (Temporal energy modulation): Rapid attack times and sustained envelope plateaus vs speech modulation.
- Hypothesis D (Sub-band turbulence): Stable high-frequency turbulence (>2.5 kHz and >6.0 kHz) vs fluctuating speech formants.

Provides 32 handcrafted temporal features across 4 distinct functional families for ablation:
- Family A (7 dims): Phonation Continuity & Vocal Closures
- Family B (6 dims): Sub-band Turbulence & Spectral Ratios
- Family C (7 dims): Temporal Energy & Envelope Modulation
- Family D (12 dims): Spectral Dynamics & Transition Flux
"""

from __future__ import annotations

import logging
import math
from typing import Dict, List, Tuple

import numpy as np
from scipy import signal

logger = logging.getLogger("temporal_extractor")

TARGET_SAMPLE_RATE = 16000

TEMPORAL_FEATURE_NAMES = [
    # Family C: Temporal Energy & Envelope Modulation (7)
    "rms_energy_mean",
    "rms_energy_std",
    "energy_modulation_depth",
    "log_attack_time_ms",
    "temporal_crest_factor_db",
    "energy_decay_rate",
    "temporal_centroid",
    # Family D: Spectral Dynamics & Transition Flux (12)
    "spectral_centroid_mean",
    "spectral_centroid_std",
    "spectral_centroid_velocity",
    "spectral_bandwidth_mean",
    "spectral_bandwidth_std",
    "spectral_flux_mean",
    "spectral_flux_std",
    "spectral_flatness_mean",
    "spectral_flatness_std",
    "spectral_rolloff_85_mean",
    "zero_crossing_rate_mean",
    "zero_crossing_rate_std",
    # Family A: Phonation Continuity & Vocal Closures (7)
    "voiced_frame_ratio",
    "max_continuous_voiced_sec",
    "mean_voiced_segment_sec",
    "vocal_closure_gap_count",
    "closure_gap_frequency_hz",
    "mean_closure_gap_ms",
    "closure_to_voiced_ratio",
    # Family B: Sub-band Turbulence & Spectral Ratios (6)
    "subband_low_ratio",
    "subband_mid_ratio",
    "subband_high_ratio",
    "subband_turbulence_ratio",
    "high_to_low_band_ratio",
    "turbulence_temporal_modulation",
]


class TemporalPhonationExtractor:
    """Vectorized high-throughput temporal phonation and acoustic feature extractor."""

    def __init__(self, sr: int = TARGET_SAMPLE_RATE):
        self.sr = sr
        self.frame_len = 1024  # 64 ms at 16 kHz
        self.hop_len = 512     # 32 ms hop (50% overlap)
        self.n_fft = 1024
        self.window = signal.windows.hann(self.frame_len, sym=False).astype(np.float32)

        # Autocorrelation lag bounds for human pitch (80 Hz to 1200 Hz)
        self.min_lag = int(sr / 1200)  # ~13 samples
        self.max_lag = int(sr / 80)    # ~200 samples

        # Frequency bin indices for sub-band analysis
        freqs = np.fft.rfftfreq(self.n_fft, d=1.0 / self.sr)
        self.idx_low = np.where(freqs < 800.0)[0]
        self.idx_mid = np.where((freqs >= 800.0) & (freqs < 2500.0))[0]
        self.idx_high = np.where((freqs >= 2500.0) & (freqs < 6000.0))[0]
        self.idx_turb = np.where(freqs >= 6000.0)[0]
        self.freqs = freqs

    def extract_temporal_features(self, waveform: np.ndarray) -> np.ndarray:
        """Extract complete 32-dim temporal feature vector from audio buffer."""
        # Sanitize waveform: remove DC offset and handle non-finite
        wf = np.nan_to_num(waveform, nan=0.0, posinf=1.0, neginf=-1.0).astype(np.float32)
        wf = wf - np.mean(wf)
        n_samples = len(wf)

        # Handle extreme silence or ultra-short buffers safely
        if n_samples < 320 or float(np.sqrt(np.mean(wf ** 2) + 1e-12)) < 1e-6:
            return np.zeros(32, dtype=np.float32)

        # Pad short buffers to at least one frame
        if n_samples < self.frame_len:
            wf = np.pad(wf, (0, self.frame_len - n_samples), mode="constant")
            n_samples = len(wf)

        duration_sec = max(0.02, n_samples / self.sr)

        # Stride framing for fast vectorized frame analysis
        n_frames = (n_samples - self.frame_len) // self.hop_len + 1
        shape = (n_frames, self.frame_len)
        strides = (wf.strides[0] * self.hop_len, wf.strides[0])
        frames = np.lib.stride_tricks.as_strided(wf, shape=shape, strides=strides)

        # Apply Hann window
        windowed = frames * self.window

        # ---------------------------------------------------------------------
        # 1. Short-Time Frame Energy & Temporal Envelope (Family C)
        # ---------------------------------------------------------------------
        frame_rms = np.sqrt(np.mean(windowed ** 2, axis=1) + 1e-12)
        rms_mean = float(np.mean(frame_rms))
        rms_std = float(np.std(frame_rms))
        rms_max = float(np.max(frame_rms))
        rms_min = float(np.min(frame_rms))
        energy_mod_depth = float((rms_max - rms_min) / (rms_mean + 1e-6))

        # Peak and temporal crest factor
        peak_amp = float(np.max(np.abs(wf)))
        temporal_crest_db = 20.0 * math.log10(max(peak_amp, 1e-6) / max(rms_mean, 1e-6))

        # Log Attack Time: time from 10% to 90% peak envelope rise
        idx_max = int(np.argmax(frame_rms))
        thresh_10 = 0.10 * rms_max
        thresh_90 = 0.90 * rms_max
        pre_peak = frame_rms[: idx_max + 1]
        i10 = int(np.where(pre_peak >= thresh_10)[0][0]) if np.any(pre_peak >= thresh_10) else 0
        i90 = int(np.where(pre_peak >= thresh_90)[0][0]) if np.any(pre_peak >= thresh_90) else idx_max
        attack_time_ms = max(1.0, (i90 - i10) * (self.hop_len / self.sr) * 1000.0)
        log_attack_time = float(math.log10(attack_time_ms))

        # Energy Decay Rate: decay slope after peak
        post_peak = frame_rms[idx_max:]
        if len(post_peak) > 1:
            decay_rate = float((post_peak[0] - post_peak[-1]) / max(0.01, len(post_peak) * (self.hop_len / self.sr)))
        else:
            decay_rate = 0.0

        # Temporal Centroid (center of mass of energy envelope normalized to [0, 1])
        t_axis = np.linspace(0.0, 1.0, n_frames)
        total_energy = float(np.sum(frame_rms) + 1e-12)
        temporal_centroid = float(np.sum(t_axis * frame_rms) / total_energy)

        feat_family_c = [
            rms_mean,
            rms_std,
            energy_mod_depth,
            log_attack_time,
            temporal_crest_db,
            decay_rate,
            temporal_centroid,
        ]

        # ---------------------------------------------------------------------
        # 2. STFT Spectral Dynamics & Transition Flux (Family D)
        # ---------------------------------------------------------------------
        spec = np.abs(np.fft.rfft(windowed, n=self.n_fft, axis=1))  # (n_frames, 513)
        power_spec = spec ** 2
        spec_sum = np.sum(spec, axis=1, keepdims=True) + 1e-12
        norm_spec = spec / spec_sum

        # Spectral Centroid
        centroids = np.sum(norm_spec * self.freqs, axis=1)
        centroid_mean = float(np.mean(centroids))
        centroid_std = float(np.std(centroids))
        centroid_velocity = float(np.mean(np.abs(np.diff(centroids)))) if len(centroids) > 1 else 0.0

        # Spectral Bandwidth
        bandwidths = np.sqrt(np.sum(norm_spec * ((self.freqs - centroids[:, None]) ** 2), axis=1) + 1e-12)
        bandwidth_mean = float(np.mean(bandwidths))
        bandwidth_std = float(np.std(bandwidths))

        # Spectral Flux (Euclidean distance between adjacent normalized magnitude spectra)
        if n_frames > 1:
            flux_frames = np.sqrt(np.sum(np.diff(norm_spec, axis=0) ** 2, axis=1))
            flux_mean = float(np.mean(flux_frames))
            flux_std = float(np.std(flux_frames))
        else:
            flux_mean, flux_std = 0.0, 0.0

        # Spectral Flatness (Wiener entropy: geometric mean / arithmetic mean)
        geom_mean = np.exp(np.mean(np.log(power_spec + 1e-12), axis=1))
        arith_mean = np.mean(power_spec, axis=1) + 1e-12
        flatness_frames = geom_mean / arith_mean
        flatness_mean = float(np.mean(flatness_frames))
        flatness_std = float(np.std(flatness_frames))

        # Spectral Rolloff 85%
        cum_power = np.cumsum(power_spec, axis=1)
        total_p = cum_power[:, -1:]
        thresh_85 = 0.85 * total_p
        rolloff_idx = np.argmax(cum_power >= thresh_85, axis=1)
        rolloff_mean = float(np.mean(self.freqs[rolloff_idx]))

        # Zero-Crossing Rate across frames
        zcr_frames = np.mean(np.abs(np.diff(np.sign(frames), axis=1)), axis=1) * 0.5
        zcr_mean = float(np.mean(zcr_frames))
        zcr_std = float(np.std(zcr_frames))

        feat_family_d = [
            centroid_mean,
            centroid_std,
            centroid_velocity,
            bandwidth_mean,
            bandwidth_std,
            flux_mean,
            flux_std,
            flatness_mean,
            flatness_std,
            rolloff_mean,
            zcr_mean,
            zcr_std,
        ]

        # ---------------------------------------------------------------------
        # 3. Phonation Continuity & Vocal Closure Gaps (Family A)
        # ---------------------------------------------------------------------
        # Vectorized normalized autocorrelation for pitch tracking
        # We compute autocorrelation via FFT of windowed frames
        n_fft_ac = 2048
        spec_ac = np.fft.rfft(windowed, n=n_fft_ac, axis=1)
        rx = np.fft.irfft(spec_ac * np.conj(spec_ac), n=n_fft_ac, axis=1)[:, : self.max_lag + 1]
        r0 = np.maximum(1e-7, rx[:, 0:1])
        r_norm = rx / r0

        search_lags = r_norm[:, self.min_lag : self.max_lag + 1]
        max_peaks = np.max(search_lags, axis=1)

        # Voiced threshold: correlation peak >= 0.28 AND frame RMS >= 0.05 * rms_max
        voicing_thresh = 0.28
        energy_gate = 0.05 * rms_max
        is_voiced = (max_peaks >= voicing_thresh) & (frame_rms >= energy_gate)
        voiced_ratio = float(np.mean(is_voiced))

        # Phonation segment analysis: run-length encoding of voiced frames
        voiced_int = is_voiced.astype(int)
        runs = []
        gaps = []
        current_state = voiced_int[0]
        current_len = 1

        for s in voiced_int[1:]:
            if s == current_state:
                current_len += 1
            else:
                if current_state == 1:
                    runs.append(current_len)
                else:
                    gaps.append(current_len)
                current_state = s
                current_len = 1
        if current_state == 1:
            runs.append(current_len)
        else:
            gaps.append(current_len)

        frame_duration_sec = self.hop_len / self.sr  # 0.032s = 32ms

        if runs:
            max_continuous_voiced_sec = float(max(runs) * frame_duration_sec)
            mean_voiced_segment_sec = float(np.mean(runs) * frame_duration_sec)
        else:
            max_continuous_voiced_sec = 0.0
            mean_voiced_segment_sec = 0.0

        # Closure gaps: unvoiced segments between voiced runs with length between 30ms and 200ms
        closure_gaps = [g for g in gaps if 1 <= g <= 6]  # 32ms to ~192ms
        closure_gap_count = len(closure_gaps)
        closure_gap_freq_hz = float(closure_gap_count / duration_sec)
        mean_closure_gap_ms = float(np.mean(closure_gaps) * frame_duration_sec * 1000.0) if closure_gaps else 0.0

        total_closure_time = float(sum(closure_gaps) * frame_duration_sec) if closure_gaps else 0.0
        total_voiced_time = float(sum(runs) * frame_duration_sec) if runs else 0.0
        closure_to_voiced_ratio = float(total_closure_time / max(0.01, total_voiced_time))

        feat_family_a = [
            voiced_ratio,
            max_continuous_voiced_sec,
            mean_voiced_segment_sec,
            float(closure_gap_count),
            closure_gap_freq_hz,
            mean_closure_gap_ms,
            closure_to_voiced_ratio,
        ]

        # ---------------------------------------------------------------------
        # 4. Sub-band Turbulence & Spectral Modulation (Family B)
        # ---------------------------------------------------------------------
        e_total = np.sum(power_spec, axis=1) + 1e-12
        e_low = np.sum(power_spec[:, self.idx_low], axis=1)
        e_mid = np.sum(power_spec[:, self.idx_mid], axis=1)
        e_high = np.sum(power_spec[:, self.idx_high], axis=1)
        e_turb = np.sum(power_spec[:, self.idx_turb], axis=1)

        subband_low_ratio = float(np.mean(e_low / e_total))
        subband_mid_ratio = float(np.mean(e_mid / e_total))
        subband_high_ratio = float(np.mean(e_high / e_total))
        subband_turb_ratio = float(np.mean(e_turb / e_total))

        high_low_frame_ratios = e_high / (e_low + 1e-6)
        high_to_low_band_ratio = float(np.mean(high_low_frame_ratios))
        turb_temporal_mod = float(np.std(high_low_frame_ratios))

        feat_family_b = [
            subband_low_ratio,
            subband_mid_ratio,
            subband_high_ratio,
            subband_turb_ratio,
            high_to_low_band_ratio,
            turb_temporal_mod,
        ]

        # Assemble full 32-dimensional vector: C (7) + D (12) + A (7) + B (6)
        full_vec = feat_family_c + feat_family_d + feat_family_a + feat_family_b
        return np.nan_to_num(np.array(full_vec, dtype=np.float32), nan=0.0, posinf=1e4, neginf=-1e4)

    def extract_family(self, waveform: np.ndarray, family: str) -> np.ndarray:
        """Extract a specific temporal feature family for ablation experiments."""
        full = self.extract_temporal_features(waveform)
        # Indices:
        # C: 0..6 (7)
        # D: 7..18 (12)
        # A: 19..25 (7)
        # B: 26..31 (6)
        fam = family.upper()
        if fam == "C":
            return full[:7]
        elif fam == "D":
            return full[7:19]
        elif fam == "A":
            return full[19:26]
        elif fam == "B":
            return full[26:32]
        else:
            raise ValueError(f"Unknown temporal family: {family}")

    def extract_short_time_feature_sequence(self, waveform: np.ndarray, max_frames: int = 70) -> np.ndarray:
        """Extract short-time 16-dim temporal feature sequence for 1D Temporal CNN (Model B)."""
        wf = np.nan_to_num(waveform, nan=0.0, posinf=1.0, neginf=-1.0).astype(np.float32)
        wf = wf - np.mean(wf)
        n_samples = len(wf)

        seq = np.zeros((max_frames, 16), dtype=np.float32)
        if n_samples < 320 or float(np.sqrt(np.mean(wf ** 2) + 1e-12)) < 1e-6:
            return seq

        if n_samples < self.frame_len:
            wf = np.pad(wf, (0, self.frame_len - n_samples), mode="constant")
            n_samples = len(wf)

        n_frames = min((n_samples - self.frame_len) // self.hop_len + 1, max_frames)
        shape = (n_frames, self.frame_len)
        strides = (wf.strides[0] * self.hop_len, wf.strides[0])
        frames = np.lib.stride_tricks.as_strided(wf, shape=shape, strides=strides)

        windowed = frames * self.window

        # 1. RMS (1)
        rms = np.sqrt(np.mean(windowed ** 2, axis=1) + 1e-12)

        # 2. Spectrum (Centroid, Bandwidth, Flatness, 4 Sub-bands = 7)
        spec = np.abs(np.fft.rfft(windowed, n=self.n_fft, axis=1))
        p_spec = spec ** 2
        spec_sum = np.sum(spec, axis=1, keepdims=True) + 1e-12
        norm_s = spec / spec_sum

        centroid = np.sum(norm_s * self.freqs, axis=1)
        bandwidth = np.sqrt(np.sum(norm_s * ((self.freqs - centroid[:, None]) ** 2), axis=1) + 1e-12)

        geom_m = np.exp(np.mean(np.log(p_spec + 1e-12), axis=1))
        arith_m = np.mean(p_spec, axis=1) + 1e-12
        flatness = geom_m / arith_m

        e_tot = np.sum(p_spec, axis=1) + 1e-12
        r_low = np.sum(p_spec[:, self.idx_low], axis=1) / e_tot
        r_mid = np.sum(p_spec[:, self.idx_mid], axis=1) / e_tot
        r_high = np.sum(p_spec[:, self.idx_high], axis=1) / e_tot
        r_turb = np.sum(p_spec[:, self.idx_turb], axis=1) / e_tot

        # 3. ZCR (1)
        zcr = np.mean(np.abs(np.diff(np.sign(frames), axis=1)), axis=1) * 0.5

        # 4. Voicing correlation peak (1)
        spec_ac = np.fft.rfft(windowed, n=2048, axis=1)
        rx = np.fft.irfft(spec_ac * np.conj(spec_ac), n=2048, axis=1)[:, : self.max_lag + 1]
        r_norm = rx / np.maximum(1e-7, rx[:, 0:1])
        v_peak = np.max(r_norm[:, self.min_lag : self.max_lag + 1], axis=1)

        # 5. Flux (1)
        flux = np.zeros(n_frames, dtype=np.float32)
        if n_frames > 1:
            flux[1:] = np.sqrt(np.sum(np.diff(norm_s, axis=0) ** 2, axis=1))

        # 6. Deltas of centroid, rms, high ratio (3)
        d_centroid = np.gradient(centroid)
        d_rms = np.gradient(rms)
        d_high = np.gradient(r_high)

        # 7. Crest (1)
        crest = np.max(np.abs(frames), axis=1) / (rms + 1e-6)

        feats_16 = np.column_stack([
            rms, centroid, bandwidth, flatness, r_low, r_mid, r_high, r_turb,
            zcr, v_peak, flux, d_centroid, d_rms, d_high, crest,
            np.log1p(np.maximum(0.0, r_high / (r_low + 1e-6)))
        ]).astype(np.float32)

        seq[:n_frames, :] = feats_16
        return seq


if __name__ == "__main__":
    extractor = TemporalPhonationExtractor()
    dummy = (np.random.randn(16000) * 0.1).astype(np.float32)
    feats = extractor.extract_temporal_features(dummy)
    print("Extracted temporal features shape:", feats.shape)
    assert len(feats) == 32
    print("Features sample:", feats[:8])
    seq = extractor.extract_short_time_feature_sequence(dummy, max_frames=70)
    print("Extracted feature sequence shape:", seq.shape)
    assert seq.shape == (70, 16)
    print("Temporal feature extractor validated successfully!")
