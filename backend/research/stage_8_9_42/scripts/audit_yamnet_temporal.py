"""
Stage 8.9.42: YAMNet Temporal Representation & Pooling Audit
Evaluates:
- Frame count distribution across duration regimes (<0.5s, 0.5-0.96s, >0.96s)
- Alternative temporal pooling methods:
  1. Mean Pooling (Baseline B-Frozen)
  2. Max Pooling across frames
  3. Energy-Weighted Pooling (RMS-weighted)
  4. Mask-Aware Pooling (silence-frame rejection)
- Impact on:
  - Stage 8.9.41 Positives (N=57)
  - Stage 8.9.40 Hard Negatives (N=145)
  - Stage 8.9.40 Shouted Speech (N=54)
- Verification of whether post-hoc pooling can resolve the short-scream YAMNet dilution problem.
"""
import os
import sys
import json
import csv
from pathlib import Path
import numpy as np
import soundfile as sf
import torch
import joblib

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(BACKEND_DIR / "research" / "stage_8_9_39"))

from src.audio.preprocessor import load_audio
from src.config import TARGET_SAMPLE_RATE
from src.model.yamnet_loader import YAMNetLoader
from scripts.train_config_b import DualEncoderAcousticModel

STAGE40_DIR = BACKEND_DIR / "research" / "stage_8_9_40"
STAGE41_DIR = BACKEND_DIR / "research" / "stage_8_9_41"
STAGE42_DIR = BACKEND_DIR / "research" / "stage_8_9_42"
STAGE39_DIR = BACKEND_DIR / "research" / "stage_8_9_39"

VOCAL_CLASS_INDICES = [0, 1, 2, 3, 6, 7, 8, 13, 14, 16, 17]
CROWD_CLASS_INDICES = [67, 68, 69]
SCREAM_CLASS_INDEX = 6

def compute_frame_rms(waveform, n_frames, window_size=15360, hop_size=7680):
    rms_list = []
    for i in range(n_frames):
        start = i * hop_size
        end = start + window_size
        if start >= len(waveform):
            rms_list.append(1e-6)
            continue
        chunk = waveform[start:min(end, len(waveform))]
        rms = float(np.sqrt(np.mean(chunk**2))) if len(chunk) > 0 else 1e-6
        rms_list.append(max(rms, 1e-6))
    return np.array(rms_list, dtype=np.float32)

def extract_pooled_features(preds, embs, wf, pooling_mode="mean"):
    n_frames = len(embs)
    vocal_frames = np.max(preds[:, VOCAL_CLASS_INDICES], axis=1)
    crowd_frames = np.max(preds[:, CROWD_CLASS_INDICES], axis=1)
    scream_frames = preds[:, SCREAM_CLASS_INDEX]

    if n_frames == 1 or pooling_mode == "mean":
        f_sem = np.mean(embs, axis=0).astype(np.float32)
        f_acoust = np.array([
            float(np.max(vocal_frames)),
            float(np.mean(vocal_frames)),
            float(np.max(crowd_frames)),
            float(np.mean(crowd_frames)),
            float(np.max(scream_frames)),
            float(np.mean(scream_frames)),
        ], dtype=np.float32)
        return f_sem, f_acoust

    frame_rms = compute_frame_rms(wf, n_frames)

    if pooling_mode == "max":
        # Feature-wise max for semantic embedding
        f_sem = np.max(embs, axis=0).astype(np.float32)
        f_acoust = np.array([
            float(np.max(vocal_frames)),
            float(np.max(vocal_frames)),
            float(np.max(crowd_frames)),
            float(np.max(crowd_frames)),
            float(np.max(scream_frames)),
            float(np.max(scream_frames)),
        ], dtype=np.float32)
    elif pooling_mode == "energy_weighted":
        weights = frame_rms / np.sum(frame_rms)
        f_sem = np.sum(embs * weights[:, None], axis=0).astype(np.float32)
        f_acoust = np.array([
            float(np.max(vocal_frames)),
            float(np.sum(vocal_frames * weights)),
            float(np.max(crowd_frames)),
            float(np.sum(crowd_frames * weights)),
            float(np.max(scream_frames)),
            float(np.sum(scream_frames * weights)),
        ], dtype=np.float32)
    elif pooling_mode == "mask_aware":
        peak_rms = np.max(frame_rms)
        silence_thresh = max(0.10 * peak_rms, 0.005)
        active_mask = frame_rms >= silence_thresh
        if np.any(active_mask):
            f_sem = np.mean(embs[active_mask], axis=0).astype(np.float32)
            f_acoust = np.array([
                float(np.max(vocal_frames)),
                float(np.mean(vocal_frames[active_mask])),
                float(np.max(crowd_frames)),
                float(np.mean(crowd_frames[active_mask])),
                float(np.max(scream_frames)),
                float(np.mean(scream_frames[active_mask])),
            ], dtype=np.float32)
        else:
            f_sem = np.mean(embs, axis=0).astype(np.float32)
            f_acoust = np.array([
                float(np.max(vocal_frames)),
                float(np.mean(vocal_frames)),
                float(np.max(crowd_frames)),
                float(np.mean(crowd_frames)),
                float(np.max(scream_frames)),
                float(np.mean(scream_frames)),
            ], dtype=np.float32)
    else:
        raise ValueError(f"Unknown pooling mode: {pooling_mode}")

    return f_sem, f_acoust

def main():
    print("=" * 80)
    print("STAGE 8.9.42: YAMNET TEMPORAL REPRESENTATION & POOLING AUDIT")
    print("=" * 80)

    # 1. Load Model and Calibrator
    ckpt_path = STAGE39_DIR / "checkpoints" / "config_b" / "best_model.pt"
    calib_path = STAGE39_DIR / "checkpoints" / "config_b" / "platt_calibrator.joblib"
    print(f"Loading Config B model: {ckpt_path}")
    ckpt = torch.load(ckpt_path, map_location='cpu')
    model = DualEncoderAcousticModel(sem_dim=1024, acoustic_dim=6, proj_sem=128, proj_acoust=32)
    model.load_state_dict(ckpt['model_state_dict'])
    model.eval()

    calibrator = joblib.load(calib_path)
    threshold = 0.24
    print(f"Frozen threshold: {threshold}")

    # 2. Load YAMNet
    print("Loading YAMNet model...")
    yamnet = YAMNetLoader()
    yamnet.load()

    # 3. Load Datasets
    pos_manifest = STAGE41_DIR / "manifests" / "stage_8_9_41_positive_manifest.csv"
    neg_manifest = STAGE40_DIR / "manifests" / "new_cohort_manifest.csv"

    pos_rows = []
    with open(pos_manifest, "r", encoding="utf-8") as f:
        pos_rows = list(csv.DictReader(f))

    neg_rows = []
    with open(neg_manifest, "r", encoding="utf-8") as f:
        neg_rows = list(csv.DictReader(f))

    print(f"Loaded {len(pos_rows)} positive rows and {len(neg_rows)} negative rows.")

    datasets = {
        "positives": (pos_rows, 1),
        "negatives": (neg_rows, 0)
    }

    pooling_modes = ["mean", "max", "energy_weighted", "mask_aware"]
    results = {m: {"pos_tp": 0, "pos_total": len(pos_rows),
                   "neg_fp": 0, "neg_total": len(neg_rows),
                   "shout_fp": 0, "shout_total": 0,
                   "ultra_short_tp": 0, "ultra_short_total": 0,
                   "short_tp": 0, "short_total": 0,
                   "predictions": []} for m in pooling_modes}

    # Pre-extract YAMNet raw frames for efficiency
    raw_cache = {}
    print("\nExtracting raw YAMNet frames for all audio files...")
    
    # Analyze frame count vs duration
    frame_counts = {"d_under_0_5": 0, "d_0_5_to_0_96": 0, "d_over_0_96": 0}
    single_frame_under_0_96 = 0

    all_items = [(r, 1) for r in pos_rows] + [(r, 0) for r in neg_rows]
    for idx, (r, is_pos) in enumerate(all_items):
        file_id = r["file_id"]
        rel_path = r["workspace_audio_path"]
        audio_path = REPO_ROOT / rel_path
        dur = float(r["duration_seconds"])

        wf, _ = load_audio(audio_path, target_sr=TARGET_SAMPLE_RATE)
        preds, embs, _ = yamnet.infer(wf)
        raw_cache[file_id] = (preds, embs, wf, dur, r)

        n_frames = len(embs)
        if dur < 0.5:
            frame_counts["d_under_0_5"] += 1
            if n_frames == 1:
                single_frame_under_0_96 += 1
        elif dur <= 0.96:
            frame_counts["d_0_5_to_0_96"] += 1
            if n_frames == 1:
                single_frame_under_0_96 += 1
        else:
            frame_counts["d_over_0_96"] += 1

        if (idx + 1) % 50 == 0 or (idx + 1) == len(all_items):
            print(f"Processed {idx + 1}/{len(all_items)} audio files...")

    print(f"\nFrame count distribution:")
    print(f"  Duration < 0.5s: {frame_counts['d_under_0_5']} clips (all {single_frame_under_0_96} <= 0.96s have exactly 1 frame)")
    print(f"  Duration 0.5-0.96s: {frame_counts['d_0_5_to_0_96']} clips")
    print(f"  Duration > 0.96s: {frame_counts['d_over_0_96']} clips")

    # Evaluate each pooling mode
    for m in pooling_modes:
        print(f"\nEvaluating pooling strategy: {m}...")
        for r in pos_rows:
            fid = r["file_id"]
            preds, embs, wf, dur, meta = raw_cache[fid]
            subtype = meta["acoustic_subtype"]
            is_ultra_short = (subtype == "short_scream" and dur < 0.5)
            is_short = (subtype == "short_scream" or dur <= 1.0)

            f_sem, f_acoust = extract_pooled_features(preds, embs, wf, pooling_mode=m)
            mask_acoust = (~np.isnan(f_acoust) & (f_acoust > 0.0)).astype(np.float32)

            t_sem = torch.tensor(f_sem[None, :], dtype=torch.float32)
            t_acoust = torch.tensor(f_acoust[None, :], dtype=torch.float32)
            t_mask = torch.tensor(mask_acoust[None, :], dtype=torch.float32)

            with torch.no_grad():
                logit, _, _ = model(t_sem, t_acoust, t_mask)
                prob = float(calibrator.predict_proba(logit.numpy().reshape(-1, 1))[:, 1][0])

            pred = 1 if prob >= threshold else 0
            if pred == 1:
                results[m]["pos_tp"] += 1
            if is_ultra_short:
                results[m]["ultra_short_total"] += 1
                if pred == 1:
                    results[m]["ultra_short_tp"] += 1
            if is_short:
                results[m]["short_total"] += 1
                if pred == 1:
                    results[m]["short_tp"] += 1

            results[m]["predictions"].append({
                "file_id": fid, "label": 1, "prob": prob, "pred": pred, "subtype": subtype, "dur": dur
            })

        for r in neg_rows:
            fid = r["file_id"]
            preds, embs, wf, dur, meta = raw_cache[fid]
            cat = meta.get("target_category", "")
            is_shout = (cat == "shouting_and_speech")

            f_sem, f_acoust = extract_pooled_features(preds, embs, wf, pooling_mode=m)
            mask_acoust = (~np.isnan(f_acoust) & (f_acoust > 0.0)).astype(np.float32)

            t_sem = torch.tensor(f_sem[None, :], dtype=torch.float32)
            t_acoust = torch.tensor(f_acoust[None, :], dtype=torch.float32)
            t_mask = torch.tensor(mask_acoust[None, :], dtype=torch.float32)

            with torch.no_grad():
                logit, _, _ = model(t_sem, t_acoust, t_mask)
                prob = float(calibrator.predict_proba(logit.numpy().reshape(-1, 1))[:, 1][0])

            pred = 1 if prob >= threshold else 0
            if pred == 1:
                results[m]["neg_fp"] += 1
            if is_shout:
                results[m]["shout_total"] += 1
                if pred == 1:
                    results[m]["shout_fp"] += 1

            results[m]["predictions"].append({
                "file_id": fid, "label": 0, "prob": prob, "pred": pred, "category": cat, "dur": dur
            })

    # Summary table
    print("\n" + "=" * 90)
    print(f"{'Pooling Mode':<18} | {'Pos Recall':<12} | {'Ultra-Short':<12} | {'Short Recall':<12} | {'HN-FPR':<10} | {'Shout-FPR':<10}")
    print("-" * 90)
    summary_data = []
    for m in pooling_modes:
        res = results[m]
        pos_rec = res["pos_tp"] / res["pos_total"] * 100
        ultra_rec = (res["ultra_short_tp"] / res["ultra_short_total"] * 100) if res["ultra_short_total"] > 0 else 0
        short_rec = (res["short_tp"] / res["short_total"] * 100) if res["short_total"] > 0 else 0
        hn_fpr = res["neg_fp"] / res["neg_total"] * 100
        shout_fpr = (res["shout_fp"] / res["shout_total"] * 100) if res["shout_total"] > 0 else 0

        print(f"{m:<18} | {res['pos_tp']}/{res['pos_total']} ({pos_rec:.1f}%) | {res['ultra_short_tp']}/{res['ultra_short_total']} ({ultra_rec:.1f}%) | {res['short_tp']}/{res['short_total']} ({short_rec:.1f}%) | {res['neg_fp']}/{res['neg_total']} ({hn_fpr:.2f}%) | {res['shout_fp']}/{res['shout_total']} ({shout_fpr:.2f}%)")

        summary_data.append({
            "pooling_mode": m,
            "positive_recall": pos_rec,
            "positive_tp": res["pos_tp"],
            "positive_total": res["pos_total"],
            "ultra_short_recall": ultra_rec,
            "ultra_short_tp": res["ultra_short_tp"],
            "ultra_short_total": res["ultra_short_total"],
            "short_scream_recall": short_rec,
            "short_scream_tp": res["short_tp"],
            "short_scream_total": res["short_total"],
            "hard_negative_fpr": hn_fpr,
            "hard_negative_fp": res["neg_fp"],
            "hard_negative_total": res["neg_total"],
            "shouted_speech_fpr": shout_fpr,
            "shouted_speech_fp": res["shout_fp"],
            "shouted_speech_total": res["shout_total"],
        })
    print("=" * 90)

    # Save results json
    out_json = STAGE42_DIR / "results" / "yamnet_temporal_audit.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({
            "summary": summary_data,
            "frame_counts": frame_counts,
            "threshold": threshold
        }, f, indent=2)
    print(f"\nSaved audit results: {out_json}")

if __name__ == "__main__":
    main()

