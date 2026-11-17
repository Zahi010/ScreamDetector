"""Automated Silence and Ambient Audio Generation Pipeline (Stage 8.9.17).

Generates diverse, strictly controlled acoustic silence and ambient audio recordings:
1. Pure Digital Silence (zeros at multiple durations).
2. Near-Silence Gaussian white noise across multiple calibrated SNR/RMS levels (-100 dBFS to -52 dBFS).
3. Near-Silence Pink noise (1/f spectral density modeling electronic and microphone self-noise).
4. Near-Silence Brown noise (1/f^2 spectral density modeling diffuse environmental floor).
5. Synthetic Room Tone & Ambience (HVAC rumble, subtle acoustic resonances).

Every generated file includes complete provenance metadata (seed, RMS, peak, SNR, generation method).
"""

from __future__ import annotations

import csv
import json
import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import soundfile as sf

logger = logging.getLogger("silence_ambient_generator")

TARGET_SAMPLE_RATE = 16000
WORKSPACE_DIR = Path(__file__).resolve().parent.parent


def generate_digital_silence(duration_seconds: float, sample_rate: int = TARGET_SAMPLE_RATE) -> np.ndarray:
    """Generate perfectly silent audio buffer (exact zeros)."""
    n_samples = int(round(duration_seconds * sample_rate))
    return np.zeros(n_samples, dtype=np.float32)


def generate_gaussian_noise(
    duration_seconds: float, target_rms: float, sample_rate: int = TARGET_SAMPLE_RATE, seed: int = 42
) -> np.ndarray:
    """Generate white Gaussian noise scaled to target RMS."""
    rng = np.random.default_rng(seed)
    n_samples = int(round(duration_seconds * sample_rate))
    noise = rng.standard_normal(n_samples).astype(np.float32)
    current_rms = float(np.sqrt(np.mean(noise ** 2) + 1e-12))
    scale = target_rms / max(current_rms, 1e-12)
    return (noise * scale).astype(np.float32)


def generate_pink_noise(
    duration_seconds: float, target_rms: float, sample_rate: int = TARGET_SAMPLE_RATE, seed: int = 42
) -> np.ndarray:
    """Generate 1/f pink noise using Voss-McCartney algorithm scaled to target RMS."""
    rng = np.random.default_rng(seed)
    n_samples = int(round(duration_seconds * sample_rate))
    # Voss-McCartney algorithm with 16 octaves
    num_rows = 16
    array = rng.standard_normal((num_rows, n_samples // num_rows + 1))
    pink = np.zeros(n_samples, dtype=np.float32)

    # Simplified frequency domain filtering: 1 / sqrt(f)
    white = rng.standard_normal(n_samples).astype(np.float32)
    fft_vals = np.fft.rfft(white)
    freqs = np.fft.rfftfreq(n_samples, d=1.0 / sample_rate)
    freqs[0] = freqs[1] if len(freqs) > 1 else 1.0  # avoid divide by zero
    pink_fft = fft_vals / np.sqrt(freqs)
    pink = np.fft.irfft(pink_fft, n=n_samples).astype(np.float32)

    # Normalize to target RMS
    current_rms = float(np.sqrt(np.mean(pink ** 2) + 1e-12))
    scale = target_rms / max(current_rms, 1e-12)
    return (pink * scale).astype(np.float32)


def generate_brown_noise(
    duration_seconds: float, target_rms: float, sample_rate: int = TARGET_SAMPLE_RATE, seed: int = 42
) -> np.ndarray:
    """Generate 1/f^2 brown (Brownian) noise scaled to target RMS."""
    rng = np.random.default_rng(seed)
    n_samples = int(round(duration_seconds * sample_rate))
    white = rng.standard_normal(n_samples).astype(np.float32)
    # Integrate white noise to create Brownian motion
    brown = np.cumsum(white).astype(np.float32)
    # Detrend
    brown = brown - np.mean(brown)
    current_rms = float(np.sqrt(np.mean(brown ** 2) + 1e-12))
    scale = target_rms / max(current_rms, 1e-12)
    return (brown * scale).astype(np.float32)


def generate_room_tone(
    duration_seconds: float,
    target_rms: float,
    sample_rate: int = TARGET_SAMPLE_RATE,
    seed: int = 42,
    hum_freq_hz: float = 60.0,
) -> np.ndarray:
    """Generate realistic indoor room tone with diffuse floor and low-level electrical/HVAC hum."""
    rng = np.random.default_rng(seed)
    n_samples = int(round(duration_seconds * sample_rate))
    t = np.linspace(0.0, duration_seconds, n_samples, endpoint=False, dtype=np.float32)

    # Diffuse background (brown + pink mix)
    p_noise = generate_pink_noise(duration_seconds, target_rms * 0.7, sample_rate=sample_rate, seed=seed)
    b_noise = generate_brown_noise(duration_seconds, target_rms * 0.5, sample_rate=sample_rate, seed=seed + 100)
    diffuse = p_noise + b_noise

    # Faint HVAC / power line fundamental + 2nd harmonic
    hum_amp = target_rms * 0.2
    hum = (hum_amp * np.sin(2.0 * np.pi * hum_freq_hz * t) +
           (hum_amp * 0.3) * np.sin(2.0 * np.pi * 2.0 * hum_freq_hz * t)).astype(np.float32)

    combined = diffuse + hum
    combined = combined - np.mean(combined)
    current_rms = float(np.sqrt(np.mean(combined ** 2) + 1e-12))
    scale = target_rms / max(current_rms, 1e-12)
    return (combined * scale).astype(np.float32)


class SilenceAmbientGenerator:
    """Manages automated creation, audio file persistence, and manifest generation for silence."""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_rows: List[Dict[str, Any]] = []

    def generate_all(self, base_seed: int = 1000) -> List[Dict[str, Any]]:
        """Generate comprehensive 150-sample suite of silence, near-silence, and room tone."""
        self.manifest_rows.clear()
        logger.info("Generating automated silence and room tone dataset...")

        durations = [1.0, 1.5, 2.0, 3.0, 5.0]
        digital_durations = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]
        # In 16-bit PCM, minimum quantization step is ~3e-5; using rms >= 1e-4 ensures audible, non-zero samples
        rms_levels = [1e-4, 2e-4, 4e-4, 8e-4, 1.5e-3, 2.5e-3, 5.0e-3]

        # 1. Pure Digital Silence (10 files: 10 distinct durations)
        idx = 1
        for dur in digital_durations:
            file_id = f"gen_silence_digital_{idx:03d}"
            fname = f"{file_id}.wav"
            fpath = self.output_dir / fname
            audio = generate_digital_silence(dur)
            sf.write(str(fpath), audio, TARGET_SAMPLE_RATE, subtype="PCM_16")

            grp_id = f"synthetic_silence_digital_grp_{(idx % 3) + 1}"
            self.manifest_rows.append({
                "file_id": file_id,
                "filename": fname,
                "relative_path": str(fpath.relative_to(self.output_dir.parent.parent)).replace("\\", "/"),
                "absolute_path": str(fpath).replace("\\", "/"),
                "source_dataset": "Generated_Silence_Pipeline",
                "category": "SILENCE_DIGITAL",
                "binary_label": "non_scream",
                "generation_method": "digital_zero",
                "random_seed": 0,
                "duration_seconds": dur,
                "sample_rate": TARGET_SAMPLE_RATE,
                "bit_depth": 16,
                "audio_rms": 0.0,
                "audio_peak": 0.0,
                "noise_type": "none",
                "target_snr_db": -120.0,
                "source_group_id": grp_id,
                "license": "CC0-1.0",
                "commercial_eligibility": "COMMERCIALLY_ELIGIBLE",
                "attribution": "Festival Scream Detector Synthetic Pipeline",
            })
            idx += 1

        # 2. Gaussian Near-Silence (35 files: 7 rms x 5 durations)
        idx = 1
        for rms in rms_levels:
            for dur in durations:
                seed = base_seed + idx * 19
                file_id = f"gen_silence_gaussian_{idx:03d}"
                fname = f"{file_id}.wav"
                fpath = self.output_dir / fname
                audio = generate_gaussian_noise(dur, target_rms=rms, seed=seed)
                sf.write(str(fpath), audio, TARGET_SAMPLE_RATE, subtype="PCM_16")

                measured_rms = float(np.sqrt(np.mean(audio ** 2)))
                peak = float(np.max(np.abs(audio)))
                dbfs = 20.0 * math.log10(max(measured_rms, 1e-12))
                grp_id = f"synthetic_silence_gaussian_grp_{(idx % 5) + 1}"

                self.manifest_rows.append({
                    "file_id": file_id,
                    "filename": fname,
                    "relative_path": str(fpath.relative_to(self.output_dir.parent.parent)).replace("\\", "/"),
                    "absolute_path": str(fpath).replace("\\", "/"),
                    "source_dataset": "Generated_Silence_Pipeline",
                    "category": "SILENCE_NEAR_ZERO",
                    "binary_label": "non_scream",
                    "generation_method": "gaussian_white_noise",
                    "random_seed": seed,
                    "duration_seconds": dur,
                    "sample_rate": TARGET_SAMPLE_RATE,
                    "bit_depth": 16,
                    "audio_rms": round(measured_rms, 8),
                    "audio_peak": round(peak, 6),
                    "noise_type": "gaussian_white",
                    "target_snr_db": round(dbfs, 2),
                    "source_group_id": grp_id,
                    "license": "CC0-1.0",
                    "commercial_eligibility": "COMMERCIALLY_ELIGIBLE",
                    "attribution": "Festival Scream Detector Synthetic Pipeline",
                })
                idx += 1

        # 3. Pink Noise Near-Silence (35 files: 7 rms x 5 durations)
        idx = 1
        for rms in rms_levels:
            for dur in durations:
                seed = base_seed + 1000 + idx * 23
                file_id = f"gen_silence_pink_{idx:03d}"
                fname = f"{file_id}.wav"
                fpath = self.output_dir / fname
                audio = generate_pink_noise(dur, target_rms=rms, seed=seed)
                sf.write(str(fpath), audio, TARGET_SAMPLE_RATE, subtype="PCM_16")

                measured_rms = float(np.sqrt(np.mean(audio ** 2)))
                peak = float(np.max(np.abs(audio)))
                dbfs = 20.0 * math.log10(max(measured_rms, 1e-12))
                grp_id = f"synthetic_silence_pink_grp_{(idx % 5) + 1}"

                self.manifest_rows.append({
                    "file_id": file_id,
                    "filename": fname,
                    "relative_path": str(fpath.relative_to(self.output_dir.parent.parent)).replace("\\", "/"),
                    "absolute_path": str(fpath).replace("\\", "/"),
                    "source_dataset": "Generated_Silence_Pipeline",
                    "category": "SILENCE_NEAR_ZERO",
                    "binary_label": "non_scream",
                    "generation_method": "voss_pink_noise",
                    "random_seed": seed,
                    "duration_seconds": dur,
                    "sample_rate": TARGET_SAMPLE_RATE,
                    "bit_depth": 16,
                    "audio_rms": round(measured_rms, 8),
                    "audio_peak": round(peak, 6),
                    "noise_type": "pink_1_over_f",
                    "target_snr_db": round(dbfs, 2),
                    "source_group_id": grp_id,
                    "license": "CC0-1.0",
                    "commercial_eligibility": "COMMERCIALLY_ELIGIBLE",
                    "attribution": "Festival Scream Detector Synthetic Pipeline",
                })
                idx += 1

        # 4. Brown Noise Near-Silence (35 files: 7 rms x 5 durations)
        idx = 1
        for rms in rms_levels:
            for dur in durations:
                seed = base_seed + 2000 + idx * 29
                file_id = f"gen_silence_brown_{idx:03d}"
                fname = f"{file_id}.wav"
                fpath = self.output_dir / fname
                audio = generate_brown_noise(dur, target_rms=rms, seed=seed)
                sf.write(str(fpath), audio, TARGET_SAMPLE_RATE, subtype="PCM_16")

                measured_rms = float(np.sqrt(np.mean(audio ** 2)))
                peak = float(np.max(np.abs(audio)))
                dbfs = 20.0 * math.log10(max(measured_rms, 1e-12))
                grp_id = f"synthetic_silence_brown_grp_{(idx % 5) + 1}"

                self.manifest_rows.append({
                    "file_id": file_id,
                    "filename": fname,
                    "relative_path": str(fpath.relative_to(self.output_dir.parent.parent)).replace("\\", "/"),
                    "absolute_path": str(fpath).replace("\\", "/"),
                    "source_dataset": "Generated_Silence_Pipeline",
                    "category": "SILENCE_NEAR_ZERO",
                    "binary_label": "non_scream",
                    "generation_method": "integrated_brown_noise",
                    "random_seed": seed,
                    "duration_seconds": dur,
                    "sample_rate": TARGET_SAMPLE_RATE,
                    "bit_depth": 16,
                    "audio_rms": round(measured_rms, 8),
                    "audio_peak": round(peak, 6),
                    "noise_type": "brown_1_over_f_squared",
                    "target_snr_db": round(dbfs, 2),
                    "source_group_id": grp_id,
                    "license": "CC0-1.0",
                    "commercial_eligibility": "COMMERCIALLY_ELIGIBLE",
                    "attribution": "Festival Scream Detector Synthetic Pipeline",
                })
                idx += 1

        # 5. Synthetic Room Tone & HVAC Ambience (35 files: 7 rms x 5 durations)
        idx = 1
        for rms in rms_levels:
            for dur in durations:
                seed = base_seed + 3000 + idx * 37
                file_id = f"gen_ambient_room_{idx:03d}"
                fname = f"{file_id}.wav"
                fpath = self.output_dir / fname
                audio = generate_room_tone(dur, target_rms=rms, seed=seed, hum_freq_hz=60.0 if (idx % 2 == 0) else 50.0)
                sf.write(str(fpath), audio, TARGET_SAMPLE_RATE, subtype="PCM_16")

                measured_rms = float(np.sqrt(np.mean(audio ** 2)))
                peak = float(np.max(np.abs(audio)))
                dbfs = 20.0 * math.log10(max(measured_rms, 1e-12))
                grp_id = f"synthetic_ambient_room_grp_{(idx % 5) + 1}"

                self.manifest_rows.append({
                    "file_id": file_id,
                    "filename": fname,
                    "relative_path": str(fpath.relative_to(self.output_dir.parent.parent)).replace("\\", "/"),
                    "absolute_path": str(fpath).replace("\\", "/"),
                    "source_dataset": "Generated_Silence_Pipeline",
                    "category": "AMBIENT_ROOM",
                    "binary_label": "non_scream",
                    "generation_method": "synthetic_room_tone_hvac",
                    "random_seed": seed,
                    "duration_seconds": dur,
                    "sample_rate": TARGET_SAMPLE_RATE,
                    "bit_depth": 16,
                    "audio_rms": round(measured_rms, 8),
                    "audio_peak": round(peak, 6),
                    "noise_type": "diffuse_room_tone_with_hum",
                    "target_snr_db": round(dbfs, 2),
                    "source_group_id": grp_id,
                    "license": "CC0-1.0",
                    "commercial_eligibility": "COMMERCIALLY_ELIGIBLE",
                    "attribution": "Festival Scream Detector Synthetic Pipeline",
                })
                idx += 1

        logger.info("Successfully generated %d silence and ambient audio files.", len(self.manifest_rows))
        return self.manifest_rows

    def save_manifest(self, manifest_path: Path) -> None:
        """Save generated silence metadata manifest as CSV."""
        if not self.manifest_rows:
            return
        fieldnames = list(self.manifest_rows[0].keys())
        with open(manifest_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.manifest_rows)
        logger.info("Saved silence manifest to %s", manifest_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    out_dir = WORKSPACE_DIR / "data" / "generated_silence"
    generator = SilenceAmbientGenerator(output_dir=out_dir)
    generator.generate_all()
    manifest_p = WORKSPACE_DIR / "data" / "manifests" / "generated_silence_manifest.csv"
    generator.save_manifest(manifest_p)
    print(f"Generated silence suite successfully saved to {manifest_p}")
