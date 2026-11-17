#!/usr/bin/env python3
"""
STAGE 8.9.66 — Track F: Historical Evaluation Cohort Reconciliation
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
This system is an experimental acoustic research prototype and is not certified for life-safety use.
"""

import csv
import json
from pathlib import Path
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
STAGE66_DIR = SCRIPT_DIR.parent
RESEARCH_DIR = STAGE66_DIR.parent
STAGE60_DIR = RESEARCH_DIR / "stage_8_9_60"
STAGE61_DIR = RESEARCH_DIR / "stage_8_9_61"
STAGE65_DIR = RESEARCH_DIR / "stage_8_9_65"


def audit_cohort_history():
    print("=" * 80)
    print("STAGE 8.9.66 — TRACK F: HISTORICAL EVALUATION COHORT RECONCILIATION")
    print("MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.")
    print("=" * 80)

    # Historical cohort evolutions:
    # 1. Stage 60/61 Sealed Cohort: N=700 (200 pos, 500 neg)
    with open(STAGE60_DIR / "future_evaluation_manifest.json", "r", encoding="utf-8") as f:
        s60_data = json.load(f)
    s60_recs = s60_data["recordings"]

    s60_pos = sum(1 for r in s60_recs if r["binary_label"] == 1)
    s60_neg = sum(1 for r in s60_recs if r["binary_label"] == 0)

    # 2. Earlier Stage 60 Planning Proposal: N=1,050 Low-Prevalence
    # 240 positive, 810 negative (prevalence = 22.86%)
    p_early = {
        "design_id": "Design_Early_LowPrevalence",
        "total_n": 1050,
        "n_pos": 240,
        "n_neg": 810,
        "prevalence": 240 / 1050,
        "pos_short": 120,
        "pos_sust": 120,
        "neg_shouted": 150,
        "neg_whistle": 120,
        "neg_crowd": 180,
        "neg_ambient": 360,
        "primary_objective": "Realistic rare-event surveillance prevalence with high negative statistical power."
    }

    # 3. Stage 65 Balanced Proposal: N=1,050
    # 550 positive, 500 negative (prevalence = 52.38%)
    p_stage65 = {
        "design_id": "Design_Stage65_Balanced",
        "total_n": 1050,
        "n_pos": 550,
        "n_neg": 500,
        "prevalence": 550 / 1050,
        "pos_short": 350,
        "pos_sust": 200,
        "neg_shouted": 120,
        "neg_whistle": 80,
        "neg_crowd": 120,
        "neg_ambient": 180,
        "primary_objective": "High positive sub-cohort resolution and short-scream statistical power."
    }

    # 4. Stage 66 Authoritative Reconciled Design: N=1,050
    # 350 positive, 700 negative (prevalence = 33.33%, 1:2 ratio)
    p_stage66 = {
        "design_id": "Design_Stage66_Reconciled",
        "total_n": 1050,
        "n_pos": 350,
        "n_neg": 700,
        "prevalence": 350 / 1050,
        "pos_short": 220,
        "pos_sust": 130,
        "neg_shouted": 160,
        "neg_whistle": 100,
        "neg_crowd": 160,
        "neg_ambient": 280,
        "primary_objective": "Rigorous 1:2 prevalence balance ensuring >95% power on all 5 gates with 160 shouted speech."
    }

    designs = [p_early, p_stage65, p_stage66]
    alloc_csv = STAGE66_DIR / "evaluation_cohort_allocation.csv"

    rows = []
    for d in designs:
        rows.append({
            "design_id": d["design_id"],
            "total_recordings": d["total_n"],
            "positive_recordings": d["n_pos"],
            "negative_recordings": d["n_neg"],
            "prevalence_pct": round(d["prevalence"] * 100, 2),
            "short_screams": d["pos_short"],
            "sustained_screams": d["pos_sust"],
            "shouted_speech_negatives": d["neg_shouted"],
            "whistle_tone_negatives": d["neg_whistle"],
            "crowd_cheer_negatives": d["neg_crowd"],
            "ambient_environmental_negatives": d["neg_ambient"],
            "rationale": d["primary_objective"]
        })

    pd.DataFrame(rows).to_csv(alloc_csv, index=False)
    print(f"Emitted {alloc_csv.name}.")

    # Author evaluation_cohort_history_audit.md
    hist_md = STAGE66_DIR / "evaluation_cohort_history_audit.md"
    with open(hist_md, "w", encoding="utf-8") as f:
        f.write("# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.\n\n")
        f.write("# HISTORICAL EVALUATION COHORT RECONCILIATION REPORT\n")
        f.write("**Forensic Audit of Sample Size Evolution, Prevalence Drift, and Cohort Topologies**\n\n")
        f.write("## 1. Safety Designation\n")
        f.write("Non-certified acoustic research prototype. Prohibited for life-safety use, emergency alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.\n\n")
        f.write("All tests utilize legally acquired recorded audio files and safe playback protocols only.\n\n---\n\n")
        f.write("## 2. Chronological Evolution of Evaluation Cohorts\n\n")
        f.write("| Stage & Cohort Description | Total N | Positives | Negatives | Prevalence | Sub-Cohorts & Focus |\n")
        f.write("|---|---|---|---|---|---|\n")
        f.write(f"| **Stage 60 Sealed Cohort** | {len(s60_recs)} | {s60_pos} | {s60_neg} | {s60_pos/len(s60_recs)*100:.1f}% | Preserved, cryptographically sealed benchmark. |\n")
        f.write(f"| **Early Stage 60 Planning ($N=1,050$)** | 1,050 | 240 | 810 | 22.86% | Realistic surveillance monitoring; high negative focus. |\n")
        f.write(f"| **Stage 65 Balanced Proposal** | 1,050 | 550 | 500 | 52.38% | Sub-second scream focus (350 short screams). |\n")
        f.write(f"| **Stage 66 Reconciled Authoritative Design** | **1,050** | **350** | **700** | **33.33%** | **Harmonized 1:2 ratio with 220 short screams and 160 shouted speech.** |\n\n---\n\n")
        f.write("## 3. Discrepancy & Prevalence Drift Forensics\n\n")
        f.write("### A. Why did the allocation shift from 240/810 to 550/500?\n")
        f.write("In Stage 8.9.64 and 8.9.65, research discovered that Candidate E1's primary historical vulnerability was short screams (<1.00s).\n")
        f.write("To achieve statistical power for fine-grained subgroup comparisons (e.g. ultra-short $\\le 0.50$s vs standard short), the Stage 65 planning team inflated positive allocations to 550.\n\n")
        f.write("### B. Flaws in the Balanced 550/500 Design\n")
        f.write("1. **Prevalence Distortion:** A 52.38% scream prevalence is unrepresentative of operational environments where emergency events are rare anomalies ($<1\\%$).\n")
        f.write("2. **Under-Sampling Hard Negatives:** Compressing negatives to 500 constrained the budget for shouted speech (only 120 allocated) and industrial noise.\n")
        f.write("3. **Precision Distortion:** A balanced cohort produces an artificially high positive predictive value (PPV), masking false alarm costs.\n\n")
        f.write("### C. Why Reconciled 350/700 is the Authoritative Solution\n")
        f.write("- **$N=350$ Positives:** Provides 220 short screams and 130 sustained screams. As proven in Track F power calculations, 220 short screams provides **$>99.5\\%$ statistical power** for Gate 4 ($\ge 90\\%$), eliminating the need for 550 positives.\n")
        f.write("- **$N=700$ Negatives:** Provides 160 shouted-speech files (powering Gate 3 to $>96\\%$) and 540 diverse environmental/transient negatives (powering Gate 2 to $>98\\%$).\n")
        f.write("- **Realistic 1:2 Ratio:** Balances statistical efficiency with operational rigor.\n")
    print(f"Emitted {hist_md.name}.")


if __name__ == "__main__":
    audit_cohort_history()

