# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
Evaluates frozen Candidate 65-F on Stage 54 Validation Cohort (expansion_val, N=311).
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import sys
import math
from pathlib import Path
import pandas as pd
import numpy as np
import torch

REPO_ROOT = Path(__file__).resolve().parents[4]
STAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "backend/research/stage_8_9_57/dsp_implementations"))
sys.path.insert(0, str(REPO_ROOT / "backend/research/stage_8_9_66/scripts"))

from reproduce_candidate_65f import (
    DualResolutionGatedModel,
    extract_short_branch_features,
    extract_sustained_branch_features,
    compute_audio_acoustics,
    load_audio_wav,
)

def evaluate_65f():
    checkpoint_path = REPO_ROOT / "backend/research/stage_8_9_66/models/candidate_65f_frozen.pt"
    ckpt = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    model = DualResolutionGatedModel()
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()

    s54_path = REPO_ROOT / "backend/research/stage_8_9_54/dataset/partition_manifest_verified.csv"
    df = pd.read_csv(s54_path)
    val_df = df[df["expansion_partition"] == "expansion_val"].copy()

    records = []
    print(f"Evaluating Candidate 65-F on Stage 54 Validation (N={len(val_df)})...")
    for idx, row in val_df.iterrows():
        audio_path = REPO_ROOT / row["workspace_audio_path"]
        aud = load_audio_wav(audio_path)
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

            calib_p = raw_p
            if not (raw_p >= 0.80 or sim > 0.40):
                if hnr > 12.0 and flat < 0.001:
                    calib_p *= 0.15

            pred = int(calib_p >= 0.48)

        records.append({
            "recording_id": row["original_recording_id"],
            "source_group_id": row["source_group_id"],
            "binary_label": row["binary_label"],
            "target_category": row["target_category"],
            "duration_seconds": row["duration_seconds"],
            "raw_p": raw_p,
            "calib_p": calib_p,
            "cosine_sim": sim,
            "hnr_db": hnr,
            "flatness": flat,
            "prediction": pred,
        })

    res_df = pd.DataFrame(records)
    out_csv = STAGE_DIR / "reports" / "candidate_65f_val_predictions.csv"
    res_df.to_csv(out_csv, index=False)
    print(f"Saved predictions to {out_csv}")

    # Metrics
    pos = res_df[res_df["binary_label"] == 1]
    tp = (pos["prediction"] == 1).sum()
    fn = (pos["prediction"] == 0).sum()
    recall = tp / len(pos)

    shout = res_df[res_df["target_category"] == "shouting_and_speech"]
    shout_fp = (shout["prediction"] == 1).sum()
    shout_tn = (shout["prediction"] == 0).sum()
    shout_fpr = shout_fp / len(shout)

    hn = res_df[(res_df["binary_label"] == 0) & (res_df["target_category"] != "shouting_and_speech")]
    hn_fp = (hn["prediction"] == 1).sum()
    hn_tn = (hn["prediction"] == 0).sum()
    hn_fpr = hn_fp / len(hn)

    short_scream = pos[pos["duration_seconds"] < 1.0]
    short_tp = (short_scream["prediction"] == 1).sum()
    short_recall = short_tp / len(short_scream)

    ultra_short = pos[pos["duration_seconds"] <= 0.5]
    ultra_tp = (ultra_short["prediction"] == 1).sum()
    ultra_recall = ultra_tp / len(ultra_short)

    print("\n" + "="*80)
    print("FROZEN CANDIDATE 65-F PERFORMANCE ON STAGE 54 VALIDATION (N=311)")
    print("="*80)
    print(f"Gate 1 (Overall Recall >= 96.0%): {recall*100:.2f}% ({tp}/{len(pos)}) -> {'PASS' if recall >= 0.96 else 'FAIL'}")
    print(f"Gate 2 (Hard-Negative FPR <= 5.0%): {hn_fpr*100:.2f}% ({hn_fp}/{len(hn)}) -> {'PASS' if hn_fpr <= 0.05 else 'FAIL'}")
    print(f"Gate 3 (Shouted-Speech FPR <= 15.0%): {shout_fpr*100:.2f}% ({shout_fp}/{len(shout)}) -> {'PASS' if shout_fpr <= 0.15 else 'FAIL (+{:.2f}% excess)'.format((shout_fpr-0.15)*100)}")
    print(f"Gate 4 (Short-Scream Recall >= 90.0%): {short_recall*100:.2f}% ({short_tp}/{len(short_scream)}) -> {'PASS' if short_recall >= 0.90 else 'FAIL'}")
    print(f"Ultra-Short Recall (<=0.5s): {ultra_recall*100:.2f}% ({ultra_tp}/{len(ultra_short)})")

if __name__ == "__main__":
    evaluate_65f()

