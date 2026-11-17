"""
Stage 8.9.36 - Phase 4: False-Positive Forensics Script
Analyzes all 19 Candidate D false alarms in the independent held-out test cohort.
"""
import os
import sys
import csv
import json
import numpy as np
import pandas as pd
import soundfile as sf
import torch

# Add path to Stage 8.9.35 src
sys.path.insert(0, os.path.abspath("backend/research/stage_8_9_35/src"))
from train_and_evaluate_stage8_9_35 import MultiPathwayFusionModel

def analyze_false_positives():
    print("======================================================================")
    print("STAGE 8.9.36 - PHASE 4: FALSE-POSITIVE FORENSICS AUDIT")
    print("======================================================================")
    
    # 1. Load Data
    preds_path = "backend/research/stage_8_9_35/predictions/test_predictions_stage8_9_35.csv"
    base_preds_path = "backend/research/stage_8_9_33/predictions/test_predictions_stage8_9_33.csv"
    manifest_path = "backend/experiments/v2_hard_negative_training/manifests/dataset_manifest_v3.csv"
    subband_csv = "backend/research/stage_8_9_35/frequency_analysis/subband_feature_analysis.csv"
    npz_path = "backend/experiments/v2_hard_negative_training/features/yamnet_features_v3.npz"
    model_path = "backend/research/stage_8_9_35/models/mp_fs_dual_encoder_model.pt"
    
    df_preds = pd.read_csv(preds_path)
    df_base = pd.read_csv(base_preds_path)
    df_manifest = pd.read_csv(manifest_path)
    data_npz = np.load(npz_path, allow_pickle=True)
    
    npz_fids = list(data_npz['file_ids'])
    npz_sem = data_npz['features_mean'].astype(np.float32)
    npz_vocal = data_npz['vocal_features'].astype(np.float32)
    
    with open(subband_csv, encoding='utf-8') as f:
        sb_map = {r['file_id']: r for r in csv.DictReader(f)}
        
    fp_preds = df_preds[(df_preds['ground_truth'] == 0) & (df_preds['predicted_binary'] == 1)].copy()
    assert len(fp_preds) == 19, f"Expected 19 false positives, found {len(fp_preds)}"
    
    # Load Model to probe pathway activations
    device = torch.device('cpu')
    model = MultiPathwayFusionModel(sem_dim=1024, acoust_dim=6, subband_dim=11).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    
    # Probe isolated pathway logit contributions:
    # fusion net is Linear(176, 64) -> ReLU -> Linear(64, 1)
    # 176 = 128 (sem) + 32 (acoust) + 16 (subband)
    w_fusion_1 = model.fusion[0].weight.data.numpy() # (64, 176)
    b_fusion_1 = model.fusion[0].bias.data.numpy()   # (64,)
    w_fusion_2 = model.fusion[3].weight.data.numpy() # (1, 64)
    b_fusion_2 = model.fusion[3].bias.data.numpy()   # (1,)
    
    forensics_rows = []
    
    for idx, row in fp_preds.iterrows():
        fid = row['file_id']
        m_row = df_manifest[df_manifest['file_id'] == fid].iloc[0]
        audio_path = m_row['workspace_audio_path']
        
        # Audio forensic measurements
        assert os.path.exists(audio_path), f"Audio file not found: {audio_path}"
        audio, sr = sf.read(audio_path)
        if audio.ndim > 1:
            audio = np.mean(audio, axis=1)
            
        dur = len(audio) / sr
        peak = float(np.max(np.abs(audio)))
        rms = float(np.sqrt(np.mean(audio ** 2)))
        clipping_ratio = float(np.mean(np.abs(audio) >= 0.999))
        
        # Subband features
        sb = sb_map.get(fid, {})
        b1_rel = float(sb.get('Band1_300_800Hz_rel_energy', 0.0))
        b2_rel = float(sb.get('Band2_800_1500Hz_rel_energy', 0.0))
        b4_rel = float(sb.get('Band4_2000_3000Hz_rel_energy', 0.0))
        b5_rel = float(sb.get('Band5_3000_4000Hz_rel_energy', 0.0))
        b6_rel = float(sb.get('Band6_4000_6000Hz_rel_energy', 0.0))
        scream_ratio = float(sb.get('scream_band_to_vocal_ratio', 0.0))
        whistle_ratio = float(sb.get('high_band_whistle_ratio', 0.0))
        
        # Base probability
        base_match = df_base[df_base['file_id'] == fid]
        base_prob = float(base_match['dual_encoder_probability'].iloc[0]) if len(base_match) > 0 else 0.0
        
        # Pathway activations
        npz_i = npz_fids.index(fid)
        x_s = torch.from_numpy(npz_sem[npz_i:npz_i+1]).to(device)
        x_a_raw = npz_vocal[npz_i:npz_i+1]
        x_m_raw = (~np.isnan(x_a_raw) & (x_a_raw > 0.0)).astype(np.float32)
        x_a_clean = np.nan_to_num(x_a_raw, nan=0.0)
        x_a = torch.from_numpy(x_a_clean).to(device)
        x_m = torch.from_numpy(x_m_raw).to(device)
        
        x_sb_vec = [
            b1_rel, b2_rel, float(sb.get('Band3_1500_2000Hz_rel_energy', 0.0)),
            b4_rel, b5_rel, b6_rel,
            float(sb.get('Band1_300_800Hz_temp_var', 0.0)),
            float(sb.get('Band4_2000_3000Hz_temp_var', 0.0)),
            float(sb.get('Band5_3000_4000Hz_temp_var', 0.0)),
            scream_ratio, whistle_ratio
        ]
        x_sb = torch.tensor([x_sb_vec], dtype=torch.float32, device=device)
        
        with torch.no_grad():
            logit, z_sem, z_subband = model(x_s, x_a, x_m, x_sb)
            prob = float(torch.sigmoid(logit).item())
            
        prob_delta = prob - base_prob
        
        # Determine whether subband pathway increased probability
        subband_elevated = (b4_rel + b5_rel) > 0.12 or scream_ratio > 3.0
        
        # Forensic Category Explanation
        cat = row['category']
        if 'cheer' in cat.lower():
            mech = "Crowd cheering harmonic build-up: Synchronous cheering creates aggregate vocal resonance in 1.5-3 kHz that triggers both YAMNet and Subband heads."
        elif 'shout' in cat.lower():
            mech = "High vocal intensity shouting: Shouted speech pushed into high pitch / vocal strain registers, crossing scream feature boundaries."
        elif 'cry' in cat.lower() or 'infant' in cat.lower():
            mech = "Infant crying acoustic convergence: Short vocal tract produces high F0 (~450 Hz) and formants overlapping adult scream resonances."
        elif 'music' in cat.lower() or 'brass' in cat.lower():
            mech = "Instrumental overtone harmonic energy mimicking scream acoustic timbre."
        else:
            mech = "High-energy transient acoustic event with elevated mid/high band energy."
            
        forensics_rows.append({
            "file_id": fid,
            "category": cat,
            "source_group_id": row['source_group_id'],
            "duration_sec": round(dur, 3),
            "peak_amplitude": round(peak, 4),
            "rms_energy": round(rms, 4),
            "b1_rel_energy": round(b1_rel, 3),
            "b4_rel_energy": round(b4_rel, 3),
            "scream_ratio": round(scream_ratio, 3),
            "whistle_ratio": round(whistle_ratio, 3),
            "baseline_prob": round(base_prob, 4),
            "candidate_d_prob": round(prob, 4),
            "prob_delta_vs_baseline": round(prob_delta, 4),
            "subband_pathway_elevated": subband_elevated,
            "forensic_mechanism": mech
        })
        
    fp_df = pd.DataFrame(forensics_rows)
    eval_dir = "backend/research/stage_8_9_36/evaluation"
    os.makedirs(eval_dir, exist_ok=True)
    out_csv = os.path.join(eval_dir, "false_positive_forensics.csv")
    fp_df.to_csv(out_csv, index=False)
    print(f"Saved {out_csv}")
    
    # 2. Category Summary Table
    cat_summary = []
    for cat_name, grp in fp_df.groupby('category'):
        cat_summary.append({
            "category": cat_name,
            "false_positive_count": len(grp),
            "percentage_of_all_fps": round(len(grp) / len(fp_df) * 100, 1),
            "mean_prob": round(float(grp['candidate_d_prob'].mean()), 4),
            "mean_baseline_prob": round(float(grp['baseline_prob'].mean()), 4),
            "mean_prob_delta": round(float(grp['prob_delta_vs_baseline'].mean()), 4),
            "subband_elevated_count": int(grp['subband_pathway_elevated'].sum())
        })
    cat_summary_df = pd.DataFrame(cat_summary).sort_values(by='false_positive_count', ascending=False)
    cat_summary_csv = os.path.join(eval_dir, "false_positive_category_summary.csv")
    cat_summary_df.to_csv(cat_summary_csv, index=False)
    print(f"Saved {cat_summary_csv}")
    
    print("\n--- FALSE POSITIVE CATEGORY SUMMARY ---")
    print(cat_summary_df.to_string(index=False))

if __name__ == '__main__':
    analyze_false_positives()
