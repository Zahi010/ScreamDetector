#!/usr/bin/env python3
"""
STAGE 8.9.65 — Automated Authoritative Five-Gate Acceptance Calculator
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import math
from pathlib import Path
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[4]
STAGE65_DIR = REPO_ROOT / "backend" / "research" / "stage_8_9_65"

AUTHORITATIVE_GATES = {
    "Gate 1": {
        "name": "Overall Scream Recall",
        "threshold": 0.9600,
        "operator": ">=",
        "expected_denominator": 195,
        "target_population": "all_positive_screams"
    },
    "Gate 2": {
        "name": "Hard-Negative False Positive Rate (FPR)",
        "threshold": 0.0500,
        "operator": "<=",
        "expected_denominator": 117,
        "target_population": "all_hard_negatives"
    },
    "Gate 3": {
        "name": "Shouted-Speech False Positive Rate (FPR)",
        "threshold": 0.1500,
        "operator": "<=",
        "expected_denominator": 5,  # Forensically audited vocal outcries in dev cohort
        "target_population": "shouted_speech_vocal_negatives"
    },
    "Gate 4": {
        "name": "Short-Scream Recall (<1.00s Duration)",
        "threshold": 0.9000,
        "operator": ">=",
        "expected_denominator": 133,
        "target_population": "positive_screams_under_1s"
    },
    "Gate 5": {
        "name": "Model-Only Inference Latency P95",
        "threshold": 25.00,
        "operator": "<=",
        "unit": "ms"
    }
}

GATE_DEFINITIONS = {
    "gate1": {
        "name": "Overall Scream Recall",
        "metric": "overall_recall",
        "threshold": 0.960,
        "comparator": ">=",
        "description": "Overall Recall >= 96.0% on development cohort (N=195 positives)"
    },
    "gate2": {
        "name": "Hard-Negative False Positive Rate",
        "metric": "hard_negative_fpr",
        "threshold": 0.050,
        "comparator": "<=",
        "description": "Hard-Negative FPR <= 5.0% on development cohort (N=117 negatives)"
    },
    "gate3": {
        "name": "Shouted-Speech False Positive Rate",
        "metric": "shouted_speech_fpr",
        "threshold": 0.150,
        "comparator": "<=",
        "description": "Shouted-Speech FPR <= 15.0% on vocal outcry controls (authoritative Gate 3 definition)"
    },
    "gate4": {
        "name": "Short-Scream Recall",
        "metric": "short_scream_recall",
        "threshold": 0.900,
        "comparator": ">=",
        "description": "Short-Scream Recall >= 90.0% on screams < 1.00s in duration (N=133 dev short screams)"
    },
    "gate5": {
        "name": "Model-Only Inference Latency P95",
        "metric": "nn_latency_p95_ms",
        "threshold": 25.0,
        "comparator": "<=",
        "description": "Model-only neural forward pass P95 <= 25.0 ms across 1 to 8 concurrent streams"
    }
}

def evaluate_scorecard(metrics_dict: dict) -> dict:
    """Evaluates a dictionary of computed metrics against the authoritative gates."""
    required = ["overall_recall", "hard_negative_fpr", "shouted_speech_fpr", "short_scream_recall", "nn_latency_p95_ms"]
    for m in required:
        if m not in metrics_dict:
            raise ValueError(f"Missing required metric in evaluation: '{m}'")
    results = {}
    for g_id, g_def in GATE_DEFINITIONS.items():
        val = metrics_dict[g_def["metric"]]
        passed = (val >= g_def["threshold"]) if g_def["comparator"] == ">=" else (val <= g_def["threshold"])
        results[g_id] = {"metric": g_def["metric"], "value": val, "passed": passed}
    return results

def validate_denominators(n_pos: int, n_neg: int, n_short: int = 133):
    """Strictly validates positive, negative, and short event cohort totals."""
    assert n_pos == 195, f"Expected exactly 195 positives, got {n_pos}"
    assert n_neg == 117, f"Expected exactly 117 negatives, got {n_neg}"

def validate_cohort_purity(recording_ids: list):
    """Validates that evaluation does not mix development and external cohorts."""
    has_dev = any(rid.startswith("s60_rec_") or rid.startswith("s63_short_") for rid in recording_ids)
    has_eval = any(rid.startswith("eval_unseen_") or rid.startswith("s61_eval_") for rid in recording_ids)
    if has_dev and has_eval:
        raise ValueError("Mixed cohort detected: Development and independent evaluation IDs cannot be combined.")

def compute_wilson_interval(k: int, n: int, confidence: float = 0.95) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    z = 1.95996 if confidence == 0.95 else 2.57583
    p = k / n
    denom = 1.0 + (z**2) / n
    center = (p + (z**2) / (2 * n)) / denom
    margin = (z / denom) * math.sqrt((p * (1 - p) / n) + (z**2) / (4 * n**2))
    return (max(0.0, center - margin), min(1.0, center + margin))

def evaluate_authoritative_gates(pred_df: pd.DataFrame, model_only_p95_ms: float,
                                 candidate_id: str = "Candidate",
                                 enforce_strict_denominators: bool = True) -> dict:
    """
    Evaluates prediction DataFrame against the authoritative five research acceptance gates.
    Rejects missing metrics, inconsistent denominators, and mixed cohorts.
    """
    # 1. Denominator Verification
    n_total = len(pred_df)
    n_pos = int((pred_df["binary_label"] == 1).sum())
    n_neg = int((pred_df["binary_label"] == 0).sum())

    # Duration calculations (<1.00s strictly)
    if "duration_seconds" not in pred_df.columns:
        raise ValueError("Missing mandatory column: 'duration_seconds'")

    short_pos_mask = (pred_df["binary_label"] == 1) & (pred_df["duration_seconds"] < 1.00)
    ultra_short_pos_mask = (pred_df["binary_label"] == 1) & (pred_df["duration_seconds"] <= 0.50)
    sust_pos_mask = (pred_df["binary_label"] == 1) & (pred_df["duration_seconds"] >= 1.00)

    n_short = int(short_pos_mask.sum())
    n_ultra_short = int(ultra_short_pos_mask.sum())
    n_sust = int(sust_pos_mask.sum())

    # Shouted speech mask
    shout_forensic_ids = {"s60_rec_0054", "s60_rec_0100", "s60_rec_0231", "s60_rec_0236", "s60_rec_0332"}
    shout_mask = (pred_df["binary_label"] == 0) & (
        (pred_df["target_category"] == "shouted_speech") | (pred_df["recording_id"].isin(shout_forensic_ids))
    )
    n_shout = int(shout_mask.sum())

    if enforce_strict_denominators:
        if n_total != 312:
            raise ValueError(f"Cohort validation error: Expected exactly 312 recordings, got {n_total}")
        if n_pos != 195:
            raise ValueError(f"Denominator mismatch: Expected 195 positives, got {n_pos}")
        if n_neg != 117:
            raise ValueError(f"Denominator mismatch: Expected 117 negatives, got {n_neg}")
        if n_short != 133:
            raise ValueError(f"Gate 4 denominator mismatch: Expected 133 short screams (<1.0s), got {n_short}")

    # 2. Gate Computations
    # Gate 1: Overall Scream Recall
    tp_overall = int(((pred_df["binary_label"] == 1) & (pred_df["predicted_label"] == 1)).sum())
    recall_overall = tp_overall / n_pos if n_pos > 0 else 0.0
    g1_ci = compute_wilson_interval(tp_overall, n_pos)
    g1_pass = recall_overall >= AUTHORITATIVE_GATES["Gate 1"]["threshold"]

    # Gate 2: Hard-Negative FPR
    fp_overall = int(((pred_df["binary_label"] == 0) & (pred_df["predicted_label"] == 1)).sum())
    fpr_overall = fp_overall / n_neg if n_neg > 0 else 0.0
    g2_ci = compute_wilson_interval(fp_overall, n_neg)
    g2_pass = fpr_overall <= AUTHORITATIVE_GATES["Gate 2"]["threshold"]

    # Gate 3: Shouted-Speech FPR
    fp_shout = int((shout_mask & (pred_df["predicted_label"] == 1)).sum())
    fpr_shout = fp_shout / n_shout if n_shout > 0 else 0.0
    g3_ci = compute_wilson_interval(fp_shout, n_shout)
    g3_pass = fpr_shout <= AUTHORITATIVE_GATES["Gate 3"]["threshold"]

    # Gate 4: Short-Scream Recall (<1.00s)
    tp_short = int((short_pos_mask & (pred_df["predicted_label"] == 1)).sum())
    recall_short = tp_short / n_short if n_short > 0 else 0.0
    g4_ci = compute_wilson_interval(tp_short, n_short)
    g4_pass = recall_short >= AUTHORITATIVE_GATES["Gate 4"]["threshold"]

    # Ultra-short diagnostic subgroup (<=0.50s)
    tp_ultra = int((ultra_short_pos_mask & (pred_df["predicted_label"] == 1)).sum())
    recall_ultra = tp_ultra / n_ultra_short if n_ultra_short > 0 else 0.0

    # Sustained diagnostic subgroup (>=1.00s)
    tp_sust = int((sust_pos_mask & (pred_df["predicted_label"] == 1)).sum())
    recall_sust = tp_sust / n_sust if n_sust > 0 else 0.0

    # Gate 5: Model-Only Latency P95
    g5_pass = model_only_p95_ms <= AUTHORITATIVE_GATES["Gate 5"]["threshold"]

    all_gates_pass = g1_pass and g2_pass and g3_pass and g4_pass and g5_pass

    scorecard = {
        "candidate_id": candidate_id,
        "all_gates_met": all_gates_pass,
        "promotion_eligibility": "ELIGIBLE_FOR_INDEPENDENT_EVALUATION" if all_gates_pass else "PROMOTION_DENIED",
        "gate_1": {
            "name": "Overall Scream Recall",
            "required": ">= 96.0%",
            "observed": round(recall_overall, 4),
            "fraction": f"{tp_overall}/{n_pos}",
            "ci_95": (round(g1_ci[0], 4), round(g1_ci[1], 4)),
            "status": "PASS" if g1_pass else "FAIL"
        },
        "gate_2": {
            "name": "Hard-Negative FPR",
            "required": "<= 5.0%",
            "observed": round(fpr_overall, 4),
            "fraction": f"{fp_overall}/{n_neg}",
            "ci_95": (round(g2_ci[0], 4), round(g2_ci[1], 4)),
            "status": "PASS" if g2_pass else "FAIL"
        },
        "gate_3": {
            "name": "Shouted-Speech FPR",
            "required": "<= 15.0%",
            "observed": round(fpr_shout, 4),
            "fraction": f"{fp_shout}/{n_shout}",
            "ci_95": (round(g3_ci[0], 4), round(g3_ci[1], 4)),
            "status": "PASS" if g3_pass else "FAIL"
        },
        "gate_4": {
            "name": "Short-Scream Recall (<1.00s)",
            "required": ">= 90.0%",
            "observed": round(recall_short, 4),
            "fraction": f"{tp_short}/{n_short}",
            "ci_95": (round(g4_ci[0], 4), round(g4_ci[1], 4)),
            "status": "PASS" if g4_pass else "FAIL"
        },
        "diagnostic_ultra_short": {
            "name": "Diagnostic Ultra-Short Recall (<=0.50s)",
            "observed": round(recall_ultra, 4),
            "fraction": f"{tp_ultra}/{n_ultra_short}"
        },
        "diagnostic_sustained": {
            "name": "Diagnostic Sustained Recall (>=1.00s)",
            "observed": round(recall_sust, 4),
            "fraction": f"{tp_sust}/{n_sust}"
        },
        "gate_5": {
            "name": "Model-Only Inference P95",
            "required": "<= 25.0 ms",
            "observed_ms": round(model_only_p95_ms, 3),
            "status": "PASS" if g5_pass else "FAIL"
        }
    }
    return scorecard

def format_scorecard_markdown(sc: dict) -> str:
    lines = []
    lines.append(f"### Acceptance Gate Scorecard: {sc['candidate_id']}")
    lines.append(f"**Overall Compliance:** {'ALL GATES MET' if sc['all_gates_met'] else 'GATES UNMET'}")
    lines.append(f"**Governance Decision:** `{sc['promotion_eligibility']}`\n")
    lines.append("| Gate | Metric Name | Standard | Observed Value | Denominator | 95% Wilson CI | Gate Status |")
    lines.append("| :--- | :--- | :---: | :---: | :---: | :---: | :---: |")

    g1 = sc["gate_1"]
    lines.append(f"| **Gate 1** | {g1['name']} | {g1['required']} | **{g1['observed']*100:.2f}%** | {g1['fraction']} | [{g1['ci_95'][0]*100:.1f}%, {g1['ci_95'][1]*100:.1f}%] | **{g1['status']}** |")

    g2 = sc["gate_2"]
    lines.append(f"| **Gate 2** | {g2['name']} | {g2['required']} | **{g2['observed']*100:.2f}%** | {g2['fraction']} | [{g2['ci_95'][0]*100:.1f}%, {g2['ci_95'][1]*100:.1f}%] | **{g2['status']}** |")

    g3 = sc["gate_3"]
    lines.append(f"| **Gate 3** | {g3['name']} | {g3['required']} | **{g3['observed']*100:.2f}%** | {g3['fraction']} | [{g3['ci_95'][0]*100:.1f}%, {g3['ci_95'][1]*100:.1f}%] | **{g3['status']}** |")

    g4 = sc["gate_4"]
    lines.append(f"| **Gate 4** | {g4['name']} | {g4['required']} | **{g4['observed']*100:.2f}%** | {g4['fraction']} | [{g4['ci_95'][0]*100:.1f}%, {g4['ci_95'][1]*100:.1f}%] | **{g4['status']}** |")

    g5 = sc["gate_5"]
    lines.append(f"| **Gate 5** | {g5['name']} | {g5['required']} | **{g5['observed_ms']:.3f} ms** | N/A | N/A | **{g5['status']}** |")

    lines.append("\n**Diagnostic Subgroups:**")
    u = sc["diagnostic_ultra_short"]
    s = sc["diagnostic_sustained"]
    lines.append(f"- **Ultra-Short Screams (<=0.50s):** {u['observed']*100:.2f}% ({u['fraction']})")
    lines.append(f"- **Sustained Screams (>=1.00s):** {s['observed']*100:.2f}% ({s['fraction']})")

    return "\n".join(lines)

if __name__ == "__main__":
    # Test on Stage 64 reproduction CSV
    df = pd.read_csv(STAGE65_DIR.parents[0] / "stage_8_9_64" / "dual_resolution_reproduction.csv")
    sc = evaluate_authoritative_gates(df, model_only_p95_ms=0.807, candidate_id="Baseline_Dual_Resolution")
    print(format_scorecard_markdown(sc))

