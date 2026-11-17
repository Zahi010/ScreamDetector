import os
import json
import numpy as np
import pandas as pd
import soundfile as sf

# MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
STAGE_DIR = os.path.join(REPO_ROOT, "backend", "research", "stage_8_9_59")
STAGE54_DIR = os.path.join(REPO_ROOT, "backend", "research", "stage_8_9_54")
STAGE58_DIR = os.path.join(REPO_ROOT, "backend", "research", "stage_8_9_58")

def analyze_audio_file(audio_path):
    if not os.path.exists(audio_path):
        return {
            "exists": False,
            "sr": 0,
            "channels": 0,
            "rms_energy": 0.0,
            "peak_amp": 0.0,
            "snr_db_estimate": 0.0,
            "spectral_centroid_hz": 0.0
        }
    
    data, sr = sf.read(audio_path)
    if data.ndim > 1:
        data = data.mean(axis=1)
        
    rms = float(np.sqrt(np.mean(data**2)))
    peak = float(np.max(np.abs(data)))
    
    # Estimate background noise floor from lowest 10% frames
    frame_len = int(0.05 * sr) # 50 ms
    hop = frame_len // 2
    if len(data) >= frame_len:
        num_frames = (len(data) - frame_len) // hop + 1
        frame_energies = [np.mean(data[i*hop : i*hop + frame_len]**2) for i in range(num_frames)]
        min_e = np.percentile(frame_energies, 10)
        max_e = np.percentile(frame_energies, 95)
        snr_est = float(10.0 * np.log10(max(max_e, 1e-9) / max(min_e, 1e-9)))
    else:
        snr_est = 20.0
        
    # Spectral centroid estimate
    fft = np.abs(np.fft.rfft(data))
    freqs = np.fft.rfftfreq(len(data), 1.0 / sr)
    if np.sum(fft) > 1e-8:
        centroid = float(np.sum(freqs * fft) / np.sum(fft))
    else:
        centroid = 0.0
        
    return {
        "exists": True,
        "sr": sr,
        "channels": 1,
        "rms_energy": round(rms, 6),
        "peak_amp": round(peak, 6),
        "snr_db_estimate": round(snr_est, 2),
        "spectral_centroid_hz": round(centroid, 1)
    }

def main():
    print("Executing Phase B: Frozen Candidate E1 False-Negative Forensics...")
    
    manifest_p = os.path.join(STAGE54_DIR, "dataset", "partition_manifest_verified.csv")
    df_man = pd.read_csv(manifest_p)
    
    pred_p = os.path.join(STAGE58_DIR, "prediction_comparison.csv")
    df_pred = pd.read_csv(pred_p)
    
    # Identify the 16 false negatives (ground_truth_label == 1 and c5_prediction == 0)
    fn_df_pred = df_pred[(df_pred["ground_truth_label"] == 1) & (df_pred["c5_prediction"] == 0)].copy()
    print(f"Total false negatives identified: {len(fn_df_pred)}")
    
    # Merge with full manifest
    merged = pd.merge(fn_df_pred, df_man, on="expansion_file_id", suffixes=("", "_manifest"))
    
    fn_records = []
    for idx, r in merged.iterrows():
        audio_rel = r["workspace_audio_path"]
        audio_abs = os.path.join(REPO_ROOT, audio_rel)
        audio_props = analyze_audio_file(audio_abs)
        
        dur = float(r["duration_seconds"])
        if dur < 0.5:
            dur_class = "Ultra-Short (<0.5s)"
        elif dur < 1.0:
            dur_class = "Short (0.5-1.0s)"
        else:
            dur_class = "Sustained (>=1.0s)"
            
        prob = float(r["c5_probability"])
        thresh = 0.6800
        
        # Determine directly observed acoustic characteristics
        obs_acoustics = []
        if audio_props["rms_energy"] < 0.03:
            obs_acoustics.append("Low Intensity / Low RMS (<0.03)")
        if audio_props["snr_db_estimate"] < 12.0:
            obs_acoustics.append("Low SNR / High Background Masking (<12 dB)")
        if audio_props["spectral_centroid_hz"] < 1500.0:
            obs_acoustics.append("Low Spectral Centroid (<1500 Hz, Muffled/Gasp)")
        elif audio_props["spectral_centroid_hz"] > 4000.0:
            obs_acoustics.append("High Spectral Centroid (>4000 Hz, Thin/Sibilant)")
            
        # Metadata-derived characteristics
        meta_chars = []
        src_ds = str(r["source_dataset"])
        if "synth" in src_ds or "synth" in r["expansion_file_id"]:
            meta_chars.append("Synthetic Scream with Added Noise / SNR Offset")
        if "fsd50k" in src_ds or "fsd50k" in r["expansion_file_id"]:
            meta_chars.append("FSD50K In-the-Wild Crowd / Foley Recording")
        if "nigens" in src_ds or "nigens" in r["expansion_file_id"]:
            meta_chars.append("NIGENS Vocalization (Acoustically ambiguous: gasp/surprise)")
        if "openslr" in src_ds or "openslr" in r["expansion_file_id"]:
            meta_chars.append("OpenSLR Emotional Speech / Vocal Effort")
            
        subtype = str(r["subtype_tags"])
        if pd.notna(subtype) and subtype != "":
            meta_chars.append(f"Subtype: {subtype}")
            
        # Hypothesis requiring testing
        hypotheses = []
        if "nigens" in src_ds:
            hypotheses.append("Vocal effort level below scream threshold (perceptual gasp rather than full phonatory scream)")
        if "synth" in src_ds and audio_props["snr_db_estimate"] < 10.0:
            hypotheses.append("Harmonic scream structure obscured by diffuse crowd/pink noise masking")
        if dur >= 1.0 and audio_props["rms_energy"] < 0.04:
            hypotheses.append("Extended vocal duration exhibits non-stationary decay below detection threshold")
            
        rec = {
            "expansion_file_id": r["expansion_file_id"],
            "original_recording_id": r["original_recording_id"],
            "source_group_id": r["source_group_id"],
            "source_dataset": r["source_dataset"],
            "duration_seconds": dur,
            "duration_category": dur_class,
            "target_category": r["target_category"],
            "subtype_tags": r["subtype_tags"],
            "ground_truth_label": 1,
            "c5_probability": prob,
            "classification_threshold": thresh,
            "c5_prediction": 0,
            "prediction_margin": round(thresh - prob, 6),
            "creator": r["creator"],
            "license": r["license"],
            "audio_file_exists": audio_props["exists"],
            "rms_energy": audio_props["rms_energy"],
            "peak_amplitude": audio_props["peak_amp"],
            "snr_db_estimate": audio_props["snr_db_estimate"],
            "spectral_centroid_hz": audio_props["spectral_centroid_hz"],
            "observed_acoustic_characteristics": "; ".join(obs_acoustics) if obs_acoustics else "Standard Intensity/Centroid",
            "metadata_derived_characteristics": "; ".join(meta_chars) if meta_chars else "None",
            "hypotheses_for_testing": "; ".join(hypotheses) if hypotheses else "Acoustic boundary case near decision threshold"
        }
        fn_records.append(rec)
        
    df_fn_out = pd.DataFrame(fn_records)
    fn_csv = os.path.join(STAGE_DIR, "false_negative_recordings.csv")
    df_fn_out.to_csv(fn_csv, index=False)
    print(f"Saved {len(df_fn_out)} false negatives to {fn_csv}")
    
    # Sustained scream analysis
    # Total sustained in validation: 60. Detected: 46. FN: 14.
    sustained_fns = df_fn_out[df_fn_out["duration_seconds"] >= 1.0]
    short_fns = df_fn_out[df_fn_out["duration_seconds"] < 1.0]
    print(f"False Negatives by duration: Sustained: {len(sustained_fns)}/60 (Recall: {(60-len(sustained_fns))/60*100:.2f}%), Short: {len(short_fns)}/39 (Recall: {(39-len(short_fns))/39*100:.2f}%)")
    
if __name__ == "__main__":
    main()

