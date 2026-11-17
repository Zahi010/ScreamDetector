"""
Stage 8.9.36 - Phase 6: Short-Scream Evidence and Source-Group Audit Script
Audits all short scream recordings (<1.0s duration) across the dataset corpus,
analyzes duration brackets, source group independence, duplicate risks,
calculates 95% Wilson confidence intervals, and proposes an acquisition plan.
"""
import os
import json
import numpy as np
import pandas as pd

def wilson_score_interval(k, n, confidence=0.95):
    """Calculates Wilson score interval for binomial proportion."""
    if n == 0:
        return (0.0, 0.0)
    z = 1.95996 # 95% confidence
    p_hat = k / n
    denom = 1 + (z**2) / n
    center = (p_hat + (z**2) / (2 * n)) / denom
    margin = (z * np.sqrt((p_hat * (1 - p_hat) / n) + (z**2) / (4 * n**2))) / denom
    lower = max(0.0, center - margin)
    upper = min(1.0, center + margin)
    return (round(lower * 100, 2), round(upper * 100, 2))

def audit_short_screams():
    print("======================================================================")
    print("STAGE 8.9.36 - PHASE 6: SHORT-SCREAM EVIDENCE & SOURCE-GROUP AUDIT")
    print("======================================================================")
    
    manifest_path = "backend/experiments/v2_hard_negative_training/manifests/dataset_manifest_v3.csv"
    p35_path = "backend/research/stage_8_9_35/predictions/test_predictions_stage8_9_35.csv"
    
    manifest = pd.read_csv(manifest_path)
    p35_df = pd.read_csv(p35_path)
    p35_map = {r['file_id']: r for _, r in p35_df.iterrows()}
    
    screams = manifest[manifest['binary_label'] == 'scream'].copy()
    print(f"Total Scream Recordings in Corpus: {len(screams)}")
    
    bins = [0.0, 0.5, 0.8, 1.0, 1.5, 999.0]
    labels = ['<0.5s', '0.5-0.8s', '0.8-1.0s', '1.0-1.5s', '>1.5s']
    screams['bracket'] = pd.cut(screams['duration_seconds'], bins=bins, labels=labels, right=False)
    
    # 1. Corpus Duration Breakdown
    corpus_breakdown = []
    for b in labels:
        b_all = screams[screams['bracket'] == b]
        b_train = screams[(screams['bracket'] == b) & (screams['split'] == 'train')]
        b_val = screams[(screams['bracket'] == b) & (screams['split'] == 'val')]
        b_test = screams[(screams['bracket'] == b) & (screams['split'] == 'test')]
        
        # Test detection metrics
        test_detected = 0
        for fid in b_test['file_id']:
            if fid in p35_map and p35_map[fid]['predicted_binary'] == 1:
                test_detected += 1
                
        test_n = len(b_test)
        test_rec = (test_detected / test_n * 100) if test_n > 0 else 0.0
        ci_low, ci_high = wilson_score_interval(test_detected, test_n) if test_n > 0 else (0.0, 0.0)
        
        corpus_breakdown.append({
            "bracket": b,
            "total_corpus_files": len(b_all),
            "total_source_groups": b_all['source_group_id'].nunique(),
            "train_files": len(b_train),
            "val_files": len(b_val),
            "test_files": test_n,
            "test_detected": test_detected,
            "test_recall_pct": round(test_rec, 2) if test_n > 0 else "N/A",
            "wilson_95_ci": f"[{ci_low}%, {ci_high}%]" if test_n > 0 else "N/A",
            "evidence_status": "ADEQUATE" if test_n >= 30 else ("INSUFFICIENT SAMPLE SIZE (<30)" if test_n > 0 else "ZERO SAMPLES")
        })
        
    print("\n--- CORPUS DURATION BRACKET SUMMARY ---")
    df_bracket = pd.DataFrame(corpus_breakdown)
    print(df_bracket.to_string(index=False))

    # 2. Source-Group Analysis for Short Screams (<1.0s)
    short_screams = screams[screams['duration_seconds'] < 1.0].copy()
    print(f"\nTotal Short Screams in Full Corpus (<1.0s): {len(short_screams)}")
    print(f"Unique Source Groups in Short Screams: {short_screams['source_group_id'].nunique()}")
    
    short_rows = []
    for idx, r in short_screams.iterrows():
        fid = r['file_id']
        test_pred = p35_map.get(fid, None)
        
        det_status = "N/A (Not in Test)"
        cand_prob = "N/A"
        if test_pred is not None:
            det_status = "DETECTED (TP)" if test_pred['predicted_binary'] == 1 else "MISSED (FN)"
            cand_prob = round(float(test_pred['mp_dual_encoder_probability']), 4)
            
        # Check potential duplicate source recording
        orig_id = str(r['original_recording_id'])
        is_synth = r['is_synthesized']
        
        short_rows.append({
            "file_id": fid,
            "split": r['split'],
            "duration_sec": round(float(r['duration_seconds']), 3),
            "duration_bracket": str(r['bracket']),
            "source_group_id": r['source_group_id'],
            "original_recording_id": orig_id,
            "creator": r['creator'],
            "license": r['license'],
            "is_synthesized": is_synth,
            "test_detection_status": det_status,
            "candidate_d_prob": cand_prob
        })
        
    df_short = pd.DataFrame(short_rows)
    eval_dir = "backend/research/stage_8_9_36/evaluation"
    os.makedirs(eval_dir, exist_ok=True)
    out_csv = os.path.join(eval_dir, "short_scream_source_group_analysis.csv")
    df_short.to_csv(out_csv, index=False)
    print(f"Saved {out_csv}")
    
    # Check for multiple files from same original recording or uploader
    print("\nSource Group Concentration in Short Screams:")
    print(df_short['source_group_id'].value_counts())
    
    return corpus_breakdown, df_short

if __name__ == '__main__':
    audit_short_screams()
