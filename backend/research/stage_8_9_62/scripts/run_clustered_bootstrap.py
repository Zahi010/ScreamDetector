#!/usr/bin/env python3
"""
STAGE 8.9.62 — Phase A5 & A6: Clustered Bootstrap Reproduction & Multiple Comparisons Correction
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import csv
import json
from pathlib import Path
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE61_DIR = BACKEND_DIR / "research" / "stage_8_9_61"
STAGE62_DIR = BACKEND_DIR / "research" / "stage_8_9_62"

def benjamini_hochberg(p_values, q=0.05):
    """
    Applies the Benjamini-Hochberg FDR correction.
    Returns: adjusted_p_values, rejected_hypotheses (boolean array)
    """
    m = len(p_values)
    sorted_indices = np.argsort(p_values)
    sorted_p = np.array(p_values)[sorted_indices]
    
    adj_p = np.zeros(m)
    min_adj_p = 1.0
    for i in range(m - 1, -1, -1):
        rank = i + 1
        p_adj = sorted_p[i] * m / rank
        min_adj_p = min(min_adj_p, p_adj)
        adj_p[i] = min(min_adj_p, 1.0)
        
    # Unsort
    orig_adj_p = np.zeros(m)
    orig_adj_p[sorted_indices] = adj_p
    rejected = orig_adj_p <= q
    return orig_adj_p.tolist(), rejected.tolist()

def main():
    preds_file = STAGE61_DIR / "sealed_cohort_predictions.csv"
    with open(preds_file, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Group recordings by source_group_id
    sg_to_recs = {}
    cand_maps = {}
    for r in rows:
        cid = r["candidate_id"]
        rid = r["recording_id"]
        sg = r["source_group_id"]
        if sg not in sg_to_recs:
            sg_to_recs[sg] = []
        if rid not in sg_to_recs[sg]:
            sg_to_recs[sg].append(rid)
        if cid not in cand_maps:
            cand_maps[cid] = {}
        cand_maps[cid][rid] = r

    unique_sgs = sorted(list(sg_to_recs.keys()))
    n_sgs = len(unique_sgs)
    assert n_sgs == 453, f"Expected 453 SGs, got {n_sgs}"

    # Pre-map labels and predictions as integer arrays for speed
    # rec_idx mapping
    all_rids = sorted(list(cand_maps["Candidate_E1_Static_C5"].keys()))
    rid_to_idx = {rid: i for i, rid in enumerate(all_rids)}
    y_true = np.array([int(cand_maps["Candidate_E1_Static_C5"][rid]["binary_label"]) for rid in all_rids])

    preds = {}
    for cid in cand_maps:
        preds[cid] = np.array([int(cand_maps[cid][rid]["predicted_label"]) for rid in all_rids])

    sg_indices = [np.array([rid_to_idx[rid] for rid in sg_to_recs[sg]]) for sg in unique_sgs]

    # Clustered Bootstrap: 2,000 iterations
    N_BOOTSTRAP = 2000
    rng = np.random.default_rng(seed=42)

    comparisons = [
        ("Candidate_E1_Static_C5", "Candidate_B_Baseline"),
        ("Candidate_E1_Rolling_C5_EMA", "Candidate_B_Baseline"),
        ("Candidate_E1_Static_C5", "Candidate_B_Intervention_D"),
        ("Candidate_E1_Rolling_C5_EMA", "Candidate_E1_Static_C5")
    ]

    boot_diffs = {pair: {"recall": [], "fpr": [], "precision": [], "f1": [], "accuracy": []} for pair in comparisons}

    print(f"Running {N_BOOTSTRAP} source-group clustered bootstrap iterations across {n_sgs} clusters...")
    for b in range(N_BOOTSTRAP):
        sampled_sg_idx = rng.choice(n_sgs, size=n_sgs, replace=True)
        # Gather all recording indices
        boot_rec_idx = np.concatenate([sg_indices[i] for i in sampled_sg_idx])

        y_boot = y_true[boot_rec_idx]
        pos_mask = (y_boot == 1)
        neg_mask = (y_boot == 0)
        n_pos = np.sum(pos_mask)
        n_neg = np.sum(neg_mask)
        n_all = len(y_boot)

        cand_metrics = {}
        for cid in preds:
            p_boot = preds[cid][boot_rec_idx]
            tp = np.sum((p_boot == 1) & pos_mask)
            fp = np.sum((p_boot == 1) & neg_mask)
            fn = np.sum((p_boot == 0) & pos_mask)
            tn = np.sum((p_boot == 0) & neg_mask)

            rec = tp / n_pos if n_pos > 0 else 0.0
            fpr = fp / n_neg if n_neg > 0 else 0.0
            prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
            acc = (tp + tn) / n_all

            cand_metrics[cid] = {"recall": rec, "fpr": fpr, "precision": prec, "f1": f1, "accuracy": acc}

        for c1, c2 in comparisons:
            for m in ["recall", "fpr", "precision", "f1", "accuracy"]:
                diff = cand_metrics[c1][m] - cand_metrics[c2][m]
                boot_diffs[(c1, c2)][m].append(diff)

    bootstrap_summary = []
    print("\n" + "="*80)
    print("PHASE A5: SOURCE-GROUP CLUSTERED BOOTSTRAP RESULTS (2,000 RESAMPLES)")
    print("="*80)

    for c1, c2 in comparisons:
        row = {"candidate_1": c1, "candidate_2": c2, "bootstrap_iterations": N_BOOTSTRAP, "cluster_count": n_sgs}
        for m in ["recall", "fpr", "precision", "f1", "accuracy"]:
            arr = np.array(boot_diffs[(c1, c2)][m]) * 100.0  # in percentage
            mean_val = np.mean(arr)
            ci_low = np.percentile(arr, 2.5)
            ci_high = np.percentile(arr, 97.5)
            row[f"{m}_delta_mean_pct"] = round(mean_val, 2)
            row[f"{m}_delta_ci_low_pct"] = round(ci_low, 2)
            row[f"{m}_delta_ci_high_pct"] = round(ci_high, 2)

        bootstrap_summary.append(row)
        print(f"[{c1}] vs [{c2}]:")
        print(f"  Recall Delta:    {row['recall_delta_mean_pct']:+.2f}% [95% CI: {row['recall_delta_ci_low_pct']:+.2f}%, {row['recall_delta_ci_high_pct']:+.2f}%]")
        print(f"  FPR Delta:       {row['fpr_delta_mean_pct']:+.2f}% [95% CI: {row['fpr_delta_ci_low_pct']:+.2f}%, {row['fpr_delta_ci_high_pct']:+.2f}%]")
        print(f"  Accuracy Delta:  {row['accuracy_delta_mean_pct']:+.2f}% [95% CI: {row['accuracy_delta_ci_low_pct']:+.2f}%, {row['accuracy_delta_ci_high_pct']:+.2f}%]")
        print(f"  F1 Delta:        {row['f1_delta_mean_pct']:+.2f}% [95% CI: {row['f1_delta_ci_low_pct']:+.2f}%, {row['f1_delta_ci_high_pct']:+.2f}%]")

    out_boot_csv = STAGE62_DIR / "clustered_bootstrap_reproduction.csv"
    with open(out_boot_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(bootstrap_summary[0].keys()))
        w.writeheader()
        w.writerows(bootstrap_summary)
    print(f"Wrote {out_boot_csv}")

    # -------------------------------------------------------------------------
    # Phase A6: Multiple Testing Correction (Benjamini-Hochberg)
    # -------------------------------------------------------------------------
    # Collect all hypothesis tests from paired recall, FPR, and accuracy
    # Load from previous CSVs
    with open(STAGE62_DIR / "paired_recall_comparisons.csv") as f:
        rec_rows = list(csv.DictReader(f))
    with open(STAGE62_DIR / "paired_fpr_comparisons.csv") as f:
        fpr_rows = list(csv.DictReader(f))
    with open(STAGE62_DIR / "overall_accuracy_comparisons.csv") as f:
        acc_rows = list(csv.DictReader(f))

    all_hypotheses = []
    for r in rec_rows:
        all_hypotheses.append({
            "test_domain": "Paired Recall (Positives Only)",
            "comparison": f"{r['candidate_1']} vs {r['candidate_2']}",
            "sample_size": int(r["sample_size_positives"]),
            "metric_delta_pct": float(r["recall_diff_pct"]),
            "raw_mcnemar_exact_p": float(r["mcnemar_exact_binomial_p"]),
            "test_type": "Exact McNemar Binomial Test"
        })
    for r in fpr_rows:
        all_hypotheses.append({
            "test_domain": "Paired FPR (Negatives Only)",
            "comparison": f"{r['candidate_1']} vs {r['candidate_2']}",
            "sample_size": int(r["sample_size_negatives"]),
            "metric_delta_pct": float(r["fpr_diff_pct"]),
            "raw_mcnemar_exact_p": float(r["mcnemar_exact_binomial_p"]),
            "test_type": "Exact McNemar Binomial Test"
        })
    for r in acc_rows:
        all_hypotheses.append({
            "test_domain": "Overall Accuracy (All Recordings)",
            "comparison": f"{r['candidate_1']} vs {r['candidate_2']}",
            "sample_size": int(r["sample_size_all"]),
            "metric_delta_pct": float(r["accuracy_diff_pct"]),
            "raw_mcnemar_exact_p": float(r["mcnemar_exact_binomial_p"]),
            "test_type": "Exact McNemar Binomial Test"
        })

    p_vals = [h["raw_mcnemar_exact_p"] for h in all_hypotheses]
    adj_p, rejections = benjamini_hochberg(p_vals, q=0.05)

    for i, h in enumerate(all_hypotheses):
        h["fdr_adjusted_p_bh"] = round(adj_p[i], 6)
        h["significant_fdr_05"] = rejections[i]

    print("\n" + "="*80)
    print("PHASE A6: BENJAMINI-HOCHBERG MULTIPLE COMPARISON CORRECTION (q=0.05)")
    print("="*80)
    for h in all_hypotheses:
        print(f"[{h['test_domain']}] {h['comparison']}")
        print(f"  Delta={h['metric_delta_pct']:+.2f}%, Raw p={h['raw_mcnemar_exact_p']:.6f}, Adj p={h['fdr_adjusted_p_bh']:.6f} -> Significant: {h['significant_fdr_05']}")

    out_mtc_csv = STAGE62_DIR / "multiple_testing_correction.csv"
    with open(out_mtc_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(all_hypotheses[0].keys()))
        w.writeheader()
        w.writerows(all_hypotheses)
    print(f"Wrote {out_mtc_csv}")

if __name__ == "__main__":
    main()

