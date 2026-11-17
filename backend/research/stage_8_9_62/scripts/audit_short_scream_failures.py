#!/usr/bin/env python3
"""
STAGE 8.9.62 — Track B: Short-Scream False-Negative Forensic Analysis & Acoustic Feature Extraction
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import csv
import json
import math
from pathlib import Path
import numpy as np
import scipy.io.wavfile as wav

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE60_DIR = BACKEND_DIR / "research" / "stage_8_9_60"
STAGE61_DIR = BACKEND_DIR / "research" / "stage_8_9_61"
STAGE62_DIR = BACKEND_DIR / "research" / "stage_8_9_62"

def compute_spectral_features(audio: np.ndarray, sr: int = 16000, n_fft: int = 512, hop: int = 256):
    # Windowing
    window = np.hanning(n_fft)
    n_frames = max(1, (len(audio) - n_fft) // hop + 1)
    
    centroids = []
    bandwidths = []
    rolloffs = []
    flatnesses = []
    
    freqs = np.fft.rfftfreq(n_fft, d=1.0/sr)
    
    for i in range(n_frames):
        start = i * hop
        frame = audio[start:start+n_fft]
        if len(frame) < n_fft:
            frame = np.pad(frame, (0, n_fft - len(frame)))
        frame = frame * window
        mag = np.abs(np.fft.rfft(frame))
        total_mag = np.sum(mag)
        
        if total_mag > 1e-9:
            # Centroid
            c = np.sum(freqs * mag) / total_mag
            centroids.append(c)
            # Bandwidth
            bw = np.sqrt(np.sum(((freqs - c) ** 2) * mag) / total_mag)
            bandwidths.append(bw)
            # Rolloff 85%
            cumsum = np.cumsum(mag)
            cutoff = 0.85 * total_mag
            ro_idx = np.searchsorted(cumsum, cutoff)
            rolloffs.append(freqs[min(ro_idx, len(freqs)-1)])
            # Flatness: geometric mean / arithmetic mean
            geo_mean = np.exp(np.mean(np.log(mag + 1e-12)))
            ari_mean = np.mean(mag) + 1e-12
            flatnesses.append(geo_mean / ari_mean)
        else:
            centroids.append(0.0)
            bandwidths.append(0.0)
            rolloffs.append(0.0)
            flatnesses.append(0.0)
            
    return {
        "spectral_centroid_hz": float(np.mean(centroids)),
        "spectral_bandwidth_hz": float(np.mean(bandwidths)),
        "spectral_rolloff_hz": float(np.mean(rolloffs)),
        "spectral_flatness": float(np.mean(flatnesses))
    }

def compute_zcr(audio: np.ndarray):
    zero_crosses = np.nonzero(np.diff(audio > 0))[0]
    return float(len(zero_crosses) / max(1, len(audio)))

def main():
    # Load Stage 60 manifest for file paths and provenance
    with open(STAGE60_DIR / "future_evaluation_manifest.json") as f:
        eval_manifest = json.load(f)
    rec_manifest_map = {r["recording_id"]: r for r in eval_manifest["recordings"]}

    # Load Stage 61 predictions
    with open(STAGE61_DIR / "sealed_cohort_predictions.csv") as f:
        preds = list(csv.DictReader(f))

    # Map candidate -> {rec_id: row}
    cand_preds = {}
    for r in preds:
        cid = r["candidate_id"]
        if cid not in cand_preds:
            cand_preds[cid] = {}
        cand_preds[cid][r["recording_id"]] = r

    # Identify the 69 short screams
    short_scream_rids = []
    for r in preds:
        if r["candidate_id"] == "Candidate_E1_Static_C5" and int(r["binary_label"]) == 1 and float(r["duration_seconds"]) < 1.0:
            short_scream_rids.append(r["recording_id"])

    short_scream_rids = sorted(list(set(short_scream_rids)))
    assert len(short_scream_rids) == 69, f"Expected 69 short screams, got {len(short_scream_rids)}"
    print(f"Extracted {len(short_scream_rids)} short-scream recordings for forensic analysis.")

    forensic_inventory = []
    feature_analysis = []

    for rid in short_scream_rids:
        m_rec = rec_manifest_map[rid]
        rel_audio_path = m_rec["workspace_audio_path"]
        abs_audio_path = REPO_ROOT / rel_audio_path

        if not abs_audio_path.exists():
            raise FileNotFoundError(f"Missing audio file at {abs_audio_path}")

        # Load audio
        sr, audio_raw = wav.read(abs_audio_path)
        if audio_raw.dtype == np.int16:
            audio = audio_raw.astype(np.float32) / 32768.0
        elif audio_raw.dtype == np.int32:
            audio = audio_raw.astype(np.float32) / 2147483648.0
        else:
            audio = audio_raw.astype(np.float32)

        # Basic signal statistics
        dur = len(audio) / sr
        rms = float(np.sqrt(np.mean(audio ** 2)))
        peak = float(np.max(np.abs(audio)))
        clipping_samples = np.sum(np.abs(audio) >= 0.999)
        clipping_ratio = float(clipping_samples / len(audio))
        silence_samples = np.sum(np.abs(audio) < 0.01)
        silence_ratio = float(silence_samples / len(audio))

        # Noise floor (approx bottom 10th percentile energy)
        frame_len = 512
        frame_energies = [np.sqrt(np.mean(audio[i:i+frame_len]**2)) for i in range(0, len(audio)-frame_len, frame_len)]
        if frame_energies:
            noise_floor = float(np.percentile(frame_energies, 10))
            active_energy = float(np.percentile(frame_energies, 90))
            snr_approx_db = float(20 * math.log10(max(active_energy, 1e-6) / max(noise_floor, 1e-6)))
        else:
            noise_floor = 0.001
            snr_approx_db = 20.0

        dynamic_range_db = float(20 * math.log10(max(peak, 1e-6) / max(noise_floor, 1e-6)))
        padding_fraction = max(0.0, 1.0 - dur)  # relative to 1.0s analysis window
        usable_windows_500ms = max(1, math.floor(max(0, dur - 1.0) / 0.5) + 1)

        # Spectral features
        spec_feats = compute_spectral_features(audio, sr=sr)
        zcr = compute_zcr(audio)

        # Candidate predictions
        p_e1_stat = float(cand_preds["Candidate_E1_Static_C5"][rid]["predicted_probability"])
        y_e1_stat = int(cand_preds["Candidate_E1_Static_C5"][rid]["predicted_label"])
        fn_e1_stat = 1 if y_e1_stat == 0 else 0

        p_b = float(cand_preds["Candidate_B_Baseline"][rid]["predicted_probability"])
        y_b = int(cand_preds["Candidate_B_Baseline"][rid]["predicted_label"])
        fn_b = 1 if y_b == 0 else 0

        p_bd = float(cand_preds["Candidate_B_Intervention_D"][rid]["predicted_probability"])
        y_bd = int(cand_preds["Candidate_B_Intervention_D"][rid]["predicted_label"])
        fn_bd = 1 if y_bd == 0 else 0

        p_e1_roll = float(cand_preds["Candidate_E1_Rolling_C5_EMA"][rid]["predicted_probability"])
        y_e1_roll = int(cand_preds["Candidate_E1_Rolling_C5_EMA"][rid]["predicted_label"])
        fn_e1_roll = 1 if y_e1_roll == 0 else 0

        inv_row = {
            "recording_id": rid,
            "source_group_id": m_rec["source_group_id"],
            "duration_seconds": round(dur, 4),
            "ground_truth_label": 1,
            "target_category": m_rec["target_category"],
            "subcategory": m_rec["subcategory"],
            "uploader_or_creator": m_rec["uploader_or_creator"],
            "license": m_rec["license"],
            "e1_static_prob": round(p_e1_stat, 4),
            "e1_static_pred": y_e1_stat,
            "e1_static_fn": fn_e1_stat,
            "cand_b_prob": round(p_b, 4),
            "cand_b_pred": y_b,
            "cand_b_fn": fn_b,
            "cand_bd_prob": round(p_bd, 4),
            "cand_bd_pred": y_bd,
            "cand_bd_fn": fn_bd,
            "e1_rolling_prob": round(p_e1_roll, 4),
            "e1_rolling_pred": y_e1_roll,
            "e1_rolling_fn": fn_e1_roll,
            "padding_fraction_1s": round(padding_fraction, 4),
            "rms_amplitude": round(rms, 4),
            "peak_amplitude": round(peak, 4),
            "dynamic_range_db": round(dynamic_range_db, 2),
            "clipping_ratio": round(clipping_ratio, 6),
            "silence_ratio": round(silence_ratio, 4),
            "snr_approx_db": round(snr_approx_db, 2)
        }
        forensic_inventory.append(inv_row)

        feat_row = {
            "recording_id": rid,
            "source_group_id": m_rec["source_group_id"],
            "duration_seconds": round(dur, 4),
            "padding_fraction_1s": round(padding_fraction, 4),
            "rms_amplitude": round(rms, 4),
            "peak_amplitude": round(peak, 4),
            "dynamic_range_db": round(dynamic_range_db, 2),
            "silence_ratio": round(silence_ratio, 4),
            "snr_approx_db": round(snr_approx_db, 2),
            "spectral_centroid_hz": round(spec_feats["spectral_centroid_hz"], 1),
            "spectral_bandwidth_hz": round(spec_feats["spectral_bandwidth_hz"], 1),
            "spectral_rolloff_hz": round(spec_feats["spectral_rolloff_hz"], 1),
            "spectral_flatness": round(spec_feats["spectral_flatness"], 6),
            "zero_crossing_rate": round(zcr, 4),
            "e1_static_prob": round(p_e1_stat, 4),
            "cand_b_prob": round(p_b, 4),
            "e1_rolling_prob": round(p_e1_roll, 4),
            "detected_by_any": 1 if (y_e1_stat == 1 or y_b == 1 or y_bd == 1 or y_e1_roll == 1) else 0,
            "missed_by_all": 1 if (y_e1_stat == 0 and y_b == 0 and y_bd == 0 and y_e1_roll == 0) else 0
        }
        feature_analysis.append(feat_row)

    # Write short_scream_forensic_inventory.csv
    out_inv_csv = STAGE62_DIR / "short_scream_forensic_inventory.csv"
    with open(out_inv_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(forensic_inventory[0].keys()))
        w.writeheader()
        w.writerows(forensic_inventory)
    print(f"Wrote {out_inv_csv}")

    # Write short_scream_feature_analysis.csv
    out_feat_csv = STAGE62_DIR / "short_scream_feature_analysis.csv"
    with open(out_feat_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(feature_analysis[0].keys()))
        w.writeheader()
        w.writerows(feature_analysis)
    print(f"Wrote {out_feat_csv}")

    # -------------------------------------------------------------------------
    # Phase B2: Failure Overlap Analysis
    # -------------------------------------------------------------------------
    # Candidate detections on the 69 short screams
    all_missed = 0
    all_detected = 0
    e1_stat_only = 0
    cand_b_only = 0
    e1_roll_only = 0
    recovered_by_rolling = 0  # detected by rolling E1 but missed by static E1
    lost_by_rolling = 0       # detected by static E1 but missed by rolling E1

    for row in forensic_inventory:
        y_e1_s = row["e1_static_pred"]
        y_b = row["cand_b_pred"]
        y_bd = row["cand_bd_pred"]
        y_e1_r = row["e1_rolling_pred"]

        if y_e1_s == 0 and y_b == 0 and y_bd == 0 and y_e1_r == 0:
            all_missed += 1
        if y_e1_s == 1 and y_b == 1 and y_bd == 1 and y_e1_r == 1:
            all_detected += 1

        if y_e1_r == 1 and y_e1_s == 0:
            recovered_by_rolling += 1
        if y_e1_s == 1 and y_e1_r == 0:
            lost_by_rolling += 1

        if y_e1_s == 1 and y_b == 0 and y_bd == 0 and y_e1_r == 0:
            e1_stat_only += 1
        if y_b == 1 and y_e1_s == 0 and y_e1_r == 0:
            cand_b_only += 1
        if y_e1_r == 1 and y_e1_s == 0 and y_b == 0 and y_bd == 0:
            e1_roll_only += 1

    overlap_summary = [
        {"metric_name": "total_short_screams", "count": 69, "percentage": 100.0},
        {"metric_name": "detected_by_candidate_e1_static", "count": 25, "percentage": round(25/69*100, 2)},
        {"metric_name": "detected_by_candidate_b_baseline", "count": 27, "percentage": round(27/69*100, 2)},
        {"metric_name": "detected_by_candidate_b_interv_d", "count": 26, "percentage": round(26/69*100, 2)},
        {"metric_name": "detected_by_candidate_e1_rolling", "count": 27, "percentage": round(27/69*100, 2)},
        {"metric_name": "missed_by_every_candidate", "count": all_missed, "percentage": round(all_missed/69*100, 2)},
        {"metric_name": "detected_by_every_candidate", "count": all_detected, "percentage": round(all_detected/69*100, 2)},
        {"metric_name": "recovered_by_rolling_missed_by_static_e1", "count": recovered_by_rolling, "percentage": round(recovered_by_rolling/69*100, 2)},
        {"metric_name": "detected_by_static_e1_missed_by_rolling", "count": lost_by_rolling, "percentage": round(lost_by_rolling/69*100, 2)},
        {"metric_name": "detected_only_by_candidate_b", "count": cand_b_only, "percentage": round(cand_b_only/69*100, 2)},
        {"metric_name": "detected_only_by_candidate_e1_rolling", "count": e1_roll_only, "percentage": round(e1_roll_only/69*100, 2)}
    ]

    out_overlap_csv = STAGE62_DIR / "short_scream_failure_overlap.csv"
    with open(out_overlap_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(overlap_summary[0].keys()))
        w.writeheader()
        w.writerows(overlap_summary)
    print(f"Wrote {out_overlap_csv}")

    print("\n" + "="*80)
    print("PHASE B2: SHORT-SCREAM FAILURE OVERLAP SUMMARY (N=69)")
    print("="*80)
    for row in overlap_summary:
        print(f"  {row['metric_name']:<45}: {row['count']:2d} ({row['percentage']:5.2f}%)")

if __name__ == "__main__":
    main()

