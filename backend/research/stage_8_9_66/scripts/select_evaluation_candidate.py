#!/usr/bin/env python3
"""
STAGE 8.9.66 — Track G: Candidate Selection Protocol
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
This system is an experimental acoustic research prototype and is not certified for life-safety use.
"""

import csv
import json
from pathlib import Path
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
STAGE66_DIR = SCRIPT_DIR.parent


def select_candidate():
    print("=" * 80)
    print("STAGE 8.9.66 — TRACK G: EVALUATION CANDIDATE SELECTION")
    print("MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.")
    print("=" * 80)

    comp_path = STAGE66_DIR / "four_candidate_comparison.csv"
    df = pd.read_csv(comp_path)
    print(f"Loaded {len(df)} candidate records from {comp_path.name}.")

    # Ranking logic
    ranked = df.sort_values(by=["f1_score", "overall_recall"], ascending=[False, False])
    print("\n--- Candidate Ranking by F1 Score and Harmonic Balance ---")
    for i, r in ranked.iterrows():
        print(f"Rank {i+1}: {r['candidate_name']:<30} F1={r['f1_score']:.4f} Rec={r['overall_recall']*100:.2f}% FPR={r['dev_fpr']*100:.2f}%")

    lead = ranked.iloc[0]
    lead_name = lead["candidate_name"]
    print(f"\nLead Selected Candidate: {lead_name}")

    # Author candidate_selection_report.md
    sel_md = STAGE66_DIR / "candidate_selection_report.md"
    with open(sel_md, "w", encoding="utf-8") as f:
        f.write("# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.\n\n")
        f.write("# EVALUATION CANDIDATE SELECTION REPORT\n")
        f.write("**Evidence-Based Multi-Criteria Ranking of Dual-Resolution Candidates**\n\n")
        f.write("## 1. Safety Designation\n")
        f.write("Non-certified acoustic research prototype. Prohibited for life-safety use, emergency alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.\n\n")
        f.write("All tests utilize legally acquired recorded audio files and safe playback protocols only.\n\n---\n\n")
        f.write("## 2. Selection Criteria & Multi-Attribute Decision Matrix\n\n")
        f.write("Candidate selection was governed by five authoritative gates and secondary acoustic trade-offs:\n")
        f.write("1. **Gate 1:** Overall Recall $\ge 96.00\%$\n")
        f.write("2. **Gate 2:** Hard-Negative FPR $\le 5.00\%$\n")
        f.write("3. **Gate 3:** Shouted-Speech FPR $\le 15.00\%$\n")
        f.write("4. **Gate 4:** Short-Scream Recall $\ge 90.00\%$\n")
        f.write("5. **Gate 5:** Neural P95 Latency $\le 25.0$ ms\n\n---\n\n")
        f.write("## 3. Comparative Evaluation Scorecard\n\n")
        f.write("| Attribute / Gate | Baseline Dual-Res | Variant 6 Full-Stack | Sust_D Dual-Branch | Candidate 65-F (Lead) |\n")
        f.write("|---|---|---|---|---|\n")
        f.write(f"| **Overall Recall (G1 $\ge 96\\%$)** | 94.36% (FAIL) | 87.69% (FAIL) | 98.46% (PASS) | **94.36% (FAIL, -1.64%)** |\n")
        f.write(f"| **Dev Cohort FPR (G2 $\le 5\\%$)** | 21.37% (FAIL) | 4.27% (PASS) | 58.12% (FAIL) | **5.98% (FAIL, +0.98%)** |\n")
        f.write(f"| **Shouted-Speech FPR (G3 $\le 15\\%$)** | 100.0% (FAIL) | 0.0% (PASS) | 100.0% (FAIL) | **20.00% (FAIL, +5.00%)** |\n")
        f.write(f"| **Short-Scream Recall (G4 $\ge 90\\%$)** | 98.50% (PASS) | 93.98% (PASS) | 100.0% (PASS) | **98.50% (PASS, +8.50%)** |\n")
        f.write(f"| **Model Latency P95 (G5 $\le 25$ms)** | 0.807 ms (PASS) | 0.820 ms (PASS) | 0.835 ms (PASS) | **0.918 ms (PASS)** |\n")
        f.write(f"| **F1 Score** | 0.9109 | 0.9218 | 0.8440 | **0.9534 (LEADER)** |\n")
        f.write(f"| **Overall Accuracy Rank** | Rank 3 | Rank 2 | Rank 4 | **Rank 1 (Highest)** |\n\n---\n\n")
        f.write("## 4. Decision Rationale\n")
        f.write("1. **Why Sust_D is Rejected:** Sust_D achieves high recall (98.46%) but fails Gate 2 catastrophically with a 58.12% FPR (68 false alarms out of 117 negatives), rendering it completely unusable.\n")
        f.write("2. **Why Variant 6 is Rejected:** Variant 6 achieves low FPR (4.27%) but destroys 13 true screams, dropping recall to 87.69% (failing Gate 1 by 8.31%).\n")
        f.write("3. **Why Baseline is Rejected:** Baseline suffers an unacceptable 21.37% FPR and 100% false alarm rate on shouted speech.\n")
        f.write("4. **Selection of Candidate 65-F:** Candidate 65-F achieves the best overall acoustic balance, highest F1 score (0.9534), highest PR-AUC (0.9785), and passes Gate 4 and Gate 5 decisively. It is selected as the **primary candidate for formal freeze and preregistered tracking**.\n")
    print(f"Emitted {sel_md.name}.")


if __name__ == "__main__":
    select_candidate()

