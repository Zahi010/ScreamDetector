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
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, average_precision_score, confusion_matrix

BACKEND_DIR = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector\backend")
STAGE_DIR = BACKEND_DIR / "research" / "stage_8_9_39"
CACHE_PATH = STAGE_DIR / "cache" / "stage_8_9_39_features.npz"
CKPT_DIR = STAGE_DIR / "checkpoints" / "config_d"
CKPT_DIR.mkdir(parents=True, exist_ok=True)
PRED_DIR = STAGE_DIR / "predictions" / "validation"
PRED_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR = STAGE_DIR / "results" / "training"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------
# 1. Model Definition: Candidate D (MultiPathwayFusionModel)
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

class FrequencySubbandHead(nn.Module):
    def __init__(self, in_dim=11, hidden_dim=32, proj_dim=16):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.10),
            nn.Linear(hidden_dim, proj_dim)
        )
    def forward(self, x_subband):
        x_safe = torch.nan_to_num(x_subband, nan=0.0)
        return F.normalize(self.net(x_safe), p=2, dim=-1)

class MultiPathwayFusionModel(nn.Module):
    """
    Configuration D: Multi-Pathway Frequency-Subband Dual-Encoder (MP-FS-DualEncoder).
    Fuses Path A (1024-d YAMNet) + Path B (12-d Phonation) + Path C (11-d Frequency Subbands).
    """
    def __init__(self, sem_dim=1024, acoust_dim=6, subband_dim=11):
        super().__init__()
        self.sem_head = SemanticProjectionHead(sem_dim, 256, 128)
        self.acoust_head = PhonationMaskedHead(acoust_dim, 64, 32)
        self.subband_head = FrequencySubbandHead(subband_dim, 32, 16)
        
        # Multimodal Fusion: 128 + 32 + 16 = 176 dimensions
        self.fusion = nn.Sequential(
            nn.Linear(128 + 32 + 16, 64),
            nn.ReLU(),
            nn.Dropout(0.10),
            nn.Linear(64, 1)
        )
        
    def forward(self, x_sem, x_acoust, mask_acoust, x_subband):
        z_sem = self.sem_head(x_sem)
        z_acoust = self.acoust_head(x_acoust, mask_acoust)
        z_subband = self.subband_head(x_subband)
        
        fused = torch.cat([z_sem, z_acoust, z_subband], dim=-1)
        logits = self.fusion(fused).squeeze(-1)
        return logits, z_sem, z_subband

# -------------------------------------------------------------
# 2. Supervised Contrastive Loss
# -------------------------------------------------------------
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
        has_pos = (mask.sum(1) > 0)
        if not has_pos.any():
            return torch.tensor(0.0, device=features.device, requires_grad=True)
            
        log_prob = logits - torch.log(denom + 1e-9)
        mean_log_prob_pos = (mask * log_prob).sum(1) / (mask.sum(1) + 1e-9)
        loss = -mean_log_prob_pos[has_pos].mean()
        return loss

def evaluate_predictions(y_true, y_prob, threshold=0.35):
    y_pred = (y_prob >= threshold).astype(int)
    rec = recall_score(y_true, y_pred, zero_division=0)
    prec = precision_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    try:
        roc_auc = roc_auc_score(y_true, y_prob)
    except Exception:
        roc_auc = 0.5
    try:
        pr_auc = average_precision_score(y_true, y_prob)
    except Exception:
        pr_auc = 0.0
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    fpr = fp / (fp + tn + 1e-9)
    return {
        'recall': float(rec),
        'precision': float(prec),
        'f1': float(f1),
        'fpr': float(fpr),
        'roc_auc': float(roc_auc),
        'pr_auc': float(pr_auc),
        'tp': int(tp), 'fp': int(fp), 'fn': int(fn), 'tn': int(tn)
    }

def main():
    print("=" * 80)
    print("STAGE 8.9.39: CONTROLLED RETRAINING — CANDIDATE D (MultiPathwayFusionModel)")
    print("=" * 80)

    # Determinism
    SEED = 42
    torch.manual_seed(SEED)
    np.random.seed(SEED)

    # 1. Load Data
    data = np.load(CACHE_PATH, allow_pickle=True)
    splits = data['splits']
    train_idx = np.where(splits == 'v4_train')[0]
    val_idx = np.where(splits == 'v4_val')[0]

    print(f"Loaded feature cache from: {CACHE_PATH}")
    print(f"  v4_train samples: {len(train_idx)} (Screams: {np.sum(data['labels'][train_idx] == 1)})")
    print(f"  v4_val samples:   {len(val_idx)} (Screams: {np.sum(data['labels'][val_idx] == 1)})")

    # Tensors
    t_sem_train = torch.tensor(data['X_sem'][train_idx], dtype=torch.float32)
    t_acoust_train = torch.tensor(data['X_acoust'][train_idx], dtype=torch.float32)
    t_mask_train = torch.tensor(data['mask_acoust'][train_idx], dtype=torch.float32)
    t_sb_train = torch.tensor(data['X_subband'][train_idx], dtype=torch.float32)
    t_y_train = torch.tensor(data['labels'][train_idx], dtype=torch.float32)

    t_sem_val = torch.tensor(data['X_sem'][val_idx], dtype=torch.float32)
    t_acoust_val = torch.tensor(data['X_acoust'][val_idx], dtype=torch.float32)
    t_mask_val = torch.tensor(data['mask_acoust'][val_idx], dtype=torch.float32)
    t_sb_val = torch.tensor(data['X_subband'][val_idx], dtype=torch.float32)
    t_y_val = torch.tensor(data['labels'][val_idx], dtype=torch.float32)
    y_val_np = data['labels'][val_idx]

    train_dataset = TensorDataset(t_sem_train, t_acoust_train, t_mask_train, t_sb_train, t_y_train)
    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True, drop_last=False)

    # 2. Instantiate Model
    model = MultiPathwayFusionModel(sem_dim=1024, acoust_dim=6, subband_dim=11)
    param_count = sum(p.numel() for p in model.parameters() if p.requires_grad)
    model_size_kb = sum(p.numel() * 4 for p in model.parameters()) / 1024
    print(f"Candidate D Parameters: {param_count:,} ({model_size_kb:.2f} KB)")

    # Optimizer, Loss, Scheduler
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.0001)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=35)
    bce_criterion = nn.BCEWithLogitsLoss()
    supcon_criterion = SupConLoss(temperature=0.05)

    # Training state
    MAX_EPOCHS = 35
    PATIENCE = 8
    best_val_f1 = -1.0
    best_epoch = 0
    patience_counter = 0
    best_model_state = None
    best_val_probs = None
    best_val_logits = None

    history = []
    start_time = time.time()

    print("\nStarting Training (Max Epochs: 35, Patience: 8 on val_f1)...")
    for epoch in range(1, MAX_EPOCHS + 1):
        model.train()
        train_bce_sum = 0.0
        train_con_sum = 0.0
        train_total_sum = 0.0
        batches = 0

        for b_sem, b_acoust, b_mask, b_sb, b_y in train_loader:
            optimizer.zero_grad()
            logits, z_sem, z_sb = model(b_sem, b_acoust, b_mask, b_sb)
            
            loss_bce = bce_criterion(logits, b_y)
            loss_con = supcon_criterion(z_sem, b_y.long())
            loss = loss_bce + 0.5 * loss_con
            
            loss.backward()
            optimizer.step()

            train_bce_sum += loss_bce.item()
            train_con_sum += loss_con.item()
            train_total_sum += loss.item()
            batches += 1

        scheduler.step()
        train_bce_avg = train_bce_sum / batches
        train_con_avg = train_con_sum / batches
        train_total_avg = train_total_sum / batches

        # Validation Evaluation
        model.eval()
        with torch.no_grad():
            v_logits, _, _ = model(t_sem_val, t_acoust_val, t_mask_val, t_sb_val)
            v_bce = bce_criterion(v_logits, t_y_val).item()
            v_probs = torch.sigmoid(v_logits).numpy()
            v_metrics = evaluate_predictions(y_val_np, v_probs, threshold=0.35)

        val_f1 = v_metrics['f1']
        val_rec = v_metrics['recall']
        val_prec = v_metrics['precision']
        val_pr_auc = v_metrics['pr_auc']
        val_roc_auc = v_metrics['roc_auc']

        epoch_record = {
            'epoch': epoch,
            'train_total_loss': round(train_total_avg, 4),
            'train_bce_loss': round(train_bce_avg, 4),
            'train_supcon_loss': round(train_con_avg, 4),
            'val_loss': round(v_bce, 4),
            'val_f1': round(val_f1, 4),
            'val_recall': round(val_rec, 4),
            'val_precision': round(val_prec, 4),
            'val_pr_auc': round(val_pr_auc, 4),
            'val_roc_auc': round(val_roc_auc, 4),
            'lr': round(scheduler.get_last_lr()[0], 6)
        }
        history.append(epoch_record)

        is_best = (val_f1 > best_val_f1)
        if is_best:
            best_val_f1 = val_f1
            best_epoch = epoch
            best_model_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            best_val_probs = v_probs.copy()
            best_val_logits = v_logits.numpy().copy()
            patience_counter = 0
            star = " [*BEST]"
        else:
            patience_counter += 1
            star = ""

        if epoch % 5 == 0 or is_best or epoch == MAX_EPOCHS:
            print(f"Epoch {epoch:2d}/{MAX_EPOCHS}: TrainLoss={train_total_avg:.4f} | ValLoss={v_bce:.4f} | ValF1={val_f1:.4f} (Rec={val_rec:.4f}, Prec={val_prec:.4f}, PR-AUC={val_pr_auc:.4f}){star}")

        if patience_counter >= PATIENCE:
            print(f"\n[EARLY STOP] No validation F1 improvement for {PATIENCE} epochs. Stopping at epoch {epoch}.")
            break

    total_training_time = time.time() - start_time
    print(f"\nTraining Complete in {total_training_time:.2f}s.")
    print(f"Best Validation Epoch: {best_epoch} with Val F1: {best_val_f1:.4f}")

    # Save Best Checkpoint
    best_ckpt_path = CKPT_DIR / "best_model.pt"
    torch.save({
        'epoch': best_epoch,
        'model_state_dict': best_model_state,
        'best_val_f1': best_val_f1,
        'hyperparameters': {
            'lr': 0.001,
            'weight_decay': 0.0001,
            'batch_size': 64,
            'seed': SEED,
            'max_epochs': MAX_EPOCHS
        },
        'architecture': 'MultiPathwayFusionModel',
        'param_count': param_count
    }, best_ckpt_path)
    print(f"Saved best checkpoint to: {best_ckpt_path}")

    # Save History CSV
    history_csv = RESULTS_DIR / "config_d_training_history.csv"
    with open(history_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(history[0].keys()))
        w.writeheader()
        w.writerows(history)
    print(f"Saved training history to: {history_csv}")

    # Save Validation Predictions at Best Checkpoint
    val_pred_csv = PRED_DIR / "config_d_val_predictions.csv"
    val_fids = data['file_ids'][val_idx]
    val_cats = data['categories'][val_idx]
    val_sgs = data['source_groups'][val_idx]

    val_pred_rows = []
    for i in range(len(val_idx)):
        val_pred_rows.append({
            'file_id': val_fids[i],
            'category': val_cats[i],
            'source_group_id': val_sgs[i],
            'ground_truth': int(y_val_np[i]),
            'logit': float(best_val_logits[i]),
            'probability': float(best_val_probs[i])
        })
    with open(val_pred_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=['file_id', 'category', 'source_group_id', 'ground_truth', 'logit', 'probability'])
        w.writeheader()
        w.writerows(val_pred_rows)
    print(f"Saved validation predictions to: {val_pred_csv}")

    # Save Training Summary JSON
    summary = {
        'candidate': 'Configuration D (MultiPathwayFusionModel)',
        'best_epoch': best_epoch,
        'best_val_f1': float(best_val_f1),
        'total_epochs_trained': len(history),
        'total_training_time_seconds': float(round(total_training_time, 2)),
        'parameter_count': param_count,
        'checkpoint_path': str(best_ckpt_path),
        'val_predictions_path': str(val_pred_csv),
        'history_csv_path': str(history_csv)
    }
    summary_path = RESULTS_DIR / "config_d_training_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Saved training summary to: {summary_path}")

if __name__ == "__main__":
    main()
