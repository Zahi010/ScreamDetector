"""
Stage 8.9.42: Train Custom Log-Mel CNN Models (Without Pretrained Weights or YAMNet)
Models:
1. CustomLogMelCNN (CNN-LogMel): Standard 4-stage 2D CNN with global temporal-frequency pooling.
2. CustomMultiScaleCNN (CNN-MultiScale): Multi-scale temporal kernel CNN with sliding-window support.
Trained strictly on v4_train (N=820), validated on v4_val (N=339).
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
STAGE42_DIR = BACKEND_DIR / "research" / "stage_8_9_42"
CACHE_PATH = STAGE42_DIR / "results" / "logmel_spectrograms_cache.npz"

MODELS_DIR = STAGE42_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
CONFIGS_DIR = STAGE42_DIR / "configs"
CONFIGS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR = STAGE42_DIR / "results" / "training"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------
# 1. Dataset & Collate Fn
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
        lmel = self.cache_data[f"logmel_{fid}"] # shape: (64, T)
        # Find label
        all_fids = self.cache_data["file_ids"]
        f_idx = np.where(all_fids == fid)[0][0]
        label = int(self.cache_data["labels"][f_idx])

        # Random crop or pad for training batching
        T = lmel.shape[1]
        if self.is_train:
            if T > self.target_len:
                start = np.random.randint(0, T - self.target_len + 1)
                patch = lmel[:, start:start + self.target_len]
            else:
                pad_len = self.target_len - T
                pad_left = pad_len // 2
                pad_right = pad_len - pad_left
                patch = np.pad(lmel, ((0, 0), (pad_left, pad_right)), mode="edge")
        else:
            # During eval, if smaller than 16 frames pad to 16, else pass full length
            if T < 16:
                patch = np.pad(lmel, ((0, 0), (0, 16 - T)), mode="edge")
            else:
                patch = lmel

        return torch.tensor(patch, dtype=torch.float32).unsqueeze(0), torch.tensor(label, dtype=torch.float32), fid

def pad_collate_fn(batch):
    # Sort by length descending
    batch.sort(key=lambda x: x[0].shape[2], reverse=True)
    max_len = max(x[0].shape[2] for x in batch)
    tensors = []
    labels = []
    fids = []
    for x, y, fid in batch:
        T = x.shape[2]
        if T < max_len:
            pad = max_len - T
            x = F.pad(x, (0, pad), mode="replicate")
        tensors.append(x)
        labels.append(y)
        fids.append(fid)
    return torch.stack(tensors, dim=0), torch.tensor(labels, dtype=torch.float32), fids

# -------------------------------------------------------------
# 2. Architectures
# -------------------------------------------------------------
class CustomLogMelCNN(nn.Module):
    """Candidate 1: Compact 4-stage 2D CNN with adaptive pooling."""
    def __init__(self, in_channels=1, num_classes=1):
        super().__init__()
        self.conv1 = nn.Sequential(
            nn.Conv2d(in_channels, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2, 2)
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2, 2)
        )
        self.conv3 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2, 2)
        )
        self.conv4 = nn.Sequential(
            nn.Conv2d(128, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU()
        )
        self.fc = nn.Sequential(
            nn.Linear(128 * 2, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, num_classes)
        )

    def forward(self, x):
        h = self.conv1(x)
        h = self.conv2(h)
        h = self.conv3(h)
        h = self.conv4(h)
        avg_p = F.adaptive_avg_pool2d(h, (1, 1)).flatten(1)
        max_p = F.adaptive_max_pool2d(h, (1, 1)).flatten(1)
        feat = torch.cat([avg_p, max_p], dim=1)
        logits = self.fc(feat).squeeze(-1)
        return logits

class MultiScaleTemporalBlock(nn.Module):
    """Captures 3 different temporal resolutions: transient (~50ms), medium (~110ms), sustained (~240ms)."""
    def __init__(self, in_c, out_c):
        super().__init__()
        branch_c = out_c // 3
        rem_c = out_c - branch_c * 2
        self.b1 = nn.Sequential(
            nn.Conv2d(in_c, branch_c, kernel_size=(3, 3), padding=(1, 1)),
            nn.BatchNorm2d(branch_c),
            nn.ReLU()
        )
        self.b2 = nn.Sequential(
            nn.Conv2d(in_c, branch_c, kernel_size=(3, 7), padding=(1, 3)),
            nn.BatchNorm2d(branch_c),
            nn.ReLU()
        )
        self.b3 = nn.Sequential(
            nn.Conv2d(in_c, rem_c, kernel_size=(3, 15), padding=(1, 7)),
            nn.BatchNorm2d(rem_c),
            nn.ReLU()
        )

    def forward(self, x):
        return torch.cat([self.b1(x), self.b2(x), self.b3(x)], dim=1)

class CustomMultiScaleCNN(nn.Module):
    """Candidate 2: Multi-Scale Temporal CNN with fine burst detection."""
    def __init__(self, in_channels=1, num_classes=1):
        super().__init__()
        self.stem = nn.Sequential(
            nn.Conv2d(in_channels, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2, 2)
        )
        self.ms1 = MultiScaleTemporalBlock(32, 64)
        self.pool1 = nn.MaxPool2d(2, 2)

        self.ms2 = MultiScaleTemporalBlock(64, 128)
        self.pool2 = nn.MaxPool2d(2, 2)

        self.conv_final = nn.Sequential(
            nn.Conv2d(128, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU()
        )
        self.fc = nn.Sequential(
            nn.Linear(128 * 2, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, num_classes)
        )

    def forward(self, x):
        h = self.stem(x)
        h = self.pool1(self.ms1(h))
        h = self.pool2(self.ms2(h))
        h = self.conv_final(h)
        avg_p = F.adaptive_avg_pool2d(h, (1, 1)).flatten(1)
        max_p = F.adaptive_max_pool2d(h, (1, 1)).flatten(1)
        feat = torch.cat([avg_p, max_p], dim=1)
        logits = self.fc(feat).squeeze(-1)
        return logits

# -------------------------------------------------------------
# 3. Training Function
# -------------------------------------------------------------
def train_model(model_name, model_class, cache_data, train_ids, val_ids, epochs=30, batch_size=32, lr=1e-3):
    print(f"\n==================================================")
    print(f"Training: {model_name}")
    print(f"==================================================")
    torch.manual_seed(42)
    np.random.seed(42)

    train_ds = LogMelDataset(cache_data, train_ids, is_train=True, target_len=64)
    val_ds = LogMelDataset(cache_data, val_ids, is_train=False)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, collate_fn=pad_collate_fn)
    val_loader = DataLoader(val_ds, batch_size=1, shuffle=False)

    model = model_class()
    # Compute positive weight for balanced BCE
    all_fids = cache_data["file_ids"]
    train_indices = [np.where(all_fids == fid)[0][0] for fid in train_ids]
    train_labels = cache_data["labels"][train_indices]
    n_pos = np.sum(train_labels == 1)
    n_neg = np.sum(train_labels == 0)
    pos_weight = torch.tensor([n_neg / max(n_pos, 1)], dtype=torch.float32)
    print(f"Train samples: {len(train_ids)} (Pos: {n_pos}, Neg: {n_neg}, pos_weight: {pos_weight.item():.2f})")

    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)

    best_val_auc = 0.0
    best_epoch = 0
    best_state = None
    best_val_preds = None

    history = []

    for ep in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        for x, y, _ in train_loader:
            optimizer.zero_grad()
            logits = model(x)
            loss = criterion(logits, y)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * len(y)
        train_loss /= len(train_ids)
        scheduler.step()

        # Validation
        model.eval()
        val_logits = []
        val_targets = []
        with torch.no_grad():
            for x, y, fid in val_loader:
                logit = model(x)
                val_logits.append(logit.item())
                val_targets.append(y.item())

        val_logits = np.array(val_logits)
        val_targets = np.array(val_targets)
        val_probs = 1.0 / (1.0 + np.exp(-val_logits))

        val_auc = roc_auc_score(val_targets, val_probs)
        val_ap = average_precision_score(val_targets, val_probs)

        history.append({
            "epoch": ep, "train_loss": train_loss, "val_auc": val_auc, "val_ap": val_ap
        })

        if val_auc > best_val_auc:
            best_val_auc = val_auc
            best_epoch = ep
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            best_val_preds = (val_targets, val_probs)

        if ep % 5 == 0 or ep == epochs:
            print(f"Epoch {ep:2d}/{epochs} | Train Loss: {train_loss:.4f} | Val AUC: {val_auc:.4f} | Val AP: {val_ap:.4f} | Best AUC: {best_val_auc:.4f} (ep {best_epoch})")

    print(f"\nTraining Complete for {model_name}. Best Epoch: {best_epoch} with Val AUC: {best_val_auc:.4f}")

    # Threshold Selection on Validation Set
    val_targets, val_probs = best_val_preds
    thresholds = np.linspace(0.05, 0.95, 91)
    best_thresh = 0.5
    best_f1 = 0.0
    selected_metrics = {}

    for t in thresholds:
        bin_p = (val_probs >= t).astype(int)
        tn, fp, fn, tp = confusion_matrix(val_targets, bin_p, labels=[0, 1]).ravel()
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0

        # We constrain FPR <= 0.12 (on val hard negatives) while maximizing F1
        if fpr <= 0.12 and f1 > best_f1:
            best_f1 = f1
            best_thresh = float(t)
            selected_metrics = {
                "threshold": best_thresh, "f1": f1, "recall": rec, "precision": prec,
                "fpr": fpr, "tp": int(tp), "fp": int(fp), "tn": int(tn), "fn": int(fn)
            }

    if not selected_metrics:
        best_thresh = 0.50
        bin_p = (val_probs >= 0.5).astype(int)
        tn, fp, fn, tp = confusion_matrix(val_targets, bin_p, labels=[0, 1]).ravel()
        selected_metrics = {
            "threshold": 0.5, "f1": f1_score(val_targets, bin_p),
            "recall": recall_score(val_targets, bin_p), "precision": precision_score(val_targets, bin_p),
            "fpr": float(fp / (fp + tn)), "tp": int(tp), "fp": int(fp), "tn": int(tn), "fn": int(fn)
        }

    print(f"Selected Validation Threshold: {best_thresh:.4f} (Val F1: {selected_metrics['f1']:.4f}, Recall: {selected_metrics['recall']:.4f}, FPR: {selected_metrics['fpr']:.4f})")

    # Save Checkpoint
    ckpt_path = MODELS_DIR / f"{model_name.lower().replace('-', '_')}_best.pt"
    torch.save({
        "model_name": model_name,
        "model_class": model_class.__name__,
        "model_state_dict": best_state,
        "best_epoch": best_epoch,
        "best_val_auc": best_val_auc,
        "selected_threshold": best_thresh,
        "val_metrics": selected_metrics,
        "architecture_params": {
            "n_mels": 64, "hop_length": 256, "n_fft": 1024, "target_sr": 16000
        }
    }, ckpt_path)
    print(f"Saved checkpoint: {ckpt_path}")

    # Save Config
    cfg_path = CONFIGS_DIR / f"{model_name.lower().replace('-', '_')}_config.json"
    with open(cfg_path, "w", encoding="utf-8") as f:
        json.dump({
            "model_name": model_name,
            "checkpoint_path": str(ckpt_path),
            "decision_threshold": best_thresh,
            "validation_auc": best_val_auc,
            "validation_metrics": selected_metrics,
            "training_history": history
        }, f, indent=2)
    print(f"Saved config: {cfg_path}")

    return ckpt_path, best_thresh

def main():
    print("=" * 80)
    print("STAGE 8.9.42: CUSTOM CNN TRAINING ON LOG-MEL SPECTROGRAMS")
    print("=" * 80)

    print(f"Loading cached spectrogram dataset: {CACHE_PATH}")
    cache_data = np.load(CACHE_PATH, allow_pickle=True)

    splits = cache_data["splits"]
    file_ids = cache_data["file_ids"]

    train_ids = file_ids[splits == "v4_train"]
    val_ids = file_ids[splits == "v4_val"]

    print(f"Total dataset: {len(file_ids)} clips.")
    print(f"Train clips: {len(train_ids)}, Val clips: {len(val_ids)}")

    # 1. Train Candidate 1: CNN-LogMel
    train_model(
        model_name="CNN-LogMel",
        model_class=CustomLogMelCNN,
        cache_data=cache_data,
        train_ids=train_ids,
        val_ids=val_ids,
        epochs=30,
        batch_size=32,
        lr=1e-3
    )

    # 2. Train Candidate 2: CNN-MultiScale
    train_model(
        model_name="CNN-MultiScale",
        model_class=CustomMultiScaleCNN,
        cache_data=cache_data,
        train_ids=train_ids,
        val_ids=val_ids,
        epochs=30,
        batch_size=32,
        lr=1e-3
    )

    print("\nCustom CNN training complete for both candidates.")

if __name__ == "__main__":
    main()

