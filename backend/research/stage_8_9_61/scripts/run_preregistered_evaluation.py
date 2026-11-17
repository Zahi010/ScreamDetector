#!/usr/bin/env python3
"""
STAGE 8.9.61 — Preregistered Independent Evaluation Script (N=700)
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
Executes the preregistered evaluation benchmark on the unsealed cohort.
"""

import hashlib
import json
import math
import os
import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
import scipy.stats as stats
import soundfile as sf
import torch
import torch.nn as nn
import torch.nn.functional as F

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE54_DIR = BACKEND_DIR / "research" / "stage_8_9_54"
STAGE44_DIR = BACKEND_DIR / "research" / "stage_8_9_44"
STAGE49_DIR = BACKEND_DIR / "research" / "stage_8_9_49"
STAGE57_DIR = BACKEND_DIR / "research" / "stage_8_9_57"
STAGE60_DIR = BACKEND_DIR / "research" / "stage_8_9_60"
STAGE61_DIR = BACKEND_DIR / "research" / "stage_8_9_61"
EXP_DIR = STAGE61_DIR / "rolling_window_experiments"

sys.path.insert(0, str(STAGE49_DIR / "scripts"))
from whistle_discriminator import apply_intervention_d

def sha256_file(path_str: str) -> str:
    sha = hashlib.sha256()
    with open(path_str, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()

# Candidate E Dual-Branch Classifier
class ResearchDualHeadClassifier(nn.Module):
    def __init__(self, sem_dim=1024, acoust_dim=6, subband_dim=11):
        super().__init__()
        self.sem_proj = nn.Sequential(nn.Linear(sem_dim, 128), nn.ReLU(), nn.Dropout(0.20))
        self.acoust_proj = nn.Sequential(nn.Linear(acoust_dim * 2 + subband_dim, 64), nn.ReLU(), nn.Dropout(0.15))
        self.gate = nn.Sequential(nn.Linear(128 + 64, 32), nn.Sigmoid())
        self.classifier = nn.Sequential(nn.Linear(128 + 64, 64), nn.ReLU(), nn.Linear(64, 1))
    def forward(self, x_sem, x_acoust, mask_acoust, x_subband):
        z_s = self.sem_proj(x_sem)
        acoust_combined = torch.cat([torch.nan_to_num(x_acoust, nan=0.0), mask_acoust, x_subband], dim=-1)
        z_a = self.acoust_proj(acoust_combined)
        fused = torch.cat([z_s, z_a], dim=-1)
        return self.classifier(fused).squeeze(-1)

# Candidate B Dual-Encoder Classifier
class SemanticProjectionHead(nn.Module):
    def __init__(self, in_dim=1024, hidden_dim=256, proj_dim=128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.15),
            nn.Linear(hidden_dim, proj_dim)
        )
    def forward(self, x):
        return F.normalize(self.net(x), p=2, dim=-1)

class PhonationMaskedHead(nn.Module):
    def __init__(self, in_dim=6, hidden_dim=64, proj_dim=32):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim * 2, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.10),
            nn.Linear(hidden_dim, proj_dim)
        )
    def forward(self, x_acoust, mask_acoust):
        x_safe = torch.nan_to_num(x_acoust, nan=0.0)
        combined = torch.cat([x_safe, mask_acoust], dim=-1)
        return F.normalize(self.net(combined), p=2, dim=-1)

class DualEncoderAcousticModel(nn.Module):
    def __init__(self, sem_dim=1024, acoustic_dim=6, proj_sem=128, proj_acoust=32):
        super().__init__()
        self.sem_head = SemanticProjectionHead(sem_dim, 256, proj_sem)
        self.acoust_head = PhonationMaskedHead(acoustic_dim, 64, proj_acoust)
        self.fusion = nn.Sequential(
            nn.Linear(proj_sem + proj_acoust, 64),
            nn.ReLU(),
            nn.Dropout(0.10),
            nn.Linear(64, 1)
        )
    def forward(self, x_sem, x_acoust, mask_acoust):
        z_sem = self.sem_head(x_sem)
        z_acoust = self.acoust_head(x_acoust, mask_acoust)
        fused = torch.cat([z_sem, z_acoust], dim=-1)
        return self.fusion(fused).squeeze(-1)

def wilson_ci(k, n, confidence=0.95):
    if n == 0:
        return 0.0, 0.0
    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    spread = z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denom
    return max(0.0, centre - spread), min(1.0, centre + spread)

def main():
    print("=" * 80)
    print("STAGE 8.9.61: TRACK B PREREGISTERED INDEPENDENT EVALUATION (N=700)")
    print("=" * 80)
    
    # 1. Cryptographic pre-flight checks
    manifest_p = STAGE60_DIR / "future_evaluation_manifest.json"
    prereg_p = STAGE61_DIR / "independent_evaluation_preregistration.md"
    freeze_p = STAGE61_DIR / "rolling_window_candidate_freeze.json"
    e1_ckpt_p = STAGE54_DIR / "training" / "candidate_e_v954_weighted.pt"
    b_ckpt_p = STAGE44_DIR / "models" / "config_b_mask.pt"
    d_code_p = STAGE49_DIR / "scripts" / "whistle_discriminator.py"
    c5_dsp_p = STAGE57_DIR / "dsp_implementations" / "c5_combined.py"
    
    assert sha256_file(str(manifest_p)) == "9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd"
    assert sha256_file(str(freeze_p)) == "a56982b014e12697982d927c917f1039de35c72b1dc20a1c9ac61dc74e2275df"
    assert sha256_file(str(e1_ckpt_p)) == "37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564"
    assert sha256_file(str(b_ckpt_p)) == "f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378"
    assert sha256_file(str(d_code_p)) == "3d98aa7496c6ba89066cfa345a6d0c1ee3605c30821f869a049001c4ad4a8bd2"
    assert sha256_file(str(c5_dsp_p)) == "d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58"
    print("All cryptographic pre-flight checks passed.")
    
    # 2. Load models
    model_e1 = ResearchDualHeadClassifier(sem_dim=1024, acoust_dim=6, subband_dim=11)
    model_e1.load_state_dict(torch.load(e1_ckpt_p, map_location="cpu", weights_only=True))
    model_e1.eval()
    
    model_b = DualEncoderAcousticModel(sem_dim=1024, acoustic_dim=6, proj_sem=128, proj_acoust=32)
    model_b.load_state_dict(torch.load(b_ckpt_p, map_location="cpu", weights_only=True))
    model_b.eval()
    print("Candidate E1 and Candidate B checkpoints loaded successfully.")
    
    # 3. Load feature container
    feat_npz = EXP_DIR / "sealed_cohort_features.npz"
    if not feat_npz.exists():
        print(f"Error: {feat_npz} missing! Run extract_sealed_cohort_features.py first.")
        return
        
    container = np.load(feat_npz, allow_pickle=True)
    features_dict = container["data"].item()
    print(f"Loaded features for {len(features_dict)} sealed recordings.")
    assert len(features_dict) == 700, "Sealed cohort must contain exactly 700 recordings!"
    
    # 4. Run Inference for all 4 Candidates
    # Formulate recording predictions
    rec_keys = list(features_dict.keys())
    
    # Static Candidate E1
    # Candidate B
    # Candidate B + Intervention D
    # Rolling Candidate E1 EMA
    
    candidate_predictions = {
        "Candidate_E1_Static_C5": {"preds": [], "probs": []},
        "Candidate_B_Baseline": {"preds": [], "probs": []},
        "Candidate_B_Intervention_D": {"preds": [], "probs": []},
        "Candidate_E1_Rolling_C5_EMA": {"preds": [], "probs": []}
    }
    
    recording_meta = []
    
    with torch.no_grad():
        for k in rec_keys:
            v = features_dict[k]
            y_true = v["binary_label"]
            sg = v["source_group_id"]
            cat = v["target_category"]
            subcat = v["subcategory"]
            dur = v["duration"]
            rel_p = v["workspace_audio_path"]
            
            recording_meta.append({
                "recording_id": k,
                "source_group_id": sg,
                "binary_label": y_true,
                "target_category": cat,
                "subcategory": subcat,
                "duration_seconds": dur
            })
            
            # --- Candidate 1: Candidate E1 Static C5 (Center 1.0s window, theta=0.6800) ---
            s_stat = torch.from_numpy(v["sem_static"]).unsqueeze(0)
            a_stat = torch.from_numpy(v["acoust_static"]).unsqueeze(0)
            m_stat = torch.from_numpy(v["mask_static"]).unsqueeze(0)
            sb_stat = torch.from_numpy(v["subband_static"]).unsqueeze(0)
            
            logit_e1_stat = model_e1(s_stat, a_stat, m_stat, sb_stat).item()
            prob_e1_stat = float(1.0 / (1.0 + np.exp(-logit_e1_stat)))
            pred_e1_stat = int(prob_e1_stat >= 0.6800)
            candidate_predictions["Candidate_E1_Static_C5"]["probs"].append(prob_e1_stat)
            candidate_predictions["Candidate_E1_Static_C5"]["preds"].append(pred_e1_stat)
            
            # --- Candidate 2: Candidate B Baseline (theta=0.8000) ---
            logit_b = model_b(s_stat, a_stat, m_stat).item()
            prob_b = float(1.0 / (1.0 + np.exp(-logit_b)))
            pred_b = int(prob_b >= 0.8000)
            candidate_predictions["Candidate_B_Baseline"]["probs"].append(prob_b)
            candidate_predictions["Candidate_B_Baseline"]["preds"].append(pred_b)
            
            # --- Candidate 3: Candidate B + Intervention D ---
            # Run Intervention D on raw audio
            audio_path = REPO_ROOT / rel_p
            raw_audio, sr_raw = sf.read(str(audio_path))
            if raw_audio.ndim > 1:
                raw_audio = np.mean(raw_audio, axis=1)
            pred_b_d, status_d, _ = apply_intervention_d(raw_audio, prob_b, pred_b, sr=sr_raw)
            candidate_predictions["Candidate_B_Intervention_D"]["probs"].append(prob_b)
            candidate_predictions["Candidate_B_Intervention_D"]["preds"].append(int(pred_b_d))
            
            # --- Candidate 4: Candidate E1 Rolling C5 EMA (alpha=0.50, theta=0.6000) ---
            s_roll = torch.from_numpy(v["sem_rolling"])
            a_roll = torch.from_numpy(v["acoust_rolling"])
            m_roll = torch.from_numpy(v["mask_rolling"])
            sb_roll = torch.from_numpy(v["subband_rolling"])
            
            logits_roll = model_e1(s_roll, a_roll, m_roll, sb_roll).numpy()
            if logits_roll.ndim == 0:
                logits_roll = np.array([logits_roll])
            probs_roll = 1.0 / (1.0 + np.exp(-logits_roll))
            
            # EMA aggregation: z_t = 0.5 * p_t + 0.5 * z_{t-1}
            alpha = 0.50
            z = probs_roll[0]
            ema_scores = [z]
            for p in probs_roll[1:]:
                z = alpha * p + (1.0 - alpha) * z
                ema_scores.append(z)
            agg_score_ema = float(max(ema_scores))
            pred_e1_roll = int(agg_score_ema >= 0.6000)
            candidate_predictions["Candidate_E1_Rolling_C5_EMA"]["probs"].append(agg_score_ema)
            candidate_predictions["Candidate_E1_Rolling_C5_EMA"]["preds"].append(pred_e1_roll)
            
    # 5. Build recording-level prediction table
    pred_table_rows = []
    cand_info = {
        "Candidate_E1_Static_C5": {
            "checkpoint_sha256": "37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564",
            "dsp_sha256": "d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58",
            "threshold": 0.6800,
            "window_duration": 1.0,
            "hop_duration": 1.0,
            "strategy": "static_center_window"
        },
        "Candidate_B_Baseline": {
            "checkpoint_sha256": "f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378",
            "dsp_sha256": "f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378",
            "threshold": 0.8000,
            "window_duration": 1.0,
            "hop_duration": 1.0,
            "strategy": "static_center_window"
        },
        "Candidate_B_Intervention_D": {
            "checkpoint_sha256": "f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378",
            "dsp_sha256": "3d98aa7496c6ba89066cfa345a6d0c1ee3605c30821f869a049001c4ad4a8bd2",
            "threshold": 0.8000,
            "window_duration": 1.0,
            "hop_duration": 1.0,
            "strategy": "static_center_window_with_whistle_rejection"
        },
        "Candidate_E1_Rolling_C5_EMA": {
            "checkpoint_sha256": "37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564",
            "dsp_sha256": "d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58",
            "threshold": 0.6000,
            "window_duration": 1.0,
            "hop_duration": 0.5,
            "strategy": "rolling_window_ema_alpha_0_5"
        }
    }
    
    for c_name, c_data in candidate_predictions.items():
        info = cand_info[c_name]
        for i, meta in enumerate(recording_meta):
            pred = c_data["preds"][i]
            prob = c_data["probs"][i]
            y = meta["binary_label"]
            pred_table_rows.append({
                "recording_id": meta["recording_id"],
                "source_group_id": meta["source_group_id"],
                "binary_label": y,
                "target_category": meta["target_category"],
                "subcategory": meta["subcategory"],
                "duration_seconds": meta["duration_seconds"],
                "candidate_id": c_name,
                "model_checkpoint_sha256": info["checkpoint_sha256"],
                "dsp_sha256": info["dsp_sha256"],
                "threshold": info["threshold"],
                "window_duration_seconds": info["window_duration"],
                "hop_duration_seconds": info["hop_duration"],
                "aggregation_strategy": info["strategy"],
                "predicted_probability": round(prob, 4),
                "predicted_label": pred,
                "is_correct": int(pred == y)
            })
            
    df_pred_table = pd.DataFrame(pred_table_rows)
    out_preds_csv = STAGE61_DIR / "sealed_cohort_predictions.csv"
    df_pred_table.to_csv(out_preds_csv, index=False)
    print(f"\nSaved sealed cohort predictions to: {out_preds_csv}")
    
    # 6. Compute independent evaluation metrics table
    y_true_all = np.array([m["binary_label"] for m in recording_meta])
    dur_all = np.array([m["duration_seconds"] for m in recording_meta])
    cat_all = np.array([m["target_category"] for m in recording_meta])
    subcat_all = np.array([m["subcategory"] for m in recording_meta])
    
    pos_mask = (y_true_all == 1)
    neg_mask = (y_true_all == 0)
    sustained_mask = pos_mask & (dur_all >= 1.0)
    short_mask = pos_mask & (dur_all < 1.0)
    shout_mask = (cat_all == "shouted_speech")
    
    metric_rows = []
    
    for c_name, c_data in candidate_predictions.items():
        preds = np.array(c_data["preds"])
        probs = np.array(c_data["probs"])
        
        tp = int(np.sum((preds == 1) & (y_true_all == 1)))
        fn = int(np.sum((preds == 0) & (y_true_all == 1)))
        fp = int(np.sum((preds == 1) & (y_true_all == 0)))
        tn = int(np.sum((preds == 0) & (y_true_all == 0)))
        
        rec = tp / 200.0
        fpr = fp / 500.0
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        f1 = 2 * prec * rec / (prec + rec + 1e-9)
        
        sustained_rec = float(np.sum((preds == 1) & sustained_mask) / np.sum(sustained_mask))
        short_rec = float(np.sum((preds == 1) & short_mask) / np.sum(short_mask))
        shout_fpr = float(np.sum((preds == 1) & shout_mask) / np.sum(shout_mask))
        
        rec_ci_l, rec_ci_h = wilson_ci(tp, 200)
        fpr_ci_l, fpr_ci_h = wilson_ci(fp, 500)
        
        metric_rows.append({
            "candidate_id": c_name,
            "total_recordings": 700,
            "tp": tp,
            "fn": fn,
            "fp": fp,
            "tn": tn,
            "overall_recall": round(rec, 4),
            "recall_ci_low": round(rec_ci_l, 4),
            "recall_ci_high": round(rec_ci_h, 4),
            "hard_negative_fpr": round(fpr, 4),
            "fpr_ci_low": round(fpr_ci_l, 4),
            "fpr_ci_high": round(fpr_ci_h, 4),
            "shouted_speech_fpr": round(shout_fpr, 4),
            "precision": round(prec, 4),
            "f1": round(f1, 4),
            "sustained_scream_recall": round(sustained_rec, 4),
            "short_scream_recall": round(short_rec, 4)
        })
        
        print(f"\n{c_name}:")
        print(f"  Overall Recall:     {rec*100:.2f}% ({tp}/200) [95% CI: {rec_ci_l*100:.1f}% - {rec_ci_h*100:.1f}%]")
        print(f"  Sustained Recall:   {sustained_rec*100:.2f}% ({np.sum((preds==1)&sustained_mask)}/{np.sum(sustained_mask)})")
        print(f"  Short Recall:       {short_rec*100:.2f}% ({np.sum((preds==1)&short_mask)}/{np.sum(short_mask)})")
        print(f"  Hard-Negative FPR:  {fpr*100:.2f}% ({fp}/500) [95% CI: {fpr_ci_l*100:.1f}% - {fpr_ci_h*100:.1f}%]")
        print(f"  Shouted-Speech FPR: {shout_fpr*100:.2f}% ({np.sum((preds==1)&shout_mask)}/{np.sum(shout_mask)})")
        print(f"  Precision:          {prec*100:.2f}%")
        print(f"  F1-Score:           {f1*100:.2f}%")
        
    df_metrics = pd.DataFrame(metric_rows)
    out_metrics_csv = STAGE61_DIR / "independent_evaluation_metrics.csv"
    df_metrics.to_csv(out_metrics_csv, index=False)
    print(f"\nSaved independent evaluation metrics to: {out_metrics_csv}")

if __name__ == "__main__":
    main()

