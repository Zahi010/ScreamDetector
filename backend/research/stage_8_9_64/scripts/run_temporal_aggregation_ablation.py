#!/usr/bin/env python3
"""
STAGE 8.9.64 — Track F: Temporal Aggregation & Branch-Aware Corroboration Ablations
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import csv
import json
import math
from pathlib import Path
import numpy as np
import torch

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE54_DIR = BACKEND_DIR / "research" / "stage_8_9_54"
STAGE61_DIR = BACKEND_DIR / "research" / "stage_8_9_61"
STAGE64_DIR = BACKEND_DIR / "research" / "stage_8_9_64"

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

def evaluate_aggregation_method(probs: np.ndarray, method_name: str) -> tuple[int, int, int, float]:
    """
    Evaluates temporal aggregation methods on rolling window probabilities.
    Returns: (triggered, raw_window_triggers, post_event_triggers, detection_delay_ms)
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
        lockout = 0
        ref_triggers = []
        for i, p in enumerate(probs):
            if lockout > 0:
                lockout -= 1
                continue
            if p >= 0.5000:
                ref_triggers.append(i)
                lockout = 10  # 10 hops * 50 ms = 500 ms
        post_triggers = len(ref_triggers)
        if len(ref_triggers) > 0:
            triggered = 1
            delay_ms = float(ref_triggers[0] * 50.0)

    elif method_name == "Method_F_Branch_Aware_Corroboration":
        # Branch-aware: if transient peak (short burst), require K=2 or peak >= 0.75
        # Plus 500ms refractory lockout
        lockout = 0
        branch_triggers = []
        for i in range(len(probs)):
            if lockout > 0:
                lockout -= 1
                continue
            p = probs[i]
            if p >= 0.7500:
                branch_triggers.append(i)
                lockout = 10
            elif p >= 0.5000:
                # Require adjacent corroboration
                has_corrob = False
                if i > 0 and probs[i-1] >= 0.4500:
                    has_corrob = True
                elif i < len(probs) - 1 and probs[i+1] >= 0.4500:
                    has_corrob = True
                if has_corrob:
                    branch_triggers.append(i)
                    lockout = 10
        post_triggers = len(branch_triggers)
        if len(branch_triggers) > 0:
            triggered = 1
            delay_ms = float(branch_triggers[0] * 50.0)

    return triggered, raw_triggers, post_triggers, delay_ms

def main():
    print("=" * 80)
    print("STAGE 8.9.64 — TRACK F: TEMPORAL AGGREGATION & BRANCH-AWARE CORROBORATION")
    print("=" * 80)

    npz_path = STAGE61_DIR / "rolling_window_experiments" / "dev_rolling_features.npz"
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
    n_short = sum(1 for r in rec_list if r["binary_label"] == 1 and r["duration_seconds"] < 1.0)
    n_sust = sum(1 for r in rec_list if r["binary_label"] == 1 and r["duration_seconds"] >= 1.0)

    methods = [
        ("Method_Baseline_Any_Window", "Baseline (Any Window >= 0.50)"),
        ("Method_A_Consecutive_Evidence_K2", "Method A: Consecutive Evidence (K=2, 100 ms sustained)"),
        ("Method_B_Bounded_EMA_0.30", "Method B: Bounded EMA (alpha=0.30, thresh=0.45)"),
        ("Method_C_Peak_With_Corroboration", "Method C: Peak with Corroboration (Peak >= 0.70)"),
        ("Method_D_Event_Merging", "Method D: Event-Level Merging (<200ms gap)"),
        ("Method_E_Refractory_Holdoff_500ms", "Method E: Refractory Holdoff (500 ms lockout)"),
        ("Method_F_Branch_Aware_Corroboration", "Method F: Branch-Aware Corroboration + Holdoff")
    ]

    metrics = []
    print(f"\n{'Method':<36} {'Recall':<8} {'FPR':<8} {'F1':<8} {'ShortRec':<10} {'MeanDelay':<10} {'P95Delay':<10} {'FragRatio':<10}")
    print("-" * 104)

    for mid, desc in methods:
        tp = fn = fp = tn = 0
        short_tp = sust_tp = 0
        delays = []
        total_raw = 0
        total_post = 0

        for r in rec_list:
            dec, raw_trig, post_trig, delay = evaluate_aggregation_method(r["window_probs"], mid)
            total_raw += raw_trig
            total_post += post_trig
            if dec == 1:
                delays.append(delay)

            y = r["binary_label"]
            dur = r["duration_seconds"]

            if y == 1:
                if dec == 1:
                    tp += 1
                    if dur < 1.0:
                        short_tp += 1
                    else:
                        sust_tp += 1
                else:
                    fn += 1
            else:
                if dec == 1:
                    fp += 1
                else:
                    tn += 1

        recall = tp / n_pos if n_pos > 0 else 0.0
        fpr = fp / n_neg if n_neg > 0 else 0.0
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        f1 = 2 * prec * recall / (prec + recall) if (prec + recall) > 0 else 0.0
        short_rec = short_tp / n_short if n_short > 0 else 0.0
        mean_delay = float(np.mean(delays)) if len(delays) > 0 else 0.0
        p95_delay = float(np.percentile(delays, 95)) if len(delays) > 0 else 0.0
        frag_ratio = total_post / tp if tp > 0 else 1.0

        res = {
            "method_id": mid,
            "description": desc,
            "overall_recall": round(recall, 4),
            "gate1_pass": recall >= 0.960,
            "fpr": round(fpr, 4),
            "gate2_pass": fpr <= 0.050,
            "f1_score": round(f1, 4),
            "short_scream_recall": round(short_rec, 4),
            "gate4_pass": short_rec >= 0.900,
            "mean_latency_delay_ms": round(mean_delay, 2),
            "p95_latency_delay_ms": round(p95_delay, 2),
            "event_fragmentation_ratio": round(frag_ratio, 2),
            "raw_alarm_count": total_raw,
            "post_alarm_count": total_post,
            "tp": tp, "fp": fp, "fn": fn, "tn": tn
        }
        metrics.append(res)
        print(f"{mid:<36} {recall:<8.4f} {fpr:<8.4f} {f1:<8.4f} {short_rec:<10.4f} {mean_delay:<10.1f} {p95_delay:<10.1f} {frag_ratio:<10.2f}")

    out_csv = STAGE64_DIR / "temporal_aggregation_metrics.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(metrics[0].keys()))
        w.writeheader()
        w.writerows(metrics)
    print(f"\nWrote temporal aggregation benchmark metrics to {out_csv}")

if __name__ == "__main__":
    main()

