"""
Stage 8.9.22 - Validated Nonlinear Acoustics Extractor

Integrates:
1. Validated instantaneous SHR with octave resolution and local floor subtraction.
2. Signal-conditioned pitch failure (high_energy_vocal_pitch_failure).
3. HNR with harmonic stability.
4. Formant dispersion with explicit confidence flag.
5. AM/FM modulation (20-80 Hz flutter band).
6. Temporal attack and crest dynamics.
7. Feature reliability vector output for dynamic routing.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List, Tuple
import numpy as np
from scipy.signal import lfilter

from .shr_formula_validation import SHRFormulaValidator
from .signal_conditioned_pitch import SignalConditionedPitchTracker

logger = logging.getLogger("validated_nonlinear_acoustics")

class ValidatedNonlinearAcousticExtractor:
    def __init__(self, sample_rate: int = 16000):
        self.sr = sample_rate
        self.shr_validator = SHRFormulaValidator(sample_rate=sample_rate)
        self.pitch_tracker = SignalConditionedPitchTracker(sample_rate=sample_rate)
        self.lpc_order = 18

    def extract_features(self, audio: np.ndarray) -> Dict[str, Any]:
        """
        Extracts 24 validated nonlinear acoustic features along with confidence weights.
        """
        # 1. Pitch & Signal-Conditioned Tracking Failure
        p_res = self.pitch_tracker.analyze_audio(audio)

        # 2. Robust Instantaneous SHR
        s_res = self.shr_validator.robust_instantaneous_shr(audio)

        # 3. Harmonic-to-Noise Ratio (HNR)
        peak = float(np.max(np.abs(audio)))
        if peak > 1e-6:
            norm_audio = audio / peak
        else:
            norm_audio = audio.copy()

        full_acorr = np.correlate(norm_audio, norm_audio, mode='full')[len(norm_audio)-1:]
        min_lag = int(self.sr / 1000.0)
        max_lag = int(self.sr / 80.0)

        if full_acorr[0] > 1e-6 and len(full_acorr) > max_lag:
            peak_val = np.max(full_acorr[min_lag:max_lag])
            harm_ratio = min(0.999, max(1e-4, peak_val / (full_acorr[0] + 1e-8)))
            hnr_db = float(10.0 * np.log10(harm_ratio / (1.0 - harm_ratio + 1e-6)))
            hnr_conf = float(min(1.0, max(0.0, (hnr_db + 10.0) / 30.0)))
        else:
            hnr_db = -10.0
            hnr_conf = 0.0

        # Frame HNR instability
        frame_len = 640
        hop_len = 320
        n_sub = max(1, int((len(norm_audio) - frame_len) / hop_len) + 1)
        sub_hnrs = []
        for i in range(0, n_sub, 2):
            sub_f = norm_audio[i*hop_len : i*hop_len + frame_len]
            ac = np.correlate(sub_f, sub_f, mode='full')[len(sub_f)-1:]
            if ac[0] > 1e-6 and len(ac) > max_lag:
                pk = np.max(ac[min_lag:max_lag])
                hr = min(0.99, max(0.01, pk / (ac[0] + 1e-8)))
                sub_hnrs.append(10.0 * np.log10(hr / (1.0 - hr + 1e-6)))
        hnr_instability = float(np.std(sub_hnrs)) if len(sub_hnrs) > 1 else 0.0

        # 4. Formants & Formant Dispersion
        f1_list, f2_list = [], []
        formant_confs = []
        for i in range(0, n_sub, 4):
            sub_f = norm_audio[i*hop_len : i*hop_len + frame_len]
            if np.max(np.abs(sub_f)) < 1e-3:
                continue
            pe = lfilter([1.0, -0.97], [1.0], sub_f * np.hamming(len(sub_f)))
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
                cand_f2 = [fr for fr, b in zip(freqs, bw) if 1000 <= fr <= 3200 and b < 700]
                if cand_f1 and cand_f2:
                    f1_list.append(cand_f1[0])
                    f2_list.append(cand_f2[0])
                    formant_confs.append(1.0)
                else:
                    formant_confs.append(0.0)
            except Exception:
                formant_confs.append(0.0)

        formant_confidence = float(np.mean(formant_confs)) if formant_confs else 0.0
        if formant_confidence >= 0.35 and f1_list and f2_list:
            f1_mean = float(np.mean(f1_list))
            f2_mean = float(np.mean(f2_list))
            formant_dispersion = float(f2_mean - f1_mean)
            formant_available = 1.0
        else:
            f1_mean = 0.0
            f2_mean = 0.0
            formant_dispersion = 0.0
            formant_available = 0.0

        # 5. Modulation (20-80 Hz Flutter) & Dynamics
        env = np.abs(norm_audio)
        env_fft = np.abs(np.fft.rfft(env - np.mean(env)))
        env_freqs = np.fft.rfftfreq(len(env), 1.0 / self.sr)
        flutter_mask = (env_freqs >= 20.0) & (env_freqs <= 80.0)
        tot_mod_pow = np.sum(env_fft**2) + 1e-12
        am_flutter_ratio = float(np.sum(env_fft[flutter_mask]**2) / tot_mod_pow)

        # Attack Time & Crest Factor
        max_val = float(np.max(env))
        t_10 = np.where(env >= 0.10 * max_val)[0]
        t_90 = np.where(env >= 0.90 * max_val)[0]
        if len(t_10) > 0 and len(t_90) > 0 and t_90[0] >= t_10[0]:
            attack_ms = max(1.0, float((t_90[0] - t_10[0]) / self.sr * 1000.0))
        else:
            attack_ms = 10.0
        log_attack_time = float(np.log10(attack_ms))
        crest_factor_db = float(20.0 * np.log10(max(max_val, 1e-6) / (np.sqrt(np.mean(norm_audio**2)) + 1e-6)))

        # Feature vector assembly (24 continuous dimensions)
        feature_vector = np.array([
            # Signal-conditioned pitch failure & dynamics (6)
            p_res["high_energy_vocal_pitch_failure"],
            p_res["high_energy_pitch_failure"],
            p_res["raw_pitch_failure_rate"],
            p_res["mean_pitch_conf"],
            p_res["discontinuity_rate"],
            p_res["f0_cv"],
            # Robust Instantaneous SHR (3)
            s_res["shr_db"],
            s_res["mean_shr"],
            s_res["biphonic_fraction"],
            # HNR & Instability (2)
            hnr_db,
            hnr_instability,
            # Formants & Dispersion (4)
            f1_mean,
            f2_mean,
            formant_dispersion,
            formant_available,
            # Modulation & Flutter (2)
            am_flutter_ratio,
            p_res["f0_std"],
            # Temporal Attack & Crest (3)
            log_attack_time,
            attack_ms,
            crest_factor_db,
            # Quality & Signal Integrity (4)
            p_res["clipping_ratio"],
            p_res["dropout_ratio"],
            p_res["vocal_confidence"],
            s_res["shr_confidence"]
        ], dtype=np.float32)

        feature_names = [
            "high_energy_vocal_pitch_failure", "high_energy_pitch_failure", "raw_pitch_failure_rate",
            "mean_pitch_conf", "discontinuity_rate", "f0_cv",
            "shr_db", "mean_shr", "biphonic_fraction",
            "hnr_db", "hnr_instability",
            "f1_mean", "f2_mean", "formant_dispersion", "formant_available",
            "am_flutter_ratio", "f0_std",
            "log_attack_time", "attack_time_ms", "crest_factor_db",
            "clipping_ratio", "dropout_ratio", "vocal_confidence", "shr_confidence"
        ]

        confidences = {
            "pitch_confidence": p_res["vocal_confidence"],
            "shr_confidence": s_res["shr_confidence"],
            "hnr_confidence": hnr_conf,
            "formant_confidence": formant_confidence,
            "temporal_confidence": float(min(1.0, max(0.2, crest_factor_db / 15.0)))
        }

        return {
            "feature_vector": feature_vector,
            "feature_names": feature_names,
            "confidences": confidences,
            "metrics": {
                **p_res,
                **s_res,
                "hnr_db": round(hnr_db, 2),
                "formant_dispersion": round(formant_dispersion, 1),
                "formant_confidence": round(formant_confidence, 3),
                "attack_ms": round(attack_ms, 1),
                "crest_factor_db": round(crest_factor_db, 2)
            }
        }
