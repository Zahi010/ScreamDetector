import os
import sys
import json
import csv
from pathlib import Path
import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score, average_precision_score, precision_score, recall_score, confusion_matrix

BACKEND_DIR = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector\backend")
STAGE_DIR = BACKEND_DIR / "research" / "stage_8_9_39"
PRED_DIR = STAGE_DIR / "predictions" / "validation"
CALIB_DIR = STAGE_DIR / "results" / "calibration"
CALIB_DIR.mkdir(parents=True, exist_ok=True)
CKPT_DIR_B = STAGE_DIR / "checkpoints" / "config_b"
CKPT_DIR_D = STAGE_DIR / "checkpoints" / "config_d"

def compute_ece(y_true, y_prob, n_bins=10):
    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    bin_details = []
    
    for i in range(n_bins):
        b_low = bin_edges[i]
        b_high = bin_edges[i + 1]
        mask = (y_prob >= b_low) & (y_prob < b_high) if i < n_bins - 1 else (y_prob >= b_low) & (y_prob <= b_high)
        count = int(np.sum(mask))
        if count > 0:
            bin_acc = float(np.mean(y_true[mask]))
            bin_conf = float(np.mean(y_prob[mask]))
            err = abs(bin_acc - bin_conf)
            ece += (count / len(y_true)) * err
            bin_details.append({
                'bin_index': i + 1,
                'bin_range': f"[{b_low:.2f}, {b_high:.2f}]",
                'count': count,
                'accuracy': round(bin_acc, 4),
                'confidence': round(bin_conf, 4),
                'calibration_error': round(err, 4)
            })
        else:
            bin_details.append({
                'bin_index': i + 1,
                'bin_range': f"[{b_low:.2f}, {b_high:.2f}]",
                'count': 0,
                'accuracy': 0.0,
                'confidence': round((b_low + b_high) / 2.0, 4),
                'calibration_error': 0.0
            })
    return float(ece), bin_details

def audit_model_calibration(val_csv_path, model_name, save_dir):
    with open(val_csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    y_true = np.array([int(r['ground_truth']) for r in rows])
    logits = np.array([float(r['logit']) for r in rows]).reshape(-1, 1)
    uncal_probs = np.array([float(r['probability']) for r in rows])

    # 1. Evaluate Uncalibrated Probabilities
    uncal_brier = float(brier_score_loss(y_true, uncal_probs))
    uncal_ece, uncal_bins = compute_ece(y_true, uncal_probs)
    uncal_roc = float(roc_auc_score(y_true, uncal_probs))
    uncal_pr = float(average_precision_score(y_true, uncal_probs))

    # At default threshold 0.35
    uncal_pred = (uncal_probs >= 0.35).astype(int)
    uncal_rec = float(recall_score(y_true, uncal_pred, zero_division=0))
    uncal_prec = float(precision_score(y_true, uncal_pred, zero_division=0))
    tn, fp, fn, tp = confusion_matrix(y_true, uncal_pred, labels=[0, 1]).ravel()
    uncal_fpr = float(fp / (fp + tn + 1e-9))

    # 2. Fit Platt Scaling (Logistic Regression on Logits strictly on validation)
    # Platt scaling fits a logistic transform: P(y=1|f) = 1 / (1 + exp(A*f + B))
    platt_model = LogisticRegression(C=1.0, solver='lbfgs', max_iter=1000)
    platt_model.fit(logits, y_true)
    
    # Predict calibrated probabilities
    cal_probs = platt_model.predict_proba(logits)[:, 1]

    cal_brier = float(brier_score_loss(y_true, cal_probs))
    cal_ece, cal_bins = compute_ece(y_true, cal_probs)
    cal_roc = float(roc_auc_score(y_true, cal_probs))
    cal_pr = float(average_precision_score(y_true, cal_probs))

    # Calibrated at standard threshold 0.35
    cal_pred = (cal_probs >= 0.35).astype(int)
    cal_rec = float(recall_score(y_true, cal_pred, zero_division=0))
    cal_prec = float(precision_score(y_true, cal_pred, zero_division=0))
    c_tn, c_fp, c_fn, c_tp = confusion_matrix(y_true, cal_pred, labels=[0, 1]).ravel()
    cal_fpr = float(c_fp / (c_fp + c_tn + 1e-9))

    # Save Platt model
    platt_path = save_dir / "platt_calibrator.joblib"
    joblib.dump(platt_model, platt_path)
    print(f"[{model_name}] Saved Platt calibrator to: {platt_path}")

    brier_improved = (cal_brier < uncal_brier)
    ece_improved = (cal_ece < uncal_ece)

    report = {
        'model_name': model_name,
        'platt_parameters': {
            'coef_A': float(platt_model.coef_[0][0]),
            'intercept_B': float(platt_model.intercept_[0])
        },
        'uncalibrated': {
            'brier_score': round(uncal_brier, 4),
            'ece': round(uncal_ece, 4),
            'roc_auc': round(uncal_roc, 4),
            'pr_auc': round(uncal_pr, 4),
            'recall_at_0_35': round(uncal_rec, 4),
            'precision_at_0_35': round(uncal_prec, 4),
            'fpr_at_0_35': round(uncal_fpr, 4)
        },
        'platt_calibrated': {
            'brier_score': round(cal_brier, 4),
            'ece': round(cal_ece, 4),
            'roc_auc': round(cal_roc, 4),
            'pr_auc': round(cal_pr, 4),
            'recall_at_0_35': round(cal_rec, 4),
            'precision_at_0_35': round(cal_prec, 4),
            'fpr_at_0_35': round(cal_fpr, 4)
        },
        'deltas': {
            'brier_delta': round(cal_brier - uncal_brier, 4),
            'ece_delta': round(cal_ece - uncal_ece, 4),
            'brier_improved': brier_improved,
            'ece_improved': ece_improved
        },
        'uncalibrated_bins': uncal_bins,
        'calibrated_bins': cal_bins
    }

    print(f"[{model_name}] Calibration Results:")
    print(f"  Brier Score: Uncal={uncal_brier:.4f} -> Cal={cal_brier:.4f} (Improved: {brier_improved})")
    print(f"  ECE:         Uncal={uncal_ece:.4f} -> Cal={cal_ece:.4f} (Improved: {ece_improved})")
    print(f"  ROC-AUC:     Uncal={uncal_roc:.4f} -> Cal={cal_roc:.4f}")
    print(f"  PR-AUC:      Uncal={uncal_pr:.4f} -> Cal={cal_pr:.4f}")

    return report

def main():
    print("=" * 80)
    print("STAGE 8.9.39: PROBABILITY CALIBRATION AUDIT (PLATT SCALING)")
    print("=" * 80)

    val_b = PRED_DIR / "config_b_val_predictions.csv"
    val_d = PRED_DIR / "config_d_val_predictions.csv"

    report_b = audit_model_calibration(val_b, "Candidate B (DualEncoderAcousticModel)", CKPT_DIR_B)
    report_d = audit_model_calibration(val_d, "Candidate D (MultiPathwayFusionModel)", CKPT_DIR_D)

    full_calibration_summary = {
        'protocol': {
            'method': 'Platt Scaling (Logistic Regression on validation logits)',
            'fitting_cohort': 'v4_val (N=339) ONLY',
            'test_cohort_exposure': False,
            'purpose': 'Assess empirical reliability and probability calibration'
        },
        'candidate_b': report_b,
        'candidate_d': report_d
    }

    out_json = CALIB_DIR / "calibration_metrics.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(full_calibration_summary, f, indent=2)
    print(f"\nCalibration report saved to: {out_json}")

    # Save Reliability diagrams table
    bins_csv = CALIB_DIR / "reliability_diagram_bins.csv"
    bin_rows = []
    for b in report_b['uncalibrated_bins']:
        bin_rows.append({
            'model': 'Candidate_B',
            'calibration_type': 'uncalibrated',
            'bin_index': b['bin_index'],
            'bin_range': b['bin_range'],
            'count': b['count'],
            'accuracy': b['accuracy'],
            'confidence': b['confidence'],
            'error': b['calibration_error']
        })
    for b in report_b['calibrated_bins']:
        bin_rows.append({
            'model': 'Candidate_B',
            'calibration_type': 'platt_calibrated',
            'bin_index': b['bin_index'],
            'bin_range': b['bin_range'],
            'count': b['count'],
            'accuracy': b['accuracy'],
            'confidence': b['confidence'],
            'error': b['calibration_error']
        })
    for b in report_d['uncalibrated_bins']:
        bin_rows.append({
            'model': 'Candidate_D',
            'calibration_type': 'uncalibrated',
            'bin_index': b['bin_index'],
            'bin_range': b['bin_range'],
            'count': b['count'],
            'accuracy': b['accuracy'],
            'confidence': b['confidence'],
            'error': b['calibration_error']
        })
    for b in report_d['calibrated_bins']:
        bin_rows.append({
            'model': 'Candidate_D',
            'calibration_type': 'platt_calibrated',
            'bin_index': b['bin_index'],
            'bin_range': b['bin_range'],
            'count': b['count'],
            'accuracy': b['accuracy'],
            'confidence': b['confidence'],
            'error': b['calibration_error']
        })
    with open(bins_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=['model', 'calibration_type', 'bin_index', 'bin_range', 'count', 'accuracy', 'confidence', 'error'])
        w.writeheader()
        w.writerows(bin_rows)
    print(f"Reliability diagrams bin table saved to: {bins_csv}")

if __name__ == "__main__":
    main()
