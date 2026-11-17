"""
Stage 8.9.23 Investigation E: Comprehensive Audit of SHR and Pitch Tracking Implementations
Evaluates:
1. SHR mathematical definition (numerator/denominator, dB conversion)
2. Decibel conversion scaling (10 * log10 vs 20 * log10)
3. Pitch failure representation (missing vs arbitrary numeric values)
4. Mains hum (50-60 Hz) contamination & local baseline noise subtraction
5. Digital clipping, dropouts, and near-silence handling
6. Physical validity conditions for HNR and SHR
"""

import numpy as np
import scipy.signal as signal
from pathlib import Path
import json

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = WORKSPACE_DIR.parent.parent
STAGE22_DIR = BACKEND_DIR / "research" / "stage_8_9_22"

import sys
sys.path.insert(0, str(STAGE22_DIR))

from src.shr_formula_validation import SHRFormulaValidator
from src.signal_conditioned_pitch import SignalConditionedPitchTracker

def run_shr_pitch_audit():
    sr = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)

    validator = SHRFormulaValidator(sample_rate=sr)
    pitch_tracker = SignalConditionedPitchTracker(sample_rate=sr)

    audit_records = {}

    # 1. Pure Modal Phonation (300 Hz + 4 harmonics, zero subharmonics)
    s1 = (
        1.0 * np.sin(2 * np.pi * 300 * t) +
        0.5 * np.sin(2 * np.pi * 600 * t) +
        0.25 * np.sin(2 * np.pi * 900 * t) +
        0.125 * np.sin(2 * np.pi * 1200 * t)
    )
    leg_s1 = validator.legacy_shr(s1, 300.0)
    rob_s1 = validator.robust_instantaneous_shr(s1)
    audit_records["pure_modal_tone"] = {
        "description": "Pure modal vowel, F0=300Hz, 4 harmonics",
        "legacy_shr_db": leg_s1[1],
        "robust_shr_db": rob_s1["shr_db"],
        "confidence": rob_s1["shr_confidence"],
        "biphonic_fraction": rob_s1["biphonic_fraction"],
        "expected": "SHR <= -30 dB, high confidence"
    }

    # 2. Period-Doubled Biphonation (300 Hz + strong F0/2 = 150 Hz)
    s2 = (
        1.0 * np.sin(2 * np.pi * 300 * t) +
        0.8 * np.sin(2 * np.pi * 150 * t) +  # F0/2
        0.5 * np.sin(2 * np.pi * 600 * t) +
        0.4 * np.sin(2 * np.pi * 450 * t)    # 3F0/2
    )
    leg_s2 = validator.legacy_shr(s2, 300.0)
    rob_s2 = validator.robust_instantaneous_shr(s2)
    audit_records["period_doubled_biphonic"] = {
        "description": "Period-doubled distress biphonation, F0=300Hz + F0/2=150Hz",
        "legacy_shr_db": leg_s2[1],
        "robust_shr_db": rob_s2["shr_db"],
        "confidence": rob_s2["shr_confidence"],
        "biphonic_fraction": rob_s2["biphonic_fraction"],
        "expected": "SHR >= -6 dB, high confidence"
    }

    # 3. Modal Shouting with 60 Hz Electrical Ground Loop
    s3 = (
        1.0 * np.sin(2 * np.pi * 180 * t) +   # F0 = 180 Hz
        0.5 * np.sin(2 * np.pi * 360 * t) +   # 2F0
        0.4 * np.sin(2 * np.pi * 60 * t)      # 60 Hz ground hum (coincides with F0/3)
    )
    leg_s3 = validator.legacy_shr(s3, 180.0)
    rob_s3 = validator.robust_instantaneous_shr(s3)
    audit_records["shout_with_60hz_hum"] = {
        "description": "Modal shouting F0=180Hz + 60Hz mains hum (coinciding with F0/3)",
        "legacy_shr_db": leg_s3[1],
        "robust_shr_db": rob_s3["shr_db"],
        "confidence": rob_s3["shr_confidence"],
        "biphonic_fraction": rob_s3["biphonic_fraction"],
        "expected": "Local baseline subtraction rejects hum as non-vocal; robust SHR distinguishes from true bifurcation"
    }

    # 4. Digital Clipping (Square wave saturation)
    s4 = np.clip(10.0 * np.sin(2 * np.pi * 300 * t), -0.99, 0.99)
    res_s4_pitch = pitch_tracker.analyze_audio(s4)
    audit_records["clipped_audio"] = {
        "description": "Severely clipped square saturation (> 15 dB overdriven)",
        "high_energy_vocal_pitch_failure": res_s4_pitch["high_energy_vocal_pitch_failure"],
        "pitch_confidence": res_s4_pitch["vocal_confidence"],
        "clipping_ratio": res_s4_pitch["clipping_ratio"],
        "expected": "Clipping detected separately, not confused with chaotic vocal folds"
    }

    # 5. Near-Silence / Low Ambient Noise
    s5 = np.random.normal(0, 0.001, int(sr * duration))
    res_s5_pitch = pitch_tracker.analyze_audio(s5)
    audit_records["ambient_silence"] = {
        "description": "Low ambient silence, RMS < 0.005",
        "high_energy_vocal_pitch_failure": res_s5_pitch["high_energy_vocal_pitch_failure"],
        "pitch_confidence": res_s5_pitch["vocal_confidence"],
        "eligible_frames": res_s5_pitch["eligible_vocal_he_frames"],
        "expected": "No eligible frames -> returns 0.0 with 0.0 confidence (UNAVAILABLE)"
    }

    print("SHR and Pitch Implementation Audit Results:")
    print(json.dumps(audit_records, indent=2))
    return audit_records

if __name__ == "__main__":
    run_shr_pitch_audit()
