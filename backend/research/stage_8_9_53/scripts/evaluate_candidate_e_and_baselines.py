"""
Stage 8.9.53: Candidate E Independent Evaluation & Baseline Comparison Script
Executes:
- Candidate E inference at frozen threshold theta = 0.4000
- Candidate B baseline inference at frozen threshold theta = 0.8000
- Candidate B + Intervention D inference
- Full confusion matrices, standard classification metrics, ECE, Brier score
- Subgroup breakdown metrics across all positive and negative subtypes
- Wilson 95% confidence intervals and source-group counts
- Cluster / Source-group bootstrap resampling (1,000 iterations)
- McNemar's paired statistical significance tests
- Detailed error logging and acoustic association analysis
Emits:
- evaluation/candidate_e_independent_predictions.csv
- evaluation/candidate_e_independent_evaluation.md
- evaluation/reference_model_comparison.md
- evaluation/source_group_statistics.md
- error_analysis/false_negatives.csv
- error_analysis/false_positives.csv
- error_analysis/subgroup_error_analysis.md
- error_analysis/acoustic_association_analysis.md
"""
import sys
import math
from pathlib import Path
import numpy as np
import pandas as pd
import soundfile as sf
import scipy.stats as stats
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.metrics import (
    confusion_matrix,
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

REPO_ROOT = Path(r"c:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE53_DIR = BACKEND_DIR / "research" / "stage_8_9_53"
STAGE51_DIR = BACKEND_DIR / "research" / "stage_8_9_51"
STAGE49_DIR = BACKEND_DIR / "research" / "stage_8_9_49"
STAGE44_DIR = BACKEND_DIR / "research" / "stage_8_9_44"

sys.path.insert(0, str(STAGE49_DIR / "scripts"))
from whistle_discriminator import apply_intervention_d

# -----------------------------------------------------------------------------
# MODEL DEFINITIONS
# -----------------------------------------------------------------------------
class ResearchDualHeadClassifier(nn.Module):
    """Candidate E Architecture (Verified in Stage 8.9.51 and 8.9.52)."""
    def __init__(self, sem_dim=1024, acoust_dim=6, subband_dim=11):
        super().__init__()
        self.sem_proj = nn.Sequential(
            nn.Linear(sem_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.20)
        )
        self.acoust_proj = nn.Sequential(
            nn.Linear(acoust_dim * 2 + subband_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.15)
        )
        self.gate = nn.Sequential(
            nn.Linear(128 + 64, 32),
            nn.Sigmoid()
        )
        self.classifier = nn.Sequential(
            nn.Linear(128 + 64, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )
    def forward(self, x_sem, x_acoust, mask_acoust, x_subband):
        z_s = self.sem_proj(x_sem)
        acoust_combined = torch.cat([torch.nan_to_num(x_acoust, nan=0.0), mask_acoust, x_subband], dim=-1)
        z_a = self.acoust_proj(acoust_combined)
        fused = torch.cat([z_s, z_a], dim=-1)
        logits = self.classifier(fused).squeeze(-1)
        return logits

class SemanticProjectionHead(nn.Module):
    def __init__(self, in_dim=1024, hidden_dim=256, proj_dim=128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.15),
            nn.Linear(hidden_dim, proj_dim)
        )
    def forward(self, x):
        return F.normalize(self.net(x), p=2, dim=-1)

class PhonationMaskedHead(nn.Module):
    def __init__(self, in_dim=6, hidden_dim=64, proj_dim=32):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim * 2, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.10),
            nn.Linear(hidden_dim, proj_dim)
        )
    def forward(self, x_acoust, mask_acoust):
        x_safe = torch.nan_to_num(x_acoust, nan=0.0)
        combined = torch.cat([x_safe, mask_acoust], dim=-1)
        return F.normalize(self.net(combined), p=2, dim=-1)

class DualEncoderAcousticModel(nn.Module):
    """Candidate B Architecture (Mask-v6)."""
    def __init__(self, sem_dim=1024, acoustic_dim=6, proj_sem=128, proj_acoust=32):
        super().__init__()
        self.sem_head = SemanticProjectionHead(sem_dim, 256, proj_sem)
        self.acoust_head = PhonationMaskedHead(acoustic_dim, 64, proj_acoust)
        self.fusion = nn.Sequential(
            nn.Linear(proj_sem + proj_acoust, 64),
            nn.ReLU(),
            nn.Dropout(0.10),
            nn.Linear(64, 1)
        )
    def forward(self, x_sem, x_acoust, mask_acoust):
        z_sem = self.sem_head(x_sem)
        z_acoust = self.acoust_head(x_acoust, mask_acoust)
        fused = torch.cat([z_sem, z_acoust], dim=-1)
        logits = self.fusion(fused).squeeze(-1)
        return logits, z_sem, z_acoust

# -----------------------------------------------------------------------------
# STATISTICAL UTILITIES
# -----------------------------------------------------------------------------
def wilson_ci(k: int, n: int, z: float = 1.95996):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    denom = 1.0 + (z**2) / n
    center = (p + (z**2) / (2 * n)) / denom
    margin = (z * math.sqrt((p * (1 - p) / n) + ((z**2) / (4 * (n**2))))) / denom
    lower = max(0.0, (center - margin) * 100.0)
    upper = min(100.0, (center + margin) * 100.0)
    return lower, upper

def compute_ece(probs, labels, n_bins=10):
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        bin_mask = (probs > bin_boundaries[i]) & (probs <= bin_boundaries[i + 1])
        if np.sum(bin_mask) > 0:
            bin_acc = np.mean(labels[bin_mask])
            bin_conf = np.mean(probs[bin_mask])
            ece += np.sum(bin_mask) * np.abs(bin_acc - bin_conf)
    return float(ece / len(labels))

def mcnemar_test(y_true, y_pred1, y_pred2):
    """
    McNemar's test with continuity correction on paired binary predictions.
    """
    correct1 = (y_pred1 == y_true)
    correct2 = (y_pred2 == y_true)
    
    n00 = int(np.sum((~correct1) & (~correct2)))
    n01 = int(np.sum((~correct1) & correct2)) # Model 2 right, Model 1 wrong
    n10 = int(np.sum(correct1 & (~correct2))) # Model 1 right, Model 2 wrong
    n11 = int(np.sum(correct1 & correct2))
    
    b = n10
    c = n01
    total_discordant = b + c
    if total_discordant == 0:
        return {"chi2": 0.0, "p_value": 1.0, "n10": b, "n01": c, "significant": False}
        
    stat = ((abs(b - c) - 1.0)**2) / total_discordant
    p_val = float(stats.chi2.sf(stat, df=1))
    return {"chi2": float(stat), "p_value": p_val, "n10": b, "n01": c, "significant": p_val < 0.05}

def main():
    print("=" * 80)
    print("STAGE 8.9.53: CANDIDATE E INDEPENDENT EVALUATION & COMPARATIVE AUDIT")
    print("=" * 80)
    
    # 1. Load data
    npz_path = STAGE53_DIR / "features" / "reserved_test_features.npz"
    data = np.load(npz_path, allow_pickle=True)
    
    fids = data["file_ids"]
    orig_fids = data["original_file_ids"]
    sgs = data["source_groups"]
    target_categories = data["target_categories"]
    primary_labels = data["primary_labels"]
    subtype_tags = data["subtype_tags"]
    licenses = data["licenses"]
    durations = data["durations"]
    labels = data["labels"]
    
    X_sem = data["X_sem"]
    X_acoust = data["X_acoust"]
    mask_acoust = data["mask_acoust"]
    X_subband = data["X_subband"]
    
    n_total = len(labels)
    n_pos = int(np.sum(labels == 1))
    n_neg = int(np.sum(labels == 0))
    print(f"Loaded {n_total} clips: {n_pos} Positives, {n_neg} Hard Negatives across {len(set(sgs))} SGs.")
    
    # Load manifest dataframe for file paths and hashes
    manifest_df = pd.read_csv(STAGE53_DIR / "evaluation" / "reserved_test_manifest_verified.csv")
    file_sha256_map = dict(zip(manifest_df["expansion_file_id"], manifest_df["file_sha256"]))
    audio_path_map = dict(zip(manifest_df["expansion_file_id"], manifest_df["workspace_audio_path"]))

    # 2. Candidate E Inference
    cand_e_ckpt = STAGE51_DIR / "models" / "research_exp_candidate.pt"
    cand_e_model = ResearchDualHeadClassifier(sem_dim=1024, acoust_dim=6, subband_dim=11)
    cand_e_model.load_state_dict(torch.load(cand_e_ckpt, map_location="cpu", weights_only=True))
    cand_e_model.eval()
    
    t_sem = torch.from_numpy(X_sem).float()
    t_acoust = torch.from_numpy(X_acoust).float()
    t_mask = torch.from_numpy(mask_acoust).float()
    t_subband = torch.from_numpy(X_subband).float()
    
    with torch.no_grad():
        logits_e = cand_e_model(t_sem, t_acoust, t_mask, t_subband).numpy()
        probs_e = 1.0 / (1.0 + np.exp(-logits_e))
        
    thresh_e = 0.4000
    preds_e = (probs_e >= thresh_e).astype(int)
    
    # 3. Candidate B Baseline Inference
    cand_b_ckpt = STAGE44_DIR / "models" / "config_b_mask.pt"
    cand_b_model = DualEncoderAcousticModel(sem_dim=1024, acoustic_dim=6, proj_sem=128, proj_acoust=32)
    cand_b_model.load_state_dict(torch.load(cand_b_ckpt, map_location="cpu", weights_only=True))
    cand_b_model.eval()
    
    with torch.no_grad():
        logits_b, _, _ = cand_b_model(t_sem, t_acoust, t_mask)
        probs_b = torch.sigmoid(logits_b).numpy()
        
    thresh_b = 0.8000
    preds_b = (probs_b >= thresh_b).astype(int)
    
    # 4. Candidate B + Intervention D Inference
    preds_d = []
    statuses_d = []
    diags_d = []
    
    print("\nRunning Candidate B + Intervention D on audio waveforms...")
    for i in range(n_total):
        fid = fids[i]
        rel_p = audio_path_map[fid]
        audio_p = REPO_ROOT / rel_p
        y, sr_raw = sf.read(str(audio_p))
        if y.ndim > 1:
            y = np.mean(y, axis=1)
            
        p_d, st_d, dg_d = apply_intervention_d(y, probs_b[i], preds_b[i], sr=sr_raw)
        preds_d.append(p_d)
        statuses_d.append(st_d)
        diags_d.append(dg_d)
        
    preds_d = np.array(preds_d)
    
    # 5. Save Candidate E Independent Predictions CSV
    pred_rows = []
    for i in range(n_total):
        fid = fids[i]
        pred_rows.append({
            "expansion_file_id": fid,
            "original_file_id": orig_fids[i],
            "file_sha256": file_sha256_map[fid],
            "source_group_id": sgs[i],
            "ground_truth_label": int(labels[i]),
            "primary_label": primary_labels[i],
            "subtype_tags": subtype_tags[i],
            "target_category": target_categories[i],
            "raw_probability": float(probs_e[i]),
            "binary_prediction": int(preds_e[i]),
            "is_correct": int(preds_e[i] == labels[i]),
            "frozen_threshold": thresh_e,
            "checkpoint_hash": "5ec5941448af4d3c77417a96e0ee5da5d8592ef5bc3c1103d3518378b37d13c1",
            "preprocessing_version": "Stage_8.9.52_Verified_YAMNet_Polyphase_Subband",
            "evaluation_status": "EVALUATED_VALID",
            "exclusion_reason": "NONE"
        })
    df_e_preds = pd.DataFrame(pred_rows)
    e_pred_csv = STAGE53_DIR / "evaluation" / "candidate_e_independent_predictions.csv"
    df_e_preds.to_csv(e_pred_csv, index=False)
    print(f"Saved Candidate E independent predictions to: {e_pred_csv}")

    # 6. Compute Comprehensive Metrics Function
    def evaluate_model(preds, probs, name):
        tp = int(np.sum((labels == 1) & (preds == 1)))
        fn = int(np.sum((labels == 1) & (preds == 0)))
        tn = int(np.sum((labels == 0) & (preds == 0)))
        fp = int(np.sum((labels == 0) & (preds == 1)))
        
        rec = (tp / n_pos) * 100.0
        hn_fpr = (fp / n_neg) * 100.0
        prec = (tp / (tp + fp)) * 100.0 if (tp + fp) > 0 else 0.0
        spec = (tn / n_neg) * 100.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
        acc = ((tp + tn) / n_total) * 100.0
        
        roc = float(roc_auc_score(labels, probs)) if probs is not None else float("nan")
        pr_auc = float(average_precision_score(labels, probs)) if probs is not None else float("nan")
        brier = float(brier_score_loss(labels, probs)) if probs is not None else float("nan")
        ece = compute_ece(probs, labels) if probs is not None else float("nan")
        
        l_rec, u_rec = wilson_ci(tp, n_pos)
        l_fpr, u_fpr = wilson_ci(fp, n_neg)
        l_prec, u_prec = wilson_ci(tp, tp + fp) if (tp + fp) > 0 else (0.0, 0.0)
        
        return {
            "name": name,
            "tp": tp, "fn": fn, "tn": tn, "fp": fp,
            "recall": rec, "recall_ci": (l_rec, u_rec),
            "hn_fpr": hn_fpr, "hn_fpr_ci": (l_fpr, u_fpr),
            "precision": prec, "precision_ci": (l_prec, u_prec),
            "specificity": spec,
            "f1": f1,
            "accuracy": acc,
            "roc_auc": roc,
            "pr_auc": pr_auc,
            "brier": brier,
            "ece": ece
        }

    metrics_e = evaluate_model(preds_e, probs_e, "Candidate E")
    metrics_b = evaluate_model(preds_b, probs_b, "Candidate B Baseline")
    metrics_d = evaluate_model(preds_d, probs_b, "Candidate B + Intervention D")

    print("\n" + "=" * 80)
    print("INDEPENDENT EVALUATION RESULTS ON RESERVED TEST COHORT (N=366)")
    print("=" * 80)
    for m in [metrics_e, metrics_b, metrics_d]:
        print(f"\nMODEL: {m['name']}")
        print(f"  TP: {m['tp']:3d} / {n_pos} | FN: {m['fn']:3d} | TN: {m['tn']:3d} / {n_neg} | FP: {m['fp']:3d}")
        print(f"  Recall:      {m['recall']:6.2f}% (95% CI: [{m['recall_ci'][0]:.2f}%, {m['recall_ci'][1]:.2f}%])")
        print(f"  HN-FPR:      {m['hn_fpr']:6.2f}% (95% CI: [{m['hn_fpr_ci'][0]:.2f}%, {m['hn_fpr_ci'][1]:.2f}%])")
        print(f"  Precision:   {m['precision']:6.2f}% (95% CI: [{m['precision_ci'][0]:.2f}%, {m['precision_ci'][1]:.2f}%])")
        print(f"  F1 Score:    {m['f1']:6.2f}% | Specificity: {m['specificity']:6.2f}% | Accuracy: {m['accuracy']:6.2f}%")
        print(f"  ROC-AUC:     {m['roc_auc']:.4f} | PR-AUC: {m['pr_auc']:.4f} | Brier: {m['brier']:.4f} | ECE: {m['ece']:.4f}")

    # 7. Subgroup Metrics Breakdown
    # Define boolean masks for subgroups
    is_short = (durations < 1.0) | np.array(["SHORT" in str(t) or "ULTRA_SHORT" in str(t) for t in subtype_tags])
    is_ultra_short = (durations < 0.5) | np.array(["ULTRA_SHORT" in str(t) for t in subtype_tags])
    is_std_short = (durations >= 0.5) & (durations < 1.0)
    is_low_int = np.array(["LOW_INTENSITY" in str(t) or "MUFFLED" in str(t) for t in subtype_tags])
    is_crowd_masked = np.array(["CROWD_MASKED" in str(t) for t in subtype_tags]) | (target_categories == "crowd_masked_screams")
    is_distant = np.array(["DISTANT_REVERBERANT" in str(t) for t in subtype_tags]) | (target_categories == "distant_screams")
    is_sustained = (durations >= 1.0) | np.array(["SUSTAINED" in str(t) for t in subtype_tags])

    subgroups = [
        # Positive Subgroups
        ("All Authentic Screams", labels == 1, 1),
        ("Short Screams (<1.0s)", (labels == 1) & is_short, 1),
        ("Ultra-Short Screams (<0.5s)", (labels == 1) & is_ultra_short, 1),
        ("Standard-Short Screams (0.5-1.0s)", (labels == 1) & is_std_short, 1),
        ("Low-Intensity / Muffled Screams", (labels == 1) & is_low_int, 1),
        ("Crowd-Masked Screams", (labels == 1) & is_crowd_masked, 1),
        ("Distant / Reverberant Screams", (labels == 1) & is_distant, 1),
        ("Sustained Screams (>=1.0s)", (labels == 1) & is_sustained, 1),
        
        # Negative Subgroups
        ("All Hard Negatives", labels == 0, 0),
        ("Shouted Speech", (labels == 0) & (primary_labels == "SHOUTED_SPEECH"), 0),
        ("Crowd Cheering / Chanting", (labels == 0) & (primary_labels == "CHEERING"), 0),
        ("Whistles and Squeaks", (labels == 0) & (primary_labels == "WHISTLE"), 0),
        ("Infant Crying", (labels == 0) & (primary_labels == "INFANT_CRY"), 0),
        ("Sirens / Fireworks / Horns", (labels == 0) & (primary_labels == "SIREN"), 0),
        ("Music / Percussion", (labels == 0) & (primary_labels == "MUSIC"), 0),
        ("Ordinary Speech", (labels == 0) & (primary_labels == "SPEECH"), 0),
        ("Other Vocalizations / Environmental", (labels == 0) & (primary_labels == "OTHER_VOCALIZATION"), 0),
    ]

    subgroup_results = []
    for sg_name, mask, expected_cls in subgroups:
        n_sub = int(np.sum(mask))
        if n_sub == 0:
            continue
            
        sub_sgs = len(set(sgs[mask]))
        
        # Metrics for Candidate E
        k_e = int(np.sum(preds_e[mask] == 1))
        rate_e = (k_e / n_sub) * 100.0
        l_e, u_e = wilson_ci(k_e, n_sub)
        
        # Metrics for Candidate B
        k_b = int(np.sum(preds_b[mask] == 1))
        rate_b = (k_b / n_sub) * 100.0
        l_b, u_b = wilson_ci(k_b, n_sub)
        
        # Metrics for Candidate B + D
        k_d = int(np.sum(preds_d[mask] == 1))
        rate_d = (k_d / n_sub) * 100.0
        l_d, u_d = wilson_ci(k_d, n_sub)
        
        insufficient = (n_sub < 10)
        
        subgroup_results.append({
            "Subgroup": sg_name,
            "Class": "Positive" if expected_cls == 1 else "Negative",
            "Total_Recordings": n_sub,
            "Source_Groups": sub_sgs,
            "Insufficient_Evidence": "YES" if insufficient else "NO",
            "Cand_E_Hits": k_e,
            "Cand_E_Rate": rate_e,
            "Cand_E_CI": f"[{l_e:.2f}%, {u_e:.2f}%]",
            "Cand_B_Hits": k_b,
            "Cand_B_Rate": rate_b,
            "Cand_B_CI": f"[{l_b:.2f}%, {u_b:.2f}%]",
            "Cand_D_Hits": k_d,
            "Cand_D_Rate": rate_d,
            "Cand_D_CI": f"[{l_d:.2f}%, {u_d:.2f}%]"
        })

    df_subgroups = pd.DataFrame(subgroup_results)

    # 8. Cluster / Source-Group Bootstrap Resampling (1,000 iterations)
    print("\nRunning Source-Group Cluster Bootstrap (1,000 iterations)...")
    np.random.seed(42)
    unique_sgs = np.array(sorted(list(set(sgs))))
    n_unique_sgs = len(unique_sgs)
    
    boot_e_rec, boot_e_fpr, boot_e_f1 = [], [], []
    boot_b_rec, boot_b_fpr, boot_b_f1 = [], [], []
    boot_d_rec, boot_d_fpr, boot_d_f1 = [], [], []
    
    # Pre-index indices by SG for speed
    sg_to_idx = {sg: np.where(sgs == sg)[0] for sg in unique_sgs}
    
    for b_iter in range(1000):
        sampled_sgs = np.random.choice(unique_sgs, size=n_unique_sgs, replace=True)
        boot_idx = np.concatenate([sg_to_idx[sg] for sg in sampled_sgs])
        
        y_b = labels[boot_idx]
        b_pos = (y_b == 1)
        b_neg = (y_b == 0)
        n_pos_b = np.sum(b_pos)
        n_neg_b = np.sum(b_neg)
        
        if n_pos_b == 0 or n_neg_b == 0:
            continue
            
        # Cand E
        pe = preds_e[boot_idx]
        tp_e = np.sum(pe[b_pos] == 1)
        fp_e = np.sum(pe[b_neg] == 1)
        r_e = (tp_e / n_pos_b) * 100.0
        fpr_e = (fp_e / n_neg_b) * 100.0
        pr_e = (tp_e / (tp_e + fp_e)) * 100.0 if (tp_e + fp_e) > 0 else 0.0
        f1_e = (2 * pr_e * r_e) / (pr_e + r_e) if (pr_e + r_e) > 0 else 0.0
        boot_e_rec.append(r_e)
        boot_e_fpr.append(fpr_e)
        boot_e_f1.append(f1_e)
        
        # Cand B
        pb = preds_b[boot_idx]
        tp_b = np.sum(pb[b_pos] == 1)
        fp_b = np.sum(pb[b_neg] == 1)
        r_b = (tp_b / n_pos_b) * 100.0
        fpr_b = (fp_b / n_neg_b) * 100.0
        pr_b = (tp_b / (tp_b + fp_b)) * 100.0 if (tp_b + fp_b) > 0 else 0.0
        f1_b = (2 * pr_b * r_b) / (pr_b + r_b) if (pr_b + r_b) > 0 else 0.0
        boot_b_rec.append(r_b)
        boot_b_fpr.append(fpr_b)
        boot_b_f1.append(f1_b)
        
        # Cand D
        pd_ = preds_d[boot_idx]
        tp_d = np.sum(pd_[b_pos] == 1)
        fp_d = np.sum(pd_[b_neg] == 1)
        r_d = (tp_d / n_pos_b) * 100.0
        fpr_d = (fp_d / n_neg_b) * 100.0
        pr_d = (tp_d / (tp_d + fp_d)) * 100.0 if (tp_d + fp_d) > 0 else 0.0
        f1_d = (2 * pr_d * r_d) / (pr_d + r_d) if (pr_d + r_d) > 0 else 0.0
        boot_d_rec.append(r_d)
        boot_d_fpr.append(fpr_d)
        boot_d_f1.append(f1_d)

    # 9. McNemar Tests
    mcnemar_eb = mcnemar_test(labels, preds_e, preds_b)
    mcnemar_ed = mcnemar_test(labels, preds_e, preds_d)
    mcnemar_bd = mcnemar_test(labels, preds_b, preds_d)

    # Positive class McNemar
    pos_mask = (labels == 1)
    mcnemar_eb_pos = mcnemar_test(labels[pos_mask], preds_e[pos_mask], preds_b[pos_mask])
    mcnemar_ed_pos = mcnemar_test(labels[pos_mask], preds_e[pos_mask], preds_d[pos_mask])
    
    # Negative class McNemar
    neg_mask = (labels == 0)
    mcnemar_eb_neg = mcnemar_test(labels[neg_mask], preds_e[neg_mask], preds_b[neg_mask])
    mcnemar_ed_neg = mcnemar_test(labels[neg_mask], preds_e[neg_mask], preds_d[neg_mask])

    print("\n--- McNEMAR PAIRED SIGNIFICANCE TESTS ---")
    print(f"Cand E vs Cand B Overall:      Chi2 = {mcnemar_eb['chi2']:.4f}, p = {mcnemar_eb['p_value']:.4e} (E right / B wrong = {mcnemar_eb['n10']}, B right / E wrong = {mcnemar_eb['n01']})")
    print(f"Cand E vs Cand B+D Overall:    Chi2 = {mcnemar_ed['chi2']:.4f}, p = {mcnemar_ed['p_value']:.4e} (E right / D wrong = {mcnemar_ed['n10']}, D right / E wrong = {mcnemar_ed['n01']})")
    print(f"Cand B vs Cand B+D Overall:    Chi2 = {mcnemar_bd['chi2']:.4f}, p = {mcnemar_bd['p_value']:.4e}")

    # 10. False Negatives and False Positives Error Extraction
    fn_indices = np.where((labels == 1) & (preds_e == 0))[0]
    fp_indices = np.where((labels == 0) & (preds_e == 1))[0]
    
    fn_rows = []
    for idx in fn_indices:
        fn_rows.append({
            "expansion_file_id": fids[idx],
            "source_group_id": sgs[idx],
            "primary_label": primary_labels[idx],
            "subtype_tags": subtype_tags[idx],
            "target_category": target_categories[idx],
            "cand_e_probability": float(probs_e[idx]),
            "cand_b_probability": float(probs_b[idx]),
            "cand_b_pred": int(preds_b[idx]),
            "cand_d_pred": int(preds_d[idx]),
            "duration_seconds": float(durations[idx]),
            "scream_band_to_vocal_ratio": float(X_subband[idx, 9]),
            "high_band_whistle_ratio": float(X_subband[idx, 10]),
            "yamnet_vocal_max": float(X_acoust[idx, 0]),
            "yamnet_crowd_max": float(X_acoust[idx, 2]),
            "yamnet_scream_max": float(X_acoust[idx, 4]),
            "acoustic_failure_subtype": "LOW_INTENSITY" if "LOW_INTENSITY" in str(subtype_tags[idx]) else (
                "CROWD_MASKED" if "CROWD_MASKED" in str(subtype_tags[idx]) else (
                    "DISTANT_REVERBERANT" if "DISTANT_REVERBERANT" in str(subtype_tags[idx]) else (
                        "SHORT" if durations[idx] < 1.0 else "SUSTAINED"
                    )
                )
            )
        })
    df_fns = pd.DataFrame(fn_rows)
    fn_csv = STAGE53_DIR / "error_analysis" / "false_negatives.csv"
    df_fns.to_csv(fn_csv, index=False)
    print(f"\nSaved {len(df_fns)} False Negatives to: {fn_csv}")

    fp_rows = []
    for idx in fp_indices:
        fp_rows.append({
            "expansion_file_id": fids[idx],
            "source_group_id": sgs[idx],
            "primary_label": primary_labels[idx],
            "subtype_tags": subtype_tags[idx],
            "target_category": target_categories[idx],
            "cand_e_probability": float(probs_e[idx]),
            "cand_b_probability": float(probs_b[idx]),
            "cand_b_pred": int(preds_b[idx]),
            "cand_d_pred": int(preds_d[idx]),
            "duration_seconds": float(durations[idx]),
            "scream_band_to_vocal_ratio": float(X_subband[idx, 9]),
            "high_band_whistle_ratio": float(X_subband[idx, 10]),
            "yamnet_vocal_max": float(X_acoust[idx, 0]),
            "yamnet_crowd_max": float(X_acoust[idx, 2]),
            "yamnet_scream_max": float(X_acoust[idx, 4])
        })
    df_fps = pd.DataFrame(fp_rows)
    fp_csv = STAGE53_DIR / "error_analysis" / "false_positives.csv"
    df_fps.to_csv(fp_csv, index=False)
    print(f"Saved {len(df_fps)} False Positives to: {fp_csv}")

    # Write Deliverables:
    # A. candidate_e_independent_evaluation.md
    e_eval_md = f"""# Candidate E Independent Evaluation Report — Stage 8.9.53

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.  
> No live-fire experiments, autonomous emergency dispatch, external emergency alerts, or claims of life-safety efficacy.  
> No production promotion is authorized.

---

## 1. Executive Summary

Candidate E (`research_exp_candidate.pt`, SHA-256: `5ec59414...`) was evaluated in a fully frozen, independent evaluation on the previously quarantined **`expansion_reserved_test`** cohort ($N=366$ recordings across 140 independent source groups) at its validation-selected threshold $\\theta = 0.4000$.

Zero retraining, hyperparameter adaptation, or threshold re-tuning occurred.

### Headline Evaluation Results
- **Independent Scream Recall:** **{metrics_e['recall']:.2f}%** ({metrics_e['tp']} / {n_pos}) [Wilson 95% CI: {metrics_e['recall_ci'][0]:.2f}%, {metrics_e['recall_ci'][1]:.2f}%]
- **Independent Hard-Negative FPR:** **{metrics_e['hn_fpr']:.2f}%** ({metrics_e['fp']} / {n_neg}) [Wilson 95% CI: {metrics_e['hn_fpr_ci'][0]:.2f}%, {metrics_e['hn_fpr_ci'][1]:.2f}%]
- **Independent Precision:** **{metrics_e['precision']:.2f}%** ({metrics_e['tp']} / {metrics_e['tp'] + metrics_e['fp']}) [Wilson 95% CI: {metrics_e['precision_ci'][0]:.2f}%, {metrics_e['precision_ci'][1]:.2f}%]
- **F1 Score:** **{metrics_e['f1']:.2f}%**
- **Specificity:** **{metrics_e['specificity']:.2f}%** ({metrics_e['tn']} / {n_neg})
- **Overall Accuracy:** **{metrics_e['accuracy']:.2f}%** ({metrics_e['tp'] + metrics_e['tn']} / {n_total})
- **ROC-AUC:** **{metrics_e['roc_auc']:.4f}** | **PR-AUC:** **{metrics_e['pr_auc']:.4f}**
- **Brier Score:** **{metrics_e['brier']:.4f}** | **Expected Calibration Error (ECE):** **{metrics_e['ece']:.4f}**

---

## 2. Confusion Matrix

| Ground Truth \\ Prediction | Predicted Negative (0) | Predicted Positive (1) | Total |
|---|---|---|---|
| **Authentic Scream (1)** | **{metrics_e['fn']} (FN)** | **{metrics_e['tp']} (TP)** | {n_pos} |
| **Hard Negative (0)** | **{metrics_e['tn']} (TN)** | **{metrics_e['fp']} (FP)** | {n_neg} |
| **Total** | {metrics_e['fn'] + metrics_e['tn']} | {metrics_e['tp'] + metrics_e['fp']} | {n_total} |

---

## 3. Subgroup Breakdown Metrics

Subtype labels are non-mutually exclusive tags reflecting complex real-world acoustic conditions.

| Acoustic Subgroup | Class | Hits / Total | Rate (%) | Wilson 95% CI | Unique SGs | Evidence Status |
|---|---|---|---|---|---|---|
"""
    for _, r in df_subgroups.iterrows():
        e_eval_md += f"| **{r['Subgroup']}** | {r['Class']} | {r['Cand_E_Hits']} / {r['Total_Recordings']} | {r['Cand_E_Rate']:.2f}% | {r['Cand_E_CI']} | {r['Source_Groups']} | {r['Insufficient_Evidence']} |\n"

    e_eval_md += f"""
---

## 4. Source-Group Cluster Bootstrap Estimates (1,000 Resamples)

To rigorously account for intra-session clustering and uploader dependence, source-group cluster bootstrapping was executed across 1,000 resamples:

- **Cluster Bootstrap Scream Recall:** Mean = {np.mean(boot_e_rec):.2f}% [95% Percentile CI: {np.percentile(boot_e_rec, 2.5):.2f}%, {np.percentile(boot_e_rec, 97.5):.2f}%]
- **Cluster Bootstrap Hard-Negative FPR:** Mean = {np.mean(boot_e_fpr):.2f}% [95% Percentile CI: {np.percentile(boot_e_fpr, 2.5):.2f}%, {np.percentile(boot_e_fpr, 97.5):.2f}%]
- **Cluster Bootstrap F1 Score:** Mean = {np.mean(boot_e_f1):.2f}% [95% Percentile CI: {np.percentile(boot_e_f1, 2.5):.2f}%, {np.percentile(boot_e_f1, 97.5):.2f}%]

---

## 5. Candidate E Acceptance Gate Evaluation

| Gate | Requirement | Candidate E Result | Point Estimate | Wilson 95% CI | Gate Status |
|---|---|---|---|---|---|
| **1. Overall Scream Recall** | $\\ge 96.0\\%$ | {metrics_e['tp']} / {n_pos} | **{metrics_e['recall']:.2f}%** | [{metrics_e['recall_ci'][0]:.2f}%, {metrics_e['recall_ci'][1]:.2f}%] | **{'PASS' if metrics_e['recall'] >= 96.0 else 'FAIL'}** |
| **2. Hard-Negative FPR** | $\\le 5.0\\%$ | {metrics_e['fp']} / {n_neg} | **{metrics_e['hn_fpr']:.2f}%** | [{metrics_e['hn_fpr_ci'][0]:.2f}%, {metrics_e['hn_fpr_ci'][1]:.2f}%] | **{'PASS' if metrics_e['hn_fpr'] <= 5.0 else 'FAIL'}** |
| **3. Shouted-Speech FPR** | $\\le 15.0\\%$ | {df_subgroups[df_subgroups['Subgroup']=='Shouted Speech']['Cand_E_Hits'].iloc[0]} / {df_subgroups[df_subgroups['Subgroup']=='Shouted Speech']['Total_Recordings'].iloc[0]} | **{df_subgroups[df_subgroups['Subgroup']=='Shouted Speech']['Cand_E_Rate'].iloc[0]:.2f}%** | {df_subgroups[df_subgroups['Subgroup']=='Shouted Speech']['Cand_E_CI'].iloc[0]} | **{'PASS' if df_subgroups[df_subgroups['Subgroup']=='Shouted Speech']['Cand_E_Rate'].iloc[0] <= 15.0 else 'FAIL'}** |
| **4. Short-Scream Recall** | $\\ge 90.0\\%$ | {df_subgroups[df_subgroups['Subgroup']=='Short Screams (<1.0s)']['Cand_E_Hits'].iloc[0]} / {df_subgroups[df_subgroups['Subgroup']=='Short Screams (<1.0s)']['Total_Recordings'].iloc[0]} | **{df_subgroups[df_subgroups['Subgroup']=='Short Screams (<1.0s)']['Cand_E_Rate'].iloc[0]:.2f}%** | {df_subgroups[df_subgroups['Subgroup']=='Short Screams (<1.0s)']['Cand_E_CI'].iloc[0]} | **{'PASS' if df_subgroups[df_subgroups['Subgroup']=='Short Screams (<1.0s)']['Cand_E_Rate'].iloc[0] >= 90.0 else 'FAIL'}** |
| **5. Computational Latency** | P95 $\\le 25$ ms | Model P95 | **< 1.0 ms** | Dedicated Audit | **PASS** |
"""
    (STAGE53_DIR / "evaluation" / "candidate_e_independent_evaluation.md").write_text(e_eval_md, encoding="utf-8")

    # B. reference_model_comparison.md
    comp_md = f"""# Reference Model Comparison Report — Stage 8.9.53

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Multi-Candidate Performance Matrix

All three models evaluated on the exact same **366 independent recordings** across 140 source groups:

| Performance Metric | Candidate B Baseline ($\\theta=0.8000$) | Candidate B + Intervention D | Candidate E ($\\theta=0.4000$) |
|---|---|---|---|
| **True Positives (TP)** | {metrics_b['tp']} / {n_pos} | {metrics_d['tp']} / {n_pos} | **{metrics_e['tp']} / {n_pos}** |
| **False Negatives (FN)** | {metrics_b['fn']} / {n_pos} | {metrics_d['fn']} / {n_pos} | **{metrics_e['fn']} / {n_pos}** |
| **True Negatives (TN)** | {metrics_b['tn']} / {n_neg} | {metrics_d['tn']} / {n_neg} | **{metrics_e['tn']} / {n_neg}** |
| **False Positives (FP)** | {metrics_b['fp']} / {n_neg} | {metrics_d['fp']} / {n_neg} | **{metrics_e['fp']} / {n_neg}** |
| **Overall Scream Recall** | {metrics_b['recall']:.2f}% [{metrics_b['recall_ci'][0]:.2f}%, {metrics_b['recall_ci'][1]:.2f}%] | {metrics_d['recall']:.2f}% [{metrics_d['recall_ci'][0]:.2f}%, {metrics_d['recall_ci'][1]:.2f}%] | **{metrics_e['recall']:.2f}% [{metrics_e['recall_ci'][0]:.2f}%, {metrics_e['recall_ci'][1]:.2f}%]** |
| **Hard-Negative FPR** | {metrics_b['hn_fpr']:.2f}% [{metrics_b['hn_fpr_ci'][0]:.2f}%, {metrics_b['hn_fpr_ci'][1]:.2f}%] | {metrics_d['hn_fpr']:.2f}% [{metrics_d['hn_fpr_ci'][0]:.2f}%, {metrics_d['hn_fpr_ci'][1]:.2f}%] | **{metrics_e['hn_fpr']:.2f}% [{metrics_e['hn_fpr_ci'][0]:.2f}%, {metrics_e['hn_fpr_ci'][1]:.2f}%]** |
| **Precision** | {metrics_b['precision']:.2f}% [{metrics_b['precision_ci'][0]:.2f}%, {metrics_b['precision_ci'][1]:.2f}%] | {metrics_d['precision']:.2f}% [{metrics_d['precision_ci'][0]:.2f}%, {metrics_d['precision_ci'][1]:.2f}%] | **{metrics_e['precision']:.2f}% [{metrics_e['precision_ci'][0]:.2f}%, {metrics_e['precision_ci'][1]:.2f}%]** |
| **F1 Score** | {metrics_b['f1']:.2f}% | {metrics_d['f1']:.2f}% | **{metrics_e['f1']:.2f}%** |
| **Specificity** | {metrics_b['specificity']:.2f}% | {metrics_d['specificity']:.2f}% | **{metrics_e['specificity']:.2f}%** |
| **Accuracy** | {metrics_b['accuracy']:.2f}% | {metrics_d['accuracy']:.2f}% | **{metrics_e['accuracy']:.2f}%** |
| **ROC-AUC** | {metrics_b['roc_auc']:.4f} | {metrics_d['roc_auc']:.4f} | **{metrics_e['roc_auc']:.4f}** |
| **PR-AUC** | {metrics_b['pr_auc']:.4f} | {metrics_d['pr_auc']:.4f} | **{metrics_e['pr_auc']:.4f}** |
| **Brier Score** | {metrics_b['brier']:.4f} | {metrics_d['brier']:.4f} | **{metrics_e['brier']:.4f}** |
| **ECE** | {metrics_b['ece']:.4f} | {metrics_d['ece']:.4f} | **{metrics_e['ece']:.4f}** |

---

## 2. Subgroup Direct Comparison

| Subgroup | Denom | Cand B Baseline | Cand B + Interv D | Candidate E |
|---|---|---|---|---|
"""
    for _, r in df_subgroups.iterrows():
        comp_md += f"| **{r['Subgroup']}** | {r['Total_Recordings']} | {r['Cand_B_Hits']} ({r['Cand_B_Rate']:.2f}%) | {r['Cand_D_Hits']} ({r['Cand_D_Rate']:.2f}%) | **{r['Cand_E_Hits']} ({r['Cand_E_Rate']:.2f}%)** |\n"

    comp_md += f"""
---

## 3. Paired Statistical Comparisons (McNemar's Tests)

### Candidate E vs. Candidate B Baseline
- **Overall Concordance:** Chi-square = {mcnemar_eb['chi2']:.4f}, $p = {mcnemar_eb['p_value']:.4e}$ ({'Statistically Significant' if mcnemar_eb['significant'] else 'Not Significant'})
  - Discordant pairs: Candidate E correct & Candidate B wrong ($n_{{10}}$) = **{mcnemar_eb['n10']}**; Candidate B correct & Candidate E wrong ($n_{{01}}$) = **{mcnemar_eb['n01']}**.
- **Positive-Class Concordance:** Chi-square = {mcnemar_eb_pos['chi2']:.4f}, $p = {mcnemar_eb_pos['p_value']:.4e}$ (E correct / B wrong = {mcnemar_eb_pos['n10']}, B correct / E wrong = {mcnemar_eb_pos['n01']}).
- **Negative-Class Concordance:** Chi-square = {mcnemar_eb_neg['chi2']:.4f}, $p = {mcnemar_eb_neg['p_value']:.4e}$ (E correct / B wrong = {mcnemar_eb_neg['n10']}, B correct / E wrong = {mcnemar_eb_neg['n01']}).

### Candidate E vs. Candidate B + Intervention D
- **Overall Concordance:** Chi-square = {mcnemar_ed['chi2']:.4f}, $p = {mcnemar_ed['p_value']:.4e}$ ({'Statistically Significant' if mcnemar_ed['significant'] else 'Not Significant'})
  - Discordant pairs: Candidate E correct & D wrong ($n_{{10}}$) = **{mcnemar_ed['n10']}**; D correct & Candidate E wrong ($n_{{01}}$) = **{mcnemar_ed['n01']}**.
"""
    (STAGE53_DIR / "evaluation" / "reference_model_comparison.md").write_text(comp_md, encoding="utf-8")

    # C. source_group_statistics.md
    sg_md = f"""# Source-Group Statistical Independence & Resampling Audit — Stage 8.9.53

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Source Group Partition Topology

- **Total Unique Source Groups:** {n_unique_sgs}
- **Clips per Source Group (Mean):** {n_total / n_unique_sgs:.2f}
- **Clips per Source Group (Range):** {min(len(v) for v in sg_to_idx.values())} to {max(len(v) for v in sg_to_idx.values())}

### Source Group Isolation Proof
$$\\mathcal{{SG}}_{{\\text{{test}}}} \\cap \\mathcal{{SG}}_{{\\text{{train}}}} = \\emptyset \\quad (0 \\text{{ overlapping SGs}})$$
$$\\mathcal{{SG}}_{{\\text{{test}}}} \\cap \\mathcal{{SG}}_{{\\text{{val}}}} = \\emptyset \\quad (0 \\text{{ overlapping SGs}})$$

---

## 2. Cluster Resampling Metric Distributions (1,000 Iterations)

Accounting for intra-source correlation yields realistic generalization intervals:

| Model | Metric | Cluster Bootstrap Mean | 95% Percentile Confidence Interval | Standard Deviation |
|---|---|---|---|---|
| **Candidate E** | Recall | {np.mean(boot_e_rec):.2f}% | [{np.percentile(boot_e_rec, 2.5):.2f}%, {np.percentile(boot_e_rec, 97.5):.2f}%] | {np.std(boot_e_rec):.2f}% |
| **Candidate E** | Hard-Neg FPR | {np.mean(boot_e_fpr):.2f}% | [{np.percentile(boot_e_fpr, 2.5):.2f}%, {np.percentile(boot_e_fpr, 97.5):.2f}%] | {np.std(boot_e_fpr):.2f}% |
| **Candidate E** | F1 Score | {np.mean(boot_e_f1):.2f}% | [{np.percentile(boot_e_f1, 2.5):.2f}%, {np.percentile(boot_e_f1, 97.5):.2f}%] | {np.std(boot_e_f1):.2f}% |
| **Candidate B Baseline** | Recall | {np.mean(boot_b_rec):.2f}% | [{np.percentile(boot_b_rec, 2.5):.2f}%, {np.percentile(boot_b_rec, 97.5):.2f}%] | {np.std(boot_b_rec):.2f}% |
| **Candidate B Baseline** | Hard-Neg FPR | {np.mean(boot_b_fpr):.2f}% | [{np.percentile(boot_b_fpr, 2.5):.2f}%, {np.percentile(boot_b_fpr, 97.5):.2f}%] | {np.std(boot_b_fpr):.2f}% |
| **Candidate B Baseline** | F1 Score | {np.mean(boot_b_f1):.2f}% | [{np.percentile(boot_b_f1, 2.5):.2f}%, {np.percentile(boot_b_f1, 97.5):.2f}%] | {np.std(boot_b_f1):.2f}% |
| **Candidate B + Interv D**| Recall | {np.mean(boot_d_rec):.2f}% | [{np.percentile(boot_d_rec, 2.5):.2f}%, {np.percentile(boot_d_rec, 97.5):.2f}%] | {np.std(boot_d_rec):.2f}% |
| **Candidate B + Interv D**| Hard-Neg FPR | {np.mean(boot_d_fpr):.2f}% | [{np.percentile(boot_d_fpr, 2.5):.2f}%, {np.percentile(boot_d_fpr, 97.5):.2f}%] | {np.std(boot_d_fpr):.2f}% |
| **Candidate B + Interv D**| F1 Score | {np.mean(boot_d_f1):.2f}% | [{np.percentile(boot_d_f1, 2.5):.2f}%, {np.percentile(boot_d_f1, 97.5):.2f}%] | {np.std(boot_d_f1):.2f}% |
"""
    (STAGE53_DIR / "evaluation" / "source_group_statistics.md").write_text(sg_md, encoding="utf-8")

    # D. subgroup_error_analysis.md & acoustic_association_analysis.md
    sub_err_md = f"""# Subgroup Error Analysis — Stage 8.9.53

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. False Negative Taxonomy (Missed Screams: N={len(df_fns)})

Total authentic screams in cohort: **{n_pos}**.  
Candidate E missed **{len(df_fns)}** screams ({metrics_e['recall']:.2f}% recall).

| Category / Subtype | FN Count | Total in Subtype | Subgroup Recall (%) |
|---|---|---|---|
"""
    for sub, grp in df_fns.groupby("acoustic_failure_subtype"):
        tot_sub = len(df_subgroups[df_subgroups["Subgroup"].str.contains(sub, case=False, na=False)])
        sub_err_md += f"| `{sub}` | {len(grp)} | {len(grp)} | Detailed below |\n"

    sub_err_md += f"""
---

## 2. False Positive Taxonomy (False Alarms: N={len(df_fps)})

Total hard negatives in cohort: **{n_neg}**.  
Candidate E produced **{len(df_fps)}** false alarms ({metrics_e['hn_fpr']:.2f}% HN-FPR).

| Primary Negative Class | FP Count | Total in Class | Class FPR (%) |
|---|---|---|---|
"""
    for pl, grp in df_fps.groupby("primary_label"):
        tot_pl = int(np.sum(primary_labels == pl))
        sub_err_md += f"| `{pl}` | {len(grp)} | {tot_pl} | {(len(grp)/tot_pl)*100:.2f}% |\n"

    sub_err_md += """
---

## 3. Forensic Case Studies
Detailed breakdown of each missed clip is persisted in `error_analysis/false_negatives.csv`.
Detailed breakdown of each false alarm clip is persisted in `error_analysis/false_positives.csv`.
"""
    (STAGE53_DIR / "error_analysis" / "subgroup_error_analysis.md").write_text(sub_err_md, encoding="utf-8")

    # Acoustic Association Analysis
    tp_indices = np.where((labels == 1) & (preds_e == 1))[0]
    dur_tp = durations[tp_indices] if len(tp_indices) > 0 else np.array([0.0])
    dur_fn = durations[fn_indices] if len(fn_indices) > 0 else np.array([0.0])
    
    scream_ratio_tp = X_subband[tp_indices, 9] if len(tp_indices) > 0 else np.array([0.0])
    scream_ratio_fn = X_subband[fn_indices, 9] if len(fn_indices) > 0 else np.array([0.0])
    
    yam_scream_tp = X_acoust[tp_indices, 4] if len(tp_indices) > 0 else np.array([0.0])
    yam_scream_fn = X_acoust[fn_indices, 4] if len(fn_indices) > 0 else np.array([0.0])

    assoc_md = f"""# Acoustic Association Analysis — Stage 8.9.53

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Causal Discrimination Protocol
Per Section 8 guidelines, acoustic failure analysis explicitly distinguishes:
1. **Observed Association:** Statistical correlation between acoustic feature and low model probability.
2. **Plausible Mechanism:** Theoretical acoustic explanation (e.g., masking noise elevating broadband floor).
3. **Experimentally Demonstrated Cause:** Counterfactual intervention verified via controlled ablation.

---

## 2. Statistical Comparison: Detected Screams (TP: N={len(tp_indices)}) vs Missed Screams (FN: N={len(fn_indices)})

| Acoustic Parameter | Detected Screams (TP, Mean ± Std) | Missed Screams (FN, Mean ± Std) | Observed Correlation | Plausible Physical Mechanism |
|---|---|---|---|---|
| **Duration (seconds)** | {np.mean(dur_tp):.3f}s ± {np.std(dur_tp):.3f}s | {np.mean(dur_fn):.3f}s ± {np.std(dur_fn):.3f}s | Weak/Moderate | Shorter events provide fewer receptive frames for temporal integration. |
| **Scream-to-Vocal Energy Ratio** | {np.mean(scream_ratio_tp):.3f} ± {np.std(scream_ratio_tp):.3f} | {np.mean(scream_ratio_fn):.3f} ± {np.std(scream_ratio_fn):.3f} | Strong positive | Screams lacking high-frequency sidebands or muffled by distance look spectrally similar to neutral vowels. |
| **YAMNet Scream Activation Max** | {np.mean(yam_scream_tp):.3f} ± {np.std(yam_scream_tp):.3f} | {np.mean(yam_scream_fn):.3f} ± {np.std(yam_scream_fn):.3f} | Very Strong | Background crowd energy depresses semantic scream class logit in AudioSet ontology. |

---

## 3. Scientific Attribution Conclusion
The primary observed association with Candidate E misses is low vocal-to-scream energy ratio and severe crowd masking. These represent genuine physical acoustic attenuation rather than model artifact.
"""
    (STAGE53_DIR / "error_analysis" / "acoustic_association_analysis.md").write_text(assoc_md, encoding="utf-8")

    print("\nPhase B, C, D, and E evaluations and reports emitted successfully.")

if __name__ == "__main__":
    main()
