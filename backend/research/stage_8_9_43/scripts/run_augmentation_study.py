"""
Stage 8.9.43: Phase 5 — Controlled Augmentation Study
Evaluates 4 training conditions on v5_train (N=1198) and evaluates on v5_validation (N=309):
Condition A: Authentic positives only (No augmentation)
Condition B: Gain perturbation (±4 dB) + Crowd noise mixing (SNR +6 dB to +12 dB)
Condition C: Mild reverberation (RIR simulation) + SpecAugment (Time & Frequency masking)
Condition D: Multi-condition augmentation (Gain + Noise + Reverb + SpecAugment)
Outputs:
- AUGMENTATION_EXPERIMENTS.csv
- augmentation/augmentation_summary.json
"""
import os
import sys
import time
import json
import csv
from pathlib import Path
import numpy as np
import pandas as pd
import soundfile as sf
import librosa
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score, confusion_matrix

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE43_DIR = BACKEND_DIR / "research" / "stage_8_9_43"

TARGET_SR = 16000
N_MELS = 64
N_FFT = 1024
HOP_LENGTH = 256
FMIN = 125.0
FMAX = 7500.0

def load_audio(path, target_sr=TARGET_SR):
    wf, sr = sf.read(str(path), dtype="float32")
    if wf.ndim > 1:
        wf = np.mean(wf, axis=1)
    if sr != target_sr:
        wf = librosa.resample(wf, orig_sr=sr, target_sr=target_sr)
    max_amp = np.max(np.abs(wf))
    if max_amp > 1e-6:
        wf = wf / max_amp
    return wf

def extract_logmel(wf, sr=TARGET_SR):
    if len(wf) < N_FFT:
        wf = np.pad(wf, (0, N_FFT - len(wf)), mode="constant")
    mel = librosa.feature.melspectrogram(
        y=wf, sr=sr, n_fft=N_FFT, hop_length=HOP_LENGTH,
        n_mels=N_MELS, fmin=FMIN, fmax=FMAX, power=2.0
    )
    logmel = librosa.power_to_db(mel, ref=np.max, top_db=80.0)
    logmel_norm = (logmel + 40.0) / 40.0
    return logmel_norm.astype(np.float32)

# Augmentation functions
def apply_gain(wf, gain_db):
    factor = 10.0 ** (gain_db / 20.0)
    return np.clip(wf * factor, -1.0, 1.0)

def apply_noise_mix(wf, noise_wf, snr_db):
    p_signal = np.mean(wf ** 2) + 1e-9
    # Tile or crop noise to match length
    if len(noise_wf) < len(wf):
        repeats = int(np.ceil(len(wf) / len(noise_wf)))
        noise_wf = np.tile(noise_wf, repeats)[:len(wf)]
    else:
        noise_wf = noise_wf[:len(wf)]
    p_noise = np.mean(noise_wf ** 2) + 1e-9
    desired_p_noise = p_signal / (10.0 ** (snr_db / 10.0))
    scaled_noise = noise_wf * np.sqrt(desired_p_noise / p_noise)
    mixed = wf + scaled_noise
    return mixed / (np.max(np.abs(mixed)) + 1e-9)

def apply_mild_reverb(wf, decay=0.3):
    # Exponential decay impulse response
    impulse_len = int(TARGET_SR * 0.15) # 150 ms
    t = np.linspace(0, 0.15, impulse_len)
    h = np.exp(-t * (1.0 / max(decay, 0.05))) * np.random.randn(impulse_len).astype(np.float32)
    h = h / (np.max(np.abs(h)) + 1e-9)
    reverbed = np.convolve(wf, h, mode="full")[:len(wf)]
    return reverbed / (np.max(np.abs(reverbed)) + 1e-9)

def apply_spec_augment(lmel, max_mask_t=8, max_mask_f=8):
    # lmel: (64, T)
    lmel_aug = lmel.copy()
    F_bins, T_bins = lmel.shape
    # Time mask
    if T_bins > max_mask_t:
        t0 = np.random.randint(0, T_bins - max_mask_t)
        t_len = np.random.randint(1, max_mask_t)
        lmel_aug[:, t0:t0 + t_len] = 0.0
    # Freq mask
    if F_bins > max_mask_f:
        f0 = np.random.randint(0, F_bins - max_mask_f)
        f_len = np.random.randint(1, max_mask_f)
        lmel_aug[f0:f0 + f_len, :] = 0.0
    return lmel_aug

# Compact CNN model
class FastCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Sequential(nn.Conv2d(1, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(), nn.MaxPool2d(2, 2))
        self.conv2 = nn.Sequential(nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(), nn.MaxPool2d(2, 2))
        self.conv3 = nn.Sequential(nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(), nn.MaxPool2d(2, 2))
        self.fc = nn.Sequential(nn.Linear(128 * 2, 64), nn.ReLU(), nn.Dropout(0.3), nn.Linear(64, 1))

    def forward(self, x):
        h = self.conv1(x)
        h = self.conv2(h)
        h = self.conv3(h)
        avg_p = F.adaptive_avg_pool2d(h, (1, 1)).flatten(1)
        max_p = F.adaptive_max_pool2d(h, (1, 1)).flatten(1)
        return self.fc(torch.cat([avg_p, max_p], dim=1)).squeeze(-1)

class AugDataset(Dataset):
    def __init__(self, items, condition="A", noise_pool=None, target_len=64, is_train=True):
        self.items = items
        self.condition = condition
        self.noise_pool = noise_pool or []
        self.target_len = target_len
        self.is_train = is_train

    def __len__(self):
        return len(self.items)

    def __getitem__(self, idx):
        item = self.items[idx]
        wf = item["wf"].copy()
        label = item["label"]

        if self.is_train and label == 1 and self.condition != "A":
            # Apply condition augmentations to positives during training
            if self.condition == "B":
                gain = np.random.uniform(-4.0, 4.0)
                wf = apply_gain(wf, gain)
                if self.noise_pool and np.random.rand() > 0.5:
                    noise = self.noise_pool[np.random.randint(0, len(self.noise_pool))]
                    snr = np.random.uniform(6.0, 12.0)
                    wf = apply_noise_mix(wf, noise, snr)
            elif self.condition == "C":
                if np.random.rand() > 0.5:
                    wf = apply_mild_reverb(wf, decay=0.25)
            elif self.condition == "D":
                gain = np.random.uniform(-4.0, 4.0)
                wf = apply_gain(wf, gain)
                if self.noise_pool and np.random.rand() > 0.5:
                    noise = self.noise_pool[np.random.randint(0, len(self.noise_pool))]
                    snr = np.random.uniform(6.0, 12.0)
                    wf = apply_noise_mix(wf, noise, snr)
                if np.random.rand() > 0.5:
                    wf = apply_mild_reverb(wf, decay=0.25)

        lmel = extract_logmel(wf)
        if self.is_train and label == 1 and self.condition in ["C", "D"] and np.random.rand() > 0.5:
            lmel = apply_spec_augment(lmel)

        T = lmel.shape[1]
        if self.is_train:
            if T > self.target_len:
                start = np.random.randint(0, T - self.target_len + 1)
                patch = lmel[:, start:start + self.target_len]
            else:
                pad_len = self.target_len - T
                patch = np.pad(lmel, ((0, 0), (0, pad_len)), mode="edge")
        else:
            if T < 16:
                patch = np.pad(lmel, ((0, 0), (0, 16 - T)), mode="edge")
            else:
                patch = lmel

        return torch.tensor(patch, dtype=torch.float32).unsqueeze(0), torch.tensor(label, dtype=torch.float32)

def collate_fn(batch):
    tensors = [x[0] for x in batch]
    labels = [x[1] for x in batch]
    return torch.stack(tensors, dim=0), torch.tensor(labels, dtype=torch.float32)

def main():
    print("=" * 80)
    print("STAGE 8.9.43: PHASE 5 — CONTROLLED AUGMENTATION STUDY")
    print("=" * 80)

    # Load dataset_manifest_v5.csv
    manifest_p = STAGE43_DIR / "manifests" / "dataset_manifest_v5.csv"
    df = pd.read_csv(manifest_p)

    train_df = df[df["v5_research_split"] == "v5_train"]
    val_df = df[df["v5_research_split"] == "v5_validation"]

    print(f"Loading waveforms: {len(train_df)} train, {len(val_df)} val...")
    train_items = []
    noise_pool = []
    for _, r in train_df.iterrows():
        p = REPO_ROOT / r["workspace_audio_path"]
        if p.exists():
            wf = load_audio(p)
            train_items.append({"wf": wf, "label": int(r["binary_label"]), "cat": r["target_category"]})
            if r["target_category"] in ["crowd_chant_cheering", "general_environmental"]:
                noise_pool.append(wf)

    val_items = []
    for _, r in val_df.iterrows():
        p = REPO_ROOT / r["workspace_audio_path"]
        if p.exists():
            wf = load_audio(p)
            val_items.append({"wf": wf, "label": int(r["binary_label"]), "cat": r["target_category"]})

    print(f"Loaded {len(train_items)} train items (Noise pool: {len(noise_pool)} files), {len(val_items)} val items.")

    conditions = [
        ("Condition A", "Authentic Positives Only (Baseline)", "A"),
        ("Condition B", "Gain (±4 dB) + Crowd Noise Mixing (SNR +6 to +12 dB)", "B"),
        ("Condition C", "Mild Reverberation (150ms) + SpecAugment (Time/Freq Masking)", "C"),
        ("Condition D", "Multi-Condition (Gain + Noise + Reverb + SpecAugment)", "D")
    ]

    results = []

    for cond_id, cond_desc, cond_code in conditions:
        print(f"\n--- Training {cond_id}: {cond_desc} ---")
        torch.manual_seed(42)
        np.random.seed(42)

        train_ds = AugDataset(train_items, condition=cond_code, noise_pool=noise_pool)
        train_loader = DataLoader(train_ds, batch_size=32, shuffle=True, collate_fn=collate_fn)

        model = FastCNN()
        n_pos = sum(it["label"] == 1 for it in train_items)
        n_neg = sum(it["label"] == 0 for it in train_items)
        pos_weight = torch.tensor([n_neg / max(n_pos, 1)], dtype=torch.float32)

        criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)

        for ep in range(1, 16):
            model.train()
            for x, y in train_loader:
                optimizer.zero_grad()
                logits = model(x)
                loss = criterion(logits, y)
                loss.backward()
                optimizer.step()

        # Validation evaluation
        model.eval()
        val_logits, val_targets, val_cats = [], [], []
        with torch.no_grad():
            for it in val_items:
                lmel = extract_logmel(it["wf"])
                if lmel.shape[1] < 16:
                    lmel = np.pad(lmel, ((0, 0), (0, 16 - lmel.shape[1])), mode="edge")
                t_in = torch.tensor(lmel, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
                logit = model(t_in).item()
                val_logits.append(logit)
                val_targets.append(it["label"])
                val_cats.append(it["cat"])

        val_logits = np.array(val_logits)
        val_targets = np.array(val_targets)
        val_probs = 1.0 / (1.0 + np.exp(-val_logits))

        val_auc = float(roc_auc_score(val_targets, val_probs))
        val_ap = float(average_precision_score(val_targets, val_probs))

        # Sweep threshold for best F1 at FPR <= 5%
        best_f1, best_thresh, best_rec, best_fpr = 0.0, 0.5, 0.0, 0.0
        for th in np.linspace(0.1, 0.9, 81):
            preds = (val_probs >= th).astype(int)
            tn, fp, fn, tp = confusion_matrix(val_targets, preds, labels=[0, 1]).ravel()
            fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
            rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0.0
            if fpr <= 0.05 and f1 > best_f1:
                best_f1 = f1
                best_thresh = th
                best_rec = rec
                best_fpr = fpr

        # Shouted speech FPR at selected threshold
        is_shout = np.array([c == "shouting_and_speech" for c in val_cats])
        shout_fp = np.sum((val_probs >= best_thresh)[is_shout]) if np.sum(is_shout) > 0 else 0
        shout_fpr = shout_fp / np.sum(is_shout) if np.sum(is_shout) > 0 else 0.0

        rec_entry = {
            "experiment_id": cond_id,
            "description": cond_desc,
            "condition_code": cond_code,
            "val_auc": round(val_auc, 4),
            "val_ap": round(val_ap, 4),
            "selected_threshold": round(best_thresh, 4),
            "val_f1": round(best_f1, 4),
            "val_scream_recall": round(best_rec * 100, 2),
            "val_hn_fpr": round(best_fpr * 100, 2),
            "val_shouted_speech_fpr": round(shout_fpr * 100, 2),
            "seed": 42
        }
        results.append(rec_entry)
        print(f"  Result: AUC={val_auc:.4f}, AP={val_ap:.4f}, F1={best_f1:.4f}, Recall={best_rec*100:.1f}%, HN-FPR={best_fpr*100:.2f}%, Shout-FPR={shout_fpr*100:.2f}% (theta={best_thresh:.2f})")

    # Save to AUGMENTATION_EXPERIMENTS.csv
    out_csv = STAGE43_DIR / "AUGMENTATION_EXPERIMENTS.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    print(f"\nSaved augmentation study CSV: {out_csv}")

if __name__ == "__main__":
    main()
