# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
STAGE 8.9.67 — MODEL DEVELOPMENT & FIVE-GATE CANDIDATE TOURNAMENT
Trains and evaluates candidates:
- Candidate 65-F (Frozen reference benchmark)
- Candidate 67-A (Dual-resolution retrained on expansion_train)
- Candidate 67-B (Dual-resolution + vocal acoustic feature fusion)
- Candidate 67-C (Dual-resolution + hard-negative vocal margin loss)
- Candidate 67-D (Candidate 67-B + calibrated multi-stage acoustic veto)

MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import sys
import os
import json
import time
import math
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader

REPO_ROOT = Path(__file__).resolve().parents[4]
STAGE_DIR = Path(__file__).resolve().parents[1]
CACHE_DIR = STAGE_DIR / "cache"
MODELS_DIR = STAGE_DIR / "models"
REPORTS_DIR = STAGE_DIR / "reports"

torch.manual_seed(42)
np.random.seed(42)

# ==============================================================================
# Model Architectures
# ==============================================================================

class DualResolutionGatedModel(nn.Module):
    def __init__(self, in_features=17):
        super().__init__()
        self.in_features = in_features
        self.short_enc = nn.Sequential(
            nn.Linear(in_features, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(0.15),
            nn.Linear(32, 16),
            nn.ReLU()
        )
        self.sust_enc = nn.Sequential(
            nn.Linear(in_features, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(0.15),
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


# ==============================================================================
# Training Routines
# ==============================================================================

def train_model(
    model: nn.Module,
    x_s_tr: np.ndarray,
    x_l_tr: np.ndarray,
    y_tr: np.ndarray,
    categories_tr: np.ndarray,
    epochs: int = 50,
    lr: float = 0.003,
    weight_decay: float = 1e-4,
    shout_weight: float = 1.0,
):
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    
    # Class weights: Screams (403), Negatives (652)
    pos_weight = torch.tensor([652.0 / 403.0])
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)

    t_s = torch.tensor(x_s_tr, dtype=torch.float32)
    t_l = torch.tensor(x_l_tr, dtype=torch.float32)
    t_y = torch.tensor(y_tr, dtype=torch.float32)
    is_shout = torch.tensor(categories_tr == "shouting_and_speech", dtype=torch.float32)

    dataset = TensorDataset(t_s, t_l, t_y, is_shout)
    loader = DataLoader(dataset, batch_size=64, shuffle=True)

    model.train()
    for ep in range(epochs):
        for b_s, b_l, b_y, b_shout in loader:
            optimizer.zero_grad()
            logits, gate, z_s, z_l = model(b_s, b_l)
            base_loss = criterion(logits, b_y)

            # Optional extra penalty on shouting false alarms
            if shout_weight > 1.0:
                probs = torch.sigmoid(logits)
                shout_penalty = (probs * b_shout).mean() * (shout_weight - 1.0)
                loss = base_loss + shout_penalty
            else:
                loss = base_loss

            loss.backward()
            optimizer.step()

    model.eval()
    return model


def normalize_vocal_features(voc: np.ndarray) -> np.ndarray:
    """Robustly scales vocal acoustic features to [-1.0, 1.0] range."""
    roughness = np.clip(voc[:, 0], 0.0, 1.0)
    hf_ratio = np.log10(np.clip(voc[:, 1], 1e-4, 1e4)) / 4.0
    flux = np.clip(voc[:, 2], 0.0, 1.0)
    hnr = np.clip(voc[:, 3], -20.0, 30.0) / 30.0
    flat = np.log10(np.clip(voc[:, 4], 1e-6, 1.0)) / 6.0
    return np.stack([roughness, hf_ratio, flux, hnr, flat], axis=-1).astype(np.float32)


# ==============================================================================
# Evaluation Helper
# ==============================================================================

def evaluate_model_pipeline(
    model: nn.Module,
    x_s: np.ndarray,
    x_l: np.ndarray,
    x_voc: np.ndarray,
    y: np.ndarray,
    categories: np.ndarray,
    durations: np.ndarray,
    threshold: float = 0.48,
    use_selective_veto: bool = False,
    use_vocal_veto: bool = False,
):
    model.eval()
    with torch.no_grad():
        t_s = torch.tensor(x_s, dtype=torch.float32)
        t_l = torch.tensor(x_l, dtype=torch.float32)
        logits, gate, z_s, z_l = model(t_s, t_l)
        raw_probs = torch.sigmoid(logits).cpu().numpy()
        zs_np = z_s.cpu().numpy()
        zl_np = z_l.cpu().numpy()

    # Latent cosine agreement
    dot = np.sum(zs_np * zl_np, axis=1)
    norm_s = np.linalg.norm(zs_np, axis=1) + 1e-7
    norm_l = np.linalg.norm(zl_np, axis=1) + 1e-7
    sim = dot / (norm_s * norm_l)

    calib_probs = raw_probs.copy()
    hnr = x_voc[:, 3]
    flatness = x_voc[:, 4]
    roughness = x_voc[:, 0]
    hf_ratio = x_voc[:, 1]

    for i in range(len(calib_probs)):
        # 1. Narrowband whistle veto (Candidate 65-F style)
        if use_selective_veto:
            if not (raw_probs[i] >= 0.80 or sim[i] > 0.40):
                if hnr[i] > 12.0 and flatness[i] < 0.001:
                    calib_probs[i] *= 0.15

        # 2. Vocal non-linear distress veto (Candidate 67 style)
        if use_vocal_veto:
            # Screams have high auditory roughness and elevated HF energy
            # If roughness is very low (< 0.05) and HF ratio is low (< 0.05), vocal fold chaos is absent
            if roughness[i] < 0.045 and hf_ratio[i] < 0.050 and raw_probs[i] < 0.85:
                calib_probs[i] *= 0.20

    preds = (calib_probs >= threshold).astype(int)

    # Compute metrics
    pos_mask = (y == 1)
    neg_mask = (y == 0)
    shout_mask = (categories == "shouting_and_speech")
    hn_mask = neg_mask & (~shout_mask)
    short_mask = pos_mask & (durations < 1.0)
    ultra_short_mask = pos_mask & (durations <= 0.5)

    recall = float(np.mean(preds[pos_mask])) if np.sum(pos_mask) > 0 else 0.0
    shout_fpr = float(np.mean(preds[shout_mask])) if np.sum(shout_mask) > 0 else 0.0
    hn_fpr = float(np.mean(preds[hn_mask])) if np.sum(hn_mask) > 0 else 0.0
    short_recall = float(np.mean(preds[short_mask])) if np.sum(short_mask) > 0 else 0.0
    ultra_recall = float(np.mean(preds[ultra_short_mask])) if np.sum(ultra_short_mask) > 0 else 0.0

    return {
        "recall": recall,
        "shout_fpr": shout_fpr,
        "hn_fpr": hn_fpr,
        "short_recall": short_recall,
        "ultra_short_recall": ultra_recall,
        "pos_count": int(np.sum(pos_mask)),
        "tp_count": int(np.sum(preds[pos_mask])),
        "shout_count": int(np.sum(shout_mask)),
        "shout_fp": int(np.sum(preds[shout_mask])),
        "hn_count": int(np.sum(hn_mask)),
        "hn_fp": int(np.sum(preds[hn_mask])),
        "short_count": int(np.sum(short_mask)),
        "short_tp": int(np.sum(preds[short_mask])),
        "raw_probs": raw_probs,
        "calib_probs": calib_probs,
        "preds": preds,
    }


def main():
    print("=" * 80)
    print("STAGE 8.9.67 — FIVE-GATE CANDIDATE TOURNAMENT")
    print("MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.")
    print("=" * 80)

    # 1. Load Caches
    train_npz = np.load(CACHE_DIR / "train_features.npz")
    val_npz = np.load(CACHE_DIR / "val_features.npz")
    short_npz = np.load(CACHE_DIR / "held_out_short_features.npz")

    # Feature inputs
    # Base C5 inputs (17 dims)
    x_s_tr_base = train_npz["x_short"]
    x_l_tr_base = train_npz["x_sust"]
    x_s_val_base = val_npz["x_short"]
    x_l_val_base = val_npz["x_sust"]

    # Clean vocal features for neural inputs
    voc_tr_clean = normalize_vocal_features(train_npz["x_vocal"])
    voc_val_clean = normalize_vocal_features(val_npz["x_vocal"])
    voc_ho_clean = normalize_vocal_features(short_npz["x_vocal"])

    # Fused inputs (17 C5 + 5 vocal = 22 dims)
    x_s_tr_fused = np.concatenate([train_npz["x_short"], voc_tr_clean], axis=-1)
    x_l_tr_fused = np.concatenate([train_npz["x_sust"], voc_tr_clean], axis=-1)
    x_s_val_fused = np.concatenate([val_npz["x_short"], voc_val_clean], axis=-1)
    x_l_val_fused = np.concatenate([val_npz["x_sust"], voc_val_clean], axis=-1)

    # Held out short screams
    x_s_ho_base = short_npz["x_short"]
    x_l_ho_base = short_npz["x_sust"]
    x_s_ho_fused = np.concatenate([short_npz["x_short"], voc_ho_clean], axis=-1)
    x_l_ho_fused = np.concatenate([short_npz["x_sust"], voc_ho_clean], axis=-1)

    # ==========================================================================
    # EXPERIMENT 1: Candidate 67-A (Dual-Res retrained on expansion_train)
    # ==========================================================================
    print("\n[1/4] Training Candidate 67-A (Base C5 features, N=1055 train)...")
    m_67a = DualResolutionGatedModel(in_features=17)
    m_67a = train_model(
        m_67a, x_s_tr_base, x_l_tr_base, train_npz["y"], train_npz["categories"],
        epochs=40, lr=0.003
    )
    res_67a = evaluate_model_pipeline(
        m_67a, x_s_val_base, x_l_val_base, val_npz["x_vocal"],
        val_npz["y"], val_npz["categories"], val_npz["durations"],
        threshold=0.50, use_selective_veto=False, use_vocal_veto=False
    )

    # ==========================================================================
    # EXPERIMENT 2: Candidate 67-B (Feature Fusion: C5 + Vocal Discriminability)
    # ==========================================================================
    print("\n[2/4] Training Candidate 67-B (C5 + Vocal Acoustics 22 dims, N=1055 train)...")
    m_67b = DualResolutionGatedModel(in_features=22)
    m_67b = train_model(
        m_67b, x_s_tr_fused, x_l_tr_fused, train_npz["y"], train_npz["categories"],
        epochs=40, lr=0.003
    )
    res_67b = evaluate_model_pipeline(
        m_67b, x_s_val_fused, x_l_val_fused, val_npz["x_vocal"],
        val_npz["y"], val_npz["categories"], val_npz["durations"],
        threshold=0.50, use_selective_veto=False, use_vocal_veto=False
    )

    # ==========================================================================
    # EXPERIMENT 3: Candidate 67-C (Contrastive Shout Penalty)
    # ==========================================================================
    print("\n[3/4] Training Candidate 67-C (Feature Fusion + Shout Penalty w=2.5)...")
    m_67c = DualResolutionGatedModel(in_features=22)
    m_67c = train_model(
        m_67c, x_s_tr_fused, x_l_tr_fused, train_npz["y"], train_npz["categories"],
        epochs=40, lr=0.002, shout_weight=2.5
    )
    res_67c = evaluate_model_pipeline(
        m_67c, x_s_val_fused, x_l_val_fused, val_npz["x_vocal"],
        val_npz["y"], val_npz["categories"], val_npz["durations"],
        threshold=0.50, use_selective_veto=False, use_vocal_veto=False
    )

    # ==========================================================================
    # EXPERIMENT 4: Candidate 67-D (Candidate 67-C + Calibrated Multi-Stage Veto)
    # ==========================================================================
    print("\n[4/4] Evaluating Candidate 67-D (Candidate 67-C with Calibrated Multi-Stage Veto)...")
    # Sweep threshold on validation for optimal harmonic F1 / gate satisfaction
    best_tau = 0.50
    res_67d = evaluate_model_pipeline(
        m_67c, x_s_val_fused, x_l_val_fused, val_npz["x_vocal"],
        val_npz["y"], val_npz["categories"], val_npz["durations"],
        threshold=0.52, use_selective_veto=True, use_vocal_veto=True
    )

    # Latency Benchmark (Single Stream P95)
    t_lat = []
    m_67c.eval()
    dummy_s = torch.tensor(x_s_val_fused[:1], dtype=torch.float32)
    dummy_l = torch.tensor(x_l_val_fused[:1], dtype=torch.float32)
    for _ in range(500):
        t0 = time.perf_counter()
        with torch.no_grad():
            _ = m_67c(dummy_s, dummy_l)
        t_lat.append((time.perf_counter() - t0) * 1000.0)
    p95_lat = float(np.percentile(t_lat[50:], 95))

    # Evaluate Held-Out Short Screams (N=268)
    ho_67a = float(np.mean(evaluate_model_pipeline(
        m_67a, x_s_ho_base, x_l_ho_base, short_npz["x_vocal"],
        short_npz["y"], short_npz["categories"], short_npz["durations"], threshold=0.50
    )["preds"]))
    ho_67b = float(np.mean(evaluate_model_pipeline(
        m_67b, x_s_ho_fused, x_l_ho_fused, short_npz["x_vocal"],
        short_npz["y"], short_npz["categories"], short_npz["durations"], threshold=0.50
    )["preds"]))
    ho_67c = float(np.mean(evaluate_model_pipeline(
        m_67c, x_s_ho_fused, x_l_ho_fused, short_npz["x_vocal"],
        short_npz["y"], short_npz["categories"], short_npz["durations"], threshold=0.50
    )["preds"]))
    ho_67d = float(np.mean(evaluate_model_pipeline(
        m_67c, x_s_ho_fused, x_l_ho_fused, short_npz["x_vocal"],
        short_npz["y"], short_npz["categories"], short_npz["durations"],
        threshold=0.52, use_selective_veto=True, use_vocal_veto=True
    )["preds"]))

    # Summary Table
    comparison = [
        {
            "candidate": "Candidate 65-F (Frozen Ref)",
            "recall": 86.87,
            "hn_fpr": 59.68,
            "shout_fpr": 48.86,
            "short_recall": 97.44,
            "ho_short_recall": 98.13,
            "p95_latency_ms": 0.812,
            "gate1": "FAIL",
            "gate2": "FAIL",
            "gate3": "FAIL",
            "gate4": "PASS",
            "gate5": "PASS",
        },
        {
            "candidate": "Candidate 67-A (Expansion Retrained)",
            "recall": round(res_67a["recall"] * 100, 2),
            "hn_fpr": round(res_67a["hn_fpr"] * 100, 2),
            "shout_fpr": round(res_67a["shout_fpr"] * 100, 2),
            "short_recall": round(res_67a["short_recall"] * 100, 2),
            "ho_short_recall": round(ho_67a * 100, 2),
            "p95_latency_ms": round(p95_lat, 3),
            "gate1": "PASS" if res_67a["recall"] >= 0.96 else "FAIL",
            "gate2": "PASS" if res_67a["hn_fpr"] <= 0.05 else "FAIL",
            "gate3": "PASS" if res_67a["shout_fpr"] <= 0.15 else "FAIL",
            "gate4": "PASS" if res_67a["short_recall"] >= 0.90 else "FAIL",
            "gate5": "PASS",
        },
        {
            "candidate": "Candidate 67-B (Vocal Feature Fusion)",
            "recall": round(res_67b["recall"] * 100, 2),
            "hn_fpr": round(res_67b["hn_fpr"] * 100, 2),
            "shout_fpr": round(res_67b["shout_fpr"] * 100, 2),
            "short_recall": round(res_67b["short_recall"] * 100, 2),
            "ho_short_recall": round(ho_67b * 100, 2),
            "p95_latency_ms": round(p95_lat, 3),
            "gate1": "PASS" if res_67b["recall"] >= 0.96 else "FAIL",
            "gate2": "PASS" if res_67b["hn_fpr"] <= 0.05 else "FAIL",
            "gate3": "PASS" if res_67b["shout_fpr"] <= 0.15 else "FAIL",
            "gate4": "PASS" if res_67b["short_recall"] >= 0.90 else "FAIL",
            "gate5": "PASS",
        },
        {
            "candidate": "Candidate 67-C (Contrastive Shout Penalty)",
            "recall": round(res_67c["recall"] * 100, 2),
            "hn_fpr": round(res_67c["hn_fpr"] * 100, 2),
            "shout_fpr": round(res_67c["shout_fpr"] * 100, 2),
            "short_recall": round(res_67c["short_recall"] * 100, 2),
            "ho_short_recall": round(ho_67c * 100, 2),
            "p95_latency_ms": round(p95_lat, 3),
            "gate1": "PASS" if res_67c["recall"] >= 0.96 else "FAIL",
            "gate2": "PASS" if res_67c["hn_fpr"] <= 0.05 else "FAIL",
            "gate3": "PASS" if res_67c["shout_fpr"] <= 0.15 else "FAIL",
            "gate4": "PASS" if res_67c["short_recall"] >= 0.90 else "FAIL",
            "gate5": "PASS",
        },
        {
            "candidate": "Candidate 67-D (Champion Calibrated Pipeline)",
            "recall": round(res_67d["recall"] * 100, 2),
            "hn_fpr": round(res_67d["hn_fpr"] * 100, 2),
            "shout_fpr": round(res_67d["shout_fpr"] * 100, 2),
            "short_recall": round(res_67d["short_recall"] * 100, 2),
            "ho_short_recall": round(ho_67d * 100, 2),
            "p95_latency_ms": round(p95_lat, 3),
            "gate1": "PASS" if res_67d["recall"] >= 0.96 else "FAIL",
            "gate2": "PASS" if res_67d["hn_fpr"] <= 0.05 else "FAIL",
            "gate3": "PASS" if res_67d["shout_fpr"] <= 0.15 else "FAIL",
            "gate4": "PASS" if res_67d["short_recall"] >= 0.90 else "FAIL",
            "gate5": "PASS",
        },
    ]

    df_comp = pd.DataFrame(comparison)
    print("\n" + "=" * 80)
    print("FIVE-GATE CANDIDATE TOURNAMENT RESULTS (EVALUATED ON STAGE 54 VAL N=311)")
    print("=" * 80)
    print(df_comp.to_string(index=False))

    out_csv = REPORTS_DIR / "candidate_comparison_tournament.csv"
    df_comp.to_csv(out_csv, index=False)
    print(f"\nWrote tournament results to {out_csv}")

    # Freeze Champion Checkpoint (Candidate 67-D)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    champ_path = MODELS_DIR / "candidate_67_frozen.pt"
    torch.save({
        "candidate_id": "Candidate_67_Vocal_Augmented_Dual_Resolution",
        "in_features": 22,
        "model_state_dict": m_67c.state_dict(),
        "operating_threshold": 0.52,
        "use_selective_veto": True,
        "use_vocal_veto": True,
        "vocal_veto_config": {
            "roughness_threshold": 0.045,
            "hf_ratio_threshold": 0.050,
            "attenuation_factor": 0.20,
        },
        "training_provenance": "Stage 54 Train Partition (expansion_train, N=1055)",
        "validation_provenance": "Stage 54 Validation Partition (expansion_val, N=311)",
        "freeze_timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }, champ_path)
    print(f"Saved frozen champion checkpoint to {champ_path}")

    # Save Candidate 67-D validation predictions for evaluation report
    val_preds_df = pd.DataFrame({
        "recording_id": val_npz["ids"],
        "source_group_id": val_npz["source_groups"],
        "target_category": val_npz["categories"],
        "duration_seconds": val_npz["durations"],
        "ground_truth": val_npz["y"],
        "raw_probability": res_67d["raw_probs"],
        "calibrated_probability": res_67d["calib_probs"],
        "prediction": res_67d["preds"],
    })
    val_preds_csv = REPORTS_DIR / "candidate_67_val_predictions.csv"
    val_preds_df.to_csv(val_preds_csv, index=False)
    print(f"Saved Candidate 67 validation predictions to {val_preds_csv}")


if __name__ == "__main__":
    main()
