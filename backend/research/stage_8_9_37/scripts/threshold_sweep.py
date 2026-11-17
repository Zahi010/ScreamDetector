"""
Stage 8.9.37 - Task 2 & 3: Per-Model Validation Threshold Sweep & Operating Point Selection
Performs exhaustive threshold sweeps on validation predictions (N=293), computes all metrics,
generates validation diagnostic plots, and selects Operating Points A, B, C, D using strict validation data only.
"""
import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc, precision_recall_curve, confusion_matrix

def run_threshold_sweep():
    print("======================================================================")
    print("STAGE 8.9.37 - TASK 2 & 3: PER-MODEL VALIDATION THRESHOLD SWEEPS")
    print("======================================================================")
    
    val_csv = "backend/research/stage_8_9_37/results/threshold_sweeps/validation_predictions_all_candidates.csv"
    val_df = pd.read_csv(val_csv)
    
    y_true = val_df['ground_truth'].values
    categories = val_df['category'].values
    is_short = val_df['is_short_scream'].values
    
    total_pos = np.sum(y_true == 1) # 79
    total_neg = np.sum(y_true == 0) # 214
    shout_mask = (categories == 'shouting_and_speech')
    total_shout = np.sum(shout_mask) # 74
    total_short = np.sum(is_short == 1) # 6
    
    print(f"Validation Cohort: Total={len(val_df)}, Screams={total_pos}, Negatives={total_neg}, Shouts={total_shout}, ShortScreams={total_short}")
    
    candidates = [
        ("Config_A", "prob_config_a", "YAMNet-Only"),
        ("Config_B", "prob_config_b", "Dual-Encoder (Phonation)"),
        ("Config_C", "prob_config_c", "YAMNet + Subband"),
        ("Config_D", "prob_config_d", "MP-FS-DualEncoder")
    ]
    
    # Thresholds: 0.05 to 0.95 in 0.01 increments plus existing operating points
    thresholds = np.round(np.arange(0.05, 0.951, 0.01), 2).tolist()
    if 0.35 not in thresholds:
        thresholds.append(0.35)
    if 0.43 not in thresholds:
        thresholds.append(0.43)
    thresholds = sorted(list(set(thresholds)))
    
    os.makedirs("backend/research/stage_8_9_37/results/threshold_sweeps", exist_ok=True)
    os.makedirs("backend/research/stage_8_9_37/plots", exist_ok=True)
    
    sweep_results = {}
    
    for code, col, name in candidates:
        probs = val_df[col].values
        rows = []
        for th in thresholds:
            preds = (probs >= th).astype(int)
            tp = int(np.sum((preds == 1) & (y_true == 1)))
            fp = int(np.sum((preds == 1) & (y_true == 0)))
            tn = int(np.sum((preds == 0) & (y_true == 0)))
            fn = int(np.sum((preds == 0) & (y_true == 1)))
            
            prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
            spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
            hn_fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
            
            # Shouted-speech FPR
            fp_shout = int(np.sum((preds == 1) & shout_mask))
            shout_fpr = fp_shout / total_shout if total_shout > 0 else 0.0
            
            # Short-scream recall
            tp_short = int(np.sum((preds == 1) & (is_short == 1)))
            short_rec = tp_short / total_short if total_short > 0 else 0.0
            
            bal_acc = 0.5 * (rec + spec)
            
            rows.append({
                "threshold": round(th, 2),
                "model_code": code,
                "model_name": name,
                "TP": tp,
                "FP": fp,
                "TN": tn,
                "FN": fn,
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1_score": round(f1, 4),
                "specificity": round(spec, 4),
                "hard_negative_fpr": round(hn_fpr, 4),
                "shouted_speech_fpr": round(shout_fpr, 4),
                "short_scream_recall": round(short_rec, 4),
                "short_tp": tp_short,
                "short_total": total_short,
                "balanced_accuracy": round(bal_acc, 4),
                "false_alerts_per_hour": "N/A (discrete clips)"
            })
            
        sweep_df = pd.DataFrame(rows)
        sweep_results[code] = sweep_df
        out_csv = f"backend/research/stage_8_9_37/results/threshold_sweeps/sweep_{code.lower()}.csv"
        sweep_df.to_csv(out_csv, index=False)
        print(f"Generated {out_csv} ({len(sweep_df)} thresholds)")
        
    # Combine sweeps
    all_sweeps_df = pd.concat([sweep_results[c[0]] for c in candidates], ignore_index=True)
    all_sweeps_df.to_csv("backend/research/stage_8_9_37/results/threshold_sweeps/all_models_validation_sweep_summary.csv", index=False)
    
    # -------------------------------------------------------------
    # Plotting Diagnostic Validation Curves
    # -------------------------------------------------------------
    colors = {
        "Config_A": "#1f77b4", # Blue
        "Config_B": "#2ca02c", # Green
        "Config_C": "#ff7f0e", # Orange
        "Config_D": "#d62728"  # Red
    }
    
    # 1. Precision vs Threshold
    plt.figure(figsize=(9, 5))
    for code, col, name in candidates:
        df = sweep_results[code]
        plt.plot(df['threshold'], df['precision'], label=name, color=colors[code], lw=2)
    plt.axvline(0.35, color='gray', linestyle='--', alpha=0.7, label='Frozen Prod (0.35)')
    plt.xlabel('Decision Threshold')
    plt.ylabel('Validation Precision')
    plt.title('Validation Precision vs. Threshold (Stage 8.9.37)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("backend/research/stage_8_9_37/plots/val_precision_vs_threshold.png", dpi=150)
    plt.close()

    # 2. Recall vs Threshold
    plt.figure(figsize=(9, 5))
    for code, col, name in candidates:
        df = sweep_results[code]
        plt.plot(df['threshold'], df['recall'], label=name, color=colors[code], lw=2)
    plt.axvline(0.35, color='gray', linestyle='--', alpha=0.7, label='Frozen Prod (0.35)')
    plt.axhline(0.96, color='black', linestyle=':', label='Gate 1: Recall >= 96%')
    plt.xlabel('Decision Threshold')
    plt.ylabel('Validation Recall')
    plt.title('Validation Recall vs. Threshold (Stage 8.9.37)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("backend/research/stage_8_9_37/plots/val_recall_vs_threshold.png", dpi=150)
    plt.close()

    # 3. F1 vs Threshold
    plt.figure(figsize=(9, 5))
    for code, col, name in candidates:
        df = sweep_results[code]
        plt.plot(df['threshold'], df['f1_score'], label=name, color=colors[code], lw=2)
    plt.axvline(0.35, color='gray', linestyle='--', alpha=0.7, label='Frozen Prod (0.35)')
    plt.xlabel('Decision Threshold')
    plt.ylabel('Validation F1-Score')
    plt.title('Validation F1-Score vs. Threshold (Stage 8.9.37)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("backend/research/stage_8_9_37/plots/val_f1_vs_threshold.png", dpi=150)
    plt.close()

    # 4. Hard-Negative FPR vs Threshold
    plt.figure(figsize=(9, 5))
    for code, col, name in candidates:
        df = sweep_results[code]
        plt.plot(df['threshold'], df['hard_negative_fpr'], label=name, color=colors[code], lw=2)
    plt.axhline(0.05, color='red', linestyle=':', label='Gate 2: HN-FPR <= 5%')
    plt.axvline(0.35, color='gray', linestyle='--', alpha=0.7, label='Frozen Prod (0.35)')
    plt.xlabel('Decision Threshold')
    plt.ylabel('Validation Hard-Negative FPR')
    plt.title('Validation Hard-Negative FPR vs. Threshold (Stage 8.9.37)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("backend/research/stage_8_9_37/plots/val_hn_fpr_vs_threshold.png", dpi=150)
    plt.close()

    # 5. Shouted-Speech FPR vs Threshold
    plt.figure(figsize=(9, 5))
    for code, col, name in candidates:
        df = sweep_results[code]
        plt.plot(df['threshold'], df['shouted_speech_fpr'], label=name, color=colors[code], lw=2)
    plt.axhline(0.15, color='red', linestyle=':', label='Gate 3: Shout-FPR <= 15%')
    plt.axvline(0.35, color='gray', linestyle='--', alpha=0.7, label='Frozen Prod (0.35)')
    plt.xlabel('Decision Threshold')
    plt.ylabel('Validation Shouted-Speech FPR')
    plt.title('Validation Shouted-Speech FPR vs. Threshold (Stage 8.9.37)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("backend/research/stage_8_9_37/plots/val_shout_fpr_vs_threshold.png", dpi=150)
    plt.close()

    # 6. Precision-Recall Curves
    plt.figure(figsize=(8, 6))
    for code, col, name in candidates:
        probs = val_df[col].values
        p, r, _ = precision_recall_curve(y_true, probs)
        pr_auc = auc(r, p)
        plt.plot(r, p, label=f"{name} (PR-AUC = {pr_auc:.4f})", color=colors[code], lw=2)
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Validation Precision-Recall Curves (Stage 8.9.37)')
    plt.grid(True, alpha=0.3)
    plt.legend(loc='lower left')
    plt.tight_layout()
    plt.savefig("backend/research/stage_8_9_37/plots/val_precision_recall_curves.png", dpi=150)
    plt.close()

    # 7. ROC Curves
    plt.figure(figsize=(8, 6))
    for code, col, name in candidates:
        probs = val_df[col].values
        fpr, tpr, _ = roc_curve(y_true, probs)
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, label=f"{name} (ROC-AUC = {roc_auc:.4f})", color=colors[code], lw=2)
    plt.plot([0, 1], [0, 1], 'k--', alpha=0.5)
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate (Recall)')
    plt.title('Validation ROC Curves (Stage 8.9.37)')
    plt.grid(True, alpha=0.3)
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig("backend/research/stage_8_9_37/plots/val_roc_curves.png", dpi=150)
    plt.close()

    print("Diagnostic plots generated in backend/research/stage_8_9_37/plots/")
    
    # -------------------------------------------------------------
    # Task 3: Select Multiple Operating Points Per Model
    # -------------------------------------------------------------
    selected_points = {}
    
    for code, col, name in candidates:
        df = sweep_results[code]
        probs = val_df[col].values
        
        # Point A: Maximum Validation F1
        # Tie-breaker: higher recall, lower HN-FPR, higher threshold
        sorted_a = df.sort_values(by=['f1_score', 'recall', 'hard_negative_fpr', 'threshold'],
                                  ascending=[False, False, True, False])
        pt_a = sorted_a.iloc[0].to_dict()
        
        # Point B: Recall-Oriented
        # Maximize recall subject to HN-FPR <= 0.05 AND Shout-FPR <= 0.15
        feas_b = df[(df['hard_negative_fpr'] <= 0.05) & (df['shouted_speech_fpr'] <= 0.15)]
        if len(feas_b) > 0:
            sorted_b = feas_b.sort_values(by=['recall', 'hard_negative_fpr', 'f1_score', 'threshold'],
                                          ascending=[False, True, False, False])
            pt_b = sorted_b.iloc[0].to_dict()
            pt_b['feasible'] = True
            pt_b['feasibility_note'] = "Satisfies validation HN-FPR <= 5% and Shout-FPR <= 15%"
        else:
            # Fallback: strictly report no feasible threshold, and find closest threshold
            sorted_b = df.sort_values(by=['hard_negative_fpr', 'shouted_speech_fpr', 'recall'],
                                      ascending=[True, True, False])
            pt_b = sorted_b.iloc[0].to_dict()
            pt_b['feasible'] = False
            pt_b['feasibility_note'] = "NO FEASIBLE THRESHOLD satisfying HN-FPR <= 5% and Shout-FPR <= 15%"
            
        # Point C: False-Alarm-Oriented
        # Minimize HN-FPR while preserving highest achievable recall (recall >= 0.80 if available, else max recall)
        feas_c = df[df['recall'] >= 0.80]
        if len(feas_c) > 0:
            sorted_c = feas_c.sort_values(by=['hard_negative_fpr', 'shouted_speech_fpr', 'recall', 'threshold'],
                                          ascending=[True, True, False, False])
            pt_c = sorted_c.iloc[0].to_dict()
            pt_c['feasible'] = True
            pt_c['feasibility_note'] = "Preserves Recall >= 80% with minimum HN-FPR"
        else:
            sorted_c = df.sort_values(by=['hard_negative_fpr', 'recall', 'threshold'],
                                      ascending=[True, False, False])
            pt_c = sorted_c.iloc[0].to_dict()
            pt_c['feasible'] = False
            pt_c['feasibility_note'] = "Recall < 80% across all thresholds; lowest HN-FPR chosen"

        # Point D: Balanced Operational Point
        # Practical balance: minimize Euclidean distance to ideal operating point (Recall=1.0, HN-FPR=0.0)
        # combined_dist = (1 - recall)^2 + (hn_fpr)^2 + (0.5 * shout_fpr)^2
        df_copy = df.copy()
        df_copy['dist_to_ideal'] = (1.0 - df_copy['recall'])**2 + (df_copy['hard_negative_fpr'])**2 + (0.5 * df_copy['shouted_speech_fpr'])**2
        sorted_d = df_copy.sort_values(by=['dist_to_ideal', 'f1_score', 'threshold'],
                                       ascending=[True, False, False])
        pt_d = sorted_d.iloc[0].to_dict()
        del pt_d['dist_to_ideal']
        pt_d['feasible'] = True
        pt_d['feasibility_note'] = "Optimal balance minimizing distance to ideal operating point"
        
        selected_points[code] = {
            "model_name": name,
            "operating_point_A_max_f1": pt_a,
            "operating_point_B_recall_oriented": pt_b,
            "operating_point_C_fa_oriented": pt_c,
            "operating_point_D_balanced": pt_d,
            "existing_operating_point_0_35": df[df['threshold'] == 0.35].iloc[0].to_dict() if len(df[df['threshold'] == 0.35]) > 0 else None,
            "existing_operating_point_0_43": df[df['threshold'] == 0.43].iloc[0].to_dict() if len(df[df['threshold'] == 0.43]) > 0 else None
        }

    # Save selected operating points
    out_json = "backend/research/stage_8_9_37/results/threshold_sweeps/selected_operating_points.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(selected_points, f, indent=2)
    print(f"Saved selected operating points to {out_json}")
    
    # Format a clean table of selected points
    summary_rows = []
    for code, col, name in candidates:
        sp = selected_points[code]
        for pt_key, label in [
            ("operating_point_A_max_f1", "Point A: Max F1"),
            ("operating_point_B_recall_oriented", "Point B: Recall-Oriented"),
            ("operating_point_C_fa_oriented", "Point C: FA-Oriented"),
            ("operating_point_D_balanced", "Point D: Balanced"),
            ("existing_operating_point_0_35", "Frozen Prod (0.35)"),
            ("existing_operating_point_0_43", "Stage 8.9.36 Best (0.43)")
        ]:
            item = sp.get(pt_key)
            if item:
                summary_rows.append({
                    "model_code": code,
                    "model_name": name,
                    "operating_point": label,
                    "threshold": item['threshold'],
                    "recall": item['recall'],
                    "precision": item['precision'],
                    "f1_score": item['f1_score'],
                    "hn_fpr": item['hard_negative_fpr'],
                    "shout_fpr": item['shouted_speech_fpr'],
                    "short_scream_recall": item['short_scream_recall'],
                    "feasible": item.get('feasible', 'N/A')
                })
    summary_df = pd.DataFrame(summary_rows)
    summary_csv = "backend/research/stage_8_9_37/results/threshold_sweeps/selected_operating_points_summary.csv"
    summary_df.to_csv(summary_csv, index=False)
    print(f"Saved {summary_csv}")
    
    # 8. Confusion Matrices Plot for Point A and Point D across all 4 models
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    for idx, (code, col, name) in enumerate(candidates):
        for row_idx, pt_key, pt_label in [(0, "operating_point_A_max_f1", "Point A (Max F1)"),
                                          (1, "operating_point_D_balanced", "Point D (Balanced)")]:
            th = selected_points[code][pt_key]['threshold']
            preds = (val_df[col].values >= th).astype(int)
            cm = confusion_matrix(y_true, preds)
            ax = axes[row_idx, idx]
            im = ax.imshow(cm, cmap='Blues', interpolation='nearest')
            ax.set_title(f"{name}\n{pt_label} (th={th:.2f})", fontsize=10)
            ax.set_xticks([0, 1])
            ax.set_yticks([0, 1])
            ax.set_xticklabels(['Neg', 'Scream'])
            ax.set_yticklabels(['Neg', 'Scream'])
            for i in range(2):
                for j in range(2):
                    ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                            color="white" if cm[i, j] > cm.max()/2 else "black", fontweight='bold')
            if idx == 0:
                ax.set_ylabel('True Label')
            if row_idx == 1:
                ax.set_xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig("backend/research/stage_8_9_37/plots/val_confusion_matrices.png", dpi=150)
    plt.close()
    print("Saved val_confusion_matrices.png")

if __name__ == "__main__":
    run_threshold_sweep()
