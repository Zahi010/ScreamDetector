#!/usr/bin/env python3
"""
STAGE 8.9.66 — Track G: Final Model Freeze Protocol
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
This system is an experimental acoustic research prototype and is not certified for life-safety use.
"""

import csv
import hashlib
import json
import sys
import time
from pathlib import Path
import numpy as np
import scipy.io.wavfile as wav
import torch
import torch.nn as nn
import torch.optim as optim

SCRIPT_DIR = Path(__file__).resolve().parent
STAGE66_DIR = SCRIPT_DIR.parent
MODELS_DIR = STAGE66_DIR / "models"
RESEARCH_DIR = STAGE66_DIR.parent
BACKEND_DIR = RESEARCH_DIR.parent
REPO_ROOT = BACKEND_DIR.parent

STAGE57_DIR = RESEARCH_DIR / "stage_8_9_57"
STAGE63_DIR = RESEARCH_DIR / "stage_8_9_63"

sys.path.insert(0, str(STAGE57_DIR / "dsp_implementations"))
from c5_combined import extract_subband_vector_c5, extract_phonation_stats_c5


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def load_audio_wav(path: Path):
    sr, raw = wav.read(path)
    if raw.ndim > 1:
        raw = np.mean(raw, axis=1)
    if raw.dtype == np.int16:
        aud = raw.astype(np.float32) / 32768.0
    elif raw.dtype == np.int32:
        aud = raw.astype(np.float32) / 2147483648.0
    else:
        aud = raw.astype(np.float32)
    return aud


def extract_short_branch_features(audio: np.ndarray, sr: int = 16000):
    n_250ms = int(0.250 * sr)
    if len(audio) < n_250ms:
        chunk = np.pad(audio, (0, n_250ms - len(audio)))
    else:
        frame_len = 400
        hop_len = 160
        windows = np.lib.stride_tricks.sliding_window_view(audio, frame_len)[::hop_len]
        frame_e = np.sum(windows ** 2, axis=1)
        best_frame = np.argmax(frame_e)
        center_samp = best_frame * hop_len
        start_samp = max(0, center_samp - n_250ms // 2)
        end_samp = min(len(audio), start_samp + n_250ms)
        if end_samp - start_samp < n_250ms:
            start_samp = max(0, end_samp - n_250ms)
        chunk = audio[start_samp:end_samp]
        if len(chunk) < n_250ms:
            chunk = np.pad(chunk, (0, n_250ms - len(chunk)))

    tiled = np.tile(chunk, 4)[:16000]
    norm = tiled / (np.max(np.abs(tiled)) + 1e-9)
    sb_v = extract_subband_vector_c5(norm, sr=sr)
    ac_v = extract_phonation_stats_c5(norm, sr=sr)
    return np.concatenate([sb_v, ac_v])


def extract_sustained_branch_features(audio: np.ndarray, sr: int = 16000):
    if len(audio) >= 16000:
        c = audio[len(audio)//2 - 8000 : len(audio)//2 + 8000]
    else:
        c = np.pad(audio, (0, 16000 - len(audio)))
    norm = c / (np.max(np.abs(c)) + 1e-9)
    sb_v = extract_subband_vector_c5(norm, sr=sr)
    ac_v = extract_phonation_stats_c5(norm, sr=sr)
    return np.concatenate([sb_v, ac_v])


class DualResolutionGatedModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.short_enc = nn.Sequential(
            nn.Linear(17, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(0.10),
            nn.Linear(32, 16),
            nn.ReLU()
        )
        self.sust_enc = nn.Sequential(
            nn.Linear(17, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(0.10),
            nn.Linear(32, 16),
            nn.ReLU()
        )
        self.gate_net = nn.Sequential(
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )
        self.head = nn.Linear(16, 1)

    def forward(self, x_short, x_sust):
        z_s = self.short_enc(x_short)
        z_l = self.sust_enc(x_sust)
        fused_in = torch.cat([z_s, z_l], dim=-1)
        gate = self.gate_net(fused_in)
        z_fused = gate * z_s + (1.0 - gate) * z_l
        logits = self.head(z_fused).squeeze(-1)
        return logits, gate.squeeze(-1), z_s, z_l


def freeze_model():
    print("=" * 80)
    print("STAGE 8.9.66 — TRACK G: FINAL MODEL FREEZE & METADATA SERIALIZATION")
    print("MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.")
    print("=" * 80)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load Development Manifest
    dev_manifest_path = STAGE63_DIR / "stage_63_development_manifest.csv"
    with open(dev_manifest_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"Loaded {len(rows)} recordings for final candidate parameter freeze.")

    X_short = []
    X_sust = []
    y_true = []
    subcategories = []

    for r in rows:
        aud = load_audio_wav(REPO_ROOT / r["workspace_audio_path"])
        f_s = extract_short_branch_features(aud)
        f_l = extract_sustained_branch_features(aud)
        X_short.append(f_s)
        X_sust.append(f_l)
        y_true.append(int(r["binary_label"]))
        subcategories.append(r["subcategory"].lower())

    X_short = np.array(X_short, dtype=np.float32)
    X_sust = np.array(X_sust, dtype=np.float32)
    y_true = np.array(y_true, dtype=np.float32)

    # Compute contrastive weights (w=1.60 for whistles/tones/squeaks, w=1.25 for shouts)
    ref_weights = np.ones(len(y_true), dtype=np.float32)
    for i in range(len(y_true)):
        if y_true[i] == 0:
            if "whistle" in subcategories[i] or "tone" in subcategories[i] or "squeak" in subcategories[i]:
                ref_weights[i] = 1.60
            elif "shout" in subcategories[i] or "victim" in subcategories[i]:
                ref_weights[i] = 1.25

    pos_weight = float(np.sum(y_true == 0) / np.sum(y_true == 1))

    # Train final model on full development cohort
    print("Training full-cohort frozen weights (Seed 42)...")
    torch.manual_seed(42)
    np.random.seed(42)

    model = DualResolutionGatedModel()
    optimizer = optim.Adam(model.parameters(), lr=0.005, weight_decay=1e-4)
    criterion = nn.BCEWithLogitsLoss(weight=torch.tensor(ref_weights),
                                     pos_weight=torch.tensor([pos_weight]))

    X_s_t = torch.tensor(X_short, dtype=torch.float32)
    X_l_t = torch.tensor(X_sust, dtype=torch.float32)
    y_t = torch.tensor(y_true, dtype=torch.float32)

    model.train()
    for epoch in range(40):
        optimizer.zero_grad()
        logits, _, _, _ = model(X_s_t, X_l_t)
        loss = criterion(logits, y_t)
        loss.backward()
        optimizer.step()

    # Save frozen checkpoint
    checkpoint_path = MODELS_DIR / "candidate_65f_frozen.pt"
    torch.save({
        "model_state_dict": model.state_dict(),
        "model_architecture": "DualResolutionGatedModel",
        "stage": "8.9.66",
        "candidate_id": "Candidate_65_F_Combined_Selective",
        "random_seed": 42,
        "input_dim_short": 17,
        "input_dim_sust": 17,
        "latent_dim": 16,
        "decision_threshold": 0.48,
        "selective_suppression_stack": {
            "high_confidence_bypass_threshold": 0.80,
            "branch_cosine_agreement_threshold": 0.40,
            "narrow_band_whistle_hnr_db": 12.0,
            "narrow_band_whistle_flatness": 0.001,
            "narrow_band_attenuation_factor": 0.15
        }
    }, checkpoint_path)

    checkpoint_sha256 = sha256_file(checkpoint_path)
    print(f"Saved frozen checkpoint to {checkpoint_path.name}")
    print(f"Checkpoint SHA-256: {checkpoint_sha256}")

    # Metadata dictionary
    meta = {
        "candidate_id": "Candidate_65_F_Combined_Selective",
        "checkpoint_file": checkpoint_path.name,
        "checkpoint_sha256": checkpoint_sha256,
        "architecture_class": "DualResolutionGatedModel",
        "features": {
            "short_branch": "250ms high-energy slice, tiled x4, C5 DSP (6 subbands, 11 phonation)",
            "sustained_branch": "1000ms centered window, C5 DSP (6 subbands, 11 phonation)"
        },
        "operating_hyperparameters": {
            "decision_threshold": 0.48,
            "high_confidence_bypass": 0.80,
            "branch_cosine_agreement_threshold": 0.40,
            "whistle_hnr_threshold_db": 12.0,
            "whistle_flatness_threshold": 0.001,
            "whistle_attenuation_multiplier": 0.15
        },
        "development_performance": {
            "overall_recall": 0.9436,
            "hard_negative_fpr": 0.0598,
            "shouted_speech_fpr": 0.2000,
            "short_scream_recall": 0.9850,
            "ultra_short_recall": 1.0000,
            "sustained_recall": 0.8548,
            "f1_score": 0.9534,
            "roc_auc": 0.9622,
            "pr_auc": 0.9785,
            "model_p95_latency_ms": 0.918
        },
        "gate_status_summary": {
            "gate1_recall_ge_96": False,
            "gate2_fpr_le_5": False,
            "gate3_shouted_fpr_le_15": False,
            "gate4_short_recall_ge_90": True,
            "gate5_latency_p95_le_25ms": True,
            "all_gates_pass": False
        },
        "evaluation_readiness_recommendation": "NOT READY FOR INDEPENDENT EVALUATION",
        "freeze_timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

    meta_path = MODELS_DIR / "candidate_freeze_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print(f"Emitted {meta_path.name}.")

    # Author candidate_freeze_report.md
    freeze_md = STAGE66_DIR / "candidate_freeze_report.md"
    with open(freeze_md, "w", encoding="utf-8") as f:
        f.write("# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.\n\n")
        f.write("# CANDIDATE 65-F FORMAL FREEZE REPORT\n")
        f.write("**Cryptographic Checkpoint Locking, Hyperparameter Serialization, and Freeze Manifest**\n\n")
        f.write("## 1. Safety Designation\n")
        f.write("Non-certified acoustic research prototype. Prohibited for life-safety use, emergency alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.\n\n")
        f.write("All tests utilize legally acquired recorded audio files and safe playback protocols only.\n\n---\n\n")
        f.write("## 2. Frozen Checkpoint Specification\n\n")
        f.write(f"- **Candidate Name:** `Candidate_65_F_Combined_Selective`\n")
        f.write(f"- **Checkpoint Path:** `models/candidate_65f_frozen.pt`\n")
        f.write(f"- **Cryptographic SHA-256:** `{checkpoint_sha256}`\n")
        f.write(f"- **Metadata File:** `models/candidate_freeze_metadata.json`\n")
        f.write(f"- **Freeze Timestamp:** `{meta['freeze_timestamp_utc']}`\n\n---\n\n")
        f.write("## 3. Parameter and Architectural Freeze\n\n")
        f.write("1. **Encoder Topologies:**\n")
        f.write("   - Short Branch: Linear(17, 32) -> BatchNorm1d -> ReLU -> Dropout(0.10) -> Linear(32, 16) -> ReLU\n")
        f.write("   - Sustained Branch: Linear(17, 32) -> BatchNorm1d -> ReLU -> Dropout(0.10) -> Linear(32, 16) -> ReLU\n")
        f.write("2. **Blending Mechanism:**\n")
        f.write("   - Gate Network: Linear(32, 16) -> ReLU -> Linear(16, 1) -> Sigmoid()\n")
        f.write("   - Fusion: $z_{\\text{fused}} = \\gamma z_s + (1 - \\gamma) z_l$\n")
        f.write("   - Head: Linear(16, 1)\n")
        f.write("3. **Post-Processing Suppression Constants:**\n")
        f.write("   - Calibrated Operating Threshold: $\\tau = 0.48$\n")
        f.write("   - High-Confidence Protection Threshold: $p_{\\text{protect}} = 0.80$\n")
        f.write("   - Latent Cosine Agreement Threshold: $\\text{sim}_{\\text{thresh}} = 0.40$\n")
        f.write("   - Narrow-Band Whistle Veto: $\\text{HNR} > 12.0\\text{ dB}$ AND $\\text{Flatness} < 0.001$\n")
        f.write("   - Attenuation Multiplier: $0.15$\n\n---\n\n")
        f.write("## 4. Integrity and Immutability Guarantee\n")
        f.write("The checkpoint and metadata are permanently locked. No downstream retuning, fine-tuning, or parameter adjustment is permitted without incrementing the research stage and invalidating preregistration.\n")
    print(f"Emitted {freeze_md.name}.")


if __name__ == "__main__":
    freeze_model()

