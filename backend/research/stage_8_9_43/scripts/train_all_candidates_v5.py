"""
Stage 8.9.43: Phase 6 — Controlled Retraining of All 4 Model Candidates on Dataset Manifest v5
Trained strictly on v5_train (N=1,198).
Thresholds selected strictly on v5_validation (N=309) to enforce Hard-Negative FPR <= 5.0%.

Candidates:
1. Candidate A: Config-B-v5 (DualEncoderAcousticModel on YAMNet 1024-d + 6-d phonation features)
2. Candidate B: CNN-LogMel-v5 (CustomLogMelCNN on 64-bin log-mel spectrograms)
3. Candidate C: CNN-MultiScale-v5 (CustomMultiScaleCNN with 3x3, 3x7, 3x15 temporal kernels)
4. Candidate D: CNN-Temporal-v5 (CustomTemporalCNN with temporal conv pooling)

Outputs:
- models/<candidate_id>.pt
- configs/<candidate_id>.json
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
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score, precision_score, recall_score, confusion_matrix

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE43_DIR = BACKEND_DIR / "research" / "stage_8_9_43"

MANIFEST_P = STAGE43_DIR / "manifests" / "dataset_manifest_v5.csv"
LOGMEL_CACHE_P = STAGE43_DIR / "features" / "logmel_v5_cache.npz"
YAMNET_CACHE_P = STAGE43_DIR / "features" / "yamnet_v5_cache.npz"

MODELS_DIR = STAGE43_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
CONFIGS_DIR = STAGE43_DIR / "configs"
CONFIGS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR = STAGE43_DIR / "results" / "training"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------
# 1. Candidate A: Config-B-v5 (DualEncoderAcousticModel)
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
# 2. Candidate B: CustomLogMelCNN
# -------------------------------------------------------------
class CustomLogMelCNN(nn.Module):
    def __init__(self, in_channels=1, num_classes=1):
        super().__init__()
        self.conv1 = nn.Sequential(nn.Conv2d(in_channels, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(), nn.MaxPool2d(2, 2))
        self.conv2 = nn.Sequential(nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(), nn.MaxPool2d(2, 2))
        self.conv3 = nn.Sequential(nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(), nn.MaxPool2d(2, 2))
        self.conv4 = nn.Sequential(nn.Conv2d(128, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU())
        self.fc = nn.Sequential(nn.Linear(128 * 2, 64), nn.ReLU(), nn.Dropout(0.3), nn.Linear(64, num_classes))

    def forward(self, x):
        h = self.conv4(self.conv3(self.conv2(self.conv1(x))))
        avg_p = F.adaptive_avg_pool2d(h, (1, 1)).flatten(1)
        max_p = F.adaptive_max_pool2d(h, (1, 1)).flatten(1)
        return self.fc(torch.cat([avg_p, max_p], dim=1)).squeeze(-1)

# -------------------------------------------------------------
# 3. Candidate C: CustomMultiScaleCNN
# -------------------------------------------------------------
class MultiScaleTemporalBlock(nn.Module):
    def __init__(self, in_c, out_c):
        super().__init__()
        branch_c = out_c // 3
        rem_c = out_c - branch_c * 2
        self.b1 = nn.Sequential(nn.Conv2d(in_c, branch_c, (3, 3), padding=(1, 1)), nn.BatchNorm2d(branch_c), nn.ReLU())
        self.b2 = nn.Sequential(nn.Conv2d(in_c, branch_c, (3, 7), padding=(1, 3)), nn.BatchNorm2d(branch_c), nn.ReLU())
        self.b3 = nn.Sequential(nn.Conv2d(in_c, rem_c, (3, 15), padding=(1, 7)), nn.BatchNorm2d(rem_c), nn.ReLU())

    def forward(self, x):
        return torch.cat([self.b1(x), self.b2(x), self.b3(x)], dim=1)

class CustomMultiScaleCNN(nn.Module):
    def __init__(self, in_channels=1, num_classes=1):
        super().__init__()
        self.stem = nn.Sequential(nn.Conv2d(in_channels, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(), nn.MaxPool2d(2, 2))
        self.ms1 = MultiScaleTemporalBlock(32, 64)
        self.pool1 = nn.MaxPool2d(2, 2)
        self.ms2 = MultiScaleTemporalBlock(64, 128)
        self.pool2 = nn.MaxPool2d(2, 2)
        self.conv_final = nn.Sequential(nn.Conv2d(128, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU())
        self.fc = nn.Sequential(nn.Linear(128 * 2, 64), nn.ReLU(), nn.Dropout(0.3), nn.Linear(64, num_classes))

    def forward(self, x):
        h = self.conv_final(self.pool2(self.ms2(self.pool1(self.ms1(self.stem(x))))))
        avg_p = F.adaptive_avg_pool2d(h, (1, 1)).flatten(1)
        max_p = F.adaptive_max_pool2d(h, (1, 1)).flatten(1)
        return self.fc(torch.cat([avg_p, max_p], dim=1)).squeeze(-1)

# -------------------------------------------------------------
# 4. Candidate D: CustomTemporalCNN
# -------------------------------------------------------------
class CustomTemporalCNN(nn.Module):
    """
    Candidate D: Preserves temporal resolution across frames and applies 
    temporal 1D convolutions + max pooling across time.
    Specially responsive to ultra-short bursts (<500ms).
    """
    def __init__(self, in_channels=1, num_classes=1):
        super().__init__()
        self.stem = nn.Sequential(nn.Conv2d(in_channels, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(), nn.MaxPool2d((2, 1), (2, 1)))
        self.ms1 = MultiScaleTemporalBlock(32, 64)
        self.pool1 = nn.MaxPool2d((2, 1), (2, 1))
        self.ms2 = MultiScaleTemporalBlock(64, 128)
        self.pool2 = nn.MaxPool2d((2, 1), (2, 1))
        # Now frequency dimension is 64 / 8 = 8 bins.
        self.freq_pool = nn.AdaptiveAvgPool2d((1, None)) # (B, 128, 1, T)
        self.temporal_conv = nn.Sequential(
            nn.Conv1d(128, 128, kernel_size=5, padding=2),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Conv1d(128, 64, kernel_size=3, padding=1),
            nn.BatchNorm1d(64),
            nn.ReLU()
        )
        self.fc = nn.Sequential(
            nn.Linear(64 * 2, 32),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(32, num_classes)
        )

    def forward(self, x):
        # x: (B, 1, 64, T)
        h = self.pool2(self.ms2(self.pool1(self.ms1(self.stem(x)))))
        h_t = self.freq_pool(h).squeeze(2) # (B, 128, T)
        t_feats = self.temporal_conv(h_t)   # (B, 64, T)
        # Max-pool and avg-pool over time
        max_t = torch.max(t_feats, dim=-1)[0]
        avg_t = torch.mean(t_feats, dim=-1)
        fused = torch.cat([max_t, avg_t], dim=-1)
        return self.fc(fused).squeeze(-1)

# -------------------------------------------------------------
# 5. LogMel Dataset
# -------------------------------------------------------------
class LogMelDataset(Dataset):
    def __init__(self, cache_data, file_ids, is_train=True, target_len=64):
        self.cache_data = cache_data
        self.file_ids = list(file_ids)
        self.is_train = is_train
        self.target_len = target_len

    def __len__(self):
        return len(self.file_ids)

    def __getitem__(self, idx):
        fid = self.file_ids[idx]
        lmel = self.cache_data[f"logmel_{fid}"]
        all_fids = self.cache_data["file_ids"]
        f_idx = np.where(all_fids == fid)[0][0]
        label = int(self.cache_data["labels"][f_idx])
        T = lmel.shape[1]
        if self.is_train:
            if T > self.target_len:
                start = np.random.randint(0, T - self.target_len + 1)
                patch = lmel[:, start:start + self.target_len]
            else:
                pad_len = self.target_len - T
                pad_l = pad_len // 2
                pad_r = pad_len - pad_l
                patch = np.pad(lmel, ((0, 0), (pad_l, pad_r)), mode="edge")
        else:
            if T < 16:
                patch = np.pad(lmel, ((0, 0), (0, 16 - T)), mode="edge")
            else:
                patch = lmel
        return torch.tensor(patch, dtype=torch.float32).unsqueeze(0), torch.tensor(label, dtype=torch.float32), fid

def collate_fn_logmel(batch):
    batch.sort(key=lambda x: x[0].shape[2], reverse=True)
    max_len = max(x[0].shape[2] for x in batch)
    tensors, labels, fids = [], [], []
    for x, y, fid in batch:
        T = x.shape[2]
        if T < max_len:
            x = F.pad(x, (0, max_len - T), mode="replicate")
        tensors.append(x)
        labels.append(y)
        fids.append(fid)
    return torch.stack(tensors, dim=0), torch.tensor(labels, dtype=torch.float32), fids

# -------------------------------------------------------------
# 6. Training Pipeline Functions
# -------------------------------------------------------------
def calibrate_threshold(targets, probs, categories, max_fpr=0.05):
    best_f1 = 0.0
    best_th = 0.50
    best_rec = 0.0
    best_hn_fpr = 0.0
    best_shout_fpr = 0.0
    is_shout = np.array([c == "shouting_and_speech" for c in categories])

    for th in np.linspace(0.05, 0.95, 91):
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

def train_config_b(y_data, train_mask, val_mask, epochs=40, lr=1e-3, batch_size=32):
    print("\n--- Training Candidate A: Config-B-v5 (DualEncoderAcousticModel) ---")
    torch.manual_seed(42)
    np.random.seed(42)

    X_sem_tr = torch.tensor(y_data["X_sem"][train_mask], dtype=torch.float32)
    X_ac_tr = torch.tensor(y_data["X_acoust"][train_mask], dtype=torch.float32)
    M_ac_tr = torch.tensor(y_data["mask_acoust"][train_mask], dtype=torch.float32)
    y_tr = torch.tensor(y_data["labels"][train_mask], dtype=torch.float32)

    X_sem_va = torch.tensor(y_data["X_sem"][val_mask], dtype=torch.float32)
    X_ac_va = torch.tensor(y_data["X_acoust"][val_mask], dtype=torch.float32)
    M_ac_va = torch.tensor(y_data["mask_acoust"][val_mask], dtype=torch.float32)
    y_va = y_data["labels"][val_mask]
    cats_va = y_data["categories"][val_mask]

    n_pos = int(y_tr.sum().item())
    n_neg = len(y_tr) - n_pos
    pos_weight = torch.tensor([n_neg / max(n_pos, 1)], dtype=torch.float32)

    model = DualEncoderAcousticModel()
    criterion_bce = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    criterion_supcon = SupConLoss(temperature=0.05)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)

    dataset_tr = torch.utils.data.TensorDataset(X_sem_tr, X_ac_tr, M_ac_tr, y_tr)
    loader_tr = DataLoader(dataset_tr, batch_size=batch_size, shuffle=True)

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

        # Validation eval
        model.eval()
        with torch.no_grad():
            logits_va, _, _ = model(X_sem_va, X_ac_va, M_ac_va)
            probs_va = torch.sigmoid(logits_va).numpy()
            auc_va = roc_auc_score(y_va, probs_va)
            if auc_va > best_val_auc:
                best_val_auc = auc_va
                best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
                best_probs = probs_va

    model.load_state_dict(best_state)
    th_star, f1, rec, hn_fpr, shout_fpr = calibrate_threshold(y_va, best_probs, cats_va)
    ap_va = average_precision_score(y_va, best_probs)
    print(f"Candidate A Best Val AUC: {best_val_auc:.4f}, AP: {ap_va:.4f}, F1: {f1:.4f}, Recall: {rec*100:.1f}%, HN-FPR: {hn_fpr*100:.2f}%, Shout-FPR: {shout_fpr*100:.2f}% (theta*={th_star:.2f})")

    ckpt_p = MODELS_DIR / "config_b_v5.pt"
    torch.save(best_state, ckpt_p)
    cfg = {
        "candidate_id": "Config-B-v5",
        "architecture": "DualEncoderAcousticModel",
        "checkpoint": str(ckpt_p.name),
        "selected_threshold": th_star,
        "val_auc": round(best_val_auc, 4),
        "val_ap": round(ap_va, 4),
        "val_f1": round(f1, 4),
        "val_recall": round(rec * 100, 2),
        "val_hn_fpr": round(hn_fpr * 100, 2),
        "val_shouted_speech_fpr": round(shout_fpr * 100, 2)
    }
    with open(CONFIGS_DIR / "config_b_v5.json", "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

    return cfg, best_val_auc

def train_cnn(candidate_id, model_class, cache_lm, train_fids, val_fids, epochs=35, lr=1e-3, batch_size=32):
    print(f"\n--- Training {candidate_id}: {model_class.__name__} ---")
    torch.manual_seed(42)
    np.random.seed(42)

    train_ds = LogMelDataset(cache_lm, train_fids, is_train=True, target_len=64)
    val_ds = LogMelDataset(cache_lm, val_fids, is_train=False)

    loader_tr = DataLoader(train_ds, batch_size=batch_size, shuffle=True, collate_fn=collate_fn_logmel)
    loader_va = DataLoader(val_ds, batch_size=1, shuffle=False)

    all_fids = cache_lm["file_ids"]
    train_idx = [np.where(all_fids == fid)[0][0] for fid in train_fids]
    val_idx = [np.where(all_fids == fid)[0][0] for fid in val_fids]

    train_labels = cache_lm["labels"][train_idx]
    val_labels = cache_lm["labels"][val_idx]
    val_cats = cache_lm["categories"][val_idx]

    n_pos = np.sum(train_labels == 1)
    n_neg = np.sum(train_labels == 0)
    pos_weight = torch.tensor([n_neg / max(n_pos, 1)], dtype=torch.float32)

    model = model_class()
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)

    best_val_auc = 0.0
    best_state = None
    best_probs = None

    for ep in range(1, epochs + 1):
        model.train()
        for x, y, _ in loader_tr:
            optimizer.zero_grad()
            logits = model(x)
            loss = criterion(logits, y)
            loss.backward()
            optimizer.step()
        scheduler.step()

        # Validation
        model.eval()
        val_logits = []
        with torch.no_grad():
            for x, _, _ in loader_va:
                val_logits.append(model(x).item())
        probs_va = 1.0 / (1.0 + np.exp(-np.array(val_logits)))
        auc_va = roc_auc_score(val_labels, probs_va)

        if auc_va > best_val_auc:
            best_val_auc = auc_va
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            best_probs = probs_va

    th_star, f1, rec, hn_fpr, shout_fpr = calibrate_threshold(val_labels, best_probs, val_cats)
    ap_va = average_precision_score(val_labels, best_probs)
    print(f"{candidate_id} Best Val AUC: {best_val_auc:.4f}, AP: {ap_va:.4f}, F1: {f1:.4f}, Recall: {rec*100:.1f}%, HN-FPR: {hn_fpr*100:.2f}%, Shout-FPR: {shout_fpr*100:.2f}% (theta*={th_star:.2f})")

    file_tag = candidate_id.lower().replace("-", "_")
    ckpt_p = MODELS_DIR / f"{file_tag}.pt"
    torch.save(best_state, ckpt_p)
    cfg = {
        "candidate_id": candidate_id,
        "architecture": model_class.__name__,
        "checkpoint": str(ckpt_p.name),
        "selected_threshold": th_star,
        "val_auc": round(best_val_auc, 4),
        "val_ap": round(ap_va, 4),
        "val_f1": round(f1, 4),
        "val_recall": round(rec * 100, 2),
        "val_hn_fpr": round(hn_fpr * 100, 2),
        "val_shouted_speech_fpr": round(shout_fpr * 100, 2)
    }
    with open(CONFIGS_DIR / f"{file_tag}.json", "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

    return cfg, best_val_auc

def main():
    print("=" * 80)
    print("STAGE 8.9.43: RETRAINING ALL 4 MODEL CANDIDATES ON DATASET MANIFEST V5")
    print("=" * 80)
    t0 = time.time()

    # Load YAMNet cache
    y_data = np.load(YAMNET_CACHE_P, allow_pickle=True)
    y_splits = y_data["splits"]
    train_mask_y = (y_splits == "v5_train")
    val_mask_y = (y_splits == "v5_validation")
    print(f"YAMNet cache: {len(y_splits)} clips (Train: {np.sum(train_mask_y)}, Val: {np.sum(val_mask_y)})")

    # Load LogMel cache
    lm_data = np.load(LOGMEL_CACHE_P, allow_pickle=True)
    lm_splits = lm_data["splits"]
    lm_fids = lm_data["file_ids"]
    train_fids_lm = lm_fids[lm_splits == "v5_train"]
    val_fids_lm = lm_fids[lm_splits == "v5_validation"]
    print(f"LogMel cache: {len(lm_splits)} clips (Train: {len(train_fids_lm)}, Val: {len(val_fids_lm)})")

    all_configs = []

    # 1. Candidate A: Config-B-v5
    cfg_a, auc_a = train_config_b(y_data, train_mask_y, val_mask_y, epochs=40)
    all_configs.append(cfg_a)

    # 2. Candidate B: CNN-LogMel-v5
    cfg_b, auc_b = train_cnn("CNN-LogMel-v5", CustomLogMelCNN, lm_data, train_fids_lm, val_fids_lm, epochs=30)
    all_configs.append(cfg_b)

    # 3. Candidate C: CNN-MultiScale-v5
    cfg_c, auc_c = train_cnn("CNN-MultiScale-v5", CustomMultiScaleCNN, lm_data, train_fids_lm, val_fids_lm, epochs=30)
    all_configs.append(cfg_c)

    # 4. Candidate D: CNN-Temporal-v5
    cfg_d, auc_d = train_cnn("CNN-Temporal-v5", CustomTemporalCNN, lm_data, train_fids_lm, val_fids_lm, epochs=30)
    all_configs.append(cfg_d)

    # Save summary
    sum_p = RESULTS_DIR / "candidate_training_summary.json"
    with open(sum_p, "w", encoding="utf-8") as f:
        json.dump(all_configs, f, indent=2)

    print(f"\nAll 4 candidates successfully trained in {time.time() - t0:.1f}s.")
    print(f"Summary written to: {sum_p}")

if __name__ == "__main__":
    main()

