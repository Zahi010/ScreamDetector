"""
Stage 8.9.44: Phase C & D — Controlled Model Retraining and Threshold Calibration
Trains DualEncoderAcousticModel under 5 controlled conditions:
- Condition A: Authentic v5_train only (Config-B-v5-baseline)
- Condition B: Authentic + RIR Augmentation (Config-B-RIR)
- Condition C: Authentic + Attenuation Augmentation (Config-B-Atten)
- Condition D: Authentic + Background Masking (Config-B-Mask)
- Condition E: Authentic + Combined Environmental Augmentation (Config-B-EnvCombined)

Threshold calibration on v5_validation enforces Hard-Negative FPR <= 5.0%.
Outputs:
- models/<candidate_tag>.pt
- configs/<candidate_tag>.json
- results/training/candidate_training_summary.json
"""
import os
import sys
import time
import json
import csv
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import TensorDataset, DataLoader
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, confusion_matrix

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE43_DIR = BACKEND_DIR / "research" / "stage_8_9_43"
STAGE44_DIR = BACKEND_DIR / "research" / "stage_8_9_44"

YAMNET_V5_CACHE_P = STAGE43_DIR / "features" / "yamnet_v5_cache.npz"
AUG_CACHE_P = STAGE44_DIR / "features" / "augmented_features_v6.npz"

MODELS_DIR = STAGE44_DIR / "models"
CONFIGS_DIR = STAGE44_DIR / "configs"
RESULTS_DIR = STAGE44_DIR / "results" / "training"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
CONFIGS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------
# 1. Architecture: DualEncoderAcousticModel
# -------------------------------------------------------------
class SemanticProjectionHead(nn.Module):
    def __init__(self, input_dim=1024, hidden_dim=256, proj_dim=128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
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

class SupConLoss(nn.Module):
    def __init__(self, temperature=0.05):
        super().__init__()
        self.temperature = temperature
    def forward(self, features, labels):
        batch_size = features.shape[0]
        labels = labels.contiguous().view(-1, 1)
        mask = torch.eq(labels, labels.T).float()
        sim_matrix = torch.div(torch.matmul(features, features.T), self.temperature)
        logits_max, _ = torch.max(sim_matrix, dim=1, keepdim=True)
        logits = sim_matrix - logits_max.detach()
        logits_mask = torch.scatter(
            torch.ones_like(mask), 1, torch.arange(batch_size).view(-1, 1).to(features.device), 0
        )
        mask = mask * logits_mask
        exp_logits = torch.exp(logits) * logits_mask
        denom = exp_logits.sum(1, keepdim=True)
        num_pos = mask.sum(1)
        valid = num_pos > 0
        if not valid.any():
            return torch.tensor(0.0, device=features.device, requires_grad=True)
        log_prob = logits - torch.log(denom + 1e-9)
        mean_log_prob_pos = (mask * log_prob).sum(1)[valid] / num_pos[valid]
        return -mean_log_prob_pos.mean()

# -------------------------------------------------------------
# 2. Calibration & ECE Metrics
# -------------------------------------------------------------
def compute_ece(targets, probs, n_bins=10):
    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    n = len(targets)
    for i in range(n_bins):
        b_low, b_high = bin_edges[i], bin_edges[i + 1]
        mask = (probs >= b_low) & (probs < b_high if i < n_bins - 1 else probs <= b_high)
        if np.sum(mask) > 0:
            bin_acc = np.mean(targets[mask])
            bin_conf = np.mean(probs[mask])
            ece += (np.sum(mask) / n) * np.abs(bin_acc - bin_conf)
    return float(ece)

def calibrate_threshold(targets, probs, categories, max_fpr=0.05):
    best_f1 = 0.0
    best_th = 0.50
    best_rec = 0.0
    best_hn_fpr = 0.0
    best_shout_fpr = 0.0
    is_shout = np.array([c == "shouting_and_speech" for c in categories])

    for th in np.linspace(0.10, 0.95, 86):
        preds = (probs >= th).astype(int)
        tn, fp, fn, tp = confusion_matrix(targets, preds, labels=[0, 1]).ravel()
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0.0
        if fpr <= max_fpr and f1 > best_f1:
            best_f1 = f1
            best_th = th
            best_rec = rec
            best_hn_fpr = fpr
            shout_fp = np.sum((probs >= th)[is_shout]) if np.sum(is_shout) > 0 else 0
            best_shout_fpr = shout_fp / np.sum(is_shout) if np.sum(is_shout) > 0 else 0.0

    return float(best_th), float(best_f1), float(best_rec), float(best_hn_fpr), float(best_shout_fpr)

# -------------------------------------------------------------
# 3. Training Loop
# -------------------------------------------------------------
def train_candidate(cand_id, cand_tag, X_sem_tr, X_ac_tr, M_ac_tr, y_tr, X_sem_va, X_ac_va, M_ac_va, y_va, cats_va, epochs=40, lr=1e-3, batch_size=32):
    print(f"\n==================================================")
    print(f"Training: {cand_id} ({cand_tag})")
    print(f"Train samples: {len(y_tr)} (Pos: {int((y_tr==1).sum())}, Neg: {int((y_tr==0).sum())})")
    print(f"Val samples: {len(y_va)} (Pos: {int((y_va==1).sum())}, Neg: {int((y_va==0).sum())})")
    print(f"==================================================")

    torch.manual_seed(42)
    np.random.seed(42)

    n_pos = int((y_tr == 1).sum())
    n_neg = int((y_tr == 0).sum())
    pos_weight = torch.tensor([n_neg / max(n_pos, 1)], dtype=torch.float32)

    model = DualEncoderAcousticModel()
    criterion_bce = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    criterion_supcon = SupConLoss(temperature=0.05)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)

    ds_tr = TensorDataset(
        torch.tensor(X_sem_tr, dtype=torch.float32),
        torch.tensor(X_ac_tr, dtype=torch.float32),
        torch.tensor(M_ac_tr, dtype=torch.float32),
        torch.tensor(y_tr, dtype=torch.float32)
    )
    loader_tr = DataLoader(ds_tr, batch_size=batch_size, shuffle=True)

    t_sem_va = torch.tensor(X_sem_va, dtype=torch.float32)
    t_ac_va = torch.tensor(X_ac_va, dtype=torch.float32)
    t_m_va = torch.tensor(M_ac_va, dtype=torch.float32)

    best_val_auc = 0.0
    best_state = None
    best_probs = None

    for ep in range(1, epochs + 1):
        model.train()
        for b_sem, b_ac, b_m, b_y in loader_tr:
            optimizer.zero_grad()
            logits, z_sem, z_ac = model(b_sem, b_ac, b_m)
            loss_bce = criterion_bce(logits, b_y)
            z_fused = torch.cat([z_sem, z_ac], dim=-1)
            loss_con = criterion_supcon(z_fused, b_y)
            loss = loss_bce + 0.15 * loss_con
            loss.backward()
            optimizer.step()
        scheduler.step()

        # Validation
        model.eval()
        with torch.no_grad():
            logits_va, _, _ = model(t_sem_va, t_ac_va, t_m_va)
            probs_va = torch.sigmoid(logits_va).numpy()
            auc_va = roc_auc_score(y_va, probs_va)
            if auc_va > best_val_auc:
                best_val_auc = auc_va
                best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
                best_probs = probs_va

    # Calibrate on validation set
    th_star, f1, rec, hn_fpr, shout_fpr = calibrate_threshold(y_va, best_probs, cats_va)
    ap_va = float(average_precision_score(y_va, best_probs))
    brier_va = float(brier_score_loss(y_va, best_probs))
    ece_va = compute_ece(y_va, best_probs)

    print(f"Result {cand_id}: Val AUC={best_val_auc:.4f}, AP={ap_va:.4f}, F1={f1:.4f}, Rec={rec*100:.1f}%, HN-FPR={hn_fpr*100:.2f}%, Shout-FPR={shout_fpr*100:.2f}%, Brier={brier_va:.4f}, ECE={ece_va:.4f} (theta*={th_star:.4f})")

    # Save model checkpoint
    ckpt_p = MODELS_DIR / f"{cand_tag}.pt"
    torch.save(best_state, ckpt_p)

    cfg = {
        "candidate_id": cand_id,
        "candidate_tag": cand_tag,
        "architecture": "DualEncoderAcousticModel",
        "checkpoint": str(ckpt_p.name),
        "selected_threshold": round(th_star, 4),
        "val_auc": round(best_val_auc, 4),
        "val_ap": round(ap_va, 4),
        "val_f1": round(f1, 4),
        "val_recall": round(rec * 100, 2),
        "val_hn_fpr": round(hn_fpr * 100, 2),
        "val_shouted_speech_fpr": round(shout_fpr * 100, 2),
        "val_brier_score": round(brier_va, 4),
        "val_ece": round(ece_va, 4),
        "train_samples": len(y_tr),
        "train_pos": n_pos,
        "train_neg": n_neg
    }
    with open(CONFIGS_DIR / f"{cand_tag}.json", "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

    return cfg

def main():
    print("=" * 80)
    print("STAGE 8.9.44: TRAINING 5 CONTROLLED ENVIRONMENTAL CANDIDATES")
    print("=" * 80)
    t0 = time.time()

    # 1. Load authentic v5 cache
    y_data = np.load(YAMNET_V5_CACHE_P, allow_pickle=True)
    splits = y_data["splits"]
    tr_mask = (splits == "v5_train")
    va_mask = (splits == "v5_validation")

    X_sem_base = y_data["X_sem"][tr_mask]
    X_ac_base = y_data["X_acoust"][tr_mask]
    M_ac_base = y_data["mask_acoust"][tr_mask]
    y_base = y_data["labels"][tr_mask]

    X_sem_va = y_data["X_sem"][va_mask]
    X_ac_va = y_data["X_acoust"][va_mask]
    M_ac_va = y_data["mask_acoust"][va_mask]
    y_va = y_data["labels"][va_mask]
    cats_va = y_data["categories"][va_mask]

    # 2. Load augmented cache
    aug_data = np.load(AUG_CACHE_P, allow_pickle=True)
    aug_conds = aug_data["conditions"]

    all_configs = []

    # Condition A: Authentic v5_train only
    cfg_a = train_candidate(
        "Candidate A (Config-B-v5-baseline)", "config_b_v5_baseline",
        X_sem_base, X_ac_base, M_ac_base, y_base,
        X_sem_va, X_ac_va, M_ac_va, y_va, cats_va
    )
    all_configs.append(cfg_a)

    # Condition B: Authentic + RIR
    m_b = (aug_conds == "B")
    X_sem_b = np.concatenate([X_sem_base, aug_data["X_sem"][m_b]], axis=0)
    X_ac_b = np.concatenate([X_ac_base, aug_data["X_acoust"][m_b]], axis=0)
    M_ac_b = np.concatenate([M_ac_base, aug_data["mask_acoust"][m_b]], axis=0)
    y_b = np.concatenate([y_base, np.ones(np.sum(m_b), dtype=np.int32)], axis=0)
    cfg_b = train_candidate(
        "Candidate B (Config-B-RIR)", "config_b_rir",
        X_sem_b, X_ac_b, M_ac_b, y_b,
        X_sem_va, X_ac_va, M_ac_va, y_va, cats_va
    )
    all_configs.append(cfg_b)

    # Condition C: Authentic + Attenuation
    m_c = (aug_conds == "C")
    X_sem_c = np.concatenate([X_sem_base, aug_data["X_sem"][m_c]], axis=0)
    X_ac_c = np.concatenate([X_ac_base, aug_data["X_acoust"][m_c]], axis=0)
    M_ac_c = np.concatenate([M_ac_base, aug_data["mask_acoust"][m_c]], axis=0)
    y_c = np.concatenate([y_base, np.ones(np.sum(m_c), dtype=np.int32)], axis=0)
    cfg_c = train_candidate(
        "Candidate C (Config-B-Atten)", "config_b_atten",
        X_sem_c, X_ac_c, M_ac_c, y_c,
        X_sem_va, X_ac_va, M_ac_va, y_va, cats_va
    )
    all_configs.append(cfg_c)

    # Condition D: Authentic + Background Masking
    m_d = (aug_conds == "D")
    X_sem_d = np.concatenate([X_sem_base, aug_data["X_sem"][m_d]], axis=0)
    X_ac_d = np.concatenate([X_ac_base, aug_data["X_acoust"][m_d]], axis=0)
    M_ac_d = np.concatenate([M_ac_base, aug_data["mask_acoust"][m_d]], axis=0)
    y_d = np.concatenate([y_base, np.ones(np.sum(m_d), dtype=np.int32)], axis=0)
    cfg_d = train_candidate(
        "Candidate D (Config-B-Mask)", "config_b_mask",
        X_sem_d, X_ac_d, M_ac_d, y_d,
        X_sem_va, X_ac_va, M_ac_va, y_va, cats_va
    )
    all_configs.append(cfg_d)

    # Condition E: Authentic + Combined Environmental
    m_e = (aug_conds == "E")
    X_sem_e = np.concatenate([X_sem_base, aug_data["X_sem"][m_e]], axis=0)
    X_ac_e = np.concatenate([X_ac_base, aug_data["X_acoust"][m_e]], axis=0)
    M_ac_e = np.concatenate([M_ac_base, aug_data["mask_acoust"][m_e]], axis=0)
    y_e = np.concatenate([y_base, np.ones(np.sum(m_e), dtype=np.int32)], axis=0)
    cfg_e = train_candidate(
        "Candidate E (Config-B-EnvCombined)", "config_b_env_combined",
        X_sem_e, X_ac_e, M_ac_e, y_e,
        X_sem_va, X_ac_va, M_ac_va, y_va, cats_va
    )
    all_configs.append(cfg_e)

    # Save summary
    out_json = RESULTS_DIR / "candidate_training_summary.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(all_configs, f, indent=2)

    print(f"\nAll 5 candidates trained and calibrated in {time.time() - t0:.1f}s.")
    print(f"Training summary saved: {out_json}")

if __name__ == "__main__":
    main()

