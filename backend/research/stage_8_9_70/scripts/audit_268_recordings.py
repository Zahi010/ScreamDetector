# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
AUDIT 268-CLIP SHORT-SCREAM PERFORMANCE GAP & SUBGROUP BREAKDOWN
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import torch

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "backend"))

from research.stage_8_9_67.scripts.train_and_evaluate_candidates import (
    DualResolutionGatedModel,
    normalize_vocal_features
)

ho_data = np.load(REPO_ROOT / "backend/research/stage_8_9_67/cache/held_out_short_features.npz")
voc_ho_clean = normalize_vocal_features(ho_data["x_vocal"])
x_s_ho = np.concatenate([ho_data["x_short"], voc_ho_clean], axis=-1)
x_l_ho = np.concatenate([ho_data["x_sust"], voc_ho_clean], axis=-1)

ckpt_69 = torch.load(REPO_ROOT / "backend/research/stage_8_9_69/models/candidate_69_frozen.pt", weights_only=False)
net = DualResolutionGatedModel(in_features=22)
net.load_state_dict(ckpt_69["model_state_dict"])
net.eval()

with torch.no_grad():
    t_s = torch.tensor(x_s_ho, dtype=torch.float32)
    t_l = torch.tensor(x_l_ho, dtype=torch.float32)
    logits, gate, z_s, z_l = net(t_s, t_l)
    raw_probs = torch.sigmoid(logits).numpy()
    zs_np = z_s.numpy()
    zl_np = z_l.numpy()

dot = np.sum(zs_np * zl_np, axis=1)
norm_s = np.linalg.norm(zs_np, axis=1) + 1e-7
norm_l = np.linalg.norm(zl_np, axis=1) + 1e-7
sim = dot / (norm_s * norm_l)

x_voc = ho_data["x_vocal"]
roughness, hf_ratio, flux, hnr, flatness = [x_voc[:, i] for i in range(5)]
durs = ho_data["durations"]
sg = ho_data["source_groups"]
ids = ho_data["ids"]

p = raw_probs.copy()
v_w = np.zeros(len(p), bool)
v_hf = np.zeros(len(p), bool)
v_fl = np.zeros(len(p), bool)
v_voc = np.zeros(len(p), bool)

for i in range(len(p)):
    if not (raw_probs[i] >= 0.80 or sim[i] > 0.40):
        if hnr[i] > 12.0 and flatness[i] < 0.001:
            p[i] *= 0.15
            v_w[i] = True
    if hf_ratio[i] < 0.008 and roughness[i] < 0.050 and raw_probs[i] < 0.75:
        p[i] *= 0.20
        v_hf[i] = True
    if flux[i] < 0.036 and roughness[i] < 0.060 and raw_probs[i] < 0.75:
        if hf_ratio[i] <= 1.0:
            p[i] *= 0.20
            v_fl[i] = True
    if roughness[i] < 0.022 and hf_ratio[i] < 0.050 and raw_probs[i] < 0.85:
        p[i] *= 0.20
        v_voc[i] = True

th = 0.4920
pred = (p >= th).astype(int)

df = pd.DataFrame({
    "id": ids, "source_group": sg, "duration": durs,
    "raw_prob": raw_probs, "calib_prob": p, "pred": pred,
    "v_whistle": v_w, "v_hfcr": v_hf, "v_flux": v_fl, "v_vocal": v_voc
})

tp_count = int(df["pred"].sum())
total_count = len(df)
rec = float(df["pred"].mean() * 100)
print(f"Total: {total_count}, TP: {tp_count}, FN: {total_count - tp_count}, Recall: {rec:.2f}%\n")

b1 = df[df["duration"] <= 0.250]
b2 = df[(df["duration"] > 0.250) & (df["duration"] <= 0.500)]
b3 = df[(df["duration"] > 0.500) & (df["duration"] <= 1.000)]
b4 = df[df["duration"] > 1.000]

print(f"0–250 ms:    {b1['pred'].sum()}/{len(b1)} = {b1['pred'].mean()*100:.2f}% (count={len(b1)})")
print(f"250–500 ms:  {b2['pred'].sum()}/{len(b2)} = {b2['pred'].mean()*100:.2f}% (count={len(b2)})")
print(f"500–1000 ms: {b3['pred'].sum()}/{len(b3)} = {b3['pred'].mean()*100:.2f}% (count={len(b3)})")
print(f">1000 ms:    {b4['pred'].sum()}/{len(b4)} = {b4['pred'].mean()*100:.2f}% (count={len(b4)})")

print("\nRecall by Source Group:")
for grp, gdf in df.groupby("source_group"):
    print(f"  {grp:15}: {gdf['pred'].sum():3d}/{len(gdf):3d} = {gdf['pred'].mean()*100:6.2f}% | mean_raw={gdf['raw_prob'].mean():.3f} | mean_calib={gdf['calib_prob'].mean():.3f}")

print("\nAmong 112 False Negatives:")
fn_df = df[df["pred"] == 0]
raw_low = (fn_df["raw_prob"] < 0.4920).sum()
raw_hi = (fn_df["raw_prob"] >= 0.4920).sum()
print(f"  raw_prob < 0.4920 (inherent neural underconfidence): {raw_low}/{len(fn_df)} ({raw_low/len(fn_df)*100:.1f}%)")
print(f"  raw_prob >= 0.4920 (suppressed by veto):             {raw_hi}/{len(fn_df)} ({raw_hi/len(fn_df)*100:.1f}%)")
print(f"  Veto triggers among FNs: Whistle={fn_df['v_whistle'].sum()}, HFCR={fn_df['v_hfcr'].sum()}, Flux={fn_df['v_flux'].sum()}, Vocal={fn_df['v_vocal'].sum()}")

# Export subgroup results to CSV
out_csv = REPO_ROOT / "backend/research/stage_8_9_70/reports/short_scream_268_subgroup_results.csv"
subgroups_data = [
    {"duration_subgroup": "0-250 ms", "count": len(b1), "tp": int(b1['pred'].sum()), "fn": len(b1) - int(b1['pred'].sum()), "recall": round(float(b1['pred'].mean()*100), 2)},
    {"duration_subgroup": "250-500 ms", "count": len(b2), "tp": int(b2['pred'].sum()), "fn": len(b2) - int(b2['pred'].sum()), "recall": round(float(b2['pred'].mean()*100), 2)},
    {"duration_subgroup": "500-1000 ms", "count": len(b3), "tp": int(b3['pred'].sum()), "fn": len(b3) - int(b3['pred'].sum()), "recall": round(float(b3['pred'].mean()*100), 2)},
    {"duration_subgroup": ">1000 ms", "count": len(b4), "tp": int(b4['pred'].sum()), "fn": len(b4) - int(b4['pred'].sum()), "recall": 0.0 if len(b4)==0 else round(float(b4['pred'].mean()*100), 2)},
]
pd.DataFrame(subgroups_data).to_csv(out_csv, index=False)
print(f"\nWrote subgroup results to {out_csv}")

