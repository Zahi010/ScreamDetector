"""
Stage 8.9.36 - Phase 1: Baseline Reconciliation Script
Audits and reconciles the discrepancy between Stage 8.9.34 (86/102 detections at 0.35)
and Stage 8.9.35 (84/102 detections at 0.43).
"""
import os
import json
import numpy as np
import pandas as pd

def reconcile():
    print("======================================================================")
    print("STAGE 8.9.36 - PHASE 1: BASELINE RECONCILIATION AUDIT")
    print("======================================================================")
    
    p33_path = "backend/research/stage_8_9_33/predictions/test_predictions_stage8_9_33.csv"
    p34_path = "backend/research/stage_8_9_34/predictions/test_predictions_stage8_9_34.csv"
    p35_path = "backend/research/stage_8_9_35/predictions/test_predictions_stage8_9_35.csv"
    
    assert os.path.exists(p33_path), f"Missing {p33_path}"
    assert os.path.exists(p34_path), f"Missing {p34_path}"
    assert os.path.exists(p35_path), f"Missing {p35_path}"
    
    df33 = pd.read_csv(p33_path)
    df34 = pd.read_csv(p34_path)
    df35 = pd.read_csv(p35_path)
    
    # Verify test set alignment
    assert len(df33) == len(df34) == len(df35) == 293
    assert (df33['file_id'] == df34['file_id']).all()
    assert (df33['file_id'] == df35['file_id']).all()
    print("Verified: Test cohort file IDs are 100% identical and in identical order (N=293).")
    
    y_true = df33['ground_truth'].values # 102 screams, 191 hard negatives
    probs = df33['dual_encoder_probability'].values
    
    # Calculate baseline metrics at 0.35 and 0.43
    thresholds = [0.35, 0.43]
    recomputed = {}
    
    for th in thresholds:
        preds = (probs >= th).astype(int)
        tp = int(np.sum((preds == 1) & (y_true == 1)))
        fn = int(np.sum((preds == 0) & (y_true == 1)))
        fp = int(np.sum((preds == 1) & (y_true == 0)))
        tn = int(np.sum((preds == 0) & (y_true == 0)))
        
        rec = tp / (tp + fn)
        fpr = fp / (fp + tn)
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        spec = tn / (tn + fp)
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
        
        # Shout FPR (category == 'shouted_speech' or 'shout')
        shout_mask = (y_true == 0) & (df33['category'].str.lower().str.contains('shout'))
        shout_total = int(np.sum(shout_mask))
        shout_fp = int(np.sum((preds == 1) & shout_mask))
        shout_fpr = shout_fp / shout_total if shout_total > 0 else 0.0
        
        recomputed[f"threshold_{th}"] = {
            "threshold": th,
            "tp": tp, "fn": fn, "fp": fp, "tn": tn,
            "recall": round(rec * 100, 2),
            "hn_fpr": round(fpr * 100, 2),
            "shout_fpr": round(shout_fpr * 100, 2),
            "shout_fp": shout_fp,
            "shout_total": shout_total,
            "precision": round(prec * 100, 2),
            "specificity": round(spec * 100, 2),
            "f1": round(f1, 4)
        }
        print(f"\nRecomputed Baseline at Threshold {th:.2f}:")
        print(f"  Recall: {rec*100:.2f}% ({tp}/{tp+fn})")
        print(f"  HN-FPR: {fpr*100:.2f}% ({fp}/{fp+tn})")
        print(f"  Shout-FPR: {shout_fpr*100:.2f}% ({shout_fp}/{shout_total})")
        print(f"  F1: {f1:.4f}")

    # Identify recordings with differing decisions between 0.35 and 0.43
    pred_035 = (probs >= 0.35).astype(int)
    pred_043 = (probs >= 0.43).astype(int)
    diff_mask = (pred_035 != pred_043)
    
    diff_df = df33[diff_mask].copy()
    diff_df['prob'] = diff_df['dual_encoder_probability']
    diff_df['pred_at_035'] = pred_035[diff_mask]
    diff_df['pred_at_043'] = pred_043[diff_mask]
    diff_df['impact'] = diff_df.apply(
        lambda r: "Scream Missed at 0.43 (FN)" if r['ground_truth'] == 1 
        else "False Alarm Avoided at 0.43 (TN)", axis=1
    )
    
    diff_cols = ['file_id', 'category', 'source_group_id', 'ground_truth', 'prob', 'pred_at_035', 'pred_at_043', 'impact']
    diff_df = diff_df[diff_cols]
    
    print("\n--- RECORDINGS WITH DISCORDANT DECISIONS BETWEEN 0.35 AND 0.43 (N = %d) ---" % len(diff_df))
    print(diff_df.to_string(index=False))
    
    # Save outputs
    eval_dir = "backend/research/stage_8_9_36/evaluation"
    os.makedirs(eval_dir, exist_ok=True)
    
    diff_csv_path = os.path.join(eval_dir, "baseline_prediction_diff.csv")
    diff_df.to_csv(diff_csv_path, index=False)
    print(f"\nSaved {diff_csv_path}")
    
    json_path = os.path.join(eval_dir, "baseline_recomputed_metrics.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(recomputed, f, indent=2)
    print(f"Saved {json_path}")
    
    return recomputed, diff_df

if __name__ == "__main__":
    reconcile()
