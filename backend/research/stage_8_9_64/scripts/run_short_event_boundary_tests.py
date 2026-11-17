#!/usr/bin/env python3
"""
STAGE 8.9.64 — Track C: Short-Event Boundary Robustness & Position Sensitivity Testing
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import csv
import math
import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
import scipy.io.wavfile as wav
import torch

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE57_DIR = BACKEND_DIR / "research" / "stage_8_9_57"
STAGE63_DIR = BACKEND_DIR / "research" / "stage_8_9_63"
STAGE64_DIR = BACKEND_DIR / "research" / "stage_8_9_64"

sys.path.insert(0, str(STAGE57_DIR / "dsp_implementations"))
from c5_combined import extract_subband_vector_c5, extract_phonation_stats_c5
from reproduce_dual_resolution import DualResolutionGatedModel, extract_short_branch_features, extract_sustained_branch_features, load_audio_wav

def generate_synthetic_scream_burst(duration_s: float, sr: int = 16000) -> np.ndarray:
    n_samples = int(duration_s * sr)
    t = np.linspace(0, duration_s, n_samples, endpoint=False)
    # Fundamental frequency sweeping from 900 Hz to 1800 Hz
    f0 = 900.0 + 900.0 * np.sin(np.pi * t / duration_s)
    phase0 = 2 * np.pi * np.cumsum(f0) / sr

    # Additive harmonics with roughness (subharmonics & AM modulation)
    s = np.sin(phase0) + 0.6 * np.sin(2 * phase0) + 0.4 * np.sin(3 * phase0) + 0.3 * np.sin(4 * phase0)
    # Roughness modulation (35 Hz amplitude tremor characteristic of panic scream)
    am = 0.75 + 0.25 * np.sin(2 * np.pi * 35.0 * t)
    s = s * am

    # Envelope with rapid 15 ms rise and 30 ms fall
    rise_samples = min(int(0.015 * sr), n_samples // 4)
    fall_samples = min(int(0.030 * sr), n_samples // 4)
    env = np.ones(n_samples, dtype=np.float32)
    if rise_samples > 0:
        env[:rise_samples] = np.linspace(0.0, 1.0, rise_samples)
    if fall_samples > 0:
        env[-fall_samples:] = np.linspace(1.0, 0.0, fall_samples)

    burst = (s * env).astype(np.float32)
    burst = burst / (np.max(np.abs(burst)) + 1e-9)
    return burst

def main():
    print("=" * 80)
    print("STAGE 8.9.64 — TRACK C: SHORT-EVENT BOUNDARY ROBUSTNESS")
    print("=" * 80)

    # Load frozen dual-resolution model checkpoint
    model_path = STAGE64_DIR / "models" / "stage63_dual_resolution_gated.pt"
    assert model_path.exists(), "Trained model checkpoint must exist"
    model = DualResolutionGatedModel()
    model.load_state_dict(torch.load(model_path, map_location="cpu", weights_only=True))
    model.eval()

    durations = [0.100, 0.150, 0.250, 0.350, 0.500, 0.750, 0.900]
    hop_sizes_s = [0.050, 0.100, 0.250]
    positions = [
        ("start", 0.00),
        ("quarter", 0.25),
        ("center", 0.50),
        ("three_quarter", 0.75),
        ("near_hop_edge", 0.90),
        ("straddle_2_windows", -1.0),  # Special logic
        ("straddle_3_windows", -2.0),
        ("rec_start", 0.0),
        ("rec_end", -3.0)
    ]

    sr = 16000
    rec_len_samples = int(3.0 * sr)  # 3.0 second background timeline

    results = []
    print("Executing Phase C1 & C2: Controlled Boundary Offset Matrix...")

    for hop_s in hop_sizes_s:
        hop_samples = int(hop_s * sr)
        for dur in durations:
            burst = generate_synthetic_scream_burst(dur, sr=sr)
            dur_samples = len(burst)

            for pos_name, pos_val in positions:
                timeline = np.random.normal(0.0, 0.005, rec_len_samples).astype(np.float32)

                if pos_name == "rec_start":
                    offset_samples = 0
                elif pos_name == "rec_end":
                    offset_samples = rec_len_samples - dur_samples
                elif pos_name == "straddle_2_windows":
                    # Place burst so half is in window i and half in window i+1
                    offset_samples = int(1.0 * sr) - dur_samples // 2
                elif pos_name == "straddle_3_windows":
                    offset_samples = int(1.0 * sr) - int(dur_samples * 0.75)
                else:
                    # Position relative to a 250ms window boundary starting at 1.0s
                    win_start = int(1.0 * sr)
                    offset_samples = win_start + int(pos_val * (int(0.250 * sr) - min(dur_samples, int(0.250 * sr))))

                offset_samples = max(0, min(offset_samples, rec_len_samples - dur_samples))
                timeline[offset_samples : offset_samples + dur_samples] += burst

                # Slide windows across timeline
                scores = []
                delays = []
                first_detection_time = None
                window_duration_samples = int(1.000 * sr)  # 1.0s window for sustained branch

                num_hops = (rec_len_samples - window_duration_samples) // hop_samples
                for h in range(num_hops):
                    w_start = h * hop_samples
                    w_end = w_start + window_duration_samples
                    chunk = timeline[w_start:w_end]

                    f_s = extract_short_branch_features(chunk, sr=sr)
                    f_l = extract_sustained_branch_features(chunk, sr=sr)

                    t_s = torch.tensor(f_s, dtype=torch.float32).unsqueeze(0)
                    t_l = torch.tensor(f_l, dtype=torch.float32).unsqueeze(0)

                    with torch.no_grad():
                        logit = model(t_s, t_l)
                        prob = float(torch.sigmoid(logit).item())

                    scores.append(prob)
                    if prob >= 0.50 and first_detection_time is None:
                        first_detection_time = w_start / sr
                        delays.append(max(0.0, (w_start - offset_samples) / sr))

                max_score = float(np.max(scores))
                detected = int(max_score >= 0.50)
                contributing_windows = int(np.sum(np.array(scores) >= 0.50))
                det_delay_ms = round(float(delays[0] * 1000.0), 2) if delays else None

                results.append({
                    "hop_size_ms": int(hop_s * 1000),
                    "event_duration_ms": int(dur * 1000),
                    "boundary_position": pos_name,
                    "max_detection_score": round(max_score, 4),
                    "is_detected": detected,
                    "contributing_windows": contributing_windows,
                    "detection_delay_ms": det_delay_ms,
                    "padding_fraction": round(max(0.0, 1.0 - dur / 0.250), 3) if dur < 0.250 else 0.0
                })

    # Summary statistics for boundary sensitivity
    df_synth = pd.DataFrame(results)
    print(f"\nSynthetic Boundary Experiments Completed: {len(df_synth)} configurations tested.")

    # Phase C3: Real Recording Boundary Evaluation
    print("\nExecuting Phase C3: Real Recording Boundary Evaluation on Development Manifest...")
    ann_path = STAGE63_DIR / "short_scream_annotation_records.csv"
    dev_path = STAGE63_DIR / "stage_63_development_manifest.csv"
    assert ann_path.exists() and dev_path.exists()

    df_ann = pd.read_csv(ann_path)
    df_dev = pd.read_csv(dev_path)

    real_results = []
    hop_samples_50ms = int(0.050 * sr)
    win_len = int(1.000 * sr)

    for _, ann in df_ann.iterrows():
        rec_id = ann["recording_id"]
        dev_row = df_dev[df_dev["recording_id"] == rec_id]
        if dev_row.empty:
            continue
        audio_path = REPO_ROOT / dev_row.iloc[0]["workspace_audio_path"]
        audio = load_audio_wav(audio_path)

        # Pad audio if shorter than 1.0s to allow evaluation
        if len(audio) < win_len:
            pad_len = win_len - len(audio)
            audio = np.pad(audio, (0, pad_len))

        onset_s = float(ann["r1_onset"])
        offset_s = float(ann["r1_offset"])
        dur_s = float(ann["r1_event_duration"])

        # Sliding evaluation
        hop_scores = []
        hop_times = []
        first_det_t = None
        hops = max(1, (len(audio) - win_len) // hop_samples_50ms + 1)

        for h in range(hops):
            s_idx = h * hop_samples_50ms
            e_idx = s_idx + win_len
            chunk = audio[s_idx:e_idx] if e_idx <= len(audio) else audio[-win_len:]

            f_s = extract_short_branch_features(chunk, sr=sr)
            f_l = extract_sustained_branch_features(chunk, sr=sr)

            with torch.no_grad():
                logit = model(torch.tensor(f_s, dtype=torch.float32).unsqueeze(0),
                              torch.tensor(f_l, dtype=torch.float32).unsqueeze(0))
                prob = float(torch.sigmoid(logit).item())

            hop_scores.append(prob)
            t_win = s_idx / sr
            hop_times.append(t_win)

            if prob >= 0.50 and first_det_t is None:
                first_det_t = t_win

        max_prob = max(hop_scores)
        detected = int(max_prob >= 0.50)
        delay_ms = max(0.0, (first_det_t - onset_s) * 1000.0) if first_det_t is not None else None
        num_triggers = sum(p >= 0.50 for p in hop_scores)

        real_results.append({
            "recording_id": rec_id,
            "event_onset_s": round(onset_s, 4),
            "event_offset_s": round(offset_s, 4),
            "event_duration_s": round(dur_s, 4),
            "max_score": round(max_prob, 4),
            "is_detected": detected,
            "detection_delay_ms": round(delay_ms, 2) if delay_ms is not None else None,
            "num_positive_windows": num_triggers,
            "is_fragmented": int(num_triggers > 2)
        })

    out_csv = STAGE64_DIR / "short_event_boundary_metrics.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader()
        w.writerows(results)
    print(f"Wrote synthetic boundary metrics to {out_csv}")

    # Compute high-level position variance statistics
    by_pos = df_synth.groupby("boundary_position")["is_detected"].mean()
    worst_pos = by_pos.min()
    best_pos = by_pos.max()
    mean_rec = by_pos.mean()
    print("\nPosition Recall Summary (across all synthetic tests):")
    print(f"  Best-Position Recall:     {best_pos*100:.2f}%")
    print(f"  Worst-Position Recall:    {worst_pos*100:.2f}% (straddle/edge boundaries)")
    print(f"  Mean Position Recall:     {mean_rec*100:.2f}%")
    print(f"  Boundary Failure Delta:   {(best_pos - worst_pos)*100:.2f}%")

    df_real = pd.DataFrame(real_results)
    real_rec = df_real["is_detected"].mean()
    mean_delay = df_real["detection_delay_ms"].dropna().mean()
    print(f"\nReal Development Recordings Boundary Summary (N={len(df_real)}):")
    print(f"  Real Short Detection Rate:  {real_rec*100:.2f}%")
    print(f"  Mean Detection Delay:       {mean_delay:.2f} ms")

if __name__ == "__main__":
    main()
