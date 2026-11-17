"""
Stage 8.9.21 - Experiment F: Controlled Noisy Environments & Synthetic SNR Mixtures

Generates reproducible acoustic mixtures across:
- Signal over noise pairs:
  1. Scream over crowd noise
  2. Scream over music
  3. Scream over cheering
  4. Scream over shouting
  5. Scream over wind
  6. Shouting over music
  7. Cheering over crowd noise
  8. Infant crying over ambient noise
- SNR levels: -5 dB, 0 dB, 5 dB, 10 dB, 15 dB, 20 dB, and clean (+inf).
- Strict source-group and split isolation: No source recording appears in both train and test.
- Full provenance manifest generation.
"""

from __future__ import annotations

import json
import logging
import os
import wave
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np

logger = logging.getLogger("controlled_snr_mixtures")

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = WORKSPACE_DIR.parent.parent

def load_wav(filepath: str | Path, target_sr: int = 16000, max_duration: float = 3.0) -> np.ndarray:
    with wave.open(str(filepath), 'rb') as w:
        n_channels = w.getnchannels()
        sr = w.getframerate()
        max_samples = int(max_duration * sr) if max_duration > 0 else w.getnframes()
        n_frames = min(w.getnframes(), max_samples)
        raw = w.readframes(n_frames)
        sig = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        if n_channels > 1:
            sig = sig.reshape(-1, n_channels).mean(axis=1)

    # Simple resampling if not 16000
    if sr != target_sr:
        new_len = int(len(sig) * target_sr / sr)
        sig = np.interp(np.linspace(0, len(sig), new_len, endpoint=False), np.arange(len(sig)), sig)
    return sig.astype(np.float32)

class ControlledSNRMixtureGenerator:
    def __init__(self, target_sr: int = 16000, seed: int = 42):
        self.sr = target_sr
        self.rng = np.random.RandomState(seed)

    def mix_signals(self, signal: np.ndarray, noise: np.ndarray, snr_db: float) -> Tuple[np.ndarray, float]:
        """
        Mixes signal and noise at target SNR (dB).
        Returns: (mixture, achieved_snr_db)
        """
        if len(signal) == 0:
            return noise.copy(), -999.0
        if len(noise) == 0 or snr_db >= 90.0:
            return signal.copy(), 999.0

        # Match duration: Loop or tile noise if shorter than signal; crop if longer
        if len(noise) < len(signal):
            n_repeats = int(np.ceil(len(signal) / len(noise)))
            noise_matched = np.tile(noise, n_repeats)[:len(signal)]
        else:
            # Pick random offset
            max_offset = len(noise) - len(signal)
            offset = self.rng.randint(0, max_offset + 1)
            noise_matched = noise[offset : offset + len(signal)]

        rms_sig = np.sqrt(np.mean(signal**2)) + 1e-9
        rms_noise = np.sqrt(np.mean(noise_matched**2)) + 1e-9

        # Calculate noise scale factor
        desired_noise_rms = rms_sig / (10.0 ** (snr_db / 20.0))
        noise_scale = desired_noise_rms / rms_noise
        noise_scaled = noise_matched * noise_scale

        mix = signal + noise_scaled

        # Normalize headroom if clipping
        peak = np.max(np.abs(mix))
        if peak > 0.95:
            mix = mix * (0.95 / peak)

        achieved_rms_noise = np.sqrt(np.mean(noise_scaled**2)) + 1e-9
        achieved_snr = float(20.0 * np.log10(rms_sig / achieved_rms_noise))

        return mix.astype(np.float32), achieved_snr

def build_controlled_mixture_dataset(max_pairs_per_type: int = 25) -> Tuple[List[Dict], Dict[str, np.ndarray]]:
    """
    Scans repo for available audio files categorized by role and split,
    and synthesizes controlled mixtures across -5, 0, 5, 10, 15, 20 dB and clean.
    """
    f17_path = BACKEND_DIR / "experiments/stage8_9_17_automated_dataset_reconstruction/data/features_stage8_9_17.npz"
    d17 = np.load(f17_path, allow_pickle=True)
    file_ids = d17['file_ids']
    splits = d17['splits']
    source_groups = d17['source_groups']
    cats = d17['canonical_categories']

    id_to_meta = {
        fid: {
            "split": splits[i],
            "source_group": source_groups[i],
            "category": cats[i]
        }
        for i, fid in enumerate(file_ids)
    }

    # Map all wavs in backend
    import glob
    all_wav_paths = glob.glob(str(BACKEND_DIR / "**/*.wav"), recursive=True)
    stem_to_path = {os.path.splitext(os.path.basename(w))[0]: w for w in all_wav_paths}

    # Add supplementary short screams
    supp_manifest_path = BACKEND_DIR / "experiments/stage8_9_20_acoustic_discriminability/data/supplementary_short_screams_manifest.json"
    supp_items = []
    if supp_manifest_path.exists():
        with open(supp_manifest_path, "r") as fp:
            raw_manifest = json.load(fp)
            supp_items = raw_manifest.get("records", []) if isinstance(raw_manifest, dict) else raw_manifest

    generator = ControlledSNRMixtureGenerator()

    # Organize sound pools by role and split
    # Signals: SCREAM, SHOUTING, CHEERING, INFANT_CRY
    # Backgrounds: CROWD, MUSIC, CHEERING, SHOUTING, WIND/AMBIENT
    sound_pools = {
        "test": {"scream": [], "shouting": [], "cheering": [], "infant_crying": [], "crowd": [], "music": [], "wind_ambient": []},
        "train_val": {"scream": [], "shouting": [], "cheering": [], "infant_crying": [], "crowd": [], "music": [], "wind_ambient": []}
    }

    for fid, meta in id_to_meta.items():
        if fid not in stem_to_path:
            continue
        p = stem_to_path[fid]
        sp = "test" if meta["split"] == "test" else "train_val"
        c = meta["category"]

        item = {"id": fid, "path": p, "source_group": meta["source_group"], "category": c}
        if "SCREAM" in c:
            sound_pools[sp]["scream"].append(item)
        elif "SHOUTING" in c:
            sound_pools[sp]["shouting"].append(item)
        elif "CHEERING" in c:
            sound_pools[sp]["cheering"].append(item)
            sound_pools[sp]["crowd"].append(item)
        elif "CRYING" in c:
            sound_pools[sp]["infant_crying"].append(item)
        elif "MUSIC" in c or "SINGING" in c:
            sound_pools[sp]["music"].append(item)
        elif "AMBIENT" in c or "ROOM" in c:
            sound_pools[sp]["wind_ambient"].append(item)

    # Add supplementary short screams to test pool
    for s in supp_items:
        rel_p = s.get("rel_path")
        p = BACKEND_DIR / rel_p if rel_p else None
        if p and p.exists():
            sound_pools["test"]["scream"].append({
                "id": s.get("record_id", s.get("original_stem")),
                "path": str(p),
                "source_group": s.get("source_group", "supp_short_screams"),
                "category": "SHORT_SCREAM"
            })

    # Mixture configurations required by Section 8
    target_pairs = [
        ("scream", "crowd", "Scream over crowd noise", 1),
        ("scream", "music", "Scream over music", 1),
        ("scream", "cheering", "Scream over cheering", 1),
        ("scream", "shouting", "Scream over shouting", 1),
        ("scream", "wind_ambient", "Scream over wind", 1),
        ("shouting", "music", "Shouting over music", 0),
        ("cheering", "crowd", "Cheering over crowd noise", 0),
        ("infant_crying", "wind_ambient", "Infant crying over ambient noise", 0)
    ]

    snr_levels = [-5.0, 0.0, 5.0, 10.0, 15.0, 20.0, 999.0] # 999 = clean

    mixture_records = []
    mixture_waveforms = {}

    for split in ["test", "train_val"]:
        pool = sound_pools[split]
        for sig_cat, bg_cat, pair_label, label_binary in target_pairs:
            sig_list = pool[sig_cat]
            bg_list = pool[bg_cat]
            if not sig_list or not bg_list:
                continue

            n_pairs = min(max_pairs_per_type, len(sig_list), len(bg_list))
            for i in range(n_pairs):
                sig_item = sig_list[i]
                # Pick bg from different source group
                cand_bg = [b for b in bg_list if b["source_group"] != sig_item["source_group"]]
                if not cand_bg:
                    continue
                bg_item = cand_bg[i % len(cand_bg)]

                try:
                    sig_audio = load_wav(sig_item["path"])
                    bg_audio = load_wav(bg_item["path"])
                except Exception:
                    continue

                for snr in snr_levels:
                    mix_audio, achieved_snr = generator.mix_signals(sig_audio, bg_audio, snr)
                    mix_id = f"{split}_{sig_cat}_in_{bg_cat}_{i}_snr_{int(snr) if snr < 100 else 'clean'}"

                    rec = {
                        "mixture_id": mix_id,
                        "pair_label": pair_label,
                        "split": split,
                        "target_snr_db": snr,
                        "achieved_snr_db": round(achieved_snr, 2),
                        "label_binary": label_binary,
                        "foreground_id": sig_item["id"],
                        "foreground_category": sig_item["category"],
                        "foreground_source_group": sig_item["source_group"],
                        "background_id": bg_item["id"],
                        "background_category": bg_item["category"],
                        "background_source_group": bg_item["source_group"],
                        "duration_sec": round(len(mix_audio) / 16000.0, 3)
                    }
                    mixture_records.append(rec)
                    mixture_waveforms[mix_id] = mix_audio

    # Save manifest
    manifest_path = WORKSPACE_DIR / "data/controlled_snr_mixtures_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w") as fp:
        json.dump(mixture_records, fp, indent=2)

    logger.info(f"Generated {len(mixture_records)} controlled SNR mixtures. Manifest: {manifest_path}")
    print(f"Generated {len(mixture_records)} controlled SNR mixtures across {len(snr_levels)} SNR conditions.")
    return mixture_records, mixture_waveforms

if __name__ == "__main__":
    records, waves = build_controlled_mixture_dataset(max_pairs_per_type=15)
