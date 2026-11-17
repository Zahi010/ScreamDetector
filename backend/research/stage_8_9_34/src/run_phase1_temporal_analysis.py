import os
import csv
import json
from pathlib import Path
import numpy as np
import soundfile as sf
import scipy.signal as signal

def compute_temporal_features(y, sr):
    """
    Extract comprehensive temporal, envelope, and modulation features from raw waveform.
    """
    # 1. Total duration
    total_dur = len(y) / sr
    
    # 2. RMS Energy Envelope (10ms hop, 25ms frame)
    frame_len = int(0.025 * sr)
    hop_len = int(0.010 * sr)
    num_frames = max(1, (len(y) - frame_len) // hop_len + 1)
    
    energy_env = []
    for i in range(num_frames):
        seg = y[i * hop_len : i * hop_len + frame_len]
        rms = np.sqrt(np.mean(seg**2) + 1e-9)
        energy_env.append(rms)
    energy_env = np.array(energy_env)
    
    # Normalize envelope
    peak_energy = np.max(energy_env) if len(energy_env) > 0 else 1e-9
    norm_env = energy_env / (peak_energy + 1e-9)
    
    # 3. Burst segmentation (energy > 20% of peak)
    active_mask = (norm_env >= 0.20).astype(int)
    
    # Identify contiguous active regions
    diff = np.diff(np.pad(active_mask, (1, 1), 'constant'))
    starts = np.where(diff == 1)[0]
    ends = np.where(diff == -1)[0]
    
    burst_durations = [(ends[k] - starts[k]) * 0.010 for k in range(len(starts))]
    
    # Inter-burst intervals (silence intervals between bursts)
    if len(starts) > 1:
        silence_durations = [(starts[k+1] - ends[k]) * 0.010 for k in range(len(starts) - 1)]
    else:
        silence_durations = [0.0]
        
    num_bursts = len(burst_durations)
    mean_burst_dur = float(np.mean(burst_durations)) if burst_durations else 0.0
    max_burst_dur = float(np.max(burst_durations)) if burst_durations else 0.0
    mean_silence_dur = float(np.mean(silence_durations)) if silence_durations else 0.0
    
    # Burst continuity ratio (longest continuous burst / total duration)
    burst_continuity = max_burst_dur / max(total_dur, 0.01)
    
    # 4. Amplitude Modulation Frequency & Envelope Periodicity
    # Autocorrelation of energy envelope to detect recurring vocal bursts
    if len(norm_env) > 50:
        env_demean = norm_env - np.mean(norm_env)
        autocorr = np.correlate(env_demean, env_demean, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        autocorr = autocorr / (autocorr[0] + 1e-9)
        
        # Search for periodic peaks between 0.3s (30 frames) and 2.5s (250 frames)
        search_range = autocorr[30:min(len(autocorr), 250)]
        if len(search_range) > 0:
            peak_lag = np.argmax(search_range) + 30
            periodicity_score = float(search_range[peak_lag - 30])
            estimated_period_sec = peak_lag * 0.010
            repetition_rate_hz = 1.0 / estimated_period_sec if estimated_period_sec > 0 else 0.0
        else:
            periodicity_score = 0.0
            repetition_rate_hz = 0.0
    else:
        periodicity_score = 0.0
        repetition_rate_hz = 0.0
        
    # 5. Spectral Centroid Temporal Trajectory
    # Simple zero-crossing rate variance as proxy for spectral evolution
    zcrs = []
    for i in range(num_frames):
        seg = y[i * hop_len : i * hop_len + frame_len]
        zcr = np.mean(np.abs(np.diff(np.sign(seg)))) / 2.0
        zcrs.append(zcr)
    zcr_std = float(np.std(zcrs)) if zcrs else 0.0
    
    # 6. Modulation Depth
    mod_depth = float((np.max(energy_env) - np.min(energy_env)) / (np.max(energy_env) + np.min(energy_env) + 1e-9))
    
    return {
        'total_duration_sec': round(total_dur, 3),
        'num_bursts': num_bursts,
        'bursts_per_sec': round(num_bursts / max(total_dur, 0.01), 2),
        'mean_burst_dur_sec': round(mean_burst_dur, 3),
        'max_burst_dur_sec': round(max_burst_dur, 3),
        'mean_silence_dur_sec': round(mean_silence_dur, 3),
        'burst_continuity_ratio': round(burst_continuity, 3),
        'envelope_periodicity_score': round(max(0.0, periodicity_score), 4),
        'repetition_rate_hz': round(repetition_rate_hz, 2),
        'modulation_depth': round(mod_depth, 4),
        'spectral_variation_zcr_std': round(zcr_std, 4)
    }

def main():
    print("=" * 70)
    print("STAGE 8.9.34 - CHECKPOINT 2: PHASE 1 TEMPORAL DATA ANALYSIS")
    print("=" * 70)
    
    manifest_path = 'backend/experiments/v2_hard_negative_training/manifests/dataset_manifest_v3.csv'
    with open(manifest_path, encoding='utf-8') as f:
        records = list(csv.DictReader(f))
        
    # Filter categories of interest
    target_cats = ['infant_crying', 'crowd_chant_cheering', 'shouting_and_speech']
    crying_recs = [r for r in records if r['target_category'] == 'infant_crying']
    screams_recs = [r for r in records if r['binary_label'] == 'scream']
    shout_recs = [r for r in records if r['target_category'] == 'shouting_and_speech']
    cheer_recs = [r for r in records if r['target_category'] == 'crowd_chant_cheering']
    
    print(f"Dataset Pool: Screams={len(screams_recs)}, Crying={len(crying_recs)}, Shouting={len(shout_recs)}, Cheering={len(cheer_recs)}")
    
    # Process files
    analysis_rows = []
    
    selected_cohort = (
        [('scream', r) for r in screams_recs[:60]] +
        [('infant_crying', r) for r in crying_recs[:60]] +
        [('shouting_and_speech', r) for r in shout_recs[:40]] +
        [('crowd_chant_cheering', r) for r in cheer_recs[:40]]
    )
    
    print(f"Extracting temporal dynamics from {len(selected_cohort)} audio files...")
    
    for cat_label, r in selected_cohort:
        fpath = r['workspace_audio_path']
        if not os.path.exists(fpath):
            continue
            
        try:
            audio, sr = sf.read(fpath)
            if audio.ndim > 1:
                audio = np.mean(audio, axis=1)
                
            feats = compute_temporal_features(audio, sr)
            feats['file_id'] = r['file_id']
            feats['category'] = cat_label
            feats['split'] = r['split']
            feats['source_group_id'] = r['source_group_id']
            analysis_rows.append(feats)
        except Exception as e:
            continue
            
    print(f"Successfully computed features for {len(analysis_rows)} recordings.")
    
    # Save temporal_feature_analysis.csv
    out_csv = 'backend/research/stage_8_9_34/temporal_analysis/temporal_feature_analysis.csv'
    with open(out_csv, 'w', newline='', encoding='utf-8') as f:
        fields = [
            'file_id', 'category', 'split', 'source_group_id', 'total_duration_sec',
            'num_bursts', 'bursts_per_sec', 'mean_burst_dur_sec', 'max_burst_dur_sec',
            'mean_silence_dur_sec', 'burst_continuity_ratio', 'envelope_periodicity_score',
            'repetition_rate_hz', 'modulation_depth', 'spectral_variation_zcr_std'
        ]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(analysis_rows)
    print(f"Saved {out_csv}")
    
    # Analyze distributions by category
    print("\n--- Summary of Category Temporal Dynamics ---")
    summary_by_cat = {}
    for cat in ['scream', 'infant_crying', 'shouting_and_speech', 'crowd_chant_cheering']:
        cat_rows = [r for r in analysis_rows if r['category'] == cat]
        if not cat_rows: continue
        
        burst_rates = [r['bursts_per_sec'] for r in cat_rows]
        periodicities = [r['envelope_periodicity_score'] for r in cat_rows]
        continuities = [r['burst_continuity_ratio'] for r in cat_rows]
        rep_rates = [r['repetition_rate_hz'] for r in cat_rows if r['repetition_rate_hz'] > 0]
        mean_silences = [r['mean_silence_dur_sec'] for r in cat_rows]
        
        summary_by_cat[cat] = {
            'mean_burst_rate': np.mean(burst_rates),
            'std_burst_rate': np.std(burst_rates),
            'mean_periodicity': np.mean(periodicities),
            'std_periodicity': np.std(periodicities),
            'mean_continuity': np.mean(continuities),
            'mean_repetition_hz': np.mean(rep_rates) if rep_rates else 0.0,
            'mean_silence_sec': np.mean(mean_silences)
        }
        
        print(f"Category: {cat:22s} | Periodicity: {np.mean(periodicities):.3f} +/- {np.std(periodicities):.3f} | Burst Continuity: {np.mean(continuities):.3f} | Repetition: {np.mean(rep_rates):.2f} Hz")
        
    # Analyze False Negatives from Stage 8.9.33 in temporal context
    fn_path = 'backend/research/stage_8_9_33/forensic_analysis/false_negative_forensics.csv'
    fn_analysis_rows = []
    if os.path.exists(fn_path):
        with open(fn_path, encoding='utf-8') as f:
            fn_records = list(csv.DictReader(f))
        for fn in fn_records:
            fid = fn['file_id']
            # Find in records
            match = [r for r in records if r['file_id'] == fid]
            if match and os.path.exists(match[0]['workspace_audio_path']):
                a, sr = sf.read(match[0]['workspace_audio_path'])
                if a.ndim > 1: a = np.mean(a, axis=1)
                tf = compute_temporal_features(a, sr)
                tf['file_id'] = fid
                tf['ground_truth'] = fn.get('ground_truth', 'scream')
                tf['reported_prob'] = fn.get('dual_encoder_probability', '0.0')
                tf['failure_reason'] = fn.get('failure_cause', 'Unknown')
                fn_analysis_rows.append(tf)
                
    if fn_analysis_rows:
        out_fn = 'backend/research/stage_8_9_34/temporal_analysis/false_negative_temporal_analysis.csv'
        with open(out_fn, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(fn_analysis_rows[0].keys()))
            w.writeheader()
            w.writerows(fn_analysis_rows)
        print(f"Saved {out_fn}")
        
    print("\nCHECKPOINT 2 TEMPORAL FEATURE EXTRACTION COMPLETE.")

if __name__ == '__main__':
    main()
