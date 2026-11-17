"""
Stage 8.9.36 - Phase 2: Threshold and Operating-Point Audit Script
Audits the validation-based threshold selection process for Candidate D
and evaluates the recall vs. false-positive trade-offs between 0.3500 and 0.4300.
"""
import os
import sys
import json
import csv
import numpy as np
import pandas as pd
import torch

# Add path to Stage 8.9.35 src
sys.path.insert(0, os.path.abspath("backend/research/stage_8_9_35/src"))
from train_and_evaluate_stage8_9_35 import MultiPathwayFusionModel

def audit_thresholds():
    print("======================================================================")
    print("STAGE 8.9.36 - PHASE 2: THRESHOLD AND OPERATING-POINT AUDIT")
    print("======================================================================")

    # 1. Load Data
    data_path = 'backend/experiments/v2_hard_negative_training/features/yamnet_features_v3.npz'
    data = np.load(data_path, allow_pickle=True)
    
    valid_idx = np.where(data['binary_labels'] != 'ambiguous')[0]
    file_ids = data['file_ids'][valid_idx]
    splits = data['splits'][valid_idx]
    binary_labels = data['binary_labels'][valid_idx]
    categories = data['categories'][valid_idx]
    
    X_sem = data['features_mean'][valid_idx].astype(np.float32)
    X_acoust = data['vocal_features'][valid_idx].astype(np.float32)
    mask_acoust = (~np.isnan(X_acoust) & (X_acoust > 0.0)).astype(np.float32)
    X_acoust = np.nan_to_num(X_acoust, nan=0.0)
    
    y = np.array([1 if b == 'scream' else 0 for b in binary_labels])
    
    # Load subband features
    subband_csv = 'backend/research/stage_8_9_35/frequency_analysis/subband_feature_analysis.csv'
    with open(subband_csv, encoding='utf-8') as f:
        sb_rows = {r['file_id']: r for r in csv.DictReader(f)}
        
    X_sb = []
    for fid in file_ids:
        if fid in sb_rows:
            r = sb_rows[fid]
            vec = [
                float(r['Band1_300_800Hz_rel_energy']),
                float(r['Band2_800_1500Hz_rel_energy']),
                float(r['Band3_1500_2000Hz_rel_energy']),
                float(r['Band4_2000_3000Hz_rel_energy']),
                float(r['Band5_3000_4000Hz_rel_energy']),
                float(r['Band6_4000_6000Hz_rel_energy']),
                float(r['Band1_300_800Hz_temp_var']),
                float(r['Band4_2000_3000Hz_temp_var']),
                float(r['Band5_3000_4000Hz_temp_var']),
                float(r['scream_band_to_vocal_ratio']),
                float(r['high_band_whistle_ratio'])
            ]
        else:
            vec = [0.0] * 11
        X_sb.append(vec)
    X_sb = np.array(X_sb, dtype=np.float32)
    
    val_m = (splits == 'val')
    test_m = (splits == 'test')
    
    # 2. Load Candidate D Model Weights
    device = torch.device('cpu')
    model = MultiPathwayFusionModel(sem_dim=1024, acoust_dim=6, subband_dim=11).to(device)
    model_path = 'backend/research/stage_8_9_35/models/mp_fs_dual_encoder_model.pt'
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    
    # Predict on Validation Set
    with torch.no_grad():
        v_sem = torch.from_numpy(X_sem[val_m]).to(device)
        v_acoust = torch.from_numpy(X_acoust[val_m]).to(device)
        v_mask = torch.from_numpy(mask_acoust[val_m]).to(device)
        v_sb = torch.from_numpy(X_sb[val_m]).to(device)
        logits_val, _, _ = model(v_sem, v_acoust, v_mask, v_sb)
        probs_val = torch.sigmoid(logits_val).numpy()
        
    y_val = y[val_m]
    cats_val = categories[val_m]
    
    # Predict on Test Set
    with torch.no_grad():
        t_sem = torch.from_numpy(X_sem[test_m]).to(device)
        t_acoust = torch.from_numpy(X_acoust[test_m]).to(device)
        t_mask = torch.from_numpy(mask_acoust[test_m]).to(device)
        t_sb = torch.from_numpy(X_sb[test_m]).to(device)
        logits_test, _, _ = model(t_sem, t_acoust, t_mask, t_sb)
        probs_test = torch.sigmoid(logits_test).numpy()
        
    y_test = y[test_m]
    cats_test = categories[test_m]

    # 3. Validation Threshold Sweep across [0.20, 0.60]
    sweep_results = []
    best_f1 = -1.0
    best_th = 0.35
    
    for th in np.arange(0.20, 0.61, 0.01):
        th_val = round(float(th), 2)
        preds = (probs_val >= th_val).astype(int)
        tp = int(np.sum((preds == 1) & (y_val == 1)))
        fn = int(np.sum((preds == 0) & (y_val == 1)))
        fp = int(np.sum((preds == 1) & (y_val == 0)))
        tn = int(np.sum((preds == 0) & (y_val == 0)))
        
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
        
        # Category specific false alarm rates on validation
        shout_m = (y_val == 0) & (pd.Series(cats_val).str.lower().str.contains('shout').values)
        cry_m = (y_val == 0) & (pd.Series(cats_val).str.lower().str.contains('cry').values)
        cheer_m = (y_val == 0) & (pd.Series(cats_val).str.lower().str.contains('cheer').values)
        
        shout_fpr = np.sum((preds == 1) & shout_m) / np.sum(shout_m) if np.sum(shout_m) > 0 else 0.0
        cry_fpr = np.sum((preds == 1) & cry_m) / np.sum(cry_m) if np.sum(cry_m) > 0 else 0.0
        cheer_fpr = np.sum((preds == 1) & cheer_m) / np.sum(cheer_m) if np.sum(cheer_m) > 0 else 0.0
        
        if f1 > best_f1:
            best_f1 = f1
            best_th = th_val
            
        sweep_results.append({
            "threshold": th_val,
            "val_recall": round(rec * 100, 2),
            "val_hn_fpr": round(fpr * 100, 2),
            "val_precision": round(prec * 100, 2),
            "val_specificity": round(spec * 100, 2),
            "val_f1": round(f1, 4),
            "val_shout_fpr": round(shout_fpr * 100, 2),
            "val_cry_fpr": round(cry_fpr * 100, 2),
            "val_cheer_fpr": round(cheer_fpr * 100, 2)
        })
        
    sweep_df = pd.DataFrame(sweep_results)
    out_dir = 'backend/research/stage_8_9_36/evaluation'
    os.makedirs(out_dir, exist_ok=True)
    sweep_csv_path = os.path.join(out_dir, 'validation_threshold_sweep.csv')
    sweep_df.to_csv(sweep_csv_path, index=False)
    print(f"Validation Sweep complete: Best Val F1 = {best_f1:.4f} at theta* = {best_th:.2f}")

    # 4. Compare Performance at 0.3500 vs. 0.4300 on Validation and Test
    def compute_metrics(p, y_arr, c_arr, threshold):
        preds = (p >= threshold).astype(int)
        tp = int(np.sum((preds == 1) & (y_arr == 1)))
        fn = int(np.sum((preds == 0) & (y_arr == 1)))
        fp = int(np.sum((preds == 1) & (y_arr == 0)))
        tn = int(np.sum((preds == 0) & (y_arr == 0)))
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
        
        shout_m = (y_arr == 0) & (pd.Series(c_arr).str.lower().str.contains('shout').values)
        cry_m = (y_arr == 0) & (pd.Series(c_arr).str.lower().str.contains('cry').values)
        cheer_m = (y_arr == 0) & (pd.Series(c_arr).str.lower().str.contains('cheer').values)
        
        shout_fpr = np.sum((preds == 1) & shout_m) / np.sum(shout_m) if np.sum(shout_m) > 0 else 0.0
        cry_fpr = np.sum((preds == 1) & cry_m) / np.sum(cry_m) if np.sum(cry_m) > 0 else 0.0
        cheer_fpr = np.sum((preds == 1) & cheer_m) / np.sum(cheer_m) if np.sum(cheer_m) > 0 else 0.0
        
        return {
            "threshold": threshold,
            "tp": tp, "fn": fn, "fp": fp, "tn": tn,
            "recall": round(rec * 100, 2),
            "hn_fpr": round(fpr * 100, 2),
            "precision": round(prec * 100, 2),
            "specificity": round(spec * 100, 2),
            "f1": round(f1, 4),
            "shout_fpr": round(shout_fpr * 100, 2),
            "cry_fpr": round(cry_fpr * 100, 2),
            "cheer_fpr": round(cheer_fpr * 100, 2)
        }

    comparison = {
        "validation_selected_threshold": best_th,
        "selection_criterion": "Maximum Validation F1-Score (strictly validation partition)",
        "test_labels_used_for_selection": False,
        "validation_metrics": {
            "threshold_0.35": compute_metrics(probs_val, y_val, cats_val, 0.35),
            "threshold_0.43": compute_metrics(probs_val, y_val, cats_val, 0.43)
        },
        "test_metrics": {
            "threshold_0.35": compute_metrics(probs_test, y_test, cats_test, 0.35),
            "threshold_0.43": compute_metrics(probs_test, y_test, cats_test, 0.43)
        }
    }
    
    comp_json_path = os.path.join(out_dir, 'threshold_comparison.json')
    with open(comp_json_path, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=2)
    print(f"Saved {comp_json_path}")
    
    print("\n--- TEST METRICS AT THRESHOLD 0.35 vs. 0.43 ---")
    print(f"At 0.35: Recall={comparison['test_metrics']['threshold_0.35']['recall']}%, HN-FPR={comparison['test_metrics']['threshold_0.35']['hn_fpr']}%, Shout-FPR={comparison['test_metrics']['threshold_0.35']['shout_fpr']}%")
    print(f"At 0.43: Recall={comparison['test_metrics']['threshold_0.43']['recall']}%, HN-FPR={comparison['test_metrics']['threshold_0.43']['hn_fpr']}%, Shout-FPR={comparison['test_metrics']['threshold_0.43']['shout_fpr']}%")

if __name__ == '__main__':
    audit_thresholds()
