"""
Stage 8.9.38 - Task 2: Label Adjudication Resolution & Dual Historical Evaluation Views
Investigates the two disputed recordings:
- v2_nigens_242607__reitanna__gasp-oooh
- v2_nigens_242644__reitanna__another-surprised-oooh
Generates two distinct evaluation views:
View A: Original-Label Historical Baseline (N=293: 102 screams, 191 negatives)
View B: Adjudicated-Label Analytical View (N=293: 100 screams, 193 negatives)
"""
import os
import json
import numpy as np
import pandas as pd

def resolve_label_adjudication():
    print("======================================================================")
    print("STAGE 8.9.38 - TASK 2: LABEL ADJUDICATION & DUAL HISTORICAL VIEWS")
    print("======================================================================")
    
    out_dir = "backend/research/stage_8_9_38/audits"
    report_dir = "backend/research/stage_8_9_38/reports"
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(report_dir, exist_ok=True)
    
    test_csv = "backend/research/stage_8_9_37/results/test_evaluations/test_predictions_all_candidates.csv"
    test_df = pd.read_csv(test_csv)
    
    disputed_ids = [
        "v2_nigens_242607__reitanna__gasp-oooh",
        "v2_nigens_242644__reitanna__another-surprised-oooh"
    ]
    
    disp_rows = test_df[test_df['file_id'].isin(disputed_ids)]
    print("\nDisputed Files Model Predictions:")
    for _, r in disp_rows.iterrows():
        print(f"[{r['file_id']}] GT={r['ground_truth']} | P(Config A)={r['prob_config_a']:.4f} | P(Config B)={r['prob_config_b']:.4f} | P(Config D)={r['prob_config_d']:.4f}")
        
    candidates = [
        ("Config_A", "prob_config_a", "YAMNet-Only", 0.38),
        ("Config_B", "prob_config_b", "Dual-Encoder Baseline", 0.44),
        ("Config_C", "prob_config_c", "YAMNet + Subband", 0.30),
        ("Config_D", "prob_config_d", "MP-FS-DualEncoder", 0.43)
    ]
    
    # Generate View A and View B metrics
    results = []
    
    for code, col, name, th in candidates:
        probs = test_df[col].values
        preds = (probs >= th).astype(int)
        
        # --- VIEW A: Original Labels (102 screams, 191 negatives) ---
        y_orig = test_df['ground_truth'].values
        tp_a = int(np.sum((preds == 1) & (y_orig == 1)))
        fp_a = int(np.sum((preds == 1) & (y_orig == 0)))
        tn_a = int(np.sum((preds == 0) & (y_orig == 0)))
        fn_a = int(np.sum((preds == 0) & (y_orig == 1)))
        
        rec_a = tp_a / (tp_a + fn_a)
        prec_a = tp_a / (tp_a + fp_a) if (tp_a + fp_a) > 0 else 0.0
        f1_a = 2 * prec_a * rec_a / (prec_a + rec_a) if (prec_a + rec_a) > 0 else 0.0
        hn_fpr_a = fp_a / (fp_a + tn_a)
        
        # Shouted speech FPR (shouting_and_speech has 48 clips in test)
        shout_mask = (test_df['category'] == 'shouting_and_speech')
        shout_fpr_a = int(np.sum((preds == 1) & shout_mask)) / np.sum(shout_mask)
        
        # --- VIEW B: Adjudicated Labels (100 screams, 193 negatives) ---
        y_adj = y_orig.copy()
        for d_id in disputed_ids:
            idx = test_df[test_df['file_id'] == d_id].index[0]
            y_adj[idx] = 0 # Adjudicated as true non-scream
            
        tp_b = int(np.sum((preds == 1) & (y_adj == 1)))
        fp_b = int(np.sum((preds == 1) & (y_adj == 0)))
        tn_b = int(np.sum((preds == 0) & (y_adj == 0)))
        fn_b = int(np.sum((preds == 0) & (y_adj == 1)))
        
        rec_b = tp_b / (tp_b + fn_b)
        prec_b = tp_b / (tp_b + fp_b) if (tp_b + fp_b) > 0 else 0.0
        f1_b = 2 * prec_b * rec_b / (prec_b + rec_b) if (prec_b + rec_b) > 0 else 0.0
        hn_fpr_b = fp_b / (fp_b + tn_b)
        shout_fpr_b = shout_fpr_a # Shouting category unaffected
        
        results.append({
            "model_code": code,
            "model_name": name,
            "threshold": th,
            # View A
            "view_a_total_screams": 102,
            "view_a_total_negatives": 191,
            "view_a_recall_frac": f"{tp_a}/102",
            "view_a_recall": round(rec_a, 4),
            "view_a_hn_fpr_frac": f"{fp_a}/191",
            "view_a_hn_fpr": round(hn_fpr_a, 4),
            "view_a_shout_fpr": round(shout_fpr_a, 4),
            "view_a_f1": round(f1_a, 4),
            # View B
            "view_b_total_screams": 100,
            "view_b_total_negatives": 193,
            "view_b_recall_frac": f"{tp_b}/100",
            "view_b_recall": round(rec_b, 4),
            "view_b_hn_fpr_frac": f"{fp_b}/193",
            "view_b_hn_fpr": round(hn_fpr_b, 4),
            "view_b_shout_fpr": round(shout_fpr_b, 4),
            "view_b_f1": round(f1_b, 4),
            # Delta
            "recall_delta_pct": round((rec_b - rec_a) * 100, 2),
            "hn_fpr_delta_pct": round((hn_fpr_b - hn_fpr_a) * 100, 2)
        })
        
    res_df = pd.DataFrame(results)
    csv_out = os.path.join(out_dir, "dual_view_historical_metrics.csv")
    res_df.to_csv(csv_out, index=False)
    print(f"\nSaved dual view comparison to {csv_out}")
    
    print("\n--- Dual View Historical Comparison Summary ---")
    for _, r in res_df.iterrows():
        print(f"[{r['model_name']}] th={r['threshold']}")
        print(f"  View A (Original):    Recall={r['view_a_recall_frac']} ({r['view_a_recall']*100:.2f}%) | HN-FPR={r['view_a_hn_fpr_frac']} ({r['view_a_hn_fpr']*100:.2f}%)")
        print(f"  View B (Adjudicated): Recall={r['view_b_recall_frac']} ({r['view_b_recall']*100:.2f}%) | HN-FPR={r['view_b_hn_fpr_frac']} ({r['view_b_hn_fpr']*100:.2f}%)")
        print(f"  Delta: Recall +{r['recall_delta_pct']}% | HN-FPR {r['hn_fpr_delta_pct']}%")

if __name__ == "__main__":
    resolve_label_adjudication()
