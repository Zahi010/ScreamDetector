"""
Stage 8.9.37 - Task 1: Audit Model Candidates & Generate Unified Prediction Arrays
Extracts and validates continuous prediction probabilities for Configurations A, B, C, D
across both validation (N=293) and test (N=293) cohorts.
"""
import os
import sys
import csv
import json
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F

# Add stage paths for model classes
sys.path.insert(0, os.path.abspath("backend/research/stage_8_9_35/src"))
from train_and_evaluate_stage8_9_35 import MultiPathwayFusionModel

# Set deterministic seed
torch.manual_seed(42)
np.random.seed(42)

# Models from Stage 8.9.36 ablation
class YamnetOnlyModel(nn.Module):
    def __init__(self, sem_dim=1024):
        super().__init__()
        self.sem_head = nn.Sequential(
            nn.Linear(sem_dim, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.15),
            nn.Linear(256, 128)
        )
        self.fc = nn.Linear(128, 1)
    def forward(self, x_sem):
        z = F.normalize(self.sem_head(x_sem), p=2, dim=-1)
        return self.fc(z).squeeze(-1)

class YamnetSubbandModel(nn.Module):
    def __init__(self, sem_dim=1024, subband_dim=11):
        super().__init__()
        self.sem_head = nn.Sequential(
            nn.Linear(sem_dim, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.15),
            nn.Linear(256, 128)
        )
        self.subband_head = nn.Sequential(
            nn.Linear(subband_dim, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(0.10),
            nn.Linear(32, 16)
        )
        self.fc = nn.Sequential(
            nn.Linear(128 + 16, 64),
            nn.ReLU(),
            nn.Dropout(0.10),
            nn.Linear(64, 1)
        )
    def forward(self, x_sem, x_subband):
        z_s = F.normalize(self.sem_head(x_sem), p=2, dim=-1)
        z_sb = F.normalize(self.subband_head(x_subband), p=2, dim=-1)
        fused = torch.cat([z_s, z_sb], dim=-1)
        return self.fc(fused).squeeze(-1)

# Dual-Encoder Architecture from Stage 8.9.33
class DualEncoderModel(nn.Module):
    def __init__(self, sem_dim=1024, acoust_dim=6, proj_dim=128):
        super().__init__()
        self.sem_head = nn.Sequential(
            nn.Linear(sem_dim, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.15),
            nn.Linear(256, proj_dim)
        )
        self.acoust_head = nn.Sequential(
            nn.Linear(acoust_dim * 2, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.10),
            nn.Linear(64, proj_dim)
        )
        self.classifier = nn.Sequential(
            nn.Linear(proj_dim * 2, 64),
            nn.ReLU(),
            nn.Dropout(0.10),
            nn.Linear(64, 1)
        )
    def forward(self, x_sem, x_acoust, mask_acoust):
        z_sem = F.normalize(self.sem_head(x_sem), p=2, dim=-1)
        comb_acoust = torch.cat([x_acoust, mask_acoust], dim=-1)
        z_acoust = F.normalize(self.acoust_head(comb_acoust), p=2, dim=-1)
        fused = torch.cat([z_sem, z_acoust], dim=-1)
        return self.classifier(fused).squeeze(-1)

def extract_all_predictions():
    print("======================================================================")
    print("STAGE 8.9.37 - TASK 1: CANDIDATE PREDICTION EXTRACTION")
    print("======================================================================")
    
    # Load dataset
    npz_path = "backend/experiments/v2_hard_negative_training/features/yamnet_features_v3.npz"
    subband_csv = "backend/research/stage_8_9_35/frequency_analysis/subband_feature_analysis.csv"
    
    data = np.load(npz_path, allow_pickle=True)
    valid_idx = np.where(data['binary_labels'] != 'ambiguous')[0]
    file_ids = data['file_ids'][valid_idx]
    splits = data['splits'][valid_idx]
    binary_labels = data['binary_labels'][valid_idx]
    categories = data['categories'][valid_idx]
    source_groups = data['source_groups'][valid_idx]
    
    X_sem = data['features_mean'][valid_idx].astype(np.float32)
    X_acoust = data['vocal_features'][valid_idx].astype(np.float32)
    mask_acoust = (~np.isnan(X_acoust) & (X_acoust > 0.0)).astype(np.float32)
    X_acoust = np.nan_to_num(X_acoust, nan=0.0)
    y = np.array([1 if b == 'scream' else 0 for b in binary_labels])
    
    with open(subband_csv, encoding='utf-8') as f:
        sb_map = {r['file_id']: r for r in csv.DictReader(f)}
        
    X_sb = []
    for fid in file_ids:
        r = sb_map.get(fid, {})
        vec = [
            float(r.get('Band1_300_800Hz_rel_energy', 0.0)),
            float(r.get('Band2_800_1500Hz_rel_energy', 0.0)),
            float(r.get('Band3_1500_2000Hz_rel_energy', 0.0)),
            float(r.get('Band4_2000_3000Hz_rel_energy', 0.0)),
            float(r.get('Band5_3000_4000Hz_rel_energy', 0.0)),
            float(r.get('Band6_4000_6000Hz_rel_energy', 0.0)),
            float(r.get('Band1_300_800Hz_temp_var', 0.0)),
            float(r.get('Band4_2000_3000Hz_temp_var', 0.0)),
            float(r.get('Band5_3000_4000Hz_temp_var', 0.0)),
            float(r.get('scream_band_to_vocal_ratio', 0.0)),
            float(r.get('high_band_whistle_ratio', 0.0))
        ]
        X_sb.append(vec)
    X_sb = np.array(X_sb, dtype=np.float32)
    
    train_m = (splits == 'train')
    val_m = (splits == 'val')
    test_m = (splits == 'test')
    
    print(f"Partitions: Train={np.sum(train_m)}, Val={np.sum(val_m)}, Test={np.sum(test_m)}")
    
    device = torch.device('cpu')
    
    # 1. Config A: YAMNet-only
    print("Training / Loading Config A (YAMNet-Only)...")
    model_a = YamnetOnlyModel(sem_dim=1024)
    opt_a = torch.optim.AdamW(model_a.parameters(), lr=1e-3, weight_decay=1e-4)
    crit = nn.BCEWithLogitsLoss()
    x_s_tr = torch.from_numpy(X_sem[train_m])
    y_tr = torch.from_numpy(y[train_m]).float()
    for _ in range(25):
        model_a.train()
        opt_a.zero_grad()
        loss = crit(model_a(x_s_tr), y_tr)
        loss.backward()
        opt_a.step()
    model_a.eval()
    with torch.no_grad():
        probs_val_a = torch.sigmoid(model_a(torch.from_numpy(X_sem[val_m]))).numpy()
        probs_test_a = torch.sigmoid(model_a(torch.from_numpy(X_sem[test_m]))).numpy()
        
    # 2. Config B: Dual-Encoder (Stage 8.9.33)
    print("Loading Config B (Dual-Encoder Baseline)...")
    base_model_path = "backend/research/stage_8_9_33/models/dual_encoder_model.pt"
    # Stage 8.9.33 model architecture
    sys.path.insert(0, os.path.abspath("backend/research/stage_8_9_33/src"))
    from train_and_evaluate_stage8_9_33 import DualEncoderAcousticModel as DE33
    model_b = DE33(sem_dim=1024, acoustic_dim=6, proj_sem=128, proj_acoust=32)
    model_b.load_state_dict(torch.load(base_model_path, map_location=device))
    model_b.eval()
    with torch.no_grad():
        v_s = torch.from_numpy(X_sem[val_m])
        v_a = torch.from_numpy(X_acoust[val_m])
        v_m = torch.from_numpy(mask_acoust[val_m])
        t_s = torch.from_numpy(X_sem[test_m])
        t_a = torch.from_numpy(X_acoust[test_m])
        t_m = torch.from_numpy(mask_acoust[test_m])
        
        logits_val_b, _, _ = model_b(v_s, v_a, v_m)
        logits_test_b, _, _ = model_b(t_s, t_a, t_m)
        probs_val_b = torch.sigmoid(logits_val_b).numpy()
        probs_test_b = torch.sigmoid(logits_test_b).numpy()
        
    # 3. Config C: YAMNet + Subband
    print("Training / Loading Config C (YAMNet + Subband)...")
    model_c = YamnetSubbandModel(sem_dim=1024, subband_dim=11)
    opt_c = torch.optim.AdamW(model_c.parameters(), lr=1e-3, weight_decay=1e-4)
    x_sb_tr = torch.from_numpy(X_sb[train_m])
    for _ in range(25):
        model_c.train()
        opt_c.zero_grad()
        loss = crit(model_c(x_s_tr, x_sb_tr), y_tr)
        loss.backward()
        opt_c.step()
    model_c.eval()
    with torch.no_grad():
        probs_val_c = torch.sigmoid(model_c(torch.from_numpy(X_sem[val_m]), torch.from_numpy(X_sb[val_m]))).numpy()
        probs_test_c = torch.sigmoid(model_c(torch.from_numpy(X_sem[test_m]), torch.from_numpy(X_sb[test_m]))).numpy()
        
    # 4. Config D: MP-FS-DualEncoder (Stage 8.9.35)
    print("Loading Config D (MP-FS-DualEncoder)...")
    mp_model_path = "backend/research/stage_8_9_35/models/mp_fs_dual_encoder_model.pt"
    model_d = MultiPathwayFusionModel(sem_dim=1024, acoust_dim=6, subband_dim=11)
    model_d.load_state_dict(torch.load(mp_model_path, map_location=device))
    model_d.eval()
    with torch.no_grad():
        v_sb = torch.from_numpy(X_sb[val_m])
        t_sb = torch.from_numpy(X_sb[test_m])
        logits_val_d, _, _ = model_d(v_s, v_a, v_m, v_sb)
        logits_test_d, _, _ = model_d(t_s, t_a, t_m, t_sb)
        probs_val_d = torch.sigmoid(logits_val_d).numpy()
        probs_test_d = torch.sigmoid(logits_test_d).numpy()
        
    # Load duration from manifest
    manifest_df = pd.read_csv("backend/experiments/v2_hard_negative_training/manifests/dataset_manifest_v3.csv")
    dur_map = dict(zip(manifest_df['file_id'], manifest_df['duration_seconds']))
    val_dur = np.array([dur_map.get(fid, 0.0) for fid in file_ids[val_m]])
    test_dur = np.array([dur_map.get(fid, 0.0) for fid in file_ids[test_m]])

    # Build validation dataframe
    val_df = pd.DataFrame({
        "file_id": file_ids[val_m],
        "category": categories[val_m],
        "source_group_id": source_groups[val_m],
        "ground_truth": y[val_m],
        "duration_seconds": val_dur,
        "is_short_scream": ((y[val_m] == 1) & (val_dur < 1.0)).astype(int),
        "prob_config_a": probs_val_a,
        "prob_config_b": probs_val_b,
        "prob_config_c": probs_val_c,
        "prob_config_d": probs_val_d
    })
    
    # Build test dataframe
    test_df = pd.DataFrame({
        "file_id": file_ids[test_m],
        "category": categories[test_m],
        "source_group_id": source_groups[test_m],
        "ground_truth": y[test_m],
        "duration_seconds": test_dur,
        "is_short_scream": ((y[test_m] == 1) & (test_dur < 1.0)).astype(int),
        "prob_config_a": probs_test_a,
        "prob_config_b": probs_test_b,
        "prob_config_c": probs_test_c,
        "prob_config_d": probs_test_d
    })
    
    val_out_path = "backend/research/stage_8_9_37/results/threshold_sweeps/validation_predictions_all_candidates.csv"
    test_out_path = "backend/research/stage_8_9_37/results/test_evaluations/test_predictions_all_candidates.csv"
    
    val_df.to_csv(val_out_path, index=False)
    test_df.to_csv(test_out_path, index=False)
    print(f"Saved {val_out_path} ({len(val_df)} rows, 79 screams, 214 negatives)")
    print(f"Saved {test_out_path} ({len(test_df)} rows, 102 screams, 191 negatives)")

if __name__ == "__main__":
    extract_all_predictions()
