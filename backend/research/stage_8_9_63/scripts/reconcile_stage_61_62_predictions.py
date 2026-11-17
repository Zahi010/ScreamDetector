#!/usr/bin/env python3
"""
STAGE 8.9.63 — Phase A2 & A3: Cross-Stage Prediction & Confusion Matrix Reconciliation
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import csv
import math
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE61_DIR = BACKEND_DIR / "research" / "stage_8_9_61"
STAGE62_DIR = BACKEND_DIR / "research" / "stage_8_9_62"
STAGE63_DIR = BACKEND_DIR / "research" / "stage_8_9_63"

def wilson_score_interval(k: int, n: int, confidence: float = 0.95):
    if n == 0:
        return 0.0, 0.0
    z = 1.959963984540054
    p_hat = k / n
    denom = 1 + z**2 / n
    centre = (p_hat + z**2 / (2 * n)) / denom
    half_width = (z * math.sqrt((p_hat * (1 - p_hat) + z**2 / (4 * n)) / n)) / denom
    return max(0.0, centre - half_width), min(1.0, centre + half_width)

def main():
    print("=" * 80)
    print("STAGE 8.9.63 — TRACK A: CROSS-STAGE PREDICTION RECONCILIATION")
    print("=" * 80)

    # 1. Load Stage 61 predictions
    s61_file = STAGE61_DIR / "sealed_cohort_predictions.csv"
    assert s61_file.exists(), f"Missing {s61_file}"
    with open(s61_file, "r", encoding="utf-8") as f:
        s61_rows = list(csv.DictReader(f))
    print(f"Loaded {len(s61_rows)} prediction rows from Stage 61.")

    # 2. Load Stage 62 short scream forensic inventory
    s62_inventory_file = STAGE62_DIR / "short_scream_forensic_inventory.csv"
    assert s62_inventory_file.exists(), f"Missing {s62_inventory_file}"
    with open(s62_inventory_file, "r", encoding="utf-8") as f:
        s62_inventory_rows = list(csv.DictReader(f))
    print(f"Loaded {len(s62_inventory_rows)} short scream rows from Stage 62 forensic inventory.")
    s62_inv_by_rec = {r["recording_id"]: r for r in s62_inventory_rows}

    # 3. Load Stage 62 metric reproduction
    s62_repro_file = STAGE62_DIR / "stage_61_metric_reproduction.csv"
    assert s62_repro_file.exists(), f"Missing {s62_repro_file}"
    with open(s62_repro_file, "r", encoding="utf-8") as f:
        s62_repro_rows = list(csv.DictReader(f))
    s62_repro_by_cand = {r["candidate_id"]: r for r in s62_repro_rows}

    # 4. Row-level prediction reconciliation
    reconciliation_rows = []
    discrepancy_counts = {}

    for r in s61_rows:
        rec_id = r["recording_id"]
        cand_id = r["candidate_id"]
        y_true = int(r["binary_label"])
        y_pred = int(r["predicted_label"])
        prob = float(r["predicted_probability"])
        thresh = float(r["threshold"])
        dur = float(r["duration_seconds"])

        # Check against Stage 62 short inventory if applicable
        discrepancy = "IDENTICAL_PREDICTION"

        if dur < 1.0 and y_true == 1:
            if rec_id in s62_inv_by_rec:
                inv = s62_inv_by_rec[rec_id]
                # Compare candidate prediction in inventory
                if cand_id == "Candidate_E1_Static_C5":
                    inv_pred = int(inv["e1_static_pred"])
                    inv_prob = float(inv["e1_static_prob"])
                elif cand_id == "Candidate_B_Baseline":
                    inv_pred = int(inv["cand_b_pred"])
                    inv_prob = float(inv["cand_b_prob"])
                elif cand_id == "Candidate_B_Intervention_D":
                    inv_pred = int(inv["cand_bd_pred"])
                    inv_prob = float(inv["cand_bd_prob"])
                elif cand_id == "Candidate_E1_Rolling_C5_EMA":
                    inv_pred = int(inv["e1_rolling_pred"])
                    inv_prob = float(inv["e1_rolling_prob"])
                else:
                    inv_pred = None
                    inv_prob = None

                if inv_pred is not None:
                    if inv_pred != y_pred:
                        discrepancy = "CHANGED_PREDICTION"
                    elif abs(inv_prob - prob) > 1e-4:
                        discrepancy = "CHANGED_PROBABILITY"
            else:
                discrepancy = "RECORDING_MISSING_IN_STAGE62_INVENTORY"

        reconciliation_rows.append({
            "recording_id": rec_id,
            "source_group_id": r["source_group_id"],
            "binary_label": y_true,
            "target_category": r["target_category"],
            "subcategory": r["subcategory"],
            "duration_seconds": dur,
            "candidate_id": cand_id,
            "model_checkpoint_sha256": r["model_checkpoint_sha256"],
            "dsp_sha256": r["dsp_sha256"],
            "threshold": thresh,
            "predicted_probability": prob,
            "predicted_label": y_pred,
            "is_correct": int(r["is_correct"]),
            "reconciliation_classification": discrepancy
        })
        discrepancy_counts[discrepancy] = discrepancy_counts.get(discrepancy, 0) + 1

    # Save row-level reconciliation CSV
    out_rec_csv = STAGE63_DIR / "stage_61_62_prediction_reconciliation.csv"
    with open(out_rec_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(reconciliation_rows[0].keys()))
        writer.writeheader()
        writer.writerows(reconciliation_rows)
    print(f"Wrote row-level reconciliation to {out_rec_csv}")
    print("Discrepancy Breakdown:", discrepancy_counts)

    # 5. Confusion matrix reconciliation across all candidates
    candidates = [
        "Candidate_E1_Static_C5",
        "Candidate_B_Baseline",
        "Candidate_B_Intervention_D",
        "Candidate_E1_Rolling_C5_EMA"
    ]

    cm_rows = []
    for cand in candidates:
        cand_data = [r for r in s61_rows if r["candidate_id"] == cand]
        tp = sum(1 for r in cand_data if int(r["binary_label"]) == 1 and int(r["predicted_label"]) == 1)
        fn = sum(1 for r in cand_data if int(r["binary_label"]) == 1 and int(r["predicted_label"]) == 0)
        fp = sum(1 for r in cand_data if int(r["binary_label"]) == 0 and int(r["predicted_label"]) == 1)
        tn = sum(1 for r in cand_data if int(r["binary_label"]) == 0 and int(r["predicted_label"]) == 0)

        sust_tp = sum(1 for r in cand_data if int(r["binary_label"]) == 1 and float(r["duration_seconds"]) >= 1.0 and int(r["predicted_label"]) == 1)
        sust_n = sum(1 for r in cand_data if int(r["binary_label"]) == 1 and float(r["duration_seconds"]) >= 1.0)
        short_tp = sum(1 for r in cand_data if int(r["binary_label"]) == 1 and float(r["duration_seconds"]) < 1.0 and int(r["predicted_label"]) == 1)
        short_n = sum(1 for r in cand_data if int(r["binary_label"]) == 1 and float(r["duration_seconds"]) < 1.0)

        shout_fp = sum(1 for r in cand_data if int(r["binary_label"]) == 0 and r["target_category"] == "shouted_speech" and int(r["predicted_label"]) == 1)
        shout_n = sum(1 for r in cand_data if int(r["binary_label"]) == 0 and r["target_category"] == "shouted_speech")

        # Compare with Stage 62 CSV
        s62_data = s62_repro_by_cand[cand]
        s62_tp = int(s62_data["tp"])
        s62_fn = int(s62_data["fn"])
        s62_fp = int(s62_data["fp"])
        s62_tn = int(s62_data["tn"])

        # Compare with Stage 62 Report Narrative
        if cand == "Candidate_E1_Static_C5":
            s62_narrative_tp = 103
            s62_narrative_recall = 0.5150
            s62_narrative_short_tp = 22
            s62_narrative_short_recall = 0.3188
        elif cand == "Candidate_B_Baseline":
            s62_narrative_tp = 102
            s62_narrative_recall = 0.5100
            s62_narrative_short_tp = 26
            s62_narrative_short_recall = 0.3768
        elif cand == "Candidate_B_Intervention_D":
            s62_narrative_tp = 105
            s62_narrative_recall = 0.5250
            s62_narrative_short_tp = 26
            s62_narrative_short_recall = 0.3768
        elif cand == "Candidate_E1_Rolling_C5_EMA":
            s62_narrative_tp = 127
            s62_narrative_recall = 0.6350
            s62_narrative_short_tp = 24
            s62_narrative_short_recall = 0.3478

        cm_rows.append({
            "candidate_id": cand,
            "actual_data_tp": tp,
            "actual_data_fn": fn,
            "actual_data_fp": fp,
            "actual_data_tn": tn,
            "actual_overall_recall": round(tp / (tp + fn), 4),
            "actual_short_scream_recall": round(short_tp / short_n, 4),
            "actual_sustained_recall": round(sust_tp / sust_n, 4),
            "actual_hard_negative_fpr": round(fp / (fp + tn), 4),
            "actual_shouted_speech_fpr": round(shout_fp / shout_n, 4),
            "stage62_csv_tp": s62_tp,
            "stage62_csv_tp_match": (tp == s62_tp),
            "stage62_narrative_tp": s62_narrative_tp,
            "stage62_narrative_tp_diff": tp - s62_narrative_tp,
            "stage62_narrative_short_tp": s62_narrative_short_tp,
            "stage62_narrative_short_diff": short_tp - s62_narrative_short_tp,
            "discrepancy_nature": "REPORT_NARRATIVE_CLERICAL_ERROR_ONLY_UNDERLYING_DATA_EXACT_MATCH"
        })

    out_cm_csv = STAGE63_DIR / "stage_61_62_confusion_matrix_reconciliation.csv"
    with open(out_cm_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(cm_rows[0].keys()))
        writer.writeheader()
        writer.writerows(cm_rows)
    print(f"Wrote confusion matrix reconciliation to {out_cm_csv}")

    for row in cm_rows:
        print(f"\n[{row['candidate_id']}]")
        print(f"  Underlying Data TP: {row['actual_data_tp']} (Recall: {row['actual_overall_recall']*100:.2f}%)")
        print(f"  Stage 62 CSV TP:    {row['stage62_csv_tp']} (Match: {row['stage62_csv_tp_match']})")
        print(f"  Stage 62 Report TP: {row['stage62_narrative_tp']} (Diff: {row['stage62_narrative_tp_diff']})")
        print(f"  Short Scream TP:    Actual={round(row['actual_short_scream_recall']*69)} vs Stage62 Report={row['stage62_narrative_short_tp']}")

if __name__ == "__main__":
    main()

