import os
import sys
import csv
import numpy as np
import soundfile as sf
import scipy.signal as signal
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import recall_score, precision_score, f1_score, confusion_matrix

BANDS = [
    ("Band1_300_800Hz", 300, 800),
    ("Band2_800_1500Hz", 800, 1500),
    ("Band3_1500_2000Hz", 1500, 2000),
    ("Band4_2000_3000Hz", 2000, 3000),
    ("Band5_3000_4000Hz", 3000, 4000),
    ("Band6_4000_6000Hz", 4000, 6000)
]

def extract_subband_features(audio, sr=16000):
    """
    Extract frequency-subband acoustic features using digital Butterworth IIR filters.
    """
    nyq = sr / 2.0
    total_energy = np.sum(audio ** 2) + 1e-9
    
    subband_feats = {}
    band_energies = []
    
    for b_name, f_low, f_high in BANDS:
        # 4th order bandpass filter
        low_norm = f_low / nyq
        high_norm = min(0.999, f_high / nyq)
        b, a = signal.butter(4, [low_norm, high_norm], btype='band')
        
        filtered = signal.filtfilt(b, a, audio)
        band_energy = np.sum(filtered ** 2)
        band_energies.append(band_energy)
        
        rel_energy = band_energy / total_energy
        rms = np.sqrt(np.mean(filtered ** 2) + 1e-9)
        
        # Temporal energy variation
        hop = int(0.010 * sr)
        frame = int(0.025 * sr)
        n_frames = max(1, (len(filtered) - frame) // hop + 1)
        frame_rms = [np.sqrt(np.mean(filtered[i*hop:i*hop+frame]**2) + 1e-9) for i in range(n_frames)]
        energy_std = float(np.std(frame_rms))
        energy_mean = float(np.mean(frame_rms))
        temp_var = energy_std / (energy_mean + 1e-9)
        
        # Spectral flux proxy
        flux = float(np.mean(np.diff(frame_rms)**2)) if len(frame_rms) > 1 else 0.0
        
        subband_feats[f"{b_name}_rel_energy"] = round(float(rel_energy), 4)
        subband_feats[f"{b_name}_rms"] = round(float(rms), 4)
        subband_feats[f"{b_name}_temp_var"] = round(float(temp_var), 4)
        subband_feats[f"{b_name}_flux"] = round(float(flux), 6)
        
    # High-to-Low energy ratio: (2k-4k Hz) / (300-1500 Hz)
    low_e = band_energies[0] + band_energies[1] + 1e-9
    scream_band_e = band_energies[3] + band_energies[4] + 1e-9
    subband_feats['scream_band_to_vocal_ratio'] = round(float(scream_band_e / low_e), 4)
    
    # Very high band ratio: (4k-6k Hz) / total
    subband_feats['high_band_whistle_ratio'] = round(float(band_energies[5] / total_energy), 4)
    
    return subband_feats

def main():
    print("=" * 70)
    print("STAGE 8.9.35 - CHECKPOINT 2: FREQUENCY-SUBBAND ANALYSIS & MODELING")
    print("=" * 70)
    
    manifest_path = 'backend/experiments/v2_hard_negative_training/manifests/dataset_manifest_v3.csv'
    with open(manifest_path, encoding='utf-8') as f:
        records = list(csv.DictReader(f))
        
    print(f"Total manifest records: {len(records)}")
    
    analysis_rows = []
    X_subband = []
    y_labels = []
    splits = []
    categories = []
    file_ids = []
    
    print("Extracting frequency-subband acoustic features across corpus...")
    
    for r in records:
        fpath = r['workspace_audio_path']
        if not os.path.exists(fpath):
            continue
            
        try:
            audio, sr = sf.read(fpath)
            if audio.ndim > 1:
                audio = np.mean(audio, axis=1)
                
            sb_feats = extract_subband_features(audio, sr)
            
            row = {
                'file_id': r['file_id'],
                'category': r['target_category'],
                'split': r['split'],
                'binary_label': r['binary_label']
            }
            row.update(sb_feats)
            analysis_rows.append(row)
            
            # Numeric feature vector
            vec = [
                sb_feats['Band1_300_800Hz_rel_energy'],
                sb_feats['Band2_800_1500Hz_rel_energy'],
                sb_feats['Band3_1500_2000Hz_rel_energy'],
                sb_feats['Band4_2000_3000Hz_rel_energy'],
                sb_feats['Band5_3000_4000Hz_rel_energy'],
                sb_feats['Band6_4000_6000Hz_rel_energy'],
                sb_feats['Band1_300_800Hz_temp_var'],
                sb_feats['Band4_2000_3000Hz_temp_var'],
                sb_feats['Band5_3000_4000Hz_temp_var'],
                sb_feats['scream_band_to_vocal_ratio'],
                sb_feats['high_band_whistle_ratio']
            ]
            X_subband.append(vec)
            y_labels.append(1 if r['binary_label'] == 'scream' else 0)
            splits.append(r['split'])
            categories.append(r['target_category'])
            file_ids.append(r['file_id'])
            
        except Exception as e:
            continue
            
    print(f"Successfully processed {len(analysis_rows)} recordings.")
    
    # Save subband_feature_analysis.csv
    out_csv = 'backend/research/stage_8_9_35/frequency_analysis/subband_feature_analysis.csv'
    with open(out_csv, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(analysis_rows[0].keys()))
        w.writeheader()
        w.writerows(analysis_rows)
    print(f"Saved {out_csv}")
    
    # Convert to numpy
    X_subband = np.array(X_subband, dtype=np.float32)
    y_labels = np.array(y_labels, dtype=int)
    splits = np.array(splits)
    categories = np.array(categories)
    
    # Subband feature statistics by category
    print("\n--- Relative Energy Distribution by Frequency Band ---")
    cat_summary = {}
    for cat in ['scream', 'infant_crying', 'shouting_and_speech', 'crowd_chant_cheering', 'whistles_and_squeaks']:
        c_m = (categories == cat)
        if np.sum(c_m) == 0: continue
        c_rows = [analysis_rows[i] for i in np.where(c_m)[0]]
        b1 = np.mean([r['Band1_300_800Hz_rel_energy'] for r in c_rows])
        b2 = np.mean([r['Band2_800_1500Hz_rel_energy'] for r in c_rows])
        b4 = np.mean([r['Band4_2000_3000Hz_rel_energy'] for r in c_rows])
        b5 = np.mean([r['Band5_3000_4000Hz_rel_energy'] for r in c_rows])
        b6 = np.mean([r['Band6_4000_6000Hz_rel_energy'] for r in c_rows])
        ratio = np.mean([r['scream_band_to_vocal_ratio'] for r in c_rows])
        
        print(f"Category: {cat:22s} | 300-800Hz: {b1*100:4.1f}% | 800-1.5kHz: {b2*100:4.1f}% | 2k-3kHz: {b4*100:4.1f}% | 3k-4kHz: {b5*100:4.1f}% | 4k-6kHz: {b6*100:4.1f}% | Ratio (2k-4k)/(low): {ratio:.2f}")

    # Evaluate Subband Classifiers
    train_m = (splits == 'train')
    val_m = (splits == 'val')
    test_m = (splits == 'test')
    
    print(f"\nTraining Subband Classifiers on Train ({np.sum(train_m)}), evaluating on Test ({np.sum(test_m)})...")
    
    sb_rf = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42, class_weight='balanced')
    sb_rf.fit(X_subband[train_m], y_labels[train_m])
    
    sb_lr = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
    sb_lr.fit(X_subband[train_m], y_labels[train_m])
    
    rf_probs = sb_rf.predict_proba(X_subband[test_m])[:, 1]
    lr_probs = sb_lr.predict_proba(X_subband[test_m])[:, 1]
    
    def eval_subband(probs, y_t, cats_t, th=0.35):
        y_p = (probs >= th).astype(int)
        rec = recall_score(y_t, y_p, zero_division=0)
        tn, fp, fn, tp = confusion_matrix(y_t, y_p, labels=[0, 1]).ravel()
        fpr = fp / (fp + tn + 1e-9)
        shout_m = (cats_t == 'shouting_and_speech')
        shout_fpr = np.mean(probs[shout_m] >= th) if np.sum(shout_m) > 0 else 0.0
        cry_m = (cats_t == 'infant_crying')
        cry_fpr = np.mean(probs[cry_m] >= th) if np.sum(cry_m) > 0 else 0.0
        cheer_m = (cats_t == 'crowd_chant_cheering')
        cheer_fpr = np.mean(probs[cheer_m] >= th) if np.sum(cheer_m) > 0 else 0.0
        f1 = f1_score(y_t, y_p, zero_division=0)
        return rec, fpr, shout_fpr, cry_fpr, cheer_fpr, f1
        
    rf_rec, rf_fpr, rf_shout, rf_cry, rf_cheer, rf_f1 = eval_subband(rf_probs, y_labels[test_m], categories[test_m])
    lr_rec, lr_fpr, lr_shout, lr_cry, lr_cheer, lr_f1 = eval_subband(lr_probs, y_labels[test_m], categories[test_m])
    
    print(f"Subband Random Forest : Recall={rf_rec*100:.2f}%, HN-FPR={rf_fpr*100:.2f}%, Shout-FPR={rf_shout*100:.2f}%, Cry-FPR={rf_cry*100:.2f}%, Cheer-FPR={rf_cheer*100:.2f}%, F1={rf_f1:.4f}")
    print(f"Subband Logistic Reg  : Recall={lr_rec*100:.2f}%, HN-FPR={lr_fpr*100:.2f}%, Shout-FPR={lr_shout*100:.2f}%, Cry-FPR={lr_cry*100:.2f}%, Cheer-FPR={lr_cheer*100:.2f}%, F1={lr_f1:.4f}")

    # Save frequency_feature_results.csv
    out_results = 'backend/research/stage_8_9_35/evaluation/frequency_feature_results.csv'
    res_rows = [
        {
            'model_name': 'Subband_Random_Forest',
            'test_recall': f"{rf_rec*100:.2f}%",
            'test_hn_fpr': f"{rf_fpr*100:.2f}%",
            'test_shout_fpr': f"{rf_shout*100:.2f}%",
            'test_infant_cry_fpr': f"{rf_cry*100:.2f}%",
            'test_crowd_cheer_fpr': f"{rf_cheer*100:.2f}%",
            'test_f1': f"{rf_f1:.4f}"
        },
        {
            'model_name': 'Subband_Logistic_Regression',
            'test_recall': f"{lr_rec*100:.2f}%",
            'test_hn_fpr': f"{lr_fpr*100:.2f}%",
            'test_shout_fpr': f"{lr_shout*100:.2f}%",
            'test_infant_cry_fpr': f"{lr_cry*100:.2f}%",
            'test_crowd_cheer_fpr': f"{lr_cheer*100:.2f}%",
            'test_f1': f"{lr_f1:.4f}"
        }
    ]
    with open(out_results, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(res_rows[0].keys()))
        w.writeheader()
        w.writerows(res_rows)
    print(f"Saved {out_results}")

if __name__ == '__main__':
    main()
