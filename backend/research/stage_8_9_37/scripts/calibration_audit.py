"""
Stage 8.9.37 - Task 5: Probability Calibration Audit
Evaluates calibration of uncalibrated scores, fits Platt Scaling and Isotonic Regression
strictly on validation data (N=293), calculates Brier score and ECE, generates reliability
diagrams and score distributions, and evaluates impact on operating decisions.
"""
import os
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import brier_score_loss
from sklearn.calibration import calibration_curve

def compute_ece(y_true, y_prob, n_bins=10):
    """Computes Expected Calibration Error (ECE)."""
    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    total_samples = len(y_true)
    for i in range(n_bins):
        bin_mask = (y_prob >= bin_edges[i]) & (y_prob < bin_edges[i + 1])
        if i == n_bins - 1: # Include upper bound on last bin
            bin_mask = (y_prob >= bin_edges[i]) & (y_prob <= bin_edges[i + 1])
        bin_count = np.sum(bin_mask)
        if bin_count > 0:
            bin_acc = np.mean(y_true[bin_mask])
            bin_conf = np.mean(y_prob[bin_mask])
            ece += (bin_count / total_samples) * np.abs(bin_acc - bin_conf)
    return float(ece)

def run_calibration_audit():
    print("======================================================================")
    print("STAGE 8.9.37 - TASK 5: PROBABILITY CALIBRATION AUDIT")
    print("======================================================================")
    
    val_csv = "backend/research/stage_8_9_37/results/threshold_sweeps/validation_predictions_all_candidates.csv"
    test_csv = "backend/research/stage_8_9_37/results/test_evaluations/test_predictions_all_candidates.csv"
    val_df = pd.read_csv(val_csv)
    test_df = pd.read_csv(test_csv)
    
    y_val = val_df['ground_truth'].values
    y_test = test_df['ground_truth'].values
    val_cats = val_df['category'].values
    
    candidates = [
        ("Config_A", "prob_config_a", "YAMNet-Only"),
        ("Config_B", "prob_config_b", "Dual-Encoder (Phonation)"),
        ("Config_C", "prob_config_c", "YAMNet + Subband"),
        ("Config_D", "prob_config_d", "MP-FS-DualEncoder")
    ]
    
    cal_dir = "backend/research/stage_8_9_37/results/calibration"
    model_cal_dir = os.path.join(cal_dir, "calibrators")
    os.makedirs(model_cal_dir, exist_ok=True)
    os.makedirs("backend/research/stage_8_9_37/plots", exist_ok=True)
    
    cal_metrics = []
    
    # New calibrated probability columns for val and test
    val_cal_df = val_df.copy()
    test_cal_df = test_df.copy()
    
    # -------------------------------------------------------------
    # 1. Fit Calibrators on Validation Set Only & Evaluate
    # -------------------------------------------------------------
    for code, col, name in candidates:
        p_val_raw = val_df[col].values
        p_test_raw = test_df[col].values
        
        # Uncalibrated metrics
        brier_uncal = float(brier_score_loss(y_val, p_val_raw))
        ece_uncal = compute_ece(y_val, p_val_raw)
        
        # Fit Platt Scaling (Logistic Regression on probability feature)
        # Note: LogisticRegression with C=1.0 or high C
        platt = LogisticRegression(C=1.0, solver='lbfgs', random_state=42)
        platt.fit(p_val_raw.reshape(-1, 1), y_val)
        p_val_platt = platt.predict_proba(p_val_raw.reshape(-1, 1))[:, 1]
        p_test_platt = platt.predict_proba(p_test_raw.reshape(-1, 1))[:, 1]
        brier_platt = float(brier_score_loss(y_val, p_val_platt))
        ece_platt = compute_ece(y_val, p_val_platt)
        joblib.dump(platt, os.path.join(model_cal_dir, f"platt_{code.lower()}.joblib"))
        
        # Fit Isotonic Regression
        iso = IsotonicRegression(out_of_bounds='clip', y_min=0.0, y_max=1.0)
        iso.fit(p_val_raw, y_val)
        p_val_iso = iso.predict(p_val_raw)
        p_test_iso = iso.predict(p_test_raw)
        brier_iso = float(brier_score_loss(y_val, p_val_iso))
        ece_iso = compute_ece(y_val, p_val_iso)
        joblib.dump(iso, os.path.join(model_cal_dir, f"isotonic_{code.lower()}.joblib"))
        
        # Store in calibrated dataframes
        val_cal_df[f"{col}_platt"] = p_val_platt
        val_cal_df[f"{col}_isotonic"] = p_val_iso
        test_cal_df[f"{col}_platt"] = p_test_platt
        test_cal_df[f"{col}_isotonic"] = p_test_iso
        
        cal_metrics.append({
            "model_code": code,
            "model_name": name,
            "calibration_method": "Uncalibrated",
            "val_brier_score": round(brier_uncal, 4),
            "val_ece": round(ece_uncal, 4)
        })
        cal_metrics.append({
            "model_code": code,
            "model_name": name,
            "calibration_method": "Platt Scaling",
            "val_brier_score": round(brier_platt, 4),
            "val_ece": round(ece_platt, 4)
        })
        cal_metrics.append({
            "model_code": code,
            "model_name": name,
            "calibration_method": "Isotonic Regression",
            "val_brier_score": round(brier_iso, 4),
            "val_ece": round(ece_iso, 4)
        })
        
        print(f"[{name}]")
        print(f"  Uncalibrated: Brier={brier_uncal:.4f}, ECE={ece_uncal:.4f}")
        print(f"  Platt Scale:  Brier={brier_platt:.4f}, ECE={ece_platt:.4f}")
        print(f"  Isotonic Reg: Brier={brier_iso:.4f}, ECE={ece_iso:.4f}")

    metrics_df = pd.DataFrame(cal_metrics)
    metrics_csv = os.path.join(cal_dir, "validation_calibration_metrics.csv")
    metrics_df.to_csv(metrics_csv, index=False)
    print(f"\nSaved {metrics_csv}")
    
    val_cal_df.to_csv(os.path.join(cal_dir, "validation_predictions_calibrated.csv"), index=False)
    test_cal_df.to_csv(os.path.join(cal_dir, "test_predictions_calibrated.csv"), index=False)
    
    # -------------------------------------------------------------
    # 2. Reliability Diagrams Plot
    # -------------------------------------------------------------
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()
    
    for idx, (code, col, name) in enumerate(candidates):
        ax = axes[idx]
        p_raw = val_df[col].values
        p_platt = val_cal_df[f"{col}_platt"].values
        p_iso = val_cal_df[f"{col}_isotonic"].values
        
        frac_pos_raw, mean_pred_raw = calibration_curve(y_val, p_raw, n_bins=8, strategy='uniform')
        frac_pos_platt, mean_pred_platt = calibration_curve(y_val, p_platt, n_bins=8, strategy='uniform')
        frac_pos_iso, mean_pred_iso = calibration_curve(y_val, p_iso, n_bins=8, strategy='uniform')
        
        ax.plot([0, 1], [0, 1], 'k--', label='Perfect Calibration', alpha=0.6)
        ax.plot(mean_pred_raw, frac_pos_raw, 's-', label=f"Uncal (ECE={compute_ece(y_val, p_raw):.3f})", color='#d62728', lw=1.8)
        ax.plot(mean_pred_platt, frac_pos_platt, 'o-', label=f"Platt (ECE={compute_ece(y_val, p_platt):.3f})", color='#1f77b4', lw=1.8)
        ax.plot(mean_pred_iso, frac_pos_iso, '^-', label=f"Isotonic (ECE={compute_ece(y_val, p_iso):.3f})", color='#2ca02c', lw=1.8)
        
        ax.set_title(f"Reliability Diagram: {name}", fontsize=11, fontweight='bold')
        ax.set_xlabel('Mean Predicted Probability')
        ax.set_ylabel('Fraction of Positives (Empirical)')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='lower right', fontsize=9)
        
    plt.tight_layout()
    plt.savefig("backend/research/stage_8_9_37/plots/val_reliability_diagrams.png", dpi=150)
    plt.close()
    print("Saved val_reliability_diagrams.png")

    # -------------------------------------------------------------
    # 3. Score Distributions Across Critical Vocal Categories
    # -------------------------------------------------------------
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    categories_to_plot = [
        ("scream", "Screams (Genuine)", "#2ca02c"),
        ("shouting_and_speech", "Shouted Speech (HN)", "#d62728"),
        ("crowd_chant_cheering", "Crowd Cheering (HN)", "#ff7f0e"),
        ("infant_crying", "Infant Crying (HN)", "#9467bd")
    ]
    
    for idx, (code, col, name) in enumerate(candidates):
        ax = axes[idx]
        probs = val_df[col].values
        for cat_key, cat_label, cat_color in categories_to_plot:
            if cat_key == "scream":
                cat_mask = (y_val == 1)
            else:
                cat_mask = (val_cats == cat_key)
            if np.sum(cat_mask) > 0:
                ax.hist(probs[cat_mask], bins=np.linspace(0, 1, 21), alpha=0.45,
                        label=f"{cat_label} (N={np.sum(cat_mask)})", color=cat_color, density=True)
        ax.axvline(0.35, color='gray', linestyle='--', label='Prod Thresh (0.35)')
        ax.set_title(f"Score Distribution: {name}", fontsize=11, fontweight='bold')
        ax.set_xlabel('Predicted Probability Score')
        ax.set_ylabel('Density')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper center', fontsize=8)
        
    plt.tight_layout()
    plt.savefig("backend/research/stage_8_9_37/plots/val_score_distributions_by_category.png", dpi=150)
    plt.close()
    print("Saved val_score_distributions_by_category.png")

if __name__ == "__main__":
    run_calibration_audit()
