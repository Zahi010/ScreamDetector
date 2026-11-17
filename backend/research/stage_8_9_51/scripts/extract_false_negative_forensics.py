"""
Stage 8.9.51: Comprehensive Acoustic & Model Forensic Extraction Script
Extracts all Workstream A acoustic, spectral, temporal, and model features
for all 29 False Negatives and 131 True Positives from the Stage 8.9.50 Independent Cohort.
"""
import sys
import math
from pathlib import Path
import numpy as np
import pandas as pd
import soundfile as sf
import scipy.signal as signal
import scipy.stats as stats
import librosa
import torch
import torch.nn as nn
import torch.nn.functional as F

REPO_ROOT = Path(r"c:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE49_DIR = BACKEND_DIR / "research" / "stage_8_9_49"
STAGE51_DIR = BACKEND_DIR / "research" / "stage_8_9_51"
sys.path.insert(0, str(STAGE49_DIR / "scripts"))

from whistle_discriminator import (
    apply_intervention_d,
    extract_envelope_modulation,
    extract_spectral_concentration
)
from run_evaluations import DualEncoderAcousticModel, CANDIDATE_B_CKPT, FROZEN_THRESHOLD

def compute_audio_forensics(y, sr=16000):
    """
    Computes fine-grained acoustic, spectral, vocal, and temporal features for a single audio recording.
    """
    n_samples = len(y)
    duration_sec = n_samples / sr
    
    # Peak & RMS
    peak = float(np.max(np.abs(y))) if n_samples > 0 else 0.0
    rms = float(np.sqrt(np.mean(y**2))) if n_samples > 0 else 0.0
    crest_factor = float(peak / (rms + 1e-9))
    crest_factor_db = 20.0 * np.log10(crest_factor + 1e-9)
    
    # Dynamic Range & Clipping
    sorted_abs = np.sort(np.abs(y))
    p95 = float(np.percentile(sorted_abs, 95)) if n_samples > 0 else 0.0
    p05 = float(np.percentile(sorted_abs, 5)) if n_samples > 0 else 0.0
    dyn_range_db = float(20.0 * np.log10((p95 + 1e-9) / (p05 + 1e-9)))
    clipping_ratio = float(np.mean(np.abs(y) >= 0.999))
    
    # Silence Ratio & Noise Floor
    # Silence: samples below -40 dB relative to peak or below 0.05 * RMS
    silence_thresh = max(1e-4, 0.05 * rms)
    silence_ratio = float(np.mean(np.abs(y) < silence_thresh))
    
    # Frame-based analysis (hop = 10 ms, win = 25 ms)
    hop_length = int(0.010 * sr)
    frame_length = int(0.025 * sr)
    if n_samples >= frame_length:
        frames = librosa.util.frame(y, frame_length=frame_length, hop_length=hop_length)
        frame_rms = np.sqrt(np.mean(frames**2, axis=0) + 1e-12)
        noise_floor_rms = float(np.percentile(frame_rms, 10))
        active_rms = float(np.percentile(frame_rms, 90))
        snr_db = float(20.0 * np.log10((active_rms + 1e-9) / (noise_floor_rms + 1e-9)))
    else:
        frame_rms = np.array([rms])
        noise_floor_rms = rms
        active_rms = rms
        snr_db = 0.0
        
    noise_floor_db = float(20.0 * np.log10(noise_floor_rms + 1e-9))
    
    # Spectral Features (FFT)
    fft_vals = np.abs(np.fft.rfft(y))
    freqs = np.fft.rfftfreq(n_samples, d=1.0/sr)
    power = fft_vals**2
    sum_power = np.sum(power) + 1e-12
    
    centroid = float(np.sum(freqs * power) / sum_power)
    bandwidth = float(np.sqrt(np.max([0.0, np.sum(((freqs - centroid)**2) * power) / sum_power])))
    
    # Spectral Rolloff (85%)
    cum_power = np.cumsum(power)
    rolloff_idx = np.searchsorted(cum_power, 0.85 * sum_power)
    spectral_rolloff = float(freqs[min(rolloff_idx, len(freqs)-1)])
    
    # Zero Crossing Rate
    zcr = float(np.mean(librosa.feature.zero_crossing_rate(y, frame_length=frame_length, hop_length=hop_length)))
    
    # Subband Energy Distributions
    low_mask = freqs < 1000.0
    mid_mask = (freqs >= 1000.0) & (freqs <= 4000.0)
    high_mask = freqs > 4000.0
    low_e_ratio = float(np.sum(power[low_mask]) / sum_power)
    mid_e_ratio = float(np.sum(power[mid_mask]) / sum_power)
    high_e_ratio = float(np.sum(power[high_mask]) / sum_power)
    
    # Vocal formant presence & whistle ratio
    spec_conc = extract_spectral_concentration(y, sr=sr)
    vocal_band_ratio = spec_conc["vocal_band_ratio"]
    whistle_band_ratio = spec_conc["whistle_band_ratio"]
    spectral_flatness = spec_conc["flatness"]
    
    # Pitch / F0 Estimation via YIN
    f0 = 0.0
    f0_valid = False
    hnr_db = 0.0
    try:
        f0_series = librosa.yin(y, fmin=150, fmax=1200, sr=sr, frame_length=frame_length, hop_length=hop_length)
        voiced = ~np.isnan(f0_series) & (f0_series > 150) & (f0_series < 1200)
        if np.sum(voiced) >= 3:
            f0 = float(np.median(f0_series[voiced]))
            f0_valid = True
            # HNR estimate on voiced segments
            # Autocorrelation peak ratio
            autocorr = signal.correlate(y, y, mode='full')
            mid = len(autocorr) // 2
            lag = int(sr / f0)
            if mid + lag < len(autocorr) and autocorr[mid] > 1e-12:
                peak_r = autocorr[mid + lag] / autocorr[mid]
                if 0.0 < peak_r < 1.0:
                    hnr_db = float(10.0 * np.log10(peak_r / (1.0 - peak_r + 1e-9)))
    except Exception:
        f0 = 0.0
        f0_valid = False
        
    # Temporal & Envelope Dynamics
    env = np.abs(signal.hilbert(y)) if n_samples > 50 else np.abs(y)
    env_mean = float(np.mean(env))
    env_std = float(np.std(env))
    env_cv = float(env_std / (env_mean + 1e-9))
    
    # Vocal Onset & Event Timing
    # Active region: where frame_rms >= 10% peak_frame_rms
    peak_frame_rms = float(np.max(frame_rms)) if len(frame_rms) > 0 else 0.0
    active_frames = np.where(frame_rms >= 0.10 * peak_frame_rms)[0]
    
    if len(active_frames) > 0:
        onset_frame = active_frames[0]
        offset_frame = active_frames[-1]
        peak_frame = np.argmax(frame_rms)
        
        onset_time_sec = float(onset_frame * hop_length / sr)
        peak_time_sec = float(peak_frame * hop_length / sr)
        vocal_event_dur_sec = float((offset_frame - onset_frame + 1) * hop_length / sr)
        attack_time_ms = float(max(0.0, (peak_time_sec - onset_time_sec) * 1000.0))
        
        # Decay time to 50% of peak
        decay_frames = np.where((np.arange(len(frame_rms)) >= peak_frame) & (frame_rms <= 0.50 * peak_frame_rms))[0]
        if len(decay_frames) > 0:
            decay_time_ms = float((decay_frames[0] - peak_frame) * hop_length / sr * 1000.0)
        else:
            decay_time_ms = float((len(frame_rms) - 1 - peak_frame) * hop_length / sr * 1000.0)
    else:
        onset_time_sec = 0.0
        peak_time_sec = 0.0
        vocal_event_dur_sec = duration_sec
        attack_time_ms = 0.0
        decay_time_ms = 0.0
        
    # Temporal Persistence: fraction of frames >= 20% peak RMS
    temporal_persistence = float(np.mean(frame_rms >= 0.20 * peak_frame_rms)) if peak_frame_rms > 0 else 0.0
    
    # Intermittent vs Continuous: count dips below 20% between onset and offset
    if len(active_frames) > 2:
        inner_frames = frame_rms[onset_frame:offset_frame+1]
        dips = np.where(inner_frames < 0.20 * peak_frame_rms)[0]
        is_intermittent = bool(len(dips) >= 3)
    else:
        is_intermittent = False
        
    # YAMNet & Model Window Framing
    # Standard YAMNet input window is 0.96 seconds (15360 samples at 16kHz), step 0.48 seconds
    model_window_sec = 0.96
    padding_ratio = float(max(0.0, model_window_sec - duration_sec) / model_window_sec)
    n_valid_frames = max(1, int(np.ceil(duration_sec / 0.48)))
    n_padded_frames = 1 if duration_sec < model_window_sec else 0
    event_center_sec = onset_time_sec + (vocal_event_dur_sec / 2.0)
    alignment_offset_ms = float((event_center_sec - (model_window_sec / 2.0)) * 1000.0)
    
    # Envelope Modulation (whistle trill extraction)
    mod = extract_envelope_modulation(y, sr=sr)
    
    return {
        "duration_sec": duration_sec,
        "vocal_event_dur_sec": vocal_event_dur_sec,
        "peak_amp": peak,
        "rms_amp": rms,
        "crest_factor": crest_factor,
        "crest_factor_db": crest_factor_db,
        "dyn_range_db": dyn_range_db,
        "clipping_ratio": clipping_ratio,
        "silence_ratio": silence_ratio,
        "snr_db": snr_db,
        "noise_floor_db": noise_floor_db,
        "spectral_centroid_hz": centroid,
        "spectral_bandwidth_hz": bandwidth,
        "spectral_rolloff_hz": spectral_rolloff,
        "zcr": zcr,
        "low_e_ratio": low_e_ratio,
        "mid_e_ratio": mid_e_ratio,
        "high_e_ratio": high_e_ratio,
        "vocal_band_ratio": vocal_band_ratio,
        "whistle_band_ratio": whistle_band_ratio,
        "spectral_flatness": spectral_flatness,
        "f0_hz": f0,
        "f0_valid": int(f0_valid),
        "hnr_db": hnr_db,
        "env_mean": env_mean,
        "env_std": env_std,
        "env_cv": env_cv,
        "onset_time_sec": onset_time_sec,
        "peak_time_sec": peak_time_sec,
        "attack_time_ms": attack_time_ms,
        "decay_time_ms": decay_time_ms,
        "temporal_persistence": temporal_persistence,
        "is_intermittent": int(is_intermittent),
        "padding_ratio": padding_ratio,
        "n_valid_frames": n_valid_frames,
        "n_padded_frames": n_padded_frames,
        "alignment_offset_ms": alignment_offset_ms,
        "trill_f_hz": mod["trill_f_hz"],
        "trill_power_ratio": mod["trill_power_ratio"],
        "trill_periodicity": mod["trill_periodicity"]
    }

def main():
    print("=" * 80)
    print("STAGE 8.9.51: WORKSTREAM A & B FORENSIC EXTRACTION")
    print("=" * 80)
    
    # Load independent evaluation predictions
    pred_path = STAGE49_DIR / "INDEPENDENT_EVALUATION_PREDICTIONS.csv"
    if not pred_path.exists():
        raise FileNotFoundError(f"Missing {pred_path}")
    preds_df = pd.read_csv(pred_path)
    print(f"Loaded {len(preds_df)} independent predictions.")
    
    # Load features npz
    feat_path = STAGE49_DIR / "features" / "independent_features.npz"
    feat_npz = np.load(feat_path, allow_pickle=True)
    file_id_to_idx = {fid: idx for idx, fid in enumerate(feat_npz["file_ids"])}
    
    # Load Candidate B model
    model = DualEncoderAcousticModel()
    state = torch.load(CANDIDATE_B_CKPT, map_location="cpu", weights_only=True)
    model.load_state_dict(state)
    model.eval()
    
    audio_dir = STAGE49_DIR / "audio" / "independent"
    
    # Filter authentic positives (N=160)
    positives_df = preds_df[preds_df["binary_label"] == 1].copy()
    print(f"Total authentic positives: {len(positives_df)}")
    fn_mask = (positives_df["candidate_b_pred"] == 0)
    print(f"  - False Negatives (FN): {int(np.sum(fn_mask))}")
    print(f"  - True Positives (TP):  {int(np.sum(~fn_mask))}")
    
    all_results = []
    
    for _, row in positives_df.iterrows():
        file_id = row["file_id"]
        wav_path = audio_dir / f"{file_id}.wav"
        if not wav_path.exists():
            raise FileNotFoundError(f"Audio file missing: {wav_path}")
            
        y, sr = sf.read(str(wav_path))
        if y.ndim > 1:
            y = np.mean(y, axis=1)
            
        # Audio forensics
        forensics = compute_audio_forensics(y, sr=sr)
        
        # Model features from npz
        idx = file_id_to_idx[file_id]
        x_sem = feat_npz["X_sem"][idx]
        x_acoust = feat_npz["X_acoust"][idx]
        mask_acoust = feat_npz["mask_acoust"][idx]
        x_subband = feat_npz["X_subband"][idx]
        
        # Forward pass for intermediate representations
        with torch.no_grad():
            t_sem = torch.from_numpy(x_sem).unsqueeze(0).float()
            t_acoust = torch.from_numpy(x_acoust).unsqueeze(0).float()
            t_mask = torch.from_numpy(mask_acoust).unsqueeze(0).float()
            logits, z_sem, z_acoust = model(t_sem, t_acoust, t_mask)
            logit_val = float(logits[0])
            prob_val = float(torch.sigmoid(logits)[0])
            z_sem_norm = float(torch.norm(z_sem[0], p=2))
            z_acoust_norm = float(torch.norm(z_acoust[0], p=2))
            
        rec = {
            "file_id": file_id,
            "target_category": row["target_category"],
            "acoustic_subtype": row["acoustic_subtype"],
            "source_group_id": row["source_group_id"],
            "binary_label": int(row["binary_label"]),
            "candidate_b_prob": float(row["candidate_b_prob"]),
            "candidate_b_pred": int(row["candidate_b_pred"]),
            "is_false_negative": int(row["candidate_b_pred"] == 0),
            "intervention_d_pred": int(row["intervention_d_pred"]),
            "intervention_d_audit_tag": row["intervention_d_audit_tag"],
            # Intermediate Model Activations
            "model_logit": logit_val,
            "recomputed_prob": prob_val,
            "z_sem_norm": z_sem_norm,
            "z_acoust_norm": z_acoust_norm,
            "sem_emb_mean": float(np.mean(x_sem)),
            "sem_emb_std": float(np.std(x_sem)),
            "sem_emb_l2": float(np.linalg.norm(x_sem)),
            "acoust_vocal_max": float(x_acoust[0]),
            "acoust_vocal_mean": float(x_acoust[1]),
            "acoust_crowd_max": float(x_acoust[2]),
            "acoust_crowd_mean": float(x_acoust[3]),
            "acoust_scream_max": float(x_acoust[4]),
            "acoust_scream_mean": float(x_acoust[5]),
            "subband_low_energy": float(x_subband[0]),
            "subband_mid_energy": float(x_subband[1]),
            "subband_high_energy": float(x_subband[5]),
            "subband_scream_ratio": float(x_subband[9]),
            **forensics
        }
        all_results.append(rec)
        
    df_all = pd.DataFrame(all_results)
    
    # Save all authentic positives forensics
    out_all_path = STAGE51_DIR / "results" / "ALL_AUTHENTIC_POSITIVES_FORENSICS.csv"
    df_all.to_csv(out_all_path, index=False)
    print(f"Saved all 160 positives forensics to: {out_all_path}")
    
    # Save 29 false negatives forensics
    df_fn = df_all[df_all["is_false_negative"] == 1].copy()
    out_fn_path = STAGE51_DIR / "results" / "FALSE_NEGATIVE_FORENSICS_DETAILED.csv"
    df_fn.to_csv(out_fn_path, index=False)
    print(f"Saved 29 false negatives forensics to: {out_fn_path}")
    
    # Build False Negative Taxonomy
    # Categories:
    # 1. Low-intensity or muffled vocalization
    # 2. Distant or reverberant scream
    # 3. Crowd-masked scream
    # 4. Low-SNR scream
    # 5. Short-duration or partially captured scream
    # 6. Unusual pitch or harmonic structure
    # 7. Strong background transient interference
    # 8. Window alignment or padding issue
    # 9. Possible annotation ambiguity
    # 10. Unknown or mixed cause
    
    taxonomy_rows = []
    for _, fn_row in df_fn.iterrows():
        fid = fn_row["file_id"]
        subtype = fn_row["acoustic_subtype"]
        prob = fn_row["candidate_b_prob"]
        rms = fn_row["rms_amp"]
        snr = fn_row["snr_db"]
        dur = fn_row["duration_sec"]
        pad = fn_row["padding_ratio"]
        f0_val = fn_row["f0_hz"]
        f0_v = bool(fn_row["f0_valid"])
        vocal_ratio = fn_row["vocal_band_ratio"]
        scream_max = fn_row["acoust_scream_max"]
        vocal_max = fn_row["acoust_vocal_max"]
        crowd_max = fn_row["acoust_crowd_max"]
        
        primary = ""
        secondaries = []
        evidence = []
        conf = "HIGH"
        adj_req = False
        
        # Classification heuristics grounded directly in acoustic measurements:
        if subtype == "low_intensity_muffled_scream":
            primary = "Low-intensity or muffled vocalization"
            evidence.append(f"Subtype: {subtype}; RMS={rms:.4f}; Centroid={fn_row['spectral_centroid_hz']:.1f}Hz")
            if snr < 12.0:
                secondaries.append("Low-SNR scream")
                evidence.append(f"Low SNR: {snr:.1f} dB")
            if pad > 0.3:
                secondaries.append("Window alignment or padding issue")
                evidence.append(f"Padding ratio: {pad:.2f}")
        elif subtype == "crowd_masked_scream":
            primary = "Crowd-masked scream"
            evidence.append(f"Subtype: {subtype}; Crowd YAMNet score={crowd_max:.3f}; SNR={snr:.1f}dB")
            if snr < 10.0:
                secondaries.append("Low-SNR scream")
                evidence.append(f"Acoustic masking: SNR={snr:.1f}dB")
            if rms < 0.05:
                secondaries.append("Low-intensity or muffled vocalization")
                evidence.append(f"Low RMS: {rms:.4f}")
        elif subtype == "sustained_scream":
            # Sustained scream misses: check if low SNR, low intensity, or atypical pitch/voicing
            if rms < 0.035:
                primary = "Low-intensity or muffled vocalization"
                evidence.append(f"Subtype: {subtype}; Very low RMS={rms:.4f}; Peak={fn_row['peak_amp']:.4f}")
                secondaries.append("Low-SNR scream")
                evidence.append(f"SNR={snr:.1f}dB")
            elif snr < 10.0:
                primary = "Low-SNR scream"
                evidence.append(f"Subtype: {subtype}; Degraded SNR={snr:.1f}dB with background interference")
                secondaries.append("Crowd-masked scream" if crowd_max > 0.3 else "Distant or reverberant scream")
            elif not f0_v or f0_val > 900:
                primary = "Unusual pitch or harmonic structure"
                evidence.append(f"Subtype: {subtype}; Non-standard pitch dynamics (F0 valid={f0_v}, F0={f0_val:.1f}Hz)")
                secondaries.append("Low-intensity or muffled vocalization")
            else:
                primary = "Unknown or mixed cause"
                evidence.append(f"Subtype: {subtype}; RMS={rms:.4f}, SNR={snr:.1f}dB; borderline prob={prob:.4f}")
                secondaries.append("Low-intensity or muffled vocalization")
                conf = "MEDIUM"
                adj_req = True
        elif subtype == "short_scream":
            # Short scream misses: check if padding / alignment dilution
            if pad > 0.25 or dur < 0.70:
                primary = "Window alignment or padding issue"
                evidence.append(f"Subtype: {subtype}; Short duration {dur:.2f}s diluted by YAMNet 960ms window (padding {pad:.1%})")
                if snr < 12.0:
                    secondaries.append("Low-SNR scream")
                    evidence.append(f"SNR={snr:.1f}dB")
            elif rms < 0.04:
                primary = "Low-intensity or muffled vocalization"
                evidence.append(f"Subtype: {subtype}; Low amplitude RMS={rms:.4f}")
                secondaries.append("Window alignment or padding issue")
            else:
                primary = "Short-duration or partially captured scream"
                evidence.append(f"Subtype: {subtype}; Event duration {dur:.2f}s with rapid attack/decay")
                secondaries.append("Window alignment or padding issue")
        else:
            primary = "Unknown or mixed cause"
            evidence.append(f"Subtype: {subtype}; Prob={prob:.4f}")
            conf = "MEDIUM"
            adj_req = True
            
        taxonomy_rows.append({
            "file_id": fid,
            "target_category": fn_row["target_category"],
            "acoustic_subtype": subtype,
            "source_group_id": fn_row["source_group_id"],
            "candidate_b_prob": prob,
            "primary_failure_mechanism": primary,
            "secondary_failure_mechanisms": "; ".join(secondaries) if secondaries else "None",
            "supporting_evidence": " | ".join(evidence),
            "confidence_level": conf,
            "human_adjudication_required": "YES" if adj_req else "NO",
            "rms_amplitude": rms,
            "snr_db": snr,
            "duration_sec": dur,
            "padding_ratio": pad,
            "f0_estimate_hz": f0_val if f0_v else "Unvoiced/Untracked",
            "vocal_formant_band_ratio": vocal_ratio,
            "yamnet_scream_frame_max": scream_max,
            "yamnet_vocal_frame_max": vocal_max,
            "yamnet_crowd_frame_max": crowd_max
        })
        
    tax_df = pd.DataFrame(taxonomy_rows)
    tax_out_path = STAGE51_DIR / "FALSE_NEGATIVE_TAXONOMY.csv"
    tax_df.to_csv(tax_out_path, index=False)
    print(f"Saved False Negative Taxonomy to: {tax_out_path}")
    print("\nTaxonomy Primary Mechanism Summary:")
    print(tax_df["primary_failure_mechanism"].value_counts())
    print("\nWorkstream A & B extraction complete!")

if __name__ == "__main__":
    main()

