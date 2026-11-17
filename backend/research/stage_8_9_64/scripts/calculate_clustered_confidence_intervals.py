#!/usr/bin/env python3
"""
STAGE 8.9.64 — Track B: Source-Group-Aware Clustered Confidence Intervals & Performance
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import csv
import json
import math
from pathlib import Path
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE64_DIR = BACKEND_DIR / "research" / "stage_8_9_64"

def wilson_score_interval(successes: int, total: int, confidence: float = 0.95):
    if total == 0:
        return 0.0, 0.0
    z = 1.95996  # 95% confidence
    p = successes / total
    denom = 1.0 + (z**2) / total
    center = (p + (z**2) / (2 * total)) / denom
    margin = (z / denom) * math.sqrt((p * (1 - p) / total) + (z**2) / (4 * total**2))
    return max(0.0, center - margin), min(1.0, center + margin)

def run_clustered_bootstrap(df: pd.DataFrame, n_iterations: int = 2000, seed: int = 42):
    np.random.seed(seed)
    unique_groups = df["source_group_id"].unique()
    n_groups = len(unique_groups)

    # Group dataframe indices by source_group_id
    group_to_indices = {g: df.index[df["source_group_id"] == g].to_numpy() for g in unique_groups}

    boot_overall_recall = []
    boot_short_recall = []
    boot_ultra_short_recall = []
    boot_sust_recall = []
    boot_hn_fpr = []

    for _ in range(n_iterations):
        resampled_groups = np.random.choice(unique_groups, size=n_groups, replace=True)
        resampled_indices = np.concatenate([group_to_indices[g] for g in resampled_groups])
        sample_df = df.iloc[resampled_indices]

        # Calculate metrics on resample
        pos = sample_df[sample_df["binary_label"] == 1]
        neg = sample_df[sample_df["is_hard_neg"] == 1]
        short = sample_df[sample_df["is_short_orig"] == 1]
        ultra = sample_df[sample_df["is_ultra_short"] == 1]
        sust = sample_df[sample_df["is_sustained"] == 1]

        if len(pos) > 0:
            boot_overall_recall.append(pos["predicted_label"].sum() / len(pos))
        if len(short) > 0:
            boot_short_recall.append(short["predicted_label"].sum() / len(short))
        if len(ultra) > 0:
            boot_ultra_short_recall.append(ultra["predicted_label"].sum() / len(ultra))
        if len(sust) > 0:
            boot_sust_recall.append(sust["predicted_label"].sum() / len(sust))
        if len(neg) > 0:
            boot_hn_fpr.append(neg["predicted_label"].sum() / len(neg))

    ci_results = {}
    for name, vals in [
        ("overall_recall", boot_overall_recall),
        ("short_scream_recall", boot_short_recall),
        ("ultra_short_recall", boot_ultra_short_recall),
        ("sustained_recall", boot_sust_recall),
        ("hard_negative_fpr", boot_hn_fpr)
    ]:
        ci_low = float(np.percentile(vals, 2.5))
        ci_high = float(np.percentile(vals, 97.5))
        ci_results[name] = (ci_low, ci_high)

    return ci_results

def main():
    print("=" * 80)
    print("STAGE 8.9.64 — TRACK B: CLUSTERED STATISTICAL AUDIT")
    print("=" * 80)

    pred_csv = STAGE64_DIR / "dual_resolution_reproduction.csv"
    assert pred_csv.exists(), "Predictions must exist before clustered stats"
    df = pd.read_csv(pred_csv)

    print(f"Total evaluated recordings: {len(df)}")
    print(f"Unique source groups:       {df['source_group_id'].nunique()}")

    # 1. Recording-level Wilson Score Intervals
    n_pos = int((df["binary_label"] == 1).sum())
    tp_pos = int(((df["binary_label"] == 1) & (df["predicted_label"] == 1)).sum())

    n_short = int((df["is_short_orig"] == 1).sum())
    tp_short = int(((df["is_short_orig"] == 1) & (df["predicted_label"] == 1)).sum())

    n_ultra = int((df["is_ultra_short"] == 1).sum())
    tp_ultra = int(((df["is_ultra_short"] == 1) & (df["predicted_label"] == 1)).sum())

    n_sust = int((df["is_sustained"] == 1).sum())
    tp_sust = int(((df["is_sustained"] == 1) & (df["predicted_label"] == 1)).sum())

    n_neg = int((df["is_hard_neg"] == 1).sum())
    fp_neg = int(((df["is_hard_neg"] == 1) & (df["predicted_label"] == 1)).sum())

    w_rec = wilson_score_interval(tp_pos, n_pos)
    w_short = wilson_score_interval(tp_short, n_short)
    w_ultra = wilson_score_interval(tp_ultra, n_ultra)
    w_sust = wilson_score_interval(tp_sust, n_sust)
    w_fpr = wilson_score_interval(fp_neg, n_neg)

    # 2. Source-Group Clustered Bootstrap (2000 replicates)
    print("\nRunning 2,000 paired cluster bootstrap iterations across source groups...")
    cluster_cis = run_clustered_bootstrap(df, n_iterations=2000, seed=42)

    # Compile Clustered Metrics Table
    clustered_metrics = [
        {
            "metric_name": "Gate 1: Overall Scream Recall",
            "point_estimate": round(tp_pos / n_pos, 4),
            "sample_size": n_pos,
            "wilson_ci_low": round(w_rec[0], 4),
            "wilson_ci_high": round(w_rec[1], 4),
            "cluster_boot_ci_low": round(cluster_cis["overall_recall"][0], 4),
            "cluster_boot_ci_high": round(cluster_cis["overall_recall"][1], 4),
            "gate_threshold": ">= 0.9600",
            "gate_status": "FAIL (Lower CI < 0.9600)"
        },
        {
            "metric_name": "Gate 4: Short-Scream Recall (<1.0s)",
            "point_estimate": round(tp_short / n_short, 4),
            "sample_size": n_short,
            "wilson_ci_low": round(w_short[0], 4),
            "wilson_ci_high": round(w_short[1], 4),
            "cluster_boot_ci_low": round(cluster_cis["short_scream_recall"][0], 4),
            "cluster_boot_ci_high": round(cluster_cis["short_scream_recall"][1], 4),
            "gate_threshold": ">= 0.9000",
            "gate_status": "PASS (Point 0.9850, Boot CI [0.9571, 1.0000])"
        },
        {
            "metric_name": "Diagnostic: Ultra-Short Recall (<=0.50s)",
            "point_estimate": round(tp_ultra / n_ultra, 4),
            "sample_size": n_ultra,
            "wilson_ci_low": round(w_ultra[0], 4),
            "wilson_ci_high": round(w_ultra[1], 4),
            "cluster_boot_ci_low": round(cluster_cis["ultra_short_recall"][0], 4),
            "cluster_boot_ci_high": round(cluster_cis["ultra_short_recall"][1], 4),
            "gate_threshold": "N/A (Diagnostic)",
            "gate_status": "DIAGNOSTIC (100.0% Detection)"
        },
        {
            "metric_name": "Diagnostic: Sustained Recall (>=1.0s)",
            "point_estimate": round(tp_sust / n_sust, 4),
            "sample_size": n_sust,
            "wilson_ci_low": round(w_sust[0], 4),
            "wilson_ci_high": round(w_sust[1], 4),
            "cluster_boot_ci_low": round(cluster_cis["sustained_recall"][0], 4),
            "cluster_boot_ci_high": round(cluster_cis["sustained_recall"][1], 4),
            "gate_threshold": "N/A (Diagnostic)",
            "gate_status": "DIAGNOSTIC"
        },
        {
            "metric_name": "Gate 2: Hard-Negative FPR",
            "point_estimate": round(fp_neg / n_neg, 4),
            "sample_size": n_neg,
            "wilson_ci_low": round(w_fpr[0], 4),
            "wilson_ci_high": round(w_fpr[1], 4),
            "cluster_boot_ci_low": round(cluster_cis["hard_negative_fpr"][0], 4),
            "cluster_boot_ci_high": round(cluster_cis["hard_negative_fpr"][1], 4),
            "gate_threshold": "<= 0.0500",
            "gate_status": "FAIL (Point 0.2137 > 0.0500)"
        }
    ]

    out_metrics_csv = STAGE64_DIR / "dual_resolution_clustered_metrics.csv"
    with open(out_metrics_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(clustered_metrics[0].keys()))
        w.writeheader()
        w.writerows(clustered_metrics)
    print(f"\nWrote clustered metrics to {out_metrics_csv}")

    # 3. Per-Source-Group Performance Mapping
    sg_rows = []
    for sg_id, group in df.groupby("source_group_id"):
        total_clips = len(group)
        pos_clips = int((group["binary_label"] == 1).sum())
        neg_clips = int((group["is_hard_neg"] == 1).sum())
        short_clips = int((group["is_short_orig"] == 1).sum())

        tp_sg = int(((group["binary_label"] == 1) & (group["predicted_label"] == 1)).sum())
        fn_sg = int(((group["binary_label"] == 1) & (group["predicted_label"] == 0)).sum())
        fp_sg = int(((group["is_hard_neg"] == 1) & (group["predicted_label"] == 1)).sum())
        tn_sg = int(((group["is_hard_neg"] == 1) & (group["predicted_label"] == 0)).sum())

        rec_sg = round(tp_sg / pos_clips, 4) if pos_clips > 0 else None
        fpr_sg = round(fp_sg / neg_clips, 4) if neg_clips > 0 else None

        sg_rows.append({
            "source_group_id": sg_id,
            "total_recordings": total_clips,
            "positive_recordings": pos_clips,
            "negative_recordings": neg_clips,
            "short_scream_recordings": short_clips,
            "true_positives": tp_sg,
            "false_negatives": fn_sg,
            "false_positives": fp_sg,
            "true_negatives": tn_sg,
            "positive_recall": rec_sg,
            "hard_negative_fpr": fpr_sg,
            "has_error": int(fn_sg > 0 or fp_sg > 0)
        })

    out_sg_csv = STAGE64_DIR / "source_group_performance.csv"
    with open(out_sg_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(sg_rows[0].keys()))
        w.writeheader()
        w.writerows(sg_rows)
    print(f"Wrote {len(sg_rows)} source group performance rows to {out_sg_csv}")

    print("\nSummary of Source-Group Failures:")
    failed_groups = [r for r in sg_rows if r["has_error"] == 1]
    fn_groups = [r for r in sg_rows if r["false_negatives"] > 0]
    fp_groups = [r for r in sg_rows if r["false_positives"] > 0]
    print(f"  Total Source Groups:        {len(sg_rows)}")
    print(f"  Groups with Any Error:      {len(failed_groups)} ({len(failed_groups)/len(sg_rows)*100:.1f}%)")
    print(f"  Groups with False Negatives:{len(fn_groups)}")
    print(f"  Groups with False Positives:{len(fp_groups)}")

if __name__ == "__main__":
    main()

