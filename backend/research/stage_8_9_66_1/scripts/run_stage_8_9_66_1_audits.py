#!/usr/bin/env python3
"""
STAGE 8.9.66.1 — Comprehensive Provenance, Leakage, and Unseen Evaluation Audit Engine
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
This system is an experimental acoustic research prototype and is not certified for life-safety use.
"""

import csv
import hashlib
import json
import math
import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
import scipy.io.wavfile as wav
import scipy.signal as signal
import torch
import torch.nn as nn

SCRIPT_DIR = Path(__file__).resolve().parent
STAGE66_1_DIR = SCRIPT_DIR.parent
REPORTS_DIR = STAGE66_1_DIR / "reports"
RESEARCH_DIR = STAGE66_1_DIR.parent
BACKEND_DIR = RESEARCH_DIR.parent
REPO_ROOT = BACKEND_DIR.parent

sys.path.insert(0, str(RESEARCH_DIR / "stage_8_9_57" / "dsp_implementations"))
from c5_combined import extract_subband_vector_c5, extract_phonation_stats_c5


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def load_audio_wav(path: Path):
    sr, raw = wav.read(path)
    if raw.ndim > 1:
        raw = np.mean(raw, axis=1)
    if raw.dtype == np.int16:
        aud = raw.astype(np.float32) / 32768.0
    elif raw.dtype == np.int32:
        aud = raw.astype(np.float32) / 2147483648.0
    else:
        aud = raw.astype(np.float32)
    return aud


def extract_short_branch_features(audio: np.ndarray, sr: int = 16000):
    n_250ms = int(0.250 * sr)
    if len(audio) < n_250ms:
        chunk = np.pad(audio, (0, n_250ms - len(audio)))
    else:
        frame_len = 400
        hop_len = 160
        windows = np.lib.stride_tricks.sliding_window_view(audio, frame_len)[::hop_len]
        frame_e = np.sum(windows ** 2, axis=1)
        best_frame = np.argmax(frame_e)
        center_samp = best_frame * hop_len
        start_samp = max(0, center_samp - n_250ms // 2)
        end_samp = min(len(audio), start_samp + n_250ms)
        if end_samp - start_samp < n_250ms:
            start_samp = max(0, end_samp - n_250ms)
        chunk = audio[start_samp:end_samp]
        if len(chunk) < n_250ms:
            chunk = np.pad(chunk, (0, n_250ms - len(chunk)))

    tiled = np.tile(chunk, 4)[:16000]
    norm = tiled / (np.max(np.abs(tiled)) + 1e-9)
    sb_v = extract_subband_vector_c5(norm, sr=sr)
    ac_v = extract_phonation_stats_c5(norm, sr=sr)
    return np.concatenate([sb_v, ac_v])


def extract_sustained_branch_features(audio: np.ndarray, sr: int = 16000):
    if len(audio) >= 16000:
        c = audio[len(audio)//2 - 8000 : len(audio)//2 + 8000]
    else:
        c = np.pad(audio, (0, 16000 - len(audio)))
    norm = c / (np.max(np.abs(c)) + 1e-9)
    sb_v = extract_subband_vector_c5(norm, sr=sr)
    ac_v = extract_phonation_stats_c5(norm, sr=sr)
    return np.concatenate([sb_v, ac_v])


def compute_audio_acoustics(audio: np.ndarray, sr: int = 16000):
    rms = float(np.sqrt(np.mean(audio**2) + 1e-9))
    if len(audio) < int(sr * 0.025):
        return 0.0, 0.0, rms
    b, a = signal.butter(2, 70.0 / (sr / 2.0), btype='high')
    filtered = signal.filtfilt(b, a, audio)
    min_lag = int(sr / 2000.0)
    max_lag = int(sr / 80.0)
    autocorr = signal.correlate(filtered, filtered, mode='full', method='fft')
    autocorr = autocorr[len(autocorr)//2:]
    r0 = autocorr[0]
    if r0 <= 1e-9 or len(autocorr) <= max_lag:
        hnr_db = 0.0
    else:
        norm_autocorr = autocorr / r0
        lag_range = norm_autocorr[min_lag:max_lag]
        r_max = float(np.max(lag_range))
        if r_max <= 0.01:
            hnr_db = -20.0
        elif r_max >= 0.999:
            hnr_db = 30.0
        else:
            hnr_db = float(np.clip(10.0 * np.log10(r_max / (1.0 - r_max + 1e-9)), -25.0, 35.0))
    f, pxx = signal.periodogram(audio, fs=sr)
    pxx = pxx + 1e-12
    flatness = float(np.exp(np.mean(np.log(pxx))) / np.mean(pxx))
    return float(hnr_db), float(flatness), float(rms)


class DualResolutionGatedModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.short_enc = nn.Sequential(
            nn.Linear(17, 32), nn.BatchNorm1d(32), nn.ReLU(), nn.Dropout(0.10), nn.Linear(32, 16), nn.ReLU()
        )
        self.sust_enc = nn.Sequential(
            nn.Linear(17, 32), nn.BatchNorm1d(32), nn.ReLU(), nn.Dropout(0.10), nn.Linear(32, 16), nn.ReLU()
        )
        self.gate_net = nn.Sequential(
            nn.Linear(32, 16), nn.ReLU(), nn.Linear(16, 1), nn.Sigmoid()
        )
        self.head = nn.Linear(16, 1)

    def forward(self, x_short, x_sust):
        z_s = self.short_enc(x_short)
        z_l = self.sust_enc(x_sust)
        fused_in = torch.cat([z_s, z_l], dim=-1)
        gate = self.gate_net(fused_in)
        z_fused = gate * z_s + (1.0 - gate) * z_l
        logits = self.head(z_fused).squeeze(-1)
        return logits, gate.squeeze(-1), z_s, z_l


def run_audits():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("STAGE 8.9.66.1 — AUDIT ENGINE EXECUTION")
    print("MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.")
    print("=" * 80)

    # 1. Load All Historical Manifests
    dev_path = RESEARCH_DIR / "stage_8_9_63" / "stage_63_development_manifest.csv"
    dev_df = pd.read_csv(dev_path)

    s54_path = RESEARCH_DIR / "stage_8_9_54" / "dataset" / "partition_manifest_verified.csv"
    s54_df = pd.read_csv(s54_path)

    s60_sealed_path = RESEARCH_DIR / "stage_8_9_60" / "future_evaluation_manifest.json"
    with open(s60_sealed_path, "r", encoding="utf-8") as f:
        s60_sealed_recs = json.load(f)["recordings"]
    s60_sealed_df = pd.DataFrame(s60_sealed_recs)

    s60_acq_path = RESEARCH_DIR / "stage_8_9_60" / "acquisition_manifest.csv"
    s60_acq_df = pd.read_csv(s60_acq_path)

    shout_path = RESEARCH_DIR / "stage_8_9_66" / "shouted_speech_manifest.csv"
    shout_df = pd.read_csv(shout_path)

    hn_path = RESEARCH_DIR / "stage_8_9_66" / "hard_negative_expansion_manifest.csv"
    hn_df = pd.read_csv(hn_path)

    short401_path = RESEARCH_DIR / "stage_8_9_64" / "stage_64_short_scream_manifest.csv"
    short401_df = pd.read_csv(short401_path)

    # 2. Build Overlap Matrix (Sub-stage 8.9.66.1.4)
    print("\n--- Computing Dataset Overlap Matrix ---")
    datasets = {
        "N=312 Development Cohort": dev_df,
        "Stage 54 Train Partition": s54_df[s54_df["expansion_partition"] == "expansion_train"],
        "Stage 54 Validation Partition": s54_df[s54_df["expansion_partition"] == "expansion_val"],
        "Stage 54 Reserved Test": s54_df[s54_df["expansion_partition"] == "expansion_reserved_test"],
        "Stage 60 Sealed Cohort (N=700)": s60_sealed_df,
        "Stage 64 Short Screams (N=401)": short401_df,
        "Stage 66 Shouted Speech (N=529)": shout_df,
        "Stage 66 Hard Negatives (N=462)": hn_df
    }

    overlap_rows = []
    ds_names = list(datasets.keys())
    for i, name1 in enumerate(ds_names):
        df1 = datasets[name1]
        pcm1 = set(df1["pcm_sha256"].dropna().values)
        sg1 = set(df1["source_group_id"].dropna().values)
        for j, name2 in enumerate(ds_names):
            df2 = datasets[name2]
            pcm2 = set(df2["pcm_sha256"].dropna().values)
            sg2 = set(df2["source_group_id"].dropna().values)
            exact_overlap = len(pcm1.intersection(pcm2))
            sg_overlap = len(sg1.intersection(sg2))
            overlap_rows.append({
                "dataset_a": name1,
                "dataset_b": name2,
                "dataset_a_count": len(df1),
                "dataset_b_count": len(df2),
                "exact_pcm_overlap": exact_overlap,
                "source_group_overlap": sg_overlap,
                "pct_pcm_overlap_of_a": round(exact_overlap / len(df1) * 100, 2) if len(df1) > 0 else 0.0
            })

    overlap_df = pd.DataFrame(overlap_rows)
    overlap_csv = REPORTS_DIR / "recording_source_group_overlap_matrix.csv"
    overlap_df.to_csv(overlap_csv, index=False)
    print(f"Emitted {overlap_csv.name}.")

    # 3. Classify Newly Acquired Negatives (Sub-stage 8.9.66.1.5)
    print("\n--- Classifying Expanded Negatives Exposure ---")
    dev_pcm = set(dev_df["pcm_sha256"])
    dev_sg = set(dev_df["source_group_id"])
    s60_pcm = set(s60_sealed_df["pcm_sha256"])
    s60_sg = set(s60_sealed_df["source_group_id"])
    s54_part_map = dict(zip(s54_df["pcm_sha256"], s54_df["expansion_partition"]))

    exposure_records = []
    for _, r in shout_df.iterrows():
        pcm = r["pcm_sha256"]
        sg = r["source_group_id"]
        rid = r["recording_id"]
        if pcm in dev_pcm:
            exp_status = "PREVIOUSLY_EXPOSED"
            exp_detail = "In N=312 Development Cohort (s60_rec_0332)"
            is_unseen = False
        elif sg in dev_sg:
            exp_status = "SOURCE_GROUP_OVERLAP"
            exp_detail = "Source group present in N=312 Development Cohort"
            is_unseen = False
        elif pcm in s60_pcm:
            exp_status = "PREVIOUSLY_EXPOSED"
            exp_detail = "Member of Stage 60 Sealed Cohort (Must Remain Sealed)"
            is_unseen = False
        elif sg in s60_sg:
            exp_status = "SOURCE_GROUP_OVERLAP"
            exp_detail = "Source group present in Stage 60 Sealed Cohort"
            is_unseen = False
        elif pcm in s54_part_map:
            part = s54_part_map[pcm]
            if part in ("expansion_train", "expansion_val"):
                exp_status = "PREVIOUSLY_EXPOSED"
                exp_detail = f"In Stage 54 {part} (historical Candidate E1 training/val)"
                is_unseen = False
            elif part == "expansion_reserved_test":
                exp_status = "CONFIRMED_UNSEEN"
                exp_detail = "Stage 54 Reserved Test (Never used in Dual-Res training/tuning/selection)"
                is_unseen = True
            else:
                exp_status = "UNKNOWN_PROVENANCE"
                exp_detail = f"Stage 54 partition {part}"
                is_unseen = False
        else:
            exp_status = "UNKNOWN_PROVENANCE"
            exp_detail = "Unindexed acquisition file"
            is_unseen = False

        exposure_records.append({
            "cohort": "shouted_speech",
            "recording_id": rid,
            "source_group_id": sg,
            "duration_seconds": r["duration_seconds"],
            "license": r["license"],
            "exposure_classification": exp_status,
            "exposure_detail": exp_detail,
            "eligible_for_frozen_inference": is_unseen
        })

    for _, r in hn_df.iterrows():
        pcm = r["pcm_sha256"]
        sg = r["source_group_id"]
        rid = r["recording_id"]
        if pcm in dev_pcm:
            exp_status = "PREVIOUSLY_EXPOSED"
            exp_detail = "In N=312 Development Cohort (used in 65-F training/tuning)"
            is_unseen = False
        elif sg in dev_sg:
            exp_status = "SOURCE_GROUP_OVERLAP"
            exp_detail = "Source group present in N=312 Development Cohort"
            is_unseen = False
        elif pcm in s60_pcm:
            exp_status = "PREVIOUSLY_EXPOSED"
            exp_detail = "Member of Stage 60 Sealed Cohort (Must Remain Sealed)"
            is_unseen = False
        elif sg in s60_sg:
            exp_status = "SOURCE_GROUP_OVERLAP"
            exp_detail = "Source group present in Stage 60 Sealed Cohort"
            is_unseen = False
        else:
            exp_status = "CONFIRMED_UNSEEN"
            exp_detail = "Unconsumed acquisition pool (Not in Dev or Sealed)"
            is_unseen = True

        exposure_records.append({
            "cohort": "hard_negatives",
            "recording_id": rid,
            "source_group_id": sg,
            "duration_seconds": r["duration_seconds"],
            "license": r["license"],
            "exposure_classification": exp_status,
            "exposure_detail": exp_detail,
            "eligible_for_frozen_inference": is_unseen
        })

    exp_df = pd.DataFrame(exposure_records)
    exp_csv = REPORTS_DIR / "dataset_exposure_classification.csv"
    exp_df.to_csv(exp_csv, index=False)
    print(f"Emitted {exp_csv.name} ({len(exp_df)} records).")

    print("\n--- Shouted Speech Exposure Summary ---")
    print(exp_df[exp_df["cohort"] == "shouted_speech"]["exposure_classification"].value_counts())

    print("\n--- Hard Negative Exposure Summary ---")
    print(exp_df[exp_df["cohort"] == "hard_negatives"]["exposure_classification"].value_counts())

    # 4. Frozen Inference on Eligible Unseen Shouted-Speech (Sub-stage 8.9.66.1.5 & 6.1)
    # The 111 shouted speech files from Stage 54 expansion_reserved_test are confirmed unseen by Candidate 65-F!
    eligible_shout = exp_df[(exp_df["cohort"] == "shouted_speech") & (exp_df["eligible_for_frozen_inference"] == True)]
    print(f"\n--- Running Frozen Inference on {len(eligible_shout)} Eligible Unseen Shouted-Speech Files ---")

    ckpt_path = RESEARCH_DIR / "stage_8_9_66" / "models" / "candidate_65f_frozen.pt"
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=True)
    model = DualResolutionGatedModel()
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()

    shout_pred_rows = []
    shout_dict = dict(zip(shout_df["recording_id"], shout_df["workspace_audio_path"]))

    for _, r in eligible_shout.iterrows():
        rid = r["recording_id"]
        rel_path = shout_dict[rid]
        aud = load_audio_wav(REPO_ROOT / rel_path)
        f_s = extract_short_branch_features(aud)
        f_l = extract_sustained_branch_features(aud)
        hnr, flat, rms = compute_audio_acoustics(aud)

        with torch.no_grad():
            t_s = torch.tensor(f_s, dtype=torch.float32).unsqueeze(0)
            t_l = torch.tensor(f_l, dtype=torch.float32).unsqueeze(0)
            logit, gate, z_s, z_l = model(t_s, t_l)
            raw_p = float(torch.sigmoid(logit).item())
            zs_v = z_s.squeeze(0).numpy()
            zl_v = z_l.squeeze(0).numpy()
            sim = float(np.dot(zs_v, zl_v) / (np.linalg.norm(zs_v) * np.linalg.norm(zl_v) + 1e-7))

            # Apply candidate 65-f selective suppression
            calib_p = raw_p
            if not (raw_p >= 0.80 or sim > 0.40):
                if hnr > 12.0 and flat < 0.001:
                    calib_p *= 0.15

            pred = int(calib_p >= 0.48)

            shout_pred_rows.append({
                "recording_id": rid,
                "source_group_id": r["source_group_id"],
                "ground_truth": 0,
                "raw_probability": round(raw_p, 5),
                "calibrated_probability": round(calib_p, 5),
                "branch_cosine_similarity": round(sim, 4),
                "hnr_db": round(hnr, 2),
                "spectral_flatness": round(flat, 6),
                "prediction": pred,
                "false_positive": pred,
                "true_negative": 1 - pred
            })

    shout_pred_df = pd.DataFrame(shout_pred_rows)
    shout_pred_csv = REPORTS_DIR / "frozen_inference_shouted_speech_predictions.csv"
    shout_pred_df.to_csv(shout_pred_csv, index=False)
    print(f"Emitted {shout_pred_csv.name}.")

    n_eval = len(shout_pred_df)
    n_fp = shout_pred_df["false_positive"].sum()
    fpr_shout = n_fp / n_eval

    # 95% Wilson score confidence interval
    z = 1.95996
    denom = 1.0 + (z**2) / n_eval
    center = (fpr_shout + (z**2) / (2 * n_eval)) / denom
    margin = (z * math.sqrt((fpr_shout * (1.0 - fpr_shout) + (z**2) / (4 * n_eval)) / n_eval)) / denom
    ci_lower = max(0.0, center - margin)
    ci_upper = min(1.0, center + margin)

    print(f"\nFrozen Inference Results on Unseen Shouted-Speech (N={n_eval}):")
    print(f"  False Positives: {n_fp} / {n_eval}")
    print(f"  Observed Shouted-Speech FPR: {fpr_shout*100:.2f}% (95% CI: [{ci_lower*100:.2f}%, {ci_upper*100:.2f}%])")
    print(f"  Gate 3 Requirement (<= 15.00%): {'PASS' if fpr_shout <= 0.150 else 'FAIL (+{:.2f}% excess)'.format((fpr_shout - 0.150)*100)}")

    # 5. Checkpoint Hash Record (Sub-stage 8.9.66.1.7)
    ckpt_record = {
        "candidate_id": "Candidate_65_F_Combined_Selective",
        "frozen_checkpoint_relative_path": "backend/research/stage_8_9_66/models/candidate_65f_frozen.pt",
        "checkpoint_sha256": sha256_file(ckpt_path),
        "metadata_relative_path": "backend/research/stage_8_9_66/models/candidate_freeze_metadata.json",
        "metadata_sha256": sha256_file(RESEARCH_DIR / "stage_8_9_66" / "models" / "candidate_freeze_metadata.json"),
        "dsp_preprocessor_relative_path": "backend/research/stage_8_9_57/dsp_implementations/c5_combined.py",
        "dsp_preprocessor_sha256": sha256_file(RESEARCH_DIR / "stage_8_9_57" / "dsp_implementations" / "c5_combined.py"),
        "reproduction_script_relative_path": "backend/research/stage_8_9_66/scripts/reproduce_candidate_65f.py",
        "reproduction_script_sha256": sha256_file(RESEARCH_DIR / "stage_8_9_66" / "scripts" / "reproduce_candidate_65f.py"),
        "frozen_hyperparameters": {
            "decision_threshold": 0.48,
            "high_confidence_bypass": 0.80,
            "branch_cosine_agreement_threshold": 0.40,
            "narrow_band_whistle_hnr_db": 12.0,
            "narrow_band_whistle_flatness": 0.001,
            "attenuation_factor": 0.15
        },
        "audit_timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

    ckpt_json_path = REPORTS_DIR / "candidate_65f_checkpoint_hash_record.json"
    with open(ckpt_json_path, "w", encoding="utf-8") as f:
        json.dump(ckpt_record, f, indent=2)
    print(f"Emitted {ckpt_json_path.name}.")

    return {
        "overlap_matrix": overlap_df,
        "exposure_classification": exp_df,
        "shouted_inference": {
            "n_eval": n_eval,
            "n_fp": int(n_fp),
            "fpr": round(fpr_shout, 4),
            "ci_95": [round(ci_lower, 4), round(ci_upper, 4)],
            "gate3_pass": fpr_shout <= 0.150
        },
        "checkpoint_record": ckpt_record
    }


if __name__ == "__main__":
    run_audits()

