import os
import sys
import json
import csv
from pathlib import Path
from collections import defaultdict
import numpy as np

BACKEND_DIR = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector\backend")
STAGE_DIR = BACKEND_DIR / "research" / "stage_8_9_39"
PRED_DIR = STAGE_DIR / "predictions"
RESULTS_DIR = STAGE_DIR / "results" / "metrics"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
THRESH_CONFIG = STAGE_DIR / "config" / "threshold_config.json"

def analyze_model_errors(pred_csv_path, threshold, model_name, cohort_name, ground_truth_col='ground_truth'):
    with open(pred_csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    fn_list = []
    fp_list = []
    tp_list = []
    tn_list = []

    cat_breakdown = defaultdict(lambda: {'total': 0, 'tp': 0, 'fp': 0, 'tn': 0, 'fn': 0})
    sg_fn_counts = defaultdict(int)
    sg_fp_counts = defaultdict(int)

    for r in rows:
        fid = r['file_id']
        cat = r['category']
        sg = r['source_group_id']
        prob = float(r['probability'])
        y = int(r.get(ground_truth_col, r.get('ground_truth_view_a', 0)))
        pred = 1 if prob >= threshold else 0

        cat_breakdown[cat]['total'] += 1

        if y == 1 and pred == 1:
            tp_list.append(r)
            cat_breakdown[cat]['tp'] += 1
        elif y == 1 and pred == 0:
            fn_list.append(r)
            cat_breakdown[cat]['fn'] += 1
            sg_fn_counts[sg] += 1
        elif y == 0 and pred == 1:
            fp_list.append(r)
            cat_breakdown[cat]['fp'] += 1
            sg_fp_counts[sg] += 1
        else:
            tn_list.append(r)
            cat_breakdown[cat]['tn'] += 1

    fn_by_cat = {c: cat_breakdown[c]['fn'] for c in cat_breakdown if cat_breakdown[c]['fn'] > 0}
    fp_by_cat = {c: cat_breakdown[c]['fp'] for c in cat_breakdown if cat_breakdown[c]['fp'] > 0}

    print(f"\n[{model_name}] Error Forensics on {cohort_name} (Threshold theta={threshold:.2f}):")
    print(f"  Total Clips: {len(rows)} | TP: {len(tp_list)} | TN: {len(tn_list)} | FN: {len(fn_list)} | FP: {len(fp_list)}")
    print(f"  False Negatives by Category: {fn_by_cat}")
    print(f"  False Positives by Category: {fp_by_cat}")
    if sg_fn_counts:
        top_sg_fn = sorted(sg_fn_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        print(f"  Top FN Source Groups: {top_sg_fn}")
    if sg_fp_counts:
        top_sg_fp = sorted(sg_fp_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        print(f"  Top FP Source Groups: {top_sg_fp}")

    return {
        'model_name': model_name,
        'cohort': cohort_name,
        'threshold': float(threshold),
        'counts': {'tp': len(tp_list), 'tn': len(tn_list), 'fn': len(fn_list), 'fp': len(fp_list)},
        'fn_by_category': fn_by_cat,
        'fp_by_category': fp_by_cat,
        'category_breakdown': dict(cat_breakdown),
        'fn_source_groups': dict(sg_fn_counts),
        'fp_source_groups': dict(sg_fp_counts),
        'false_negatives': fn_list,
        'false_positives': fp_list
    }

def main():
    print("=" * 80)
    print("STAGE 8.9.39: COMPREHENSIVE ERROR ANALYSIS & HUMAN-REVIEW QUEUE")
    print("=" * 80)

    with open(THRESH_CONFIG, "r", encoding="utf-8") as f:
        thresh_cfg = json.load(f)

    th_b = thresh_cfg['candidate_b']['primary_evaluation_threshold']
    th_d = thresh_cfg['candidate_d']['primary_evaluation_threshold']

    # 1. Historical Test Cohort
    hist_b_path = PRED_DIR / "historical_test" / "config_b_historical_predictions.csv"
    hist_d_path = PRED_DIR / "historical_test" / "config_d_historical_predictions.csv"

    # View A Analysis (Original Labels)
    hist_b_err_a = analyze_model_errors(hist_b_path, th_b, "Candidate B", "Historical Test (View A)", 'ground_truth_view_a')
    hist_d_err_a = analyze_model_errors(hist_d_path, th_d, "Candidate D", "Historical Test (View A)", 'ground_truth_view_a')

    # View B Analysis (Adjudicated Labels)
    hist_b_err_b = analyze_model_errors(hist_b_path, th_b, "Candidate B", "Historical Test (View B)", 'ground_truth_view_b')
    hist_d_err_b = analyze_model_errors(hist_d_path, th_d, "Candidate D", "Historical Test (View B)", 'ground_truth_view_b')

    # 2. Expansion Test Cohort
    exp_b_path = PRED_DIR / "expansion_test" / "config_b_expansion_predictions.csv"
    exp_d_path = PRED_DIR / "expansion_test" / "config_d_expansion_predictions.csv"

    exp_b_err = analyze_model_errors(exp_b_path, th_b, "Candidate B", "Reserved Expansion Test", 'ground_truth')
    exp_d_err = analyze_model_errors(exp_d_path, th_d, "Candidate D", "Reserved Expansion Test", 'ground_truth')

    # 3. Build Human-Review Queue
    # Flag clips where models disagree or confidence is near boundary [0.20, 0.45]
    review_queue = []
    
    with open(hist_b_path, "r", encoding="utf-8") as f:
        b_hist_rows = {r['file_id']: r for r in csv.DictReader(f)}
    with open(hist_d_path, "r", encoding="utf-8") as f:
        d_hist_rows = {r['file_id']: r for r in csv.DictReader(f)}

    for fid, r_b in b_hist_rows.items():
        r_d = d_hist_rows[fid]
        prob_b = float(r_b['probability'])
        prob_d = float(r_d['probability'])
        y_a = int(r_b['ground_truth_view_a'])
        y_b = int(r_b['ground_truth_view_b'])
        
        pred_b = 1 if prob_b >= th_b else 0
        pred_d = 1 if prob_d >= th_d else 0

        # Review criteria: either model made an error, or model disagreement, or boundary probability
        is_error = (pred_b != y_b) or (pred_d != y_b)
        is_disagreement = (pred_b != pred_d)
        is_boundary = (0.20 <= prob_b <= 0.45) or (0.20 <= prob_d <= 0.45)

        if is_error or is_disagreement:
            reason = []
            if pred_b != y_b:
                reason.append(f"Candidate B {'FN' if y_b==1 else 'FP'} (prob={prob_b:.4f})")
            if pred_d != y_b:
                reason.append(f"Candidate D {'FN' if y_b==1 else 'FP'} (prob={prob_d:.4f})")
            if is_disagreement:
                reason.append("Model Decision Disagreement")

            review_queue.append({
                'cohort': 'v4_historical_test',
                'file_id': fid,
                'category': r_b['category'],
                'source_group_id': r_b['source_group_id'],
                'duration_seconds': r_b['duration_seconds'],
                'ground_truth_view_a': y_a,
                'ground_truth_view_b': y_b,
                'cand_b_prob': round(prob_b, 4),
                'cand_b_pred': pred_b,
                'cand_d_prob': round(prob_d, 4),
                'cand_d_pred': pred_d,
                'review_priority': 'HIGH' if (is_disagreement and is_error) else 'MEDIUM',
                'review_reason': "; ".join(reason)
            })

    review_csv = RESULTS_DIR / "human_review_queue.csv"
    with open(review_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            'cohort', 'file_id', 'category', 'source_group_id', 'duration_seconds',
            'ground_truth_view_a', 'ground_truth_view_b',
            'cand_b_prob', 'cand_b_pred', 'cand_d_prob', 'cand_d_pred',
            'review_priority', 'review_reason'
        ])
        w.writeheader()
        w.writerows(review_queue)
    print(f"\nGenerated human-review queue: {len(review_queue)} flagged clips saved to {review_csv}")

    # Save complete error summary JSON
    summary = {
        'candidate_b': {
            'historical_view_a': {k: v for k, v in hist_b_err_a.items() if k not in ('false_negatives', 'false_positives')},
            'historical_view_b': {k: v for k, v in hist_b_err_b.items() if k not in ('false_negatives', 'false_positives')},
            'expansion_test': {k: v for k, v in exp_b_err.items() if k not in ('false_negatives', 'false_positives')}
        },
        'candidate_d': {
            'historical_view_a': {k: v for k, v in hist_d_err_a.items() if k not in ('false_negatives', 'false_positives')},
            'historical_view_b': {k: v for k, v in hist_d_err_b.items() if k not in ('false_negatives', 'false_positives')},
            'expansion_test': {k: v for k, v in exp_d_err.items() if k not in ('false_negatives', 'false_positives')}
        },
        'human_review_queue_count': len(review_queue)
    }

    out_json = RESULTS_DIR / "error_analysis_summary.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Error analysis summary saved to: {out_json}")

if __name__ == "__main__":
    main()
