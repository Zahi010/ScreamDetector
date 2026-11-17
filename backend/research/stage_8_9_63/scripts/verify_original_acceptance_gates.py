#!/usr/bin/env python3
"""
STAGE 8.9.63 — Original Acceptance Gate Verification Script
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import sys

GATE_DEFINITIONS = {
    "Gate 1": {"name": "Overall scream recall", "threshold": 0.96, "operator": ">=", "metric_key": "overall_recall"},
    "Gate 2": {"name": "Hard-negative FPR", "threshold": 0.05, "operator": "<=", "metric_key": "hard_negative_fpr"},
    "Gate 3": {"name": "Shouted-speech FPR", "threshold": 0.15, "operator": "<=", "metric_key": "shouted_speech_fpr"},
    "Gate 4": {"name": "Short-scream recall", "threshold": 0.90, "operator": ">=", "metric_key": "short_scream_recall"},
    "Gate 5": {"name": "Model-only inference P95", "threshold": 25.0, "operator": "<=", "metric_key": "model_p95_ms"}
}

def evaluate_candidate(candidate_id: str, metrics: dict):
    print(f"\nEvaluating Candidate [{candidate_id}] against Original 5 Gates:")
    all_passed = True
    for gid, gdef in GATE_DEFINITIONS.items():
        val = metrics.get(gdef["metric_key"])
        if val is None:
            print(f"  {gid} ({gdef['name']}): MISSING METRIC")
            all_passed = False
            continue
        if gdef["operator"] == ">=":
            passed = val >= gdef["threshold"]
            print(f"  {gid} ({gdef['name']}): {val*100:.2f}% vs req {gdef['threshold']*100:.2f}% -> {'PASSED' if passed else 'FAILED'}")
        else:
            passed = val <= gdef["threshold"]
            unit = "ms" if gid == "Gate 5" else "%"
            scale = 1.0 if gid == "Gate 5" else 100.0
            print(f"  {gid} ({gdef['name']}): {val*scale:.2f}{unit} vs req {gdef['threshold']*scale:.2f}{unit} -> {'PASSED' if passed else 'FAILED'}")
        if not passed:
            all_passed = False
    print(f"  Overall Verdict: {'APPROVED' if all_passed else 'REJECTED'}")
    return all_passed

def main():
    # Historical Candidate Metrics on Sealed 700 Cohort
    candidates = {
        "Candidate_E1_Static_C5": {
            "overall_recall": 0.5800,
            "hard_negative_fpr": 0.1920,
            "shouted_speech_fpr": 0.2267,
            "short_scream_recall": 0.3623,
            "model_p95_ms": 0.58
        },
        "Candidate_B_Baseline": {
            "overall_recall": 0.5750,
            "hard_negative_fpr": 0.1580,
            "shouted_speech_fpr": 0.1400,
            "short_scream_recall": 0.3913,
            "model_p95_ms": 0.42
        },
        "Candidate_E1_Rolling_C5_EMA": {
            "overall_recall": 0.7000,
            "hard_negative_fpr": 0.3540,
            "shouted_speech_fpr": 0.3067,
            "short_scream_recall": 0.3913,
            "model_p95_ms": 0.58
        }
    }

    for cid, m in candidates.items():
        evaluate_candidate(cid, m)

if __name__ == "__main__":
    main()

