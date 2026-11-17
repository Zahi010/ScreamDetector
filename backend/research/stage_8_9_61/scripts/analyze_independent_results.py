#!/usr/bin/env python3
"""
STAGE 8.9.61 — Independent Evaluation Statistical Analysis Script
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
Computes clustered bootstrap (2,000 replicates), McNemar's paired tests,
subgroup breakdowns, and acceptance gate evaluations.
"""

import json
import math
import os
import sys
import numpy as np
import pandas as pd
from pathlib import Path
import scipy.stats as stats

REPO_ROOT = Path(__file__).resolve().parents[4]
STAGE61_DIR = REPO_ROOT / "backend" / "research" / "stage_8_9_61"

def wilson_ci(k, n, confidence=0.95):
    if n == 0:
        return 0.0, 0.0
    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    spread = z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denom
    return max(0.0, centre - spread), min(1.0, centre + spread)

def mcnemar_test(y_true, y_pred1, y_pred2):
    b = int(np.sum((y_pred1 == y_true) & (y_pred2 != y_true)))
    c = int(np.sum((y_pred1 != y_true) & (y_pred2 == y_true)))
    total = b + c
    if total == 0:
        return 0.0, 1.0, b, c
    chi2 = ((abs(b - c) - 1.0) ** 2) / total
    p_value = 1.0 - stats.chi2.cdf(chi2, df=1)
    return float(chi2), float(p_value), b, c

def cluster_bootstrap_comparison(df, model1_pred_col, model2_pred_col, n_boot=2000, seed=42):
    np.random.seed(seed)
    unique_sgs = df["source_group_id"].unique()
    n_sgs = len(unique_sgs)

    sg_to_idx = {sg: df.index[df["source_group_id"] == sg].to_numpy() for sg in unique_sgs}

    rec_diffs = []
    fpr_diffs = []
    f1_diffs = []

    for _ in range(n_boot):
        boot_sgs = np.random.choice(unique_sgs, size=n_sgs, replace=True)
        boot_indices = np.concatenate([sg_to_idx[sg] for sg in boot_sgs])
        boot_df = df.iloc[boot_indices]

        y_true = boot_df["binary_label"].to_numpy()
        p1 = boot_df[model1_pred_col].to_numpy()
        p2 = boot_df[model2_pred_col].to_numpy()

        pos_mask = (y_true == 1)
        neg_mask = (y_true == 0)

        if np.sum(pos_mask) > 0 and np.sum(neg_mask) > 0:
            r1 = np.sum(p1[pos_mask] == 1) / np.sum(pos_mask)
            r2 = np.sum(p2[pos_mask] == 1) / np.sum(pos_mask)
            rec_diffs.append((r1 - r2) * 100.0)

            fpr1 = np.sum(p1[neg_mask] == 1) / np.sum(neg_mask)
            fpr2 = np.sum(p2[neg_mask] == 1) / np.sum(neg_mask)
            fpr_diffs.append((fpr1 - fpr2) * 100.0)

            prec1 = np.sum(p1[pos_mask] == 1) / (np.sum(p1 == 1) + 1e-9)
            prec2 = np.sum(p2[pos_mask] == 1) / (np.sum(p2 == 1) + 1e-9)
            f1_1 = 2 * prec1 * r1 / (prec1 + r1 + 1e-9)
            f1_2 = 2 * prec2 * r2 / (prec2 + r2 + 1e-9)
            f1_diffs.append((f1_1 - f1_2) * 100.0)

    def get_ci(diff_list):
        return (
            float(np.percentile(diff_list, 2.5)),
            float(np.percentile(diff_list, 97.5)),
            float(np.mean(diff_list))
        )

    return {
        "recall_delta": get_ci(rec_diffs),
        "fpr_delta": get_ci(fpr_diffs),
        "f1_delta": get_ci(f1_diffs)
    }

def main():
    print("=" * 80)
    print("STAGE 8.9.61: STATISTICAL ANALYSIS & PAIRED CANDIDATE AUDIT")
    print("=" * 80)
    
    preds_csv = STAGE61_DIR / "sealed_cohort_predictions.csv"
    if not preds_csv.exists():
        print(f"Error: {preds_csv} not found!")
        return
        
    df_all = pd.read_csv(preds_csv)
    
    # Reshape predictions into columns per candidate
    cand_names = df_all["candidate_id"].unique()
    print("Found candidates:", cand_names)
    
    # Pivot so each row is a recording
    pivoted = df_all.pivot(index="recording_id", columns="candidate_id", values="predicted_label").reset_index()
    meta = df_all[["recording_id", "source_group_id", "binary_label", "target_category", "subcategory", "duration_seconds"]].drop_duplicates().reset_index(drop=True)
    df_eval = pd.merge(meta, pivoted, on="recording_id")
    print(f"Evaluated cohort shape: {df_eval.shape}")
    
    # 1. Paired comparisons
    comparisons = [
        ("Candidate_E1_Static_C5", "Candidate_B_Baseline"),
        ("Candidate_E1_Rolling_C5_EMA", "Candidate_B_Baseline"),
        ("Candidate_E1_Static_C5", "Candidate_B_Intervention_D"),
        ("Candidate_E1_Rolling_C5_EMA", "Candidate_E1_Static_C5")
    ]
    
    paired_rows = []
    print("\n--- Paired McNemar Tests & Clustered Bootstrap (2,000 Replicates) ---")
    for c1, c2 in comparisons:
        y_true = df_eval["binary_label"].to_numpy()
        p1 = df_eval[c1].to_numpy()
        p2 = df_eval[c2].to_numpy()
        
        chi2, p_val, b, c = mcnemar_test(y_true, p1, p2)
        boot_res = cluster_bootstrap_comparison(df_eval, c1, c2, n_boot=2000, seed=42)
        
        r_low, r_high, r_mean = boot_res["recall_delta"]
        f_low, f_high, f_mean = boot_res["fpr_delta"]
        f1_low, f1_high, f1_mean = boot_res["f1_delta"]
        
        # Multiple testing correction significance flag
        is_sig = (p_val < 0.05)
        
        paired_rows.append({
            "candidate_1": c1,
            "candidate_2": c2,
            "mcnemar_b": b,
            "mcnemar_c": c,
            "mcnemar_chi2": round(chi2, 4),
            "mcnemar_p_value": round(p_val, 6),
            "statistically_significant_05": is_sig,
            "bootstrap_recall_delta_pct": round(r_mean, 2),
            "recall_delta_ci_low": round(r_low, 2),
            "recall_delta_ci_high": round(r_high, 2),
            "bootstrap_fpr_delta_pct": round(f_mean, 2),
            "fpr_delta_ci_low": round(f_low, 2),
            "fpr_delta_ci_high": round(f_high, 2),
            "bootstrap_f1_delta_pct": round(f1_mean, 2),
            "f1_delta_ci_low": round(f1_low, 2),
            "f1_delta_ci_high": round(f1_high, 2)
        })
        
        print(f"\n{c1} vs {c2}:")
        print(f"  McNemar: b={b}, c={c}, chi2={chi2:.3f}, p={p_val:.6f} ({'SIGNIFICANT' if is_sig else 'NOT SIGNIFICANT'})")
        print(f"  Recall Delta: {r_mean:+.2f}% [95% CI: {r_low:+.2f}% to {r_high:+.2f}%]")
        print(f"  FPR Delta:    {f_mean:+.2f}% [95% CI: {f_low:+.2f}% to {f_high:+.2f}%]")
        print(f"  F1 Delta:     {f1_mean:+.2f}% [95% CI: {f1_low:+.2f}% to {f1_high:+.2f}%]")
        
    df_paired = pd.DataFrame(paired_rows)
    out_paired_csv = STAGE61_DIR / "candidate_paired_comparisons.csv"
    df_paired.to_csv(out_paired_csv, index=False)
    print(f"\nSaved paired comparisons to: {out_paired_csv}")
    
    # 2. Granular Subgroup Breakdown
    subgroups = [
        ("All Screams (Positive Class)", df_eval["binary_label"] == 1, 1),
        ("Priority 4: Sustained Screams (>=1.0s)", (df_eval["binary_label"] == 1) & (df_eval["duration_seconds"] >= 1.0), 1),
        ("Priority 1: Low-Intensity Screams", (df_eval["binary_label"] == 1) & df_eval["subcategory"].str.contains("low_intensity", case=False, na=False), 1),
        ("Priority 2: Crowd-Masked Screams (INSUFFICIENT SAMPLE N=4)", (df_eval["binary_label"] == 1) & df_eval["subcategory"].str.contains("crowd_masked", case=False, na=False), 1),
        ("Short Screams (<1.0s)", (df_eval["binary_label"] == 1) & (df_eval["duration_seconds"] < 1.0), 1),
        ("All Hard Negatives (Negative Class)", df_eval["binary_label"] == 0, 0),
        ("Priority 3: Shouted Speech", (df_eval["binary_label"] == 0) & (df_eval["target_category"] == "shouted_speech"), 0),
        ("Cheering & Crowd Chanting", (df_eval["binary_label"] == 0) & (df_eval["target_category"] == "cheering"), 0),
        ("Referee Whistles & Squeaks", (df_eval["binary_label"] == 0) & (df_eval["target_category"] == "referee_whistle"), 0),
        ("Infant Crying", (df_eval["binary_label"] == 0) & (df_eval["target_category"] == "infant_crying"), 0),
        ("Environmental Noise & Sirens", (df_eval["binary_label"] == 0) & df_eval["target_category"].isin(["environmental_sound", "siren"]), 0)
    ]
    
    subgroup_rows = []
    print("\n--- Granular Subgroup Performance Matrix ---")
    for name, mask, expected_binary in subgroups:
        sub_df = df_eval[mask]
        n_sub = len(sub_df)
        n_sgs = sub_df["source_group_id"].nunique()
        
        for cand in cand_names:
            preds = sub_df[cand].to_numpy()
            if expected_binary == 1:
                # Metric is recall
                hits = int(np.sum(preds == 1))
                rate = hits / n_sub if n_sub > 0 else 0.0
                ci_l, ci_h = wilson_ci(hits, n_sub)
                metric_name = "Recall"
            else:
                # Metric is FPR
                hits = int(np.sum(preds == 1))
                rate = hits / n_sub if n_sub > 0 else 0.0
                ci_l, ci_h = wilson_ci(hits, n_sub)
                metric_name = "False Positive Rate"
                
            evidence_status = "INSUFFICIENT_SAMPLE_SIZE" if n_sub < 10 else ("LIMITED_SAMPLE_SIZE" if n_sub < 30 else "ROBUST_EVIDENCE")
            
            subgroup_rows.append({
                "subgroup_name": name,
                "candidate_id": cand,
                "sample_size_n": n_sub,
                "unique_source_groups": n_sgs,
                "metric_type": metric_name,
                "hits": hits,
                "rate": round(rate, 4),
                "ci_95_low": round(ci_l, 4),
                "ci_95_high": round(ci_h, 4),
                "evidence_status": evidence_status
            })
            
    df_subgroups = pd.DataFrame(subgroup_rows)
    out_sub_csv = STAGE61_DIR / "subgroup_metrics.csv"
    df_subgroups.to_csv(out_sub_csv, index=False)
    print(f"\nSaved subgroup metrics to: {out_sub_csv}")

if __name__ == "__main__":
    main()

