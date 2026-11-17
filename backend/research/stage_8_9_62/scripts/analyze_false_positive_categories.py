#!/usr/bin/env python3
"""
STAGE 8.9.62 — Phase D3: False-Positive Distractor Category Analysis
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
    z = 1.959963984540054
    p_hat = k / n
    denominator = 1 + z**2 / n
    centre_adj = (p_hat + z**2 / (2 * n)) / denominator
    half_width = (z * math.sqrt((p_hat * (1 - p_hat) + z**2 / (4 * n)) / n)) / denominator
    return max(0.0, centre_adj - half_width), min(1.0, centre_adj + half_width)

def main():
    preds_file = STAGE61_DIR / "sealed_cohort_predictions.csv"
    with open(preds_file, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Candidates to audit
    candidates = [
        "Candidate_E1_Static_C5",
        "Candidate_B_Baseline",
        "Candidate_B_Intervention_D",
        "Candidate_E1_Rolling_C5_EMA"
    ]

    # Target categories among hard negatives (binary_label == 0)
    categories = [
        ("shouted_speech", "Shouted Speech & Shouts"),
        ("referee_whistle", "Referee Whistles & Squeaks"),
        ("cheering", "Cheering & Crowd Chanting"),
        ("infant_crying", "Infant Crying"),
        ("environmental_sound", "Environmental Noise & Sirens")
    ]

    category_results = []

    print("\n" + "="*80)
    print("PHASE D3: FALSE-POSITIVE DISTRACTOR CATEGORY AUDIT (N=500 HARD NEGATIVES)")
    print("="*80)

    for cat_key, cat_name in categories:
        for cid in candidates:
            cand_rows = [r for r in rows if r["candidate_id"] == cid and int(r["binary_label"]) == 0 and r["target_category"] == cat_key]
            n_samples = len(cand_rows)
            unique_sgs = len(set(r["source_group_id"] for r in cand_rows))

            fp_count = sum(1 for r in cand_rows if int(r["predicted_label"]) == 1)
            fpr = fp_count / n_samples if n_samples > 0 else 0.0
            ci_low, ci_high = wilson_score_interval(fp_count, n_samples)

            if n_samples >= 30:
                evidence = "ROBUST_EVIDENCE"
            elif n_samples >= 10:
                evidence = "LIMITED_SAMPLE_SIZE"
            else:
                evidence = "INSUFFICIENT_SAMPLE_SIZE"

            category_results.append({
                "target_category": cat_key,
                "category_display_name": cat_name,
                "candidate_id": cid,
                "sample_size_n": n_samples,
                "unique_source_groups": unique_sgs,
                "false_positive_count": fp_count,
                "false_positive_rate": round(fpr, 4),
                "fpr_ci_low": round(ci_low, 4),
                "fpr_ci_high": round(ci_high, 4),
                "evidence_status": evidence
            })

    out_csv = STAGE62_DIR / "false_positive_category_metrics.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(category_results[0].keys()))
        w.writeheader()
        w.writerows(category_results)

    print(f"Wrote {out_csv}")
    for cat_key, cat_name in categories:
        print(f"\n--- {cat_name} ---")
        for res in [r for r in category_results if r["target_category"] == cat_key]:
            print(f"  {res['candidate_id']:<32}: {res['false_positive_count']:2d} / {res['sample_size_n']:3d} ({res['false_positive_rate']*100:5.2f}%) [95% CI: {res['fpr_ci_low']*100:4.1f}%, {res['fpr_ci_high']*100:4.1f}%] - {res['evidence_status']}")

if __name__ == "__main__":
    main()

