#!/usr/bin/env python3
"""
STAGE 8.9.65 — Track H: Statistical Power Analysis for N=1,050 Independent Evaluation
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import math
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import norm

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE65_DIR = BACKEND_DIR / "research" / "stage_8_9_65"

def compute_cluster_power(p_alt: float, p_null: float, n_total: int, cluster_size_m: float, icc_rho: float, alpha: float = 0.05, one_sided: bool = True):
    """Computes statistical power accounting for cluster design effects."""
    deff = 1.0 + (cluster_size_m - 1.0) * icc_rho
    n_eff = n_total / deff

    z_alpha = norm.ppf(1.0 - alpha) if one_sided else norm.ppf(1.0 - alpha / 2.0)

    # Standard error under null and alternative
    se_null = math.sqrt(p_null * (1.0 - p_null) / n_eff)
    se_alt = math.sqrt(p_alt * (1.0 - p_alt) / n_eff)

    if p_alt > p_null:
        # Testing H0: p <= p_null vs H1: p > p_null
        crit_val = p_null + z_alpha * se_null
        z_beta = (crit_val - p_alt) / se_alt
        power = 1.0 - norm.cdf(z_beta)
    else:
        # Testing H0: p >= p_null vs H1: p < p_null
        crit_val = p_null - z_alpha * se_null
        z_beta = (p_alt - crit_val) / se_alt
        power = 1.0 - norm.cdf(z_beta)

    return {
        "n_nominal": n_total,
        "cluster_size_m": cluster_size_m,
        "icc_rho": icc_rho,
        "design_effect": round(deff, 4),
        "n_effective": round(n_eff, 1),
        "p_null": p_null,
        "p_alt": p_alt,
        "alpha": alpha,
        "power": round(float(power), 4)
    }

def main():
    print("=" * 80)
    print("STAGE 8.9.65 — TRACK H: STATISTICAL POWER ANALYSIS FOR N=1,050 COHORT")
    print("=" * 80)

    # Candidate 65 cohort composition
    # N = 1,050 total:
    # 550 Positives: 350 Short Screams (< 1.0s), 200 Sustained Screams (>= 1.0s)
    # 500 Negatives: 120 Shouted Speech, 150 Whistles/Tones, 100 Squeaks, 130 Ambient Soundscapes
    scenarios = [
        {
            "gate": "Gate_1_Overall_Recall",
            "p_alt": 0.960,  # Target recall
            "p_null": 0.930, # Conservative null benchmark
            "n_total": 550,
            "m": 1.35,
            "rho": 0.06
        },
        {
            "gate": "Gate_2_Hard_Negative_FPR",
            "p_alt": 0.040,  # Target FPR
            "p_null": 0.075, # Unacceptable FPR threshold
            "n_total": 500,
            "m": 1.15,
            "rho": 0.04
        },
        {
            "gate": "Gate_3_Shouted_Speech_FPR",
            "p_alt": 0.100,  # Target shouted FPR
            "p_null": 0.200, # Substandard shouted FPR
            "n_total": 120,
            "m": 1.20,
            "rho": 0.05
        },
        {
            "gate": "Gate_4_Short_Scream_Recall",
            "p_alt": 0.960,  # Target short-scream recall
            "p_null": 0.900, # Acceptance minimum
            "n_total": 350,
            "m": 1.30,
            "rho": 0.06
        }
    ]

    results = []
    print(f"{'Gate Target':<28} {'N_Nominal':<10} {'N_Eff':<8} {'P_Null':<8} {'P_Alt':<8} {'DesignEff':<10} {'Power':<8}")
    print("-" * 88)

    for sc in scenarios:
        p_res = compute_cluster_power(
            p_alt=sc["p_alt"],
            p_null=sc["p_null"],
            n_total=sc["n_total"],
            cluster_size_m=sc["m"],
            icc_rho=sc["rho"]
        )
        p_res["gate_target"] = sc["gate"]
        results.append(p_res)
        print(f"{sc['gate']:<28} {p_res['n_nominal']:<10} {p_res['n_effective']:<8.1f} {p_res['p_null']:<8.3f} {p_res['p_alt']:<8.3f} {p_res['design_effect']:<10.3f} {p_res['power']:<8.4f}")

    out_csv = STAGE65_DIR / "future_evaluation_power_analysis.csv"
    pd.DataFrame(results).to_csv(out_csv, index=False)
    print(f"\nEmitted power analysis results to {out_csv}")

if __name__ == "__main__":
    main()

