"""
Stage 8.9.43: Phase 1.1 & 1.2 — Unified Positive-Class Dataset Audit & Acoustic Profiling
Audits all existing positive scream recordings (v4 splits N=438 + Stage 8.9.41 N=57 = 495 recordings)
Extracts 15 acoustic parameters and compiles POSITIVE_DATASET_AUDIT.csv.
"""
import os
import sys
import hashlib
import csv
from pathlib import Path
import numpy as np
import soundfile as sf
import librosa
import scipy.signal as signal

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE38_DIR = BACKEND_DIR / "research" / "stage_8_9_38"
STAGE41_DIR = BACKEND_DIR / "research" / "stage_8_9_41"
STAGE42_DIR = BACKEND_DIR / "research" / "stage_8_9_42"
STAGE43_DIR = BACKEND_DIR / "research" / "stage_8_9_43"

TARGET_SR = 16000

def compute_hashes(audio_path):
    # File SHA-256
    sha256 = hashlib.sha256(audio_path.read_bytes()).hexdigest()
    # PCM SHA-256 (normalized float32 PCM bytes)
    wf, sr = sf.read(str(audio_path), dtype="float32")
    if wf.ndim > 1:
        wf = np.mean(wf, axis=1)
    if sr != TARGET_SR:
        wf = librosa.resample(wf, orig_sr=sr, target_sr=TARGET_SR)
    pcm_sha256 = hashlib.sha256(wf.astype(np.float32).tobytes()).hexdigest()
    return sha256, pcm_sha256, wf

def extract_acoustic_features(wf, sr=TARGET_SR):
    dur = len(wf) / sr
    rms = float(np.sqrt(np.mean(wf**2)))
    peak = float(np.max(np.abs(wf)))
    dyn_range = 20.0 * np.log10((peak + 1e-9) / (rms + 1e-9))

    # Spectral features
    stft = np.abs(librosa.stft(y=wf, n_fft=1024, hop_length=256))
    cent = float(np.mean(librosa.feature.spectral_centroid(S=stft, sr=sr)))
    bw = float(np.mean(librosa.feature.spectral_bandwidth(S=stft, sr=sr)))
    rolloff = float(np.mean(librosa.feature.spectral_rolloff(S=stft, sr=sr, roll_percent=0.85)))
    zcr = float(np.mean(librosa.feature.zero_crossing_rate(y=wf)))

    # Spectral flux
    stft_norm = stft / (np.sum(stft, axis=0, keepdims=True) + 1e-9)
    if stft_norm.shape[1] > 1:
        flux = float(np.mean(np.sqrt(np.sum((stft_norm[:, 1:] - stft_norm[:, :-1])**2, axis=0))))
    else:
        flux = 0.0

    # F0 via Yin
    try:
        f0 = librosa.yin(wf, fmin=150, fmax=1500, sr=sr, frame_length=1024, hop_length=256)
        voiced = f0[~np.isnan(f0)]
        f0_mean = float(np.mean(voiced)) if len(voiced) > 0 else 0.0
    except Exception:
        f0_mean = 0.0

    # HNR (Harmonic-to-Noise Ratio estimation via autocorrelation)
    try:
        autocorr = signal.correlate(wf, wf, mode="full")
        autocorr = autocorr[len(autocorr)//2:]
        if len(autocorr) > int(sr / 150):
            r0 = autocorr[0]
            # Search peak between 150 Hz and 1500 Hz
            min_lag = int(sr / 1500)
            max_lag = int(sr / 150)
            r_peak = np.max(autocorr[min_lag:max_lag]) if max_lag < len(autocorr) else 0.0
            if r_peak > 0 and r0 > r_peak:
                hnr_db = float(10.0 * np.log10(r_peak / (r0 - r_peak + 1e-9)))
            else:
                hnr_db = -10.0
        else:
            hnr_db = 0.0
    except Exception:
        hnr_db = 0.0

    # Temporal Envelope: Attack time and Decay time
    hop_env = int(0.010 * sr) # 10ms
    win_env = int(0.025 * sr) # 25ms
    n_frames = max(1, (len(wf) - win_env) // hop_env + 1)
    env = np.array([np.sqrt(np.mean(wf[i*hop_env:i*hop_env+win_env]**2)) for i in range(n_frames)])
    peak_idx = int(np.argmax(env))
    peak_env = env[peak_idx]

    # Attack: time from 10% peak to peak
    thresh_10 = 0.10 * peak_env
    pre_peak = np.where(env[:peak_idx] <= thresh_10)[0]
    start_idx = pre_peak[-1] if len(pre_peak) > 0 else 0
    attack_ms = float((peak_idx - start_idx) * 10.0)

    # Decay: time from peak to 10% peak
    post_peak = np.where(env[peak_idx:] <= thresh_10)[0]
    end_idx = (peak_idx + post_peak[0]) if len(post_peak) > 0 else len(env) - 1
    decay_ms = float((end_idx - peak_idx) * 10.0)

    # Reverberation / RT60 estimate (T30 extrapolated from decay slope)
    if decay_ms > 50.0:
        rt60_est = float(min(decay_ms * 3.0 / 1000.0, 3.0))
    else:
        rt60_est = float(decay_ms * 2.0 / 1000.0)

    # Estimated SNR (Peak 200ms RMS vs 10th percentile background noise)
    noise_floor = float(np.percentile(env, 10)) + 1e-6
    peak_energy = float(peak_env) + 1e-6
    snr_est_db = float(20.0 * np.log10(peak_energy / noise_floor))

    return {
        "duration_seconds": round(dur, 4),
        "rms_energy": round(rms, 6),
        "peak_amplitude": round(peak, 6),
        "dynamic_range_db": round(dyn_range, 2),
        "spectral_centroid_hz": round(cent, 1),
        "spectral_bandwidth_hz": round(bw, 1),
        "spectral_rolloff_hz": round(rolloff, 1),
        "zero_crossing_rate": round(zcr, 4),
        "hnr_db": round(hnr_db, 2),
        "f0_mean_hz": round(f0_mean, 1),
        "spectral_flux": round(flux, 4),
        "attack_time_ms": round(attack_ms, 1),
        "decay_time_ms": round(decay_ms, 1),
        "estimated_rt60_s": round(rt60_est, 3),
        "estimated_snr_db": round(snr_est_db, 2)
    }

def main():
    print("=" * 80)
    print("STAGE 8.9.43: PHASE 1 — AUDITING EXISTING POSITIVE SCREAM DATASET")
    print("=" * 80)

    # 1. Load 37 missed scream IDs from Stage 8.9.42 False-Negative Audit
    fn_csv = STAGE42_DIR / "FALSE_NEGATIVE_FORENSIC_AUDIT.csv"
    missed_fids = set()
    if fn_csv.exists():
        with open(fn_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                missed_fids.add(r["file_id"])
    print(f"Loaded {len(missed_fids)} false-negative recording IDs from Stage 8.9.42.")

    # 2. Load v4 splits and dataset manifest
    v4_manifest_p = STAGE38_DIR / "manifests" / "dataset_manifest_v4.csv"
    v4_split_p = STAGE38_DIR / "manifests" / "research_split_v4.csv"

    v4_splits = {}
    with open(v4_split_p, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            v4_splits[r["file_id"]] = r["v4_research_split"]

    positive_records = []

    # 3. Process v4 positive recordings
    with open(v4_manifest_p, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r["binary_label"] != "scream":
                continue
            fid = r["file_id"]
            audio_path = Path(r["workspace_audio_path"])
            if not audio_path.exists():
                print(f"Warning: missing audio file: {audio_path}")
                continue

            sha256, pcm_sha256, wf = compute_hashes(audio_path)
            feats = extract_acoustic_features(wf)

            # Provenance determination
            is_synth = (r.get("is_synthesized", "0") == "1") or ("synth" in r.get("original_recording_id", "").lower())
            provenance = "SYNTHETIC" if is_synth else "AUTHENTIC_FIELD_RECORDING"
            partition = v4_splits.get(fid, "UNKNOWN")
            evaluated = "YES" if partition in ["v4_historical_test", "v4_reserved_expansion_test"] else "NO"

            rec = {
                "recording_id": fid,
                "source_dataset": r.get("source_dataset", "UNKNOWN"),
                "source_url": r.get("source_url", "UNKNOWN"),
                "original_uploader": r.get("creator", "UNKNOWN"),
                "license": r.get("license", "UNKNOWN"),
                "parent_recording_id": r.get("original_recording_id", fid),
                "excerpt_id": fid,
                "source_group_id": r.get("source_group_id", "UNKNOWN"),
                "original_sample_rate": int(r.get("sample_rate", 16000)),
                "channel_count": int(r.get("channels", 1)),
                "sha256": sha256,
                "pcm_sha256": pcm_sha256,
                "acoustic_subtype": r.get("acoustic_subtype", r.get("target_category", "scream")),
                "provenance": provenance,
                "existing_partition": partition,
                "previously_evaluated": evaluated,
                "stage_8_9_41_missed_cohort": "NO",
                **feats
            }
            positive_records.append(rec)

    print(f"Extracted features for {len(positive_records)} v4 positive screams.")

    # 4. Process Stage 8.9.41 positive recordings (N=57)
    s41_manifest_p = STAGE41_DIR / "manifests" / "stage_8_9_41_positive_manifest.csv"
    with open(s41_manifest_p, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            fid = r["file_id"]
            audio_path = REPO_ROOT / r["workspace_audio_path"]
            if not audio_path.exists():
                print(f"Warning: missing audio file: {audio_path}")
                continue

            sha256, pcm_sha256, wf = compute_hashes(audio_path)
            feats = extract_acoustic_features(wf)

            is_missed = "YES" if fid in missed_fids else "NO"

            rec = {
                "recording_id": fid,
                "source_dataset": r.get("source_dataset", "freesound_stage_8_9_41"),
                "source_url": r.get("source_url", "UNKNOWN"),
                "original_uploader": r.get("creator", "UNKNOWN"),
                "license": r.get("license", "UNKNOWN"),
                "parent_recording_id": r.get("original_recording_id", fid),
                "excerpt_id": fid,
                "source_group_id": r.get("source_group_id", "UNKNOWN"),
                "original_sample_rate": int(r.get("sample_rate", 16000)),
                "channel_count": int(r.get("channels", 1)),
                "sha256": sha256,
                "pcm_sha256": pcm_sha256,
                "acoustic_subtype": r.get("acoustic_subtype", "scream"),
                "provenance": "AUTHENTIC_FIELD_RECORDING",
                "existing_partition": "stage_8_9_41_independent_test",
                "previously_evaluated": "YES",
                "stage_8_9_41_missed_cohort": is_missed,
                **feats
            }
            positive_records.append(rec)

    print(f"Total positive recordings audited: {len(positive_records)}")

    # 5. Save to POSITIVE_DATASET_AUDIT.csv
    out_csv = STAGE43_DIR / "POSITIVE_DATASET_AUDIT.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = list(positive_records[0].keys())
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(positive_records)

    print(f"Successfully generated: {out_csv} ({len(positive_records)} rows)")

if __name__ == "__main__":
    main()

