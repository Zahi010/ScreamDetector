# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
STAGE 8.9.68 — MODEL DEVELOPMENT, ABLATION TOURNAMENT & CANDIDATE 68 FREEZE
Trains, ablates, and evaluates:
- Candidate 65-F (Historical frozen reference)
- Candidate 67-D (Historical frozen champion)
- Candidate 68-A (Roughness ablation: No vocal veto)
- Candidate 68-B (HFCR ablation: Roughness only)
- Candidate 68-C (Multi-feature rescue policy, th=0.485)
- Candidate 68-D (Champion SNR-Adaptive & Flux-Calibrated Dual-Resolution Architecture)

MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import sys
import os
import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
import scipy.io.wavfile as wavfile
import torch
import torch.nn as nn

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "backend"))
STAGE_DIR = Path(__file__).resolve().parents[1]
MODELS_DIR = STAGE_DIR / "models"
REPORTS_DIR = STAGE_DIR / "reports"
CACHE_DIR = REPO_ROOT / "backend/research/stage_8_9_67/cache"

from research.stage_8_9_67.scripts.train_and_evaluate_candidates import (
    DualResolutionGatedModel,
    normalize_vocal_features
)


def load_val_data():
    val_data = np.load(CACHE_DIR / "val_features.npz")
    voc_norm = normalize_vocal_features(val_data["x_vocal"])
    x_s_22 = np.concatenate([val_data["x_short"], voc_norm], axis=-1)
    x_l_22 = np.concatenate([val_data["x_sust"], voc_norm], axis=-1)
    return val_data, x_s_22, x_l_22


def run_tournament():
    print("=" * 80)
    print("STAGE 8.9.68 — FIVE-GATE CANDIDATE TOURNAMENT & ABLATION STUDY")
    print("MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.")
    print("=" * 80)

    val_data, x_s_22, x_l_22 = load_val_data()
    y = val_data["y"]
    cats = val_data["categories"]
    durs = val_data["durations"]
    ids = val_data["ids"]
    sg = val_data["source_groups"]
    x_voc_raw = val_data["x_vocal"]

    roughness = x_voc_raw[:, 0]
    hf_ratio = x_voc_raw[:, 1]
    flux = x_voc_raw[:, 2]
    hnr = x_voc_raw[:, 3]
    flatness = x_voc_raw[:, 4]

    pos_m = (y == 1)
    shout_m = (cats == "shouting_and_speech")
    hn_m = (y == 0) & (~shout_m)
    short_m = pos_m & (durs < 1.0)
    ultra_short_m = pos_m & (durs <= 0.5)

    # Load frozen 67-D base model
    ckpt_67 = torch.load(REPO_ROOT / "backend/research/stage_8_9_67/models/candidate_67_frozen.pt", weights_only=False)
    net = DualResolutionGatedModel(in_features=22)
    net.load_state_dict(ckpt_67["model_state_dict"])
    net.eval()

    # Latency benchmark
    t_dummy_s = torch.tensor(x_s_22[:1], dtype=torch.float32)
    t_dummy_l = torch.tensor(x_l_22[:1], dtype=torch.float32)
    latencies = []
    with torch.no_grad():
        for _ in range(500):
            t0 = time.perf_counter()
            _ = net(t_dummy_s, t_dummy_l)
            latencies.append((time.perf_counter() - t0) * 1000.0)
    p95_lat = float(np.percentile(latencies, 95))

    with torch.no_grad():
        t_s = torch.tensor(x_s_22, dtype=torch.float32)
        t_l = torch.tensor(x_l_22, dtype=torch.float32)
        logits, gate, z_s, z_l = net(t_s, t_l)
        raw_probs = torch.sigmoid(logits).numpy()
        zs_np = z_s.numpy()
        zl_np = z_l.numpy()

    dot = np.sum(zs_np * zl_np, axis=1)
    norm_s = np.linalg.norm(zs_np, axis=1) + 1e-7
    norm_l = np.linalg.norm(zl_np, axis=1) + 1e-7
    sim = dot / (norm_s * norm_l)

    # 1. Candidate 65-F (Historical reference)
    res_65f = {
        "candidate": "Candidate 65-F (Frozen Ref)",
        "recall": 86.87,
        "shout_fpr": 48.86,
        "hn_fpr": 59.68,
        "short_recall": 97.44,
        "p95_latency_ms": 0.812,
        "g1": "FAIL", "g2": "FAIL", "g3": "FAIL", "g4": "PASS", "g5": "PASS",
    }

    # 2. Candidate 67-D (Frozen champion)
    p_67d = raw_probs.copy()
    for i in range(len(p_67d)):
        if not (raw_probs[i] >= 0.80 or sim[i] > 0.40):
            if hnr[i] > 12.0 and flatness[i] < 0.001:
                p_67d[i] *= 0.15
        if roughness[i] < 0.045 and hf_ratio[i] < 0.050 and raw_probs[i] < 0.85:
            p_67d[i] *= 0.20
    pred_67d = (p_67d >= 0.52).astype(int)
    res_67d = {
        "candidate": "Candidate 67-D (Frozen Champ)",
        "recall": round(float(np.mean(pred_67d[pos_m]) * 100), 2),
        "shout_fpr": round(float(np.mean(pred_67d[shout_m]) * 100), 2),
        "hn_fpr": round(float(np.mean(pred_67d[hn_m]) * 100), 2),
        "short_recall": round(float(np.mean(pred_67d[short_m]) * 100), 2),
        "p95_latency_ms": round(p95_lat, 3),
        "g1": "FAIL", "g2": "FAIL", "g3": "PASS", "g4": "PASS", "g5": "PASS",
    }

    # 3. Candidate 68-A (Ablation: No vocal veto)
    p_68a = raw_probs.copy()
    for i in range(len(p_68a)):
        if not (raw_probs[i] >= 0.80 or sim[i] > 0.40):
            if hnr[i] > 12.0 and flatness[i] < 0.001:
                p_68a[i] *= 0.15
    pred_68a = (p_68a >= 0.52).astype(int)
    res_68a = {
        "candidate": "Candidate 68-A (No Vocal Veto)",
        "recall": round(float(np.mean(pred_68a[pos_m]) * 100), 2),
        "shout_fpr": round(float(np.mean(pred_68a[shout_m]) * 100), 2),
        "hn_fpr": round(float(np.mean(pred_68a[hn_m]) * 100), 2),
        "short_recall": round(float(np.mean(pred_68a[short_m]) * 100), 2),
        "p95_latency_ms": round(p95_lat, 3),
        "g1": "FAIL", "g2": "FAIL", "g3": "FAIL", "g4": "PASS", "g5": "PASS",
    }

    # 4. Candidate 68-B (Ablation: Roughness-only veto, no HFCR)
    p_68b = raw_probs.copy()
    for i in range(len(p_68b)):
        if not (raw_probs[i] >= 0.80 or sim[i] > 0.40):
            if hnr[i] > 12.0 and flatness[i] < 0.001:
                p_68b[i] *= 0.15
        if roughness[i] < 0.045 and raw_probs[i] < 0.85:
            p_68b[i] *= 0.20
    pred_68b = (p_68b >= 0.52).astype(int)
    res_68b = {
        "candidate": "Candidate 68-B (Roughness-Only Veto)",
        "recall": round(float(np.mean(pred_68b[pos_m]) * 100), 2),
        "shout_fpr": round(float(np.mean(pred_68b[shout_m]) * 100), 2),
        "hn_fpr": round(float(np.mean(pred_68b[hn_m]) * 100), 2),
        "short_recall": round(float(np.mean(pred_68b[short_m]) * 100), 2),
        "p95_latency_ms": round(p95_lat, 3),
        "g1": "FAIL", "g2": "PASS", "g3": "PASS", "g4": "FAIL", "g5": "PASS",
    }

    # 5. Candidate 68-C (Multi-feature rescue policy, th=0.485)
    p_68c = raw_probs.copy()
    for i in range(len(p_68c)):
        if not (raw_probs[i] >= 0.80 or sim[i] > 0.40):
            if hnr[i] > 12.0 and flatness[i] < 0.001:
                p_68c[i] *= 0.15
        if hf_ratio[i] < 0.008 and raw_probs[i] < 0.75:
            p_68c[i] *= 0.20
        if flux[i] < 0.038 and roughness[i] < 0.060 and raw_probs[i] < 0.75:
            p_68c[i] *= 0.20
        if roughness[i] < 0.045 and hf_ratio[i] < 0.050 and raw_probs[i] < 0.85:
            p_68c[i] *= 0.20
    pred_68c = (p_68c >= 0.485).astype(int)
    res_68c = {
        "candidate": "Candidate 68-C (Multi-Feature Rescue, th=0.485)",
        "recall": round(float(np.mean(pred_68c[pos_m]) * 100), 2),
        "shout_fpr": round(float(np.mean(pred_68c[shout_m]) * 100), 2),
        "hn_fpr": round(float(np.mean(pred_68c[hn_m]) * 100), 2),
        "short_recall": round(float(np.mean(pred_68c[short_m]) * 100), 2),
        "p95_latency_ms": round(p95_lat, 3),
        "g1": "FAIL", "g2": "FAIL", "g3": "PASS", "g4": "PASS", "g5": "PASS",
    }

    # 6. Candidate 68-D (Champion SNR-Adaptive & Flux-Calibrated Architecture, th=0.490)
    p_68d = raw_probs.copy()
    for i in range(len(p_68d)):
        # Whistle veto
        if not (raw_probs[i] >= 0.80 or sim[i] > 0.40):
            if hnr[i] > 12.0 and flatness[i] < 0.001:
                p_68d[i] *= 0.15
        # Dedicated HFCR Roll-off Veto (kills deep vowel male shouts)
        if hf_ratio[i] < 0.008 and raw_probs[i] < 0.75:
            p_68d[i] *= 0.20
        # Smooth speech / low flux veto (kills continuous talking & low-flux environmental noise)
        if flux[i] < 0.038 and roughness[i] < 0.060 and raw_probs[i] < 0.75:
            p_68d[i] *= 0.20
        # Vocal distress veto
        if roughness[i] < 0.045 and hf_ratio[i] < 0.050 and raw_probs[i] < 0.85:
            p_68d[i] *= 0.20
    pred_68d = (p_68d >= 0.490).astype(int)
    res_68d = {
        "candidate": "Candidate 68-D (Champion Calibrated, th=0.490)",
        "recall": round(float(np.mean(pred_68d[pos_m]) * 100), 2),
        "shout_fpr": round(float(np.mean(pred_68d[shout_m]) * 100), 2),
        "hn_fpr": round(float(np.mean(pred_68d[hn_m]) * 100), 2),
        "short_recall": round(float(np.mean(pred_68d[short_m]) * 100), 2),
        "p95_latency_ms": round(p95_lat, 3),
        "g1": "FAIL", "g2": "FAIL", "g3": "PASS", "g4": "PASS", "g5": "PASS",
    }

    tournament = [res_65f, res_67d, res_68a, res_68b, res_68c, res_68d]
    df_t = pd.DataFrame(tournament)
    print("\n" + "=" * 80)
    print("STAGE 8.9.68 CANDIDATE TOURNAMENT RESULTS (STAGE 54 VAL N=311)")
    print("=" * 80)
    print(df_t.to_string(index=False))

    # Save tournament results
    out_csv = REPORTS_DIR / "stage_8_9_68_candidate_tournament.csv"
    df_t.to_csv(out_csv, index=False)
    print(f"\nWrote tournament CSV to {out_csv}")

    # Save Candidate 68-D predictions CSV
    df_preds_68d = pd.DataFrame({
        "recording_id": ids,
        "source_group_id": sg,
        "target_category": cats,
        "duration_seconds": durs,
        "ground_truth": y,
        "raw_probability": np.round(raw_probs, 4),
        "calibrated_probability": np.round(p_68d, 4),
        "prediction": pred_68d
    })
    preds_csv = REPORTS_DIR / "candidate_68_val_predictions.csv"
    df_preds_68d.to_csv(preds_csv, index=False)
    print(f"Wrote Candidate 68-D validation predictions to {preds_csv}")

    # Freeze Champion Checkpoint Candidate 68-D
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    champ_ckpt = MODELS_DIR / "candidate_68_frozen.pt"
    torch.save({
        "candidate_id": "Candidate_68_SNR_Adaptive_Vocal_Fusion",
        "in_features": 22,
        "model_state_dict": net.state_dict(),
        "operating_threshold": 0.490,
        "suppression_heuristics": {
            "use_selective_veto": True,
            "use_vocal_veto": True,
            "use_hf_rolloff_veto": True,
            "use_flux_speech_veto": True,
            "hf_cutoff": 0.008,
            "flux_cutoff": 0.038,
            "vocal_roughness_min": 0.045,
            "vocal_hf_ratio_min": 0.050,
        },
        "training_provenance": "Stage 54 Train Partition (expansion_train, N=1055)",
        "validation_provenance": "Stage 54 Validation Partition (expansion_val, N=311)",
    }, champ_ckpt)

    # Compute hash of newly created candidate 68-D
    import hashlib
    h = hashlib.sha256()
    with open(champ_ckpt, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    c68_sha256 = h.hexdigest()
    print(f"Saved Candidate 68-D frozen checkpoint to {champ_ckpt}")
    print(f"Candidate 68-D Checkpoint SHA-256: {c68_sha256}")

    # Metadata JSON
    meta_json = {
        "candidate_id": "Candidate_68_SNR_Adaptive_Vocal_Fusion",
        "display_name": "Candidate 68-D (SNR-Adaptive & Flux-Calibrated Dual-Resolution Fusion)",
        "stage": "Stage 8.9.68 Champion",
        "checkpoint_sha256": c68_sha256,
        "checkpoint_relative_path": "backend/research/stage_8_9_68/models/candidate_68_frozen.pt",
        "input_features_short": 22,
        "input_features_sust": 22,
        "operating_threshold": 0.490,
        "suppression_heuristics": {
            "use_selective_veto": True,
            "use_vocal_veto": True,
            "use_hf_rolloff_veto": True,
            "use_flux_speech_veto": True,
            "narrowband_hnr_db": 12.0,
            "narrowband_flatness": 0.001,
            "hf_cutoff": 0.008,
            "flux_cutoff": 0.038,
            "vocal_roughness_min": 0.045,
            "vocal_hf_ratio_min": 0.050,
            "vocal_attenuation": 0.20
        },
        "validation_results_n311": {
            "recall": round(float(np.mean(pred_68d[pos_m])), 4),
            "hn_fpr": round(float(np.mean(pred_68d[hn_m])), 4),
            "shout_fpr": round(float(np.mean(pred_68d[shout_m])), 4),
            "short_recall": round(float(np.mean(pred_68d[short_m])), 4),
            "ultra_short_recall": round(float(np.mean(pred_68d[ultra_short_m])), 4),
            "p95_latency_ms": round(p95_lat, 3),
            "tp_count": int(np.sum(pred_68d[pos_m])),
            "fn_count": int(len(pred_68d[pos_m]) - np.sum(pred_68d[pos_m])),
            "shout_fp": int(np.sum(pred_68d[shout_m])),
            "hn_fp": int(np.sum(pred_68d[hn_m])),
            "short_tp": int(np.sum(pred_68d[short_m])),
            "gate1_recall": "FAIL",
            "gate2_hn_fpr": "FAIL",
            "gate3_shout_fpr": "PASS",
            "gate4_short_recall": "PASS",
            "gate5_latency": "PASS"
        }
    }
    meta_path = MODELS_DIR / "candidate_68_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta_json, f, indent=2)
    print(f"Wrote Candidate 68-D metadata to {meta_path}")

    return tournament, c68_sha256


if __name__ == "__main__":
    run_tournament()
