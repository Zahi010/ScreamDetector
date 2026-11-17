#!/usr/bin/env python3
"""
STAGE 8.9.62 — Phase A2, A3, A4: Forensic Paired Statistical Auditing
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import csv
import math
from pathlib import Path
from scipy import stats

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE61_DIR = BACKEND_DIR / "research" / "stage_8_9_61"
STAGE62_DIR = BACKEND_DIR / "research" / "stage_8_9_62"

def paired_proportion_ci(b: int, c: int, n: int, confidence: float = 0.95):
    """
    Wald / Newcombe paired proportion difference confidence interval.
    Diff = (b - c) / n
    Variance = ((b + c) - (b - c)^2 / n) / n^2
    """
    if n == 0:
        return 0.0, 0.0, 0.0
    p_diff = (b - c) / n
    var = ((b + c) - ((b - c) ** 2) / n) / (n ** 2)
    se = math.sqrt(max(0.0, var))
    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    ci_low = max(-1.0, p_diff - z * se)
    ci_high = min(1.0, p_diff + z * se)
    return p_diff, ci_low, ci_high

def mcnemar_exact_and_corrected(b: int, c: int):
    """
    Computes exact two-tailed binomial p-value and continuity-corrected chi-square.
    """
    total = b + c
    if total == 0:
        return 0.0, 1.0, 1.0
    # Exact binomial p-value
    # Two-sided p-value from binomial(n=total, p=0.5)
    binom_p = stats.binomtest(min(b, c), total, 0.5, alternative="two-sided").pvalue
    # Continuity-corrected chi-square
    chi2 = ((abs(b - c) - 1.0) ** 2) / total
    chi2_p = stats.chi2.sf(chi2, df=1)
    return chi2, chi2_p, binom_p

def main():
    preds_file = STAGE61_DIR / "sealed_cohort_predictions.csv"
    with open(preds_file, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Map candidate -> {rec_id: row}
    cand_maps = {}
    for r in rows:
        c = r["candidate_id"]
        if c not in cand_maps:
            cand_maps[c] = {}
        cand_maps[c][r["recording_id"]] = r

    pos_recs = [r["recording_id"] for r in rows if r["candidate_id"] == "Candidate_E1_Static_C5" and int(r["binary_label"]) == 1]
    neg_recs = [r["recording_id"] for r in rows if r["candidate_id"] == "Candidate_E1_Static_C5" and int(r["binary_label"]) == 0]
    all_recs = [r["recording_id"] for r in rows if r["candidate_id"] == "Candidate_E1_Static_C5"]

    assert len(pos_recs) == 200
    assert len(neg_recs) == 500
    assert len(all_recs) == 700

    # -------------------------------------------------------------------------
    # Phase A2: Correct Paired Recall Comparisons (Positives Only, N=200)
    # -------------------------------------------------------------------------
    recall_pairs = [
        ("Candidate_E1_Rolling_C5_EMA", "Candidate_E1_Static_C5"),
        ("Candidate_E1_Rolling_C5_EMA", "Candidate_B_Baseline"),
        ("Candidate_E1_Static_C5", "Candidate_B_Baseline"),
        ("Candidate_E1_Rolling_C5_EMA", "Candidate_B_Intervention_D"),
    ]

    recall_results = []
    print("\n" + "="*80)
    print("PHASE A2: CORRECT PAIRED RECALL COMPARISONS (POSITIVES ONLY, N=200)")
    print("="*80)

    for c1, c2 in recall_pairs:
        # Contingency on positives:
        # both_detect: c1=1, c2=1
        # c1_detect_c2_miss: c1=1, c2=0 (b)
        # c1_miss_c2_detect: c1=0, c2=1 (c)
        # both_miss: c1=0, c2=0
        both_detect = 0
        b = 0  # c1 detect, c2 miss
        c = 0  # c1 miss, c2 detect
        both_miss = 0

        for rid in pos_recs:
            p1 = int(cand_maps[c1][rid]["predicted_label"])
            p2 = int(cand_maps[c2][rid]["predicted_label"])
            if p1 == 1 and p2 == 1:
                both_detect += 1
            elif p1 == 1 and p2 == 0:
                b += 1
            elif p1 == 0 and p2 == 1:
                c += 1
            else:
                both_miss += 1

        rec1 = (both_detect + b) / 200.0
        rec2 = (both_detect + c) / 200.0
        diff, ci_low, ci_high = paired_proportion_ci(b, c, 200)
        chi2, chi2_p, binom_p = mcnemar_exact_and_corrected(b, c)

        recall_results.append({
            "candidate_1": c1,
            "candidate_2": c2,
            "sample_size_positives": 200,
            "both_detect": both_detect,
            "cand1_detect_cand2_miss_b": b,
            "cand1_miss_cand2_detect_c": c,
            "both_miss": both_miss,
            "cand1_recall": round(rec1, 4),
            "cand2_recall": round(rec2, 4),
            "recall_diff_pct": round(diff * 100, 2),
            "recall_diff_ci_low_pct": round(ci_low * 100, 2),
            "recall_diff_ci_high_pct": round(ci_high * 100, 2),
            "mcnemar_chi2": round(chi2, 4),
            "mcnemar_continuity_p": round(chi2_p, 6),
            "mcnemar_exact_binomial_p": round(binom_p, 6),
            "statistically_significant_05": binom_p < 0.05
        })

        print(f"[{c1}] vs [{c2}]:")
        print(f"  Contingency: BothDetect={both_detect}, b={b}, c={c}, BothMiss={both_miss}")
        print(f"  Recall: {rec1*100:.2f}% vs {rec2*100:.2f}% -> Diff = {diff*100:+.2f}% [95% CI: {ci_low*100:+.2f}%, {ci_high*100:+.2f}%]")
        print(f"  McNemar: chi2={chi2:.4f} (p={chi2_p:.6f}), Exact Binomial p={binom_p:.6f} -> Sig: {binom_p < 0.05}")

    out_recall_csv = STAGE62_DIR / "paired_recall_comparisons.csv"
    with open(out_recall_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(recall_results[0].keys()))
        w.writeheader()
        w.writerows(recall_results)
    print(f"Wrote {out_recall_csv}")

    # -------------------------------------------------------------------------
    # Phase A3: Correct Paired FPR Comparisons (Negatives Only, N=500)
    # -------------------------------------------------------------------------
    fpr_pairs = [
        ("Candidate_E1_Rolling_C5_EMA", "Candidate_E1_Static_C5"),
        ("Candidate_E1_Rolling_C5_EMA", "Candidate_B_Baseline"),
        ("Candidate_E1_Rolling_C5_EMA", "Candidate_B_Intervention_D"),
        ("Candidate_B_Baseline", "Candidate_B_Intervention_D"),
        ("Candidate_E1_Static_C5", "Candidate_B_Baseline")
    ]

    fpr_results = []
    print("\n" + "="*80)
    print("PHASE A3: CORRECT PAIRED FPR COMPARISONS (NEGATIVES ONLY, N=500)")
    print("="*80)

    for c1, c2 in fpr_pairs:
        # Contingency on negatives:
        # both_fp: c1=1, c2=1
        # c1_fp_c2_tn: c1=1, c2=0 (b)
        # c1_tn_c2_fp: c1=0, c2=1 (c)
        # both_tn: c1=0, c2=0
        both_fp = 0
        b = 0  # c1 FP, c2 TN
        c = 0  # c1 TN, c2 FP
        both_tn = 0

        for rid in neg_recs:
            p1 = int(cand_maps[c1][rid]["predicted_label"])
            p2 = int(cand_maps[c2][rid]["predicted_label"])
            if p1 == 1 and p2 == 1:
                both_fp += 1
            elif p1 == 1 and p2 == 0:
                b += 1
            elif p1 == 0 and p2 == 1:
                c += 1
            else:
                both_tn += 1

        fpr1 = (both_fp + b) / 500.0
        fpr2 = (both_fp + c) / 500.0
        diff, ci_low, ci_high = paired_proportion_ci(b, c, 500)
        chi2, chi2_p, binom_p = mcnemar_exact_and_corrected(b, c)

        fpr_results.append({
            "candidate_1": c1,
            "candidate_2": c2,
            "sample_size_negatives": 500,
            "both_fp": both_fp,
            "cand1_fp_cand2_tn_b": b,
            "cand1_tn_cand2_fp_c": c,
            "both_tn": both_tn,
            "cand1_fpr": round(fpr1, 4),
            "cand2_fpr": round(fpr2, 4),
            "fpr_diff_pct": round(diff * 100, 2),
            "fpr_diff_ci_low_pct": round(ci_low * 100, 2),
            "fpr_diff_ci_high_pct": round(ci_high * 100, 2),
            "mcnemar_chi2": round(chi2, 4),
            "mcnemar_continuity_p": round(chi2_p, 6),
            "mcnemar_exact_binomial_p": round(binom_p, 6),
            "statistically_significant_05": binom_p < 0.05
        })

        print(f"[{c1}] vs [{c2}]:")
        print(f"  Contingency: BothFP={both_fp}, b={b}, c={c}, BothTN={both_tn}")
        print(f"  FPR: {fpr1*100:.2f}% vs {fpr2*100:.2f}% -> Diff = {diff*100:+.2f}% [95% CI: {ci_low*100:+.2f}%, {ci_high*100:+.2f}%]")
        print(f"  McNemar: chi2={chi2:.4f} (p={chi2_p:.6f}), Exact Binomial p={binom_p:.6f} -> Sig: {binom_p < 0.05}")

    out_fpr_csv = STAGE62_DIR / "paired_fpr_comparisons.csv"
    with open(out_fpr_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(fpr_results[0].keys()))
        w.writeheader()
        w.writerows(fpr_results)
    print(f"Wrote {out_fpr_csv}")

    # -------------------------------------------------------------------------
    # Phase A4: Overall Accuracy Comparisons (All Recordings, N=700)
    # -------------------------------------------------------------------------
    acc_pairs = [
        ("Candidate_E1_Static_C5", "Candidate_B_Baseline"),
        ("Candidate_E1_Rolling_C5_EMA", "Candidate_B_Baseline"),
        ("Candidate_E1_Static_C5", "Candidate_B_Intervention_D"),
        ("Candidate_E1_Rolling_C5_EMA", "Candidate_E1_Static_C5"),
    ]

    acc_results = []
    print("\n" + "="*80)
    print("PHASE A4: OVERALL ACCURACY / CORRECTNESS COMPARISONS (ALL N=700)")
    print("="*80)

    for c1, c2 in acc_pairs:
        # Contingency across all 700:
        # both_correct: c1 correct, c2 correct
        # c1_correct_c2_incorrect: c1 correct, c2 wrong (b)
        # c1_incorrect_c2_correct: c1 wrong, c2 correct (c)
        # both_incorrect: c1 wrong, c2 wrong
        both_correct = 0
        b = 0  # c1 correct, c2 wrong
        c = 0  # c1 wrong, c2 correct
        both_wrong = 0

        for rid in all_recs:
            corr1 = (int(cand_maps[c1][rid]["predicted_label"]) == int(cand_maps[c1][rid]["binary_label"]))
            corr2 = (int(cand_maps[c2][rid]["predicted_label"]) == int(cand_maps[c2][rid]["binary_label"]))
            if corr1 and corr2:
                both_correct += 1
            elif corr1 and not corr2:
                b += 1
            elif not corr1 and corr2:
                c += 1
            else:
                both_wrong += 1

        acc1 = (both_correct + b) / 700.0
        acc2 = (both_correct + c) / 700.0
        diff, ci_low, ci_high = paired_proportion_ci(b, c, 700)
        chi2, chi2_p, binom_p = mcnemar_exact_and_corrected(b, c)

        acc_results.append({
            "candidate_1": c1,
            "candidate_2": c2,
            "sample_size_all": 700,
            "both_correct": both_correct,
            "cand1_correct_cand2_wrong_b": b,
            "cand1_wrong_cand2_correct_c": c,
            "both_wrong": both_wrong,
            "cand1_accuracy": round(acc1, 4),
            "cand2_accuracy": round(acc2, 4),
            "accuracy_diff_pct": round(diff * 100, 2),
            "accuracy_diff_ci_low_pct": round(ci_low * 100, 2),
            "accuracy_diff_ci_high_pct": round(ci_high * 100, 2),
            "mcnemar_chi2": round(chi2, 4),
            "mcnemar_continuity_p": round(chi2_p, 6),
            "mcnemar_exact_binomial_p": round(binom_p, 6),
            "statistically_significant_05": binom_p < 0.05
        })

        print(f"[{c1}] vs [{c2}]:")
        print(f"  Contingency: BothCorrect={both_correct}, b={b}, c={c}, BothWrong={both_wrong}")
        print(f"  Accuracy: {acc1*100:.2f}% vs {acc2*100:.2f}% -> Diff = {diff*100:+.2f}% [95% CI: {ci_low*100:+.2f}%, {ci_high*100:+.2f}%]")
        print(f"  McNemar: chi2={chi2:.4f} (p={chi2_p:.6f}), Exact Binomial p={binom_p:.6f} -> Sig: {binom_p < 0.05}")

    out_acc_csv = STAGE62_DIR / "overall_accuracy_comparisons.csv"
    with open(out_acc_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(acc_results[0].keys()))
        w.writeheader()
        w.writerows(acc_results)
    print(f"Wrote {out_acc_csv}")

if __name__ == "__main__":
    main()

