"""
Stage 8.9.37 - Task 4: Matched-Operating-Point Comparison
Compares model candidates under:
1. Individually selected validation thresholds (Point A, B, C, D).
2. Matched validation operating conditions (Matched HN-FPR ~ 5%, Matched HN-FPR ~ 10%, Matched Recall ~ 80%).
All matches are determined strictly using validation data.
"""
import os
import json
import numpy as np
import pandas as pd

def run_matched_comparison():
    print("======================================================================")
    print("STAGE 8.9.37 - TASK 4: MATCHED-OPERATING-POINT COMPARISON")
    print("======================================================================")
    
    os.makedirs("backend/research/stage_8_9_37/results/operating_point_comparisons", exist_ok=True)
    
    # Load sweep results
    candidates = ["config_a", "config_b", "config_c", "config_d"]
    sweeps = {}
    for c in candidates:
        csv_path = f"backend/research/stage_8_9_37/results/threshold_sweeps/sweep_{c}.csv"
        sweeps[c] = pd.read_csv(csv_path)
        
    # Load selected operating points
    sel_json_path = "backend/research/stage_8_9_37/results/threshold_sweeps/selected_operating_points.json"
    with open(sel_json_path, encoding='utf-8') as f:
        sel_points = json.load(f)
        
    # -------------------------------------------------------------
    # Comparison 1: Individually Selected Validation Thresholds
    # -------------------------------------------------------------
    rows_comp1 = []
    pt_types = [
        ("operating_point_A_max_f1", "Point A (Max F1)"),
        ("operating_point_B_recall_oriented", "Point B (Recall-Oriented)"),
        ("operating_point_C_fa_oriented", "Point C (FA-Oriented)"),
        ("operating_point_D_balanced", "Point D (Balanced)"),
        ("existing_operating_point_0_35", "Frozen Baseline (0.35)")
    ]
    
    for c_code in ["Config_A", "Config_B", "Config_C", "Config_D"]:
        c_dict = sel_points[c_code]
        m_name = c_dict["model_name"]
        for pt_key, pt_label in pt_types:
            item = c_dict.get(pt_key)
            if item:
                rows_comp1.append({
                    "model_code": c_code,
                    "model_name": m_name,
                    "operating_point": pt_label,
                    "selected_threshold": item["threshold"],
                    "val_recall": item["recall"],
                    "val_precision": item["precision"],
                    "val_f1_score": item["f1_score"],
                    "val_hn_fpr": item["hard_negative_fpr"],
                    "val_shout_fpr": item["shouted_speech_fpr"],
                    "val_short_recall": item["short_scream_recall"],
                    "gate1_rec_ge_96": item["recall"] >= 0.96,
                    "gate2_hn_le_5": item["hard_negative_fpr"] <= 0.05,
                    "gate3_shout_le_15": item["shouted_speech_fpr"] <= 0.15,
                    "gate4_short_ge_90": item["short_scream_recall"] >= 0.90,
                    "all_val_gates_met": (item["recall"] >= 0.96 and
                                          item["hard_negative_fpr"] <= 0.05 and
                                          item["shouted_speech_fpr"] <= 0.15 and
                                          item["short_scream_recall"] >= 0.90)
                })
                
    df_comp1 = pd.DataFrame(rows_comp1)
    csv_comp1 = "backend/research/stage_8_9_37/results/operating_point_comparisons/comparison1_individual_thresholds.csv"
    df_comp1.to_csv(csv_comp1, index=False)
    print(f"Saved {csv_comp1}")
    
    # -------------------------------------------------------------
    # Comparison 2: Matched Validation Operating Points
    # -------------------------------------------------------------
    # Target 1: Matched HN-FPR ~ 5.0% (Gate 2 standard)
    # Target 2: Matched HN-FPR ~ 10.0%
    # Target 3: Matched Recall ~ 80.0%
    # Target 4: Matched Shout-FPR ~ 10.0%
    
    match_targets = [
        ("Matched HN-FPR ~ 5%", "hard_negative_fpr", 0.05, "min_abs_diff"),
        ("Matched HN-FPR ~ 10%", "hard_negative_fpr", 0.10, "min_abs_diff"),
        ("Matched Recall ~ 80%", "recall", 0.80, "min_abs_diff"),
        ("Matched Shout-FPR ~ 10%", "shouted_speech_fpr", 0.10, "min_abs_diff")
    ]
    
    rows_comp2 = []
    for cond_name, col_name, target_val, rule in match_targets:
        for c in candidates:
            df = sweeps[c]
            # Find nearest row
            diffs = (df[col_name] - target_val).abs()
            best_idx = diffs.idxmin()
            row = df.loc[best_idx]
            
            rows_comp2.append({
                "condition": cond_name,
                "target_metric": col_name,
                "target_value": target_val,
                "model_code": row["model_code"],
                "model_name": row["model_name"],
                "matched_threshold": row["threshold"],
                "actual_metric_val": row[col_name],
                "val_recall": row["recall"],
                "val_precision": row["precision"],
                "val_f1_score": row["f1_score"],
                "val_hn_fpr": row["hard_negative_fpr"],
                "val_shout_fpr": row["shouted_speech_fpr"],
                "val_short_recall": row["short_scream_recall"]
            })
            
    df_comp2 = pd.DataFrame(rows_comp2)
    csv_comp2 = "backend/research/stage_8_9_37/results/operating_point_comparisons/comparison2_matched_operating_conditions.csv"
    df_comp2.to_csv(csv_comp2, index=False)
    print(f"Saved {csv_comp2}")
    
    print("\n--- Summary of Matched HN-FPR ~ 5% (Gate 2 Target) ---")
    hn5 = df_comp2[df_comp2['condition'] == "Matched HN-FPR ~ 5%"]
    for _, r in hn5.iterrows():
        print(f"[{r['model_name']}] th={r['matched_threshold']:.2f} | HN-FPR={r['val_hn_fpr']*100:.2f}% | Recall={r['val_recall']*100:.2f}% | Shout-FPR={r['val_shout_fpr']*100:.2f}%")
        
    print("\n--- Summary of Matched Recall ~ 80% ---")
    rec80 = df_comp2[df_comp2['condition'] == "Matched Recall ~ 80%"]
    for _, r in rec80.iterrows():
        print(f"[{r['model_name']}] th={r['matched_threshold']:.2f} | Recall={r['val_recall']*100:.2f}% | HN-FPR={r['val_hn_fpr']*100:.2f}% | Shout-FPR={r['val_shout_fpr']*100:.2f}%")

if __name__ == "__main__":
    run_matched_comparison()
