#!/usr/bin/env python3
"""
STAGE 8.9.62 — Phase A1: Reconstruct Stage 8.9.61 Metrics
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import csv
import math
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE61_DIR = BACKEND_DIR / "research" / "stage_8_9_61"
STAGE62_DIR = BACKEND_DIR / "research" / "stage_8_9_62"

def wilson_score_interval(k: int, n: int, confidence: float = 0.95):
    if n == 0:
        return 0.0, 0.0
    z = 1.959963984540054  # 95%
    p_hat = k / n
    denominator = 1 + z**2 / n
    centre_adjusted_probability = (p_hat + z**2 / (2 * n)) / denominator
    half_width = (z * math.sqrt((p_hat * (1 - p_hat) + z**2 / (4 * n)) / n)) / denominator
    return max(0.0, centre_adjusted_probability - half_width), min(1.0, centre_adjusted_probability + half_width)

def main():
    preds_file = STAGE61_DIR / "sealed_cohort_predictions.csv"
    if not preds_file.exists():
        raise FileNotFoundError(f"Missing {preds_file}")

    rows = []
    with open(preds_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

    print(f"Loaded {len(rows)} prediction rows.")

    candidates = [
        "Candidate_E1_Static_C5",
        "Candidate_B_Baseline",
        "Candidate_B_Intervention_D",
        "Candidate_E1_Rolling_C5_EMA"
    ]

    reproduced_metrics = []

    for cand in candidates:
        cand_rows = [r for r in rows if r["candidate_id"] == cand]
        assert len(cand_rows) == 700, f"Expected 700 rows for {cand}, got {len(cand_rows)}"

        tp = fn = fp = tn = 0
        sust_tp = sust_n = 0
        short_tp = short_n = 0
        shout_fp = shout_n = 0
        whistle_fp = whistle_n = 0

        for r in cand_rows:
            y = int(r["binary_label"])
            y_pred = int(r["predicted_label"])
            dur = float(r["duration_seconds"])
            cat = r["target_category"]

            if y == 1:
                if y_pred == 1:
                    tp += 1
                else:
                    fn += 1

                if dur >= 1.0:
                    sust_n += 1
                    if y_pred == 1:
                        sust_tp += 1
                else:
                    short_n += 1
                    if y_pred == 1:
                        short_tp += 1
            else:
                if y_pred == 1:
                    fp += 1
                else:
                    tn += 1

                if cat == "shouted_speech":
                    shout_n += 1
                    if y_pred == 1:
                        shout_fp += 1
                elif cat == "referee_whistle":
                    whistle_n += 1
                    if y_pred == 1:
                        whistle_fp += 1

        total_pos = tp + fn
        total_neg = fp + tn
        total_all = tp + fn + fp + tn

        recall = tp / total_pos
        rec_ci_low, rec_ci_high = wilson_score_interval(tp, total_pos)

        fpr = fp / total_neg
        fpr_ci_low, fpr_ci_high = wilson_score_interval(fp, total_neg)

        shout_fpr = shout_fp / shout_n if shout_n > 0 else 0.0
        whistle_fpr = whistle_fp / whistle_n if whistle_n > 0 else 0.0
        sust_recall = sust_tp / sust_n if sust_n > 0 else 0.0
        short_recall = short_tp / short_n if short_n > 0 else 0.0

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        accuracy = (tp + tn) / total_all

        reproduced_metrics.append({
            "candidate_id": cand,
            "total_recordings": total_all,
            "tp": tp,
            "fn": fn,
            "fp": fp,
            "tn": tn,
            "overall_recall": round(recall, 4),
            "recall_ci_low": round(rec_ci_low, 4),
            "recall_ci_high": round(rec_ci_high, 4),
            "sustained_scream_recall": round(sust_recall, 4),
            "short_scream_recall": round(short_recall, 4),
            "hard_negative_fpr": round(fpr, 4),
            "fpr_ci_low": round(fpr_ci_low, 4),
            "fpr_ci_high": round(fpr_ci_high, 4),
            "shouted_speech_fpr": round(shout_fpr, 4),
            "referee_whistle_fpr": round(whistle_fpr, 4),
            "precision": round(precision, 4),
            "f1": round(f1, 4),
            "accuracy": round(accuracy, 4)
        })

    out_csv = STAGE62_DIR / "stage_61_metric_reproduction.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(reproduced_metrics[0].keys()))
        writer.writeheader()
        writer.writerows(reproduced_metrics)

    print(f"Wrote {out_csv}")
    for m in reproduced_metrics:
        print(f"\n[{m['candidate_id']}]")
        print(f"  TP={m['tp']}, FN={m['fn']}, FP={m['fp']}, TN={m['tn']}, Acc={m['accuracy']:.4f}")
        print(f"  Recall={m['overall_recall']:.4f} (Sustained={m['sustained_scream_recall']:.4f}, Short={m['short_scream_recall']:.4f})")
        print(f"  FPR={m['hard_negative_fpr']:.4f} (Shout={m['shouted_speech_fpr']:.4f}, Whistle={m['referee_whistle_fpr']:.4f})")
        print(f"  Precision={m['precision']:.4f}, F1={m['f1']:.4f}")

if __name__ == "__main__":
    main()

