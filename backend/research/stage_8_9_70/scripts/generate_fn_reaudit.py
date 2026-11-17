# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
STAGE 8.9.70 — MULTI-LABEL FALSE NEGATIVE RE-AUDIT
Generates: backend/research/stage_8_9_70/reports/candidate69_false_negative_reaudit.csv
Audits overlapping failure mechanisms (reverberation, low SNR, raw underconfidence, active vetoes)
without forcing mutually exclusive classifications.

MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import torch

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "backend"))
STAGE_DIR = Path(__file__).resolve().parents[1]
REPORTS_DIR = STAGE_DIR / "reports"

from research.stage_8_9_67.scripts.train_and_evaluate_candidates import (
    DualResolutionGatedModel,
    normalize_vocal_features
)

val_data = np.load(REPO_ROOT / "backend/research/stage_8_9_67/cache/val_features.npz")
y = val_data["y"]
cats = val_data["categories"]
durs = val_data["durations"]
ids = val_data["ids"]
sg = val_data["source_groups"]
voc_norm = normalize_vocal_features(val_data["x_vocal"])
x_s_22 = np.concatenate([val_data["x_short"], voc_norm], axis=-1)
x_l_22 = np.concatenate([val_data["x_sust"], voc_norm], axis=-1)

x_voc = val_data["x_vocal"]
roughness = x_voc[:, 0]
hf_ratio = x_voc[:, 1]
flux = x_voc[:, 2]
hnr = x_voc[:, 3]
flatness = x_voc[:, 4]

# Load Stage 69 False Negative Forensics for acoustic measurements (SNR, RT60, etc.)
df_forensics = pd.read_csv(REPO_ROOT / "backend/research/stage_8_9_69/false_negative_forensic_analysis.csv")
forensic_map = {r["recording_id"]: r for _, r in df_forensics.iterrows()}

ckpt_69 = torch.load(REPO_ROOT / "backend/research/stage_8_9_69/models/candidate_69_frozen.pt", weights_only=False)
net = DualResolutionGatedModel(in_features=22)
net.load_state_dict(ckpt_69["model_state_dict"])
net.eval()

with torch.no_grad():
    t_s = torch.tensor(x_s_22, dtype=torch.float32)
    t_l = torch.tensor(x_l_22, dtype=torch.float32)
    logits, gate, z_s, z_l = net(t_s, t_l)
    raw_probs = torch.sigmoid(logits).numpy()
    zs_np = z_s.numpy()
    zl_np = z_l.numpy()

dot = np.sum(zs_np * zl_np, axis=1)
norm_s = np.linalg.norm(zs_np, axis=1) + 1e-7
norm_l = np.linalg.norm(zl_np, axis=1) + 1e-7
sim = dot / (norm_s * norm_l)

p_69 = raw_probs.copy()
v_w = np.zeros(len(p_69), bool)
v_hf = np.zeros(len(p_69), bool)
v_fl = np.zeros(len(p_69), bool)
v_voc = np.zeros(len(p_69), bool)

for i in range(len(p_69)):
    if not (raw_probs[i] >= 0.80 or sim[i] > 0.40):
        if hnr[i] > 12.0 and flatness[i] < 0.001:
            p_69[i] *= 0.15
            v_w[i] = True
    if hf_ratio[i] < 0.008 and roughness[i] < 0.050 and raw_probs[i] < 0.75:
        p_69[i] *= 0.20
        v_hf[i] = True
    if flux[i] < 0.036 and roughness[i] < 0.060 and raw_probs[i] < 0.75 and hf_ratio[i] <= 1.0:
        p_69[i] *= 0.20
        v_fl[i] = True
    if roughness[i] < 0.022 and hf_ratio[i] < 0.050 and raw_probs[i] < 0.85:
        p_69[i] *= 0.20
        v_voc[i] = True

pred = (p_69 >= 0.4920).astype(int)

# Identify all positive scream clips that were FNs in Candidate 68-D (N=25) or Candidate 69-D (N=20)
pos_idx = np.where(y == 1)[0]
fn_69_idx = set(np.where((y == 1) & (pred == 0))[0])
all_fn_ids = set(df_forensics["recording_id"]).union({ids[i] for i in fn_69_idx})

rows = []
for i in pos_idx:
    rec_id = ids[i]
    if rec_id not in all_fn_ids:
        continue

    f_meta = forensic_map.get(rec_id, {})
    snr_val = f_meta.get("snr_db", np.nan)
    rt60_val = f_meta.get("rt60_seconds", np.nan)
    clip_r = f_meta.get("clipping_ratio", 0.0)
    sil_r = f_meta.get("silence_ratio", 0.0)

    # Multi-label condition evaluation
    is_low_snr = (snr_val < 15.0) if pd.notna(snr_val) else (flatness[i] > 0.05)
    is_reverb = (rt60_val > 1.20) if pd.notna(rt60_val) else False
    is_underconf = (raw_probs[i] < 0.4920)
    active_vetoes = []
    if v_w[i]: active_vetoes.append("WHISTLE_VETO")
    if v_hf[i]: active_vetoes.append("HFCR_VETO")
    if v_fl[i]: active_vetoes.append("FLUX_VETO")
    if v_voc[i]: active_vetoes.append("VOCAL_DISTRESS_VETO")
    veto_str = "; ".join(active_vetoes) if active_vetoes else "NONE"

    # Multi-label mechanisms
    mechanisms = []
    if is_reverb: mechanisms.append("DIFFUSE_REVERBERATION_SMEARING")
    if is_low_snr: mechanisms.append("LOW_SNR_ENVIRONMENTAL_MASKING")
    if is_underconf: mechanisms.append("RAW_NEURAL_UNDERCONFIDENCE")
    if active_vetoes: mechanisms.append(f"VETO_ACTIVE({veto_str})")

    # Observed evidence vs Hypothesized explanation
    obs_evidence = f"p_raw={raw_probs[i]:.3f}, p_post={p_69[i]:.3f}, gate={gate.numpy()[i]:.3f}, sim={sim[i]:.3f}, R={roughness[i]:.4f}, HFCR={hf_ratio[i]:.4f}, Flux={flux[i]:.4f}, SNR={snr_val:.1f}dB, RT60={rt60_val:.2f}s"
    hyp_explanation = " + ".join(mechanisms) if mechanisms else "UNIDENTIFIED"

    rows.append({
        "recording_id": rec_id,
        "source_group_id": sg[i],
        "ground_truth_label": 1,
        "duration_seconds": round(float(durs[i]), 3),
        "raw_neural_prob": round(float(raw_probs[i]), 4),
        "post_veto_prob_69d": round(float(p_69[i]), 4),
        "prediction_69d": int(pred[i]),
        "status_69d": "RESCUED_TP" if pred[i] == 1 else "FALSE_NEGATIVE",
        "snr_db_measured": round(float(snr_val), 2) if pd.notna(snr_val) else "N/A",
        "rt60_seconds_measured": round(float(rt60_val), 2) if pd.notna(rt60_val) else "N/A",
        "branch_cosine_agreement": round(float(sim[i]), 3),
        "gate_weight_short": round(float(gate.numpy()[i]), 3),
        "active_vetoes_69d": veto_str,
        "multi_label_reverberation": bool(is_reverb),
        "multi_label_low_snr": bool(is_low_snr),
        "multi_label_underconfidence": bool(is_underconf),
        "multi_label_veto_suppression": bool(len(active_vetoes) > 0),
        "observed_empirical_evidence": obs_evidence,
        "hypothesized_co_occurring_mechanisms": hyp_explanation
    })

df_out = pd.DataFrame(rows)
out_csv = REPORTS_DIR / "candidate69_false_negative_reaudit.csv"
df_out.to_csv(out_csv, index=False)
print(f"Generated multi-label false-negative re-audit table: {out_csv} ({len(df_out)} rows)")

# Print overlap summary
print("\nMulti-Label Failure Mode Co-occurrence Analysis:")
print(f"  Total False Negatives evaluated: {len(df_out)}")
print(f"  Reverberation smearing:           {df_out['multi_label_reverberation'].sum()}/{len(df_out)} ({df_out['multi_label_reverberation'].mean()*100:.1f}%)")
print(f"  Low SNR masking:                 {df_out['multi_label_low_snr'].sum()}/{len(df_out)} ({df_out['multi_label_low_snr'].mean()*100:.1f}%)")
print(f"  Raw neural underconfidence:      {df_out['multi_label_underconfidence'].sum()}/{len(df_out)} ({df_out['multi_label_underconfidence'].mean()*100:.1f}%)")
print(f"  Active veto suppression:         {df_out['multi_label_veto_suppression'].sum()}/{len(df_out)} ({df_out['multi_label_veto_suppression'].mean()*100:.1f}%)")

# Co-occurrence pairs
reverb_and_snr = (df_out['multi_label_reverberation'] & df_out['multi_label_low_snr']).sum()
reverb_and_underconf = (df_out['multi_label_reverberation'] & df_out['multi_label_underconfidence']).sum()
underconf_and_veto = (df_out['multi_label_underconfidence'] & df_out['multi_label_veto_suppression']).sum()
print(f"\nCo-occurring Overlaps:")
print(f"  Reverberation + Low SNR:                 {reverb_and_snr} clips")
print(f"  Reverberation + Neural Underconfidence:  {reverb_and_underconf} clips")
print(f"  Neural Underconfidence + Veto:           {underconf_and_veto} clips")

