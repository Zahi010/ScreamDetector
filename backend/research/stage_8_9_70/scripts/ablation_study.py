# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
STAGE 8.9.70 — CONTROLLED VETO ARCHITECTURE ABLATIONS (A THROUGH G)
Evaluates:
A. Full Candidate 69-D (All 4 vetoes)
B. Candidate 69-D without narrowband whistle veto
C. Candidate 69-D without roughness-conditioned HFCR veto
D. Candidate 69-D without high-frequency-bypassed flux veto
E. Candidate 69-D without calibrated vocal distress veto
F. Candidate 69-D with minimal necessary suppression mechanisms (Whistle + Vocal Distress only)
G. Candidate 69-D without ANY post-neural vetoes (Raw neural logits at th=0.4920)

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

pos_m = (y == 1)
shout_m = (cats == "shouting_and_speech")
hn_m = (y == 0) & (~shout_m)
short_m = pos_m & (durs < 1.0)

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

def evaluate_ablation(name, whistle=True, hfcr=True, flux_v=True, vocal=True, th=0.4920):
    p = raw_probs.copy()
    for i in range(len(p)):
        if whistle:
            if not (raw_probs[i] >= 0.80 or sim[i] > 0.40):
                if hnr[i] > 12.0 and flatness[i] < 0.001:
                    p[i] *= 0.15
        if hfcr:
            if hf_ratio[i] < 0.008 and roughness[i] < 0.050 and raw_probs[i] < 0.75:
                p[i] *= 0.20
        if flux_v:
            if flux[i] < 0.036 and roughness[i] < 0.060 and raw_probs[i] < 0.75:
                if hf_ratio[i] <= 1.0:
                    p[i] *= 0.20
        if vocal:
            if roughness[i] < 0.022 and hf_ratio[i] < 0.050 and raw_probs[i] < 0.85:
                p[i] *= 0.20
    pred = (p >= th).astype(int)
    
    tp = int(np.sum(pred[pos_m]))
    fn = int(len(pred[pos_m]) - tp)
    rec = float(tp / len(pred[pos_m]) * 100)
    
    sh_fp = int(np.sum(pred[shout_m]))
    sh_tn = int(len(pred[shout_m]) - sh_fp)
    sh_fpr = float(sh_fp / len(pred[shout_m]) * 100)
    
    hn_fp = int(np.sum(pred[hn_m]))
    hn_tn = int(len(pred[hn_m]) - hn_fp)
    hn_fpr = float(hn_fp / len(pred[hn_m]) * 100)
    
    sh_tp = int(np.sum(pred[short_m]))
    sh_fn = int(len(pred[short_m]) - sh_tp)
    sh_rec = float(sh_tp / len(pred[short_m]) * 100)
    
    return {
        "ablation_id": name,
        "whistle": whistle, "hfcr": hfcr, "flux": flux_v, "vocal": vocal,
        "overall_tp": tp, "overall_fn": fn, "overall_recall": round(rec, 2),
        "shouted_fp": sh_fp, "shouted_tn": sh_tn, "shouted_fpr": round(sh_fpr, 2),
        "hard_neg_fp": hn_fp, "hard_neg_tn": hn_tn, "hard_neg_fpr": round(hn_fpr, 2),
        "short_scream_tp": sh_tp, "short_scream_fn": sh_fn, "short_scream_recall": round(sh_rec, 2),
        "calib_probs": p, "preds": pred
    }

res_a = evaluate_ablation("A: Full Candidate 69-D", whistle=True, hfcr=True, flux_v=True, vocal=True)
res_b = evaluate_ablation("B: No Whistle Veto", whistle=False, hfcr=True, flux_v=True, vocal=True)
res_c = evaluate_ablation("C: No HFCR Veto", whistle=True, hfcr=False, flux_v=True, vocal=True)
res_d = evaluate_ablation("D: No Flux Veto", whistle=True, hfcr=True, flux_v=False, vocal=True)
res_e = evaluate_ablation("E: No Vocal Distress Veto", whistle=True, hfcr=True, flux_v=True, vocal=False)
res_f = evaluate_ablation("F: Minimal (Whistle + Vocal Only)", whistle=True, hfcr=False, flux_v=False, vocal=True)
res_g = evaluate_ablation("G: Zero Vetoes (Raw Neural Only)", whistle=False, hfcr=False, flux_v=False, vocal=False)

ablations = [res_a, res_b, res_c, res_d, res_e, res_f, res_g]

# Print Comparison Table
print("=" * 100)
print("STAGE 8.9.70 — VETO ARCHITECTURE ABLATION STUDY RESULTS (STAGE 54 VAL N=311)")
print("=" * 100)
summary_rows = []
base_pred = res_a["preds"]

for res in ablations:
    cur_pred = res["preds"]
    tp_gained = int(np.sum((base_pred == 0) & (cur_pred == 1) & pos_m))
    tp_lost = int(np.sum((base_pred == 1) & (cur_pred == 0) & pos_m))
    sh_fp_gained = int(np.sum((base_pred == 0) & (cur_pred == 1) & shout_m))
    sh_fp_lost = int(np.sum((base_pred == 1) & (cur_pred == 0) & shout_m))
    hn_fp_gained = int(np.sum((base_pred == 0) & (cur_pred == 1) & hn_m))
    hn_fp_lost = int(np.sum((base_pred == 1) & (cur_pred == 0) & hn_m))
    
    summary_rows.append({
        "ablation_id": res["ablation_id"],
        "recall": f"{res['overall_recall']}% ({res['overall_tp']}/99)",
        "tp_delta": f"+{tp_gained}/-{tp_lost}" if res["ablation_id"] != res_a["ablation_id"] else "0",
        "shouted_fpr": f"{res['shouted_fpr']}% ({res['shouted_fp']}/88)",
        "shout_fp_delta": f"+{sh_fp_gained}/-{sh_fp_lost}" if res["ablation_id"] != res_a["ablation_id"] else "0",
        "hard_neg_fpr": f"{res['hard_neg_fpr']}% ({res['hard_neg_fp']}/124)",
        "hn_fp_delta": f"+{hn_fp_gained}/-{hn_fp_lost}" if res["ablation_id"] != res_a["ablation_id"] else "0",
        "short_recall": f"{res['short_scream_recall']}% ({res['short_scream_tp']}/39)"
    })

df_sum = pd.DataFrame(summary_rows)
print(df_sum.to_string(index=False))

# Export to CSV
out_csv = STAGE_DIR / "reports/veto_ablation_results.csv"
export_df = pd.DataFrame([{k: v for k, v in r.items() if k not in ("calib_probs", "preds")} for r in ablations])
export_df.to_csv(out_csv, index=False)
print(f"\nWrote veto ablation results to {out_csv}")

