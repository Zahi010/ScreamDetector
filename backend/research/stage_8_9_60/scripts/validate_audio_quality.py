import os
import json
import numpy as np
import pandas as pd
import soundfile as sf

# MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
STAGE_DIR = os.path.join(REPO_ROOT, "backend", "research", "stage_8_9_60")

def compute_audio_quality(audio_path):
    if not os.path.exists(audio_path):
        return {
            "file_exists": False,
            "sample_rate": 0,
            "channels": 0,
            "duration_sec": 0.0,
            "rms_energy": 0.0,
            "peak_amplitude": 0.0,
            "clipping_ratio": 0.0,
            "silence_ratio": 0.0,
            "snr_db": "NOT RELIABLY MEASURABLE",
            "quality_grade": "CORRUPT_OR_MISSING"
        }
        
    try:
        data, sr = sf.read(audio_path)
        if data.ndim > 1:
            data = data.mean(axis=1)
            
        dur = float(len(data) / sr)
        rms = float(np.sqrt(np.mean(data**2)))
        peak = float(np.max(np.abs(data)))
        
        # Clipping ratio (|x| >= 0.999)
        clip_count = int(np.sum(np.abs(data) >= 0.999))
        clip_ratio = float(clip_count / max(len(data), 1))
        
        # Silence ratio (frames of 50ms with RMS < 0.001)
        frame_len = int(0.05 * sr)
        hop = frame_len // 2
        if len(data) >= frame_len:
            n_frames = (len(data) - frame_len) // hop + 1
            frame_energies = [np.sqrt(np.mean(data[i*hop : i*hop + frame_len]**2)) for i in range(n_frames)]
            silence_frames = sum(1 for e in frame_energies if e < 0.001)
            silence_ratio = float(silence_frames / n_frames)
            
            # SNR calculation protocol
            min_e = np.percentile(frame_energies, 10)
            max_e = np.percentile(frame_energies, 95)
            if min_e > 1e-6 and max_e > min_e:
                snr_val = round(float(20.0 * np.log10(max_e / min_e)), 2)
            else:
                snr_val = "NOT RELIABLY MEASURABLE"
        else:
            silence_ratio = 0.0
            snr_val = "NOT RELIABLY MEASURABLE"
            
        # Quality grading
        if clip_ratio > 0.05:
            grade = "HEAVY_CLIPPING"
        elif clip_ratio > 0.005:
            grade = "MODERATE_CLIPPING"
        elif silence_ratio > 0.80:
            grade = "EXCESSIVE_SILENCE"
        elif rms < 0.005:
            grade = "LOW_AMPLITUDE"
        else:
            grade = "VALID_CLEAN_AUDIO"
            
        return {
            "file_exists": True,
            "sample_rate": sr,
            "channels": 1,
            "duration_sec": round(dur, 3),
            "rms_energy": round(rms, 6),
            "peak_amplitude": round(peak, 6),
            "clipping_ratio": round(clip_ratio, 6),
            "silence_ratio": round(silence_ratio, 4),
            "snr_db": snr_val,
            "quality_grade": grade
        }
    except Exception as e:
        return {
            "file_exists": False,
            "sample_rate": 0,
            "channels": 0,
            "duration_sec": 0.0,
            "rms_energy": 0.0,
            "peak_amplitude": 0.0,
            "clipping_ratio": 0.0,
            "silence_ratio": 0.0,
            "snr_db": "NOT RELIABLY MEASURABLE",
            "quality_grade": f"DECODE_ERROR ({str(e)})"
        }

def main():
    print("Executing Phase G: Audio Quality Validation & SNR Measurement...")
    manifest_p = os.path.join(STAGE_DIR, "acquisition_manifest.csv")
    if not os.path.exists(manifest_p):
        print("[INFO] acquisition_manifest.csv not found. Running standalone demonstration.")
        return
        
    df_acq = pd.read_csv(manifest_p)
    quality_rows = []
    
    for idx, r in df_acq.iterrows():
        audio_abs = os.path.join(REPO_ROOT, r["workspace_audio_path"])
        metrics = compute_audio_quality(audio_abs)
        metrics["recording_id"] = r["recording_id"]
        metrics["target_category"] = r["target_category"]
        metrics["source_group_id"] = r["source_group_id"]
        quality_rows.append(metrics)
        
    df_qual = pd.DataFrame(quality_rows)
    out_csv = os.path.join(STAGE_DIR, "audio_quality_metrics.csv")
    df_qual.to_csv(out_csv, index=False)
    print(f"Saved audio quality metrics to {out_csv} ({len(df_qual)} recordings)")
    print("\nQuality Grade Breakdown:")
    print(df_qual["quality_grade"].value_counts())

if __name__ == "__main__":
    main()

