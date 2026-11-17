#!/usr/bin/env python3
"""
STAGE 8.9.64 — Track G: Future Evaluation Statistical Power & Sample-Size Rationale
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import csv
import math
from pathlib import Path
import numpy as np
from scipy import stats

REPO_ROOT = Path(__file__).resolve().parents[4]
STAGE64_DIR = REPO_ROOT / "backend" / "research" / "stage_8_9_64"

def compute_wilson_ci_width(n: int, p: float, z: float = 1.96) -> float:
    denom = 1.0 + (z**2) / n
    center = (p + (z**2) / (2 * n)) / denom
    margin = (z / denom) * math.sqrt((p * (1 - p) / n) + (z**2) / (4 * n**2))
    return 2.0 * margin

def compute_statistical_power(n: int, p_null: float, p_alt: float, alpha: float = 0.05) -> float:
    """Power to reject H0: p <= p_null in favor of H1: p >= p_alt."""
    z_alpha = stats.norm.ppf(1.0 - alpha)
    # Standard errors under null and alt
    se_null = math.sqrt(p_null * (1.0 - p_null) / n)
    se_alt = math.sqrt(p_alt * (1.0 - p_alt) / n)
    # Critical threshold
    crit_val = p_null + z_alpha * se_null
    # Z-score under alt
    z_beta = (crit_val - p_alt) / se_alt
    power = 1.0 - stats.norm.cdf(z_beta)
    return float(power)

def main():
    print("=" * 80)
    print("STAGE 8.9.64 — TRACK G: FUTURE EVALUATION STATISTICAL POWER ANALYSIS")
    print("=" * 80)

    # Future Cohort Specifications
    n_total = 1050
    n_pos = 240
    n_neg = 810
    n_short = 120
    n_sust = 120
    m_cluster_cap = 3.0  # Max recordings per source group
    n_source_groups_target = 600

    print(f"Target Future Evaluation Cohort:")
    print(f"  Total Recordings:              {n_total}")
    print(f"  Total Scream Positives:        {n_pos}")
    print(f"    - Short Screams (< 1.00s):   {n_short}")
    print(f"    - Sustained Screams (>=1.0s):{n_sust}")
    print(f"  Total Hard Negatives:          {n_neg}")
    print(f"  Target Source Groups:          >= {n_source_groups_target}")
    print(f"  Source-Group Cluster Cap:      <= {m_cluster_cap} clips / group\n")

    rho_values = [0.00, 0.05, 0.10, 0.15, 0.20]
    power_records = []

    print(f"{'Gate Target':<30} {'Subgroup':<12} {'N_Nominal':<10} {'ICC (rho)':<10} {'DEFF':<8} {'N_Eff':<8} {'CI Half-Width':<14} {'Power (1-beta)':<15}")
    print("-" * 110)

    # 1. Gate 1: Overall Recall (Null = 96.0%, Alt = 98.0%, alpha = 0.05)
    for rho in rho_values:
        deff = 1.0 + (m_cluster_cap - 1.0) * rho
        n_eff = int(n_pos / deff)
        ci_half = compute_wilson_ci_width(n_eff, 0.960, z=1.96) / 2.0
        pwr = compute_statistical_power(n_eff, p_null=0.960, p_alt=0.985, alpha=0.05)
        
        power_records.append({
            "gate": "Gate 1 (Overall Recall)",
            "subgroup": "all_screams",
            "nominal_n": n_pos,
            "cluster_cap": m_cluster_cap,
            "icc_rho": rho,
            "design_effect": round(deff, 3),
            "effective_n": n_eff,
            "ci_95_half_width": round(ci_half, 4),
            "statistical_power": round(pwr, 4)
        })
        print(f"{'Gate 1 (Recall >= 96%)':<30} {'all_screams':<12} {n_pos:<10} {rho:<10.2f} {deff:<8.3f} {n_eff:<8} {ci_half:<14.4f} {pwr:<15.4f}")

    # 2. Gate 2: False Positive Rate (Null = 5.0%, Alt = 3.0%, alpha = 0.05)
    for rho in rho_values:
        deff = 1.0 + (m_cluster_cap - 1.0) * rho
        n_eff = int(n_neg / deff)
        ci_half = compute_wilson_ci_width(n_eff, 0.050, z=1.96) / 2.0
        pwr = compute_statistical_power(n_eff, p_null=0.050, p_alt=0.030, alpha=0.05)
        
        power_records.append({
            "gate": "Gate 2 (False Positive Rate)",
            "subgroup": "all_negatives",
            "nominal_n": n_neg,
            "cluster_cap": m_cluster_cap,
            "icc_rho": rho,
            "design_effect": round(deff, 3),
            "effective_n": n_eff,
            "ci_95_half_width": round(ci_half, 4),
            "statistical_power": round(pwr, 4)
        })
        print(f"{'Gate 2 (FPR <= 5%)':<30} {'all_negatives':<12} {n_neg:<10} {rho:<10.2f} {deff:<8.3f} {n_eff:<8} {ci_half:<14.4f} {pwr:<15.4f}")

    # 3. Gate 4: Short-Scream Recall (Null = 90.0%, Alt = 95.0%, alpha = 0.05)
    for rho in rho_values:
        deff = 1.0 + (m_cluster_cap - 1.0) * rho
        n_eff = int(n_short / deff)
        ci_half = compute_wilson_ci_width(n_eff, 0.900, z=1.96) / 2.0
        pwr = compute_statistical_power(n_eff, p_null=0.900, p_alt=0.955, alpha=0.05)
        
        power_records.append({
            "gate": "Gate 4 (Short-Scream Recall)",
            "subgroup": "short_screams",
            "nominal_n": n_short,
            "cluster_cap": m_cluster_cap,
            "icc_rho": rho,
            "design_effect": round(deff, 3),
            "effective_n": n_eff,
            "ci_95_half_width": round(ci_half, 4),
            "statistical_power": round(pwr, 4)
        })
        print(f"{'Gate 4 (Short Rec >= 90%)':<30} {'short_screams':<12} {n_short:<10} {rho:<10.2f} {deff:<8.3f} {n_eff:<8} {ci_half:<14.4f} {pwr:<15.4f}")

    out_csv = STAGE64_DIR / "future_evaluation_power_metrics.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(power_records[0].keys()))
        w.writeheader()
        w.writerows(power_records)
    print(f"\nEmitted statistical power analysis to {out_csv}")

if __name__ == "__main__":
    main()

