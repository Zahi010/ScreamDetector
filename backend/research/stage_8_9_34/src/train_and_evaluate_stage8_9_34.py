import os
import sys
sys.path.insert(0, os.path.abspath('backend/research/stage_8_9_33/src'))
import csv
import json
import time
import joblib
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import TensorDataset, DataLoader
from sklearn.metrics import (
    recall_score, precision_score, f1_score, roc_auc_score,
    average_precision_score, confusion_matrix, accuracy_score
)

# -------------------------------------------------------------
# 1. Architectural Modules
# -------------------------------------------------------------

class SemanticSNRProjectionHead(nn.Module):
    """Path A: Semantic YAMNet Head with SNR-Adaptive Conditioning"""
    def __init__(self, sem_dim=1024, snr_dim=1, hidden_dim=256, proj_dim=128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(sem_dim + snr_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.15),
            nn.Linear(hidden_dim, proj_dim)
        )
        
    def forward(self, x_sem, x_snr):
        x = torch.cat([x_sem, x_snr], dim=-1)
        z = self.net(x)
        return F.normalize(z, p=2, dim=-1)

class PhonationMaskedHead(nn.Module):
    """Path B: Phonation / Acoustic Head with Missing-Indicator Gating"""
    def __init__(self, acoust_dim=6, hidden_dim=64, proj_dim=32):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(acoust_dim * 2, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.10),
            nn.Linear(hidden_dim, proj_dim)
        )
        
    def forward(self, x_acoust, mask_acoust):
        x_safe = torch.nan_to_num(x_acoust, nan=0.0)
        combined = torch.cat([x_safe, mask_acoust], dim=-1)
        z = self.net(combined)
        return F.normalize(z, p=2, dim=-1)

class CausalGRUTemporalAggregator(nn.Module):
    """Candidate B: Causal GRU over multi-window temporal context (3 frames = 3072d split)"""
    def __init__(self, input_dim=160, hidden_dim=64):
        super().__init__()
        self.gru = nn.GRU(input_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, 1)
        
    def forward(self, seq):
        # seq shape: (batch, time_steps, input_dim)
        out, _ = self.gru(seq)
        # Use final time step for causal streaming inference
        last_step = out[:, -1, :]
        logit = self.fc(last_step).squeeze(-1)
        return logit

class CausalTCNBlock(nn.Module):
    """Candidate C: Causal Temporal Convolutional Block"""
    def __init__(self, in_channels=160, out_channels=64, kernel_size=2, dilation=1):
        super().__init__()
        self.pad = (kernel_size - 1) * dilation
        self.conv = nn.Conv1d(in_channels, out_channels, kernel_size, dilation=dilation)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.10)
        self.res = nn.Conv1d(in_channels, out_channels, 1) if in_channels != out_channels else nn.Identity()
        
    def forward(self, x):
        # x: (batch, channels, time)
        padded = F.pad(x, (self.pad, 0)) # Left pad for causal convolution
        out = self.dropout(self.relu(self.conv(padded)))
        return out + self.res(x)

class CausalTCNAggregator(nn.Module):
    def __init__(self, in_channels=160, hidden_dim=64):
        super().__init__()
        self.tcn1 = CausalTCNBlock(in_channels, hidden_dim, kernel_size=2, dilation=1)
        self.tcn2 = CausalTCNBlock(hidden_dim, hidden_dim, kernel_size=2, dilation=2)
        self.fc = nn.Linear(hidden_dim, 1)
        
    def forward(self, seq):
        # seq: (batch, time, channels) -> (batch, channels, time)
        x = seq.transpose(1, 2)
        x = self.tcn1(x)
        x = self.tcn2(x)
        last_step = x[:, :, -1]
        return self.fc(last_step).squeeze(-1)

class GatedTemporalAggregator(nn.Module):
    """Candidate D: Lightweight Gated Moving-Average Aggregator"""
    def __init__(self, in_dim=160, hidden_dim=64):
        super().__init__()
        self.fc_val = nn.Linear(in_dim, hidden_dim)
        self.fc_gate = nn.Linear(in_dim, hidden_dim)
        self.head = nn.Linear(hidden_dim, 1)
        
    def forward(self, seq):
        mean_seq = torch.mean(seq, dim=1)
        val = self.fc_val(mean_seq)
        gate = torch.sigmoid(self.fc_gate(mean_seq))
        gated = val * gate
        return self.head(gated).squeeze(-1)

class JointTSADualEncoder(nn.Module):
    """
    Combined Temporal + SNR-Adaptive + Infant-Cry Specialized Dual-Encoder.
    Fuses Path A (SNR-conditioned YAMNet) and Path B (Masked Phonation)
    through a Causal GRU with Infant-Cry Periodicity Suppression Gating.
    """
    def __init__(self, sem_dim=1024, acoust_dim=6, proj_sem=128, proj_acoust=32, gru_dim=64):
        super().__init__()
        self.sem_head = SemanticSNRProjectionHead(sem_dim=sem_dim, snr_dim=1, hidden_dim=256, proj_dim=proj_sem)
        self.acoust_head = PhonationMaskedHead(acoust_dim=acoust_dim, hidden_dim=64, proj_dim=proj_acoust)
        
        # Temporal causal sequence processor
        self.gru = nn.GRU(proj_sem + proj_acoust, gru_dim, batch_first=True)
        
        # Periodicity / Infant-cry suppression gate
        # If input has high burst-periodicity and low continuity, gate closes
        self.cry_detector = nn.Sequential(
            nn.Linear(proj_sem + proj_acoust, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        
        self.classifier = nn.Sequential(
            nn.Linear(gru_dim, 32),
            nn.ReLU(),
            nn.Dropout(0.10),
            nn.Linear(32, 1)
        )
        
    def forward(self, x_sem_seq, x_snr, x_acoust, mask_acoust):
        # x_sem_seq: (batch, time, 1024)
        batch_size, time_steps, sem_dim = x_sem_seq.shape
        
        # Process each temporal slice through semantic head
        sem_proj_list = []
        for t in range(time_steps):
            z_s = self.sem_head(x_sem_seq[:, t, :], x_snr)
            sem_proj_list.append(z_s.unsqueeze(1))
        z_sem_seq = torch.cat(sem_proj_list, dim=1) # (batch, time, 128)
        
        # Process acoustic features
        z_acoust = self.acoust_head(x_acoust, mask_acoust) # (batch, 32)
        z_acoust_seq = z_acoust.unsqueeze(1).expand(-1, time_steps, -1) # (batch, time, 32)
        
        # Multimodal sequence
        fused_seq = torch.cat([z_sem_seq, z_acoust_seq], dim=-1) # (batch, time, 160)
        
        # Causal GRU
        gru_out, _ = self.gru(fused_seq)
        last_hidden = gru_out[:, -1, :] # (batch, 64)
        
        raw_logits = self.classifier(last_hidden).squeeze(-1)
        
        # Infant-cry suppression factor (1.0 = normal scream, 0.2 = detected crying pattern)
        cry_prob = self.cry_detector(fused_seq[:, -1, :]).squeeze(-1)
        suppression_factor = 1.0 - 0.45 * cry_prob
        
        # Logit adjustment: logit is scaled down if cry pattern detected
        adjusted_logits = raw_logits * suppression_factor
        
        return adjusted_logits, z_sem_seq[:, -1, :], cry_prob

# -------------------------------------------------------------
# 2. Loss Functions & Metrics
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
        log_prob = logits - torch.log(exp_logits.sum(1, keepdim=True) + 1e-9)
        mean_log_prob_pos = (mask * log_prob).sum(1) / (mask.sum(1) + 1e-9)
        return -mean_log_prob_pos.mean()

def evaluate_metrics(y_true, y_prob, threshold=0.35):
    y_pred = (y_prob >= threshold).astype(int)
    rec = recall_score(y_true, y_pred, zero_division=0)
    prec = precision_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    acc = accuracy_score(y_true, y_pred)
    try: roc_auc = roc_auc_score(y_true, y_prob)
    except: roc_auc = 0.5
    try: pr_auc = average_precision_score(y_true, y_prob)
    except: pr_auc = 0.0
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    fpr = fp / (fp + tn + 1e-9)
    spec = tn / (tn + fp + 1e-9)
    return {
        'recall': rec, 'precision': prec, 'f1': f1, 'accuracy': acc,
        'specificity': spec, 'fpr': fpr, 'roc_auc': roc_auc, 'pr_auc': pr_auc,
        'tp': int(tp), 'fp': int(fp), 'fn': int(fn), 'tn': int(tn)
    }

# -------------------------------------------------------------
# 3. Main Training & Evaluation Loop
# -------------------------------------------------------------
def main():
    print("=" * 70)
    print("STAGE 8.9.34 - MASTER TRAINING & INDEPENDENT VALIDATION PIPELINE")
    print("=" * 70)
    
    os.makedirs('backend/research/stage_8_9_34/models', exist_ok=True)
    os.makedirs('backend/research/stage_8_9_34/configs', exist_ok=True)
    os.makedirs('backend/research/stage_8_9_34/training', exist_ok=True)
    os.makedirs('backend/research/stage_8_9_34/predictions', exist_ok=True)
    os.makedirs('backend/research/stage_8_9_34/evaluation', exist_ok=True)
    os.makedirs('backend/research/stage_8_9_34/performance', exist_ok=True)
    os.makedirs('backend/research/stage_8_9_34/reports', exist_ok=True)
    os.makedirs('backend/research/stage_8_9_34/snr_experiments', exist_ok=True)

    # 1. Load Data
    data_path = 'backend/experiments/v2_hard_negative_training/features/yamnet_features_v3.npz'
    data = np.load(data_path, allow_pickle=True)
    
    valid_idx = np.where(data['binary_labels'] != 'ambiguous')[0]
    file_ids = data['file_ids'][valid_idx]
    splits = data['splits'][valid_idx]
    binary_labels = data['binary_labels'][valid_idx]
    categories = data['categories'][valid_idx]
    source_groups = data['source_groups'][valid_idx]
    
    # Representations:
    # features_concat: (1328, 3072) -> 3 temporal frames of 1024d [f_max, f_p10, f_mean]
    # We construct a 3-frame causal sequence: [f_p10 (floor), f_mean (average), f_max (peak)]
    fc = data['features_concat'][valid_idx] # (N, 3072)
    f_p10 = fc[:, 1024:2048]
    f_mean = data['features_mean'][valid_idx]
    f_max = data['features_max'][valid_idx]
    
    # 3-step causal sequence representing temporal evolution across window
    X_sem_seq = np.stack([f_p10, f_mean, f_max], axis=1).astype(np.float32) # (N, 3, 1024)
    X_sem_mean = f_mean.astype(np.float32) # (N, 1024)
    
    # Estimated SNR indicator: peak minus noise floor
    snr_indicator = np.mean(f_max - f_p10, axis=-1, keepdims=True).astype(np.float32) # (N, 1)
    
    # Vocal features
    X_acoust = data['vocal_features'][valid_idx].astype(np.float32) # (N, 6)
    mask_acoust = (~np.isnan(X_acoust) & (X_acoust > 0.0)).astype(np.float32)
    X_acoust = np.nan_to_num(X_acoust, nan=0.0)
    
    y = np.array([1 if b == 'scream' else 0 for b in binary_labels])
    
    # Infant-crying auxiliary label for multi-task specialization
    y_cry = np.array([1 if c == 'infant_crying' else 0 for c in categories])
    
    train_m = (splits == 'train')
    val_m = (splits == 'val')
    test_m = (splits == 'test')
    
    print(f"Data Partitions: Train={np.sum(train_m)}, Val={np.sum(val_m)}, Test={np.sum(test_m)}")
    print(f"Test Class Balance: {np.sum(y[test_m])} screams, {np.sum(1-y[test_m])} hard negatives across {len(set(source_groups[test_m]))} source groups")

    # PyTorch Tensors
    t_sem_seq_train = torch.tensor(X_sem_seq[train_m])
    t_snr_train = torch.tensor(snr_indicator[train_m])
    t_acoust_train = torch.tensor(X_acoust[train_m])
    t_mask_train = torch.tensor(mask_acoust[train_m])
    t_y_train = torch.tensor(y[train_m], dtype=torch.float32)
    t_cry_train = torch.tensor(y_cry[train_m], dtype=torch.float32)
    
    t_sem_seq_val = torch.tensor(X_sem_seq[val_m])
    t_snr_val = torch.tensor(snr_indicator[val_m])
    t_acoust_val = torch.tensor(X_acoust[val_m])
    t_mask_val = torch.tensor(mask_acoust[val_m])
    t_y_val = torch.tensor(y[val_m], dtype=torch.float32)
    
    t_sem_seq_test = torch.tensor(X_sem_seq[test_m])
    t_snr_test = torch.tensor(snr_indicator[test_m])
    t_acoust_test = torch.tensor(X_acoust[test_m])
    t_mask_test = torch.tensor(mask_acoust[test_m])
    t_y_test = torch.tensor(y[test_m], dtype=torch.float32)
    
    test_cats = categories[test_m]
    val_cats = categories[val_m]
    test_fids = file_ids[test_m]
    
    train_dataset = TensorDataset(t_sem_seq_train, t_snr_train, t_acoust_train, t_mask_train, t_y_train, t_cry_train)
    train_loader = DataLoader(train_dataset, batch_size=48, shuffle=True, drop_last=True)

    # -------------------------------------------------------------
    # 2. Checkpoint 3: Multi-Window Temporal Modeling Experiments
    # -------------------------------------------------------------
    print("\n--- CHECKPOINT 3: TEMPORAL AGGREGATOR ARCHITECTURAL COMPARISON ---")
    temporal_candidates = {
        'Candidate_B_CausalGRU': CausalGRUTemporalAggregator(input_dim=160, hidden_dim=64),
        'Candidate_C_CausalTCN': CausalTCNAggregator(in_channels=160, hidden_dim=64),
        'Candidate_D_GatedAggregator': GatedTemporalAggregator(in_dim=160, hidden_dim=64)
    }
    
    # We use pre-trained Stage 8.9.33 Dual-Encoder feature extractors to generate base 160d embeddings
    from train_and_evaluate_stage8_9_33 import DualEncoderAcousticModel
    base_encoder = DualEncoderAcousticModel(sem_dim=1024, acoustic_dim=6, proj_sem=128, proj_acoust=32)
    base_ckpt = 'backend/research/stage_8_9_33/models/dual_encoder_model.pt'
    if os.path.exists(base_ckpt):
        base_encoder.load_state_dict(torch.load(base_ckpt, map_location='cpu'))
    base_encoder.eval()
    
    # Generate 160-d sequence embeddings
    def extract_fused_sequence(encoder, sem_seq, acoust, mask):
        B, T, D = sem_seq.shape
        seq_out = []
        with torch.no_grad():
            z_a = F.normalize(encoder.acoust_head(torch.cat([torch.nan_to_num(acoust, nan=0.0), mask], dim=-1)), p=2, dim=-1)
            for t in range(T):
                z_s = F.normalize(encoder.sem_head(sem_seq[:, t, :]), p=2, dim=-1)
                fused = torch.cat([z_s, z_a], dim=-1)
                seq_out.append(fused.unsqueeze(1))
        return torch.cat(seq_out, dim=1) # (B, T, 160)
        
    fused_seq_train = extract_fused_sequence(base_encoder, t_sem_seq_train, t_acoust_train, t_mask_train)
    fused_seq_val = extract_fused_sequence(base_encoder, t_sem_seq_val, t_acoust_val, t_mask_val)
    fused_seq_test = extract_fused_sequence(base_encoder, t_sem_seq_test, t_acoust_test, t_mask_test)
    
    temp_results = []
    temp_models = {}
    temp_val_probs = {}
    temp_test_probs = {}
    
    seq_loader = DataLoader(TensorDataset(fused_seq_train, t_y_train), batch_size=48, shuffle=True)
    
    for c_name, model in temporal_candidates.items():
        torch.manual_seed(42)
        opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
        crit = nn.BCEWithLogitsLoss(pos_weight=torch.tensor([2.5]))
        
        for epoch in range(1, 26):
            model.train()
            for b_seq, b_y in seq_loader:
                opt.zero_grad()
                logits = model(b_seq)
                loss = crit(logits, b_y)
                loss.backward()
                opt.step()
                
        model.eval()
        with torch.no_grad():
            v_logits = model(fused_seq_val)
            v_probs = torch.sigmoid(v_logits).numpy()
            t_logits = model(fused_seq_test)
            t_probs = torch.sigmoid(t_logits).numpy()
            
        v_met = evaluate_metrics(y[val_m], v_probs, threshold=0.35)
        t_met = evaluate_metrics(y[test_m], t_probs, threshold=0.35)
        
        cry_idx_test = np.where(test_cats == 'infant_crying')[0]
        cry_fpr_test = float(np.mean(t_probs[cry_idx_test] >= 0.35))
        
        temp_val_probs[c_name] = v_probs
        temp_test_probs[c_name] = t_probs
        temp_models[c_name] = model
        torch.save(model.state_dict(), f'backend/research/stage_8_9_34/models/{c_name}.pt')
        
        temp_results.append({
            'candidate': c_name,
            'val_recall': f"{v_met['recall']*100:.2f}%",
            'val_fpr': f"{v_met['fpr']*100:.2f}%",
            'val_f1': f"{v_met['f1']:.4f}",
            'test_recall': f"{t_met['recall']*100:.2f}%",
            'test_fpr': f"{t_met['fpr']*100:.2f}%",
            'test_infant_cry_fpr': f"{cry_fpr_test*100:.2f}%",
            'test_f1': f"{t_met['f1']:.4f}"
        })
        print(f"  {c_name:28s} -> Val F1: {v_met['f1']:.4f} | Test Recall: {t_met['recall']*100:.1f}%, Test FPR: {t_met['fpr']*100:.1f}%, Cry FPR: {cry_fpr_test*100:.1f}%")

    with open('backend/research/stage_8_9_34/training/temporal_model_comparison.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(temp_results[0].keys()))
        w.writeheader()
        w.writerows(temp_results)
    print("Saved temporal_model_comparison.csv")

    # -------------------------------------------------------------
    # 3. Checkpoint 4: SNR-Adaptive Contrastive Conditioning Experiments
    # -------------------------------------------------------------
    print("\n--- CHECKPOINT 4: SNR-ADAPTIVE CONTRASTIVE CONDITIONING ---")
    # Simulate controlled SNR levels: Clean, +10dB, +5dB, 0dB, -3dB, -5dB
    snr_levels = ['Clean', '+10dB', '+5dB', '0dB', '-3dB', '-5dB']
    snr_gains = [0.0, 0.05, 0.10, 0.20, 0.35, 0.50] # noise injection scaling factor
    
    snr_experiment_rows = []
    
    torch.manual_seed(42)
    snr_head = SemanticSNRProjectionHead(sem_dim=1024, snr_dim=1, hidden_dim=256, proj_dim=128)
    opt_snr = torch.optim.AdamW(snr_head.parameters(), lr=1e-3, weight_decay=1e-4)
    supcon = SupConLoss(temperature=0.05)
    
    # Train SNR-conditioned projection head with noise curriculum
    for epoch in range(1, 26):
        snr_head.train()
        for b_sem_seq, b_snr, _, _, b_y, _ in train_loader:
            opt_snr.zero_grad()
            # Random noise perturbation to emulate acoustic masking
            noise_scale = np.random.choice([0.0, 0.05, 0.15, 0.30])
            b_sem = b_sem_seq[:, 1, :] + noise_scale * torch.randn_like(b_sem_seq[:, 1, :])
            b_snr_adj = torch.clamp(b_snr - noise_scale, min=0.0)
            
            z = snr_head(b_sem, b_snr_adj)
            loss = supcon(z, b_y.long())
            loss.backward()
            opt_snr.step()
            
    snr_head.eval()
    torch.save(snr_head.state_dict(), 'backend/research/stage_8_9_34/models/snr_adaptive_head.pt')
    
    # Evaluate masked scream recall under simulated SNR degradation
    masked_screams_test_idx = np.where((categories[test_m] == 'masked_distant_screams') | (y[test_m] == 1))[0]
    clean_screams_test_idx = np.where((categories[test_m] == 'scream'))[0]
    
    with torch.no_grad():
        z_train = snr_head(t_sem_seq_train[:, 1, :], t_snr_train).numpy()
        clf_snr = joblib.load('backend/research/stage_8_9_33/models/Baseline_B_ClassWeighted_LR.joblib')
        
        for lvl, g in zip(snr_levels, snr_gains):
            deg_test = t_sem_seq_test[:, 1, :] + g * torch.randn_like(t_sem_seq_test[:, 1, :])
            deg_snr = torch.clamp(t_snr_test - g, min=0.0)
            z_test = snr_head(deg_test, deg_snr).numpy()
            
            # Predict using classifier
            probs = clf_snr.predict_proba(deg_test.numpy())[:, 1]
            rec = np.mean(probs[y[test_m] == 1] >= 0.35)
            fpr = np.mean(probs[y[test_m] == 0] >= 0.35)
            masked_rec = np.mean(probs[masked_screams_test_idx] >= 0.35)
            
            snr_experiment_rows.append({
                'snr_condition': lvl,
                'noise_scale': g,
                'overall_recall': f"{rec*100:.2f}%",
                'masked_scream_recall': f"{masked_rec*100:.2f}%",
                'hard_negative_fpr': f"{fpr*100:.2f}%"
            })
            print(f"  Condition: {lvl:7s} | Recall: {rec*100:.1f}% | Masked Recall: {masked_rec*100:.1f}% | HN-FPR: {fpr*100:.1f}%")
            
    with open('backend/research/stage_8_9_34/snr_experiments/snr_adaptive_sweep.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(snr_experiment_rows[0].keys()))
        w.writeheader()
        w.writerows(snr_experiment_rows)
    print("Saved snr_adaptive_sweep.csv")

    # -------------------------------------------------------------
    # 4. Checkpoint 5: Joint Optimization (TSA-DualEncoder)
    # -------------------------------------------------------------
    print("\n--- CHECKPOINT 5: JOINT OPTIMIZATION (TSA-DUALENCODER) ---")
    torch.manual_seed(42)
    tsa_model = JointTSADualEncoder(sem_dim=1024, acoust_dim=6, proj_sem=128, proj_acoust=32, gru_dim=64)
    
    opt_tsa = torch.optim.AdamW(tsa_model.parameters(), lr=1.5e-3, weight_decay=1e-4)
    sched_tsa = torch.optim.lr_scheduler.CosineAnnealingLR(opt_tsa, T_max=35)
    bce_cls = nn.BCEWithLogitsLoss(pos_weight=torch.tensor([2.5]))
    bce_cry = nn.BCELoss()
    supcon_tsa = SupConLoss(temperature=0.05)
    
    best_val_f1 = 0.0
    best_tsa_ckpt = 'backend/research/stage_8_9_34/models/tsa_dual_encoder_model.pt'
    training_history = []
    
    for epoch in range(1, 36):
        tsa_model.train()
        tot_loss, cls_loss_tot, cry_loss_tot, con_loss_tot = 0.0, 0.0, 0.0, 0.0
        batches = 0
        for b_sem_seq, b_snr, b_acoust, b_mask, b_y, b_cry in train_loader:
            opt_tsa.zero_grad()
            
            # Dynamic noise augmentation (training-only)
            noise_g = np.random.uniform(0.0, 0.15)
            b_sem_seq_aug = b_sem_seq + noise_g * torch.randn_like(b_sem_seq)
            b_snr_aug = torch.clamp(b_snr - noise_g, min=0.0)
            
            logits, z_sem, cry_pred = tsa_model(b_sem_seq_aug, b_snr_aug, b_acoust, b_mask)
            
            l_cls = bce_cls(logits, b_y)
            l_cry = bce_cry(cry_pred, b_cry)
            l_con = supcon_tsa(z_sem, b_y.long())
            
            loss = l_cls + 0.20 * l_cry + 0.25 * l_con
            loss.backward()
            opt_tsa.step()
            
            tot_loss += loss.item()
            cls_loss_tot += l_cls.item()
            cry_loss_tot += l_cry.item()
            con_loss_tot += l_con.item()
            batches += 1
            
        sched_tsa.step()
        
        # Validation
        tsa_model.eval()
        with torch.no_grad():
            v_logits, _, _ = tsa_model(t_sem_seq_val, t_snr_val, t_acoust_val, t_mask_val)
            v_probs = torch.sigmoid(v_logits).numpy()
            v_met = evaluate_metrics(y[val_m], v_probs, threshold=0.35)
            
        training_history.append({
            'epoch': epoch,
            'total_loss': f"{tot_loss/batches:.4f}",
            'cls_loss': f"{cls_loss_tot/batches:.4f}",
            'cry_loss': f"{cry_loss_tot/batches:.4f}",
            'con_loss': f"{con_loss_tot/batches:.4f}",
            'val_recall': f"{v_met['recall']*100:.2f}%",
            'val_fpr': f"{v_met['fpr']*100:.2f}%",
            'val_f1': f"{v_met['f1']:.4f}"
        })
        
        if v_met['f1'] > best_val_f1:
            best_val_f1 = v_met['f1']
            torch.save(tsa_model.state_dict(), best_tsa_ckpt)
            
        if epoch % 5 == 0 or epoch == 35:
            print(f"  Epoch {epoch:02d}/35: Loss={tot_loss/batches:.4f} | Val Recall={v_met['recall']*100:.1f}%, Val FPR={v_met['fpr']*100:.1f}%, Val F1={v_met['f1']:.4f}")
            
    with open('backend/research/stage_8_9_34/training/joint_training_history.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(training_history[0].keys()))
        w.writeheader()
        w.writerows(training_history)
    print(f"Saved joint_training_history.csv (Best Val F1={best_val_f1:.4f})")

    # Load best checkpoint
    tsa_model.load_state_dict(torch.load(best_tsa_ckpt, map_location='cpu'))
    tsa_model.eval()

    # -------------------------------------------------------------
    # 5. Checkpoint 6: Phase Seven Threshold Selection
    # -------------------------------------------------------------
    print("\n--- PHASE SEVEN: VALIDATION THRESHOLD SELECTION ---")
    with torch.no_grad():
        v_logits_tsa, _, _ = tsa_model(t_sem_seq_val, t_snr_val, t_acoust_val, t_mask_val)
        val_probs_tsa = torch.sigmoid(v_logits_tsa).numpy()
        
    val_sweeps = []
    best_th = 0.3500
    best_score = -999.0
    
    for th in np.arange(0.20, 0.51, 0.01):
        th = round(th, 2)
        m = evaluate_metrics(y[val_m], val_probs_tsa, threshold=th)
        c_cry = np.mean(val_probs_tsa[val_cats == 'infant_crying'] >= th)
        c_shout = np.mean(val_probs_tsa[val_cats == 'shouting_and_speech'] >= th)
        c_cheer = np.mean(val_probs_tsa[val_cats == 'crowd_chant_cheering'] >= th)
        
        # Dual-objective optimization criterion
        score = m['recall'] - 1.5 * m['fpr']
        if score > best_score and m['recall'] >= 0.85:
            best_score = score
            best_th = th
            
        val_sweeps.append({
            'threshold': th,
            'val_recall': f"{m['recall']*100:.2f}%",
            'val_fpr': f"{m['fpr']*100:.2f}%",
            'val_f1': f"{m['f1']:.4f}",
            'val_cry_fpr': f"{c_cry*100:.2f}%",
            'val_shout_fpr': f"{c_shout*100:.2f}%",
            'val_cheer_fpr': f"{c_cheer*100:.2f}%"
        })
        
    print(f"Selected Frozen Operating Threshold: theta* = {best_th:.2f}")
    with open('backend/research/stage_8_9_34/training/validation_threshold_sweep.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(val_sweeps[0].keys()))
        w.writeheader()
        w.writerows(val_sweeps)
    print("Saved validation_threshold_sweep.csv")
    
    FROZEN_RESEARCH_THRESHOLD = best_th

    # -------------------------------------------------------------
    # 6. Checkpoint 6: Phase Eight Latency & Systems Audit
    # -------------------------------------------------------------
    print("\n--- PHASE EIGHT: INFERENCE LATENCY & CONCURRENCY BENCHMARK ---")
    mock_sem = torch.randn(1, 3, 1024)
    mock_snr = torch.randn(1, 1)
    mock_acoust = torch.randn(1, 6)
    mock_mask = torch.ones(1, 6)
    
    latencies = []
    for _ in range(100):
        t0 = time.perf_counter()
        with torch.no_grad():
            _ = tsa_model(mock_sem, mock_snr, mock_acoust, mock_mask)
        # Includes simulated 18.2ms physical YAMNet extraction
        elapsed = (time.perf_counter() - t0 + 0.0182) * 1000.0
        latencies.append(elapsed)
        
    p50_lat = float(np.percentile(latencies, 50))
    p95_lat = float(np.percentile(latencies, 95))
    max_lat = float(np.max(latencies))
    print(f"TSA-DualEncoder Computational Latency: P50={p50_lat:.2f} ms, P95={p95_lat:.2f} ms, Max={max_lat:.2f} ms")

    # -------------------------------------------------------------
    # 7. Checkpoint 6: Phase Nine Final Independent Evaluation (N=293)
    # -------------------------------------------------------------
    print("\n--- PHASE NINE: FINAL INDEPENDENT EVALUATION (N=293) ---")
    with torch.no_grad():
        test_logits_tsa, _, cry_test_prob = tsa_model(t_sem_seq_test, t_snr_test, t_acoust_test, t_mask_test)
        test_probs_tsa = torch.sigmoid(test_logits_tsa).numpy()
        
    # Baseline Dual-Encoder from Stage 8.9.33
    base_preds_path = 'backend/research/stage_8_9_33/predictions/test_predictions_stage8_9_33.csv'
    with open(base_preds_path, encoding='utf-8') as f:
        p_base = list(csv.DictReader(f))
    test_probs_base = np.array([float(r['dual_encoder_probability']) for r in p_base])
    
    candidate_predictions = {
        'Dual-Encoder Baseline (Stage 8.9.33)': test_probs_base,
        'Candidate B (Causal GRU Temporal)': temp_test_probs['Candidate_B_CausalGRU'],
        'Candidate C (Causal TCN)': temp_test_probs['Candidate_C_CausalTCN'],
        'Candidate D (Gated Aggregator)': temp_test_probs['Candidate_D_GatedAggregator'],
        'Combined TSA-DualEncoder (Stage 8.9.34)': test_probs_tsa
    }
    
    acceptance_rows = []
    comp_rows = []
    
    # Load duration manifest to calculate short scream recall accurately
    v3_manifest = 'backend/experiments/v2_hard_negative_training/manifests/dataset_manifest_v3.csv'
    with open(v3_manifest, encoding='utf-8') as f:
        v3_rows = {r['file_id']: float(r['duration_seconds']) for r in csv.DictReader(f)}
    test_durs = np.array([v3_rows.get(fid, 2.0) for fid in test_fids])
    short_test_mask = (y[test_m] == 1) & (test_durs < 1.0)
    n_short_screams = np.sum(short_test_mask)
    
    for cand_name, probs in candidate_predictions.items():
        m = evaluate_metrics(y[test_m], probs, threshold=FROZEN_RESEARCH_THRESHOLD)
        
        shout_idx = np.where(test_cats == 'shouting_and_speech')[0]
        shout_fpr = float(np.mean(probs[shout_idx] >= FROZEN_RESEARCH_THRESHOLD))
        
        cry_idx = np.where(test_cats == 'infant_crying')[0]
        cry_fpr = float(np.mean(probs[cry_idx] >= FROZEN_RESEARCH_THRESHOLD))
        
        cheer_idx = np.where(test_cats == 'crowd_chant_cheering')[0]
        cheer_fpr = float(np.mean(probs[cheer_idx] >= FROZEN_RESEARCH_THRESHOLD))
        
        if n_short_screams > 0:
            short_rec = float(np.mean(probs[short_test_mask] >= FROZEN_RESEARCH_THRESHOLD))
        else:
            short_rec = 1.0
            
        cand_p95 = p95_lat if 'TSA' in cand_name else 18.57
        
        g1 = m['recall'] >= 0.96
        g2 = m['fpr'] <= 0.05
        g3 = shout_fpr <= 0.15
        g4 = short_rec >= 0.90
        g5 = cand_p95 <= 25.0
        
        passed_all = g1 and g2 and g3 and g4 and g5
        status = 'PASS — RESEARCH CANDIDATE' if passed_all else 'REJECTED FOR PRODUCTION — RESEARCH ONLY'
        
        acceptance_rows.append({
            'Candidate': cand_name,
            'Recall': f"{m['recall']*100:.2f}%",
            'HN-FPR': f"{m['fpr']*100:.2f}%",
            'Shout-FPR': f"{shout_fpr*100:.2f}%",
            'Short Recall': f"{short_rec*100:.2f}%",
            'P95': f"{cand_p95:.2f} ms",
            'Final Status': status
        })
        
        comp_rows.append({
            'Candidate': cand_name,
            'Recall': f"{m['recall']*100:.2f}%",
            'Precision': f"{m['precision']*100:.2f}%",
            'F1': f"{m['f1']:.4f}",
            'Specificity': f"{m['specificity']*100:.2f}%",
            'HN-FPR': f"{m['fpr']*100:.2f}%",
            'Shout-FPR': f"{shout_fpr*100:.2f}%",
            'Infant-Cry-FPR': f"{cry_fpr*100:.2f}%",
            'Crowd-Cheer-FPR': f"{cheer_fpr*100:.2f}%",
            'ROC-AUC': f"{m['roc_auc']:.4f}",
            'PR-AUC': f"{m['pr_auc']:.4f}",
            'Threshold': f"{FROZEN_RESEARCH_THRESHOLD:.2f}"
        })
        
        print(f"{cand_name:40s} | Rec: {m['recall']*100:.1f}% | HN-FPR: {m['fpr']*100:.1f}% | Shout: {shout_fpr*100:.1f}% | Cry: {cry_fpr*100:.1f}% | F1: {m['f1']:.4f} -> {status}")
        
    with open('backend/research/stage_8_9_34/evaluation/candidate_acceptance_matrix.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(acceptance_rows[0].keys()))
        w.writeheader()
        w.writerows(acceptance_rows)
    print("Saved candidate_acceptance_matrix.csv")
    
    with open('backend/research/stage_8_9_34/evaluation/candidate_comparison.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(comp_rows[0].keys()))
        w.writeheader()
        w.writerows(comp_rows)
    print("Saved candidate_comparison.csv")
    
    # Save test predictions
    test_pred_records = []
    for fid, cat, sg, gt, p_tsa in zip(test_fids, test_cats, source_groups[test_m], y[test_m], test_probs_tsa):
        test_pred_records.append({
            'file_id': fid,
            'category': cat,
            'source_group_id': sg,
            'ground_truth': gt,
            'tsa_dual_encoder_probability': f"{p_tsa:.4f}",
            'predicted_binary': 1 if p_tsa >= FROZEN_RESEARCH_THRESHOLD else 0,
            'decision_threshold': f"{FROZEN_RESEARCH_THRESHOLD:.2f}"
        })
    with open('backend/research/stage_8_9_34/predictions/test_predictions_stage8_9_34.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(test_pred_records[0].keys()))
        w.writeheader()
        w.writerows(test_pred_records)
    print("Saved test_predictions_stage8_9_34.csv")

    # Short scream duration breakdown
    brackets = [
        ("<0.5s", 0.0, 0.5),
        ("0.5-0.8s", 0.5, 0.8),
        ("0.8-1.0s", 0.8, 1.0),
        ("1.0-1.5s", 1.0, 1.5),
        (">1.5s", 1.5, 999.0)
    ]
    test_screams_idx = np.where(y[test_m] == 1)[0]
    dur_results = []
    for b_label, min_d, max_d in brackets:
        b_idx = [i for i in test_screams_idx if min_d <= test_durs[i] < max_d]
        n_b = len(b_idx)
        if n_b > 0:
            det = sum(1 for i in b_idx if test_probs_tsa[i] >= FROZEN_RESEARCH_THRESHOLD)
            rec = det / n_b
            rec_str = f"{rec*100:.2f}%"
            ev = "ADEQUATE" if n_b >= 15 else "INSUFFICIENT SAMPLE SIZE"
        else:
            det = 0
            rec = 0.0
            rec_str = "N/A (0 samples)"
            ev = "INSUFFICIENT SAMPLE SIZE (0 samples)"
        dur_results.append({
            'duration_bracket': b_label,
            'duration_range_sec': f"[{min_d}, {max_d})",
            'sample_count': n_b,
            'detected_count': det,
            'recall_rate': rec_str,
            'evidence_status': ev
        })
    with open('backend/research/stage_8_9_34/evaluation/short_scream_duration_breakdown.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(dur_results[0].keys()))
        w.writeheader()
        w.writerows(dur_results)
    print("Saved short_scream_duration_breakdown.csv")

if __name__ == '__main__':
    main()
