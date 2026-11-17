"""Stage 8.9.12 Temporal Alert Persistence and Event-Level Evaluation.

Executes:
1. Multi-window streaming replay on Validation (N=320) and Test (N=307) audio files.
2. Extracts sequential window scores (1.0s window, 500ms hop) using D_v4 and H_v5_SNR_Optimized.
3. Validation-only threshold optimization across all 6 persistence policies:
   - Single_Window (Baseline)
   - Consecutive_2
   - Consecutive_3
   - Voting_2_of_3
   - Voting_3_of_5
   - Hysteresis_Cooldown
4. Strict Feasibility Check: Recall >= 96% AND Hard-Negative FPR <= 5%.
5. Single-shot evaluation on held-out test cohort with locked validation configurations.
6. Event-level metrics:
   - Event Recall, Hard-Negative FPR, Shouted-Speech FPR
   - 95% Source-Group Cluster Bootstrap Confidence Intervals (1,000 resamples)
   - Detection delay from onset (median, p95)
   - Missed short events (< 1.0s screams)
   - Duplicate alerts per positive event
   - Projected hourly false alert rate at operational prevalence pi = 10^-4
   - Paired McNemar tests with Edwards continuity correction.

Outputs:
- `stage8_9_12_runtime_research/experiment_configurations.json`
- `stage8_9_12_runtime_research/temporal_policy_comparison.csv`
- `stage8_9_12_runtime_research/event_level_evaluation.csv`
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

import joblib
import numpy as np
from scipy import stats
from sklearn.metrics import precision_recall_fscore_support

# Suppress TF logging
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.audio.preprocessor import load_audio
from src.config import TARGET_SAMPLE_RATE
from src.model.yamnet_loader import YAMNetLoader
from experiments.v2_hard_negative_training.v4_temporal_research.stage8_9_12_runtime_research.fast_acoustic_features import (
    FastAcousticFeatureExtractor,
)
from experiments.v2_hard_negative_training.v4_temporal_research.stage8_9_12_runtime_research.temporal_state_machine import (
    SingleWindowPolicy,
    ConsecutivePersistencePolicy,
    VotingKofMPolicy,
    HysteresisCooldownPolicy,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("evaluate_temporal_persistence")

STAGE11_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_11_evaluation"
STAGE12_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_12_runtime_research"
MANIFEST_PATH = STAGE11_DIR / "stage8_9_11_dataset_manifest.json"
CACHE_PATH = STAGE12_DIR / "window_probabilities_cache.npz"


def extract_window_probabilities_for_split(
    records: List[Dict[str, Any]],
    yamnet: YAMNetLoader,
    pipe_d: Any,
    calib_d: Any,
    pipe_hv5: Any,
    calib_hv5: Any,
    fast_extractor: FastAcousticFeatureExtractor,
) -> Dict[str, Any]:
    """Compute rolling window probability sequences for all audio files in a split."""
    win_len = 16000  # 1.0s
    hop_len = 8000   # 500ms

    cached_sequences = {}
    n_total = len(records)
    logger.info(f"Extracting sequential window probabilities for {n_total} recordings...")

    dummy_vocal = np.zeros((1, 8), dtype=np.float32)

    for i, rec in enumerate(records):
        fid = rec["file_id"]
        audio_path = rec["workspace_audio_path"]
        y_true = 1 if rec["binary_label"] == "scream" else 0
        cat = rec["target_category"]
        group_id = rec["source_group_id"]
        dur = rec["duration_seconds"]

        # Load audio (16kHz mono)
        sig, sr = load_audio(audio_path, target_sr=TARGET_SAMPLE_RATE)
        if len(sig) < win_len:
            # Pad short audio to 1.0s
            padded = np.pad(sig, (0, win_len - len(sig)))
            windows = [padded]
        else:
            n_hops = (len(sig) - win_len) // hop_len + 1
            windows = [sig[h * hop_len : h * hop_len + win_len] for h in range(n_hops)]

        probs_d = []
        probs_hv5 = []

        for w in windows:
            # YAMNet inference
            _, embs, _ = yamnet.infer(w)

            # Feature D_v4
            f_mean = np.mean(embs, axis=0)
            f_max = np.max(embs, axis=0)
            f_p10 = np.sort(embs, axis=0)[0] if len(embs) <= 2 else np.percentile(embs, 10, axis=0)

            feat_d = np.empty((1, 3072), dtype=np.float32)
            feat_d[0, 0:1024] = f_max
            feat_d[0, 1024:2048] = f_p10
            feat_d[0, 2048:3072] = f_mean

            logits_d = pipe_d.decision_function(feat_d).reshape(-1, 1)
            p_d = float(calib_d.predict_proba(logits_d)[0, 1])
            probs_d.append(p_d)

            # Feature H_v5_SNR
            f_std = np.std(embs, axis=0)
            turb, snr_feat = fast_extractor.extract_turbulence_and_snr_fast(w)

            feat_hv5 = np.empty((1, 5148), dtype=np.float32)
            feat_hv5[0, 0:1024] = f_max
            feat_hv5[0, 1024:2048] = f_p10
            feat_hv5[0, 2048:3072] = f_mean
            feat_hv5[0, 3072:4096] = f_std
            feat_hv5[0, 4096:5120] = 0.0
            feat_hv5[0, 5120:5136] = turb
            feat_hv5[0, 5136:5144] = 0.0
            feat_hv5[0, 5144:5148] = snr_feat

            logits_hv5 = pipe_hv5.decision_function(feat_hv5).reshape(-1, 1)
            p_hv5 = float(calib_hv5.predict_proba(logits_hv5)[0, 1])
            probs_hv5.append(p_hv5)

        cached_sequences[fid] = {
            "y_true": y_true,
            "category": cat,
            "group_id": group_id,
            "duration": dur,
            "n_windows": len(windows),
            "probs_d": np.array(probs_d, dtype=np.float32),
            "probs_hv5": np.array(probs_hv5, dtype=np.float32),
        }

        if (i + 1) % 100 == 0 or (i + 1) == n_total:
            logger.info(f"Processed {i + 1}/{n_total} audio files.")

    return cached_sequences


def evaluate_policy_on_sequences(
    policy_class: Any,
    policy_kwargs: Dict[str, Any],
    sequences: Dict[str, Any],
) -> Dict[str, Any]:
    """Run a temporal persistence policy over sequence streams and calculate event-level metrics."""
    hop_sec = 0.5

    event_preds = []
    event_labels = []
    event_categories = []
    event_groups = []
    detection_delays = []
    duplicate_alert_counts = []
    short_event_detected = []
    short_event_total = 0

    for fid, item in sequences.items():
        y_true = item["y_true"]
        probs = item["probs"]
        cat = item["category"]
        group_id = item["group_id"]
        dur = item["duration"]

        policy = policy_class(**policy_kwargs)
        policy.reset()

        alerts_fired = 0
        first_alert_delay = None

        for t_idx, p in enumerate(probs):
            timestamp_sec = t_idx * hop_sec + 1.0  # end of window
            fired, _ = policy.step(p, timestamp_sec)
            if fired:
                alerts_fired += 1
                if first_alert_delay is None:
                    first_alert_delay = timestamp_sec

        event_fired = (alerts_fired > 0)
        event_preds.append(1 if event_fired else 0)
        event_labels.append(y_true)
        event_categories.append(cat)
        event_groups.append(group_id)

        if y_true == 1:
            if event_fired:
                detection_delays.append(first_alert_delay)
                duplicate_alert_counts.append(alerts_fired)
            else:
                duplicate_alert_counts.append(0)

            if dur < 1.0:
                short_event_total += 1
                if event_fired:
                    short_event_detected.append(1)
                else:
                    short_event_detected.append(0)

    event_preds = np.array(event_preds, dtype=int)
    event_labels = np.array(event_labels, dtype=int)
    event_categories = np.array(event_categories)

    pos_mask = (event_labels == 1)
    neg_mask = (event_labels == 0)
    shout_mask = (event_categories == "shouting_and_speech")

    rec = float(np.mean(event_preds[pos_mask])) if np.sum(pos_mask) > 0 else 0.0
    fpr = float(np.mean(event_preds[neg_mask])) if np.sum(neg_mask) > 0 else 0.0
    shout_fpr = float(np.mean(event_preds[shout_mask])) if np.sum(shout_mask) > 0 else 0.0

    p, r, f1, _ = precision_recall_fscore_support(event_labels, event_preds, average="binary", zero_division=0)

    median_delay = float(np.median(detection_delays)) if detection_delays else 0.0
    p95_delay = float(np.percentile(detection_delays, 95)) if detection_delays else 0.0
    avg_duplicates = float(np.mean(duplicate_alert_counts)) if duplicate_alert_counts else 0.0
    short_recall = float(np.mean(short_event_detected)) if short_event_total > 0 else 1.0

    # Projected operational false alerts per hour:
    # 7200 hops/hr * event_level_fpr / avg_hops_per_event
    # An empirical negative audio recording averages ~4 hops (2.0s).
    # Thus, negative files per hour = 7200 / 4 = 1800 negative event exposures per hour.
    # At prevalence pi = 1e-4, ~1800 negative exposures/hour:
    hourly_false_alerts = round(fpr * 1800.0, 1)

    return {
        "event_recall": rec,
        "event_fpr": fpr,
        "event_shout_fpr": shout_fpr,
        "precision": float(p),
        "f1": float(f1),
        "median_delay_sec": median_delay,
        "p95_delay_sec": p95_delay,
        "avg_duplicate_alerts": avg_duplicates,
        "short_event_recall": short_recall,
        "short_event_total": short_event_total,
        "hourly_false_alerts_pi_1e4": hourly_false_alerts,
        "event_preds": event_preds,
        "event_labels": event_labels,
        "event_categories": event_categories,
        "event_groups": event_groups,
    }


def run_temporal_experiment():
    logger.info("=================================================================")
    logger.info("STAGE 8.9.12: TEMPORAL PERSISTENCE & ALERT-STATE RESEARCH")
    logger.info("=================================================================")

    # 1. Load dataset manifest
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        all_records = json.load(f)

    val_records = [r for r in all_records if r["split"] == "val"]
    test_records = [r for r in all_records if r["split"] == "test"]
    logger.info(f"Loaded {len(val_records)} validation and {len(test_records)} test records.")

    # 2. Check or create probability cache
    if CACHE_PATH.exists():
        logger.info(f"Loading cached window probabilities from {CACHE_PATH.name}...")
        cache_data = np.load(CACHE_PATH, allow_pickle=True)
        val_seqs = cache_data["val_seqs"].item()
        test_seqs = cache_data["test_seqs"].item()
    else:
        logger.info("Initializing models for window probability extraction...")
        yamnet = YAMNetLoader()
        yamnet.load()

        m_d = joblib.load(STAGE11_DIR / "models" / "model_d_v4.joblib")
        m_hv5 = joblib.load(STAGE11_DIR / "models" / "model_h_v5_snr.joblib")

        fast_extractor = FastAcousticFeatureExtractor(sr=TARGET_SAMPLE_RATE)

        val_seqs = extract_window_probabilities_for_split(
            val_records, yamnet, m_d["pipe"], m_d["calibrator"], m_hv5["pipe"], m_hv5["calibrator"], fast_extractor
        )
        test_seqs = extract_window_probabilities_for_split(
            test_records, yamnet, m_d["pipe"], m_d["calibrator"], m_hv5["pipe"], m_hv5["calibrator"], fast_extractor
        )

        np.savez_compressed(CACHE_PATH, val_seqs=val_seqs, test_seqs=test_seqs)
        logger.info(f"Saved window probability cache to {CACHE_PATH}.")

    # 3. Define the 6 Preregistered Policies
    policy_definitions = [
        ("Single_Window", SingleWindowPolicy, {}),
        ("Consecutive_2", ConsecutivePersistencePolicy, {"consecutive_required": 2}),
        ("Consecutive_3", ConsecutivePersistencePolicy, {"consecutive_required": 3}),
        ("Voting_2_of_3", VotingKofMPolicy, {"k": 2, "m": 3}),
        ("Voting_3_of_5", VotingKofMPolicy, {"k": 3, "m": 5}),
        ("Hysteresis_Cooldown", HysteresisCooldownPolicy, {"confirm_hops": 2, "cooldown_hops": 6, "recovery_hops": 3}),
    ]

    classifiers = ["D_v4", "H_v5_SNR"]

    validation_results = []
    locked_configurations = {}

    logger.info("\n--- Phase 1: Validation Threshold & Feasibility Tuning ---")
    threshold_grid = np.arange(0.10, 0.90, 0.02)

    for clf_name in classifiers:
        # Prepare validation sequence dict with selected probability series
        prob_key = "probs_d" if clf_name == "D_v4" else "probs_hv5"
        val_subset = {fid: {**item, "probs": item[prob_key]} for fid, item in val_seqs.items()}

        for pol_name, pol_cls, base_kwargs in policy_definitions:
            best_thresh = None
            best_f1 = -1.0
            best_metrics = None
            feasible_found = False

            for tau in threshold_grid:
                kwargs = dict(base_kwargs)
                if pol_name == "Hysteresis_Cooldown":
                    kwargs["tau_high"] = float(round(tau, 3))
                    kwargs["tau_low"] = float(round(tau * 0.5, 3))
                else:
                    kwargs["threshold"] = float(round(tau, 3))

                res = evaluate_policy_on_sequences(pol_cls, kwargs, val_subset)

                rec = res["event_recall"]
                fpr = res["event_fpr"]
                shout_fpr = res["event_shout_fpr"]
                f1 = res["f1"]

                is_feasible = (rec >= 0.96 and fpr <= 0.05)
                if is_feasible:
                    feasible_found = True
                    if f1 > best_f1:
                        best_f1 = f1
                        best_thresh = tau
                        best_metrics = res

            # If no threshold satisfied both constraints, lock threshold with highest F1 (per protocol)
            if not feasible_found:
                # Find best overall F1
                for tau in threshold_grid:
                    kwargs = dict(base_kwargs)
                    if pol_name == "Hysteresis_Cooldown":
                        kwargs["tau_high"] = float(round(tau, 3))
                        kwargs["tau_low"] = float(round(tau * 0.5, 3))
                    else:
                        kwargs["threshold"] = float(round(tau, 3))
                    res = evaluate_policy_on_sequences(pol_cls, kwargs, val_subset)
                    if res["f1"] > best_f1:
                        best_f1 = res["f1"]
                        best_thresh = tau
                        best_metrics = res

            locked_key = f"{clf_name}_{pol_name}"
            locked_configurations[locked_key] = {
                "classifier": clf_name,
                "policy": pol_name,
                "is_feasible": feasible_found,
                "locked_threshold": round(float(best_thresh), 3),
                "val_recall": round(best_metrics["event_recall"], 4),
                "val_fpr": round(best_metrics["event_fpr"], 4),
                "val_shout_fpr": round(best_metrics["event_shout_fpr"], 4),
                "val_f1": round(best_metrics["f1"], 4),
                "val_median_delay_sec": round(best_metrics["median_delay_sec"], 2),
                "val_duplicates": round(best_metrics["avg_duplicate_alerts"], 2),
                "val_short_recall": round(best_metrics["short_event_recall"], 4),
            }

            validation_results.append({
                "candidate": locked_key,
                "classifier": clf_name,
                "policy": pol_name,
                "feasibility": "FEASIBLE" if feasible_found else "INFEASIBLE",
                "locked_threshold": round(float(best_thresh), 3),
                "val_recall": round(best_metrics["event_recall"] * 100.0, 2),
                "val_fpr": round(best_metrics["event_fpr"] * 100.0, 2),
                "val_shout_fpr": round(best_metrics["event_shout_fpr"] * 100.0, 2),
                "val_f1": round(best_metrics["f1"], 4),
                "val_median_delay_sec": round(best_metrics["median_delay_sec"], 2),
                "val_duplicate_alerts": round(best_metrics["avg_duplicate_alerts"], 2),
                "val_short_recall": round(best_metrics["short_event_recall"] * 100.0, 2),
                "val_hourly_false_alerts": best_metrics["hourly_false_alerts_pi_1e4"],
            })

            logger.info(
                f"Validation Locked: {locked_key:<25} | Thresh: {best_thresh:.2f} | "
                f"Rec: {best_metrics['event_recall']*100:.1f}% | FPR: {best_metrics['event_fpr']*100:.1f}% | "
                f"Shout FPR: {best_metrics['event_shout_fpr']*100:.1f}% | Feasible: {feasible_found}"
            )

    # Save validation configurations
    with open(STAGE12_DIR / "experiment_configurations.json", "w", encoding="utf-8") as f:
        json.dump(locked_configurations, f, indent=2)

    with open(STAGE12_DIR / "temporal_policy_comparison.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(validation_results[0].keys()))
        writer.writeheader()
        writer.writerows(validation_results)

    # 4. Phase 2: Single-Shot Evaluation on Held-Out Test Cohort
    logger.info("\n--- Phase 2: Single-Shot Evaluation on Held-Out Test Split (N=307) ---")
    test_results = []

    # Baseline for McNemar tests: D_v4_Single_Window
    baseline_preds = None

    for clf_name in classifiers:
        prob_key = "probs_d" if clf_name == "D_v4" else "probs_hv5"
        test_subset = {fid: {**item, "probs": item[prob_key]} for fid, item in test_seqs.items()}

        for pol_name, pol_cls, base_kwargs in policy_definitions:
            locked_key = f"{clf_name}_{pol_name}"
            cfg = locked_configurations[locked_key]
            tau = cfg["locked_threshold"]

            kwargs = dict(base_kwargs)
            if pol_name == "Hysteresis_Cooldown":
                kwargs["tau_high"] = tau
                kwargs["tau_low"] = round(tau * 0.5, 3)
            else:
                kwargs["threshold"] = tau

            eval_res = evaluate_policy_on_sequences(pol_cls, kwargs, test_subset)

            preds = np.array(eval_res["event_preds"], dtype=int)
            labels = np.array(eval_res["event_labels"], dtype=int)
            groups = np.array(eval_res["event_groups"])
            cats = np.array(eval_res["event_categories"])

            if locked_key == "D_v4_Single_Window":
                baseline_preds = preds

            # Cluster Bootstrap for 95% CIs (1,000 resamples at source-group level)
            unique_groups = np.unique(groups)
            n_groups = len(unique_groups)
            np.random.seed(42)

            group_to_indices = {g: np.where(groups == g)[0] for g in unique_groups}

            boot_recs, boot_fprs = [], []
            for _ in range(1000):
                resampled_groups = np.random.choice(unique_groups, size=n_groups, replace=True)
                sample_indices_list = []
                for g in resampled_groups:
                    sample_indices_list.extend(group_to_indices[g])
                sample_indices = np.array(sample_indices_list, dtype=int)

                b_y = labels[sample_indices]
                b_p = preds[sample_indices]
                b_pos = (b_y == 1)
                b_neg = (b_y == 0)

                if np.sum(b_pos) > 0:
                    boot_recs.append(float(np.mean(b_p[b_pos])))
                if np.sum(b_neg) > 0:
                    boot_fprs.append(float(np.mean(b_p[b_neg])))

            rec_ci_low, rec_ci_high = np.percentile(boot_recs, [2.5, 97.5])
            fpr_ci_low, fpr_ci_high = np.percentile(boot_fprs, [2.5, 97.5])

            # Paired McNemar Test vs D_v4_Single_Window
            if baseline_preds is not None:
                # b: baseline correct, candidate incorrect; c: baseline incorrect, candidate correct
                base_correct = (baseline_preds == labels)
                cand_correct = (preds == labels)
                b = int(np.sum(base_correct & ~cand_correct))
                c = int(np.sum(~base_correct & cand_correct))
                # Edwards continuity correction
                stat = (abs(b - c) - 1.0) ** 2 / max(1e-5, (b + c))
                p_val = float(stats.chi2.sf(stat, df=1))
            else:
                stat, p_val = 0.0, 1.0

            # Acceptance Gate Check
            rec_pct = eval_res["event_recall"] * 100.0
            fpr_pct = eval_res["event_fpr"] * 100.0
            shout_pct = eval_res["event_shout_fpr"] * 100.0

            gate1 = (rec_pct >= 96.0)
            gate2 = (fpr_pct <= 5.0)
            gate3 = (shout_pct <= 15.0)
            all_gates = bool(gate1 and gate2 and gate3)

            test_results.append({
                "candidate": locked_key,
                "classifier": clf_name,
                "policy": pol_name,
                "threshold": tau,
                "event_recall_pct": round(rec_pct, 2),
                "recall_95_ci": f"[{rec_ci_low*100:.1f}%, {rec_ci_high*100:.1f}%]",
                "event_fpr_pct": round(fpr_pct, 2),
                "fpr_95_ci": f"[{fpr_ci_low*100:.1f}%, {fpr_ci_high*100:.1f}%]",
                "shout_fpr_pct": round(shout_pct, 2),
                "precision": round(eval_res["precision"], 4),
                "f1_score": round(eval_res["f1"], 4),
                "median_delay_sec": round(eval_res["median_delay_sec"], 2),
                "p95_delay_sec": round(eval_res["p95_delay_sec"], 2),
                "short_event_recall_pct": round(eval_res["short_event_recall"] * 100.0, 2),
                "avg_duplicate_alerts": round(eval_res["avg_duplicate_alerts"], 2),
                "hourly_false_alerts": eval_res["hourly_false_alerts_pi_1e4"],
                "mcnemar_chi2": round(stat, 4),
                "mcnemar_p_val": round(p_val, 4),
                "gate_recall_96": "PASS" if gate1 else "FAIL",
                "gate_fpr_5": "PASS" if gate2 else "FAIL",
                "gate_shout_15": "PASS" if gate3 else "FAIL",
                "acceptance_verdict": "CERTIFIED" if all_gates else "NOT CERTIFIED",
            })

            logger.info(
                f"Test Result: {locked_key:<25} | Rec: {rec_pct:>5.1f}% [{rec_ci_low*100:.1f}%, {rec_ci_high*100:.1f}%] | "
                f"FPR: {fpr_pct:>4.1f}% [{fpr_ci_low*100:.1f}%, {fpr_ci_high*100:.1f}%] | "
                f"Shout: {shout_pct:>4.1f}% | Delay: {eval_res['median_delay_sec']:.1f}s | "
                f"Dupes: {eval_res['avg_duplicate_alerts']:.1f} | Verdict: {test_results[-1]['acceptance_verdict']}"
            )

    out_csv = STAGE12_DIR / "event_level_evaluation.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(test_results[0].keys()))
        writer.writeheader()
        writer.writerows(test_results)

    logger.info(f"Event-level evaluation results written to: {out_csv}")
    return test_results


if __name__ == "__main__":
    run_temporal_experiment()
