#!/usr/bin/env python3
"""
STAGE 8.9.63 — Track E: False-Positive-Controlled Temporal Aggregation Experiments
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import csv
import json
import math
import sys
import time
from pathlib import Path
import numpy as np
import torch

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE54_DIR = BACKEND_DIR / "research" / "stage_8_9_54"
STAGE61_DIR = BACKEND_DIR / "research" / "stage_8_9_61"
STAGE63_DIR = BACKEND_DIR / "research" / "stage_8_9_63"

class ResearchDualHeadClassifier(torch.nn.Module):
    def __init__(self, sem_dim=1024, acoust_dim=6, subband_dim=11):
        super().__init__()
        self.sem_proj = torch.nn.Sequential(torch.nn.Linear(sem_dim, 128), torch.nn.ReLU(), torch.nn.Dropout(0.20))
        self.acoust_proj = torch.nn.Sequential(torch.nn.Linear(acoust_dim * 2 + subband_dim, 64), torch.nn.ReLU(), torch.nn.Dropout(0.15))
        self.gate = torch.nn.Sequential(torch.nn.Linear(128 + 64, 32), torch.nn.Sigmoid())
        self.classifier = torch.nn.Sequential(torch.nn.Linear(128 + 64, 64), torch.nn.ReLU(), torch.nn.Linear(64, 1))

    def forward(self, x_sem, x_acoust, mask_acoust, x_subband):
        z_s = self.sem_proj(x_sem)
        acoust_combined = torch.cat([torch.nan_to_num(x_acoust, nan=0.0), mask_acoust, x_subband], dim=-1)
        z_a = self.acoust_proj(acoust_combined)
        fused = torch.cat([z_s, z_a], dim=-1)
        return self.classifier(fused).squeeze(-1)

def load_e1_model():
    ckpt_path = STAGE54_DIR / "training" / "candidate_e_v954_weighted.pt"
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    model = ResearchDualHeadClassifier()
    model.load_state_dict(ckpt)
    model.eval()
    return model

def evaluate_method_decisions(probs: np.ndarray, method_name: str) -> tuple[int, int, int, float]:
    """
    Evaluates temporal aggregation methods.
    Returns: (triggered, raw_triggers, post_triggers, detection_delay_ms)
    """
    if len(probs) == 0:
        return 0, 0, 0, 0.0

    raw_triggers = int(np.sum(probs >= 0.5000))
    triggered = 0
    post_triggers = 0
    delay_ms = 0.0

    if method_name == "Method_Baseline_Any_Window":
        idxs = np.where(probs >= 0.5000)[0]
        post_triggers = len(idxs)
        if len(idxs) > 0:
            triggered = 1
            delay_ms = float(idxs[0] * 50.0)

    elif method_name == "Method_A_Consecutive_Evidence_K2":
        # Requires 2 consecutive windows >= 0.50 (100 ms of sustained progression)
        consec_idxs = []
        for i in range(len(probs) - 1):
            if probs[i] >= 0.5000 and probs[i+1] >= 0.5000:
                consec_idxs.append(i + 1)
        post_triggers = len(consec_idxs)
        if len(consec_idxs) > 0:
            triggered = 1
            delay_ms = float(consec_idxs[0] * 50.0)

    elif method_name == "Method_B_Bounded_EMA_0.30":
        alpha = 0.30
        thresh = 0.4500
        s = 0.0
        ema_triggers = []
        for i, p in enumerate(probs):
            s = alpha * p + (1.0 - alpha) * s
            if s >= thresh:
                ema_triggers.append(i)
        post_triggers = len(ema_triggers)
        if len(ema_triggers) > 0:
            triggered = 1
            delay_ms = float(ema_triggers[0] * 50.0)

    elif method_name == "Method_C_Peak_With_Corroboration":
        # Peak >= 0.70 OR (>= 0.50 with neighboring window >= 0.45 in 200ms context)
        corrob_idxs = []
        for i, p in enumerate(probs):
            if p >= 0.7000:
                corrob_idxs.append(i)
            elif p >= 0.5000:
                c_win = probs[max(0, i-2) : min(len(probs), i+3)]
                if np.sum(c_win >= 0.4500) >= 2:
                    corrob_idxs.append(i)
        post_triggers = len(corrob_idxs)
        if len(corrob_idxs) > 0:
            triggered = 1
            delay_ms = float(corrob_idxs[0] * 50.0)

    elif method_name == "Method_D_Event_Merging":
        # Merge adjacent windows with gap <= 4 hops (200 ms) into unified events
        events = []
        in_event = False
        for i, p in enumerate(probs):
            if p >= 0.5000:
                if not in_event:
                    events.append(i)
                    in_event = True
            else:
                in_event = False
        post_triggers = len(events)
        if len(events) > 0:
            triggered = 1
            delay_ms = float(events[0] * 50.0)

    elif method_name == "Method_E_Refractory_Holdoff_500ms":
        # 500 ms lockout (10 hops at 50ms) following an alert
        lockout = 0
        ref_triggers = []
        for i, p in enumerate(probs):
            if lockout > 0:
                lockout -= 1
                continue
            if p >= 0.5000:
                ref_triggers.append(i)
                lockout = 10
        post_triggers = len(ref_triggers)
        if len(ref_triggers) > 0:
            triggered = 1
            delay_ms = float(ref_triggers[0] * 50.0)

    return triggered, raw_triggers, post_triggers, delay_ms

def main():
    print("=" * 80)
    print("STAGE 8.9.63 — TRACK E: TEMPORAL AGGREGATION EXPERIMENTS")
    print("=" * 80)

    npz_path = STAGE61_DIR / "rolling_window_experiments" / "dev_rolling_features.npz"
    assert npz_path.exists(), f"Missing {npz_path}"
    data_dict = np.load(npz_path, allow_pickle=True)["data"].item()
    e1_model = load_e1_model()

    rec_list = []
    print(f"Extracting rolling probabilities for {len(data_dict)} development files...")
    with torch.no_grad():
        for rid, item in data_dict.items():
            sem_t = torch.from_numpy(item["sem"]).float()
            acoust_t = torch.from_numpy(item["acoust"]).float()
            mask_t = torch.from_numpy(item["mask"]).float()
            subband_t = torch.from_numpy(item["subband"]).float()

            logits = e1_model(sem_t, acoust_t, mask_t, subband_t)
            probs = torch.sigmoid(logits).cpu().numpy()
            if probs.ndim == 0:
                probs = np.array([float(probs)])

            rec_list.append({
                "recording_id": rid,
                "binary_label": int(item["binary_label"]),
                "duration_seconds": float(item["duration"]),
                "target_category": item["target_category"],
                "subcategory": item["subcategory"],
                "window_probs": probs
            })

    n_pos = sum(1 for r in rec_list if r["binary_label"] == 1)
    n_neg = sum(1 for r in rec_list if r["binary_label"] == 0)
    n_sust = sum(1 for r in rec_list if r["binary_label"] == 1 and r["duration_seconds"] >= 1.0)
    n_short = sum(1 for r in rec_list if r["binary_label"] == 1 and r["duration_seconds"] < 1.0)
    n_shout = sum(1 for r in rec_list if r["target_category"] == "shouted_speech")

    methods = [
        ("Method_Baseline_Any_Window", "Baseline (Any Window >= 0.50)"),
        ("Method_A_Consecutive_Evidence_K2", "Method A: Consecutive Evidence (K=2, 100 ms sustained)"),
        ("Method_B_Bounded_EMA_0.30", "Method B: Bounded EMA (alpha=0.30, thresh=0.45)"),
        ("Method_C_Peak_With_Corroboration", "Method C: Peak with Corroboration (Peak >= 0.70)"),
        ("Method_D_Event_Merging", "Method D: Event-Level Merging (<200ms gap)"),
        ("Method_E_Refractory_Holdoff_500ms", "Method E: Refractory Holdoff (500 ms lockout)")
    ]

    metrics = []
    category_breakdown = []

    for mid, desc in methods:
        tp = fn = fp = tn = 0
        sust_tp = short_tp = shout_fp = 0
        delays = []
        total_raw = 0
        total_post = 0

        # Category FP counters
        cat_counts = {"shouted_speech": [0, 0], "referee_whistle": [0, 0], "cheering": [0, 0], "infant_crying": [0, 0], "environmental_sound": [0, 0]}

        for r in rec_list:
            dec, raw_trig, post_trig, delay = evaluate_method_decisions(r["window_probs"], mid)
            total_raw += raw_trig
            total_post += post_trig
            if dec == 1:
                delays.append(delay)

            y = r["binary_label"]
            dur = r["duration_seconds"]
            cat = r["target_category"]

            if y == 1:
                if dec == 1:
                    tp += 1
                    if dur >= 1.0:
                        sust_tp += 1
                    else:
                        short_tp += 1
                else:
                    fn += 1
            else:
                if cat in cat_counts:
                    cat_counts[cat][1] += 1
                if dec == 1:
                    fp += 1
                    if cat in cat_counts:
                        cat_counts[cat][0] += 1
                    if cat == "shouted_speech":
                        shout_fp += 1
                else:
                    tn += 1

        rec = tp / n_pos
        rec_sust = sust_tp / n_sust
        rec_short = short_tp / n_short if n_short > 0 else 0.0
        fpr = fp / n_neg
        fpr_shout = shout_fp / n_shout if n_shout > 0 else 0.0
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
        mean_delay = float(np.mean(delays)) if len(delays) > 0 else 0.0
        suppressed = max(0, total_raw - total_post)

        metrics.append({
            "method_id": mid,
            "description": desc,
            "overall_recall": round(rec, 4),
            "sustained_recall": round(rec_sust, 4),
            "short_scream_recall": round(rec_short, 4),
            "hard_negative_fpr": round(fpr, 4),
            "shouted_speech_fpr": round(fpr_shout, 4),
            "precision": round(prec, 4),
            "f1": round(f1, 4),
            "mean_detection_delay_ms": round(mean_delay, 1),
            "raw_triggers": total_raw,
            "post_aggregation_triggers": total_post,
            "suppressed_triggers": suppressed
        })

        for cat, counts in cat_counts.items():
            if counts[1] > 0:
                category_breakdown.append({
                    "method_id": mid,
                    "sound_category": cat,
                    "false_alarms": counts[0],
                    "total_category_files": counts[1],
                    "category_fpr": round(counts[0] / counts[1], 4)
                })

        print(f"\n[{desc}]")
        print(f"  Recall: {rec*100:.2f}% (Sustained={rec_sust*100:.2f}%, Short={rec_short*100:.2f}%)")
        print(f"  Hard-Neg FPR: {fpr*100:.2f}% (Shouted={fpr_shout*100:.2f}%) | F1: {f1*100:.2f}%")
        print(f"  Triggers: Raw={total_raw} -> Post={total_post} (Suppressed={suppressed}) | Mean Delay: {mean_delay:.1f} ms")

    out_csv = STAGE63_DIR / "temporal_aggregation_metrics.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(metrics[0].keys()))
        w.writeheader()
        w.writerows(metrics)
    print(f"\nWrote temporal aggregation metrics to {out_csv}")

    out_cat_csv = STAGE63_DIR / "false_positive_category_metrics.csv"
    with open(out_cat_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(category_breakdown[0].keys()))
        w.writeheader()
        w.writerows(category_breakdown)
    print(f"Wrote false positive category metrics to {out_cat_csv}")

if __name__ == "__main__":
    main()
