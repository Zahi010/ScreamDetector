"""Stage 8.9.13 Dual-Path Event Boundary Logic and Evaluation.

Implements:
1. Comprehensive validation parameter search across Dual-Path state machine policies.
2. Strict Validation Feasibility Check (Recall >= 96% AND Hard-Negative FPR <= 5%).
3. Single-shot held-out test evaluation with cluster-bootstrap 95% CIs.
4. Separate evaluation of:
   - Event-level recall (all screams)
   - Brief scream recall (< 1.0s duration)
   - Event-level hard-negative FPR
   - Event-level shouted-speech FPR
   - Duplicate alert reduction
   - Detection delay relative to event onset
   - Operational hourly false alert rates
5. Paired McNemar hypothesis tests against single-window baseline.

Outputs:
- `stage8_9_13_event_logic/temporal_policy_validation_results.csv`
- `stage8_9_13_event_logic/experiment_configurations.json`
- `stage8_9_13_event_logic/event_level_test_results.csv`
- `stage8_9_13_event_logic/detection_delay_analysis.csv`
"""

from __future__ import annotations

import csv
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
from scipy import stats
from sklearn.metrics import precision_recall_fscore_support

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("evaluate_event_logic")

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))

STAGE11_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_11_evaluation"
STAGE12_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_12_runtime_research"
STAGE13_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_13_event_logic"
CACHE_PATH = STAGE12_DIR / "window_probabilities_cache.npz"
MANIFEST_PATH = STAGE11_DIR / "stage8_9_11_dataset_manifest.json"

from experiments.v2_hard_negative_training.v4_temporal_research.stage8_9_13_event_logic.dual_path_state_machine import (
    DualPathEventStateMachine,
)
from experiments.v2_hard_negative_training.v4_temporal_research.stage8_9_12_runtime_research.temporal_state_machine import (
    SingleWindowPolicy,
    ConsecutivePersistencePolicy,
    HysteresisCooldownPolicy,
)


def evaluate_state_machine_on_dataset(
    sm_factory: Any,
    dataset: Dict[str, Any],
    prob_key: str = "probs_d",
) -> Dict[str, Any]:
    """Evaluate an alert state machine over a dataset of sequential recordings."""
    hop_sec = 0.5

    event_preds = []
    event_labels = []
    event_categories = []
    event_groups = []
    detection_delays_all = []
    detection_delays_short = []
    detection_delays_sustained = []
    detection_delays_masked = []
    duplicate_counts = []
    short_events_total = 0
    short_events_detected = 0

    for fid, item in dataset.items():
        y_true = item["y_true"]
        probs = item[prob_key]
        cat = item["category"]
        group_id = item["group_id"]
        dur = item["duration"]

        sm = sm_factory()
        sm.reset()

        alerts_fired = 0
        first_alert_time = None

        for t_idx, p in enumerate(probs):
            timestamp_sec = t_idx * hop_sec + 1.0  # window endpoint
            fired, _ = sm.step(p, timestamp_sec)
            if fired:
                alerts_fired += 1
                if first_alert_time is None:
                    first_alert_time = timestamp_sec

        has_alert = (alerts_fired > 0)
        event_preds.append(1 if has_alert else 0)
        event_labels.append(y_true)
        event_categories.append(cat)
        event_groups.append(group_id)

        if y_true == 1:
            duplicate_counts.append(max(0, alerts_fired - 1) if has_alert else 0)
            if has_alert:
                detection_delays_all.append(first_alert_time)
                if cat == "masked_distant_screams":
                    detection_delays_masked.append(first_alert_time)

            if dur < 1.0:
                short_events_total += 1
                if has_alert:
                    short_events_detected += 1
                    detection_delays_short.append(first_alert_time)
            else:
                if has_alert:
                    detection_delays_sustained.append(first_alert_time)

    preds = np.array(event_preds, dtype=int)
    labels = np.array(event_labels, dtype=int)
    categories = np.array(event_categories)
    groups = np.array(event_groups)

    pos_mask = (labels == 1)
    neg_mask = (labels == 0)
    shout_mask = (categories == "shouting_and_speech")

    rec = float(np.mean(preds[pos_mask])) if np.sum(pos_mask) > 0 else 0.0
    fpr = float(np.mean(preds[neg_mask])) if np.sum(neg_mask) > 0 else 0.0
    shout_fpr = float(np.mean(preds[shout_mask])) if np.sum(shout_mask) > 0 else 0.0

    p, r, f1, _ = precision_recall_fscore_support(labels, preds, average="binary", zero_division=0)

    short_rec = float(short_events_detected / short_events_total) if short_events_total > 0 else 1.0
    avg_dupes = float(np.mean(duplicate_counts)) if duplicate_counts else 0.0

    # Operational false alerts per hour (assumed 1800 negative audio events per hour)
    hourly_fa = round(fpr * 1800.0, 1)

    return {
        "event_recall": rec,
        "event_fpr": fpr,
        "event_shout_fpr": shout_fpr,
        "precision": float(p),
        "f1": float(f1),
        "short_event_recall": short_rec,
        "short_events_total": short_events_total,
        "short_events_detected": short_events_detected,
        "avg_duplicate_alerts": avg_dupes,
        "hourly_false_alerts": hourly_fa,
        "median_delay_all": float(np.median(detection_delays_all)) if detection_delays_all else 0.0,
        "p95_delay_all": float(np.percentile(detection_delays_all, 95)) if detection_delays_all else 0.0,
        "median_delay_short": float(np.median(detection_delays_short)) if detection_delays_short else 0.0,
        "median_delay_sustained": float(np.median(detection_delays_sustained)) if detection_delays_sustained else 0.0,
        "median_delay_masked": float(np.median(detection_delays_masked)) if detection_delays_masked else 0.0,
        "preds": preds,
        "labels": labels,
        "categories": categories,
        "groups": groups,
    }


def run_event_logic_experiment():
    logger.info("=================================================================")
    logger.info("STAGE 8.9.13: DUAL-PATH EVENT BOUNDARY LOGIC RESEARCH")
    logger.info("=================================================================")

    # 1. Load dataset probability cache
    cache = np.load(CACHE_PATH, allow_pickle=True)
    val_seqs = cache["val_seqs"].item()
    test_seqs = cache["test_seqs"].item()
    logger.info(f"Loaded probability cache: {len(val_seqs)} validation and {len(test_seqs)} test sequences.")

    # 2. Define Experimental State Machine Policies
    # We test on Model D_v4 (Edge-Ready, 18.18ms latency) and Model H_v5_SNR
    candidate_definitions = [
        # Baselines
        {
            "id": "D_v4_Single_Window_Base",
            "classifier": "D_v4",
            "prob_key": "probs_d",
            "type": "Single_Window",
            "param_grid": [{"threshold": round(t, 2)} for t in np.arange(0.30, 0.92, 0.04)],
            "factory": lambda p: SingleWindowPolicy(threshold=p["threshold"]),
        },
        {
            "id": "D_v4_Consecutive_2_Base",
            "classifier": "D_v4",
            "prob_key": "probs_d",
            "type": "Consecutive_2",
            "param_grid": [{"threshold": round(t, 2), "consecutive_required": 2} for t in np.arange(0.30, 0.90, 0.04)],
            "factory": lambda p: ConsecutivePersistencePolicy(consecutive_required=p["consecutive_required"], threshold=p["threshold"]),
        },
        {
            "id": "D_v4_Hysteresis_Cooldown_Base",
            "classifier": "D_v4",
            "prob_key": "probs_d",
            "type": "Hysteresis_Cooldown",
            "param_grid": [{"tau_high": round(t, 2), "tau_low": round(t * 0.5, 2)} for t in np.arange(0.30, 0.90, 0.04)],
            "factory": lambda p: HysteresisCooldownPolicy(tau_high=p["tau_high"], tau_low=p["tau_low"]),
        },
        # Dual-Path Policies
        {
            "id": "D_v4_DualPath_Balanced",
            "classifier": "D_v4",
            "prob_key": "probs_d",
            "type": "DualPath_Balanced",
            "param_grid": [
                {"tau_fast": round(tf, 2), "tau_sustained": round(ts, 2), "tau_release": round(ts * 0.5, 2), "sustained_confirm_hops": 2, "cooldown_hops": 6}
                for tf in [0.75, 0.80, 0.85, 0.90]
                for ts in [0.45, 0.55, 0.65, 0.70]
                if tf > ts
            ],
            "factory": lambda p: DualPathEventStateMachine(
                tau_fast=p["tau_fast"],
                tau_sustained=p["tau_sustained"],
                tau_release=p["tau_release"],
                sustained_confirm_hops=p["sustained_confirm_hops"],
                cooldown_hops=p["cooldown_hops"],
                name="DualPath_Balanced",
            ),
        },
        {
            "id": "D_v4_DualPath_ShortEventPrioritized",
            "classifier": "D_v4",
            "prob_key": "probs_d",
            "type": "DualPath_ShortPrioritized",
            "param_grid": [
                {"tau_fast": round(tf, 2), "tau_sustained": round(ts, 2), "tau_release": round(ts * 0.4, 2), "sustained_confirm_hops": 2, "cooldown_hops": 4}
                for tf in [0.65, 0.70, 0.75, 0.80]
                for ts in [0.40, 0.50, 0.60]
                if tf > ts
            ],
            "factory": lambda p: DualPathEventStateMachine(
                tau_fast=p["tau_fast"],
                tau_sustained=p["tau_sustained"],
                tau_release=p["tau_release"],
                sustained_confirm_hops=p["sustained_confirm_hops"],
                cooldown_hops=p["cooldown_hops"],
                name="DualPath_ShortPrioritized",
            ),
        },
        {
            "id": "D_v4_DualPath_HighConfidence",
            "classifier": "D_v4",
            "prob_key": "probs_d",
            "type": "DualPath_HighConfidence",
            "param_grid": [
                {"tau_fast": round(tf, 2), "tau_sustained": round(ts, 2), "tau_release": round(ts * 0.5, 2), "sustained_confirm_hops": 3, "cooldown_hops": 8}
                for tf in [0.85, 0.90, 0.95]
                for ts in [0.60, 0.70, 0.75]
                if tf > ts
            ],
            "factory": lambda p: DualPathEventStateMachine(
                tau_fast=p["tau_fast"],
                tau_sustained=p["tau_sustained"],
                tau_release=p["tau_release"],
                sustained_confirm_hops=p["sustained_confirm_hops"],
                cooldown_hops=p["cooldown_hops"],
                name="DualPath_HighConfidence",
            ),
        },
        # Model H_v5_SNR Dual-Path for Comparison
        {
            "id": "H_v5_DualPath_Balanced",
            "classifier": "H_v5_SNR",
            "prob_key": "probs_hv5",
            "type": "DualPath_Balanced",
            "param_grid": [
                {"tau_fast": round(tf, 2), "tau_sustained": round(ts, 2), "tau_release": round(ts * 0.5, 2), "sustained_confirm_hops": 2, "cooldown_hops": 6}
                for tf in [0.70, 0.80, 0.85]
                for ts in [0.35, 0.45, 0.55]
                if tf > ts
            ],
            "factory": lambda p: DualPathEventStateMachine(
                tau_fast=p["tau_fast"],
                tau_sustained=p["tau_sustained"],
                tau_release=p["tau_release"],
                sustained_confirm_hops=p["sustained_confirm_hops"],
                cooldown_hops=p["cooldown_hops"],
                name="DualPath_Balanced",
            ),
        },
    ]

    validation_summary_records = []
    locked_configs = {}

    logger.info("\n--- Phase 1: Validation Parameter Search & Feasibility Audit ---")

    for cdef in candidate_definitions:
        cid = cdef["id"]
        prob_key = cdef["prob_key"]
        param_grid = cdef["param_grid"]
        factory = cdef["factory"]

        best_params = None
        best_f1 = -1.0
        best_metrics = None
        is_feasible = False

        # First search for feasible parameter sets (Rec >= 96% AND FPR <= 5%)
        for pset in param_grid:
            fn = lambda: factory(pset)
            m = evaluate_state_machine_on_dataset(fn, val_seqs, prob_key=prob_key)
            if m["event_recall"] >= 0.96 and m["event_fpr"] <= 0.05:
                is_feasible = True
                if m["f1"] > best_f1:
                    best_f1 = m["f1"]
                    best_params = pset
                    best_metrics = m

        # If none feasible, find best overall F1 trade-off
        if not is_feasible:
            for pset in param_grid:
                fn = lambda: factory(pset)
                m = evaluate_state_machine_on_dataset(fn, val_seqs, prob_key=prob_key)
                if m["f1"] > best_f1:
                    best_f1 = m["f1"]
                    best_params = pset
                    best_metrics = m

        locked_configs[cid] = {
            "id": cid,
            "classifier": cdef["classifier"],
            "type": cdef["type"],
            "is_feasible": is_feasible,
            "locked_params": best_params,
            "val_recall_pct": round(best_metrics["event_recall"] * 100.0, 2),
            "val_short_recall_pct": round(best_metrics["short_event_recall"] * 100.0, 2),
            "val_fpr_pct": round(best_metrics["event_fpr"] * 100.0, 2),
            "val_shout_fpr_pct": round(best_metrics["event_shout_fpr"] * 100.0, 2),
            "val_f1": round(best_metrics["f1"], 4),
            "val_median_delay_sec": round(best_metrics["median_delay_all"], 2),
            "val_avg_dupes": round(best_metrics["avg_duplicate_alerts"], 2),
            "val_hourly_fa": best_metrics["hourly_false_alerts"],
        }

        validation_summary_records.append({
            "candidate_id": cid,
            "classifier": cdef["classifier"],
            "policy_type": cdef["type"],
            "feasibility_status": "FEASIBLE" if is_feasible else "INFEASIBLE",
            "locked_parameters": str(best_params),
            "val_event_recall_pct": round(best_metrics["event_recall"] * 100.0, 2),
            "val_short_scream_recall_pct": round(best_metrics["short_event_recall"] * 100.0, 2),
            "val_event_fpr_pct": round(best_metrics["event_fpr"] * 100.0, 2),
            "val_shouted_speech_fpr_pct": round(best_metrics["event_shout_fpr"] * 100.0, 2),
            "val_f1_score": round(best_metrics["f1"], 4),
            "val_median_delay_sec": round(best_metrics["median_delay_all"], 2),
            "val_duplicate_alerts_per_event": round(best_metrics["avg_duplicate_alerts"], 2),
            "val_hourly_false_alerts": best_metrics["hourly_false_alerts"],
        })

        logger.info(
            f"Validation Candidate: {cid:<32} | Status: {validation_summary_records[-1]['feasibility_status']:<10} | "
            f"Rec: {best_metrics['event_recall']*100:.1f}% | Short: {best_metrics['short_event_recall']*100:.1f}% | "
            f"FPR: {best_metrics['event_fpr']*100:.1f}% | Shout: {best_metrics['event_shout_fpr']*100:.1f}%"
        )

    # Save validation records
    with open(STAGE13_DIR / "experiment_configurations.json", "w", encoding="utf-8") as f:
        json.dump(locked_configs, f, indent=2)

    val_csv = STAGE13_DIR / "temporal_policy_validation_results.csv"
    with open(val_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(validation_summary_records[0].keys()))
        writer.writeheader()
        writer.writerows(validation_summary_records)

    # 3. Phase 2: Single-Shot Evaluation on Held-Out Test Cohort (N=307)
    logger.info("\n--- Phase 2: Single-Shot Evaluation on Held-Out Test Split (N=307) ---")

    test_results_records = []
    delay_analysis_records = []

    # Baseline for McNemar
    baseline_preds = None

    for cdef in candidate_definitions:
        cid = cdef["id"]
        prob_key = cdef["prob_key"]
        factory = cdef["factory"]
        locked_p = locked_configs[cid]["locked_params"]

        fn = lambda: factory(locked_p)
        eval_res = evaluate_state_machine_on_dataset(fn, test_seqs, prob_key=prob_key)

        preds = eval_res["preds"]
        labels = eval_res["labels"]
        groups = eval_res["groups"]
        cats = eval_res["categories"]

        if cid == "D_v4_Single_Window_Base":
            baseline_preds = preds

        # Source-group cluster bootstrap for 95% CIs
        unique_groups = np.unique(groups)
        n_groups = len(unique_groups)
        np.random.seed(42)
        group_to_indices = {g: np.where(groups == g)[0] for g in unique_groups}

        boot_recs, boot_fprs = [], []
        for _ in range(1000):
            resampled = np.random.choice(unique_groups, size=n_groups, replace=True)
            idx_list = []
            for g in resampled:
                idx_list.extend(group_to_indices[g])
            sample_idx = np.array(idx_list, dtype=int)

            b_y = labels[sample_idx]
            b_p = preds[sample_idx]
            b_pos = (b_y == 1)
            b_neg = (b_y == 0)
            if np.sum(b_pos) > 0:
                boot_recs.append(float(np.mean(b_p[b_pos])))
            if np.sum(b_neg) > 0:
                boot_fprs.append(float(np.mean(b_p[b_neg])))

        ci_rec_low, ci_rec_high = np.percentile(boot_recs, [2.5, 97.5])
        ci_fpr_low, ci_fpr_high = np.percentile(boot_fprs, [2.5, 97.5])

        # Paired McNemar Test vs D_v4_Single_Window_Base
        if baseline_preds is not None:
            base_correct = (baseline_preds == labels)
            cand_correct = (preds == labels)
            b = int(np.sum(base_correct & ~cand_correct))
            c = int(np.sum(~base_correct & cand_correct))
            mcnemar_stat = (abs(b - c) - 1.0) ** 2 / max(1e-5, (b + c))
            mcnemar_p = float(stats.chi2.sf(mcnemar_stat, df=1))
        else:
            mcnemar_stat, mcnemar_p = 0.0, 1.0

        rec_pct = eval_res["event_recall"] * 100.0
        fpr_pct = eval_res["event_fpr"] * 100.0
        shout_pct = eval_res["event_shout_fpr"] * 100.0

        gate1 = (rec_pct >= 96.0)
        gate2 = (fpr_pct <= 5.0)
        gate3 = (shout_pct <= 15.0)
        all_gates_pass = bool(gate1 and gate2 and gate3)

        test_results_records.append({
            "candidate_id": cid,
            "classifier": cdef["classifier"],
            "policy_type": cdef["type"],
            "parameters": str(locked_p),
            "event_recall_pct": round(rec_pct, 2),
            "recall_95_ci": f"[{ci_rec_low*100:.1f}%, {ci_rec_high*100:.1f}%]",
            "short_scream_recall_pct": round(eval_res["short_event_recall"] * 100.0, 2),
            "short_screams_detected_vs_total": f"{eval_res['short_events_detected']}/{eval_res['short_events_total']}",
            "event_fpr_pct": round(fpr_pct, 2),
            "fpr_95_ci": f"[{ci_fpr_low*100:.1f}%, {ci_fpr_high*100:.1f}%]",
            "shouted_speech_fpr_pct": round(shout_pct, 2),
            "precision": round(eval_res["precision"], 4),
            "f1_score": round(eval_res["f1"], 4),
            "median_delay_sec": round(eval_res["median_delay_all"], 2),
            "p95_delay_sec": round(eval_res["p95_delay_all"], 2),
            "duplicate_alerts_per_event": round(eval_res["avg_duplicate_alerts"], 2),
            "hourly_false_alerts": eval_res["hourly_false_alerts"],
            "mcnemar_chi2": round(mcnemar_stat, 4),
            "mcnemar_p_value": round(mcnemar_p, 4),
            "gate_recall_96": "PASS" if gate1 else "FAIL",
            "gate_fpr_5": "PASS" if gate2 else "FAIL",
            "gate_shout_15": "PASS" if gate3 else "FAIL",
            "final_acceptance_verdict": "CERTIFIED" if all_gates_pass else "NOT CERTIFIED",
        })

        delay_analysis_records.append({
            "candidate_id": cid,
            "median_delay_all_screams_sec": round(eval_res["median_delay_all"], 2),
            "p95_delay_all_screams_sec": round(eval_res["p95_delay_all"], 2),
            "median_delay_brief_screams_sec": round(eval_res["median_delay_short"], 2),
            "median_delay_sustained_screams_sec": round(eval_res["median_delay_sustained"], 2),
            "median_delay_masked_screams_sec": round(eval_res["median_delay_masked"], 2),
            "short_scream_preservation_status": "PRESERVED" if eval_res["short_event_recall"] > 0.0 else "SUPPRESSED (BLIND)",
        })

        logger.info(
            f"Test Result: {cid:<32} | Rec: {rec_pct:>5.1f}% [{ci_rec_low*100:.1f}%, {ci_rec_high*100:.1f}%] | "
            f"Short Rec: {eval_res['short_event_recall']*100:>5.1f}% | "
            f"FPR: {fpr_pct:>4.1f}% [{ci_fpr_low*100:.1f}%, {ci_fpr_high*100:.1f}%] | "
            f"Shout: {shout_pct:>4.1f}% | Delay: {eval_res['median_delay_all']:.1f}s | "
            f"Dupes: {eval_res['avg_duplicate_alerts']:.2f} | Verdict: {test_results_records[-1]['final_acceptance_verdict']}"
        )

    # Save test results
    test_csv = STAGE13_DIR / "event_level_test_results.csv"
    with open(test_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(test_results_records[0].keys()))
        writer.writeheader()
        writer.writerows(test_results_records)

    delay_csv = STAGE13_DIR / "detection_delay_analysis.csv"
    with open(delay_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(delay_analysis_records[0].keys()))
        writer.writeheader()
        writer.writerows(delay_analysis_records)

    logger.info(f"Test evaluation results saved to {test_csv.name} and {delay_csv.name}.")
    return test_results_records


if __name__ == "__main__":
    run_event_logic_experiment()
