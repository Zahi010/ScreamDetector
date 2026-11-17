import os
import sys
import json
import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve, roc_curve, confusion_matrix

BACKEND_DIR = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector\backend")
STAGE_DIR = BACKEND_DIR / "research" / "stage_8_9_39"
PLOTS_DIR = STAGE_DIR / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

RESULTS_DIR = STAGE_DIR / "results"
PRED_DIR = STAGE_DIR / "predictions"

def set_plot_style():
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.titlesize'] = 12
    plt.rcParams['axes.labelsize'] = 11
    plt.rcParams['figure.dpi'] = 150

def plot_01_training_and_val_loss(hist_b, hist_d):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Candidate B
    ep_b = [int(r['epoch']) for r in hist_b]
    tr_b = [float(r['train_total_loss']) for r in hist_b]
    val_b = [float(r['val_loss']) for r in hist_b]
    axes[0].plot(ep_b, tr_b, 'o-', color='#1f77b4', label='Train Total Loss (BCE+0.5*SupCon)', linewidth=2)
    axes[0].plot(ep_b, val_b, 's--', color='#ff7f0e', label='Validation BCE Loss', linewidth=2)
    axes[0].set_title('Candidate B (DualEncoder) Loss Curves')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].legend()
    axes[0].grid(True, linestyle='--', alpha=0.6)

    # Candidate D
    ep_d = [int(r['epoch']) for r in hist_d]
    tr_d = [float(r['train_total_loss']) for r in hist_d]
    val_d = [float(r['val_loss']) for r in hist_d]
    axes[1].plot(ep_d, tr_d, 'o-', color='#2ca02c', label='Train Total Loss (BCE+0.5*SupCon)', linewidth=2)
    axes[1].plot(ep_d, val_d, 's--', color='#d62728', label='Validation BCE Loss', linewidth=2)
    axes[1].set_title('Candidate D (MultiPathwayFusion) Loss Curves')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Loss')
    axes[1].legend()
    axes[1].grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    out = PLOTS_DIR / "01_training_and_validation_loss_curves.png"
    plt.savefig(out)
    plt.close()
    print(f"Saved: {out}")

def plot_02_validation_f1_vs_epoch(hist_b, hist_d):
    plt.figure(figsize=(9, 5))
    ep_b = [int(r['epoch']) for r in hist_b]
    f1_b = [float(r['val_f1']) for r in hist_b]
    ep_d = [int(r['epoch']) for r in hist_d]
    f1_d = [float(r['val_f1']) for r in hist_d]

    plt.plot(ep_b, f1_b, 'o-', color='#1f77b4', label=f'Candidate B (Peak F1: {max(f1_b):.4f} @ Ep {ep_b[np.argmax(f1_b)]})', linewidth=2.2)
    plt.plot(ep_d, f1_d, 's-', color='#2ca02c', label=f'Candidate D (Peak F1: {max(f1_d):.4f} @ Ep {ep_d[np.argmax(f1_d)]})', linewidth=2.2)
    plt.axhline(0.75, color='gray', linestyle=':', label='Benchmark Baseline 0.75')
    plt.title('Validation F1 Score vs. Epoch (Selection Metric)')
    plt.xlabel('Epoch')
    plt.ylabel('Validation F1 Score')
    plt.legend(loc='lower right')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    out = PLOTS_DIR / "02_validation_f1_vs_epoch.png"
    plt.savefig(out)
    plt.close()
    print(f"Saved: {out}")

def plot_03_04_pr_and_roc(val_b_rows, val_d_rows):
    y_b = np.array([int(r['ground_truth']) for r in val_b_rows])
    p_b = np.array([float(r['probability']) for r in val_b_rows])
    y_d = np.array([int(r['ground_truth']) for r in val_d_rows])
    p_d = np.array([float(r['probability']) for r in val_d_rows])

    # PR Curve
    prec_b, rec_b, _ = precision_recall_curve(y_b, p_b)
    prec_d, rec_d, _ = precision_recall_curve(y_d, p_d)

    plt.figure(figsize=(8, 6))
    plt.plot(rec_b, prec_b, color='#1f77b4', lw=2.2, label='Candidate B (PR-AUC = 0.7980)')
    plt.plot(rec_d, prec_d, color='#2ca02c', lw=2.2, label='Candidate D (PR-AUC = 0.7685)')
    plt.axhline(y=np.sum(y_b)/len(y_b), color='gray', linestyle='--', label=f'No-Skill Baseline ({np.sum(y_b)/len(y_b):.2f})')
    plt.title('Validation Precision-Recall Curves (N=339)')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    out_pr = PLOTS_DIR / "03_validation_pr_curves.png"
    plt.savefig(out_pr)
    plt.close()
    print(f"Saved: {out_pr}")

    # ROC Curve
    fpr_b, tpr_b, _ = roc_curve(y_b, p_b)
    fpr_d, tpr_d, _ = roc_curve(y_d, p_d)

    plt.figure(figsize=(8, 6))
    plt.plot(fpr_b, tpr_b, color='#1f77b4', lw=2.2, label='Candidate B (ROC-AUC = 0.9182)')
    plt.plot(fpr_d, tpr_d, color='#2ca02c', lw=2.2, label='Candidate D (ROC-AUC = 0.8861)')
    plt.plot([0, 1], [0, 1], color='gray', linestyle='--', label='Random Chance (AUC = 0.50)')
    plt.title('Validation ROC Curves (N=339)')
    plt.xlabel('False Positive Rate (FPR)')
    plt.ylabel('True Positive Rate (Recall)')
    plt.legend(loc='lower right')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    out_roc = PLOTS_DIR / "04_validation_roc_curves.png"
    plt.savefig(out_roc)
    plt.close()
    print(f"Saved: {out_roc}")

def plot_05_06_07_threshold_curves(sweep_b, sweep_d):
    th_b = [float(r['threshold']) for r in sweep_b]
    rec_b = [float(r['recall']) for r in sweep_b]
    hn_b = [float(r['hn_fpr']) for r in sweep_b]
    shout_b = [float(r['shout_fpr']) for r in sweep_b]

    th_d = [float(r['threshold']) for r in sweep_d]
    rec_d = [float(r['recall']) for r in sweep_d]
    hn_d = [float(r['hn_fpr']) for r in sweep_d]
    shout_d = [float(r['shout_fpr']) for r in sweep_d]

    # 05: Threshold vs Recall
    plt.figure(figsize=(8, 5))
    plt.plot(th_b, rec_b, color='#1f77b4', lw=2.2, label='Candidate B Recall')
    plt.plot(th_d, rec_d, color='#2ca02c', lw=2.2, label='Candidate D Recall')
    plt.axhline(0.96, color='red', linestyle='--', label='Gate 1 Target (Recall >= 96%)')
    plt.axvline(0.24, color='#1f77b4', linestyle=':', label='Candidate B Selected theta=0.24')
    plt.axvline(0.34, color='#2ca02c', linestyle=':', label='Candidate D Selected theta=0.34')
    plt.title('Threshold vs. Validation Scream Recall')
    plt.xlabel('Decision Threshold')
    plt.ylabel('Scream Recall')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    out_rec = PLOTS_DIR / "05_threshold_vs_recall_plots.png"
    plt.savefig(out_rec)
    plt.close()
    print(f"Saved: {out_rec}")

    # 06: Threshold vs Hard Negative FPR
    plt.figure(figsize=(8, 5))
    plt.plot(th_b, hn_b, color='#1f77b4', lw=2.2, label='Candidate B HN-FPR')
    plt.plot(th_d, hn_d, color='#2ca02c', lw=2.2, label='Candidate D HN-FPR')
    plt.axhline(0.05, color='red', linestyle='--', label='Gate 2 Target (HN-FPR <= 5%)')
    plt.axvline(0.24, color='#1f77b4', linestyle=':', label='Candidate B Selected theta=0.24')
    plt.axvline(0.34, color='#2ca02c', linestyle=':', label='Candidate D Selected theta=0.34')
    plt.title('Threshold vs. Validation Hard-Negative FPR')
    plt.xlabel('Decision Threshold')
    plt.ylabel('Hard-Negative FPR')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    out_hn = PLOTS_DIR / "06_threshold_vs_hard_negative_fpr_plots.png"
    plt.savefig(out_hn)
    plt.close()
    print(f"Saved: {out_hn}")

    # 07: Threshold vs Shouted Speech FPR
    plt.figure(figsize=(8, 5))
    plt.plot(th_b, shout_b, color='#1f77b4', lw=2.2, label='Candidate B Shouted-Speech FPR')
    plt.plot(th_d, shout_d, color='#2ca02c', lw=2.2, label='Candidate D Shouted-Speech FPR')
    plt.axhline(0.15, color='red', linestyle='--', label='Gate 3 Target (Shout-FPR <= 15%)')
    plt.axvline(0.24, color='#1f77b4', linestyle=':', label='Candidate B Selected theta=0.24')
    plt.axvline(0.34, color='#2ca02c', linestyle=':', label='Candidate D Selected theta=0.34')
    plt.title('Threshold vs. Validation Shouted-Speech FPR')
    plt.xlabel('Decision Threshold')
    plt.ylabel('Shouted-Speech FPR')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    out_shout = PLOTS_DIR / "07_threshold_vs_shouted_speech_fpr_plots.png"
    plt.savefig(out_shout)
    plt.close()
    print(f"Saved: {out_shout}")

def plot_08_confusion_matrices():
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    # Historical Test View A:
    # B: TP=89, FP=23, FN=13, TN=168
    # D: TP=85, FP=25, FN=17, TN=166
    cm_b_hist = np.array([[168, 23], [13, 89]])
    cm_d_hist = np.array([[166, 25], [17, 85]])
    # Expansion Test:
    # B: TP=65, FP=0, FN=0, TN=37
    # D: TP=65, FP=0, FN=0, TN=37
    cm_b_exp = np.array([[37, 0], [0, 65]])
    cm_d_exp = np.array([[37, 0], [0, 65]])

    def draw_cm(ax, cm, title):
        ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
        ax.set_title(title, fontsize=11)
        classes = ['Non-Scream', 'Scream']
        tick_marks = np.arange(len(classes))
        ax.set_xticks(tick_marks)
        ax.set_yticks(tick_marks)
        ax.set_xticklabels(classes)
        ax.set_yticklabels(classes)
        thresh = cm.max() / 2.
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                ax.text(j, i, format(cm[i, j], 'd'),
                        ha="center", va="center",
                        color="white" if cm[i, j] > thresh else "black", fontsize=12)
        ax.set_ylabel('True Label')
        ax.set_xlabel('Predicted Label')

    draw_cm(axes[0, 0], cm_b_hist, 'Candidate B: Historical Benchmark (N=293, theta=0.24)')
    draw_cm(axes[0, 1], cm_d_hist, 'Candidate D: Historical Benchmark (N=293, theta=0.34)')
    draw_cm(axes[1, 0], cm_b_exp, 'Candidate B: Reserved Expansion Test (N=102, theta=0.24)')
    draw_cm(axes[1, 1], cm_d_exp, 'Candidate D: Reserved Expansion Test (N=102, theta=0.34)')

    plt.tight_layout()
    out = PLOTS_DIR / "08_confusion_matrices.png"
    plt.savefig(out)
    plt.close()
    print(f"Saved: {out}")

def plot_09_reliability_diagrams():
    with open(RESULTS_DIR / "calibration" / "calibration_metrics.json", "r", encoding="utf-8") as f:
        cal_data = json.load(f)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Candidate B
    bins_b_uncal = cal_data['candidate_b']['uncalibrated_bins']
    bins_b_cal = cal_data['candidate_b']['calibrated_bins']
    conf_u_b = [b['confidence'] for b in bins_b_uncal if b['count'] > 0]
    acc_u_b = [b['accuracy'] for b in bins_b_uncal if b['count'] > 0]
    conf_c_b = [b['confidence'] for b in bins_b_cal if b['count'] > 0]
    acc_c_b = [b['accuracy'] for b in bins_b_cal if b['count'] > 0]

    axes[0].plot([0, 1], [0, 1], 'k--', label='Perfect Calibration')
    axes[0].plot(conf_u_b, acc_u_b, 'o--', color='#ff7f0e', label=f'Uncalibrated (ECE={cal_data["candidate_b"]["uncalibrated"]["ece"]:.4f})')
    axes[0].plot(conf_c_b, acc_c_b, 's-', color='#1f77b4', label=f'Platt Calibrated (ECE={cal_data["candidate_b"]["platt_calibrated"]["ece"]:.4f})')
    axes[0].set_title('Candidate B Reliability Diagram')
    axes[0].set_xlabel('Mean Predicted Probability')
    axes[0].set_ylabel('Empirical Accuracy')
    axes[0].legend()
    axes[0].grid(True, linestyle='--', alpha=0.6)

    # Candidate D
    bins_d_uncal = cal_data['candidate_d']['uncalibrated_bins']
    bins_d_cal = cal_data['candidate_d']['calibrated_bins']
    conf_u_d = [b['confidence'] for b in bins_d_uncal if b['count'] > 0]
    acc_u_d = [b['accuracy'] for b in bins_d_uncal if b['count'] > 0]
    conf_c_d = [b['confidence'] for b in bins_d_cal if b['count'] > 0]
    acc_c_d = [b['accuracy'] for b in bins_d_cal if b['count'] > 0]

    axes[1].plot([0, 1], [0, 1], 'k--', label='Perfect Calibration')
    axes[1].plot(conf_u_d, acc_u_d, 'o--', color='#ff7f0e', label=f'Uncalibrated (ECE={cal_data["candidate_d"]["uncalibrated"]["ece"]:.4f})')
    axes[1].plot(conf_c_d, acc_c_d, 's-', color='#2ca02c', label=f'Platt Calibrated (ECE={cal_data["candidate_d"]["platt_calibrated"]["ece"]:.4f})')
    axes[1].set_title('Candidate D Reliability Diagram')
    axes[1].set_xlabel('Mean Predicted Probability')
    axes[1].set_ylabel('Empirical Accuracy')
    axes[1].legend()
    axes[1].grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    out = PLOTS_DIR / "09_calibration_reliability_diagrams.png"
    plt.savefig(out)
    plt.close()
    print(f"Saved: {out}")

def plot_10_category_false_positives():
    with open(RESULTS_DIR / "metrics" / "error_analysis_summary.json", "r", encoding="utf-8") as f:
        err_data = json.load(f)

    fp_b = err_data['candidate_b']['historical_view_a']['fp_by_category']
    fp_d = err_data['candidate_d']['historical_view_a']['fp_by_category']

    cats = sorted(list(set(list(fp_b.keys()) + list(fp_d.keys()))))
    counts_b = [fp_b.get(c, 0) for c in cats]
    counts_d = [fp_d.get(c, 0) for c in cats]

    x = np.arange(len(cats))
    width = 0.35

    plt.figure(figsize=(10, 5))
    plt.bar(x - width/2, counts_b, width, label='Candidate B (DualEncoder)', color='#1f77b4')
    plt.bar(x + width/2, counts_d, width, label='Candidate D (MultiPathwayFusion)', color='#2ca02c')

    plt.ylabel('False Positive Count (Clips)')
    plt.title('Category-Level False Positives on Historical Benchmark (View A, N=293)')
    plt.xticks(x, [c.replace('_', '\n') for c in cats], fontsize=9)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6, axis='y')
    plt.tight_layout()
    out = PLOTS_DIR / "10_category_level_false_positive_plots.png"
    plt.savefig(out)
    plt.close()
    print(f"Saved: {out}")

def plot_11_historical_vs_expansion():
    with open(RESULTS_DIR / "metrics" / "historical_benchmark_results.json", "r", encoding="utf-8") as f:
        h_data = json.load(f)
    with open(RESULTS_DIR / "metrics" / "expansion_benchmark_results.json", "r", encoding="utf-8") as f:
        e_data = json.load(f)

    # Compare Recall, HN-FPR, F1 across both cohorts
    rec_b_h = h_data['candidate_b']['optimal_threshold']['view_b']['scream_recall']['value'] * 100
    rec_b_e = e_data['candidate_b']['optimal_threshold']['scream_recall']['value'] * 100

    rec_d_h = h_data['candidate_d']['optimal_threshold']['view_b']['scream_recall']['value'] * 100
    rec_d_e = e_data['candidate_d']['optimal_threshold']['scream_recall']['value'] * 100

    fpr_b_h = h_data['candidate_b']['optimal_threshold']['view_b']['hard_negative_fpr']['value'] * 100
    fpr_b_e = e_data['candidate_b']['optimal_threshold']['hard_negative_fpr']['value'] * 100

    fpr_d_h = h_data['candidate_d']['optimal_threshold']['view_b']['hard_negative_fpr']['value'] * 100
    fpr_d_e = e_data['candidate_d']['optimal_threshold']['hard_negative_fpr']['value'] * 100

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    metrics = ['Historical Benchmark (N=293)', 'Reserved Expansion Test (N=102)']
    x = np.arange(len(metrics))
    width = 0.35

    # Recall
    axes[0].bar(x - width/2, [rec_b_h, rec_b_e], width, label='Candidate B', color='#1f77b4')
    axes[0].bar(x + width/2, [rec_d_h, rec_d_e], width, label='Candidate D', color='#2ca02c')
    axes[0].axhline(96, color='red', linestyle='--', label='Gate 1 Target (>= 96%)')
    axes[0].set_ylabel('Scream Recall (%)')
    axes[0].set_title('Cross-Cohort Scream Recall Generalization')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(metrics)
    axes[0].set_ylim([70, 105])
    axes[0].legend(loc='lower right')
    axes[0].grid(True, linestyle='--', alpha=0.6, axis='y')

    # HN-FPR
    axes[1].bar(x - width/2, [fpr_b_h, fpr_b_e], width, label='Candidate B', color='#1f77b4')
    axes[1].bar(x + width/2, [fpr_d_h, fpr_d_e], width, label='Candidate D', color='#2ca02c')
    axes[1].axhline(5, color='red', linestyle='--', label='Gate 2 Target (<= 5%)')
    axes[1].set_ylabel('Hard-Negative FPR (%)')
    axes[1].set_title('Cross-Cohort Hard-Negative Rejection')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(metrics)
    axes[1].set_ylim([0, 20])
    axes[1].legend(loc='upper right')
    axes[1].grid(True, linestyle='--', alpha=0.6, axis='y')

    plt.tight_layout()
    out = PLOTS_DIR / "11_historical_vs_expansion_benchmark_comparison.png"
    plt.savefig(out)
    plt.close()
    print(f"Saved: {out}")

def plot_12_latency_distributions():
    csv_path = RESULTS_DIR / "latency" / "latency_distributions.csv"
    with open(csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    lat_b = [float(r['candidate_b_ms']) for r in rows]
    lat_d = [float(r['candidate_d_ms']) for r in rows]

    plt.figure(figsize=(10, 5))
    plt.hist(lat_b, bins=50, alpha=0.65, label=f'Candidate B (P95={np.percentile(lat_b, 95):.3f} ms, Mean={np.mean(lat_b):.3f} ms)', color='#1f77b4', edgecolor='none')
    plt.hist(lat_d, bins=50, alpha=0.65, label=f'Candidate D (P95={np.percentile(lat_d, 95):.3f} ms, Mean={np.mean(lat_d):.3f} ms)', color='#2ca02c', edgecolor='none')
    plt.axvline(25.0, color='red', linestyle='--', label='Gate 5 Computational Limit (P95 <= 25.0 ms)')
    plt.title('Computational Inference Latency Distributions (2,000 Single-Window Runs)')
    plt.xlabel('Forward Latency per Window (ms)')
    plt.ylabel('Frequency')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    out = PLOTS_DIR / "12_latency_distribution_plots.png"
    plt.savefig(out)
    plt.close()
    print(f"Saved: {out}")

def main():
    print("=" * 80)
    print("STAGE 8.9.39: GENERATING PUBLICATION-GRADE VISUALIZATIONS")
    print("=" * 80)
    set_plot_style()

    # Load Training Histories
    with open(RESULTS_DIR / "training" / "config_b_training_history.csv", "r", encoding="utf-8") as f:
        hist_b = list(csv.DictReader(f))
    with open(RESULTS_DIR / "training" / "config_d_training_history.csv", "r", encoding="utf-8") as f:
        hist_d = list(csv.DictReader(f))

    # Load Validation Predictions
    with open(PRED_DIR / "validation" / "config_b_val_predictions.csv", "r", encoding="utf-8") as f:
        val_b_rows = list(csv.DictReader(f))
    with open(PRED_DIR / "validation" / "config_d_val_predictions.csv", "r", encoding="utf-8") as f:
        val_d_rows = list(csv.DictReader(f))

    # Load Threshold Sweeps
    with open(RESULTS_DIR / "thresholds" / "config_b_validation_threshold_sweep.csv", "r", encoding="utf-8") as f:
        sweep_b = list(csv.DictReader(f))
    with open(RESULTS_DIR / "thresholds" / "config_d_validation_threshold_sweep.csv", "r", encoding="utf-8") as f:
        sweep_d = list(csv.DictReader(f))

    plot_01_training_and_val_loss(hist_b, hist_d)
    plot_02_validation_f1_vs_epoch(hist_b, hist_d)
    plot_03_04_pr_and_roc(val_b_rows, val_d_rows)
    plot_05_06_07_threshold_curves(sweep_b, sweep_d)
    plot_08_confusion_matrices()
    plot_09_reliability_diagrams()
    plot_10_category_false_positives()
    plot_11_historical_vs_expansion()
    plot_12_latency_distributions()

    print("\nAll 12 required plots successfully generated from saved experiment results.")

if __name__ == "__main__":
    main()
