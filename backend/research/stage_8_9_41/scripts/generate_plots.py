"""
Stage 8.9.41: Publication-Quality Research Plots
Generates:
1. plots/recall_confidence_intervals.png
2. plots/duration_stratified_recall.png
3. plots/source_group_performance.png
"""
import os
import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
STAGE41_DIR = REPO_ROOT / "backend" / "research" / "stage_8_9_41"
PLOTS_DIR = STAGE41_DIR / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

# Styling
plt.rcParams.update({
    'font.sans-serif': 'Arial',
    'font.family': 'sans-serif',
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.titlesize': 13,
    'axes.grid': True,
    'grid.alpha': 0.35,
    'grid.linestyle': '--'
})

def plot_recall_confidence_intervals(metrics_data):
    print("Generating recall confidence intervals plot...")
    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=300)

    cohorts = [
        ("Expansion Cohort\n(Stage 8.9.39, N=65)", 1.0, [0.9442, 1.0]),
        ("New Positive Cohort\n(Stage 8.9.41, N=57)", metrics_data["standalone_stage_8_9_41_positive_cohort"]["recall"], metrics_data["standalone_stage_8_9_41_positive_cohort"]["ci95_wilson"]),
        ("Combined Positive Suite\n(Total N=122)", metrics_data["combined_positive_suite"]["recall"], metrics_data["combined_positive_suite"]["ci95_wilson"])
    ]

    y_pos = np.arange(len(cohorts))
    recalls = [c[1] * 100 for c in cohorts]
    err_low = [recalls[i] - c[2][0] * 100 for i, c in enumerate(cohorts)]
    err_high = [c[2][1] * 100 - recalls[i] for i, c in enumerate(cohorts)]

    ax.errorbar(recalls, y_pos, xerr=[err_low, err_high], fmt='o', color='#1f77b4',
                ecolor='#1f77b4', elinewidth=2.5, capsize=6, capthick=1.5, markersize=8)

    ax.axvline(96.0, color='crimson', linestyle='--', linewidth=2, label='Gate 1 Target: Overall Recall ≥ 96.0%')
    ax.axvline(90.0, color='darkorange', linestyle=':', linewidth=1.8, label='Gate 4 Target: Short-Scream Recall ≥ 90.0%')

    ax.set_yticks(y_pos)
    ax.set_yticklabels([c[0] for c in cohorts])
    ax.set_xlabel('Observed Scream Recall (%)')
    ax.set_xlim(20, 105)
    ax.set_title('Stage 8.9.41: Positive Recall & 95% Wilson Confidence Intervals\n[RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE]', fontweight='bold')
    ax.legend(loc='lower left', framealpha=0.95)

    for i, c in enumerate(cohorts):
        val = c[1] * 100
        ci = [c[2][0] * 100, c[2][1] * 100]
        ax.annotate(f"{val:.1f}%\n[{ci[0]:.1f}%, {ci[1]:.1f}%]",
                    xy=(val, y_pos[i]), xytext=(0, 10), textcoords="offset points",
                    ha='center', fontsize=8.5, fontweight='bold', color='#1f77b4')

    plt.tight_layout()
    out_path = PLOTS_DIR / "recall_confidence_intervals.png"
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")

def plot_duration_stratified_recall():
    print("Generating duration-stratified recall plot...")
    dur_csv = STAGE41_DIR / "reports" / "duration_stratified_results.csv"
    df = pd.read_csv(dur_csv)

    fig, ax = plt.subplots(figsize=(8.5, 5), dpi=300)

    x = np.arange(len(df))
    recalls = df["recall"].values * 100
    yerr_low = recalls - df["ci95_low"].values * 100
    yerr_high = df["ci95_high"].values * 100 - recalls

    bars = ax.bar(x, recalls, width=0.45, yerr=[yerr_low, yerr_high], capsize=5,
                  color='#2ca02c', alpha=0.85, edgecolor='black', linewidth=0.8)

    ax.axhline(96.0, color='crimson', linestyle='--', linewidth=1.5, label='Gate 1 Target (≥ 96%)')
    ax.axhline(90.0, color='darkorange', linestyle=':', linewidth=1.5, label='Gate 4 Target (≥ 90%)')

    ax.set_xticks(x)
    labels = [f"{r['stratum']}\n(N={r['total_clips']})" for _, r in df.iterrows()]
    ax.set_xticklabels(labels)
    ax.set_ylabel('Recall (%)')
    ax.set_ylim(-2, 110)
    ax.set_title('Stage 8.9.41: Recall Across Scream Duration Strata\n[RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE]', fontweight='bold')
    ax.legend(loc='upper left', framealpha=0.95)

    for bar, val, frac in zip(bars, recalls, df["fraction"]):
        ax.annotate(f"{val:.1f}%\n({frac})", xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                    xytext=(0, 6), textcoords="offset points", ha='center', fontsize=8.5, fontweight='bold')

    plt.tight_layout()
    out_path = PLOTS_DIR / "duration_stratified_recall.png"
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")

def plot_source_group_performance():
    print("Generating source-group performance plot...")
    sg_csv = STAGE41_DIR / "reports" / "source_group_results.csv"
    df = pd.read_csv(sg_csv)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8), dpi=300)
    fig.suptitle('Stage 8.9.41: Source-Group Detection & Predicted Probability Distribution\n[RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE]', fontweight='bold')

    # Left: Histogram of mean probability per source group
    ax1.hist(df["mean_prob"], bins=15, range=(0.0, 1.0), color='#1f77b4', alpha=0.8, edgecolor='black')
    ax1.axvline(0.24, color='crimson', linestyle='--', linewidth=2, label='Threshold (θ = 0.24)')
    ax1.set_xlabel('Mean Predicted Probability per Source Group')
    ax1.set_ylabel('Number of Source Groups')
    ax1.set_title('Source Group Probability Distribution (N=41)')
    ax1.legend(loc='upper right')

    # Right: Source Group Detection Status
    n_detected = (df["recall"] > 0).sum()
    n_missed = len(df) - n_detected
    wedges, texts, autotexts = ax2.pie(
        [n_detected, n_missed],
        labels=[f'Detected\n({n_detected} SGs, {n_detected/len(df)*100:.1f}%)', f'Missed\n({n_missed} SGs, {n_missed/len(df)*100:.1f}%)'],
        autopct='%1.1f%%',
        colors=['#2ca02c', '#d62728'],
        startangle=140,
        textprops=dict(fontsize=9, fontweight='bold'),
        wedgeprops=dict(edgecolor='black', linewidth=1)
    )
    ax2.set_title('Source Group Level Detection (At Least 1 Clip)')

    plt.tight_layout()
    out_path = PLOTS_DIR / "source_group_performance.png"
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")

def main():
    metrics_path = STAGE41_DIR / "results" / "metrics" / "evaluation_results.json"
    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics_data = json.load(f)

    plot_recall_confidence_intervals(metrics_data)
    plot_duration_stratified_recall()
    plot_source_group_performance()
    print("\nAll publication plots successfully generated.")

if __name__ == "__main__":
    main()

