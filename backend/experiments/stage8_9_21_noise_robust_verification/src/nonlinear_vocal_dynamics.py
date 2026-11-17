"""
Stage 8.9.21 - Experiment A: Nonlinear Vocal Dynamics Feature Extractor
Extracts:
1. Subharmonic-to-Harmonic Ratio (SHR): F0/2 and F0/3 subharmonic energy vs harmonic energy.
2. Pitch Tracking Failure & Reliability: Valid %, invalid %, unvoiced %, discontinuity rate,
   tracking failure duration, and phonation-vs-noise failure distinction.
3. Harmonic-to-Noise Ratio (HNR): Standardized autocorrelation/cepstral method.
4. Formant Dispersion (F2 - F1) with LPC estimation confidence & missingness flag.
5. Pitch Stability & Variation: Pitch CV (std / mean).
6. Harmonic Instability: Frame-to-frame HNR delta variance.
7. Frequency Modulation (FM): Modulation depth in 20-80 Hz flutter band.
8. Amplitude Modulation (AM): Envelope flutter in 20-80 Hz band.
9. Spectral Flatness & Spectral Entropy.
10. Temporal Vocal Attack & Decay: tau_attack, tau_decay, crest factor.
"""

from __future__ import annotations

import logging
import math
import numpy as np
from scipy.signal import lfilter, find_peaks

logger = logging.getLogger("nonlinear_vocal_dynamics")

class NonlinearVocalDynamicsExtractor:
    def __init__(self, sample_rate: int = 16000):
        self.sr = sample_rate
        self.frame_len = int(0.040 * self.sr)  # 40ms = 640 samples
        self.hop_len = int(0.010 * self.sr)    # 10ms = 160 samples
        self.lpc_order = 18                    # 2 + 16 (for 16 kHz)

    def extract_features(self, audio: np.ndarray) -> np.ndarray:
        """
        Extracts 28-dimensional nonlinear vocal dynamics descriptor vector.
        """
        if len(audio) < self.frame_len:
            audio = np.pad(audio, (0, self.frame_len - len(audio)))

        # Normalize
        peak = np.max(np.abs(audio))
        if peak > 1e-6:
            audio = audio / peak

        # Frame audio
        n_frames = max(1, int((len(audio) - self.frame_len) / self.hop_len) + 1)
        frames = [audio[i * self.hop_len : i * self.hop_len + self.frame_len] for i in range(n_frames)]
        frames = np.array(frames)

        # -------------------------------------------------------------
        # 1. Fundamental Frequency & Frame-by-Frame Pitch Tracking
        # -------------------------------------------------------------
        min_lag = int(self.sr / 1000.0) # 1000 Hz ceiling -> 16 samples
        max_lag = int(self.sr / 80.0)   # 80 Hz floor -> 200 samples

        f0_list = []
        conf_list = []
        rms_list = []
        unvoiced_count = 0
        invalid_count = 0
        valid_count = 0

        for f in frames:
            w = f * np.hamming(len(f))
            f_rms = np.sqrt(np.mean(f**2)) + 1e-12
            rms_list.append(f_rms)

            if f_rms < 1e-4:
                unvoiced_count += 1
                f0_list.append(0.0)
                conf_list.append(0.0)
                continue

            # Normalized Autocorrelation
            acorr = np.correlate(w, w, mode='full')[len(w) - 1:]
            if acorr[0] > 1e-6:
                norm_acorr = acorr / acorr[0]
                search = norm_acorr[min_lag:max_lag]
                if len(search) > 0:
                    peak_idx = np.argmax(search) + min_lag
                    peak_val = float(norm_acorr[peak_idx])
                    conf_list.append(peak_val)
                    if peak_val >= 0.40:
                        pitch = self.sr / float(peak_idx)
                        f0_list.append(pitch)
                        valid_count += 1
                    else:
                        invalid_count += 1
                        f0_list.append(0.0)
                else:
                    invalid_count += 1
                    f0_list.append(0.0)
                    conf_list.append(0.0)
            else:
                invalid_count += 1
                f0_list.append(0.0)
                conf_list.append(0.0)

        f0_arr = np.array(f0_list)
        conf_arr = np.array(conf_list)
        rms_arr = np.array(rms_list)

        valid_pitch_ratio = float(valid_count / n_frames)
        invalid_pitch_ratio = float(invalid_count / n_frames)
        unvoiced_ratio = float(unvoiced_count / n_frames)
        mean_pitch_conf = float(np.mean(conf_arr))

        # Longest continuous pitch tracking failure (ms)
        is_failed = (f0_arr == 0).astype(int)
        longest_failure_frames = 0
        cur_fail = 0
        for v in is_failed:
            if v == 1:
                cur_fail += 1
                if cur_fail > longest_failure_frames:
                    longest_failure_frames = cur_fail
            else:
                cur_fail = 0
        max_failure_duration_ms = float(longest_failure_frames * (self.hop_len / self.sr) * 1000.0)

        # Pitch tracking failure cause: High-energy failure (irregular phonation) vs Low-energy failure (silence/noise)
        high_energy_fail_frames = np.sum((f0_arr == 0) & (rms_arr > 0.15))
        irregular_phonation_ratio = float(high_energy_fail_frames / max(1, invalid_count + unvoiced_count))

        # Pitch discontinuity rate (|Delta F0| > 100 Hz between consecutive voiced frames)
        voiced_f0 = f0_arr[f0_arr > 0]
        if len(voiced_f0) > 1:
            f0_deltas = np.abs(np.diff(voiced_f0))
            discontinuity_rate = float(np.mean(f0_deltas > 100.0))
            f0_mean = float(np.mean(voiced_f0))
            f0_std = float(np.std(voiced_f0))
            f0_cv = float(f0_std / (f0_mean + 1e-6))
            f0_range = float(np.max(voiced_f0) - np.min(voiced_f0))
        else:
            discontinuity_rate = 1.0
            f0_mean = 0.0
            f0_std = 0.0
            f0_cv = 1.0
            f0_range = 0.0

        # -------------------------------------------------------------
        # 2. Subharmonic-to-Harmonic Ratio (SHR)
        # -------------------------------------------------------------
        # If voiced, analyze spectral peaks around F0/2 and F0/3 relative to integer harmonics (2F0, 3F0)
        fft_mag = np.abs(np.fft.rfft(audio * np.hamming(len(audio))))
        fft_freqs = np.fft.rfftfreq(len(audio), 1.0 / self.sr)

        if f0_mean > 80.0:
            # Subharmonic search around F0/2 and F0/3
            sub_f2 = f0_mean / 2.0
            sub_f3 = f0_mean / 3.0
            harm_f2 = 2.0 * f0_mean
            harm_f3 = 3.0 * f0_mean

            def band_energy(f_center, bw=25.0):
                mask = (fft_freqs >= f_center - bw) & (fft_freqs <= f_center + bw)
                return float(np.sum(fft_mag[mask]**2))

            e_sub = band_energy(sub_f2) + band_energy(sub_f3)
            e_harm = band_energy(harm_f2) + band_energy(harm_f3) + band_energy(f0_mean)
            shr = float(e_sub / (e_harm + 1e-8))
            shr_db = float(10.0 * np.log10(max(shr, 1e-5)))
        else:
            shr = 0.0
            shr_db = -30.0

        # -------------------------------------------------------------
        # 3. Harmonic-to-Noise Ratio (HNR)
        # -------------------------------------------------------------
        full_acorr = np.correlate(audio, audio, mode='full')[len(audio)-1:]
        if full_acorr[0] > 1e-6 and len(full_acorr) > max_lag:
            peak_val = np.max(full_acorr[min_lag:max_lag])
            harm_ratio = min(0.999, max(1e-4, peak_val / (full_acorr[0] + 1e-8)))
            hnr_db = float(10.0 * np.log10(harm_ratio / (1.0 - harm_ratio + 1e-6)))
        else:
            hnr_db = -10.0

        # Frame-to-frame HNR delta variance (Harmonic instability)
        frame_hnrs = []
        for f in frames[::4]:
            ac = np.correlate(f, f, mode='full')[len(f)-1:]
            if ac[0] > 1e-6 and len(ac) > max_lag:
                pk = np.max(ac[min_lag:max_lag])
                hr = min(0.99, max(0.01, pk / (ac[0] + 1e-8)))
                frame_hnrs.append(10.0 * np.log10(hr / (1.0 - hr + 1e-6)))
            else:
                frame_hnrs.append(-10.0)
        hnr_instability = float(np.std(frame_hnrs)) if len(frame_hnrs) > 1 else 0.0

        # -------------------------------------------------------------
        # 4. Formant Dispersion (F2 - F1) & Estimation Confidence
        # -------------------------------------------------------------
        f1_list, f2_list = [], []
        formant_conf_list = []

        # Subsample for speed (every 8th frame)
        for f in frames[::8]:
            if np.max(np.abs(f)) < 1e-4:
                continue
            pe = lfilter([1.0, -0.97], [1.0], f * np.hamming(len(f)))
            r = np.correlate(pe, pe, mode='full')[len(pe)-1: len(pe) + self.lpc_order + 1]
            if r[0] < 1e-6:
                continue

            try:
                a = np.zeros(self.lpc_order + 1)
                a[0] = 1.0
                e = r[0]
                for k in range(1, self.lpc_order + 1):
                    lam = -np.sum(a[:k] * r[k:0:-1]) / (e + 1e-8)
                    a[1:k+1] += lam * a[k-1::-1]
                    e *= (1.0 - lam**2)

                roots = np.roots(a)
                roots = roots[np.iscomplex(roots)]
                roots = roots[np.imag(roots) > 0]
                angles = np.angle(roots)
                freqs = sorted(angles * (self.sr / (2.0 * np.pi)))
                bw = -np.log(np.abs(roots)) * (self.sr / np.pi)

                cand_f1 = [fr for fr, b in zip(freqs, bw) if 250 <= fr <= 1200 and b < 500]
                cand_f2 = [fr for fr, b in zip(freqs, bw) if 1000 <= fr <= 3000 and b < 700]

                if cand_f1 and cand_f2:
                    f1_list.append(cand_f1[0])
                    f2_list.append(cand_f2[0])
                    formant_conf_list.append(1.0)
                else:
                    formant_conf_list.append(0.0)
            except Exception:
                formant_conf_list.append(0.0)

        formant_confidence = float(np.mean(formant_conf_list)) if formant_conf_list else 0.0
        if formant_confidence > 0.30 and f1_list and f2_list:
            f1_mean = float(np.mean(f1_list))
            f2_mean = float(np.mean(f2_list))
            formant_dispersion = float(f2_mean - f1_mean)
            formant_available_flag = 1.0
        else:
            f1_mean = 0.0
            f2_mean = 0.0
            formant_dispersion = 0.0
            formant_available_flag = 0.0 # Formants unavailable or collapsed

        # -------------------------------------------------------------
        # 5. Frequency & Amplitude Modulation (20-80 Hz Tremolo / Flutter)
        # -------------------------------------------------------------
        # Amplitude envelope modulation
        env = np.abs(audio)
        env_fft = np.abs(np.fft.rfft(env - np.mean(env)))
        env_freqs = np.fft.rfftfreq(len(env), 1.0 / self.sr)
        flutter_mask = (env_freqs >= 20.0) & (env_freqs <= 80.0)
        tot_mod_power = np.sum(env_fft**2) + 1e-12
        am_flutter_ratio = float(np.sum(env_fft[flutter_mask]**2) / tot_mod_power)

        # Frequency modulation variance
        if len(voiced_f0) > 3:
            fm_deltas = np.abs(np.diff(voiced_f0))
            fm_depth = float(np.std(fm_deltas) / (f0_mean + 1e-6))
        else:
            fm_depth = 1.0

        # -------------------------------------------------------------
        # 6. Spectral Flatness & Spectral Entropy
        # -------------------------------------------------------------
        pow_spec = fft_mag**2 + 1e-12
        geom_mean = np.exp(np.mean(np.log(pow_spec)))
        arith_mean = np.mean(pow_spec)
        spectral_flatness = float(geom_mean / (arith_mean + 1e-12))

        norm_pow = pow_spec / np.sum(pow_spec)
        spectral_entropy = float(-np.sum(norm_pow * np.log2(norm_pow + 1e-12)) / np.log2(len(norm_pow)))

        # -------------------------------------------------------------
        # 7. Temporal Vocal Attack & Decay
        # -------------------------------------------------------------
        half_len = len(env) // 2
        attack_env = env[:half_len]
        decay_env = env[half_len:]

        peak_idx = np.argmax(env)
        peak_time_ms = float(peak_idx / self.sr * 1000.0)

        # Log attack time (10% to 90% peak)
        max_val = np.max(env)
        t_10 = np.where(env >= 0.10 * max_val)[0]
        t_90 = np.where(env >= 0.90 * max_val)[0]
        if len(t_10) > 0 and len(t_90) > 0 and t_90[0] >= t_10[0]:
            attack_ms = max(1.0, float((t_90[0] - t_10[0]) / self.sr * 1000.0))
        else:
            attack_ms = 10.0
        log_attack_time = float(np.log10(attack_ms))

        # Temporal crest factor (Peak / RMS in dB)
        tot_rms = np.sqrt(np.mean(audio**2)) + 1e-6
        crest_factor_db = float(20.0 * np.log10(max(max_val, 1e-6) / tot_rms))

        # -------------------------------------------------------------
        # Assemble 28-Dimensional Feature Vector
        # -------------------------------------------------------------
        features = np.array([
            # 1. Pitch & Tracking Failure (7)
            valid_pitch_ratio, invalid_pitch_ratio, unvoiced_ratio, mean_pitch_conf,
            max_failure_duration_ms, irregular_phonation_ratio, discontinuity_rate,
            # 2. Pitch Dynamics & Stability (4)
            f0_mean, f0_std, f0_cv, f0_range,
            # 3. Subharmonic Ratio & HNR (4)
            shr_db, hnr_db, hnr_instability, (shr / (1.0 + shr)),
            # 4. Formants & Dispersion (5)
            f1_mean, f2_mean, formant_dispersion, formant_confidence, formant_available_flag,
            # 5. Modulation & Flutter (2)
            am_flutter_ratio, fm_depth,
            # 6. Spectral Flatness & Entropy (2)
            spectral_flatness, spectral_entropy,
            # 7. Temporal Onset & Crest (4)
            log_attack_time, attack_ms, crest_factor_db, peak_time_ms
        ], dtype=np.float32)

        return features

    @property
    def feature_names(self) -> list[str]:
        return [
            "valid_pitch_ratio", "invalid_pitch_ratio", "unvoiced_ratio", "mean_pitch_conf",
            "max_failure_duration_ms", "irregular_phonation_ratio", "discontinuity_rate",
            "f0_mean", "f0_std", "f0_cv", "f0_range",
            "shr_db", "hnr_db", "hnr_instability", "shr_norm",
            "f1_mean", "f2_mean", "formant_dispersion", "formant_confidence", "formant_available_flag",
            "am_flutter_ratio", "fm_depth",
            "spectral_flatness", "spectral_entropy",
            "log_attack_time", "attack_time_ms", "crest_factor_db", "peak_time_ms"
        ]
