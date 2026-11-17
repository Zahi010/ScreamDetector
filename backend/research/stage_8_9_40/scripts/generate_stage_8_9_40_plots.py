"""
Stage 8.9.40: Publication-Quality Research Plot Generation
Generates 4 figures in backend/research/stage_8_9_40/plots/:
1. category_fpr_comparison.png
2. roc_pr_curves_multi_cohort.png
3. wilson_ci_comparison.png
4. streaming_latency_distribution.png
"""
import os
import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, precision_recall_curve, auc

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE39_DIR = BACKEND_DIR / "research" / "stage_8_9_39"
STAGE40_DIR = BACKEND_DIR / "research" / "stage_8_9_40"
sys.path.insert(0, str(STAGE39_DIR))

from scripts.train_config_b import DualEncoderAcousticModel
from scripts.train_config_d import MultiPathwayFusionModel

PLOTS_DIR = STAGE40_DIR / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

# Set publication style
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
    'lines.linewidth': 1.8,
    'axes.grid': True,
    'grid.alpha': 0.35,
    'grid.linestyle': '--'
})

def plot_category_fpr(metrics_json_path):
    print("Generating category FPR comparison plot...")
    with open(metrics_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    b_cats = data["candidate_b"]["new_independent_cohort_n145"]["category_metrics"]
    d_cats = data["candidate_d"]["new_independent_cohort_n145"]["category_metrics"]

    categories = list(b_cats.keys())
    cat_labels = [
        "Crowd Chanting\n(N=30)",
        "Environmental\n(N=10)",
        "Infant Crying\n(N=15)",
        "Sirens & SFX\n(N=15)",
        "Shouted Speech\n(N=54)",
        "Whistles\n(N=21)"
    ]

    b_vals = [b_cats[c]["fpr"] * 100 for c in categories]
    d_vals = [d_cats[c]["fpr"] * 100 for c in categories]

    # CI errors
    b_err_low = [b_vals[i] - b_cats[c]["ci95"][0]*100 for i, c in enumerate(categories)]
    b_err_high = [b_cats[c]["ci95"][1]*100 - b_vals[i] for i, c in enumerate(categories)]
    b_err = [b_err_low, b_err_high]

    d_err_low = [d_vals[i] - d_cats[c]["ci95"][0]*100 for i, c in enumerate(categories)]
    d_err_high = [d_cats[c]["ci95"][1]*100 - d_vals[i] for i, c in enumerate(categories)]
    d_err = [d_err_low, d_err_high]

    x = np.arange(len(categories))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    bars1 = ax.bar(x - width/2, b_vals, width, yerr=b_err, capsize=4, label='Config B (DualEncoder, θ=0.24)', color='#1f77b4', alpha=0.88, edgecolor='black', linewidth=0.8)
    bars2 = ax.bar(x + width/2, d_vals, width, yerr=d_err, capsize=4, label='Config D (MultiPathway, θ=0.34)', color='#ff7f0e', alpha=0.88, edgecolor='black', linewidth=0.8)

    ax.axhline(15.0, color='crimson', linestyle=':', linewidth=1.5, label='Gate 3 Target: Shouted Speech FPR ≤ 15%')
    ax.axhline(5.0, color='darkgreen', linestyle='--', linewidth=1.5, label='Gate 2 Target: Overall Hard-Negative FPR ≤ 5%')

    ax.set_ylabel('False Positive Rate (%)')
    ax.set_title('Stage 8.9.40: Category False Positive Rates on New Independent Cohort (N=145)\n[RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE]', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(cat_labels)
    ax.legend(loc='upper right', framealpha=0.95)
    ax.set_ylim(-0.5, 35)

    # Annotate values
    for bar, val in zip(bars1, b_vals):
        if val > 0:
            ax.annotate(f"{val:.1f}%", xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                        xytext=(0, 5), textcoords="offset points", ha='center', va='bottom', fontsize=8, fontweight='bold')
    for bar, val in zip(bars2, d_vals):
        if val > 0:
            ax.annotate(f"{val:.1f}%", xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                        xytext=(0, 5), textcoords="offset points", ha='center', va='bottom', fontsize=8, fontweight='bold')

    plt.tight_layout()
    out_path = PLOTS_DIR / "category_fpr_comparison.png"
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")

def plot_wilson_ci_comparison(metrics_json_path):
    print("Generating Wilson CI comparison plot...")
    with open(metrics_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Metrics to compare:
    # 1. Overall Recall (Exp, N=65) -> Gate 1: >= 96%
    # 2. Hard-Negative FPR (New, N=145) -> Gate 2: <= 5%
    # 3. Shouted Speech FPR (New, N=54) -> Gate 3: <= 15%
    # 4. Short-Scream Recall (Exp, N=65) -> Gate 4: >= 90%
    metrics_info = [
        ("Gate 1: Overall Recall\n(Exp N=65, Target ≥ 96%)", 96.0, "ge",
         data["candidate_b"]["frozen_expansion_cohort_n102"]["scream_recall"],
         data["candidate_d"]["frozen_expansion_cohort_n102"]["scream_recall"]),
        ("Gate 2: Hard-Negative FPR\n(New N=145, Target ≤ 5%)", 5.0, "le",
         data["candidate_b"]["new_independent_cohort_n145"]["hard_negative_fpr"],
         data["candidate_d"]["new_independent_cohort_n145"]["hard_negative_fpr"]),
        ("Gate 3: Shouted-Speech FPR\n(New N=54, Target ≤ 15%)", 15.0, "le",
         data["candidate_b"]["new_independent_cohort_n145"]["category_metrics"]["shouting_and_speech"],
         data["candidate_d"]["new_independent_cohort_n145"]["category_metrics"]["shouting_and_speech"]),
        ("Gate 4: Short-Scream Recall\n(Exp N=65, Target ≥ 90%)", 90.0, "ge",
         data["candidate_b"]["frozen_expansion_cohort_n102"]["short_scream_recall"],
         data["candidate_d"]["frozen_expansion_cohort_n102"]["short_scream_recall"])
    ]

    fig, axes = plt.subplots(1, 4, figsize=(14, 5), dpi=300)
    fig.suptitle('Stage 8.9.40: Research Acceptance Gates & 95% Wilson Score Confidence Intervals\n[RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE]', fontweight='bold')

    def get_val(d):
        for k in ["value", "fpr", "recall"]:
            if k in d and d[k] is not None:
                return float(d[k])
        return 0.0

    for ax, (title, target_val, comp_type, b_stat, d_stat) in zip(axes, metrics_info):
        # Extract values
        b_val = get_val(b_stat) * 100
        b_ci = [b_stat["ci95"][0] * 100, b_stat["ci95"][1] * 100]
        d_val = get_val(d_stat) * 100
        d_ci = [d_stat["ci95"][0] * 100, d_stat["ci95"][1] * 100]

        # Plot point and error bar
        ax.errorbar([0], [b_val], yerr=[[b_val - b_ci[0]], [b_ci[1] - b_val]], fmt='o', color='#1f77b4', ecolor='#1f77b4', elinewidth=2, capsize=6, capthick=1.5, markersize=8, label='Config B')
        ax.errorbar([1], [d_val], yerr=[[d_val - d_ci[0]], [d_ci[1] - d_val]], fmt='s', color='#ff7f0e', ecolor='#ff7f0e', elinewidth=2, capsize=6, capthick=1.5, markersize=8, label='Config D')

        # Target line
        ax.axhline(target_val, color='crimson', linestyle='--', linewidth=1.5, label=f'Target ({target_val}%)')

        ax.set_xticks([0, 1])
        ax.set_xticklabels(['Config B', 'Config D'])
        ax.set_title(title, fontsize=9.5)
        ax.set_ylabel('Percentage (%)')

        if comp_type == 'ge':
            ax.set_ylim(80, 102)
        else:
            ax.set_ylim(-1, 20)

        # Text annotation of CI
        ax.text(0, b_ci[0] - (2 if comp_type=='ge' else -1), f"[{b_ci[0]:.1f}, {b_ci[1]:.1f}]%", ha='center', fontsize=7.5, color='#1f77b4', fontweight='bold')
        ax.text(1, d_ci[0] - (2 if comp_type=='ge' else -1), f"[{d_ci[0]:.1f}, {d_ci[1]:.1f}]%", ha='center', fontsize=7.5, color='#ff7f0e', fontweight='bold')

    axes[0].legend(loc='lower left', fontsize=8)
    plt.tight_layout()
    out_path = PLOTS_DIR / "wilson_ci_comparison.png"
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")

def plot_roc_pr_curves():
    print("Generating ROC and PR curves...")
    # Load Stage 8.9.39 features and splits
    v4_cache = np.load(STAGE39_DIR / "cache" / "stage_8_9_39_features.npz", allow_pickle=True)
    splits = v4_cache['splits']
    exp_idx = np.where(splits == 'v4_reserved_expansion_test')[0]

    y_exp = v4_cache['labels'][exp_idx]

    # Evaluate models on expansion
    ckpt_b = torch.load(STAGE39_DIR / "checkpoints" / "config_b" / "best_model.pt", map_location='cpu')
    model_b = DualEncoderAcousticModel(sem_dim=1024, acoustic_dim=6, proj_sem=128, proj_acoust=32)
    model_b.load_state_dict(ckpt_b['model_state_dict'])
    model_b.eval()

    ckpt_d = torch.load(STAGE39_DIR / "checkpoints" / "config_d" / "best_model.pt", map_location='cpu')
    model_d = MultiPathwayFusionModel(sem_dim=1024, acoust_dim=6, subband_dim=11)
    model_d.load_state_dict(ckpt_d['model_state_dict'])
    model_d.eval()

    t_sem = torch.tensor(v4_cache['X_sem'][exp_idx], dtype=torch.float32)
    t_ac = torch.tensor(v4_cache['X_acoust'][exp_idx], dtype=torch.float32)
    t_m = torch.tensor(v4_cache['mask_acoust'][exp_idx], dtype=torch.float32)
    t_sb = torch.tensor(v4_cache['X_subband'][exp_idx], dtype=torch.float32)

    with torch.no_grad():
        logits_b, _, _ = model_b(t_sem, t_ac, t_m)
        probs_b = torch.sigmoid(logits_b).numpy().flatten()
        logits_d, _, _ = model_d(t_sem, t_ac, t_m, t_sb)
        probs_d = torch.sigmoid(logits_d).numpy().flatten()

    fpr_b, tpr_b, _ = roc_curve(y_exp, probs_b)
    auc_b = auc(fpr_b, tpr_b)
    fpr_d, tpr_d, _ = roc_curve(y_exp, probs_d)
    auc_d = auc(fpr_d, tpr_d)

    prec_b, rec_b, _ = precision_recall_curve(y_exp, probs_b)
    pr_auc_b = auc(rec_b, prec_b)
    prec_d, rec_d, _ = precision_recall_curve(y_exp, probs_d)
    pr_auc_d = auc(rec_d, prec_d)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5), dpi=300)
    fig.suptitle('Stage 8.9.40: Discrimination Performance on Frozen Expansion Cohort (N=102)\n[RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE]', fontweight='bold')

    # ROC
    ax1.plot(fpr_b, tpr_b, label=f'Config B (AUC = {auc_b:.4f})', color='#1f77b4', linewidth=2)
    ax1.plot(fpr_d, tpr_d, label=f'Config D (AUC = {auc_d:.4f})', color='#ff7f0e', linewidth=2, linestyle='--')
    ax1.plot([0, 1], [0, 1], color='gray', linestyle=':', label='Random Guess')
    ax1.set_xlabel('False Positive Rate')
    ax1.set_ylabel('True Positive Rate')
    ax1.set_title('Receiver Operating Characteristic (ROC)')
    ax1.legend(loc='lower right')
    ax1.set_xlim(-0.02, 1.02)
    ax1.set_ylim(-0.02, 1.02)

    # PR
    ax2.plot(rec_b, prec_b, label=f'Config B (PR-AUC = {pr_auc_b:.4f})', color='#1f77b4', linewidth=2)
    ax2.plot(rec_d, prec_d, label=f'Config D (PR-AUC = {pr_auc_d:.4f})', color='#ff7f0e', linewidth=2, linestyle='--')
    ax2.set_xlabel('Recall')
    ax2.set_ylabel('Precision')
    ax2.set_title('Precision-Recall Curve')
    ax2.legend(loc='lower left')
    ax2.set_xlim(-0.02, 1.02)
    ax2.set_ylim(-0.02, 1.02)

    plt.tight_layout()
    out_path = PLOTS_DIR / "roc_pr_curves_multi_cohort.png"
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")

def plot_latency_distribution():
    print("Generating streaming latency distribution plot...")
    deadline_csv = STAGE40_DIR / "results" / "metrics" / "streaming_deadline_results.csv"
    if not deadline_csv.exists():
        print(f"Warning: {deadline_csv} not found, skipping plot.")
        return

    df_lat = pd.read_csv(deadline_csv)
    stage_csv = STAGE40_DIR / "results" / "metrics" / "latency_stage_breakdown.csv"
    df_stages = pd.read_csv(stage_csv) if stage_csv.exists() else None

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=300)
    fig.suptitle('Stage 8.9.40: Streaming Hop Latency & Concurrency Scaling (Deadline = 100 ms)\n[RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE]', fontweight='bold')

    # Left: Concurrency Scaling
    df_b = df_lat[df_lat["candidate"] == "B"]
    df_d = df_lat[df_lat["candidate"] == "D"]

    streams = df_b["concurrent_streams"].values
    ax1.plot(streams, df_b["p50_ms"], 'o-', label='Config B (P50)', color='#1f77b4')
    ax1.plot(streams, df_b["p95_ms"], 'o--', label='Config B (P95)', color='#1f77b4', alpha=0.7)
    ax1.plot(streams, df_d["p50_ms"], 's-', label='Config D (P50)', color='#ff7f0e')
    ax1.plot(streams, df_d["p95_ms"], 's--', label='Config D (P95)', color='#ff7f0e', alpha=0.7)

    ax1.axhline(100.0, color='crimson', linestyle=':', linewidth=2, label='100 ms Hop Deadline')
    ax1.set_xlabel('Concurrent Audio Streams')
    ax1.set_ylabel('Hop Processing Latency (ms)')
    ax1.set_title('Hop Latency vs. Concurrent Streams')
    ax1.set_xticks(streams)
    ax1.legend(loc='upper left', fontsize=8.5)
    ax1.set_ylim(0, 110)

    # Right: Stage Breakdown (Config D - full pipeline)
    if df_stages is not None:
        stage_names = [
            "Ring Buffer", "Normalize", "YAMNet", "Phonation",
            "Subband DSP", "Tensor Conv", "PyTorch Fwd", "Platt Calib", "Decision"
        ]
        # Map rows
        stage_keys = [
            "Stage1_RingBufferWindowing", "Stage2_AudioNormalization", "Stage3_YAMNetInference",
            "Stage4_PhonationSlicing", "Stage5_SubbandFilterbankDSP", "Stage6_TensorConversion_ConfigD",
            "Stage7_ModelForward_ConfigD", "Stage8_PlattCalibration_ConfigD", "Stage9_DecisionLogic_ConfigD"
        ]
        p50s = []
        for k in stage_keys:
            r = df_stages[df_stages["stage_name"] == k]
            p50s.append(r["p50_ms"].values[0] if len(r) > 0 else 0.0)

        y_pos = np.arange(len(stage_names))
        ax2.barh(y_pos, p50s, color='#2ca02c', alpha=0.8, edgecolor='black', linewidth=0.8)
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(stage_names, fontsize=8.5)
        ax2.set_xlabel('Median Latency (ms)')
        ax2.set_title('Full Pipeline 10-Stage Latency Breakdown (Config D)')
        ax2.invert_yaxis()

        for i, v in enumerate(p50s):
            ax2.text(v + 0.1, i, f"{v:.2f} ms", va='center', fontsize=8, fontweight='bold')

    plt.tight_layout()
    out_path = PLOTS_DIR / "streaming_latency_distribution.png"
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")

def main():
    metrics_path = STAGE40_DIR / "results" / "metrics" / "frozen_model_evaluation_results.json"
    if not metrics_path.exists():
        print(f"Error: {metrics_path} does not exist!")
        return

    plot_category_fpr(metrics_path)
    plot_wilson_ci_comparison(metrics_path)
    plot_roc_pr_curves()
    plot_latency_distribution()
    print("\nAll publication plots successfully generated in:", PLOTS_DIR)

if __name__ == "__main__":
    main()
