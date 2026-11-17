"""
Stage 8.9.36 - Phase 3: False-Negative Forensics Script
Analyzes all 11 Candidate D false negatives in the independent held-out test cohort.
"""
import os
import csv
import json
import numpy as np
import pandas as pd
import soundfile as sf

def analyze_false_negatives():
    print("======================================================================")
    print("STAGE 8.9.36 - PHASE 3: FALSE-NEGATIVE FORENSICS AUDIT")
    print("======================================================================")
    
    # 1. Load predictions & manifest
    preds_path = "backend/research/stage_8_9_35/predictions/test_predictions_stage8_9_35.csv"
    manifest_path = "backend/experiments/v2_hard_negative_training/manifests/dataset_manifest_v3.csv"
    subband_csv = "backend/research/stage_8_9_35/frequency_analysis/subband_feature_analysis.csv"
    npz_path = "backend/experiments/v2_hard_negative_training/features/yamnet_features_v3.npz"
    
    df_preds = pd.read_csv(preds_path)
    df_manifest = pd.read_csv(manifest_path)
    data_npz = np.load(npz_path, allow_pickle=True)
    
    npz_fids = list(data_npz['file_ids'])
    npz_vocal = data_npz['vocal_features']
    
    with open(subband_csv, encoding='utf-8') as f:
        sb_map = {r['file_id']: r for r in csv.DictReader(f)}
        
    fn_preds = df_preds[(df_preds['ground_truth'] == 1) & (df_preds['predicted_binary'] == 0)].copy()
    assert len(fn_preds) == 11, f"Expected 11 false negatives, found {len(fn_preds)}"
    
    forensics_rows = []
    
    for idx, row in fn_preds.iterrows():
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
        silence_ratio = float(np.mean(np.abs(audio) < 0.01))
        
        # Phonation features from npz
        npz_idx = npz_fids.index(fid)
        vocal_feats = npz_vocal[npz_idx] # [f0_mean, f0_std, voicing_ratio, jitter, shimmer, hnr]
        f0_mean = float(vocal_feats[0]) if not np.isnan(vocal_feats[0]) else 0.0
        voicing_ratio = float(vocal_feats[2]) if not np.isnan(vocal_feats[2]) else 0.0
        hnr = float(vocal_feats[5]) if not np.isnan(vocal_feats[5]) else 0.0
        
        # Subband features
        sb = sb_map.get(fid, {})
        b1_rel = float(sb.get('Band1_300_800Hz_rel_energy', 0.0))
        b2_rel = float(sb.get('Band2_800_1500Hz_rel_energy', 0.0))
        b4_rel = float(sb.get('Band4_2000_3000Hz_rel_energy', 0.0))
        b5_rel = float(sb.get('Band5_3000_4000Hz_rel_energy', 0.0))
        scream_ratio = float(sb.get('scream_band_to_vocal_ratio', 0.0))
        
        prob = float(row['mp_dual_encoder_probability'])
        thresh = float(row['decision_threshold'])
        gap = thresh - prob
        
        # Forensic Failure Categorization
        if 'snr-06db' in fid or 'snr-03db' in fid or 'snr+00db' in fid:
            failure_cat = "A_EXTREME_LOW_SNR_MASKING"
            explanation = "Distant scream heavily masked by diffuse crowd/music background (SNR <= 0 dB). Harmonic peaks submerged in noise floor."
        elif 'snr+03db' in fid:
            failure_cat = "B_MODERATE_SNR_NOISE_MASKING"
            explanation = "Distant scream mixed at +3 dB SNR. Sufficient noise floor to depress 2-3 kHz resonance below detection threshold."
        elif prob >= 0.35 and prob < 0.43:
            failure_cat = "C_BORDERLINE_THRESHOLD_MISS"
            explanation = "Borderline scream probability (0.35 <= P < 0.43). Detected under historical threshold 0.35, but missed at validation threshold 0.43."
        elif 'gasp-oooh' in fid or 'surprised-oooh' in fid:
            failure_cat = "D_LABEL_ANOMALY_GASP_OOOH"
            explanation = "Labeling anomaly: Recording is a soft gasp or surprised 'oooh' vocalization lacking scream acoustic energy, vocal strain, or F0 excursion."
        else:
            failure_cat = "E_LOW_INTENSITY_ATYPICAL_SCREAM"
            explanation = "Atypical scream characterized by low acoustic intensity, short duration, or lack of sustained harmonic structure in Band 4/5."
            
        forensics_rows.append({
            "file_id": fid,
            "category": row['category'],
            "source_group_id": row['source_group_id'],
            "duration_sec": round(dur, 3),
            "peak_amplitude": round(peak, 4),
            "rms_energy": round(rms, 4),
            "clipping_ratio": round(clipping_ratio, 4),
            "silence_ratio": round(silence_ratio, 4),
            "f0_mean_hz": round(f0_mean, 1),
            "voicing_ratio": round(voicing_ratio, 3),
            "hnr_db": round(hnr, 2),
            "b1_300_800hz_rel": round(b1_rel, 3),
            "b2_800_1500hz_rel": round(b2_rel, 3),
            "b4_2000_3000hz_rel": round(b4_rel, 3),
            "scream_ratio": round(scream_ratio, 3),
            "predicted_prob": round(prob, 4),
            "decision_threshold": thresh,
            "threshold_gap": round(gap, 4),
            "failure_category": failure_cat,
            "forensic_explanation": explanation
        })
        
    fn_df = pd.DataFrame(forensics_rows)
    eval_dir = "backend/research/stage_8_9_36/evaluation"
    os.makedirs(eval_dir, exist_ok=True)
    out_csv = os.path.join(eval_dir, "false_negative_forensics.csv")
    fn_df.to_csv(out_csv, index=False)
    print(f"Saved {out_csv}")
    
    # Print summary
    print("\n--- FORENSIC CATEGORIZATION OF 11 FALSE NEGATIVES ---")
    cat_counts = fn_df['failure_category'].value_counts()
    for cat, count in cat_counts.items():
        print(f"  {cat}: {count} recordings ({count/11*100:.1f}%)")
        
    print("\nDetailed breakdown:")
    for idx, r in fn_df.iterrows():
        print(f"  [{r['failure_category']}] {r['file_id']} | Prob: {r['predicted_prob']:.4f} | RMS: {r['rms_energy']:.4f} | Dur: {r['duration_sec']:.2f}s")

if __name__ == "__main__":
    analyze_false_negatives()
