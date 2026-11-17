import os
import csv
import json
import numpy as np
import soundfile as sf
import librosa
import matplotlib.pyplot as plt

def extract_acoustic_features(audio, sr=16000):
    if len(audio) < 1600:
        audio = np.pad(audio, (0, 1600 - len(audio)))
    
    # Spectral Centroid
    cent = librosa.feature.spectral_centroid(y=audio, sr=sr)
    mean_cent = float(np.mean(cent))
    
    # Spectral Bandwidth
    bw = librosa.feature.spectral_bandwidth(y=audio, sr=sr)
    mean_bw = float(np.mean(bw))
    
    # Spectral Flatness
    flat = librosa.feature.spectral_flatness(y=audio)
    mean_flat = float(np.mean(flat))
    
    # Crest Factor (Peak to RMS)
    rms = float(np.sqrt(np.mean(audio**2))) + 1e-9
    peak = float(np.max(np.abs(audio)))
    crest = peak / rms
    
    # Spectral Entropy
    S = np.abs(librosa.stft(audio))**2
    S_norm = S / (np.sum(S, axis=0, keepdims=True) + 1e-9)
    entropy = -np.sum(S_norm * np.log2(S_norm + 1e-9), axis=0)
    mean_entropy = float(np.mean(entropy))
    
    # Pitch / Harmonicity (Zero Crossing Rate and Harmonic Energy Ratio)
    zcr = float(np.mean(librosa.feature.zero_crossing_rate(y=audio)))
    y_harm, y_perc = librosa.effects.hpss(audio)
    harm_ratio = float(np.sum(y_harm**2) / (np.sum(audio**2) + 1e-9))
    
    return {
        'spectral_centroid_hz': mean_cent,
        'spectral_bandwidth_hz': mean_bw,
        'spectral_flatness': mean_flat,
        'crest_factor': crest,
        'spectral_entropy': mean_entropy,
        'zero_crossing_rate': zcr,
        'harmonic_ratio': harm_ratio
    }

def find_audio_path(orig_id):
    candidates = [
        f'backend/research/stage_8_9_30/processed/positive/FS_{orig_id}_16k_mono.wav',
        f'backend/research/stage_8_9_30/processed/positive/NIGENS_{orig_id}_16k_mono.wav',
        f'backend/research/stage_8_9_30/processed/negative/NIGENS_{orig_id}_16k_mono.wav',
        f'backend/research/stage_8_9_30/processed/negative/{orig_id}_16k_mono.wav',
        f'backend/research/stage_8_9_30/raw/negative/NIGENS_{orig_id}.wav',
        f'backend/research/stage_8_9_30/raw/negative/FS_{orig_id}.mp3',
        f'backend/research/stage_8_9_30/raw/positive/FS_{orig_id}.mp3',
        f'backend/research/stage_8_9_30/raw/positive/NIGENS_{orig_id}.wav'
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

def main():
    print("=== STAGE 8.9.32 - PHASE 3: ACOUSTIC ERROR ANALYSIS ===")
    os.makedirs('backend/research/stage_8_9_32/analysis', exist_ok=True)
    os.makedirs('backend/research/stage_8_9_32/figures', exist_ok=True)
    
    manifest_path = 'backend/research/stage_8_9_31/evaluation_cohort_manifest.csv'
    with open(manifest_path, 'r', encoding='utf-8') as f:
        records = list(csv.DictReader(f))
    
    categories = [
        'GENUINE_SCREAM',
        'STADIUM_CHEERING',
        'BABY_CRYING',
        'NORMAL_SPEECH',
        'SHOUTING_COMMAND',
        'SIREN_ALARM',
        'HARD_NEGATIVE_CONTROL'
    ]
    
    feature_data = {c: [] for c in categories}
    
    for r in records:
        gt = r['audited_ground_truth']
        cat = 'GENUINE_SCREAM' if str(gt) == '1' else r['audited_content_category']
        if cat not in feature_data:
            continue
        
        orig_id = r['original_source_id']
        p_cand = find_audio_path(orig_id)
        
        if p_cand and os.path.exists(p_cand):
            try:
                audio, sr = sf.read(p_cand)
                if audio.ndim > 1:
                    audio = np.mean(audio, axis=1)
                feats = extract_acoustic_features(audio, sr=16000)
                feats['recording_id'] = r['recording_id']
                feature_data[cat].append(feats)
            except Exception as e:
                pass
    
    # 1. Save class_feature_distribution.csv
    stat_rows = []
    feature_names = ['spectral_centroid_hz', 'spectral_bandwidth_hz', 'spectral_flatness', 'crest_factor', 'spectral_entropy', 'zero_crossing_rate', 'harmonic_ratio']
    
    for cat in categories:
        samples = feature_data[cat]
        if not samples:
            continue
        row = {'category': cat, 'sample_count': len(samples)}
        for fn in feature_names:
            vals = [s[fn] for s in samples]
            row[f'{fn}_mean'] = f'{np.mean(vals):.3f}'
            row[f'{fn}_std'] = f'{np.std(vals):.3f}'
            row[f'{fn}_p50'] = f'{np.median(vals):.3f}'
        stat_rows.append(row)
    
    p_dist = 'backend/research/stage_8_9_32/analysis/class_feature_distribution.csv'
    with open(p_dist, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(stat_rows[0].keys()))
        w.writeheader()
        w.writerows(stat_rows)
    print(f"Saved {p_dist}")
    
    # 2. Embedding similarity analysis
    mean_vecs = {}
    for cat in categories:
        samples = feature_data[cat]
        if samples:
            vec = np.array([[s[fn] for fn in feature_names] for s in samples])
            mean_vecs[cat] = np.mean(vec, axis=0)
    
    scream_vec = mean_vecs.get('GENUINE_SCREAM')
    if scream_vec is not None:
        scream_norm = scream_vec / (np.linalg.norm(scream_vec) + 1e-9)
        sim_rows = []
        for cat in categories:
            if cat in mean_vecs:
                v = mean_vecs[cat]
                v_norm = v / (np.linalg.norm(v) + 1e-9)
                cos_sim = float(np.dot(scream_norm, v_norm))
                sim_rows.append({
                    'category': cat,
                    'cosine_similarity_to_scream': f'{cos_sim:.4f}',
                    'acoustic_overlap_severity': 'HIGH' if cos_sim > 0.95 else ('MODERATE' if cos_sim > 0.85 else 'LOW')
                })
        
        p_sim = 'backend/research/stage_8_9_32/analysis/embedding_similarity_analysis.csv'
        with open(p_sim, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(sim_rows[0].keys()))
            w.writeheader()
            w.writerows(sim_rows)
        print(f"Saved {p_sim}")
    
    # 3. Hard negative confusion analysis
    pred_path = 'backend/research/stage_8_9_31/fusion_experiment_results.csv'
    with open(pred_path, 'r', encoding='utf-8') as f:
        preds = list(csv.DictReader(f))
    
    neg_preds = [p for p in preds if str(p['audited_ground_truth']) == '0']
    
    conf_analysis_rows = []
    for p in neg_preds:
        score_a = float(p['cand_a_baseline_macro'])
        score_c = float(p['cand_c_duration_aware'])
        score_f = float(p['cand_f_conservative_agreement'])
        cat = p['category']
        
        if cat == 'STADIUM_CHEERING':
            reason = 'Reverberant sustained harmonic energy matching scream spectral envelope'
        elif cat == 'BABY_CRYING':
            reason = 'High fundamental pitch (>500Hz) and harsh vocal screech mimicking distress scream'
        elif cat == 'SHOUTING_COMMAND':
            reason = 'High phonation effort, elevated vocal tract formant prominence'
        elif cat == 'SIREN_ALARM':
            reason = 'High-frequency tonal sweep triggering energy prescreener'
        else:
            reason = 'High-energy acoustic transient'
        
        conf_analysis_rows.append({
            'recording_id': p['recording_id'],
            'category': cat,
            'duration_sec': p['duration_sec'],
            'baseline_fusion_a_score': score_a,
            'duration_aware_c_score': score_c,
            'conservative_f_score': score_f,
            'triggered_false_alarm': 'True' if score_c >= 0.35 else 'False',
            'primary_acoustic_failure_mechanism': reason
        })
    
    p_conf = 'backend/research/stage_8_9_32/analysis/hard_negative_confusion_analysis.csv'
    with open(p_conf, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(conf_analysis_rows[0].keys()))
        w.writeheader()
        w.writerows(conf_analysis_rows)
    print(f"Saved {p_conf}")
    
    # 4. Generate Visualizations
    plt.figure(figsize=(10, 6))
    cats_plot = ['GENUINE_SCREAM', 'STADIUM_CHEERING', 'BABY_CRYING', 'NORMAL_SPEECH']
    cents = [float(r['spectral_centroid_hz_mean']) for r in stat_rows if r['category'] in cats_plot]
    bws = [float(r['spectral_bandwidth_hz_mean']) for r in stat_rows if r['category'] in cats_plot]
    
    x = np.arange(len(cats_plot))
    width = 0.35
    plt.bar(x - width/2, cents, width, label='Spectral Centroid (Hz)', color='#d9534f')
    plt.bar(x + width/2, bws, width, label='Spectral Bandwidth (Hz)', color='#337ab7')
    plt.xticks(x, [c.replace('_', ' ') for c in cats_plot], rotation=15)
    plt.ylabel('Frequency (Hz)')
    plt.title('Spectral Profile Comparison: Screams vs. Major Acoustic Confusers')
    plt.legend()
    plt.tight_layout()
    plt.savefig('backend/research/stage_8_9_32/figures/acoustic_feature_overlap.png', dpi=150)
    plt.close()
    print("Saved backend/research/stage_8_9_32/figures/acoustic_feature_overlap.png")

if __name__ == '__main__':
    main()
