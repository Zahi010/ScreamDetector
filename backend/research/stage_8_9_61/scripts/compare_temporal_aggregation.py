#!/usr/bin/env python3
"""
STAGE 8.9.61 — Temporal Aggregation Comparison & Development Evaluation Script
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
Evaluates Strategies A, B, C, D, E exclusively on development data.
"""

import json
import math
import os
import sys
import numpy as np
import pandas as pd
from pathlib import Path
import scipy.stats as stats
import torch
import torch.nn as nn

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE54_DIR = BACKEND_DIR / "research" / "stage_8_9_54"
STAGE55_DIR = BACKEND_DIR / "research" / "stage_8_9_55"
STAGE61_DIR = BACKEND_DIR / "research" / "stage_8_9_61"
EXP_DIR = STAGE61_DIR / "rolling_window_experiments"

# Dual-branch Candidate E Architecture
class ResearchDualHeadClassifier(nn.Module):
    def __init__(self, sem_dim=1024, acoust_dim=6, subband_dim=11):
        super().__init__()
        self.sem_proj = nn.Sequential(
            nn.Linear(sem_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.20)
        )
        self.acoust_proj = nn.Sequential(
            nn.Linear(acoust_dim * 2 + subband_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.15)
        )
        self.gate = nn.Sequential(
            nn.Linear(128 + 64, 32),
            nn.Sigmoid()
        )
        self.classifier = nn.Sequential(
            nn.Linear(128 + 64, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )
    def forward(self, x_sem, x_acoust, mask_acoust, x_subband):
        z_s = self.sem_proj(x_sem)
        acoust_combined = torch.cat([torch.nan_to_num(x_acoust, nan=0.0), mask_acoust, x_subband], dim=-1)
        z_a = self.acoust_proj(acoust_combined)
        fused = torch.cat([z_s, z_a], dim=-1)
        logits = self.classifier(fused).squeeze(-1)
        return logits

def wilson_ci(k, n, confidence=0.95):
    if n == 0:
        return 0.0, 0.0
    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    spread = z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denom
    return max(0.0, centre - spread), min(1.0, centre + spread)

def evaluate_strategy_decisions(probs_seq, strategy, theta_base=0.6800):
    """
    Given an array of window probabilities probs_seq = [p_0, p_1, ..., p_{T-1}]:
    Computes aggregate score and binary alert decision for the recording.
    """
    probs = np.array(probs_seq, dtype=np.float32)
    T = len(probs)
    if T == 0:
        return 0.0, 0
        
    if strategy == "Strategy_A_Independent":
        # Any window exceeds theta_base
        agg_score = float(np.max(probs))
        decision = int(agg_score >= theta_base)
        return agg_score, decision
        
    elif strategy == "Strategy_B_Persistence_K2":
        # Requires 2 consecutive windows >= theta_base
        if T == 1:
            agg_score = float(probs[0])
            decision = int(agg_score >= theta_base)
        else:
            consec_pairs = [min(probs[i], probs[i+1]) for i in range(T - 1)]
            agg_score = float(max(consec_pairs))
            decision = int(agg_score >= theta_base)
        return agg_score, decision
        
    elif strategy == "Strategy_C_Hysteresis":
        # Entry threshold = 0.6800, Exit threshold = 0.4000
        # Active state requires persistence of at least 2 windows or strong peak
        theta_high = 0.6800
        theta_low = 0.4000
        state = 0
        active_counts = 0
        max_active_len = 0
        current_len = 0
        
        for p in probs:
            if state == 0:
                if p >= theta_high:
                    state = 1
                    current_len = 1
                    active_counts += 1
            else:
                if p >= theta_low:
                    current_len += 1
                    active_counts += 1
                else:
                    state = 0
                    if current_len > max_active_len:
                        max_active_len = current_len
                    current_len = 0
        if current_len > max_active_len:
            max_active_len = current_len
            
        agg_score = float(np.max(probs))
        # Hysteresis alert registered if entered active state
        decision = int(active_counts > 0)
        return agg_score, decision
        
    elif strategy == "Strategy_D_Rolling_EMA":
        # Exponential moving average: z_t = 0.5 * p_t + 0.5 * z_{t-1}
        alpha = 0.50
        z = probs[0]
        ema_scores = [z]
        for p in probs[1:]:
            z = alpha * p + (1.0 - alpha) * z
            ema_scores.append(z)
        agg_score = float(max(ema_scores))
        theta_ema = 0.6000 # calibrated on dev data
        decision = int(agg_score >= theta_ema)
        return agg_score, decision
        
    elif strategy == "Strategy_E_Max_Window_W2":
        # Bounded max over 2 windows
        agg_score = float(np.max(probs))
        decision = int(agg_score >= theta_base)
        return agg_score, decision
        
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

def main():
    print("=" * 80)
    print("STAGE 8.9.61: TEMPORAL AGGREGATION DEVELOPMENT BENCHMARK")
    print("=" * 80)
    
    # 1. Load model checkpoint
    ckpt_p = STAGE54_DIR / "training" / "candidate_e_v954_weighted.pt"
    assert ckpt_p.exists(), f"Missing checkpoint: {ckpt_p}"
    
    model = ResearchDualHeadClassifier(sem_dim=1024, acoust_dim=6, subband_dim=11)
    model.load_state_dict(torch.load(ckpt_p, map_location="cpu", weights_only=True))
    model.eval()
    print("Candidate E1 model loaded successfully.")
    
    # 2. Load extracted rolling window features
    feat_p = EXP_DIR / "dev_rolling_features.npz"
    if not feat_p.exists():
        print(f"Error: {feat_p} not found! Run extract_dev_rolling_features.py first.")
        return
        
    container = np.load(feat_p, allow_pickle=True)
    results_dict = container["data"].item()
    print(f"Loaded rolling features for {len(results_dict)} development recordings.")
    
    # 3. Compute window-level probabilities for all recordings
    recording_probs = {}
    print("\nRunning Candidate E1 neural network inference on 500 ms rolling hops...")
    with torch.no_grad():
        for rec_id, rec_data in results_dict.items():
            sem = torch.from_numpy(rec_data["sem"]).float()
            ac = torch.from_numpy(rec_data["acoust"]).float()
            mask = torch.from_numpy(rec_data["mask"]).float()
            sb = torch.from_numpy(rec_data["subband"]).float()
            
            logits = model(sem, ac, mask, sb).numpy()
            if logits.ndim == 0:
                logits = np.array([logits])
            probs = 1.0 / (1.0 + np.exp(-logits))
            recording_probs[rec_id] = probs
            
    # 4. Evaluate each aggregation strategy
    strategies = [
        "Strategy_A_Independent",
        "Strategy_B_Persistence_K2",
        "Strategy_C_Hysteresis",
        "Strategy_D_Rolling_EMA",
        "Strategy_E_Max_Window_W2"
    ]
    
    pred_rows = []
    metric_rows = []
    
    rec_keys = list(results_dict.keys())
    y_true = np.array([results_dict[k]["binary_label"] for k in rec_keys], dtype=int)
    sgs = np.array([results_dict[k]["source_group_id"] for k in rec_keys])
    subcats = np.array([results_dict[k]["subcategory"] for k in rec_keys])
    durations = np.array([results_dict[k]["duration"] for k in rec_keys])
    
    pos_mask = (y_true == 1)
    neg_mask = (y_true == 0)
    sustained_mask = pos_mask & (durations >= 1.0)
    short_mask = pos_mask & (durations < 1.0)
    
    n_pos = int(np.sum(pos_mask))
    n_neg = int(np.sum(neg_mask))
    n_sustained = int(np.sum(sustained_mask))
    n_short = int(np.sum(short_mask))
    
    print(f"\nDevelopment Cohort Breakdown:")
    print(f"  Total:     {len(rec_keys)}")
    print(f"  Positives: {n_pos} (Sustained: {n_sustained}, Short: {n_short})")
    print(f"  Negatives: {n_neg}")
    
    for strat in strategies:
        preds = []
        scores = []
        for k in rec_keys:
            p_seq = recording_probs[k]
            score, dec = evaluate_strategy_decisions(p_seq, strat)
            preds.append(dec)
            scores.append(score)
            
            pred_rows.append({
                "recording_id": k,
                "source_group_id": results_dict[k]["source_group_id"],
                "binary_label": results_dict[k]["binary_label"],
                "target_category": results_dict[k]["target_category"],
                "subcategory": results_dict[k]["subcategory"],
                "duration_seconds": results_dict[k]["duration"],
                "strategy": strat,
                "aggregate_score": round(score, 4),
                "predicted_label": dec,
                "is_correct": int(dec == results_dict[k]["binary_label"])
            })
            
        preds = np.array(preds, dtype=int)
        scores = np.array(scores, dtype=np.float32)
        
        # Metrics
        tp = int(np.sum((preds == 1) & (y_true == 1)))
        fn = int(np.sum((preds == 0) & (y_true == 1)))
        fp = int(np.sum((preds == 1) & (y_true == 0)))
        tn = int(np.sum((preds == 0) & (y_true == 0)))
        
        recall = tp / n_pos if n_pos > 0 else 0.0
        fpr = fp / n_neg if n_neg > 0 else 0.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall + 1e-9)
        
        sustained_rec = float(np.sum((preds == 1) & sustained_mask) / n_sustained) if n_sustained > 0 else 0.0
        short_rec = float(np.sum((preds == 1) & short_mask) / n_short) if n_short > 0 else 0.0
        
        rec_ci_low, rec_ci_high = wilson_ci(tp, n_pos)
        fpr_ci_low, fpr_ci_high = wilson_ci(fp, n_neg)
        
        metric_rows.append({
            "strategy": strat,
            "total_recordings": len(rec_keys),
            "tp": tp,
            "fn": fn,
            "fp": fp,
            "tn": tn,
            "recall": round(recall, 4),
            "recall_ci_low": round(rec_ci_low, 4),
            "recall_ci_high": round(rec_ci_high, 4),
            "hard_negative_fpr": round(fpr, 4),
            "fpr_ci_low": round(fpr_ci_low, 4),
            "fpr_ci_high": round(fpr_ci_high, 4),
            "precision": round(precision, 4),
            "f1": round(f1, 4),
            "sustained_scream_recall": round(sustained_rec, 4),
            "short_scream_recall": round(short_rec, 4)
        })
        
        print(f"\n{strat}:")
        print(f"  Recall:        {recall*100:.2f}% ({tp}/{n_pos}) [95% CI: {rec_ci_low*100:.1f}% - {rec_ci_high*100:.1f}%]")
        print(f"  Sustained Rec: {sustained_rec*100:.2f}%")
        print(f"  Short Rec:     {short_rec*100:.2f}%")
        print(f"  Hard-Neg FPR:  {fpr*100:.2f}% ({fp}/{n_neg}) [95% CI: {fpr_ci_low*100:.1f}% - {fpr_ci_high*100:.1f}%]")
        print(f"  Precision:     {precision*100:.2f}%")
        print(f"  F1-Score:      {f1*100:.2f}%")
        
    df_metrics = pd.DataFrame(metric_rows)
    df_preds = pd.DataFrame(pred_rows)
    
    out_metrics = STAGE61_DIR / "temporal_aggregation_metrics.csv"
    out_preds = STAGE61_DIR / "rolling_window_development_predictions.csv"
    
    df_metrics.to_csv(out_metrics, index=False)
    df_preds.to_csv(out_preds, index=False)
    
    print(f"\nSaved metrics to: {out_metrics}")
    print(f"Saved predictions to: {out_preds}")

if __name__ == "__main__":
    main()

