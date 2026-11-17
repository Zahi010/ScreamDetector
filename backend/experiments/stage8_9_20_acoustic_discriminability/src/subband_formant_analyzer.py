"""
Stage 8.9.20: Sub-Band Formant Analyzer, Pitch Perturbation & Turbulence Extractor
Computes:
1. Pitch & Pitch Perturbation: F0 median, variance, range, Jitter, Shimmer, Voicing probability, Pitch failure flag.
2. Harmonic & Formant Structure: LPC formants F1, F2, F3, Formant dispersion, HNR, Spectral Flatness.
3. Sub-Band Turbulence: 4 frequency bands (<1k, 1-2.5k, 2.5-6k, >6k) energy ratios, modulation, turbulence persistence.
"""

import os
import wave
import numpy as np
from scipy.signal import lfilter

class SubBandFormantAnalyzer:
    def __init__(self, sample_rate: int = 16000):
        self.sr = sample_rate
        self.frame_len = int(0.040 * self.sr)  # 40ms = 640 samples
        self.hop_len = int(0.010 * self.sr)    # 10ms = 160 samples
        self.lpc_order = 18                    # 2 + 16 (for 16 kHz)

    def extract_features(self, audio: np.ndarray) -> np.ndarray:
        """
        Extracts 24-dimensional sub-band formant, pitch perturbation & turbulence vector.
        """
        if len(audio) < self.frame_len:
            pad = np.zeros(self.frame_len - len(audio), dtype=np.float32)
            audio = np.concatenate([audio, pad])

        # Normalize audio safely
        peak = np.max(np.abs(audio))
        if peak > 1e-6:
            audio = audio / peak

        # Frame audio
        n_frames = max(1, int((len(audio) - self.frame_len) / self.hop_len) + 1)
        frames = []
        for i in range(n_frames):
            start = i * self.hop_len
            frames.append(audio[start:start + self.frame_len])
        frames = np.array(frames)

        # -------------------------------------------------------------
        # 1. Pitch & Pitch Perturbation (Autocorrelation F0, Jitter, Shimmer)
        # -------------------------------------------------------------
        f0_list = []
        amp_list = []
        voiced_frames = 0
        min_lag = int(self.sr / 1000.0) # max pitch 1000 Hz -> 16 samples
        max_lag = int(self.sr / 80.0)   # min pitch 80 Hz -> 200 samples

        # Process every 2nd frame for real-time efficiency (20ms step)
        pitch_frames = frames[::2]
        for f in pitch_frames:
            w_frame = f * np.hamming(len(f))
            amp = np.max(np.abs(w_frame))
            amp_list.append(amp)

            acorr = np.correlate(w_frame, w_frame, mode='full')
            acorr = acorr[len(w_frame) - 1:]

            if acorr[0] > 1e-6:
                norm_acorr = acorr / acorr[0]
                search_region = norm_acorr[min_lag:max_lag]
                if len(search_region) > 0:
                    peak_idx = np.argmax(search_region) + min_lag
                    peak_val = norm_acorr[peak_idx]
                    if peak_val > 0.40:
                        pitch = self.sr / float(peak_idx)
                        f0_list.append(pitch)
                        voiced_frames += 1
                    else:
                        f0_list.append(0.0)
                else:
                    f0_list.append(0.0)
            else:
                f0_list.append(0.0)

        f0_arr = np.array(f0_list)
        voiced_mask = f0_arr > 0
        p_voiced = voiced_frames / max(1.0, float(len(pitch_frames)))

        if np.sum(voiced_mask) > 3:
            v_f0 = f0_arr[voiced_mask]
            f0_median = float(np.median(v_f0))
            f0_std = float(np.std(v_f0))
            f0_range = float(np.max(v_f0) - np.min(v_f0))

            periods = 1.0 / (v_f0 + 1e-6)
            diff_p = np.abs(np.diff(periods))
            jitter = float(np.mean(diff_p) / (np.mean(periods) + 1e-6))

            v_amps = np.array(amp_list)[voiced_mask]
            diff_a = np.abs(np.diff(v_amps))
            shimmer = float(np.mean(diff_a) / (np.mean(v_amps) + 1e-6))
            pitch_failure = 0.0
        else:
            f0_median = 0.0
            f0_std = 0.0
            f0_range = 0.0
            jitter = 0.0
            shimmer = 0.0
            pitch_failure = 1.0

        # -------------------------------------------------------------
        # 2. Harmonic & Formant Structure (LPC F1, F2, F3, HNR)
        # Subsample every 8th frame (~80ms step, 12 frames per sec) for real-time budget
        # -------------------------------------------------------------
        f1_list, f2_list, f3_list = [], [], []
        lpc_frames = frames[::8]

        for f in lpc_frames:
            if np.max(np.abs(f)) < 1e-4:
                continue
            pe_frame = lfilter([1.0, -0.97], [1.0], f * np.hamming(len(f)))
            r = np.correlate(pe_frame, pe_frame, mode='full')
            r = r[len(pe_frame)-1: len(pe_frame) + self.lpc_order + 1]
            if r[0] < 1e-6:
                continue

            try:
                a = np.zeros(self.lpc_order + 1)
                a[0] = 1.0
                e = r[0]
                for k in range(1, self.lpc_order + 1):
                    lam = -np.sum(a[:k] * r[k:0:-1]) / (e + 1e-8)
                    a[1:k+1] += lam * a[k-1::-1]
                    e *= (1.0 - lam ** 2)

                roots = np.roots(a)
                roots = roots[np.iscomplex(roots)]
                roots = roots[np.imag(roots) > 0]
                angles = np.angle(roots)
                freqs = sorted(angles * (self.sr / (2.0 * np.pi)))

                cand_f1 = [fr for fr in freqs if 250 <= fr <= 1200]
                cand_f2 = [fr for fr in freqs if 1000 <= fr <= 3000]
                cand_f3 = [fr for fr in freqs if 2000 <= fr <= 4500]

                if cand_f1: f1_list.append(cand_f1[0])
                if cand_f2: f2_list.append(cand_f2[0])
                if cand_f3: f3_list.append(cand_f3[0])
            except Exception:
                pass

        f1_mean = float(np.mean(f1_list)) if f1_list else 0.0
        f2_mean = float(np.mean(f2_list)) if f2_list else 0.0
        f3_mean = float(np.mean(f3_list)) if f3_list else 0.0
        f1_std = float(np.std(f1_list)) if len(f1_list) > 1 else 0.0
        f2_std = float(np.std(f2_list)) if len(f2_list) > 1 else 0.0
        formant_dispersion = float(f2_mean - f1_mean) if (f1_mean > 0 and f2_mean > 0) else 0.0

        # Harmonic-to-Noise Ratio (HNR)
        full_acorr = np.correlate(audio, audio, mode='full')
        full_acorr = full_acorr[len(audio)-1:]
        if full_acorr[0] > 1e-6 and len(full_acorr) > max_lag:
            peak_val = np.max(full_acorr[min_lag:max_lag])
            harm_ratio = peak_val / (full_acorr[0] + 1e-8)
            hnr_db = float(10.0 * np.log10(max(harm_ratio / (1.0 - harm_ratio + 1e-6), 1e-4)))
        else:
            hnr_db = -10.0

        # Spectral Flatness
        fft_mag = np.abs(np.fft.rfft(audio * np.hamming(len(audio))))
        fft_pow = fft_mag ** 2 + 1e-12
        geom_mean = np.exp(np.mean(np.log(fft_pow)))
        arith_mean = np.mean(fft_pow)
        spectral_flatness = float(geom_mean / (arith_mean + 1e-12))

        # -------------------------------------------------------------
        # 3. Sub-Band Turbulence (4 Frequency Bands)
        # -------------------------------------------------------------
        freqs = np.fft.rfftfreq(len(audio), 1.0 / self.sr)
        b1_mask = (freqs < 1000)
        b2_mask = (freqs >= 1000) & (freqs < 2500)
        b3_mask = (freqs >= 2500) & (freqs < 6000)
        b4_mask = (freqs >= 6000)

        e_total = np.sum(fft_pow) + 1e-12
        e1 = float(np.sum(fft_pow[b1_mask]) / e_total)
        e2 = float(np.sum(fft_pow[b2_mask]) / e_total)
        e3 = float(np.sum(fft_pow[b3_mask]) / e_total)
        e4 = float(np.sum(fft_pow[b4_mask]) / e_total)

        # High-to-Low ratio: (Band3 + Band4) / (Band1 + Band2)
        high_low_ratio = float((e3 + e4) / (e1 + e2 + 1e-6))
        turbulence_ratio = float(e4 / (e_total + 1e-6))

        # Sub-band temporal modulation (variance across frames)
        frame_e3 = []
        frame_e4 = []
        for f in frames:
            f_pow = np.abs(np.fft.rfft(f * np.hamming(len(f)))) ** 2
            f_freqs = np.fft.rfftfreq(len(f), 1.0 / self.sr)
            f_tot = np.sum(f_pow) + 1e-12
            frame_e3.append(np.sum(f_pow[(f_freqs >= 2500) & (f_freqs < 6000)]) / f_tot)
            frame_e4.append(np.sum(f_pow[f_freqs >= 6000]) / f_tot)

        turb_mod_b3 = float(np.std(frame_e3))
        turb_mod_b4 = float(np.std(frame_e4))
        turb_persistence = float(np.mean(frame_e4))

        # Construct 24-dimensional feature vector
        features = np.array([
            # 1. Pitch & Perturbation (7 features)
            f0_median, f0_std, f0_range, jitter, shimmer, p_voiced, pitch_failure,
            # 2. Formants & Harmonics (9 features)
            f1_mean, f1_std, f2_mean, f2_std, f3_mean, formant_dispersion, hnr_db, spectral_flatness,
            (f1_mean / (f2_mean + 1e-6)),
            # 3. Sub-Band Turbulence (8 features)
            e1, e2, e3, e4, high_low_ratio, turbulence_ratio, turb_mod_b3, turb_persistence
        ], dtype=np.float32)

        return features

    @property
    def feature_names(self):
        return [
            "f0_median", "f0_std", "f0_range", "jitter", "shimmer", "p_voiced", "pitch_failure_flag",
            "f1_mean", "f1_std", "f2_mean", "f2_std", "f3_mean", "formant_dispersion", "hnr_db", "spectral_flatness", "f1_f2_ratio",
            "band1_energy_lt1k", "band2_energy_1k_2_5k", "band3_energy_2_5k_6k", "band4_energy_gt6k",
            "high_low_subband_ratio", "turbulence_ratio_gt6k", "turbulence_modulation_b3", "turbulence_persistence_b4"
        ]
