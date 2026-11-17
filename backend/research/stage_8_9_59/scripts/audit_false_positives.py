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
            "rms_energy": 0.0,
            "peak_amp": 0.0,
            "snr_db_estimate": 0.0,
            "spectral_centroid_hz": 0.0,
            "spectral_flatness": 0.0
        }
    
    data, sr = sf.read(audio_path)
    if data.ndim > 1:
        data = data.mean(axis=1)
        
    rms = float(np.sqrt(np.mean(data**2)))
    peak = float(np.max(np.abs(data)))
    
    # SNR estimate
    frame_len = int(0.05 * sr)
    hop = frame_len // 2
    if len(data) >= frame_len:
        num_frames = (len(data) - frame_len) // hop + 1
        frame_energies = [np.mean(data[i*hop : i*hop + frame_len]**2) for i in range(num_frames)]
        min_e = np.percentile(frame_energies, 10)
        max_e = np.percentile(frame_energies, 95)
        snr_est = float(10.0 * np.log10(max(max_e, 1e-9) / max(min_e, 1e-9)))
    else:
        snr_est = 20.0
        
    # Spectral properties
    fft = np.abs(np.fft.rfft(data))
    freqs = np.fft.rfftfreq(len(data), 1.0 / sr)
    if np.sum(fft) > 1e-8:
        centroid = float(np.sum(freqs * fft) / np.sum(fft))
    else:
        centroid = 0.0
        
    # Spectral flatness (geometric mean / arithmetic mean)
    fft_sq = fft**2 + 1e-12
    geom_mean = np.exp(np.mean(np.log(fft_sq)))
    arith_mean = np.mean(fft_sq)
    flatness = float(geom_mean / arith_mean) if arith_mean > 0 else 0.0
        
    return {
        "exists": True,
        "sr": sr,
        "rms_energy": round(rms, 6),
        "peak_amp": round(peak, 6),
        "snr_db_estimate": round(snr_est, 2),
        "spectral_centroid_hz": round(centroid, 1),
        "spectral_flatness": round(flatness, 6)
    }

def main():
    print("Executing Phase C: False-Positive Forensics & Shouted-Speech Audit...")
    
    manifest_p = os.path.join(STAGE54_DIR, "dataset", "partition_manifest_verified.csv")
    df_man = pd.read_csv(manifest_p)
    
    pred_p = os.path.join(STAGE58_DIR, "prediction_comparison.csv")
    df_pred = pd.read_csv(pred_p)
    
    # Identify all false positives on validation set (ground_truth_label == 0 and c5_prediction == 1)
    fp_df_pred = df_pred[(df_pred["ground_truth_label"] == 0) & (df_pred["c5_prediction"] == 1)].copy()
    print(f"Total false positives identified under C5: {len(fp_df_pred)}")
    
    # Merge with full manifest
    merged = pd.merge(fp_df_pred, df_man, on="expansion_file_id", suffixes=("", "_manifest"))
    
    fp_records = []
    for idx, r in merged.iterrows():
        audio_rel = r["workspace_audio_path"]
        audio_abs = os.path.join(REPO_ROOT, audio_rel)
        audio_props = analyze_audio_file(audio_abs)
        
        prob = float(r["c5_probability"])
        thresh = 0.6800
        cat = str(r["target_category"])
        src_grp = str(r["source_group_id"])
        
        # Classify root cause pattern
        patterns = []
        if cat == "shouting_and_speech":
            if "2208" in r["expansion_file_id"] or "2208" in src_grp:
                patterns.append("High-effort theatrical shouting session (Session 2208)")
            elif "3439" in r["expansion_file_id"] or "3439" in src_grp:
                patterns.append("Aggressive sustained vocal shouting with phonatory strain (Session 3439)")
            elif "1687" in r["expansion_file_id"]:
                patterns.append("Loud sports vocal projection (Session 1687)")
            else:
                patterns.append("Vocal tract tension / elevated F0 during shouting")
        elif cat == "infant_crying":
            patterns.append("High fundamental frequency and acoustic roughness overlapping scream bands (Infant crying)")
        elif cat == "crowd_chant_cheering":
            patterns.append("High-pitched harmonic cheering with synchronized vocal bursts")
        else:
            patterns.append("Acoustic energy concentration in 2000-4000 Hz band")
            
        # Distinguish annotation / ambiguity
        ambiguity_type = "Actual False Positive (Model Discrimination Limitation)"
        if "343952" in r["expansion_file_id"] or "343965" in r["expansion_file_id"]:
            ambiguity_type = "Acoustically Ambiguous (High-effort shriek/shout borderline vocalization)"
            
        rec = {
            "expansion_file_id": r["expansion_file_id"],
            "original_recording_id": r["original_recording_id"],
            "source_group_id": src_grp,
            "target_category": cat,
            "subtype_tags": r["subtype_tags"],
            "duration_seconds": float(r["duration_seconds"]),
            "ground_truth_label": 0,
            "c5_probability": prob,
            "classification_threshold": thresh,
            "c5_prediction": 1,
            "probability_excess": round(prob - thresh, 6),
            "creator": r["creator"],
            "license": r["license"],
            "audio_file_exists": audio_props["exists"],
            "rms_energy": audio_props["rms_energy"],
            "peak_amplitude": audio_props["peak_amp"],
            "snr_db_estimate": audio_props["snr_db_estimate"],
            "spectral_centroid_hz": audio_props["spectral_centroid_hz"],
            "spectral_flatness": audio_props["spectral_flatness"],
            "root_cause_pattern": "; ".join(patterns),
            "annotation_ambiguity_status": ambiguity_type
        }
        fp_records.append(rec)
        
    df_fp_out = pd.DataFrame(fp_records)
    fp_csv = os.path.join(STAGE_DIR, "false_positive_recordings.csv")
    df_fp_out.to_csv(fp_csv, index=False)
    print(f"Saved {len(df_fp_out)} false positives to {fp_csv}")
    
    # Shouted speech deep-dive
    shout_fps = df_fp_out[df_fp_out["target_category"] == "shouting_and_speech"]
    print(f"\nShouted speech false positives: {len(shout_fps)}")
    print("Source group distribution among shouted speech FPs:")
    print(shout_fps["source_group_id"].value_counts())
    
    # Save shouted speech breakdown
    shout_summary = {
        "total_shouted_speech_validation": 88,
        "shouted_speech_fp_count": len(shout_fps),
        "shouted_speech_fpr": round(len(shout_fps) / 88.0 * 100, 2),
        "source_groups_represented": shout_fps["source_group_id"].nunique(),
        "source_group_counts": shout_fps["source_group_id"].value_counts().to_dict(),
        "mean_duration": round(float(shout_fps["duration_seconds"].mean()), 2),
        "mean_probability": round(float(shout_fps["c5_probability"].mean()), 4)
    }
    with open(os.path.join(STAGE_DIR, "shouted_speech_summary.json"), "w") as f:
        json.dump(shout_summary, f, indent=2)
    print(f"Saved shouted speech summary: {shout_summary}")

if __name__ == "__main__":
    main()

