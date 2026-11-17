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
PRED_DIR = STAGE_DIR / "predictions" / "expansion_test"
PRED_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR = STAGE_DIR / "results" / "metrics"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

from scripts.train_config_b import DualEncoderAcousticModel
from scripts.train_config_d import MultiPathwayFusionModel

def wilson_score_interval(k, n, confidence=0.95):
    if n == 0:
        return 0.0, 0.0, 0.0
    z = 1.95996
    p_hat = k / n
    denom = 1 + (z**2) / n
    center = (p_hat + (z**2) / (2 * n)) / denom
    margin = (z / denom) * np.sqrt((p_hat * (1 - p_hat) / n) + (z**2) / (4 * n**2))
    ci_low = max(0.0, center - margin)
    ci_high = min(1.0, center + margin)
    return float(p_hat), float(ci_low), float(ci_high)

def evaluate_expansion_cohort(y_true, y_prob, threshold, categories, durations):
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

    # Gate 3: Shouted Speech FPR
    shout_mask = (categories == 'shouting_and_speech')
    n_shout = int(np.sum(shout_mask))
    if n_shout > 0:
        shout_fp = int(np.sum(shout_mask & (y_pred == 1)))
        shout_fpr, shout_low, shout_high = wilson_score_interval(shout_fp, n_shout)
    else:
        shout_fp = 0
        shout_fpr, shout_low, shout_high = 0.0, 0.0, 0.0

    # Gate 4: Short Scream Recall (screams <= 1.0s)
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

    # Gate Status Evaluation
    # Gate 1: Scream Recall >= 96%
    gate_1_pass = (rec >= 0.96)
    # Gate 2: Hard-Negative FPR <= 5%
    gate_2_pass = (hn_fpr <= 0.05)
    # Gate 3: Shouted-Speech FPR <= 15% (require at least 15 examples for statistical validity)
    if n_shout < 15:
        gate_3_status = "INSUFFICIENT EVIDENCE"
        gate_3_pass = False
    else:
        gate_3_pass = (shout_fpr <= 0.15)
        gate_3_status = "PASS" if gate_3_pass else "FAIL"

    # Gate 4: Short-Scream Recall >= 90%
    if n_short_scream < 20:
        gate_4_status = "INSUFFICIENT EVIDENCE"
        gate_4_pass = False
    else:
        gate_4_pass = (ss_rec >= 0.90)
        gate_4_status = "PASS" if gate_4_pass else "FAIL"

    return {
        'threshold': float(threshold),
        'tp': tp, 'fp': fp, 'tn': tn, 'fn': fn,
        'scream_recall': {
            'value': round(rec, 4), 'fraction': f"{tp}/{n_pos}",
            'ci95': [round(rec_low, 4), round(rec_high, 4)],
            'target': '>= 0.96',
            'status': "PASS" if gate_1_pass else "FAIL"
        },
        'hard_negative_fpr': {
            'value': round(hn_fpr, 4), 'fraction': f"{fp}/{n_neg}",
            'ci95': [round(fpr_low, 4), round(fpr_high, 4)],
            'target': '<= 0.05',
            'status': "PASS" if gate_2_pass else "FAIL"
        },
        'shouted_speech_fpr': {
            'value': round(shout_fpr, 4), 'fraction': f"{shout_fp}/{n_shout}",
            'ci95': [round(shout_low, 4), round(shout_high, 4)],
            'target': '<= 0.15',
            'status': gate_3_status
        },
        'short_scream_recall': {
            'value': round(ss_rec, 4), 'fraction': f"{ss_tp}/{n_short_scream}",
            'ci95': [round(ss_low, 4), round(ss_high, 4)],
            'target': '>= 0.90',
            'status': gate_4_status
        },
        'precision': round(prec, 4),
        'f1_score': round(f1, 4),
        'roc_auc': round(roc_auc, 4),
        'pr_auc': round(pr_auc, 4),
        'all_gates_passed': bool(gate_1_pass and gate_2_pass and gate_3_pass and gate_4_pass)
    }

def main():
    print("=" * 80)
    print("STAGE 8.9.39: EVALUATION B — RESERVED EXPANSION GENERALIZATION BENCHMARK (N=102)")
    print("=" * 80)

    with open(THRESH_CONFIG, "r", encoding="utf-8") as f:
        thresh_cfg = json.load(f)

    # 1. Load Data
    data = np.load(CACHE_PATH, allow_pickle=True)
    splits = data['splits']
    exp_idx = np.where(splits == 'v4_reserved_expansion_test')[0]

    split_csv = BACKEND_DIR / "research" / "stage_8_9_38" / "manifests" / "research_split_v4.csv"
    with open(split_csv, "r", encoding="utf-8") as f:
        split_dict = {r["file_id"]: float(r["duration_seconds"]) for r in csv.DictReader(f)}

    file_ids = data['file_ids'][exp_idx]
    categories = data['categories'][exp_idx]
    source_groups = data['source_groups'][exp_idx]
    y_true = data['labels'][exp_idx]
    durations = np.array([split_dict.get(fid, 0.5) for fid in file_ids])

    print(f"Reserved Expansion Test Set N = {len(exp_idx)}")
    print(f"  Positives (Short Screams): {np.sum(y_true == 1)} (Expected: 65)")
    print(f"  Negatives (Hard Negatives): {np.sum(y_true == 0)} (Expected: 37)")
    print(f"  Unique Source Groups: {len(np.unique(source_groups))} (Expected: 49)")

    t_sem = torch.tensor(data['X_sem'][exp_idx], dtype=torch.float32)
    t_acoust = torch.tensor(data['X_acoust'][exp_idx], dtype=torch.float32)
    t_mask = torch.tensor(data['mask_acoust'][exp_idx], dtype=torch.float32)
    t_sb = torch.tensor(data['X_subband'][exp_idx], dtype=torch.float32)

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
    for i in range(len(exp_idx)):
        b_pred_rows.append({
            'file_id': file_ids[i],
            'category': categories[i],
            'source_group_id': source_groups[i],
            'duration_seconds': durations[i],
            'ground_truth': int(y_true[i]),
            'logit': float(b_logits[i]),
            'probability': float(b_probs[i])
        })
    with open(PRED_DIR / "config_b_expansion_predictions.csv", "w", newline="", encoding="utf-8") as f:
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
    for i in range(len(exp_idx)):
        d_pred_rows.append({
            'file_id': file_ids[i],
            'category': categories[i],
            'source_group_id': source_groups[i],
            'duration_seconds': durations[i],
            'ground_truth': int(y_true[i]),
            'logit': float(d_logits[i]),
            'probability': float(d_probs[i])
        })
    with open(PRED_DIR / "config_d_expansion_predictions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(d_pred_rows[0].keys()))
        w.writeheader()
        w.writerows(d_pred_rows)

    # Thresholds:
    th_b_opt = thresh_cfg['candidate_b']['primary_evaluation_threshold']
    th_b_bal = thresh_cfg['candidate_b']['balanced_evaluation_threshold']
    th_d_opt = thresh_cfg['candidate_d']['primary_evaluation_threshold']
    th_d_bal = thresh_cfg['candidate_d']['balanced_evaluation_threshold']

    print(f"\n--- CANDIDATE B EXPANSION GENERALIZATION RESULTS ---")
    results_b = {
        'optimal_threshold': evaluate_expansion_cohort(y_true, b_probs, th_b_opt, categories, durations),
        'balanced_threshold': evaluate_expansion_cohort(y_true, b_probs, th_b_bal, categories, durations),
        'ref_threshold_0_35': evaluate_expansion_cohort(y_true, b_probs, 0.35, categories, durations)
    }
    rb = results_b['optimal_threshold']
    print(f"Optimal Threshold (theta={th_b_opt}):")
    print(f"  Gate 1 - Overall Recall:      {rb['scream_recall']['fraction']} ({rb['scream_recall']['value']*100:.2f}%) 95% CI: {rb['scream_recall']['ci95']} -> {rb['scream_recall']['status']}")
    print(f"  Gate 2 - Hard-Negative FPR:   {rb['hard_negative_fpr']['fraction']} ({rb['hard_negative_fpr']['value']*100:.2f}%) 95% CI: {rb['hard_negative_fpr']['ci95']} -> {rb['hard_negative_fpr']['status']}")
    print(f"  Gate 3 - Shouted-Speech FPR:  {rb['shouted_speech_fpr']['fraction']} ({rb['shouted_speech_fpr']['value']*100:.2f}%) 95% CI: {rb['shouted_speech_fpr']['ci95']} -> {rb['shouted_speech_fpr']['status']}")
    print(f"  Gate 4 - Short-Scream Recall: {rb['short_scream_recall']['fraction']} ({rb['short_scream_recall']['value']*100:.2f}%) 95% CI: {rb['short_scream_recall']['ci95']} -> {rb['short_scream_recall']['status']}")
    print(f"  F1 Score: {rb['f1_score']:.4f} | PR-AUC: {rb['pr_auc']:.4f} | ROC-AUC: {rb['roc_auc']:.4f}")

    print(f"\n--- CANDIDATE D EXPANSION GENERALIZATION RESULTS ---")
    results_d = {
        'optimal_threshold': evaluate_expansion_cohort(y_true, d_probs, th_d_opt, categories, durations),
        'balanced_threshold': evaluate_expansion_cohort(y_true, d_probs, th_d_bal, categories, durations),
        'ref_threshold_0_35': evaluate_expansion_cohort(y_true, d_probs, 0.35, categories, durations)
    }
    rd = results_d['optimal_threshold']
    print(f"Optimal Threshold (theta={th_d_opt}):")
    print(f"  Gate 1 - Overall Recall:      {rd['scream_recall']['fraction']} ({rd['scream_recall']['value']*100:.2f}%) 95% CI: {rd['scream_recall']['ci95']} -> {rd['scream_recall']['status']}")
    print(f"  Gate 2 - Hard-Negative FPR:   {rd['hard_negative_fpr']['fraction']} ({rd['hard_negative_fpr']['value']*100:.2f}%) 95% CI: {rd['hard_negative_fpr']['ci95']} -> {rd['hard_negative_fpr']['status']}")
    print(f"  Gate 3 - Shouted-Speech FPR:  {rd['shouted_speech_fpr']['fraction']} ({rd['shouted_speech_fpr']['value']*100:.2f}%) 95% CI: {rd['shouted_speech_fpr']['ci95']} -> {rd['shouted_speech_fpr']['status']}")
    print(f"  Gate 4 - Short-Scream Recall: {rd['short_scream_recall']['fraction']} ({rd['short_scream_recall']['value']*100:.2f}%) 95% CI: {rd['short_scream_recall']['ci95']} -> {rd['short_scream_recall']['status']}")
    print(f"  F1 Score: {rd['f1_score']:.4f} | PR-AUC: {rd['pr_auc']:.4f} | ROC-AUC: {rd['roc_auc']:.4f}")

    expansion_summary = {
        'cohort': 'v4_reserved_expansion_test',
        'n_total': len(exp_idx),
        'candidate_b': results_b,
        'candidate_d': results_d
    }

    out_json = RESULTS_DIR / "expansion_benchmark_results.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(expansion_summary, f, indent=2)
    print(f"\nExpansion benchmark results saved to: {out_json}")

if __name__ == "__main__":
    main()
