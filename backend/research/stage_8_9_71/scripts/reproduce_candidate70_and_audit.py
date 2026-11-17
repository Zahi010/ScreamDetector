# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
STAGE 8.9.71 — INDEPENDENT REPRODUCTION & FALSE-POSITIVE FORENSIC AUDIT
Reproduces Candidate 70-D performance across all statistical dimensions and
extracts detailed forensics for the 12 Hard-Negative False Positives.

MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from sklearn.metrics import (
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    precision_recall_curve,
    auc,
    brier_score_loss
)

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "backend"))
STAGE_DIR = Path(__file__).resolve().parents[1]
REPORTS_DIR = STAGE_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

from research.stage_8_9_67.scripts.train_and_evaluate_candidates import (
    DualResolutionGatedModel,
    normalize_vocal_features
)

# 1. Load Data
val_data = np.load(REPO_ROOT / "backend/research/stage_8_9_67/cache/val_features.npz")
ho_data = np.load(REPO_ROOT / "backend/research/stage_8_9_67/cache/held_out_short_features.npz")

y_val = val_data["y"]
cats_val = val_data["categories"]
durs_val = val_data["durations"]
sgs_val = val_data["source_groups"]
ids_val = val_data["ids"]

pos_m = (y_val == 1)
shout_m = (cats_val == "shouting_and_speech")
hn_m = (y_val == 0) & (~shout_m)
short_m = pos_m & (durs_val < 1.0)

roughness = val_data["x_vocal"][:, 0]
hf_ratio = val_data["x_vocal"][:, 1]
flux = val_data["x_vocal"][:, 2]
hnr = val_data["x_vocal"][:, 3]
flatness = val_data["x_vocal"][:, 4]

voc_val = normalize_vocal_features(val_data["x_vocal"])
x_s_val = np.concatenate([val_data["x_short"], voc_val], axis=-1)
x_l_val = np.concatenate([val_data["x_sust"], voc_val], axis=-1)

# 2. Load Frozen Candidate 70-D Checkpoint
ckpt_70_path = REPO_ROOT / "backend/research/stage_8_9_70/models/candidate_70_frozen.pt"
ckpt_70 = torch.load(ckpt_70_path, weights_only=False)
net_70 = DualResolutionGatedModel(in_features=22)
net_70.load_state_dict(ckpt_70["model_state_dict"])
net_70.eval()

# 3. Model Forward Pass
with torch.no_grad():
    t_s = torch.tensor(x_s_val, dtype=torch.float32)
    t_l = torch.tensor(x_l_val, dtype=torch.float32)
    logits_70, gate_70, z_s_70, z_l_70 = net_70(t_s, t_l)
    raw_probs = torch.sigmoid(logits_70).numpy()
    zs_np = z_s_70.numpy()
    zl_np = z_l_70.numpy()
    sim = np.sum(zs_np * zl_np, axis=1) / ((np.linalg.norm(zs_np, axis=1) + 1e-7) * (np.linalg.norm(zl_np, axis=1) + 1e-7))

# 4. Candidate 70-D Post-Processing
p_70 = raw_probs.copy()
active_vetoes_record = []

for i in range(len(p_70)):
    vetoes = []
    # 1. Whistle Veto
    if not (raw_probs[i] >= 0.80 or sim[i] > 0.40):
        if hnr[i] > 12.0 and flatness[i] < 0.001:
            p_70[i] *= 0.15
            vetoes.append("whistle_veto")
    # 2. Conditioned Flux Speech Veto (HFCR is pruned)
    if flux[i] < 0.036 and roughness[i] < 0.060 and raw_probs[i] < 0.75 and hf_ratio[i] <= 1.0:
        p_70[i] *= 0.20
        vetoes.append("flux_veto")
    # 3. Calibrated Vocal Distress Veto
    if roughness[i] < 0.022 and hf_ratio[i] < 0.050 and raw_probs[i] < 0.85:
        p_70[i] *= 0.20
        vetoes.append("vocal_distress_veto")
    # 4. Resonance Agreement Rescue
    if sim[i] > 0.78 and hf_ratio[i] > 0.12 and raw_probs[i] > 0.40:
        p_70[i] = min(0.99, p_70[i] + 0.035)
        vetoes.append("resonance_rescue")

    active_vetoes_record.append("+".join(vetoes) if vetoes else "none")

threshold = 0.4920
pred_70 = (p_70 >= threshold).astype(int)

# 5. Core Statistical Metrics on Validation Cohort (N=311)
tp = int(np.sum((pred_70 == 1) & pos_m))
fn = int(np.sum((pred_70 == 0) & pos_m))
fp_total = int(np.sum((pred_70 == 1) & (~pos_m)))
tn_total = int(np.sum((pred_70 == 0) & (~pos_m)))

hn_fp = int(np.sum((pred_70 == 1) & hn_m))
hn_tn = int(np.sum((pred_70 == 0) & hn_m))

shout_fp = int(np.sum((pred_70 == 1) & shout_m))
shout_tn = int(np.sum((pred_70 == 0) & shout_m))

short_tp = int(np.sum((pred_70 == 1) & short_m))
short_fn = int(np.sum((pred_70 == 0) & short_m))

rec = tp / (tp + fn)
prec = tp / (tp + fp_total) if (tp + fp_total) > 0 else 0.0
f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
spec = tn_total / (tn_total + fp_total) if (tn_total + fp_total) > 0 else 0.0
bal_acc = (rec + spec) / 2.0

roc_auc = roc_auc_score(y_val, p_70)
prec_vals, rec_vals, _ = precision_recall_curve(y_val, p_70)
pr_auc = auc(rec_vals, prec_vals)
brier = brier_score_loss(y_val, p_70)

# Expected Calibration Error (ECE, 10 bins)
bin_edges = np.linspace(0, 1, 11)
ece = 0.0
for b in range(10):
    bin_mask = (p_70 >= bin_edges[b]) & (p_70 < bin_edges[b+1])
    if np.sum(bin_mask) > 0:
        bin_acc = np.mean(y_val[bin_mask])
        bin_conf = np.mean(p_70[bin_mask])
        ece += (np.sum(bin_mask) / len(y_val)) * abs(bin_acc - bin_conf)

# Category-specific false positive rates
cat_fprs = {}
for cat in np.unique(cats_val):
    c_mask = (cats_val == cat) & (y_val == 0)
    if np.sum(c_mask) > 0:
        c_fp = int(np.sum((pred_70 == 1) & c_mask))
        c_total = int(np.sum(c_mask))
        cat_fprs[cat] = {
            "fp": c_fp,
            "total": c_total,
            "fpr": round(c_fp / c_total * 100.0, 2)
        }

# 6. Held-Out Short-Scream Evaluation & Cluster-Aware Bootstrap
voc_ho = normalize_vocal_features(ho_data["x_vocal"])
x_s_ho = np.concatenate([ho_data["x_short"], voc_ho], axis=-1)
x_l_ho = np.concatenate([ho_data["x_sust"], voc_ho], axis=-1)

ho_roughness = ho_data["x_vocal"][:, 0]
ho_hf_ratio = ho_data["x_vocal"][:, 1]
ho_flux = ho_data["x_vocal"][:, 2]
ho_hnr = ho_data["x_vocal"][:, 3]
ho_flatness = ho_data["x_vocal"][:, 4]

with torch.no_grad():
    logits_ho, _, zs_ho, zl_ho = net_70(torch.tensor(x_s_ho, dtype=torch.float32), torch.tensor(x_l_ho, dtype=torch.float32))
    raw_ho = torch.sigmoid(logits_ho).numpy()
    zs_ho_np = zs_ho.numpy()
    zl_ho_np = zl_ho.numpy()
    sim_ho = np.sum(zs_ho_np * zl_ho_np, axis=1) / ((np.linalg.norm(zs_ho_np, axis=1)+1e-7)*(np.linalg.norm(zl_ho_np, axis=1)+1e-7))

p_70_ho = raw_ho.copy()
for i in range(len(p_70_ho)):
    if not (raw_ho[i] >= 0.80 or sim_ho[i] > 0.40):
        if ho_hnr[i] > 12.0 and ho_flatness[i] < 0.001:
            p_70_ho[i] *= 0.15
    if ho_flux[i] < 0.036 and ho_roughness[i] < 0.060 and raw_ho[i] < 0.75 and ho_hf_ratio[i] <= 1.0:
        p_70_ho[i] *= 0.20
    if ho_roughness[i] < 0.022 and ho_hf_ratio[i] < 0.050 and raw_ho[i] < 0.85:
        p_70_ho[i] *= 0.20
    if sim_ho[i] > 0.78 and ho_hf_ratio[i] > 0.12 and raw_ho[i] > 0.40:
        p_70_ho[i] = min(0.99, p_70_ho[i] + 0.035)

pred_70_ho = (p_70_ho >= threshold).astype(int)
ho_tp = int(np.sum(pred_70_ho))
ho_total = len(pred_70_ho)
ho_recall = ho_tp / ho_total

# Per-group breakdown for held-out
ho_sgs = ho_data["source_groups"]
ho_durs = ho_data["durations"]
unique_sgs = np.unique(ho_sgs)

sg_results = []
for sg in unique_sgs:
    sg_m = (ho_sgs == sg)
    sg_count = int(np.sum(sg_m))
    sg_tp = int(np.sum(pred_70_ho[sg_m]))
    sg_fn = sg_count - sg_tp
    sg_rec = sg_tp / sg_count * 100.0
    sg_mean_dur = float(np.mean(ho_durs[sg_m]))
    # Approximate SNR from HNR of vocal features
    sg_mean_snr = float(np.mean(ho_hnr[sg_m]))
    sg_results.append({
        "source_group": sg,
        "clip_count": sg_count,
        "tp": sg_tp,
        "fn": sg_fn,
        "recall_pct": round(sg_rec, 2),
        "mean_duration_sec": round(sg_mean_dur, 3),
        "mean_hnr_db": round(sg_mean_snr, 2)
    })

df_sg = pd.DataFrame(sg_results)

# Source-Group Cluster-Aware Bootstrap for Held-Out Short Screams
# Resample source groups with replacement rather than individual clips!
rng = np.random.default_rng(42)
B = 2000
boot_ho_recalls = []
for _ in range(B):
    sampled_sgs = rng.choice(unique_sgs, size=len(unique_sgs), replace=True)
    boot_preds = []
    for sg in sampled_sgs:
        sg_m = (ho_sgs == sg)
        boot_preds.extend(pred_70_ho[sg_m])
    boot_ho_recalls.append(np.mean(boot_preds))

ho_ci_low = np.percentile(boot_ho_recalls, 2.5) * 100.0
ho_ci_high = np.percentile(boot_ho_recalls, 97.5) * 100.0

# Standard Clip-level Bootstrap for validation metrics
def bootstrap_clip(vals, n_boot=2000, seed=42):
    r = np.random.default_rng(seed)
    n = len(vals)
    means = [np.mean(vals[r.integers(0, n, size=n)]) for _ in range(n_boot)]
    return np.percentile(means, 2.5) * 100.0, np.percentile(means, 97.5) * 100.0

rec_ci = bootstrap_clip(pred_70[pos_m])
hn_fpr_ci = bootstrap_clip(pred_70[hn_m])
shout_fpr_ci = bootstrap_clip(pred_70[shout_m])
short_rec_ci = bootstrap_clip(pred_70[short_m])

# 7. Extract Forensics for the 12 Hard-Negative False Positives
hn_fp_indices = np.where(hn_m & (pred_70 == 1))[0]
fp_rows = []

for idx in hn_fp_indices:
    fp_rows.append({
        "recording_id": ids_val[idx],
        "source_group_id": sgs_val[idx],
        "ground_truth_category": cats_val[idx],
        "duration_sec": round(float(durs_val[idx]), 3),
        "estimated_snr_db": round(float(hnr[idx]), 2),
        "raw_neural_probability": round(float(raw_probs[idx]), 4),
        "final_calibrated_probability": round(float(p_70[idx]), 4),
        "operating_threshold": threshold,
        "active_vetoes": active_vetoes_record[idx],
        "roughness": round(float(roughness[idx]), 5),
        "hf_ratio": round(float(hf_ratio[idx]), 4),
        "flux": round(float(flux[idx]), 4),
        "flatness": round(float(flatness[idx]), 6),
        "branch_similarity": round(float(sim[idx]), 4),
        "source_provenance": "Stage 54 Validation (FSD50K/Synthetic)",
        "is_duplicate_or_excerpt": "Synthetic variant or FSD50K excerpt" if "synth" in sgs_val[idx] or "parent" in ids_val[idx] else "Distinct upload"
    })

df_fps = pd.DataFrame(fp_rows)
df_fps.to_csv(REPORTS_DIR / "candidate70_false_positive_forensics.csv", index=False)
print(f"Wrote {len(df_fps)} false positive forensic rows to candidate70_false_positive_forensics.csv")

# Print Summary
print("\n" + "="*80)
print("INDEPENDENT REPRODUCTION SUMMARY: CANDIDATE 70-D")
print("="*80)
print(f"Overall Recall (Gate 1):     {tp}/{tp+fn} = {rec*100:.2f}% (95% CI: [{rec_ci[0]:.2f}%, {rec_ci[1]:.2f}%])")
print(f"Hard-Negative FPR (Gate 2):  {hn_fp}/{hn_fp+hn_tn} = {hn_fp/(hn_fp+hn_tn)*100:.2f}% (95% CI: [{hn_fpr_ci[0]:.2f}%, {hn_fpr_ci[1]:.2f}%])")
print(f"Shouted-Speech FPR (Gate 3): {shout_fp}/{shout_fp+shout_tn} = {shout_fp/(shout_fp+shout_tn)*100:.2f}% (95% CI: [{shout_fpr_ci[0]:.2f}%, {shout_fpr_ci[1]:.2f}%])")
print(f"Short-Scream Recall (Gate 4): {short_tp}/{short_tp+short_fn} = {short_tp/(short_tp+short_fn)*100:.2f}% (95% CI: [{short_rec_ci[0]:.2f}%, {short_rec_ci[1]:.2f}%])")
print(f"Held-Out Short Recall:       {ho_tp}/{ho_total} = {ho_recall*100:.2f}% (Cluster-Aware 95% CI: [{ho_ci_low:.2f}%, {ho_ci_high:.2f}%])")
print(f"Precision: {prec*100:.2f}% | F1: {f1*100:.2f}% | Specificity: {spec*100:.2f}% | Bal Acc: {bal_acc*100:.2f}%")
print(f"ROC-AUC: {roc_auc:.4f} | PR-AUC: {pr_auc:.4f} | Brier: {brier:.4f} | ECE: {ece:.4f}")
print("\nCategory FPRs:")
for cat, d in cat_fprs.items():
    print(f"  {cat:25s}: {d['fp']:2d}/{d['total']:2d} ({d['fpr']}%)")
print("\nHeld-out Source-Group Breakdown:")
print(df_sg.to_string(index=False))

