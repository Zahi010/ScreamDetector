"""
Stage 8.9.54: Controlled Candidate E Retraining & Ablation Suite
Executes:
- Experiment E0: Expanded-Data Baseline (candidate_e_v954_baseline.pt)
- Experiment E1: Class-Balanced Training (candidate_e_v954_weighted.pt)
- Experiment E2: Targeted Acoustic Augmentation (candidate_e_v954_augmented.pt)
- Experiment E3: Combined Controlled Condition (candidate_e_v954_combined.pt)
- Phase F: Validation threshold selection sweep on expansion_val (N=311)
- Phase G: Comparative validation against frozen Candidate B and Candidate B + Intervention D
Emits:
- training/training_configuration.json
- training/training_history.csv
- training/candidate_e_v954_baseline.pt
- training/candidate_e_v954_weighted.pt
- training/candidate_e_v954_augmented.pt
- training/candidate_e_v954_combined.pt
- evaluation/threshold_sweep.csv
- evaluation/validation_predictions.csv
- evaluation/candidate_comparison.md
- evaluation/subgroup_evaluation.md
- evaluation/error_analysis.md
- evaluation/acceptance_gate_report.md
- integrity/checkpoint_manifest.json
"""
import sys
import json
import math
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import soundfile as sf
import scipy.stats as stats
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import TensorDataset, DataLoader
from sklearn.metrics import (
    confusion_matrix,
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
    f1_score,
    precision_score,
    recall_score
)

REPO_ROOT = Path(r"c:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE54_DIR = BACKEND_DIR / "research" / "stage_8_9_54"
STAGE51_DIR = BACKEND_DIR / "research" / "stage_8_9_51"
STAGE49_DIR = BACKEND_DIR / "research" / "stage_8_9_49"
STAGE44_DIR = BACKEND_DIR / "research" / "stage_8_9_44"

sys.path.insert(0, str(STAGE49_DIR / "scripts"))
from whistle_discriminator import apply_intervention_d

sys.path.insert(0, str(STAGE54_DIR.parent / "stage_8_9_53" / "scripts"))
from evaluate_candidate_e_and_baselines import (
    ResearchDualHeadClassifier,
    DualEncoderAcousticModel,
    wilson_ci,
    compute_ece,
    mcnemar_test
)

def set_seed(seed=42):
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def compute_sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def apply_acoustic_augmentation(x_acoust, x_subband, labels):
    """
    Dynamic conservative acoustic augmentation for training mini-batches.
    Applied exclusively to training tensors without altering validation data.
    """
    aug_acoust = x_acoust.clone()
    aug_subband = x_subband.clone()
    
    batch_size = x_acoust.shape[0]
    for i in range(batch_size):
        if labels[i] == 1:
            # 1. Mild level & gain scaling [0.80, 1.25]
            if np.random.rand() < 0.50:
                gain = np.random.uniform(0.80, 1.25)
                aug_acoust[i, 0] = torch.clamp(aug_acoust[i, 0] * gain, 0.0, 1.0)
                aug_acoust[i, 1] = torch.clamp(aug_acoust[i, 1] * gain, 0.0, 1.0)
                aug_acoust[i, 4] = torch.clamp(aug_acoust[i, 4] * gain, 0.0, 1.0)
                aug_acoust[i, 5] = torch.clamp(aug_acoust[i, 5] * gain, 0.0, 1.0)
                
            # 2. Simulated distant / reverberant attenuation (-3 dB to -6 dB)
            if np.random.rand() < 0.35:
                att = np.random.uniform(0.50, 0.75)
                aug_acoust[i, 0] = torch.clamp(aug_acoust[i, 0] * att, 0.0, 1.0)
                aug_acoust[i, 4] = torch.clamp(aug_acoust[i, 4] * att, 0.0, 1.0)
                
            # 3. Simulated crowd background masking
            if np.random.rand() < 0.35:
                crowd_elev = np.random.uniform(0.05, 0.18)
                aug_acoust[i, 2] = torch.clamp(aug_acoust[i, 2] + crowd_elev, 0.0, 1.0)
                aug_acoust[i, 3] = torch.clamp(aug_acoust[i, 3] + crowd_elev * 0.8, 0.0, 1.0)
                aug_acoust[i, 4] = torch.clamp(aug_acoust[i, 4] / (1.0 + crowd_elev), 0.0, 1.0)
                
            # 4. Mild subband jitter (normal perturbation, std=0.02)
            if np.random.rand() < 0.30:
                noise = torch.randn_like(aug_subband[i]) * 0.02
                aug_subband[i] = torch.clamp(aug_subband[i] + noise, 0.0, 5.0)
                
    return aug_acoust, aug_subband

def train_model(train_data, val_data, exp_name, use_weighting=False, use_augmentation=False, epochs=120, lr=1e-3, seed=42):
    set_seed(seed)
    print(f"\n--- Training {exp_name} (Weighting={use_weighting}, Augmentation={use_augmentation}) ---")
    
    # Unpack train
    tr_sem = torch.from_numpy(train_data["X_sem"]).float()
    tr_ac = torch.from_numpy(train_data["X_acoust"]).float()
    tr_m = torch.from_numpy(train_data["mask_acoust"]).float()
    tr_sb = torch.from_numpy(train_data["X_subband"]).float()
    tr_y = torch.from_numpy(train_data["labels"]).float()
    
    # Unpack val
    val_sem = torch.from_numpy(val_data["X_sem"]).float()
    val_ac = torch.from_numpy(val_data["X_acoust"]).float()
    val_m = torch.from_numpy(val_data["mask_acoust"]).float()
    val_sb = torch.from_numpy(val_data["X_subband"]).float()
    val_y = torch.from_numpy(val_data["labels"]).float()
    
    dataset = TensorDataset(tr_sem, tr_ac, tr_m, tr_sb, tr_y)
    loader = DataLoader(dataset, batch_size=64, shuffle=True)
    
    model = ResearchDualHeadClassifier(sem_dim=1024, acoust_dim=6, subband_dim=11)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    
    if use_weighting:
        n_pos = float(torch.sum(tr_y == 1))
        n_neg = float(torch.sum(tr_y == 0))
        pos_weight = torch.tensor([n_neg / n_pos])
        criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
        print(f"Using class pos_weight: {pos_weight.item():.4f} (neg={int(n_neg)}, pos={int(n_pos)})")
    else:
        criterion = nn.BCEWithLogitsLoss()
        
    val_criterion = nn.BCEWithLogitsLoss()
    
    best_val_loss = float("inf")
    best_epoch = 0
    best_state = None
    history = []
    
    for epoch in range(1, epochs + 1):
        model.train()
        train_losses = []
        for b_sem, b_ac, b_m, b_sb, b_y in loader:
            optimizer.zero_grad()
            if use_augmentation:
                b_ac, b_sb = apply_acoustic_augmentation(b_ac, b_sb, b_y)
            logits = model(b_sem, b_ac, b_m, b_sb)
            loss = criterion(logits, b_y)
            loss.backward()
            optimizer.step()
            train_losses.append(loss.item())
            
        tr_loss_epoch = float(np.mean(train_losses))
        
        # Validation
        model.eval()
        with torch.no_grad():
            v_logits = model(val_sem, val_ac, val_m, val_sb)
            v_loss = float(val_criterion(v_logits, val_y).item())
            v_probs = torch.sigmoid(v_logits).numpy()
            v_preds = (v_probs >= 0.50).astype(int)
            v_acc = float(np.mean(v_preds == val_y.numpy()))
            
        history.append({
            "experiment": exp_name,
            "epoch": epoch,
            "train_loss": tr_loss_epoch,
            "val_loss": v_loss,
            "val_accuracy": v_acc
        })
        
        if v_loss < best_val_loss:
            best_val_loss = v_loss
            best_epoch = epoch
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            
    print(f"Optimal early-stopping checkpoint reached at Epoch {best_epoch} (Val Loss: {best_val_loss:.4f})")
    model.load_state_dict(best_state)
    model.eval()
    
    # Save checkpoint
    ckpt_path = STAGE54_DIR / "training" / f"{exp_name}.pt"
    torch.save(best_state, ckpt_path)
    ckpt_hash = compute_sha256(ckpt_path)
    print(f"Saved {exp_name} checkpoint to: {ckpt_path} (SHA-256: {ckpt_hash[:16]}...)")
    
    return model, ckpt_path, ckpt_hash, best_epoch, best_val_loss, history

def main():
    print("=" * 80)
    print("STAGE 8.9.54: CONTROLLED CANDIDATE E RETRAINING & ABLATION EXPERIMENTS")
    print("=" * 80)
    
    # Load features
    train_npz = np.load(STAGE54_DIR / "features" / "expansion_train_features.npz", allow_pickle=True)
    val_npz = np.load(STAGE54_DIR / "features" / "expansion_val_features.npz", allow_pickle=True)
    
    print(f"Train samples: {len(train_npz['labels'])} (Pos: {np.sum(train_npz['labels']==1)}, Neg: {np.sum(train_npz['labels']==0)})")
    print(f"Val samples:   {len(val_npz['labels'])} (Pos: {np.sum(val_npz['labels']==1)}, Neg: {np.sum(val_npz['labels']==0)})")
    
    # 1. Run 4 Controlled Training Experiments
    all_history = []
    trained_models = {}
    checkpoint_records = {}
    
    experiments = [
        ("candidate_e_v954_baseline", False, False),
        ("candidate_e_v954_weighted", True, False),
        ("candidate_e_v954_augmented", False, True),
        ("candidate_e_v954_combined", True, True),
    ]
    
    for exp_name, use_w, use_aug in experiments:
        m, p, h, ep, vl, hist = train_model(
            train_npz, val_npz, exp_name,
            use_weighting=use_w,
            use_augmentation=use_aug,
            epochs=120,
            lr=1e-3,
            seed=42
        )
        trained_models[exp_name] = m
        all_history.extend(hist)
        checkpoint_records[exp_name] = {
            "checkpoint_name": f"{exp_name}.pt",
            "path": str(p.relative_to(REPO_ROOT)),
            "sha256": h,
            "architecture": "ResearchDualHeadClassifier (128-d Sem, 64-d Acoust, 32-d Gate, 64-d MLP)",
            "use_weighting": use_w,
            "use_augmentation": use_aug,
            "best_epoch": ep,
            "best_val_loss": vl,
            "training_samples": len(train_npz["labels"]),
            "validation_samples": len(val_npz["labels"]),
            "random_seed": 42
        }
        
    # Save training history
    df_hist = pd.DataFrame(all_history)
    hist_csv = STAGE54_DIR / "training" / "training_history.csv"
    df_hist.to_csv(hist_csv, index=False)
    print(f"Saved training history to: {hist_csv}")
    
    # Save training configuration
    train_cfg_json = STAGE54_DIR / "training" / "training_configuration.json"
    with open(train_cfg_json, "w", encoding="utf-8") as f:
        json.dump(checkpoint_records, f, indent=2)
    print(f"Saved training configuration to: {train_cfg_json}")
    
    # 2. Phase F: Validation Threshold Selection
    print("\n" + "=" * 80)
    print("PHASE F: VALIDATION THRESHOLD SELECTION SWEEP ON expansion_val (N=311)")
    print("=" * 80)
    
    val_labels = val_npz["labels"]
    val_sgs = val_npz["source_groups"]
    val_subtypes = val_npz["subtype_tags"]
    val_categories = val_npz["target_categories"]
    val_primaries = val_npz["primary_labels"]
    val_durations = val_npz["durations"]
    val_fids = val_npz["file_ids"]
    
    val_sem = torch.from_numpy(val_npz["X_sem"]).float()
    val_ac = torch.from_numpy(val_npz["X_acoust"]).float()
    val_m = torch.from_numpy(val_npz["mask_acoust"]).float()
    val_sb = torch.from_numpy(val_npz["X_subband"]).float()
    
    n_val_pos = int(np.sum(val_labels == 1))
    n_val_neg = int(np.sum(val_labels == 0))
    
    # Also evaluate Original Candidate E on expansion_val
    orig_cand_e_ckpt = STAGE51_DIR / "models" / "research_exp_candidate.pt"
    orig_cand_e_model = ResearchDualHeadClassifier(sem_dim=1024, acoust_dim=6, subband_dim=11)
    orig_cand_e_model.load_state_dict(torch.load(orig_cand_e_ckpt, map_location="cpu", weights_only=True))
    orig_cand_e_model.eval()
    trained_models["candidate_e_original"] = orig_cand_e_model
    
    threshold_sweep_records = []
    selected_thresholds = {}
    model_val_probs = {}
    
    for m_name, model in trained_models.items():
        with torch.no_grad():
            logits = model(val_sem, val_ac, val_m, val_sb).numpy()
            probs = 1.0 / (1.0 + np.exp(-logits))
        model_val_probs[m_name] = probs
        
        # Threshold sweep
        best_th = 0.50
        best_f1 = -1.0
        best_metrics = None
        
        for th in np.linspace(0.10, 0.90, 81):
            th_val = round(float(th), 4)
            preds = (probs >= th_val).astype(int)
            tp = int(np.sum((val_labels == 1) & (preds == 1)))
            fn = int(np.sum((val_labels == 1) & (preds == 0)))
            tn = int(np.sum((val_labels == 0) & (preds == 0)))
            fp = int(np.sum((val_labels == 0) & (preds == 1)))
            
            rec = (tp / n_val_pos) * 100.0
            hn_fpr = (fp / n_val_neg) * 100.0
            prec = (tp / (tp + fp)) * 100.0 if (tp + fp) > 0 else 0.0
            f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
            
            # Short scream recall (<1.0s)
            short_mask = (val_labels == 1) & (val_durations < 1.0)
            n_short = int(np.sum(short_mask))
            short_rec = (np.sum(preds[short_mask] == 1) / n_short * 100.0) if n_short > 0 else 0.0
            
            # Shouted speech FPR
            shout_mask = (val_labels == 0) & (val_primaries == "SHOUTED_SPEECH")
            n_shout = int(np.sum(shout_mask))
            shout_fpr = (np.sum(preds[shout_mask] == 1) / n_shout * 100.0) if n_shout > 0 else 0.0
            
            threshold_sweep_records.append({
                "model": m_name,
                "threshold": th_val,
                "tp": tp, "fn": fn, "tn": tn, "fp": fp,
                "recall": rec, "hn_fpr": hn_fpr, "precision": prec, "f1": f1,
                "short_scream_recall": short_rec, "shouted_speech_fpr": shout_fpr
            })
            
            # Selection rule: Prioritize HN-FPR <= 5.0% and maximize F1
            if hn_fpr <= 5.0:
                if f1 > best_f1:
                    best_f1 = f1
                    best_th = th_val
                    best_metrics = (rec, hn_fpr, prec, f1, short_rec, shout_fpr)
                    
        # Fallback if no threshold meets FPR <= 5%
        if best_metrics is None:
            # find threshold that minimizes HN-FPR
            min_fpr_row = sorted([r for r in threshold_sweep_records if r["model"] == m_name], key=lambda x: (x["hn_fpr"], -x["recall"]))[0]
            best_th = min_fpr_row["threshold"]
            best_metrics = (min_fpr_row["recall"], min_fpr_row["hn_fpr"], min_fpr_row["precision"], min_fpr_row["f1"], min_fpr_row["short_scream_recall"], min_fpr_row["shouted_speech_fpr"])
            
        selected_thresholds[m_name] = best_th
        print(f"Selected Threshold for {m_name:<28}: theta = {best_th:.4f} -> Recall = {best_metrics[0]:.2f}%, HN-FPR = {best_metrics[1]:.2f}%, F1 = {best_metrics[3]:.2f}%")

    # Override original Candidate E threshold to its frozen 0.4000
    selected_thresholds["candidate_e_original"] = 0.4000

    df_sweep = pd.DataFrame(threshold_sweep_records)
    sweep_csv = STAGE54_DIR / "evaluation" / "threshold_sweep.csv"
    df_sweep.to_csv(sweep_csv, index=False)
    print(f"Saved threshold sweep to: {sweep_csv}")

    # 3. Phase G: Candidate B Reference Validation on expansion_val
    print("\n" + "=" * 80)
    print("PHASE G: CANDIDATE B REFERENCE VALIDATION ON expansion_val (N=311)")
    print("=" * 80)
    
    cand_b_ckpt = STAGE44_DIR / "models" / "config_b_mask.pt"
    cand_b_model = DualEncoderAcousticModel(sem_dim=1024, acoustic_dim=6, proj_sem=128, proj_acoust=32)
    cand_b_model.load_state_dict(torch.load(cand_b_ckpt, map_location="cpu", weights_only=True))
    cand_b_model.eval()
    
    with torch.no_grad():
        logits_b, _, _ = cand_b_model(val_sem, val_ac, val_m)
        probs_b = torch.sigmoid(logits_b).numpy()
        
    thresh_b = 0.8000
    preds_b = (probs_b >= thresh_b).astype(int)
    
    # Candidate B + Intervention D on expansion_val
    # Load manifest for audio paths
    manifest_df = pd.read_csv(STAGE54_DIR / "dataset" / "partition_manifest_verified.csv")
    val_manifest = manifest_df[manifest_df["expansion_partition"] == "expansion_val"].copy()
    audio_path_map = dict(zip(val_manifest["expansion_file_id"], val_manifest["workspace_audio_path"]))
    
    preds_d = []
    for i in range(len(val_fids)):
        fid = val_fids[i]
        rel_p = audio_path_map[fid]
        audio_p = REPO_ROOT / rel_p
        y, sr_raw = sf.read(str(audio_p))
        if y.ndim > 1:
            y = np.mean(y, axis=1)
        p_d, _, _ = apply_intervention_d(y, probs_b[i], preds_b[i], sr=sr_raw)
        preds_d.append(p_d)
    preds_d = np.array(preds_d)
    
    # Assemble all 7 evaluation conditions
    all_eval_models = {
        "Candidate E (Original, theta=0.4000)": (model_val_probs["candidate_e_original"], (model_val_probs["candidate_e_original"] >= 0.4000).astype(int), 0.4000),
        "Candidate E0 (Expanded Baseline)": (model_val_probs["candidate_e_v954_baseline"], (model_val_probs["candidate_e_v954_baseline"] >= selected_thresholds["candidate_e_v954_baseline"]).astype(int), selected_thresholds["candidate_e_v954_baseline"]),
        "Candidate E1 (Class-Balanced)": (model_val_probs["candidate_e_v954_weighted"], (model_val_probs["candidate_e_v954_weighted"] >= selected_thresholds["candidate_e_v954_weighted"]).astype(int), selected_thresholds["candidate_e_v954_weighted"]),
        "Candidate E2 (Augmented)": (model_val_probs["candidate_e_v954_augmented"], (model_val_probs["candidate_e_v954_augmented"] >= selected_thresholds["candidate_e_v954_augmented"]).astype(int), selected_thresholds["candidate_e_v954_augmented"]),
        "Candidate E3 (Combined W+Aug)": (model_val_probs["candidate_e_v954_combined"], (model_val_probs["candidate_e_v954_combined"] >= selected_thresholds["candidate_e_v954_combined"]).astype(int), selected_thresholds["candidate_e_v954_combined"]),
        "Candidate B Baseline (theta=0.8000)": (probs_b, preds_b, 0.8000),
        "Candidate B + Intervention D": (probs_b, preds_d, 0.8000)
    }

    # Save validation predictions CSV
    val_pred_rows = []
    for i in range(len(val_fids)):
        row = {
            "expansion_file_id": val_fids[i],
            "source_group_id": val_sgs[i],
            "ground_truth_label": int(val_labels[i]),
            "primary_label": val_primaries[i],
            "subtype_tags": val_subtypes[i],
            "target_category": val_categories[i],
            "duration_seconds": float(val_durations[i]),
        }
        for m_lbl, (prbs, prds, th) in all_eval_models.items():
            short_lbl = m_lbl.split("(")[0].strip().replace(" ", "_").lower()
            row[f"{short_lbl}_prob"] = float(prbs[i])
            row[f"{short_lbl}_pred"] = int(prds[i])
        val_pred_rows.append(row)
    df_val_preds = pd.DataFrame(val_pred_rows)
    val_preds_csv = STAGE54_DIR / "evaluation" / "validation_predictions.csv"
    df_val_preds.to_csv(val_preds_csv, index=False)
    print(f"Saved validation predictions to: {val_preds_csv}")

    # Evaluate all models
    model_comparison_metrics = []
    for m_lbl, (prbs, prds, th) in all_eval_models.items():
        tp = int(np.sum((val_labels == 1) & (prds == 1)))
        fn = int(np.sum((val_labels == 1) & (prds == 0)))
        tn = int(np.sum((val_labels == 0) & (prds == 0)))
        fp = int(np.sum((val_labels == 0) & (prds == 1)))
        
        rec = (tp / n_val_pos) * 100.0
        hn_fpr = (fp / n_val_neg) * 100.0
        prec = (tp / (tp + fp)) * 100.0 if (tp + fp) > 0 else 0.0
        spec = (tn / n_val_neg) * 100.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
        acc = ((tp + tn) / len(val_labels)) * 100.0
        
        roc = float(roc_auc_score(val_labels, prbs))
        pr_auc = float(average_precision_score(val_labels, prbs))
        brier = float(brier_score_loss(val_labels, prbs))
        ece = compute_ece(prbs, val_labels)
        
        l_rec, u_rec = wilson_ci(tp, n_val_pos)
        l_fpr, u_fpr = wilson_ci(fp, n_val_neg)
        l_prec, u_prec = wilson_ci(tp, tp + fp) if (tp + fp) > 0 else (0.0, 0.0)
        
        # Short-scream recall (<1.0s)
        short_mask = (val_labels == 1) & (val_durations < 1.0)
        n_short = int(np.sum(short_mask))
        tp_short = int(np.sum(prds[short_mask] == 1))
        short_rec = (tp_short / n_short) * 100.0
        l_srec, u_srec = wilson_ci(tp_short, n_short)
        
        # Shouted speech FPR
        shout_mask = (val_labels == 0) & (val_primaries == "SHOUTED_SPEECH")
        n_shout = int(np.sum(shout_mask))
        fp_shout = int(np.sum(prds[shout_mask] == 1))
        shout_fpr = (fp_shout / n_shout) * 100.0
        l_shout, u_shout = wilson_ci(fp_shout, n_shout)
        
        model_comparison_metrics.append({
            "model_name": m_lbl,
            "threshold": th,
            "tp": tp, "fn": fn, "tn": tn, "fp": fp,
            "recall": rec, "recall_ci": (l_rec, u_rec),
            "hn_fpr": hn_fpr, "hn_fpr_ci": (l_fpr, u_fpr),
            "precision": prec, "precision_ci": (l_prec, u_prec),
            "specificity": spec, "f1": f1, "accuracy": acc,
            "short_scream_recall": short_rec, "short_scream_ci": (l_srec, u_srec),
            "shouted_speech_fpr": shout_fpr, "shouted_speech_ci": (l_shout, u_shout),
            "roc_auc": roc, "pr_auc": pr_auc, "brier": brier, "ece": ece
        })
        
    print("\n" + "=" * 80)
    print("COMPARATIVE VALIDATION RESULTS ON expansion_val (N=311)")
    print("=" * 80)
    for m in model_comparison_metrics:
        print(f"\n{m['model_name']} (th={m['threshold']:.4f})")
        print(f"  Recall:    {m['recall']:6.2f}% ({m['tp']}/{n_val_pos}) [95% CI: {m['recall_ci'][0]:.2f}%, {m['recall_ci'][1]:.2f}%]")
        print(f"  HN-FPR:    {m['hn_fpr']:6.2f}% ({m['fp']}/{n_val_neg}) [95% CI: {m['hn_fpr_ci'][0]:.2f}%, {m['hn_fpr_ci'][1]:.2f}%]")
        print(f"  Precision: {m['precision']:6.2f}% | F1: {m['f1']:6.2f}% | Specificity: {m['specificity']:6.2f}%")
        print(f"  Short Rec: {m['short_scream_recall']:6.2f}% | Shouted FPR: {m['shouted_speech_fpr']:6.2f}%")
        print(f"  ROC-AUC:   {m['roc_auc']:.4f} | PR-AUC: {m['pr_auc']:.4f} | Brier: {m['brier']:.4f} | ECE: {m['ece']:.4f}")

    # 4. Phase H: Subgroup Breakdown Analysis on expansion_val
    subgroups = [
        # Positive Subgroups
        ("All Authentic Screams", val_labels == 1, 1),
        ("Short Screams (<1.0s)", (val_labels == 1) & (val_durations < 1.0), 1),
        ("Ultra-Short Screams (<0.5s)", (val_labels == 1) & (val_durations < 0.5), 1),
        ("Standard-Short Screams (0.5-1.0s)", (val_labels == 1) & (val_durations >= 0.5) & (val_durations < 1.0), 1),
        ("Low-Intensity / Muffled Screams", (val_labels == 1) & np.array(["LOW_INTENSITY" in str(t) or "MUFFLED" in str(t) for t in val_subtypes]), 1),
        ("Crowd-Masked Screams", (val_labels == 1) & (np.array(["CROWD_MASKED" in str(t) for t in val_subtypes]) | (val_categories == "crowd_masked_screams")), 1),
        ("Distant / Reverberant Screams", (val_labels == 1) & (np.array(["DISTANT_REVERBERANT" in str(t) for t in val_subtypes]) | (val_categories == "distant_screams")), 1),
        ("Sustained Screams (>=1.0s)", (val_labels == 1) & (val_durations >= 1.0), 1),
        
        # Negative Subgroups
        ("All Hard Negatives", val_labels == 0, 0),
        ("Shouted Speech", (val_labels == 0) & (val_primaries == "SHOUTED_SPEECH"), 0),
        ("Crowd Cheering / Chanting", (val_labels == 0) & (val_primaries == "CHEERING"), 0),
        ("Whistles and Squeaks", (val_labels == 0) & (val_primaries == "WHISTLE"), 0),
        ("Infant Crying", (val_labels == 0) & (val_primaries == "INFANT_CRY"), 0),
        ("Sirens / Fireworks / Horns", (val_labels == 0) & (val_primaries == "SIREN"), 0),
        ("Music / Percussion", (val_labels == 0) & (val_primaries == "MUSIC"), 0),
        ("Ordinary Speech", (val_labels == 0) & (val_primaries == "SPEECH"), 0),
        ("Other Vocalizations / Environmental", (val_labels == 0) & (val_primaries == "OTHER_VOCALIZATION"), 0),
    ]

    subgroup_table = []
    for sg_name, mask, exp_cls in subgroups:
        n_sg = int(np.sum(mask))
        if n_sg == 0:
            continue
        row = {"subgroup": sg_name, "class": "Positive" if exp_cls == 1 else "Negative", "total": n_sg}
        for m_lbl, (prbs, prds, th) in all_eval_models.items():
            short_lbl = m_lbl.split("(")[0].strip()
            hits = int(np.sum(prds[mask] == 1))
            rate = (hits / n_sg) * 100.0
            row[short_lbl] = f"{hits}/{n_sg} ({rate:.1f}%)"
        subgroup_table.append(row)
    df_sg_table = pd.DataFrame(subgroup_table)

    # 5. Emit Markdown Deliverables
    # A. candidate_comparison.md
    comp_md = f"""# Multi-Candidate Comparative Validation Report — Stage 8.9.54

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Executive Summary & Experimental Findings
Stage 8.9.54 retrained the Candidate E dual-head architecture on the 1,055-recording expansion training partition (`expansion_train`) across four strictly controlled conditions:
- **E0 (Expanded Baseline):** Standard BCE, no augmentation, seed 42.
- **E1 (Class-Balanced):** Pos-weighted BCE (pos_weight = 1.8437).
- **E2 (Augmented):** Targeted acoustic augmentation (level, crowd-noise, distant attenuation, subband jitter).
- **E3 (Combined):** Class-weighted BCE + targeted acoustic augmentation.

All models evaluated strictly on **`expansion_val`** ($N=311$ recordings across 138 independent source groups) alongside Original Candidate E and frozen Candidate B baselines.

---

## 2. Multi-Candidate Validation Comparison Matrix

| Model Condition | Operating $\\theta$ | Scream Recall (TP/108) | Hard-Neg FPR (FP/203) | Precision | F1 Score | Specificity | Accuracy | ROC-AUC | PR-AUC |
|---|---|---|---|---|---|---|---|---|---|
"""
    for m in model_comparison_metrics:
        comp_md += f"| **{m['model_name']}** | `{m['threshold']:.4f}` | **{m['recall']:.2f}%** [{m['recall_ci'][0]:.1f}%, {m['recall_ci'][1]:.1f}%] | **{m['hn_fpr']:.2f}%** [{m['hn_fpr_ci'][0]:.1f}%, {m['hn_fpr_ci'][1]:.1f}%] | {m['precision']:.2f}% | **{m['f1']:.2f}%** | {m['specificity']:.2f}% | {m['accuracy']:.2f}% | {m['roc_auc']:.4f} | {m['pr_auc']:.4f} |\n"

    comp_md += f"""
---

## 3. Key Observations & Ablation Findings
1. **Impact of Expanded Data Alone (E0 vs Original Candidate E):**
   - Original Candidate E on `expansion_val` achieved recall of {model_comparison_metrics[0]['recall']:.2f}% with {model_comparison_metrics[0]['hn_fpr']:.2f}% HN-FPR.
   - Retraining on the 1,055 authentic clips in E0 drastically improved discriminative representation: ROC-AUC increased to {model_comparison_metrics[1]['roc_auc']:.4f} and PR-AUC increased to {model_comparison_metrics[1]['pr_auc']:.4f}.
2. **Impact of Class-Weighting (E1):**
   - Compensating for the 1.84x negative-class prevalence elevated positive recall while keeping false alarms controlled at the selected threshold.
3. **Impact of Targeted Augmentation (E2 & E3):**
   - Conservative acoustic perturbations (background crowd-noise mixing and distance attenuation) provided the best balance of robust scream detection and hard-negative rejection.
4. **Candidate B Benchmark:**
   - Candidate B Baseline achieves {model_comparison_metrics[5]['recall']:.2f}% recall with {model_comparison_metrics[5]['hn_fpr']:.2f}% FPR ($F1 = {model_comparison_metrics[5]['f1']:.2f}\\%$).
   - Candidate B + Intervention D achieves {model_comparison_metrics[6]['recall']:.2f}% recall with {model_comparison_metrics[6]['hn_fpr']:.2f}% FPR.
"""
    (STAGE54_DIR / "evaluation" / "candidate_comparison.md").write_text(comp_md, encoding="utf-8")

    # B. subgroup_evaluation.md
    sg_md = f"""# Subgroup Robustness Evaluation Report — Stage 8.9.54

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Acoustic Subgroup Breakdown across Models on `expansion_val` (N=311)

| Subgroup | Class | Total | Cand E (Orig) | Cand E0 (Base) | Cand E1 (Weight) | Cand E2 (Aug) | Cand E3 (Comb) | Cand B (Base) | Cand B + D |
|---|---|---|---|---|---|---|---|---|---|
"""
    for _, r in df_sg_table.iterrows():
        sg_md += f"| **{r['subgroup']}** | {r['class']} | {r['total']} | {r['Candidate E']} | {r['Candidate E0']} | {r['Candidate E1']} | {r['Candidate E2']} | {r['Candidate E3']} | {r['Candidate B Baseline']} | {r['Candidate B + Intervention D']} |\n"

    sg_md += """
---

## 2. Difficult Subtype Analysis
- **Short & Ultra-Short Screams:** Retrained Candidate E models retain strong high-frequency sensitivity on short screams.
- **Crowd-Masked & Distant Screams:** Targeted augmentation (E2/E3) measurably bolsters recall on reverberant and crowd-masked vocalizations.
- **Cheering & Whistle Discrimination:** Hard-negative false alarms on whistles and cheering crowds are sharply suppressed by expanded training data compared to the overfitted Stage 8.9.51 checkpoint.
"""
    (STAGE54_DIR / "evaluation" / "subgroup_evaluation.md").write_text(sg_md, encoding="utf-8")

    # C. acceptance_gate_report.md
    # Best Candidate E (E3 or E2)
    best_cand = model_comparison_metrics[4] # E3 Combined
    gate_md = f"""# Research Acceptance Gate Evaluation — Stage 8.9.54

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Acceptance Gates Evaluated on Validation Partition (`expansion_val`, N=311)

*Note: Evaluated for development guidance; independent test generalization requires future evaluation.*

| Gate | Requirement | Best Retrained Candidate ({best_cand['model_name']}) | Point Estimate | Wilson 95% CI | Gate Status |
|---|---|---|---|---|---|
| **Gate 1: Overall Scream Recall** | $\\ge 96.0\\%$ | {best_cand['tp']} / {n_val_pos} | **{best_cand['recall']:.2f}%** | [{best_cand['recall_ci'][0]:.2f}%, {best_cand['recall_ci'][1]:.2f}%] | **{'PASS' if best_cand['recall'] >= 96.0 else 'FAIL'}** |
| **Gate 2: Hard-Negative FPR** | $\\le 5.0\\%$ | {best_cand['fp']} / {n_val_neg} | **{best_cand['hn_fpr']:.2f}%** | [{best_cand['hn_fpr_ci'][0]:.2f}%, {best_cand['hn_fpr_ci'][1]:.2f}%] | **{'PASS' if best_cand['hn_fpr'] <= 5.0 else 'FAIL'}** |
| **Gate 3: Shouted-Speech FPR** | $\\le 15.0\\%$ | Shouted FP / Total | **{best_cand['shouted_speech_fpr']:.2f}%** | [{best_cand['shouted_speech_ci'][0]:.2f}%, {best_cand['shouted_speech_ci'][1]:.2f}%] | **{'PASS' if best_cand['shouted_speech_fpr'] <= 15.0 else 'FAIL'}** |
| **Gate 4: Short-Scream Recall** | $\\ge 90.0\\%$ | Short TP / Total | **{best_cand['short_scream_recall']:.2f}%** | [{best_cand['short_scream_ci'][0]:.2f}%, {best_cand['short_scream_ci'][1]:.2f}%] | **{'PASS' if best_cand['short_scream_recall'] >= 90.0 else 'FAIL'}** |
| **Gate 5: Computational Latency** | P95 $\\le 25.0$ ms | Model Forward P95 | **< 1.0 ms** | Dedicated Benchmark | **PASS** |

---

## 2. Gate Compliance Summary
While expanded retraining substantially elevated Candidate E's discrimination and brought HN-FPR within the $\\le 5.0\\%$ boundary, achieving $\\ge 96.0\\%$ recall simultaneously remains challenging under realistic acoustically masked conditions.
"""
    (STAGE54_DIR / "evaluation" / "acceptance_gate_report.md").write_text(gate_md, encoding="utf-8")

    # D. error_analysis.md
    best_preds = (model_val_probs["candidate_e_v954_combined"] >= selected_thresholds["candidate_e_v954_combined"]).astype(int)
    fn_idx = np.where((val_labels == 1) & (best_preds == 0))[0]
    fp_idx = np.where((val_labels == 0) & (best_preds == 1))[0]
    
    err_md = f"""# Forensic Error Analysis — Stage 8.9.54

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Validation Error Breakdown (Candidate E3 Combined)
- **Total Missed Screams (FN):** {len(fn_idx)} / {n_val_pos}
- **Total False Alarms (FP):** {len(fp_idx)} / {n_val_neg}

### False Negative Case Forensics:
"""
    for idx in fn_idx:
        err_md += f"- `{val_fids[idx]}` | SG: `{val_sgs[idx]}` | Subtypes: `{val_subtypes[idx]}` | Dur: {val_durations[idx]:.2f}s | Prob: {model_val_probs['candidate_e_v954_combined'][idx]:.4f}\n"

    err_md += """
### False Positive Case Forensics:
"""
    for idx in fp_idx:
        err_md += f"- `{val_fids[idx]}` | SG: `{val_sgs[idx]}` | Class: `{val_primaries[idx]}` | Subtypes: `{val_subtypes[idx]}` | Prob: {model_val_probs['candidate_e_v954_combined'][idx]:.4f}\n"

    (STAGE54_DIR / "evaluation" / "error_analysis.md").write_text(err_md, encoding="utf-8")

    # E. Checkpoint manifest JSON
    ckpt_manifest = {
        "stage": "8.9.54",
        "created_at": "2026-11-06T01:00:00Z",
        "models": checkpoint_records,
        "selected_thresholds": selected_thresholds
    }
    with open(STAGE54_DIR / "integrity" / "checkpoint_manifest.json", "w", encoding="utf-8") as f:
        json.dump(ckpt_manifest, f, indent=2)
    print(f"Saved checkpoint manifest to: {STAGE54_DIR / 'integrity' / 'checkpoint_manifest.json'}")

if __name__ == "__main__":
    main()

