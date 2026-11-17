import os
import sys
import json
import csv
from pathlib import Path
import numpy as np

BACKEND_DIR = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector\backend")
STAGE_DIR = BACKEND_DIR / "research" / "stage_8_9_39"
PRED_DIR = STAGE_DIR / "predictions" / "validation"
RESULTS_DIR = STAGE_DIR / "results" / "thresholds"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_DIR = STAGE_DIR / "config"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# Also load durations from research_split_v4.csv to identify short screams in validation
SPLIT_CSV = BACKEND_DIR / "research" / "stage_8_9_38" / "manifests" / "research_split_v4.csv"

def run_threshold_sweep(val_csv_path, model_name):
    with open(val_csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    with open(SPLIT_CSV, "r", encoding="utf-8") as f:
        split_dict = {r["file_id"]: float(r["duration_seconds"]) for r in csv.DictReader(f)}

    y_true = np.array([int(r['ground_truth']) for r in rows])
    y_prob = np.array([float(r['probability']) for r in rows])
    categories = np.array([r['category'] for r in rows])
    durations = np.array([split_dict.get(r['file_id'], 2.0) for r in rows])

    n_total = len(y_true)
    n_pos = np.sum(y_true == 1)
    n_neg = np.sum(y_true == 0)

    # Shouted speech mask
    shout_mask = (categories == 'shouting_and_speech')
    n_shout = np.sum(shout_mask)

    # Short scream mask: positive screams with duration <= 1.0s
    short_scream_mask = (y_true == 1) & (durations <= 1.0)
    n_short_scream = np.sum(short_scream_mask)

    print(f"\n[{model_name}] Validation Cohort Breakdown (N={n_total}):")
    print(f"  Positives (Screams): {n_pos}")
    print(f"  Negatives (Hard Negatives): {n_neg}")
    print(f"  Shouted Speech Negatives: {n_shout}")
    print(f"  Short Screams (<= 1.0s): {n_short_scream}")

    thresholds = [round(t, 2) for t in np.arange(0.05, 0.951, 0.01)]
    sweep_results = []

    for th in thresholds:
        y_pred = (y_prob >= th).astype(int)

        tp = int(np.sum((y_true == 1) & (y_pred == 1)))
        fp = int(np.sum((y_true == 0) & (y_pred == 1)))
        tn = int(np.sum((y_true == 0) & (y_pred == 0)))
        fn = int(np.sum((y_true == 1) & (y_pred == 0)))

        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
        spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        hn_fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        bal_acc = (rec + spec) / 2.0

        # Shouted speech FPR
        if n_shout > 0:
            shout_fp = int(np.sum(shout_mask & (y_pred == 1)))
            shout_fpr = shout_fp / n_shout
        else:
            shout_fp = 0
            shout_fpr = 0.0

        # Short scream recall
        if n_short_scream > 0:
            ss_tp = int(np.sum(short_scream_mask & (y_pred == 1)))
            ss_rec = ss_tp / n_short_scream
        else:
            ss_tp = 0
            ss_rec = 0.0

        # Distance to ideal (Recall=1.0, HN-FPR=0.0)
        dist_to_ideal = np.sqrt((1.0 - rec)**2 + (hn_fpr - 0.0)**2)

        sweep_results.append({
            'threshold': float(th),
            'tp': int(tp),
            'fp': int(fp),
            'tn': int(tn),
            'fn': int(fn),
            'precision': float(round(prec, 4)),
            'recall': float(round(rec, 4)),
            'f1': float(round(f1, 4)),
            'specificity': float(round(spec, 4)),
            'hn_fpr': float(round(hn_fpr, 4)),
            'shout_fpr': float(round(shout_fpr, 4)),
            'shout_fp': int(shout_fp),
            'shout_n': int(n_shout),
            'short_scream_recall': float(round(ss_rec, 4)),
            'short_scream_tp': int(ss_tp),
            'short_scream_n': int(n_short_scream),
            'balanced_accuracy': float(round(bal_acc, 4)),
            'distance_to_ideal': float(round(dist_to_ideal, 4))
        })

    # Operating Point Selection
    # Operating Point A: Max Validation F1 (tie-breaker: higher recall, then lower threshold)
    sorted_by_f1 = sorted(sweep_results, key=lambda x: (x['f1'], x['recall'], -x['threshold']), reverse=True)
    point_a = sorted_by_f1[0]

    # Operating Point B: Recall-Oriented (Recall >= 90% with minimum HN-FPR)
    recall_90 = [r for r in sweep_results if r['recall'] >= 0.90]
    if recall_90:
        point_b = sorted(recall_90, key=lambda x: (x['hn_fpr'], -x['recall'], x['threshold']))[0]
    else:
        # Fallback to maximum recall
        point_b = sorted(sweep_results, key=lambda x: (x['recall'], -x['hn_fpr']))[0]

    # Operating Point C: False-Alarm-Oriented (Minimum HN-FPR with Recall >= 80%)
    recall_80 = [r for r in sweep_results if r['recall'] >= 0.80]
    if recall_80:
        point_c = sorted(recall_80, key=lambda x: (x['hn_fpr'], -x['f1'], x['threshold']))[0]
    else:
        point_c = sorted(sweep_results, key=lambda x: (x['hn_fpr'], -x['f1']))[0]

    # Operating Point D: Balanced Operational Point (Minimum distance to (Recall=1, HN-FPR=0))
    point_d = sorted(sweep_results, key=lambda x: (x['distance_to_ideal'], -x['f1']))[0]

    operating_points = {
        'operating_point_a_max_f1': point_a,
        'operating_point_b_recall_oriented': point_b,
        'operating_point_c_fa_oriented': point_c,
        'operating_point_d_balanced': point_d
    }

    print(f"Selected Operating Points for {model_name}:")
    print(f"  Point A (Max F1):   theta={point_a['threshold']} | F1={point_a['f1']:.4f} | Rec={point_a['recall']:.4f} | HN-FPR={point_a['hn_fpr']:.4f} | Shout-FPR={point_a['shout_fpr']:.4f}")
    print(f"  Point B (Rec>=90%): theta={point_b['threshold']} | F1={point_b['f1']:.4f} | Rec={point_b['recall']:.4f} | HN-FPR={point_b['hn_fpr']:.4f} | Shout-FPR={point_b['shout_fpr']:.4f}")
    print(f"  Point C (FA-min):   theta={point_c['threshold']} | F1={point_c['f1']:.4f} | Rec={point_c['recall']:.4f} | HN-FPR={point_c['hn_fpr']:.4f} | Shout-FPR={point_c['shout_fpr']:.4f}")
    print(f"  Point D (Balanced): theta={point_d['threshold']} | F1={point_d['f1']:.4f} | Rec={point_d['recall']:.4f} | HN-FPR={point_d['hn_fpr']:.4f} | Shout-FPR={point_d['shout_fpr']:.4f}")

    return sweep_results, operating_points

def main():
    print("=" * 80)
    print("STAGE 8.9.39: VALIDATION-ONLY THRESHOLD SWEEP & OPERATING POINT SELECTION")
    print("=" * 80)

    # 1. Sweep Candidate B
    val_b = PRED_DIR / "config_b_val_predictions.csv"
    sweep_b, points_b = run_threshold_sweep(val_b, "Candidate B (DualEncoderAcousticModel)")

    csv_b = RESULTS_DIR / "config_b_validation_threshold_sweep.csv"
    with open(csv_b, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(sweep_b[0].keys()))
        w.writeheader()
        w.writerows(sweep_b)

    json_b = RESULTS_DIR / "config_b_operating_points.json"
    with open(json_b, "w", encoding="utf-8") as f:
        json.dump(points_b, f, indent=2)

    # 2. Sweep Candidate D
    val_d = PRED_DIR / "config_d_val_predictions.csv"
    sweep_d, points_d = run_threshold_sweep(val_d, "Candidate D (MultiPathwayFusionModel)")

    csv_d = RESULTS_DIR / "config_d_validation_threshold_sweep.csv"
    with open(csv_d, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(sweep_d[0].keys()))
        w.writeheader()
        w.writerows(sweep_d)

    json_d = RESULTS_DIR / "config_d_operating_points.json"
    with open(json_d, "w", encoding="utf-8") as f:
        json.dump(points_d, f, indent=2)

    # Master Threshold Configuration to Freeze
    master_threshold_config = {
        'candidate_b': {
            'model_name': 'DualEncoderAcousticModel',
            'operating_points': points_b,
            'primary_evaluation_threshold': points_b['operating_point_a_max_f1']['threshold'],
            'balanced_evaluation_threshold': points_b['operating_point_d_balanced']['threshold']
        },
        'candidate_d': {
            'model_name': 'MultiPathwayFusionModel',
            'operating_points': points_d,
            'primary_evaluation_threshold': points_d['operating_point_a_max_f1']['threshold'],
            'balanced_evaluation_threshold': points_d['operating_point_d_balanced']['threshold']
        },
        'protocol_constraints': {
            'sweep_range': [0.05, 0.95],
            'sweep_step': 0.01,
            'selection_cohort': 'v4_val_strictly_isolated',
            'test_cohort_exposure': False
        }
    }
    master_config_path = CONFIG_DIR / "threshold_config.json"
    with open(master_config_path, "w", encoding="utf-8") as f:
        json.dump(master_threshold_config, f, indent=2)
    print(f"\n[FROZEN] Master Threshold Config locked to: {master_config_path}")

if __name__ == "__main__":
    main()
