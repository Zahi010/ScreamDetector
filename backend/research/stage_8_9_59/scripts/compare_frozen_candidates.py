import os
import json
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, precision_recall_curve, auc, precision_score, recall_score, f1_score

# MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
STAGE_DIR = os.path.join(REPO_ROOT, "backend", "research", "stage_8_9_59")
STAGE54_DIR = os.path.join(REPO_ROOT, "backend", "research", "stage_8_9_54")
STAGE58_DIR = os.path.join(REPO_ROOT, "backend", "research", "stage_8_9_58")

def compute_metrics(y_true, y_pred, y_prob):
    tp = int(((y_true == 1) & (y_pred == 1)).sum())
    fp = int(((y_true == 0) & (y_pred == 1)).sum())
    fn = int(((y_true == 1) & (y_pred == 0)).sum())
    tn = int(((y_true == 0) & (y_pred == 0)).sum())
    
    rec = tp / max(tp + fn, 1)
    prec = tp / max(tp + fp, 1)
    f1 = 2 * prec * rec / max(prec + rec, 1e-9)
    fpr = fp / max(fp + tn, 1)
    
    roc_auc = float(roc_auc_score(y_true, y_prob))
    p_curve, r_curve, _ = precision_recall_curve(y_true, y_prob)
    pr_auc = float(auc(r_curve, p_curve))
    
    return {
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "recall": round(rec, 4),
        "precision": round(prec, 4),
        "f1": round(f1, 4),
        "fpr": round(fpr, 4),
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4)
    }

def main():
    print("Executing Phase D: Cross-Candidate Error Comparison...")
    
    df54 = pd.read_csv(os.path.join(STAGE54_DIR, "evaluation", "validation_predictions.csv"))
    df58 = pd.read_csv(os.path.join(STAGE58_DIR, "prediction_comparison.csv"))
    
    y_true = df58["ground_truth_label"].values
    durs = df58["duration_seconds"].values
    cats = df58["target_category"].values
    
    # Candidate 1: Candidate E1 + C5 (frozen theta = 0.6800)
    e1_prob = df58["c5_probability"].values
    e1_pred = df58["c5_prediction"].values
    
    # Candidate 2: Candidate B baseline (frozen theta = 0.8000)
    b_prob = df54["candidate_b_baseline_prob"].values
    b_pred = df54["candidate_b_baseline_pred"].values
    
    # Candidate 3: Candidate B + Intervention D (frozen theta = 0.8000 + whistle veto)
    bd_prob = df54["candidate_b_+_intervention_d_prob"].values
    bd_pred = df54["candidate_b_+_intervention_d_pred"].values
    
    candidates = [
        {"name": "Candidate E1 + C5", "prob": e1_prob, "pred": e1_pred, "theta": 0.6800, "lat_p50": 0.49, "lat_p95": 0.50},
        {"name": "Candidate B Baseline", "prob": b_prob, "pred": b_pred, "theta": 0.8000, "lat_p50": 0.62, "lat_p95": 0.68},
        {"name": "Candidate B + Intervention D", "prob": bd_prob, "pred": bd_pred, "theta": 0.8000, "lat_p50": 0.75, "lat_p95": 0.82}
    ]
    
    summary_metrics = []
    for cand in candidates:
        m = compute_metrics(y_true, cand["pred"], cand["prob"])
        
        # Subgroup metrics
        short_mask = (y_true == 1) & (durs < 1.0)
        sustained_mask = (y_true == 1) & (durs >= 1.0)
        ultra_short_mask = (y_true == 1) & (durs < 0.5)
        shout_mask = (y_true == 0) & (cats == "shouting_and_speech")
        
        short_rec = cand["pred"][short_mask].sum() / max(short_mask.sum(), 1)
        sust_rec = cand["pred"][sustained_mask].sum() / max(sustained_mask.sum(), 1)
        ultra_rec = cand["pred"][ultra_short_mask].sum() / max(ultra_short_mask.sum(), 1)
        shout_fpr = cand["pred"][shout_mask].sum() / max(shout_mask.sum(), 1)
        
        summary_metrics.append({
            "candidate": cand["name"],
            "threshold": cand["theta"],
            "recall": m["recall"],
            "precision": m["precision"],
            "f1": m["f1"],
            "hard_negative_fpr": m["fpr"],
            "shouted_speech_fpr": round(float(shout_fpr), 4),
            "short_scream_recall": round(float(short_rec), 4),
            "sustained_scream_recall": round(float(sust_rec), 4),
            "ultra_short_recall": round(float(ultra_rec), 4),
            "roc_auc": m["roc_auc"],
            "pr_auc": m["pr_auc"],
            "model_latency_p50_ms": cand["lat_p50"],
            "model_latency_p95_ms": cand["lat_p95"],
            "tp": m["tp"],
            "fp": m["fp"],
            "fn": m["fn"],
            "tn": m["tn"]
        })
        
    df_summary = pd.DataFrame(summary_metrics)
    print("\nSummary Candidate Comparison Matrix:")
    print(df_summary[["candidate", "recall", "hard_negative_fpr", "shouted_speech_fpr", "short_scream_recall", "sustained_scream_recall", "f1", "roc_auc"]])
    
    # Detailed recording-level comparison
    comp_rows = []
    for i in range(len(y_true)):
        fid = df58.loc[i, "expansion_file_id"]
        gt = int(y_true[i])
        cat = cats[i]
        dur = durs[i]
        
        p_e1 = e1_pred[i]
        p_b = b_pred[i]
        p_bd = bd_pred[i]
        
        prob_e1 = e1_prob[i]
        prob_b = b_prob[i]
        prob_bd = bd_prob[i]
        
        # Agreement check
        all_agree = (p_e1 == p_b == p_bd)
        disagreement = not all_agree
        
        # FN classifications
        is_fn_e1 = (gt == 1 and p_e1 == 0)
        is_fn_b = (gt == 1 and p_b == 0)
        is_fn_bd = (gt == 1 and p_bd == 0)
        
        shared_fn = (is_fn_e1 and is_fn_b and is_fn_bd)
        unique_fn_e1 = (is_fn_e1 and not is_fn_b and not is_fn_bd)
        unique_fn_b = (is_fn_b and not is_fn_e1)
        
        # FP classifications
        is_fp_e1 = (gt == 0 and p_e1 == 1)
        is_fp_b = (gt == 0 and p_b == 1)
        is_fp_bd = (gt == 0 and p_bd == 1)
        
        shared_fp = (is_fp_e1 and is_fp_b and is_fp_bd)
        unique_fp_e1 = (is_fp_e1 and not is_fp_b and not is_fp_bd)
        unique_fp_b = (is_fp_b and not is_fp_e1)
        
        comp_rows.append({
            "expansion_file_id": fid,
            "target_category": cat,
            "duration_seconds": dur,
            "ground_truth_label": gt,
            "cand_e1_prob": round(float(prob_e1), 6),
            "cand_e1_pred": int(p_e1),
            "cand_b_prob": round(float(prob_b), 6),
            "cand_b_pred": int(p_b),
            "cand_bd_prob": round(float(prob_bd), 6),
            "cand_bd_pred": int(p_bd),
            "all_candidates_agree": all_agree,
            "disagreement": disagreement,
            "shared_false_negative": shared_fn,
            "unique_fn_cand_e1": unique_fn_e1,
            "unique_fn_cand_b": unique_fn_b,
            "shared_false_positive": shared_fp,
            "unique_fp_cand_e1": unique_fp_e1,
            "unique_fp_cand_b": unique_fp_b
        })
        
    df_comp = pd.DataFrame(comp_rows)
    comp_csv = os.path.join(STAGE_DIR, "candidate_error_comparison.csv")
    df_comp.to_csv(comp_csv, index=False)
    print(f"\nSaved {len(df_comp)} recording comparisons to {comp_csv}")
    
    # Disagreements summary
    n_disagree = df_comp["disagreement"].sum()
    print(f"Total recordings where candidates disagree: {n_disagree} / 311 ({n_disagree/311*100:.2f}%)")
    print(f"Shared False Negatives: {df_comp['shared_false_negative'].sum()}")
    print(f"Unique FN Cand E1: {df_comp['unique_fn_cand_e1'].sum()} | Unique FN Cand B: {df_comp['unique_fn_cand_b'].sum()}")
    print(f"Shared False Positives: {df_comp['shared_false_positive'].sum()}")
    print(f"Unique FP Cand E1: {df_comp['unique_fp_cand_e1'].sum()} | Unique FP Cand B: {df_comp['unique_fp_cand_b'].sum()}")

    # Save summary json
    with open(os.path.join(STAGE_DIR, "cross_candidate_summary.json"), "w") as f:
        json.dump(summary_metrics, f, indent=2)

if __name__ == "__main__":
    main()

