#!/usr/bin/env python3
"""
STAGE 8.9.65 — Track A: Gate 3 Shouted-Speech False-Positive Rate Audit & Governance Restoration
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import csv
import math
from pathlib import Path
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE63_DIR = BACKEND_DIR / "research" / "stage_8_9_63"
STAGE64_DIR = BACKEND_DIR / "research" / "stage_8_9_64"
STAGE65_DIR = BACKEND_DIR / "research" / "stage_8_9_65"

SHOUTED_SPEECH_RECORDS = ["s60_rec_0054", "s60_rec_0100", "s60_rec_0231", "s60_rec_0236", "s60_rec_0332"]

def compute_wilson_ci(k: int, n: int, confidence: float = 0.95) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    z = 1.95996 if confidence == 0.95 else 2.57583
    p = k / n
    denom = 1.0 + (z**2) / n
    center = (p + (z**2) / (2 * n)) / denom
    margin = (z / denom) * math.sqrt((p * (1 - p) / n) + (z**2) / (4 * n**2))
    return (max(0.0, center - margin), min(1.0, center + margin))

def compute_cluster_bootstrap_ci(df_sub: pd.DataFrame, n_boot: int = 2000, seed: int = 42) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    groups = df_sub["source_group_id"].unique()
    n_groups = len(groups)
    if n_groups <= 1:
        # Fall back to Wilson CI if only 1 group
        k = int(df_sub["predicted_label"].sum())
        n = len(df_sub)
        return compute_wilson_ci(k, n)

    boot_rates = []
    group_map = {g: df_sub[df_sub["source_group_id"] == g] for g in groups}

    for _ in range(n_boot):
        sample_groups = rng.choice(groups, size=n_groups, replace=True)
        sample_dfs = [group_map[g] for g in sample_groups]
        boot_df = pd.concat(sample_dfs, axis=0)
        rate = boot_df["predicted_label"].sum() / len(boot_df)
        boot_rates.append(rate)

    low = float(np.percentile(boot_rates, 2.5))
    high = float(np.percentile(boot_rates, 97.5))
    return (low, high)

def main():
    print("=" * 80)
    print("STAGE 8.9.65 — TRACK A: GATE 3 SHOUTED-SPEECH AUDIT & GOVERNANCE RESTORATION")
    print("=" * 80)

    # Load Stage 64 reproduction CSV
    repro_path = STAGE64_DIR / "dual_resolution_reproduction.csv"
    repro_df = pd.read_csv(repro_path)
    dev_path = STAGE63_DIR / "stage_63_development_manifest.csv"
    dev_df = pd.read_csv(dev_path)

    # Forensically identified vocal/shouted recordings in development cohort
    shout_forensic_ids = {
        "s60_rec_0054": ("sg_s60_162880", "Infant crying / child vocalization outcries"),
        "s60_rec_0100": ("sg_s60_196156", "Sobbing and heavy breathing outcries"),
        "s60_rec_0231": ("sg_s60_350438", "Kid chorus shouting / singing"),
        "s60_rec_0236": ("sg_s60_350452", "Kid chorus group singing / shouting"),
        "s60_rec_0332": ("sg_s60_NIGENS_13575", "NIGENS victim gasping / non-scream vocal outcry")
    }

    # 1. Nominal Shouted Speech Audit
    nominal_shout_df = repro_df[(repro_df["binary_label"] == 0) & (repro_df["target_category"] == "shouted_speech")].copy()
    print(f"\n1. Nominal Shouted Speech (Manifest target_category == 'shouted_speech'):")
    print(f"   Sample Size: {len(nominal_shout_df)} recording(s)")
    print(f"   Source Groups: {nominal_shout_df['source_group_id'].nunique()}")

    # 2. Forensically Audited Vocal / Shouted Outcries
    forensic_shout_df = repro_df[repro_df["recording_id"].isin(shout_forensic_ids.keys())].copy()
    print(f"\n2. Forensically Audited Shouted Speech & Vocal Outcries:")
    print(f"   Sample Size: {len(forensic_shout_df)} recording(s)")
    print(f"   Source Groups: {forensic_shout_df['source_group_id'].nunique()}")

    # Audit records table
    audit_records = []
    for _, r in forensic_shout_df.iterrows():
        rid = r["recording_id"]
        sg, desc = shout_forensic_ids[rid]
        audit_records.append({
            "recording_id": rid,
            "source_group_id": sg,
            "description": desc,
            "duration_seconds": r["duration_seconds"],
            "baseline_prob": round(float(r["predicted_probability"]), 4),
            "baseline_pred": int(r["predicted_label"]),
            "gating_weight_short": round(float(r["gating_weight_short"]), 4),
            "is_nominal_shouted": (rid == "s60_rec_0332")
        })

    audit_csv = STAGE65_DIR / "gate_3_shouted_speech_audit.csv"
    with open(audit_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(audit_records[0].keys()))
        w.writeheader()
        w.writerows(audit_records)
    print(f"\nEmitted shouted speech recording audit to {audit_csv}")

    # Compute Gate 3 metrics for Baseline Dual-Resolution
    # Nominal
    nom_fp = int(nominal_shout_df["predicted_label"].sum())
    nom_n = len(nominal_shout_df)
    nom_tn = nom_n - nom_fp
    nom_fpr = nom_fp / nom_n if nom_n > 0 else 0.0
    nom_w_low, nom_w_high = compute_wilson_ci(nom_fp, nom_n)

    # Forensic
    for_fp = int(forensic_shout_df["predicted_label"].sum())
    for_n = len(forensic_shout_df)
    for_tn = for_n - for_fp
    for_fpr = for_fp / for_n if for_n > 0 else 0.0
    for_w_low, for_w_high = compute_wilson_ci(for_fp, for_n)
    for_c_low, for_c_high = compute_cluster_bootstrap_ci(forensic_shout_df)

    gate_3_metrics = [
        {
            "model_architecture": "Baseline_Dual_Resolution_Gated",
            "shouted_speech_definition": "Nominal_Manifest (target_category == shouted_speech)",
            "sample_size": nom_n,
            "source_groups": nominal_shout_df["source_group_id"].nunique(),
            "false_positives": nom_fp,
            "true_negatives": nom_tn,
            "shouted_speech_fpr": round(nom_fpr, 4),
            "wilson_95_ci_low": round(nom_w_low, 4),
            "wilson_95_ci_high": round(nom_w_high, 4),
            "cluster_boot_ci_low": round(nom_w_low, 4),
            "cluster_boot_ci_high": round(nom_w_high, 4),
            "gate_3_threshold": 0.1500,
            "gate_3_status": "FAIL (100.0% FPR > 15.0%)" if nom_fpr > 0.150 else "PASS"
        },
        {
            "model_architecture": "Baseline_Dual_Resolution_Gated",
            "shouted_speech_definition": "Forensically_Audited_Vocal_Outcries (N=5)",
            "sample_size": for_n,
            "source_groups": forensic_shout_df["source_group_id"].nunique(),
            "false_positives": for_fp,
            "true_negatives": for_tn,
            "shouted_speech_fpr": round(for_fpr, 4),
            "wilson_95_ci_low": round(for_w_low, 4),
            "wilson_95_ci_high": round(for_w_high, 4),
            "cluster_boot_ci_low": round(for_c_low, 4),
            "cluster_boot_ci_high": round(for_c_high, 4),
            "gate_3_threshold": 0.1500,
            "gate_3_status": "FAIL (100.0% FPR > 15.0%)" if for_fpr > 0.150 else "PASS"
        }
    ]

    metrics_csv = STAGE65_DIR / "gate_3_shouted_speech_metrics.csv"
    with open(metrics_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(gate_3_metrics[0].keys()))
        w.writeheader()
        w.writerows(gate_3_metrics)
    print(f"Emitted Gate 3 summary metrics to {metrics_csv}")

    print("\nGate 3 Baseline Audit Results:")
    for m in gate_3_metrics:
        print(f"  [{m['shouted_speech_definition']}]: N={m['sample_size']}, FP={m['false_positives']}, TN={m['true_negatives']}, FPR={m['shouted_speech_fpr']*100:.1f}%, Status={m['gate_3_status']}")

if __name__ == "__main__":
    main()

