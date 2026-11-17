"""
Stage 8.9.52: Phase B — Candidate E Reproducibility and Leakage Audit Script
Loads saved checkpoint `backend/research/stage_8_9_51/models/research_exp_candidate.pt`,
executes pure inference on the validation split (N=120) without retraining,
recomputes all validation metrics, verifies threshold theta=0.4000,
checks source-group isolation and leakage between Dev and Val.
Emits:
- stage_8_9_52/candidate_e/candidate_e_validation_predictions.csv
- Prints detailed verification diagnostics
"""
import sys
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import soundfile as sf
import torch
import torch.nn as nn

REPO_ROOT = Path(r"c:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE49_DIR = BACKEND_DIR / "research" / "stage_8_9_49"
STAGE51_DIR = BACKEND_DIR / "research" / "stage_8_9_51"
STAGE52_DIR = BACKEND_DIR / "research" / "stage_8_9_52"

sys.path.insert(0, str(STAGE51_DIR / "scripts"))
from run_controlled_experiments import ResearchDualHeadClassifier
from run_evaluations import wilson_ci

def compute_pcm_hash(audio_array):
    audio_16 = np.clip(audio_array, -1.0, 1.0)
    audio_pcm = (audio_16 * 32767.0).astype(np.int16)
    return hashlib.sha256(audio_pcm.tobytes()).hexdigest()

def main():
    print("=" * 80)
    print("STAGE 8.9.52: PHASE B — CANDIDATE E REPRODUCIBILITY & LEAKAGE AUDIT")
    print("=" * 80)
    
    cand_e_ckpt = STAGE51_DIR / "models" / "research_exp_candidate.pt"
    if not cand_e_ckpt.exists():
        raise FileNotFoundError(f"Missing Candidate E checkpoint: {cand_e_ckpt}")
        
    with open(cand_e_ckpt, "rb") as f:
        ckpt_hash = hashlib.sha256(f.read()).hexdigest()
    print(f"Candidate E Checkpoint Path: {cand_e_ckpt}")
    print(f"Candidate E SHA-256 Digest:   {ckpt_hash}")
    
    # 1. Load validation data
    val_feat_path = STAGE49_DIR / "features" / "val_features.npz"
    val_npz = np.load(val_feat_path, allow_pickle=True)
    
    val_fids = val_npz["file_ids"]
    val_subtypes = val_npz["subtypes"]
    val_categories = val_npz["categories"]
    val_sgs = val_npz["source_groups"]
    val_labels = val_npz["labels"]
    
    val_sem = torch.from_numpy(val_npz["X_sem"]).float()
    val_ac = torch.from_numpy(val_npz["X_acoust"]).float()
    val_m = torch.from_numpy(val_npz["mask_acoust"]).float()
    val_sb = torch.from_numpy(val_npz["X_subband"]).float()
    
    print(f"Loaded {len(val_fids)} validation clips from: {val_feat_path.name}")
    
    # 2. Instantiate and load model without retraining
    model = ResearchDualHeadClassifier(sem_dim=1024, acoust_dim=6, subband_dim=11)
    state = torch.load(cand_e_ckpt, map_location="cpu", weights_only=True)
    model.load_state_dict(state)
    model.eval()
    
    # 3. Pure deterministic inference
    with torch.no_grad():
        logits = model(val_sem, val_ac, val_m, val_sb).numpy()
        probs = 1.0 / (1.0 + np.exp(-logits))
        
    threshold = 0.4000
    preds = (probs >= threshold).astype(int)
    
    # 4. Compute metrics
    pos_mask = (val_labels == 1)
    neg_mask = (val_labels == 0)
    
    n_pos = int(np.sum(pos_mask))
    n_neg = int(np.sum(neg_mask))
    
    tp = int(np.sum(preds[pos_mask] == 1))
    fn = int(np.sum(preds[pos_mask] == 0))
    tn = int(np.sum(preds[neg_mask] == 0))
    fp = int(np.sum(preds[neg_mask] == 1))
    
    recall = (tp / n_pos) * 100.0
    hn_fpr = (fp / n_neg) * 100.0
    prec = (tp / (tp + fp)) * 100.0 if (tp + fp) > 0 else 0.0
    f1 = (2 * prec * recall) / (prec + recall) if (prec + recall) > 0 else 0.0
    
    l_rec, u_rec = wilson_ci(tp, n_pos)
    l_fpr, u_fpr = wilson_ci(fp, n_neg)
    
    print("\n--- CANDIDATE E VALIDATION REPRODUCTION RESULTS ---")
    print(f"Operating Threshold:             theta = {threshold:.4f}")
    print(f"True Positives (TP):             {tp} / {n_pos}")
    print(f"False Negatives (FN):            {fn} / {n_pos}")
    print(f"True Negatives (TN):             {tn} / {n_neg}")
    print(f"False Positives (FP):            {fp} / {n_neg}")
    print(f"Validation Positive Recall:      {recall:.2f}% (95% CI: [{l_rec:.2f}%, {u_rec:.2f}%])")
    print(f"Validation Hard-Negative FPR:    {hn_fpr:.2f}% (95% CI: [{l_fpr:.2f}%, {u_fpr:.2f}%])")
    print(f"Validation Precision:            {prec:.2f}%")
    print(f"Validation F1 Score:             {f1:.2f}%")
    
    # 5. Emit validation predictions CSV
    pred_rows = []
    for i in range(len(val_fids)):
        pred_rows.append({
            "file_id": val_fids[i],
            "source_group_id": val_sgs[i],
            "target_category": val_categories[i],
            "acoustic_subtype": val_subtypes[i],
            "ground_truth_label": int(val_labels[i]),
            "raw_logit": float(logits[i]),
            "calibrated_prob": float(probs[i]),
            "threshold": threshold,
            "prediction": int(preds[i]),
            "is_correct": int(preds[i] == val_labels[i])
        })
        
    df_preds = pd.DataFrame(pred_rows)
    cand_e_pred_csv = STAGE52_DIR / "candidate_e" / "candidate_e_validation_predictions.csv"
    df_preds.to_csv(cand_e_pred_csv, index=False)
    print(f"Saved Candidate E validation predictions to: {cand_e_pred_csv}")
    
    # 6. Leakage Audit
    print("\n--- LEAKAGE AUDIT: Dev (Training) vs Val (Validation) ---")
    dev_feat_path = STAGE49_DIR / "features" / "dev_features.npz"
    dev_npz = np.load(dev_feat_path, allow_pickle=True)
    
    dev_fids = set(dev_npz["file_ids"])
    val_fids_set = set(val_fids)
    
    dev_sgs = set(dev_npz["source_groups"])
    val_sgs_set = set(val_sgs)
    
    # File overlaps
    file_overlap = dev_fids.intersection(val_fids_set)
    print(f"File ID Overlaps:                {len(file_overlap)}")
    
    # Source group overlaps
    sg_overlap = dev_sgs.intersection(val_sgs_set)
    print(f"Source-Group Overlaps:           {len(sg_overlap)}")
    
    # Audio hash overlaps
    dev_audio_dir = STAGE49_DIR / "audio" / "dev"
    val_audio_dir = STAGE49_DIR / "audio" / "val"
    
    dev_file_hashes = {}
    dev_pcm_hashes = {}
    for fid in dev_fids:
        p = dev_audio_dir / f"{fid}.wav"
        with open(p, "rb") as fh:
            h = hashlib.sha256(fh.read()).hexdigest()
        y, _ = sf.read(str(p))
        pcm_h = compute_pcm_hash(y)
        dev_file_hashes[h] = fid
        dev_pcm_hashes[pcm_h] = fid
        
    val_file_hashes = {}
    val_pcm_hashes = {}
    for fid in val_fids_set:
        p = val_audio_dir / f"{fid}.wav"
        with open(p, "rb") as fh:
            h = hashlib.sha256(fh.read()).hexdigest()
        y, _ = sf.read(str(p))
        pcm_h = compute_pcm_hash(y)
        val_file_hashes[h] = fid
        val_pcm_hashes[pcm_h] = fid
        
    hash_overlap = set(dev_file_hashes.keys()).intersection(set(val_file_hashes.keys()))
    pcm_overlap = set(dev_pcm_hashes.keys()).intersection(set(val_pcm_hashes.keys()))
    
    print(f"Exact File SHA-256 Overlaps:     {len(hash_overlap)}")
    print(f"Decoded PCM SHA-256 Overlaps:    {len(pcm_overlap)}")
    
    # Check if test data was accessed
    indep_feat_path = STAGE49_DIR / "features" / "independent_features.npz"
    indep_npz = np.load(indep_feat_path, allow_pickle=True)
    indep_fids = set(indep_npz["file_ids"])
    indep_sgs = set(indep_npz["source_groups"])
    
    print(f"Dev vs Independent File Overlap: {len(dev_fids.intersection(indep_fids))}")
    print(f"Dev vs Independent SG Overlap:   {len(dev_sgs.intersection(indep_sgs))}")
    print(f"Val vs Independent File Overlap: {len(val_fids_set.intersection(indep_fids))}")
    print(f"Val vs Independent SG Overlap:   {len(val_sgs_set.intersection(indep_sgs))}")
    
    if len(file_overlap) == 0 and len(sg_overlap) == 0 and len(hash_overlap) == 0 and len(pcm_overlap) == 0:
        print("\nLEAKAGE AUDIT DETERMINATION: PASS (Zero Source-Group, File, or PCM Leakage)")
    else:
        print("\nLEAKAGE AUDIT DETERMINATION: FAIL (Leakage Detected!)")

if __name__ == "__main__":
    main()

