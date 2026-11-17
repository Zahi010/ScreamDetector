#!/usr/bin/env python3
"""
STAGE 8.9.64 — Track E: False-Positive Forensic Inventory & Contrastive Hard-Negative Curation
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import csv
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import scipy.io.wavfile as wav
import scipy.signal as signal

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE60_DIR = BACKEND_DIR / "research" / "stage_8_9_60"
STAGE61_DIR = BACKEND_DIR / "research" / "stage_8_9_61"
STAGE63_DIR = BACKEND_DIR / "research" / "stage_8_9_63"
STAGE64_DIR = BACKEND_DIR / "research" / "stage_8_9_64"

def compute_hnr_and_spectral_props(audio_path: Path):
    """Compute HNR, spectral flatness, and spectral flux for a WAV file."""
    sr, aud = wav.read(audio_path)
    if aud.ndim > 1:
        aud = np.mean(aud, axis=1)
    if aud.dtype == np.int16:
        aud = aud.astype(np.float32) / 32768.0
    elif aud.dtype == np.int32:
        aud = aud.astype(np.float32) / 2147483648.0
    else:
        aud = aud.astype(np.float32)

    # High-pass filter
    if len(aud) < int(sr * 0.025):
        return 0.0, 0.0, 0.0
    
    b, a = signal.butter(2, 70.0 / (sr / 2.0), btype='high')
    filtered = signal.filtfilt(b, a, aud)

    # FFT-based Autocorrelation
    min_lag = int(sr / 2000.0)
    max_lag = int(sr / 80.0)
    autocorr = signal.correlate(filtered, filtered, mode='full', method='fft')
    autocorr = autocorr[len(autocorr)//2:]
    r0 = autocorr[0]

    if r0 <= 1e-9 or len(autocorr) <= max_lag:
        hnr_db = 0.0
    else:
        norm_autocorr = autocorr / r0
        lag_range = norm_autocorr[min_lag:max_lag]
        r_max = float(np.max(lag_range))
        if r_max <= 0.01:
            hnr_db = -20.0
        elif r_max >= 0.999:
            hnr_db = 30.0
        else:
            hnr_db = float(np.clip(10.0 * np.log10(r_max / (1.0 - r_max + 1e-9)), -25.0, 35.0))

    # Spectral Flatness
    f, pxx = signal.periodogram(aud, fs=sr)
    pxx = pxx + 1e-12
    flatness = float(np.exp(np.mean(np.log(pxx))) / np.mean(pxx))

    # Spectral Flux
    f_stft, t_stft, sxx = signal.spectrogram(aud, fs=sr, nperseg=400, noverlap=200)
    if sxx.shape[1] >= 2:
        flux = float(np.mean(np.sqrt(np.sum(np.diff(sxx, axis=1)**2, axis=0))))
    else:
        flux = 0.0

    return round(hnr_db, 2), round(flatness, 5), round(flux, 4)

def main():
    print("=" * 80)
    print("STAGE 8.9.64 — TRACK E: FALSE-POSITIVE FORENSICS & CONTRASTIVE HARD-NEGATIVE MINING")
    print("=" * 80)

    # 1. Load sealed cohort to ensure strict isolation
    sealed_csv = STAGE61_DIR / "sealed_cohort_predictions.csv"
    sealed_df = pd.read_csv(sealed_csv)
    sealed_rec_ids = set(sealed_df["recording_id"].unique())
    print(f"Loaded {len(sealed_rec_ids)} sealed cohort recording IDs for quarantine validation.")

    # 2. Forensic audit of the 25 False Positives from Dual-Resolution Baseline
    repro_df = pd.read_csv(STAGE64_DIR / "dual_resolution_reproduction.csv")
    dev_df = pd.read_csv(STAGE63_DIR / "stage_63_development_manifest.csv")
    dev_map = {r["recording_id"]: r for _, r in dev_df.iterrows()}

    # Filter to false positives: ground truth 0, predicted 1
    fp_df = repro_df[(repro_df["binary_label"] == 0) & (repro_df["predicted_label"] == 1)].copy()
    print(f"Identified {len(fp_df)} false-positive recordings from dual-resolution baseline evaluation.")

    # Acoustic Taxonomy Mapping
    taxonomy_rules = {
        "169005": ("whistle_pure_tone", "Ultra high pitch acoustic dog whistle"),
        "109827": ("friction_squeak", "Plastic tube friction squeak transient"),
        "109830": ("friction_squeak", "Plastic tube friction squeak transient"),
        "109831": ("friction_squeak", "Plastic tube friction squeak transient"),
        "118979": ("chimes_bells_metallic", "Windchimes metallic resonance"),
        "162880": ("shouted_speech_vocal", "Infant crying / child vocalization"),
        "175842": ("vehicle_horn_siren", "Car horn acoustic blast"),
        "186933": ("whistle_pure_tone", "Single short rocket whistle burst"),
        "196156": ("shouted_speech_vocal", "Sobbing and heavy breathing outcries"),
        "235667": ("friction_squeak", "Rubber wheel squeak transient loop"),
        "24731":  ("friction_squeak", "Short friction squeak transient"),
        "323723": ("friction_squeak", "Distant chair creak transient"),
        "335107": ("environmental_transient", "Weak clapping and crowd applause transients"),
        "350438": ("shouted_speech_vocal", "Young children chorus shouting/singing"),
        "350452": ("shouted_speech_vocal", "Young children group singing/shouting"),
        "36160":  ("chimes_bells_metallic", "Rally bells metallic percussion"),
        "371853": ("vehicle_horn_siren", "Classic vehicle horn acoustic blast"),
        "375627": ("chimes_bells_metallic", "Windchimes metallic resonance"),
        "380941": ("environmental_transient", "Wind in bushes acoustic turbulence"),
        "50405":  ("chimes_bells_metallic", "Windchimes metallic resonance"),
        "50744":  ("chimes_bells_metallic", "Electric guitar distorted harmonic break"),
        "66586":  ("vehicle_horn_siren", "Car horn acoustic blast remix"),
        "s60_rec_0332": ("shouted_speech_vocal", "NIGENS victim gasping and non-scream vocal outcry"),
        "s60_rec_0555": ("whistle_pure_tone", "Stage 49 whistle tone sample"),
        "s60_rec_0556": ("whistle_pure_tone", "Stage 49 whistle tone sample")
    }

    forensic_inventory = []
    for _, row in fp_df.iterrows():
        rec_id = row["recording_id"]
        meta = dev_map.get(rec_id, {})
        audio_rel = meta.get("workspace_audio_path", "")
        audio_path = REPO_ROOT / audio_rel

        # Match against taxonomy rules
        matched_class = "other_acoustic_transient"
        root_cause = "Transient acoustic energy triggering short branch gating"
        for key, (tax_class, cause) in taxonomy_rules.items():
            if key in rec_id or key in audio_rel:
                matched_class = tax_class
                root_cause = cause
                break

        # Compute physical acoustics
        hnr_db, flatness, flux = compute_hnr_and_spectral_props(audio_path)

        forensic_inventory.append({
            "recording_id": rec_id,
            "source_group_id": row["source_group_id"],
            "dataset_name": meta.get("dataset_name", "Unknown"),
            "subcategory": row["subcategory"],
            "acoustic_error_class": matched_class,
            "duration_seconds": round(float(row["duration_seconds"]), 3),
            "predicted_probability": round(float(row["predicted_probability"]), 4),
            "gating_weight_short": round(float(row["gating_weight_short"]), 4),
            "hnr_db": hnr_db,
            "spectral_flatness": flatness,
            "spectral_flux": flux,
            "root_cause_analysis": root_cause,
            "quarantine_sealed_check": "PASS_UNEXPOSED" if rec_id not in sealed_rec_ids else "FAIL_LEAKED"
        })

    fp_inv_df = pd.DataFrame(forensic_inventory)
    fp_inv_path = STAGE64_DIR / "false_positive_forensic_inventory.csv"
    fp_inv_df.to_csv(fp_inv_path, index=False)
    print(f"Emitted false positive forensic inventory to {fp_inv_path}")

    # Taxonomy counts
    tax_counts = fp_inv_df["acoustic_error_class"].value_counts()
    print("\nFalse Positive Breakdown by Acoustic Error Class:")
    for cls_name, cnt in tax_counts.items():
        print(f"  {cls_name:<26}: {cnt:>2} ({cnt/len(fp_inv_df)*100:.1f}%)")

    # 3. Build Contrastive Hard-Negative Development Pool
    # We mine difficult non-targets from dev partition (stage8_8 approved, stage49 whistle, etc.)
    # ensuring zero overlap with sealed cohort and strictly unexposed source groups.
    print("\nCurating Contrastive Hard-Negative Development Pool...")
    
    # Pool 1: Stage 63 dev negative recordings (117 recordings)
    # Pool 2: Additional unconsumed non-screams from development pools
    all_dev_negs = dev_df[dev_df["binary_label"] == 0].copy()
    
    contrastive_records = []
    for _, r in all_dev_negs.iterrows():
        rec_id = r["recording_id"]
        if rec_id in sealed_rec_ids:
            continue
        
        audio_path = REPO_ROOT / r["workspace_audio_path"]
        if not audio_path.exists():
            continue

        hnr_db, flatness, flux = compute_hnr_and_spectral_props(audio_path)
        
        # Determine error class
        matched_class = "environmental_noise"
        for key, (tax_class, _) in taxonomy_rules.items():
            if key in rec_id or key in r["workspace_audio_path"]:
                matched_class = tax_class
                break
        
        contrastive_records.append({
            "recording_id": rec_id,
            "source_group_id": r["source_group_id"],
            "dataset_name": r["dataset_name"],
            "subcategory": r["subcategory"],
            "acoustic_error_class": matched_class,
            "duration_seconds": r["duration_seconds"],
            "license": r["license"],
            "hnr_db": hnr_db,
            "spectral_flatness": flatness,
            "spectral_flux": flux,
            "hard_negative_weight": 2.5 if matched_class in ["whistle_pure_tone", "shouted_speech_vocal", "friction_squeak"] else 1.0,
            "sealed_cohort_overlap": False
        })

    contrastive_df = pd.DataFrame(contrastive_records)
    contrastive_path = STAGE64_DIR / "contrastive_hard_negative_metrics.csv"
    contrastive_df.to_csv(contrastive_path, index=False)
    print(f"Emitted {len(contrastive_df)} contrastive hard-negative records to {contrastive_path}")

    # Verify zero leakage
    leaks = [r["recording_id"] for r in contrastive_records if r["recording_id"] in sealed_rec_ids]
    assert len(leaks) == 0, f"FATAL: Sealed cohort leakage detected: {leaks}"
    print("VERIFICATION: Zero sealed-cohort overlap confirmed across all contrastive negatives.")

if __name__ == "__main__":
    main()

