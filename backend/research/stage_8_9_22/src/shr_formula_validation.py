"""
Stage 8.9.22 - Forensic Audit: SHR Formula Validation on Synthetic and Real Signals

Validates:
1. Pure harmonic tone (F0 = 300 Hz, harmonics at 600, 900, 1200 Hz) -> Must have LOW SHR (< -25 dB).
2. Period-doubled biphonation (F0 = 300 Hz, subharmonics at 150, 450, 750 Hz) -> Must have HIGH SHR (> -6 dB).
3. Period-tripled vocal chaos (F0 = 300 Hz, subharmonics at 100, 200, 400, 500 Hz).
4. Low-frequency background noise confuser (180 Hz voice + 50/60 Hz mains hum).

Compares:
- Legacy Stage 8.9.21 implementation (whole-signal static FFT with f0_mean fallback to -30 dB).
- Robust Frame-Level Instantaneous SHR algorithm (tracking subharmonic peak prominence per voiced frame).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, Tuple
import numpy as np

WORKSPACE_DIR = Path(__file__).resolve().parent.parent

class SHRFormulaValidator:
    def __init__(self, sample_rate: int = 16000):
        self.sr = sample_rate

    def generate_synthetic_signals(self, duration_sec: float = 1.0) -> Dict[str, Tuple[np.ndarray, float]]:
        """Generates ground-truth synthetic signals with known F0 and subharmonic presence."""
        t = np.linspace(0, duration_sec, int(self.sr * duration_sec), endpoint=False)
        f0 = 300.0

        # 1. Pure harmonic vocal tone (Modal phonation - zero subharmonics)
        pure_harmonic = (
            1.0 * np.sin(2 * np.pi * f0 * t) +
            0.6 * np.sin(2 * np.pi * 2 * f0 * t) +
            0.4 * np.sin(2 * np.pi * 3 * f0 * t) +
            0.2 * np.sin(2 * np.pi * 4 * f0 * t)
        )
        pure_harmonic += 0.01 * np.random.randn(len(t)) # minor noise floor

        # 2. Period-doubled biphonation (Subharmonics at F0/2, 3F0/2, 5F0/2)
        biphonic = pure_harmonic.copy() + (
            0.8 * np.sin(2 * np.pi * (f0 / 2.0) * t) +
            0.5 * np.sin(2 * np.pi * (3 * f0 / 2.0) * t) +
            0.3 * np.sin(2 * np.pi * (5 * f0 / 2.0) * t)
        )

        # 3. Period-tripled vocal bifurcation (F0/3, 2F0/3, 4F0/3)
        tripled = pure_harmonic.copy() + (
            0.7 * np.sin(2 * np.pi * (f0 / 3.0) * t) +
            0.6 * np.sin(2 * np.pi * (2 * f0 / 3.0) * t) +
            0.4 * np.sin(2 * np.pi * (4 * f0 / 3.0) * t)
        )

        # 4. Speech shouting (180 Hz) corrupted by 60 Hz mains hum and HVAC rumble
        f0_shout = 180.0
        shout_hum = (
            1.0 * np.sin(2 * np.pi * f0_shout * t) +
            0.7 * np.sin(2 * np.pi * 2 * f0_shout * t) +
            0.5 * np.sin(2 * np.pi * 3 * f0_shout * t) +
            0.8 * np.sin(2 * np.pi * 60.0 * t) + # 60 Hz hum (close to F0/3 = 60 Hz!)
            0.4 * np.sin(2 * np.pi * 90.0 * t)   # 90 Hz subharmonic alias (F0/2 = 90 Hz!)
        )

        # 5. Pure broadband white noise (total phonation collapse / unvoiced)
        white_noise = np.random.randn(len(t)).astype(np.float32)

        return {
            "pure_harmonic_modal": (pure_harmonic.astype(np.float32), f0),
            "period_doubled_biphonic": (biphonic.astype(np.float32), f0),
            "period_tripled_biphonic": (tripled.astype(np.float32), f0),
            "speech_shout_with_hum": (shout_hum.astype(np.float32), f0_shout),
            "unvoiced_noise_collapse": (white_noise, 0.0)
        }

    def legacy_shr(self, audio: np.ndarray, f0_mean: float) -> Tuple[float, float]:
        """Exact Stage 8.9.21 SHR calculation."""
        fft_mag = np.abs(np.fft.rfft(audio * np.hamming(len(audio))))
        fft_freqs = np.fft.rfftfreq(len(audio), 1.0 / self.sr)

        if f0_mean > 80.0:
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
        return shr, shr_db

    def robust_instantaneous_shr(self, audio: np.ndarray, frame_len: int = 640, hop_len: int = 160) -> Dict[str, Any]:
        """
        Robust Frame-Level Instantaneous SHR algorithm:
        1. Frames audio (40ms, 10ms hop).
        2. Estimates frame-level F0 using normalized autocorrelation.
        3. For voiced frames with high confidence (>0.45):
           - Evaluates spectral peaks at instantaneous odd subharmonics (F0/2, 3F0/2) vs integer harmonics (F0, 2F0, 3F0).
           - Subtracts local noise floor baseline to avoid mains hum / ambient bias.
        4. Distinguishes unvoiced / chaotic frames from low SHR.
        """
        n_frames = max(1, int((len(audio) - frame_len) / hop_len) + 1)
        frames = [audio[i * hop_len : i * hop_len + frame_len] for i in range(n_frames)]

        min_lag = int(self.sr / 1000.0)
        max_lag = int(self.sr / 80.0)

        voiced_shrs = []
        valid_frames = 0
        unvoiced_frames = 0

        for f in frames:
            f_rms = np.sqrt(np.mean(f**2))
            if f_rms < 1e-3:
                unvoiced_frames += 1
                continue

            w = f * np.hamming(len(f))
            acorr = np.correlate(w, w, mode='full')[len(w) - 1:]
            if acorr[0] < 1e-6:
                unvoiced_frames += 1
                continue

            norm_acorr = acorr / acorr[0]
            search = norm_acorr[min_lag:max_lag]
            if len(search) == 0:
                unvoiced_frames += 1
                continue

            peak_idx = np.argmax(search) + min_lag
            peak_val = float(norm_acorr[peak_idx])

            if peak_val >= 0.40:
                cand_f0 = self.sr / float(peak_idx)
                valid_frames += 1

                # Frame-level FFT
                mag = np.abs(np.fft.rfft(w, n=1024))
                freqs = np.fft.rfftfreq(1024, 1.0 / self.sr)

                def band_peak(f_c, bw=25.0):
                    m = (freqs >= f_c - bw) & (freqs <= f_c + bw)
                    return float(np.max(mag[m]**2)) if np.any(m) else 1e-9

                # Check if detected pitch was an octave error (halved frequency)
                # If cand_f0 has strong energy at 2*cand_f0, test both hypotheses
                p_base = cand_f0
                if p_base < 200.0 and band_peak(2 * p_base) > 1.5 * band_peak(p_base):
                    f0_true = 2 * p_base
                else:
                    f0_true = p_base

                # Subharmonics at 0.5*F0, 1.5*F0, 2.5*F0
                e_sub = band_peak(0.5 * f0_true) + band_peak(1.5 * f0_true) + band_peak(2.5 * f0_true)
                # Harmonics at F0, 2*F0, 3*F0
                e_harm = band_peak(f0_true) + band_peak(2.0 * f0_true) + band_peak(3.0 * f0_true)

                local_noise = float(np.median(mag[(freqs >= 50) & (freqs <= 3000)]**2)) + 1e-9
                e_sub_clean = max(1e-9, e_sub - 3.0 * local_noise)
                e_harm_clean = max(1e-9, e_harm - 3.0 * local_noise)

                f_shr = float(e_sub_clean / (e_harm_clean + 1e-8))
                voiced_shrs.append(f_shr)
            else:
                unvoiced_frames += 1

        if voiced_shrs:
            mean_shr = float(np.mean(voiced_shrs))
            shr_db = float(10.0 * np.log10(max(mean_shr, 1e-4)))
            shr_confidence = float(len(voiced_shrs) / n_frames)
            biphonic_fraction = float(np.mean([s > 0.25 for s in voiced_shrs]))
        else:
            mean_shr = 0.0
            shr_db = -30.0
            shr_confidence = 0.0
            biphonic_fraction = 0.0

        return {
            "mean_shr": round(mean_shr, 4),
            "shr_db": round(shr_db, 2),
            "shr_confidence": round(shr_confidence, 3),
            "biphonic_fraction": round(biphonic_fraction, 3),
            "valid_voiced_frames": valid_frames,
            "unvoiced_frames": unvoiced_frames
        }

    def run_benchmark(self) -> Dict[str, Any]:
        signals = self.generate_synthetic_signals()
        benchmark_results = {}

        for name, (audio, true_f0) in signals.items():
            # Legacy SHR
            leg_shr, leg_shr_db = self.legacy_shr(audio, true_f0)
            # Robust SHR
            rob_res = self.robust_instantaneous_shr(audio)

            benchmark_results[name] = {
                "true_f0": true_f0,
                "legacy_shr_db": round(leg_shr_db, 2),
                "robust_shr_db": rob_res["shr_db"],
                "robust_shr_confidence": rob_res["shr_confidence"],
                "robust_biphonic_fraction": rob_res["biphonic_fraction"],
                "physical_interpretation": (
                    "HIGH_BIPHONATION" if rob_res["shr_db"] > -8.0 and rob_res["shr_confidence"] > 0.4
                    else "MODAL_HARMONIC" if rob_res["shr_confidence"] > 0.4
                    else "UNVOICED_CHAOS_OR_NOISE"
                )
            }

        out_path = WORKSPACE_DIR / "reports/shr_validation_results.json"
        with open(out_path, "w") as fp:
            json.dump(benchmark_results, fp, indent=2)

        return benchmark_results

if __name__ == "__main__":
    validator = SHRFormulaValidator()
    res = validator.run_benchmark()
    print("SHR Formula Validation Completed:")
    for k, v in res.items():
        print(f"  {k}: Legacy={v['legacy_shr_db']} dB | Robust={v['robust_shr_db']} dB (Conf={v['robust_shr_confidence']}) -> {v['physical_interpretation']}")
