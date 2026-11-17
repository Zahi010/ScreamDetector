#!/usr/bin/env python3
"""
STAGE 8.9.63 — Phase C4: Padding Hypothesis Experimental Validation Script
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import csv
import math
import sys
from pathlib import Path
import numpy as np
import scipy.io.wavfile as wav
import torch

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE54_DIR = BACKEND_DIR / "research" / "stage_8_9_54"
STAGE57_DIR = BACKEND_DIR / "research" / "stage_8_9_57"
STAGE63_DIR = BACKEND_DIR / "research" / "stage_8_9_63"

sys.path.insert(0, str(STAGE57_DIR / "dsp_implementations"))
from c5_combined import extract_subband_vector_c5, extract_phonation_stats_c5

class ResearchDualHeadClassifier(torch.nn.Module):
    def __init__(self, sem_dim=1024, acoust_dim=6, subband_dim=11):
        super().__init__()
        self.sem_proj = torch.nn.Sequential(torch.nn.Linear(sem_dim, 128), torch.nn.ReLU(), torch.nn.Dropout(0.20))
        self.acoust_proj = torch.nn.Sequential(torch.nn.Linear(acoust_dim * 2 + subband_dim, 64), torch.nn.ReLU(), torch.nn.Dropout(0.15))
        self.gate = torch.nn.Sequential(torch.nn.Linear(128 + 64, 32), torch.nn.Sigmoid())
        self.classifier = torch.nn.Sequential(torch.nn.Linear(128 + 64, 64), torch.nn.ReLU(), torch.nn.Linear(64, 1))

    def forward(self, x_sem, x_acoust, mask_acoust, x_subband):
        z_s = self.sem_proj(x_sem)
        acoust_combined = torch.cat([torch.nan_to_num(x_acoust, nan=0.0), mask_acoust, x_subband], dim=-1)
        z_a = self.acoust_proj(acoust_combined)
        fused = torch.cat([z_s, z_a], dim=-1)
        return self.classifier(fused).squeeze(-1)

def load_e1_model():
    ckpt_path = STAGE54_DIR / "training" / "candidate_e_v954_weighted.pt"
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    model = ResearchDualHeadClassifier()
    model.load_state_dict(ckpt)
    model.eval()
    return model

def synthesize_vocal_burst(duration_s: float, sr: int = 16000, f0: float = 750.0):
    """Generates synthetic scream-like burst with harmonic overtone and chaotic roughness."""
    t = np.linspace(0, duration_s, int(sr * duration_s), endpoint=False)
    # Fundamental + Formants
    sig = np.sin(2 * np.pi * f0 * t) * 0.5
    sig += np.sin(2 * np.pi * (f0 * 2.1) * t) * 0.3
    sig += np.sin(2 * np.pi * (f0 * 3.2) * t) * 0.2
    # Non-linear roughness modulation
    sig *= (1.0 + 0.3 * np.sin(2 * np.pi * 35 * t))
    # Gaussian noise burst (aperiodic roughness)
    noise = np.random.normal(0, 0.15, len(t))
    sig += noise
    # Window envelope (raised cosine attack/decay)
    env = np.hanning(len(t)) ** 0.5
    sig *= env
    sig = sig / (np.max(np.abs(sig)) + 1e-9)
    return sig

def main():
    print("=" * 80)
    print("STAGE 8.9.63 — PHASE C4: PADDING HYPOTHESIS EXPERIMENTAL VALIDATION")
    print("=" * 80)

    sr = 16000
    model = load_e1_model()

    durations = [0.15, 0.25, 0.35, 0.50, 0.75, 1.00]
    padding_experiments = []

    for dur in durations:
        burst = synthesize_vocal_burst(dur, sr=sr)
        n_burst = len(burst)
        active_rms = np.sqrt(np.mean(burst ** 2))

        # 1. Fixed 1.0s zero-padding (Centered)
        pad_total = 16000 - n_burst
        pad_left = pad_total // 2
        pad_right = pad_total - pad_left
        padded_audio = np.pad(burst, (pad_left, pad_right))
        padded_rms = np.sqrt(np.mean(padded_audio ** 2))
        measured_dilution_db = 10 * np.log10((padded_rms ** 2) / (active_rms ** 2) + 1e-12)
        theoretical_dilution_db = 10 * np.log10(dur / 1.0)

        # 2. Extract features under C5
        sb_padded = extract_subband_vector_c5(padded_audio, sr=sr)
        ac_padded = extract_phonation_stats_c5(padded_audio, sr=sr)

        # 3. Active-region cropping (tiled to 1.0s buffer to simulate full density)
        n_tiles = int(math.ceil(16000 / n_burst))
        active_tiled = np.tile(burst, n_tiles)[:16000]
        sb_active = extract_subband_vector_c5(active_tiled, sr=sr)
        ac_active = extract_phonation_stats_c5(active_tiled, sr=sr)

        # 4. Duration-aware normalized features
        dur_factor = min(1.0, max(0.1, dur))
        sb_normed = sb_padded / dur_factor

        # 5. Measure model activations
        # Dummy semantic embedding (zeroed for controlled acoustic head evaluation)
        sem_dummy = torch.zeros((1, 1024))
        mask_dummy = torch.ones((1, 6))

        with torch.no_grad():
            logit_padded = model(sem_dummy, torch.tensor(ac_padded, dtype=torch.float32).unsqueeze(0), mask_dummy, torch.tensor(sb_padded, dtype=torch.float32).unsqueeze(0)).item()
            logit_active = model(sem_dummy, torch.tensor(ac_active, dtype=torch.float32).unsqueeze(0), mask_dummy, torch.tensor(sb_active, dtype=torch.float32).unsqueeze(0)).item()
            logit_normed = model(sem_dummy, torch.tensor(ac_active, dtype=torch.float32).unsqueeze(0), mask_dummy, torch.tensor(sb_normed, dtype=torch.float32).unsqueeze(0)).item()

        prob_padded = 1.0 / (1.0 + np.exp(-logit_padded))
        prob_active = 1.0 / (1.0 + np.exp(-logit_active))
        prob_normed = 1.0 / (1.0 + np.exp(-logit_normed))

        padding_experiments.append({
            "burst_duration_s": dur,
            "padding_fraction": round(1.0 - dur, 3),
            "theoretical_dilution_db": round(theoretical_dilution_db, 2),
            "measured_dilution_db": round(measured_dilution_db, 2),
            "padded_logit": round(logit_padded, 4),
            "padded_prob": round(prob_padded, 4),
            "active_tiled_logit": round(logit_active, 4),
            "active_tiled_prob": round(prob_active, 4),
            "dur_normed_logit": round(logit_normed, 4),
            "dur_normed_prob": round(prob_normed, 4),
            "logit_drop_from_padding": round(logit_active - logit_padded, 4),
            "prob_drop_from_padding": round(prob_active - prob_padded, 4)
        })

    out_csv = STAGE63_DIR / "padding_hypothesis_results.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(padding_experiments[0].keys()))
        w.writeheader()
        w.writerows(padding_experiments)
    print(f"Wrote padding hypothesis results to {out_csv}")

    for exp in padding_experiments:
        print(f"\n[Duration: {exp['burst_duration_s']:.2f}s | Pad: {exp['padding_fraction']*100:.1f}%]")
        print(f"  Energy Dilution: Theoretical={exp['theoretical_dilution_db']:.2f} dB, Measured={exp['measured_dilution_db']:.2f} dB")
        print(f"  Padded:   Logit={exp['padded_logit']:+.4f}, Prob={exp['padded_prob']*100:.2f}%")
        print(f"  Active:   Logit={exp['active_tiled_logit']:+.4f}, Prob={exp['active_tiled_prob']*100:.2f}%")
        print(f"  Impact:   Logit Drop = {exp['logit_drop_from_padding']:+.4f}, Prob Drop = {exp['prob_drop_from_padding']*100:+.2f}%")

if __name__ == "__main__":
    main()

