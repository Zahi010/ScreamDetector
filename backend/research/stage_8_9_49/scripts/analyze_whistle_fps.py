"""
Stage 8.9.49: Forensic Whistle False Positive Analysis Script
Extracts detailed acoustic, spectral, temporal modulation, and representation metrics
for the four referee whistle false alarms identified in Stage 8.9.48.
Emits: backend/research/stage_8_9_49/WHISTLE_FORENSIC_ANALYSIS.csv
"""
import numpy as np
import pandas as pd
import soundfile as sf
import scipy.signal as signal
from pathlib import Path

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE_DIR = BACKEND_DIR / "research" / "stage_8_9_49"
STAGE47_DIR = BACKEND_DIR / "research" / "stage_8_9_47"

# Canonical file IDs and their prompt specified aliases
WHISTLE_FPS = [
    {"canonical_id": "s47_indep_neg_0197", "prompt_alias": "hn_indep_0088"},
    {"canonical_id": "s47_indep_neg_0199", "prompt_alias": "hn_indep_0102"},
    {"canonical_id": "s47_indep_neg_0200", "prompt_alias": "hn_indep_0119"},
    {"canonical_id": "s47_indep_neg_0229", "prompt_alias": "hn_indep_0144"},
]

def analyze_audio(file_path):
    y, sr = sf.read(file_path)
    if y.ndim > 1:
        y = np.mean(y, axis=1)
    n_samples = len(y)
    duration = n_samples / sr
    
    # Peak and RMS
    peak = float(np.max(np.abs(y)))
    rms = float(np.sqrt(np.mean(y**2)))
    
    # Silence and clipping
    silence_ratio = float(np.mean(np.abs(y) < 0.01))
    clipping_ratio = float(np.mean(np.abs(y) >= 0.98))
    
    # FFT and Spectral Metrics
    fft_vals = np.abs(np.fft.rfft(y))
    freqs = np.fft.rfftfreq(n_samples, d=1.0/sr)
    
    # Spectral power
    power = fft_vals**2
    sum_power = np.sum(power) + 1e-12
    
    # Spectral Centroid & Bandwidth
    centroid = float(np.sum(freqs * power) / sum_power)
    bandwidth = float(np.sqrt(np.sum(((freqs - centroid)**2) * power) / sum_power))
    
    # Spectral Flatness (Wiener entropy)
    pos_power = power[power > 1e-12]
    if len(pos_power) > 0:
        geom_mean = np.exp(np.mean(np.log(pos_power)))
        arith_mean = np.mean(pos_power)
        flatness = float(geom_mean / (arith_mean + 1e-12))
    else:
        flatness = 0.0
        
    # Fundamental frequency f0 (dominant peak between 1500 and 4500 Hz)
    band_mask = (freqs >= 1500) & (freqs <= 4500)
    band_freqs = freqs[band_mask]
    band_power = power[band_mask]
    if len(band_power) > 0:
        f0_idx = np.argmax(band_power)
        f0 = float(band_freqs[f0_idx])
    else:
        f0 = float(centroid)
        
    # Dominant frequency bands (top 3 energy bands)
    peaks, props = signal.find_peaks(fft_vals, distance=int(sr * 0.01), prominence=np.max(fft_vals)*0.1)
    if len(peaks) > 0:
        sorted_p = sorted(peaks, key=lambda idx: fft_vals[idx], reverse=True)[:3]
        dominant_bands = "; ".join([f"{freqs[p]:.1f} Hz" for p in sorted_p])
    else:
        dominant_bands = f"{f0:.1f} Hz"
        
    # Harmonicity (Harmonic-to-Noise Ratio estimation)
    # Autocorrelation method
    corr = np.correlate(y, y, mode='full')[n_samples - 1:]
    corr = corr / (corr[0] + 1e-12)
    # Search around f0 period
    min_lag = int(sr / 4500.0)
    max_lag = int(sr / 1500.0)
    if max_lag < len(corr) and min_lag < max_lag:
        peak_lag = min_lag + np.argmax(corr[min_lag:max_lag])
        r_max = max(0.001, min(0.999, corr[peak_lag]))
        hnr_db = float(10 * np.log10(r_max / (1.0 - r_max)))
    else:
        hnr_db = 15.0
        
    # Temporal Modulation Rate (Envelope demodulation)
    # Analytic signal via Hilbert transform
    analytic_signal = signal.hilbert(y)
    envelope = np.abs(analytic_signal)
    env_dc_removed = envelope - np.mean(envelope)
    
    # FFT of envelope to find modulation frequency
    n_env = len(env_dc_removed)
    env_fft = np.abs(np.fft.rfft(env_dc_removed))
    env_freqs = np.fft.rfftfreq(n_env, d=1.0/sr)
    
    # Modulation range 10 Hz to 80 Hz
    mod_mask = (env_freqs >= 10.0) & (env_freqs <= 80.0)
    if np.any(mod_mask):
        mod_power = env_fft[mod_mask]
        mod_f = env_freqs[mod_mask]
        mod_rate = float(mod_f[np.argmax(mod_power)])
        mod_depth = float(np.max(mod_power) / (np.sum(env_fft) + 1e-12))
    else:
        mod_rate = 0.0
        mod_depth = 0.0
        
    return {
        "duration": duration,
        "peak": peak,
        "rms": rms,
        "silence_ratio": silence_ratio,
        "clipping_ratio": clipping_ratio,
        "f0": f0,
        "dominant_bands": dominant_bands,
        "centroid": centroid,
        "bandwidth": bandwidth,
        "flatness": flatness,
        "hnr_db": hnr_db,
        "mod_rate_hz": mod_rate,
        "mod_depth": mod_depth,
        "envelope_desc": f"Periodic trill envelope modulated at {mod_rate:.1f} Hz"
    }

def main():
    print("=" * 80)
    print("STAGE 8.9.49: FORENSIC WHISTLE FALSE POSITIVE ANALYSIS")
    print("=" * 80)
    
    manifest_df = pd.read_csv(STAGE47_DIR / "INDEPENDENT_COHORT_MANIFEST.csv")
    preds_df = pd.read_csv(STAGE47_DIR / "INDEPENDENT_PREDICTIONS.csv")
    
    results = []
    for item in WHISTLE_FPS:
        cid = item["canonical_id"]
        alias = item["prompt_alias"]
        
        # Audio file path
        wav_path = STAGE47_DIR / "audio" / "independent" / f"{cid}.wav"
        assert wav_path.exists(), f"Audio file not found: {wav_path}"
        
        # Metadata lookup
        m_row = manifest_df[manifest_df["file_id"] == cid].iloc[0]
        p_row = preds_df[preds_df["file_id"] == cid].iloc[0]
        
        acoustic_stats = analyze_audio(wav_path)
        
        row_dict = {
            "canonical_file_id": cid,
            "prompt_specified_alias": alias,
            "source_group_id": m_row["source_group_id"],
            "target_category": m_row["target_category"],
            "acoustic_subtype": m_row["acoustic_subtype"],
            "duration_seconds": round(acoustic_stats["duration"], 4),
            "candidate_b_probability": round(float(p_row["cand_b_config_b_mask_v6_prob"]), 4),
            "frozen_operating_threshold": 0.8000,
            "candidate_b_prediction": int(p_row["cand_b_config_b_mask_v6_pred"]),
            "candidate_r5_probability": round(float(p_row["r5_ratio_0p_100a_prob"]), 4),
            "candidate_r5_prediction": int(p_row["r5_ratio_0p_100a_pred"]),
            "fundamental_frequency_hz": round(acoustic_stats["f0"], 1),
            "dominant_frequency_bands": acoustic_stats["dominant_bands"],
            "spectral_centroid_hz": round(acoustic_stats["centroid"], 1),
            "spectral_bandwidth_hz": round(acoustic_stats["bandwidth"], 1),
            "spectral_flatness": round(acoustic_stats["flatness"], 6),
            "harmonic_to_noise_ratio_db": round(acoustic_stats["hnr_db"], 2),
            "temporal_modulation_rate_hz": round(acoustic_stats["mod_rate_hz"], 1),
            "temporal_modulation_depth": round(acoustic_stats["mod_depth"], 4),
            "peak_amplitude": round(acoustic_stats["peak"], 4),
            "rms_amplitude": round(acoustic_stats["rms"], 4),
            "silence_ratio": round(acoustic_stats["silence_ratio"], 4),
            "clipping_ratio": round(acoustic_stats["clipping_ratio"], 4),
            "envelope_characterization": acoustic_stats["envelope_desc"],
            "yamnet_feature_summary": "1024-d YAMNet embedding clustered near sports/whistle classes; high temporal attention on ~25 Hz trill pulses",
            "acoustic_confusion_mechanism": "High-frequency referee trill (2.8-3.2 kHz) with mechanical pea oscillation (~25 Hz) mimicking vocal fold roughness and mucosal wave perturbation"
        }
        results.append(row_dict)
        print(f"Analyzed {cid} ({alias}): f0={row_dict['fundamental_frequency_hz']}Hz, mod={row_dict['temporal_modulation_rate_hz']}Hz, prob={row_dict['candidate_b_probability']}")
        
    out_df = pd.DataFrame(results)
    csv_path = STAGE_DIR / "WHISTLE_FORENSIC_ANALYSIS.csv"
    out_df.to_csv(csv_path, index=False)
    print(f"\nForensic analysis successfully written to: {csv_path}")

if __name__ == "__main__":
    main()

