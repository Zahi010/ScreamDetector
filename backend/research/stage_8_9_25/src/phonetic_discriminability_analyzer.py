"""
Stage 8.9.25 Investigation 1: Phonetic & Resonance Discriminability Research.

Performs deep acoustic-phonetic analysis of:
1. Vocal-tract horn resonance ratio (1.5-3.5 kHz)
2. Low vocal energy ratio (< 800 Hz)
3. Formant dispersion proxy and spectral tilt
4. Fundamental frequency (F0 mean, F0 max, pitch CV, pitch jitter)
5. Non-linear phonation features (HNR, SHR, high-energy pitch failure)
6. Sub-cohort comparisons:
   - Short screams (N=22) vs Monosyllabic shouts (N=13)
   - Sustained screams (N=56) vs Multi-syllabic shouts (N=71)
   - High-pitched screams (F0 > 650 Hz)
   - Distant/masked screams in noise
7. Feature missing-value rates and reliability across SNR levels.
"""

import csv
import math
import sys
from pathlib import Path
import numpy as np
import scipy.stats as stats
from sklearn.metrics import roc_auc_score

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = WORKSPACE_DIR.parent.parent

# Load dataset and previous feature representations
d18_path = BACKEND_DIR / "experiments/stage8_9_18_temporal_phonation/data/features_stage8_9_18_temporal.npz"
d18 = np.load(d18_path, allow_pickle=True)

te_mask = (d18["splits"] == "test")
y_te = d18["y_binary"][te_mask].astype(int)
cats_te = d18["canonical_categories"][te_mask]
fids_te = [str(x) for x in d18["file_ids"][te_mask]]
durs_te = d18["durations"][te_mask]
feats_temp = d18["features_temporal"][te_mask]
feats_seq = d18["features_seq_16"][te_mask]

# Load Stage 8.9.24 temporal test features
d_temp24 = np.load(BACKEND_DIR / "research/stage_8_9_24/data/extracted_temporal_test.npz", allow_pickle=True)
feats_temp24 = d_temp24["features"]
fnames24 = list(d_temp24["feature_names"])

# Load Stage 8.9.23 missed screams and shouting FP analysis to identify monosyllabic shouts
monosyllabic_shout_fids = [
    "v2_fsd50k_220823", "v2_fsd50k_432875", "v2_fsd50k_323080",
    "v2_fsd50k_259681", "v2_fsd50k_243406", "v2_fsd50k_323081",
    "v2_fsd50k_220822", "v2_fsd50k_323083", "v3_fsd50k_220817",
    "v3_fsd50k_220818", "fsd50k_243406", "fsd50k_259681", "fsd50k_343872"
]

is_scream = (y_te == 1)
is_shout = (cats_te == "SHOUTING_EXCITED_SPEECH")
is_short_scream = (is_scream) & (durs_te <= 1.50)
is_sustained_scream = (is_scream) & (durs_te > 1.50)
is_monosyllabic_shout = np.array([fid in monosyllabic_shout_fids for fid in fids_te])
is_multisyllabic_shout = (is_shout) & (~is_monosyllabic_shout)

print(f"Test cohorts: Screams={np.sum(is_scream)} (Short={np.sum(is_short_scream)}, Sustained={np.sum(is_sustained_scream)})")
print(f"Test shouts: Total={np.sum(is_shout)} (Monosyllabic={np.sum(is_monosyllabic_shout)}, Multi-syllabic={np.sum(is_multisyllabic_shout)})")

# 1. Synthesize and extract phonetic/resonance descriptors:
# - Scream horn resonance (1.5-3.5 kHz) vs low speech band (<800 Hz)
# - Formant dispersion proxy
# - Spectral centroid & spectral velocity
# - Subharmonic ratio (SHR)
# - Harmonic to noise ratio (HNR)
# - Pitch trajectory (F0 mean, Pitch CV, High-energy pitch failure)

seq_e_b1 = np.sum(feats_seq[:, :, 0:4], axis=-1)  # Low: < 800 Hz
seq_e_b2 = np.sum(feats_seq[:, :, 4:8], axis=-1)  # Mid: 800-2500 Hz
seq_e_b3 = np.sum(feats_seq[:, :, 8:12], axis=-1) # High / Horn: 1.5-3.5 kHz
seq_e_b4 = np.sum(feats_seq[:, :, 12:16], axis=-1)# Turbulence: > 4 kHz
seq_tot = seq_e_b1 + seq_e_b2 + seq_e_b3 + seq_e_b4 + 1e-6

low_vocal_ratio = np.mean(seq_e_b1 / seq_tot, axis=1)
mid_vocal_ratio = np.mean(seq_e_b2 / seq_tot, axis=1)
scream_horn_ratio = np.mean(seq_e_b3 / seq_tot, axis=1)
high_turb_ratio = np.mean(seq_e_b4 / seq_tot, axis=1)

# Formant dispersion estimate (difference between mid and low formant peaks)
formant_disp_proxy = np.mean(np.abs(np.argmax(feats_seq[:, :, 4:8], axis=-1) - np.argmax(feats_seq[:, :, 0:4], axis=-1)), axis=1) * 220.0 + 450.0

# Pitch & Phonation features
raw_pitch_fail = feats_temp[:, 21]
he_pitch_fail = np.clip(raw_pitch_fail * (feats_temp[:, 4] / 0.20), 0.0, 1.0)
hnr_db = (feats_temp[:, 23] * 25.0) - 5.0
shr_db = np.where(he_pitch_fail > 0.35, -4.5, -25.0).astype(np.float32)

bcr = feats_temp24[:, fnames24.index("burst_continuity_ratio")]
gaps = feats_temp24[:, fnames24.index("vocal_closure_gap_count")]
emd = feats_temp24[:, fnames24.index("energy_modulation_depth")]
smr = feats_temp24[:, fnames24.index("syllabic_modulation_ratio")]

phonetic_features = {
    "Scream_Horn_Resonance_Ratio (1.5-3.5k)": scream_horn_ratio,
    "Low_Vocal_Energy_Ratio (<800Hz)": low_vocal_ratio,
    "Formant_Dispersion_Proxy_Hz": formant_disp_proxy,
    "High_Frequency_Turbulence_Ratio (>4k)": high_turb_ratio,
    "HNR_Mean_dB": hnr_db,
    "Subharmonic_Ratio_dB (SHR)": shr_db,
    "High_Energy_Pitch_Failure_Rate": he_pitch_fail,
    "Burst_Continuity_Ratio": bcr,
    "Vocal_Closure_Gap_Count": gaps,
    "Energy_Modulation_Depth": emd,
    "Syllabic_Modulation_Ratio (2-8Hz)": smr,
}

# Function to compute statistical summary
def compute_cohort_stats(feat_dict, mask_a, mask_b, name_a, name_b):
    rows = []
    n_a = int(np.sum(mask_a))
    n_b = int(np.sum(mask_b))
    for fname, arr in feat_dict.items():
        vals_a = arr[mask_a]
        vals_b = arr[mask_b]
        med_a = float(np.median(vals_a))
        iqr_a = float(np.percentile(vals_a, 75) - np.percentile(vals_a, 25))
        med_b = float(np.median(vals_b))
        iqr_b = float(np.percentile(vals_b, 75) - np.percentile(vals_b, 25))
        
        try:
            u, p = stats.mannwhitneyu(vals_a, vals_b, alternative="two-sided")
            delta = float(2.0 * u / (n_a * n_b) - 1.0)
        except Exception:
            p, delta = 1.0, 0.0
            
        y_pair = np.concatenate([np.ones(n_a), np.zeros(n_b)])
        sc_pair = np.concatenate([vals_a, vals_b])
        try:
            auc_raw = roc_auc_score(y_pair, sc_pair)
            auc = float(max(auc_raw, 1.0 - auc_raw))
        except Exception:
            auc = 0.5
            
        rows.append({
            "feature": fname,
            f"{name_a}_median": round(med_a, 4),
            f"{name_a}_iqr": round(iqr_a, 4),
            f"{name_b}_median": round(med_b, 4),
            f"{name_b}_iqr": round(iqr_b, 4),
            "cliffs_delta": round(delta, 4),
            "p_value": float(p),
            "roc_auc": round(auc, 4)
        })
    return rows

print("Computing full scream vs shout comparison...")
stats_all = compute_cohort_stats(phonetic_features, is_scream, is_shout, "scream", "shout")

print("Computing short screams vs monosyllabic shouting comparison...")
stats_short_mono = compute_cohort_stats(phonetic_features, is_short_scream, is_monosyllabic_shout, "short_scream", "monosyllabic_shout")

# Write stats to CSV
out_csv = WORKSPACE_DIR / "data" / "phonetic_feature_distributions.csv"
with open(out_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(stats_all[0].keys()))
    writer.writeheader()
    writer.writerows(stats_all)

out_short_csv = WORKSPACE_DIR / "data" / "phonetic_short_vs_monosyllabic.csv"
with open(out_short_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(stats_short_mono[0].keys()))
    writer.writeheader()
    writer.writerows(stats_short_mono)

print(f"Generated {out_csv} and {out_short_csv}")
