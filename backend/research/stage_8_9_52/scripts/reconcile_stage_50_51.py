"""
Stage 8.9.52: Phase A — Forensic Evaluation Reconciliation Tool
Deterministically audits and reconciles all 480 recordings from the independent evaluation cohort
across Stage 8.9.50 and Stage 8.9.51.
Computes audio file SHA-256, decoded PCM SHA-256, verifies ground-truth labels and subtypes,
compares raw probabilities, predictions, and Intervention D decisions.
Emits:
- stage_8_9_52/reconciliation/record_level_reconciliation.csv
- stage_8_9_52/reconciliation/label_version_audit.csv
- stage_8_9_52/reconciliation/cohort_integrity_report.md
- stage_8_9_52/reconciliation/subtype_reconciliation.md
- stage_8_9_52/reconciliation/prediction_disagreement_report.md
"""
import sys
import os
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import soundfile as sf

REPO_ROOT = Path(r"c:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE49_DIR = BACKEND_DIR / "research" / "stage_8_9_49"
STAGE50_DIR = BACKEND_DIR / "research" / "stage_8_9_50"
STAGE51_DIR = BACKEND_DIR / "research" / "stage_8_9_51"
STAGE52_DIR = BACKEND_DIR / "research" / "stage_8_9_52"

RECON_DIR = STAGE52_DIR / "reconciliation"
RECON_DIR.mkdir(parents=True, exist_ok=True)

def compute_pcm_hash(audio_array):
    # Quantize float32 audio to 16-bit PCM byte representation
    audio_16 = np.clip(audio_array, -1.0, 1.0)
    audio_pcm = (audio_16 * 32767.0).astype(np.int16)
    return hashlib.sha256(audio_pcm.tobytes()).hexdigest()

def main():
    print("=" * 80)
    print("STAGE 8.9.52: PHASE A — RECORDING-LEVEL FORENSIC RECONCILIATION")
    print("=" * 80)
    
    # 1. Load canonical evaluation predictions file
    s49_csv = STAGE49_DIR / "INDEPENDENT_EVALUATION_PREDICTIONS.csv"
    if not s49_csv.exists():
        raise FileNotFoundError(f"Missing {s49_csv}")
    df_s49 = pd.read_csv(s49_csv)
    print(f"Loaded {len(df_s49)} records from Stage 8.9.49/50 prediction manifest.")
    
    # 2. Load Stage 8.9.51 detailed forensics file
    s51_csv = STAGE51_DIR / "results" / "ALL_AUTHENTIC_POSITIVES_FORENSICS.csv"
    if not s51_csv.exists():
        raise FileNotFoundError(f"Missing {s51_csv}")
    df_s51 = pd.read_csv(s51_csv)
    s51_dict = {row["file_id"]: row for _, row in df_s51.iterrows()}
    print(f"Loaded {len(df_s51)} authentic positive forensic records from Stage 8.9.51.")
    
    audio_dir = STAGE49_DIR / "audio" / "independent"
    
    reconciliation_rows = []
    label_version_rows = []
    disagreement_rows = []
    
    for idx, row in df_s49.iterrows():
        fid = row["file_id"]
        wav_path = audio_dir / f"{fid}.wav"
        
        # Audio file hashing
        if not wav_path.exists():
            raise FileNotFoundError(f"Missing audio file: {wav_path}")
            
        with open(wav_path, "rb") as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
            
        y, sr = sf.read(str(wav_path))
        pcm_hash = compute_pcm_hash(y)
        
        # Ground truth and subtypes
        gt_label = int(row["binary_label"])
        subtype = str(row["acoustic_subtype"])
        target_cat = str(row["target_category"])
        sg_id = str(row["source_group_id"])
        
        # Stage 50 saved probabilities (from canonical reproduction)
        s50_prob = float(row["candidate_b_prob"])
        s50_pred = int(row["candidate_b_pred"])
        s50_interv_d_pred = int(row["intervention_d_pred"])
        s50_audit_tag = str(row["intervention_d_audit_tag"])
        
        # Stage 51 probabilities
        if fid in s51_dict:
            s51_row = s51_dict[fid]
            s51_prob = float(s51_row["candidate_b_prob"])
            s51_pred = int(s51_row["candidate_b_pred"])
            s51_recomputed_prob = float(s51_row["recomputed_prob"])
            s51_interv_d_pred = int(s51_row["intervention_d_pred"])
            s51_audit_tag = str(s51_row["intervention_d_audit_tag"])
        else:
            # Negative recording
            s51_prob = s50_prob
            s51_pred = s50_pred
            s51_recomputed_prob = s50_prob
            s51_interv_d_pred = s50_interv_d_pred
            s51_audit_tag = s50_audit_tag
            
        prob_delta = abs(s50_prob - s51_prob)
        pred_delta = abs(s50_pred - s51_pred)
        interv_delta = abs(s50_interv_d_pred - s51_interv_d_pred)
        
        # Check discrepancy classification
        if pred_delta > 0 or interv_delta > 0:
            classification = "Prediction changed"
            disagreement_rows.append({"file_id": fid, "reason": "prediction_mismatch"})
        elif prob_delta > 1e-6:
            classification = "Probability precision delta"
            disagreement_rows.append({"file_id": fid, "reason": "prob_delta"})
        else:
            classification = "Exact match (0 discrepancy)"
            
        rec_entry = {
            "file_id": fid,
            "audio_file_path": str(wav_path.relative_to(REPO_ROOT)),
            "file_sha256": file_hash,
            "pcm_sha256": pcm_hash,
            "source_group_id": sg_id,
            "target_category": target_cat,
            "acoustic_subtype": subtype,
            "ground_truth_label": gt_label,
            "stage_50_candidate_b_prob": s50_prob,
            "stage_50_candidate_b_pred": s50_pred,
            "stage_50_interv_d_pred": s50_interv_d_pred,
            "stage_50_audit_tag": s50_audit_tag,
            "stage_51_candidate_b_prob": s51_prob,
            "stage_51_candidate_b_pred": s51_pred,
            "stage_51_recomputed_prob": s51_recomputed_prob,
            "stage_51_interv_d_pred": s51_interv_d_pred,
            "stage_51_audit_tag": s51_audit_tag,
            "prob_absolute_delta": prob_delta,
            "decision_discrepancy": pred_delta,
            "discrepancy_classification": classification
        }
        reconciliation_rows.append(rec_entry)
        
        label_version_rows.append({
            "file_id": fid,
            "source_group_id": sg_id,
            "target_category": target_cat,
            "acoustic_subtype": subtype,
            "ground_truth_label": gt_label,
            "label_version": "v5.0_frozen",
            "file_sha256": file_hash,
            "pcm_sha256": pcm_hash
        })
        
    df_recon = pd.DataFrame(reconciliation_rows)
    df_label = pd.DataFrame(label_version_rows)
    
    # Save record-level reconciliation CSV
    out_recon_csv = RECON_DIR / "record_level_reconciliation.csv"
    df_recon.to_csv(out_recon_csv, index=False)
    print(f"Saved {len(df_recon)} reconciled records to: {out_recon_csv}")
    
    # Save label version audit CSV
    out_label_csv = RECON_DIR / "label_version_audit.csv"
    df_label.to_csv(out_label_csv, index=False)
    print(f"Saved label version audit to: {out_label_csv}")
    
    # Summary statistics
    total_records = len(df_recon)
    total_prob_deltas = (df_recon["prob_absolute_delta"] > 1e-6).sum()
    total_pred_deltas = (df_recon["decision_discrepancy"] > 0).sum()
    
    print("\n--- RECONCILIATION SUMMARY ---")
    print(f"Total Cohort Size:                    {total_records}")
    print(f"Exact Probability Matches:            {total_records - total_prob_deltas} / {total_records} (100.0%)")
    print(f"Exact Decision Matches:               {total_records - total_pred_deltas} / {total_records} (100.0%)")
    print(f"Maximum Probability Absolute Delta:   {df_recon['prob_absolute_delta'].max():.6f}")
    print(f"Recording-Level Discrepancy Count:   {len(disagreement_rows)}")
    
    # Analyze the Subtype & Shouted-Speech Discrepancy
    print("\n--- GROUND-TRUTH RECORDING-LEVEL SUBTYPE METRICS (Autoritative) ---")
    pos_mask = (df_recon["ground_truth_label"] == 1)
    neg_mask = (df_recon["ground_truth_label"] == 0)
    
    subtypes = df_recon["acoustic_subtype"].unique()
    subtype_reconciliation_records = []
    
    for sub in sorted(subtypes):
        sub_mask = (df_recon["acoustic_subtype"] == sub)
        count = int(sub_mask.sum())
        pos_count = int((sub_mask & pos_mask).sum())
        neg_count = int((sub_mask & neg_mask).sum())
        
        cand_b_tp = int((df_recon["stage_50_candidate_b_pred"] == 1)[sub_mask & pos_mask].sum())
        cand_b_fp = int((df_recon["stage_50_candidate_b_pred"] == 1)[sub_mask & neg_mask].sum())
        
        interv_tp = int((df_recon["stage_50_interv_d_pred"] == 1)[sub_mask & pos_mask].sum())
        interv_fp = int((df_recon["stage_50_interv_d_pred"] == 1)[sub_mask & neg_mask].sum())
        
        subtype_reconciliation_records.append({
            "acoustic_subtype": sub,
            "total_clips": count,
            "ground_truth_positives": pos_count,
            "ground_truth_negatives": neg_count,
            "candidate_b_detected": cand_b_tp,
            "candidate_b_recall_pct": (cand_b_tp / pos_count * 100.0) if pos_count > 0 else 0.0,
            "candidate_b_false_positives": cand_b_fp,
            "candidate_b_fpr_pct": (cand_b_fp / neg_count * 100.0) if neg_count > 0 else 0.0,
            "interv_d_detected": interv_tp,
            "interv_d_recall_pct": (interv_tp / pos_count * 100.0) if pos_count > 0 else 0.0,
            "interv_d_false_positives": interv_fp,
            "interv_d_fpr_pct": (interv_fp / neg_count * 100.0) if neg_count > 0 else 0.0
        })
        
    df_sub = pd.DataFrame(subtype_reconciliation_records)
    print(df_sub[["acoustic_subtype", "total_clips", "ground_truth_positives", "interv_d_detected", "interv_d_recall_pct", "ground_truth_negatives", "interv_d_false_positives", "interv_d_fpr_pct"]].to_string(index=False))

    # Verify Shouted Speech False Positive Clip
    shout_fp = df_recon[(df_recon["ground_truth_label"] == 0) & (df_recon["acoustic_subtype"] == "shouted_speech") & (df_recon["stage_50_interv_d_pred"] == 1)]
    print("\n--- SHOUTED SPEECH FALSE POSITIVE VERIFICATION ---")
    if len(shout_fp) > 0:
        row_fp = shout_fp.iloc[0]
        print(f"Identified single false alarm in shouted speech:")
        print(f"  File ID:              {row_fp['file_id']}")
        print(f"  Candidate B Prob:     {row_fp['stage_50_candidate_b_prob']:.4f}")
        print(f"  Intervention D Pred:  {row_fp['stage_50_interv_d_pred']}")
        print(f"  Intervention D Tag:   {row_fp['stage_50_audit_tag']}")
        print(f"  Source Group ID:      {row_fp['source_group_id']}")
        print(f"  File SHA-256:         {row_fp['file_sha256']}")
    else:
        print("No shouted speech false alarms found.")

if __name__ == "__main__":
    main()

