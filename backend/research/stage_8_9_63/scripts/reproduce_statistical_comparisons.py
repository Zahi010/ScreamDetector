#!/usr/bin/env python3
"""
STAGE 8.9.63 — Phase A4: Statistical Forensic Reconciliation
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import csv
import math
from pathlib import Path
import numpy as np
from scipy import stats

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE61_DIR = BACKEND_DIR / "research" / "stage_8_9_61"
STAGE63_DIR = BACKEND_DIR / "research" / "stage_8_9_63"

def paired_proportion_ci(b: int, c: int, n: int, confidence: float = 0.95):
    if n == 0:
        return 0.0, 0.0, 0.0
    p_diff = (b - c) / n
    var = ((b + c) - ((b - c) ** 2) / n) / (n ** 2)
    se = math.sqrt(max(0.0, var))
    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    ci_low = max(-1.0, p_diff - z * se)
    ci_high = min(1.0, p_diff + z * se)
    return p_diff, ci_low, ci_high

def mcnemar_exact(b: int, c: int):
    total = b + c
    if total == 0:
        return 1.0
    return float(stats.binomtest(min(b, c), total, 0.5, alternative="two-sided").pvalue)

def benjamini_hochberg(p_values: list):
    m = len(p_values)
    sorted_indices = np.argsort(p_values)
    sorted_p = np.array(p_values)[sorted_indices]
    adj_p = np.zeros(m)
    current_min = 1.0
    for i in range(m - 1, -1, -1):
        rank = i + 1
        adj = (sorted_p[i] * m) / rank
        current_min = min(current_min, adj)
        adj_p[i] = min(1.0, current_min)
    final_adj_p = np.zeros(m)
    final_adj_p[sorted_indices] = adj_p
    return final_adj_p.tolist()

def main():
    preds_file = STAGE61_DIR / "sealed_cohort_predictions.csv"
    with open(preds_file, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

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

    # 1. Recall comparisons (Positives only, N=200)
    recall_pairs = [
        ("Candidate_E1_Static_C5", "Candidate_B_Baseline"),
        ("Candidate_E1_Static_C5", "Candidate_B_Intervention_D"),
        ("Candidate_E1_Rolling_C5_EMA", "Candidate_E1_Static_C5"),
        ("Candidate_E1_Rolling_C5_EMA", "Candidate_B_Baseline"),
    ]
    recall_results = []
    p_vals = []

    for c1, c2 in recall_pairs:
        both_detect = 0
        b = 0
        c = 0
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
        p = mcnemar_exact(b, c)
        p_vals.append(p)
        recall_results.append({
            "pair": f"{c1} vs {c2}",
            "metric": "Recall (Positives N=200)",
            "both_detect": both_detect,
            "b": b,
            "c": c,
            "both_miss": both_miss,
            "rec1": rec1,
            "rec2": rec2,
            "diff_pct": diff * 100,
            "ci_low_pct": ci_low * 100,
            "ci_high_pct": ci_high * 100,
            "p_exact": p
        })

    # 2. FPR comparisons (Negatives only, N=500)
    fpr_pairs = [
        ("Candidate_E1_Static_C5", "Candidate_B_Baseline"),
        ("Candidate_E1_Static_C5", "Candidate_B_Intervention_D"),
        ("Candidate_E1_Rolling_C5_EMA", "Candidate_E1_Static_C5"),
        ("Candidate_E1_Rolling_C5_EMA", "Candidate_B_Baseline"),
    ]
    fpr_results = []
    for c1, c2 in fpr_pairs:
        both_fp = 0
        b = 0
        c = 0
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
        p = mcnemar_exact(b, c)
        p_vals.append(p)
        fpr_results.append({
            "pair": f"{c1} vs {c2}",
            "metric": "FPR (Negatives N=500)",
            "both_fp": both_fp,
            "b": b,
            "c": c,
            "both_tn": both_tn,
            "fpr1": fpr1,
            "fpr2": fpr2,
            "diff_pct": diff * 100,
            "ci_low_pct": ci_low * 100,
            "ci_high_pct": ci_high * 100,
            "p_exact": p
        })

    # 3. Overall Accuracy comparisons (All N=700)
    acc_pairs = [
        ("Candidate_E1_Static_C5", "Candidate_B_Baseline"),
        ("Candidate_E1_Rolling_C5_EMA", "Candidate_B_Baseline"),
        ("Candidate_E1_Static_C5", "Candidate_B_Intervention_D"),
        ("Candidate_E1_Rolling_C5_EMA", "Candidate_E1_Static_C5"),
    ]
    acc_results = []
    for c1, c2 in acc_pairs:
        both_correct = 0
        b = 0
        c = 0
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
        p = mcnemar_exact(b, c)
        p_vals.append(p)
        acc_results.append({
            "pair": f"{c1} vs {c2}",
            "metric": "Accuracy (All N=700)",
            "both_correct": both_correct,
            "b": b,
            "c": c,
            "both_wrong": both_wrong,
            "acc1": acc1,
            "acc2": acc2,
            "diff_pct": diff * 100,
            "ci_low_pct": ci_low * 100,
            "ci_high_pct": ci_high * 100,
            "p_exact": p
        })

    # Benjamini-Hochberg across all 12 planned family comparisons
    adj_p_vals = benjamini_hochberg(p_vals)
    all_tests = recall_results + fpr_results + acc_results
    for i, t in enumerate(all_tests):
        t["p_adj_bh"] = adj_p_vals[i]
        t["significant_05"] = adj_p_vals[i] < 0.05

    print("\n" + "=" * 80)
    print("RECONCILED STATISTICAL HYPOTHESIS TESTS (BENJAMINI-HOCHBERG FDR q=0.05)")
    print("=" * 80)
    for t in all_tests:
        print(f"\n[{t['metric']}] {t['pair']}")
        print(f"  Contingency: b={t['b']}, c={t['c']}, Diff={t['diff_pct']:+.2f}% [95% CI: {t['ci_low_pct']:+.2f}%, {t['ci_high_pct']:+.2f}%]")
        print(f"  Exact p={t['p_exact']:.6f}, BH-FDR adj p={t['p_adj_bh']:.6f} -> Sig: {t['significant_05']}")

    # 4. Source-Group Clustered Bootstrapping (2,000 resamples)
    print("\n" + "=" * 80)
    print("SOURCE-GROUP CLUSTERED BOOTSTRAPPING (B=2,000 resamples across 453 clusters)")
    print("=" * 80)
    sg_map = {}
    for r in rows:
        sg = r["source_group_id"]
        if sg not in sg_map:
            sg_map[sg] = []
        if r["candidate_id"] == "Candidate_E1_Static_C5":
            sg_map[sg].append(r["recording_id"])

    unique_sgs = sorted(list(sg_map.keys()))
    n_clusters = len(unique_sgs)
    assert n_clusters == 453, f"Expected 453 clusters, got {n_clusters}"

    np.random.seed(42)
    B = 2000
    boot_diffs_rec = []
    boot_diffs_fpr = []

    for _ in range(B):
        sample_sgs = np.random.choice(unique_sgs, size=n_clusters, replace=True)
        sample_recs = []
        for sg in sample_sgs:
            sample_recs.extend(sg_map[sg])

        # Recall on pos
        pos_sample = [rid for rid in sample_recs if int(cand_maps["Candidate_E1_Static_C5"][rid]["binary_label"]) == 1]
        if len(pos_sample) > 0:
            rec_e1 = sum(int(cand_maps["Candidate_E1_Static_C5"][rid]["predicted_label"]) for rid in pos_sample) / len(pos_sample)
            rec_b = sum(int(cand_maps["Candidate_B_Baseline"][rid]["predicted_label"]) for rid in pos_sample) / len(pos_sample)
            boot_diffs_rec.append(rec_e1 - rec_b)

        # FPR on neg
        neg_sample = [rid for rid in sample_recs if int(cand_maps["Candidate_E1_Static_C5"][rid]["binary_label"]) == 0]
        if len(neg_sample) > 0:
            fpr_e1 = sum(int(cand_maps["Candidate_E1_Static_C5"][rid]["predicted_label"]) for rid in neg_sample) / len(neg_sample)
            fpr_b = sum(int(cand_maps["Candidate_B_Baseline"][rid]["predicted_label"]) for rid in neg_sample) / len(neg_sample)
            boot_diffs_fpr.append(fpr_e1 - fpr_b)

    rec_ci = np.percentile(boot_diffs_rec, [2.5, 97.5]) * 100
    fpr_ci = np.percentile(boot_diffs_fpr, [2.5, 97.5]) * 100

    print(f"Paired Recall Diff (Static E1 - Cand B):  {np.mean(boot_diffs_rec)*100:+.2f}% [95% Clustered CI: {rec_ci[0]:+.2f}%, {rec_ci[1]:+.2f}%]")
    print(f"Paired FPR Diff (Static E1 - Cand B):     {np.mean(boot_diffs_fpr)*100:+.2f}% [95% Clustered CI: {fpr_ci[0]:+.2f}%, {fpr_ci[1]:+.2f}%]")

if __name__ == "__main__":
    main()

