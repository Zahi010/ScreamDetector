"""
Stage 8.9.50: Historical Whistle & Siren False-Positive Revalidation Script
Re-evaluates the four Stage 8.9.48 Candidate B referee whistle false alarms and the emergency siren false alarm.
Reports acoustic characteristics, filter activation status, and classification correctness.
Emits: backend/research/stage_8_9_50/WHISTLE_FORENSIC_REVALIDATION.csv
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import soundfile as sf

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE47_DIR = BACKEND_DIR / "research" / "stage_8_9_47"
STAGE49_DIR = BACKEND_DIR / "research" / "stage_8_9_49"
STAGE50_DIR = BACKEND_DIR / "research" / "stage_8_9_50"

sys.path.insert(0, str(STAGE49_DIR / "scripts"))
from whistle_discriminator import (
    apply_intervention_d,
    extract_spectral_concentration,
    extract_envelope_modulation
)

HISTORICAL_CLIPS = [
    {
        "canonical_file_id": "s47_indep_neg_0197",
        "prompt_alias": "hn_indep_0088",
        "target_category": "whistles_and_squeaks",
        "acoustic_subtype": "referee_whistle",
        "source_group_id": "s47_sg_neg_080",
        "evidence_tier": "Historical Forensic Cohort (Stage 8.9.47/48)"
    },
    {
        "canonical_file_id": "s47_indep_neg_0199",
        "prompt_alias": "hn_indep_0102",
        "target_category": "whistles_and_squeaks",
        "acoustic_subtype": "referee_whistle",
        "source_group_id": "s47_sg_neg_082",
        "evidence_tier": "Historical Forensic Cohort (Stage 8.9.47/48)"
    },
    {
        "canonical_file_id": "s47_indep_neg_0200",
        "prompt_alias": "hn_indep_0119",
        "target_category": "whistles_and_squeaks",
        "acoustic_subtype": "referee_whistle",
        "source_group_id": "s47_sg_neg_083",
        "evidence_tier": "Historical Forensic Cohort (Stage 8.9.47/48)"
    },
    {
        "canonical_file_id": "s47_indep_neg_0229",
        "prompt_alias": "hn_indep_0144",
        "target_category": "whistles_and_squeaks",
        "acoustic_subtype": "referee_whistle",
        "source_group_id": "s47_sg_neg_076",
        "evidence_tier": "Historical Forensic Cohort (Stage 8.9.47/48)"
    },
    {
        "canonical_file_id": "s47_indep_neg_0244",
        "prompt_alias": "hn_indep_0142",
        "target_category": "sfx_sirens_fireworks",
        "acoustic_subtype": "emergency_siren",
        "source_group_id": "s47_sg_neg_100",
        "evidence_tier": "Historical Forensic Cohort (Stage 8.9.47/48)"
    },
]

def main():
    print("=" * 80)
    print("STAGE 8.9.50: WHISTLE & SIREN FALSE-POSITIVE REVALIDATION")
    print("=" * 80)
    
    preds_47 = pd.read_csv(STAGE47_DIR / "INDEPENDENT_PREDICTIONS.csv")
    rows = []
    
    for item in HISTORICAL_CLIPS:
        fid = item["canonical_file_id"]
        alias = item["prompt_alias"]
        cat = item["target_category"]
        st = item["acoustic_subtype"]
        sg = item["source_group_id"]
        tier = item["evidence_tier"]
        
        audio_p = STAGE47_DIR / "audio" / "independent" / f"{fid}.wav"
        y, sr = sf.read(str(audio_p))
        if y.ndim > 1:
            y = np.mean(y, axis=1)
            
        dur = len(y) / sr
        p_row = preds_47[preds_47["file_id"] == fid].iloc[0]
        p_raw = float(p_row["cand_b_config_b_mask_v6_prob"])
        b_pred = int(p_row["cand_b_config_b_mask_v6_pred"])
        
        spec = extract_spectral_concentration(y, sr)
        mod = extract_envelope_modulation(y, sr)
        
        # Estimate carrier f0
        fft_v = np.abs(np.fft.rfft(y))
        freqs = np.fft.rfftfreq(len(y), d=1.0/sr)
        peak_idx = np.argmax(fft_v)
        f0 = float(freqs[peak_idx])
        
        d_pred, d_tag, diag = apply_intervention_d(y, p_raw, b_pred, sr=sr)
        
        # Correctness: ground truth is 0 (negative)
        correct_b = (b_pred == 0)
        correct_d = (d_pred == 0)
        rejection_activated = (b_pred == 1 and d_pred == 0)
        
        row_dict = {
            "canonical_file_id": fid,
            "prompt_specified_alias": alias,
            "evidence_tier": tier,
            "source_group_id": sg,
            "target_category": cat,
            "acoustic_subtype": st,
            "duration_seconds": round(dur, 4),
            "candidate_b_probability": round(p_raw, 4),
            "candidate_b_binary_decision": b_pred,
            "intervention_d_binary_decision": d_pred,
            "intervention_d_audit_tag": d_tag,
            "rejection_layer_activated": rejection_activated,
            "carrier_frequency_hz": round(f0, 1),
            "spectral_bandwidth_hz": round(spec["bandwidth"], 1),
            "whistle_band_energy_ratio": round(spec["whistle_band_ratio"], 4),
            "vocal_band_energy_ratio": round(spec["vocal_band_ratio"], 4),
            "temporal_modulation_frequency_hz": round(mod["trill_f_hz"], 1),
            "temporal_envelope_periodicity": round(mod["trill_periodicity"], 3),
            "candidate_b_correct": correct_b,
            "intervention_d_correct": correct_d,
            "forensic_status": "CORRECTED_BY_FILTER" if rejection_activated else ("ALREADY_CORRECT" if correct_d else "FALSE_ALARM")
        }
        rows.append(row_dict)
        print(f"Validated {fid} ({alias}): Cand B Pred={b_pred} -> Interv D Pred={d_pred} ({d_tag}) | Correct={correct_d}")
        
    out_df = pd.DataFrame(rows)
    out_path = STAGE50_DIR / "WHISTLE_FORENSIC_REVALIDATION.csv"
    out_df.to_csv(out_path, index=False)
    print(f"\nSaved revalidation forensics to: {out_path}")

if __name__ == "__main__":
    main()

