import os
import sys
import json
import csv
from pathlib import Path
import numpy as np
import torch
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, average_precision_score, confusion_matrix

BACKEND_DIR = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector\backend")
sys.path.insert(0, str(BACKEND_DIR))

STAGE_DIR = BACKEND_DIR / "research" / "stage_8_9_39"
sys.path.insert(0, str(STAGE_DIR))

CACHE_PATH = STAGE_DIR / "cache" / "stage_8_9_39_features.npz"
CKPT_DIR_B = STAGE_DIR / "checkpoints" / "config_b"
CKPT_DIR_D = STAGE_DIR / "checkpoints" / "config_d"
THRESH_CONFIG = STAGE_DIR / "config" / "threshold_config.json"
PRED_DIR = STAGE_DIR / "predictions" / "historical_test"
PRED_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR = STAGE_DIR / "results" / "metrics"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

from scripts.train_config_b import DualEncoderAcousticModel
from scripts.train_config_d import MultiPathwayFusionModel

ADJ_FILE_1 = "v2_nigens_242607__reitanna__gasp-oooh"
ADJ_FILE_2 = "v2_nigens_242644__reitanna__another-surprised-oooh"

def wilson_score_interval(k, n, confidence=0.95):
    if n == 0:
        return 0.0, 0.0, 0.0
    z = 1.95996 # 95%
    p_hat = k / n
    denom = 1 + (z**2) / n
    center = (p_hat + (z**2) / (2 * n)) / denom
    margin = (z / denom) * np.sqrt((p_hat * (1 - p_hat) / n) + (z**2) / (4 * n**2))
    ci_low = max(0.0, center - margin)
    ci_high = min(1.0, center + margin)
    return float(p_hat), float(ci_low), float(ci_high)

def compute_metrics(y_true, y_prob, threshold, categories, durations):
    y_pred = (y_prob >= threshold).astype(int)
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))

    n_pos = tp + fn
    n_neg = fp + tn

    rec, rec_low, rec_high = wilson_score_interval(tp, n_pos)
    hn_fpr, fpr_low, fpr_high = wilson_score_interval(fp, n_neg)

    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
    
    # Shouted speech FPR
    shout_mask = (categories == 'shouting_and_speech')
    n_shout = int(np.sum(shout_mask))
    if n_shout > 0:
        shout_fp = int(np.sum(shout_mask & (y_pred == 1)))
        shout_fpr, shout_low, shout_high = wilson_score_interval(shout_fp, n_shout)
    else:
        shout_fp = 0
        shout_fpr, shout_low, shout_high = 0.0, 0.0, 0.0

    # Short screams recall (screams with dur <= 1.0s)
    short_scream_mask = (y_true == 1) & (durations <= 1.0)
    n_short_scream = int(np.sum(short_scream_mask))
    if n_short_scream > 0:
        ss_tp = int(np.sum(short_scream_mask & (y_pred == 1)))
        ss_rec, ss_low, ss_high = wilson_score_interval(ss_tp, n_short_scream)
    else:
        ss_tp = 0
        ss_rec, ss_low, ss_high = 0.0, 0.0, 0.0

    try:
        roc_auc = float(roc_auc_score(y_true, y_prob))
    except Exception:
        roc_auc = 0.5
    try:
        pr_auc = float(average_precision_score(y_true, y_prob))
    except Exception:
        pr_auc = 0.0

    return {
        'threshold': float(threshold),
        'tp': tp, 'fp': fp, 'tn': tn, 'fn': fn,
        'scream_recall': {
            'value': round(rec, 4), 'fraction': f"{tp}/{n_pos}",
            'ci95': [round(rec_low, 4), round(rec_high, 4)]
        },
        'hard_negative_fpr': {
            'value': round(hn_fpr, 4), 'fraction': f"{fp}/{n_neg}",
            'ci95': [round(fpr_low, 4), round(fpr_high, 4)]
        },
        'shouted_speech_fpr': {
            'value': round(shout_fpr, 4), 'fraction': f"{shout_fp}/{n_shout}",
            'ci95': [round(shout_low, 4), round(shout_high, 4)]
        },
        'short_scream_recall': {
            'value': round(ss_rec, 4), 'fraction': f"{ss_tp}/{n_short_scream}",
            'ci95': [round(ss_low, 4), round(ss_high, 4)]
        },
        'precision': round(prec, 4),
        'f1_score': round(f1, 4),
        'roc_auc': round(roc_auc, 4),
        'pr_auc': round(pr_auc, 4)
    }

def main():
    print("=" * 80)
    print("STAGE 8.9.39: EVALUATION A — HISTORICAL CONTINUITY BENCHMARK (N=293)")
    print("=" * 80)

    with open(THRESH_CONFIG, "r", encoding="utf-8") as f:
        thresh_cfg = json.load(f)

    # 1. Load Data
    data = np.load(CACHE_PATH, allow_pickle=True)
    splits = data['splits']
    hist_idx = np.where(splits == 'v4_historical_test')[0]

    # Load durations from split csv
    split_csv = BACKEND_DIR / "research" / "stage_8_9_38" / "manifests" / "research_split_v4.csv"
    with open(split_csv, "r", encoding="utf-8") as f:
        split_dict = {r["file_id"]: float(r["duration_seconds"]) for r in csv.DictReader(f)}

    file_ids = data['file_ids'][hist_idx]
    categories = data['categories'][hist_idx]
    source_groups = data['source_groups'][hist_idx]
    durations = np.array([split_dict.get(fid, 2.0) for fid in file_ids])

    # View A: Original Label (both gasp-oooh files are scream = 1)
    y_view_a = data['labels'][hist_idx].copy()
    
    # View B: Adjudicated Label (both gasp-oooh files are non_scream = 0)
    y_view_b = y_view_a.copy()
    for i, fid in enumerate(file_ids):
        if fid in (ADJ_FILE_1, ADJ_FILE_2):
            y_view_b[i] = 0

    print(f"Historical Test Set N = {len(hist_idx)}")
    print(f"  View A (Original):    Screams={np.sum(y_view_a == 1)} (Expected: 102), Negatives={np.sum(y_view_a == 0)} (Expected: 191)")
    print(f"  View B (Adjudicated): Screams={np.sum(y_view_b == 1)} (Expected: 100), Negatives={np.sum(y_view_b == 0)} (Expected: 193)")

    t_sem = torch.tensor(data['X_sem'][hist_idx], dtype=torch.float32)
    t_acoust = torch.tensor(data['X_acoust'][hist_idx], dtype=torch.float32)
    t_mask = torch.tensor(data['mask_acoust'][hist_idx], dtype=torch.float32)
    t_sb = torch.tensor(data['X_subband'][hist_idx], dtype=torch.float32)

    # 2. Evaluate Candidate B
    ckpt_b_path = CKPT_DIR_B / "best_model.pt"
    ckpt_b = torch.load(ckpt_b_path, map_location='cpu')
    model_b = DualEncoderAcousticModel(sem_dim=1024, acoustic_dim=6, proj_sem=128, proj_acoust=32)
    model_b.load_state_dict(ckpt_b['model_state_dict'])
    model_b.eval()

    with torch.no_grad():
        b_logits, _, _ = model_b(t_sem, t_acoust, t_mask)
        b_probs = torch.sigmoid(b_logits).numpy()

    # Save Candidate B Predictions
    b_pred_rows = []
    for i in range(len(hist_idx)):
        b_pred_rows.append({
            'file_id': file_ids[i],
            'category': categories[i],
            'source_group_id': source_groups[i],
            'duration_seconds': durations[i],
            'ground_truth_view_a': int(y_view_a[i]),
            'ground_truth_view_b': int(y_view_b[i]),
            'logit': float(b_logits[i]),
            'probability': float(b_probs[i])
        })
    with open(PRED_DIR / "config_b_historical_predictions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(b_pred_rows[0].keys()))
        w.writeheader()
        w.writerows(b_pred_rows)

    # 3. Evaluate Candidate D
    ckpt_d_path = CKPT_DIR_D / "best_model.pt"
    ckpt_d = torch.load(ckpt_d_path, map_location='cpu')
    model_d = MultiPathwayFusionModel(sem_dim=1024, acoust_dim=6, subband_dim=11)
    model_d.load_state_dict(ckpt_d['model_state_dict'])
    model_d.eval()

    with torch.no_grad():
        d_logits, _, _ = model_d(t_sem, t_acoust, t_mask, t_sb)
        d_probs = torch.sigmoid(d_logits).numpy()

    # Save Candidate D Predictions
    d_pred_rows = []
    for i in range(len(hist_idx)):
        d_pred_rows.append({
            'file_id': file_ids[i],
            'category': categories[i],
            'source_group_id': source_groups[i],
            'duration_seconds': durations[i],
            'ground_truth_view_a': int(y_view_a[i]),
            'ground_truth_view_b': int(y_view_b[i]),
            'logit': float(d_logits[i]),
            'probability': float(d_probs[i])
        })
    with open(PRED_DIR / "config_d_historical_predictions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(d_pred_rows[0].keys()))
        w.writeheader()
        w.writerows(d_pred_rows)

    # Thresholds to evaluate:
    # 1. Validation Operating Point A (Max F1)
    # 2. Validation Operating Point D (Balanced)
    # 3. Standard 0.35 (Production reference)
    # 4. Historical Stage 8.9.34 / 8.9.35 thresholds (0.44 for B, 0.43 for D)
    th_b_opt = thresh_cfg['candidate_b']['primary_evaluation_threshold']
    th_b_bal = thresh_cfg['candidate_b']['balanced_evaluation_threshold']
    th_d_opt = thresh_cfg['candidate_d']['primary_evaluation_threshold']
    th_d_bal = thresh_cfg['candidate_d']['balanced_evaluation_threshold']

    print(f"\n--- CANDIDATE B HISTORICAL BENCHMARK RESULTS ---")
    results_b = {
        'optimal_threshold': {
            'view_a': compute_metrics(y_view_a, b_probs, th_b_opt, categories, durations),
            'view_b': compute_metrics(y_view_b, b_probs, th_b_opt, categories, durations)
        },
        'balanced_threshold': {
            'view_a': compute_metrics(y_view_a, b_probs, th_b_bal, categories, durations),
            'view_b': compute_metrics(y_view_b, b_probs, th_b_bal, categories, durations)
        },
        'ref_threshold_0_35': {
            'view_a': compute_metrics(y_view_a, b_probs, 0.35, categories, durations),
            'view_b': compute_metrics(y_view_b, b_probs, 0.35, categories, durations)
        },
        'hist_threshold_0_44': {
            'view_a': compute_metrics(y_view_a, b_probs, 0.44, categories, durations),
            'view_b': compute_metrics(y_view_b, b_probs, 0.44, categories, durations)
        }
    }
    va_b = results_b['optimal_threshold']['view_a']
    vb_b = results_b['optimal_threshold']['view_b']
    print(f"Optimal Threshold (theta={th_b_opt}):")
    print(f"  View A: Recall={va_b['scream_recall']['fraction']} ({va_b['scream_recall']['value']*100:.2f}%) | HN-FPR={va_b['hard_negative_fpr']['fraction']} ({va_b['hard_negative_fpr']['value']*100:.2f}%) | Shout-FPR={va_b['shouted_speech_fpr']['fraction']} ({va_b['shouted_speech_fpr']['value']*100:.2f}%) | F1={va_b['f1_score']:.4f}")
    print(f"  View B: Recall={vb_b['scream_recall']['fraction']} ({vb_b['scream_recall']['value']*100:.2f}%) | HN-FPR={vb_b['hard_negative_fpr']['fraction']} ({vb_b['hard_negative_fpr']['value']*100:.2f}%) | Shout-FPR={vb_b['shouted_speech_fpr']['fraction']} ({vb_b['shouted_speech_fpr']['value']*100:.2f}%) | F1={vb_b['f1_score']:.4f}")

    print(f"\n--- CANDIDATE D HISTORICAL BENCHMARK RESULTS ---")
    results_d = {
        'optimal_threshold': {
            'view_a': compute_metrics(y_view_a, d_probs, th_d_opt, categories, durations),
            'view_b': compute_metrics(y_view_b, d_probs, th_d_opt, categories, durations)
        },
        'balanced_threshold': {
            'view_a': compute_metrics(y_view_a, d_probs, th_d_bal, categories, durations),
            'view_b': compute_metrics(y_view_b, d_probs, th_d_bal, categories, durations)
        },
        'ref_threshold_0_35': {
            'view_a': compute_metrics(y_view_a, d_probs, 0.35, categories, durations),
            'view_b': compute_metrics(y_view_b, d_probs, 0.35, categories, durations)
        },
        'hist_threshold_0_43': {
            'view_a': compute_metrics(y_view_a, d_probs, 0.43, categories, durations),
            'view_b': compute_metrics(y_view_b, d_probs, 0.43, categories, durations)
        }
    }
    va_d = results_d['optimal_threshold']['view_a']
    vb_d = results_d['optimal_threshold']['view_b']
    print(f"Optimal Threshold (theta={th_d_opt}):")
    print(f"  View A: Recall={va_d['scream_recall']['fraction']} ({va_d['scream_recall']['value']*100:.2f}%) | HN-FPR={va_d['hard_negative_fpr']['fraction']} ({va_d['hard_negative_fpr']['value']*100:.2f}%) | Shout-FPR={va_d['shouted_speech_fpr']['fraction']} ({va_d['shouted_speech_fpr']['value']*100:.2f}%) | F1={va_d['f1_score']:.4f}")
    print(f"  View B: Recall={vb_d['scream_recall']['fraction']} ({vb_d['scream_recall']['value']*100:.2f}%) | HN-FPR={vb_d['hard_negative_fpr']['fraction']} ({vb_d['hard_negative_fpr']['value']*100:.2f}%) | Shout-FPR={vb_d['shouted_speech_fpr']['fraction']} ({vb_d['shouted_speech_fpr']['value']*100:.2f}%) | F1={vb_d['f1_score']:.4f}")

    benchmark_summary = {
        'cohort': 'v4_historical_test',
        'n_total': len(hist_idx),
        'candidate_b': results_b,
        'candidate_d': results_d
    }

    out_json = RESULTS_DIR / "historical_benchmark_results.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(benchmark_summary, f, indent=2)
    print(f"\nHistorical benchmark results saved to: {out_json}")

if __name__ == "__main__":
    main()
