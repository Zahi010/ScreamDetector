"""
Stage 8.9.46: Phase C & D — Train Probabilistic Augmentation Ratio Candidates
Investigates the effect of pristine-to-augmented positive sample ratios on generalization:
- Candidate R1: Config-B-Ratio-100P-0A (100% pristine / 0% transformed)
- Candidate R2: Config-B-Ratio-75P-25A (75% pristine / 25% transformed)
- Candidate R3: Config-B-Ratio-50P-50A (50% pristine / 50% transformed)
- Candidate R4: Config-B-Ratio-25P-75A (25% pristine / 75% transformed)
- Candidate R5: Config-B-Ratio-0P-100A (0% pristine / 100% transformed)
- Candidate R6: Config-B-Dynamic-50P-50A (Dynamic epoch-level 50/50 probabilistic sampling)

MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
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
from torch.utils.data import TensorDataset, DataLoader, Dataset
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, confusion_matrix

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE43_DIR = BACKEND_DIR / "research" / "stage_8_9_43"
STAGE45_DIR = BACKEND_DIR / "research" / "stage_8_9_45"
STAGE46_DIR = BACKEND_DIR / "research" / "stage_8_9_46"

YAMNET_V5_CACHE_P = STAGE43_DIR / "features" / "yamnet_v5_cache.npz"
AUG_CACHE_V7_P = STAGE45_DIR / "features" / "augmented_features_v7.npz"

MODELS_DIR = STAGE46_DIR / "models"
CONFIGS_DIR = STAGE46_DIR / "configs"
AUG_DIR = STAGE46_DIR / "augmentation"
RESULTS_DIR = STAGE46_DIR / "results" / "training"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
CONFIGS_DIR.mkdir(parents=True, exist_ok=True)
AUG_DIR.mkdir(parents=True, exist_ok=True)
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
# 3. Dynamic Epoch Dataset for Candidate R6
# -------------------------------------------------------------
class DynamicRatioDataset(Dataset):
    def __init__(self, X_sem_base, X_ac_base, M_ac_base, y_base,
                 X_sem_pristine, X_ac_pristine, M_ac_pristine,
                 X_sem_trans, X_ac_trans, M_ac_trans,
                 p_transform=0.5):
        self.X_sem_base = torch.tensor(X_sem_base, dtype=torch.float32)
        self.X_ac_base = torch.tensor(X_ac_base, dtype=torch.float32)
        self.M_ac_base = torch.tensor(M_ac_base, dtype=torch.float32)
        self.y_base = torch.tensor(y_base, dtype=torch.float32)

        self.X_sem_pristine = torch.tensor(X_sem_pristine, dtype=torch.float32)
        self.X_ac_pristine = torch.tensor(X_ac_pristine, dtype=torch.float32)
        self.M_ac_pristine = torch.tensor(M_ac_pristine, dtype=torch.float32)

        self.X_sem_trans = torch.tensor(X_sem_trans, dtype=torch.float32)
        self.X_ac_trans = torch.tensor(X_ac_trans, dtype=torch.float32)
        self.M_ac_trans = torch.tensor(M_ac_trans, dtype=torch.float32)

        self.p_transform = p_transform
        self.n_base = len(self.y_base)
        self.n_aug = len(self.X_sem_trans)
        self.n_total = self.n_base + self.n_aug

    def __len__(self):
        return self.n_total

    def __getitem__(self, idx):
        if idx < self.n_base:
            return self.X_sem_base[idx], self.X_ac_base[idx], self.M_ac_base[idx], self.y_base[idx]
        else:
            aug_idx = idx - self.n_base
            # Dynamic sampling: with probability p_transform, use transformed; else pristine
            if torch.rand(1).item() < self.p_transform:
                return self.X_sem_trans[aug_idx], self.X_ac_trans[aug_idx], self.M_ac_trans[aug_idx], torch.tensor(1.0)
            else:
                return self.X_sem_pristine[aug_idx], self.X_ac_pristine[aug_idx], self.M_ac_pristine[aug_idx], torch.tensor(1.0)

# -------------------------------------------------------------
# 4. Training Function
# -------------------------------------------------------------
def train_model(cand_id, cand_tag, loader_tr, n_train_pos, n_train_neg,
                X_sem_va, X_ac_va, M_ac_va, y_va, cats_va, epochs=40, lr=1e-3):
    print(f"\n==================================================")
    print(f"Training: {cand_id} ({cand_tag})")
    print(f"Train Pos: {n_train_pos}, Train Neg: {n_train_neg} | Val Samples: {len(y_va)}")
    print(f"==================================================")

    torch.manual_seed(42)
    np.random.seed(42)

    pos_weight = torch.tensor([n_train_neg / max(n_train_pos, 1)], dtype=torch.float32)

    model = DualEncoderAcousticModel()
    criterion_bce = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    criterion_supcon = SupConLoss(temperature=0.05)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)

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
        "train_samples": n_train_pos + n_train_neg,
        "train_pos": n_train_pos,
        "train_neg": n_train_neg
    }
    cfg_p = CONFIGS_DIR / f"{cand_tag}.json"
    with open(cfg_p, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

    return cfg

def main():
    print("=" * 80)
    print("STAGE 8.9.46: TRAINING PROBABILISTIC AUGMENTATION RATIO EXPERIMENT")
    print("=" * 80)

    # 1. Load Base Features
    base_cache = np.load(YAMNET_V5_CACHE_P, allow_pickle=True)
    splits = base_cache["splits"]
    labels = base_cache["labels"]
    categories = base_cache["categories"]
    file_ids = base_cache["file_ids"]
    sgs = base_cache["source_groups"]

    tr_mask = (splits == "v5_train")
    va_mask = (splits == "v5_validation")

    X_sem_tr_base = base_cache["X_sem"][tr_mask]
    X_ac_tr_base = base_cache["X_acoust"][tr_mask]
    M_ac_tr_base = base_cache["mask_acoust"][tr_mask]
    y_tr_base = labels[tr_mask]

    # Authentic training positive features (N=401)
    tr_pos_submask = (y_tr_base == 1)
    X_sem_tr_pos_auth = X_sem_tr_base[tr_pos_submask]
    X_ac_tr_pos_auth = X_ac_tr_base[tr_pos_submask]
    M_ac_tr_pos_auth = M_ac_tr_base[tr_pos_submask]
    fids_tr_pos = file_ids[tr_mask][tr_pos_submask]
    sgs_tr_pos = sgs[tr_mask][tr_pos_submask]

    # Validation
    X_sem_va = base_cache["X_sem"][va_mask]
    X_ac_va = base_cache["X_acoust"][va_mask]
    M_ac_va = base_cache["mask_acoust"][va_mask]
    y_va = labels[va_mask]
    cats_va = categories[va_mask]

    # 2. Load Transformed Features (Alternate Condition C and Condition E)
    aug_cache = np.load(AUG_CACHE_V7_P, allow_pickle=True)
    c_mask = (aug_cache["conditions"] == "C")
    e_mask = (aug_cache["conditions"] == "E")

    X_sem_c = aug_cache["X_sem"][c_mask]
    X_ac_c = aug_cache["X_acoust"][c_mask]
    M_ac_c = aug_cache["mask_acoust"][c_mask]

    X_sem_e = aug_cache["X_sem"][e_mask]
    X_ac_e = aug_cache["X_acoust"][e_mask]
    M_ac_e = aug_cache["mask_acoust"][e_mask]

    # Blended transformed pool: even indices use C, odd indices use E
    N_pos = len(X_sem_tr_pos_auth)  # 401
    X_sem_trans = np.zeros_like(X_sem_c)
    X_ac_trans = np.zeros_like(X_ac_c)
    M_ac_trans = np.zeros_like(M_ac_c)

    for i in range(N_pos):
        if i % 2 == 0:
            X_sem_trans[i] = X_sem_c[i]
            X_ac_trans[i] = X_ac_c[i]
            M_ac_trans[i] = M_ac_c[i]
        else:
            X_sem_trans[i] = X_sem_e[i]
            X_ac_trans[i] = X_ac_e[i]
            M_ac_trans[i] = M_ac_e[i]

    # 3. Ratio Configurations
    ratios = [
        ("Candidate R1 (Ratio-100P-0A)", "config_b_ratio_100p_0a", 1.0, 0.0),
        ("Candidate R2 (Ratio-75P-25A)", "config_b_ratio_75p_25a", 0.75, 0.25),
        ("Candidate R3 (Ratio-50P-50A)", "config_b_ratio_50p_50a", 0.50, 0.50),
        ("Candidate R4 (Ratio-25P-75A)", "config_b_ratio_25p_75a", 0.25, 0.75),
        ("Candidate R5 (Ratio-0P-100A)", "config_b_ratio_0p_100a", 0.0, 1.0),
    ]

    configs = {}

    for cand_id, cand_tag, p_pristine, p_trans in ratios:
        n_trans = int(round(N_pos * p_trans))
        n_pristine = N_pos - n_trans

        # Construct augmented slot
        X_sem_aug_slot = np.zeros_like(X_sem_tr_pos_auth)
        X_ac_aug_slot = np.zeros_like(X_ac_tr_pos_auth)
        M_ac_aug_slot = np.zeros_like(M_ac_tr_pos_auth)

        # Transformed indices: uniformly spaced across the 401 clips
        if n_trans > 0:
            trans_indices = set(np.round(np.linspace(0, N_pos - 1, n_trans)).astype(int))
        else:
            trans_indices = set()

        manifest_rows = []
        for i in range(N_pos):
            fid = fids_tr_pos[i]
            sg = sgs_tr_pos[i]
            if i in trans_indices:
                X_sem_aug_slot[i] = X_sem_trans[i]
                X_ac_aug_slot[i] = X_ac_trans[i]
                M_ac_aug_slot[i] = M_ac_trans[i]
                trans_type = "Transformed_MildMask" if i % 2 == 0 else "Transformed_MaskAtten"
            else:
                X_sem_aug_slot[i] = X_sem_tr_pos_auth[i]
                X_ac_aug_slot[i] = X_ac_tr_pos_auth[i]
                M_ac_aug_slot[i] = M_ac_tr_pos_auth[i]
                trans_type = "Pristine_Authentic"

            manifest_rows.append({
                "slot_id": f"aug_slot_{cand_tag}_{fid}",
                "original_file_id": fid,
                "source_group_id": sg,
                "assigned_type": trans_type,
                "ratio_condition": cand_tag
            })

        # Save manifest
        mf_p = AUG_DIR / f"augmentation_manifest_{cand_tag}.csv"
        with open(mf_p, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(manifest_rows[0].keys()))
            writer.writeheader()
            writer.writerows(manifest_rows)

        # Assemble full training set
        X_sem_tr = np.vstack([X_sem_tr_base, X_sem_aug_slot])
        X_ac_tr = np.vstack([X_ac_tr_base, X_ac_aug_slot])
        M_ac_tr = np.vstack([M_ac_tr_base, M_ac_aug_slot])
        y_tr = np.concatenate([y_tr_base, np.ones(N_pos, dtype=int)])

        ds_tr = TensorDataset(
            torch.tensor(X_sem_tr, dtype=torch.float32),
            torch.tensor(X_ac_tr, dtype=torch.float32),
            torch.tensor(M_ac_tr, dtype=torch.float32),
            torch.tensor(y_tr, dtype=torch.float32)
        )
        loader_tr = DataLoader(ds_tr, batch_size=32, shuffle=True)

        n_pos_tot = int((y_tr == 1).sum())  # 802
        n_neg_tot = int((y_tr == 0).sum())  # 797

        cfg = train_model(
            cand_id, cand_tag, loader_tr, n_pos_tot, n_neg_tot,
            X_sem_va, X_ac_va, M_ac_va, y_va, cats_va
        )
        configs[cand_tag] = cfg

    # 4. Candidate R6: Dynamic 50/50 Probabilistic Sampling
    cand_id_r6 = "Candidate R6 (Dynamic-50P-50A)"
    cand_tag_r6 = "config_b_dynamic_50p_50a"

    ds_dyn = DynamicRatioDataset(
        X_sem_tr_base, X_ac_tr_base, M_ac_tr_base, y_tr_base,
        X_sem_tr_pos_auth, X_ac_tr_pos_auth, M_ac_tr_pos_auth,
        X_sem_trans, X_ac_trans, M_ac_trans,
        p_transform=0.5
    )
    loader_dyn = DataLoader(ds_dyn, batch_size=32, shuffle=True)

    # Save manifest for dynamic condition
    dyn_rows = [{
        "slot_id": f"aug_slot_dyn_{fids_tr_pos[i]}",
        "original_file_id": fids_tr_pos[i],
        "source_group_id": sgs_tr_pos[i],
        "assigned_type": "Dynamic_Bernoulli_p0.5",
        "ratio_condition": cand_tag_r6
    } for i in range(N_pos)]
    mf_dyn_p = AUG_DIR / f"augmentation_manifest_{cand_tag_r6}.csv"
    with open(mf_dyn_p, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(dyn_rows[0].keys()))
        writer.writeheader()
        writer.writerows(dyn_rows)

    cfg_r6 = train_model(
        cand_id_r6, cand_tag_r6, loader_dyn, 802, 797,
        X_sem_va, X_ac_va, M_ac_va, y_va, cats_va
    )
    configs[cand_tag_r6] = cfg_r6

    # Save summary
    summary_p = RESULTS_DIR / "candidate_training_summary_v8.json"
    with open(summary_p, "w", encoding="utf-8") as f:
        json.dump(configs, f, indent=2)
    print(f"\nAll 6 ratio candidates successfully trained and saved.")

if __name__ == "__main__":
    main()

