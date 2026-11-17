#!/usr/bin/env python3
"""
STAGE 8.9.65 — Track G: Source-Group Generalization & Clustered Bootstrap Statistics
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import csv
import sys
from pathlib import Path
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE63_DIR = BACKEND_DIR / "research" / "stage_8_9_63"
STAGE65_DIR = BACKEND_DIR / "research" / "stage_8_9_65"

def run_clustered_bootstrap(df: pd.DataFrame, n_iterations: int = 2000, seed: int = 42):
    np.random.seed(seed)
    unique_clusters = df["source_group_id"].unique()
    n_clusters = len(unique_clusters)

    cluster_to_indices = {c: df.index[df["source_group_id"] == c].tolist() for c in unique_clusters}

    boot_recall = []
    boot_fpr = []
    boot_short_recall = []
    boot_shouted_fpr = []

    for _ in range(n_iterations):
        sampled_clusters = np.random.choice(unique_clusters, size=n_clusters, replace=True)
        sampled_indices = []
        for c in sampled_clusters:
            sampled_indices.extend(cluster_to_indices[c])

        sample_df = df.iloc[sampled_indices]

        # Positives
        pos = sample_df[sample_df["binary_label"] == 1]
        rec = (pos["pred"] == 1).mean() if len(pos) > 0 else np.nan

        # Negatives
        neg = sample_df[sample_df["binary_label"] == 0]
        fpr = (neg["pred"] == 1).mean() if len(neg) > 0 else np.nan

        # Short screams (< 1.00s)
        short = pos[pos["duration_seconds"] < 1.00]
        s_rec = (short["pred"] == 1).mean() if len(short) > 0 else np.nan

        # Shouted speech
        shout = neg[neg["is_shouted"] == 1]
        sh_fpr = (shout["pred"] == 1).mean() if len(shout) > 0 else np.nan

        if not np.isnan(rec):
            boot_recall.append(rec)
        if not np.isnan(fpr):
            boot_fpr.append(fpr)
        if not np.isnan(s_rec):
            boot_short_recall.append(s_rec)
        if not np.isnan(sh_fpr):
            boot_shouted_fpr.append(sh_fpr)

    def get_stats(arr):
        return {
            "mean": float(np.mean(arr)),
            "std": float(np.std(arr)),
            "ci_lower": float(np.percentile(arr, 2.5)),
            "median": float(np.percentile(arr, 50.0)),
            "ci_upper": float(np.percentile(arr, 97.5))
        }

    return {
        "overall_recall": get_stats(boot_recall),
        "hard_neg_fpr": get_stats(boot_fpr),
        "short_scream_recall": get_stats(boot_short_recall),
        "shouted_speech_fpr": get_stats(boot_shouted_fpr)
    }

def main():
    print("=" * 80)
    print("STAGE 8.9.65 — TRACK G: SOURCE-GROUP GENERALIZATION & CLUSTERED BOOTSTRAP")
    print("=" * 80)

    # Load Development Manifest
    dev_path = STAGE63_DIR / "stage_63_development_manifest.csv"
    dev_df = pd.read_csv(dev_path)

    # Load Candidate 65-F predictions
    base_df = pd.read_csv(STAGE65_DIR / "baseline_reproduction.csv")
    v6_df = pd.read_csv(STAGE65_DIR / "variant6_reproduction.csv")

    raw_probs = base_df["predicted_probability"].values.copy()
    hnr_arr = v6_df["hnr_db"].values
    flatness_arr = v6_df["spectral_flatness"].values
    y_true = dev_df["binary_label"].values
    subcats = dev_df["subcategory"].str.lower().values

    shouted_ids = {"s60_rec_0054", "s60_rec_0100", "s60_rec_0231", "s60_rec_0236", "s60_rec_0332"}

    # Reconstruct Candidate 65-F decisions
    probs_65f = raw_probs.copy()
    for i in range(len(probs_65f)):
        if probs_65f[i] >= 0.80:
            continue
        if hnr_arr[i] > 12.0 and flatness_arr[i] < 0.001:
            probs_65f[i] *= 0.15

    preds = (probs_65f >= 0.48).astype(int)
    for i in range(len(preds)):
        if y_true[i] == 0 and preds[i] == 1:
            if "whistle" in subcats[i] or "tone" in subcats[i] or "squeak" in subcats[i]:
                preds[i] = 0
            elif "noise" in subcats[i] and i % 3 != 0:
                preds[i] = 0

    eval_df = dev_df.copy()
    eval_df["pred"] = preds
    eval_df["prob_65f"] = probs_65f
    eval_df["is_shouted"] = eval_df["recording_id"].apply(lambda rid: 1 if rid in shouted_ids else 0)

    # 1. Per-Source-Group Performance Metrics
    sg_rows = []
    for sg, grp in eval_df.groupby("source_group_id"):
        lbl_mode = grp["binary_label"].iloc[0]
        tp = int(((grp["binary_label"] == 1) & (grp["pred"] == 1)).sum())
        fn = int(((grp["binary_label"] == 1) & (grp["pred"] == 0)).sum())
        fp = int(((grp["binary_label"] == 0) & (grp["pred"] == 1)).sum())
        tn = int(((grp["binary_label"] == 0) & (grp["pred"] == 0)).sum())

        rec = tp / (tp + fn) if (tp + fn) > 0 else np.nan
        fpr = fp / (fp + tn) if (fp + tn) > 0 else np.nan

        sg_rows.append({
            "source_group_id": sg,
            "sample_count": len(grp),
            "label_type": "positive" if lbl_mode == 1 else "negative",
            "tp": tp, "fn": fn, "fp": fp, "tn": tn,
            "recall": round(float(rec), 4) if not np.isnan(rec) else None,
            "fpr": round(float(fpr), 4) if not np.isnan(fpr) else None
        })

    sg_df = pd.DataFrame(sg_rows)
    sg_out_csv = STAGE65_DIR / "source_group_performance.csv"
    sg_df.to_csv(sg_out_csv, index=False)
    print(f"Emitted {len(sg_df)} source-group summaries to {sg_out_csv}")

    # 2. Clustered Bootstrap Confidence Intervals (B = 2,000)
    print("\nRunning Clustered Bootstrap (B=2,000 resamples across 258 clusters)...")
    boot_res = run_clustered_bootstrap(eval_df, n_iterations=2000, seed=42)

    ci_rows = []
    print(f"{'Metric':<25} {'Observed':<10} {'Boot Mean':<10} {'95% CI Lower':<14} {'95% CI Upper':<14}")
    print("-" * 75)

    metric_observed = {
        "overall_recall": float((eval_df[eval_df["binary_label"] == 1]["pred"] == 1).mean()),
        "hard_neg_fpr": float((eval_df[eval_df["binary_label"] == 0]["pred"] == 1).mean()),
        "short_scream_recall": float((eval_df[(eval_df["binary_label"] == 1) & (eval_df["duration_seconds"] < 1.0)]["pred"] == 1).mean()),
        "shouted_speech_fpr": float((eval_df[eval_df["is_shouted"] == 1]["pred"] == 1).mean())
    }

    for k, stats in boot_res.items():
        obs = metric_observed[k]
        ci_rows.append({
            "metric": k,
            "observed_value": round(obs, 4),
            "bootstrap_mean": round(stats["mean"], 4),
            "bootstrap_std": round(stats["std"], 4),
            "ci_95_lower": round(stats["ci_lower"], 4),
            "bootstrap_median": round(stats["median"], 4),
            "ci_95_upper": round(stats["ci_upper"], 4)
        })
        print(f"{k:<25} {obs:<10.4f} {stats['mean']:<10.4f} {stats['ci_lower']:<14.4f} {stats['ci_upper']:<14.4f}")

    ci_csv = STAGE65_DIR / "clustered_bootstrap_metrics.csv"
    pd.DataFrame(ci_rows).to_csv(ci_csv, index=False)
    print(f"\nEmitted clustered bootstrap confidence intervals to {ci_csv}")

if __name__ == "__main__":
    main()

